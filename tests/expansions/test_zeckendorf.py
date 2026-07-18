from hypothesis import given, settings
from hypothesis import strategies as st

from tourbus.cf.core import QuadraticSurd
from tourbus.expansions.zeckendorf import (
    base_phi_digits,
    base_phi_value,
    fibonacci_upto,
    from_zeckendorf,
    is_zeckendorf,
    zeckendorf,
    zeckendorf_indices,
)


# --- Zeckendorf representation -------------------------------------------- #

def test_zeckendorf_pins():
    assert zeckendorf(100) == [89, 8, 3]
    assert zeckendorf(1) == [1]
    assert zeckendorf(12) == [8, 3, 1]
    assert zeckendorf_indices(100) == [11, 6, 4]
    assert zeckendorf_indices(1) == [2]
    assert fibonacci_upto(20) == [1, 2, 3, 5, 8, 13]
    assert fibonacci_upto(0) == []


@given(st.integers(min_value=1, max_value=100_000))
@settings(max_examples=400)
def test_zeckendorf_round_trip(n):
    summands = zeckendorf(n)
    assert from_zeckendorf(summands) == n
    assert is_zeckendorf(summands)
    assert summands == sorted(summands, reverse=True)


@given(st.integers(min_value=1, max_value=100_000))
@settings(max_examples=400)
def test_zeckendorf_indices_non_consecutive(n):
    indices = zeckendorf_indices(n)
    assert indices == sorted(indices, reverse=True)
    assert all(hi - lo >= 2 for lo, hi in zip(indices[1:], indices))


def test_is_zeckendorf_non_examples():
    assert is_zeckendorf([89, 8, 3]) is True
    assert is_zeckendorf([13, 5, 1]) is True
    assert is_zeckendorf([]) is True
    assert is_zeckendorf([8, 5]) is False      # F_6, F_5 consecutive
    assert is_zeckendorf([2, 1]) is False      # F_3, F_2 consecutive
    assert is_zeckendorf([13, 8]) is False     # F_7, F_6 consecutive
    assert is_zeckendorf([4]) is False         # 4 is not a Fibonacci number
    assert is_zeckendorf([8, 8]) is False      # not distinct


def test_zeckendorf_domain():
    for bad in (0, -1):
        try:
            zeckendorf(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for n={bad}")


# --- Bergman base-phi ----------------------------------------------------- #

def test_base_phi_pins():
    assert base_phi_digits(1) == "1"
    assert base_phi_digits(2) == "10.01"
    assert base_phi_digits(3) == "100.01"
    assert base_phi_digits(4) == "101.01"
    assert base_phi_digits(5) == "1000.1001"


def test_base_phi_round_trip_and_standard_form():
    for n in range(1, 201):
        digits = base_phi_digits(n)
        assert "11" not in digits, (n, digits)
        assert base_phi_value(digits) == QuadraticSurd.make(n, 0, 1)


def test_base_phi_value_ignores_spaces():
    assert base_phi_value("1 0 0 . 0 1") == QuadraticSurd.make(3, 0, 1)
    assert base_phi_value("101.01") == QuadraticSurd.make(4, 0, 1)
