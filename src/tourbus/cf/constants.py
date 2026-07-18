"""Continued fractions of the celebrity constants.

* ``phi`` and ``sqrt(n)`` are exact quadratic surds (periodic).
* ``e`` has a known exact pattern ``[2; 1, 2, 1, 1, 4, 1, 1, 6, ...]`` and is
  generated term-by-term with no rounding at all.
* ``pi`` and the other transcendental constants are seeded from a rigorous
  decimal bracket and expanded only as far as that precision certifies — we
  never emit a partial quotient we cannot prove.
"""

from __future__ import annotations

import decimal
from decimal import Decimal
from fractions import Fraction
from typing import Callable, Iterator

from .core import CF, CFKind
from .expand import cf_from_fraction, cf_from_interval

__all__ = [
    "phi_cf",
    "sqrt_cf",
    "e_cf",
    "tan1_cf",
    "pi_cf",
    "pi_cf_via_gcf",
    "gamma_cf",
    "catalan_cf",
    "log2_ratio_cf",
    "khinchin_cf",
]

# High-precision decimal strings for constants without a clean closed-form CF
# or a cheap high-precision series. ~100 significant digits -> ~40 certified
# continued-fraction terms, plenty for the tour's demonstrations.
_GAMMA = "0.57721566490153286060651209008240243104215933593992359880576723488486772677766467093694706329174674951463"
_CATALAN = "0.91596559417721901505460351493238411077414937428167213426649811962176301977625476947935651292611510624857"
_KHINCHIN = "2.68545200106530644530971483548179569382038229399446295305115234555721885953715200280114117493184769799515"


def phi_cf() -> CF:
    """The golden ratio, ``[1; 1, 1, 1, ...]``.

    >>> phi_cf().terms(6)
    [1, 1, 1, 1, 1, 1]
    """
    return CF.periodic([], [1])


def sqrt_cf(n: int) -> CF:
    """The continued fraction of ``sqrt(n)`` (finite iff ``n`` is a square).

    >>> str(sqrt_cf(2))
    '[1; (2)]'
    >>> str(sqrt_cf(7))
    '[2; (1, 1, 1, 4)]'
    """
    return CF.from_quadratic(0, n, 1)


def e_cf(max_terms: int | None = None) -> CF:
    """Euler's number ``e = [2; 1, 2, 1, 1, 4, 1, 1, 6, ...]`` (exact pattern).

    >>> e_cf().terms(11)
    [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1]
    """

    def factory() -> Iterator[int]:
        count = 0

        def emit(v: int) -> Iterator[int]:
            nonlocal count
            count += 1
            yield v

        yield from emit(2)
        k = 1
        while max_terms is None or count < max_terms:
            for v in (1, 2 * k, 1):
                if max_terms is not None and count >= max_terms:
                    return
                yield from emit(v)
            k += 1

    return CF.from_stream(factory, kind=CFKind.INFINITE)


def tan1_cf() -> CF:
    """Lambert's ``tan(1) = [1; 1, 1, 3, 1, 5, 1, 7, ...]``, certified exactly.

    The alternating Taylor partial sums for ``sin(1)`` and ``cos(1)`` are
    exact Fractions that bracket their limits, so ``(sin_lo/cos_hi,
    sin_hi/cos_lo)`` rigorously brackets ``tan(1)`` — no rounding anywhere.
    (Lambert's own generalized CF is *not* used: its convergents approach
    monotonically, so the alternation-based ``gcf_to_simple`` bracket would
    not certify it.)

    >>> tan1_cf().terms(10)
    [1, 1, 1, 3, 1, 5, 1, 7, 1, 9]
    """

    def bracket(parity: int, count: int) -> tuple[Fraction, Fraction]:
        # Partial sums of sum_j (-1)^j / (2j + parity)! — consecutive ones
        # bracket the limit (alternating, strictly shrinking terms).
        total = prev = Fraction(0)
        fact = 1                      # parity! for parity in {0, 1}
        sign = 1
        for j in range(count):
            prev = total
            total += Fraction(sign, fact)
            sign = -sign
            fact *= (parity + 2 * j + 1) * (parity + 2 * j + 2)
        lo, hi = sorted((prev, total))
        return lo, hi

    def produce(prec: int) -> tuple[Fraction, Fraction]:
        count = prec + 8
        sin_lo, sin_hi = bracket(1, count)
        cos_lo, cos_hi = bracket(0, count)
        return sin_lo / cos_hi, sin_hi / cos_lo

    return CF.from_stream(
        lambda: cf_from_interval(produce), kind=CFKind.INFINITE
    )


