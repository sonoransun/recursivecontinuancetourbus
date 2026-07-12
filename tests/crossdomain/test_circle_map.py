"""Tests for the sine circle map: winding numbers, tongues, devil's staircase."""

import math
import xml.dom.minidom as minidom
from fractions import Fraction

import pytest

from tourbus.crossdomain import circle_map


def test_winding_number_rigid_rotation():
    # K == 0 is the rigid rotation, so the winding number is Omega exactly.
    assert circle_map.winding_number(0.3, 0.0) == 0.3
    assert circle_map.winding_number(0.71, 0.0) == 0.71


def test_winding_number_locks_on_half():
    # At (Omega, K) = (0.5, 1.0) the orbit is locked on the 1/2 tongue.
    assert round(circle_map.winding_number(0.5, 1.0), 6) == 0.5


def test_winding_number_locks_on_zero():
    # Omega = 0.02 sits inside the wide 0/1 tongue at K = 1.
    assert round(circle_map.winding_number(0.02, 1.0), 4) == 0.0


def test_tongue_width_zero_over_one_is_one_over_pi():
    # The 0/1 tongue has the exact width K/pi; at K=1 that is 1/pi.
    assert round(circle_map.tongue_width(0, 1, 1.0), 4) == 0.3183
    assert abs(circle_map.tongue_width(0, 1, 1.0) - 1.0 / math.pi) < 1e-9


def test_tongue_is_a_point_at_zero_coupling():
    assert circle_map.tongue_width(0, 1, 0.0) == 0.0
    assert circle_map.tongue_boundaries(1, 2, 0.0) == (0.5, 0.5)


def test_tongue_boundaries_symmetric():
    lo, hi = circle_map.tongue_boundaries(0, 1, 1.0)
    # Edges are -/+ K/2pi, symmetric about Omega = 0.
    assert abs(lo + hi) < 1e-9
    assert abs(hi - 1.0 / (2 * math.pi)) < 1e-9


def test_half_tongue_contains_center():
    lo, hi = circle_map.tongue_boundaries(1, 2, 1.0)
    assert lo < 0.5 < hi
    assert hi - lo > 0.0


def test_locked_rational_inside_and_outside():
    assert circle_map.locked_rational(0.02, 1.0) == Fraction(0, 1)
    assert circle_map.locked_rational(0.5, 1.0) == Fraction(1, 2)
    # No locking at K = 0.
    assert circle_map.locked_rational(0.3, 0.0) is None


def test_devil_staircase_monotone_and_endpoints():
    steps = circle_map.devil_staircase(1.0, samples=25)
    ws = [w for _, w in steps]
    assert all(b >= a for a, b in zip(ws, ws[1:]))
    assert round(ws[0], 6) == 0.0
    assert round(ws[-1], 6) == 1.0


def test_farey_tongue_order_is_mediant_tree():
    assert circle_map.farey_tongue_order(0) == [Fraction(0, 1), Fraction(1, 1)]
    assert circle_map.farey_tongue_order(2) == [
        Fraction(0, 1),
        Fraction(1, 1),
        Fraction(1, 2),
        Fraction(1, 3),
        Fraction(2, 3),
    ]
    # The golden mean 1/phi is chased by these mediants (Fibonacci ratios).
    order = circle_map.farey_tongue_order(6)
    assert Fraction(5, 8) in order  # a Fibonacci convergent to 1/phi


def test_staircase_svg_is_well_formed():
    svg = circle_map.staircase_svg(1.0, samples=40)
    doc = minidom.parseString(svg)
    assert doc.documentElement.tagName == "svg"
    assert len(doc.getElementsByTagName("svg")) == 1
    assert len(doc.getElementsByTagName("polyline")) == 1


@pytest.mark.slow
@pytest.mark.statistical
def test_full_staircase_is_monotone():
    # A denser staircase with default iteration counts must stay monotone.
    steps = circle_map.devil_staircase(1.0, samples=200)
    ws = [w for _, w in steps]
    assert all(b >= a for a, b in zip(ws, ws[1:]))
