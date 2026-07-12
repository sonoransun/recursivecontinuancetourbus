"""Huckel molecular-orbital theory as a continuant.

In simple Huckel theory the pi-electron energy levels of a conjugated molecule
are ``E = alpha + x*beta`` where ``x`` runs over the eigenvalues of the
molecule's graph (adjacency matrix). For a **linear polyene** (a path of ``n``
carbons) the secular determinant obeys the very three-term recurrence of
:func:`tourbus.frontier.continuants.continuant` — only with a minus sign, the
Hirzebruch-Jung convention of :func:`tourbus.frontier.variants.minus_cf`:

    phi_0 = 1,  phi_1 = x,  phi_k = x * phi_{k-1} - phi_{k-2}.

Its roots are exactly ``x_k = 2 cos(k*pi/(n+1))``. A conjugated ring of ``n``
carbons (an annulene) has ``x_k = 2 cos(2*pi*k/n)``, which reproduces Huckel's
4n+2 aromaticity rule. And the golden ratio hides in butadiene: its four levels
are exactly ``+/- phi`` and ``+/- 1/phi``.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

__all__ = [
    "secular_polynomial",
    "cycle_secular_polynomial",
    "secular_via_continuant",
    "polyene_energies",
    "annulene_energies",
    "homo_lumo_gap",
    "total_pi_energy",
    "is_aromatic",
]


def _sub(a: list[int], b: list[int]) -> list[int]:
    n = max(len(a), len(b))
    a = [0] * (n - len(a)) + a
    b = [0] * (n - len(b)) + b
    return [x - y for x, y in zip(a, b)]


def _poly_eval(p: Sequence[int], x):
    r = 0
    for c in p:
        r = r * x + c
    return r


def secular_polynomial(n: int) -> list[int]:
    """Integer coefficients (high->low) of the P_n polyene secular determinant.

    This IS the continuant recurrence ``phi_k = x*phi_{k-1} - phi_{k-2}``.

    >>> secular_polynomial(4)          # x^4 - 3x^2 + 1  (butadiene)
    [1, 0, -3, 0, 1]
    >>> secular_polynomial(2)          # x^2 - 1  (ethylene)
    [1, 0, -1]
    """
    if n <= 0:
        return [1]
    prev2, prev = [1], [1, 0]
    for _ in range(2, n + 1):
        shifted = prev + [0]            # x * prev
        prev2, prev = prev, _sub(shifted, prev2)
    return prev


def cycle_secular_polynomial(n: int) -> list[int]:
    """Integer coefficients of the C_n annulene secular determinant.

    Equals ``phi_n - phi_{n-2} - 2`` (trace of the transfer matrix).

    >>> cycle_secular_polynomial(6)    # x^6 - 6x^4 + 9x^2 - 4  (benzene)
    [1, 0, -6, 0, 9, 0, -4]
    """
    phi_n = secular_polynomial(n)
    phi_n2 = secular_polynomial(n - 2)
    poly = _sub(phi_n, phi_n2)
    poly[-1] -= 2
    return poly


def secular_via_continuant(n: int, x: Fraction) -> Fraction:
    """Evaluate the polyene secular determinant at ``x`` by the continuant recurrence.

    >>> secular_via_continuant(4, Fraction(2))
    Fraction(5, 1)
    """
    x = Fraction(x)
    prev2, prev = Fraction(1), x
    if n == 0:
        return Fraction(1)
    for _ in range(2, n + 1):
        prev2, prev = prev, x * prev - prev2
    return prev


def polyene_energies(n: int) -> list[float]:
    """The ``n`` polyene levels ``2 cos(k*pi/(n+1))`` in units of beta, descending.

    >>> [round(e, 6) for e in polyene_energies(4)]    # +/- phi, +/- 1/phi
    [1.618034, 0.618034, -0.618034, -1.618034]
    """
    return sorted((2 * math.cos(k * math.pi / (n + 1)) for k in range(1, n + 1)),
                  reverse=True)


def annulene_energies(n: int) -> list[float]:
    """The ``n`` annulene levels ``2 cos(2*pi*k/n)``, descending.

    >>> [round(e, 6) for e in annulene_energies(6)]   # benzene
    [2.0, 1.0, 1.0, -1.0, -1.0, -2.0]
    """
    return sorted((2 * math.cos(2 * math.pi * k / n) for k in range(n)), reverse=True)


def homo_lumo_gap(levels: Sequence[float], n_electrons: int) -> float:
    """HOMO-LUMO gap (in units of |beta|) filling 2 electrons per level.

    >>> round(homo_lumo_gap(annulene_energies(6), 6), 6)
    2.0
    """
    n_occ = n_electrons // 2
    if n_occ == 0 or n_occ >= len(levels):
        return 0.0
    return levels[n_occ - 1] - levels[n_occ]


def total_pi_energy(levels: Sequence[float], n_electrons: int) -> float:
    """Total pi-electron energy (sum of occupied x, times beta), 2 e- per level.

    >>> total_pi_energy(annulene_energies(6), 6)
    8.0
    """
    remaining = n_electrons
    total = 0.0
    for x in levels:
        take = min(2, remaining)
        total += take * x
        remaining -= take
        if remaining <= 0:
            break
    return total


def is_aromatic(ring_size: int, n_electrons: int) -> str:
    """Huckel 4n+2 verdict from the pi-electron count of a conjugated monocycle.

    >>> is_aromatic(6, 6), is_aromatic(4, 4), is_aromatic(8, 8)
    ('aromatic', 'antiaromatic', 'antiaromatic')
    >>> is_aromatic(5, 6)   # cyclopentadienyl anion: aromatic (6 pi e-)
    'aromatic'
    """
    if n_electrons % 4 == 2:
        return "aromatic"
    if n_electrons % 4 == 0 and ring_size % 4 == 0:
        return "antiaromatic"
    return "nonaromatic"
