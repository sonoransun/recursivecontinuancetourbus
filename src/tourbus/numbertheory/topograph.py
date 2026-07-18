"""Conway's topograph, and the river that *is* the continued fraction of sqrt(d).

John Conway's *The Sensual (Quadratic) Form* (1997) draws a binary quadratic form
``Q(x, y) = a x^2 + b x y + c y^2`` not as an equation but as a *landscape*. Put
the primitive vectors of the integer lattice at the faces of an infinite trivalent
tree (each face a "region", each meeting of three regions a "superbase"), label
every region with its ``Q`` value, and a startling amount of the theory becomes
something you can *see*.

For the indefinite form ``Q(x, y) = x^2 - d y^2`` the picture organizes around one
feature: the **river**, the unique bi-infinite path whose two banks carry values
of opposite sign -- positive regions on one side, negative on the other. Walk the
river and the floors you read off are exactly the partial quotients of
``sqrt(d)``; the river is *periodic*, and its period is the period of the
continued fraction (Stop 6). Where the river touches a region of value ``1`` you
have a **well** -- and a solution of Pell's equation ``x^2 - d y^2 = 1`` (Stop 7).
Step off the river and Conway's **climbing lemma** takes over: values grow, and
keep growing, the farther you go, so the whole tree is a landscape with a single
valley floor -- the river -- and no other local minima.

The arithmetic that runs the whole picture is a single rule. Across any edge, the
two regions ``r`` and ``r'`` on opposite sides relate to the edge's two endpoint
regions ``p, q`` by the arithmetic progression ``r + r' = 2(p + q)``, i.e.
``r' = 2(p + q) - r``. That same "replace one coordinate by a linear function of
the others" move is the Vieta jump of the Markov tree (:mod:`~tourbus.frontier.\
markov`): the topograph and the Markov triples are cousins, and :func:`markov_edge`
makes the family resemblance explicit.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..cf.expand import _floor_quad, cf_from_quadratic
from .pell import fundamental_solution

__all__ = [
    "form_value",
    "RiverCell",
    "river_cells",
    "river_period",
    "river_values",
    "pell_from_river",
    "climbing_lemma_ok",
    "topograph_strip",
    "topograph_data",
    "markov_edge",
]


def form_value(a: int, b: int, c: int, x: int, y: int) -> int:
    """Evaluate the binary quadratic form ``a x^2 + b x y + c y^2`` at ``(x, y)``.

    >>> form_value(1, 0, -2, 3, 2)      # 3^2 - 2*2^2 = 1  (a Pell well)
    1
    >>> form_value(1, 0, -7, 8, 3)      # 8^2 - 7*3^2 = 1
    1
    >>> form_value(1, 1, -1, 1, 0)      # x^2 + xy - y^2 at (1, 0)
    1
    """
    return a * x * x + b * x * y + c * y * y


@dataclass(frozen=True)
class RiverCell:
    """One PQa state ``(P, Q, a)`` visited as the river flows over sqrt(d).

    The complete quotient at this step is ``(P + sqrt(d)) / Q``, whose floor is
    the partial quotient ``a``. ``Q`` is (up to the alternating sign supplied by
    :func:`river_values`) the value ``x^2 - d y^2`` of the region the river is
    passing at this step.

    >>> RiverCell(1, 2, 1)
    RiverCell(P=1, Q=2, a=1)
    """

    P: int
    Q: int
    a: int


def _pqa_states(d: int, count: int) -> list[RiverCell]:
    """The first ``count`` PQa states of sqrt(d), starting from ``(P, Q) = (0, 1)``.

    Mirrors the recurrence inside :func:`~tourbus.cf.expand.cf_from_quadratic`:
    ``a = floor((P + sqrt(d)) / Q)``, then ``P' = a Q - P`` and
    ``Q' = (d - P'^2) / Q``. We borrow that module's exact integer floor
    (``_floor_quad``, private but same package) so no float rounding creeps in.
    """
    states: list[RiverCell] = []
    P, Q = 0, 1
    for _ in range(count):
        a = _floor_quad(P, d, Q)
        states.append(RiverCell(P, Q, a))
        Pn = a * Q - P
        Qn = (d - Pn * Pn) // Q
        P, Q = Pn, Qn
    return states


def river_cells(d: int) -> list[RiverCell]:
    """The PQa states along exactly one period of the river of sqrt(d).

    State 0 is the "shore" ``(0, 1)`` whose floor is ``floor(sqrt(d))`` (the
    pre-period); the returned cells are states ``1 .. L``, the one full period.
    The partial quotients of the returned cells equal :func:`river_period`.

    >>> [(c.P, c.Q, c.a) for c in river_cells(7)]
    [(2, 3, 1), (1, 2, 1), (1, 3, 1), (2, 1, 4)]
    >>> [c.a for c in river_cells(2)]
    [2]
    """
    _, period = cf_from_quadratic(0, d, 1)
    if not period:
        raise ValueError(f"d must be a positive non-square, got {d}")
    L = len(period)
    states = _pqa_states(d, L + 1)
    cells = states[1 : L + 1]
    assert [c.a for c in cells] == period, "PQa period disagrees with cf_from_quadratic"
    return cells


def river_period(d: int) -> list[int]:
    """The period of the continued fraction of sqrt(d) -- the river's period.

    >>> river_period(7)
    [1, 1, 1, 4]
    >>> river_period(2)
    [2]
    >>> river_period(61)
    [1, 4, 3, 1, 2, 2, 1, 3, 4, 1, 14]
    """
    _, period = cf_from_quadratic(0, d, 1)
    if not period:
        raise ValueError(f"d must be a positive non-square, got {d}")
    return period


def river_values(d: int) -> list[int]:
    """The signed form values ``x^2 - d y^2`` flanking one river period.

    The region carrying PQa denominator ``Q_i`` is the value of ``x^2 - d y^2``
    at the ``i``-th convergent, namely ``(-1)^i * Q_i`` -- so along the river the
    values *strictly alternate in sign*, positive bank against negative bank.
    (Empirically grounded: every one of these signed values is a genuine value of
    the form -- see the brute-force cross-check in the tests.)

    >>> river_values(7)
    [-3, 2, -3, 1]
    >>> river_values(2)
    [-1]
    >>> river_values(13)
    [-4, 3, -3, 4, -1]
    """
    cells = river_cells(d)
    # cells[i] carries Q_{i+1}; its convergent has value (-1)^{i+1} Q_{i+1}.
    return [(-1) ** (i + 1) * c.Q for i, c in enumerate(cells)]


def pell_from_river(d: int) -> tuple[int, int]:
    """The fundamental Pell solution ``x^2 - d y^2 = 1`` read off the river.

    A well on the river -- a region of value ``+1``, which is exactly where a
    PQa ``Q`` returns to ``1`` -- is a fundamental solution of Pell's equation.
    We defer to :func:`~tourbus.numbertheory.pell.fundamental_solution` for the
    exact convergent bookkeeping.

    >>> pell_from_river(2)
    (3, 2)
    >>> pell_from_river(7)
    (8, 3)
    >>> pell_from_river(61)
    (1766319049, 226153980)
    """
    sol = fundamental_solution(d, 1)
    if sol is None:
        raise ValueError(f"d must be a positive non-square, got {d}")
    return sol.x, sol.y


def climbing_lemma_ok(d: int, *, steps: int = 6) -> bool:
    """Check Conway's climbing lemma on the value-tree, walking off the river.

    Start from a genuine positive superbase adjacent to the river: with
    ``m = ceil(sqrt(d))`` the vectors ``(m, 1)``, ``(m+1, 1)`` and their negative
    sum give the value triple ``(m^2 - d, (m+1)^2 - d, (2m+1)^2 - 4d)``, all
    positive. Then walk *away* from the river: at each step reflect the smallest
    value ``v`` of the triple to ``2*(sum of the other two) - v`` (the topograph
    edge rule ``r' = 2(p + q) - r``). The lemma says values then only climb; we
    verify the triple's total strictly increases at every step. A demonstrative
    computational check, not a proof.

    >>> climbing_lemma_ok(2)
    True
    >>> climbing_lemma_ok(61)
    True
    >>> all(climbing_lemma_ok(d) for d in (3, 7, 13))
    True
    """
    from math import isqrt

    m = isqrt(d)
    if m * m == d:
        raise ValueError(f"d must be a positive non-square, got {d}")
    m += 1  # ceil(sqrt(d)) for non-square d
    triple = (m * m - d, (m + 1) * (m + 1) - d, (2 * m + 1) * (2 * m + 1) - 4 * d)
    if min(triple) <= 0:  # defensive; construction guarantees positivity
        return False
    total = sum(triple)
    for _ in range(steps):
        lo, mid, hi = sorted(triple)
        triple = (2 * (mid + hi) - lo, mid, hi)
        new_total = sum(triple)
        if new_total <= total:
            return False
        total = new_total
    return True


def topograph_strip(d: int, *, width: int = 72) -> list[str]:
    """A three-row ASCII rendering of one river period, for the CLI stop.

    Row 0 carries the positive-bank region values, row 2 the negative-bank ones,
    and the middle row draws the river as ``o`` nodes joined by its partial
    quotients ``a=...``. Every row is at most ``width`` characters; if a long
    period will not fit, the strip is truncated with a trailing ``...``. The
    output is deterministic and derived entirely from :func:`river_cells` /
    :func:`river_values`.

    >>> strip = topograph_strip(7)
    >>> strip[1]                                # the river: nodes and floors
    'o~a=1~o~a=1~o~a=1~o~a=4~o'
    >>> [row.strip() for row in (strip[0], strip[2])]   # positive / negative banks
    ['+2      +1', '-3      -3']
    >>> all(len(row) <= 72 for row in topograph_strip(166))
    True
    """
    cells = river_cells(d)
    values = river_values(d)
    labels = [f"a={c.a}" for c in cells]
    vstrs = [f"{v:+d}" for v in values]
    col = max((len(s) for s in labels + vstrs), default=1)

    def render(n: int, trailing: bool) -> tuple[str, str, str]:
        top_cells, mid_cells, bot_cells = [], ["o"], []
        for i in range(n):
            top_cells.append((vstrs[i] if values[i] > 0 else "").center(col))
            bot_cells.append((vstrs[i] if values[i] < 0 else "").center(col))
            mid_cells.append(f"~{labels[i]}~".center(col + 2, "~"))
            mid_cells.append("o")
        tail = "..." if trailing else ""
        top = " " + " ".join(top_cells) + (" " + tail if trailing else "")
        bot = " " + " ".join(bot_cells) + (" " + tail if trailing else "")
        mid = "".join(mid_cells) + tail
        return top, mid, bot

    n = len(cells)
    top, mid, bot = render(n, trailing=False)
    while n > 0 and max(len(top), len(mid), len(bot)) > width:
        n -= 1
        top, mid, bot = render(n, trailing=True)
    return [top.rstrip(), mid, bot.rstrip()]


def topograph_data(d: int, *, bank_depth: int = 2) -> dict:
    """A JSON-able description of one river period, for an SVG figure.

    Shape::

        {
          "d": d,
          "period": [a_1, ..., a_L],
          "river": [ {"P", "Q", "a", "above", "below"}, ... ],   # one per cell
          "banks": [ [v1, v2, ...], ... ],                        # one per cell
        }

    Each ``river`` entry is a PQa cell plus the two region values flanking that
    stretch of river (``above`` positive, ``below`` negative -- the cell's own
    signed value paired with its cyclic neighbour's, which by the sign-alternation
    always have opposite sign). Each ``banks`` entry is ``bank_depth`` region
    values marching away from the river, generated by the topograph reflection
    ``2*(p + q) - r`` -- one ring of off-river values the figure can draw as the
    hillside behind each bank.

    >>> data = topograph_data(7)
    >>> data["d"], data["period"]
    (7, [1, 1, 1, 4])
    >>> data["river"][0]
    {'P': 2, 'Q': 3, 'a': 1, 'above': 2, 'below': -3}
    >>> len(data["banks"]) == 4 and all(len(b) == 2 for b in data["banks"])
    True
    """
    if bank_depth < 0:
        raise ValueError(f"bank_depth must be >= 0, got {bank_depth}")
    cells = river_cells(d)
    values = river_values(d)
    L = len(cells)

    river = []
    for i, c in enumerate(cells):
        # The next region along the river has the next cell's magnitude but the
        # opposite sign (the banks strictly alternate). Taking values[(i+1)%L]
        # directly would misread the sign when the period has length 1, where the
        # cyclic neighbour is the region itself.
        this_val = values[i]
        next_val = -(1 if this_val > 0 else -1) * abs(values[(i + 1) % L])
        river.append(
            {
                "P": c.P,
                "Q": c.Q,
                "a": c.a,
                "above": max(this_val, next_val),
                "below": min(this_val, next_val),
            }
        )

    banks = []
    for i in range(L):
        triple = (
            abs(values[i]),
            abs(values[(i + 1) % L]),
            abs(values[(i - 1) % L]),
        )
        ring: list[int] = []
        for _ in range(bank_depth):
            lo, mid, hi = sorted(triple)
            nxt = 2 * (mid + hi) - lo
            ring.append(nxt)
            triple = (nxt, mid, hi)
        banks.append(ring)

    return {"d": d, "period": [c.a for c in cells], "river": river, "banks": banks}


def markov_edge(triple: tuple[int, int, int]) -> list[tuple[int, int, int]]:
    """The three Vieta neighbours of a Markov triple ``(x, y, z)``.

    Replace one coordinate at a time using the second root of the Markov
    quadratic: ``x -> 3 y z - x``, and cyclically for ``y`` and ``z``. This is
    the very same "linear-in-the-others" move as the topograph's
    ``r' = 2(p + q) - r`` -- the Markov tree and Conway's tree are cousins (see
    :func:`~tourbus.frontier.markov.markov_triples`).

    >>> markov_edge((1, 1, 1))
    [(2, 1, 1), (1, 2, 1), (1, 1, 2)]
    >>> markov_edge((1, 2, 5))
    [(29, 2, 5), (1, 13, 5), (1, 2, 1)]
    """
    x, y, z = triple
    return [(3 * y * z - x, y, z), (x, 3 * x * z - y, z), (x, y, 3 * x * y - z)]
