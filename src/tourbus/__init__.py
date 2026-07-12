"""Recursive Continuance Tour Bus — recursion and continued fractions.

``tourbus`` is a standard-library-only computational engine for a guided tour
through recursion and continued fractions, from Euclid's algorithm to Gosper's
exact stream arithmetic and the open problems at the frontier.

The public surface re-exported here is the exact-arithmetic core; the guided
tour lives in :mod:`tourbus.tour` and is reached via ``python -m tourbus``.
"""

from __future__ import annotations

__version__ = "1.0.0"

from .cf.core import CF, CFKind, QuadraticSurd
from .cf.convergents import (
    best_approximation,
    best_approximations,
    convergent_pairs,
    recurrence,
    semiconvergents,
)
from .cf.constants import e_cf, phi_cf, pi_cf, sqrt_cf
from .cf.expand import cf_from_fraction, cf_from_quadratic
from .cf import gosper

__all__ = [
    "__version__",
    "CF",
    "CFKind",
    "QuadraticSurd",
    "cf_from_fraction",
    "cf_from_quadratic",
    "recurrence",
    "convergent_pairs",
    "semiconvergents",
    "best_approximation",
    "best_approximations",
    "phi_cf",
    "sqrt_cf",
    "e_cf",
    "pi_cf",
    "gosper",
]
