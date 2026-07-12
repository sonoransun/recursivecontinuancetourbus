"""Pretty-printing helpers for continued fractions and rationals.

The canonical textual form is ``[a0; a1, a2, ...]`` — a semicolon after the
integer part, commas thereafter. Periodic tails are wrapped in parentheses,
e.g. ``[1; (2)]`` for sqrt(2); an optional Unicode overline variant renders the
repeated block with combining overlines for terminals that support it.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Sequence

_OVERLINE = "̅"  # combining overline; renders above the preceding glyph


def cf_to_str(
    terms: Sequence[int],
    *,
    period: Sequence[int] | None = None,
    truncated: bool = False,
    overline: bool = False,
) -> str:
    """Render partial quotients in ``[a0; a1, a2, ...]`` notation.

    ``terms`` are the leading (preperiod) partial quotients. If ``period`` is
    given, it is rendered as a repeated block. ``truncated`` appends an ellipsis
    to signal an infinite/unfinished expansion.

    >>> cf_to_str([4, 2, 6, 7])
    '[4; 2, 6, 7]'
    >>> cf_to_str([3], truncated=True)
    '[3; ...]'
    >>> cf_to_str([1], period=[2])
    '[1; (2)]'
    >>> cf_to_str([], period=[1])
    '[(1)]'
    """
    terms = list(terms)
    if not terms and not period:
        return "[]"

    head = terms[0] if terms else None
    rest = terms[1:] if terms else []

    pieces: list[str] = []
    if head is not None:
        pieces.append(str(head))

    tail_bits = [str(t) for t in rest]

    if period:
        block = ", ".join(str(t) for t in period)
        block = f"({_overline(block) if overline else block})"
        tail_bits.append(block)
    elif truncated:
        tail_bits.append("...")

    if head is None:
        # No integer part supplied (e.g. a pure-period CF with empty preperiod).
        body = ", ".join(tail_bits)
        return f"[{body}]"

    if tail_bits:
        return f"[{pieces[0]}; {', '.join(tail_bits)}]"
    return f"[{pieces[0]}]"


def _overline(text: str) -> str:
    return "".join(ch + _OVERLINE for ch in text)


def fraction_str(x: Fraction | int) -> str:
    """Compact rational rendering: integers stay integers, else ``p/q``.

    >>> fraction_str(Fraction(22, 7))
    '22/7'
    >>> fraction_str(Fraction(6, 3))
    '2'
    """
    f = Fraction(x)
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def join_terms(terms: Iterable[int]) -> str:
    """Join partial quotients as ``a0; a1, a2, ...`` without brackets."""
    terms = list(terms)
    if not terms:
        return ""
    if len(terms) == 1:
        return str(terms[0])
    return f"{terms[0]}; " + ", ".join(str(t) for t in terms[1:])
