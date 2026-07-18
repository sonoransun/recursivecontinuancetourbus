"""Luroth and Pierce expansions: two more doorways off the Branch Line.

**Luroth (1883).** Every ``x`` in ``(0, 1)`` unfolds as

    x = 1/a_1 + 1/(a_1(a_1-1) a_2) + 1/(a_1(a_1-1) a_2(a_2-1) a_3) + ...

with digits ``a_k >= 2``.  Unlike the continued fraction and Engel machines --
where rationals *terminate* -- a rational Luroth expansion is eventually
**periodic**, exactly like a decimal.  The map is ``T(x) = a(a-1)x - (a-1)`` for
the digit ``a`` covering ``x``; iterated on a rational it cycles through a finite
set of states, so we detect the repeat and split the digits into a preperiod and
a repeating period.  (A naive "loop until the remainder is zero" therefore hangs
on almost every rational.)  The one finite case is an exact hit ``x = 1/n``,
which terminates with the single digit ``n`` and an empty period.

The Luroth digits are the "honest casino" foil to Gauss--Kuzmin: under Lebesgue
measure they are *i.i.d.* with ``P(digit = k) = 1/(k(k-1))`` for ``k >= 2`` -- no
memory between draws, unlike the correlated partial quotients of a CF.

**Pierce (the alternating Engel).** With strictly increasing digits,

    x = 1/a_1 - 1/(a_1 a_2) + 1/(a_1 a_2 a_3) - ...

driven by ``a = floor(1/x); x <- 1 - a*x``.  The sign alternation makes rationals
terminate again, in strictly increasing digits.  Its cameo here is ``1/phi``,
whose Pierce digits we compute in *exact* quadratic-surd arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from ..cf.core import QuadraticSurd, surd_floor

__all__ = [
    "luroth_expansion",
    "luroth_eval",
    "pierce_expansion",
    "pierce_eval",
    "pierce_of_reciprocal_phi",
]


def luroth_expansion(x: Fraction) -> tuple[list[int], list[int]]:
    """The Luroth expansion of ``x`` in ``(0, 1)`` as ``(preperiod, period)``.

    Iterates the Luroth map, recording the state that produced each digit; the
    first repeated state marks where the period begins.  An exact hit ``x = 1/n``
    terminates the expansion with an empty period.

    >>> luroth_expansion(Fraction(7, 10))     # rationals are eventually periodic
    ([2], [3])
    >>> luroth_expansion(Fraction(1, 2))      # exact hit terminates
    ([2], [])
    >>> luroth_expansion(Fraction(3, 8))
    ([3, 4], [])
    """
    x = Fraction(x)
    if not (0 < x < 1):
        raise ValueError(f"Luroth expansion is defined for x in (0, 1); got {x}")
    digits: list[int] = []
    seen: dict[Fraction, int] = {}
    while True:
        if x in seen:  # state recurs: everything from here on repeats
            start = seen[x]
            return digits[:start], digits[start:]
        seen[x] = len(digits)
        n = x.denominator // x.numerator  # floor(1/x) for the positive Fraction x
        if Fraction(1, n) == x:  # exact hit: a terminating (finite) expansion
            digits.append(n)
            return digits, []
        a = n + 1
        digits.append(a)
        x = a * (a - 1) * x - (a - 1)


def _luroth_fold(digits: Sequence[int]) -> tuple[Fraction, Fraction]:
    """Fold Luroth digits into ``(partial_sum, tail_weight)``.

    ``partial_sum`` is ``sum_k w_k / a_k`` and ``tail_weight`` is the product
    ``prod_k 1/(a_k(a_k-1))`` -- the factor multiplying whatever series follows.
    """
    total = Fraction(0)
    weight = Fraction(1)  # w_k: the coefficient in front of term k, w_1 = 1
    for a in digits:
        if a < 2:
            raise ValueError(f"Luroth digits must be >= 2; got {a}")
        total += weight / a
        weight /= a * (a - 1)
    return total, weight


def luroth_eval(preperiod: Sequence[int], period: Sequence[int] = ()) -> Fraction:
    """The exact value of a (possibly periodic) Luroth expansion.

    The periodic tail ``t`` satisfies the linear equation ``t = c + r*t`` from
    summing its geometric repeats, where ``c = sum W_k/q_k`` over one period and
    ``r = prod 1/(q_k(q_k-1)) < 1``; so ``t = c/(1 - r)`` is computed in closed
    form and the whole value is *exact* -- no truncation, no ``unfold`` knob.
    Round-trips :func:`luroth_expansion` exactly on every ``x`` in ``(0, 1)``.

    >>> luroth_eval([2], [3]) == Fraction(7, 10)
    True
    >>> luroth_eval([2]) == Fraction(1, 2)
    True
    """
    pre_sum, tail_weight = _luroth_fold(preperiod)
    if not period:
        return pre_sum
    c, r = _luroth_fold(period)
    tail = c / (1 - r)  # r < 1 since every q >= 2, so this is well-defined
    return pre_sum + tail_weight * tail


def pierce_expansion(x: Fraction) -> list[int]:
    """The Pierce expansion of ``x`` in ``(0, 1)``: strictly increasing, finite.

    Runs ``a = floor(1/x); x <- 1 - a*x`` until the remainder is exactly zero.

    >>> pierce_expansion(Fraction(5, 17))
    [3, 8, 17]
    >>> pierce_expansion(Fraction(1, 3))
    [3]
    """
    x = Fraction(x)
    if not (0 < x < 1):
        raise ValueError(f"Pierce expansion is defined for x in (0, 1); got {x}")
    digits: list[int] = []
    while x != 0:
        a = x.denominator // x.numerator  # floor(1/x)
        digits.append(a)
        x = 1 - a * x
    return digits


def pierce_eval(digits: Sequence[int]) -> Fraction:
    """Sum the alternating Pierce series ``sum_k (-1)^(k+1) / (a_1 ... a_k)``.

    Inverse of :func:`pierce_expansion` on the digits it produces.

    >>> pierce_eval([3, 8, 17]) == Fraction(5, 17)
    True
    """
    total = Fraction(0)
    denom = 1  # running product a_1 ... a_k
    sign = 1
    for a in digits:
        denom *= a
        total += Fraction(sign, denom)
        sign = -sign
    return total


def pierce_of_reciprocal_phi(n: int) -> list[int]:
    """The first ``n`` Pierce digits of ``1/phi = (sqrt(5) - 1)/2``, computed exactly.

    The whole expansion is carried out in :class:`QuadraticSurd` arithmetic with
    the exact :func:`surd_floor`, never floating point -- a floor that is off by
    one for a value a hair below an integer would send the greedy expansion
    astray.  Each step reciprocates (``inv = 1/x``), takes the exact floor, then
    applies the Pierce step ``x <- 1 - a*x``.

    The digits are *not* Lucas numbers, though Lucas numbers ``L_k`` (2, 1, 3, 4,
    7, 11, 18, ..., ``L_{k+1} = L_k + L_{k-1}``) organize them: after ``4 = L_3``,
    the pairs **straddle** Lucas numbers of *tripling* index -- ``17, 19`` bracket
    ``L_6 = 18`` and ``5777, 5779`` bracket ``L_18 = 5778``.  They grow doubly
    exponentially, so ``n`` must stay small.

    >>> pierce_of_reciprocal_phi(7)
    [1, 2, 4, 17, 19, 5777, 5779]
    """
    if n < 0:
        raise ValueError(f"n must be non-negative; got {n}")
    if n > 12:
        raise ValueError(
            "Pierce digits of 1/phi grow doubly exponentially; keep n <= 12"
        )
    x = QuadraticSurd.make(Fraction(-1, 2), Fraction(1, 2), 5)  # (sqrt(5) - 1)/2
    digits: list[int] = []
    for _ in range(n):
        inv = x.homographic(0, 1, 1, 0)          # 1/x
        a = surd_floor(inv)
        digits.append(a)
        x = x.homographic(-a, 1, 0, 1)           # 1 - a*x
    return digits
