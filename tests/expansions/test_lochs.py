import math
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tourbus.cf.constants import pi_cf
from tourbus.expansions.lochs import (
    LOCHS_CONSTANT,
    agreeing_decimals,
    lochs_constant,
    lochs_experiment,
    lochs_ratio,
)

# Rationals strictly inside (0, 1): a / (a + b) with a, b >= 1.
_unit = st.builds(
    lambda a, b: Fraction(a, a + b),
    st.integers(min_value=1, max_value=2000),
    st.integers(min_value=1, max_value=2000),
)

# Certify pi's partial quotients once (200 decimal digits pins well past 40 terms,
# and matches the 1000-digit default) so the individual tests do no pi arithmetic.
PI_TERMS = pi_cf(decimal_digits=200).terms(40)


def test_constant():
    assert round(LOCHS_CONSTANT, 7) == 0.9702701
    assert lochs_constant() == LOCHS_CONSTANT


def test_agreeing_pins():
    assert agreeing_decimals(Fraction(1, 3), Fraction(3333, 10000)) == 4
    assert agreeing_decimals(Fraction(1, 7), Fraction(142, 1000)) == 3
    assert agreeing_decimals(Fraction(22, 7), Fraction(333, 106)) == 2
    assert agreeing_decimals(Fraction(2), Fraction(3)) == 0            # integer parts differ
    assert agreeing_decimals(Fraction(5, 7), Fraction(5, 7), cap=50) == 50   # identical -> cap


@given(_unit, _unit)
@settings(max_examples=200)
def test_agreeing_property(x, y):
    # Small cap: identical draws would otherwise loop to the default 10000 with
    # astronomically large powers of ten. Fractions of denominator <= 4000 differ
    # within a handful of digits, so 60 never truncates a genuine disagreement.
    d = agreeing_decimals(x, y, cap=60)
    assert d >= 0
    assert agreeing_decimals(y, x, cap=60) == d
    # Both live in (0, 1), so integer parts match: the claimed digits really agree,
    assert math.floor(x * 10 ** d) == math.floor(y * 10 ** d)
    # and one digit further they part ways.
    if x != y:
        assert math.floor(x * 10 ** (d + 1)) != math.floor(y * 10 ** (d + 1))


def test_experiment_structure():
    exp = lochs_experiment(PI_TERMS, max_terms=6)
    assert [row["digits"] for row in exp] == [2, 4, 6, 9, 9, 9]
    assert exp[0]["convergent"] == Fraction(22, 7)
    assert exp[0]["n"] == 1
    assert set(exp[0]) == {"n", "convergent", "digits", "ratio"}
    assert all(row["ratio"] == row["digits"] / row["n"] for row in exp)


def test_ratio_band_pi():
    # A Lochs-typical number lands its terms->digits ratio near 1/0.9703 ~= 1.03.
    r = lochs_ratio(PI_TERMS, max_terms=12)
    assert 0.8 <= r <= 1.3


def test_reciprocal_recovers_constant_pi():
    r = lochs_ratio(PI_TERMS, max_terms=20)
    assert abs(1 / r - LOCHS_CONSTANT) < 0.15


def test_digit_counts_monotone_pi():
    exp = lochs_experiment(PI_TERMS, max_terms=25)
    counts = [row["digits"] for row in exp]
    assert all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1))


def test_too_few_terms_raises():
    with pytest.raises(ValueError):
        lochs_experiment([3, 7, 15, 1], max_terms=12)
    with pytest.raises(ValueError):
        lochs_experiment(PI_TERMS, max_terms=0)
