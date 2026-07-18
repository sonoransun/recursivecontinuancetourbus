"""CLI contract tests: flag positions, pinned errors, listings, determinism."""

from __future__ import annotations

import pytest

from tourbus.tour.demos import DEMOS
from tourbus.tour.registry import STOPS


# -- flag-position regressions ---------------------------------------------- #
# Global flags used to be silently ignored before a subcommand: the
# subparser's defaults clobbered the already-parsed values.

@pytest.mark.parametrize("before, after", [
    (("--width", "44", "--no-color", "stop", "5"),
     ("stop", "5", "--width", "44", "--no-color")),
    (("--no-color", "stop", "5"), ("stop", "5", "--no-color")),
    (("--color", "stop", "5"), ("stop", "5", "--color")),
    (("--ascii", "--no-color", "stop", "5"), ("stop", "5", "--ascii", "--no-color")),
    (("--seed", "5", "--no-color", "demo", "gauss"),
     ("--no-color", "demo", "gauss", "--seed", "5")),
    # Globals after the demo name land in REMAINDER; they must still apply.
    (("--ascii", "--no-color", "demo", "gauss"),
     ("demo", "gauss", "--ascii", "--no-color")),
    (("--width", "44", "--no-color", "demo", "collatz"),
     ("demo", "collatz", "--width", "44", "--no-color")),
], ids=["width", "no-color", "color", "ascii", "seed",
        "ascii-after-demo", "width-after-demo"])
def test_global_flags_work_before_and_after_subcommand(run_cli, before, after):
    code_b, out_b = run_cli(*before)
    code_a, out_a = run_cli(*after)
    assert code_b == code_a == 0
    assert out_b == out_a


def test_width_before_subcommand_takes_effect(run_cli):
    _, narrow = run_cli("--width", "40", "--no-color", "stop", "5")
    _, wide = run_cli("--width", "100", "--no-color", "stop", "5")
    # The header rule is exactly one console width of glyphs.
    assert len(narrow.splitlines()[0]) == 40
    assert len(wide.splitlines()[0]) == 100


def test_seed_before_subcommand_takes_effect(run_cli):
    _, seed0 = run_cli("--no-color", "demo", "gauss")
    _, seed5 = run_cli("--seed", "5", "--no-color", "demo", "gauss")
    assert seed0 != seed5


def test_color_before_subcommand_takes_effect(run_cli):
    _, colored = run_cli("--color", "stop", "1")
    _, plain = run_cli("--no-color", "stop", "1")
    assert "\x1b[" in colored
    assert "\x1b[" not in plain


def test_explicit_width_is_clamped_to_minimum(run_cli):
    _, out = run_cli("--width", "10", "--no-color", "stop", "1")
    assert len(out.splitlines()[0]) == 40
    assert all(len(line) <= 40 for line in out.splitlines()[:4])  # header block


def test_ascii_after_demo_name_takes_effect(run_cli):
    # Regression: REMAINDER used to swallow trailing global flags silently.
    code, out = run_cli("demo", "gauss", "--ascii", "--no-color")
    assert code == 0
    assert "#" in out          # the ascii bar glyph
    assert "█" not in out


def test_width_after_demo_name_is_not_a_demo_arg(run_cli):
    # Regression: "--width" used to reach the demo as its positional argument.
    code, out = run_cli("demo", "collatz", "--width", "40", "--no-color")
    assert code == 0
    assert "demo error:" not in out
    assert "Collatz flight of 27" in out


def test_demo_specific_flags_survive_the_global_reparse(run_cli):
    code, out = run_cli("demo", "gosper", "--op", "mul", "sqrt2", "sqrt3", "--no-color")
    assert code == 0
    assert "sqrt2 mul sqrt3" in out


# -- pinned error messages and exit codes ------------------------------------ #

def test_stop_out_of_range(run_cli):
    code, out = run_cli("stop", "99", "--no-color")
    assert code == 1
    assert out.strip() == "no stop 99 (valid 1..15)"


def test_stop_zero(run_cli):
    code, out = run_cli("stop", "0", "--no-color")
    assert code == 1
    assert out.strip() == "no stop 0 (valid 1..15)"


def test_unknown_demo(run_cli):
    code, out = run_cli("demo", "nosuch", "--no-color")
    assert code == 1
    assert out.strip() == "unknown demo 'nosuch'; try 'demo --list'"


def test_gosper_unknown_op(run_cli):
    # Regression: this used to leak the KeyError as "demo error: 'bogus'".
    code, out = run_cli("demo", "gosper", "--op", "bogus", "--no-color")
    assert code == 1
    assert out.strip() == "unknown op 'bogus' (add|sub|mul|div)"


def test_frontier_out_of_range(run_cli):
    code, out = run_cli("frontier", "99", "--no-color")
    assert code == 1
    assert "no express stop 99 (valid 1..9)" in out


def test_crossdomain_out_of_range(run_cli):
    code, out = run_cli("crossdomain", "99", "--no-color")
    assert code == 1
    assert "no cross-domain stop 99 (valid 1..7)" in out


def test_heritage_out_of_range(run_cli):
    code, out = run_cli("heritage", "99", "--no-color")
    assert code == 1
    assert "no heritage stop 99 (valid 1..9)" in out


def test_branch_out_of_range(run_cli):
    code, out = run_cli("branch", "99", "--no-color")
    assert code == 1
    assert "no branch stop 99 (valid 1..6)" in out


# -- the Heritage Line --------------------------------------------------------- #

