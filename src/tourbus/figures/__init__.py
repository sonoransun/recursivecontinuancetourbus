"""The tour's teaching figures: deterministic SVG documents for the docs.

Each ``fig_*`` function takes no arguments and returns one complete,
standalone ``<svg>`` document string; :data:`FIGURES` at the bottom maps the
committed asset basename to its generator. The build step writes each entry
to ``docs/assets/<name>`` and the converter inlines them, several to a page,
so every figure obeys one theming contract:

* the root ``<svg>`` carries ``color="#6e7781"`` (legible mid-gray on both
  GitHub themes; the site stylesheet overrides it with ``var(--ink)``),
* every stroke and fill is ``currentColor`` (or ``none``),
* no ``<style>`` tags and no ``id`` attributes anywhere, so inlined figures
  can never collide with each other or with the page.

Figures that reuse an existing generator (call tree, phyllotaxis, curves,
butterfly, staircase) are passed through :func:`_themed`, which performs the
string surgery for the contract and re-parses the result to prove it is
still well-formed XML.
"""

from __future__ import annotations

import math
import re
import xml.dom.minidom as minidom
from fractions import Fraction
from math import isqrt
from typing import Callable

from ..cf.constants import e_cf, phi_cf, pi_cf
from ..cf.convergents import convergent_pairs
from ..cf.expand import cf_from_quadratic
from ..crossdomain.circle_map import staircase_svg
from ..crossdomain.hofstadter import butterfly_svg
from ..crossdomain.phyllotaxis import golden_angle, phyllotaxis_svg
from ..dynamics.gauss import gauss_orbit, kuzmin_theoretical
from ..fractals import _svg
from ..fractals.calltree import fib_call_tree, tree_to_svg
from ..fractals.curves import dragon, koch, sierpinski_arrowhead
from ..numbertheory.stern_brocot import farey

__all__ = [
    "fig_calltree",
    "fig_convergent_error",
    "fig_phyllotaxis",
    "fig_period_wheel",
    "fig_stern_brocot",
    "fig_ford_circles",
    "fig_gauss_kuzmin",
    "fig_koch_sierpinski",
    "fig_dragon",
    "fig_markov_tree",
    "fig_butterfly",
    "fig_staircase",
    "fig_topograph",
    "fig_egyptian_growth",
    "fig_zeckendorf",
    "fig_cutting_sequence",
    "fig_rogers_ramanujan",
    "FIGURES",
]

_INK = "#6e7781"


def _themed(svg: str) -> str:
    """Enforce the theming contract on a finished SVG document string.

    Injects ``color="#6e7781"`` into the root tag, rewrites any hardcoded
    ``stroke="black"`` to ``currentColor``, and re-parses the result so the
    surgery can never ship a malformed document.

    >>> _themed('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"></svg>')
    '<svg color="#6e7781" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"></svg>'
    """
    if not svg.startswith("<svg "):
        raise ValueError("expected a document starting with '<svg '")
    out = svg.replace('stroke="black"', 'stroke="currentColor"')
    out = out.replace("<svg ", f'<svg color="{_INK}" ', 1)
    minidom.parseString(out)
    return out


def _text(
    x: float,
    y: float,
    s: str,
    *,
    size: float = 12.0,
    anchor: str = "middle",
    extra: str = "",
) -> str:
    """One themed ``<text>`` element (monospace, ``currentColor``)."""
    at = f" {extra}" if extra else ""
    return (
        f'<text x="{_svg.fmt(x)}" y="{_svg.fmt(y)}" font-family="monospace" '
        f'font-size="{_svg.fmt(size)}" text-anchor="{anchor}" '
        f'fill="currentColor"{at}>{_svg.escape(s)}</text>'
    )


def _line(
    x1: float, y1: float, x2: float, y2: float, *, width: float = 1.0, extra: str = ""
) -> str:
    """One themed ``<line>`` element."""
    at = f" {extra}" if extra else ""
    return (
        f'<line x1="{_svg.fmt(x1)}" y1="{_svg.fmt(y1)}" x2="{_svg.fmt(x2)}" '
        f'y2="{_svg.fmt(y2)}" stroke="currentColor" '
        f'stroke-width="{_svg.fmt(width)}"{at}/>'
    )


def _svg_parts(doc: str) -> tuple[tuple[float, float, float, float], str]:
    """Split a generated document into its viewBox numbers and its body.

    The body is everything inside the root element with the ``<title>``
    removed, ready to be re-wrapped in a ``<g transform=...>`` panel.
    """
    m = re.search(r'viewBox="([^"]+)"', doc)
    if m is None:
        raise ValueError("document has no viewBox")
    parts = tuple(float(t) for t in m.group(1).split())
    body = doc[doc.index(">") + 1 : doc.rindex("</svg>")]
    body = re.sub(r"<title>.*?</title>", "", body, count=1)
    return (parts[0], parts[1], parts[2], parts[3]), body


# --------------------------------------------------------------------------- #
#  1. The fib call tree (Stop 1).
# --------------------------------------------------------------------------- #

