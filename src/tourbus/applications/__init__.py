"""Applications — the "so what" of continued fractions and recursion.

Where :mod:`tourbus.cf` builds the machinery, this subpackage points it at the
world and shows what it buys you:

* :mod:`~tourbus.applications.calendar` — leap-year rules are the convergents
  of the tropical year (Julian ``1/4``, Jalali ``8/33``, ...).
* :mod:`~tourbus.applications.gears` — cutting a gear train to an irrational
  ratio, the way Huygens built his planetarium (``206/7``).
* :mod:`~tourbus.applications.music` — equal temperament as the convergents of
  ``log2(3/2)``; why the piano has twelve keys.
* :mod:`~tourbus.applications.wiener` — breaking RSA when the private exponent
  is small, using the convergents of the public ``e/n``.
* :mod:`~tourbus.applications.collatz` — the ``3n+1`` map, a recursion as short
  as Euclid's yet still unproven, set against the CF machinery for contrast.

Everything here is standard-library only.
"""

from __future__ import annotations

from .calendar import (
    GREGORIAN,
    tropical_year_convergents,
    leap_rule_description,
)
from .gears import HUYGENS_TARGET, gear_ratio, huygens_gear
from .music import (
    JUST_FIFTH_CENTS,
    PYTHAGOREAN_COMMA,
    equal_temperament_convergents,
    cents_error,
    pythagorean_comma_cents,
)
from .wiener import (
    RSAKey,
    make_safe_key,
    make_vulnerable_key,
    wiener_attack,
)
from .collatz import collatz_orbit, collatz_stats

__all__ = [
    # calendar
    "tropical_year_convergents",
    "leap_rule_description",
    "GREGORIAN",
    # gears
    "gear_ratio",
    "huygens_gear",
    "HUYGENS_TARGET",
    # music
    "equal_temperament_convergents",
    "cents_error",
    "pythagorean_comma_cents",
    "JUST_FIFTH_CENTS",
    "PYTHAGOREAN_COMMA",
    # wiener
    "RSAKey",
    "make_vulnerable_key",
    "make_safe_key",
    "wiener_attack",
    # collatz
    "collatz_orbit",
    "collatz_stats",
]
