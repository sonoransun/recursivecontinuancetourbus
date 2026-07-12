"""Tiny shared helpers for emitting compact, well-formed SVG.

Nothing here is exported from the subpackage; it is the low plumbing that the
curve, gasket, and call-tree renderers all lean on. Two invariants matter:

* every document is a single ``<svg xmlns=...>`` root so it parses standalone
  under :func:`xml.dom.minidom.parseString`, and
* coordinates are rounded to four decimals so the strings stay small when a
  fractal explodes into thousands of segments.
"""

from __future__ import annotations

from typing import Iterable

Point = tuple[float, float]

_SVG_OPEN = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'


def fmt(value: float) -> str:
    """Format a coordinate as a short decimal string (``-0`` normalized to ``0``).

    >>> fmt(1.0)
    '1'
    >>> fmt(2.50000)
    '2.5'
    >>> fmt(-0.0)
    '0'
    >>> fmt(1.23456789)
    '1.2346'
    """
    v = round(float(value), 4)
    if v == 0:  # collapses both 0.0 and -0.0
        return "0"
    return f"{v:.4f}".rstrip("0").rstrip(".")


def escape(text: str) -> str:
    """Escape the three characters that would break XML character data.

    >>> escape("f(a & b) < c")
    'f(a &amp; b) &lt; c'
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bounds(points: Iterable[Point]) -> tuple[float, float, float, float]:
    """Axis-aligned bounding box ``(minx, miny, maxx, maxy)`` of ``points``.

    >>> bounds([(0, 0), (3, 1), (-1, 4)])
    (-1, 0, 3, 4)
    """
    it = iter(points)
    try:
        x0, y0 = next(it)
    except StopIteration:
        raise ValueError("bounding box of an empty point set is undefined")
    minx = maxx = x0
    miny = maxy = y0
    for x, y in it:
        if x < minx:
            minx = x
        if x > maxx:
            maxx = x
        if y < miny:
            miny = y
        if y > maxy:
            maxy = y
    return minx, miny, maxx, maxy


def viewbox(minx: float, miny: float, width: float, height: float) -> str:
    """Render a viewBox string from a corner and a size."""
    return f"{fmt(minx)} {fmt(miny)} {fmt(width)} {fmt(height)}"


def padded_viewbox(
    minx: float,
    miny: float,
    maxx: float,
    maxy: float,
    *,
    pad_frac: float = 0.05,
) -> str:
    """A viewBox around ``[minx,maxx] x [miny,maxy]`` with a fractional margin.

    Degenerate (zero-width or zero-height) boxes are widened to 1 unit so the
    result is always a finite, non-empty rectangle.
    """
    w = maxx - minx
    h = maxy - miny
    if w <= 0:
        w = 1.0
    if h <= 0:
        h = 1.0
    pad = pad_frac * max(w, h)
    return viewbox(minx - pad, miny - pad, w + 2 * pad, h + 2 * pad)


def document(body: str, *, viewbox_str: str, title: str | None = None) -> str:
    """Wrap ``body`` in a single well-formed ``<svg>`` root element."""
    head = _SVG_OPEN.format(vb=viewbox_str)
    title_el = f"<title>{escape(title)}</title>" if title else ""
    return f"{head}{title_el}{body}</svg>"
