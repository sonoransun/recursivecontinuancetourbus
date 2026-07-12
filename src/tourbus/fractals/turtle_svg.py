"""A turtle that reads an L-system word and draws it as SVG polylines.

The turtle carries a position and a heading and walks the command string one
symbol at a time. The alphabet is the usual one:

======  ====================================================================
symbol  action
======  ====================================================================
draw    move forward one step, extending the current polyline
``f``   move forward one step *without* drawing (breaks the polyline)
``+``   turn left by ``cfg.angle`` degrees
``-``   turn right by ``cfg.angle`` degrees
``[``   push the current position and heading onto a stack
``]``   pop them back (a jump, so the polyline breaks)
======  ====================================================================

Which letters count as *draw* is configurable, and that flexibility is the
whole trick behind reusing one interpreter for four different curves. In the
Koch and dragon systems ``F`` and ``G`` both draw; in the Sierpiński arrowhead
``A`` and ``B`` draw; in the Hilbert system ``A`` and ``B`` are non-drawing
variables and only ``F`` draws. The default draw set ``"FGAB"`` handles the
first three; Hilbert passes an explicit ``draw="F"``.

Coordinates are computed with the mathematical convention (``y`` grows upward)
and flipped once, at render time, because SVG's ``y`` axis points down.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence

from . import _svg

__all__ = ["TurtleConfig", "commands_to_points", "points_to_svg"]

Point = tuple[float, float]
Polyline = list[Point]

DEFAULT_DRAW = "FGAB"


@dataclass
class TurtleConfig:
    """Geometry knobs for the turtle walk.

    ``step`` is the length of one forward move, ``angle`` the number of degrees
    a ``+``/``-`` turns through, and ``start_heading`` the initial direction in
    degrees measured counter-clockwise from the positive x-axis.
    """

    step: float = 10.0
    angle: float = 90.0
    start_heading: float = 0.0


def commands_to_points(
    commands: str,
    cfg: TurtleConfig,
    *,
    draw: Iterable[str] = DEFAULT_DRAW,
) -> list[Polyline]:
    """Interpret an L-system ``commands`` word into a list of polylines.

    Each polyline is a list of ``(x, y)`` points describing one continuous
    pen-down stroke; the pen lifts (and a new polyline begins) at ``f``, at a
    ``]`` pop, and at the very end. Polylines of a single point draw nothing and
    are dropped.

    >>> cfg = TurtleConfig(step=1, angle=90)
    >>> commands_to_points("F+F", cfg)
    [[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]]
    >>> # 'A' is a non-drawing variable when it is outside the draw set:
    >>> commands_to_points("AA", cfg, draw="F")
    [[(0.0, 0.0)]]
    """
    draw_set = frozenset(draw)
    x = y = 0.0
    heading = math.radians(cfg.start_heading)
    turn = math.radians(cfg.angle)
    step = cfg.step

    polylines: list[Polyline] = []
    current: Polyline = [(x, y)]
    stack: list[tuple[float, float, float]] = []

    def flush() -> None:
        if len(current) >= 2:
            polylines.append(current)

    for ch in commands:
        if ch in draw_set:
            x += step * math.cos(heading)
            y += step * math.sin(heading)
            current.append((x, y))
        elif ch == "f":
            flush()
            x += step * math.cos(heading)
            y += step * math.sin(heading)
            current = [(x, y)]
        elif ch == "+":
            heading += turn
        elif ch == "-":
            heading -= turn
        elif ch == "[":
            stack.append((x, y, heading))
        elif ch == "]":
            flush()
            if stack:
                x, y, heading = stack.pop()
            current = [(x, y)]
        # every other symbol (e.g. a non-drawing variable) is a no-op
    flush()

    # The doctest above wants to see the degenerate single-point stroke, so keep
    # a lone stroke when nothing at all was drawn; otherwise flush() has spoken.
    if not polylines:
        polylines.append(current if len(current) >= 1 else [(0.0, 0.0)])
    return polylines


def points_to_svg(
    polylines: Sequence[Polyline],
    *,
    stroke: str = "currentColor",
    width: float = 1.0,
    pad_frac: float = 0.05,
    title: str | None = None,
) -> str:
    """Render polylines as a complete, standalone ``<svg>`` document string.

    The bounding box is taken over every point, the image is flipped vertically
    so it reads upright, and a ``pad_frac`` margin is added. Each polyline uses
    a rounded-join, rounded-cap ``<polyline>`` with ``fill="none"`` and a
    non-scaling stroke so the line stays visible however the SVG is scaled.
    """
    all_points = [p for poly in polylines for p in poly]
    if not all_points:
        return _svg.document("", viewbox_str=_svg.viewbox(0, 0, 1, 1), title=title)

    # Flip y (SVG grows downward) before measuring so the box matches the marks.
    flipped = [[(x, -y) for (x, y) in poly] for poly in polylines]
    flat = [p for poly in flipped for p in poly]
    minx, miny, maxx, maxy = _svg.bounds(flat)
    vb = _svg.padded_viewbox(minx, miny, maxx, maxy, pad_frac=pad_frac)

    parts: list[str] = []
    for poly in flipped:
        if len(poly) < 2:
            continue
        pts = " ".join(f"{_svg.fmt(x)},{_svg.fmt(y)}" for x, y in poly)
        parts.append(
            f'<polyline points="{pts}" fill="none" stroke="{stroke}" '
            f'stroke-width="{_svg.fmt(width)}" stroke-linecap="round" '
            f'stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
        )
    return _svg.document("".join(parts), viewbox_str=vb, title=title)
