"""The four turtle curves, plus the Cantor set, as complete SVG documents.

Each generator here fixes an L-system and a turtle geometry, expands the word to
the requested depth, walks it, and hands the polylines to
:func:`~tourbus.fractals.turtle_svg.points_to_svg`. The similarity dimension of
each curve — the exponent ``d`` for which ``N`` copies scaled by ``1/s`` satisfy
``N = s**d`` — is recorded in the SVG ``<title>`` so the figure carries its own
label. Koch is ``ln 4 / ln 3 ≈ 1.2619``, the Sierpiński arrowhead
``ln 3 / ln 2 ≈ 1.5850``, and the Cantor set ``ln 2 / ln 3 ≈ 0.6309``. The
Heighway dragon and the Hilbert curve both fill area in the limit, dimension 2.

Depth caps keep every call cheap: beyond them the generators raise
``ValueError`` rather than emit a multi-megabyte document.
"""

from __future__ import annotations

from . import _svg
from .lsystem import LSystem, expand
from .turtle_svg import TurtleConfig, commands_to_points, points_to_svg

__all__ = ["koch", "sierpinski_arrowhead", "dragon", "hilbert", "cantor"]

_KOCH_MAX = 6
_ARROWHEAD_MAX = 8
_DRAGON_MAX = 14
_HILBERT_MAX = 7
_CANTOR_MAX = 7


def _check(depth: int, cap: int, name: str) -> None:
    if depth < 0:
        raise ValueError(f"{name} depth must be non-negative")
    if depth > cap:
        raise ValueError(f"{name} depth {depth} exceeds the cap of {cap}")


def koch(iterations: int) -> str:
    """The Koch curve of the given depth (dimension ``ln 4 / ln 3 ≈ 1.2619``).

    Axiom ``F`` under ``F -> F+F--F+F`` at 60°; each pass replaces every segment
    with four, so depth ``n`` draws ``4**n`` segments.
    """
    _check(iterations, _KOCH_MAX, "koch")
    word = expand(LSystem("F", {"F": "F+F--F+F"}, angle=60), iterations)
    polylines = commands_to_points(word, TurtleConfig(step=10.0, angle=60.0))
    return points_to_svg(
        polylines, width=1.5, title="Koch curve — dimension ln4/ln3 ≈ 1.2619"
    )


def sierpinski_arrowhead(iterations: int) -> str:
    """The Sierpiński arrowhead curve (dimension ``ln 3 / ln 2 ≈ 1.5850``).

    Axiom ``A`` under ``A -> B-A-B``, ``B -> A+B+A`` at 60°. Both ``A`` and ``B``
    draw, so the single continuous path sweeps out the Sierpiński triangle. The
    start heading flips with the parity of ``iterations`` to keep the figure
    sitting on a level base.
    """
    _check(iterations, _ARROWHEAD_MAX, "sierpinski_arrowhead")
    word = expand(
        LSystem("A", {"A": "B-A-B", "B": "A+B+A"}, angle=60), iterations
    )
    heading = 0.0 if iterations % 2 == 0 else 60.0
    cfg = TurtleConfig(step=10.0, angle=60.0, start_heading=heading)
    polylines = commands_to_points(word, cfg)  # default draw set covers A and B
    return points_to_svg(
        polylines,
        width=1.5,
        title="Sierpinski arrowhead — dimension ln3/ln2 ≈ 1.5850",
    )


def dragon(iterations: int) -> str:
    """The Heighway dragon curve (an area-filling curve, dimension 2).

    Axiom ``F`` under ``F -> F+G``, ``G -> F-G`` at 90°. Both ``F`` and ``G``
    draw; the number of segments doubles each pass, giving ``2**n`` at depth
    ``n``.
    """
    _check(iterations, _DRAGON_MAX, "dragon")
    word = expand(LSystem("F", {"F": "F+G", "G": "F-G"}, angle=90), iterations)
    polylines = commands_to_points(word, TurtleConfig(step=8.0, angle=90.0))
    return points_to_svg(
        polylines, width=1.5, title="Heighway dragon — dimension 2"
    )


def hilbert(order: int) -> str:
    """The Hilbert space-filling curve of the given order (dimension 2).

    Axiom ``A`` under ``A -> +BF-AFA-FB+``, ``B -> -AF+BFB+FA-`` at 90°. Here
    ``A`` and ``B`` are structural variables that never move the pen — only
    ``F`` draws — so the interpreter is given the explicit draw set ``"F"``.
    """
    _check(order, _HILBERT_MAX, "hilbert")
    word = expand(
        LSystem("A", {"A": "+BF-AFA-FB+", "B": "-AF+BFB+FA-"}, angle=90),
        order,
    )
    polylines = commands_to_points(
        word, TurtleConfig(step=10.0, angle=90.0), draw="F"
    )
    return points_to_svg(
        polylines, width=1.5, title=f"Hilbert curve, order {order} — dimension 2"
    )


def cantor(iterations: int) -> str:
    """The Cantor middle-thirds set as stacked bars (dimension ``ln 2 / ln 3``).

    Row 0 is the whole unit interval; each subsequent row removes the open
    middle third of every surviving bar. The rows are drawn top to bottom so the
    dust visibly thins out. Depth ``n`` produces ``n + 1`` rows and ``2**n`` bars
    in the last one.
    """
    _check(iterations, _CANTOR_MAX, "cantor")
    total_width = 300.0
    bar_height = 10.0
    row_gap = 8.0

    rows: list[list[tuple[float, float]]] = [[(0.0, 1.0)]]
    for _ in range(iterations):
        nxt: list[tuple[float, float]] = []
        for a, b in rows[-1]:
            third = (b - a) / 3.0
            nxt.append((a, a + third))
            nxt.append((b - third, b))
        rows.append(nxt)

    rects: list[str] = []
    for i, segments in enumerate(rows):
        y = i * (bar_height + row_gap)
        for a, b in segments:
            x = a * total_width
            w = (b - a) * total_width
            rects.append(
                f'<rect x="{_svg.fmt(x)}" y="{_svg.fmt(y)}" '
                f'width="{_svg.fmt(w)}" height="{_svg.fmt(bar_height)}" '
                f'fill="currentColor"/>'
            )

    bottom = (len(rows) - 1) * (bar_height + row_gap) + bar_height
    vb = _svg.padded_viewbox(0.0, 0.0, total_width, bottom)
    return _svg.document(
        "".join(rects),
        viewbox_str=vb,
        title="Cantor set — dimension ln2/ln3 ≈ 0.6309",
    )
