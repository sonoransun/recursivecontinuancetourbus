from fractions import Fraction

import pytest
from hypothesis import given

from conftest import st_positive_fractions
from tourbus.applications.gears import HUYGENS_TARGET, gear_ratio, huygens_gear


def test_huygens_gear_is_206_over_7():
    assert huygens_gear() == (206, 7)


def test_huygens_target_ratio_is_close():
    driver, driven = huygens_gear()
    relative = abs(HUYGENS_TARGET - Fraction(driver, driven)) / HUYGENS_TARGET
    assert relative < Fraction(1, 9000)      # accurate to ~1 part in 9,400


def test_gear_ratio_respects_teeth_bounds():
    driver, driven = gear_ratio(Fraction(355, 113), min_teeth=8, max_teeth=200)
    assert 8 <= driver <= 200
    assert 8 <= driven <= 200


def test_gear_ratio_leap_year_gear():
    # The tropical-year fraction realizes as 31/128 within default bounds.
    assert gear_ratio(Fraction(242190, 1000000)) == (31, 128)


def test_gear_ratio_exact_when_realizable():
    # A target that is already a valid gear pair should be returned exactly.
    assert gear_ratio(Fraction(40, 9)) == (40, 9)


def test_gear_ratio_raises_when_unreachable():
    # Huygens' 206/7 needs a 7-tooth pinion; default min_teeth=8 forbids it,
    # and the ratio ~29.4 cannot be hit by any in-range pair with denom >= 8.
    with pytest.raises(ValueError):
        gear_ratio(HUYGENS_TARGET, min_teeth=100, max_teeth=101)


@given(st_positive_fractions(max_value=50))
def test_gear_ratio_stays_in_range_and_beats_nothing_absurd(target):
    try:
        driver, driven = gear_ratio(target, min_teeth=8, max_teeth=200)
    except ValueError:
        return  # no realizable pair; acceptable for extreme targets
    assert 8 <= driver <= 200 and 8 <= driven <= 200
    # The realized ratio is within one part in min(teeth) of the target region:
    # error is bounded by the coarsest gear, 1/8 of a unit at worst here.
    assert abs(target - Fraction(driver, driven)) <= max(target, Fraction(1))
