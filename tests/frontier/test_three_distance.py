from fractions import Fraction

from hypothesis import given
from hypothesis import strategies as st

from tourbus.frontier import three_distance as T


@given(
    st.integers(min_value=2, max_value=80),
    st.integers(min_value=1, max_value=79),
    st.integers(min_value=2, max_value=120),
)
def test_at_most_three_gap_lengths(q, p, n):
    alpha = Fraction(p % q, q)
    rep = T.three_distance_report(alpha, n)
    assert rep["num_distinct"] <= 3


@given(
    st.integers(min_value=2, max_value=80),
    st.integers(min_value=1, max_value=79),
    st.integers(min_value=2, max_value=120),
)
def test_largest_gap_is_sum_and_lengths_total_one(q, p, n):
    alpha = Fraction(p % q, q)
    rep = T.three_distance_report(alpha, n)
    assert rep["largest_is_sum"]
    assert rep["total"] == 1


def test_example():
    rep = T.three_distance_report(Fraction(5, 8), 6)
    assert rep["num_distinct"] == 2
    assert rep["distinct_lengths"] == [Fraction(1, 8), Fraction(1, 4)]
