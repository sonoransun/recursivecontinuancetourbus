import math
from fractions import Fraction

import pytest

from tourbus.crossdomain import huckel
from tourbus.crossdomain import recursion_method as R


# --- exact Lanczos and the continued-fraction Green's function ------------- #

def test_dimer_lanczos_coefficients():
    a, b2 = R.lanczos_coefficients(R.chain_hamiltonian(2), 0)
    assert a == [Fraction(0), Fraction(0)]
    assert b2 == [Fraction(1)]


def test_chain_lanczos_is_the_free_chain():
    # From an end site the Krylov space is the whole chain: a all 0, b^2 all 1.
    for n in range(2, 8):
        a, b2 = R.lanczos_coefficients(R.chain_hamiltonian(n), 0)
        assert a == [Fraction(0)] * n
        assert b2 == [Fraction(1)] * (n - 1)


def test_green_function_dimer_is_two_thirds():
    a, b2 = R.lanczos_coefficients(R.chain_hamiltonian(2), 0)
    assert R.green_function_cf(a, b2, Fraction(2)) == Fraction(2, 3)


def test_green_function_is_exact_for_rational_energy():
    # G_00(z) for the free chain is a Fraction at rational z, with real poles.
    a, b2 = R.lanczos_coefficients(R.chain_hamiltonian(3), 0)
    g = R.green_function_cf(a, b2, Fraction(3))
    assert isinstance(g, Fraction)
    # exact resolvent (3 I - H)^{-1}_{00} for the 3-site chain
    assert g == Fraction(8, 21)


def test_max_steps_truncates():
    a, b2 = R.lanczos_coefficients(R.chain_hamiltonian(10), 0, max_steps=4)
    assert len(a) == 4
    assert len(b2) == 3


# --- spectral poles equal the Huckel polyene spectrum ---------------------- #

def test_dimer_poles():
    a, b2 = R.lanczos_coefficients(R.chain_hamiltonian(2), 0)
    assert R.spectral_poles(a, b2) == [-1.0, 1.0]


def test_chain_poles_equal_huckel_polyene_energies():
    for n in range(2, 9):
        a, b2 = R.lanczos_coefficients(R.chain_hamiltonian(n), 0)
        poles = sorted(R.spectral_poles(a, b2))
        energies = sorted(huckel.polyene_energies(n))
        assert len(poles) == n
        for p, e in zip(poles, energies):
            assert p == pytest.approx(e, abs=1e-9)


def test_chain3_poles_are_zero_and_plus_minus_sqrt2():
    a, b2 = R.lanczos_coefficients(R.chain_hamiltonian(3), 0)
    poles = sorted(R.spectral_poles(a, b2))
    assert poles[0] == pytest.approx(-math.sqrt(2), abs=1e-9)
    assert poles[1] == pytest.approx(0.0, abs=1e-9)
    assert poles[2] == pytest.approx(math.sqrt(2), abs=1e-9)


def test_ring_poles_are_a_subset_of_the_ring_spectrum():
    # Lanczos from one site only resolves the symmetric sector, so it returns a
    # reduced Jacobi matrix whose poles are genuine ring eigenvalues.
    for n in range(4, 9):
        a, b2 = R.lanczos_coefficients(R.ring_hamiltonian(n), 0)
        poles = R.spectral_poles(a, b2)
        ring_eigs = [2 * math.cos(2 * math.pi * k / n) for k in range(n)]
        for p in poles:
            assert any(abs(p - e) < 1e-7 for e in ring_eigs)


# --- local density of states ----------------------------------------------- #

def test_local_dos_is_nonnegative():
    H = R.chain_hamiltonian(4)
    energies = [x / 10 for x in range(-25, 26)]
    assert all(v >= 0 for v in R.local_dos(H, 0, energies, eta=0.05))


def test_local_dos_peaks_at_eigenvalues():
    # The dimer LDOS is larger on its +/-1 poles than in the gap centre.
    H = R.chain_hamiltonian(2)
    on_pole = R.local_dos(H, 0, [1.0], eta=0.05)[0]
    in_gap = R.local_dos(H, 0, [0.0], eta=0.05)[0]
    assert on_pole > 10 * in_gap


# --- builders --------------------------------------------------------------- #

def test_builders_are_symmetric_integer_matrices():
    for H in (R.chain_hamiltonian(5), R.ring_hamiltonian(5),
              R.path_from_edges([(0, 1), (1, 2), (2, 0)], 3)):
        n = len(H)
        for i in range(n):
            for j in range(n):
                assert H[i][j] == H[j][i]
                assert H[i][j] in (0, 1)
            assert H[i][i] == 0          # zero on-site energy


def test_ring_adds_the_closing_bond():
    H = R.ring_hamiltonian(5)
    assert H[0][4] == 1 and H[4][0] == 1


# --- Bethe lattice ---------------------------------------------------------- #

def test_bethe_self_energy_is_exact_surd():
    d = R.bethe_self_energy(4, 3)             # (4 - sqrt(8)) / 4 = 1 - sqrt(2)/2
    assert str(d) == "1 - 1/2*sqrt(2)"
    # satisfies (q-1) D^2 - E D + t^2 = 0  exactly at the float level
    val = 2 * float(d) ** 2 - 4 * float(d) + 1
    assert val == pytest.approx(0.0, abs=1e-12)


def test_bethe_self_energy_rejects_in_band_energy():
    with pytest.raises(ValueError):
        R.bethe_self_energy(0, 3)            # inside the band: complex


def test_bethe_dos_band_centre_1d_chain():
    assert R.bethe_lattice_dos(0.0, 2, 1.0) == pytest.approx(1 / (2 * math.pi))


def test_bethe_dos_outside_band_is_zero():
    assert R.bethe_lattice_dos(3.0, 3, 1.0) == 0.0


def test_bethe_dos_coordination_three_centre():
    assert R.bethe_lattice_dos(0.0, 3, 1.0) == pytest.approx(2 ** 0.5 / (3 * math.pi))


def test_bethe_green_dos_matches_closed_form():
    # -Im G(E + i0+)/pi should reproduce the closed-form DOS inside the band.
    for E in (-2.0, -1.0, 0.0, 0.5, 1.5, 2.0):
        g = R.bethe_lattice_green(complex(E, 1e-7), 3, 1.0)
        num = -g.imag / math.pi
        assert num == pytest.approx(R.bethe_lattice_dos(E, 3, 1.0), abs=1e-3)


@pytest.mark.slow
@pytest.mark.statistical
def test_bethe_dos_integrates_to_one():
    # The density of states is normalized: its band integral is 1.
    for q in (3, 4, 5):
        edge = 2 * math.sqrt(q - 1)
        npts = 200_000
        dx = 2 * edge / npts
        total = sum(
            R.bethe_lattice_dos(-edge + (i + 0.5) * dx, q, 1.0) * dx
            for i in range(npts)
        )
        assert total == pytest.approx(1.0, abs=2e-3)
