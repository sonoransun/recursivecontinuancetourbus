from fractions import Fraction

from hypothesis import given
from hypothesis import strategies as st

from tourbus_testkit import st_positive_fractions
from tourbus.frontier.continuants import (
    continuant,
    continuant_euler,
    convergent_via_continuants,
)
from tourbus.cf.convergents import convergent_pairs
from tourbus.cf.expand import cf_from_fraction

_terms = st.lists(st.integers(min_value=1, max_value=12), min_size=0, max_size=9)


@given(_terms)
def test_euler_rule_matches_recurrence(seq):
    assert continuant(seq) == continuant_euler(seq)


@given(_terms)
def test_palindrome_identity(seq):
    assert continuant(seq) == continuant(list(reversed(seq)))


def test_all_ones_is_fibonacci():
    # K(1,...,1) with n ones is F_{n+1}
    fib = [1, 1]
    for _ in range(12):
        fib.append(fib[-1] + fib[-2])
    for n in range(1, 12):
        assert continuant([1] * n) == fib[n]


@given(st_positive_fractions())
def test_convergents_are_continuants(x):
    terms = list(cf_from_fraction(x))
    p, q = convergent_via_continuants(terms)
    hk = list(convergent_pairs(terms))
    assert (p, q) == hk[-1]
