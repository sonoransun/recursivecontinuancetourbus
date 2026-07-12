"""Wiener's attack: a small RSA private exponent leaks the whole key.

RSA picks a modulus ``n = p*q`` and exponents ``e``, ``d`` with
``e*d = 1 (mod phi(n))``, publishing ``(n, e)`` and hiding ``d``. A tempting
optimisation is to choose ``d`` *small*, so decryption is fast. Wiener (1990)
showed this is fatal: if ``d < n**0.25 / 3`` the attacker can recover ``d`` from
the public key alone.

The mechanism is pure continued fractions. From ``e*d - k*phi = 1`` for some
integer ``k``, divide by ``d*phi``:

    | e/n - k/d | = | e/n - e/phi + (e/phi - k/d) |  ~  small,

and because ``phi`` is very close to ``n``, ``k/d`` turns out to be so good an
approximation of ``e/n`` that it must be one of its **convergents**. So the
attack simply walks the convergents of ``e/n``; each denominator is a guess at
``d``, checked by reconstructing ``phi`` and factoring ``n``. The whole thing
is stdlib arithmetic — no third-party crypto library in sight.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction
from math import gcd, isqrt

from ..cf.convergents import convergent_pairs
from ..cf.expand import cf_from_fraction

__all__ = [
    "RSAKey",
    "is_probable_prime",
    "gen_prime",
    "egcd",
    "modinv",
    "make_vulnerable_key",
    "make_safe_key",
    "wiener_attack",
]

# Small primes used both as trial divisors and as Miller-Rabin witnesses. This
# fixed witness set makes ``is_probable_prime`` deterministic (and exact for
# every n below 3.3e24, far past anything these demos generate).
_WITNESSES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


@dataclass(frozen=True)
class RSAKey:
    """An RSA keypair, private parts and factorisation included (it's a demo).

    ``n = p*q`` is the modulus, ``e`` the public exponent, ``d`` the private
    exponent with ``e*d = 1 (mod (p-1)(q-1))``.
    """

    n: int
    e: int
    d: int
    p: int
    q: int


# --------------------------------------------------------------------------- #
#  Stdlib number-theory helpers.
# --------------------------------------------------------------------------- #

def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclid: return ``(g, x, y)`` with ``a*x + b*y == g == gcd(a, b)``.

    >>> egcd(240, 46)
    (2, -9, 47)
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def modinv(a: int, m: int) -> int:
    """The inverse of ``a`` modulo ``m``; raises if none exists.

    >>> modinv(17993, 89964)
    5
    """
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse modulo {m}")
    return x % m


def is_probable_prime(n: int) -> bool:
    """Deterministic Miller-Rabin over a fixed witness set.

    Exact for all ``n`` these demos produce (the witness set certifies every
    integer below 3.3e24).

    >>> is_probable_prime(90581)      # 379 * 239
    False
    >>> is_probable_prime(379)
    True
    >>> [n for n in range(2, 20) if is_probable_prime(n)]
    [2, 3, 5, 7, 11, 13, 17, 19]
    """
    if n < 2:
        return False
    for p in _WITNESSES:
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in _WITNESSES:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def gen_prime(bits: int, rng: random.Random) -> int:
    """A random ``bits``-bit prime (top and bottom bits forced set).

    Draws candidates from the supplied :class:`random.Random`, so a seeded
    generator makes the result reproducible.

    >>> gen_prime(16, random.Random(0))
    60331
    """
    if bits < 2:
        raise ValueError("need at least 2 bits")
    while True:
        candidate = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


# --------------------------------------------------------------------------- #
#  Key generation.
# --------------------------------------------------------------------------- #

def make_vulnerable_key(bits: int = 256, *, rng: random.Random | None = None) -> RSAKey:
    """Build an RSA key with a Wiener-small private exponent ``d``.

    Chooses balanced primes ``q < p < 2q`` of about ``bits/2`` each, then a
    small ``d < n**0.25 / 3`` coprime to ``phi``, and sets ``e = d**-1 mod phi``.
    Such a key is exactly what :func:`wiener_attack` breaks. Pass a seeded
    ``rng`` for reproducibility.

    >>> key = make_vulnerable_key(128, rng=random.Random(1))
    >>> key.e * key.d % ((key.p - 1) * (key.q - 1))
    1
    >>> key.d < round(key.n ** 0.25) // 3          # provably Wiener-weak
    True
    """
    if rng is None:
        rng = random.Random()
    half = bits // 2
    while True:
        p = gen_prime(half, rng)
        q = gen_prime(half, rng)
        if p == q:
            continue
        if p < q:
            p, q = q, p
        if not q < p < 2 * q:  # balanced primes: keeps Wiener's bound in force
            continue
        n = p * q
        phi = (p - 1) * (q - 1)
        bound = isqrt(isqrt(n)) // 3  # floor(n**0.25 / 3), Wiener's threshold
        if bound < 3:
            continue
        d = _small_coprime(phi, bound, rng)
        if d is None:
            continue
        e = modinv(d, phi)
        if e == d:  # degenerate; redraw
            continue
        return RSAKey(n=n, e=e, d=d, p=p, q=q)


def make_safe_key(bits: int = 256, *, rng: random.Random | None = None) -> RSAKey:
    """Build a Wiener-safe RSA key with the standard public exponent ``e = 65537``.

    Here ``d`` is large (roughly the size of ``n``), so ``k/d`` is nowhere near
    a convergent of ``e/n`` and :func:`wiener_attack` finds nothing.

    >>> key = make_safe_key(256, rng=random.Random(2))
    >>> key.e
    65537
    >>> wiener_attack(key.e, key.n) is None
    True
    """
    if rng is None:
        rng = random.Random()
    half = bits // 2
    e = 65537
    while True:
        p = gen_prime(half, rng)
        q = gen_prime(half, rng)
        if p == q:
            continue
        if p < q:
            p, q = q, p
        phi = (p - 1) * (q - 1)
        if gcd(e, phi) != 1:
            continue
        d = modinv(e, phi)
        return RSAKey(n=p * q, e=e, d=d, p=p, q=q)


def _small_coprime(phi: int, bound: int, rng: random.Random) -> int | None:
    """A random odd ``d`` in ``[3, bound)`` coprime to ``phi``, or ``None``."""
    for _ in range(200):
        d = rng.randrange(3, bound) | 1
        if gcd(d, phi) == 1:
            return d
    return None


# --------------------------------------------------------------------------- #
#  The attack.
# --------------------------------------------------------------------------- #

def wiener_attack(e: int, n: int) -> int | None:
    """Recover the private exponent ``d`` from a public key ``(e, n)``, or ``None``.

    Walks the convergents ``k/d`` of ``e/n``. For each, a candidate ``phi`` is
    read off ``e*d - 1 = k*phi``; if it divides evenly, ``p`` and ``q`` are the
    roots of ``x**2 - (n - phi + 1) x + n`` and are checked against ``n``. The
    first convergent that factors ``n`` yields the true ``d``. Returns ``None``
    when no convergent works — i.e. the key is not Wiener-weak.

    >>> wiener_attack(17993, 90581)        # textbook: n = 379 * 239, d = 5
    5
    """
    for k, d in convergent_pairs(cf_from_fraction(Fraction(e, n))):
        if k == 0:  # the [0; ...] head: k/d = 0/1 tells us nothing
            continue
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        # p and q solve x^2 - (p+q) x + pq = 0 with p+q = n - phi + 1, pq = n.
        p_plus_q = n - phi + 1
        disc = p_plus_q * p_plus_q - 4 * n
        if disc < 0:
            continue
        root = isqrt(disc)
        if root * root != disc:  # not a perfect square: this convergent is wrong
            continue
        if (p_plus_q + root) % 2 != 0:
            continue
        p = (p_plus_q + root) // 2
        q = (p_plus_q - root) // 2
        if p * q == n:
            return d
    return None
