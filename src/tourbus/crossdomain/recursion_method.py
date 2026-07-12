"""The recursion method: a lattice Green's function IS a continued fraction.

Haydock's *recursion method* (condensed-matter physics) computes the local
density of states of a tight-binding Hamiltonian without ever diagonalizing it.
The trick is the **Lanczos** recursion, which tridiagonalizes ``H`` around a
starting site into a chain of coefficients ``a_n`` (on-site) and ``b_n^2``
(hopping). The diagonal site Green's function is then, exactly, a continued
fraction in those coefficients::

    G_00(z) = 1 / (z - a0 - b1^2 / (z - a1 - b2^2 / (z - a2 - ...)))

This is the very ``h_n = a_n h_{n-1} - b_n^2 h_{n-2}`` three-term recurrence of
the Huckel secular determinant (:mod:`tourbus.crossdomain.huckel`) and of every
continued-fraction convergent — here it produces a *resolvent*. Two payoffs:

* the poles of the terminating continued fraction are the exact eigenvalues,
  the same ``2 cos(k pi / (n+1))`` spectrum as a Huckel polyene; and
* the **Bethe lattice** (a tree of coordination ``q``) closes the recursion on
  itself in one step, so its Green's function is a single quadratic surd — the
  self-energy that a whole infinite lattice contributes to one site.

Everything on the exact (rational-energy) path stays in :class:`fractions.Fraction`
or :class:`~tourbus.cf.core.QuadraticSurd`; the spectral (real-energy) path uses
``cmath`` for the retarded ``E + i*eta`` resolvent.
"""

from __future__ import annotations

import cmath
import math
from fractions import Fraction
from typing import Sequence

from ..cf.core import QuadraticSurd

__all__ = [
    "lanczos_coefficients",
    "green_function_cf",
    "local_dos",
    "spectral_poles",
    "chain_hamiltonian",
    "ring_hamiltonian",
    "path_from_edges",
    "bethe_self_energy",
    "bethe_lattice_green",
    "bethe_lattice_dos",
]


# --------------------------------------------------------------------------- #
#  Tight-binding Hamiltonians (integer nearest-neighbour hopping, t = 1).
# --------------------------------------------------------------------------- #

def chain_hamiltonian(n: int) -> list[list[int]]:
    """Open linear chain of ``n`` sites (a path graph), hopping ``t = 1``.

    >>> chain_hamiltonian(3)
    [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    """
    H = [[0] * n for _ in range(n)]
    for i in range(n - 1):
        H[i][i + 1] = H[i + 1][i] = 1
    return H


def ring_hamiltonian(n: int) -> list[list[int]]:
    """Periodic ring of ``n`` sites (a cycle graph ``C_n``), hopping ``t = 1``.

    >>> ring_hamiltonian(4)
    [[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]]
    """
    H = chain_hamiltonian(n)
    if n >= 3:
        H[0][n - 1] = H[n - 1][0] = 1
    return H


def path_from_edges(edges: Sequence[tuple[int, int]], n: int) -> list[list[int]]:
    """Integer adjacency Hamiltonian on ``n`` sites for an explicit edge list.

    >>> path_from_edges([(0, 1), (1, 2), (2, 0)], 3)   # a triangle
    [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    """
    H = [[0] * n for _ in range(n)]
    for i, j in edges:
        H[i][j] = H[j][i] = 1
    return H


# --------------------------------------------------------------------------- #
#  Exact Lanczos tridiagonalization.
# --------------------------------------------------------------------------- #

def _matvec(H: Sequence[Sequence], v: Sequence[Fraction]) -> list[Fraction]:
    return [sum(Fraction(H[i][j]) * v[j] for j in range(len(v))) for i in range(len(v))]


def _dot(u: Sequence[Fraction], v: Sequence[Fraction]) -> Fraction:
    return sum(x * y for x, y in zip(u, v))


def lanczos_coefficients(
    H: Sequence[Sequence], start: int, *, max_steps: int | None = None
) -> tuple[list[Fraction], list[Fraction]]:
    """Exact (unnormalized) Lanczos coefficients ``a_n`` and ``b_n^2`` from ``start``.

    Runs the recurrence ``u_{-1} = 0``, ``u_0 = e_start`` and, at each step,

        a_n   = <u_n, H u_n> / <u_n, u_n>
        b_n^2 = <u_n, u_n> / <u_{n-1}, u_{n-1}>              (b_0^2 = 0)
        u_{n+1} = H u_n - a_n u_n - b_n^2 u_{n-1},

    terminating when the Krylov space is exhausted (``<u_m, u_m> = 0``). Returns
    ``(a[0..m-1], b2[1..m-1])`` as exact :class:`~fractions.Fraction`. ``b2`` has
    one fewer entry than ``a``.

    >>> lanczos_coefficients(chain_hamiltonian(2), 0)
    ([Fraction(0, 1), Fraction(0, 1)], [Fraction(1, 1)])
    >>> a, b2 = lanczos_coefficients(chain_hamiltonian(4), 0)
    >>> a, b2
    ([Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)], [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)])
    """
    n = len(H)
    u_prev = [Fraction(0)] * n
    u_cur = [Fraction(0)] * n
    u_cur[start] = Fraction(1)
    norm_prev = Fraction(0)
    norm_cur = _dot(u_cur, u_cur)

    a: list[Fraction] = []
    b2: list[Fraction] = []
    step = 0
    while max_steps is None or step < max_steps:
        Hu = _matvec(H, u_cur)
        a_n = _dot(u_cur, Hu) / norm_cur
        a.append(a_n)
        bn2 = Fraction(0) if step == 0 else norm_cur / norm_prev
        if step >= 1:
            b2.append(bn2)
        u_next = [Hu[i] - a_n * u_cur[i] - bn2 * u_prev[i] for i in range(n)]
        norm_next = _dot(u_next, u_next)
        if norm_next == 0:
            break
        u_prev, u_cur = u_cur, u_next
        norm_prev, norm_cur = norm_cur, norm_next
        step += 1
    return a, b2


