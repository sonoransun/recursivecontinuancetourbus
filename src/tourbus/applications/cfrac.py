"""CFRAC: factoring by continued fractions (Morrison & Brillhart, 1970/1975).

Lehmer and Powers proposed the idea in 1931; Morrison and Brillhart turned it
into the first modern "combine congruences" factorization when, in 1970, they
split the seventh Fermat number ``F7 = 2**128 + 1`` on an IBM 360/91 in about
ninety minutes (published 1975). It is the direct ancestor of the quadratic
sieve and the number field sieve.

The engine is pure continued fractions. Expand ``sqrt(k*N)`` with the integer
PQa recurrence; its denominators ``Q_i`` are small — below ``2*sqrt(k*N)`` — and
so unusually likely to be *smooth* (to factor completely over a small set of
primes). The convergent numerators ``A_i`` satisfy the key congruence

    A_i**2  ==  (-1)**(i+1) * Q_{i+1}   (mod N),

so every smooth ``Q`` is a congruence of a square to a signed smooth number.
Collect enough of them, find a combination whose exponent vectors (the sign
bit included) sum to zero over ``GF(2)``, and their product is a genuine
``X**2 == Y**2 (mod N)``. Then ``gcd(X - Y, N)`` is, with good odds, a proper
factor. The whole thing is stdlib integer arithmetic — no floats, no luck asked
of the hardware.

The indexing above is the one trap: it is ``A_i`` paired with ``Q_{i+1}``, not
``Q_i``. Get it wrong by one and every congruence is real but every gcd is
trivial. :func:`cfrac_relations` is written to that pairing and the tests pin
it on ``N = 13290059``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from math import gcd, isqrt

from .wiener import is_probable_prime

__all__ = [
    "FERMAT_F7",
    "F7_FACTORS",
    "Relation",
    "smoothness_base",
    "cfrac_relations",
    "solve_gf2",
    "congruence_of_squares",
    "cfrac_factor",
    "cfrac_demo_trace",
    "verify_f7",
]

# The seventh Fermat number and the split Morrison & Brillhart published in 1975.
FERMAT_F7: int = 2**128 + 1
F7_FACTORS: tuple[int, int] = (59649589127497217, 5704689200685129054721)


@dataclass(frozen=True)
class Relation:
    """One smooth congruence ``a_mod_n**2 == signed_q (mod n)``.

    ``index`` is the PQa step ``i`` that produced it, ``a_mod_n`` the convergent
    numerator ``A_i`` reduced mod ``n``, and ``signed_q`` the value
    ``(-1)**(i+1) * Q_{i+1}``. ``factors`` is that signed value's factorisation
    over the smoothness base: prime ``-> exponent``, with the sign carried on the
    key ``-1``.

    >>> Relation(4, 171341, -2050, {2: 1, 5: 2, 41: 1, -1: 1}).signed_q
    -2050
    """

    index: int
    a_mod_n: int
    signed_q: int
    factors: dict[int, int]


# --------------------------------------------------------------------------- #
#  The smoothness base.
# --------------------------------------------------------------------------- #

def smoothness_base(n: int, bound: int) -> list[int]:
    """The primes ``p <= bound`` that can divide a ``Q_i``, with ``-1`` in front.

    An odd prime ``p`` divides some PQa denominator only when ``n`` is a
    quadratic residue modulo ``p`` (or ``p`` divides ``n``); every other prime is
    wasted in the base. The Euler criterion ``n**((p-1)/2) mod p`` is ``0`` when
    ``p | n``, ``1`` for a residue and ``p-1`` for a non-residue, so we keep ``p``
    exactly when that value is ``0`` or ``1``. ``2`` is always kept, and ``-1``
    leads the list to carry the sign of each congruence.

    >>> smoothness_base(13290059, 20)
    [-1, 2, 5, 13]
    >>> smoothness_base(9788111, 20)
    [-1, 2, 5, 7, 11, 17]
    """
    sieve = bytearray([1]) * (bound + 1)
    if bound >= 0:
        sieve[0] = 0
    if bound >= 1:
        sieve[1] = 0
    for i in range(2, isqrt(bound) + 1):
        if sieve[i]:
            sieve[i * i : bound + 1 : i] = bytearray(len(range(i * i, bound + 1, i)))
    base = [-1]
    for p in range(2, bound + 1):
        if not sieve[p]:
            continue
        if p == 2 or pow(n % p, (p - 1) // 2, p) in (0, 1):
            base.append(p)
    return base


def _factor_smooth(m: int, primes: Sequence[int]) -> tuple[dict[int, int], int]:
    """Trial-divide positive ``m`` over ``primes``; return ``(exponents, cofactor)``.

    ``cofactor`` is ``1`` exactly when ``m`` is smooth over ``primes``.
    """
    exps: dict[int, int] = {}
    for p in primes:
        while m % p == 0:
            exps[p] = exps.get(p, 0) + 1
            m //= p
    return exps, m


# --------------------------------------------------------------------------- #
#  Collecting relations from the continued fraction of sqrt(k*n).
# --------------------------------------------------------------------------- #

def cfrac_relations(
    n: int,
    *,
    bound: int = 80,
    multiplier: int = 1,
    max_steps: int = 5000,
    want: int | None = None,
) -> list[Relation]:
    """Walk ``sqrt(multiplier*n)`` and collect smooth congruences of squares.

    Runs the integer PQa recurrence, tracking the convergent numerator ``A_i``
    reduced mod ``n``. At each step the next denominator ``Q_{i+1}`` is
    trial-divided over the base; whenever it is smooth a :class:`Relation` for
    ``A_i**2 == (-1)**(i+1) * Q_{i+1} (mod n)`` is recorded. Stops after ``want``
    relations (default ``len(base) + 2``, enough for a null combination) or
    ``max_steps`` PQa steps. ``multiplier*n`` may not equal ``n`` mod anything —
    since ``multiplier*n == 0 (mod n)`` the key congruence still holds mod ``n``.

    >>> cfrac_relations(13290059)[0]
    Relation(index=4, a_mod_n=171341, signed_q=-2050, factors={2: 1, 5: 2, 41: 1, -1: 1})
    """
    base = smoothness_base(n, bound)
    primes = base[1:]  # drop the leading -1
    if want is None:
        want = len(base) + 2

    d = multiplier * n
    root = isqrt(d)
    if root * root == d:  # multiplier*n is a perfect square: the CF terminates
        return []

    p_i, q_i = 0, 1
    a_prev, a_prev2 = 1, 0  # A_{-1} = 1, A_{-2} = 0
    relations: list[Relation] = []
    for i in range(max_steps):
        a = (p_i + root) // q_i
        a_cur = (a * a_prev + a_prev2) % n
        p_next = a * q_i - p_i
        q_next = (d - p_next * p_next) // q_i

        sign = -1 if i % 2 == 0 else 1  # (-1)**(i+1)
        exps, cofactor = _factor_smooth(q_next, primes)
        if cofactor == 1:
            factors = dict(exps)
            if sign < 0:
                factors[-1] = 1
            relations.append(
                Relation(index=i, a_mod_n=a_cur, signed_q=sign * q_next, factors=factors)
            )

        a_prev2, a_prev = a_prev, a_cur
        p_i, q_i = p_next, q_next
        if q_i == 0:  # perfect-square radicand slipped through: stop before /0
            break
        if len(relations) >= want:
            break
    return relations


# --------------------------------------------------------------------------- #
#  Linear algebra over GF(2).
# --------------------------------------------------------------------------- #

def solve_gf2(vectors: list[list[int]]) -> list[list[int]]:
    """All null combinations of ``vectors`` over ``GF(2)``.

    Each returned item is a list of row indices whose vectors XOR to zero — a
    basis of the (left) null space. Standard augmented-identity elimination:
    every row carries a marker of which originals built it, and a row that
    reduces to zero hands back its marker as a dependency. Deterministic.

    >>> solve_gf2([[1, 0], [1, 0], [0, 1]])
    [[0, 1]]
    >>> solve_gf2([[1, 1], [0, 1], [1, 0]])
    [[0, 1, 2]]
    """
    m = len(vectors)
    if m == 0:
        return []
    rows_v = []
    rows_mark = []
    for i, vec in enumerate(vectors):
        bits = 0
        for j, b in enumerate(vec):
            if b & 1:
                bits |= 1 << j
        rows_v.append(bits)
        rows_mark.append(1 << i)

    pivots: dict[int, int] = {}  # column (highest set bit) -> owning row
    results: list[list[int]] = []
    for i in range(m):
        v, mark = rows_v[i], rows_mark[i]
        while v:
            hb = v.bit_length() - 1
            if hb in pivots:
                pr = pivots[hb]
                v ^= rows_v[pr]
                mark ^= rows_mark[pr]
            else:
                pivots[hb] = i
                rows_v[i], rows_mark[i] = v, mark
                break
        else:  # v exhausted to zero: mark is a null combination
            results.append([idx for idx in range(m) if (mark >> idx) & 1])
    return results


def congruence_of_squares(
    n: int, relations: Sequence[Relation], combo: Sequence[int]
) -> tuple[int, int]:
    """Fold a null combination into a single ``X**2 == Y**2 (mod n)``.

    ``X`` is the product of the ``a_mod_n`` over ``combo``; ``Y`` is the square
    root of the combined right-hand side, i.e. the product of ``p**(e/2)`` over
    the summed exponents (which are all even because ``combo`` is null). The
    identity is asserted before returning.

    >>> congruence_of_squares(
    ...     15, [Relation(0, 7, 4, {2: 2}), Relation(1, 8, 4, {2: 2})], [0, 1]
    ... )
    (11, 4)
    """
    x = 1
    totals: dict[int, int] = {}
    for idx in combo:
        rel = relations[idx]
        x = (x * rel.a_mod_n) % n
        for key, e in rel.factors.items():
            totals[key] = totals.get(key, 0) + e
    y = 1
    for key, total in totals.items():
        assert total % 2 == 0, "combo is not a null combination"
        y = (y * pow(key % n, total // 2, n)) % n
    assert (x * x - y * y) % n == 0
    return x, y


# --------------------------------------------------------------------------- #
#  The pipeline.
# --------------------------------------------------------------------------- #

def _exponent_vectors(base: Sequence[int], relations: Sequence[Relation]) -> list[list[int]]:
    """GF(2) exponent vectors of ``relations`` in the column order of ``base``."""
    column = {key: j for j, key in enumerate(base)}
    vectors = []
    for rel in relations:
        vec = [0] * len(base)
        for key, e in rel.factors.items():
            vec[column[key]] = e & 1
        vectors.append(vec)
    return vectors


def _first_split(
    n: int, base: Sequence[int], relations: Sequence[Relation]
) -> tuple[list[int], int, int, tuple[int, int]] | None:
    """First null combination that yields a proper factor: ``(combo, X, Y, (p, q))``."""
    vectors = _exponent_vectors(base, relations)
    for combo in solve_gf2(vectors):
        if not combo:
            continue
        x, y = congruence_of_squares(n, relations, combo)
        for candidate in (gcd(x - y, n), gcd(x + y, n)):
            if 1 < candidate < n:
                other = n // candidate
                lo, hi = (candidate, other) if candidate <= other else (other, candidate)
                return list(combo), x, y, (lo, hi)
    return None


def cfrac_factor(
    n: int, *, bound: int = 80, multiplier: int = 1, max_steps: int = 5000
) -> tuple[int, int]:
    """Factor ``n`` by CFRAC, returning ``(p, q)`` with ``p <= q`` and ``p*q == n``.

    Trivial cases go first: ``n <= 1`` and primes raise :class:`ValueError`, the
    small primes ``2, 3, 5`` are peeled off directly, and a perfect square splits
    as ``(s, s)``. Otherwise it collects relations, folds every null combination
    until a gcd bites, and — when the base multiplier's period is too short to
    give enough smooth denominators — retries with the classic multipliers
    ``3, 5, 7``.

    >>> cfrac_factor(13290059)
    (3119, 4261)
    >>> cfrac_factor(1005973)
    (997, 1009)
    """
    if n <= 1:
        raise ValueError(f"n must be > 1, got {n}")
    for p in (2, 3, 5):
        if n % p == 0 and n != p:
            return (p, n // p)
    root = isqrt(n)
    if root * root == n:
        return (root, root)
    if is_probable_prime(n):
        raise ValueError(f"{n} is prime; there is nothing to factor")

    base = smoothness_base(n, bound)
    tried: set[int] = set()
    for mult in (multiplier, 3, 5, 7):
        if mult in tried:
            continue
        tried.add(mult)
        relations = cfrac_relations(n, bound=bound, multiplier=mult, max_steps=max_steps)
        split = _first_split(n, base, relations)
        if split is not None:
            return split[3]
    raise ValueError(f"CFRAC did not split {n}; increase bound or max_steps")


def cfrac_demo_trace(n: int, *, bound: int = 80, max_steps: int = 5000) -> dict:
    """The pieces a tour stop needs to *tell* the CFRAC story on ``n``.

    Returns the smoothness ``base``, the first few relations as dicts, how many
    were collected, the winning ``combo`` of relation indices, the folded ``X``
    and ``Y``, and the resulting ``factors`` ``(p, q)``.

    >>> trace = cfrac_demo_trace(13290059)
    >>> trace["factors"]
    (3119, 4261)
    >>> trace["base"]
    [-1, 2, 5, 13, 31, 41, 43, 53, 67]
    >>> (trace["X"] ** 2 - trace["Y"] ** 2) % 13290059
    0
    """
    base = smoothness_base(n, bound)
    for mult in (1, 3, 5, 7):
        relations = cfrac_relations(n, bound=bound, multiplier=mult, max_steps=max_steps)
        split = _first_split(n, base, relations)
        if split is not None:
            combo, x, y, factors = split
            return {
                "base": base,
                "relations": [asdict(r) for r in relations[:3]],
                "n_relations": len(relations),
                "combo": combo,
                "X": x,
                "Y": y,
                "factors": factors,
            }
    raise ValueError(f"CFRAC did not split {n}; increase bound or max_steps")


def verify_f7() -> bool:
    """Check that :data:`F7_FACTORS` really multiplies back to :data:`FERMAT_F7`.

    >>> verify_f7()
    True
    """
    return F7_FACTORS[0] * F7_FACTORS[1] == FERMAT_F7
