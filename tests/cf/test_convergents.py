from fractions import Fraction
from math import gcd

from hypothesis import given

from conftest import st_fractions
from tourbus.cf.convergents import (
    best_approximation,
    best_approximations,
    convergent_pairs,
    recurrence,
    semiconvergents,
)
from tourbus.cf.expand import cf_from_fraction


@given(st_fractions())
def test_convergents_are_reduced(x):
    for h, k in convergent_pairs(cf_from_fraction(x)):
        if k != 0:
            assert gcd(h, k) == 1


@given(st_fractions())
def test_determinant_identity(x):
    pairs = list(convergent_pairs(cf_from_fraction(x)))
    for n in range(1, len(pairs)):
        h_n, k_n = pairs[n]
        h_p, k_p = pairs[n - 1]
        assert h_n * k_p - h_p * k_n == (-1) ** (n - 1)


@given(st_fractions(max_value=5000))
def test_convergents_straddle_and_bound(x):
    pairs = [(h, k) for h, k in convergent_pairs(cf_from_fraction(x)) if k > 0]
    convs = [Fraction(h, k) for h, k in pairs]
    # Error bound |x - h_n/k_n| < 1/(k_n * k_{n+1}).
    for n in range(len(pairs) - 1):
        _, k_n = pairs[n]
        _, k_next = pairs[n + 1]
        assert abs(x - convs[n]) <= Fraction(1, k_n * k_next)


@given(st_fractions(max_value=5000), st_fractions(max_value=200))
def test_best_approximation_matches_limit_denominator(x, cap):
    n = max(1, cap.denominator)
    assert best_approximation(x, n) == Fraction(x).limit_denominator(n)


def test_pi_landmarks():
    from tourbus.cf.constants import pi_cf

    assert best_approximation(pi_cf(), 113) == Fraction(355, 113)
    assert best_approximation(pi_cf(), 100) == Fraction(311, 99)


def test_best_approximations_ladder():
    got = [str(c) for c in best_approximations(Fraction(415, 93), 100)]
    assert got == ["4", "9/2", "58/13", "415/93"]


def test_semiconvergents_include_convergents():
    semis = list(semiconvergents([3, 7]))
    assert semis[0] == Fraction(3)
    assert semis[-1] == Fraction(22, 7)
    # 22/7 is a convergent, so it must appear.
    assert Fraction(22, 7) in semis
