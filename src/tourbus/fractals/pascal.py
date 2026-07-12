"""Pascal's triangle modulo 2 — the Sierpiński gasket hiding in the binomials.

Colour a cell of Pascal's triangle black when its binomial coefficient is odd
and white when it is even, and the Sierpiński gasket appears. The reason is
Kummer's theorem / Lucas' congruence: ``C(n, k)`` is odd exactly when the binary
digits of ``k`` are a subset of those of ``n``, which the bit test
``(k & (n - k)) == 0`` decides in one operation without ever forming the
(possibly enormous) coefficient. That the same fractal shows up here and as the
:func:`~tourbus.fractals.curves.sierpinski_arrowhead` turtle curve is the whole
point: self-similar structure has many disguises.
"""

from __future__ import annotations

from . import _svg

__all__ = ["pascal_mod2"]

_ROWS_MAX = 64


def _is_odd_binomial(n: int, k: int) -> bool:
    """Whether ``C(n, k)`` is odd, by Lucas' congruence modulo 2.

    >>> [k for k in range(5) if _is_odd_binomial(4, k)]  # row 4: 1 4 6 4 1
    [0, 4]
    >>> all(_is_odd_binomial(7, k) for k in range(8))     # row 7 is all-odd
    True
    """
    return (k & (n - k)) == 0


def pascal_mod2(rows: int, *, color: str = "currentColor") -> str:
    """Render ``rows`` rows of Pascal's triangle mod 2 as a filled gasket.

    Each odd entry becomes a small upward-pointing triangle; the even entries are
    left blank. Rows are centred so the odd cells tile into the Sierpiński
    gasket. ``color`` fills the triangles and defaults to ``currentColor`` so the
    figure inherits the surrounding text colour in light or dark themes.
    """
    if rows < 1:
        raise ValueError("rows must be at least 1")
    if rows > _ROWS_MAX:
        raise ValueError(f"rows {rows} exceeds the cap of {_ROWS_MAX}")

    cell = 10.0
    half = cell / 2.0
    triangles: list[str] = []
    for n in range(rows):
        y_top = n * cell
        y_bot = y_top + cell
        for k in range(n + 1):
            if not _is_odd_binomial(n, k):
                continue
            cx = (k - n / 2.0) * cell
            pts = (
                f"{_svg.fmt(cx)},{_svg.fmt(y_top)} "
                f"{_svg.fmt(cx - half)},{_svg.fmt(y_bot)} "
                f"{_svg.fmt(cx + half)},{_svg.fmt(y_bot)}"
            )
            triangles.append(f'<polygon points="{pts}" fill="{color}"/>')

    span = rows * cell
    vb = _svg.padded_viewbox(-span / 2.0, 0.0, span / 2.0, span)
    return _svg.document(
        "".join(triangles),
        viewbox_str=vb,
        title=f"Pascal's triangle mod 2, {rows} rows — Sierpinski gasket",
    )
