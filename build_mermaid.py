"""Render a small Mermaid subset to inline SVG at build time.

Supported grammar: ``flowchart TD|LR`` with node declarations ``ID[label]``
(rectangle), ``ID(label)`` (stadium), ``ID{label}`` (diamond), edges
``A --> B`` and ``A -->|label| B``, chains ``A --> B --> C``, ``%%`` comments,
and blank lines; and ``timeline`` with an optional ``title`` line, ``section``
lines, and ``period : event [: event ...]`` entries.  Labels may be wrapped in
double quotes (the quotes are delimiters and are stripped); quoted labels may
contain parentheses, colons, pipes, and equals signs.  Cycles are supported:
back-edges (found by DFS from source nodes in declaration order) are routed
around the left side of the diagram; the remaining forward DAG is layered by
longest path.

Everything outside the subset raises :class:`MermaidError` with a message that
starts ``{src_name}:{line}:`` where ``line`` is ``line_no`` plus the 1-based
offset of the offending line inside ``source`` (callers pass the absolute line
number of the opening fence so errors point into the .md file).

Build tooling only: this module stays out of the ``tourbus`` package and never
imports it.  Output is deterministic (same source, same bytes) and contains no
``id`` attributes, ``<defs>``, or ``<marker>`` elements, so any number of
diagrams can share a page.
"""

from __future__ import annotations

import math
import re
import textwrap

CH = 7.9  # monospace advance per character at font-size 13
NODE_H = 30.0
DIAMOND_H = 42.0
MIN_W = 44.0
LAYER_GAP = 44.0
NODE_GAP = 26.0
PAD = 10.0
ARROW_LEN = 8.0
ARROW_HALF = 3.5
LANE_FIRST = 16.0  # offset of the first back-edge lane left of the content
LANE_STEP = 14.0  # spacing between nested back-edge lanes
BASELINE = 4.5  # vertical nudge that centers 13 px text on a point
LABEL_H = 16.0
TIMELINE_W = 640.0
SPINE_X = 170.0
SURFACE = "var(--surface,#fff)"
BRASS = "var(--brass,#b5751a)"

_ID_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_KEYWORDS = ("subgraph", "end", "style", "classDef", "class", "click",
             "linkStyle", "direction")
_BAD_ARROWS = ("-.-", "==>", "---", "--o", "--x", "<--")
_SHAPES = {"[": ("]", "rect"), "(": (")", "stadium"), "{": ("}", "diamond")}


class MermaidError(ValueError):
    """A mermaid construct outside the supported subset."""


def _fmt(value: float) -> str:
    """Round a coordinate to four decimals, normalizing ``-0`` to ``0``."""
    v = round(float(value), 4)
    if v == 0:
        return "0"
    return f"{v:.4f}".rstrip("0").rstrip(".")