def fig_calltree() -> str:
    """The call tree of the naive doubly-recursive ``fib(7)``.

    >>> svg = fig_calltree()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    return _themed(tree_to_svg(fib_call_tree(7)))


# --------------------------------------------------------------------------- #
#  2. Convergent error decay for phi, e, pi (Stop 3).
# --------------------------------------------------------------------------- #

def _error_series(terms: list[int]) -> list[float]:
    """``log10 |x - p_n/q_n|`` for ``n = 0..12``, measured exactly.

    The reference value is the deepest convergent of ``terms`` itself: its
    own error is orders of magnitude below the ``n <= 12`` errors plotted
    (about ``1e-13`` at worst for phi, astronomically less for e and pi), so
    the exact-Fraction differences are correct to far beyond plotting
    precision. Floats appear only inside the final ``log10``.
    """
    pairs = list(convergent_pairs(terms))
    h, k = pairs[-1]
    reference = Fraction(h, k)
    return [
        math.log10(float(abs(reference - Fraction(p, q)))) for p, q in pairs[:13]
    ]


def fig_convergent_error() -> str:
    """How fast convergents converge: ``log10`` error against ``n`` for phi, e, pi.

    phi is the worst-approximable number (the shallowest line), e has its
    patterned middle course, and pi's giant partial quotient 292 shows up as
    the cliff after ``n = 3``. Terms are exact; ``pi``'s come from a
    121-digit certified bracket (the same certified digits as the default
    seed, just cheaper).

    >>> svg = fig_convergent_error()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    series = [
        ("phi", None, _error_series(phi_cf().terms(32))),
        ("e", "7 4", _error_series(e_cf().terms(32))),
        ("pi", "2 4", _error_series(pi_cf(decimal_digits=120).terms(32))),
    ]

    w, h = 760.0, 430.0
    ml, mr, mt, mb = 76.0, 18.0, 30.0, 56.0
    y_top = 0.0
    y_bot = 2.0 * math.floor(min(min(ys) for _, _, ys in series) / 2.0)

    def sx(n: float) -> float:
        return ml + n / 12.0 * (w - ml - mr)

    def sy(v: float) -> float:
        return mt + (y_top - v) / (y_top - y_bot) * (h - mt - mb)

    parts: list[str] = []
    # Axes.
    parts.append(_line(ml, mt, ml, h - mb, width=1.2))
    parts.append(_line(ml, h - mb, w - mr, h - mb, width=1.2))
    for n in range(13):
        parts.append(_line(sx(n), h - mb, sx(n), h - mb + 5, width=1.0))
        parts.append(_text(sx(n), h - mb + 20, str(n), size=11.0))
    v = y_top
    while v >= y_bot:
        parts.append(_line(ml - 5, sy(v), ml, sy(v), width=1.0))
        parts.append(_text(ml - 9, sy(v) + 4, str(int(v)), size=11.0, anchor="end"))
        v -= 2.0
    parts.append(_text((ml + w - mr) / 2.0, h - 14, "n (convergent index)", size=12.0))
    ylx, yly = 20.0, (mt + h - mb) / 2.0
    parts.append(
        _text(
            ylx,
            yly,
            "log10 |x - pn/qn|",
            size=12.0,
            extra=f'transform="rotate(-90 {_svg.fmt(ylx)} {_svg.fmt(yly)})"',
        )
    )

    # The three polylines with point markers.
    for label, dash, ys in series:
        pts = " ".join(f"{_svg.fmt(sx(n))},{_svg.fmt(sy(v))}" for n, v in enumerate(ys))
        dash_at = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(
            f'<polyline points="{pts}" fill="none" stroke="currentColor" '
            f'stroke-width="1.8"{dash_at}/>'
        )
        for n, v in enumerate(ys):
            parts.append(
                f'<circle cx="{_svg.fmt(sx(n))}" cy="{_svg.fmt(sy(v))}" r="2.6" '
                f'fill="currentColor"/>'
            )

    # Legend, top right of the plot area.
    lx, ly = w - mr - 130.0, mt + 16.0
    for i, (label, dash, _ys) in enumerate(series):
        yy = ly + i * 20.0
        dash_at = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(
            f'<line x1="{_svg.fmt(lx)}" y1="{_svg.fmt(yy)}" '
            f'x2="{_svg.fmt(lx + 36)}" y2="{_svg.fmt(yy)}" '
            f'stroke="currentColor" stroke-width="1.8"{dash_at}/>'
        )
        parts.append(_text(lx + 46.0, yy + 4.0, label, size=12.0, anchor="start"))

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Convergent error decay for phi, e, and pi",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  3. Phyllotaxis head at the golden angle (Stop 4).
# --------------------------------------------------------------------------- #

def fig_phyllotaxis() -> str:
    """A 600-seed phyllotaxis head at the golden angle.

    >>> svg = fig_phyllotaxis()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    return _themed(
        phyllotaxis_svg(600, golden_angle(), title="600 seeds at the golden angle")
    )


# --------------------------------------------------------------------------- #
#  4. Period lengths of sqrt(d) (Stop 6).
# --------------------------------------------------------------------------- #

def fig_period_wheel() -> str:
    """Period length of the continued fraction of ``sqrt(d)``, ``d = 2..99``.

    A bar per nonsquare ``d``, with the famous outliers labeled: ``d = 61``
    (the Pell troublemaker, period 11) and ``d = 94`` (the longest period in
    range, 16). No pattern in sight — that is the point.

    >>> svg = fig_period_wheel()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    periods: dict[int, int] = {}
    for d in range(2, 100):
        s = isqrt(d)
        if s * s != d:
            periods[d] = len(cf_from_quadratic(0, d, 1)[1])
    pmax = max(periods.values())

    w, h = 760.0, 380.0
    ml, mr, mt, mb = 62.0, 16.0, 48.0, 50.0

    def sx(d: float) -> float:
        return ml + (d - 2.0) / 97.0 * (w - ml - mr)

    def sy(p: float) -> float:
        return h - mb - p / pmax * (h - mt - mb)

    parts: list[str] = []
    parts.append(
        _text(w / 2.0, 22.0, "Period of the continued fraction of sqrt(d)", size=14.0)
    )
    parts.append(_line(ml, mt, ml, h - mb, width=1.2))
    parts.append(_line(ml, h - mb, w - mr, h - mb, width=1.2))
    for p in range(0, pmax + 1, 4):
        parts.append(_line(ml - 5, sy(p), ml, sy(p), width=1.0))
        parts.append(_text(ml - 9, sy(p) + 4, str(p), size=11.0, anchor="end"))
    for d in (2, 25, 50, 75, 99):
        parts.append(_line(sx(d), h - mb, sx(d), h - mb + 5, width=1.0))
        parts.append(_text(sx(d), h - mb + 20, str(d), size=11.0))
    parts.append(_text((ml + w - mr) / 2.0, h - 12, "d (nonsquare)", size=12.0))
    ylx, yly = 20.0, (mt + h - mb) / 2.0
    parts.append(
        _text(
            ylx,
            yly,
            "period length",
            size=12.0,
            extra=f'transform="rotate(-90 {_svg.fmt(ylx)} {_svg.fmt(yly)})"',
        )
    )

    bar_w = 5.0
    for d in sorted(periods):
        top = sy(periods[d])
        parts.append(
            f'<rect x="{_svg.fmt(sx(d) - bar_w / 2)}" y="{_svg.fmt(top)}" '
            f'width="{_svg.fmt(bar_w)}" height="{_svg.fmt(h - mb - top)}" '
            f'fill="currentColor"/>'
        )
    for d in (61, 94):
        parts.append(_text(sx(d), sy(periods[d]) - 7.0, f"d={d}", size=11.0))

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Period lengths of sqrt(d) for nonsquare d up to 99",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  5. The Stern-Brocot tree (Stop 8).
# --------------------------------------------------------------------------- #

