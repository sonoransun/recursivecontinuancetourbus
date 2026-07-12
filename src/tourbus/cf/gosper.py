"""Gosper's exact continued-fraction arithmetic (HAKMEM item 101).

Arithmetic performed directly on the partial-quotient *streams*, never on
floating-point or truncated decimals. Two engines:

* :func:`homographic` emits the continued fraction of ``(a*x + b) / (c*x + d)``
  from the stream of ``x``.
* :func:`bihomographic` emits ``(a*xy + b*x + c*y + d) / (e*xy + f*x + g*y + h)``
  from the streams of ``x`` and ``y`` — giving ``x+y``, ``x-y``, ``x*y``,
  ``x/y`` for free.

Each engine keeps a small integer state, *ingests* an input term when the
output is not yet determined, and *emits* an output term when every corner of
the input's remaining range agrees on the next integer. This is recursion
meeting corecursion: the recurrence consumes structure, Gosper produces it,
one term at a time and only when certain.

Termination is the subtle part. On a finite (rational) input the stream ends
and the leftover exact rational is flushed. On two infinite inputs whose true
result is rational (e.g. ``sqrt(2) * sqrt(2) == 2``) no finite prefix can prove
the result — the engine would ingest forever — so a generous stall guard raises
:class:`GosperStall` to make that undecidability visible rather than hang.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Iterator

from .core import CF, CFKind
from .expand import cf_from_fraction

__all__ = [
    "GosperStall",
    "homographic",
    "bihomographic",
    "add",
    "sub",
    "mul",
    "div",
    "affine",
    "reciprocal",
]

DEFAULT_STALL_LIMIT = 5000


class GosperStall(RuntimeError):
    """Raised when the engine ingests too long without emitting a term.

    In practice this means the true result is rational while the inputs are
    infinite streams — a case no finite computation can certify.
    """


def _same_sign(p: int, q: int) -> bool:
    return (p > 0 and q > 0) or (p < 0 and q < 0)


def homographic(
    x: Iterable[int],
    m: tuple[int, int, int, int],
    *,
    stall_limit: int = DEFAULT_STALL_LIMIT,
) -> Iterator[int]:
    """Emit the continued fraction of ``(a*x + b) / (c*x + d)``.

    >>> list(homographic(iter([1, 2, 2, 2, 2, 2, 2]), (0, 1, 1, 0)))[:4]  # 1/sqrt-ish
    [0, 1, 2, 2]
    """
    a, b, c, d = m
    # Degenerate (constant) transform: value is a/c everywhere.
    if a * d - b * c == 0:
        if c != 0:
            yield from cf_from_fraction(Fraction(a, c))
        elif d != 0:
            yield from cf_from_fraction(Fraction(b, d))
        return

    it = iter(x)
    ingested = 0
    since_emit = 0
    while True:
        can_emit = (
            ingested >= 1
            and c != 0
            and (c + d) != 0
            and _same_sign(c, c + d)
        )
        if can_emit:
            q_hi = a // c              # input tail -> +inf
            q_lo = (a + b) // (c + d)  # input tail == 1
            if q_hi == q_lo:
                q = q_hi
                yield q
                a, b, c, d = c, d, a - q * c, b - q * d
                since_emit = 0
                continue
        # Need more of the input.
        try:
            p = next(it)
        except StopIteration:
            # Input finished: the remaining value is exactly a/c.
            if c != 0:
                yield from cf_from_fraction(Fraction(a, c))
            return
        a, b, c, d = a * p + b, a, c * p + d, c
        ingested += 1
        since_emit += 1
        if since_emit > stall_limit:
            raise GosperStall("homographic ingested too long without emitting")


def bihomographic(
    x: Iterable[int],
    y: Iterable[int],
    m: tuple[int, int, int, int, int, int, int, int],
    *,
    stall_limit: int = DEFAULT_STALL_LIMIT,
) -> Iterator[int]:
    """Emit the CF of ``(a*xy + b*x + c*y + d) / (e*xy + f*x + g*y + h)``."""
    a, b, c, d, e, f, g, h = m
    ix: Iterator[int] | None = iter(x)
    iy: Iterator[int] | None = iter(y)
    got_x = got_y = 0
    since_emit = 0

    while True:
        # If either input is exhausted, the problem collapses to a single-
        # variable homographic transform (that variable's tail -> +infinity).
        if ix is None and iy is None:
            if e != 0:
                yield from cf_from_fraction(Fraction(a, e))
            return
        if ix is None:
            # x -> infinity: value = (a*y + b) / (e*y + f)
            yield from homographic(iy, (a, b, e, f), stall_limit=stall_limit)
            return
        if iy is None:
            # y -> infinity: value = (a*x + c) / (e*x + g)
            yield from homographic(ix, (a, c, e, g), stall_limit=stall_limit)
            return

        # Try to emit: the four corner denominators must be nonzero & same sign.
        dens = (e, e + f, e + g, e + f + g + h)
        nums = (a, a + b, a + c, a + b + c + d)
        can_emit = (
            got_x >= 1
            and got_y >= 1
            and all(dv != 0 for dv in dens)
            and all(_same_sign(dens[0], dv) for dv in dens[1:])
        )
        if can_emit:
            qs = {nums[i] // dens[i] for i in range(4)}
            if len(qs) == 1:
                q = qs.pop()
                yield q
                a, b, c, d, e, f, g, h = (
                    e, f, g, h,
                    a - q * e, b - q * f, c - q * g, d - q * h,
                )
                since_emit = 0
                continue

        # Otherwise ingest. Choose the variable with more remaining influence,
        # measured by the sub-transform determinants |a*g - c*e| (x) vs
        # |a*f - b*e| (y). Ties and degeneracies fall back to whatever is live.
        infl_x = abs(a * g - c * e)
        infl_y = abs(a * f - b * e)
        ingest_x = infl_x >= infl_y
        if ingest_x:
            try:
                p = next(ix)
                a, b, c, d, e, f, g, h = (
                    a * p + c, b * p + d, a, b,
                    e * p + g, f * p + h, e, f,
                )
                got_x += 1
            except StopIteration:
                ix = None
                continue
        else:
            try:
                p = next(iy)
                a, b, c, d, e, f, g, h = (
                    a * p + b, a, c * p + d, c,
                    e * p + f, e, g * p + h, g,
                )
                got_y += 1
            except StopIteration:
                iy = None
                continue
        since_emit += 1
        if since_emit > stall_limit:
            raise GosperStall(
                "bihomographic ingested too long without emitting "
                "(the exact result is likely rational)"
            )


# --------------------------------------------------------------------------- #
#  Friendly wrappers returning CF objects.
# --------------------------------------------------------------------------- #

def _bi(x: CF, y: CF, m, *, stall_limit=DEFAULT_STALL_LIMIT) -> CF:
    kind = (
        CFKind.FINITE
        if x.is_finite() and y.is_finite()
        else CFKind.UNKNOWN
    )
    return CF.from_stream(
        lambda: bihomographic(iter(x), iter(y), m, stall_limit=stall_limit),
        kind=kind,
    )


def add(x: CF, y: CF, *, stall_limit=DEFAULT_STALL_LIMIT) -> CF:
    """Exact ``x + y`` as a continued fraction."""
    return _bi(x, y, (0, 1, 1, 0, 0, 0, 0, 1), stall_limit=stall_limit)


def sub(x: CF, y: CF, *, stall_limit=DEFAULT_STALL_LIMIT) -> CF:
    """Exact ``x - y``."""
    return _bi(x, y, (0, 1, -1, 0, 0, 0, 0, 1), stall_limit=stall_limit)


def mul(x: CF, y: CF, *, stall_limit=DEFAULT_STALL_LIMIT) -> CF:
    """Exact ``x * y``."""
    return _bi(x, y, (1, 0, 0, 0, 0, 0, 0, 1), stall_limit=stall_limit)


def div(x: CF, y: CF, *, stall_limit=DEFAULT_STALL_LIMIT) -> CF:
    """Exact ``x / y``."""
    return _bi(x, y, (0, 1, 0, 0, 0, 0, 1, 0), stall_limit=stall_limit)


def affine(x: CF, p: Fraction | int, q: Fraction | int = 0) -> CF:
    """Exact ``p*x + q`` for rational ``p, q``."""
    p = Fraction(p)
    q = Fraction(q)
    pn, pd = p.numerator, p.denominator
    qn, qd = q.numerator, q.denominator
    # p*x + q = (pn*qd*x + qn*pd) / (pd*qd)
    m = (pn * qd, qn * pd, 0, pd * qd)
    kind = CFKind.FINITE if x.is_finite() else CFKind.UNKNOWN
    return CF.from_stream(lambda: homographic(iter(x), m), kind=kind)


def reciprocal(x: CF) -> CF:
    """Exact ``1 / x``."""
    kind = CFKind.FINITE if x.is_finite() else CFKind.UNKNOWN
    return CF.from_stream(lambda: homographic(iter(x), (0, 1, 1, 0)), kind=kind)