def _esc(text: str) -> str:
    """Escape a string for use in SVG text content or attribute values."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _text(x: float, y: float, content: str, anchor: str = "",
          fill: str = "currentColor", bold: bool = False) -> str:
    a = f' text-anchor="{anchor}"' if anchor else ""
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{_fmt(x)}" y="{_fmt(y)}"{a} fill="{fill}"{b}>'
            f"{_esc(content)}</text>")


# --- parsing ---------------------------------------------------------------- #

class _Parser:
    def __init__(self, source: str, src_name: str, line_no: int):
        self.lines = source.splitlines()
        self.src_name = src_name
        self.line_no = line_no

    def err(self, rel: int, msg: str) -> None:
        raise MermaidError(f"{self.src_name}:{self.line_no + rel}: {msg}")

    def parse(self):
        head_rel = 0
        head = ""
        for rel in range(1, len(self.lines) + 1):
            s = self.lines[rel - 1].strip()
            if s and not s.startswith("%%"):
                head_rel, head = rel, s
                break
        else:
            self.err(len(self.lines) or 1, "empty mermaid block")
        if head.split()[0] == "graph":
            self.err(head_rel, "the 'graph' keyword is not supported; "
                     f"use 'flowchart TD' or 'flowchart LR': {head!r}")
        if head.split()[0] == "flowchart":
            rest = head[len("flowchart"):].strip()
            if rest not in ("TD", "LR"):
                self.err(head_rel, f"unsupported flowchart direction {rest!r}"
                         " (only TD and LR are supported)")
            return self._parse_flowchart(head_rel, rest)
        if head == "timeline":
            return self._parse_timeline(head_rel)
        self.err(head_rel, f"unsupported mermaid diagram: {head!r}")

    def _mask_quotes(self, rel: int, s: str) -> str:
        """Blank out quoted spans so structural scans skip label text."""
        out = []
        inq = False
        for ch in s:
            if ch == '"':
                inq = not inq
                out.append(ch)
            else:
                out.append(" " if inq else ch)
        if inq:
            self.err(rel, f"unterminated quote in: {s!r}")
        return "".join(out)

    def _check_label(self, rel: int, label: str, s: str) -> None:
        if "<" in label or ">" in label:
            self.err(rel, f"HTML is not allowed in labels: {s!r}")
        if "\\n" in label:
            self.err(rel, f"explicit newlines are not allowed in labels: {s!r}")

    def _parse_flowchart(self, head_rel: int, direction: str):
        nodes: dict[str, tuple[str, str]] = {}  # id -> (label, shape)
        explicit: set[str] = set()
        edges: list[tuple[str, str, str]] = []  # (src, dst, label)
        for rel in range(head_rel + 1, len(self.lines) + 1):
            s = self.lines[rel - 1].strip()
            if not s or s.startswith("%%"):
                continue
            for kw in _KEYWORDS:
                if s == kw or s.startswith(kw + " ") or s.startswith(kw + "\t"):
                    self.err(rel, f"unsupported {kw!r} statement: {s!r}")
            masked = self._mask_quotes(rel, s)
            for bad in _BAD_ARROWS:
                if bad in masked:
                    self.err(rel, "unsupported arrow syntax "
                             f"(only '-->' is supported) in: {s!r}")
            if "&" in masked:
                self.err(rel, f"unsupported '&' fan-out in: {s!r}")
            self._parse_chain(rel, s, nodes, explicit, edges)
        if not nodes:
            self.err(head_rel, "flowchart declares no nodes")
        return ("flowchart", head_rel, direction, nodes, edges)

    def _parse_label(self, rel: int, s: str, i: int, closer: str):
        """Parse a (possibly quoted) label ending at ``closer``; return
        (label, index just past the closer)."""
        n = len(s)
        if i < n and s[i] == '"':
            j = s.find('"', i + 1)  # unterminated already caught by the mask
            label = s[i + 1:j]
            i = j + 1
        else:
            j = s.find(closer, i)
            if j < 0:
                self.err(rel, f"unclosed {closer!r} in: {s!r}")
            label = s[i:j]
            hit = sorted(set(label) & set("])}|"))
            if hit:
                self.err(rel, f"unquoted label may not contain {hit}"
                         f" (wrap the label in double quotes): {s!r}")
            i = j
        if i >= n or s[i] != closer:
            self.err(rel, f"expected {closer!r} after quoted label in: {s!r}")
        self._check_label(rel, label, s)
        return label.strip(), i + 1

    def _parse_chain(self, rel: int, s: str, nodes, explicit, edges) -> None:
        n = len(s)
        i = 0
        prev = None
        pending = ""
        while True:
            m = _ID_RE.match(s, i)
            if not m:
                self.err(rel, f"unsupported mermaid syntax: {s!r}")
            nid = m.group(0)
            i = m.end()
            if i < n and s[i] in _SHAPES:
                closer, shape = _SHAPES[s[i]]
                label, i = self._parse_label(rel, s, i + 1, closer)
                if nid in explicit and nodes[nid] != (label, shape):
                    self.err(rel, f"node {nid!r} redeclared with a different "
                             f"label or shape: {s!r}")
                nodes[nid] = (label, shape)
                explicit.add(nid)
            elif nid not in nodes:
                nodes[nid] = (nid, "rect")
            if prev is not None:
                edges.append((prev, nid, pending))
            prev = nid
            while i < n and s[i] in " \t":
                i += 1
            if i == n:
                return
            if not s.startswith("-->", i):
                self.err(rel, f"unsupported mermaid syntax at {s[i:]!r} "
                         f"in: {s!r}")
            i += 3
            while i < n and s[i] in " \t":
                i += 1
            pending = ""
            if i < n and s[i] == "|":
                pending, i = self._parse_label(rel, s, i + 1, "|")
                while i < n and s[i] in " \t":
                    i += 1

    def _parse_timeline(self, head_rel: int):
        title = None
        sections: list[tuple[str, list[tuple[str, list[str]]]]] = []
        for rel in range(head_rel + 1, len(self.lines) + 1):
            s = self.lines[rel - 1].strip()
            if not s or s.startswith("%%"):
                continue
            if s == "title" or s.startswith("title "):
                if sections or title is not None:
                    self.err(rel, f"unexpected 'title' here: {s!r}")
                title = s[len("title"):].strip()
                if not title:
                    self.err(rel, "empty timeline title")
            elif s == "section" or s.startswith("section "):
                name = s[len("section"):].strip()
                if not name:
                    self.err(rel, "empty timeline section name")
                sections.append((name, []))
            else:
                if "<" in s or ">" in s:
                    self.err(rel, f"HTML is not allowed in labels: {s!r}")
                if ":" not in s:
                    self.err(rel, "expected a 'period : event' timeline "
                             f"entry: {s!r}")
                if not sections:
                    self.err(rel, f"timeline entry before any section: {s!r}")
                parts = [p.strip() for p in s.split(":")]
                if not all(parts):
                    self.err(rel, f"empty period or event in: {s!r}")
                sections[-1][1].append((parts[0], parts[1:]))
        if not sections:
            self.err(head_rel, "timeline has no sections")
        for name, entries in sections:
            if not entries:
                self.err(head_rel, f"timeline section {name!r} has no entries")
        return ("timeline", head_rel, title, sections)


# --- flowchart layout ------------------------------------------------------- #

def _node_size(label: str, shape: str) -> tuple[float, float]:
    if shape == "diamond":
        return (max(MIN_W, len(label) * CH * 1.6 + 16), DIAMOND_H)
    return (max(MIN_W, len(label) * CH + 18), NODE_H)


def _border_t(shape: str, wh: tuple[float, float], ux: float, uy: float) -> float:
    """Distance from a shape's center to its border along unit (ux, uy)."""
    w, h = wh
    if shape == "diamond":
        return 1.0 / (abs(ux) / (w / 2) + abs(uy) / (h / 2))
    tx = (w / 2) / abs(ux) if ux else math.inf
    ty = (h / 2) / abs(uy) if uy else math.inf
    return min(tx, ty)


