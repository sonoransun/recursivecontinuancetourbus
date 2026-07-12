"""The Collatz map: the simplest recursion nobody can prove halts.

Start from any positive integer and iterate

    n -> n / 2       if n is even
    n -> 3 n + 1     if n is odd

The **Collatz conjecture** (1937, still open) says every start eventually
reaches 1. It belongs on this tour as the antithesis of continued fractions:
CF recursion is completely understood — it always terminates, its length and
error are bounded in advance — while this equally short recursion resists all
analysis. The orbit of 27 is the classic demonstration: 111 steps and a peak
of 9232 before it finally collapses to 1.
"""

from __future__ import annotations

from typing import Iterator

__all__ = ["collatz_orbit", "collatz_stats"]


def collatz_orbit(n: int) -> Iterator[int]:
    """Yield the Collatz trajectory of ``n``, from ``n`` down to a final ``1``.

    >>> list(collatz_orbit(1))
    [1]
    >>> list(collatz_orbit(6))
    [6, 3, 10, 5, 16, 8, 4, 2, 1]
    """
    if n < 1:
        raise ValueError("Collatz is defined for positive integers")
    yield n
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        yield n


def collatz_stats(n: int) -> dict:
    """Summarise the orbit of ``n``: start, step count, and peak value.

    ``steps`` counts the transitions taken to reach 1 (so ``collatz_stats(1)``
    reports 0 steps); ``max`` is the highest value the orbit visits.

    >>> collatz_stats(27) == {"start": 27, "steps": 111, "max": 9232}
    True
    >>> collatz_stats(6)
    {'start': 6, 'steps': 8, 'max': 16}
    >>> collatz_stats(1)
    {'start': 1, 'steps': 0, 'max': 1}
    """
    steps = 0
    peak = n
    for value in collatz_orbit(n):
        peak = max(peak, value)
        steps += 1
    return {"start": n, "steps": steps - 1, "max": peak}
