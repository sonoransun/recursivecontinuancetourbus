import itertools
import math
from fractions import Fraction

from tourbus.cf.gcf import brouncker_gcf, gcf_convergents


def test_term_pattern():
    terms = list(itertools.islice(brouncker_gcf(), 5))
    assert [(t.a, t.b) for t in terms] == [(1, 1), (2, 1), (2, 9), (2, 25), (2, 49)]


def test_first_convergents_pinned():
    convs = list(itertools.islice(gcf_convergents(brouncker_gcf()), 4))
    assert convs == [
        Fraction(1),
        Fraction(3, 2),
        Fraction(15, 13),
        Fraction(105, 76),
    ]


def test_four_over_convergents_approach_pi():
    convs = list(itertools.islice(gcf_convergents(brouncker_gcf()), 80))
    errors = [abs(4 / float(c) - math.pi) for c in convs]
    # Convergents alternate about 4/pi, so the error shrinks at every step
    # (slowly -- Brouncker's is famously beautiful, not famously fast).
    assert all(nxt < prev for prev, nxt in zip(errors, errors[1:]))
    assert errors[-1] < 0.03
