"""The interactive loop: navigation polish and the four-line continuation.

Driven through the shared ``ride`` fixture (see conftest), which stubs the
stop bodies so their own "try>" prompts do not eat the scripted keystrokes;
the bodies themselves are covered by the table-driven tests. What is
exercised here is the loop: headers, prompts, and navigation.
"""

from __future__ import annotations

from tourbus.tour.branch import BRANCH_STOPS
from tourbus.tour.crossline import CROSS_STOPS
from tourbus.tour.express import EXPRESS_STOPS
from tourbus.tour.heritage import HERITAGE_STOPS


def test_quit_at_the_first_stop(ride):
    out = ride("q\n")
    assert "STOP 1 / 15" in out
    assert "STOP 2 / 15" not in out
    assert "Thank you for riding." in out


def test_prompt_shows_current_position(ride):
    out = ride("q\n", start=7)
    assert "stop 7/15 · The Cattle Crossing" in out


def test_unknown_input_hints_instead_of_advancing(ride):
    out = ride("wat\nq\n", start=5)
    assert "unknown command 'wat' (h for help)" in out
    assert "STOP 6 / 15" not in out


def test_help_lists_the_commands(ride):
    out = ride("h\nq\n")
    assert "next stop" in out
    assert "previous stop" in out
    assert "off the bus" in out


def test_jump_accepts_g8_and_g_space_8(ride):
    assert "STOP 8 / 15" in ride("g8\nq\n")
    assert "STOP 8 / 15" in ride("g 8\nq\n")


def test_jump_rejects_non_decimal_digits(ride):
    # '²'.isdigit() is True but int('²') raises; the guard must be isdecimal().
    out = ride("g²\nq\n", start=5)
    assert "unknown command 'g²' (h for help)" in out
    assert "STOP 6 / 15" not in out


def test_map_shows_all_five_lines(ride):
    out = ride("m\nq\n", start=2)
    assert "THE MAIN ROUTE" in out
    assert "THE EXPRESS LINE" in out
    assert "THE CROSS-DOMAIN LINE" in out
    assert "THE HERITAGE LINE" in out
    assert "THE BRANCH LINE" in out
    assert EXPRESS_STOPS[0][0] in out
    assert CROSS_STOPS[0][0] in out
    assert HERITAGE_STOPS[0][0] in out
    assert BRANCH_STOPS[0][0] in out


def test_terminus_offers_the_express_line(ride):
    out = ride("\n\nq\n", start=15)
    assert "board the Express Line" in out
    assert "EXPRESS 1 / 9" in out


def test_declining_the_express_line_ends_the_tour(ride):
    out = ride("\nq\n", start=15)
    assert "board the Express Line" in out
    assert "EXPRESS 1 / 9" not in out
    assert "Thank you for riding." in out


def test_express_terminus_offers_the_crossdomain_line(ride):
    # Terminus -> board express -> jump to its last stop -> ride off its end.
    out = ride("\n\ng9\n\n\nq\n", start=15)
    assert "board the Cross-Domain Line" in out
    assert "CROSS-DOMAIN 1 / 7" in out


def test_crossdomain_terminus_offers_the_heritage_line(ride):
    # Terminus -> board express -> jump to its end -> board cross-domain ->
    # jump to its end -> ride off it: the Heritage Line is the next leg.
    out = ride("\n\ng9\n\n\ng7\n\n\nq\n", start=15)
    assert "board the Heritage Line" in out
    assert "HERITAGE 1 / 9" in out


def test_heritage_terminus_offers_the_branch_line(ride):
    # ...ride to the Heritage end and off it: the Branch Line is the last leg.
    out = ride("\n\ng9\n\n\ng7\n\n\ng9\n\n\nq\n", start=15)
    assert "board the Branch Line" in out
    assert "BRANCH 1 / 6" in out


def test_riding_straight_through_reaches_the_depot(ride):
    out = ride("")  # exhausted input: every prompt takes its default
    assert "EXPRESS 9 / 9" in out
    assert "CROSS-DOMAIN 7 / 7" in out
    assert "HERITAGE 9 / 9" in out
    assert "BRANCH 6 / 6" in out
    assert "Thank you for riding." in out


def test_back_crosses_a_line_boundary(ride):
    out = ride("\n\nb\nq\n", start=15)  # board express, then step back
    assert out.count("STOP 15 / 15") == 2
