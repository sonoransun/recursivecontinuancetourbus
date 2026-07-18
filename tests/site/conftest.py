"""Fixtures for build-pipeline tests: load repo-root modules by file path.

The build tools (``build_mermaid.py``, ``build_site.py``) live at the repo
root, outside the installable package, so they are imported here via
``importlib.util.spec_from_file_location`` rather than a package import.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_CACHE: dict[str, object] = {}


def _load(name: str):
    """Import repo-root module ``<name>.py`` by absolute path (cached)."""
    if name not in _CACHE:
        path = ROOT / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        _CACHE[name] = module
    return _CACHE[name]


@pytest.fixture(scope="session")
def load_module():
    """The ``_load`` helper as a fixture: ``load_module("build_mermaid")``."""
    return _load
