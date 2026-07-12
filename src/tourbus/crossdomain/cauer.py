"""The Cauer ladder: an electrical network is a continued fraction.

The driving-point impedance of a lossless LC ladder is a continued fraction in
the frequency variable ``s``:

    Z(s) = s*L1 + 1/(s*C1 + 1/(s*L2 + 1/(s*C2 + ...))).

Running the continued-fraction expansion of a rational impedance ``Z = N/D``
therefore *synthesizes* the ladder — the partial quotients (each a monomial
``c*s``) are the element values. This is :func:`tourbus.cf.expand.cf_from_fraction`
lifted from integers to polynomials: the same Euclid, one degree at a time.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from . import _poly

__all__ = ["cauer_ladder", "ladder_impedance", "ladder_to_rational"]


def cauer_ladder(num_coeffs: Sequence, den_coeffs: Sequence) -> list[Fraction]:
    """Element values of the Cauer ladder synthesizing ``Z(s) = N/D``.

    Each returned ``c_k`` is the coefficient of the monomial quotient at step k
    (odd k: a series inductor L, even k: a shunt capacitor C).

    >>> cauer_ladder([3, 0, 1], [3, 0])            # (3s^2+1)/(3s) = s + 1/(3s)
    [Fraction(1, 1), Fraction(3, 1)]
    >>> cauer_ladder([24, 0, 6, 0], [12, 0, 1])
    [Fraction(2, 1), Fraction(3, 1), Fraction(4, 1)]
    """
    num = _poly.trim(num_coeffs)
    den = _poly.trim(den_coeffs)
    elements: list[Fraction] = []
    while _poly.degree(den) >= 0 and not (len(den) == 1 and den[0] == 0):
        q, r = _poly.divmod_poly(num, den)
        if _poly.degree(q) != 1 or q[-1] != 0:
            raise ValueError("impedance is not a realizable LC ladder "
                             "(a partial quotient was not a single s-term)")
        elements.append(q[0])          # coefficient of s in the monomial quotient
        num, den = den, r
        if len(r) == 1 and r[0] == 0:
            break
    return elements


def ladder_impedance(elements: Sequence[Fraction], s) -> Fraction:
    """Fold the ladder ``c1*s + 1/(c2*s + 1/(...))`` back to a value at ``s``.

    >>> ladder_impedance([2, 3, 4], Fraction(7))
    Fraction(8274, 589)
    """
    s = Fraction(s)
    value = Fraction(elements[-1]) * s
    for c in reversed(elements[:-1]):
        value = Fraction(c) * s + 1 / value
    return value


def ladder_to_rational(elements: Sequence[Fraction]) -> tuple[list[Fraction], list[Fraction]]:
    """Reverse synthesis: build ``(N, D)`` from element values (round-trip inverse).

    Uses the polynomial convergent recurrence ``h_k = (c_k*s)*h_{k-1} + h_{k-2}``.

    >>> ladder_to_rational([2, 3, 4])
    ([Fraction(24, 1), Fraction(0, 1), Fraction(6, 1), Fraction(0, 1)], [Fraction(12, 1), Fraction(0, 1), Fraction(1, 1)])
    """
    h_prev, h_prev2 = [Fraction(1)], [Fraction(0)]   # h_{-1}=1, h_{-2}=0
    k_prev, k_prev2 = [Fraction(0)], [Fraction(1)]
    for c in elements:
        term = [Fraction(c), Fraction(0)]            # c * s
        h_prev, h_prev2 = _poly.add(_poly.mul(term, h_prev), h_prev2), h_prev
        k_prev, k_prev2 = _poly.add(_poly.mul(term, k_prev), k_prev2), k_prev
    return h_prev, k_prev
