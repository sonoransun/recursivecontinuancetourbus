from hypothesis import given
from hypothesis import strategies as st

from tourbus.recursion import fib, linear_recurrence, matrix_pow


# --- matrix_pow ------------------------------------------------------------ #

def _naive_pow(M, n):
    size = len(M)
    result = [[1 if i == j else 0 for j in range(size)] for i in range(size)]
    for _ in range(n):
        result = [
            [sum(result[i][k] * M[k][j] for k in range(size)) for j in range(size)]
            for i in range(size)
        ]
    return result


def test_matrix_pow_identity_and_first_power():
    assert matrix_pow([[1, 1], [1, 0]], 0) == [[1, 0], [0, 1]]
    assert matrix_pow([[1, 1], [1, 0]], 1) == [[1, 1], [1, 0]]


@given(st.integers(min_value=0, max_value=40))
def test_matrix_pow_matches_repeated_multiplication(n):
    M = [[1, 1], [1, 0]]
    assert matrix_pow(M, n) == _naive_pow(M, n)


@given(st.integers(min_value=0, max_value=12), st.integers(min_value=0, max_value=12))
def test_matrix_pow_is_a_homomorphism(a, b):
    M = [[2, 1], [1, 1]]
    left = matrix_pow(M, a + b)
    right = matrix_pow(M, a)
    # multiply right @ matrix_pow(M, b)
    Mb = matrix_pow(M, b)
    prod = [
        [sum(right[i][k] * Mb[k][j] for k in range(2)) for j in range(2)]
        for i in range(2)
    ]
    assert left == prod


# --- fib ------------------------------------------------------------------- #

def test_fib_base_and_anchor():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(20) == 6765
    assert fib(100) == 354224848179261915075


@given(st.integers(min_value=0, max_value=200))
def test_fib_satisfies_its_own_recurrence(n):
    assert fib(n + 2) == fib(n + 1) + fib(n)


# --- linear_recurrence ----------------------------------------------------- #

def test_linear_recurrence_reproduces_fibonacci():
    fibs = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    for n, expected in enumerate(fibs):
        assert linear_recurrence([1, 1], [0, 1], n) == expected
        assert linear_recurrence([1, 1], [0, 1], n) == fib(n)


def test_linear_recurrence_reproduces_tribonacci():
    tribs = [0, 0, 1, 1, 2, 4, 7, 13, 24, 44, 81, 149]
    for n, expected in enumerate(tribs):
        assert linear_recurrence([1, 1, 1], [0, 0, 1], n) == expected


def test_linear_recurrence_reproduces_a_signed_recurrence():
    # x_n = 2 x_{n-1} - x_{n-2} with x0=0, x1=1 is just the integers n.
    for n in range(20):
        assert linear_recurrence([2, -1], [0, 1], n) == n


@given(
    st.lists(st.integers(min_value=-4, max_value=4), min_size=1, max_size=4),
    st.integers(min_value=0, max_value=60),
)
def test_linear_recurrence_matches_direct_unrolling(coeffs, n):
    d = len(coeffs)
    init = list(range(1, d + 1))  # arbitrary distinct seeds
    # Unroll the recurrence the slow, obviously-correct way.
    seq = list(init)
    while len(seq) <= n:
        nxt = sum(coeffs[i] * seq[-1 - i] for i in range(d))
        seq.append(nxt)
    assert linear_recurrence(coeffs, init, n) == seq[n]
