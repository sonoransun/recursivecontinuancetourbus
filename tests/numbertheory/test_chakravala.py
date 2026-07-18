from math import isqrt

import pytest

from tourbus.numbertheory.chakravala import (
    ChakravalaStep,
    chakravala,
    chakravala_steps,
)
from tourbus.numbertheory.pell import fundamental_solution


def test_known_fundamentals():
    assert chakravala(61) == (1766319049, 226153980)   # Bhaskara's showpiece
    assert chakravala(67) == (48842, 5967)
    assert chakravala(109) == (158070671986249, 15140424455100)


def test_matches_pell_for_all_small_n():
    for n in range(2, 121):
        if isqrt(n) ** 2 == n:
            continue
        sol = fundamental_solution(n)
        assert chakravala(n) == (sol.x, sol.y), n


def test_every_step_satisfies_the_invariant():
    for n in range(2, 121):
        if isqrt(n) ** 2 == n:
            continue
        for step in chakravala_steps(n):
            assert step.a * step.a - n * step.b * step.b == step.k, n


def test_trace_shape():
    steps = chakravala_steps(61)
    assert steps[0] == ChakravalaStep(8, 1, 3, None)      # initial: m is None
    assert steps[1] == ChakravalaStep(39, 5, -4, 7)       # classical hand step
    assert all(s.m is not None and s.m > 0 for s in steps[1:])
    assert steps[-1].k == 1
    assert all(s.k != 1 for s in steps[:-1])              # stops at first k == 1


def test_rejects_small_n():
    for n in (1, 0, -5):
        with pytest.raises(ValueError):
            chakravala(n)
        with pytest.raises(ValueError):
            chakravala_steps(n)


def test_rejects_perfect_squares():
    for n in (4, 9, 49, 100):
        with pytest.raises(ValueError):
            chakravala(n)
        with pytest.raises(ValueError):
            chakravala_steps(n)


def test_step_is_frozen_and_hashable():
    s = ChakravalaStep(8, 1, 3, None)
    assert hash(s) == hash(ChakravalaStep(8, 1, 3, None))
    with pytest.raises(AttributeError):
        s.a = 9
