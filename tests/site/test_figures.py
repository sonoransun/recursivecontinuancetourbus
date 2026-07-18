"""Contract tests for the figures registry: determinism plus theming.

Every figure in ``tourbus.figures.FIGURES`` is a zero-argument function
returning a complete SVG document destined to be inlined several to a page,
so each one must be byte-deterministic, well-formed, themed via the root
``color`` attribute + ``currentColor``, and free of ``<style>`` tags, ``id``
attributes, and external references.
"""

from __future__ import annotations

import re
import xml.dom.minidom as minidom

import pytest

from tourbus.figures import FIGURES

EXPECTED_NAMES = [
    "fig-calltree.svg",
    "fig-convergent-error.svg",
    "fig-phyllotaxis.svg",
    "fig-period-wheel.svg",
    "fig-stern-brocot.svg",
    "fig-ford-circles.svg",
    "fig-gauss-kuzmin.svg",
    "fig-koch-sierpinski.svg",
    "fig-dragon.svg",
    "fig-markov-tree.svg",
    "fig-butterfly.svg",
    "fig-staircase.svg",
    "fig-topograph.svg",
    "fig-egyptian-growth.svg",
    "fig-zeckendorf.svg",
    "fig-cutting-sequence.svg",
    "fig-rogers-ramanujan.svg",
]

# A concrete list (never a generator) for parametrize, in registry order.
CASES = list(FIGURES.items())


def test_registry_shape():
    assert list(FIGURES) == EXPECTED_NAMES
    for name, fn in FIGURES.items():
        assert re.fullmatch(r"fig-[a-z0-9-]+\.svg", name)
        assert callable(fn)


@pytest.mark.parametrize("name,fn", CASES, ids=[name for name, _fn in CASES])
def test_figure_contract(name, fn):
    first = fn()
    second = fn()
    # Deterministic: two calls, byte-equal.
    assert first == second

    assert first.startswith("<svg")
    root = minidom.parseString(first).documentElement
    assert root.tagName == "svg"

    # Theming contract: mid-gray root color, currentColor marks, and nothing
    # that could collide when several figures are inlined into one page.
    assert root.getAttribute("color") == "#6e7781"
    assert "currentColor" in first
    assert "<style" not in first
    assert "id=" not in first

    # Self-contained: no URL anywhere but the SVG namespace declaration.
    without_xmlns = first.replace('xmlns="http://www.w3.org/2000/svg"', "", 1)
    assert "http" not in without_xmlns
