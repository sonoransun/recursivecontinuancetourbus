"""Exact polynomial arithmetic over the rationals (internal helper).

Polynomials are ``list[Fraction]`` in **descending** degree, so ``[24, 0, 6, 0]``
means ``24 s^3 + 6 s``. This is the polynomial lift of the integer Euclidean
loop in :mod:`tourbus.cf.expand`: the continued-fraction expansions that
synthesize a Cauer ladder or test Routh-Hurwitz stability are polynomial long
division, exactly the way an ordinary continued fraction is integer division.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

Poly = list


def _F(coeffs: Sequence) -> list[Fraction]:
    return [Fraction(c) for c in coeffs]


def trim(p: Sequence) -> list[Fraction]:
    """Drop leading (high-degree) zeros; the zero polynomial becomes ``[0]``.

    >>> trim([0, 0, 4, 0])
    [Fraction(4, 1), Fraction(0, 1)]
    >>> trim([0, 0])
    [Fraction(0, 1)]
    """
    q = _F(p)
    i = 0
    while i < len(q) - 1 and q[i] == 0:
        i += 1
    return q[i:]


def degree(p: Sequence) -> int:
    """Degree of ``p`` (-1 for the zero polynomial)."""
    q = trim(p)
    if len(q) == 1 and q[0] == 0:
        return -1
    return len(q) - 1


def add(a: Sequence, b: Sequence) -> list[Fraction]:
    a, b = _F(a), _F(b)
    n = max(len(a), len(b))
    a = [Fraction(0)] * (n - len(a)) + a
    b = [Fraction(0)] * (n - len(b)) + b
    return trim([x + y for x, y in zip(a, b)])


def sub(a: Sequence, b: Sequence) -> list[Fraction]:
    return add(a, [-x for x in _F(b)])


def mul(a: Sequence, b: Sequence) -> list[Fraction]:
    a, b = _F(a), _F(b)
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out)


def divmod_poly(num: Sequence, den: Sequence) -> tuple[list[Fraction], list[Fraction]]:
    """Exact polynomial long division: return ``(quotient, remainder)``.

    >>> q, r = divmod_poly([24, 0, 6, 0], [12, 0, 1])   # 24s^3+6s = 2s*(12s^2+1) + 4s
    >>> q, r
    ([Fraction(2, 1), Fraction(0, 1)], [Fraction(4, 1), Fraction(0, 1)])
    """
    num = trim(num)
    den = trim(den)
    if degree(den) < 0:
        raise ZeroDivisionError("polynomial division by zero")
    if degree(num) < degree(den):
        return [Fraction(0)], num
    r = list(num)
    dq = degree(num) - degree(den)
    q = [Fraction(0)] * (dq + 1)
    lead = den[0]
    for k in range(dq + 1):
        c = r[k] / lead
        q[k] = c
        for j in range(len(den)):
            r[k + j] -= c * den[j]
    return trim(q), trim(r)


def eval_poly(p: Sequence, x) -> Fraction:
    """Horner evaluation; exact for a rational ``x``.

    >>> eval_poly([1, 0, -3, 0, 1], Fraction(2))   # 16 - 12 + 1
    Fraction(5, 1)
    """
    result = Fraction(0)
    for c in _F(p):
        result = result * x + c
    return result
