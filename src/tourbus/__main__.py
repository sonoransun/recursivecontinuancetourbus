"""Console entry point: ``python -m tourbus``.

Delegates to the tour runner, which parses arguments and either walks the
interactive guided tour or executes a single stop / demo.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from .tour.runner import main as run

    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