def fig_stern_brocot() -> str:
    """The Stern-Brocot mediant tree to depth 5, with faded ``0/1``, ``1/0`` roots.

    Every node is the mediant of its bracketing ancestors; the layout follows
    the call-tree renderer (leaves in order, parents centered above).

    >>> svg = fig_stern_brocot()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    Node = tuple[tuple[int, int], list]  # ((p, q), children)

    def build(left: tuple[int, int], right: tuple[int, int], depth: int) -> Node:
        node = (left[0] + right[0], left[1] + right[1])
        if depth == 0:
            return (node, [])
        return (node, [build(left, node, depth - 1), build(node, right, depth - 1)])

    root = build((0, 1), (1, 0), 4)  # 5 rows of mediants, 31 nodes

    x_gap, y_gap, radius, font = 46.0, 66.0, 15.0, 10.0
    positions: dict[int, tuple[float, int]] = {}
    leaf = [0]

    def place(node: Node, depth: int) -> float:
        if not node[1]:
            x = float(leaf[0])
            leaf[0] += 1
        else:
            xs = [place(c, depth + 1) for c in node[1]]
            x = sum(xs) / len(xs)
        positions[id(node)] = (x, depth)
        return x

    place(root, 0)

    def screen(node: Node) -> tuple[float, float]:
        x, depth = positions[id(node)]
        return x * x_gap, depth * y_gap

    parts: list[str] = []

    def draw(node: Node) -> None:
        nx, ny = screen(node)
        for child in node[1]:
            cx, cy = screen(child)
            dx, dy = cx - nx, cy - ny
            dist = (dx * dx + dy * dy) ** 0.5 or 1.0
            ux, uy = dx / dist, dy / dist
            parts.append(
                _line(
                    nx + ux * radius,
                    ny + uy * radius,
                    cx - ux * radius,
                    cy - uy * radius,
                    width=1.2,
                )
            )
            draw(child)
        p, q = node[0]
        parts.append(
            f'<circle cx="{_svg.fmt(nx)}" cy="{_svg.fmt(ny)}" '
            f'r="{_svg.fmt(radius)}" fill="none" stroke="currentColor" '
            f'stroke-width="1.2"/>'
        )
        parts.append(
            _text(
                nx,
                ny,
                f"{p}/{q}",
                size=font,
                extra='dominant-baseline="central"',
            )
        )

    draw(root)

    # The boundary "fractions" 0/1 and 1/0 sit above the root, faded: they are
    # the virtual ancestors whose mediant is 1/1.
    rx, ry = screen(root)
    faded: list[str] = []
    for (p, q), off in (((0, 1), -3.2), ((1, 0), 3.2)):
        ex, ey = rx + off * x_gap, ry - y_gap
        dx, dy = rx - ex, ry - ey
        dist = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / dist, dy / dist
        faded.append(
            _line(
                ex + ux * radius,
                ey + uy * radius,
                rx - ux * radius,
                ry - uy * radius,
                width=1.2,
                extra='stroke-dasharray="4 3"',
            )
        )
        faded.append(
            _text(ex, ey, f"{p}/{q}", size=font, extra='dominant-baseline="central"')
        )
    parts.append(f'<g opacity="0.45">{"".join(faded)}</g>')

    minx = -radius
    maxx = (leaf[0] - 1) * x_gap + radius
    miny = -y_gap - radius
    maxy = 4 * y_gap + radius
    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.padded_viewbox(minx, miny, maxx, maxy),
        title="The Stern-Brocot tree to depth 5",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  6. Ford circles over the Farey fractions (Stop 8).
# --------------------------------------------------------------------------- #

def fig_ford_circles() -> str:
    """Ford circles at every ``p/q`` in the Farey sequence ``F_8``.

    Each circle sits at ``(p/q, 1/(2 q^2))`` with radius ``1/(2 q^2)``:
    tangent to the baseline, tangent to each neighbor, never overlapping.
    The largest circles carry their fraction labels.

    >>> svg = fig_ford_circles()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    scale = 380.0  # pixels per unit; the q=1 circles have radius scale/2
    xoff = scale / 2.0
    base = scale + 10.0
    w = 2.0 * scale
    h = base + 34.0

    fractions = list(farey(8))  # includes 0/1 and 1/1
    parts: list[str] = []
    parts.append(_line(xoff, base, xoff + scale, base, width=1.5))
    for tick in (0, 1):
        parts.append(
            _line(xoff + tick * scale, base, xoff + tick * scale, base + 6, width=1.2)
        )
        parts.append(_text(xoff + tick * scale, base + 22, str(tick), size=12.0))

    label_font = {1: 22.0, 2: 16.0, 3: 11.0}
    for f in fractions:
        p, q = f.numerator, f.denominator
        r = scale / (2.0 * q * q)
        cx = xoff + (p / q) * scale
        cy = base - r
        parts.append(
            f'<circle cx="{_svg.fmt(cx)}" cy="{_svg.fmt(cy)}" r="{_svg.fmt(r)}" '
            f'fill="none" stroke="currentColor" stroke-width="1.2"/>'
        )
        if q in label_font:
            parts.append(
                _text(
                    cx,
                    cy,
                    f"{p}/{q}",
                    size=label_font[q],
                    extra='dominant-baseline="central"',
                )
            )

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Ford circles over the Farey sequence F8",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  7. Gauss-Kuzmin: theory vs one long deterministic orbit (Stop 10).
# --------------------------------------------------------------------------- #