def _classify_back_edges(ids, edges, indeg, adj) -> list[bool]:
    """DFS from declaration-order sources; an edge into a node on the current
    DFS stack is a back-edge."""
    back = [False] * len(edges)
    color = {nid: 0 for nid in ids}  # 0 new, 1 on stack, 2 done
    for root in ids:
        if indeg[root] or color[root]:
            continue
        color[root] = 1
        stack = [(root, 0)]
        while stack:
            u, k = stack[-1]
            if k < len(adj[u]):
                stack[-1] = (u, k + 1)
                ei, v = adj[u][k]
                if color[v] == 1:
                    back[ei] = True
                elif color[v] == 0:
                    color[v] = 1
                    stack.append((v, 0))
            else:
                color[u] = 2
                stack.pop()
    return back


def _layer_and_order(ids, edges, back, err):
    """Longest-path layering of the forward DAG (Kahn order), then two
    barycenter passes; returns (layers, layer, preds-free ordering)."""
    decl = {nid: k for k, nid in enumerate(ids)}
    fadj = {nid: [] for nid in ids}
    fin = {nid: 0 for nid in ids}
    preds = {nid: [] for nid in ids}
    for ei, (a, b, _lab) in enumerate(edges):
        if back[ei]:
            continue
        fadj[a].append(b)
        preds[b].append(a)
        fin[b] += 1
    layer = {nid: 0 for nid in ids}
    placed: set[str] = set()
    count = 0
    while count < len(ids):
        nid = next((n for n in ids if n not in placed and fin[n] == 0), None)
        if nid is None:
            err("flowchart cannot be layered: a cycle survives back-edge "
                "removal (no node has in-degree 0)")
        placed.add(nid)
        count += 1
        for b in fadj[nid]:
            fin[b] -= 1
            layer[b] = max(layer[b], layer[nid] + 1)
    nlayers = max(layer.values()) + 1
    layers: list[list[str]] = [[] for _ in range(nlayers)]
    for nid in ids:
        layers[layer[nid]].append(nid)
    pos = {nid: i for row in layers for i, nid in enumerate(row)}

    def sweep(rng, nbrs):
        for k in rng:
            keyed = sorted(
                ((sum(pos[m] for m in nbrs[nid]) / len(nbrs[nid])
                  if nbrs[nid] else float(pos[nid]), decl[nid], nid)
                 for nid in layers[k]))
            layers[k] = [t[2] for t in keyed]
            for i, nid in enumerate(layers[k]):
                pos[nid] = i

    sweep(range(1, nlayers), preds)  # down pass: predecessor means
    sweep(range(nlayers - 2, -1, -1), fadj)  # up pass: successor means
    return layers, layer


