"""Harper's equation and the Hofstadter butterfly, built on the continuant.

An electron on a square lattice in a magnetic field of ``p/q`` flux quanta per
plaquette obeys **Harper's equation**

    psi_{n+1} + psi_{n-1} + 2 cos(2pi (p/q) n + nu) psi_n = E psi_n,

a tridiagonal eigenproblem with a ``q``-periodic diagonal. Plotting its allowed
energies against the flux draws the **Hofstadter butterfly**, a self-similar
fractal indexed by the continued fraction of the flux.

The engine underneath is the one from the Engine Room. The characteristic
polynomial of the truncated operator is a **Sturm sequence**

    d_k = (a_{k-1} - E) d_{k-1} - b^2 d_{k-2},   d_0 = 1, d_{-1} = 0,

which is exactly the three-term recurrence of
:func:`tourbus.frontier.continuants.continuant` (with ``b^2 = -1`` it *is* the
continuant of the shifted diagonal). Sign changes in that sequence count
eigenvalues, so the same recurrence that generates convergents also locates the
spectral bands. The bands themselves are read from the ``q``-step transfer
matrix, whose trace is the discriminant ``Delta(E)`` — the band condition is
``|Delta(E)| <= 4``, the polynomial echo of ``|2 cos| <= 2``.

A parity subtlety worth keeping in mind: for **odd** ``q`` the butterfly shows
``q`` clean bands and ``q - 1`` gaps, while for **even** ``q`` the two central
bands *touch* at a Dirac point ``E = 0``, so the picture reads as ``q`` bands
with a middle kiss.

On symmetry: the **band** spectrum (``|Delta(E)| <= 4``) is ``E -> -E`` symmetric
for every ``q``, because ``Delta`` has definite parity — that is the symmetry the
butterfly shows. The eigenvalues of the finite **open (Dirichlet) chain** from
:func:`harper_spectrum`, however, are exactly ``E -> -E`` symmetric only at
``q = 2``; for ``q >= 3`` they are merely traceless (sum to zero), since the
Dirichlet boundary breaks the chiral symmetry.
"""

from __future__ import annotations

import math
from math import gcd

from ..cf.convergents import convergent_pairs
from ..cf.expand import cf_from_fraction

__all__ = [
    "harper_diagonal",
    "sturm_sequence",
    "count_eigenvalues_below",
    "harper_spectrum",
    "harper_discriminant",
    "harper_bands",
    "gap_labels",
    "butterfly_svg",
]


def harper_diagonal(p: int, q: int, phase: float = 0.0) -> list[float]:
    """The ``q`` diagonal entries ``a_j = 2 cos(2pi (p/q) j + phase)``.

    >>> [round(a, 6) for a in harper_diagonal(1, 2)]
    [2.0, -2.0]
    >>> [round(a, 6) for a in harper_diagonal(1, 3)]
    [2.0, -1.0, -1.0]
    """
    return [2.0 * math.cos(2.0 * math.pi * (p / q) * j + phase) for j in range(q)]


def sturm_sequence(diag, lam: float, *, offdiag_sq: float = 1.0) -> list[float]:
    """The Sturm sequence ``d_0, d_1, ..., d_q`` of the tridiagonal ``A - lam I``.

    Uses the three-term recurrence ``d_k = (a_{k-1} - lam) d_{k-1} - b^2 d_{k-2}``
    with ``d_0 = 1``, ``d_{-1} = 0`` and ``b^2 = offdiag_sq``. The final entry
    ``d_q`` is the characteristic determinant. This *is* the continuant
    recurrence of :func:`tourbus.frontier.continuants.continuant`: with
    ``offdiag_sq = -1`` the sign flips to a plus and the values become literal
    continuants of the shifted diagonal.

    >>> sturm_sequence([2.0, -2.0], 0.0)          # det[[2,1],[1,-2]] = -5
    [1.0, 2.0, -5.0]
    >>> from tourbus.frontier.continuants import continuant
    >>> sturm_sequence([3, 7, 15, 1], 0.0, offdiag_sq=-1.0)[-1] == continuant([3, 7, 15, 1])
    True
    """
    d_prev2, d_prev = 0.0, 1.0  # d_{-1}, d_0
    out = [d_prev]
    for a in diag:
        d = (a - lam) * d_prev - offdiag_sq * d_prev2
        out.append(d)
        d_prev2, d_prev = d_prev, d
    return out


