"""Rendering primitives for the command-line tour.

Pure functions that turn data into strings: aligned tables, horizontal bar
charts, ASCII histograms, framed boxes, the route map, and the two-dimensional
"stacked" rendering of a continued fraction. Everything takes a
:class:`~tourbus.tour.termio.Console` for width and styling so the same code
draws in colour, monochrome, or pure ASCII.
"""

from __future__ import annotations

from typing import Sequence

from .termio import Console


def route_line(total: int, current: int, console: Console) -> str:
    """The ``●━━◉━━○`` progress rail with a ``STOP k / N`` label."""
    g = console.glyphs
    dots = []
    for i in range(1, total + 1):
        if i < current:
            dots.append(console.style(g.route_done, "route_done"))
        elif i == current:
            dots.append(console.style(g.route_here, "route_here"))
        else:
            dots.append(console.style(g.route_ahead, "route_ahead"))
    link = console.style(g.route_link * 2, "chrome")
    label = console.style(f"STOP {current} / {total}", "title")
    return link.join(dots) + "   " + label


def stop_header(number: int, total: int, title: str, console: Console) -> str:
    """A full stop banner: rule, route line, title, rule."""
    rule = console.style(console.glyphs.h * console.width, "chrome")
    rail = " " + route_line(total, number, console)
    heading = " " + console.style(title.upper(), "title")
    return "\n".join([rule, rail, heading, rule])


def table(
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    *,
    console: Console,
    highlight: int | None = None,
    right_align: Sequence[int] | None = None,
    indent: str = " ",
) -> str:
    """A simple aligned text table; ``highlight`` marks one row in green."""
    right = set(right_align or [])
    cells = [[str(c) for c in row] for row in rows]
    ncol = len(headers)
    widths = [len(str(headers[j])) for j in range(ncol)]
    for row in cells:
        for j in range(ncol):
            widths[j] = max(widths[j], len(row[j]) if j < len(row) else 0)

    def fmt_row(values: Sequence[str]) -> str:
        parts = []
        for j in range(ncol):
            v = values[j] if j < len(values) else ""
            parts.append(v.rjust(widths[j]) if j in right else v.ljust(widths[j]))
        return indent + "  ".join(parts)

    header_line = console.style(fmt_row([str(h) for h in headers]), "title")
    sep = console.style(
        indent + "  ".join("-" * widths[j] for j in range(ncol)), "chrome"
    )
    out = [header_line, sep]
    for i, row in enumerate(cells):
        line = fmt_row(row)
        if highlight is not None and i == highlight:
            line = console.style(line, "success")
        out.append(line)
    return "\n".join(out)


def hbars(
    pairs: Sequence[tuple[str, float]],
    *,
    console: Console,
    max_value: float | None = None,
    bar_width: int | None = None,
    indent: str = " ",
) -> str:
    """A horizontal bar chart from ``(label, value)`` pairs."""
    if not pairs:
        return ""
    labels = [p[0] for p in pairs]
    values = [float(p[1]) for p in pairs]
    hi = max_value if max_value is not None else max(values) or 1.0
    label_w = max(len(l) for l in labels)
    val_w = max(len(f"{v:g}") for v in values)
    width = bar_width or max(10, console.width - len(indent) - label_w - val_w - 4)
    g = console.glyphs
    out = []
    for label, value in zip(labels, values):
        filled = int(round((value / hi) * width)) if hi else 0
        bar = console.style(g.bar * filled, "result")
        out.append(f"{indent}{label.rjust(label_w)} {bar} {value:g}".rstrip())
    return "\n".join(out)


def histogram(
    counts: dict[int, float],
    *,
    console: Console,
    predicted: dict[int, float] | None = None,
    bar_width: int = 30,
    indent: str = " ",
) -> str:
    """Observed-vs-predicted frequency bars keyed by integer bucket."""
    if not counts:
        return ""
    keys = sorted(counts)
    hi = max(counts.values()) or 1.0
    if predicted:
        hi = max(hi, max(predicted.get(k, 0) for k in keys))
    g = console.glyphs
    out = []
    for k in keys:
        obs = counts[k]
        filled = int(round((obs / hi) * bar_width)) if hi else 0
        bar = console.style(g.bar * filled, "result")
        line = f"{indent}{str(k).rjust(3)} {bar} {obs:6.4f}"
        if predicted and k in predicted:
            line += console.style(f"   (predict {predicted[k]:6.4f})", "chrome")
        out.append(line)
    return "\n".join(out)


def box(body: str, *, console: Console, title: str | None = None, indent: str = " ") -> str:
    """Frame a block of text; optional title sits on the top border."""
    g = console.glyphs
    lines = body.split("\n")
    inner = max((len(l) for l in lines), default=0)
    if title:
        inner = max(inner, len(title) + 2)
    top_label = f" {title} " if title else ""
    top = g.tl + top_label + g.h * (inner - len(top_label) + 1) + g.tr
    bottom = g.bl + g.h * (inner + 1) + g.br
    out = [indent + console.style(top, "chrome")]
    for l in lines:
        out.append(indent + console.style(g.v, "chrome") + " " + l.ljust(inner) + console.style(g.v, "chrome"))
    out.append(indent + console.style(bottom, "chrome"))
    return "\n".join(out)


def stacked_fraction(terms: Sequence[int], *, console: Console, max_terms: int = 5) -> str:
    """Render ``[a0; a1, ...]`` as a 2-D staircase of stacked fractions."""
    shown = list(terms[:max_terms])
    truncated = len(terms) > max_terms
    if truncated:
        shown = shown + ["…"]  # ellipsis as a final "term"
    lines, _ = _frac_block(shown, console.glyphs.h)
    return "\n".join(" " + l for l in lines)


def _frac_block(terms, bar_char: str):
    if len(terms) == 1:
        return [str(terms[0])], 0
    a0 = terms[0]
    sub_lines, _ = _frac_block(terms[1:], bar_char)
    sub_w = max(len(l) for l in sub_lines)
    sub_lines = [l.ljust(sub_w) for l in sub_lines]
    num = "1"
    bar_w = max(sub_w, len(num))
    frac_lines = [num.center(bar_w), bar_char * bar_w] + sub_lines
    bar_index = 1
    prefix = f"{a0} + "
    pad = " " * len(prefix)
    out = []
    for i, l in enumerate(frac_lines):
        out.append((prefix if i == bar_index else pad) + l)
    return out, bar_index


def two_columns(left: str, right: str, *, console: Console, gap: int = 4) -> str:
    """Place two text blocks side by side (used for step-trace vs table)."""
    lcol = left.split("\n")
    rcol = right.split("\n")
    lw = max((len(l) for l in lcol), default=0)
    height = max(len(lcol), len(rcol))
    lcol += [""] * (height - len(lcol))
    rcol += [""] * (height - len(rcol))
    return "\n".join(
        f" {lcol[i].ljust(lw)}{' ' * gap}{rcol[i]}" for i in range(height)
    )
