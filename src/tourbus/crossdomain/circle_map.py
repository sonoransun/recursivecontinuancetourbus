"""The sine circle map: mode-locking, Arnold tongues, and the devil's staircase.

The circle map is the simplest system that turns a *continued fraction* into
physics. A point on the circle is driven by

    f(theta) = theta + Omega + (K / 2pi) * sin(2pi * theta)   (mod 1),

with a bare rotation ``Omega`` and a nonlinear coupling ``K``. Its **winding
number** ``w = lim_n (F^n(theta) - theta) / n`` — computed on the *lift* ``F``,
the same formula without the wrap — measures how fast orbits rotate.

When ``K > 0`` the winding number *locks*: for a whole interval of ``Omega`` it
sits exactly on a rational ``p/q`` (a period-``q`` orbit). These locking
intervals are the **Arnold tongues**; plotting ``w`` against ``Omega`` draws the
**devil's staircase**, a monotone function that is constant almost everywhere yet
climbs from 0 to 1. The tongues open first at the rationals with small
denominator — exactly the Farey/Stern-Brocot order of
:mod:`tourbus.numbertheory.stern_brocot` — and the *last* frequency to lock as
``K -> 1`` is the golden mean ``w = 1/phi``, the most badly approximable number
of Stop 4. The whole picture is the continued fraction made visible.
"""

from __future__ import annotations

import math
from fractions import Fraction

from ..cf.convergents import best_approximation
from ..numbertheory.stern_brocot import mediant

__all__ = [
    "lift",
    "winding_number",
    "tongue_boundaries",
    "tongue_width",
    "locked_rational",
    "devil_staircase",
    "farey_tongue_order",
    "staircase_svg",
]

_TAU = 2.0 * math.pi


def lift(theta: float, Omega: float, K: float) -> float:
    """One step of the *lift* ``F(theta) = theta + Omega + (K/2pi) sin(2pi theta)``.

    The lift is not reduced modulo 1, so iterating it accumulates the total
    rotation; ``sin`` is 1-periodic in ``theta`` so this is a genuine lift of the
    circle map.

    >>> round(lift(0.0, 0.3, 0.0), 6)
    0.3
    >>> round(lift(0.25, 0.0, 1.0), 6)   # theta + (1/2pi) sin(pi/2)
    0.409155
    """
    return theta + Omega + (K / _TAU) * math.sin(_TAU * theta)


def _iterate_lift(theta: float, Omega: float, K: float, n: int) -> float:
    """Apply the lift ``n`` times (the ``n``-fold composition ``F^n``)."""
    for _ in range(n):
        theta = theta + Omega + (K / _TAU) * math.sin(_TAU * theta)
    return theta


def winding_number(
    Omega: float,
    K: float,
    *,
    iters: int = 20000,
    warmup: int = 2000,
    theta0: float = 0.0,
) -> float:
    """The winding number ``w = lim (F^n(theta) - theta) / n`` of the lift.

    We iterate the lift (never wrapping — the total rotation is what we measure),
    discard ``warmup`` transient steps to settle onto the attractor, then average
    the per-step increment over ``iters`` steps. At ``K == 0`` the map is the
    rigid rotation ``theta + Omega``, so the winding number is exactly ``Omega``;
    that case is short-circuited to avoid rounding drift.

    >>> winding_number(0.3, 0.0)              # rigid rotation: w == Omega
    0.3
    >>> round(winding_number(0.5, 1.0), 6)    # locked on the 1/2 tongue
    0.5
    >>> round(winding_number(0.02, 1.0), 4)   # inside the 0/1 tongue
    0.0
    """
    if K == 0.0:
        return Omega
    theta = _iterate_lift(theta0, Omega, K, warmup)
    start = theta
    theta = _iterate_lift(theta, Omega, K, iters)
    return (theta - start) / iters


def _extremal_h(Omega: float, p: int, q: int, K: float, grid: int) -> tuple[float, float]:
    """Return ``(min_theta h, max_theta h)`` for ``h = F^q(theta) - theta - p``.

    A period-``q`` orbit with rotation ``p/q`` exists exactly when this range
    straddles zero (``min <= 0 <= max``).
    """
    lo = hi = None
    for j in range(grid):
        theta = j / grid
        h = _iterate_lift(theta, Omega, K, q) - theta - p
        if lo is None or h < lo:
            lo = h
        if hi is None or h > hi:
            hi = h
    return lo, hi  # type: ignore[return-value]


