"""Why the piano has twelve keys: the fifth is an irrational fraction of an octave.

Stack pure fifths (frequency ratio ``3/2``) and you never land back on a whole
number of octaves (ratio ``2``): that would require ``(3/2)**m == 2**n``, i.e.
``log2(3/2) = n/m`` rational, which it is not. Equal temperament asks for the
best rational ``n/m`` anyway — divide the octave into ``m`` equal steps and put
the fifth at step ``n`` — and "best rational approximation" means the
convergents of ``log2(3/2)``:

    1/2, 3/5, 7/12, 24/41, 31/53, ...

``7/12`` is the twelve-tone scale of the Western keyboard: twelve equal steps,
the fifth at the seventh. ``31/53`` is the near-perfect 53-tone scale prized in
theory. The tiny discrepancy the whole subject wrestles with — that twelve
pure fifths overshoot seven octaves — is the **Pythagorean comma**,
``3**12 / 2**19``, about a quarter of a semitone.

Pitch distance is measured in **cents**: 1200 to the octave, so a ratio ``r``
spans ``1200 * log2(r)`` cents and the just fifth is ``701.955`` cents.
"""

from __future__ import annotations

import math
from fractions import Fraction

from ..cf.constants import log2_ratio_cf
from ..cf.convergents import recurrence

__all__ = [
    "JUST_FIFTH_CENTS",
    "PYTHAGOREAN_COMMA",
    "equal_temperament_convergents",
    "cents_error",
    "pythagorean_comma_cents",
]

# The just (pure) perfect fifth, 3/2, measured in cents: 1200 * log2(3/2).
JUST_FIFTH_CENTS = 1200 * math.log2(3 / 2)

# The Pythagorean comma: twelve pure fifths minus seven octaves,
# (3/2)**12 / 2**7 = 3**12 / 2**19. The gap equal temperament must swallow.
PYTHAGOREAN_COMMA = Fraction(3 ** 12, 2 ** 19)


def equal_temperament_convergents() -> list[Fraction]:
    """The equal-tempered scales, as convergents of ``log2(3/2)``.

    Each convergent ``n/m`` means "divide the octave into ``m`` equal steps,
    place the fifth at step ``n``". Trivial convergents (fewer than two steps
    per octave) are dropped.

    >>> [str(c) for c in equal_temperament_convergents()]
    ['1/2', '3/5', '7/12', '24/41', '31/53']
    >>> Fraction(7, 12) in equal_temperament_convergents()   # the piano
    True
    """
    terms = log2_ratio_cf(3, 2).terms(7)
    return [c for c in recurrence(terms) if c.denominator >= 2]


def cents_error(ratio: Fraction) -> float:
    """Tuning error, in cents, of an equal-tempered fifth versus the just fifth.

    ``ratio`` is a convergent ``n/m`` of ``log2(3/2)``: the equal-tempered
    fifth it defines spans ``(n/m) * 1200`` cents. This returns that minus the
    just fifth's ``701.955`` cents — negative when the tempered fifth is
    slightly flat (as 12-tone equal temperament's is).

    >>> round(cents_error(Fraction(7, 12)), 3)     # 12-TET: famously ~2c flat
    -1.955
    >>> round(cents_error(Fraction(31, 53)), 3)    # 53-TET: nearly perfect
    -0.068
    """
    tempered = float(ratio) * 1200
    return tempered - JUST_FIFTH_CENTS


def pythagorean_comma_cents() -> float:
    """The Pythagorean comma in cents (about a quarter of a semitone).

    >>> round(pythagorean_comma_cents(), 2)
    23.46
    """
    return 1200 * math.log2(float(PYTHAGOREAN_COMMA))
