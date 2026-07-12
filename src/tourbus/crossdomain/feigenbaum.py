"""Period doubling and the Feigenbaum constant, from the logistic map.

The logistic map ``x -> r x (1 - x)`` is the textbook route to chaos. As ``r``
grows, a stable fixed point gives way to a 2-cycle, then a 4-cycle, an 8-cycle,
and so on: the **period-doubling cascade**, accumulating at ``r_inf ~ 3.5699``.
The parameters that matter most are the **superstable** ones ``R_n``, where the
critical point ``x = 1/2`` itself lies on the period-``2^n`` orbit
(so ``f_r^{2^n}(1/2) = 1/2``) and the orbit is maximally attracting.

The successive windows shrink by a universal ratio — the **Feigenbaum constant**

    delta = lim (R_{n-1} - R_{n-2}) / (R_n - R_{n-1}) = 4.6692016...

which is the same for *every* smooth unimodal map. It is a renormalization
eigenvalue: just as the second eigenvalue of the Gauss transfer operator in
:mod:`tourbus.frontier.gkw` sets the rate of a self-similar limit, ``delta`` is
the eigenvalue of the doubling operator acting on maps, and it governs how fast
the cascade converges. Two exact islands sit in the flood of numerics: the first
superstable parameter is ``R_0 = 2`` exactly, and the second is
``R_1 = 1 + sqrt(5)`` -- the golden-ratio surd of Stop 4.
"""

from __future__ import annotations

from ..cf.core import QuadraticSurd

__all__ = [
    "logistic",
    "critical_orbit",
    "superstable_parameter",
    "superstable_ladder",
    "feigenbaum_delta",
    "R1_exact",
    "FEIGENBAUM_DELTA",
    "FEIGENBAUM_ALPHA",
]

#: Feigenbaum's first (bifurcation-rate) constant, to machine precision.
FEIGENBAUM_DELTA = 4.669201609102990

#: Feigenbaum's second (scaling) constant alpha.
FEIGENBAUM_ALPHA = 2.502907875095892


def logistic(r: float, x: float) -> float:
    """One step of the logistic map ``r x (1 - x)``.

    >>> logistic(2.0, 0.5)      # the critical point maps to its own fixed point
    0.5
    >>> round(logistic(3.2, 0.5), 4)
    0.8
    """
    return r * x * (1.0 - x)


