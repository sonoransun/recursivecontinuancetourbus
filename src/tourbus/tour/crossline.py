"""The Cross-Domain Line: the same recurrence, across the sciences.

Seven stops showing that the continued fraction / continuant is not a niche of
number theory but the shape any chain of couplings takes — in chemistry,
condensed matter, engineering, analysis, dynamics, biology, and materials. Each
still computes live on the exact engine. Reached with ``python -m tourbus
crossdomain``.
"""

from __future__ import annotations

from fractions import Fraction

from .termio import Console
from . import render


def _subhead(c: Console, text: str) -> None:
    render.subhead(c, text)


def _souvenir(c: Console, text: str) -> None:
    render.souvenir(c, text)


# --------------------------------------------------------------------------- #

def cross_01_chemistry(c: Console) -> None:
    from ..crossdomain import huckel as H

    c.paragraph("A conjugated molecule's pi-electron energies are the eigenvalues of its "
                "carbon graph -- and for a linear chain the secular determinant is the "
                "continuant, the very recurrence behind every continued-fraction convergent.")
    c.emit()
    _subhead(c, "Live: benzene (C6) energy levels, in units of beta")
    c.emit("   " + c.style(str([round(e) for e in H.annulene_energies(6)]), "result"))
    _subhead(c, "Live: Huckel's 4n+2 aromaticity rule")
    rows = [[m, H.is_aromatic(m, m)] for m in (4, 6, 8, 10, 14)]
    c.emit(render.table(["pi electrons", "verdict"], rows, console=c, right_align=[0]))
    _subhead(c, "Live: butadiene's levels are the golden ratio")
    es = H.polyene_energies(4)
    c.emit("   " + c.style(f"{[round(e, 6) for e in es]}  =  +/-phi, +/-1/phi", "result"))
    c.emit()
    _souvenir(c, "The Huckel secular determinant IS a continuant -- chemistry's energy "
                 "levels are continued-fraction machinery.")


def cross_02_condensed_matter(c: Console) -> None:
    from ..crossdomain import recursion_method as RM

    c.paragraph("The recursion method writes a solid's local Green's function as a "
                "continued fraction G = 1/(z - a0 - b1^2/(z - a1 - ...)); its imaginary "
                "part is the density of states. A material's electronic structure is "
                "literally a continued fraction.")
    c.emit()
    _subhead(c, "Live: Lanczos coefficients of a carbon chain -> the CF")
    a, b2 = RM.lanczos_coefficients(RM.chain_hamiltonian(4), 0)
    c.emit("   " + c.style(f"a = {[str(x) for x in a]},  b^2 = {[str(x) for x in b2]}", "result"))
    c.emit("   " + c.style(f"poles (eigenvalues) = "
                           f"{sorted(round(float(p),4) for p in RM.spectral_poles(a,b2))}", "result"))
    _subhead(c, "Live: the Bethe lattice closes the CF into a closed-form DOS")
    for cn in (2, 3, 4):
        edge = 2 * (cn - 1) ** 0.5
        c.emit("   " + c.style(f"coordination {cn}: band edge +/-{edge:.4f}, "
                               f"DOS(0) = {RM.bethe_lattice_dos(0.0, cn, 1.0):.5f}", "result"))
    c.emit()
    _souvenir(c, "A molecule's density of states is a continued fraction you can hear.")


def cross_03_spectra(c: Console) -> None:
    from ..crossdomain import hofstadter as HF

    c.paragraph("An electron on a lattice in a magnetic field has a fractal spectrum -- the "
                "Hofstadter butterfly. Its eigenvalues are counted by the Sturm sequence, "
                "which is the continuant again; the gaps are labelled by the continued-"
                "fraction convergents of the magnetic flux.")
    c.emit()
    _subhead(c, "Live: Harper spectrum at flux 1/2 (edges +/-2sqrt2)")
    c.emit("   " + c.style(str([round(e, 6) for e in HF.harper_spectrum(1, 2)]), "result"))
    _subhead(c, "Live: the discriminant is a polynomial (a continuant in E)")
    c.emit("   " + c.style("flux 1/2: Delta(E) = E^2 - 4;  flux 1/3: Delta(E) = E^3 - 6E", "result"))
    _subhead(c, "Live: band counts vs flux p/q")
    rows = [[f"{p}/{q}", len(HF.harper_bands(p, q))] for (p, q) in ((1, 2), (1, 3), (2, 5), (1, 4))]
    c.emit(render.table(["flux", "bands"], rows, console=c, right_align=[1]))
    c.emit()
    _souvenir(c, "The number theory of continued fractions is drawn onto a real material's "
                 "energy levels. (Butterfly SVG in the web exposition.)")


def cross_04_dynamics(c: Console) -> None:
    from ..crossdomain import circle_map as CM
    from ..crossdomain import feigenbaum as FB

    c.paragraph("Driven oscillators lock their rhythm to rational ratios over whole "
                "intervals -- Arnold tongues, organized by the Stern-Brocot mediants of "
                "Stop 8. The locked winding number is a devil's staircase; push the "
                "doubling logic and you reach the Feigenbaum constant.")
    c.emit()
    _subhead(c, "Live: circle-map winding numbers lock onto rationals")
    rows = [[f"{Om}", f"{CM.winding_number(Om, 1.0):.4f}"] for Om in (0.0, 0.2, 0.5, 0.8)]
    c.emit(render.table(["drive Omega", "winding number (K=1)"], rows, console=c, right_align=[1]))
    c.emit("   " + c.style(f"width of the 0/1 tongue at K=1: {CM.tongue_width(0,1,1.0):.4f} (= 1/pi)", "result"))
    _subhead(c, "Live: the Feigenbaum constant from period doubling")
    c.emit("   " + c.style(f"delta ~ {FB.feigenbaum_delta(5):.4f}  (Feigenbaum {FB.FEIGENBAUM_DELTA:.4f})", "result"))
    c.emit()
    _souvenir(c, "Feigenbaum's delta is a renormalization rate -- the exact cousin of the "
                 "Gauss-Kuzmin-Wirsing constant from the Express Line.")


