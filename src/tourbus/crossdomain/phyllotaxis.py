"""Phyllotaxis: why plants grow by the golden angle (biology).

Sunflowers, pinecones, and daisies place each new primordium at the **golden
angle** — a turn of ``2 - phi = (3 - sqrt5)/2`` of a full circle, about
137.507 degrees. This is Stop 4's most-irrational number doing a job: because
phi is the hardest number to approximate by rationals, successive seeds never
line up into radial spokes, and the head fills uniformly. The *visible* spirals
(parastichies) come in counts that are consecutive Fibonacci numbers — precisely
the denominators of phi's convergents ``F_k / F_{k+1}``. A rational divergence
angle ``p/q``, by contrast, collapses the whole head onto ``q`` bare spokes.
"""

from __future__ import annotations

import math
from fractions import Fraction

from ..cf.core import QuadraticSurd
from ..fractals import _svg

__all__ = [
    "golden_angle",
    "golden_angle_degrees",
    "phyllotaxis_points",
    "parastichy_counts",
    "spoke_count",
    "phyllotaxis_svg",
]


def golden_angle() -> QuadraticSurd:
    """The golden divergence angle as a fraction of a turn: ``(3 - sqrt5)/2 = 2 - phi``.

    >>> golden_angle()
    QuadraticSurd(a=Fraction(3, 2), b=Fraction(-1, 2), D=5)
    """
    return QuadraticSurd.make(Fraction(3, 2), Fraction(-1, 2), 5)


def golden_angle_degrees() -> float:
    """The golden angle in degrees, ``360 * (2 - phi)``.

    >>> round(golden_angle_degrees(), 5)
    137.50776
    """
    return 360.0 * float(golden_angle())


def phyllotaxis_points(n: int, angle) -> list[tuple[float, float]]:
    """Vogel's model: seed ``i`` (0-based) at radius ``sqrt(i+1)``, angle ``i*turn``.

    ``angle`` is a divergence angle in *turns* (a fraction of a full circle);
    pass :func:`golden_angle` or any float/Fraction.

    >>> phyllotaxis_points(1, golden_angle())
    [(1.0, 0.0)]
    """
    t = float(angle)
    pts = []
    for i in range(n):
        r = math.sqrt(i + 1)
        theta = 2 * math.pi * i * t
        pts.append((r * math.cos(theta), r * math.sin(theta)))
    return pts


def parastichy_counts(n: int, angle=None) -> tuple[int, int]:
    """The two dominant spiral (parastichy) counts of an ``n``-seed head.

    Detected from the point cloud: the two most common index-gaps between a seed
    and its nearest neighbour. For the golden angle these are consecutive
    Fibonacci numbers.

    >>> parastichy_counts(400, golden_angle())      # consecutive Fibonacci
    (21, 34)
    """
    if angle is None:
        angle = golden_angle()
    pts = phyllotaxis_points(n, angle)
    gaps: dict[int, int] = {}
    # Interior band avoids edge effects; nearest neighbour by squared distance.
    lo, hi = n // 4, 3 * n // 4
    for i in range(lo, hi):
        xi, yi = pts[i]
        best_j, best_d = None, None
        for j in range(max(0, i - 60), min(n, i + 61)):
            if j == i:
                continue
            dx, dy = pts[j][0] - xi, pts[j][1] - yi
            d = dx * dx + dy * dy
            if best_d is None or d < best_d:
                best_d, best_j = d, j
        g = abs(best_j - i)
        gaps[g] = gaps.get(g, 0) + 1
    top = sorted(gaps, key=lambda g: gaps[g], reverse=True)[:2]
    return tuple(sorted(top))  # type: ignore[return-value]


def spoke_count(p: int, q: int) -> int:
    """A rational divergence angle ``p/q`` lands seeds on exactly this many spokes.

    >>> spoke_count(1, 5)
    5
    >>> spoke_count(2, 6)
    3
    """
    return q // math.gcd(p, q)


def phyllotaxis_svg(n: int, angle, *, title: str | None = None, dot: float = 0.7) -> str:
    """Render an ``n``-seed head as SVG dots (well-formed single ``<svg>``).

    >>> phyllotaxis_svg(50, golden_angle()).startswith('<svg')
    True
    """
    pts = phyllotaxis_points(n, angle)
    body = "".join(
        f'<circle cx="{_svg.fmt(x)}" cy="{_svg.fmt(y)}" r="{_svg.fmt(dot)}"/>'
        for x, y in pts
    )
    minx, miny, maxx, maxy = _svg.bounds(pts) if pts else (0, 0, 1, 1)
    vb = _svg.padded_viewbox(minx, miny, maxx, maxy)
    return _svg.document(f'<g fill="currentColor">{body}</g>', viewbox_str=vb, title=title)