def critical_orbit(r: float, n: int) -> list[float]:
    """The ``2^n`` successive iterates of the critical point ``x = 1/2`` under ``f_r``.

    Returns ``[f(1/2), f^2(1/2), ..., f^{2^n}(1/2)]``. At a superstable parameter
    ``R_n`` the orbit has period ``2^n`` through ``1/2``, so the final iterate
    lands back on ``1/2``.

    >>> len(critical_orbit(3.2, 3))
    8
    >>> round(critical_orbit(2.0, 0)[-1], 6)   # R_0 = 2 is superstable, period 1
    0.5
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    x = 0.5
    orbit: list[float] = []
    for _ in range(2 ** n):
        x = r * x * (1.0 - x)
        orbit.append(x)
    return orbit


def _critical_return(r: float, level: int) -> float:
    """``f_r^{2^level}(1/2) - 1/2`` — zero exactly at a level-``level`` superstable ``r``."""
    x = 0.5
    for _ in range(2 ** level):
        x = r * x * (1.0 - x)
    return x - 0.5


def _bisect_root(func, lo: float, hi: float, steps: int) -> float:
    """Bisect for a sign-changing root of ``func`` on ``[lo, hi]``."""
    flo = func(lo)
    fhi = func(hi)
    if (flo > 0.0) == (fhi > 0.0):
        raise ValueError(
            f"bracket [{lo}, {hi}] does not isolate a root "
            f"(f(lo)={flo:.3g}, f(hi)={fhi:.3g})"
        )
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        fmid = func(mid)
        if (fmid > 0.0) == (flo > 0.0):
            lo, flo = mid, fmid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def superstable_parameter(level: int, *, lo: float, hi: float, steps: int = 100) -> float:
    """The superstable parameter ``R_level`` isolated inside the bracket ``[lo, hi]``.

    Finds the root of ``g(r) = f_r^{2^level}(1/2) - 1/2`` by bisection. The
    bracket must contain the level-``level`` root and no earlier one (each
    ``R_m`` with ``m < level`` is also a root of ``g``, so the caller supplies a
    window that isolates the intended cycle).

    >>> round(superstable_parameter(0, lo=1.9, hi=2.1), 6)     # R_0 = 2 exactly
    2.0
    >>> R1 = superstable_parameter(1, lo=3.1, hi=3.3)          # R_1 = 1 + sqrt(5)
    >>> abs(R1 - float(R1_exact())) < 1e-6
    True
    """
    if level < 0:
        raise ValueError("level must be non-negative")
    return _bisect_root(lambda r: _critical_return(r, level), lo, hi, steps)


def superstable_ladder(levels: int) -> list[float]:
    """The ladder ``[R_0, R_1, ..., R_levels]`` of superstable parameters.

    ``R_0`` and ``R_1`` use fixed brackets; from ``R_2`` on, each window is
    predicted from the geometric law ``R_n ~ R_{n-1} + (R_{n-1} - R_{n-2})/delta``
    (with ``delta ~ 4.669``) and bracketed just above ``R_{n-1}`` — which is
    itself a root of the level-``n`` return map — so the bisection catches the
    new cycle. The ladder is strictly increasing and bounded above by the
    accumulation point ``r_inf ~ 3.5699``.

    >>> ladder = superstable_ladder(4)
    >>> ladder[0], round(ladder[1], 6)
    (2.0, 3.236068)
    >>> all(b > a for a, b in zip(ladder, ladder[1:]))    # strictly increasing
    True
    >>> max(ladder) < 3.5700
    True
    """
    if levels < 0:
        raise ValueError("levels must be non-negative")
    ladder = [superstable_parameter(0, lo=1.0, hi=2.9)]
    if levels >= 1:
        ladder.append(superstable_parameter(1, lo=2.9, hi=3.4))
    for n in range(2, levels + 1):
        gap = ladder[n - 1] - ladder[n - 2]
        step = gap / FEIGENBAUM_DELTA
        lo = ladder[n - 1] + 0.4 * step
        hi = ladder[n - 1] + 1.8 * step
        ladder.append(superstable_parameter(n, lo=lo, hi=hi))
    return ladder[: levels + 1]


def feigenbaum_delta(levels: int = 5) -> float:
    """Estimate ``delta`` from the deepest available ratio of window widths.

    Builds the superstable ladder to ``levels`` and returns
    ``(R_{n-1} - R_{n-2}) / (R_n - R_{n-1})`` for the last window; deeper ladders
    converge toward :data:`FEIGENBAUM_DELTA`.

    >>> 4.6 < feigenbaum_delta(4) < 4.7
    True
    >>> abs(feigenbaum_delta(6) - FEIGENBAUM_DELTA) < 0.01
    True
    """
    if levels < 2:
        raise ValueError("need at least three parameters (levels >= 2) for a ratio")
    ladder = superstable_ladder(levels)
    return (ladder[-2] - ladder[-3]) / (ladder[-1] - ladder[-2])


def R1_exact() -> QuadraticSurd:
    """The exact second superstable parameter ``R_1 = 1 + sqrt(5)``.

    An exact quadratic-surd island in the cascade: the golden-ratio radicand
    ``sqrt(5)`` of Stop 4 surfaces as the period-2 superstable parameter, and the
    numeric bisection in :func:`superstable_parameter` reproduces its float.

    >>> R1_exact()
    QuadraticSurd(a=Fraction(1, 1), b=Fraction(1, 1), D=5)
    >>> round(float(R1_exact()), 6)
    3.236068
    """
    return QuadraticSurd.make(1, 1, 5)
