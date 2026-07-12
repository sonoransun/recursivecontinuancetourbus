"""Linear recurrences by matrix exponentiation.

A linear recurrence

    x_n = c_0 x_{n-1} + c_1 x_{n-2} + ... + c_{d-1} x_{n-d}

advances its state ``[x_n, x_{n-1}, ..., x_{n-d+1}]`` by multiplying with the
*companion matrix*. Powering that matrix by fast (binary) exponentiation lets us
jump to the ``n``-th term in ``O(d^3 log n)`` exact-integer operations instead of
unrolling the recurrence ``n`` times. Fibonacci is the ``d = 2`` special case,
which is why :func:`fib` here is a two-line consequence of :func:`matrix_pow`.
"""

from __future__ import annotations

from typing import List, Sequence

__all__ = ["matrix_pow", "linear_recurrence", "fib"]

Matrix = List[List[int]]


def _identity(size: int) -> Matrix:
    """The ``size x size`` integer identity matrix."""
    return [[1 if i == j else 0 for j in range(size)] for i in range(size)]


def _mat_mul(A: Matrix, B: Matrix) -> Matrix:
    """Multiply two conformable integer matrices exactly."""
    n, k, m = len(A), len(B), len(B[0])
    out = [[0] * m for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        outi = out[i]
        for t in range(k):
            a = Ai[t]
            if a:  # skip the many zero entries in a companion matrix
                Bt = B[t]
                for j in range(m):
                    outi[j] += a * Bt[j]
    return out


def matrix_pow(M: Matrix, n: int) -> Matrix:
    """Raise a square integer matrix to the ``n``-th power by fast exponentiation.

    ``n == 0`` yields the identity; ``n >= 1`` squares-and-multiplies in
    ``O(log n)`` matrix products. All arithmetic is exact.

    >>> matrix_pow([[1, 1], [1, 0]], 5)          # Fibonacci matrix
    [[8, 5], [5, 3]]
    >>> matrix_pow([[2, 0], [0, 3]], 3)          # diagonal powers independently
    [[8, 0], [0, 27]]
    """
    if n < 0:
        raise ValueError("matrix_pow needs a non-negative exponent")
    size = len(M)
    result = _identity(size)
    base = [row[:] for row in M]
    while n > 0:
        if n & 1:
            result = _mat_mul(result, base)
        n >>= 1
        if n:
            base = _mat_mul(base, base)
    return result


def linear_recurrence(coeffs: Sequence[int], init: Sequence[int], n: int) -> int:
    """The ``n``-th term of ``x_n = sum_i coeffs[i] * x_{n-1-i}``.

    ``coeffs = [c_0, ..., c_{d-1}]`` are the recurrence coefficients (``c_0``
    multiplies the most recent term) and ``init = [x_0, x_1, ..., x_{d-1}]`` are
    the ``d`` seed values. Uses the companion matrix and :func:`matrix_pow`, so
    it costs ``O(d^3 log n)`` regardless of how large ``n`` is.

    >>> linear_recurrence([1, 1], [0, 1], 10)            # Fibonacci
    55
    >>> linear_recurrence([1, 1, 1], [0, 0, 1], 9)       # Tribonacci
    44
    >>> linear_recurrence([2, -1], [0, 1], 7)            # x_n = 2x_{n-1} - x_{n-2}
    7
    """
    d = len(coeffs)
    if d == 0:
        raise ValueError("need at least one coefficient")
    if len(init) != d:
        raise ValueError("init must supply exactly len(coeffs) seed values")
    if n < 0:
        raise ValueError("index n must be non-negative")
    if n < d:
        return int(init[n])

    # Companion matrix: first row is the coefficients, the sub-diagonal is 1s.
    C: Matrix = [list(coeffs)]
    for i in range(1, d):
        C.append([1 if j == i - 1 else 0 for j in range(d)])

    # State v_{d-1} = [x_{d-1}, x_{d-2}, ..., x_0]; x_n = (C^(n-d+1) v_{d-1})[0].
    P = matrix_pow(C, n - (d - 1))
    return sum(P[0][j] * int(init[d - 1 - j]) for j in range(d))


def fib(n: int) -> int:
    """The ``n``-th Fibonacci number via the matrix ``[[1, 1], [1, 0]]**n``.

    ``fib(0) = 0``, ``fib(1) = 1``; the ``(0, 1)`` entry of the ``n``-th power is
    exactly ``F_n``, so this is ``O(log n)`` big-integer multiplications.

    >>> [fib(n) for n in range(10)]
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    >>> fib(100)
    354224848179261915075
    """
    if n < 0:
        raise ValueError("fib is defined here for n >= 0")
    return matrix_pow([[1, 1], [1, 0]], n)[0][1]
