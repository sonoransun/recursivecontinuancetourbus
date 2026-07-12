"""Lindenmayer systems: recursion made visible as a rewriting process.

An L-system is the simplest possible model of recursion. Start with a short
string, the *axiom*, and a table of *rules* that each rewrite one symbol into a
longer word. Apply every rule to every symbol simultaneously, then do it again.
The word grows geometrically, and when a turtle later reads the word as drawing
commands (see :mod:`tourbus.fractals.turtle_svg`) the geometry it traces is a
fractal — the self-similarity of the curve is exactly the self-reference of the
rewrite rule.

The connection to the rest of :mod:`tourbus` is not incidental. The classic
Lindenmayer algae rule ``A -> AB, B -> A`` produces words whose *lengths* are
the Fibonacci numbers, the same sequence whose ratios are the convergents of
the golden ratio's continued fraction ``[1; 1, 1, 1, ...]``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

__all__ = ["LSystem", "expand"]

# A single expansion is capped here so a rule with a large growth factor cannot
# silently allocate gigabytes before anything downstream gets a chance to fail.
MAX_EXPANSION = 2_000_000


@dataclass(frozen=True)
class LSystem:
    """A deterministic, context-free L-system.

    ``rules`` maps a single-character symbol to its replacement word; any symbol
    absent from the table rewrites to itself. ``angle`` is carried along purely
    as metadata for the turtle interpreter (degrees per turn) — it plays no part
    in :func:`expand`.
    """

    axiom: str
    rules: Mapping[str, str]
    angle: float = 90.0


def expand(ls: LSystem, iterations: int) -> str:
    """Rewrite ``ls.axiom`` ``iterations`` times and return the final word.

    Every character is replaced by ``ls.rules[char]`` (or itself when it has no
    rule), simultaneously, once per iteration. The result grows by the rule's
    branching factor each round, so a length guard guards against blow-ups.

    >>> algae = LSystem("A", {"A": "AB", "B": "A"})
    >>> [expand(algae, i) for i in range(5)]
    ['A', 'AB', 'ABA', 'ABAAB', 'ABAABABA']
    >>> [len(expand(algae, i)) for i in range(7)]  # Fibonacci numbers
    [1, 2, 3, 5, 8, 13, 21]
    >>> koch = LSystem("F", {"F": "F+F--F+F"}, angle=60)
    >>> word = expand(koch, 2)
    >>> word.count("F"), len(word)  # 4**2 draw symbols, plus the turn symbols
    (16, 36)
    """
    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    word = ls.axiom
    for _ in range(iterations):
        pieces: list[str] = []
        length = 0
        for ch in word:
            repl = ls.rules.get(ch, ch)
            length += len(repl)
            if length > MAX_EXPANSION:
                raise ValueError(
                    f"expansion would exceed {MAX_EXPANSION} characters; "
                    "reduce the iteration count"
                )
            pieces.append(repl)
        word = "".join(pieces)
    return word
