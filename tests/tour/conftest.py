"""Fixtures for driving the tour CLI in-process with captured output."""

from __future__ import annotations

import dataclasses
import io
import sys

import pytest

from tourbus.tour import branch, crossline, express, heritage, registry, runner
from tourbus.tour.termio import Console


@pytest.fixture
def run_cli(capsys, monkeypatch):
    """Invoke ``runner.main(argv)`` and return ``(exit_code, stdout)``.

    stdin is replaced with an exhausted pipe so every interactive prompt falls
    back to its default, exactly as in the CI transcript runs.
    """

    def run(*argv: str):
        monkeypatch.setattr(sys, "stdin", io.StringIO(""))
        code = runner.main(list(argv))
        return code, capsys.readouterr().out

    return run


@pytest.fixture
def stub_lines(monkeypatch):
    """No-op every stop body on all five lines, keeping banners and prompts.

    Lets tests cover the full route structure (headers, boarding, the closing
    line) without paying for the stops' actual computations.
    """
    monkeypatch.setattr(registry, "STOPS", [
        dataclasses.replace(s, run=lambda c: None) for s in registry.STOPS])
    monkeypatch.setattr(express, "EXPRESS_STOPS", [
        (title, note, lambda c: None) for title, note, _ in express.EXPRESS_STOPS])
    monkeypatch.setattr(crossline, "CROSS_STOPS", [
        (title, note, lambda c: None) for title, note, _ in crossline.CROSS_STOPS])
    monkeypatch.setattr(heritage, "HERITAGE_STOPS", [
        (title, note, lambda c: None) for title, note, _ in heritage.HERITAGE_STOPS])
    monkeypatch.setattr(branch, "BRANCH_STOPS", [
        (title, note, lambda c: None) for title, note, _ in branch.BRANCH_STOPS])


class _Tty(io.StringIO):
    """A StringIO that claims to be a terminal, so the loop goes interactive."""

    def isatty(self):
        return True


@pytest.fixture
def ride(monkeypatch):
    """Ride the interactive loop with scripted keystrokes; returns the output.

    The stop bodies are stubbed out so their own "try>" prompts do not eat the
    scripted keystrokes; the bodies themselves are covered by the table-driven
    tests. What is exercised is the loop: headers, prompts, and navigation.
    """
    legs = [(label, name, [(title, note, lambda c: None) for title, note, _ in entries])
            for label, name, entries in runner._route_legs()]
    monkeypatch.setattr(runner, "_route_legs", lambda: legs)

    def _ride(keys: str, *, start: int = 1) -> str:
        out = _Tty()
        console = Console(width=80, color=False, out=out, inp=_Tty(keys))
        assert runner._cmd_tour(console, start=start) == 0
        return out.getvalue()

    return _ride
