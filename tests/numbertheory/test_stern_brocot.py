from fractions import Fraction
from math import gcd

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from tourbus_testkit import st_fractions
from tourbus.numbertheory.stern_brocot import (
    calkin_wilf,
    farey,
    farey_length,
    fusc,
    mediant,
    path_to_rational,
    rational_to_path,
    stern_brocot_bfs,
)

_positive = st_fractions(max_value=2000).map(abs).filter(lambda x: x > 0)


def test_farey_five():
    assert list(farey(5)) == [
        Fraction(0, 1), Fraction(1, 5), Fraction(1, 4), Fraction(1, 3),
        Fraction(2, 5), Fraction(1, 2), Fraction(3, 5), Fraction(2, 3),
        Fraction(3, 4), Fraction(4, 5), Fraction(1, 1),
    ]


def test_farey_length_anchor():
    assert farey_length(7) == 19
    for n in range(1, 40):
        assert farey_length(n) == len(list(farey(n)))


def test_fusc_prefix():
    assert [fusc(n) for n in range(10)] == [0, 1, 1, 2, 1, 3, 2, 3, 1, 4]


def test_calkin_wilf_prefix():
    assert list(calkin_wilf(6)) == [
        Fraction(1, 1), Fraction(1, 2), Fraction(2, 1),
        Fraction(1, 3), Fraction(3, 2), Fraction(2, 3),
    ]


def test_calkin_wilf_matches_fusc():
    got = list(calkin_wilf(40))
    for i, x in enumerate(got):
        assert x == Fraction(fusc(i + 1), fusc(i + 2))


def test_root_and_mediant():
    assert rational_to_path(Fraction(1, 1)) == ""
    assert path_to_rational("") == Fraction(1, 1)
    assert mediant(Fraction(0, 1), Fraction(1, 1)) == Fraction(1, 2)


def test_stern_brocot_bfs_levels():
    assert list(stern_brocot_bfs(0)) == []
    assert list(stern_brocot_bfs(1)) == [Fraction(1, 1)]
    assert list(stern_brocot_bfs(3)) == [
        Fraction(1, 1), Fraction(1, 2), Fraction(2, 1),
        Fraction(1, 3), Fraction(2, 3), Fraction(3, 2), Fraction(3, 1),
    ]


@given(_positive)
@settings(max_examples=300)
def test_path_round_trip(x):
    assert path_to_rational(rational_to_path(x)) == x


@given(st.integers(min_value=1, max_value=80))
@settings(max_examples=60)
def test_farey_neighbours_unimodular(n):
    seq = list(farey(n))
    for a, b in zip(seq, seq[1:]):
        # a/b < c/d neighbours satisfy b*c - a*d == 1
        assert b.numerator * a.denominator - a.numerator * b.denominator == 1
    assert seq[0] == Fraction(0, 1) and seq[-1] == Fraction(1, 1)


@given(st.integers(min_value=1, max_value=5000))
@settings(max_examples=200)
def test_fusc_recurrences(n):
    assert fusc(2 * n) == fusc(n)
    assert fusc(2 * n + 1) == fusc(n) + fusc(n + 1)


@given(st.integers(min_value=1, max_value=200))
@settings(max_examples=100)
def test_calkin_wilf_terms_are_reduced(limit):
    for x in calkin_wilf(limit):
        assert gcd(x.numerator, x.denominator) == 1
        assert x > 0


@given(_positive, _positive)
@settings(max_examples=100)
def test_mediant_between_parents(a, b):
    assume(a != b)
    lo, hi = min(a, b), max(a, b)
    m = mediant(lo, hi)
    assert lo < m < hi
