"""The Gauss-Kuzmin-Wirsing constant, computed from the transfer operator.

The Casino promised that continued-fraction digits converge to the Gauss-Kuzmin
distribution — but *how fast*? The answer is governed by the **transfer operator**
of the Gauss map,

    (L f)(x) = sum_{n>=1}  1/(n+x)^2 * f(1/(n+x)).

Its largest eigenvalue is exactly 1 (with the Gauss density as eigenfunction);
the *second* eigenvalue is the **Gauss-Kuzmin-Wirsing constant**

    lambda = -0.3036300289873...

and the discrepancy in the Gauss-Kuzmin theorem decays like ``|lambda|^n``. Wirsing
computed it in 1974; no closed form is known.

We recover it here with no special functions: discretize ``L`` as a matrix on a
grid (collocation with linear interpolation), then power-iterate starting from a
*mean-zero* function. Because ``L`` preserves the integral, the invariant
(eigenvalue-1) component of a mean-zero start is zero, so the iteration converges
to the second eigenvalue directly.
"""

from __future__ import annotations

import math

__all__ = ["GKW_CONSTANT", "transfer_matrix", "second_eigenvalue", "leading_eigenvalue"]

#: The reference value of the Gauss-Kuzmin-Wirsing constant (Wirsing, 1974).
GKW_CONSTANT = -0.30366300289873265859744812190


def transfer_matrix(grid: int = 320, terms: int = 1600) -> tuple[list[float], list[list[float]]]:
    """Collocation matrix of the Gauss-map transfer operator on a midpoint grid.

    Returns ``(nodes, A)`` with ``A[i][j]`` such that ``(A @ f)[i]`` approximates
    ``(L f)(nodes[i])`` when ``f`` is sampled on ``nodes``.
    """
    nodes = [(i + 0.5) / grid for i in range(grid)]
    A = [[0.0] * grid for _ in range(grid)]
    for i in range(grid):
        x = nodes[i]
        row = A[i]
        for n in range(1, terms + 1):
            denom = n + x
            weight = 1.0 / (denom * denom)
            y = 1.0 / denom
            t = y * grid - 0.5           # position of y on the midpoint grid
            j = math.floor(t)
            frac = t - j
            if j < 0:
                j, frac = 0, 0.0
            elif j >= grid - 1:
                j, frac = grid - 2, 1.0
            row[j] += weight * (1.0 - frac)
            row[j + 1] += weight * frac
    return nodes, A


def _matvec(A: list[list[float]], v: list[float]) -> list[float]:
    return [math.fsum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]


def _demean(v: list[float]) -> list[float]:
    m = math.fsum(v) / len(v)
    return [t - m for t in v]


def second_eigenvalue(grid: int = 320, terms: int = 1600, iters: int = 80) -> float:
    """Estimate the Gauss-Kuzmin-Wirsing constant (the second eigenvalue of L).

    >>> lam = second_eigenvalue(grid=160, terms=800, iters=60)
    >>> abs(lam - GKW_CONSTANT) < 0.01
    True
    """
    nodes, A = transfer_matrix(grid, terms)
    v = _demean([x - 0.5 for x in nodes])
    nrm = math.sqrt(math.fsum(t * t for t in v)) or 1.0
    v = [t / nrm for t in v]
    lam = 0.0
    for _ in range(iters):
        w = _demean(_matvec(A, v))
        lam = math.fsum(w[i] * v[i] for i in range(len(v)))  # Rayleigh quotient
        nrm = math.sqrt(math.fsum(t * t for t in w)) or 1.0
        v = [t / nrm for t in w]
    return lam


def leading_eigenvalue(grid: int = 320, terms: int = 1600, iters: int = 60) -> float:
    """The leading eigenvalue of L, which is exactly 1 (a discretization check).

    >>> abs(leading_eigenvalue(grid=160, terms=800, iters=40) - 1.0) < 0.01
    True
    """
    nodes, A = transfer_matrix(grid, terms)
    v = [1.0] * grid
    nrm = math.sqrt(math.fsum(t * t for t in v))
    v = [t / nrm for t in v]
    lam = 0.0
    for _ in range(iters):
        w = _matvec(A, v)
        lam = math.fsum(w[i] * v[i] for i in range(len(v)))
        nrm = math.sqrt(math.fsum(t * t for t in w)) or 1.0
        v = [t / nrm for t in w]
    return lam
