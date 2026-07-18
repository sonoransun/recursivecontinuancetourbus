"""Egyptian fractions: writing a number as a sum of distinct unit fractions.

The scribes of the Rhind Mathematical Papyrus (c. 1550 BCE) had no notation for
a general fraction. They wrote everything except ``2/3`` as a sum of *distinct*
reciprocals of integers — ``3/4`` as ``1/2 + 1/4``, ``2/5`` as ``1/3 + 1/15`` —
and kept elaborate tables to do it. Three thousand years later the question of
how to produce such a sum *algorithmically* is still surprisingly deep.

The workhorse here is the **Fibonacci–Sylvester greedy algorithm**: at each step
take the largest unit fraction that still fits, ``1/ceil(1/x)``, and subtract.
Fibonacci gave it in the *Liber Abaci* (1202); Sylvester (1880) proved it always
terminates, because the numerator of the remainder strictly decreases. The price
is that the denominators can grow **doubly exponentially** — the notorious
``5/121`` needs a five-term expansion whose last denominator has twenty-five
digits, even though ``5/121 = 1/33 + 1/121 + 1/363`` is available in three.

Two famous companions live in the same neighbourhood. **Sylvester's sequence**
``2, 3, 7, 43, ...`` is the greedy expansion of ``1`` itself. And the
**Erdős–Straus conjecture** (1948) — that ``4/n = 1/a + 1/b + 1/c`` is solvable
in positive integers for every ``n >= 2`` — remains open to this day; the
bounded search in :func:`erdos_straus` has never been observed to fail.

Everything is exact :class:`~fractions.Fraction` / integer arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

__all__ = [
    "fibonacci_sylvester",
    "egyptian_eval",
    "sylvester_sequence",
    "erdos_straus",
    "odd_greedy",
]


def fibonacci_sylvester(x: Fraction) -> list[int]:
    """Greedy unit-fraction denominators for ``x`` in ``(0, 1]``, increasing.

    At each step take ``a = ceil(1/x) = (den + num - 1) // num`` and subtract
    ``1/a``; the numerator of the remainder strictly decreases, so the process
    terminates. The denominators come out strictly increasing and distinct.

    The classic cautionary example is ``5/121``, whose greedy expansion explodes
    to five terms with a twenty-five-digit tail, even though the non-greedy
    ``1/33 + 1/121 + 1/363`` says the same thing in three.

    >>> fibonacci_sylvester(Fraction(4, 5))
    [2, 4, 20]
    >>> fibonacci_sylvester(Fraction(3, 4))
    [2, 4]
    >>> fibonacci_sylvester(Fraction(5, 121))[:4]
    [25, 757, 763309, 873960180913]
    >>> egyptian_eval(fibonacci_sylvester(Fraction(5, 121))) == Fraction(5, 121)
    True
    """
    if not 0 < x <= 1:
        raise ValueError("Fibonacci-Sylvester expects x in (0, 1]")
    denoms: list[int] = []
    while x != 0:
        a = (x.denominator + x.numerator - 1) // x.numerator  # ceil(1/x)
        denoms.append(a)
        x -= Fraction(1, a)
    return denoms


def egyptian_eval(denoms: Sequence[int]) -> Fraction:
    """Sum the unit fractions ``1/d`` exactly.

    >>> egyptian_eval([2, 4, 20])
    Fraction(4, 5)
    >>> egyptian_eval([])
    Fraction(0, 1)
    """
    total = Fraction(0)
    for d in denoms:
        total += Fraction(1, d)
    return total


def sylvester_sequence(n: int) -> list[int]:
    """The first ``n`` terms of Sylvester's sequence ``2, 3, 7, 43, 1807, ...``.

    Defined by ``s_1 = 2`` and ``s_{k+1} = s_k**2 - s_k + 1``; equivalently the
    greedy Egyptian expansion of ``1``, since ``1/s_1 + ... + 1/s_k = 1 - 1/(s_{k+1} - 1)``.

    >>> sylvester_sequence(6)
    [2, 3, 7, 43, 1807, 3263443]
    >>> sylvester_sequence(0)
    []
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    seq: list[int] = []
    s = 2
    for _ in range(n):
        seq.append(s)
        s = s * s - s + 1
    return seq


def erdos_straus(n: int) -> tuple[int, int, int] | None:
    """The lexicographically smallest ``(a, b, c)`` with ``4/n = 1/a + 1/b + 1/c``.

    A deterministic bounded search over ``a <= b <= c`` (repeats allowed, so this
    is a *representation* rather than a strict Egyptian fraction). The
    Erdős–Straus conjecture asserts a solution exists for every ``n >= 2``; it is
    unproven, so ``None`` is returned only if the search space is exhausted —
    which has never been observed to happen.

    >>> erdos_straus(5)
    (2, 4, 20)
    >>> erdos_straus(2)
    (1, 2, 2)
    >>> erdos_straus(4)
    (2, 3, 6)
    >>> a, b, c = erdos_straus(101)
    >>> Fraction(1, a) + Fraction(1, b) + Fraction(1, c) == Fraction(4, 101)
    True
    """
    if n < 2:
        raise ValueError("Erdos-Straus is stated for n >= 2")
    target = Fraction(4, n)
    best: tuple[int, int, int] | None = None
    a_lo = -(-n // 4)              # ceil(n/4): smallest a with 1/a <= 4/n
    a_hi = (3 * n) // 4 + 1
    for a in range(a_lo, a_hi + 1):
        r = target - Fraction(1, a)
        if r <= 0:
            continue
        b_lo = max(a, -(-r.denominator // r.numerator))   # max(a, ceil(1/r))
        b_hi = (2 * r.denominator) // r.numerator + 1      # floor(2/r) + 1
        for b in range(b_lo, b_hi + 1):
            c_frac = r - Fraction(1, b)
            if c_frac <= 0:
                continue
            # c_frac must itself be a unit fraction 1/c with c >= b
            if c_frac.numerator == 1 and c_frac.denominator >= b:
                triple = (a, b, c_frac.denominator)
                if best is None or triple < best:
                    best = triple
    return best


def odd_greedy(x: Fraction, *, max_terms: int = 64) -> list[int] | None:
    """Greedy Egyptian expansion restricted to distinct **odd** denominators.

    At each step take the smallest odd denominator that both exceeds the previous
    one and does not overshoot the remainder, then subtract. A sum of odd unit
    fractions has odd denominator, so a finite odd expansion can exist only when
    ``x`` reduces to an odd denominator; for those, this returns increasing odd
    denominators, and ``None`` if ``max_terms`` is reached first.

    Whether this greedy variant *always* terminates on odd-denominator inputs is
    an open problem (Stewart, Breusch): unlike the Fibonacci–Sylvester case there
    is no known monovariant, so the ``max_terms`` guard is a genuine safety net,
    not a formality.

    >>> odd_greedy(Fraction(2, 3))
    [3, 5, 9, 45]
    >>> odd_greedy(Fraction(3, 7))
    [3, 11, 231]
    >>> egyptian_eval(odd_greedy(Fraction(2, 3))) == Fraction(2, 3)
    True
    """
    if x <= 0:
        raise ValueError("odd_greedy expects x > 0")
    denoms: list[int] = []
    last = -1
    while x != 0:
        if len(denoms) >= max_terms:
            return None
        a = (x.denominator + x.numerator - 1) // x.numerator  # ceil(1/x)
        if a <= last:
            a = last + 1
        if a % 2 == 0:
            a += 1  # next odd; only shrinks 1/a further, so 1/a <= x still holds
        denoms.append(a)
        last = a
        x -= Fraction(1, a)
    return denoms
