"""Shared pytest fixtures and hypothesis strategies for the tourbus suite."""

from __future__ import annotations

import sys
from fractions import Fraction
from math import isqrt
from pathlib import Path

import pytest
from hypothesis import HealthCheck, settings
from hypothesis import strategies as st

# Make the src-layout package importable without an editable install.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Exact big-integer arithmetic can make individual examples heavy; timing is not
# what these property tests check, so disable the per-example deadline.
settings.register_profile("tourbus", deadline=None, suppress_health_check=[HealthCheck.too_slow])
settings.load_profile("tourbus")


# --- strategies ------------------------------------------------------------ #

def st_fractions(max_value: int = 10_000):
    """Non-zero-denominator rationals with bounded numerator/denominator."""
    return st.builds(
        Fraction,
        st.integers(min_value=-max_value, max_value=max_value),
        st.integers(min_value=1, max_value=max_value),
    )


def st_positive_fractions(max_value: int = 10_000):
    return st.builds(
        Fraction,
        st.integers(min_value=1, max_value=max_value),
        st.integers(min_value=1, max_value=max_value),
    )


def _is_square(n: int) -> bool:
    r = isqrt(n)
    return r * r == n


def st_nonsquare_d(min_value: int = 2, max_value: int = 500):
    return st.integers(min_value=min_value, max_value=max_value).filter(
        lambda n: not _is_square(n)
    )


@pytest.fixture
def rng():
    import random

    return random.Random(0)
