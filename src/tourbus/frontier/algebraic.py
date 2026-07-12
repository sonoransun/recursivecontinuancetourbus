"""Continued fractions of algebraic numbers of degree >= 3 — a live open problem.

Quadratic irrationals have periodic continued fractions (Lagrange). Cube roots
do not — and, strikingly, *nobody knows what their partial quotients do*. It is
an open problem whether the partial quotients of ``2^(1/3)`` are bounded; the
numerical evidence says they behave like a "random" real (geometric mean ->
Khinchin's constant, occasional enormous terms), utterly unlike the tidy
periodicity of ``sqrt(d)``.

The plastic number ``rho`` (the real root of ``x^3 = x + 1``, the cubic cousin
of the golden ratio) is a favourite specimen: its expansion coughs up a ``141``
at position 12, from nowhere.

These are computed rigorously with the same interval expander that powers ``pi``:
a high-precision decimal seed becomes a bracket, and only certified partial
quotients are emitted.
"""

from __future__ import annotations

import decimal
from decimal import Decimal
from fractions import Fraction

from ..cf.core import CF, CFKind
from ..cf.expand import cf_from_interval

__all__ = [
    "nth_root_cf",
    "cube_root_cf",
    "plastic_number_cf",
    "supergolden_cf",
    "partial_quotient_stats",
]


def _cf_from_decimal(dstr: str) -> CF:
    """A certified CF from an exact decimal string (last digit treated as +/-1)."""
    center = Fraction(dstr)
    frac_digits = len(dstr.split(".")[1]) if "." in dstr else 0
    eps = Fraction(1, 10 ** frac_digits)
    lo, hi = center - eps, center + eps
    return CF.from_stream(
        lambda: cf_from_interval(lambda _p: (lo, hi)), kind=CFKind.INFINITE
    )


def nth_root_cf(n: int, k: int = 2, *, digits: int = 60) -> CF:
    """The continued fraction of the real ``k``-th root of ``n``.

    >>> nth_root_cf(2, 3).terms(8)      # cube root of 2
    [1, 3, 1, 5, 1, 1, 4, 1]
    """
    with decimal.localcontext() as ctx:
        ctx.prec = digits + 20
        value = Decimal(n) ** (Decimal(1) / Decimal(k))
        dstr = str(+value.quantize(Decimal(10) ** -digits))
    return _cf_from_decimal(dstr)


def cube_root_cf(n: int, *, digits: int = 60) -> CF:
    """The continued fraction of ``n**(1/3)``.

    >>> cube_root_cf(2).terms(6)
    [1, 3, 1, 5, 1, 1]
    """
    return nth_root_cf(n, 3, digits=digits)


def _real_cubic_root(a: int, b: int, c: int, d: int, x0: Decimal, digits: int) -> str:
    """Newton's method for the real root of ``a x^3 + b x^2 + c x + d`` near ``x0``."""
    with decimal.localcontext() as ctx:
        ctx.prec = digits + 25
        A, B, C, D = Decimal(a), Decimal(b), Decimal(c), Decimal(d)
        x = Decimal(x0)
        for _ in range(200):
            f = ((A * x + B) * x + C) * x + D
            fp = (3 * A * x + 2 * B) * x + C
            if fp == 0:
                break
            step = f / fp
            x -= step
            if abs(step) < Decimal(10) ** -(digits + 10):
                break
        return str(+x.quantize(Decimal(10) ** -digits))


def plastic_number_cf(*, digits: int = 60) -> CF:
    """The plastic number ``rho``, real root of ``x^3 = x + 1`` (~1.3247).

    Its continued fraction is famous for a sudden ``141``.

    >>> plastic_number_cf().terms(12)
    [1, 3, 12, 1, 1, 3, 2, 3, 2, 4, 2, 141]
    """
    dstr = _real_cubic_root(1, 0, -1, -1, Decimal("1.3247"), digits)
    return _cf_from_decimal(dstr)


def supergolden_cf(*, digits: int = 60) -> CF:
    """The supergolden ratio, real root of ``x^3 = x^2 + 1`` (~1.4656)."""
    dstr = _real_cubic_root(1, -1, 0, -1, Decimal("1.4656"), digits)
    return _cf_from_decimal(dstr)


def partial_quotient_stats(cf: CF, n: int = 40) -> dict:
    """Statistics of the first ``n`` partial quotients (Khinchin-typicality probe).

    >>> s = partial_quotient_stats(cube_root_cf(2), 30)
    >>> s["count"] == 30 and s["max"] >= 8
    True
    """
    import math

    terms = cf.terms(n + 1)[1:]  # drop a0
    terms = terms[:n]
    geo = math.exp(sum(math.log(a) for a in terms) / len(terms)) if terms else 0.0
    return {
        "count": len(terms),
        "max": max(terms) if terms else 0,
        "geometric_mean": geo,          # tends toward Khinchin's ~2.685 for "typical" x
        "arithmetic_mean": sum(terms) / len(terms) if terms else 0.0,
    }
