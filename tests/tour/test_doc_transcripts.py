"""Every terminal transcript in the docs must be what the CLI prints today.

The chapters show real sessions — a fenced block whose first line is
``$ python -m tourbus ...`` followed by the output. This test replays each
command in-process (plain output, stdin exhausted, exactly as the transcripts
were captured) and compares it with the documented output, so a change to a
demo can never leave a stale transcript behind.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parents[2] / "docs"
_FENCE = re.compile(r"```\n\$ python -m tourbus ([^\n]*)\n(.*?)```", re.S)


def _transcripts() -> list[tuple[str, str, str]]:
    out = []
    for path in sorted(DOCS.glob("*.md")):
        for m in _FENCE.finditer(path.read_text(encoding="utf-8")):
            out.append((f"{path.name}: {m.group(1)}", m.group(1), m.group(2)))
    return out


CASES = _transcripts()


def test_the_docs_carry_transcripts():
    assert len(CASES) >= 70


@pytest.mark.slow
@pytest.mark.parametrize("label,command,expected", CASES, ids=[c[0] for c in CASES])
def test_documented_transcript_matches_the_cli(run_cli, label, command, expected):
    argv = command.split()
    if "--no-color" not in argv:
        argv.append("--no-color")
    _code, out = run_cli(*argv)
    assert out.rstrip("\n") == expected.rstrip("\n"), label