def _render_flowchart(direction, nodes, edges, err) -> str:
    ids = list(nodes)
    adj = {nid: [] for nid in ids}
    indeg = {nid: 0 for nid in ids}
    for ei, (a, b, _lab) in enumerate(edges):
        adj[a].append((ei, b))
        indeg[b] += 1
    back = _classify_back_edges(ids, edges, indeg, adj)
    layers, layer = _layer_and_order(ids, edges, back, err)

    horiz = direction == "LR"
    size = {nid: _node_size(*nodes[nid]) for nid in ids}
    # Major axis runs layer-to-layer (y for TD, x for LR); minor packs a layer.
    majsz = {nid: (size[nid][0] if horiz else size[nid][1]) for nid in ids}
    minsz = {nid: (size[nid][1] if horiz else size[nid][0]) for nid in ids}
    rowh = [max(majsz[nid] for nid in row) for row in layers]
    row0 = []
    acc = 0.0
    for h in rowh:
        row0.append(acc)
        acc += h + LAYER_GAP
    extent = [sum(minsz[n] for n in row) + NODE_GAP * (len(row) - 1)
              for row in layers]
    widest = max(extent)
    mm = {}  # nid -> (major center, minor center)
    for k, row in enumerate(layers):
        m = (widest - extent[k]) / 2
        for nid in row:
            mm[nid] = (row0[k] + rowh[k] / 2, m + minsz[nid] / 2)
            m += minsz[nid] + NODE_GAP

    def xy(maj: float, mn: float) -> tuple[float, float]:
        return (maj, mn) if horiz else (mn, maj)

    ctr = {nid: xy(*mm[nid]) for nid in ids}

    prims: list[tuple] = []
    for ei, (a, b, lab) in enumerate(edges):
        # Adjacent-layer forward edges draw straight; skip-layer edges are
        # routed as orthogonal polylines below so they miss intervening boxes.
        if back[ei] or layer[b] - layer[a] > 1:
            continue
        (ax, ay), (bx, by) = ctr[a], ctr[b]
        dx, dy = bx - ax, by - ay
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux, uy = dx / dist, dy / dist
        t1 = _border_t(nodes[a][1], size[a], ux, uy)
        t2 = _border_t(nodes[b][1], size[b], ux, uy)
        x1, y1 = ax + ux * t1, ay + uy * t1
        tx, ty = bx - ux * t2, by - uy * t2
        bx0, by0 = tx - ux * ARROW_LEN, ty - uy * ARROW_LEN
        px, py = -uy, ux
        prims.append(("line", x1, y1, bx0, by0))
        prims.append(("arrow", (tx, ty),
                      (bx0 + px * ARROW_HALF, by0 + py * ARROW_HALF),
                      (bx0 - px * ARROW_HALF, by0 - py * ARROW_HALF)))
        if lab:
            prims.append(("elabel", (x1 + tx) / 2, (y1 + ty) / 2, lab))

    def fan(group: list[int], ei: int) -> float:
        return (group.index(ei) - (len(group) - 1) / 2) * 8.0

    def nest(group: list[int], ei: int, room: float) -> float:
        """A turn offset in the open interval ``(0, room)``, nested by
        declaration order so sibling legs sharing a corridor never coincide."""
        return room * (group.index(ei) + 1) / (len(group) + 1)

    # Skip edges: forward edges spanning more than one layer. A straight line
    # would cut through the boxes it flies over (and be masked by their opaque
    # fill), so each is routed as an orthogonal polyline down a nested lane on
    # the RIGHT of the content: exit the source's exit border into that layer's
    # gap corridor, run out to the lane, drop down the lane past the skipped
    # rows, run back in through the target's entry gap, and enter its border.
    # (Back-edge return lanes use the left side; keeping the two apart keeps
    # them visually distinct.)  Lanes nest in declaration order; per-gap and
    # per-endpoint fans keep sibling legs off one another deterministically.
    sidx = [ei for ei in range(len(edges))
            if not back[ei] and layer[edges[ei][1]] - layer[edges[ei][0]] > 1]
    sk_exit: dict[int, list[int]] = {}   # source layer -> skip edges (per gap)
    sk_entry: dict[int, list[int]] = {}  # target layer -> skip edges (per gap)
    sk_src: dict[str, list[int]] = {}
    sk_tgt: dict[str, list[int]] = {}
    for ei in sidx:
        a, b, _lab = edges[ei]
        sk_exit.setdefault(layer[a], []).append(ei)
        sk_entry.setdefault(layer[b], []).append(ei)
        sk_src.setdefault(a, []).append(ei)
        sk_tgt.setdefault(b, []).append(ei)

    for j, ei in enumerate(sidx):
        a, b, lab = edges[ei]
        ka, kb = layer[a], layer[b]
        amaj, amin = mm[a]
        bmaj, bmin = mm[b]
        lane = widest + LANE_FIRST + j * LANE_STEP
        # Peel off toward the lane side and merge back from it, so a skip edge
        # never stacks its arrowhead on the adjacent edge that enters the same
        # box head-on at its border centre.
        exit_mn = amin + minsz[a] / 4 + fan(sk_src[a], ei)
        entry_mn = bmin + minsz[b] / 4 + fan(sk_tgt[b], ei)
        # Turn the exit corner high in the source's gap, above the band where
        # that gap's own edge labels sit (labels are opaque and drawn last, so
        # a leg turning through one would be hidden); nest sibling legs so they
        # never overlap (they may still cross, as edges do). Entry corners stay
        # at the gap centre, giving the arrow a clean vertical approach.
        exit_mj = (row0[ka] + rowh[ka]
                   + nest(sk_exit[ka], ei, LAYER_GAP / 2 - LABEL_H / 2))
        entry_mj = row0[kb] - LAYER_GAP / 2 + fan(sk_entry[kb], ei)
        a_exit = amaj + majsz[a] / 2   # source's far (layer-exit) border
        b_entry = bmaj - majsz[b] / 2  # target's near (layer-entry) border
        pts = [(a_exit, exit_mn), (exit_mj, exit_mn), (exit_mj, lane),
               (entry_mj, lane), (entry_mj, entry_mn),
               (b_entry - ARROW_LEN, entry_mn)]
        prims.append(("pline", [xy(*p) for p in pts]))
        prims.append(("arrow", xy(b_entry, entry_mn),
                      xy(b_entry - ARROW_LEN, entry_mn - ARROW_HALF),
                      xy(b_entry - ARROW_LEN, entry_mn + ARROW_HALF)))
        if lab:
            lx, ly = xy((exit_mj + entry_mj) / 2, lane)
            prims.append(("elabel", lx, ly, lab))

    # Back-edges: orthogonal return polylines routed around the left side
    # (TD; the transposed top side for LR), one nested lane per back-edge.
    bidx = [ei for ei in range(len(edges)) if back[ei]]
    by_tgt: dict[str, list[int]] = {}
    by_src: dict[str, list[int]] = {}
    for ei in bidx:
        by_src.setdefault(edges[ei][0], []).append(ei)
        by_tgt.setdefault(edges[ei][1], []).append(ei)

    for j, ei in enumerate(bidx):
        a, b, lab = edges[ei]
        lane = -(LANE_FIRST + j * LANE_STEP)
        amaj, amin = mm[a]
        bmaj, bmin = mm[b]
        entry = bmaj + fan(by_tgt[b], ei)
        border = bmin - minsz[b] / 2
        k = layer[a]
        blocked = any(mm[n][1] < amin for n in layers[k] if n != a)
        if blocked:
            # A sibling sits between the source and the lane: leave through
            # the layer-exit border and duck under the row first (4 segments).
            drop = row0[k] + rowh[k] + LAYER_GAP / 2
            pts = [(amaj + majsz[a] / 2, amin), (drop, amin), (drop, lane),
                   (entry, lane), (entry, border - ARROW_LEN)]
            vseg = (drop, entry)
        else:
            exit_maj = amaj + fan(by_src[a], ei)
            pts = [(exit_maj, amin - minsz[a] / 2), (exit_maj, lane),
                   (entry, lane), (entry, border - ARROW_LEN)]
            vseg = (exit_maj, entry)
        prims.append(("pline", [xy(*p) for p in pts]))
        prims.append(("arrow", xy(entry, border),
                      xy(entry - ARROW_HALF, border - ARROW_LEN),
                      xy(entry + ARROW_HALF, border - ARROW_LEN)))
        if lab:
            lx, ly = xy((vseg[0] + vseg[1]) / 2, lane)
            prims.append(("elabel", lx, ly, lab))

    # Spread edge labels that share a layer gap so their backing rects never
    # cover each other (deterministic: pairs in emission order, equal nudges).
    labels = [i for i, p in enumerate(prims) if p[0] == "elabel"]
    for ii in range(len(labels)):
        for jj in range(ii + 1, len(labels)):
            pi, pj = prims[labels[ii]], prims[labels[jj]]
            wi = len(pi[3]) * CH + 10
            wj = len(pj[3]) * CH + 10
            if horiz:
                if abs(pi[1] - pj[1]) >= (wi + wj) / 2:
                    continue
                sep = LABEL_H + 4.0
                gap = sep - abs(pi[2] - pj[2])
                axis = 2
            else:
                if abs(pi[2] - pj[2]) >= LABEL_H:
                    continue
                sep = (wi + wj) / 2 + 6.0
                gap = sep - abs(pi[1] - pj[1])
                axis = 1
            if gap <= 0:
                continue
            lo, hi = (ii, jj) if pi[axis] <= pj[axis] else (jj, ii)
            for which, d in ((lo, -gap / 2), (hi, gap / 2)):
                p = list(prims[labels[which]])
                p[axis] += d
                prims[labels[which]] = tuple(p)

    for nid in ids:
        label, shape = nodes[nid]
        w, h = size[nid]
        cx, cy = ctr[nid]
        prims.append(("node", shape, cx, cy, w, h))
        prims.append(("ntext", cx, cy + BASELINE, label))

    # Bounding box over every primitive, then shift into positive coordinates.
    minx = miny = math.inf
    maxx = maxy = -math.inf

    def grow(x: float, y: float) -> None:
        nonlocal minx, miny, maxx, maxy
        minx, miny = min(minx, x), min(miny, y)
        maxx, maxy = max(maxx, x), max(maxy, y)

    for p in prims:
        if p[0] == "line":
            grow(p[1], p[2])
            grow(p[3], p[4])
        elif p[0] == "arrow":
            for x, y in p[1:]:
                grow(x, y)
        elif p[0] == "pline":
            for x, y in p[1]:
                grow(x, y)
        elif p[0] == "node":
            _kind, _shape, cx, cy, w, h = p
            grow(cx - w / 2, cy - h / 2)
            grow(cx + w / 2, cy + h / 2)
        elif p[0] == "elabel":
            half = (len(p[3]) * CH + 10) / 2
            grow(p[1] - half, p[2] - LABEL_H / 2)
            grow(p[1] + half, p[2] + LABEL_H / 2)
    sx, sy = PAD - minx, PAD - miny
    width, height = maxx - minx + 2 * PAD, maxy - miny + 2 * PAD

    def pt(x: float, y: float) -> str:
        return f"{_fmt(x + sx)},{_fmt(y + sy)}"

    parts: list[str] = []
    for p in prims:  # edge strokes first, under the node boxes
        if p[0] == "line":
            parts.append(f'<line x1="{_fmt(p[1] + sx)}" y1="{_fmt(p[2] + sy)}"'
                         f' x2="{_fmt(p[3] + sx)}" y2="{_fmt(p[4] + sy)}"'
                         ' stroke="currentColor"/>')
        elif p[0] == "pline":
            pts = " ".join(pt(x, y) for x, y in p[1])
            parts.append(f'<polyline points="{pts}" fill="none"'
                         ' stroke="currentColor"/>')
    for p in prims:
        if p[0] == "arrow":
            pts = " ".join(pt(x, y) for x, y in p[1:])
            parts.append(f'<polygon points="{pts}" fill="currentColor"/>')
    for p in prims:
        if p[0] != "node":
            continue
        _kind, shape, cx, cy, w, h = p
        if shape == "diamond":
            pts = " ".join(pt(*q) for q in ((cx, cy - h / 2), (cx + w / 2, cy),
                                            (cx, cy + h / 2), (cx - w / 2, cy)))
            parts.append(f'<polygon points="{pts}" fill="{SURFACE}"'
                         ' stroke="currentColor"/>')
        else:
            rx = ' rx="15" ry="15"' if shape == "stadium" else ""
            parts.append(f'<rect x="{_fmt(cx - w / 2 + sx)}"'
                         f' y="{_fmt(cy - h / 2 + sy)}" width="{_fmt(w)}"'
                         f' height="{_fmt(h)}"{rx} fill="{SURFACE}"'
                         ' stroke="currentColor"/>')
    for p in prims:
        if p[0] == "ntext":
            parts.append(_text(p[1] + sx, p[2] + sy, p[3], anchor="middle"))
    for p in prims:  # edge labels last, on surface-backed rects
        if p[0] != "elabel":
            continue
        _kind, x, y, lab = p
        w = len(lab) * CH + 10
        parts.append(f'<rect x="{_fmt(x - w / 2 + sx)}"'
                     f' y="{_fmt(y - LABEL_H / 2 + sy)}" width="{_fmt(w)}"'
                     f' height="{_fmt(LABEL_H)}" fill="{SURFACE}"/>')
        parts.append(_text(x + sx, y + BASELINE + sy, lab, anchor="middle"))

    title = nodes[ids[0]][0]
    return _svg(width, height, title, parts)


