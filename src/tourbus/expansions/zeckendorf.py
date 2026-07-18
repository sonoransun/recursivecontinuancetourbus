"""Zeckendorf representation and Bergman's base-``phi`` number system.

Two ways of writing an integer with the Fibonacci numbers and the golden ratio,
both tied to Stop 4 of the tour, where ``phi = (1 + sqrt(5)) / 2`` first appears
as the "most irrational" number.

**Zeckendorf's theorem.** Every positive integer is a sum of *non-consecutive*
Fibonacci numbers in exactly one way — ``100 = 89 + 8 + 3``, never using two
neighbours like ``8`` and ``13``. The greedy choice (subtract the largest
Fibonacci number that fits) produces it, and the non-consecutive condition is
what makes it unique. The result was published by Zeckendorf in 1972 but was
already proved by Lekkerkerker in 1952; read off as a bit-string it is the
*Fibonacci coding* used in variable-length integer compression.

**Bergman's base-``phi``.** In 1957 George Bergman asked what happens if you use
an *irrational* base. Writing ``n`` in positional notation with powers of
``phi`` — digits ``0``/``1``, a radix point, and both positive and negative
powers — every positive integer terminates, and in standard form no two ``1``
digits are ever adjacent (because ``phi^2 = phi + 1`` lets you carry ``011``
into ``100``). Here ``2 = phi + phi^{-2}`` is ``"10.01"`` and
``4 = phi^2 + phi^0 + phi^{-2}`` is ``"101.01"``.

All comparisons are exact: powers of ``phi`` are carried as integer pairs
``(c, d)`` meaning ``c*phi + d`` in ``Z[phi]``, and their sign is decided through
the package's exact :func:`~tourbus.cf.core.surd_floor`.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from ..cf.core import QuadraticSurd, surd_floor

__all__ = [
    "fibonacci_upto",
    "zeckendorf",
    "zeckendorf_indices",
    "from_zeckendorf",
    "is_zeckendorf",
    "base_phi_digits",
    "base_phi_value",
]


def fibonacci_upto(limit: int) -> list[int]:
    """Fibonacci numbers ``1, 2, 3, 5, 8, ...`` up to ``limit`` (inclusive).

    The sequence starts at ``F_2 = 1, F_3 = 2`` (not the duplicated ``F_1 = 1``),
    so every value is distinct — exactly the pool of summands Zeckendorf uses.

    >>> fibonacci_upto(20)
    [1, 2, 3, 5, 8, 13]
    >>> fibonacci_upto(0)
    []
    """
    if limit < 1:
        return []
    fibs = [1, 2]
    while fibs[-1] + fibs[-2] <= limit:
        fibs.append(fibs[-1] + fibs[-2])
    return [f for f in fibs if f <= limit]


def zeckendorf(n: int) -> list[int]:
    """The unique non-consecutive Fibonacci summands of ``n``, descending.

    Found greedily: repeatedly subtract the largest Fibonacci number ``<= n``.
    Because consecutive Fibonacci numbers sum to the next one, the greedy choice
    can never pick two neighbours, which is exactly Zeckendorf's uniqueness.

    >>> zeckendorf(100)
    [89, 8, 3]
    >>> zeckendorf(1)
    [1]
    >>> zeckendorf(12)
    [8, 3, 1]
    """
    if n < 1:
        raise ValueError("Zeckendorf representation is defined for n >= 1")
    fibs = fibonacci_upto(n)
    out: list[int] = []
    for f in reversed(fibs):
        if f <= n:
            out.append(f)
            n -= f
    return out


def zeckendorf_indices(n: int) -> list[int]:
    """The Fibonacci *indices* of :func:`zeckendorf`, descending.

    Uses the convention ``F_2 = 1, F_3 = 2, F_4 = 3, F_5 = 5, F_6 = 8, ...`` (the
    duplicate ``F_1 = 1`` is skipped so summands are distinct). The returned
    indices are strictly descending with no two consecutive.

    >>> zeckendorf_indices(100)   # 89 = F_11, 8 = F_6, 3 = F_4
    [11, 6, 4]
    >>> zeckendorf_indices(1)
    [2]
    """
    # Build value -> index once (index 2 -> 1, index 3 -> 2, ...).
    index_of: dict[int, int] = {}
    a, b, k = 1, 2, 2
    while a <= n:
        index_of[a] = k
        a, b, k = b, a + b, k + 1
    return [index_of[f] for f in zeckendorf(n)]


def from_zeckendorf(fibs: Sequence[int]) -> int:
    """Sum a list of Fibonacci summands back into an integer.

    >>> from_zeckendorf([89, 8, 3])
    100
    >>> from_zeckendorf([])
    0
    """
    return sum(fibs)


def is_zeckendorf(fibs: Sequence[int]) -> bool:
    """Whether ``fibs`` is a valid Zeckendorf representation.

    Requires every element to be a Fibonacci number from the ``1, 2, 3, 5, ...``
    pool, all distinct, with no two *consecutive* Fibonacci indices.

    >>> is_zeckendorf([89, 8, 3])
    True
    >>> is_zeckendorf([8, 5])      # F_6 and F_5 are consecutive
    False
    >>> is_zeckendorf([2, 1])      # F_3 and F_2 are consecutive
    False
    >>> is_zeckendorf([13, 5, 1])
    True
    """
    if not fibs:
        return True
    biggest = max(fibs)
    # value -> index over the distinct-summand Fibonacci pool
    index_of: dict[int, int] = {}
    a, b, k = 1, 2, 2
    while a <= biggest:
        index_of[a] = k
        a, b, k = b, a + b, k + 1
    indices = []
    for f in fibs:
        if f not in index_of:
            return False
        indices.append(index_of[f])
    if len(set(indices)) != len(indices):
        return False
    ordered = sorted(indices)
    return all(hi - lo >= 2 for lo, hi in zip(ordered, ordered[1:]))


# --------------------------------------------------------------------------- #
#  Bergman base-phi: exact arithmetic in Z[phi] via integer pairs (c, d) that
#  stand for c*phi + d.  phi^2 = phi + 1 makes multiplication a linear map.
# --------------------------------------------------------------------------- #

def _phi_power(k: int) -> tuple[int, int]:
    """``phi**k`` as an integer pair ``(c, d)`` meaning ``c*phi + d``.

    Multiplying by ``phi`` sends ``(c, d) -> (c + d, c)`` (since
    ``phi*(c phi + d) = c(phi + 1) + d phi = (c + d) phi + c``); multiplying by
    ``phi^{-1} = phi - 1`` sends ``(c, d) -> (d, c - d)``.
    """
    c, d = 0, 1  # phi**0 = 0*phi + 1
    if k >= 0:
        for _ in range(k):
            c, d = c + d, c
    else:
        for _ in range(-k):
            c, d = d, c - d
    return c, d


def _zphi_surd(c: int, d: int) -> QuadraticSurd:
    """The value ``c*phi + d`` as an exact :class:`QuadraticSurd`."""
    # c*phi + d = c*(1 + sqrt(5))/2 + d = (c/2 + d) + (c/2)*sqrt(5)
    return QuadraticSurd.make(Fraction(c, 2) + d, Fraction(c, 2), 5)


def _zphi_nonneg(c: int, d: int) -> bool:
    """Exact test ``c*phi + d >= 0`` (zero only when ``c == d == 0``)."""
    if c == 0 and d == 0:
        return True
    return surd_floor(_zphi_surd(c, d)) >= 0


def base_phi_digits(n: int) -> str:
    """Bergman's base-``phi`` representation of a positive integer ``n``.

    Greedy over powers of ``phi``: subtract the largest ``phi**k <= n``, then
    sweep downward through positive and negative powers. Integers always
    terminate, and the standard-form result never contains two adjacent ``1``s.

    >>> base_phi_digits(1)
    '1'
    >>> base_phi_digits(2)
    '10.01'
    >>> base_phi_digits(3)
    '100.01'
    >>> base_phi_digits(4)
    '101.01'
    >>> '11' in base_phi_digits(100)
    False
    """
    if n < 1:
        raise ValueError("base-phi digits here are for positive integers")
    # Largest k with phi**k <= n.
    k = 0
    while True:
        c, d = _phi_power(k + 1)
        if _zphi_nonneg(-c, n - d):   # n - (c*phi + d) >= 0 ?
            k += 1
        else:
            break
    digits: dict[int, int] = {}
    rem_c, rem_d = 0, n
    kk = k
    while not (rem_c == 0 and rem_d == 0):
        c, d = _phi_power(kk)
        if _zphi_nonneg(rem_c - c, rem_d - d):  # remainder - phi**kk >= 0 ?
            digits[kk] = 1
            rem_c, rem_d = rem_c - c, rem_d - d
        else:
            digits.setdefault(kk, 0)
        kk -= 1
    lo = min([0, *digits])
    hi = max(0, k)
    int_part = "".join(str(digits.get(i, 0)) for i in range(hi, -1, -1))
    frac_part = "".join(str(digits.get(i, 0)) for i in range(-1, lo - 1, -1))
    return int_part + ("." + frac_part if frac_part else "")


def base_phi_value(digits: str) -> QuadraticSurd:
    """Parse a base-``phi`` string back to its exact :class:`QuadraticSurd` value.

    Digits left of the radix point weight ``phi**0, phi**1, ...`` (reading right
    to left); digits right of it weight ``phi**-1, phi**-2, ...``. Whitespace
    between digits is ignored, so ``"1 0 0 . 0 1"`` parses fine.

    >>> base_phi_value("100.01")            # equals the integer 3
    QuadraticSurd(a=Fraction(3, 1), b=Fraction(0, 1), D=1)
    >>> base_phi_value(base_phi_digits(50)) == QuadraticSurd.make(50, 0, 1)
    True
    """
    text = "".join(digits.split())
    int_part, _, frac_part = text.partition(".")
    c, d = 0, 0
    for i, ch in enumerate(reversed(int_part)):
        if ch == "1":
            pc, pd = _phi_power(i)
            c, d = c + pc, d + pd
        elif ch != "0":
            raise ValueError(f"base-phi digits must be 0/1, got {ch!r}")
    for i, ch in enumerate(frac_part, start=1):
        if ch == "1":
            pc, pd = _phi_power(-i)
            c, d = c + pc, d + pd
        elif ch != "0":
            raise ValueError(f"base-phi digits must be 0/1, got {ch!r}")
    return _zphi_surd(c, d)
