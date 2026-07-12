from __future__ import annotations

import math
from xml.dom.minidom import parseString

import pytest

from tourbus.fractals import (
    cantor,
    dragon,
    fib_call_tree,
    hilbert,
    koch,
    pascal_mod2,
    sierpinski_arrowhead,
    tree_to_svg,
)


def _generators():
    """(name, svg) for every public generator at a small, cheap depth."""
    yield "koch", koch(3)
    yield "sierpinski_arrowhead", sierpinski_arrowhead(4)
    yield "dragon", dragon(8)
    yield "hilbert", hilbert(4)
    yield "cantor", cantor(5)
    yield "pascal_mod2", pascal_mod2(16)
    yield "tree_to_svg", tree_to_svg(fib_call_tree(5))


ALL = list(_generators())


@pytest.mark.parametrize("name, svg", ALL, ids=[n for n, _ in ALL])
def test_parses_with_single_svg_root(name, svg):
    doc = parseString(svg)
    root = doc.documentElement
    assert root.tagName == "svg"
    assert root.getAttribute("xmlns") == "http://www.w3.org/2000/svg"
    # exactly one top-level <svg> element (documentElement is that element)
    top = [n for n in doc.childNodes if n.nodeType == n.ELEMENT_NODE]
    assert top == [root]


@pytest.mark.parametrize("name, svg", ALL, ids=[n for n, _ in ALL])
def test_viewbox_is_four_finite_floats(name, svg):
    root = parseString(svg).documentElement
    parts = root.getAttribute("viewBox").split()
    assert len(parts) == 4
    values = [float(p) for p in parts]
    assert all(math.isfinite(v) for v in values)
    # width and height must be positive
    assert values[2] > 0 and values[3] > 0
