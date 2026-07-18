from math import gcd

from hypothesis import given, settings
from hypothesis import strategies as st

from tourbus_testkit import st_nonsquare_d
from tourbus.cf.expand import cf_from_quadratic
from tourbus.frontier.markov import markov_triples
from tourbus.numbertheory.pell import fundamental_solution
from tourbus.numbertheory.topograph import (
    RiverCell,
    climbing_lemma_ok,
    form_value,
    markov_edge,
    pell_from_river,
    river_cells,
    river_period,
    river_values,
    topograph_data,
    topograph_strip,
)


# --------------------------------------------------------------------------- #
#  The river is the continued fraction of sqrt(d).
# --------------------------------------------------------------------------- #

@given(st_nonsquare_d(max_value=200))
def test_river_period_matches_cf(d):
    assert river_period(d) == cf_from_quadratic(0, d, 1)[1]


@given(st_nonsquare_d(max_value=200))
def test_river_cells_partial_quotients_are_the_period(d):
    cells = river_cells(d)
    assert [c.a for c in cells] == river_period(d)
    assert all(isinstance(c, RiverCell) for c in cells)
    # the PQa invariant Q_{i+1} = (d - P_{i+1}^2)/Q_i keeps every Q > 0
    assert all(c.Q > 0 for c in cells)


# --------------------------------------------------------------------------- #
#  Pell solutions are wells on the river.
# --------------------------------------------------------------------------- #

@given(st_nonsquare_d(max_value=200))
def test_pell_from_river(d):
    x, y = pell_from_river(d)
    assert x * x - d * y * y == 1
    sol = fundamental_solution(d, 1)
    assert (x, y) == (sol.x, sol.y)


def test_pell_from_river_known_values():
    assert pell_from_river(2) == (3, 2)
    assert pell_from_river(61) == (1766319049, 226153980)


# --------------------------------------------------------------------------- #
#  River values: sign alternation and a brute-force reality check.
# --------------------------------------------------------------------------- #

@given(st_nonsquare_d(max_value=200))
def test_river_values_strictly_alternate_in_sign(d):
    vals = river_values(d)
    assert all(u * v < 0 for u, v in zip(vals, vals[1:]))
    # each |value| is the Q of the corresponding cell
    assert [abs(v) for v in vals] == [c.Q for c in river_cells(d)]


def test_river_values_are_genuine_form_values():
    # Brute force: every signed river value must actually be attained by
    # x^2 - d y^2 on some primitive (x, y) with |x|, |y| <= 30.
    for d in (2, 3, 5, 6, 7, 8, 11, 13, 14, 22):
        attained = {
            form_value(1, 0, -d, x, y)
            for x in range(-30, 31)
            for y in range(-30, 31)
            if (x or y) and gcd(abs(x), abs(y)) == 1
        }
        for v in river_values(d):
            assert v in attained, (d, v)


# --------------------------------------------------------------------------- #
#  The climbing lemma.
# --------------------------------------------------------------------------- #

def test_climbing_lemma_on_known_d():
    for d in (2, 3, 7, 13, 61):
        assert climbing_lemma_ok(d)


@given(st_nonsquare_d(max_value=120))
@settings(max_examples=40)
def test_climbing_lemma_holds_generally(d):
    assert climbing_lemma_ok(d, steps=8)


# --------------------------------------------------------------------------- #
#  ASCII strip and JSON data for the figure.
# --------------------------------------------------------------------------- #

def test_topograph_strip_fits_and_is_deterministic():
    for d in (2, 3, 7, 13, 61, 166):
        rows = topograph_strip(d)
        assert len(rows) == 3
        assert all(len(row) <= 72 for row in rows)
        assert topograph_strip(d) == rows          # deterministic


def test_topograph_strip_contains_the_period():
    rows = topograph_strip(7)
    river = rows[1]
    for a in river_period(7):
        assert f"a={a}" in river


def test_topograph_data_shape():
    data = topograph_data(7)
    assert data["d"] == 7
    assert data["period"] == river_period(7)
    assert set(data.keys()) == {"d", "period", "river", "banks"}
    assert len(data["river"]) == len(river_period(7))
    for cell in data["river"]:
        assert set(cell.keys()) == {"P", "Q", "a", "above", "below"}
        assert cell["above"] > 0 > cell["below"]
    assert len(data["banks"]) == len(river_period(7))
    assert all(len(ring) == 2 for ring in data["banks"])
    # a deeper bank ring is longer and marches strictly upward
    deep = topograph_data(7, bank_depth=4)
    for ring in deep["banks"]:
        assert len(ring) == 4
        assert ring == sorted(ring) and len(set(ring)) == 4


def test_topograph_data_banks_alternate_even_for_unit_period():
    # d = n^2 + 1 has period length 1; the banks must still carry opposite signs
    # (the sign alternates around the cycle even when the Q-period does not).
    for d in (2, 5, 10, 17, 26):
        data = topograph_data(d)
        assert len(data["river"]) == 1
        cell = data["river"][0]
        assert cell["above"] > 0 > cell["below"]


# --------------------------------------------------------------------------- #
#  Markov cousin: the same tree-walk arithmetic.
# --------------------------------------------------------------------------- #

def test_markov_edge_pinned():
    assert markov_edge((1, 1, 1)) == [(2, 1, 1), (1, 2, 1), (1, 1, 2)]
    assert markov_edge((1, 2, 5)) == [(29, 2, 5), (1, 13, 5), (1, 2, 1)]


def test_markov_edge_preserves_the_markov_equation():
    def is_markov(t):
        x, y, z = t
        return x * x + y * y + z * z == 3 * x * y * z
    for t in markov_triples(200):
        for nb in markov_edge(t):
            assert is_markov(nb)


def test_markov_edge_agrees_with_frontier_tree():
    tree = set(markov_triples(10000))
    for t in markov_triples(200):
        for nb in markov_edge(t):
            key = tuple(sorted(nb))
            if min(key) >= 1 and max(key) <= 10000:
                assert key in tree
