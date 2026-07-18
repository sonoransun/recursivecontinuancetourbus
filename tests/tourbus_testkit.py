"""Shared hypothesis strategies for the tourbus suite.

Test modules import these by bare module name (the test tree has no
packages), so the module lives directly under ``tests/`` — which pytest puts
on ``sys.path`` — under a name nothing else claims.  Do NOT move these back
into a ``conftest.py``: which file a bare ``import conftest`` resolves to
depends on the pytest invocation order once several conftests exist.
"""

from __future__ import annotations

from fractions import Fraction
from math import isqrt

from hypothesis import strategies as st


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
