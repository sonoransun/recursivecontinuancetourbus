"""Minkowski's question-mark function, computed exactly.

``?(x)`` is the strictly increasing homeomorphism of ``[0, 1]`` that sends the
continued-fraction structure of a real to the binary structure of its image. It
maps quadratic irrationals to (non-dyadic) rationals and rationals to dyadic
rationals -- the "conjugacy" that flattens the Stern-Brocot tree onto the
dyadic tree. On ``[0, 1]`` with ``x = [0; a1, a2, a3, ...]``:

    ?(x) = 2 * sum_{k>=1} (-1)^(k+1) * 2^(-(a1 + ... + ak)).

Because every term is a dyadic fraction, the whole computation stays exact in
:class:`~fractions.Fraction`:

* :func:`question_mark` truncates the (finite, for rationals) series.
* :func:`question_mark_of_quadratic` sums a periodic tail as a geometric
  series, so a quadratic irrational's rational image is produced *exactly*.
* :func:`question_mark_inverse` walks the Stern-Brocot tree by the bits of the
  target -- reading run lengths of equal bits as the continued fraction.

Outside ``[0, 1]`` all three use ``?(x) = floor(x) + ?(x - floor(x))``.
"""

from __future__ import annotations

import math
from fractions import Fraction

from ..cf.core import QuadraticSurd
from ..cf.expand import cf_from_fraction, cf_from_quadratic

__all__ = [
    "question_mark",
    "question_mark_inverse",
    "question_mark_of_quadratic",
]


def question_mark(x: Fraction, *, terms: int = 60) -> Fraction:
    """Minkowski's ``?`` of a rational, evaluated exactly as a Fraction.

    The fractional part's continued fraction drives the alternating dyadic
    series; ``terms`` caps how many partial quotients are summed (a rational's
    expansion is finite and short, so the default is never a real limit here).

    >>> question_mark(Fraction(1, 2))
    Fraction(1, 2)
    >>> question_mark(Fraction(1, 3))
    Fraction(1, 4)
    >>> question_mark(Fraction(2, 3))
    Fraction(3, 4)
    >>> question_mark(Fraction(1, 1))
    Fraction(1, 1)
    >>> question_mark(Fraction(5, 2))          # ?(x+n) = ?(x) + n
    Fraction(5, 2)
    """
    x = Fraction(x)
    n = math.floor(x)
    frac = x - n
    if frac == 0:
        return Fraction(n)

    # frac in (0, 1) has CF [0; a1, a2, ...]; drop the leading a0 == 0.
    quotients = list(cf_from_fraction(frac))[1 : 1 + terms]
    total = Fraction(0)
    partial_sum = 0
    sign = 1
    for a in quotients:
        partial_sum += a
        total += sign * Fraction(1, 1 << partial_sum)
        sign = -sign
    return n + 2 * total


def question_mark_inverse(y: Fraction, *, bits: int = 60) -> Fraction:
    """The inverse of ``?`` on the reals, exact for dyadic ``y``.

    Reads ``y`` bit by bit as a walk down the Stern-Brocot tree: ``?`` sends the
    mediant of two neighbours to the midpoint of their images, so bisecting in
    the image space is a mediant step in the value space. Run lengths of equal
    bits are exactly the partial quotients of the answer. For dyadic ``y`` the
    walk terminates on the node (the ``bits`` cap only bounds non-dyadic ``y``).

    >>> question_mark_inverse(Fraction(1, 2))
    Fraction(1, 2)
    >>> question_mark_inverse(Fraction(1, 4))
    Fraction(1, 3)
    >>> question_mark_inverse(Fraction(3, 4))
    Fraction(2, 3)
    >>> question_mark_inverse(Fraction(5, 2))
    Fraction(5, 2)
    """
    y = Fraction(y)
    n = math.floor(y)
    frac = y - n
    if frac == 0:
        return Fraction(n)

    left = (0, 1)   # value-space bracket, images ?(left)=lo, ?(right)=hi
    right = (1, 1)
    lo, hi = Fraction(0), Fraction(1)
    dyadic = (frac.denominator & (frac.denominator - 1)) == 0
    steps = 0
    while True:
        mid = (lo + hi) / 2
        node = (left[0] + right[0], left[1] + right[1])
        if frac == mid:
            return n + Fraction(node[0], node[1])
        if frac < mid:
            right, hi = node, mid
        else:
            left, lo = node, mid
        steps += 1
        if not dyadic and steps >= bits:
            node = (left[0] + right[0], left[1] + right[1])
            return n + Fraction(node[0], node[1])


def question_mark_of_quadratic(P: int, D: int, Q: int) -> Fraction:
    """``?`` of the quadratic irrational ``(P + sqrt(D)) / Q``, exact and rational.

    The continued fraction is eventually periodic, so the ``?`` series splits
    into a finite pre-period part plus a geometric tail summed in closed form.
    The result is rational -- this is the direction of ``?`` that turns
    quadratic irrationals into ordinary fractions. Works for any value (the
    integer part is peeled off first); if ``D`` is a perfect square the value is
    already rational and :func:`question_mark` handles it.

    >>> question_mark_of_quadratic(-1, 5, 2)   # 1/phi = (sqrt(5)-1)/2
    Fraction(2, 3)
    >>> question_mark_of_quadratic(0, 2, 1)    # sqrt(2)
    Fraction(7, 5)
    >>> question_mark_of_quadratic(1, 5, 2)    # phi = (1+sqrt(5))/2
    Fraction(5, 3)
    """
    pre, period = cf_from_quadratic(P, D, Q)
    if not period:  # rational value: a finite continued fraction
        return question_mark(QuadraticSurd.from_pqd(P, D, Q).as_fraction())

    # Split CF [a0; a1, a2, ...] into the integer part a0 and the tail
    # partial quotients c1, c2, ... (themselves eventually periodic).
    if pre:
        a0 = pre[0]
        tail_pre = pre[1:]
        tail_per = list(period)
    else:  # purely periodic: a0 is the head of the period, tail rotates it out
        a0 = period[0]
        tail_pre = []
        tail_per = period[1:] + period[:1]

    # Pre-period contribution: finite alternating dyadic sum.
    pre_sum = Fraction(0)
    cumulative = 0
    for j, c in enumerate(tail_pre, start=1):
        cumulative += c
        pre_sum += (1 if j % 2 else -1) * Fraction(1, 1 << cumulative)
    offset = cumulative                       # S_M, sum of pre-period quotients

    # Periodic contribution: geometric series over the repeating block.
    period_sum = sum(tail_per)                # P, sum of one period
    within = Fraction(0)                      # first term positive
    inner = 0
    for i, b in enumerate(tail_per, start=1):
        inner += b
        within += (1 if i % 2 else -1) * Fraction(1, 1 << inner)
    block_sign = 1 if len(tail_pre) % 2 == 0 else -1
    ratio = (-1 if len(tail_per) % 2 else 1) * Fraction(1, 1 << period_sum)
    periodic = (
        block_sign * Fraction(1, 1 << offset) * within / (1 - ratio)
    )

    return a0 + 2 * (pre_sum + periodic)