def cross_05_engineering(c: Console) -> None:
    from ..crossdomain import cauer, routh

    c.paragraph("Two staples of engineering are continued fractions in disguise. A Cauer "
                "ladder's impedance is a CF, so expanding a rational impedance synthesizes "
                "the circuit; and a system is stable exactly when its Routh continued "
                "fraction has all positive quotients.")
    c.emit()
    _subhead(c, "Live: synthesize an LC ladder from Z(s) = (24s^3+6s)/(12s^2+1)")
    el = cauer.cauer_ladder([24, 0, 6, 0], [12, 0, 1])
    c.emit("   " + c.style(f"element values (L,C,L,...) = {[str(x) for x in el]}", "result"))
    _subhead(c, "Live: Routh-Hurwitz stability = a CF with positive quotients")
    rows = [[str(p), "stable" if routh.is_hurwitz_stable(p) else "UNSTABLE"]
            for p in ([1, 1, 1], [1, 2, 2, 1], [1, 2, 2, 40], [1, 0, 1])]
    c.emit(render.table(["polynomial coeffs", "verdict"], rows, console=c))
    c.emit()
    _souvenir(c, "Stability is a continued fraction with positive partial quotients.")


def cross_06_analysis(c: Console) -> None:
    from ..crossdomain import pade, apery

    c.paragraph("Stop 3 said convergents are the best rational approximations of a number. "
                "Do it to a power series and you get Pade approximants, which resum even "
                "divergent series. And Apery proved zeta(3) irrational with a recurrence "
                "whose solutions are the convergents of a continued fraction.")
    c.emit()
    _subhead(c, "Live: the [1/1] Pade of e^x")
    from math import factorial
    num, den = pade.pade([Fraction(1, factorial(k)) for k in range(7)], 1, 1)
    c.emit("   " + c.style(f"({num[0]} + {num[1]}x) / ({den[0]} - {abs(den[1])}x)  =  (2+x)/(2-x)", "result"))
    _subhead(c, "Live: Apery's continued fraction for zeta(3)")
    c.emit("   " + c.style(f"convergents -> {float(apery.apery_zeta3_bounds(8)[-1])}", "result"))
    c.emit("   " + c.style("zeta(3) = 1.2020569031595942...  (proven irrational, 1978)", "chrome"))
    c.emit()
    _souvenir(c, "Whether zeta(5) is irrational is still open -- recursion at the frontier.")


def cross_07_biology(c: Console) -> None:
    from ..crossdomain import phyllotaxis as PH
    from ..crossdomain import fibonacci_chain as FC

    c.paragraph("The golden ratio -- Stop 4's most-irrational number -- optimizes living "
                "and crystalline structure. Plants place seeds at the golden angle so they "
                "never fall into spokes; the visible spiral counts are Fibonacci numbers, "
                "the denominators of phi's convergents.")
    c.emit()
    _subhead(c, "Live: the golden angle and the spirals it makes")
    c.emit("   " + c.style(f"golden angle = {PH.golden_angle_degrees():.4f} degrees", "result"))
    rows = [[n, str(PH.parastichy_counts(n))] for n in (200, 400, 600)]
    c.emit(render.table(["seeds", "parastichy (Fibonacci!)"], rows, console=c, right_align=[0]))
    c.emit("   " + c.style(f"a rational angle 2/5 turn makes exactly {PH.spoke_count(2,5)} spokes.", "chrome"))
    _subhead(c, "Live: the Fibonacci quasicrystal")
    c.emit("   " + c.style(f"word = {FC.fibonacci_word(6)}  (length {len(FC.fibonacci_word(6))})", "result"))
    c.emit("   " + c.style(f"brightest diffraction peaks indexed by "
                           f"{[t[:2] for t in FC.fibonacci_peak_ladder(5)]} = Fibonacci pairs", "result"))
    c.emit()
    _souvenir(c, "One number -- phi = [1;1,1,...] -- runs sunflowers, quasicrystals, and the "
                 "last stable orbit in the solar system.")


CROSS_STOPS = [
    ("Chemistry: Molecules Are Continuants", "Huckel MO energies from the continuant recurrence.", cross_01_chemistry),
    ("Condensed Matter: A Solid's Green's Function", "The density of states as a continued fraction.", cross_02_condensed_matter),
    ("Spectra: The Hofstadter Butterfly", "Magnetic spectra counted by the Sturm continuant.", cross_03_spectra),
    ("Nonlinear Dynamics: Mode-Locking", "Arnold tongues, the devil's staircase, Feigenbaum.", cross_04_dynamics),
    ("Engineering: Ladders and Stability", "Cauer synthesis and Routh-Hurwitz as continued fractions.", cross_05_engineering),
    ("Analysis: Pade and Apery", "Resumming series; the irrationality of zeta(3).", cross_06_analysis),
    ("Biology & Materials: The Golden Thread", "Phyllotaxis and the Fibonacci quasicrystal.", cross_07_biology),
]
