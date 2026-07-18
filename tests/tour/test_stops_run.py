"""Every stop on every line, and every demo, runs clean at several widths."""

from __future__ import annotations

import pytest

from tourbus.tour.branch import BRANCH_STOPS
from tourbus.tour.crossline import CROSS_STOPS
from tourbus.tour.demos import DEMOS
from tourbus.tour.express import EXPRESS_STOPS
from tourbus.tour.heritage import HERITAGE_STOPS
from tourbus.tour.registry import STOPS

# Each configuration is passed as global flags before the subcommand.
CONFIGS = [
    pytest.param(("--width", "80"), id="w80"),
    pytest.param(("--width", "40"), id="w40"),
    pytest.param(("--ascii",), id="ascii"),
]

# Stops with multi-second computations (high-precision constants, Pell on
# large d, Gosper stream arithmetic); deselected by the default addopts.
_SLOW_STOPS = {3, 4, 9, 11}
_SLOW_EXPRESS = {7}   # Galperin block-collision simulation
_SLOW_HERITAGE = {3}  # pi_cf() at full precision for the 355/113 comparison
_SLOW_BRANCH = set()
_SLOW_DEMOS = {"blocks"}

# Demos whose defaults need arguments to exercise the happy path.
_DEMO_ARGS = {"euclid": ("252", "105")}


def _params(items, slow, prefix):
    # A list, not a generator: pytest 10 stops collecting generator argvalues.
    params = []
    for it in items:
        marks = [pytest.mark.slow] if it in slow else []
        label = f"{it:02d}" if isinstance(it, int) else str(it)
        params.append(pytest.param(it, id=prefix + label, marks=marks))
    return params


@pytest.mark.parametrize("flags", CONFIGS)
@pytest.mark.parametrize("number", _params(range(1, len(STOPS) + 1), _SLOW_STOPS, "stop"))
def test_every_main_stop_runs(run_cli, number, flags):
    code, out = run_cli(*flags, "--no-color", "stop", str(number))
    assert code == 0
    assert STOPS[number - 1].title.upper() in out


@pytest.mark.parametrize("flags", CONFIGS)
@pytest.mark.parametrize(
    "number", _params(range(1, len(EXPRESS_STOPS) + 1), _SLOW_EXPRESS, "express"))
def test_every_express_stop_runs(run_cli, number, flags):
    code, out = run_cli(*flags, "--no-color", "frontier", str(number))
    assert code == 0
    assert f"EXPRESS {number} / {len(EXPRESS_STOPS)}" in out


@pytest.mark.parametrize("flags", CONFIGS)
@pytest.mark.parametrize("number", _params(range(1, len(CROSS_STOPS) + 1), set(), "cross"))
def test_every_crossdomain_stop_runs(run_cli, number, flags):
    code, out = run_cli(*flags, "--no-color", "crossdomain", str(number))
    assert code == 0
    # Regression: cross-domain stops carry their own line label, not EXPRESS.
    assert f"CROSS-DOMAIN {number} / {len(CROSS_STOPS)}" in out
    assert "EXPRESS" not in out


@pytest.mark.parametrize("flags", CONFIGS)
@pytest.mark.parametrize(
    "number", _params(range(1, len(HERITAGE_STOPS) + 1), _SLOW_HERITAGE, "heritage"))
def test_every_heritage_stop_runs(run_cli, number, flags):
    code, out = run_cli(*flags, "--no-color", "heritage", str(number))
    assert code == 0
    # Regression: heritage stops carry their own line label, not EXPRESS.
    assert f"HERITAGE {number} / {len(HERITAGE_STOPS)}" in out
    assert "EXPRESS" not in out
    assert "CROSS-DOMAIN" not in out


@pytest.mark.parametrize("flags", CONFIGS)
@pytest.mark.parametrize(
    "number", _params(range(1, len(BRANCH_STOPS) + 1), _SLOW_BRANCH, "branch"))
def test_every_branch_stop_runs(run_cli, number, flags):
    code, out = run_cli(*flags, "--no-color", "branch", str(number))
    assert code == 0
    # Regression: branch stops carry their own line label, not EXPRESS.
    assert f"BRANCH {number} / {len(BRANCH_STOPS)}" in out
    assert "EXPRESS" not in out
    assert "CROSS-DOMAIN" not in out


@pytest.mark.parametrize("flags", CONFIGS)
@pytest.mark.parametrize("name", _params(sorted(DEMOS), _SLOW_DEMOS, "demo-"))
def test_every_demo_runs(run_cli, name, flags):
    code, out = run_cli(*flags, "--no-color", "demo", name, *_DEMO_ARGS.get(name, ()))
    assert code == 0
    assert out.strip()
    assert "demo error:" not in out
