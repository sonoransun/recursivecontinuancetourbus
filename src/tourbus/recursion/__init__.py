"""Recursion: the greatest hits, and the machinery underneath them.

This subpackage gathers the recursion set-pieces of the tour and the tools that
make them behave. Two flavours live here:

* **Fast, exact recurrences** — :func:`matrix_pow`, :func:`linear_recurrence`
  and :func:`fib` reach the ``n``-th term of any linear recurrence in
  ``O(log n)`` big-integer work via the companion matrix.
* **The recursion menagerie** — the :func:`ackermann` function (explicit-stack,
  never Python-recursive), the :func:`hyperoperation` ladder it climbs, the
  :func:`y_combinator` that conjures recursion from pure functions, and
  :func:`mccarthy91`.

:func:`counting_memoize` and :func:`fib_naive` sit alongside them to make the
cost of naive recursion visible and the cure measurable.
"""

from __future__ import annotations

from .classics import ackermann, hyperoperation, mccarthy91, y_combinator
from .memo import counting_memoize, fib_naive
from .recurrence import fib, linear_recurrence, matrix_pow

__all__ = [
    "ackermann",
    "hyperoperation",
    "y_combinator",
    "mccarthy91",
    "fib",
    "linear_recurrence",
    "matrix_pow",
    "counting_memoize",
    "fib_naive",
]