def count_eigenvalues_below(diag, lam: float, *, offdiag_sq: float = 1.0) -> int:
    """Count eigenvalues ``< lam`` of the tridiagonal operator (Sturm's theorem).

    Uses the numerically stable quotient form ``q_k = (a_k - lam) - b^2/q_{k-1}``
    (the ratio ``d_{k+1}/d_k`` of the Sturm sequence); the number of negative
    ``q_k`` equals the number of eigenvalues below ``lam``. A vanishing pivot is
    nudged by a tiny epsilon to keep the recurrence finite.

    >>> count_eigenvalues_below([2.0, -2.0], 0.0)     # one of +/-sqrt(5) is < 0
    1
    >>> count_eigenvalues_below([2.0, -2.0], -3.0)    # both above -3
    0
    """
    tiny = 1e-300
    count = 0
    q_prev = 0.0
    for k, a in enumerate(diag):
        if k == 0:
            qk = a - lam
        else:
            if q_prev == 0.0:
                q_prev = tiny
            qk = (a - lam) - offdiag_sq / q_prev
        if qk < 0.0:
            count += 1
        q_prev = qk
    return count


def harper_spectrum(p: int, q: int, *, phase: float = 0.0, tol: float = 1e-12) -> list[float]:
    """The ``q`` eigenvalues of the open (Dirichlet) tridiagonal Harper matrix.

    Found by Sturm bisection on :func:`count_eigenvalues_below`, so no linear
    algebra library is needed. Every eigenvalue lies in ``[-4, 4]`` (Gershgorin),
    and their sum is ``0`` because the diagonal of a full period sums to zero.
    For ``q = 2`` the chain is ``[[2, 1], [1, -2]]`` and the spectrum is the
    symmetric pair ``+/- sqrt(5)``.

    >>> [round(e, 6) for e in harper_spectrum(1, 2)]        # +/- sqrt(5)
    [-2.236068, 2.236068]
    >>> abs(sum(harper_spectrum(2, 5))) < 1e-9              # traceless
    True
    """
    diag = harper_diagonal(p, q, phase)
    lo, hi = -4.0 - 1e-9, 4.0 + 1e-9
    eigs: list[float] = []
    for k in range(1, q + 1):
        a, b = lo, hi
        while b - a > tol:
            mid = 0.5 * (a + b)
            if count_eigenvalues_below(diag, mid) < k:
                a = mid
            else:
                b = mid
        eigs.append(0.5 * (a + b))
    return eigs


def _transfer_trace(p: int, q: int, E: float, phase: float) -> float:
    """Trace of the ``q``-step transfer matrix ``M_{q-1} ... M_0`` at phase ``nu``.

    Each ``M_j = [[E - a_j, -1], [1, 0]]`` advances Harper's recurrence one site.
    """
    a = harper_diagonal(p, q, phase)
    m00, m01, m10, m11 = 1.0, 0.0, 0.0, 1.0
    for j in range(q):
        e = E - a[j]
        n00 = e * m00 - m10
        n01 = e * m01 - m11
        n10 = m00
        n11 = m01
        m00, m01, m10, m11 = n00, n01, n10, n11
    return m00 + m11


def harper_discriminant(p: int, q: int, E: float) -> float:
    """The phase-independent Harper discriminant ``Delta(E)``.

    The single-phase transfer trace still carries the phase ``nu``; averaging the
    traces at ``nu = 0`` and ``nu = pi/q`` cancels it, leaving the discriminant
    that governs the bands. An energy ``E`` lies in the spectrum iff
    ``|Delta(E)| <= 4``. For flux ``1/2`` the discriminant is exactly ``E^2 - 4``
    and for flux ``1/3`` it is ``E^3 - 6E``.

    >>> harper_discriminant(1, 2, 0.0)                      # E^2 - 4 at E=0
    -4.0
    >>> round(harper_discriminant(1, 2, 2 * 2 ** 0.5), 6)   # E^2 - 4 at E=2sqrt2
    4.0
    >>> [round(harper_discriminant(1, 2, e), 6) for e in (0.0, 1.0, 2.0)]
    [-4.0, -3.0, 0.0]
    >>> round(harper_discriminant(1, 3, 2.0), 6)            # E^3 - 6E at E=2
    -4.0
    """
    t0 = _transfer_trace(p, q, E, 0.0)
    t1 = _transfer_trace(p, q, E, math.pi / q)
    return 0.5 * (t0 + t1)


def _refine_band_edge(func, a: float, b: float, inside_at_a: bool, steps: int = 60) -> float:
    """Bisect ``[a, b]`` for the ``|Delta| = 4`` crossing between them."""
    for _ in range(steps):
        mid = 0.5 * (a + b)
        if (abs(func(mid)) <= 4.0) == inside_at_a:
            a = mid
        else:
            b = mid
    return 0.5 * (a + b)


