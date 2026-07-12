"""Convergents: the two-term recurrence that powers the whole tour.

Given partial quotients ``a0, a1, a2, ...`` the convergents ``h_n / k_n`` obey
the fundamental recurrence

    h_n = a_n * h_{n-1} + h_{n-2},     k_n = a_n * k_{n-1} + k_{n-2}

seeded by ``h_{-1}, h_{-2} = 1, 0`` and ``k_{-1}, k_{-2} = 0, 1``. Every good
rational approximation on the tour comes out of this recurrence.
"""

from __future__ import annotations

from fractions import Fraction
from math import isqrt
from typing import Iterable, Iterator


def convergent_pairs(terms: Iterable[int]) -> Iterator[tuple[int, int]]:
    """Yield integer convergents ``(h_n, k_n)`` for each partial quotient.

    >>> list(convergent_pairs([3, 7, 15, 1]))
    [(3, 1), (22, 7), (333, 106), (355, 113)]
    """
    h_prev, h_prev2 = 1, 0
    k_prev, k_prev2 = 0, 1
    for a in terms:
        h = a * h_prev + h_prev2
        k = a * k_prev + k_prev2
        yield h, k
        h_prev, h_prev2 = h, h_prev
        k_prev, k_prev2 = k, k_prev


def recurrence(terms: Iterable[int]) -> Iterator[Fraction]:
    """Yield successive convergents as exact :class:`~fractions.Fraction`.

    >>> [str(c) for c in recurrence([3, 7, 15, 1])]
    ['3', '22/7', '333/106', '355/113']
    """
    for h, k in convergent_pairs(terms):
        yield Fraction(h, k)


def semiconvergents(terms) -> Iterator[Fraction]:
    """Yield the convergents interleaved with the intermediate semiconvergents.

    Starting from ``C_0 = a_0``, between ``C_{n-1}`` and ``C_n`` sit the
    semiconvergents ``(h_{n-2} + t*h_{n-1}) / (k_{n-2} + t*k_{n-1})`` for
    ``t = 1 .. a_n``; the last (``t = a_n``) is ``C_n`` itself.

    >>> [str(c) for c in semiconvergents([0, 1, 2])]
    ['0', '1', '1/2', '2/3']
    >>> [str(c) for c in semiconvergents([3, 7])]
    ['3', '4', '7/2', '10/3', '13/4', '16/5', '19/6', '22/7']
    """
    terms = list(terms)
    if not terms:
        return
    h_prev2, k_prev2 = 1, 0            # h_{-1}, k_{-1}
    h_prev, k_prev = terms[0], 1       # h_0, k_0
    yield Fraction(h_prev, k_prev)     # C_0
    for a in terms[1:]:
        for t in range(1, a + 1):
            yield Fraction(h_prev2 + t * h_prev, k_prev2 + t * k_prev)
        h_new = a * h_prev + h_prev2
        k_new = a * k_prev + k_prev2
        h_prev2, k_prev2 = h_prev, k_prev
        h_prev, k_prev = h_new, k_new


def _as_terms(x) -> list[int]:
    """Coerce a Fraction / int / CF-like into a finite list of partial quotients."""
    from .core import CF

    if isinstance(x, CF):
        # A finite CF materializes; anything else we take a generous prefix of.
        if x.is_finite():
            return x.terms(10_000)
        return x.terms(80)
    from .expand import cf_from_fraction

    return list(cf_from_fraction(Fraction(x)))


def best_approximation(x, max_denominator: int) -> Fraction:
    """Best rational approximation to ``x`` with denominator ``<= max_denominator``.

    Mirrors :meth:`fractions.Fraction.limit_denominator`, but also accepts a
    :class:`~tourbus.cf.core.CF` (including irrational streams, via a prefix).

    >>> best_approximation(Fraction(3141592653589793, 1000000000000000), 113)
    Fraction(355, 113)
    """
    if max_denominator < 1:
        raise ValueError("max_denominator must be >= 1")

    from .core import CF

    if not isinstance(x, CF):
        return Fraction(x).limit_denominator(max_denominator)

    # For a (possibly irrational) CF, walk convergents/semiconvergents and keep
    # the closest fraction whose denominator fits. We compare against the CF's
    # own high-precision rational approximation as the reference point.
    ref = x.approx(120)
    best: Fraction | None = None
    best_err: Fraction | None = None
    for c in semiconvergents(x.terms(200)):
        if c.denominator > max_denominator:
            break
        err = abs(ref - c)
        if best is None or err < best_err:  # type: ignore[operator]
            best, best_err = c, err
    if best is None:
        return Fraction(int(ref))
    return best


def best_approximations(x, max_denominator: int) -> Iterator[Fraction]:
    """Yield the ladder of best approximations (2nd kind) up to the denominator cap.

    These are exactly the convergents with denominator ``<= max_denominator``.

    >>> [str(c) for c in best_approximations(Fraction(415, 93), 100)]
    ['4', '9/2', '58/13', '415/93']
    """
    for c in recurrence(_as_terms(x)):
        if c.denominator > max_denominator:
            return
        yield c
