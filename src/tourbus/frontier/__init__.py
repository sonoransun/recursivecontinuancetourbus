"""The Express Line: fringe avenues of recursion and continued fractions.

Beyond the main tour lie stranger, deeper stops — each still computed exactly
(or rigorously) on the same engine:

* :mod:`~tourbus.frontier.markov` — the Markov/Lagrange spectrum: the numbers
  that come after the golden ratio.
* :mod:`~tourbus.frontier.continuants` — the polynomial identity behind every
  convergent, with Euler's combinatorial rule.
* :mod:`~tourbus.frontier.algebraic` — continued fractions of cube roots and the
  plastic number, brushing against an open problem.
* :mod:`~tourbus.frontier.variants` — nearest-integer and Hirzebruch-Jung
  "minus" continued fractions.
* :mod:`~tourbus.frontier.three_distance` — Steinhaus's three-gap theorem.
* :mod:`~tourbus.frontier.gkw` — the Gauss-Kuzmin-Wirsing constant from the
  transfer operator.
"""

from __future__ import annotations

from .continuants import continuant, continuant_euler, convergent_via_continuants
from .markov import (
    lagrange_number,
    markov_numbers,
    markov_triples,
    markov_value,
    extremal_cf,
)
from .algebraic import cube_root_cf, nth_root_cf, plastic_number_cf, partial_quotient_stats
from .variants import nearest_integer_cf, minus_cf, regular_cf
from .three_distance import three_distance_report, gap_lengths, orbit_points
from .gkw import second_eigenvalue, leading_eigenvalue, GKW_CONSTANT
from .physics import galperin_collisions, pi_prefix

__all__ = [
    "continuant", "continuant_euler", "convergent_via_continuants",
    "markov_triples", "markov_numbers", "lagrange_number", "markov_value", "extremal_cf",
    "cube_root_cf", "nth_root_cf", "plastic_number_cf", "partial_quotient_stats",
    "nearest_integer_cf", "minus_cf", "regular_cf",
    "three_distance_report", "gap_lengths", "orbit_points",
    "second_eigenvalue", "leading_eigenvalue", "GKW_CONSTANT",
    "galperin_collisions", "pi_prefix",
]
