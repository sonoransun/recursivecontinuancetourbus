"""Leap-year rules are convergents of the tropical year.

A tropical year is not a whole number of days: it runs about ``365.2422``
days. The fractional part ``0.2422`` is *why* calendars need leap years at
all, and the successive convergents of its continued fraction are exactly the
historical intercalation schemes:

* ``1/4``    — one leap day every 4 years (the **Julian** calendar).
* ``8/33``   — eight leap days every 33 years (the **Jalali / Khayyam** rule,
  the most accurate simple scheme ever put into civil use).
* ``31/128`` — the astronomer's favourite: an error of under one day in
  100,000 years.

Each convergent is the *best* leap-year rule available for its cycle length,
which is the whole point of convergents. The modern **Gregorian** rule
``97/400`` is deliberately *not* a convergent: 400 is administratively tidy
(century years, divisible-by-400 exceptions) at a small cost in accuracy. That
tension between the mathematically optimal and the humanly convenient is the
lesson of this module.
"""

from __future__ import annotations

from fractions import Fraction

from ..cf.convergents import recurrence
from ..cf.expand import cf_from_fraction

__all__ = [
    "TROPICAL_YEAR_FRACTION",
    "GREGORIAN",
    "tropical_year_convergents",
    "leap_rule_description",
]

# The fractional part of the tropical year in days (365.242190...). Held as an
# exact rational so the continued fraction is reproducible to the last term.
TROPICAL_YEAR_FRACTION = Fraction(242190, 1000000)

# The Gregorian rule: 97 leap years every 400. NOT a convergent of the tropical
# year — a deliberate administrative choice (see the module docstring).
GREGORIAN = Fraction(97, 400)


def tropical_year_convergents(*, max_denominator: int = 500) -> list[Fraction]:
    """The leap-year rules hidden in the tropical year, as convergents.

    Returns the convergents of :data:`TROPICAL_YEAR_FRACTION` whose denominator
    (the cycle length in years) is at most ``max_denominator``. The leading
    ``0/1`` convergent is dropped: "0 leap years" is not a calendar.

    >>> [str(c) for c in tropical_year_convergents()]
    ['1/4', '7/29', '8/33', '31/128']
    >>> Fraction(1, 4) in tropical_year_convergents()      # Julian
    True
    >>> Fraction(8, 33) in tropical_year_convergents()     # Jalali / Khayyam
    True
    >>> GREGORIAN in tropical_year_convergents(max_denominator=1000)
    False
    """
    if max_denominator < 1:
        raise ValueError("max_denominator must be >= 1")
    terms = cf_from_fraction(TROPICAL_YEAR_FRACTION)
    out: list[Fraction] = []
    for c in recurrence(terms):
        if c.denominator > max_denominator:
            break
        if c == 0:  # the [0; ...] head convergent: not a leap-year rule
            continue
        out.append(c)
    return out


def leap_rule_description(frac: Fraction) -> str:
    """A human phrasing of a leap-year rule ``leap/cycle``.

    >>> leap_rule_description(Fraction(1, 4))
    '1 leap year every 4 years'
    >>> leap_rule_description(Fraction(8, 33))
    '8 leap years every 33 years'
    >>> leap_rule_description(GREGORIAN)
    '97 leap years every 400 years'
    """
    leap = frac.numerator
    cycle = frac.denominator
    year_word = "year" if leap == 1 else "years"
    return f"{leap} leap {year_word} every {cycle} years"
