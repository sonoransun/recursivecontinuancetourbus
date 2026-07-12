"""The guided tour: the interactive command-line experience.

``python -m tourbus`` boards the bus. The tour is a sequence of numbered
*stops*, each a short chapter that mixes narrative, live-computed
demonstrations, and "try this" prompts. The heavy mathematics lives in the
other subpackages; :mod:`tourbus.tour` is the conductor.
"""

from __future__ import annotations

__all__ = ["main"]


def main(argv=None) -> int:
    from .runner import main as _main

    return _main(argv)
