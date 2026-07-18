"""Bhaskara II's chakravala, the cyclic method for Pell's equation.

Five centuries before Brouncker, the chakravala ("wheel") solved
``x^2 - n*y^2 = 1`` by composing approximate solutions. Carry a triple
``(a, b, k)`` with ``a^2 - n*b^2 = k`` and repeatedly compose it with the
trivial identity ``m^2 - n*1^2 = m^2 - n`` (Brahmagupta's samasa), dividing
out ``k`` each turn of the wheel. Choosing ``m`` near ``sqrt(n)`` keeps the
new ``k`` small, and the wheel provably comes to rest at ``k = 1`` — the
fundamental solution, reached in exact integers with no square roots taken.

This is the plain historical iteration: no Brahmagupta shortcut cases for
``k`` in ``{-1, +-2, 4}``, every turn recorded. The modern route through the
periodic continued fraction of ``sqrt(n)`` lives in
:func:`~tourbus.numbertheory.pell.fundamental_solution`; the two agree on
every ``n``, which is no accident — the chakravala's ``m`` choices shadow the
partial quotients.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt

__all__ = ["ChakravalaStep", "chakravala_steps", "chakravala"]


@dataclass(frozen=True)
class ChakravalaStep:
    """One turn of the wheel: a triple ``(a, b, k)`` with ``a^2 - n*b^2 = k``.

    ``m`` is the multiplier chosen to *reach* this triple from the previous
    one; it is ``None`` on the initial step, which is not reached but chosen.

    >>> ChakravalaStep(8, 1, 3, None)
    ChakravalaStep(a=8, b=1, k=3, m=None)
    """

    a: int
    b: int
    k: int
    m: int | None


def chakravala_steps(n: int) -> list[ChakravalaStep]:
    """The full chakravala trace for ``x^2 - n*y^2 = 1``, down to ``k == 1``.

    Starts from ``(a, 1, a^2 - n)`` with ``a`` the integer nearest
    ``sqrt(n)`` (``|a^2 - n|`` minimal). While ``k != 1``, picks the
    ``m > 0`` with ``abs(k)`` dividing ``a + b*m`` — of the two such
    candidates bracketing ``sqrt(n)``, the one minimizing ``|m^2 - n|``
    (tie: the smaller) — and composes:

        ``a, b, k  <-  (a*m + n*b)/|k|, (a + b*m)/|k|, (m^2 - n)/k``

    Raises :class:`ValueError` for ``n < 2`` or a perfect square ``n``.

    >>> steps = chakravala_steps(61)
    >>> steps[0]
    ChakravalaStep(a=8, b=1, k=3, m=None)
    >>> steps[1]
    ChakravalaStep(a=39, b=5, k=-4, m=7)
    >>> steps[-1].k
    1
    """
    if n < 2:
        raise ValueError(f"n must be >= 2, got {n}")
    s = isqrt(n)
    if s * s == n:
        raise ValueError(f"n must not be a perfect square, got {n}")

    # Initial triple: b = 1 and a nearest sqrt(n). No tie is possible
    # (n - s^2 == (s+1)^2 - n would force 2*n odd).
    a = min(s, s + 1, key=lambda c: abs(c * c - n))
    b, k = 1, a * a - n
    steps = [ChakravalaStep(a, b, k, None)]

    while k != 1:
        t = abs(k)
        # b and k are coprime throughout the iteration, so the residue class
        # m = -a * b^{-1} (mod t) exists; its two members bracketing sqrt(n)
        # are the only candidates worth composing with.
        r = (-a * pow(b, -1, t)) % t
        below = r + ((s - r) // t) * t          # largest class member <= sqrt(n)
        candidates = [m for m in (below, below + t) if m > 0]
        m = min(candidates, key=lambda c: (abs(c * c - n), c))
        # Brahmagupta composition with (m, 1, m^2 - n), scaled down by k.
        # All three divisions are exact.
        a, b, k = (a * m + n * b) // t, (a + b * m) // t, (m * m - n) // k
        steps.append(ChakravalaStep(a, b, k, m))
    return steps


def chakravala(n: int) -> tuple[int, int]:
    """The fundamental solution ``(x, y)`` of ``x^2 - n*y^2 = 1``, by chakravala.

    Raises :class:`ValueError` for ``n < 2`` or a perfect square ``n``.

    >>> chakravala(61)
    (1766319049, 226153980)
    >>> chakravala(67)
    (48842, 5967)
    >>> chakravala(4)
    Traceback (most recent call last):
        ...
    ValueError: n must not be a perfect square, got 4
    """
    last = chakravala_steps(n)[-1]
    return last.a, last.b
