"""Ostrowski numeration: counting in the base a continued fraction gives you.

Fix an irrational ``alpha = [a0; a1, a2, ...]``. Its convergent denominators
``q_0 = 1, q_1 = a1, q_k = a_k q_{k-1} + q_{k-2}`` are a *numeration scale*: every
integer ``n >= 0`` has one and only one representation

    n = sum_{k>=1} b_k * q_{k-1}

subject to the legality rules ``0 <= b_1 < a_1``, ``0 <= b_k <= a_k`` for
``k >= 2``, and the carry rule ``b_k = a_k  =>  b_{k-1} = 0`` (Ostrowski, 1922).
The greedy algorithm -- peel off the largest ``q_{k-1} <= n`` -- produces it, and
the carry rule falls out automatically because hitting the ceiling ``b_k = a_k``
leaves a remainder smaller than ``q_{k-2}``.

The famous special case is ``alpha = 1/phi = [0; 1, 1, 1, ...]``: then every
``a_k = 1``, the denominators are the Fibonacci numbers, and the legality rules
collapse to "digits in ``{0, 1}`` with no two adjacent ones" -- **Zeckendorf's
theorem**. Ostrowski numeration is Zeckendorf for an arbitrary irrational.

The same ``alpha`` also cuts a line into a **Sturmian word** and sprinkles
``{k*alpha mod 1}`` into arcs of at most three lengths; :func:`characteristic_word`
and :func:`three_distance_check` are those two faces of the one object. The
Sturmian word here reproduces the Fibonacci word of
:mod:`tourbus.crossdomain.fibonacci_chain`, and the gap count is the
three-distance theorem of :mod:`tourbus.frontier.three_distance`.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

from ..cf.convergents import convergent_pairs, recurrence
from ..cf.core import QuadraticSurd, surd_floor

__all__ = [
    "ostrowski",
    "from_ostrowski",
    "is_legal_ostrowski",
    "beatty",
    "characteristic_word",
    "three_distance_check",
]


def _denominators(cf: Sequence[int]) -> list[int]:
    """The convergent denominators ``[q_0, q_1, q_2, ...]`` of ``alpha = cf``.

    These are exactly the ``k_n`` of :func:`tourbus.cf.convergents.convergent_pairs`
    (``q_0 = 1``, ``q_1 = a1``, ``q_k = a_k q_{k-1} + q_{k-2}``); ``q_{k-1}`` is
    the weight of the Ostrowski digit ``b_k``.
    """
    return [k for _h, k in convergent_pairs(cf)]


def ostrowski(n: int, cf: Sequence[int]) -> list[int]:
    """Ostrowski digits of ``n >= 0`` for ``alpha = cf``, least-significant first.

    Returns ``[b_1, b_2, ...]`` where ``n = sum_k b_k * q_{k-1}`` -- so entry
    ``i`` (0-based) is the coefficient of the denominator ``q_i``. Trailing zeros
    are dropped, so ``ostrowski(0, cf) == []`` and the last entry is always
    nonzero. ``cf`` must be long enough that some ``q_k`` exceeds ``n``.

    >>> ostrowski(10, [1] + [2] * 8)        # sqrt(2): q = 1, 2, 5, 12, ... ; 10 = 2*5
    [0, 0, 2]
    >>> ostrowski(12, [0] + [1] * 10)       # Zeckendorf: 12 = 8 + 3 + 1
    [0, 1, 0, 1, 0, 1]
    >>> ostrowski(0, [0] + [1] * 5)
    []
    """
    if n < 0:
        raise ValueError("Ostrowski numeration represents n >= 0")
    if n == 0:
        return []
    qs = _denominators(cf)
    if not qs or qs[-1] <= n:
        raise ValueError(
            f"continued fraction is too short: need some q_k > {n}, "
            f"largest available is {qs[-1] if qs else 'none'}"
        )
    jmax = max(j for j, q in enumerate(qs) if q <= n)
    digits = [0] * (jmax + 1)
    remainder = n
    for j in range(jmax, -1, -1):
        digits[j] = remainder // qs[j]
        remainder -= digits[j] * qs[j]
    while digits and digits[-1] == 0:
        digits.pop()
    return digits


def from_ostrowski(digits: Sequence[int], cf: Sequence[int]) -> int:
    """Reassemble the integer ``sum_i digits[i] * q_i`` (inverse of :func:`ostrowski`).

    >>> from_ostrowski([0, 0, 2], [1] + [2] * 8)
    10
    >>> cf = [0] + [1] * 15
    >>> from_ostrowski(ostrowski(50, cf), cf)
    50
    """
    qs = _denominators(cf)
    if len(digits) > len(qs):
        raise ValueError("continued fraction is too short for these digits")
    return sum(b * qs[i] for i, b in enumerate(digits))


def is_legal_ostrowski(digits: Sequence[int], cf: Sequence[int]) -> bool:
    """Whether ``digits`` obey the three Ostrowski legality rules for ``alpha = cf``.

    With ``digits = [b_1, b_2, ...]`` the rules are ``0 <= b_1 < a_1``,
    ``0 <= b_k <= a_k`` for ``k >= 2``, and ``b_k = a_k  =>  b_{k-1} = 0``. Every
    ``n >= 0`` has exactly one legal representation, and that is the one
    :func:`ostrowski` returns.

    >>> is_legal_ostrowski([0, 0, 2], [1] + [2] * 8)
    True
    >>> is_legal_ostrowski([2], [1] + [2] * 8)          # b_1 = a_1 = 2, must be < a_1
    False
    >>> is_legal_ostrowski([1, 2], [1] + [2] * 8)       # b_2 = a_2 but b_1 != 0
    False
    """
    if len(digits) >= len(cf):
        raise ValueError("continued fraction is too short for these digits")
    for i, b in enumerate(digits):
        if b < 0:
            return False
        if i == 0:
            if b >= cf[1]:                       # b_1 < a_1
                return False
        else:
            if b > cf[i + 1]:                    # b_k <= a_k
                return False
            if b == cf[i + 1] and digits[i - 1] != 0:   # carry rule
                return False
    return True


def _cf_value(cf: Sequence[int]) -> Fraction:
    """Exact rational value of a (finite) partial-quotient list, via convergents."""
    cf = list(cf)
    if not cf:
        raise ValueError("need at least one partial quotient")
    *_, last = recurrence(cf)
    return last


def beatty(alpha: QuadraticSurd | Fraction, n: int) -> list[int]:
    """The Beatty sequence ``[floor(k*alpha) for k in 1..n]``, computed exactly.

    ``alpha`` may be a :class:`~tourbus.cf.core.QuadraticSurd` (floored by the
    exact :func:`~tourbus.cf.core.surd_floor`, no floating point) or a
    :class:`~fractions.Fraction` (floored by :func:`math.floor`). For irrational
    ``r, s > 1`` with ``1/r + 1/s = 1`` the sequences ``floor(k*r)`` and
    ``floor(k*s)`` partition the positive integers (Beatty's theorem).

    >>> beatty(QuadraticSurd.make(0, 1, 2), 5)          # floor(k*sqrt(2))
    [1, 2, 4, 5, 7]
    >>> beatty(Fraction(3, 2), 4)
    [1, 3, 4, 6]
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    if isinstance(alpha, QuadraticSurd):
        return [
            surd_floor(QuadraticSurd.make(alpha.a * k, alpha.b * k, alpha.D))
            for k in range(1, n + 1)
        ]
    alpha = Fraction(alpha)
    return [math.floor(alpha * k) for k in range(1, n + 1)]


def characteristic_word(cf: Sequence[int], length: int) -> str:
    """The characteristic Sturmian word of ``alpha = cf in (0, 1)`` as ``0``/``1``s.

    Letter ``n`` (for ``n >= 1``) is ``s_n = floor((n+1)*alpha) - floor(n*alpha)``,
    the cutting sequence of the line of slope ``alpha``. Reading ``1`` as ``a``
    and ``0`` as ``b`` gives the geometric "long/short tile" word.

    Honesty note: ``cf`` is finite, so ``alpha`` is *rational* and this returns
    the cutting sequence of that exact rational. It agrees with the genuine
    Sturmian word of the irrational limit for every prefix shorter than the final
    convergent denominator -- so ``[0] + [1] * 30`` reproduces the Fibonacci word
    for lengths in the hundreds. That Fibonacci identity is pinned here against
    :func:`tourbus.crossdomain.fibonacci_chain.fibonacci_word`:

    >>> characteristic_word([0] + [1] * 30, 13)
    '1011010110110'
    >>> from tourbus.crossdomain.fibonacci_chain import fibonacci_word
    >>> fib = fibonacci_word(5)[:13].replace("a", "1").replace("b", "0")
    >>> characteristic_word([0] + [1] * 30, 13) == fib
    True
    """
    if length < 0:
        raise ValueError("length must be >= 0")
    alpha = _cf_value(cf)
    if not (0 < alpha < 1):
        raise ValueError(
            f"characteristic word needs alpha in (0, 1); cf evaluates to {alpha}"
        )
    letters = []
    for n in range(1, length + 1):
        letters.append("1" if math.floor((n + 1) * alpha) - math.floor(n * alpha) else "0")
    return "".join(letters)


def three_distance_check(cf: Sequence[int], n_points: int) -> bool:
    """Verify the three-distance theorem for ``{k*alpha mod 1 : k < n_points}``.

    Reuses :func:`tourbus.frontier.three_distance.three_distance_report` on the
    rational value of ``cf``: the points cut the circle into arcs of at most
    three distinct lengths, always. (This is a check, so it returns ``True`` for
    any input the theorem covers -- it is here to *exhibit* the theorem, not to
    hunt for a counterexample that cannot exist.)

    >>> three_distance_check([0, 1, 1, 1, 1, 1, 1], 12)
    True
    """
    from ..frontier.three_distance import three_distance_report

    alpha = _cf_value(cf)
    return three_distance_report(alpha, n_points)["num_distinct"] <= 3
