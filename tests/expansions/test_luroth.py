from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tourbus.expansions.luroth import (
    luroth_eval,
    luroth_expansion,
    pierce_eval,
    pierce_expansion,
    pierce_of_reciprocal_phi,
)

_PHI_DIGITS = [1, 2, 4, 17, 19, 5777, 5779]


@st.composite
def _fracs_0_1_open(draw):
    """Fractions strictly in ``(0, 1)``: 1 <= p < q <= 2000."""
    q = draw(st.integers(min_value=2, max_value=2000))
    p = draw(st.integers(min_value=1, max_value=q - 1))
    return Fraction(p, q)


# --------------------------------------------------------------------------- #
#  Luroth
# --------------------------------------------------------------------------- #

def test_luroth_pinned():
    assert luroth_expansion(Fraction(7, 10)) == ([2], [3])   # eventually periodic
    assert luroth_expansion(Fraction(1, 2)) == ([2], [])     # exact hit terminates
    assert luroth_expansion(Fraction(3, 8)) == ([3, 4], [])


def test_luroth_eval_pinned():
    assert luroth_eval([2], [3]) == Fraction(7, 10)
    assert luroth_eval([2]) == Fraction(1, 2)
    assert luroth_eval([3, 4]) == Fraction(3, 8)


def test_luroth_eval_rejects_small_digit():
    with pytest.raises(ValueError):
        luroth_eval([1])


@pytest.mark.parametrize("bad", [Fraction(0), Fraction(1), Fraction(-1, 3), Fraction(3, 2)])
def test_luroth_domain_errors(bad):
    with pytest.raises(ValueError, match=r"\(0, 1\)"):
        luroth_expansion(bad)


@given(_fracs_0_1_open())
@settings(max_examples=300)
def test_luroth_round_trip_exact(x):
    pre, per = luroth_expansion(x)
    assert luroth_eval(pre, per) == x


@given(_fracs_0_1_open())
@settings(max_examples=300)
def test_luroth_digits_at_least_two(x):
    pre, per = luroth_expansion(x)
    assert all(a >= 2 for a in pre)
    assert all(a >= 2 for a in per)


# --------------------------------------------------------------------------- #
#  Pierce
# --------------------------------------------------------------------------- #

def test_pierce_pinned():
    assert pierce_expansion(Fraction(5, 17)) == [3, 8, 17]
    assert pierce_eval([3, 8, 17]) == Fraction(5, 17)


@pytest.mark.parametrize("bad", [Fraction(0), Fraction(1), Fraction(-1, 4), Fraction(7, 3)])
def test_pierce_domain_errors(bad):
    with pytest.raises(ValueError, match=r"\(0, 1\)"):
        pierce_expansion(bad)


@given(_fracs_0_1_open())
@settings(max_examples=300)
def test_pierce_round_trip_exact(x):
    assert pierce_eval(pierce_expansion(x)) == x


@given(_fracs_0_1_open())
@settings(max_examples=300)
def test_pierce_digits_strictly_increasing(x):
    digits = pierce_expansion(x)
    assert all(b > a for a, b in zip(digits, digits[1:]))
    assert all(a >= 1 for a in digits)


# --------------------------------------------------------------------------- #
#  Pierce digits of 1/phi (exact quadratic-surd arithmetic)
# --------------------------------------------------------------------------- #

def test_pierce_phi_pinned():
    assert pierce_of_reciprocal_phi(7) == _PHI_DIGITS


def test_pierce_phi_prefixes():
    for n in range(len(_PHI_DIGITS) + 1):
        assert pierce_of_reciprocal_phi(n) == _PHI_DIGITS[:n]


def test_pierce_phi_bounds():
    with pytest.raises(ValueError):
        pierce_of_reciprocal_phi(-1)
    with pytest.raises(ValueError, match="doubly exponentially"):
        pierce_of_reciprocal_phi(13)
