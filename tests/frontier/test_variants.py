from fractions import Fraction

from hypothesis import given

from conftest import st_positive_fractions
from tourbus.frontier import variants as V


@given(st_positive_fractions())
def test_nicf_roundtrip(x):
    assert V.eval_nearest_integer_cf(V.nearest_integer_cf(x)) == x


@given(st_positive_fractions())
def test_nicf_partial_quotients_bounded_below(x):
    terms = V.nearest_integer_cf(x)
    # every partial quotient after the first has absolute value >= 2
    assert all(abs(a) >= 2 for a in terms[1:])


@given(st_positive_fractions())
def test_minus_roundtrip(x):
    assert V.eval_minus_cf(V.minus_cf(x)) == x


@given(st_positive_fractions())
def test_minus_partial_quotients_at_least_two(x):
    if x <= 1:
        return
    terms = V.minus_cf(x)
    assert all(a >= 2 for a in terms[1:])


def test_known_expansions():
    assert V.regular_cf(Fraction(415, 93)) == [4, 2, 6, 7]
    assert V.nearest_integer_cf(Fraction(29, 8)) == [4, -3, 3]
    assert V.minus_cf(Fraction(7, 5)) == [2, 2, 3]
