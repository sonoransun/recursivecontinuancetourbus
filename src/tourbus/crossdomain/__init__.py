"""Cross-domain currents: the same recurrence across the sciences.

The continuant three-term recurrence that produces every continued-fraction
convergent turns out to be the Huckel secular determinant (chemistry), the Sturm
sequence behind the Hofstadter butterfly (condensed matter), the Cauer ladder
impedance (electrical engineering), and the Pade convergent (analysis). The
golden ratio — the most badly approximable number — links phyllotaxis (biology),
the Fibonacci quasicrystal (materials), and circle-map mode-locking (nonlinear
dynamics). Each connection here is genuinely computed on the same exact engine.

Modules:

* :mod:`~tourbus.crossdomain.huckel` — Huckel pi-MO energies as a continuant.
* :mod:`~tourbus.crossdomain.recursion_method` — Green's functions as continued fractions.
* :mod:`~tourbus.crossdomain.hofstadter` — the Harper spectrum / Hofstadter butterfly.
* :mod:`~tourbus.crossdomain.circle_map` — mode-locking and the devil's staircase.
* :mod:`~tourbus.crossdomain.feigenbaum` — period doubling and universality.
* :mod:`~tourbus.crossdomain.cauer` / :mod:`~tourbus.crossdomain.routh` — ladders and stability.
* :mod:`~tourbus.crossdomain.pade` — Pade resummation.
* :mod:`~tourbus.crossdomain.apery` — Apery's proof that zeta(3) is irrational.
* :mod:`~tourbus.crossdomain.phyllotaxis` — the golden angle in plants.
* :mod:`~tourbus.crossdomain.fibonacci_chain` — the 1-D quasicrystal.
"""

from __future__ import annotations

from . import (  # noqa: F401
    huckel,
    cauer,
    routh,
    pade,
    apery,
    phyllotaxis,
    recursion_method,
    circle_map,
    feigenbaum,
    hofstadter,
    fibonacci_chain,
)

_MODULES = [
    huckel, cauer, routh, pade, apery, phyllotaxis,
    recursion_method, circle_map, feigenbaum, hofstadter, fibonacci_chain,
]

# Re-export each module's public API at the package top level, but never shadow a
# submodule of the same name (e.g. the pade() function vs the pade module — reach
# that one as ``crossdomain.pade.pade``).
_SUBMODULE_NAMES = {m.__name__.rsplit(".", 1)[-1] for m in _MODULES}

__all__: list[str] = []
for _m in _MODULES:
    for _name in getattr(_m, "__all__", []):
        if _name in _SUBMODULE_NAMES:
            continue
        globals()[_name] = getattr(_m, _name)
        __all__.append(_name)