def harper_bands(p: int, q: int, *, steps: int = 4000, span: float = 4.0) -> list[tuple[float, float]]:
    """The spectral bands ``{E : |Delta(E)| <= 4}`` as ``(low, high)`` intervals.

    The energy axis ``[-span, span]`` is scanned on a grid to find the connected
    components where ``|Delta| <= 4``, then each interior edge is sharpened by
    bisection. Odd ``q`` yields ``q`` disjoint bands; even ``q`` yields ``q``
    bands whose two central members touch at ``E = 0``. The flux-``1/2`` band
    edges are ``+/- 2 sqrt(2)``.

    >>> [(round(a, 4), round(b, 4)) for a, b in harper_bands(1, 2)]   # +/- 2sqrt2
    [(-2.8284, 2.8284)]
    >>> [(round(a, 4), round(b, 4)) for a, b in harper_bands(1, 3)]
    [(-2.7321, -2.0), (-0.7321, 0.7321), (2.0, 2.7321)]
    """
    def g(E: float) -> float:
        return harper_discriminant(p, q, E)

    xs = [-span + 2.0 * span * i / steps for i in range(steps + 1)]
    inside = [abs(g(x)) <= 4.0 for x in xs]
    bands: list[tuple[float, float]] = []
    i = 0
    while i <= steps:
        if inside[i]:
            j = i
            while j + 1 <= steps and inside[j + 1]:
                j += 1
            low = xs[i]
            high = xs[j]
            if i > 0:
                low = _refine_band_edge(g, xs[i], xs[i - 1], True)
            if j < steps:
                high = _refine_band_edge(g, xs[j], xs[j + 1], True)
            bands.append((low, high))
            i = j + 1
        else:
            i += 1
    return bands


def gap_labels(p: int, q: int) -> list[tuple[int, int]]:
    """Continued-fraction convergent labels of the principal spectral gaps.

    The gaps of the butterfly are labeled by the gap-labeling theorem; the
    dominant ones sit at the convergents ``h_i / k_i`` of the flux ``p/q``. This
    returns those convergents as ``(numerator, denominator)`` pairs, straight
    from :func:`tourbus.cf.convergents.convergent_pairs`.

    >>> gap_labels(1, 3)
    [(0, 1), (1, 3)]
    >>> gap_labels(2, 5)
    [(0, 1), (1, 2), (2, 5)]
    """
    from fractions import Fraction

    terms = list(cf_from_fraction(Fraction(p, q)))
    return list(convergent_pairs(terms))


def _fmt(value: float) -> str:
    """Round a coordinate to four decimals, normalizing ``-0`` to ``0``."""
    v = round(float(value), 4)
    if v == 0:
        return "0"
    return f"{v:.4f}".rstrip("0").rstrip(".")


def butterfly_svg(qmax: int, *, height: float = 400.0) -> str:
    """A Hofstadter-butterfly SVG: each reduced flux ``p/q`` (``q <= qmax``) drawn
    as vertical band segments at ``x = p/q``.

    Flux runs left-to-right over ``[0, 1]``; energy runs bottom-to-top over
    ``[-4, 4]``. The document is a single well-formed ``<svg>`` root.

    >>> svg = butterfly_svg(4)
    >>> svg.startswith('<svg') and svg.endswith('</svg>')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    if qmax < 1:
        raise ValueError("qmax must be at least 1")
    width = height
    pad = 0.05 * height
    emax = 4.0

    def sx(flux: float) -> float:
        return pad + flux * (width - 2 * pad)

    def sy(E: float) -> float:
        return height - pad - (E + emax) / (2 * emax) * (height - 2 * pad)

    segments: list[str] = []
    for q in range(1, qmax + 1):
        for p in range(0, q + 1):
            if gcd(p, q) != 1:
                continue
            flux = p / q
            x = sx(flux)
            for low, high in harper_bands(p, q, steps=max(200, 60 * q)):
                segments.append(
                    f'<line x1="{_fmt(x)}" y1="{_fmt(sy(low))}" '
                    f'x2="{_fmt(x)}" y2="{_fmt(sy(high))}"/>'
                )
    body = "".join(segments)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {_fmt(width)} {_fmt(height)}">'
        f"<title>Hofstadter butterfly (q &lt;= {qmax})</title>"
        f'<g stroke="black" stroke-width="0.6">{body}</g>'
        f"</svg>"
    )
