from math import isqrt

import pytest

from tourbus.applications.cfrac import (
    FERMAT_F7,
    F7_FACTORS,
    Relation,
    cfrac_demo_trace,
    cfrac_factor,
    cfrac_relations,
    congruence_of_squares,
    smoothness_base,
    solve_gf2,
    verify_f7,
)
from tourbus.applications.wiener import is_probable_prime

# The canonical Morrison-Brillhart demo plus three semiprimes the docstring
# winks at (997*1009, and the two Wieferich primes 1093 and 3511 in 3837523).
KNOWN = {
    13290059: (3119, 4261),
    1005973: (997, 1009),
    9788111: (2741, 3571),
    3837523: (1093, 3511),
}
# A couple more fixed semiprimes: primes near 2000 and near 5000.
EXTRA = {
    4003997: (1999, 2003),
    25009997: (4999, 5003),
    9036011: (3001, 3011),
}


@pytest.mark.parametrize("n, factors", {**KNOWN, **EXTRA}.items())
def test_cfrac_factors_known_semiprimes(n, factors):
    p, q = cfrac_factor(n)
    assert (p, q) == factors
    assert p <= q
    assert p * q == n
    assert is_probable_prime(p) and is_probable_prime(q)


def test_demo_target_matches_doctest():
    assert cfrac_factor(13290059) == (3119, 4261)


def test_key_congruence_indexing():
    # The off-by-one trap: A_i pairs with Q_{i+1}, signed (-1)**(i+1). Replay the
    # bare PQa recurrence and check the first dozen steps satisfy the identity.
    n = 13290059
    d = n
    root = isqrt(d)
    p_i, q_i = 0, 1
    a_prev, a_prev2 = 1, 0
    for i in range(12):
        a = (p_i + root) // q_i
        a_cur = (a * a_prev + a_prev2) % n
        p_next = a * q_i - p_i
        q_next = (d - p_next * p_next) // q_i
        sign = -1 if i % 2 == 0 else 1
        assert (a_cur * a_cur - sign * q_next) % n == 0
        a_prev2, a_prev = a_prev, a_cur
        p_i, q_i = p_next, q_next


def test_every_relation_is_a_true_congruence():
    n = 13290059
    for rel in cfrac_relations(n):
        # A_i**2 == signed_q (mod n), and signed_q equals its recorded factors.
        assert (rel.a_mod_n * rel.a_mod_n - rel.signed_q) % n == 0
        product = 1
        for key, e in rel.factors.items():
            product *= key**e
        assert product == rel.signed_q


def test_smoothness_base_only_residue_primes():
    n = 13290059
    base = smoothness_base(n, 80)
    assert base[0] == -1
    assert base == [-1, 2, 5, 13, 31, 41, 43, 53, 67]
    assert 2 in base
    for p in base[1:]:
        if p == 2:
            continue
        assert pow(n % p, (p - 1) // 2, p) in (0, 1)  # residue (or divides n)
    # 3 and 7 are non-residues of this n, so they must be absent.
    assert 3 not in base and 7 not in base


def test_smoothness_base_small_bound():
    assert smoothness_base(13290059, 20) == [-1, 2, 5, 13]


def test_solve_gf2_finds_null_combinations():
    vectors = [[1, 0], [1, 0], [0, 1], [0, 1]]
    combos = solve_gf2(vectors)
    assert combos  # a non-trivial null space exists
    for combo in combos:
        acc = [0, 0]
        for idx in combo:
            for j in range(2):
                acc[j] ^= vectors[idx][j]
        assert acc == [0, 0]


def test_solve_gf2_empty():
    assert solve_gf2([]) == []


def test_congruence_of_squares_identity():
    rels = [Relation(0, 7, 4, {2: 2}), Relation(1, 8, 4, {2: 2})]
    x, y = congruence_of_squares(15, rels, [0, 1])
    assert (x * x - y * y) % 15 == 0
    assert (x, y) == (11, 4)


def test_even_and_small_prime_split():
    # 2, 3, 5 are peeled off directly, before any continued fraction runs.
    assert cfrac_factor(10) == (2, 5)
    assert cfrac_factor(6) == (2, 3)
    assert cfrac_factor(21) == (3, 7)
    assert cfrac_factor(35) == (5, 7)
    p, q = cfrac_factor(2 * 7919)  # 2 * a big prime
    assert p == 2 and p * q == 2 * 7919


def test_perfect_square_split():
    assert cfrac_factor(49) == (7, 7)     # 7**2, odd so it reaches the sqrt case
    assert cfrac_factor(121) == (11, 11)  # 11**2
    assert cfrac_factor(169) == (13, 13)  # 13**2


@pytest.mark.parametrize("n", [7, 13, 3119, 4261, 59649589127497217])
def test_prime_input_raises(n):
    with pytest.raises(ValueError):
        cfrac_factor(n)


@pytest.mark.parametrize("n", [1, 0, -6, -13290059])
def test_nonpositive_input_raises(n):
    with pytest.raises(ValueError):
        cfrac_factor(n)


def test_verify_f7():
    assert verify_f7() is True
    assert F7_FACTORS[0] * F7_FACTORS[1] == FERMAT_F7
    assert FERMAT_F7 == 2**128 + 1


def test_demo_trace_shape():
    trace = cfrac_demo_trace(13290059)
    assert trace["factors"] == (3119, 4261)
    assert trace["base"][0] == -1
    assert trace["n_relations"] >= len(trace["base"])
    assert trace["combo"]  # non-empty winning combination
    assert (trace["X"] ** 2 - trace["Y"] ** 2) % 13290059 == 0
    assert all(isinstance(r, dict) for r in trace["relations"])
    assert set(trace["relations"][0]) == {"index", "a_mod_n", "signed_q", "factors"}


def test_determinism():
    assert cfrac_factor(13290059) == cfrac_factor(13290059)
    assert cfrac_relations(9788111) == cfrac_relations(9788111)
    assert cfrac_demo_trace(1005973) == cfrac_demo_trace(1005973)
