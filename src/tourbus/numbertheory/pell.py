"""Pell's equation, solved through the continued fraction of ``sqrt(d)``.

Pell's equation ``x^2 - d*y^2 = 1`` (and its cousin ``= -1``) is the oldest and
cleanest place where continued fractions pay for themselves. The periodic
expansion of ``sqrt(d)`` hands you the *fundamental solution* directly: the
convergent one step before the period closes is already the smallest nontrivial
integer point on the hyperbola.

The connective tissue:

* ``sqrt(d) = [a0; (a1, ..., aL)]`` has period length ``L``.
* The convergent ``h_{L-1} / k_{L-1}`` satisfies ``h^2 - d*k^2 = (-1)^L``.
* So ``= -1`` is solvable **iff** ``L`` is odd; when it is, the ``= +1``
  fundamental solution is the square of the ``= -1`` one (as a unit in
  ``Z[sqrt(d)]``).

Every larger solution is a power of the fundamental unit, which is why
:func:`solutions` is a two-term recurrence rather than a search.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from typing import Iterator

from ..cf.convergents import convergent_pairs
from ..cf.expand import cf_from_quadratic

__all__ = ["PellSolution", "fundamental_solution", "solutions"]


@dataclass(frozen=True)
class PellSolution:
    """An integer point ``(x, y)`` on ``x^2 - d*y^2 = target``.

    >>> s = PellSolution(3, 2, 2)
    >>> s.verify(1)
    True
    >>> s.verify(-1)
    False
    """

    x: int
    y: int
    d: int

    def verify(self, target: int) -> bool:
        """True when ``x^2 - d*y^2`` equals ``target`` exactly."""
        return self.x * self.x - self.d * self.y * self.y == target


def _is_square(n: int) -> bool:
    r = isqrt(n)
    return r * r == n


def fundamental_solution(d: int, target: int = 1) -> PellSolution | None:
    """The smallest positive solution of ``x^2 - d*y^2 = target``.

    ``target`` must be ``1`` or ``-1``. Returns ``None`` when no solution exists:
    for ``d < 2`` or a perfect square ``d`` (no periodic expansion), and for
    ``target == -1`` when the period of ``sqrt(d)`` has even length.

    >>> fundamental_solution(2)
    PellSolution(x=3, y=2, d=2)
    >>> fundamental_solution(2, -1)
    PellSolution(x=1, y=1, d=2)
    >>> fundamental_solution(13)
    PellSolution(x=649, y=180, d=13)
    >>> fundamental_solution(61)
    PellSolution(x=1766319049, y=226153980, d=61)
    >>> fundamental_solution(61, -1)
    PellSolution(x=29718, y=3805, d=61)
    >>> fundamental_solution(4) is None          # perfect square
    True
    >>> fundamental_solution(3, -1) is None       # even period: unsolvable
    True
    """
    if target not in (1, -1):
        return None
    if d < 2 or _is_square(d):
        return None

    pre, period = cf_from_quadratic(0, d, 1)
    length = len(period)
    if length == 0:  # defensive: non-square d always has a period
        return None

    # Convergent h_{L-1}/k_{L-1} solves x^2 - d*y^2 = (-1)^L.
    terms = pre + period                      # a_0 .. a_L  (indices 0..L)
    pairs = list(convergent_pairs(terms))
    h, k = pairs[length - 1]

    if length % 2 == 0:
        # Even period: the convergent already solves +1; -1 is impossible.
        if target == -1:
            return None
        sol = PellSolution(h, k, d)
    else:
        # Odd period: the convergent solves -1.
        if target == -1:
            sol = PellSolution(h, k, d)
        else:  # target == 1: square the fundamental (-1)-unit.
            x1, y1 = h, k
            sol = PellSolution(x1 * x1 + d * y1 * y1, 2 * x1 * y1, d)

    assert sol.verify(target), "internal error: Pell solution failed to verify"
    return sol


def solutions(d: int, target: int = 1) -> Iterator[PellSolution]:
    """Yield every positive solution of ``x^2 - d*y^2 = target``, ascending.

    The first yielded is the fundamental solution; each successive one is the
    previous multiplied by the fundamental ``+1`` unit ``(x1 + y1*sqrt(d))``.
    Multiplying by a norm-``+1`` unit preserves ``target``, so the whole ladder
    keeps the same right-hand side. Empty when :func:`fundamental_solution`
    finds none.

    >>> gen = solutions(2)
    >>> [next(gen) for _ in range(3)]
    [PellSolution(x=3, y=2, d=2), PellSolution(x=17, y=12, d=2), PellSolution(x=99, y=70, d=2)]
    >>> gen = solutions(2, -1)
    >>> [next(gen) for _ in range(3)]
    [PellSolution(x=1, y=1, d=2), PellSolution(x=7, y=5, d=2), PellSolution(x=41, y=29, d=2)]
    """
    seed = fundamental_solution(d, target)
    if seed is None:
        return
    unit = fundamental_solution(d, 1)
    if unit is None:  # unreachable for non-square d >= 2, but keep it total
        return
    a, b = unit.x, unit.y
    x, y = seed.x, seed.y
    while True:
        yield PellSolution(x, y, d)
        x, y = a * x + d * b * y, a * y + b * x
