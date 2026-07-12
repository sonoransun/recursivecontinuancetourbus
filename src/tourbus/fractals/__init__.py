"""Fractals: recursion you can see.

Where :mod:`tourbus.cf` handles the *arithmetic* of self-reference, this
subpackage handles its *geometry*. Everything here turns a recursive rule into a
self-contained SVG string ready to drop into an HTML page:

* :class:`LSystem` / :func:`expand` — string rewriting, the algebra of a fractal.
* :class:`TurtleConfig`, :func:`commands_to_points`, :func:`points_to_svg` — a
  turtle that reads a rewritten word and draws it.
* :func:`koch`, :func:`sierpinski_arrowhead`, :func:`dragon`, :func:`hilbert`,
  :func:`cantor` — the classic curves and sets, each a complete SVG document.
* :func:`pascal_mod2` — the Sierpiński gasket read straight off the binomial
  coefficients.
* :class:`TreeNode`, :func:`fib_call_tree`, :func:`tree_to_svg` — recursion
  itself, drawn as the call tree of naive ``fib``.

Every generator returns a single well-formed ``<svg xmlns=...>`` root with a
numeric ``viewBox`` and strokes/fills in ``currentColor``, so the figures parse
standalone and follow the page's light/dark theme.
"""

from __future__ import annotations

from .lsystem import LSystem, expand
from .turtle_svg import TurtleConfig, commands_to_points, points_to_svg
from .curves import koch, sierpinski_arrowhead, dragon, hilbert, cantor
from .pascal import pascal_mod2
from .calltree import TreeNode, fib_call_tree, tree_to_svg

__all__ = [
    "LSystem",
    "expand",
    "TurtleConfig",
    "commands_to_points",
    "points_to_svg",
    "koch",
    "sierpinski_arrowhead",
    "dragon",
    "hilbert",
    "cantor",
    "pascal_mod2",
    "TreeNode",
    "fib_call_tree",
    "tree_to_svg",
]
