"""Shared type aliases for the tourbus engine.

Keeping these in one place documents the little integer-tuple vocabulary the
continued-fraction algorithms speak: a partial quotient is an ``int``; the
convergent recurrence carries ``(h, k)`` integer pairs; the Gosper engine
carries small integer matrices.
"""

from __future__ import annotations

from typing import Iterator, Sequence, Tuple

#: A single partial quotient a_n of a continued fraction.
Term = int

#: A continued fraction, at its most primitive, is a stream of partial quotients.
TermStream = Iterator[Term]

#: A convergent numerator/denominator pair (h_n, k_n).
PQPair = Tuple[int, int]

#: A 2x2 integer matrix flattened as (a, b, c, d) meaning [[a, b], [c, d]].
Matrix2 = Tuple[int, int, int, int]

#: The eight coefficients of a bihomographic transform
#: (a*xy + b*x + c*y + d) / (e*xy + f*x + g*y + h).
Matrix8 = Tuple[int, int, int, int, int, int, int, int]

#: A finite run of partial quotients (e.g. the preperiod or period of a CF).
Terms = Sequence[Term]
