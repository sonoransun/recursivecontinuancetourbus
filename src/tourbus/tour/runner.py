"""The command-line entry point and the interactive tour loop.

Commands::

    tourbus                     ride the tour from the first stop
    tourbus tour --from N       start (or resume) at stop N
    tourbus stop N              print one stop, non-interactively
    tourbus list                the route map with synopses
    tourbus demo <name> [...]   run a single demonstration
    tourbus demo --list         list the demos
    tourbus --all               print the whole tour as a transcript (CI target)

Global flags: --no-color / --color, --ascii, --width N, --seed N, --fast.
Every prompt has a default, so ``--all`` and piped input never block.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .termio import Console, make_console


def _add_global_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--no-color", action="store_true", help="disable ANSI colour")
    p.add_argument("--color", action="store_true", help="force ANSI colour")
    p.add_argument("--ascii", action="store_true", help="pure-ASCII glyphs")
    p.add_argument("--width", type=int, default=None, help="output width")
    p.add_argument("--seed", type=int, default=0, help="RNG seed (for determinism)")
    p.add_argument("--fast", action="store_true", help="no animation pauses")


def _console_from(args) -> Console:
    color = None
    if getattr(args, "no_color", False):
        color = False
    elif getattr(args, "color", False):
        color = True
    return make_console(
        width=getattr(args, "width", None),
        color=color,
        ascii_only=getattr(args, "ascii", False),
        fast=getattr(args, "fast", False),
        seed=getattr(args, "seed", 0),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tourbus",
        description="The Recursive Continuance Tour Bus: a guided tour of recursion "
                    "and continued fractions.",
    )
    _add_global_flags(parser)
    parser.add_argument("--all", action="store_true",
                        help="print every stop as a non-interactive transcript")
    parser.add_argument("--version", action="store_true", help="print version and exit")

    sub = parser.add_subparsers(dest="command")

    p_tour = sub.add_parser("tour", help="ride the interactive tour")
    _add_global_flags(p_tour)
    p_tour.add_argument("--from", dest="start", type=int, default=1)

    p_stop = sub.add_parser("stop", help="print a single stop")
    _add_global_flags(p_stop)
    p_stop.add_argument("number", type=int)

    p_list = sub.add_parser("list", help="show the route map")
    _add_global_flags(p_list)

    p_frontier = sub.add_parser("frontier", help="ride the Express Line (fringe topics)")
    _add_global_flags(p_frontier)
    p_frontier.add_argument("number", nargs="?", type=int, default=None)

    p_cross = sub.add_parser("crossdomain", help="ride the Cross-Domain Line (the sciences)")
    _add_global_flags(p_cross)
    p_cross.add_argument("number", nargs="?", type=int, default=None)

    p_demo = sub.add_parser("demo", help="run one demonstration")
    _add_global_flags(p_demo)
    p_demo.add_argument("--list", dest="list_demos", action="store_true")
    p_demo.add_argument("name", nargs="?", default=None)
    # REMAINDER captures demo-specific flags like --op / --depth untouched.
    p_demo.add_argument("args", nargs=argparse.REMAINDER)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "version", False):
        from .. import __version__

        print(f"tourbus {__version__}")
        return 0

    console = _console_from(args)

    if args.command == "list":
        return _cmd_list(console)
    if args.command == "stop":
        return _cmd_stop(console, args.number)
    if args.command == "demo":
        return _cmd_demo(console, args)
    if args.command == "frontier":
        return _cmd_frontier(console, args.number)
    if args.command == "crossdomain":
        return _cmd_crossline(console, args.number)
    if args.command == "tour":
        return _cmd_tour(console, start=args.start)
    if getattr(args, "all", False):
        return _cmd_all(console)
    # default: interactive tour
    return _cmd_tour(console, start=1)


# --------------------------------------------------------------------------- #
#  Commands.
# --------------------------------------------------------------------------- #

def _title_banner(console: Console) -> None:
    from .registry import STOPS

    console.rule(console.glyphs.route_link)
    console.emit(" " + console.style("RECURSIVE CONTINUANCE TOUR BUS", "title")
                 + "  " + console.glyphs.bus)
    console.emit(" " + console.style(
        "a guided tour of recursion and continued fractions", "chrome"))
    console.rule(console.glyphs.route_link)
    console.emit()


def _cmd_list(console: Console) -> int:
    from .registry import STOPS

    _title_banner(console)
    console.emit(" " + console.style("Doors closing. First stop: Euclid, 300 BC.", "chrome"))
    console.emit()
    for s in STOPS:
        num = console.style(f"{s.number:>2}", "route_here")
        title = console.style(s.title, "title")
        console.emit(f"  {num}. {title}")
        console.paragraph(s.synopsis, indent="       ")
    console.emit()
    console.emit(" " + console.style(
        "Ride the tour: python -m tourbus     One stop: python -m tourbus stop N",
        "chrome"))
    return 0


def _print_stop(console: Console, stop, total: int) -> None:
    from . import render

    console.emit(render.stop_header(stop.number, total, stop.title, console))
    console.emit()
    console.paragraph(console.style(stop.note, "chrome"))
    console.emit()
    stop.run(console)


def _cmd_stop(console: Console, number: int) -> int:
    from .registry import STOPS, get_stop

    try:
        stop = get_stop(number)
    except KeyError as exc:
        console.emit(console.style(str(exc), "warn"))
        return 1
    _print_stop(console, stop, len(STOPS))
    return 0


def _cmd_all(console: Console) -> int:
    from .registry import STOPS

    _title_banner(console)
    for stop in STOPS:
        _print_stop(console, stop, len(STOPS))
        console.emit()
    console.emit(" " + console.style(
        "End of the line. Thank you for riding.", "success"))
    return 0


def _cmd_tour(console: Console, *, start: int) -> int:
    from .registry import STOPS

    total = len(STOPS)
    interactive = bool(getattr(console.inp, "isatty", lambda: False)()) and \
        bool(getattr(console.out, "isatty", lambda: False)())

    if not interactive:
        # Piped/non-tty: behave like --all so transcripts are complete.
        return _cmd_all(console)

    _title_banner(console)
    console.emit(" " + console.style("Doors closing. First stop: Euclid, 300 BC.", "chrome"))
    console.emit()
    idx = max(0, min(total - 1, start - 1))
    while 0 <= idx < total:
        stop = STOPS[idx]
        _print_stop(console, stop, total)
        console.emit()
        nxt = STOPS[idx + 1].title if idx + 1 < total else "the depot"
        console.emit(" " + console.style(
            f"next stop {console.glyphs.arrow} {nxt}", "chrome"))
        cmd = console.ask(
            "[Enter=go  b=back  m=map  g N=jump  q=off the bus]", "", parse=str
        ).strip().lower()
        if cmd in ("q", "quit", "exit"):
            break
        if cmd in ("b", "back"):
            idx = max(0, idx - 1)
            continue
        if cmd in ("m", "map"):
            _cmd_list(console)
            continue
        if cmd.startswith("g"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].isdigit():
                idx = max(0, min(total - 1, int(parts[1]) - 1))
                continue
        idx += 1
    console.emit(" " + console.style("Thank you for riding.", "success"))
    return 0


# --------------------------------------------------------------------------- #
#  Demos: thin wrappers exposing individual computations.
# --------------------------------------------------------------------------- #

def _cmd_demo(console: Console, args) -> int:
    from . import demos

    if getattr(args, "list_demos", False) or not args.name:
        demos.list_demos(console)
        return 0
    return demos.run_demo(console, args.name, args.args)


# --------------------------------------------------------------------------- #
#  The Express Line: fringe topics beyond the main route.
# --------------------------------------------------------------------------- #

def _express_header(console: Console, number: int, total: int, title: str) -> None:
    from . import render

    rule = console.style(console.glyphs.h * console.width, "chrome")
    tag = console.style(f"EXPRESS {number} / {total}", "marker")
    console.emit(rule)
    console.emit(" " + console.style(title.upper(), "title") + "   " + tag)
    console.emit(rule)
    console.emit()


def _cmd_frontier(console: Console, number: int | None) -> int:
    from .express import EXPRESS_STOPS

    total = len(EXPRESS_STOPS)
    console.rule(console.glyphs.route_link)
    console.emit(" " + console.style("THE EXPRESS LINE", "title") + "  " + console.glyphs.bus)
    console.emit(" " + console.style(
        "fringe avenues of recursion and continued fractions", "chrome"))
    console.rule(console.glyphs.route_link)
    console.emit()

    if number is not None:
        if not 1 <= number <= total:
            console.emit(console.style(f"no express stop {number} (valid 1..{total})", "warn"))
            return 1
        indices = [number - 1]
    else:
        indices = range(total)

    for i in indices:
        title, note, run = EXPRESS_STOPS[i]
        _express_header(console, i + 1, total, title)
        console.paragraph(console.style(note, "chrome"))
        console.emit()
        run(console)
        console.emit()
    console.emit(" " + console.style("End of the Express Line.", "success"))
    return 0


def _cmd_crossline(console: Console, number: int | None) -> int:
    from .crossline import CROSS_STOPS

    total = len(CROSS_STOPS)
    console.rule(console.glyphs.route_link)
    console.emit(" " + console.style("THE CROSS-DOMAIN LINE", "title") + "  " + console.glyphs.bus)
    console.emit(" " + console.style(
        "the same recurrence, across the sciences", "chrome"))
    console.rule(console.glyphs.route_link)
    console.emit()

    if number is not None:
        if not 1 <= number <= total:
            console.emit(console.style(f"no cross-domain stop {number} (valid 1..{total})", "warn"))
            return 1
        indices = [number - 1]
    else:
        indices = range(total)

    for i in indices:
        title, note, run = CROSS_STOPS[i]
        _express_header(console, i + 1, total, title)
        console.paragraph(console.style(note, "chrome"))
        console.emit()
        run(console)
        console.emit()
    console.emit(" " + console.style("End of the Cross-Domain Line.", "success"))
    return 0
