import math
from fractions import Fraction

import pytest

from tourbus.cf.core import QuadraticSurd
from tourbus.crossdomain import fibonacci_chain as F


# --- the word ---------------------------------------------------------------#

def test_word_examples_and_lengths():
    assert F.fibonacci_word(4) == "abaababa"
    assert [len(F.fibonacci_word(n)) for n in range(6)] == [1, 2, 3, 5, 8, 13]


def test_word_self_similarity():
    # w_{n+1} = w_n + w_{n-1}  (the defining Fibonacci concatenation).
    for n in range(1, 9):
        assert F.fibonacci_word(n + 1) == F.fibonacci_word(n) + F.fibonacci_word(n - 1)


def test_no_two_short_tiles_are_adjacent():
    # 'bb' never occurs: a hallmark of the Fibonacci substitution.
    for n in range(1, 10):
        assert "bb" not in F.fibonacci_word(n)


# --- tile frequencies -------------------------------------------------------#

def test_tile_frequencies_are_fibonacci_ratios():
    assert F.tile_frequencies(10) == (Fraction(89, 144), Fraction(55, 144))


def test_frequencies_sum_to_one_and_tend_to_golden_ratio():
    for n in range(1, 14):
        fa, fb = F.tile_frequencies(n)
        assert fa + fb == 1
    fa, fb = F.tile_frequencies(20)
    assert float(fa / fb) == pytest.approx((1 + 5 ** 0.5) / 2, abs=1e-3)


# --- exact positions in Z[phi] ---------------------------------------------#

def test_positions_are_exact_surds():
    pos = F.fibonacci_chain_positions(2)          # word 'aba'
    assert all(isinstance(p, QuadraticSurd) for p in pos)
    assert [str(p) for p in pos] == [
        "0",
        "1/2 + 1/2*sqrt(5)",
        "3/2 + 1/2*sqrt(5)",
        "2 + sqrt(5)",
    ]


def test_position_spacings_take_two_values_in_golden_ratio():
    # Consecutive gaps are the long tile (phi) and the short tile (1); their
    # ratio is exactly the golden ratio, and they live in Z[phi].
    pos = F.fibonacci_chain_positions(6)
    phi = QuadraticSurd.from_pqd(1, 5, 2)
    gaps = {round(float(pos[i + 1]) - float(pos[i]), 9) for i in range(len(pos) - 1)}
    assert len(gaps) == 2
    long_gap, short_gap = max(gaps), min(gaps)
    assert short_gap == pytest.approx(1.0, abs=1e-9)
    assert long_gap == pytest.approx(float(phi), abs=1e-9)
    assert long_gap / short_gap == pytest.approx(float(phi), abs=1e-9)


def test_numeric_positions_are_floats():
    pos = F.fibonacci_chain_positions(2, long=2.0, short=1.0)
    assert pos == [0.0, 2.0, 3.0, 5.0]
    assert all(isinstance(p, float) for p in pos)


# --- diffraction ------------------------------------------------------------#

def test_structure_factor_forward_beam_counts_atoms():
    pos = F.fibonacci_chain_positions(6, long=1.618, short=1.0)
    assert F.structure_factor(pos, 0.0) == pytest.approx(len(pos))


def test_structure_factor_is_bounded_by_atom_count():
    pos = F.fibonacci_chain_positions(7, long=1.618, short=1.0)
    for Q in (0.3, 1.0, 2.5, 5.0, 8.6):
        assert 0.0 <= F.structure_factor(pos, Q) <= len(pos) + 1e-9


def test_peak_wavevector_formula():
    tau = (1 + 5 ** 0.5) / 2
    assert F.peak_wavevector(1, 1) == pytest.approx(
        2 * math.pi * (tau + 1) / math.sqrt(tau + 2)
    )


def test_brightest_peaks_are_the_convergent_ladder():
    peaks = F.diffraction_peaks(6, hmax=8, top=4)
    assert [(p.h, p.k) for p in peaks] == [(8, 5), (5, 3), (3, 2), (2, 1)]
    # intensities are ordered and near unity for the sharp convergent peaks.
    intensities = [p.intensity for p in peaks]
    assert intensities == sorted(intensities, reverse=True)
    assert all(i > 0.7 for i in intensities)


def test_peak_ladder_is_golden_convergents():
    assert F.fibonacci_peak_ladder(6) == [
        (1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (13, 8),
    ]
    # (F_{n+1}, F_n): each index pair is consecutive Fibonacci numbers.
    ladder = F.fibonacci_peak_ladder(9)
    for (h1, k1), (h2, k2) in zip(ladder, ladder[1:]):
        assert k2 == h1          # denominators shift into numerators
        assert h2 == h1 + k1     # Fibonacci recurrence


def test_ladder_peaks_have_small_perp_momentum():
    # The whole point: convergent peaks push Q_perp -> 0, so they are sharp.
    ladder = F.fibonacci_peak_ladder(7)
    root = math.sqrt(F._TAU + 2)
    perps = [abs(2 * math.pi * (k * F._TAU - h) / root) for h, k in ladder]
    # strictly decreasing perpendicular momentum along the ladder
    assert perps == sorted(perps, reverse=True)
    assert perps[-1] < perps[0]
