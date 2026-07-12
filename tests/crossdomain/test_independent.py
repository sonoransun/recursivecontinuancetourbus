"""Adversarial cross-checks: every crossdomain claim re-derived by a *different*
method than the implementation, so a wrong-but-self-consistent result still fails.
"""

from fractions import Fraction as F
from math import comb

import pytest

from tourbus.crossdomain import huckel as H, hofstadter as HF, cauer as C, routh as R
from tourbus.crossdomain import apery as A, feigenbaum as FB, recursion_method as RM
import tourbus.crossdomain.pade as PADE


# --- tiny independent linear-algebra helpers (no numpy) -------------------- #

def _matmul(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def _trace(m):
    return sum(m[i][i] for i in range(len(m)))


def _roots(coeffs):
    """Durand-Kerner root finder (complex), independent of Routh."""
    n = len(coeffs) - 1
    a = [c / coeffs[0] for c in coeffs]
    rs = [complex(0.4, 0.9) ** k for k in range(n)]
    for _ in range(300):
        new = []
        for i in range(n):
            num = sum(a[j] * rs[i] ** (n - j) for j in range(n + 1))
            den = 1
            for j in range(n):
                if j != i:
                    den *= (rs[i] - rs[j])
            new.append(rs[i] - num / den)
        rs = new
    return rs


# --- chemistry ------------------------------------------------------------- #

def test_butadiene_roots_are_golden_ratio_by_algebra():
    phi = (1 + 5 ** 0.5) / 2
    poly = H.secular_polynomial(4)
    for x in (phi, 1 / phi, -phi, -1 / phi):
        assert abs(sum(c * x ** (4 - i) for i, c in enumerate(poly))) < 1e-9


def test_benzene_energies_match_adjacency_invariants():
    n = 6
    adj = [[0] * n for _ in range(n)]
    for i in range(n):
        adj[i][(i + 1) % n] = adj[(i + 1) % n][i] = 1
    es = H.annulene_energies(n)
    assert abs(sum(es) - _trace(adj)) < 1e-9
    assert abs(sum(e * e for e in es) - _trace(_matmul(adj, adj))) < 1e-9


# --- condensed matter / spectra -------------------------------------------- #

@pytest.mark.parametrize("p,q", [(1, 3), (2, 5), (1, 4), (3, 7), (2, 7)])
def test_harper_spectrum_matches_matrix_invariants(p, q):
    diag = HF.harper_diagonal(p, q, 0.0)
    m = [[0.0] * q for _ in range(q)]
    for i in range(q):
        m[i][i] = diag[i]
    for i in range(q - 1):
        m[i][i + 1] = m[i + 1][i] = 1.0
    sp = HF.harper_spectrum(p, q)
    assert len(sp) == q
    assert abs(sum(sp) - _trace(m)) < 1e-6
    assert abs(sum(e * e for e in sp) - _trace(_matmul(m, m))) < 1e-6


def test_harper_discriminant_matches_exact_polynomials():
    import random
    rng = random.Random(1)
    for e in (rng.uniform(-3, 3) for _ in range(30)):
        assert abs(HF.harper_discriminant(1, 2, e) - (e * e - 4)) < 1e-9
        assert abs(HF.harper_discriminant(1, 3, e) - (e ** 3 - 6 * e)) < 1e-8


def test_greens_function_dimer_by_direct_inverse():
    # dimer H=[[0,1],[1,0]]; G(z)[0,0] = z/(z^2-1); at z=2 -> 2/3
    a, b2 = RM.lanczos_coefficients(RM.chain_hamiltonian(2), 0)
    assert RM.green_function_cf(a, b2, F(2)) == F(2, 3)


@pytest.mark.slow
def test_bethe_dos_normalizes_for_bounded_coordination():
    import math
    for cn in (3, 4, 5):
        edge = 2 * math.sqrt(cn - 1)
        n = 40000
        s = sum(RM.bethe_lattice_dos(-edge + 2 * edge * (i + 0.5) / n, cn, 1.0)
                for i in range(n)) * (2 * edge / n)
        assert abs(s - 1.0) < 2e-3


# --- engineering / analysis ------------------------------------------------ #

def test_cauer_fold_matches_input_rational_exactly():
    el = C.cauer_ladder([24, 0, 6, 0], [12, 0, 1])
    assert el == [F(2), F(3), F(4)]
    for s in (2, 3, 5, 7, 11):
        folded = C.ladder_impedance(el, F(s))
        assert folded == F(24 * s ** 3 + 6 * s, 12 * s ** 2 + 1)


@pytest.mark.parametrize("poly,stable", [
    ([1, 1, 1], True), ([1, 2, 2, 1], True), ([1, 3, 3, 1], True),
    ([1, 2, 2, 40], False), ([1, 0, 1], False), ([1, -1, 1], False),
])
def test_routh_matches_actual_root_locations(poly, stable):
    rr = _roots(poly)
    actually_stable = all(r.real < -1e-9 for r in rr)
    assert actually_stable == stable        # sanity: our reference agrees with the label
    assert R.is_hurwitz_stable(poly) == actually_stable


def test_pade_of_exp_by_direct_solve():
    from math import factorial
    exp = [F(1, factorial(k)) for k in range(6)]
    # [1/1]: (a0+a1 x)/(1+b1 x) matching c0+c1 x+c2 x^2 => b1=-c2/c1=-1/2, a1=c1+c0 b1
    num, den = PADE.pade(exp, 1, 1)
    assert num == [F(1), F(1, 2)] and den == [F(1), F(-1, 2)]


def test_apery_matches_binomial_closed_form():
    a, _ = A.apery_sequences(9)
    closed = [sum(comb(n, k) ** 2 * comb(n + k, k) ** 2 for k in range(n + 1))
              for n in range(10)]
    assert [int(x) for x in a] == closed[:len(a)]


def test_feigenbaum_R1_is_cubic_root():
    # R_1 solves r^3 - 4r^2 + 8 = 0; positive non-trivial root is 1+sqrt5
    rr = [r.real for r in _roots([1, -4, 0, 8]) if abs(r.imag) < 1e-6]
    assert any(abs(r - (1 + 5 ** 0.5)) < 1e-6 for r in rr)
    assert abs(float(FB.R1_exact()) - (1 + 5 ** 0.5)) < 1e-12
