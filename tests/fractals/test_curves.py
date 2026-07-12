from __future__ import annotations

import pytest

from tourbus.fractals import (
    LSystem,
    TurtleConfig,
    cantor,
    commands_to_points,
    dragon,
    expand,
    hilbert,
    koch,
    sierpinski_arrowhead,
)


def _segment_count(word: str, cfg: TurtleConfig, **kw) -> int:
    polylines = commands_to_points(word, cfg, **kw)
    return sum(len(poly) - 1 for poly in polylines)


def test_koch_segment_count():
    # depth 1 replaces the single segment with the four of "F+F--F+F"
    word = expand(LSystem("F", {"F": "F+F--F+F"}, angle=60), 1)
    assert _segment_count(word, TurtleConfig(step=10, angle=60)) == 4
    # depth n has 4**n segments
    for n in range(4):
        word = expand(LSystem("F", {"F": "F+F--F+F"}, angle=60), n)
        assert _segment_count(word, TurtleConfig(step=10, angle=60)) == 4 ** n


def test_dragon_segment_count_doubles():
    rules = {"F": "F+G", "G": "F-G"}
    for n in range(6):
        word = expand(LSystem("F", rules, angle=90), n)
        assert _segment_count(word, TurtleConfig(step=8, angle=90)) == 2 ** n


def test_hilbert_only_f_draws():
    # With A and B non-drawing, the number of segments equals the F count.
    rules = {"A": "+BF-AFA-FB+", "B": "-AF+BFB+FA-"}
    word = expand(LSystem("A", rules, angle=90), 2)
    segs = _segment_count(word, TurtleConfig(step=10, angle=90), draw="F")
    assert segs == word.count("F")
    assert segs > 0


def test_curves_return_svg_documents():
    for svg in (koch(2), sierpinski_arrowhead(3), dragon(6), hilbert(3), cantor(4)):
        assert svg.startswith("<svg")
        assert svg.rstrip().endswith("</svg>")
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg


@pytest.mark.parametrize(
    "func, bad",
    [
        (koch, 7),
        (sierpinski_arrowhead, 9),
        (dragon, 15),
        (hilbert, 8),
        (cantor, 8),
    ],
)
def test_depth_caps_raise(func, bad):
    with pytest.raises(ValueError):
        func(bad)


@pytest.mark.parametrize("func", [koch, sierpinski_arrowhead, dragon, hilbert, cantor])
def test_negative_depth_raises(func):
    with pytest.raises(ValueError):
        func(-1)