def _bisect_increasing(func, lo: float, hi: float, steps: int) -> float:
    """Bisect for the root of a nondecreasing ``func`` on ``[lo, hi]``."""
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        if func(mid) <= 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def tongue_boundaries(
    p: int,
    q: int,
    K: float,
    *,
    lo: float | None = None,
    hi: float | None = None,
    grid: int = 2000,
    steps: int = 60,
) -> tuple[float, float]:
    """The ``Omega``-interval mode-locked to ``p/q`` at coupling ``K`` (Arnold tongue).

    With ``h(Omega, theta) = F^q(theta) - theta - p`` the period-``q`` orbit
    exists iff ``min_theta h <= 0 <= max_theta h``. Both extrema increase with
    ``Omega``, so the tongue's **left** edge is where ``max_theta h = 0`` and its
    **right** edge is where ``min_theta h = 0``; each is found by bisection. The
    search bracket ``[lo, hi]`` defaults to ``p/q +/- 1/(2q)``. At ``K == 0`` the
    tongue collapses to the single point ``Omega = p/q``.

    >>> lo, hi = tongue_boundaries(0, 1, 1.0)
    >>> round(lo, 4), round(hi, 4)           # symmetric: +/- 1/(2pi)
    (-0.1592, 0.1592)
    >>> tongue_boundaries(1, 2, 0.0)         # no coupling: a point tongue
    (0.5, 0.5)
    """
    center = p / q
    if K == 0.0:
        return (center, center)
    if lo is None:
        lo = center - 0.5 / q
    if hi is None:
        hi = center + 0.5 / q
    left = _bisect_increasing(
        lambda om: _extremal_h(om, p, q, K, grid)[1], lo, hi, steps
    )
    right = _bisect_increasing(
        lambda om: _extremal_h(om, p, q, K, grid)[0], lo, hi, steps
    )
    return (left, right)


def tongue_width(p: int, q: int, K: float, **kw) -> float:
    """Width ``right - left`` of the ``p/q`` Arnold tongue at coupling ``K``.

    The 0/1 tongue is the widest and has the exact width ``K / pi`` (its edges
    are ``Omega = -/+ K/2pi``), so at ``K = 1`` it measures ``1/pi``.

    >>> round(tongue_width(0, 1, 1.0), 4)    # == 1/pi
    0.3183
    >>> tongue_width(0, 1, 0.0)              # every tongue is a point at K=0
    0.0
    """
    left, right = tongue_boundaries(p, q, K, **kw)
    return right - left


def locked_rational(
    Omega: float,
    K: float,
    *,
    max_denominator: int = 50,
    grid: int = 1000,
    **kw,
) -> Fraction | None:
    """The rational ``p/q`` the orbit is locked to at ``(Omega, K)``, else ``None``.

    We estimate the winding number, snap it to a nearby rational with
    :func:`tourbus.cf.convergents.best_approximation`, and then *confirm* the
    plateau: a genuine ``p/q`` lock requires an actual period-``q`` orbit, i.e.
    ``min_theta h <= 0 <= max_theta h`` for ``h = F^q(theta) - theta - p`` at
    this very ``Omega``. At ``K == 0`` nothing locks, so the answer is ``None``.

    >>> locked_rational(0.02, 1.0)           # deep inside the 0/1 tongue
    Fraction(0, 1)
    >>> locked_rational(0.5, 1.0)            # the 1/2 tongue
    Fraction(1, 2)
    >>> locked_rational(0.3, 0.0) is None    # K=0: pure rotation, no locking
    True
    """
    if K == 0.0:
        return None
    w = winding_number(Omega, K, **kw)
    frac = best_approximation(w, max_denominator)
    p, q = frac.numerator, frac.denominator
    lo, hi = _extremal_h(Omega, p, q, K, grid)
    if lo <= 0.0 <= hi:
        return frac
    return None


