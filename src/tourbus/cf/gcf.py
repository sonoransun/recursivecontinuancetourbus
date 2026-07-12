"""Generalized continued fractions and conversion to simple form.

A *generalized* continued fraction allows arbitrary numerators:

    a0 + b1/(a1 + b2/(a2 + b3/(a3 + ...)))

Historically this is where order returns to numbers whose *simple* continued
fraction looks chaotic — Brouncker's and Lambert's formulas for pi are
generalized continued fractions with clean patterns.

:func:`gcf_to_simple` converts a generalized CF into simple form by tracking
consecutive convergents as a bracketing interval and emitting a simple partial
quotient only when the bracket pins its floor. This is rigorous precisely when
the generalized CF's convergents alternate about the limit (true for the
classical pi formulas below).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Iterator

from .expand import cf_from_interval

__all__ = ["GCFTerm", "gcf_convergents", "gcf_to_simple", "pi_gcf"]


@dataclass(frozen=True)
class GCFTerm:
    """One level of a generalized CF: partial denominator ``a`` and numerator ``b``.

    For the leading term (index 0) ``b`` is unused.
    """

    a: int
    b: int = 1


def gcf_convergents(terms: Iterable[GCFTerm]) -> Iterator[Fraction]:
    """Yield the convergents ``A_i / B_i`` of a generalized continued fraction.

    >>> import itertools
    >>> [str(c) for c in itertools.islice(gcf_convergents(pi_gcf()), 4)]
    ['3', '19/6', '47/15', '1321/420']
    """
    A_prev2, A_prev = 1, None
    B_prev2, B_prev = 0, None
    for i, t in enumerate(terms):
        if i == 0:
            A_prev, B_prev = t.a, 1
            yield Fraction(A_prev, B_prev)
            continue
        A = t.a * A_prev + t.b * A_prev2
        B = t.a * B_prev + t.b * B_prev2
        A_prev2, A_prev = A_prev, A
        B_prev2, B_prev = B_prev, B
        yield Fraction(A, B)


def gcf_to_simple(terms: Iterable[GCFTerm], *, max_terms: int = 400) -> Iterator[int]:
    """Convert a generalized CF to a simple CF (best-effort, bracket-certified).

    Consumes up to ``max_terms`` generalized terms, forms a bracket from the
    last two convergents, and emits the simple partial quotients that bracket
    certifies. Rigorous when the convergents alternate about the limit.
    """
    convs: list[Fraction] = []
    for i, c in enumerate(gcf_convergents(terms)):
        convs.append(c)
        if i + 1 >= max_terms:
            break
    if len(convs) < 2:
        if convs:
            from .expand import cf_from_fraction

            yield from cf_from_fraction(convs[0])
        return
    lo, hi = sorted((convs[-1], convs[-2]))

    def produce(_prec: int) -> tuple[Fraction, Fraction]:
        return lo, hi

    yield from cf_from_interval(produce)


def pi_gcf() -> Iterator[GCFTerm]:
    """The classical generalized CF ``pi = 3 + 1^2/(6 + 3^2/(6 + 5^2/(6 + ...)))``.

    >>> import itertools
    >>> [(t.a, t.b) for t in itertools.islice(pi_gcf(), 4)]
    [(3, 1), (6, 1), (6, 9), (6, 25)]
    """
    yield GCFTerm(3, 1)
    i = 1
    while True:
        yield GCFTerm(6, (2 * i - 1) ** 2)
        i += 1
