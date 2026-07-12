"""Terminal I/O: colour, glyphs, wrapping, and prompts that never block CI.

Everything here degrades gracefully. Colour is emitted only to a real TTY that
advertises support and does not set ``NO_COLOR``. Prompts fall back to their
default when input is piped or exhausted, so a full ``--all`` transcript runs
start-to-finish without a human.
"""

from __future__ import annotations

import os
import random
import shutil
import sys
import textwrap
from dataclasses import dataclass
from typing import Callable, TextIO, TypeVar

T = TypeVar("T")

# ANSI SGR codes, used only when colour is enabled.
_CODES = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "reverse": "\033[7m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
}

# Semantic roles -> code sequences.
_ROLES = {
    "title": ("bold", "cyan"),
    "chrome": ("dim",),
    "result": ("yellow",),
    "success": ("green",),
    "warn": ("red",),
    "marker": ("magenta", "bold"),
    "route_done": ("cyan",),
    "route_here": ("bold", "cyan"),
    "route_ahead": ("dim",),
}


@dataclass
class Glyphs:
    """The small symbol vocabulary, with a pure-ASCII fallback."""

    route_done: str
    route_here: str
    route_ahead: str
    route_link: str
    bus: str
    bar: str
    bar_half: str
    tl: str
    tr: str
    bl: str
    br: str
    h: str
    v: str
    arrow: str
    star: str
    bullet: str

    @classmethod
    def unicode(cls) -> "Glyphs":
        return cls(
            route_done="●", route_here="◉", route_ahead="○", route_link="━",
            bus="🚌", bar="█", bar_half="▌", tl="┌", tr="┐", bl="└", br="┘",
            h="─", v="│", arrow="→", star="⁂", bullet="▸",
        )

    @classmethod
    def ascii(cls) -> "Glyphs":
        return cls(
            route_done="*", route_here="@", route_ahead="o", route_link="-",
            bus="[BUS]", bar="#", bar_half="=", tl="+", tr="+", bl="+", br="+",
            h="-", v="|", arrow="->", star="*", bullet=">",
        )


def supports_color(stream: TextIO) -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


@dataclass
class Console:
    """Bundles output configuration and the styling/prompt helpers."""

    width: int = 80
    color: bool = False
    ascii_only: bool = False
    fast: bool = False
    out: TextIO = sys.stdout
    inp: TextIO = sys.stdin
    rng: random.Random = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.rng is None:
            self.rng = random.Random(0)
        self.glyphs = Glyphs.ascii() if self.ascii_only else Glyphs.unicode()

    # -- styling ------------------------------------------------------------ #

    def style(self, text: str, role: str) -> str:
        if not self.color or role not in _ROLES:
            return text
        prefix = "".join(_CODES[c] for c in _ROLES[role])
        return f"{prefix}{text}{_CODES['reset']}"

    def emit(self, text: str = "") -> None:
        self.out.write(text + "\n")

    def wrap(self, text: str, indent: str = " ") -> str:
        out_lines = []
        for para in text.split("\n"):
            if not para.strip():
                out_lines.append("")
                continue
            out_lines.extend(
                textwrap.wrap(
                    para,
                    width=self.width - len(indent),
                    initial_indent=indent,
                    subsequent_indent=indent,
                )
            )
        return "\n".join(out_lines)

    def paragraph(self, text: str, indent: str = " ") -> None:
        self.emit(self.wrap(text, indent))

    def rule(self, char: str | None = None) -> None:
        c = char or self.glyphs.h
        self.emit(self.style(c * self.width, "chrome"))

    # -- prompts ------------------------------------------------------------ #

    def ask(
        self,
        question: str,
        default: str,
        parse: Callable[[str], T] = str,  # type: ignore[assignment]
    ) -> T:
        """Prompt for input; fall back to ``default`` when non-interactive.

        Works in three modes: an interactive TTY (shows the prompt and reads a
        line), piped stdin (consumes the next line if present), and exhausted
        input (uses the default and announces it so transcripts stay readable).
        """
        marker = self.style(self.glyphs.bullet + " try>", "marker")
        interactive = bool(getattr(self.inp, "isatty", lambda: False)())
        if interactive:
            self.out.write(f"  {marker} {question} [{default}]: ")
            self.out.flush()
            try:
                raw = self.inp.readline()
            except (EOFError, KeyboardInterrupt):
                raw = ""
            raw = raw.strip() if raw else ""
        else:
            line = self.inp.readline() if self.inp else ""
            raw = line.strip() if line else ""
            shown = raw if raw else f"[auto: {default}]"
            self.emit(f"  {marker} {question} {shown}")
        value = raw if raw else default
        try:
            return parse(value)
        except (ValueError, ZeroDivisionError):
            return parse(default)


def make_console(
    *,
    width: int | None = None,
    color: bool | None = None,
    ascii_only: bool = False,
    fast: bool = False,
    out: TextIO | None = None,
    inp: TextIO | None = None,
    seed: int = 0,
) -> Console:
    out = out or sys.stdout
    inp = inp or sys.stdin
    if width is None:
        try:
            width = shutil.get_terminal_size().columns
        except Exception:
            width = 80
        width = max(60, min(120, width))
    if color is None:
        color = supports_color(out)
    if not getattr(out, "isatty", lambda: False)():
        fast = True
    return Console(
        width=width,
        color=color,
        ascii_only=ascii_only,
        fast=fast,
        out=out,
        inp=inp,
        rng=random.Random(seed),
    )
