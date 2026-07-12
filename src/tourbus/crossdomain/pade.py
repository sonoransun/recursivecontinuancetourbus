"""Pade approximants as continued fractions (analysis / numerics).

The C-fraction (Thiele/Viscovatov) expansion of a power series

    f(x) = a0 + a1*x/(1 + a2*x/(1 + a3*x/(1 + ...)))

has convergents equal to the Pade approximants of ``f`` — the best rational
approximations of a series, exactly as the convergents of Stop 3 are the best
rational approximations of a number. Truncating the continued fraction *resums*
a series (even a divergent one) into a rational function. The convergent
recurrence here is the same three-term machine as :mod:`tourbus.cf.convergents`,
with polynomial entries.

Coefficient lists are **ascending** here (``[1, 0, -3]`` = ``1 - 3x^2``), to match
the power series they come from.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

__all__ = ["series_to_cfrac", "pade_from_cfrac", "pade"]


def _padd(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    n = max(len(a), len(b))
    a = a + [Fraction(0)] * (n - len(a))
    b = b + [Fraction(0)] * (n - len(b))
    return [x + y for x, y in zip(a, b)]


def _pmul(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def _recip(series: list[Fraction], length: int) -> list[Fraction]:
    """Power-series reciprocal ``1/series`` truncated to ``length`` terms."""
    h = [Fraction(0)] * length
    h[0] = 1 / series[0]
    for n in range(1, length):
        s = Fraction(0)
        for i in range(1, n + 1):
            if i < len(series):
                s += series[i] * h[n - i]
        h[n] = -s / series[0]
    return h


def series_to_cfrac(taylor_coeffs: Sequence) -> list[Fraction]:
    """The regular C-fraction coefficients ``a_k`` of a power series (exact).

    >>> from math import factorial
    >>> exp = [Fraction(1, factorial(k)) for k in range(7)]
    >>> series_to_cfrac(exp)
    [Fraction(1, 1), Fraction(1, 1), Fraction(-1, 2), Fraction(1, 6), Fraction(-1, 6), Fraction(1, 10), Fraction(-1, 10)]
    """
    c = [Fraction(x) for x in taylor_coeffs]
    alphas = [c[0]]
    g = c[1:]                                  # (f - a0)/x
    while g and any(t != 0 for t in g):
        a = g[0]
        alphas.append(a)
        if a == 0:
            break
        recip = _recip(g, len(g))
        D = [a * t for t in recip]             # a_k / g  (constant term == 1)
        g = D[1:]                              # (D - 1)/x
    return alphas


def pade_from_cfrac(alphas: Sequence, n: int) -> tuple[list[Fraction], list[Fraction]]:
    """The ``n``-th convergent ``(num, den)`` of the C-fraction (ascending coeffs).

    >>> from math import factorial
    >>> exp = [Fraction(1, factorial(k)) for k in range(7)]
    >>> pade_from_cfrac(series_to_cfrac(exp), 2)     # [1/1] Pade of e^x
    ([Fraction(1, 1), Fraction(1, 2)], [Fraction(1, 1), Fraction(-1, 2)])
    """
    alphas = [Fraction(a) for a in alphas]
    A_prev2, A_prev = [Fraction(1)], [alphas[0]]      # A_{-1}=1, A_0=a0
    B_prev2, B_prev = [Fraction(0)], [Fraction(1)]    # B_{-1}=0, B_0=1
    for k in range(1, n + 1):
        term = [Fraction(0), alphas[k]]               # a_k * x
        A = _padd(A_prev, _pmul(term, A_prev2))
        B = _padd(B_prev, _pmul(term, B_prev2))
        A_prev2, A_prev = A_prev, A
        B_prev2, B_prev = B_prev, B
    # strip trailing zeros
    def _trim(p):
        while len(p) > 1 and p[-1] == 0:
            p = p[:-1]
        return p
    return _trim(A_prev), _trim(B_prev)


def pade(taylor_coeffs: Sequence, m: int, n: int) -> tuple[list[Fraction], list[Fraction]]:
    """The ``[m/n]`` Pade approximant of a power series (ascending coeffs).

    >>> from math import factorial
    >>> exp = [Fraction(1, factorial(k)) for k in range(7)]
    >>> pade(exp, 2, 2)          # [2/2] Pade of e^x
    ([Fraction(1, 1), Fraction(1, 2), Fraction(1, 12)], [Fraction(1, 1), Fraction(-1, 2), Fraction(1, 12)])
    """
    return pade_from_cfrac(series_to_cfrac(taylor_coeffs), m + n)
