"""Ramanujan's continued fractions and nested radicals.

Srinivasa Ramanujan (1887-1920) turned the continued fraction from a tool into
an art form. Two of his signatures live here, each computed on this package's
exact engine wherever the arithmetic stays rational:

* The **Rogers-Ramanujan continued fraction**

  .. math::  R(q) = \\cfrac{q^{1/5}}{1 + \\cfrac{q}{1 + \\cfrac{q^2}{1 + \\cfrac{q^3}{1 + \\dots}}}}

  a *q*-continued fraction (the partial numerators are powers of ``q``, not the
  constant ``1`` of a simple continued fraction). Its convergents are exact
  rationals for any rational ``q``. The miracle Ramanujan sent Hardy in his
  first letter of 1913: at ``q = e^{-2 pi}`` the whole infinite fraction
  collapses to a closed form built from the golden ratio,

  .. math::  R(e^{-2 pi}) = \\sqrt{\\tfrac{5 + \\sqrt 5}{2}} - \\varphi.

* Ramanujan's **nested radical** ``3 = sqrt(1 + 2 sqrt(1 + 3 sqrt(1 + 4 ...)))``,
  a puzzle he posed in the *Journal of the Indian Mathematical Society* (1911)
  that went unanswered, and its general form ``x + 1 = sqrt(1 + x sqrt(1 + (x+1)
  sqrt(...)))``.

The golden ratio threads both, tying this module to Stop 4; the ``q``-series
machinery is the same recurrence continued fractions always are, run one deeper.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import List

__all__ = [
    "rogers_ramanujan_cf",
    "rogers_ramanujan_convergents",
    "rogers_ramanujan_value",
    "rogers_ramanujan_golden",
    "RR_GOLDEN_VALUE",
    "ramanujan_nested_radical",
    "nested_radical_general",
]


def rogers_ramanujan_cf(q: Fraction, n: int) -> Fraction:
    """The ``n``-term convergent of the Rogers-Ramanujan fraction, sans prefactor.

    Returns ``C_n(q)``, the value of the terminating continued fraction

        ``1 / (1 + q / (1 + q^2 / (1 + ... + q^n / 1)))``

    exactly, for any rational ``q``. The full fraction is
    ``R(q) = q**(1/5) * C(q)``; the ``q**(1/5)`` prefactor is irrational and is
    applied only in :func:`rogers_ramanujan_value`.

    >>> from fractions import Fraction
    >>> rogers_ramanujan_cf(Fraction(1, 2), 8)
    Fraction(1611053, 2269355)
    >>> rogers_ramanujan_cf(Fraction(0), 5)   # R(0) part is 1
    Fraction(1, 1)
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    t = Fraction(1)
    for k in range(n, 0, -1):
        t = 1 + q ** k / t
    return 1 / t


def rogers_ramanujan_convergents(q: Fraction, n: int) -> List[Fraction]:
    """The convergents ``C_1(q), C_2(q), ..., C_n(q)`` as a list of exact rationals.

    Successive convergents bracket the limit from alternating sides, so the pair
    ``(C_{k}, C_{k+1})`` is a certified enclosure of ``C(q)``.

    >>> from fractions import Fraction
    >>> cs = rogers_ramanujan_convergents(Fraction(1, 2), 4)
    >>> [str(c) for c in cs]
    ['2/3', '5/7', '22/31', '93/131']
    """
    return [rogers_ramanujan_cf(q, k) for k in range(1, n + 1)]


def rogers_ramanujan_value(q: float, terms: int = 80) -> float:
    """Numeric value of ``R(q) = q**(1/5) * C(q)`` for ``0 <= q < 1``.

    >>> round(rogers_ramanujan_value(0.1), 6)
    0.574114
    """
    if not 0.0 <= q < 1.0:
        raise ValueError("Rogers-Ramanujan needs 0 <= q < 1 for convergence")
    t = 1.0
    for k in range(terms, 0, -1):
        t = 1.0 + q ** k / t
    c = 1.0 / t
    return (q ** 0.2) * c if q > 0 else 0.0


# Ramanujan's 1913 gift to Hardy: the infinite fraction at q = e^{-2 pi} is
# sqrt((5 + sqrt 5) / 2) - phi, a number built entirely from the golden ratio.
RR_GOLDEN_VALUE: float = math.sqrt((5 + math.sqrt(5)) / 2) - (1 + math.sqrt(5)) / 2


def rogers_ramanujan_golden() -> tuple[float, float, float]:
    """Ramanujan's golden identity: ``R(e^{-2 pi})`` two ways, and the gap.

    Returns ``(from_continued_fraction, closed_form, abs_error)``. The closed
    form is :data:`RR_GOLDEN_VALUE`; the continued-fraction value is summed
    directly from ``R(q)`` at ``q = e^{-2 pi}``. They agree to machine precision.

    >>> cf, closed, err = rogers_ramanujan_golden()
    >>> round(closed, 10)
    0.2840790438
    >>> err < 1e-12
    True
    """
    q = math.exp(-2 * math.pi)
    cf = rogers_ramanujan_value(q, terms=40)
    return cf, RR_GOLDEN_VALUE, abs(cf - RR_GOLDEN_VALUE)


def ramanujan_nested_radical(depth: int) -> float:
    """Ramanujan's nested radical, truncated at ``depth`` and converging to 3.

    Evaluates ``sqrt(1 + 2 sqrt(1 + 3 sqrt(1 + 4 sqrt(1 + ...))))`` down to
    ``depth`` layers. Ramanujan's identity (from the general form below with
    ``x = 2``) is that the infinite radical equals exactly ``3``.

    >>> round(ramanujan_nested_radical(30), 9)
    3.0
    >>> ramanujan_nested_radical(0)
    2.0
    """
    if depth < 0:
        raise ValueError("depth must be non-negative")
    # Seed the innermost layer with its own leading term so the truncation
    # sits on the true value; f(n) = sqrt(1 + (n+1) f(n+1)), f(1) = 3.
    t = float(depth + 2)
    for k in range(depth, 0, -1):
        t = math.sqrt(1 + (k + 1) * t)
    return t


def nested_radical_general(x: float, depth: int = 40) -> float:
    """Ramanujan's general identity ``x + 1 = sqrt(1 + x sqrt(1 + (x+1) sqrt(...)))``.

    The nested radical with leading multiplier ``x`` converges to ``x + 1``;
    ``x = 2`` recovers :func:`ramanujan_nested_radical` and the value ``3``.

    >>> round(nested_radical_general(5, 40), 6)
    6.0
    >>> round(nested_radical_general(0, 40), 6)
    1.0
    """
    if depth < 1:
        raise ValueError("depth must be positive")
    t = float(x + depth + 1)
    for k in range(depth - 1, -1, -1):
        t = math.sqrt(1 + (x + k) * t)
    return t
