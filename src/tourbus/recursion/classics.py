"""The recursion hall of fame: Ackermann, hyperoperations, Y, and McCarthy 91.

These are the canonical stress tests of what "recursion" even means:

* **Ackermann-Peter** is the textbook total-computable function that is *not*
  primitive recursive — it grows too fast for any bounded loop. We evaluate it
  with an explicit stack so Python's own call stack is never at risk.
* the **hyperoperation** hierarchy (add, multiply, exponentiate, tetrate, ...)
  is the ladder Ackermann is climbing.
* the **Y combinator** manufactures recursion out of nothing but functions —
  no name ever refers to itself.
* **McCarthy 91** is the classic verification puzzle whose nested recursion
  collapses to a suspiciously simple closed form.
"""

from __future__ import annotations

from typing import Callable

__all__ = ["ackermann", "hyperoperation", "y_combinator", "mccarthy91"]


def ackermann(m: int, n: int) -> int:
    """The Ackermann-Peter function, evaluated with an explicit stack.

    Defined by ``A(0, n) = n + 1``, ``A(m + 1, 0) = A(m, 1)`` and
    ``A(m + 1, n + 1) = A(m, A(m + 1, n))``. Rather than recurse in Python (which
    would blow the interpreter's stack almost immediately), we keep a list of
    pending ``m`` values and fold ``n`` through them iteratively — so the only
    limit is time and memory, never ``RecursionError``.

    >>> ackermann(2, 2)
    7
    >>> ackermann(3, 3)
    61
    >>> ackermann(3, 4)
    125
    >>> [ackermann(2, n) for n in range(5)]
    [3, 5, 7, 9, 11]

    ``A(4, 2)`` already has 19,729 digits, so keep the arguments small.
    """
    if m < 0 or n < 0:
        raise ValueError("Ackermann is defined for non-negative m, n")
    stack = [m]
    while stack:
        m = stack.pop()
        if m == 0:
            n = n + 1
        elif n == 0:
            stack.append(m - 1)
            n = 1
        else:
            stack.append(m - 1)  # outer A(m-1, .)
            stack.append(m)      # inner A(m, n-1) computed first
            n = n - 1
    return n


def _tetration(a: int, b: int) -> int:
    """``a`` tetrated to height ``b`` (``a^^b``): a tower of ``b`` copies of ``a``.

    Recursive by design — ``a^^b = a ** (a^^(b-1))`` — and only ever called with
    ``b`` tiny, so the Python recursion depth stays trivial.
    """
    if b == 0:
        return 1
    return a ** _tetration(a, b - 1)


def hyperoperation(n: int, a: int, b: int) -> int:
    """The ``n``-th hyperoperation ``H_n(a, b)`` in the standard indexing.

    ``H_0(a, b) = b + 1`` (successor), ``H_1 = a + b`` (addition),
    ``H_2 = a * b`` (multiplication), ``H_3 = a ** b`` (exponentiation) and
    ``H_4 = a^^b`` (tetration, a tower of ``b`` copies of ``a``). Levels 0-3 are
    computed directly; tetration is built up from exponentiation.

    Tetration explodes: ``3^^4 = 3**(3**27)`` has over three trillion digits. To
    keep the tour finite, ``n >= 4`` raises :class:`ValueError` once ``b > 3`` (or
    ``b > 2`` with a base above 3), and ``n >= 5`` (pentation and beyond) is
    refused outright.

    >>> hyperoperation(1, 3, 4)          # 3 + 4
    7
    >>> hyperoperation(2, 3, 4)          # 3 * 4
    12
    >>> hyperoperation(3, 3, 3)          # 3 ** 3
    27
    >>> hyperoperation(4, 3, 3)          # 3^^3 = 3**(3**3) = 3**27
    7625597484987
    """
    if n < 0:
        raise ValueError("hyperoperation level n must be >= 0")
    if a < 0 or b < 0:
        raise ValueError("hyperoperation is defined here for non-negative a, b")
    if n == 0:
        return b + 1
    if n == 1:
        return a + b
    if n == 2:
        return a * b
    if n == 3:
        return a ** b
    if n >= 5:
        raise ValueError(
            "hyperoperation levels >= 5 (pentation and beyond) grow too fast to "
            "compute; this tour stops at tetration"
        )
    # n == 4: tetration, guarded against astronomically large towers.
    if b > 3 or (a > 3 and b > 2):
        raise ValueError(
            f"tetration {a}^^{b} would be astronomically large; keep b small "
            "(b <= 3, and b <= 2 once a > 3)"
        )
    return _tetration(a, b)


def y_combinator() -> Callable:
    """Return a fixed-point combinator for defining recursion without self-names.

    This is the *applicative-order* fixed point (the strict Z combinator), so it
    works under Python's eager evaluation. Feed it a function that expects "a copy
    of itself" as its first argument and it returns the recursive function, with
    no name anywhere referring to itself:

    >>> fac = y_combinator()(lambda f: lambda k: 1 if k == 0 else k * f(k - 1))
    >>> fac(10)
    3628800
    >>> fib = y_combinator()(lambda f: lambda k: k if k < 2 else f(k - 1) + f(k - 2))
    >>> [fib(k) for k in range(8)]
    [0, 1, 1, 2, 3, 5, 8, 13]
    """
    return lambda f: (lambda x: f(lambda *a: x(x)(*a)))(
        lambda x: f(lambda *a: x(x)(*a))
    )


def mccarthy91(n: int) -> int:
    """McCarthy's 91 function, evaluated iteratively via a pending-call counter.

    The nested definition ``M(n) = n - 10`` for ``n > 100`` else ``M(M(n + 11))``
    famously collapses to ``91`` for every ``n <= 100`` and ``n - 10`` above it.
    Instead of recursing we track how many ``M`` applications are still pending;
    the loop reproduces the nesting exactly with no call stack.

    >>> [mccarthy91(n) for n in (0, 1, 50, 99, 100)]
    [91, 91, 91, 91, 91]
    >>> mccarthy91(101)
    91
    >>> mccarthy91(200)
    190
    """
    pending = 1
    while pending:
        if n > 100:
            n -= 10
            pending -= 1
        else:
            n += 11
            pending += 1
    return n
