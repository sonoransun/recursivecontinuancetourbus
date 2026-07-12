"""Apery's proof that zeta(3) is irrational: recursion meets a continued fraction.

In 1978 Roger Apery stunned mathematics by proving zeta(3) = sum 1/n^3 is
irrational. The engine is a linear recurrence with polynomial coefficients,

    n^3 * u_n = (34n^3 - 51n^2 + 27n - 5) * u_{n-1} - (n-1)^3 * u_{n-2},

which has two solutions ``a_n`` (integers!) and ``b_n`` (rationals) whose ratio
``b_n / a_n`` races to zeta(3) so fast — while the denominators grow only like
``e^{3n}`` — that zeta(3) cannot be rational. The same data is a continued
fraction for zeta(3). Recursion and continued fractions meet at the very edge of
what is known: whether zeta(5) is irrational is still open.
"""

from __future__ import annotations

from fractions import Fraction

__all__ = ["apery_sequences", "apery_zeta3_bounds", "apery_cf_convergents"]


def apery_sequences(N: int) -> tuple[list[Fraction], list[Fraction]]:
    """The two Apery solutions ``(a_n, b_n)`` for ``n = 0..N`` (exact Fractions).

    ``a_n`` are integers; ``b_n / a_n`` converges to zeta(3).

    >>> a, b = apery_sequences(6)
    >>> [int(x) for x in a]
    [1, 5, 73, 1445, 33001, 819005, 21460825]
    >>> b[1], b[2]
    (Fraction(6, 1), Fraction(351, 4))
    """
    a = [Fraction(1), Fraction(5)]
    b = [Fraction(0), Fraction(6)]
    for n in range(2, N + 1):
        coeff = 34 * n**3 - 51 * n**2 + 27 * n - 5
        prev3 = (n - 1) ** 3
        a.append((coeff * a[n - 1] - prev3 * a[n - 2]) / n**3)
        b.append((coeff * b[n - 1] - prev3 * b[n - 2]) / n**3)
    return a[:N + 1], b[:N + 1]


def apery_zeta3_bounds(N: int) -> list[Fraction]:
    """The convergents ``b_n / a_n`` (n >= 1), which converge rapidly to zeta(3).

    >>> float(apery_zeta3_bounds(6)[-1])
    1.2020569031595942
    """
    a, b = apery_sequences(N)
    return [b[n] / a[n] for n in range(1, N + 1)]


def apery_cf_convergents(N: int) -> list[Fraction]:
    """The classical continued fraction for zeta(3), truncated at each level.

    ``zeta(3) = 6 / (5 - 1^6/(117 - 2^6/(535 - 3^6/(...))))`` with denominators
    ``34n^3 + 51n^2 + 27n + 5``.

    >>> float(apery_cf_convergents(7)[-1])
    1.2020569031595942
    """
    def bden(n: int) -> int:
        return 34 * n**3 + 51 * n**2 + 27 * n + 5

    A_prev2, A_prev = Fraction(1), Fraction(bden(0))   # A_{-1}=1, A_0=b0'
    B_prev2, B_prev = Fraction(0), Fraction(1)
    out = []
    for i in range(1, N + 1):
        num = -Fraction(i) ** 6                         # partial numerator -n^6
        A = bden(i) * A_prev + num * A_prev2
        B = bden(i) * B_prev + num * B_prev2
        A_prev2, A_prev = A_prev, A
        B_prev2, B_prev = B_prev, B
        out.append(Fraction(6) * B / A)
    return out