def _machin_pi(prec: int) -> Decimal:
    """Compute pi to ``prec`` significant digits via Machin's formula."""
    with decimal.localcontext() as ctx:
        ctx.prec = prec + 15

        def arctan_inv(n: int) -> Decimal:
            n = Decimal(n)
            total = Decimal(0)
            power = 1 / n
            nsq = n * n
            k = 0
            sign = 1
            while True:
                term = power / (2 * k + 1)
                if term == 0:
                    break
                total += sign * term
                power /= nsq
                sign = -sign
                k += 1
            return total

        pi = 16 * arctan_inv(5) - 4 * arctan_inv(239)
        return +pi  # round to context precision


def _pi_bracket(digits: int) -> tuple[Fraction, Fraction]:
    """A rigorous rational bracket ``(lo, hi)`` around pi to ``digits`` places."""
    with decimal.localcontext() as ctx:
        ctx.prec = digits + 20
        d = _machin_pi(digits + 5)
        approx = d.quantize(Decimal(10) ** -digits, rounding=decimal.ROUND_HALF_EVEN)
        center = Fraction(approx)
    eps = Fraction(1, 10 ** digits)
    return center - eps, center + eps


def pi_cf(*, decimal_digits: int = 1000) -> CF:
    """The continued fraction of pi, certified from a decimal bracket.

    Emits provably-correct partial quotients until the ``decimal_digits`` seed
    can no longer resolve the next term, then stops. No known pattern.

    >>> pi_cf().terms(8)
    [3, 7, 15, 1, 292, 1, 1, 1]
    """
    lo, hi = _pi_bracket(decimal_digits)

    def produce(_prec: int) -> tuple[Fraction, Fraction]:
        return lo, hi

    return CF.from_stream(
        lambda: cf_from_interval(produce), kind=CFKind.INFINITE
    )


def pi_cf_via_gcf() -> CF:
    """Pi via the generalized-CF route (reach goal; alternation-certified).

    Uses Brouncker/Nilakantha-style numerators converted to simple form. Slower
    to certify than :func:`pi_cf`; provided to show that order in a *generalized*
    CF underlies the chaos of the simple one.
    """
    from .gcf import gcf_to_simple, pi_gcf

    return CF.from_stream(
        lambda: gcf_to_simple(pi_gcf(), max_terms=2000), kind=CFKind.INFINITE
    )


def _cf_from_decimal_string(s: str) -> CF:
    """Build a certified CF from an exact decimal string (assumes last digit ±1)."""
    center = Fraction(s)
    frac_digits = len(s.split(".")[1]) if "." in s else 0
    eps = Fraction(1, 10 ** frac_digits)
    lo, hi = center - eps, center + eps

    def produce(_prec: int) -> tuple[Fraction, Fraction]:
        return lo, hi

    return CF.from_stream(
        lambda: cf_from_interval(produce), kind=CFKind.INFINITE
    )


def gamma_cf() -> CF:
    """The Euler-Mascheroni constant ``gamma`` (no known pattern; open irrationality).

    >>> gamma_cf().terms(5)
    [0, 1, 1, 2, 1]
    """
    return _cf_from_decimal_string(_GAMMA)


def catalan_cf() -> CF:
    """Catalan's constant ``G`` (irrationality unknown)."""
    return _cf_from_decimal_string(_CATALAN)


def khinchin_cf() -> CF:
    """Khinchin's constant ``K0`` (irrationality unknown)."""
    return _cf_from_decimal_string(_KHINCHIN)


def log2_ratio_cf(p: int, q: int, *, digits: int = 80) -> CF:
    """The continued fraction of ``log2(p/q)`` (e.g. ``log2(3/2)`` for music).

    >>> log2_ratio_cf(3, 2).terms(6)
    [0, 1, 1, 2, 2, 3]
    """
    with decimal.localcontext() as ctx:
        ctx.prec = digits + 15
        value = (Decimal(p) / Decimal(q)).ln() / Decimal(2).ln()
        s = str(+value.quantize(Decimal(10) ** -digits))
    return _cf_from_decimal_string(s)