def test_heritage_whole_line_covers_all_stops(run_cli, stub_lines):
    from tourbus.tour.heritage import HERITAGE_STOPS

    code, out = run_cli("heritage", "--no-color")
    assert code == 0
    assert "THE HERITAGE LINE" in out
    for n, (title, _note, _run) in enumerate(HERITAGE_STOPS, start=1):
        assert f"HERITAGE {n} / {len(HERITAGE_STOPS)}" in out
        assert title.upper() in out
    assert "End of the Heritage Line." in out


def test_heritage_single_stop_is_the_chakravala(run_cli):
    code, out = run_cli("heritage", "2", "--no-color")
    assert code == 0
    assert "HERITAGE 2 / 9" in out
    assert "HERITAGE 1 / 9" not in out
    assert "1766319049" in out           # Bhaskara's d = 61, the CI grep target


@pytest.mark.slow
def test_heritage_transcript_is_deterministic(run_cli):
    code1, first = run_cli("heritage", "--no-color", "--width", "80")
    code2, second = run_cli("heritage", "--no-color", "--width", "80")
    assert code1 == code2 == 0
    assert first == second
    assert "End of the Heritage Line." in first


# -- listings ----------------------------------------------------------------- #

def test_demo_list_names_match_registry(run_cli):
    code, out = run_cli("demo", "--list", "--no-color")
    assert code == 0
    names = [line.split()[0] for line in out.splitlines() if line.startswith("  ")]
    assert names == list(DEMOS)


def test_list_shows_every_main_stop(run_cli):
    code, out = run_cli("list", "--no-color")
    assert code == 0
    for s in STOPS:
        assert s.title in out


def test_version(run_cli):
    from tourbus import __version__

    code, out = run_cli("--version")
    assert code == 0
    assert out.strip() == f"tourbus {__version__}"


# -- the interactive boarding prompt ------------------------------------------ #
# Regression: at a line's terminus, any input other than q used to board the
# next line -- b, m, and typos were silent consent. Only Enter boards now.

def test_back_at_the_boarding_prompt_returns_to_the_terminus(ride):
    out = ride("\nb\nq\n", start=15)     # Enter to the gate, b, then quit
    assert out.count("STOP 15 / 15") == 2
    assert "EXPRESS 1 / 9" not in out


def test_map_at_the_boarding_prompt_does_not_board(ride):
    out = ride("\nm\nq\n", start=15)
    assert "THE EXPRESS LINE" in out     # the map is shown...
    assert "EXPRESS 1 / 9" not in out    # ...but the bus stays at the gate


def test_help_at_the_boarding_prompt_does_not_board(ride):
    out = ride("\nh\nq\n", start=15)
    assert "previous stop" in out        # the help text
    assert "EXPRESS 1 / 9" not in out


def test_typo_at_the_boarding_prompt_reasks(ride):
    out = ride("\nwat\nq\n", start=15)
    assert "unknown command 'wat' (h for help)" in out
    assert "EXPRESS 1 / 9" not in out


# -- the non-interactive tour --------------------------------------------------- #

def test_non_tty_tour_honors_from(run_cli, stub_lines):
    # Regression: piped `tour --from N` used to print everything from stop 1.
    code, out = run_cli("tour", "--from", "14", "--no-color")
    assert code == 0
    assert "STOP 13 / 15" not in out
    assert "STOP 14 / 15" in out
    assert "STOP 15 / 15" in out
    assert "EXPRESS 9 / 9" in out        # every bonus line still follows
    assert "CROSS-DOMAIN 7 / 7" in out
    assert "HERITAGE 9 / 9" in out
    assert "BRANCH 6 / 6" in out


# -- the full transcript ------------------------------------------------------ #

def test_all_covers_all_five_lines_fast(run_cli, stub_lines):
    # The --all smoke test with the stop bodies stubbed to no-ops: the route
    # structure -- banners, every bonus line, the closing line -- stays cheap
    # to assert; the real transcript is pinned by the slow test below.
    code, out = run_cli("--all", "--no-color", "--width", "80")
    assert code == 0
    assert f"STOP {len(STOPS)} / {len(STOPS)}" in out
    assert "EXPRESS 9 / 9" in out
    assert "CROSS-DOMAIN 7 / 7" in out
    assert "HERITAGE 9 / 9" in out
    assert "BRANCH 6 / 6" in out
    assert out.index("THE CROSS-DOMAIN LINE") < out.index("THE HERITAGE LINE")
    assert out.index("THE HERITAGE LINE") < out.index("THE BRANCH LINE")
    assert "End of the line. Thank you for riding." in out


@pytest.mark.slow
def test_all_transcript_is_deterministic_and_covers_all_lines(run_cli):
    code1, first = run_cli("--all", "--no-color", "--seed", "1", "--width", "80")
    code2, second = run_cli("--all", "--no-color", "--seed", "1", "--width", "80")
    assert code1 == code2 == 0
    assert first == second
    # The whole tour: main route, then the Express, Cross-Domain, Heritage,
    # and Branch Lines, in that order.
    assert f"STOP {len(STOPS)} / {len(STOPS)}" in first
    assert "EXPRESS 9 / 9" in first
    assert "CROSS-DOMAIN 7 / 7" in first
    assert "HERITAGE 9 / 9" in first
    assert "BRANCH 6 / 6" in first
    assert first.index("THE CROSS-DOMAIN LINE") < first.index("THE HERITAGE LINE")
    assert first.index("THE HERITAGE LINE") < first.index("THE BRANCH LINE")
    assert "End of the line. Thank you for riding." in first
