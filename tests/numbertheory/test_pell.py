from hypothesis import given, settings
from hypothesis import strategies as st

from tourbus_testkit import st_nonsquare_d
from tourbus.cf.expand import cf_from_quadratic
from tourbus.numbertheory.pell import (
    PellSolution,
    fundamental_solution,
    solutions,
)


def test_known_fundamentals():
    assert (fundamental_solution(2).x, fundamental_solution(2).y) == (3, 2)
    assert fundamental_solution(2).verify(1)
    assert (fundamental_solution(2, -1).x, fundamental_solution(2, -1).y) == (1, 1)
    assert (fundamental_solution(13).x, fundamental_solution(13).y) == (649, 180)
    assert (
        fundamental_solution(61).x,
        fundamental_solution(61).y,
    ) == (1766319049, 226153980)
    assert (
        fundamental_solution(61, -1).x,
        fundamental_solution(61, -1).y,
    ) == (29718, 3805)


def test_unsolvable_and_degenerate():
    assert fundamental_solution(4) is None       # perfect square
    assert fundamental_solution(9) is None       # perfect square
    assert fundamental_solution(1) is None       # d < 2
    assert fundamental_solution(3, -1) is None   # even period, no -1 solution
    assert fundamental_solution(2, 7) is None    # unsupported target


def test_negative_solvable_iff_odd_period():
    for d in range(2, 120):
        _, period = cf_from_quadratic(0, d, 1)
        if not period:
            continue  # perfect square
        neg = fundamental_solution(d, -1)
        if len(period) % 2 == 1:
            assert neg is not None and neg.verify(-1)
        else:
            assert neg is None


def test_solution_ladder_is_strictly_increasing():
    gen = solutions(2)
    prev = None
    for _ in range(6):
        s = next(gen)
        assert s.verify(1)
        if prev is not None:
            assert s.x > prev.x and s.y > prev.y
        prev = s


def test_empty_ladder_when_no_solution():
    assert list(solutions(3, -1)) == []  # even period: no -1 ladder


@given(st_nonsquare_d())
@settings(max_examples=100)
def test_fundamental_plus_one_verifies(d):
    s = fundamental_solution(d, 1)
    assert s is not None
    assert s.verify(1)
    assert s.x > 0 and s.y > 0


@given(st_nonsquare_d())
@settings(max_examples=100)
def test_ladder_all_verify(d):
    gen = solutions(d, 1)
    for _ in range(4):
        assert next(gen).verify(1)


@given(st_nonsquare_d(), st.sampled_from([1, -1]))
@settings(max_examples=100)
def test_ladder_keeps_target(d, target):
    gen = solutions(d, target)
    got = [next(gen) for _ in range(3)] if fundamental_solution(d, target) else []
    for s in got:
        assert s.verify(target)


def test_pellsolution_is_frozen_and_hashable():
    s = PellSolution(3, 2, 2)
    assert hash(s) == hash(PellSolution(3, 2, 2))
