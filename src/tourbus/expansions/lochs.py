"""Lochs' theorem: the exchange rate between decimal digits and CF terms.

How much does one continued-fraction term "buy" you in decimal digits? Lochs
(1964) answered it for almost every real number: the first ``n`` decimal digits
determine ``m(n)`` continued-fraction partial quotients with

    m(n) / n  ->  6 * ln2 * ln10 / pi**2  =  0.9702701...

Read the other way -- the direction this module computes in, because it is the
one exact integer arithmetic makes easy -- ``n`` continued-fraction terms pin
about ``n / 0.9703 ~= 1.0306 * n`` certified decimal digits. So one CF term is
worth ~1.03 digits, and one decimal digit is worth ~0.97 CF terms.

The constant is not arbitrary. The entropy of the Gauss map (see
:func:`tourbus.dynamics.gauss.levy_estimate`, whose Levy exponent is the same
``pi**2 / (12 ln 2)``) is ``pi**2 / (6 ln 2)``; dividing the decimal entropy
``ln 10`` by it gives exactly ``6 ln2 ln10 / pi**2``. Two numeral systems, one
dynamical exchange rate.

The measurement is done with *no floating point in the digit counting*:
successive convergents ``C_n`` and ``C_{n+1}`` of the target straddle it, so the
leading decimal digits on which they agree are **certified** digits of the
target. :func:`agreeing_decimals` counts them by pure integer floors of
``x * 10**d``. Only the constant itself and the reported ratios touch ``float``.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

from ..cf.convergents import recurrence

__all__ = [
    "LOCHS_CONSTANT",
    "lochs_constant",
    "agreeing_decimals",
    "lochs_experiment",
    "lochs_ratio",
]

# 6 * ln2 * ln10 / pi**2 -- the decimal-digits-per-CF-term rate of Lochs (1964).
LOCHS_CONSTANT: float = 6 * math.log(2) * math.log(10) / math.pi ** 2


def lochs_constant() -> float:
    """Lochs' constant ``6 * ln2 * ln10 / pi**2``, recomputed from scratch.

    >>> round(lochs_constant(), 7)
    0.9702701
    """
    return 6 * math.log(2) * math.log(10) / math.pi ** 2


def agreeing_decimals(x: Fraction, y: Fraction, *, cap: int = 10_000) -> int:
    """How many leading decimal digits ``x`` and ``y`` share, by integer floors.

    Returns the largest ``d >= 0`` with ``floor(x * 10**d) == floor(y * 10**d)``.
    Because agreeing on ``d`` fractional digits implies agreeing on fewer, this
    is just the count of matching digits after the point -- and it is ``0`` the
    moment the integer parts differ. Computed with exact
    :class:`~fractions.Fraction` floors, never a rounding ``float``. Identical
    inputs agree forever, so the search is capped at ``cap`` digits.

    >>> agreeing_decimals(Fraction(1, 3), Fraction(3333, 10000))   # 0.3333... vs 0.3333
    4
    >>> agreeing_decimals(Fraction(1, 7), Fraction(142, 1000))     # 0.142857... vs 0.142
    3
    >>> agreeing_decimals(Fraction(2), Fraction(3))                # integer parts differ
    0
    """
    x = Fraction(x)
    y = Fraction(y)
    if math.floor(x) != math.floor(y):
        return 0
    d = 0
    p = 10
    while d < cap:
        if math.floor(x * p) != math.floor(y * p):
            return d
        d += 1
        p *= 10
    return d


def lochs_experiment(cf_terms: Sequence[int], *, max_terms: int = 12) -> list[dict]:
    """Measure certified decimals gained per CF term of the number ``cf_terms``.

    For each ``n = 1 .. max_terms`` the convergent ``C_n`` (from the leading
    ``n + 1`` terms) and its successor ``C_{n+1}`` straddle the target, so the
    decimals they agree on are certified digits of the target. Each row is a dict
    with keys ``"n"``, ``"convergent"`` (``C_n`` as a :class:`~fractions.Fraction`),
    ``"digits"`` (certified decimals), and ``"ratio"`` (``digits / n``, tending to
    ``1 / LOCHS_CONSTANT ~= 1.0306``). ``cf_terms`` must supply at least
    ``max_terms + 2`` partial quotients.

    >>> from ..cf.constants import pi_cf
    >>> exp = lochs_experiment(pi_cf().terms(30), max_terms=6)
    >>> [row["digits"] for row in exp]
    [2, 4, 6, 9, 9, 9]
    >>> exp[0]["convergent"]
    Fraction(22, 7)
    """
    if max_terms < 1:
        raise ValueError("max_terms must be >= 1")
    convs = list(recurrence(list(cf_terms)))
    if len(convs) < max_terms + 2:
        raise ValueError(
            f"need at least {max_terms + 2} partial quotients, got {len(convs)}"
        )
    rows: list[dict] = []
    for n in range(1, max_terms + 1):
        digits = agreeing_decimals(convs[n], convs[n + 1])
        rows.append(
            {
                "n": n,
                "convergent": convs[n],
                "digits": digits,
                "ratio": digits / n,
            }
        )
    return rows


def lochs_ratio(cf_terms: Sequence[int], *, max_terms: int = 12) -> float:
    """Certified decimals per CF term after ``max_terms`` terms of ``cf_terms``.

    This is ``digits(max_terms) / max_terms`` in the "terms -> digits" direction:
    for a Lochs-typical number (e.g. pi) it hovers near ``1 / LOCHS_CONSTANT
    ~= 1.0306``, so its reciprocal approaches :data:`LOCHS_CONSTANT` itself. Special
    numbers with small partial quotients (``sqrt(2)``, ``e``) are measure-zero
    exceptions and sit lower.

    >>> from ..cf.constants import pi_cf
    >>> round(lochs_ratio(pi_cf().terms(30), max_terms=20), 4)   # 21 digits / 20 terms
    1.05
    """
    return lochs_experiment(cf_terms, max_terms=max_terms)[-1]["ratio"]
