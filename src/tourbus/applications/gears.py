"""Cutting a gear train to an irrational ratio.

A gear pair can only realize a *rational* ratio ``driver/driven``, and only
one with both teeth counts inside a machinable range — you cannot cut a wheel
with three teeth or three thousand. So approximating a target ratio with a
buildable gear pair is exactly the "best rational approximation with bounded
numerator *and* denominator" problem, and continued fractions solve it.

The canonical example is Christiaan Huygens' planetarium (c. 1680). To model
Saturn's orbital period he needed the ratio of Saturn's year to Earth's,
roughly ``29.425``. The continued fraction hands him ``206/7`` as an early
convergent: a 206-tooth wheel driving a 7-tooth pinion, accurate to about one
part in 9,400, cut from two wheels a clockmaker could actually make.
"""

from __future__ import annotations

from fractions import Fraction

from ..cf.convergents import semiconvergents
from ..cf.expand import cf_from_fraction

__all__ = [
    "HUYGENS_TARGET",
    "gear_ratio",
    "huygens_gear",
]

# Huygens' target: the ratio of Saturn's period to Earth's, as he used it.
# Its continued fraction is [29; 2, 2, 1, 5, ...], and 206/7 is a convergent.
HUYGENS_TARGET = Fraction(77708431, 2640858)


def gear_ratio(
    target: Fraction, *, min_teeth: int = 8, max_teeth: int = 200
) -> tuple[int, int]:
    """Best realizable gear pair ``(driver, driven)`` approximating ``target``.

    Searches the convergents and semiconvergents of ``target`` — the complete
    ladder of best rational approximations — and returns the closest one whose
    teeth counts both lie in ``[min_teeth, max_teeth]``. A candidate fraction
    ``h/k`` may be scaled by a common integer factor (which leaves the ratio,
    and hence the accuracy, untouched) to bring both wheels into range.

    Raises :class:`ValueError` if no pair in range approximates ``target``.

    >>> gear_ratio(Fraction(242190, 1000000))            # a leap-year gear
    (31, 128)
    >>> gear_ratio(Fraction(355, 113))                   # pi, bounded teeth
    (179, 57)
    """
    target = Fraction(target)
    if min_teeth < 1 or max_teeth < min_teeth:
        raise ValueError("need 1 <= min_teeth <= max_teeth")

    terms = list(cf_from_fraction(target))
    best: tuple[int, int] | None = None
    best_err: Fraction | None = None
    for c in semiconvergents(terms):
        h, k = c.numerator, c.denominator
        if h <= 0 or k <= 0:  # skip degenerate / non-positive candidates
            continue
        m = 1
        while m * h <= max_teeth and m * k <= max_teeth:
            p, q = m * h, m * k
            if min_teeth <= p and min_teeth <= q:
                err = abs(target - Fraction(p, q))
                better = (
                    best is None
                    or err < best_err  # type: ignore[operator]
                    or (err == best_err and p + q < best[0] + best[1])
                )
                if better:
                    best, best_err = (p, q), err
            m += 1
    if best is None:
        raise ValueError(
            f"no gear pair with teeth in [{min_teeth}, {max_teeth}] "
            f"approximates {target}"
        )
    return best


def huygens_gear() -> tuple[int, int]:
    """Huygens' planetarium gear for Saturn: the classic ``206/7``.

    The teeth bounds are widened to admit a 7-tooth pinion and a 206-tooth
    wheel — exactly the pair Huygens cut.

    >>> huygens_gear()
    (206, 7)
    """
    return gear_ratio(HUYGENS_TARGET, min_teeth=7, max_teeth=206)