def devil_staircase(
    K: float,
    *,
    samples: int = 400,
    lo: float = 0.0,
    hi: float = 1.0,
) -> list[tuple[float, float]]:
    """Samples ``(Omega, w)`` of the devil's staircase across ``[lo, hi]``.

    The winding number is mathematically nondecreasing in ``Omega``; a running
    maximum repairs the occasional sub-ULP dip from the finite-time average so
    the returned staircase is guaranteed monotone nondecreasing.

    >>> steps = devil_staircase(1.0, samples=6)
    >>> [round(w, 3) for _, w in steps]
    [0.0, 0.125, 0.393, 0.607, 0.875, 1.0]
    >>> all(b[1] >= a[1] for a, b in zip(steps, steps[1:]))   # monotone
    True
    """
    if samples < 2:
        raise ValueError("need at least two samples")
    out: list[tuple[float, float]] = []
    running = None
    for i in range(samples):
        omega = lo + (hi - lo) * i / (samples - 1)
        w = winding_number(omega, K)
        if running is not None and w < running:
            w = running
        running = w
        out.append((omega, w))
    return out


def farey_tongue_order(depth: int) -> list[Fraction]:
    """The rationals whose tongues open first, in Farey/Stern-Brocot mediant order.

    The widest tongues sit at the simplest rationals. Starting from the boundary
    fractions ``0/1`` and ``1/1`` we repeatedly insert
    :func:`~tourbus.numbertheory.stern_brocot.mediant` children; generation
    ``depth`` lists the tongues that appear by that level, coarsest first. The
    golden mean ``1/phi ~ 0.618`` is the accumulation point these mediants chase
    and the last winding number to lock as ``K -> 1``.

    >>> farey_tongue_order(0)
    [Fraction(0, 1), Fraction(1, 1)]
    >>> farey_tongue_order(2)
    [Fraction(0, 1), Fraction(1, 1), Fraction(1, 2), Fraction(1, 3), Fraction(2, 3)]
    """
    if depth < 0:
        raise ValueError("depth must be non-negative")
    result = [Fraction(0, 1), Fraction(1, 1)]
    brackets = [(Fraction(0, 1), Fraction(1, 1))]
    for _ in range(depth):
        nxt: list[tuple[Fraction, Fraction]] = []
        for left, right in brackets:
            m = mediant(left, right)
            result.append(m)
            nxt.append((left, m))
            nxt.append((m, right))
        brackets = nxt
    return result


def _fmt(value: float) -> str:
    """Round a coordinate to four decimals, normalizing ``-0`` to ``0``."""
    v = round(float(value), 4)
    if v == 0:
        return "0"
    return f"{v:.4f}".rstrip("0").rstrip(".")


def staircase_svg(K: float, *, samples: int = 400, lo: float = 0.0, hi: float = 1.0) -> str:
    """A step-plot SVG of the devil's staircase at coupling ``K``.

    The plot is a single polyline drawn as horizontal-then-vertical steps of
    ``w`` against ``Omega``; the document is one well-formed ``<svg>`` root.

    >>> svg = staircase_svg(1.0, samples=20)
    >>> svg.startswith('<svg') and svg.endswith('</svg>')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    width, height, pad = 640.0, 400.0, 20.0
    pts = devil_staircase(K, samples=samples, lo=lo, hi=hi)
    ws = [w for _, w in pts]
    wmin, wmax = min(ws), max(ws)
    span = (wmax - wmin) or 1.0

    def sx(omega: float) -> float:
        return pad + (omega - lo) / ((hi - lo) or 1.0) * (width - 2 * pad)

    def sy(w: float) -> float:
        return height - pad - (w - wmin) / span * (height - 2 * pad)

    coords: list[tuple[float, float]] = []
    prev_y = sy(pts[0][1])
    coords.append((sx(pts[0][0]), prev_y))
    for omega, w in pts[1:]:
        x, y = sx(omega), sy(w)
        coords.append((x, prev_y))  # horizontal tread
        coords.append((x, y))       # vertical riser
        prev_y = y
    points = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in coords)
    title = f"Devil's staircase, K = {_fmt(K)}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {_fmt(width)} {_fmt(height)}">'
        f"<title>{title}</title>"
        f'<polyline fill="none" stroke="black" stroke-width="1.5" '
        f'points="{points}"/>'
        f"</svg>"
    )
