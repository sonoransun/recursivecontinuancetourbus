"""Routh-Hurwitz stability as a continued fraction (control theory).

A real polynomial is Hurwitz-stable — every root in the open left half-plane, so
the system it describes does not blow up — if and only if the continued-fraction
expansion of (its even part) / (its odd part) has **all positive quotients**.
That is the same condition, phrased as a continued fraction, as the classical
"no sign change in the first column of the Routh array." Stability is literally
a continued fraction with positive partial quotients — the polynomial echo of a
real number's regular continued fraction.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from . import _poly

__all__ = ["routh_cf", "is_hurwitz_stable"]


def _split_parity(coeffs: Sequence) -> tuple[list[Fraction], list[Fraction]]:
    """Split a descending-coefficient polynomial into even- and odd-index parts."""
    c = _poly.trim(coeffs)
    # Work by coefficient INDEX parity (position from the leading term).
    even = [c[i] if i % 2 == 0 else Fraction(0) for i in range(len(c))]
    odd = [c[i] if i % 2 == 1 else Fraction(0) for i in range(len(c))]
    return _poly.trim(even), _poly.trim(odd)


def routh_cf(coeffs: Sequence) -> list[Fraction]:
    """The leading quotients ``alpha_i`` (each a term ``alpha_i * s``) of the
    even/odd continued fraction of the polynomial.

    >>> routh_cf([1, 1, 1])            # s^2 + s + 1
    [Fraction(1, 1), Fraction(1, 1)]
    >>> routh_cf([1, 2, 2, 1])         # s^3 + 2s^2 + 2s + 1 (stable)
    [Fraction(1, 2), Fraction(4, 3), Fraction(3, 2)]
    """
    a, b = _split_parity(coeffs)
    quotients: list[Fraction] = []
    while _poly.degree(b) >= 0 and not (len(b) == 1 and b[0] == 0):
        q, r = _poly.divmod_poly(a, b)
        if _poly.degree(q) != 1:
            # a non-monomial quotient signals a zero pivot / imaginary-axis root
            quotients.append(q[0] if q else Fraction(0))
            break
        quotients.append(q[0])
        a, b = b, r
        if len(r) == 1 and r[0] == 0:
            break
    return quotients


def is_hurwitz_stable(coeffs: Sequence) -> bool:
    """True iff the polynomial is Hurwitz-stable (all CF quotients present & > 0).

    >>> is_hurwitz_stable([1, 1, 1])       # s^2+s+1
    True
    >>> is_hurwitz_stable([1, 2, 2, 40])   # a1*a2 < a0*a3 -> unstable
    False
    >>> is_hurwitz_stable([1, 0, 1])       # s^2+1: roots on the imaginary axis
    False
    """
    c = _poly.trim(coeffs)
    n = _poly.degree(c)
    if n < 1:
        return False
    quotients = routh_cf(c)
    return len(quotients) == n and all(q > 0 for q in quotients)
