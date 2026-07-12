"""Tests for Harper's equation and the Hofstadter butterfly."""

import xml.dom.minidom as minidom

import pytest

from tourbus.cf.core import QuadraticSurd
from tourbus.crossdomain import hofstadter
from tourbus.frontier.continuants import continuant


def test_harper_diagonal_values():
    assert [round(a, 6) for a in hofstadter.harper_diagonal(1, 2)] == [2.0, -2.0]
    assert [round(a, 6) for a in hofstadter.harper_diagonal(1, 3)] == [2.0, -1.0, -1.0]


def test_sturm_sequence_is_the_determinant():
    # det([[2,1],[1,-2]]) = -5 as the last Sturm entry.
    assert hofstadter.sturm_sequence([2.0, -2.0], 0.0) == [1.0, 2.0, -5.0]


def test_sturm_sequence_ties_to_continuant():
    # With offdiag_sq = -1 the recurrence IS the continuant recurrence.
    for seq in ([3, 7, 15, 1], [1, 1, 1, 1, 1], [2, 3, 4]):
        got = hofstadter.sturm_sequence(seq, 0.0, offdiag_sq=-1.0)[-1]
        assert got == continuant(seq)


def test_count_eigenvalues_below():
    diag = hofstadter.harper_diagonal(1, 2)
    assert hofstadter.count_eigenvalues_below(diag, -3.0) == 0
    assert hofstadter.count_eigenvalues_below(diag, 0.0) == 1
    assert hofstadter.count_eigenvalues_below(diag, 3.0) == 2


def test_spectrum_flux_one_half_is_root_five():
    eigs = hofstadter.harper_spectrum(1, 2)
    assert [round(e, 6) for e in eigs] == [-2.236068, 2.236068]


def test_spectrum_is_traceless():
    for p, q in [(1, 3), (2, 5), (3, 7)]:
        assert abs(sum(hofstadter.harper_spectrum(p, q))) < 1e-9


def test_discriminant_flux_one_half_is_E_squared_minus_four():
    assert hofstadter.harper_discriminant(1, 2, 0.0) == -4.0
    assert round(hofstadter.harper_discriminant(1, 2, 2 * 2 ** 0.5), 6) == 4.0
    for E in (-1.5, -0.5, 0.0, 1.0, 2.3, 3.1):
        assert abs(hofstadter.harper_discriminant(1, 2, E) - (E * E - 4.0)) < 1e-9


def test_discriminant_flux_one_third_is_cubic():
    assert round(hofstadter.harper_discriminant(1, 3, 2.0), 6) == -4.0
    for E in (-2.0, -0.5, 1.0, 2.5):
        assert abs(hofstadter.harper_discriminant(1, 3, E) - (E ** 3 - 6.0 * E)) < 1e-9


def test_bands_flux_one_half_edges_are_two_root_two():
    bands = hofstadter.harper_bands(1, 2)
    assert len(bands) == 1  # the two central bands kiss at E = 0
    lo, hi = bands[0]
    edge = float(QuadraticSurd.make(0, 2, 2))  # 2 sqrt(2)
    assert abs(lo + edge) < 1e-3
    assert abs(hi - edge) < 1e-3


def test_band_count_parity():
    # Odd q: q clean bands and q-1 gaps.
    assert len(hofstadter.harper_bands(1, 3)) == 3
    assert len(hofstadter.harper_bands(2, 5)) == 5
    # Even q: the two central bands touch, so the scan sees one fewer interval.
    assert len(hofstadter.harper_bands(1, 4)) == 3


def test_bands_symmetric_about_zero():
    for p, q in [(1, 3), (2, 5), (1, 4)]:
        bands = hofstadter.harper_bands(p, q)
        mirror = sorted((-hi, -lo) for lo, hi in bands)
        for (a, b), (c, d) in zip(bands, mirror):
            assert abs(a - c) < 1e-3 and abs(b - d) < 1e-3


def test_gap_labels_are_convergents():
    assert hofstadter.gap_labels(1, 3) == [(0, 1), (1, 3)]
    assert hofstadter.gap_labels(2, 5) == [(0, 1), (1, 2), (2, 5)]


def test_butterfly_svg_is_well_formed():
    svg = hofstadter.butterfly_svg(4)
    doc = minidom.parseString(svg)
    assert doc.documentElement.tagName == "svg"
    assert len(doc.getElementsByTagName("svg")) == 1
    assert len(doc.getElementsByTagName("line")) > 0


@pytest.mark.slow
def test_butterfly_svg_larger_flux():
    svg = hofstadter.butterfly_svg(7)
    doc = minidom.parseString(svg)
    assert doc.documentElement.tagName == "svg"