def _pi_orbit_digits() -> list[int]:
    """Partial quotients harvested from a fixed deterministic Gauss orbit.

    The seed is the fractional part of the 240-term convergent of pi (an
    exact rational with a 126-digit denominator; the 400-digit certified
    bracket pins the same partial quotients as the default seed). Iterating
    the Gauss map on it and reading off ``floor(1/x)`` at each step yields
    239 digits — no randomness anywhere.
    """
    terms = pi_cf(decimal_digits=400).terms(240)
    h, k = list(convergent_pairs(terms))[-1]
    seed = Fraction(h, k) - 3
    digits: list[int] = []
    for x in gauss_orbit(seed, steps=300):
        if x != 0:
            digits.append(math.floor(1 / x))
    return digits


def fig_gauss_kuzmin() -> str:
    """Gauss-Kuzmin law against the digit counts of one deterministic orbit.

    Paired bars for ``k = 1..10``: the outlined bars are the theoretical
    probabilities ``log2(1 + 1/(k(k+2)))`` (value labels attached); the
    filled bars are observed frequencies along the Gauss-map orbit of pi's
    240-term convergent (see :func:`_pi_orbit_digits` — fixed, no RNG).

    >>> svg = fig_gauss_kuzmin()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    digits = _pi_orbit_digits()
    total = len(digits)
    theory = [kuzmin_theoretical(k) for k in range(1, 11)]
    observed = [digits.count(k) / total for k in range(1, 11)]

    w, h = 760.0, 400.0
    ml, mr, mt, mb = 64.0, 16.0, 34.0, 56.0
    y_max = 0.45
    slot = (w - ml - mr) / 10.0
    bar_w, gap = 22.0, 4.0

    def sy(v: float) -> float:
        return h - mb - v / y_max * (h - mt - mb)

    parts: list[str] = []
    parts.append(_line(ml, mt, ml, h - mb, width=1.2))
    parts.append(_line(ml, h - mb, w - mr, h - mb, width=1.2))
    v = 0.0
    while v <= y_max + 1e-9:
        parts.append(_line(ml - 5, sy(v), ml, sy(v), width=1.0))
        parts.append(_text(ml - 9, sy(v) + 4, f"{v:.1f}", size=11.0, anchor="end"))
        v += 0.1

    for i in range(10):
        cx = ml + (i + 0.5) * slot
        tx = cx - gap / 2.0 - bar_w
        ox = cx + gap / 2.0
        t_top, o_top = sy(theory[i]), sy(observed[i])
        parts.append(
            f'<rect x="{_svg.fmt(tx)}" y="{_svg.fmt(t_top)}" '
            f'width="{_svg.fmt(bar_w)}" height="{_svg.fmt(h - mb - t_top)}" '
            f'fill="none" stroke="currentColor" stroke-width="1.5"/>'
        )
        parts.append(
            f'<rect x="{_svg.fmt(ox)}" y="{_svg.fmt(o_top)}" '
            f'width="{_svg.fmt(bar_w)}" height="{_svg.fmt(h - mb - o_top)}" '
            f'fill="currentColor" opacity="0.55"/>'
        )
        parts.append(
            _text(tx + bar_w / 2.0, t_top - 6.0, f"{theory[i]:.3f}", size=9.5)
        )
        parts.append(_text(cx, h - mb + 18.0, str(i + 1), size=11.0))

    parts.append(_text((ml + w - mr) / 2.0, h - 14, "partial quotient k", size=12.0))
    ylx, yly = 20.0, (mt + h - mb) / 2.0
    parts.append(
        _text(
            ylx,
            yly,
            "frequency",
            size=12.0,
            extra=f'transform="rotate(-90 {_svg.fmt(ylx)} {_svg.fmt(yly)})"',
        )
    )

    lx, ly = w - mr - 320.0, mt + 14.0
    parts.append(
        f'<rect x="{_svg.fmt(lx)}" y="{_svg.fmt(ly - 9)}" width="14" height="14" '
        f'fill="none" stroke="currentColor" stroke-width="1.5"/>'
    )
    parts.append(_text(lx + 22.0, ly + 3.0, "Gauss-Kuzmin law", size=11.0, anchor="start"))
    parts.append(
        f'<rect x="{_svg.fmt(lx)}" y="{_svg.fmt(ly + 13)}" width="14" height="14" '
        f'fill="currentColor" opacity="0.55"/>'
    )
    parts.append(
        _text(
            lx + 22.0,
            ly + 25.0,
            f"orbit of pi's 240-term convergent ({total} digits)",
            size=11.0,
            anchor="start",
        )
    )

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Gauss-Kuzmin distribution: theory vs a deterministic orbit",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  8. Koch and Sierpinski arrowhead, side by side (Stop 13).
# --------------------------------------------------------------------------- #

def fig_koch_sierpinski() -> str:
    """The Koch curve (depth 4) and the Sierpinski arrowhead (depth 6), paneled.

    Both curves are generated by the existing turtle renderers and rescaled
    into one document: equal-width panels, each vertically centered, with a
    caption line under each.

    >>> svg = fig_koch_sierpinski()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    panels = [
        ("Koch curve (depth 4)", koch(4)),
        ("Sierpinski arrowhead (depth 6)", sierpinski_arrowhead(6)),
    ]
    panel_w, gap, margin = 350.0, 40.0, 10.0

    placed: list[tuple[str, float, float, float, tuple[float, float, float, float], str]] = []
    heights: list[float] = []
    for label, doc in panels:
        vb, body = _svg_parts(doc)
        s = panel_w / vb[2]
        heights.append(vb[3] * s)
        placed.append((label, s, 0.0, 0.0, vb, body))
    panel_h = max(heights)

    parts: list[str] = []
    for i, (label, s, _tx, _ty, vb, body) in enumerate(placed):
        tx = margin + i * (panel_w + gap)
        ty = (panel_h - vb[3] * s) / 2.0
        a = tx - s * vb[0]
        b = ty - s * vb[1]
        parts.append(
            f'<g transform="translate({_svg.fmt(a)} {_svg.fmt(b)}) '
            f'scale({_svg.fmt(s)})">{body}</g>'
        )
        parts.append(_text(tx + panel_w / 2.0, panel_h + 24.0, label, size=12.0))

    w = 2.0 * margin + 2.0 * panel_w + gap
    h = panel_h + 36.0
    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Koch curve and Sierpinski arrowhead",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  9. The Heighway dragon (Stop 13).
