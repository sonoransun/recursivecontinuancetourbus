from fractions import Fraction

from tourbus.applications.calendar import (
    GREGORIAN,
    TROPICAL_YEAR_FRACTION,
    leap_rule_description,
    tropical_year_convergents,
)


def test_julian_and_jalali_are_convergents():
    convs = tropical_year_convergents()
    assert Fraction(1, 4) in convs      # Julian
    assert Fraction(8, 33) in convs     # Jalali / Khayyam
    assert Fraction(31, 128) in convs   # the astronomer's rule


def test_convergents_default_list():
    got = [str(c) for c in tropical_year_convergents()]
    assert got == ["1/4", "7/29", "8/33", "31/128"]


def test_max_denominator_bounds_the_cycle_length():
    for c in tropical_year_convergents(max_denominator=50):
        assert c.denominator <= 50
    # 31/128 needs a 128-year cycle, so it drops out under a tight bound.
    assert Fraction(31, 128) not in tropical_year_convergents(max_denominator=50)
    assert Fraction(31, 128) in tropical_year_convergents(max_denominator=200)


def test_convergents_actually_approximate_the_year():
    # Each successive convergent is a strictly better leap rule.
    convs = tropical_year_convergents(max_denominator=1000)
    errs = [abs(TROPICAL_YEAR_FRACTION - c) for c in convs]
    assert errs == sorted(errs, reverse=True)


def test_gregorian_is_not_a_convergent():
    # The administrative choice sits off the optimal ladder.
    assert GREGORIAN == Fraction(97, 400)
    assert GREGORIAN not in tropical_year_convergents(max_denominator=1000)


def test_leap_rule_description_phrasing():
    assert leap_rule_description(Fraction(8, 33)) == "8 leap years every 33 years"
    assert leap_rule_description(Fraction(1, 4)) == "1 leap year every 4 years"
    assert leap_rule_description(GREGORIAN) == "97 leap years every 400 years"


def test_gregorian_more_accurate_than_julian():
    julian_err = abs(TROPICAL_YEAR_FRACTION - Fraction(1, 4))
    gregorian_err = abs(TROPICAL_YEAR_FRACTION - GREGORIAN)
    assert gregorian_err < julian_err
