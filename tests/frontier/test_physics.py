from tourbus.frontier import physics as P


def test_closed_form_is_pi_digits():
    # floor(pi * 10^n) = the first n+1 digits of pi.
    assert [P.pi_prefix(n) for n in range(9)] == [
        3, 31, 314, 3141, 31415, 314159, 3141592, 31415926, 314159265
    ]


def test_simulation_matches_pi_digits():
    for n in range(5):
        assert P.galperin_collisions(n) == P.pi_prefix(n)


def test_equal_masses_give_three_collisions():
    assert P.galperin_collisions(0) == 3


def test_hundred_ratio_gives_thirtyone():
    assert P.galperin_collisions(1) == 31
