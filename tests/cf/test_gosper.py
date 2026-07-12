from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from conftest import st_fractions
from tourbus.cf.constants import sqrt_cf
from tourbus.cf.core import CF
from tourbus.cf import gosper
from tourbus.cf.gosper import homographic


def _cf(x):
    return CF.from_fraction(Fraction(x))


@given(st_fractions(max_value=500), st_fractions(max_value=500))
@settings(max_examples=200)
def test_add_matches_fraction(x, y):
    assert gosper.add(_cf(x), _cf(y)).value() == x + y


@given(st_fractions(max_value=500), st_fractions(max_value=500))
@settings(max_examples=200)
def test_sub_matches_fraction(x, y):
    assert gosper.sub(_cf(x), _cf(y)).value() == x - y


@given(st_fractions(max_value=500), st_fractions(max_value=500))
@settings(max_examples=200)
def test_mul_matches_fraction(x, y):
    assert gosper.mul(_cf(x), _cf(y)).value() == x * y


@given(st_fractions(max_value=500), st_fractions(max_value=500).filter(lambda f: f != 0))
@settings(max_examples=200)
def test_div_matches_fraction(x, y):
    assert gosper.div(_cf(x), _cf(y)).value() == x / y


@given(
    st_fractions(max_value=200),
    st.integers(min_value=-20, max_value=20),
    st.integers(min_value=-20, max_value=20),
    st.integers(min_value=-20, max_value=20),
    st.integers(min_value=-20, max_value=20),
)
@settings(max_examples=200)
def test_homographic_matches_fraction(x, a, b, c, d):
    if c * x + d == 0:
        return
    expected = (a * x + b) / (c * x + d)
    from tourbus.cf.core import CFKind

    got = CF.from_stream(
        lambda: homographic(iter(_cf(x)), (a, b, c, d)), kind=CFKind.FINITE
    ).value()
    assert got == expected


def test_silver_ratio_is_all_twos():
    # 1 + sqrt(2) = [2; 2, 2, 2, ...]
    got = gosper.affine(sqrt_cf(2), 1, 1).terms(10)
    assert got == [2] * 10


def test_sqrt2_plus_sqrt3_prefix():
    got = gosper.add(sqrt_cf(2), sqrt_cf(3)).terms(6)
    # sqrt(2)+sqrt(3) = 3.146264... -> [3; 6, 1, 5, 7, 1, ...]
    assert got[:3] == [3, 6, 1]


def test_reciprocal():
    got = gosper.reciprocal(_cf(Fraction(7, 3))).value()
    assert got == Fraction(3, 7)


def test_affine_rational_coeffs():
    got = gosper.affine(_cf(Fraction(5, 4)), Fraction(2, 3), Fraction(1, 6)).value()
    assert got == Fraction(2, 3) * Fraction(5, 4) + Fraction(1, 6)
