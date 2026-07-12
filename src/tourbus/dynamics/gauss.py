"""The Gauss map and the metric theory of continued fractions.

Strip the integer part off a real ``x`` and you are left with a fraction in
``[0, 1)``; take its reciprocal, strip *that* integer part, and you have the
next partial quotient. The engine driving that loop is the **Gauss map**

    T(x) = {1/x} = 1/x - floor(1/x),

the shift operator on continued-fraction digits: if ``x = [0; a1, a2, a3, ...]``
then ``T(x) = [0; a2, a3, ...]``. Iterating ``T`` walks down the digit stream.

The Gauss map has an invariant density ``1 / ((1 + x) ln 2)`` (Gauss's 1812
observation, proven by Kuzmin in 1928), and from it flow the three great metric
constants of the subject — the Gauss-Kuzmin digit distribution, Khinchin's
constant (the geometric mean of the partial quotients of almost every real), and
Levy's constant (the exponential growth rate of the convergent denominators).
This module lets the tour *measure* those laws on any digit stream it likes.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Iterable, Iterator

__all__ = [
    "gauss_map",
    "gauss_orbit",
    "kuzmin_theoretical",
    "kuzmin_empirical",
    "khinchin_estimate",
    "levy_estimate",
]


def gauss_map(x: Fraction) -> Fraction:
    """Apply the Gauss map ``T(x) = {1/x}`` to a rational in ``(0, 1)``.

    By convention ``T(0) = 0`` (the map has nowhere to go). For ``x`` outside
    ``(0, 1)`` this still returns the fractional part of ``1/x``; the interesting
    dynamics live on ``(0, 1)``.

    >>> gauss_map(Fraction(2, 5))          # 1/(2/5) = 5/2, drop the 2
    Fraction(1, 2)
    >>> gauss_map(Fraction(1, 3))          # 1/(1/3) = 3 exactly, no remainder
    Fraction(0, 1)
    """
    x = Fraction(x)
    if x == 0:
        return Fraction(0)
    inv = 1 / x
    return inv - math.floor(inv)


def gauss_orbit(x: Fraction, *, steps: int) -> Iterator[Fraction]:
    """Yield the orbit ``x, T(x), T^2(x), ...`` under the Gauss map.

    Produces ``steps + 1`` values (the seed plus ``steps`` images), stopping
    early if the orbit reaches ``0`` — which happens exactly when ``x`` is
    rational, since its digit stream is finite.

    >>> [str(v) for v in gauss_orbit(Fraction(2, 5), steps=4)]
    ['2/5', '1/2', '0']
    """
    x = Fraction(x)
    yield x
    for _ in range(steps):
        if x == 0:
            return
        x = gauss_map(x)
        yield x


def kuzmin_theoretical(m: int) -> float:
    """The Gauss-Kuzmin probability that a partial quotient equals ``m``.

    For almost every real number the digit ``m`` appears in the continued
    fraction with asymptotic frequency ``log2(1 + 1/(m*(m + 2)))``. The value is
    largest at ``m = 1`` (about 41.5% of all digits) and decays like ``m**-2``.

    >>> round(kuzmin_theoretical(1), 7)
    0.4150375
    >>> round(kuzmin_theoretical(2), 7)
    0.169925
    """
    if m < 1:
        raise ValueError("a partial quotient m must be >= 1")
    return math.log2(1 + 1 / (m * (m + 2)))


def kuzmin_empirical(
    terms: Iterable[int], *, max_bucket: int = 16
) -> dict[int, float]:
    """Observed frequency of each partial quotient ``m`` in ``1..max_bucket``.

    Counts how often each value ``1, 2, ..., max_bucket`` occurs among ``terms``
    and divides by the number of digits counted, giving a distribution to hold up
    against :func:`kuzmin_theoretical`. Digits larger than ``max_bucket`` (and any
    non-positive ``a0``) are simply ignored, so the returned frequencies sum to 1.

    >>> emp = kuzmin_empirical([1, 1, 2, 1, 3, 1, 2], max_bucket=4)
    >>> emp[1], emp[2], emp[3], emp[4]
    (0.5714285714285714, 0.2857142857142857, 0.14285714285714285, 0.0)
    """
    counts = {m: 0 for m in range(1, max_bucket + 1)}
    total = 0
    for a in terms:
        a = int(a)
        if 1 <= a <= max_bucket:
            counts[a] += 1
            total += 1
    if total == 0:
        return {m: 0.0 for m in range(1, max_bucket + 1)}
    return {m: counts[m] / total for m in range(1, max_bucket + 1)}


def khinchin_estimate(terms: Iterable[int]) -> float:
    """Geometric mean of the partial quotients ``a1, a2, ...`` (Khinchin's law).

    Khinchin proved that for almost every real number the geometric mean of the
    partial quotients ``a1, a2, ..., a_n`` tends to a universal constant

        K0 = 2.685452001...

    regardless of the number. This estimate is ``exp(mean(ln a_i))`` over the
    supplied digits. The leading term ``a0`` (the integer part) is dropped, since
    the theorem is a statement about the tail ``a1, a2, ...`` — and ``a0`` is
    often ``0``, which has no logarithm.

    A famously *non*-generic example: the golden ratio's digits are all ``1``, so
    its geometric mean sits at ``1.0`` forever and never approaches ``K0``.

    >>> khinchin_estimate([1] * 50)        # golden ratio: all ones
    1.0
    """
    ai = [int(a) for a in terms]
    tail = ai[1:]  # drop a0; Khinchin's theorem concerns a1, a2, ...
    if not tail:
        raise ValueError("need at least one partial quotient beyond a0")
    if any(a <= 0 for a in tail):
        raise ValueError("partial quotients a1, a2, ... must be positive")
    return math.exp(sum(math.log(a) for a in tail) / len(tail))


def levy_estimate(denominators: Iterable[int]) -> float:
    """Estimate Levy's constant from convergent denominators ``k_1, ..., k_n``.

    Levy sharpened Khinchin's picture: for almost every real the denominators of
    the convergents grow so that ``k_n ** (1/n)`` tends to

        e ** (pi**2 / (12 ln 2)) = 3.275822918...

    Given the ladder of denominators, this returns ``k_n ** (1/n)``, computed as
    ``exp(ln(k_n) / n)`` so that astronomically large denominators do not
    overflow a float.

    >>> round(levy_estimate([1, 2, 5, 13, 34]), 6)   # Fibonacci -> golden ratio
    2.024397
    """
    denoms = [int(k) for k in denominators]
    if not denoms:
        raise ValueError("need at least one convergent denominator")
    kn = denoms[-1]
    if kn <= 0:
        raise ValueError("convergent denominators must be positive")
    return math.exp(math.log(kn) / len(denoms))
