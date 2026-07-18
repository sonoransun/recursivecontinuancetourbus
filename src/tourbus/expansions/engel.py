"""Engel expansions: the ceiling-and-affine cousin of the CF machine.

Every ``x`` in ``(0, 1]`` has a unique **Engel expansion**

    x = 1/a_1 + 1/(a_1 a_2) + 1/(a_1 a_2 a_3) + ...

with integers ``a_1 <= a_2 <= a_3 <= ...`` (a *nondecreasing* run of digits).
Where the continued-fraction Engine Room takes the floor of ``x`` and then
reciprocates the remainder, the Engel machine does the mirror image: it takes
the **ceiling of the reciprocal** and then applies an affine step.  Each step is

    a = ceil(1/x),   x <- a*x - 1

emitting the digit ``a`` until ``x`` lands exactly on ``0``.  Because every step
is exact rational arithmetic, a rational ``x`` reaches ``0`` in finitely many
steps: **rational if and only if finite**, the same dichotomy the CF machine
enjoys, reached by the opposite door.

The digits never decrease, and the running product ``a_1 a_2 ... a_k`` in the
denominators grows at least geometrically, so the partial sums race to ``x``.
The showpiece is Euler's number: ``e`` regrouped as an Engel series is nothing
but the factorial series ``sum 1/k!`` with digits ``[1, 1, 2, 3, 4, 5, ...]``.
"""

from __future__ import annotations

from fractions import Fraction
from math import ceil
from typing import Sequence

__all__ = [
    "engel_expansion",
    "engel_eval",
    "engel_partial_sums",
    "engel_e_terms",
]


def engel_expansion(x: Fraction | int) -> list[int]:
    """The Engel digits of ``x`` in ``(0, 1]`` (nondecreasing; finite for rationals).

    Runs the ceiling-and-affine machine ``a = ceil(1/x); x <- a*x - 1`` until the
    remainder is exactly zero.  The emitted digits satisfy ``a_1 <= a_2 <= ...``.

    >>> engel_expansion(Fraction(3, 8))
    [3, 8]
    >>> engel_expansion(Fraction(7, 10))
    [2, 3, 5]
    >>> engel_expansion(Fraction(3, 7))     # 3/7 = 1/3 + 1/12 + 1/84
    [3, 4, 7]
    >>> engel_expansion(Fraction(1, 1))
    [1]
    """
    x = Fraction(x)
    if not (0 < x <= 1):
        raise ValueError(f"Engel expansion is defined for x in (0, 1]; got {x}")
    digits: list[int] = []
    while x != 0:
        # ceil(1/x): 1/x = den/num for the positive Fraction x, taken exactly.
        a = ceil(Fraction(x.denominator, x.numerator))
        digits.append(a)
        x = a * x - 1
    return digits


def engel_eval(digits: Sequence[int]) -> Fraction:
    """Sum the Engel series ``sum_k 1/(a_1 a_2 ... a_k)`` exactly.

    Inverse of :func:`engel_expansion` on the digits it produces.

    >>> engel_eval([3, 8]) == Fraction(3, 8)
    True
    >>> engel_eval([2, 3, 5]) == Fraction(7, 10)
    True
    """
    total = Fraction(0)
    denom = 1  # running product a_1 ... a_k
    for a in digits:
        denom *= a
        total += Fraction(1, denom)
    return total


def engel_partial_sums(digits: Sequence[int]) -> list[Fraction]:
    """The convergent partial sums ``s_k = sum_{j<=k} 1/(a_1 ... a_j)``, exact.

    The final entry equals :func:`engel_eval` of the whole digit list.

    >>> engel_partial_sums([2, 3, 5])
    [Fraction(1, 2), Fraction(2, 3), Fraction(7, 10)]
    """
    sums: list[Fraction] = []
    total = Fraction(0)
    denom = 1
    for a in digits:
        denom *= a
        total += Fraction(1, denom)
        sums.append(total)
    return sums


def engel_e_terms(n: int) -> list[int]:
    """The first ``n`` Engel digits of ``e``: ``[1, 1, 2, 3, 4, 5, ...]``.

    This is exact *by construction*, needing no expansion loop.  The Engel series
    ``e = 1/1 + 1/(1*1) + 1/(1*1*2) + 1/(1*1*2*3) + ...`` is the factorial series
    ``sum_k 1/k!`` regrouped: the running denominator ``a_1 ... a_k`` is exactly
    ``(k-1)!``, forcing ``a_1 = a_2 = 1`` and ``a_k = k - 1`` thereafter.  Hence
    ``engel_eval(engel_e_terms(n))`` is precisely the ``n``-th partial sum of
    ``sum 1/k!``.

    >>> engel_e_terms(6)
    [1, 1, 2, 3, 4, 5]
    >>> engel_eval(engel_e_terms(5)) == Fraction(65, 24)   # 1 + 1 + 1/2 + 1/6 + 1/24
    True
    """
    if n < 0:
        raise ValueError(f"n must be non-negative; got {n}")
    return [1 if i == 0 else i for i in range(n)]
