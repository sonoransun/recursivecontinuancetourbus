from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tourbus.cf.core import QuadraticSurd
from tourbus.crossdomain.fibonacci_chain import fibonacci_word
from tourbus.expansions.ostrowski import (
    beatty,
    characteristic_word,
    from_ostrowski,
    is_legal_ostrowski,
    ostrowski,
    three_distance_check,
)

# Continued fractions long enough that some q_k exceeds any n <= 5000: 30+ terms
# with every a_k >= 1 push the denominators past a million (they grow >= Fibonacci).
_cf = st.builds(
    lambda a0, tail: [a0] + tail,
    st.integers(min_value=0, max_value=3),
    st.lists(st.integers(min_value=1, max_value=6), min_size=30, max_size=40),
)

_FIXED_CFS = (
    [0] + [1] * 30,              # 1/phi -> Zeckendorf
    [1] + [2] * 30,              # sqrt(2)
    [2, 1, 3, 1, 4, 1, 5, 1, 2, 3] * 4,
)


@given(st.integers(min_value=0, max_value=5000), _cf)
@settings(max_examples=300)
def test_round_trip_and_legal(n, cf):
    digits = ostrowski(n, cf)
    assert from_ostrowski(digits, cf) == n
    assert is_legal_ostrowski(digits, cf)


@given(st.integers(min_value=0, max_value=5000))
@settings(max_examples=200)
def test_round_trip_fixed_cfs(n):
    for cf in _FIXED_CFS:
        digits = ostrowski(n, cf)
        assert from_ostrowski(digits, cf) == n
        assert is_legal_ostrowski(digits, cf)


@given(st.integers(min_value=1, max_value=5000))
@settings(max_examples=200)
def test_zeckendorf_shape(n):
    cf = [0] + [1] * 30
    digits = ostrowski(n, cf)
    # All digits binary and no two adjacent 1s: exactly Zeckendorf's theorem.
    assert all(b in (0, 1) for b in digits)
    assert all(not (digits[i] and digits[i + 1]) for i in range(len(digits) - 1))
    assert from_ostrowski(digits, cf) == n


def test_ostrowski_pins():
    assert ostrowski(12, [0] + [1] * 10) == [0, 1, 0, 1, 0, 1]   # 12 = 8 + 3 + 1
    assert ostrowski(10, [1] + [2] * 8) == [0, 0, 2]             # 10 = 2 * 5
    assert ostrowski(0, [0] + [1] * 5) == []


def test_illegal_rejected():
    cf = [1] + [2] * 8
    assert not is_legal_ostrowski([2], cf)          # b_1 = a_1, must be strictly less
    assert not is_legal_ostrowski([1, 2], cf)       # b_2 = a_2 but b_1 != 0 (carry rule)
    assert not is_legal_ostrowski([-1], cf)         # negative digit
    assert not is_legal_ostrowski([0, 3], cf)       # b_2 > a_2
    assert is_legal_ostrowski([1, 0, 1], cf)        # a legal representation
    assert is_legal_ostrowski([], cf)               # the empty rep of 0


def test_too_short_raises():
    with pytest.raises(ValueError):
        ostrowski(1000, [1, 2])            # denominators only reach 2
    with pytest.raises(ValueError):
        ostrowski(-1, [0] + [1] * 5)
    with pytest.raises(ValueError):
        is_legal_ostrowski([1, 1, 1], [0, 1])


def test_beatty_pins():
    assert beatty(QuadraticSurd.make(0, 1, 2), 5) == [1, 2, 4, 5, 7]    # floor(k*sqrt2)
    assert beatty(Fraction(3, 2), 4) == [1, 3, 4, 6]
    assert beatty(QuadraticSurd.from_pqd(1, 5, 2), 8) == [1, 3, 4, 6, 8, 9, 11, 12]


def test_beatty_complementary():
    # 1/sqrt2 + 1/(2 + sqrt2) = 1, so the two Beatty sequences partition N.
    r = QuadraticSurd.make(0, 1, 2)     # sqrt(2)
    s = QuadraticSurd.make(2, 1, 2)     # 2 + sqrt(2)
    a = set(beatty(r, 80))
    b = set(beatty(s, 80))
    assert a.isdisjoint(b)
    assert set(range(1, 40)).issubset(a | b)


def test_characteristic_word_is_fibonacci():
    fib = fibonacci_word(9).replace("a", "1").replace("b", "0")   # length 89
    cf = [0] + [1] * 40
    for length in range(0, 60):
        assert characteristic_word(cf, length) == fib[:length]


def test_characteristic_word_domain():
    with pytest.raises(ValueError):
        characteristic_word([1, 2, 3], 5)   # value 10/7 > 1, not a Sturmian slope


@given(st.integers(min_value=2, max_value=40))
@settings(max_examples=40)
def test_three_distance(n_points):
    assert three_distance_check([0, 1, 2, 1, 3, 1, 4, 2], n_points)
    assert three_distance_check([0] + [1] * 8, n_points)
