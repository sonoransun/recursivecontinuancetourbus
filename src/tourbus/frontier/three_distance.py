"""The three-distance theorem: a surprise hiding in ``{k*alpha mod 1}``.

Drop the points ``0, alpha, 2*alpha, ..., (N-1)*alpha`` (mod 1) onto a circle.
However you choose ``alpha`` and ``N``, those points cut the circle into arcs of
**at most three distinct lengths** — and when there are three, the largest is the
sum of the other two. This is the **three-distance** (or three-gap) theorem,
conjectured by Steinhaus and proved in the 1950s.

The continued fraction of ``alpha`` is exactly what controls it: the gap lengths
are the quantities ``||q_k * alpha||`` at the convergent denominators ``q_k``, so
the "resolution" of the point set jumps precisely at the convergents. Rational
approximation and equidistribution turn out to be the same story.
"""

from __future__ import annotations

from fractions import Fraction

__all__ = ["orbit_points", "gap_lengths", "three_distance_report"]


def orbit_points(alpha: Fraction, n: int) -> list[Fraction]:
    """The distinct points ``{k*alpha mod 1 : k = 0, ..., n-1}``, sorted.

    >>> orbit_points(Fraction(1, 3), 3)
    [Fraction(0, 1), Fraction(1, 3), Fraction(2, 3)]
    """
    alpha = Fraction(alpha)
    pts = {Fraction((k * alpha.numerator) % alpha.denominator, alpha.denominator)
           for k in range(n)}
    return sorted(pts)


def gap_lengths(alpha: Fraction, n: int) -> list[Fraction]:
    """The multiset of arc lengths between consecutive orbit points (circular)."""
    pts = orbit_points(alpha, n)
    if len(pts) == 1:
        return [Fraction(1)]
    gaps = [pts[i + 1] - pts[i] for i in range(len(pts) - 1)]
    gaps.append(Fraction(1) - pts[-1] + pts[0])
    return gaps


def three_distance_report(alpha: Fraction, n: int) -> dict:
    """Summarize the gaps: the distinct lengths, their counts, and the theorem check.

    >>> r = three_distance_report(Fraction(5, 8), 6)
    >>> r["num_distinct"] <= 3
    True
    >>> r["largest_is_sum"]
    True
    """
    gaps = gap_lengths(alpha, n)
    counts: dict[Fraction, int] = {}
    for g in gaps:
        counts[g] = counts.get(g, 0) + 1
    distinct = sorted(counts)
    largest_is_sum = True
    if len(distinct) == 3:
        largest_is_sum = distinct[2] == distinct[0] + distinct[1]
    return {
        "alpha": alpha,
        "n": n,
        "num_points": len(orbit_points(alpha, n)),
        "distinct_lengths": distinct,
        "counts": counts,
        "num_distinct": len(distinct),
        "largest_is_sum": largest_is_sum,
        "total": sum(g * c for g, c in counts.items()),  # must be 1
    }
