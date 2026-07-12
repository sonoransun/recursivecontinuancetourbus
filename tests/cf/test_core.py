from fractions import Fraction

import pytest

from tourbus.cf.core import CF, CFKind, QuadraticSurd


def test_reiteration_is_safe():
    cf = CF.from_fraction(Fraction(415, 93))
    first = list(cf)
    second = list(cf)
    assert first == second == [4, 2, 6, 7]
    # value() and convergents() must not consume the stream out from under str()
    assert cf.value() == Fraction(415, 93)
    assert str(cf) == "[4; 2, 6, 7]"


def test_kinds():
    assert CF.from_fraction(Fraction(3, 2)).kind is CFKind.FINITE
    assert CF.from_quadratic(0, 2, 1).kind is CFKind.PERIODIC
    assert CF.periodic([], [1]).kind is CFKind.PERIODIC
    assert CF.from_quadratic(0, 9, 1).kind is CFKind.FINITE  # perfect square


def test_is_finite():
    assert CF.from_fraction(2).is_finite() is True
    assert CF.from_quadratic(0, 2, 1).is_finite() is False


def test_finite_value():
    assert CF.from_fraction(Fraction(22, 7)).value() == Fraction(22, 7)


def test_periodic_value_golden_ratio():
    v = CF.periodic([], [1]).value()
    assert isinstance(v, QuadraticSurd)
    assert v == QuadraticSurd(Fraction(1, 2), Fraction(1, 2), 5)
    assert abs(float(v) - (1 + 5 ** 0.5) / 2) < 1e-12


def test_periodic_value_sqrt2():
    v = CF.from_quadratic(0, 2, 1).value()
    assert v.a == 0 and v.b == 1 and v.D == 2


def test_infinite_value_raises():
    from tourbus.cf.constants import pi_cf

    with pytest.raises(ValueError):
        pi_cf().value()


def test_str_periodic():
    assert str(CF.from_quadratic(0, 7, 1)) == "[2; (1, 1, 1, 4)]"
    assert str(CF.periodic([], [1])) == "[(1)]"


def test_quadratic_surd_minimal_polynomial():
    # golden ratio: x^2 - x - 1 = 0
    assert QuadraticSurd.from_pqd(1, 5, 2).minimal_polynomial() == (1, -1, -1)
    # sqrt(2): x^2 - 2 = 0
    assert QuadraticSurd.from_pqd(0, 2, 1).minimal_polynomial() == (1, 0, -2)


def test_quadratic_surd_homographic():
    s2 = QuadraticSurd.from_pqd(0, 2, 1)  # sqrt(2)
    # (sqrt2 + 1) / 1 = 1 + sqrt2
    out = s2.homographic(1, 1, 0, 1)
    assert out == QuadraticSurd(Fraction(1), Fraction(1), 2)


def test_quadratic_surd_squarefree_canonical():
    # sqrt(8) should normalize to 2*sqrt(2)
    s = QuadraticSurd.make(0, 1, 8)
    assert s.D == 2 and s.b == 2


def test_approx_of_pi():
    from tourbus.cf.constants import pi_cf

    assert pi_cf().approx(4) == Fraction(355, 113)
