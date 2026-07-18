"""The command-line entry point and the interactive tour loop.

Commands::

    tourbus                     ride the interactive tour (all five lines)
    tourbus tour --from N       board the main route at stop N
    tourbus stop N              print one main-route stop, non-interactively
    tourbus list                the main route map with synopses
    tourbus frontier [N]        the Express Line, whole or one stop
    tourbus crossdomain [N]     the Cross-Domain Line, whole or one stop
    tourbus heritage [N]        the Heritage Line, whole or one stop
    tourbus branch [N]          the Branch Line, whole or one stop
    tourbus demo <name> [...]   run a single demonstration
    tourbus demo --list         list the demos
    tourbus --all               print all five lines as a transcript (CI target)

Global flags, accepted before or after a subcommand: --no-color / --color,
--ascii, --width N, --seed N. Every prompt has a default, so ``--all`` and
piped input never block.
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from typing import Sequence

from .termio import Console, make_console


def _global_flags() -> argparse.ArgumentParser:
    """A parent parser holding the global flags.

    It is shared by the top-level parser and every subparser so the flags work
    before or after the subcommand. Every default is ``SUPPRESS``: a subparser
    only overrides a value the top-level parser already set when the flag
    actually appears after the subcommand. The real defaults are applied once,
    in :func:`_console_from`.
    """
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--no-color", action="store_true", default=argparse.SUPPRESS,
                   help="disable ANSI colour")
    p.add_argument("--color", action="store_true", default=argparse.SUPPRESS,
                   help="force ANSI colour")
    p.add_argument("--ascii", action="store_true", default=argparse.SUPPRESS,
                   help="pure-ASCII glyphs")
    p.add_argument("--width", type=int, default=argparse.SUPPRESS, help="output width")
    p.add_argument("--seed", type=int, default=argparse.SUPPRESS,
                   help="RNG seed (for determinism)")
    return p


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
        seed=getattr(args, "seed", 0),
    )


def build_parser() -> argparse.ArgumentParser:
    common = _global_flags()
    parser = argparse.ArgumentParser(
        prog="tourbus",
        description="The Recursive Continuance Tour Bus: a guided tour of recursion "
                    "and continued fractions.",
        parents=[common],
    )
    parser.add_argument("--all", action="store_true",
                        help="print every stop as a non-interactive transcript")
    parser.add_argument("--version", action="store_true", help="print version and exit")

    sub = parser.add_subparsers(dest="command")

    p_tour = sub.add_parser("tour", help="ride the interactive tour", parents=[common])
    p_tour.add_argument("--from", dest="start", type=int, default=1)

    p_stop = sub.add_parser("stop", help="print a single stop", parents=[common])
    p_stop.add_argument("number", type=int)

    sub.add_parser("list", help="show the route map", parents=[common])

    p_frontier = sub.add_parser("frontier", help="ride the Express Line (fringe topics)",
                                parents=[common])
    p_frontier.add_argument("number", nargs="?", type=int, default=None)

    p_cross = sub.add_parser("crossdomain", help="ride the Cross-Domain Line (the sciences)",
                             parents=[common])
    p_cross.add_argument("number", nargs="?", type=int, default=None)

    p_heritage = sub.add_parser("heritage", help="ride the Heritage Line (the history)",
                                parents=[common])
    p_heritage.add_argument("number", nargs="?", type=int, default=None)

    p_branch = sub.add_parser("branch", help="ride the Branch Line (other expansions)",
                              parents=[common])
    p_branch.add_argument("number", nargs="?", type=int, default=None)

    p_demo = sub.add_parser("demo", help="run one demonstration", parents=[common])
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

    if args.command == "demo":
        # REMAINDER swallows global flags placed after the demo name
        # (`demo gauss --ascii`); re-parse it with the shared parent so they
        # reach the console, and hand the demo only its own leftovers.
        _, args.args = _global_flags().parse_known_args(args.args, namespace=args)

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
    if args.command == "heritage":
        return _cmd_heritage(console, args.number)
    if args.command == "branch":
        return _cmd_branch(console, args.number)
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
        console.emit(console.style(exc.args[0], "warn"))
        return 1
    _print_stop(console, stop, len(STOPS))
    return 0


def _cmd_all(console: Console, *, start: int = 1) -> int:
    from .registry import STOPS

    start = max(1, min(len(STOPS), start))
    _title_banner(console)
    for stop in STOPS[start - 1:]:
        _print_stop(console, stop, len(STOPS))
        console.emit()
    console.emit(" " + console.style(
        "End of the main route. The tour continues on the Express Line.", "chrome"))
    console.emit()
    _cmd_frontier(console, None)
    console.emit()
    _cmd_crossline(console, None)
    console.emit()
    _cmd_heritage(console, None)
    console.emit()
    _cmd_branch(console, None)
    console.emit()
    console.emit(" " + console.style(
        "End of the line. Thank you for riding.", "success"))
    return 0


# --------------------------------------------------------------------------- #
#  The interactive tour: the main route, then the continuation lines.
# --------------------------------------------------------------------------- #

def _route_legs():
    """The five lines in riding order, normalised to ``(title, note, run)``.

    Each leg is ``(label, line name, entries)``; the label heads the position
    marker ("stop 7/15") and the EXPRESS / CROSS-DOMAIN / HERITAGE / BRANCH
    stop banners.
    """
    from .registry import STOPS
    from .express import EXPRESS_STOPS
    from .crossline import CROSS_STOPS
    from .heritage import HERITAGE_STOPS
    from .branch import BRANCH_STOPS

    main = [(s.title, s.note, s.run) for s in STOPS]
    return [
        ("STOP", "the main route", main),
        ("EXPRESS", "the Express Line", list(EXPRESS_STOPS)),
        ("CROSS-DOMAIN", "the Cross-Domain Line", list(CROSS_STOPS)),
        ("HERITAGE", "the Heritage Line", list(HERITAGE_STOPS)),
        ("BRANCH", "the Branch Line", list(BRANCH_STOPS)),
    ]


def _print_leg_stop(console: Console, legs, leg: int, idx: int) -> None:
    from . import render

    label, _line_name, entries = legs[leg]
    title, note, run = entries[idx]
    if leg == 0:
        console.emit(render.stop_header(idx + 1, len(entries), title, console))
        console.emit()
    else:
        _line_header(console, label, idx + 1, len(entries), title)
    console.paragraph(console.style(note, "chrome"))
    console.emit()
    run(console)


def _tour_map(console: Console, legs, at_leg: int, at_idx: int) -> None:
    """The full route map: all five lines, with the rider's position marked."""
    g = console.glyphs
    console.emit()
    for li, (_label, line_name, entries) in enumerate(legs):
        console.emit(" " + console.style(line_name.upper(), "title"))
        for i, (title, _note, _run) in enumerate(entries):
            if (li, i) < (at_leg, at_idx):
                dot = console.style(g.route_done, "route_done")
            elif (li, i) == (at_leg, at_idx):
                dot = console.style(g.route_here, "route_here")
            else:
                dot = console.style(g.route_ahead, "route_ahead")
            console.emit(f"  {dot} {i + 1:>2}. {title}")
        console.emit()


