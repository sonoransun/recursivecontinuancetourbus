import sys

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tourbus.recursion import ackermann, hyperoperation, mccarthy91, y_combinator


# --- Ackermann ------------------------------------------------------------- #

# A(m, n) reference table for small arguments.
_ACKERMANN_TABLE = {
    (0, 0): 1, (0, 1): 2, (0, 4): 5,
    (1, 0): 2, (1, 1): 3, (1, 5): 7,
    (2, 0): 3, (2, 2): 7, (2, 3): 9,
    (3, 0): 5, (3, 3): 61, (3, 4): 125, (3, 7): 1021,
}


@pytest.mark.parametrize(("mn", "expected"), sorted(_ACKERMANN_TABLE.items()))
def test_ackermann_small_table(mn, expected):
    assert ackermann(*mn) == expected


def test_ackermann_has_closed_forms():
    for n in range(6):
        assert ackermann(1, n) == n + 2         # A(1, n) = n + 2
        assert ackermann(2, n) == 2 * n + 3     # A(2, n) = 2n + 3
        assert ackermann(3, n) == 2 ** (n + 3) - 3  # A(3, n) = 2^(n+3) - 3


def test_ackermann_never_uses_python_recursion():
    # A(3, 6) nests far deeper than Python's call-stack limit would allow if the
    # implementation recursed; the explicit stack must handle it fine.
    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(200)
    try:
        assert ackermann(3, 6) == 509
    finally:
        sys.setrecursionlimit(limit)


# --- hyperoperations ------------------------------------------------------- #

def test_hyperoperation_ladder():
    assert hyperoperation(0, 9, 4) == 5          # successor: b + 1
    assert hyperoperation(1, 3, 4) == 7          # addition
    assert hyperoperation(2, 3, 4) == 12         # multiplication
    assert hyperoperation(3, 3, 3) == 27         # exponentiation: 3**3
    assert hyperoperation(3, 2, 10) == 1024
    # Tetration is level 4; 3^^3 = 3**(3**3) = 3**27 is the famous big value.
    assert hyperoperation(4, 3, 3) == 7625597484987
    assert hyperoperation(4, 2, 3) == 16         # 2^^3 = 2**(2**2) = 2**4
    assert hyperoperation(4, 2, 2) == 4          # 2^^2 = 2**2


@given(st.integers(min_value=0, max_value=8), st.integers(min_value=0, max_value=8))
def test_hyperoperation_low_levels_agree_with_operators(a, b):
    assert hyperoperation(0, a, b) == b + 1
    assert hyperoperation(1, a, b) == a + b
    assert hyperoperation(2, a, b) == a * b
    assert hyperoperation(3, a, b) == a ** b


def test_hyperoperation_guards_explosive_inputs():
    with pytest.raises(ValueError):
        hyperoperation(4, 3, 4)      # 3^^4 has trillions of digits
    with pytest.raises(ValueError):
        hyperoperation(4, 10, 3)     # large base, still explosive
    with pytest.raises(ValueError):
        hyperoperation(5, 2, 2)      # pentation and beyond are refused


# --- the Y combinator ------------------------------------------------------ #

def test_y_combinator_factorial_without_self_reference():
    fac = y_combinator()(lambda f: lambda k: 1 if k == 0 else k * f(k - 1))
    assert fac(0) == 1
    assert fac(10) == 3628800


def test_y_combinator_fibonacci():
    fib = y_combinator()(lambda f: lambda k: k if k < 2 else f(k - 1) + f(k - 2))
    assert [fib(k) for k in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


# --- McCarthy 91 ----------------------------------------------------------- #

@given(st.integers(min_value=-50, max_value=500))
def test_mccarthy91_closed_form(n):
    expected = 91 if n <= 100 else n - 10
    assert mccarthy91(n) == expected


def test_mccarthy91_is_91_through_100():
    assert all(mccarthy91(n) == 91 for n in range(0, 101))
    assert mccarthy91(101) == 91  # 101 - 10
    assert mccarthy91(200) == 190
