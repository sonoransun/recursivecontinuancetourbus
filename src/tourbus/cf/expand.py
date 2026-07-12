"""Turning numbers into partial-quotient streams.

Three doorways into a continued fraction:

* :func:`cf_from_fraction` — Euclid's algorithm on a rational (finite, exact).
* :func:`cf_from_quadratic` — the integer PQa recurrence on ``(P + sqrt(D))/Q``,
  with cycle detection, yielding the pre-period and period (Lagrange's theorem
  in code: every quadratic irrational is eventually periodic).
* :func:`cf_from_interval` — a rigorous lazy expansion of an arbitrary real,
  driven by an interval oracle. It emits a partial quotient only once the
  bracket pins its floor, and *stops* the moment precision runs out rather than
  guessing.
"""

from __future__ import annotations

import math
from fractions import Fraction
from math import isqrt
from typing import Callable, Iterator


def cf_from_fraction(x: Fraction | int) -> Iterator[int]:
    """Yield the canonical finite continued fraction of a rational.

    The last partial quotient is ``>= 2`` (except for a bare integer), i.e. we
    emit the ``[..., a_n]`` form rather than the equivalent ``[..., a_n-1, 1]``.

    >>> list(cf_from_fraction(Fraction(415, 93)))
    [4, 2, 6, 7]
    >>> list(cf_from_fraction(Fraction(-7, 3)))
    [-3, 1, 2]
    >>> list(cf_from_fraction(5))
    [5]
    """
    f = Fraction(x)
    terms: list[int] = []
    num, den = f.numerator, f.denominator
    while den != 0:
        a = num // den            # floor division: correct for negatives too
        terms.append(a)
        num, den = den, num - a * den
    # Canonicalize a stray trailing 1 (can only arise for degenerate inputs).
    if len(terms) > 1 and terms[-1] == 1:
        terms[-2] += 1
        terms.pop()
    yield from terms


def _le_sqrt(m: int, D: int) -> bool:
    """Exact predicate ``m <= sqrt(D)`` for integer ``m`` (D >= 0)."""
    return m <= 0 or m * m <= D


def _floor_quad(P: int, D: int, Q: int) -> int:
    """Exact floor of ``(P + sqrt(D)) / Q`` for any non-zero integer ``Q``."""
    s = isqrt(D)
    n = (P + s) // Q  # close to the truth; the loops below make it exact

    def le(k: int) -> bool:
        m = k * Q - P
        if Q > 0:  # k <= value  <=>  kQ - P <= sqrt(D)
            return _le_sqrt(m, D)
        # Q < 0:   k <= value  <=>  kQ - P >= sqrt(D)
        return m >= 0 and m * m >= D

    while le(n + 1):
        n += 1
    while not le(n):
        n -= 1
    return n


def cf_from_quadratic(P: int, D: int, Q: int) -> tuple[list[int], list[int]]:
    """Expand ``(P + sqrt(D)) / Q``; return ``(preperiod, period)``.

    If ``D`` is a perfect square the value is rational and ``period`` is empty.

    >>> cf_from_quadratic(0, 2, 1)          # sqrt(2)
    ([1], [2])
    >>> cf_from_quadratic(0, 7, 1)          # sqrt(7)
    ([2], [1, 1, 1, 4])
    >>> cf_from_quadratic(1, 5, 2)          # golden ratio
    ([], [1])
    >>> cf_from_quadratic(0, 9, 1)          # sqrt(9) = 3, rational
    ([3], [])
    """
    if Q == 0:
        raise ZeroDivisionError("Q must be non-zero")
    if D < 0:
        raise ValueError("radicand D must be non-negative")

    s = isqrt(D)
    if s * s == D:  # perfect square: a rational number
        return list(cf_from_fraction(Fraction(P + s, Q))), []

    # PQa requires Q | (D - P^2). If not, scale numerator and denominator by
    # |Q| (value unchanged, divisibility restored).
    if (D - P * P) % Q != 0:
        aq = abs(Q)
        P, D, Q = P * aq, D * aq * aq, Q * aq

    seen: dict[tuple[int, int], int] = {}
    quotients: list[int] = []
    Pi, Qi = P, Q
    i = 0
    while (Pi, Qi) not in seen:
        seen[(Pi, Qi)] = i
        a = _floor_quad(Pi, D, Qi)
        quotients.append(a)
        Pn = a * Qi - Pi
        Qn = (D - Pn * Pn) // Qi
        Pi, Qi = Pn, Qn
        i += 1
    start = seen[(Pi, Qi)]
    return quotients[:start], quotients[start:]


def cf_from_interval(
    produce: Callable[[int], tuple[Fraction, Fraction]],
) -> Iterator[int]:
    """Lazily expand a real given an interval oracle.

    ``produce(precision)`` returns a ``(lo, hi)`` bracket of the value that
    tightens as ``precision`` grows. A partial quotient is emitted only when
    ``floor(lo) == floor(hi)``; if the oracle stops tightening while the next
    floor is still ambiguous, the stream ends (we never emit a digit we cannot
    certify).
    """
    emitted: list[int] = []
    prec = 0

    while True:
        # Determine the next partial quotient, tightening the oracle until the
        # tail interval pins a single floor (or the oracle stops improving).
        while True:
            lo, hi = produce(prec)
            tail = _replay(lo, hi, emitted)
            if tail is not None:
                tlo, thi = tail
                if math.floor(tlo) == math.floor(thi):
                    a = math.floor(tlo)
                    break
            # Ambiguous (or could not reciprocate): ask for more precision.
            nxt = prec + 1
            if produce(nxt) == produce(prec):
                return  # precision exhausted; do not guess
            prec = nxt

        emitted.append(a)
        yield a


def _replay(
    lo: Fraction, hi: Fraction, emitted: list[int]
) -> tuple[Fraction, Fraction] | None:
    """Transform a full-value bracket into the tail interval after ``emitted``.

    Applies ``t -> 1/(t - a)`` for each already-emitted term ``a``. Returns
    ``None`` when the bracket is too loose to reciprocate (caller should tighten).
    """
    for a in emitted:
        lo -= a
        hi -= a
        if lo <= 0 or hi <= 0:  # bracket straddles the integer; need more precision
            return None
        lo, hi = Fraction(1) / hi, Fraction(1) / lo
    return lo, hi
