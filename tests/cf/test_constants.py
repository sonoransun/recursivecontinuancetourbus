from fractions import Fraction

from tourbus.cf.constants import (
    e_cf,
    gamma_cf,
    log2_ratio_cf,
    phi_cf,
    pi_cf,
    pi_cf_via_gcf,
    sqrt_cf,
)
from tourbus.cf.convergents import recurrence


def test_phi_all_ones():
    assert phi_cf().terms(20) == [1] * 20


def test_sqrt_cf():
    assert str(sqrt_cf(2)) == "[1; (2)]"
    assert str(sqrt_cf(7)) == "[2; (1, 1, 1, 4)]"
    assert sqrt_cf(9).is_finite() is True


def test_e_pattern():
    assert e_cf().terms(11) == [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1]
    # spot-check the 2k blocks further out
    terms = e_cf().terms(20)
    assert 8 in terms  # the (1, 8, 1) block appears


def test_pi_known_prefix():
    assert pi_cf().terms(15) == [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1]


def test_pi_convergents_landmarks():
    convs = [str(c) for c in recurrence(pi_cf().terms(5))]
    assert convs[:4] == ["3", "22/7", "333/106", "355/113"]


def test_pi_via_gcf_matches_prefix():
    # The generalized-CF route certifies at least through the famous 292.
    got = pi_cf_via_gcf().terms(5)
    assert got == [3, 7, 15, 1, 292]


def test_gamma_prefix():
    assert gamma_cf().terms(5) == [0, 1, 1, 2, 1]


def test_log2_three_halves_music():
    # Convergents 1/2, 3/5, 7/12, 24/41, 31/53 are the equal-temperament scales.
    convs = [str(c) for c in recurrence(log2_ratio_cf(3, 2).terms(7))]
    assert "7/12" in convs      # 12-tone equal temperament
    assert "24/41" in convs
