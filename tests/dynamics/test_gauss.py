import math
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from conftest import st_fractions
from tourbus.cf.constants import phi_cf, sqrt_cf
from tourbus.cf.expand import cf_from_fraction
from tourbus.dynamics import (
    gauss_map,
    gauss_orbit,
    khinchin_estimate,
    kuzmin_empirical,
    kuzmin_theoretical,
    levy_estimate,
)


def st_unit_fractions(max_den: int = 5000):
    """Rationals strictly inside ``(0, 1)`` (numerator < denominator)."""
    return st.integers(min_value=2, max_value=max_den).flatmap(
        lambda d: st.integers(min_value=1, max_value=d - 1).map(
            lambda n: Fraction(n, d)
        )
    )


# --- the Gauss map --------------------------------------------------------- #

def test_gauss_map_anchors():
    assert gauss_map(Fraction(1, 3)) == Fraction(0)   # 1/(1/3) = 3, no remainder
    assert gauss_map(Fraction(2, 5)) == Fraction(1, 2)
    assert gauss_map(Fraction(0)) == Fraction(0)


@given(st_unit_fractions())
def test_gauss_map_lands_in_unit_interval(x):
    y = gauss_map(x)
    assert 0 <= y < 1


@given(st_fractions())
def test_gauss_map_returns_a_fractional_part(x):
    # For any non-zero rational, gauss_map is the fractional part of 1/x.
    if x == 0:
        assert gauss_map(x) == 0
        return
    y = gauss_map(x)
    assert 0 <= y < 1
    assert (1 / x - y).denominator == 1  # differs from 1/x by an integer


def test_gauss_orbit_length_and_early_stop():
    orbit = list(gauss_orbit(Fraction(2, 5), steps=10))
    # 2/5 -> 1/2 -> 0, then it stops even though 10 steps were requested.
    assert orbit == [Fraction(2, 5), Fraction(1, 2), Fraction(0)]

    # An orbit that never reaches 0 within the budget yields steps+1 values.
    infinite_seed = 1 / (1 + Fraction(sqrt_cf(2).terms(30)[-1]))  # some messy rational
    got = list(gauss_orbit(infinite_seed, steps=5))
    assert len(got) <= 6


@given(st_unit_fractions())
def test_gauss_orbit_is_the_cf_tail(x):
    """floor(1 / T^j(x)) must reproduce the (j+1)-th partial quotient a_{j+1}."""
    cf = list(cf_from_fraction(x))          # [0, a1, a2, ..., a_m]
    assert cf[0] == 0
    orbit = list(gauss_orbit(x, steps=len(cf)))
    for j, val in enumerate(orbit):
        if val == 0:
            break
        assert math.floor(1 / val) == cf[j + 1]


# --- the Gauss-Kuzmin distribution ----------------------------------------- #

def test_kuzmin_theoretical_anchor():
    assert abs(kuzmin_theoretical(1) - 0.4150375) < 1e-6
    assert abs(kuzmin_theoretical(2) - 0.1699250) < 1e-6


def test_kuzmin_theoretical_is_a_decaying_distribution():
    probs = [kuzmin_theoretical(m) for m in range(1, 5000)]
    # Strictly decreasing and summing to (nearly) 1 over all m >= 1.
    assert all(a > b for a, b in zip(probs, probs[1:]))
    assert abs(sum(probs) - 1.0) < 1e-3


def test_kuzmin_theoretical_rejects_zero():
    with pytest.raises(ValueError):
        kuzmin_theoretical(0)


def test_kuzmin_empirical_counts_and_normalizes():
    emp = kuzmin_empirical([1, 1, 2, 1, 3, 1, 2, 99], max_bucket=4)
    # 99 is above max_bucket and ignored; seven digits remain (four 1s, two 2s, one 3).
    assert emp == {
        1: 4 / 7,
        2: 2 / 7,
        3: 1 / 7,
        4: 0.0,
    }
    assert abs(sum(emp.values()) - 1.0) < 1e-12


def test_kuzmin_empirical_empty_is_all_zero():
    assert kuzmin_empirical([], max_bucket=3) == {1: 0.0, 2: 0.0, 3: 0.0}


# --- Khinchin's and Levy's constants --------------------------------------- #

def test_khinchin_estimate_golden_ratio_is_one():
    # The golden ratio's digits are all 1, so its geometric mean stays at 1.0.
    assert khinchin_estimate(phi_cf().terms(50)) == pytest.approx(1.0)


def test_khinchin_estimate_drops_a0_and_is_geometric():
    # a0 = 0 is dropped; the remaining digits are all 2, so the mean is exactly 2.
    assert khinchin_estimate([0, 2, 2, 2, 2]) == pytest.approx(2.0)


def test_khinchin_estimate_needs_a_tail():
    with pytest.raises(ValueError):
        khinchin_estimate([5])


def test_levy_estimate_is_the_nth_root():
    denoms = [1, 2, 5, 13, 34]
    assert levy_estimate(denoms) == pytest.approx(34 ** (1 / 5))
    assert levy_estimate(denoms) == pytest.approx(math.exp(math.log(34) / 5))


def test_levy_estimate_handles_huge_denominators_without_overflow():
    # A denominator too large to convert to float still works via log-space.
    huge = 10 ** 400
    assert levy_estimate([2, huge]) == pytest.approx(math.exp(math.log(huge) / 2))


@pytest.mark.slow
@pytest.mark.statistical
def test_metric_constants_converge_for_pi():
    from tourbus.cf.constants import pi_cf
    from tourbus.cf.convergents import convergent_pairs

    terms = pi_cf(decimal_digits=400).terms(150)
    # Khinchin's constant K0 ~ 2.6854520 for a generic number like pi.
    assert khinchin_estimate(terms) == pytest.approx(2.685452, abs=0.6)
    denoms = [k for _, k in convergent_pairs(terms) if k > 0]
    # Levy's constant e^(pi^2/(12 ln2)) ~ 3.2758229.
    assert levy_estimate(denoms) == pytest.approx(3.275823, abs=0.3)
