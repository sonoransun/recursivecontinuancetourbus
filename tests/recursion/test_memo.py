from hypothesis import given
from hypothesis import strategies as st

from tourbus.recursion import counting_memoize, fib, fib_naive


# --- fib_naive ------------------------------------------------------------- #

@given(st.integers(min_value=0, max_value=22))
def test_fib_naive_matches_fast_fib(n):
    assert fib_naive(n) == fib(n)


def test_fib_naive_call_count_is_exponential():
    fib_naive.calls = 0
    fib_naive(10)
    # A naive fib(n) invokes itself 2*fib(n+1) - 1 times.
    assert fib_naive.calls == 2 * fib(11) - 1 == 177


# --- counting_memoize ------------------------------------------------------ #

def test_counting_memoize_returns_correct_values():
    @counting_memoize
    def mfib(n):
        return n if n < 2 else mfib(n - 1) + mfib(n - 2)

    assert [mfib(n) for n in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_counting_memoize_collapses_the_call_tree():
    @counting_memoize
    def mfib(n):
        return n if n < 2 else mfib(n - 1) + mfib(n - 2)

    assert mfib(20) == 6765
    # Memoized fib(n) makes exactly 2n-1 calls, of which n-2 are cache hits, vs
    # the naive 2*fib(n+1)-1 = 21891 calls for n = 20.
    assert mfib.calls == 2 * 20 - 1 == 39
    assert mfib.hits == 20 - 2 == 18
    assert mfib.calls < (2 * fib(21) - 1)  # dramatically fewer than naive


def test_counting_memoize_hits_only_grow_on_repeats():
    @counting_memoize
    def square(n):
        return n * n

    square(3)
    square(4)
    assert square.hits == 0     # two distinct arguments, no hits yet
    square(3)
    assert square.hits == 1     # the repeat is served from cache
    assert square.calls == 3


def test_counting_memoize_preserves_metadata():
    @counting_memoize
    def named(n):
        """A docstring to preserve."""
        return n

    assert named.__name__ == "named"
    assert named.__doc__ == "A docstring to preserve."


@given(st.integers(min_value=0, max_value=25))
def test_memoized_fib_equals_naive_fib(n):
    @counting_memoize
    def mfib(k):
        return k if k < 2 else mfib(k - 1) + mfib(k - 2)

    assert mfib(n) == fib(n)
