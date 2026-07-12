"""Continuants: the polynomial hiding inside every convergent.

The convergent numerators and denominators from the Engine Room are not just
numbers — they are values of a single family of polynomials, the **continuants**
``K(a_1, ..., a_n)``, defined by the very same three-term recurrence:

    K() = 1,   K(a_1) = a_1,   K(a_1, ..., a_n) = a_n * K(a_1, ..., a_{n-1}) + K(a_1, ..., a_{n-2}).

Two facts make them a fringe delight. First, they are **palindromic**:
``K(a_1, ..., a_n) = K(a_n, ..., a_1)`` — reversing the partial quotients leaves
the numerator unchanged (which is why ``p_{n-1}/p_n`` and ``q_{n-1}/q_n`` mirror
each other). Second, **Euler's rule**: the continuant equals the sum, over every
way of striking out disjoint adjacent pairs, of the product of what remains — so
``K(1, 1, ..., 1)`` counts domino-and-square tilings and lands exactly on a
Fibonacci number.
"""

from __future__ import annotations

from typing import Sequence

__all__ = ["continuant", "continuant_euler", "convergent_via_continuants"]


def continuant(seq: Sequence[int]) -> int:
    """The continuant ``K(a_1, ..., a_n)`` via the three-term recurrence.

    >>> continuant([])
    1
    >>> continuant([5])
    5
    >>> continuant([3, 7])          # 3*7 + 1
    22
    >>> continuant([1, 1, 1, 1, 1])  # Fibonacci F_6
    8
    """
    prev, prev2 = 1, 0  # K() , K(nothing-before)
    for a in seq:
        prev, prev2 = a * prev + prev2, prev
    return prev


def continuant_euler(seq: Sequence[int]) -> int:
    """The same continuant via Euler's combinatorial rule.

    Sum over all matchings of the path on ``n`` vertices: each matched edge
    ``(i, i+1)`` means "delete both ``a_i`` and ``a_{i+1}``"; multiply the values
    of the vertices left unmatched. Computed here with a small recursion over
    "take ``a_1`` alone" vs. "pair ``a_1`` with ``a_2``".

    >>> continuant_euler([3, 7]) == continuant([3, 7])
    True
    >>> continuant_euler([2, 3, 4])   # 2*3*4 + 2 + 4
    30
    """
    a = list(seq)

    def rec(i: int) -> int:
        if i >= len(a):
            return 1
        if i == len(a) - 1:
            return a[i]
        # a_i stays (times the rest)  +  (a_i, a_{i+1}) both struck out
        return a[i] * rec(i + 1) + rec(i + 2)

    return rec(0)


def convergent_via_continuants(terms: Sequence[int]) -> tuple[int, int]:
    """Return ``(p_n, q_n)`` built purely as continuants of the partial quotients.

    ``p_n = K(a_0, a_1, ..., a_n)`` and ``q_n = K(a_1, ..., a_n)`` — the reason
    the convergent recurrence and the continuant recurrence are the same object.

    >>> convergent_via_continuants([3, 7, 15, 1])   # a convergent of pi
    (355, 113)
    """
    terms = list(terms)
    p = continuant(terms)
    q = continuant(terms[1:])
    return p, q
