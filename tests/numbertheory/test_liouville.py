from fractions import Fraction
from math import factorial

import pytest

from tourbus.numbertheory.liouville import (
    irrationality_measure_witness,
    liouville_cf_terms,
    liouville_inequality_check,
    liouville_inequality_report,
    liouville_tail_bound,
    liouville_truncation,
    partial_quotient_peaks,
)


# --------------------------------------------------------------------------- #
#  Truncation and tail bound: exactness, denominators, monotone nesting.
# --------------------------------------------------------------------------- #

def test_truncation_exact_values():
    assert liouville_truncation(1) == Fraction(1, 10)
    assert liouville_truncation(2) == Fraction(11, 100)
    assert liouville_truncation(3) == Fraction(110001, 1_000_000)
    assert liouville_truncation(2, base=2) == Fraction(3, 4)


def test_truncation_denominator_is_base_factorial():
    for k in (1, 2, 3):
        assert liouville_truncation(k).denominator == 10 ** factorial(k)


def test_tail_bound_exact_and_shrinking():
    assert liouville_tail_bound(3) == 2 * Fraction(1, 10 ** factorial(4))
    assert liouville_tail_bound(1, base=2) == Fraction(1, 2)
    # monotone in k: truncation climbs, tail bound collapses.
    for k in range(1, 4):
        assert liouville_truncation(k) < liouville_truncation(k + 1)
        assert liouville_tail_bound(k) > liouville_tail_bound(k + 1)


def test_tail_bound_dominates_the_real_tail():
    # The bound must sit above the actual discarded mass. Compare against several
    # further real terms (truncation(k+3) - truncation(k) < bound), and confirm
    # it exceeds the single first omitted term (a sanity floor).
    for k in range(1, 4):
        first_omitted = liouville_truncation(k + 1) - liouville_truncation(k)
        accumulated = liouville_truncation(k + 3) - liouville_truncation(k)
        assert 0 < first_omitted <= accumulated < liouville_tail_bound(k)


def test_bracket_is_nested():
    # Each (truncation, truncation+tail) bracket contains the next, so they all
    # trap the same real number L.
    for k in range(1, 4):
        lo_k, hi_k = liouville_truncation(k), liouville_truncation(k) + liouville_tail_bound(k)
        lo_n = liouville_truncation(k + 1)
        hi_n = liouville_truncation(k + 1) + liouville_tail_bound(k + 1)
        assert lo_k <= lo_n < hi_n <= hi_k


# --------------------------------------------------------------------------- #
#  Certified continued-fraction prefix and the explosion.
# --------------------------------------------------------------------------- #

def test_cf_terms_pinned_prefix():
    assert liouville_cf_terms(3) == [0, 9, 11, 99, 1, 10, 9]
    assert liouville_cf_terms(4) == [0, 9, 11, 99, 1, 10, 9, 999999999999, 1, 8, 10, 1, 99, 11, 9]


def test_cf_terms_prefix_property_in_max_terms():
    full = liouville_cf_terms(4, max_terms=20)
    for n in range(len(full) + 1):
        assert liouville_cf_terms(4, max_terms=n) == full[:n]


def test_cf_terms_prefix_property_in_k():
    # A wider bracket (larger k) only *extends* the certified prefix.
    assert liouville_cf_terms(4)[: len(liouville_cf_terms(3))] == liouville_cf_terms(3)


def test_cf_terms_contain_a_monster_quotient():
    terms = liouville_cf_terms(4)
    assert max(terms) > 10 ** 4
    assert 999999999999 in terms
    peaks = partial_quotient_peaks(terms)
    assert peaks[-1] == (7, 999999999999)          # the record-setting explosion
    # records are strictly increasing by construction
    assert all(b > a for (_, a), (_, b) in zip(peaks, peaks[1:]))


# --------------------------------------------------------------------------- #
#  Irrationality-measure witness: Liouville spikes, golden ratio stays flat.
# --------------------------------------------------------------------------- #

def test_witness_liouville_spikes_above_bounded():
    liouville = irrationality_measure_witness(liouville_cf_terms(4))
    golden = irrationality_measure_witness([1] * 20)
    assert max(liouville) > 2.5          # the giant partial quotient shows up
    assert max(golden) < 2.0             # bounded quotients stay tame
    assert max(liouville) > max(golden)


def test_witness_golden_ratio_tends_to_one():
    golden = irrationality_measure_witness([1] * 20)
    assert golden == sorted(golden, reverse=True)   # monotonically decreasing
    assert abs(golden[-1] - 1.0) < 0.1              # ratios settle toward 1


# --------------------------------------------------------------------------- #
#  Liouville's degree-2 inequality: the exact verifier.
# --------------------------------------------------------------------------- #

def test_inequality_report_all_true_for_sqrt2():
    report = liouville_inequality_report(1, 0, -2)      # x^2 - 2
    assert len(report) == 8
    assert all(ok for _, _, ok in report)


def test_inequality_report_all_true_for_golden_ratio():
    report = liouville_inequality_report(1, -1, -1, cf_prefix_len=12)   # x^2 - x - 1
    assert all(ok for _, _, ok in report)


def test_inequality_holds_for_far_and_near_rationals():
    # Far away and hugging a convergent: both obey the bound.
    assert liouville_inequality_check(1, 0, -2, 1000000, 1)
    assert liouville_inequality_check(1, 0, -2, 577, 408)
    assert liouville_inequality_check(1, 0, -3, 1351, 780)   # sqrt(3) convergent


def test_inequality_rejects_non_irrational_and_degenerate():
    with pytest.raises(ValueError):
        liouville_inequality_check(1, 0, -4, 1, 1)      # root 2 is rational
    with pytest.raises(ValueError):
        liouville_inequality_check(0, 1, -1, 1, 1)      # not degree 2
    with pytest.raises(ValueError):
        liouville_inequality_check(1, 0, -2, 3, 0)      # q must be positive
