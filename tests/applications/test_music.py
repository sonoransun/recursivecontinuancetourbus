from fractions import Fraction

from tourbus.applications.music import (
    JUST_FIFTH_CENTS,
    PYTHAGOREAN_COMMA,
    cents_error,
    equal_temperament_convergents,
    pythagorean_comma_cents,
)


def test_twelve_tone_scale_is_a_convergent():
    convs = equal_temperament_convergents()
    assert Fraction(7, 12) in convs        # the Western keyboard
    assert Fraction(24, 41) in convs
    assert Fraction(31, 53) in convs       # the near-perfect 53-TET


def test_convergent_list_is_the_classic_ladder():
    got = [str(c) for c in equal_temperament_convergents()]
    assert got == ["1/2", "3/5", "7/12", "24/41", "31/53"]


def test_twelve_tet_fifth_is_two_cents_flat():
    assert abs(cents_error(Fraction(7, 12)) + 1.955) < 0.01


def test_just_fifth_constant():
    assert abs(JUST_FIFTH_CENTS - 701.955) < 0.001


def test_better_convergents_have_smaller_error():
    # 41-TET and 53-TET approximate the fifth far better than 12-TET.
    assert abs(cents_error(Fraction(31, 53))) < abs(cents_error(Fraction(7, 12)))
    assert abs(cents_error(Fraction(24, 41))) < abs(cents_error(Fraction(3, 5)))


def test_pythagorean_comma_value():
    assert PYTHAGOREAN_COMMA == Fraction(531441, 524288)
    assert PYTHAGOREAN_COMMA == Fraction(3 ** 12, 2 ** 19)
    assert abs(pythagorean_comma_cents() - 23.46) < 0.01
