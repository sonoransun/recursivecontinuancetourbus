"""Other ways to unfold a number: nearest-integer and "minus" continued fractions.

The regular continued fraction is not the only one. Two fringe cousins:

* The **nearest-integer continued fraction (NICF)** rounds to the *closest*
  integer at each step instead of taking the floor, allowing negative partial
  quotients with ``|a_i| >= 2``. It converges faster — fewer terms for the same
  accuracy — and is the expansion Gauss actually preferred.
* The **minus (Hirzebruch-Jung) continued fraction** writes
  ``a_0 - 1/(a_1 - 1/(a_2 - ...))`` with every ``a_i >= 2``. It is the language
  in which algebraic geometers resolve cyclic quotient singularities: the ``a_i``
  are the self-intersection numbers of the exceptional curves.

Both are exact on rationals and evaluate back to the number you started with.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

from ..cf.expand import cf_from_fraction

__all__ = [
    "regular_cf",
    "nearest_integer_cf",
    "minus_cf",
    "eval_regular_cf",
    "eval_nearest_integer_cf",
    "eval_minus_cf",
]


def regular_cf(x: Fraction | int) -> list[int]:
    """The ordinary (floor-based) continued fraction, for side-by-side comparison.

    >>> regular_cf(Fraction(415, 93))
    [4, 2, 6, 7]
    """
    return list(cf_from_fraction(Fraction(x)))


def nearest_integer_cf(x: Fraction | int) -> list[int]:
    """The nearest-integer continued fraction: signed integers with ``|a_i| >= 2``.

    Represents ``x = a_0 + 1/(a_1 + 1/(a_2 + ...))`` where each ``a_i`` is the
    integer closest to the running value (so the remainders shrink fastest);
    rounding up rather than down is what introduces the negative quotients.

    >>> nearest_integer_cf(Fraction(29, 8))       # 3.625 rounds up to 4
    [4, -3, 3]
    >>> eval_nearest_integer_cf(nearest_integer_cf(Fraction(29, 8)))
    Fraction(29, 8)
    """
    x = Fraction(x)
    terms: list[int] = []
    while True:
        a = math.floor(x + Fraction(1, 2))  # nearest integer (ties round down)
        terms.append(a)
        frac = x - a
        if frac == 0:
            break
        x = 1 / frac
    return terms


def minus_cf(x: Fraction | int) -> list[int]:
    """The minus / Hirzebruch-Jung continued fraction: all ``a_i >= 2`` (for i>=1).

    Represents ``x = a_0 - 1/(a_1 - 1/(a_2 - ...))``.

    >>> minus_cf(Fraction(7, 5))
    [2, 2, 3]
    >>> eval_minus_cf(minus_cf(Fraction(7, 5)))
    Fraction(7, 5)
    """
    x = Fraction(x)
    terms: list[int] = []
    while True:
        a = math.ceil(x)
        terms.append(a)
        d = a - x
        if d == 0:
            break
        x = 1 / d
    return terms


def eval_regular_cf(terms: Sequence[int]) -> Fraction:
    """Fold a regular continued fraction back to a Fraction."""
    value = Fraction(terms[-1])
    for a in reversed(terms[:-1]):
        value = a + 1 / value
    return value


def eval_nearest_integer_cf(terms: Sequence[int]) -> Fraction:
    """Fold an NICF (signed ``+`` form) back to a Fraction."""
    value = Fraction(terms[-1])
    for a in reversed(terms[:-1]):
        value = a + 1 / value
    return value


def eval_minus_cf(terms: Sequence[int]) -> Fraction:
    """Fold a minus continued fraction (``a_i - 1/...``) back to a Fraction."""
    value = Fraction(terms[-1])
    for a in reversed(terms[:-1]):
        value = a - 1 / value
    return value
