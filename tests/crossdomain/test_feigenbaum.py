"""Tests for period doubling and the Feigenbaum constant."""

import pytest

from tourbus.cf.core import QuadraticSurd
from tourbus.crossdomain import feigenbaum


def test_logistic_fixes_critical_point_at_two():
    # r = 2 sends the critical point x = 1/2 to itself.
    assert feigenbaum.logistic(2.0, 0.5) == 0.5


def test_superstable_R0_is_two():
    assert round(feigenbaum.superstable_parameter(0, lo=1.9, hi=2.1), 6) == 2.0


def test_superstable_R1_is_one_plus_root_five():
    R1 = feigenbaum.superstable_parameter(1, lo=3.1, hi=3.3)
    assert abs(R1 - float(QuadraticSurd.make(1, 1, 5))) < 1e-6


def test_R1_exact_is_a_quadratic_surd():
    surd = feigenbaum.R1_exact()
    assert surd == QuadraticSurd.make(1, 1, 5)
    assert round(float(surd), 6) == 3.236068


def test_ladder_increasing_and_bounded():
    ladder = feigenbaum.superstable_ladder(5)
    assert ladder[0] == 2.0
    assert all(b > a for a, b in zip(ladder, ladder[1:]))
    # Bounded above by the accumulation point r_inf ~ 3.5699.
    assert max(ladder) < 3.5700


def test_critical_orbit_closes_at_superstable():
    ladder = feigenbaum.superstable_ladder(3)
    for level, R in enumerate(ladder):
        orbit = feigenbaum.critical_orbit(R, level)
        assert len(orbit) == 2 ** level
        # The critical orbit returns to 1/2 at a superstable parameter.
        assert abs(orbit[-1] - 0.5) < 1e-6


def test_feigenbaum_delta_in_window():
    assert 4.6 < feigenbaum.feigenbaum_delta(4) < 4.7


@pytest.mark.slow
def test_feigenbaum_delta_converges():
    # A deeper ladder tightens toward the reference constant.
    assert abs(feigenbaum.feigenbaum_delta(7) - feigenbaum.FEIGENBAUM_DELTA) < 5e-3
