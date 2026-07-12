"""When physics counts the digits of pi: Galperin's colliding blocks.

Put a small block between a wall and a big block, and send the big block in.
Count every collision (block-block and block-wall), assuming perfectly elastic,
frictionless collisions. Galperin's theorem (2003): if the mass ratio is
``100^n``, the total number of collisions is the number formed by the **first
n+1 digits of pi**.

    mass ratio 1        ->  3 collisions
    mass ratio 100      ->  31
    mass ratio 10000    ->  314
    mass ratio 10^6     ->  3141
    ...

Why? The two-body dynamics is, after a change of coordinates, a billiard ball
bouncing inside a wedge of angle ``theta = arctan(sqrt(m/M))``; the number of
bounces is ``floor(pi / theta)``, and for ``m/M = 100^-n`` that floor reads off
pi's digits. It is a startling meeting point of mechanics, rotation numbers, and
pi — and it is exactly computable, because with integer masses and rational
initial data every velocity stays rational forever.
"""

from __future__ import annotations

import decimal
import math
from decimal import Decimal

__all__ = ["galperin_collisions", "pi_prefix"]


def galperin_collisions(n: int) -> int:
    """Event-driven simulation of the two-block system with mass ratio ``100^n``.

    Returns the total number of collisions, which equals the first ``n+1`` digits
    of pi (Galperin's theorem). The simulation uses floating point (the collision
    *count* is a robust integer); :func:`pi_prefix` gives the exact closed form.

    >>> [galperin_collisions(n) for n in range(5)]
    [3, 31, 314, 3141, 31415]
    """
    m, M = 1.0, 100.0 ** n
    xs, vs = 1.0, 0.0        # small block: position, velocity
    xb, vb = 2.0, -1.0       # big block comes in from the right, moving left
    inf = float("inf")
    count = 0
    while True:
        t_wall = -xs / vs if vs < 0 else inf          # small block hits the wall
        t_block = (xb - xs) / (vs - vb) if vs > vb else inf  # small catches big
        t = min(t_wall, t_block)
        if t == inf:
            break            # both move right, big at least as fast: no more hits
        xs += vs * t
        xb += vb * t
        if t_wall <= t_block:
            vs = -vs         # elastic bounce off the wall
        else:
            vs, vb = (
                ((m - M) * vs + 2 * M * vb) / (m + M),
                ((M - m) * vb + 2 * m * vs) / (m + M),
            )
        count += 1
    return count


def _machin_pi(prec: int) -> Decimal:
    with decimal.localcontext() as ctx:
        ctx.prec = prec + 15

        def arctan_inv(k: int) -> Decimal:
            k = Decimal(k)
            total, power, ksq, sign, i = Decimal(0), 1 / k, k * k, 1, 0
            while True:
                term = power / (2 * i + 1)
                if term == 0:
                    break
                total += sign * term
                power /= ksq
                sign = -sign
                i += 1
            return total

        return +(16 * arctan_inv(5) - 4 * arctan_inv(239))


def pi_prefix(n: int) -> int:
    """The number the collision experiment produces: the first ``n+1`` digits of pi.

    Equal to ``floor(pi * 10^n)`` — Galperin's closed form, computed in high
    precision without simulating a single collision. (The geometric picture is
    ``ceil(pi / arctan(10^-n)) - 1``; the two agree.)

    >>> [pi_prefix(n) for n in range(7)]
    [3, 31, 314, 3141, 31415, 314159, 3141592]
    """
    with decimal.localcontext() as ctx:
        ctx.prec = n + 25
        pi = _machin_pi(n + 25)
        scaled = pi * (Decimal(10) ** n)
        return int(scaled.to_integral_value(rounding=decimal.ROUND_FLOOR))
