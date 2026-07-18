"""The route rail, souvenirs, and subheads adapt to the console width."""

from __future__ import annotations

import io

from tourbus.tour import render
from tourbus.tour.termio import Console, make_console


def _console(width: int) -> Console:
    return Console(width=width, color=False, ascii_only=True)


def _capture(width: int) -> tuple[Console, io.StringIO]:
    out = io.StringIO()
    return Console(width=width, color=False, ascii_only=True, out=out), out


def test_rail_keeps_full_links_when_wide():
    rail = render.route_line(15, 7, _console(80))
    assert "@--o" in rail          # two-glyph ascii links
    assert "STOP 7 / 15" in rail
    assert len(rail) <= 79


def test_header_fits_at_width_40():
    header = render.stop_header(7, 15, "The Cattle Crossing", _console(40))
    for line in header.split("\n"):
        assert len(line) <= 40


def test_rail_wraps_label_when_very_narrow():
    rail = render.route_line(15, 7, _console(24))
    lines = rail.split("\n")
    assert len(lines) == 2
    assert "STOP 7 / 15" in lines[1]
    assert all(len(line) <= 24 for line in lines)


def test_make_console_clamps_explicit_width():
    assert make_console(width=10, color=False).width == 40
    assert make_console(width=80, color=False).width == 80


# -- souvenir and subhead wrap instead of overflowing -------------------------- #

_LONG = ("the bus keeps a little of every stop: gcd, convergents, and the one "
         "recurrence that drives them all")


def test_souvenir_wraps_at_width_40():
    c, out = _capture(40)
    render.souvenir(c, _LONG)
    lines = out.getvalue().splitlines()
    assert lines[-1] == ""                       # closes with a blank line
    body = lines[:-1]
    assert len(body) >= 2                        # long text actually wrapped
    assert body[0].startswith(" * souvenir: ")
    assert all(len(line) <= 40 for line in body)
    # Continuation lines hang under the text, past the 13-column marker.
    for line in body[1:]:
        assert line.startswith(" " * 13) and line[13] != " "


def test_subhead_wraps_at_width_minus_one():
    c, out = _capture(40)
    render.subhead(c, _LONG)
    lines = out.getvalue().splitlines()
    assert len(lines) >= 2
    assert all(len(line) <= 40 for line in lines)         # " " + (width-1)
    assert all(len(line.strip()) <= 39 for line in lines)


def test_souvenir_and_subhead_hold_the_20_column_floor():
    # Below any sane width the wrap floors at 20 columns instead of
    # degenerating to a word per line or a non-positive-width crash.
    c, out = _capture(10)
    render.souvenir(c, _LONG)
    body = [line for line in out.getvalue().splitlines() if line.strip()]
    assert all(len(line) <= 13 + 20 for line in body)
    assert len(body) < len(_LONG.split())        # words still share lines

    c, out = _capture(10)
    render.subhead(c, _LONG)
    lines = out.getvalue().splitlines()
    assert all(len(line) <= 1 + 20 for line in lines)
    assert len(lines) < len(_LONG.split())
