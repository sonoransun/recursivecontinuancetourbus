from tourbus.frontier import markov as M


def test_triples_and_numbers():
    assert M.markov_triples(30) == [(1, 1, 1), (1, 1, 2), (1, 2, 5), (1, 5, 13), (2, 5, 29)]
    assert M.markov_numbers(200) == [1, 2, 5, 13, 29, 34, 89, 169, 194]


def test_markov_triples_satisfy_equation():
    for a, b, c in M.markov_triples(500):
        assert a * a + b * b + c * c == 3 * a * b * c


def test_lagrange_numbers_below_three_and_increasing():
    vals = [float(M.lagrange_number(m)) for m in M.markov_numbers(200)]
    assert vals[0] < vals[1] < vals[2]           # sqrt5 < sqrt8 < sqrt221/5
    assert all(v < 3 for v in vals)              # the spectrum below 3
    assert abs(vals[0] - 5 ** 0.5) < 1e-12       # L_1 = sqrt(5)


def test_markov_value_equals_lagrange_number():
    # The deep identity: the Markov value of the extremal word IS L_m.
    for m in (1, 2, 5):
        word = M.extremal_cf(m)
        assert abs(M.markov_value(word) - float(M.lagrange_number(m))) < 1e-9


def test_golden_and_silver_are_extremal():
    # phi = [1;(1)] realizes sqrt(5); 1+sqrt2 = [2;(2)] realizes sqrt(8).
    assert abs(M.markov_value([1]) - 5 ** 0.5) < 1e-9
    assert abs(M.markov_value([2]) - 8 ** 0.5) < 1e-9