# --------------------------------------------------------------------------- #

def fig_dragon() -> str:
    """The Heighway dragon at depth 10.

    >>> svg = fig_dragon()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    return _themed(dragon(10))


# --------------------------------------------------------------------------- #
#  10. The Markov tree (Appendix D).
# --------------------------------------------------------------------------- #

def fig_markov_tree() -> str:
    """The tree of Markov triples grown by Vieta jumping from ``(1, 1, 1)``.

    Each triple solves ``x^2 + y^2 + z^2 = 3xyz``; a child replaces one
    member via the Vieta jump ``z -> 3xy - z``. From ``(1, 1, 1)`` the jump
    yields a single new triple twice in a row (the stem), and from
    ``(1, 2, 5)`` onward every triple branches in two. Shown: the stem plus
    the first two branching generations; the big label is the Markov number
    (the triple's maximum), the small one the triple itself.

    >>> svg = fig_markov_tree()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    Triple = tuple[int, int, int]

    def jump_children(t: Triple) -> list[Triple]:
        x, y, z = t
        left: Triple = tuple(sorted((x, z, 3 * x * z - y)))  # type: ignore[assignment]
        right: Triple = tuple(sorted((y, z, 3 * y * z - x)))  # type: ignore[assignment]
        return [left, right]

    # rows[depth] = list of (triple, parent_index_in_previous_row)
    rows: list[list[tuple[Triple, int]]] = [
        [((1, 1, 1), -1)],
        [((1, 1, 2), 0)],
        [((1, 2, 5), 0)],
    ]
    for _ in range(2):
        nxt: list[tuple[Triple, int]] = []
        for i, (t, _p) in enumerate(rows[-1]):
            for c in jump_children(t):
                nxt.append((c, i))
        rows.append(nxt)

    leaf_gap, row_gap = 168.0, 92.0
    xs: list[list[float]] = [[] for _ in rows]
    xs[-1] = [i * leaf_gap for i in range(len(rows[-1]))]
    for depth in range(len(rows) - 2, -1, -1):
        for i in range(len(rows[depth])):
            child_xs = [
                xs[depth + 1][j]
                for j, (_t, p) in enumerate(rows[depth + 1])
                if p == i
            ]
            xs[depth].append(sum(child_xs) / len(child_xs))

    parts: list[str] = []
    for depth in range(1, len(rows)):
        for j, (_t, p) in enumerate(rows[depth]):
            x1, y1 = xs[depth - 1][p], (depth - 1) * row_gap
            x2, y2 = xs[depth][j], depth * row_gap
            parts.append(_line(x1, y1 + 24.0, x2, y2 - 14.0, width=1.2))
    for depth, row in enumerate(rows):
        for j, (t, _p) in enumerate(row):
            x, y = xs[depth][j], depth * row_gap
            parts.append(_text(x, y + 4.0, str(t[2]), size=14.0))
            parts.append(_text(x, y + 19.0, f"({t[0]},{t[1]},{t[2]})", size=9.0))

    minx = min(x for row in xs for x in row) - 60.0
    maxx = max(x for row in xs for x in row) + 60.0
    miny = -18.0
    maxy = (len(rows) - 1) * row_gap + 28.0
    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.padded_viewbox(minx, miny, maxx, maxy),
        title="The Markov tree grown by Vieta jumping",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  11. The Hofstadter butterfly (Appendix F).
# --------------------------------------------------------------------------- #

def fig_butterfly() -> str:
    """The Hofstadter butterfly with flux denominators up to 20.

    ``qmax`` is pinned at 20: about 75 KB of SVG and a second of compute,
    the agreed ceiling for an inlined asset.

    >>> svg = fig_butterfly()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    return _themed(butterfly_svg(20, stroke="currentColor"))


# --------------------------------------------------------------------------- #
#  12. The devil's staircase (Appendix E).
# --------------------------------------------------------------------------- #

def fig_staircase() -> str:
    """The devil's staircase of the standard circle map at ``K = 1``.

    >>> svg = fig_staircase()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    return _themed(staircase_svg(1.0, samples=400))


# --------------------------------------------------------------------------- #
#  13. Conway's topograph: the river of x^2 - 7 y^2 (Appendix D, stop E8).
# --------------------------------------------------------------------------- #

def fig_topograph() -> str:
    """Conway's topograph: the river of ``x^2 - 7 y^2``.

    The river is the periodic path with positive form-values on one bank and
    negative on the other; one period, tiled twice, carries the partial
    quotients ``[1, 1, 1, 4]`` of ``sqrt(7)`` (Stop 6), and the ``Q = 1`` well
    is the Pell solution (Stop 7).

    >>> svg = fig_topograph()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    from ..numbertheory.topograph import topograph_data

    data = topograph_data(7)
    river = data["river"] * 2  # tile two periods so the repeat reads as a river
    n = len(river)

    w, h = 760.0, 300.0
    ml, mr = 44.0, 44.0
    y_river = 158.0
    y_above, y_below = 96.0, 224.0
    span = (w - ml - mr) / n

    def bx(i: float) -> float:
        return ml + i * span

    parts: list[str] = []
    parts.append(_text(w / 2.0, 26.0, "The river of x^2 - 7 y^2", size=14.0))
    parts.append(_text(w / 2.0, 44.0, "positive country above, negative below", size=11.0))

    # The river itself: a gentle zigzag through the cell boundaries.
    pts = []
    for j in range(n + 1):
        dy = -5.0 if j % 2 == 0 else 5.0
        pts.append((bx(j), y_river + dy))
    river_path = " ".join(f"{_svg.fmt(x)},{_svg.fmt(y)}" for x, y in pts)
    parts.append(
        f'<polyline points="{river_path}" fill="none" stroke="currentColor" '
        f'stroke-width="2.4"/>'
    )

    for i, cell in enumerate(river):
        cx = bx(i + 0.5)
        # region values above and below the river
        parts.append(_text(cx, y_above, f"+{cell['above']}", size=15.0))
        parts.append(_text(cx, y_below, f"{cell['below']}", size=15.0))
        # the partial quotient labelling this river edge
        parts.append(_text(cx, y_river - 12.0, f"a={cell['a']}", size=11.0))
        # thin edges from the river up into the positive bank and down into the negative
        nx = bx(i)
        parts.append(_line(nx, y_river, cx, y_above + 6.0, width=0.8,
                           extra='opacity="0.5"'))
        parts.append(_line(nx, y_river, cx, y_below - 6.0, width=0.8,
                           extra='opacity="0.5"'))
        # a node where edges meet the river
        parts.append(
            f'<circle cx="{_svg.fmt(nx)}" cy="{_svg.fmt(y_river - 5.0 if i % 2 == 0 else y_river + 5.0)}" '
            f'r="2.6" fill="currentColor"/>'
        )

    # the "one period" bracket over the first four cells
    x0, x1 = bx(0), bx(4)
    ybk = 262.0
    parts.append(_line(x0, ybk, x1, ybk, width=1.2))
    parts.append(_line(x0, ybk, x0, ybk - 6, width=1.2))
    parts.append(_line(x1, ybk, x1, ybk - 6, width=1.2))
    parts.append(_text((x0 + x1) / 2.0, ybk + 16.0, "one period = Pell solved", size=11.0))

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Conway topograph river of x^2 - 7 y^2",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  14. Greedy Egyptian denominator growth (Appendix I, stop B3).
# --------------------------------------------------------------------------- #

def fig_egyptian_growth() -> str:
    """Semi-log growth of greedy Egyptian-fraction denominators.

    Sylvester's expansion of ``1`` (2, 3, 7, 43, ...) and the greedy expansion
    of ``5/121`` both double their digit-count at every step -- a denominator
    explosion no continued fraction ever commits.

    >>> svg = fig_egyptian_growth()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    from ..expansions.egyptian import fibonacci_sylvester, sylvester_sequence

    series = [
        ("Sylvester's 1", sylvester_sequence(6)),
        ("greedy 5/121", fibonacci_sylvester(Fraction(5, 121))),
    ]
    ymax = 26.0  # log10 ceiling (5/121's last denominator has 25 digits)
    xmax = 6

    w, h = 720.0, 400.0
    ml, mr, mt, mb = 66.0, 130.0, 46.0, 52.0

    def sx(k: float) -> float:
        return ml + (k - 1.0) / (xmax - 1.0) * (w - ml - mr)

    def sy(v: float) -> float:
        return h - mb - v / ymax * (h - mt - mb)

    parts: list[str] = []
    parts.append(_text((ml + w - mr) / 2.0, 24.0,
                       "Greedy's bill: log-scale denominators", size=14.0))
    parts.append(_line(ml, mt, ml, h - mb, width=1.2))
    parts.append(_line(ml, h - mb, w - mr, h - mb, width=1.2))
    for v in range(0, 25, 6):
        parts.append(_line(ml - 5, sy(v), ml, sy(v), width=1.0))
        label = "1" if v == 0 else f"10^{v}"
        parts.append(_text(ml - 9, sy(v) + 4, label, size=10.0, anchor="end"))
    for k in range(1, xmax + 1):
        parts.append(_line(sx(k), h - mb, sx(k), h - mb + 5, width=1.0))
        parts.append(_text(sx(k), h - mb + 20, str(k), size=11.0))
    parts.append(_text((ml + w - mr) / 2.0, h - 14.0, "term index", size=12.0))
    ylx, yly = 22.0, (mt + h - mb) / 2.0
    parts.append(_text(ylx, yly, "denominator", size=12.0,
                       extra=f'transform="rotate(-90 {_svg.fmt(ylx)} {_svg.fmt(yly)})"'))

    dashes = ("", ' stroke-dasharray="5 4"')
    label_y = (sy(6.5), sy(24.0))
    for si, (name, denoms) in enumerate(series):
        pts = []
        for k, d in enumerate(denoms, start=1):
            v = math.log10(d)
            pts.append((sx(k), sy(v)))
        path = " ".join(f"{_svg.fmt(x)},{_svg.fmt(y)}" for x, y in pts)
        parts.append(
            f'<polyline points="{path}" fill="none" stroke="currentColor" '
            f'stroke-width="1.8"{dashes[si]}/>'
        )
        for x, y in pts:
            parts.append(f'<circle cx="{_svg.fmt(x)}" cy="{_svg.fmt(y)}" r="3.2" '
                         f'fill="currentColor"/>')
        lx = pts[-1][0] + 8.0
        parts.append(_text(lx, label_y[si], name, size=11.0, anchor="start"))

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Greedy Egyptian-fraction denominator growth (semi-log)",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  15. Zeckendorf bitmap (Appendix I, stop B4).
# --------------------------------------------------------------------------- #

def fig_zeckendorf() -> str:
    """Twelve integers written in Fibonacci binary (Zeckendorf).

    Each row is ``n`` as a sum of non-consecutive Fibonacci numbers; a filled
    square marks a used Fibonacci number. No two filled squares ever touch --
    the non-consecutive rule made visible.

    >>> svg = fig_zeckendorf()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    from ..expansions.zeckendorf import zeckendorf

    cols = [1, 2, 3, 5, 8, 13]  # F_2 .. F_7
    rows = list(range(1, 13))
    cell = 30.0
    ml, mt = 92.0, 58.0
    right_pad = 150.0
    w = ml + len(cols) * cell + right_pad
    h = mt + len(rows) * cell + 24.0

    parts: list[str] = []
    parts.append(_text(w / 2.0, 26.0, "Twelve integers in Fibonacci binary", size=14.0))
    # column headers
    for j, f in enumerate(cols):
        cx = ml + (j + 0.5) * cell
        parts.append(_text(cx, mt - 10.0, str(f), size=12.0))
    parts.append(_text(ml - 10.0, mt - 10.0, "n", size=12.0, anchor="end"))

    for i, n in enumerate(rows):
        used = set(zeckendorf(n))
        cy = mt + i * cell
        parts.append(_text(ml - 10.0, cy + cell * 0.62, str(n), size=12.0, anchor="end"))
        for j, f in enumerate(cols):
            x = ml + j * cell
            if f in used:
                parts.append(
                    f'<rect x="{_svg.fmt(x + 3)}" y="{_svg.fmt(cy + 3)}" '
                    f'width="{_svg.fmt(cell - 6)}" height="{_svg.fmt(cell - 6)}" '
                    f'fill="currentColor"/>'
                )
            else:
                parts.append(
                    f'<rect x="{_svg.fmt(x + 3)}" y="{_svg.fmt(cy + 3)}" '
                    f'width="{_svg.fmt(cell - 6)}" height="{_svg.fmt(cell - 6)}" '
                    f'fill="none" stroke="currentColor" stroke-width="0.8" '
                    f'opacity="0.4"/>'
                )
        summ = " + ".join(str(s) for s in zeckendorf(n))
        parts.append(_text(ml + len(cols) * cell + 8.0, cy + cell * 0.62,
                           f"= {summ}", size=11.0, anchor="start"))

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Zeckendorf representations of 1..12 as Fibonacci bits",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  16. Cutting sequence: the golden slope and the Fibonacci word (App. I, B5).
# --------------------------------------------------------------------------- #

def fig_cutting_sequence() -> str:
    """A line of golden slope cuts the integer grid into the Fibonacci word.

    The segment of slope ``1/phi`` from the origin crosses vertical grid lines
    (filled dots, letter ``a``) and horizontal ones (hollow dots, letter
    ``b``); read in order the crossings spell out the Fibonacci word, the
    canonical Sturmian sequence.

    >>> svg = fig_cutting_sequence()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    cols, rowsN = 13, 8
    unit = 44.0
    ml, mt = 40.0, 46.0
    w = ml + cols * unit + 20.0
    h = mt + rowsN * unit + 60.0
    slope = 2.0 / (1.0 + 5.0 ** 0.5)  # 1/phi

    def gx(x: float) -> float:
        return ml + x * unit

    def gy(y: float) -> float:
        return mt + (rowsN - y) * unit

    parts: list[str] = []
    parts.append(_text(w / 2.0, 26.0, "A golden-slope line cuts the grid", size=14.0))
    # grid
    for i in range(cols + 1):
        parts.append(_line(gx(i), gy(0), gx(i), gy(rowsN), width=0.6,
                           extra='opacity="0.35"'))
    for j in range(rowsN + 1):
        parts.append(_line(gx(0), gy(j), gx(cols), gy(j), width=0.6,
                           extra='opacity="0.35"'))

    # the golden ray
    x_end = float(cols)
    y_end = slope * x_end
    parts.append(_line(gx(0), gy(0), gx(x_end), gy(y_end), width=2.2))

    # crossings in order: gather (t, kind, letter)
    crossings = []
    for k in range(1, cols + 1):
        crossings.append((k, "a", gx(k), gy(slope * k)))          # vertical line x=k
    for m_ in range(1, rowsN + 1):
        t = m_ / slope
        if t <= x_end:
            crossings.append((t, "b", gx(t), gy(m_)))             # horizontal line y=m
    crossings.sort(key=lambda c: c[0])

    letters = []
    for _t, kind, px, py in crossings:
        if kind == "a":
            parts.append(f'<circle cx="{_svg.fmt(px)}" cy="{_svg.fmt(py)}" r="4" '
                         f'fill="currentColor"/>')
        else:
            parts.append(f'<circle cx="{_svg.fmt(px)}" cy="{_svg.fmt(py)}" r="4" '
                         f'fill="none" stroke="currentColor" stroke-width="1.4"/>')
        letters.append(kind)

    word = " ".join(letters)
    parts.append(_text(w / 2.0, h - 30.0,
                       "crossings, in order:", size=11.0))
    parts.append(_text(w / 2.0, h - 12.0, word, size=13.0))

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Golden-slope cutting sequence and the Fibonacci word",
    )
    return _themed(doc)