# --- timeline layout -------------------------------------------------------- #

def _render_timeline(title, sections) -> str:
    parts: list[str] = []
    texts: list[str] = []
    y = 12.0
    if title:
        texts.append(_text(TIMELINE_W / 2, y + 13, title, anchor="middle",
                           bold=True))
        y += 30
    dots: list[float] = []
    for name, entries in sections:
        y += 6
        texts.append(_text(24, y + 13, name.upper(), fill=BRASS, bold=True))
        y += 24
        first = None
        for period, events in entries:
            dots.append(y + 8.5)
            first = dots[-1] if first is None else first
            texts.append(_text(SPINE_X - 12, y + 13, period, anchor="end"))
            ly = y
            for ev in events:
                for line in textwrap.wrap(ev, width=52) or [ev]:
                    texts.append(_text(SPINE_X + 12, ly + 13, line))
                    ly += 18
            y = max(y + 18, ly) + 8
        # One spine segment per section keeps the headings on clear ground.
        parts.append(f'<line x1="{_fmt(SPINE_X)}" y1="{_fmt(first - 6)}"'
                     f' x2="{_fmt(SPINE_X)}" y2="{_fmt(dots[-1] + 6)}"'
                     ' stroke="currentColor" stroke-width="2"/>')
    for d in dots:
        parts.append(f'<circle cx="{_fmt(SPINE_X)}" cy="{_fmt(d)}" r="4"'
                     f' fill="{BRASS}"/>')
    parts.extend(texts)
    return _svg(TIMELINE_W, y + 6, title or sections[0][0], parts)


def _svg(width: float, height: float, title: str, parts: list[str]) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg"'
            f' viewBox="0 0 {_fmt(width)} {_fmt(height)}"'
            f' width="{_fmt(width)}" height="{_fmt(height)}" role="img"'
            f' font-family="var(--font-data,monospace)" font-size="13">'
            f"<title>{_esc(title)}</title>{''.join(parts)}</svg>")


# --- public API ------------------------------------------------------------- #

def render_diagram(source: str, src_name: str = "?", line_no: int = 0) -> str:
    """Render a mermaid ``flowchart TD|LR`` or ``timeline`` block to SVG.

    ``line_no`` is the absolute line number of the line just before the first
    source line (the opening fence), so error messages point into the file.
    """
    parsed = _Parser(source, src_name, line_no).parse()
    if parsed[0] == "flowchart":
        _kind, head_rel, direction, nodes, edges = parsed

        def err(msg: str) -> None:
            raise MermaidError(f"{src_name}:{line_no + head_rel}: {msg}")

        svg = _render_flowchart(direction, nodes, edges, err)
    else:
        _kind, _head_rel, title, sections = parsed
        svg = _render_timeline(title, sections)
    return f'<figure class="diagram" role="figure">{svg}</figure>'
