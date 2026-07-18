from fractions import Fraction

import pytest
from hypothesis import given

from tourbus_testkit import st_fractions, st_nonsquare_d
from tourbus.cf.convergents import recurrence
from tourbus.cf.expand import cf_from_fraction, cf_from_quadratic


@given(st_fractions())
def test_fraction_roundtrip(x):
    terms = list(cf_from_fraction(x))
    assert list(recurrence(terms))[-1] == x


@given(st_fractions())
def test_canonical_last_term(x):
    terms = list(cf_from_fraction(x))
    if len(terms) > 1:
        assert terms[-1] >= 2  # canonical form avoids a trailing 1


@given(st_fractions(max_value=1000))
def test_partial_quotients_positive(x):
    terms = list(cf_from_fraction(x))
    assert all(a >= 1 for a in terms[1:])  # only a0 may be <= 0


def test_known_expansions():
    assert list(cf_from_fraction(Fraction(415, 93))) == [4, 2, 6, 7]
    assert list(cf_from_fraction(Fraction(-7, 3))) == [-3, 1, 2]
    assert list(cf_from_fraction(5)) == [5]


def test_sqrt_expansions():
    assert cf_from_quadratic(0, 2, 1) == ([1], [2])
    assert cf_from_quadratic(0, 7, 1) == ([2], [1, 1, 1, 4])
    assert cf_from_quadratic(0, 23, 1) == ([4], [1, 3, 1, 8])
    assert cf_from_quadratic(1, 5, 2) == ([], [1])  # golden ratio


@given(st_nonsquare_d())
def test_sqrt_period_palindrome_and_last_term(d):
    from math import isqrt

    pre, period = cf_from_quadratic(0, d, 1)
    assert pre == [isqrt(d)]
    # The period of sqrt(d) ends in 2*a0 and its prefix is a palindrome.
    assert period[-1] == 2 * isqrt(d)
    body = period[:-1]
    assert body == body[::-1]


@given(st_nonsquare_d())
def test_sqrt_value_squares_to_d(d):
    from tourbus.cf.core import CF

    surd = CF.from_quadratic(0, d, 1).value()
    # The surd equals sqrt(d): purely irrational (a == 0) and squares back to d.
    # (b, D) may be a reduced form, e.g. sqrt(8) -> 2*sqrt(2).
    assert surd.a == 0 and surd.b > 0
    assert surd.b * surd.b * surd.D == d
    assert abs(float(surd) ** 2 - d) < 1e-9


def test_perfect_square_is_finite():
    assert cf_from_quadratic(0, 9, 1) == ([3], [])
    assert cf_from_quadratic(0, 16, 1) == ([4], [])


def test_quadratic_normalization_nondivisible():
    # (1 + sqrt(3)) / 1 needs no scaling; check a case where Q does not divide.
    pre, period = cf_from_quadratic(1, 3, 2)  # (1 + sqrt(3))/2
    from tourbus.cf.core import CF

    surd = CF.from_quadratic(1, 3, 2).value()
    assert abs(float(surd) - (1 + 3 ** 0.5) / 2) < 1e-9
