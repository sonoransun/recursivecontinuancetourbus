"""Shared pytest fixtures and hypothesis profile for the tourbus suite.

The reusable strategies live in ``tourbus_testkit.py`` (imported by test
modules as a bare name); they are re-exported here for backward
compatibility, but new tests should import from ``tourbus_testkit``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from hypothesis import HealthCheck, settings

# Make the src-layout package importable without an editable install.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
# tests/ itself must be importable for the bare `tourbus_testkit` name below
# and in test modules, regardless of which directory pytest collects first.
_TESTS = Path(__file__).resolve().parent
if str(_TESTS) not in sys.path:
    sys.path.insert(0, str(_TESTS))

from tourbus_testkit import (  # noqa: E402,F401  (re-export for old imports)
    st_fractions,
    st_nonsquare_d,
    st_positive_fractions,
)

# Exact big-integer arithmetic can make individual examples heavy; timing is not
# what these property tests check, so disable the per-example deadline.
settings.register_profile("tourbus", deadline=None, suppress_health_check=[HealthCheck.too_slow])
settings.load_profile("tourbus")


@pytest.fixture
def rng():
    import random

    return random.Random(0)
