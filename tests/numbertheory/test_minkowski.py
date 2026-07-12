from fractions import Fraction

from hypothesis import given, settings
from hypothesis import strategies as st

from conftest import st_fractions, st_nonsquare_d
from tourbus.cf.convergents import recurrence
from tourbus.cf.core import CF
from tourbus.numbertheory.minkowski import (
    question_mark,
    question_mark_inverse,
    question_mark_of_quadratic,
)

# Rationals in [0, 1] (denominators bounded so the tests stay quick).
_unit = st_fractions(max_value=400).map(
    lambda f: abs(f) - int(abs(f))
).filter(lambda x: 0 <= x < 1)


def test_anchors():
    assert question_mark(Fraction(1, 2)) == Fraction(1, 2)
    assert question_mark(Fraction(1, 3)) == Fraction(1, 4)
    assert question_mark(Fraction(2, 3)) == Fraction(3, 4)
    assert question_mark(Fraction(1, 1)) == 1
    assert question_mark(Fraction(0, 1)) == 0


def test_integer_shift():
    for n in (-3, -1, 2, 5):
        assert question_mark(Fraction(n) + Fraction(1, 3)) == n + Fraction(1, 4)


def test_fixed_points_and_endpoints():
    assert question_mark(Fraction(0)) == 0
    assert question_mark(Fraction(1)) == 1
    assert question_mark_inverse(Fraction(0)) == 0
    assert question_mark_inverse(Fraction(1)) == 1


def test_inverse_anchors():
    assert question_mark_inverse(Fraction(1, 2)) == Fraction(1, 2)
    assert question_mark_inverse(Fraction(1, 4)) == Fraction(1, 3)
    assert question_mark_inverse(Fraction(3, 4)) == Fraction(2, 3)


def test_quadratic_anchor_golden():
    # 1/phi = (sqrt(5) - 1)/2 maps to exactly 2/3.
    assert question_mark_of_quadratic(-1, 5, 2) == Fraction(2, 3)
    assert question_mark_of_quadratic(0, 2, 1) == Fraction(7, 5)  # sqrt(2)
    assert question_mark_of_quadratic(1, 5, 2) == Fraction(5, 3)  # phi


def test_strictly_increasing_on_sorted_sample():
    pts = sorted({Fraction(p, q) for q in range(1, 25) for p in range(0, q + 1)})
    vals = [question_mark(x) for x in pts]
    assert all(a < b for a, b in zip(vals, vals[1:]))


@given(_unit)
@settings(max_examples=300)
def test_inverse_round_trip(x):
    assert question_mark_inverse(question_mark(x)) == x


@given(_unit)
@settings(max_examples=300)
def test_forward_round_trip_on_dyadic(x):
    # ?(x) is dyadic for rational x, so ? o ?^{-1} recovers it exactly.
    y = question_mark(x)
    assert question_mark(question_mark_inverse(y)) == y


@given(_unit)
@settings(max_examples=200)
def test_image_stays_in_unit_interval(x):
    y = question_mark(x)
    assert 0 <= y <= 1
    assert y.denominator & (y.denominator - 1) == 0  # dyadic


@given(st_nonsquare_d())
@settings(max_examples=60)
def test_quadratic_is_rational_and_consistent(d):
    exact = question_mark_of_quadratic(0, d, 1)
    assert isinstance(exact, Fraction)
    # A high convergent of sqrt(d) is a rational very close to sqrt(d); its
    # question-mark image must converge to the exact quadratic value.
    terms = CF.from_quadratic(0, d, 1).terms(60)
    *_, approx_frac = recurrence(terms)
    assert abs(float(exact) - float(question_mark(approx_frac))) < 1e-9


@given(st_nonsquare_d())
@settings(max_examples=60)
def test_quadratic_with_preperiod(d):
    # (1 + sqrt(d)) / 2 exercises a non-trivial pre-period; still exact/rational.
    val = question_mark_of_quadratic(1, d, 2)
    assert isinstance(val, Fraction)
    terms = CF.from_quadratic(1, d, 2).terms(60)
    *_, approx_frac = recurrence(terms)
    assert abs(float(val) - float(question_mark(approx_frac))) < 1e-9
