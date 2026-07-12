"""Dynamics: the Gauss map and the metric theory of continued fractions.

Continued fractions are not just an algebraic gadget — they carry a dynamical
system. The **Gauss map** ``T(x) = {1/x}`` shifts a number's partial quotients
one place to the left, and its long-run statistics obey three celebrated laws:

* the **Gauss-Kuzmin distribution** of individual digits
  (:func:`kuzmin_theoretical`, :func:`kuzmin_empirical`),
* **Khinchin's constant**, the geometric mean of the digits of almost every real
  (:func:`khinchin_estimate`), and
* **Levy's constant**, the growth rate of the convergent denominators
  (:func:`levy_estimate`).

This subpackage supplies the map (:func:`gauss_map`, :func:`gauss_orbit`) and the
tools to measure those laws empirically on any digit stream the tour produces.
"""

from __future__ import annotations

from .gauss import (
    gauss_map,
    gauss_orbit,
    khinchin_estimate,
    kuzmin_empirical,
    kuzmin_theoretical,
    levy_estimate,
)

__all__ = [
    "gauss_map",
    "gauss_orbit",
    "kuzmin_theoretical",
    "kuzmin_empirical",
    "khinchin_estimate",
    "levy_estimate",
]
