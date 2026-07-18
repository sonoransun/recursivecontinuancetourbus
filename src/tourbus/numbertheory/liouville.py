"""Liouville numbers: the first numbers *proven* transcendental (1844).

Joseph Liouville's insight was to run the approximation argument backwards. A
real algebraic number of degree ``n`` cannot be approximated by rationals any
better than ``|alpha - p/q| > c / q^n`` (Liouville's inequality) -- its own
minimal polynomial fences it off. So a number that *is* approximable better than
any such power law cannot be algebraic at all. He then built one on purpose:

    L = sum_{n>=1} base^(-n!) = 0.110001000000000000000001000... (base 10)

The factorial spacing leaves ever-longer runs of zeros, so each truncation is an
astonishingly good rational approximation -- good enough to violate the degree-2,
then degree-3, then every degree bound. ``L`` is therefore transcendental, the
first number ever shown to be so.

The continued-fraction view is the one this tour cares about. "Too well
approximable" reads directly off the partial quotients: a rational ``p/q`` that
hugs ``L`` to within ``q^(-m)`` shows up as a partial quotient of size roughly
``q^(m-2)``. The factorial gaps make those quotients *explode* -- the CF of ``L``
is a string of small numbers punctuated by monsters like ``999999999999`` and a
72-digit giant right after it. That unbounded growth is the fingerprint of an
infinite irrationality measure, and infinite measure is transcendence.

Cross-references on the tour: Stop 4 (Hurwitz) shows ``sqrt(5)`` is the
*best-possible* uniform bound for algebraic irrationals -- the opposite extreme
from Liouville's arbitrarily-good approximations. Roth's 1955 theorem (a Fields
Medal) sharpens Liouville all the way: every algebraic irrational has
irrationality measure *exactly* 2, so the moment the measure exceeds 2 the number
is transcendental. Liouville numbers sit at measure infinity, as far past the
Roth line as a number can get.
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from math import factorial, isqrt, log
from typing import Sequence

from ..cf.convergents import convergent_pairs
from ..cf.core import QuadraticSurd, surd_floor
from ..cf.expand import cf_from_interval, cf_from_quadratic

__all__ = [
    "liouville_truncation",
    "liouville_tail_bound",
    "liouville_cf_terms",
    "partial_quotient_peaks",
    "irrationality_measure_witness",
    "liouville_inequality_check",
    "liouville_inequality_report",
]


def liouville_truncation(k: int, *, base: int = 10) -> Fraction:
    """The partial sum ``sum_{n=1..k} base^(-n!)`` as an exact rational.

    This is a lower bound for the Liouville constant and, being a finite sum of
    ``base``-power reciprocals, has denominator ``base^(k!)``.

    >>> liouville_truncation(3)
    Fraction(110001, 1000000)
    >>> liouville_truncation(1)
    Fraction(1, 10)
    >>> liouville_truncation(2, base=2)          # 1/2 + 1/4
    Fraction(3, 4)
    """
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    if base < 2:
        raise ValueError(f"base must be >= 2, got {base}")
    return sum(
        (Fraction(1, base ** factorial(n)) for n in range(1, k + 1)),
        Fraction(0),
    )


def liouville_tail_bound(k: int, *, base: int = 10) -> Fraction:
    """A rigorous upper bound on the discarded tail ``sum_{n>k} base^(-n!)``.

    The bound is ``2 * base^(-(k+1)!)``. Proof of the inequality: factor out the
    first surviving term,

        tail = base^(-(k+1)!) * (1 + base^(-((k+2)!-(k+1)!)) + ...).

    Every later exponent gap ``(n+1)! - (k+1)!`` is at least ``1``, so the series
    in parentheses is dominated term-by-term by ``1 + base^-1 + base^-2 + ...``,
    a geometric series summing to ``base/(base-1) <= 2`` for ``base >= 2``. Hence
    ``tail < 2 * base^(-(k+1)!)``. The bound is loose but *certified*, which is
    all :func:`liouville_cf_terms` needs to bracket the constant.

    >>> liouville_tail_bound(3)
    Fraction(1, 500000000000000000000000)
    >>> liouville_tail_bound(1, base=2)          # 2 * 2^(-2)
    Fraction(1, 2)
    """
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    if base < 2:
        raise ValueError(f"base must be >= 2, got {base}")
    return 2 * Fraction(1, base ** factorial(k + 1))


def liouville_cf_terms(
    k: int = 3, *, base: int = 10, max_terms: int = 20
) -> list[int]:
    """Certified partial quotients of the Liouville constant, via interval CF.

    The exact value ``L`` is bracketed between the truncation ``T_k`` and
    ``T_k + tail_bound_k`` -- a *fixed* interval, independent of any requested
    precision. Feeding that constant bracket to :func:`~tourbus.cf.expand.\
cf_from_interval` yields exactly the partial quotients the bracket can certify
    and then stops (a constant oracle never tightens, so the expander refuses to
    guess past the point where the next floor is ambiguous). The result is a
    rigorous *prefix* of the true CF, capped at ``max_terms``.

    Raising ``k`` widens the certified prefix rather than changing it: each
    result is a prefix of the next. With ``k=3`` the interval is only tight
    enough to certify through the modest quotient ``99``; the first *monster*
    partial quotient, ``999999999999`` -- the CF hallmark of a Liouville number's
    ruthless approximability -- becomes certifiable at ``k=4``.

    >>> liouville_cf_terms(3)
    [0, 9, 11, 99, 1, 10, 9]
    >>> liouville_cf_terms(4)
    [0, 9, 11, 99, 1, 10, 9, 999999999999, 1, 8, 10, 1, 99, 11, 9]
    >>> liouville_cf_terms(3) == liouville_cf_terms(4)[:7]   # prefix property
    True
    """
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    if max_terms < 0:
        raise ValueError(f"max_terms must be >= 0, got {max_terms}")
    lo = liouville_truncation(k, base=base)
    hi = lo + liouville_tail_bound(k, base=base)

    def produce(_precision: int) -> tuple[Fraction, Fraction]:
        # A constant oracle: the bracket never tightens, so cf_from_interval
        # emits precisely the certifiable prefix and halts.
        return lo, hi

    return list(itertools.islice(cf_from_interval(produce), max_terms))


def partial_quotient_peaks(terms: Sequence[int]) -> list[tuple[int, int]]:
    """The running-maximum partial quotients as ``(index, value)`` records.

    Each entry beats every earlier one, so the list narrates the "explosion":
    for a Liouville number the record values grow without bound.

    >>> partial_quotient_peaks([0, 9, 11, 99, 1, 10, 9, 999999999999])
    [(0, 0), (1, 9), (2, 11), (3, 99), (7, 999999999999)]
    >>> partial_quotient_peaks([3, 1, 4, 1, 5])
    [(0, 3), (2, 4), (4, 5)]
    """
    peaks: list[tuple[int, int]] = []
    record: int | None = None
    for i, a in enumerate(terms):
        if record is None or a > record:
            peaks.append((i, a))
            record = a
    return peaks


def irrationality_measure_witness(terms: Sequence[int]) -> list[float]:
    """Growth ratios ``log(q_{n+1}) / log(q_n)`` of the convergent denominators.

    The convergent ``p_n/q_n`` approximates the value with error
    ``|alpha - p_n/q_n| ~ q_n^(-1-r_n)``, where ``r_n`` is exactly this ratio
    (up to lower-order terms), because ``q_{n+1} ~ a_{n+1} q_n`` and the error is
    ``~ 1/(q_n q_{n+1})``. So an *unbounded* ``r_n`` means ``alpha`` is
    approximated better than ``q^(-1-B)`` for every ``B`` -- irrationality measure
    above every bound, i.e. infinite -- which by Liouville's theorem forces
    transcendence.

    The contrast is the whole point. For a number with bounded partial quotients
    (the golden ratio ``[1;1,1,...]``, say) ``q_{n+1} ~ phi * q_n``, so
    ``r_n -> 1`` and the ratios stay near 1. For the Liouville constant a giant
    partial quotient makes ``q`` leap, spiking ``r_n`` far above anything the
    bounded case reaches. (Ratios are reported as floats rounded to 4 places --
    the only place this module leaves exact arithmetic, and only for display.)

    ``q_0 = 1`` gives ``log q_0 = 0``, so denominators equal to 1 are skipped; the
    ratios returned are for consecutive convergents both having ``q > 1``.

    >>> irrationality_measure_witness([1, 1, 1, 1, 1])       # golden-ratio prefix
    [1.585, 1.465]
    >>> w = irrationality_measure_witness(
    ...     [0, 9, 11, 99, 1, 10, 9, 999999999999, 1])
    >>> max(w) > 2.5                                          # the Liouville spike
    True
    """
    qs = [k for _, k in convergent_pairs(terms)]
    out: list[float] = []
    for n in range(1, len(qs) - 1):
        if qs[n] > 1 and qs[n + 1] > 1:
            out.append(round(log(qs[n + 1]) / log(qs[n]), 4))
    return out


# --------------------------------------------------------------------------- #
#  Liouville's inequality for degree 2: an exact, rational-only verifier.
# --------------------------------------------------------------------------- #

def _surd_pos(c: Fraction, b: Fraction, D: int) -> bool:
    """Exact sign test: is ``c + b*sqrt(D) > 0``? (``c, b`` rational, ``D >= 0``)."""
    if b == 0:
        return c > 0
    if b > 0:  # b*sqrt(D) > 0; compare with -c
        return c >= 0 or b * b * D > c * c
    # b < 0: c + b*sqrt(D) > 0  <=>  c > |b|*sqrt(D)  (needs c > 0)
    return c > 0 and c * c > b * b * D


def _abs_surd_gt(a: Fraction, b: Fraction, D: int, m: Fraction) -> bool:
    """Exact test: is ``|a + b*sqrt(D)| > m`` for ``m >= 0``?

    ``|x| > m`` iff ``x - m > 0`` or ``x + m < 0``; each is an exact surd sign.
    """
    return _surd_pos(a - m, b, D) or _surd_pos(-a - m, -b, D)


def _quadratic_root(A: int, B: int, C: int) -> tuple[QuadraticSurd, int, int, int]:
    """Normalize ``A x^2 + B x + C`` to ``A > 0`` and return its larger root.

    Also returns the sign-normalized ``(A, B, C)`` (with ``A > 0``). Raises for a
    non-quadratic, or a rational / complex root.
    """
    if A == 0:
        raise ValueError("A must be non-zero (this is the degree-2 bound)")
    if A < 0:
        A, B, C = -A, -B, -C
    disc = B * B - 4 * A * C
    if disc <= 0:
        raise ValueError("need two distinct real roots (discriminant > 0)")
    if isqrt(disc) ** 2 == disc:
        raise ValueError("root is rational, not a quadratic irrational")
    # A > 0, so the "+sqrt" branch (P + sqrt(D))/Q with Q = 2A is the larger root.
    alpha = QuadraticSurd.from_pqd(-B, disc, 2 * A)
    return alpha, A, B, C


def liouville_inequality_check(A: int, B: int, C: int, p: int, q: int) -> bool:
    """Verify Liouville's degree-2 bound ``|alpha - p/q| > 1/(K q^2)`` exactly.

    ``alpha`` is the larger real root of ``A x^2 + B x + C`` (which must be a
    quadratic *irrational*), and

        K = |A| * (2 * ceil(|alpha|) + 3).

    Where this constant comes from: writing ``f(x) = A(x-alpha)(x-alpha_bar)``,
    the integer ``A p^2 + B p q + C q^2`` is non-zero (``alpha`` is irrational),
    so ``|f(p/q)| >= 1/q^2``; dividing by ``|A|*|p/q - alpha_bar|`` and bounding
    ``|p/q - alpha_bar| < 2*ceil(|alpha|) + 3`` whenever ``p/q`` is within 1 of
    ``alpha`` (and handling the far case trivially) yields the stated ``K``. This
    routine does not merely assert that derivation -- it *checks the actual
    inequality* with exact rational/surd arithmetic (all comparisons are of
    squared quantities, so no square root is ever taken numerically). ``q`` must
    be positive.

    >>> liouville_inequality_check(1, 0, -2, 3, 2)      # |sqrt(2) - 3/2| bound
    True
    >>> liouville_inequality_check(1, 0, -2, 1000000, 1)
    True
    >>> liouville_inequality_check(1, -1, -1, 8, 5)     # golden ratio, 8/5
    True
    """
    if q <= 0:
        raise ValueError(f"q must be positive, got {q}")
    alpha, A, B, C = _quadratic_root(A, B, C)

    # ceil(|alpha|): |alpha| as an exact surd, then floor + 1 (alpha irrational).
    if _surd_pos(alpha.a, alpha.b, alpha.D):
        abs_alpha = alpha
    else:
        abs_alpha = QuadraticSurd(-alpha.a, -alpha.b, alpha.D)
    ceil_abs = surd_floor(abs_alpha) + 1

    K = A * (2 * ceil_abs + 3)
    bound = Fraction(1, K * q * q)
    return _abs_surd_gt(alpha.a - Fraction(p, q), alpha.b, alpha.D, bound)


def liouville_inequality_report(
    A: int, B: int, C: int, cf_prefix_len: int = 8
) -> list[tuple[int, int, bool]]:
    """Run :func:`liouville_inequality_check` over ``alpha``'s own convergents.

    The convergents of ``alpha`` are its *hardest* rational approximations -- the
    tightest test of the bound -- yet Liouville's inequality still fences them all
    off, so every entry is ``True``. Returns ``(p, q, ok)`` for the first
    ``cf_prefix_len`` convergents.

    >>> liouville_inequality_report(1, 0, -2)           # sqrt(2)
    [(1, 1, True), (3, 2, True), (7, 5, True), (17, 12, True), (41, 29, True), (99, 70, True), (239, 169, True), (577, 408, True)]
    >>> [ok for _, _, ok in liouville_inequality_report(1, -1, -1)]   # golden ratio
    [True, True, True, True, True, True, True, True]
    """
    if cf_prefix_len < 0:
        raise ValueError(f"cf_prefix_len must be >= 0, got {cf_prefix_len}")
    _, An, Bn, Cn = _quadratic_root(A, B, C)
    disc = Bn * Bn - 4 * An * Cn
    pre, period = cf_from_quadratic(-Bn, disc, 2 * An)

    def cf_terms() -> "list[int]":
        terms: list[int] = []
        i = 0
        while len(terms) < cf_prefix_len:
            if i < len(pre):
                terms.append(pre[i])
            else:
                terms.append(period[(i - len(pre)) % len(period)])
            i += 1
        return terms

    out: list[tuple[int, int, bool]] = []
    for h, k in convergent_pairs(cf_terms()):
        out.append((h, k, liouville_inequality_check(A, B, C, h, k)))
    return out
