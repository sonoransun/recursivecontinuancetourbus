from fractions import Fraction
from math import factorial

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tourbus.expansions.engel import (
    engel_e_terms,
    engel_eval,
    engel_expansion,
    engel_partial_sums,
)


@st.composite
def _fracs_0_1_inclusive(draw):
    """Fractions in ``(0, 1]``: 1 <= p <= q <= 2000."""
    q = draw(st.integers(min_value=1, max_value=2000))
    p = draw(st.integers(min_value=1, max_value=q))
    return Fraction(p, q)


def test_pinned_examples():
    assert engel_expansion(Fraction(3, 8)) == [3, 8]
    assert engel_expansion(Fraction(7, 10)) == [2, 3, 5]
    assert engel_expansion(Fraction(3, 7)) == [3, 4, 7]  # 1/3 + 1/12 + 1/84
    assert engel_expansion(Fraction(1, 1)) == [1]


def test_integer_one_is_in_domain():
    # x = 1 is the right endpoint of (0, 1] and must be accepted.
    assert engel_expansion(1) == [1]
    assert engel_eval([1]) == Fraction(1, 1)


def test_eval_inverts_expansion_pinned():
    assert engel_eval([3, 8]) == Fraction(3, 8)
    assert engel_eval([2, 3, 5]) == Fraction(7, 10)


def test_partial_sums_final_equals_eval():
    digits = [2, 3, 5]
    sums = engel_partial_sums(digits)
    assert sums == [Fraction(1, 2), Fraction(2, 3), Fraction(7, 10)]
    assert sums[-1] == engel_eval(digits)


def test_e_terms_prefix():
    assert engel_e_terms(6) == [1, 1, 2, 3, 4, 5]
    assert engel_e_terms(0) == []
    assert engel_e_terms(1) == [1]


def test_e_terms_are_factorial_partial_sums():
    # engel_eval of the first n e-digits is the n-th partial sum of sum 1/k!.
    for n in range(1, 12):
        expected = sum(Fraction(1, factorial(k)) for k in range(n))
        assert engel_eval(engel_e_terms(n)) == expected


def test_e_terms_negative_raises():
    with pytest.raises(ValueError):
        engel_e_terms(-1)


@pytest.mark.parametrize("bad", [Fraction(0), Fraction(-1, 2), Fraction(3, 2), Fraction(5)])
def test_domain_errors(bad):
    with pytest.raises(ValueError, match=r"\(0, 1\]"):
        engel_expansion(bad)


@given(_fracs_0_1_inclusive())
@settings(max_examples=300)
def test_round_trip(x):
    assert engel_eval(engel_expansion(x)) == x


@given(_fracs_0_1_inclusive())
@settings(max_examples=300)
def test_digits_nondecreasing(x):
    digits = engel_expansion(x)
    assert all(a >= 1 for a in digits)
    assert digits == sorted(digits)


@given(_fracs_0_1_inclusive())
@settings(max_examples=200)
def test_partial_sums_increase_to_value(x):
    digits = engel_expansion(x)
    sums = engel_partial_sums(digits)
    assert sums == sorted(sums)  # strictly building up
    assert sums[-1] == x