# --------------------------------------------------------------------------- #
#  17. Rogers-Ramanujan convergents racing to the golden value (Appendix D, E9).
# --------------------------------------------------------------------------- #

def fig_rogers_ramanujan() -> str:
    """Convergents of the Rogers-Ramanujan fraction bracketing their limit.

    The ``q``-continued fraction ``R(q)`` at ``q = 1/2`` (chosen so the
    approach is visible): successive convergents fall alternately above and
    below the limit, the bracket property every continued fraction has. The
    caption records the miracle at a different ``q``: at ``q = e^{-2 pi}`` the
    limit is Ramanujan's golden surd ``sqrt((5 + sqrt 5)/2) - phi``.

    >>> svg = fig_rogers_ramanujan()
    >>> svg.startswith('<svg')
    True
    >>> import xml.dom.minidom as m
    >>> m.parseString(svg).documentElement.tagName
    'svg'
    """
    q = 0.5
    prefactor = q ** 0.2
    n_max = 8
    vals = []
    for n in range(1, n_max + 1):
        t = 1.0
        for k in range(n, 0, -1):
            t = 1.0 + q ** k / t
        vals.append(prefactor / t)
    limit = vals[-1]

    w, h = 720.0, 380.0
    ml, mr, mt, mb = 74.0, 26.0, 50.0, 52.0
    lo, hi = 0.572, 0.628

    def sx(n: float) -> float:
        return ml + (n - 1.0) / (n_max - 1.0) * (w - ml - mr)

    def sy(v: float) -> float:
        return h - mb - (v - lo) / (hi - lo) * (h - mt - mb)

    parts: list[str] = []
    parts.append(_text((ml + w - mr) / 2.0, 24.0,
                       "Rogers-Ramanujan convergents bracket their limit (q = 1/2)",
                       size=14.0))
    parts.append(_line(ml, mt, ml, h - mb, width=1.2))
    parts.append(_line(ml, h - mb, w - mr, h - mb, width=1.2))
    for i in range(5):
        v = lo + (hi - lo) * i / 4.0
        parts.append(_line(ml - 5, sy(v), ml, sy(v), width=1.0))
        parts.append(_text(ml - 9, sy(v) + 4, f"{v:.3f}", size=10.0, anchor="end"))
    for n in range(1, n_max + 1):
        parts.append(_line(sx(n), h - mb, sx(n), h - mb + 5, width=1.0))
        parts.append(_text(sx(n), h - mb + 20, str(n), size=10.0))
    parts.append(_text((ml + w - mr) / 2.0, h - 14.0, "convergent index n", size=12.0))

    # the limit, dashed
    gy = sy(limit)
    parts.append(_line(ml, gy, w - mr, gy, width=1.4, extra='stroke-dasharray="6 4"'))
    parts.append(_text(w - mr - 4, gy - 8, f"limit = {limit:.5f}", size=11.0, anchor="end"))

    pts = [(sx(n), sy(vals[n - 1])) for n in range(1, n_max + 1)]
    path = " ".join(f"{_svg.fmt(x)},{_svg.fmt(y)}" for x, y in pts)
    parts.append(f'<polyline points="{path}" fill="none" stroke="currentColor" '
                 f'stroke-width="1.6" opacity="0.7"/>')
    for x, y in pts:
        parts.append(f'<circle cx="{_svg.fmt(x)}" cy="{_svg.fmt(y)}" r="3.6" '
                     f'fill="currentColor"/>')

    doc = _svg.document(
        "".join(parts),
        viewbox_str=_svg.viewbox(0, 0, w, h),
        title="Rogers-Ramanujan continued-fraction convergents bracketing their limit",
    )
    return _themed(doc)


FIGURES: dict[str, Callable[[], str]] = {
    "fig-calltree.svg": fig_calltree,
    "fig-convergent-error.svg": fig_convergent_error,
    "fig-phyllotaxis.svg": fig_phyllotaxis,
    "fig-period-wheel.svg": fig_period_wheel,
    "fig-stern-brocot.svg": fig_stern_brocot,
    "fig-ford-circles.svg": fig_ford_circles,
    "fig-gauss-kuzmin.svg": fig_gauss_kuzmin,
    "fig-koch-sierpinski.svg": fig_koch_sierpinski,
    "fig-dragon.svg": fig_dragon,
    "fig-markov-tree.svg": fig_markov_tree,
    "fig-butterfly.svg": fig_butterfly,
    "fig-staircase.svg": fig_staircase,
    "fig-topograph.svg": fig_topograph,
    "fig-egyptian-growth.svg": fig_egyptian_growth,
    "fig-zeckendorf.svg": fig_zeckendorf,
    "fig-cutting-sequence.svg": fig_cutting_sequence,
    "fig-rogers-ramanujan.svg": fig_rogers_ramanujan,
}
