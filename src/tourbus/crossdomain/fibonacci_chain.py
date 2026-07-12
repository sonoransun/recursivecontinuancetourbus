"""The Fibonacci quasicrystal: the golden ratio as a solid.

Iterate the substitution ``a -> ab``, ``b -> a`` on a single ``a`` and you get
the **Fibonacci word** ``a, ab, aba, abaab, abaababa, ...`` — the canonical
one-dimensional quasicrystal. Lay a *long* tile of length ``phi`` for every
``a`` and a *short* tile of length ``1`` for every ``b`` and the atoms sit at
positions that live exactly in the ring ``Z[phi]``: every coordinate is a
:class:`~tourbus.cf.core.QuadraticSurd` ``p + q*sqrt(5)``.

Because the golden ratio is the number *least* approximable by rationals
(its continued fraction is ``[1; 1, 1, 1, ...]``), the chain is perfectly
ordered yet never periodic, and its X-ray diffraction pattern is a dense set of
sharp Bragg peaks indexed by *two* integers ``(h, k)``. The **brightest** peaks
land at ``(h, k) = (F_{n+1}, F_n)`` — precisely the numerator/denominator of the
golden ratio's continued-fraction convergents (:func:`tourbus.cf.convergents`).
Number theory's worst-approximable number is condensed matter's sharpest
diffraction.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from ..cf.constants import phi_cf
from ..cf.convergents import convergent_pairs
from ..cf.core import QuadraticSurd

__all__ = [
    "fibonacci_word",
    "tile_frequencies",
    "fibonacci_chain_positions",
    "structure_factor",
    "peak_wavevector",
    "DiffractionPeak",
    "diffraction_peaks",
    "fibonacci_peak_ladder",
]

# The golden ratio as an exact surd and as a float, reused throughout.
PHI = QuadraticSurd.from_pqd(1, 5, 2)         # (1 + sqrt(5)) / 2
_TAU = float(PHI)


def fibonacci_word(order: int) -> str:
    """The Fibonacci word after ``order`` inflations of ``a`` (``a->ab``, ``b->a``).

    >>> [fibonacci_word(n) for n in range(5)]
    ['a', 'ab', 'aba', 'abaab', 'abaababa']
    >>> [len(fibonacci_word(n)) for n in range(6)]      # the Fibonacci numbers
    [1, 2, 3, 5, 8, 13]
    """
    word = "a"
    for _ in range(order):
        word = "".join("ab" if c == "a" else "a" for c in word)
    return word


def tile_frequencies(order: int) -> tuple[Fraction, Fraction]:
    """Exact fractions of long (``a``) and short (``b``) tiles at a given order.

    The ratio of the two tends to the golden ratio; the frequencies are ratios
    of consecutive Fibonacci numbers.

    >>> tile_frequencies(10)
    (Fraction(89, 144), Fraction(55, 144))
    """
    word = fibonacci_word(order)
    length = len(word)
    count_a = word.count("a")
    count_b = length - count_a
    return Fraction(count_a, length), Fraction(count_b, length)


def fibonacci_chain_positions(order: int, short=Fraction(1), long=None) -> list:
    """Cumulative atom positions of the tiled chain (``a`` = long, ``b`` = short).

    With ``long=None`` (the default) the long tile is the golden ratio and the
    short tile is ``1``, so every position is an **exact**
    :class:`~tourbus.cf.core.QuadraticSurd` in ``Z[phi]`` (a rational plus a
    rational multiple of ``sqrt(5)``). Supply a numeric ``long`` to get ordinary
    ``float`` positions instead.

    >>> [str(p) for p in fibonacci_chain_positions(2)]        # word 'aba'
    ['0', '1/2 + 1/2*sqrt(5)', '3/2 + 1/2*sqrt(5)', '2 + sqrt(5)']
    >>> fibonacci_chain_positions(2, long=2.0, short=1.0)     # numeric tiles
    [0.0, 2.0, 3.0, 5.0]
    """
    word = fibonacci_word(order)
    if long is None:
        # Exact Z[phi]: track coefficients (a, b) of  a + b*sqrt(5).
        # long tile = phi = 1/2 + 1/2 sqrt(5); short tile = short (rational).
        short = Fraction(short)
        ca = Fraction(0)
        cb = Fraction(0)
        positions = [QuadraticSurd.make(ca, cb, 5)]
        for c in word:
            if c == "a":
                ca += Fraction(1, 2)
                cb += Fraction(1, 2)
            else:
                ca += short
            positions.append(QuadraticSurd.make(ca, cb, 5))
        return positions
    s = float(short)
    ell = float(long)
    x = 0.0
    positions = [0.0]
    for c in word:
        x += ell if c == "a" else s
        positions.append(x)
    return positions


def structure_factor(positions: Sequence, Q: float) -> float:
    """The single-slit structure factor ``|sum_j exp(i Q x_j)|^2 / N``.

    A direct discrete Fourier transform of the atom positions. It equals the
    atom count ``N`` when ``Q = 0`` (every atom scatters in phase) and spikes at
    the reciprocal vectors of the quasicrystal.

    >>> pos = fibonacci_chain_positions(6, long=1.618, short=1.0)
    >>> round(structure_factor(pos, 0.0), 6)
    22.0
    """
    xs = [float(p) for p in positions]
    amp = sum(cmath.exp(1j * Q * x) for x in xs)
    return abs(amp) ** 2 / len(xs)


def peak_wavevector(h: int, k: int) -> float:
    """Physical-space wavevector ``Q_par = 2 pi (h tau + k) / sqrt(tau + 2)``.

    The cut-and-project construction indexes every Bragg peak by two integers;
    this is the peak's position along the chain (``tau`` is the golden ratio).

    >>> round(peak_wavevector(1, 1), 6)
    8.648063
    >>> round(peak_wavevector(2, 1), 6)
    13.992859
    """
    return 2 * math.pi * (h * _TAU + k) / math.sqrt(_TAU + 2)


@dataclass(frozen=True)
class DiffractionPeak:
    """One Bragg reflection: Miller indices, parallel-space position, intensity."""

    h: int
    k: int
    q_parallel: float
    q_perp: float
    intensity: float


def diffraction_peaks(order: int, hmax: int = 8, top: int = 10) -> list[DiffractionPeak]:
    """The strongest Fibonacci Bragg peaks, indexed by ``(h, k)``.

    Scans integer indices ``|h|, |k| <= hmax`` (keeping one of each Friedel pair
    ``+/-(h, k)``). The peak sits at ``Q_par = 2 pi (h tau + k) / sqrt(tau + 2)``
    with a perpendicular-space coordinate ``Q_perp = 2 pi (k tau - h) /
    sqrt(tau + 2)``; its intensity is the window ``sinc^2(Q_perp * w / 2)`` with
    ``w = tau^2 / sqrt(tau + 2)``. The brightest peaks are exactly those whose
    ``h/k`` is a golden-ratio convergent, so ``Q_perp -> 0``.

    >>> peaks = diffraction_peaks(6, hmax=8, top=4)
    >>> [(p.h, p.k) for p in peaks]
    [(8, 5), (5, 3), (3, 2), (2, 1)]
    >>> round(peaks[0].intensity, 4)
    0.9861
    """
    root = math.sqrt(_TAU + 2)
    window = _TAU * _TAU / root
    peaks: list[DiffractionPeak] = []
    for h in range(-hmax, hmax + 1):
        for k in range(-hmax, hmax + 1):
            if h == 0 and k == 0:
                continue
            if not (h > 0 or (h == 0 and k > 0)):     # canonical Friedel half
                continue
            q_par = 2 * math.pi * (h * _TAU + k) / root
            q_perp = 2 * math.pi * (k * _TAU - h) / root
            arg = q_perp * window / 2
            sinc = 1.0 if arg == 0 else math.sin(arg) / arg
            peaks.append(DiffractionPeak(h, k, q_par, q_perp, sinc * sinc))
    peaks.sort(key=lambda p: (-p.intensity, abs(p.q_parallel)))
    return peaks[:top]


def fibonacci_peak_ladder(m: int) -> list[tuple[int, int]]:
    """The ``m`` brightest peak indices ``(h, k) = (F_{n+1}, F_n)``.

    These are literally the convergents of the golden ratio's continued fraction
    ``[1; 1, 1, ...]`` — the numerator/denominator pairs from
    :func:`tourbus.cf.convergents.convergent_pairs` applied to
    :func:`tourbus.cf.constants.phi_cf`.

    >>> fibonacci_peak_ladder(6)
    [(1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (13, 8)]
    """
    return [(h, k) for h, k in convergent_pairs(phi_cf().terms(m))]