# --------------------------------------------------------------------------- #
#  The continued-fraction Green's function.
# --------------------------------------------------------------------------- #

def green_function_cf(a: Sequence, b2: Sequence, z):
    """Evaluate the terminating Green's-function continued fraction at ``z``.

    ``z`` may be an exact :class:`~fractions.Fraction` (rational energy: the
    result is a Fraction) or a Python ``complex`` (a retarded ``E + i*eta``
    resolvent: the result is a ``complex``). Folded bottom-up so the arithmetic
    stays in whichever field ``z`` lives in.

    >>> a, b2 = lanczos_coefficients(chain_hamiltonian(2), 0)
    >>> green_function_cf(a, b2, Fraction(2))
    Fraction(2, 3)
    """
    m = len(a)
    if m == 0:
        raise ValueError("need at least one coefficient")
    acc = z - a[m - 1]
    for k in range(m - 2, -1, -1):
        acc = z - a[k] - b2[k] / acc
    return 1 / acc


def local_dos(
    H: Sequence[Sequence], start: int, energies: Sequence[float], eta: float = 1e-3
) -> list[float]:
    """Local density of states ``-Im G_00(E + i*eta) / pi`` at each energy.

    >>> H = chain_hamiltonian(2)
    >>> vals = local_dos(H, 0, [-1.0, 0.0, 1.0], eta=0.1)
    >>> [round(v, 4) for v in vals]        # peaks at the +/-1 eigenvalues
    [1.5955, 0.0315, 1.5955]
    """
    a, b2 = lanczos_coefficients(H, start)
    out: list[float] = []
    for E in energies:
        g = green_function_cf(a, b2, complex(E, eta))
        out.append(-g.imag / math.pi)
    return out


# --------------------------------------------------------------------------- #
#  Exact spectral poles via Sturm-sequence bisection.
# --------------------------------------------------------------------------- #

def _sturm_changes(a: Sequence[Fraction], b2: Sequence[Fraction], x: Fraction) -> int:
    """Sign changes in the leading principal minors of ``x*I - J`` at ``x``.

    Equal to the number of eigenvalues of the Jacobi matrix ``J`` (diagonal
    ``a``, off-diagonal squares ``b2``) that are strictly greater than ``x``.
    """
    m = len(a)
    d_prev2 = Fraction(1)                 # d_0
    d_prev = x - a[0]                     # d_1
    prev_sign = 1
    sign = _sign(d_prev, prev_sign)
    changes = (sign != prev_sign)
    prev_sign = sign
    for k in range(2, m + 1):
        d = (x - a[k - 1]) * d_prev - b2[k - 2] * d_prev2
        sign = _sign(d, prev_sign)
        changes += (sign != prev_sign)
        prev_sign = sign
        d_prev2, d_prev = d_prev, d
    return changes