def _tour_help(console: Console) -> None:
    for line in (
        "Enter      next stop",
        "b          previous stop",
        "m          the route map (all five lines)",
        "g N / gN   jump to stop N of the current line",
        "h, ?       this help",
        "q          off the bus",
    ):
        console.emit("   " + console.style(line, "chrome"))
    console.emit()


def _cmd_tour(console: Console, *, start: int) -> int:
    interactive = bool(getattr(console.inp, "isatty", lambda: False)()) and \
        bool(getattr(console.out, "isatty", lambda: False)())

    if not interactive:
        # Piped/non-tty: behave like --all so transcripts are complete,
        # still boarding the main route at --from N.
        return _cmd_all(console, start=start)

    legs = _route_legs()
    _title_banner(console)
    console.emit(" " + console.style("Doors closing. First stop: Euclid, 300 BC.", "chrome"))
    console.emit()
    leg = 0
    idx = max(0, min(len(legs[0][2]) - 1, start - 1))
    sep = " - " if console.ascii_only else " · "
    while True:
        label, line_name, entries = legs[leg]
        total = len(entries)
        _print_leg_stop(console, legs, leg, idx)
        console.emit()
        if idx + 1 < total:
            nxt = entries[idx + 1][0]
        elif leg + 1 < len(legs):
            nxt = legs[leg + 1][1]
        else:
            nxt = "the depot"
        console.emit(" " + console.style(
            f"next stop {console.glyphs.arrow} {nxt}", "chrome"))
        pos = f"{label.lower()} {idx + 1}/{total}{sep}{entries[idx][0]}"
        # Prompt until a navigation command; map, help, and typos re-ask
        # without re-printing (and re-computing) the whole stop.
        while True:
            cmd = console.ask(
                f"{pos}  [Enter=go  b=back  m=map  g N=jump  h=help  q=off the bus]",
                "", parse=str,
            ).strip().lower()
            if cmd in ("m", "map"):
                _tour_map(console, legs, leg, idx)
                continue
            if cmd in ("h", "?", "help"):
                _tour_help(console)
                continue
            if cmd in ("", "q", "quit", "exit", "b", "back") or \
                    (cmd.startswith("g") and cmd[1:].strip().isdecimal()):
                break
            console.emit(" " + console.style(
                f"unknown command {cmd!r} (h for help)", "warn"))
        if cmd in ("q", "quit", "exit"):
            break
        if cmd in ("b", "back"):
            if idx > 0:
                idx -= 1
            elif leg > 0:
                leg -= 1
                idx = len(legs[leg][2]) - 1
            continue
        if cmd.startswith("g"):
            n = cmd[1:].strip()  # both "g 8" and "g8"
            idx = max(0, min(total - 1, int(n) - 1))
            continue
        # Enter: roll on to the next stop, or offer the next line at a terminus.
        idx += 1
        if idx >= total:
            if leg + 1 >= len(legs):
                break
            nxt_name = legs[leg + 1][1]
            # Same contract as the stop prompt: only Enter consents to board;
            # b steps back, m and h re-ask, and typos never board silently.
            while True:
                cmd = console.ask(
                    f"end of {line_name}  [Enter=board {nxt_name}  b=back  "
                    "m=map  h=help  q=off the bus]",
                    "", parse=str,
                ).strip().lower()
                if cmd in ("m", "map"):
                    _tour_map(console, legs, leg, idx)
                    continue
                if cmd in ("h", "?", "help"):
                    _tour_help(console)
                    continue
                if cmd in ("", "q", "quit", "exit", "b", "back"):
                    break
                console.emit(" " + console.style(
                    f"unknown command {cmd!r} (h for help)", "warn"))
            if cmd in ("q", "quit", "exit"):
                break
            if cmd in ("b", "back"):
                idx = total - 1
                continue
            leg += 1
            idx = 0
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
#  The Express, Cross-Domain, and Heritage Lines: stops beyond the main route.
# --------------------------------------------------------------------------- #

