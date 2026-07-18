"""The Branch Line: other ways to unfold a number.

The regular continued fraction is one algorithm — floor, subtract, reciprocate.
Change any part of it and a number unfolds differently. This subpackage
collects the alternatives, each exact on the same engine:

* :mod:`~tourbus.expansions.engel` — Engel series, the ascending staircase of
  ceilings; the factorial expansion of ``e``.
* :mod:`~tourbus.expansions.luroth` — Lüroth (independent digits, eventually
  periodic for rationals) and Pierce (alternating) series.
* :mod:`~tourbus.expansions.egyptian` — Fibonacci–Sylvester greedy Egyptian
  fractions, Sylvester's sequence, and the Erdős–Straus conjecture.
* :mod:`~tourbus.expansions.zeckendorf` — non-consecutive Fibonacci sums and
  Bergman's base-φ numeration.
* :mod:`~tourbus.expansions.ostrowski` — Ostrowski numeration against an
  irrational, Beatty sequences, and Sturmian (Fibonacci) words.
* :mod:`~tourbus.expansions.lochs` — Lochs' theorem: the exchange rate between
  decimal digits and continued-fraction terms.
"""

from __future__ import annotations

from .engel import engel_expansion, engel_eval, engel_partial_sums, engel_e_terms
from .luroth import (
    luroth_expansion,
    luroth_eval,
    pierce_expansion,
    pierce_eval,
    pierce_of_reciprocal_phi,
)
from .egyptian import (
    fibonacci_sylvester,
    egyptian_eval,
    sylvester_sequence,
    erdos_straus,
)
from .zeckendorf import (
    zeckendorf,
    zeckendorf_indices,
    from_zeckendorf,
    is_zeckendorf,
    base_phi_digits,
    base_phi_value,
)
from .ostrowski import (
    ostrowski,
    from_ostrowski,
    is_legal_ostrowski,
    beatty,
    characteristic_word,
)
from .lochs import LOCHS_CONSTANT, lochs_constant, lochs_experiment, lochs_ratio

__all__ = [
    "engel_expansion", "engel_eval", "engel_partial_sums", "engel_e_terms",
    "luroth_expansion", "luroth_eval", "pierce_expansion", "pierce_eval",
    "pierce_of_reciprocal_phi",
    "fibonacci_sylvester", "egyptian_eval", "sylvester_sequence", "erdos_straus",
    "zeckendorf", "zeckendorf_indices", "from_zeckendorf", "is_zeckendorf",
    "base_phi_digits", "base_phi_value",
    "ostrowski", "from_ostrowski", "is_legal_ostrowski", "beatty",
    "characteristic_word",
    "LOCHS_CONSTANT", "lochs_constant", "lochs_experiment", "lochs_ratio",
]
