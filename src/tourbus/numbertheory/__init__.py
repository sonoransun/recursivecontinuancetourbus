"""Number theory that falls out of continued fractions.

Four classical structures, each built directly on the :mod:`tourbus.cf`
nucleus and each exact to the last bit:

* :mod:`~tourbus.numbertheory.pell` -- Pell's equation ``x^2 - d*y^2 = +-1``,
  solved from the periodic continued fraction of ``sqrt(d)``.
* :mod:`~tourbus.numbertheory.chakravala` -- Bhaskara II's cyclic method, the
  medieval Indian route to the same fundamental solution in exact integers.
* :mod:`~tourbus.numbertheory.stern_brocot` -- the Stern-Brocot tree, Farey
  sequences, and Stern's diatomic (``fusc``) / Calkin-Wilf enumeration of the
  positive rationals.
* :mod:`~tourbus.numbertheory.minkowski` -- Minkowski's question-mark function
  and its inverse, the conjugacy between the continued-fraction and binary
  encodings of a real.
* :mod:`~tourbus.numbertheory.liouville` -- Liouville numbers and the
  irrationality-measure view of transcendence.
* :mod:`~tourbus.numbertheory.topograph` -- Conway's topograph: the river of a
  binary quadratic form, and its identity with the continued fraction of
  ``sqrt(d)``.
"""

from __future__ import annotations

from .chakravala import ChakravalaStep, chakravala, chakravala_steps
from .liouville import (
    liouville_truncation,
    liouville_cf_terms,
    irrationality_measure_witness,
)
from .topograph import (
    form_value,
    river_cells,
    river_period,
    pell_from_river,
)
from .minkowski import (
    question_mark,
    question_mark_inverse,
    question_mark_of_quadratic,
)
from .pell import PellSolution, fundamental_solution, solutions
from .stern_brocot import (
    calkin_wilf,
    farey,
    farey_length,
    fusc,
    mediant,
    path_to_rational,
    rational_to_path,
    stern_brocot_bfs,
)

__all__ = [
    "PellSolution",
    "fundamental_solution",
    "solutions",
    "ChakravalaStep",
    "chakravala",
    "chakravala_steps",
    "rational_to_path",
    "path_to_rational",
    "mediant",
    "farey",
    "farey_length",
    "fusc",
    "calkin_wilf",
    "stern_brocot_bfs",
    "question_mark",
    "question_mark_inverse",
    "question_mark_of_quadratic",
    # liouville
    "liouville_truncation",
    "liouville_cf_terms",
    "irrationality_measure_witness",
    # topograph
    "form_value",
    "river_cells",
    "river_period",
    "pell_from_river",
]
