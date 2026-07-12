from tourbus.frontier import gkw


def test_leading_eigenvalue_is_one():
    # The transfer operator preserves the integral, so its top eigenvalue is 1.
    assert abs(gkw.leading_eigenvalue(grid=160, terms=800, iters=40) - 1.0) < 0.01


def test_gkw_constant():
    # From scratch, we recover Wirsing's -0.3036300... to a few digits.
    lam = gkw.second_eigenvalue(grid=200, terms=1000, iters=70)
    assert abs(lam - gkw.GKW_CONSTANT) < 5e-4


def test_gkw_sign_is_negative():
    lam = gkw.second_eigenvalue(grid=120, terms=600, iters=50)
    assert lam < 0  # the GKW constant is negative (alternating convergence)
