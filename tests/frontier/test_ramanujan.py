"""Ramanujan's continued fractions and nested radicals."""

from __future__ import annotations

import math
from fractions import Fraction

import pytest

from tourbus.frontier import ramanujan as R


def test_rogers_ramanujan_cf_is_exact_and_matches_backward_recurrence():
    # C_n(q) = 1/(1 + q/(1 + q^2/(1 + ... + q^n/1)))
    q = Fraction(1, 2)
    for n in range(0, 12):
        t = Fraction(1)
        for k in range(n, 0, -1):
            t = 1 + q ** k / t
        assert R.rogers_ramanujan_cf(q, n) == 1 / t


def test_rogers_ramanujan_convergents_alternate_and_narrow():
    # Exact convergents: successive ones step in alternating directions and
    # the enclosing interval strictly narrows (the continued-fraction bracket).
    q = Fraction(1, 3)
    cs = R.rogers_ramanujan_convergents(q, 8)
    diffs = [cs[i + 1] - cs[i] for i in range(len(cs) - 1)]
    for d in diffs:
        assert d != 0
    for a, b in zip(diffs, diffs[1:]):
        assert (a > 0) != (b > 0)          # signs alternate
    widths = [abs(d) for d in diffs]
    assert all(a > b for a, b in zip(widths, widths[1:]))  # intervals shrink


def test_rogers_ramanujan_pinned_convergents():
    assert R.rogers_ramanujan_cf(Fraction(1, 2), 8) == Fraction(1611053, 2269355)
    assert [str(c) for c in R.rogers_ramanujan_convergents(Fraction(1, 2), 4)] == \
        ["2/3", "5/7", "22/31", "93/131"]


def test_rogers_ramanujan_golden_identity():
    cf, closed, err = R.rogers_ramanujan_golden()
    # Ramanujan's 1913 identity: R(e^{-2 pi}) = sqrt((5+sqrt5)/2) - phi
    phi = (1 + math.sqrt(5)) / 2
    assert closed == pytest.approx(math.sqrt((5 + math.sqrt(5)) / 2) - phi)
    assert err < 1e-12
    assert cf == pytest.approx(closed, abs=1e-12)
    assert closed == pytest.approx(0.2840790438, abs=1e-9)


def test_rogers_ramanujan_value_domain():
    with pytest.raises(ValueError):
        R.rogers_ramanujan_value(1.0)
    with pytest.raises(ValueError):
        R.rogers_ramanujan_value(-0.1)


def test_nested_radical_converges_to_three():
    assert R.ramanujan_nested_radical(40) == pytest.approx(3.0, abs=1e-9)
    # monotone approach from below
    vals = [R.ramanujan_nested_radical(d) for d in range(1, 20)]
    assert all(a <= b + 1e-12 for a, b in zip(vals, vals[1:]))
    assert all(v <= 3.0 + 1e-9 for v in vals)


@pytest.mark.parametrize("x", [0, 1, 2, 5, 9])
def test_general_nested_radical_converges_to_x_plus_one(x):
    assert R.nested_radical_general(x, 45) == pytest.approx(x + 1, abs=1e-8)
