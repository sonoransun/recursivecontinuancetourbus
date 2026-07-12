from __future__ import annotations

import pytest

from tourbus.fractals import LSystem, expand


def test_axiom_at_zero_iterations():
    ls = LSystem("F", {"F": "F+F"}, angle=90)
    assert expand(ls, 0) == "F"


def test_known_small_expansion():
    ls = LSystem("F", {"F": "F+F--F+F"}, angle=60)  # Koch
    assert expand(ls, 1) == "F+F--F+F"
    word2 = expand(ls, 2)
    # every F becomes the 8-char rule; the four turn symbols are carried through
    assert word2.count("F") == 16
    assert len(word2) == 4 * 8 + 4


def test_length_growth_is_geometric():
    doubling = LSystem("F", {"F": "FF"}, angle=0)
    assert [len(expand(doubling, i)) for i in range(5)] == [1, 2, 4, 8, 16]


def test_algae_lengths_are_fibonacci():
    algae = LSystem("A", {"A": "AB", "B": "A"}, angle=0)
    assert [len(expand(algae, i)) for i in range(7)] == [1, 2, 3, 5, 8, 13, 21]


def test_symbols_without_rules_map_to_themselves():
    ls = LSystem("F+-[]G", {"F": "FF"}, angle=90)
    assert expand(ls, 1) == "FF+-[]G"


def test_negative_iterations_rejected():
    with pytest.raises(ValueError):
        expand(LSystem("F", {"F": "FF"}), -1)


def test_runaway_expansion_is_capped():
    # F -> FFFF quadruples each pass; ~4**11 > 2_000_000 well before it runs away
    with pytest.raises(ValueError):
        expand(LSystem("F", {"F": "FFFF"}), 40)
