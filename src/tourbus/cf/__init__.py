"""The continued-fraction nucleus.

Everything else in :mod:`tourbus` depends on this subpackage but not the other
way around. The central object is :class:`~tourbus.cf.core.CF`: a re-iterable,
lazily-cached stream of integer partial quotients that unifies finite,
periodic, and genuinely infinite continued fractions under one interface.
"""

from __future__ import annotations

from .core import CF, CFKind, QuadraticSurd

__all__ = ["CF", "CFKind", "QuadraticSurd"]
