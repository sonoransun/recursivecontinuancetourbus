import math

from tourbus.frontier import algebraic as A
from tourbus.cf.convergents import recurrence


def test_cube_root_two_prefix():
    assert A.cube_root_cf(2).terms(8) == [1, 3, 1, 5, 1, 1, 4, 1]


def test_cube_root_converges_to_cube_root():
    conv = list(recurrence(A.cube_root_cf(2).terms(20)))[-1]
    assert abs(float(conv) - 2 ** (1 / 3)) < 1e-9


def test_plastic_number_has_the_famous_141():
    terms = A.plastic_number_cf().terms(12)
    assert terms[:12] == [1, 3, 12, 1, 1, 3, 2, 3, 2, 4, 2, 141]
    # and it is a root of x^3 - x - 1
    rho = float(list(recurrence(A.plastic_number_cf().terms(25)))[-1])
    assert abs(rho ** 3 - rho - 1) < 1e-9


def test_algebraic_cfs_look_khinchin_typical():
    # Unlike quadratics (bounded, periodic), cube roots have large partial
    # quotients and a geometric mean near Khinchin's constant.
    s = A.partial_quotient_stats(A.cube_root_cf(2, digits=90), 40)
    assert s["max"] >= 20
    assert 2.0 < s["geometric_mean"] < 4.0
