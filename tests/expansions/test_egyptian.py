from fractions import Fraction

from hypothesis import given, settings
from hypothesis import strategies as st

from tourbus.expansions.egyptian import (
    egyptian_eval,
    erdos_straus,
    fibonacci_sylvester,
    odd_greedy,
    sylvester_sequence,
)


@st.composite
def proper_fractions(draw):
    """Fractions strictly inside ``(0, 1)`` as ``p/q`` with ``1 <= p < q <= 500``."""
    q = draw(st.integers(min_value=2, max_value=500))
    p = draw(st.integers(min_value=1, max_value=q - 1))
    return Fraction(p, q)


# --- Fibonacci-Sylvester greedy ------------------------------------------- #

def test_fibonacci_sylvester_pins():
    assert fibonacci_sylvester(Fraction(4, 5)) == [2, 4, 20]
    assert fibonacci_sylvester(Fraction(3, 4)) == [2, 4]
    # The doubly-exponential cautionary tale, pinned in full.
    assert fibonacci_sylvester(Fraction(5, 121)) == [
        25, 757, 763309, 873960180913, 1527612795642093418846225,
    ]
    # ... yet a shorter non-greedy expansion exists.
    assert Fraction(1, 33) + Fraction(1, 121) + Fraction(1, 363) == Fraction(5, 121)


@given(proper_fractions())
@settings(max_examples=400)
def test_fibonacci_sylvester_reconstructs(x):
    denoms = fibonacci_sylvester(x)
    assert egyptian_eval(denoms) == x


@given(proper_fractions())
@settings(max_examples=400)
def test_fibonacci_sylvester_strictly_increasing(x):
    denoms = fibonacci_sylvester(x)
    assert len(set(denoms)) == len(denoms)
    assert all(lo < hi for lo, hi in zip(denoms, denoms[1:]))
    assert all(d >= 2 for d in denoms)


def test_egyptian_eval_examples():
    assert egyptian_eval([2, 4, 20]) == Fraction(4, 5)
    assert egyptian_eval([]) == Fraction(0)


# --- Sylvester's sequence ------------------------------------------------- #

def test_sylvester_sequence_pin():
    assert sylvester_sequence(6) == [2, 3, 7, 43, 1807, 3263443]
    assert sylvester_sequence(0) == []


@given(st.integers(min_value=1, max_value=9))
def test_sylvester_recurrence(n):
    seq = sylvester_sequence(n)
    assert seq[0] == 2
    for a, b in zip(seq, seq[1:]):
        assert b == a * a - a + 1


@given(st.integers(min_value=1, max_value=9))
def test_sylvester_partial_sum_identity(n):
    # 1/s_1 + ... + 1/s_n = 1 - 1/(s_{n+1} - 1)
    partial = egyptian_eval(sylvester_sequence(n))
    next_term = sylvester_sequence(n + 1)[-1]
    assert partial == 1 - Fraction(1, next_term - 1)


# --- Erdos-Straus --------------------------------------------------------- #

def test_erdos_straus_pins():
    assert erdos_straus(5) == (2, 4, 20)
    assert erdos_straus(2) == (1, 2, 2)
    assert erdos_straus(4) == (2, 3, 6)


def test_erdos_straus_sample():
    for n in [2, 4] + list(range(3, 121)):
        triple = erdos_straus(n)
        assert triple is not None, n
        a, b, c = triple
        assert a <= b <= c
        assert a >= 1
        assert Fraction(1, a) + Fraction(1, b) + Fraction(1, c) == Fraction(4, n)


def test_erdos_straus_domain():
    for bad in (1, 0, -3):
        try:
            erdos_straus(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for n={bad}")


# --- Odd greedy (open termination: only fast-terminating pins are probed) -- #

def test_odd_greedy_pins():
    assert odd_greedy(Fraction(2, 3)) == [3, 5, 9, 45]
    assert odd_greedy(Fraction(3, 7)) == [3, 11, 231]
    assert odd_greedy(Fraction(1, 3)) == [3]


def test_odd_greedy_valid_when_it_terminates():
    # Small odd-denominator inputs that are known to terminate quickly; if a
    # result comes back it must be increasing, odd, distinct, and exact.
    for q in (3, 5, 7, 9):
        for p in range(1, q):
            result = odd_greedy(Fraction(p, q), max_terms=40)
            if result is None:
                continue
            assert all(d % 2 == 1 for d in result)
            assert len(set(result)) == len(result)
            assert result == sorted(result)
            assert egyptian_eval(result) == Fraction(p, q)
