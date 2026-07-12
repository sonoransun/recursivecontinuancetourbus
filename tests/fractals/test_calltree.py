from __future__ import annotations

import pytest

from tourbus.fractals import TreeNode, fib_call_tree, tree_to_svg


def _count_leaves(node: TreeNode) -> int:
    if not node.children:
        return 1
    return sum(_count_leaves(c) for c in node.children)


def _fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def test_base_cases_are_single_leaves():
    for n in (0, 1):
        root = fib_call_tree(n)
        assert root.children == []
        assert _count_leaves(root) == 1


def test_structure_of_fib3():
    root = fib_call_tree(3)
    assert root.label == "fib(3)"
    assert [c.label for c in root.children] == ["fib(2)", "fib(1)"]
    assert [c.label for c in root.children[0].children] == ["fib(1)", "fib(0)"]


def test_leaf_count_is_fibonacci():
    # The naive fib(n) call tree has F(n+1) base-case (leaf) calls.
    for n in range(0, 9):
        assert _count_leaves(fib_call_tree(n)) == _fib(n + 1)
    # spelled out for the spec's example:
    assert _count_leaves(fib_call_tree(5)) == 8


def test_depth_cap_and_negative():
    with pytest.raises(ValueError):
        fib_call_tree(9)
    with pytest.raises(ValueError):
        fib_call_tree(-1)


def test_tree_to_svg_is_a_document():
    svg = tree_to_svg(fib_call_tree(5))
    assert svg.startswith("<svg")
    assert "fib(5)" in svg
    assert svg.count("<circle") == _total_nodes(fib_call_tree(5))


def _total_nodes(node: TreeNode) -> int:
    return 1 + sum(_total_nodes(c) for c in node.children)
