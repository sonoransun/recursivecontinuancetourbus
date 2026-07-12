"""Memoization, and the call-count blowup it cures.

The naive doubly-recursive Fibonacci recomputes the same subproblems an
exponential number of times; caching each result collapses that to linear work.
This module gives you both sides of the comparison — an instrumented naive
version whose calls you can count, and a counting cache decorator that records
exactly how many of its invocations were served from memory.
"""

from __future__ import annotations

import functools
from typing import Callable

__all__ = ["counting_memoize", "fib_naive"]


def counting_memoize(fn: Callable) -> Callable:
    """Cache ``fn`` by its positional arguments, counting calls and cache hits.

    The wrapper exposes two attributes: ``.calls`` (every invocation, including
    ones served from cache) and ``.hits`` (invocations answered from the cache).
    When applied to a self-recursive function, the recursive calls go through the
    wrapper too, so the memoized recurrence does linear work.

    >>> @counting_memoize
    ... def fib(n):
    ...     return n if n < 2 else fib(n - 1) + fib(n - 2)
    >>> fib(20)
    6765
    >>> fib.calls          # 2*20 - 1 leaf/internal calls, no re-descent
    39
    >>> fib.hits           # every second summand was already cached
    18
    """
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        wrapper.calls += 1
        if args in cache:
            wrapper.hits += 1
            return cache[args]
        result = fn(*args)
        cache[args] = result
        return result

    wrapper.calls = 0
    wrapper.hits = 0
    wrapper.cache = cache
    return wrapper


def fib_naive(n: int) -> int:
    """Doubly-recursive Fibonacci, instrumented with a ``.calls`` counter.

    Correct but deliberately wasteful: ``fib_naive(n)`` invokes itself
    ``2*fib(n+1) - 1`` times, recomputing the same values over and over. Reset
    ``fib_naive.calls = 0`` before a run to measure the blowup and contrast it
    with a :func:`counting_memoize`-wrapped version.

    >>> fib_naive.calls = 0
    >>> fib_naive(10)
    55
    >>> fib_naive.calls        # 2*fib(11) - 1 = 2*89 - 1
    177
    """
    fib_naive.calls += 1
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


fib_naive.calls = 0