def _sign(value: Fraction, prev_sign: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return -prev_sign        # exact zero: adopt the opposite of the previous sign


def spectral_poles(a: Sequence[Fraction], b2: Sequence[Fraction]) -> list[float]:
    """The poles of the Green's-function continued fraction, ascending.

    These are the eigenvalues of the Jacobi (tridiagonal) matrix built from the
    Lanczos coefficients — the roots of the continued fraction's denominator.
    The characteristic Sturm sequence is evaluated in *exact* rational
    arithmetic, so each eigenvalue is bracketed rigorously and then bisected to
    a float (the eigenvalues themselves are generally irrational, e.g. the
    ``2 cos(k pi / (n+1))`` polyene spectrum).

    >>> a, b2 = lanczos_coefficients(chain_hamiltonian(2), 0)
    >>> spectral_poles(a, b2)
    [-1.0, 1.0]
    >>> a, b2 = lanczos_coefficients(chain_hamiltonian(3), 0)
    >>> [round(p, 6) for p in spectral_poles(a, b2)]     # {0, +/- sqrt(2)}
    [-1.414214, 0.0, 1.414214]
    """
    a = [Fraction(x) for x in a]
    b2 = [Fraction(x) for x in b2]
    m = len(a)
    if m == 0:
        return []
    # Gershgorin bracket: a rational bound enclosing every eigenvalue.
    radius = Fraction(0)
    for i in range(m):
        r = Fraction(0)
        if i > 0:
            r += _isqrt_ceil(b2[i - 1])
        if i < m - 1:
            r += _isqrt_ceil(b2[i])
        radius = max(radius, abs(a[i]) + r)
    lo0, hi0 = -radius - 1, radius + 1
    tol = Fraction(1, 10 ** 15)

    def less_than(x: Fraction) -> int:
        return m - _sturm_changes(a, b2, x)

    poles: list[float] = []
    for k in range(1, m + 1):
        lo, hi = lo0, hi0
        while hi - lo > tol:
            mid = (lo + hi) / 2
            if less_than(mid) >= k:
                hi = mid
            else:
                lo = mid
        poles.append(float((lo + hi) / 2))
    return poles


def _isqrt_ceil(x: Fraction) -> Fraction:
    """A rational upper bound for ``sqrt(x)`` (only used to size the bracket)."""
    r = math.isqrt(int(x) + 1) + 1
    return Fraction(r)


# --------------------------------------------------------------------------- #
#  The Bethe lattice: a self-consistent continued fraction closed in one step.
# --------------------------------------------------------------------------- #

def bethe_self_energy(E: int, coordination: int, t: int = 1) -> QuadraticSurd:
    """Exact self-energy ``Delta`` of a Bethe lattice at integer energy ``E``.

    On a Cayley tree of coordination ``q`` every branch looks identical, so the
    recursion method closes on itself: ``Delta`` obeys the quadratic
    ``(q-1) Delta^2 - E Delta + t^2 = 0``. The retarded (physical, decaying)
    root is ``Delta = (E - sign(E) sqrt(E^2 - 4(q-1)t^2)) / (2(q-1))``, an exact
    :class:`~tourbus.cf.core.QuadraticSurd` whenever ``E`` sits outside the band
    (``E^2 >= 4(q-1)t^2``).

    >>> bethe_self_energy(3, 2)                        # 1-D chain (q = 2)
    QuadraticSurd(a=Fraction(3, 2), b=Fraction(-1, 2), D=5)
    >>> print(bethe_self_energy(4, 3))                 # coordination 3
    1 - 1/2*sqrt(2)
    """
    q = coordination
    if q < 2:
        raise ValueError("coordination must be >= 2")
    disc = E * E - 4 * (q - 1) * t * t
    if disc < 0:
        raise ValueError(
            "energy is inside the band; the self-energy is complex there "
            "(use bethe_lattice_green with E + i*eta)"
        )
    Q = 2 * (q - 1)
    root = QuadraticSurd.from_pqd(E, disc, Q)          # (E + sqrt(disc)) / Q
    return root.conjugate() if E >= 0 else root         # subtract sign(E)*sqrt


def bethe_lattice_green(z, coordination: int, t: float = 1.0) -> complex:
    """Retarded Bethe-lattice site Green's function ``G(z)`` (``cmath``).

    Solves the same quadratic for complex ``z = E + i*eta`` and returns
    ``G = 1 / (z - q Delta)`` on the retarded sheet (``Im G <= 0``), so that
    ``-Im G / pi`` is a non-negative density of states.

    >>> g = bethe_lattice_green(complex(0.0, 1e-6), 3, 1.0)
    >>> round(-g.imag / math.pi, 6)                    # DOS at band centre
    0.150053
    """
    q = coordination
    s = cmath.sqrt(z * z - 4 * (q - 1) * t * t)
    for disc in (s, -s):
        delta = (z - disc) / (2 * (q - 1))
        g = 1 / (z - q * delta)
        if g.imag <= 0:
            return g
    # Fallback (real axis, both sheets real): the sign-of-E convention.
    disc = s if z.real >= 0 else -s
    delta = (z - disc) / (2 * (q - 1))
    return 1 / (z - q * delta)


def bethe_lattice_dos(E: float, coordination: int, t: float = 1.0) -> float:
    """Exact Bethe-lattice density of states (closed form).

    ``rho(E) = q sqrt(4(q-1)t^2 - E^2) / (2 pi (q^2 t^2 - E^2))`` inside the band
    ``|E| < 2 sqrt(q-1) t``, and ``0`` outside. For ``q = 2`` this collapses to
    the 1-D chain result ``1 / (pi sqrt(4 t^2 - E^2))``.

    >>> round(bethe_lattice_dos(0.0, 2, 1.0) - 1 / (2 * math.pi), 15)
    0.0
    >>> bethe_lattice_dos(3.0, 3, 1.0)                 # outside the band
    0.0
    >>> round(bethe_lattice_dos(0.0, 3, 1.0) - 2 ** 0.5 / (3 * math.pi), 15)
    0.0
    """
    q = coordination
    edge = 4 * (q - 1) * t * t
    if E * E >= edge:
        return 0.0
    return q * math.sqrt(edge - E * E) / (2 * math.pi * (q * q * t * t - E * E))
