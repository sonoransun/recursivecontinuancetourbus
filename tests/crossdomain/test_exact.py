"""Tests for the exact-arithmetic cross-domain modules."""

from fractions import Fraction

from hypothesis import given
from hypothesis import strategies as st

from tourbus.crossdomain import _poly
from tourbus.crossdomain import huckel, cauer, routh, apery, phyllotaxis
import tourbus.crossdomain.pade as pade   # submodule (name is shadowed by pade() in the package)


# --- _poly ----------------------------------------------------------------- #

_polys = st.lists(st.integers(min_value=-9, max_value=9), min_size=1, max_size=7)


@given(_polys, _polys)
def test_divmod_roundtrip(num, den):
    if _poly.degree(den) < 0:
        return
    q, r = _poly.divmod_poly(num, den)
    # num == q*den + r, and deg(r) < deg(den)
    assert _poly.add(_poly.mul(q, den), r) == _poly.trim(num)
    assert _poly.degree(r) < _poly.degree(den)


# --- huckel (chemistry = continuant) --------------------------------------- #

def test_benzene_is_aromatic_with_integer_energies():
    poly = huckel.cycle_secular_polynomial(6)
    roots = sorted(x for x in range(-3, 4) if huckel._poly_eval(poly, x) == 0)
    assert roots == [-2, -1, 1, 2]
    energies = [round(e) for e in huckel.annulene_energies(6)]
    assert energies == [2, 1, 1, -1, -1, -2]
    assert huckel.is_aromatic(6, 6) == "aromatic"


def test_huckel_4n_plus_2_rule():
    aromatic = [m for m in range(2, 24) if huckel.is_aromatic(m, m) == "aromatic"]
    assert aromatic == [2, 6, 10, 14, 18, 22]  # 4n+2


def test_butadiene_energies_are_golden_ratio():
    # x^4 - 3x^2 + 1 has roots +/- phi, +/- 1/phi
    assert huckel.secular_polynomial(4) == [1, 0, -3, 0, 1]
    es = huckel.polyene_energies(4)
    phi = (1 + 5 ** 0.5) / 2
    assert abs(es[0] - phi) < 1e-9
    assert abs(es[1] - 1 / phi) < 1e-9


@given(st.integers(min_value=1, max_value=14), st.integers(min_value=-6, max_value=6))
def test_secular_is_the_continuant(n, x):
    # evaluating the recurrence == evaluating the polynomial
    assert huckel.secular_via_continuant(n, Fraction(x)) == huckel._poly_eval(
        huckel.secular_polynomial(n), Fraction(x)
    )


# --- cauer (electrical ladder) --------------------------------------------- #

def test_cauer_known_ladder_and_roundtrip():
    el = cauer.cauer_ladder([24, 0, 6, 0], [12, 0, 1])
    assert el == [Fraction(2), Fraction(3), Fraction(4)]
    n, d = cauer.ladder_to_rational(el)
    assert [int(c) for c in n] == [24, 0, 6, 0]
    assert [int(c) for c in d] == [12, 0, 1]


def test_ladder_impedance_matches_rational():
    el = [Fraction(2), Fraction(3), Fraction(4)]
    num, den = [24, 0, 6, 0], [12, 0, 1]
    s = Fraction(7)
    assert cauer.ladder_impedance(el, s) == _poly.eval_poly(num, s) / _poly.eval_poly(den, s)


# --- routh (control stability) --------------------------------------------- #

def test_hurwitz_table():
    assert routh.is_hurwitz_stable([1, 1, 1]) is True
    assert routh.is_hurwitz_stable([1, 2, 2, 1]) is True
    assert routh.is_hurwitz_stable([1, 3, 3, 1]) is True
    assert routh.is_hurwitz_stable([1, 2, 2, 40]) is False   # violates a1a2>a0a3
    assert routh.is_hurwitz_stable([1, 0, 1]) is False        # imaginary-axis roots


# --- pade (resummation) ---------------------------------------------------- #

def test_pade_of_exp():
    from math import factorial
    exp = [Fraction(1, factorial(k)) for k in range(7)]
    num, den = pade.pade(exp, 1, 1)
    assert num == [Fraction(1), Fraction(1, 2)]   # (1+x/2)/(1-x/2)
    assert den == [Fraction(1), Fraction(-1, 2)]


def test_pade_convergent_matches_series_order():
    from math import factorial
    exp = [Fraction(1, factorial(k)) for k in range(8)]
    num, den = pade.pade(exp, 2, 2)
    # num - den*exp must vanish through order m+n = 4
    prod = [Fraction(0)] * 8
    for i, c in enumerate(den):
        for j, e in enumerate(exp):
            if i + j < 8:
                prod[i + j] += c * e
    for k in range(5):
        nk = num[k] if k < len(num) else Fraction(0)
        assert prod[k] == nk


# --- apery (zeta(3) irrationality) ----------------------------------------- #

def test_apery_sequences_and_limit():
    a, b = apery.apery_sequences(6)
    assert [int(x) for x in a] == [1, 5, 73, 1445, 33001, 819005, 21460825]
    assert all(x.denominator == 1 for x in a)   # a_n are integers
    assert abs(float(apery.apery_zeta3_bounds(8)[-1]) - 1.2020569031595942) < 1e-12


def test_apery_two_routes_agree():
    b1 = float(apery.apery_zeta3_bounds(8)[-1])
    b2 = float(apery.apery_cf_convergents(8)[-1])
    assert abs(b1 - b2) < 1e-12


# --- phyllotaxis (biology) ------------------------------------------------- #

def test_golden_angle_and_spokes():
    assert abs(phyllotaxis.golden_angle_degrees() - 137.50776) < 1e-4
    assert phyllotaxis.spoke_count(1, 5) == 5
    assert phyllotaxis.spoke_count(2, 6) == 3


def test_parastichy_are_consecutive_fibonacci():
    fibs = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89}
    for n in (200, 400, 600):
        p, q = phyllotaxis.parastichy_counts(n)
        assert p in fibs and q in fibs
        # consecutive Fibonacci: q is the next one after p
        seq = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        assert seq.index(q) == seq.index(p) + 1