def _line_header(console: Console, label: str, number: int, total: int, title: str) -> None:
    rule = console.style(console.glyphs.h * console.width, "chrome")
    tag_text = f"{label} {number} / {total}"
    tag = console.style(tag_text, "marker")
    console.emit(rule)
    # Widths are measured on the unstyled text (style() adds zero-width ANSI
    # codes). On a narrow console the tag drops to its own line and the title
    # wraps, mirroring route_line's fallback, so nothing overflows the rules.
    if 1 + len(title) + 3 + len(tag_text) <= console.width:
        console.emit(" " + console.style(title.upper(), "title") + "   " + tag)
    else:
        for line in textwrap.wrap(title.upper(), width=max(20, console.width - 1)) or [""]:
            console.emit(" " + console.style(line, "title"))
        console.emit(" " + tag)
    console.emit(rule)
    console.emit()


def _run_line(console: Console, stops, *, banner: str, tagline: str, label: str,
              end_text: str, number: int | None) -> int:
    """Print one continuation line -- whole, or a single stop by number.

    Shared by the Express, Cross-Domain, and Heritage commands. The
    out-of-range message derives from ``label`` so every line phrases it
    identically.
    """
    total = len(stops)
    console.rule(console.glyphs.route_link)
    console.emit(" " + console.style(banner, "title") + "  " + console.glyphs.bus)
    console.paragraph(console.style(tagline, "chrome"))
    console.rule(console.glyphs.route_link)
    console.emit()

    if number is not None:
        if not 1 <= number <= total:
            console.emit(console.style(
                f"no {label.lower()} stop {number} (valid 1..{total})", "warn"))
            return 1
        indices = [number - 1]
    else:
        indices = range(total)

    for i in indices:
        title, note, run = stops[i]
        _line_header(console, label, i + 1, total, title)
        console.paragraph(console.style(note, "chrome"))
        console.emit()
        run(console)
        console.emit()
    console.emit(" " + console.style(end_text, "success"))
    return 0


def _cmd_frontier(console: Console, number: int | None) -> int:
    from .express import EXPRESS_STOPS

    return _run_line(
        console, EXPRESS_STOPS,
        banner="THE EXPRESS LINE",
        tagline="fringe avenues of recursion and continued fractions",
        label="EXPRESS",
        end_text="End of the Express Line.",
        number=number,
    )


def _cmd_crossline(console: Console, number: int | None) -> int:
    from .crossline import CROSS_STOPS

    return _run_line(
        console, CROSS_STOPS,
        banner="THE CROSS-DOMAIN LINE",
        tagline="the same recurrence, across the sciences",
        label="CROSS-DOMAIN",
        end_text="End of the Cross-Domain Line.",
        number=number,
    )


def _cmd_heritage(console: Console, number: int | None) -> int:
    from .heritage import HERITAGE_STOPS

    return _run_line(
        console, HERITAGE_STOPS,
        banner="THE HERITAGE LINE",
        tagline="a history in convergents",
        label="HERITAGE",
        end_text="End of the Heritage Line.",
        number=number,
    )


def _cmd_branch(console: Console, number: int | None) -> int:
    from .branch import BRANCH_STOPS

    return _run_line(
        console, BRANCH_STOPS,
        banner="THE BRANCH LINE",
        tagline="other ways to unfold a number",
        label="BRANCH",
        end_text="End of the Branch Line.",
        number=number,
    )
