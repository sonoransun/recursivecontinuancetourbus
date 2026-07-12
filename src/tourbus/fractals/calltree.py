"""Recursion drawn literally: the call tree of naive ``fib``.

The doubly-recursive ``fib(n) = fib(n-1) + fib(n-2)`` is the canonical example of
a recursion that is elegant to write and ruinous to run, because it recomputes
the same subproblems over and over. Drawing its call tree makes the waste
visible — and makes a small miracle visible too: the number of *leaves* (the
base-case calls ``fib(0)`` and ``fib(1)``) of the tree for ``fib(n)`` is the
Fibonacci number ``F(n+1)`` itself. The tree that computes a Fibonacci number is
sized by a Fibonacci number.

:func:`tree_to_svg` lays the tree out with the simplest tidy scheme that reads
well: ``x`` from the left-to-right order of the leaves, ``y`` from the depth.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import _svg

__all__ = ["TreeNode", "fib_call_tree", "tree_to_svg"]

_FIB_MAX = 8


@dataclass
class TreeNode:
    """A node in a recursion tree: a ``label`` and its ordered ``children``."""

    label: str
    children: list["TreeNode"] = field(default_factory=list)


def fib_call_tree(n: int) -> TreeNode:
    """Build the call tree of the naive ``fib(n)``.

    Internal nodes ``fib(k)`` for ``k >= 2`` have children ``fib(k-1)`` and
    ``fib(k-2)``; ``fib(0)`` and ``fib(1)`` are the leaves.

    >>> root = fib_call_tree(3)
    >>> root.label
    'fib(3)'
    >>> [c.label for c in root.children]
    ['fib(2)', 'fib(1)']
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n > _FIB_MAX:
        raise ValueError(f"n {n} exceeds the cap of {_FIB_MAX}")

    def build(k: int) -> TreeNode:
        node = TreeNode(f"fib({k})")
        if k >= 2:
            node.children = [build(k - 1), build(k - 2)]
        return node

    return build(n)


def _layout(root: TreeNode) -> dict[int, tuple[float, int]]:
    """Assign each node an ``(x, depth)`` position keyed by ``id(node)``.

    ``x`` is the running leaf index for leaves and the mean of the children's
    ``x`` for internal nodes; ``depth`` is the distance from the root.
    """
    positions: dict[int, tuple[float, int]] = {}
    leaf = [0]

    def place(node: TreeNode, depth: int) -> float:
        if not node.children:
            x = float(leaf[0])
            leaf[0] += 1
        else:
            xs = [place(c, depth + 1) for c in node.children]
            x = sum(xs) / len(xs)
        positions[id(node)] = (x, depth)
        return x

    place(root, 0)
    return positions


def tree_to_svg(root: TreeNode) -> str:
    """Render a :class:`TreeNode` tree as a labelled node-and-edge diagram.

    Nodes are small circles with a centred label; edges are straight lines,
    trimmed to the circle rim so a label is never crossed by a line. Everything
    uses ``currentColor`` so it adapts to light and dark themes.
    """
    positions = _layout(root)
    x_gap = 62.0
    y_gap = 74.0
    radius = 17.0
    font = 11.0

    def screen(node: TreeNode) -> tuple[float, float]:
        x, depth = positions[id(node)]
        return x * x_gap, depth * y_gap

    # Walk once to collect nodes and edges in a stable, top-down order.
    nodes: list[TreeNode] = []
    edges: list[tuple[TreeNode, TreeNode]] = []
    stack = [root]
    while stack:
        node = stack.pop()
        nodes.append(node)
        for child in node.children:
            edges.append((node, child))
        stack.extend(reversed(node.children))

    edge_parts: list[str] = []
    for parent, child in edges:
        px, py = screen(parent)
        cx, cy = screen(child)
        dx, dy = cx - px, cy - py
        dist = (dx * dx + dy * dy) ** 0.5 or 1.0
        ux, uy = dx / dist, dy / dist
        x1, y1 = px + ux * radius, py + uy * radius
        x2, y2 = cx - ux * radius, cy - uy * radius
        edge_parts.append(
            f'<line x1="{_svg.fmt(x1)}" y1="{_svg.fmt(y1)}" '
            f'x2="{_svg.fmt(x2)}" y2="{_svg.fmt(y2)}" '
            f'stroke="currentColor" stroke-width="1.5"/>'
        )

    node_parts: list[str] = []
    for node in nodes:
        cx, cy = screen(node)
        node_parts.append(
            f'<circle cx="{_svg.fmt(cx)}" cy="{_svg.fmt(cy)}" '
            f'r="{_svg.fmt(radius)}" fill="none" stroke="currentColor" '
            f'stroke-width="1.5"/>'
            f'<text x="{_svg.fmt(cx)}" y="{_svg.fmt(cy)}" '
            f'font-family="monospace" font-size="{_svg.fmt(font)}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'fill="currentColor">{_svg.escape(node.label)}</text>'
        )

    xs = [screen(n)[0] for n in nodes]
    ys = [screen(n)[1] for n in nodes]
    minx, maxx = min(xs) - radius, max(xs) + radius
    miny, maxy = min(ys) - radius, max(ys) + radius
    vb = _svg.padded_viewbox(minx, miny, maxx, maxy)
    return _svg.document(
        "".join(edge_parts) + "".join(node_parts),
        viewbox_str=vb,
        title=f"Call tree of {root.label}",
    )
