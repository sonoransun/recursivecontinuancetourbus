"""The route: the ordered registry of the fifteen stops.

Each :class:`Stop` bundles its number, slug, title, a one-line route note, a
short synopsis for the ``list`` command, and a ``run`` callable that prints the
stop's body to a :class:`~tourbus.tour.termio.Console`. Stops are pure with
respect to I/O: they only write to the console they are given, which is what
lets ``--all`` produce a deterministic transcript.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .termio import Console
from . import stops


@dataclass(frozen=True)
class Stop:
    number: int
    slug: str
    title: str
    note: str
    synopsis: str
    run: Callable[[Console], None]


STOPS: list[Stop] = [
    Stop(1, "depot", "The Depot: Boarding",
         "The oldest nontrivial algorithm still in daily use is a two-line recursion.",
         "Euclid's algorithm as the ur-recursion; gcd, Bezout, Lame's theorem.",
         stops.stop_01_depot),
    Stop(2, "unfolding-road", "The Unfolding Road",
         "Run Euclid but keep the quotients, and you have invented continued fractions.",
         "CF expansion = Euclid on reals; rational <-> finite; the notation.",
         stops.stop_02_unfolding),
    Stop(3, "engine-room", "The Engine Room",
         "One two-term recurrence powers everything on this tour.",
         "Convergents, the fundamental recurrence, the determinant identity, error bounds.",
         stops.stop_03_engine),
    Stop(4, "golden", "The Golden Milestone",
         "The number hardest to approximate is the one whose CF is all ones.",
         "phi, Fibonacci, Hurwitz's theorem, the most irrational number.",
         stops.stop_04_golden),
    Stop(5, "scenic-overlook", "Scenic Overlook",
         "The Gregorian calendar, Huygens' gears, and 355/113 are one theorem in three costumes.",
         "Best rational approximation; calendars, gears, pi.",
         stops.stop_05_overlook),
    Stop(6, "loop-road", "The Loop Road",
         "Which numbers make the bus drive in circles? Exactly the roots of quadratics.",
         "Periodic CFs <-> quadratic irrationals; the sqrt(d) algorithm.",
         stops.stop_06_loop),
    Stop(7, "cattle-crossing", "The Cattle Crossing",
         "Archimedes' cattle puzzle has a 206,545-digit answer; the toll is paid in convergents.",
         "Pell's equation via the CF period of sqrt(d).",
         stops.stop_07_pell),
    Stop(8, "family-tree", "The Family Tree",
         "Every fraction has exactly one seat on an infinite binary bus.",
         "Stern-Brocot tree, Farey sequences, mediants, the question-mark function.",
         stops.stop_08_tree),
    Stop(9, "celebrity", "Celebrity Sightings",
         "e queues up in perfect order; pi boards in total chaos, and nobody knows why.",
         "The continued fractions of e and pi; generalized CFs.",
         stops.stop_09_celebrity),
    Stop(10, "casino", "The Casino",
         "Pick a random real. Its continued-fraction digits are loaded dice.",
         "The Gauss map, Gauss-Kuzmin, Khinchin's and Levy's constants.",
         stops.stop_10_casino),
    Stop(11, "assembly-line", "The Infinite Assembly Line",
         "Add sqrt(2) to e without ever computing either.",
         "Gosper's exact continued-fraction stream arithmetic.",
         stops.stop_11_gosper),
    Stop(12, "tower", "The Tower",
         "Visit the recursions that outgrow every tower you can build.",
         "Ackermann, hyperoperations, the Y combinator, McCarthy 91.",
         stops.stop_12_tower),
    Stop(13, "hall-of-mirrors", "The Hall of Mirrors",
         "A periodic continued fraction is a fractal you can hear.",
         "Fractals, self-similarity, and their link to continued fractions.",
         stops.stop_13_fractals),
    Stop(14, "souvenir-shop", "The Souvenir Shop",
         "The same convergents tune your piano and crack lazy RSA keys.",
         "Musical temperament, Wiener's RSA attack, the Collatz conjecture.",
         stops.stop_14_souvenir),
    Stop(15, "terminus", "Terminus: End of the Line",
         "The bus reaches the edge of the map. Here are the roads no one has driven.",
         "Open problems and further reading.",
         stops.stop_15_terminus),
]


def get_stop(number: int) -> Stop:
    for s in STOPS:
        if s.number == number:
            return s
    raise KeyError(f"no stop {number} (valid 1..{len(STOPS)})")
