import math

from tourbus.cf.constants import tan1_cf
from tourbus.cf.convergents import recurrence


def test_lambert_pattern_prefix():
    assert tan1_cf().terms(10) == [1, 1, 1, 3, 1, 5, 1, 7, 1, 9]


def test_lambert_pattern_continues():
    assert tan1_cf().terms(20) == [
        1, 1, 1, 3, 1, 5, 1, 7, 1, 9, 1, 11, 1, 13, 1, 15, 1, 17, 1, 19,
    ]


def test_convergents_agree_with_math_tan():
    convs = list(recurrence(tan1_cf().terms(20)))
    assert abs(float(convs[-1]) - math.tan(1.0)) < 1e-12
