"""The core continued-fraction data model.

A simple continued fraction is, at bottom, a stream of integer *partial
quotients* ``a0, a1, a2, ...`` with ``a0`` an integer and ``a_n >= 1`` for
``n >= 1``. Finite, eventually-periodic, and genuinely infinite continued
fractions differ only in how that stream ends and in what metadata we can
attach. :class:`CF` captures all three under one interface.

The one implementation subtlety worth stating up front: a :class:`CF` holds a
**factory** that produces a fresh iterator, plus a lazily-grown cache of the
terms it has already seen. That is what makes a single ``CF`` safe to iterate
repeatedly — ``value()``, ``convergents()`` and ``str()`` all walk the same
object without consuming a one-shot generator out from under each other.
"""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Iterator, Sequence

from .._util.formatting import cf_to_str

__all__ = ["CF", "CFKind", "QuadraticSurd", "surd_floor"]

_DISPLAY_TERMS = 20  # how many partial quotients str() shows for an open-ended CF


class CFKind(enum.Enum):
    """What we know about how a continued fraction ends."""

    FINITE = "finite"        # terminates: a rational number
    PERIODIC = "periodic"    # eventually periodic: a quadratic irrational
    INFINITE = "infinite"    # known infinite, no known period (e.g. e, pi)
    UNKNOWN = "unknown"      # produced lazily; may be any of the above


# --------------------------------------------------------------------------- #
#  Quadratic surds: the exact values of periodic continued fractions.
# --------------------------------------------------------------------------- #

def _squarefree_part(d: int) -> tuple[int, int]:
    """Factor ``d = s*s * r`` with ``r`` squarefree; return ``(s, r)``.

    >>> _squarefree_part(8)
    (2, 2)
    >>> _squarefree_part(12)
    (2, 3)
    >>> _squarefree_part(7)
    (1, 7)
    """
    if d < 0:
        raise ValueError("quadratic surds here use a non-negative radicand")
    s, r = 1, d
    i = 2
    while i * i <= r:
        while r % (i * i) == 0:
            r //= i * i
            s *= i
        i += 1
    return s, r


@dataclass(frozen=True)
class QuadraticSurd:
    """An exact quadratic irrational ``a + b*sqrt(D)`` with ``a, b`` rational.

    ``D`` is stored squarefree so that structurally-equal surds compare equal.
    A surd with ``b == 0`` is really a rational; :meth:`as_fraction` recovers it.
    """

    a: Fraction
    b: Fraction
    D: int

    @staticmethod
    def make(a: Fraction | int, b: Fraction | int, D: int) -> "QuadraticSurd":
        """Canonicalizing constructor: reduces ``D`` to its squarefree part."""
        a = Fraction(a)
        b = Fraction(b)
        if D < 0:
            raise ValueError("radicand must be non-negative")
        if b == 0 or D == 0:
            return QuadraticSurd(a, Fraction(0), 1)
        s, r = _squarefree_part(D)
        if r == 1:  # perfect square: fold sqrt(D) = s into the rational part
            return QuadraticSurd(a + b * s, Fraction(0), 1)
        return QuadraticSurd(a, b * s, r)

    @classmethod
    def from_pqd(cls, P: int, D: int, Q: int) -> "QuadraticSurd":
        """Build ``(P + sqrt(D)) / Q``."""
        if Q == 0:
            raise ZeroDivisionError("Q must be non-zero")
        return cls.make(Fraction(P, Q), Fraction(1, Q), D)

    def is_rational(self) -> bool:
        return self.b == 0

    def as_fraction(self) -> Fraction:
        if not self.is_rational():
            raise ValueError(f"{self} is irrational")
        return self.a

    def conjugate(self) -> "QuadraticSurd":
        return QuadraticSurd(self.a, -self.b, self.D)

    def homographic(self, p: int, q: int, r: int, s: int) -> "QuadraticSurd":
        """Return the Moebius image ``(p*self + q) / (r*self + s)`` exactly."""
        # numerator   = (p*a + q) + (p*b) sqrt(D)
        # denominator = (r*a + s) + (r*b) sqrt(D)
        num_a = p * self.a + q
        num_b = p * self.b
        den_a = r * self.a + s
        den_b = r * self.b
        # multiply through by the conjugate of the denominator
        norm = den_a * den_a - den_b * den_b * self.D
        if norm == 0:
            raise ZeroDivisionError("homographic transform hit a pole")
        out_a = (num_a * den_a - num_b * den_b * self.D) / norm
        out_b = (num_b * den_a - num_a * den_b) / norm
        return QuadraticSurd.make(out_a, out_b, self.D)

    def minimal_polynomial(self) -> tuple[int, int, int]:
        """Integer coefficients ``(A, B, C)`` with ``A x^2 + B x + C = 0``.

        >>> QuadraticSurd.from_pqd(1, 5, 2).minimal_polynomial()  # golden ratio
        (1, -1, -1)
        """
        # x = a + b sqrt(D)  =>  (x - a)^2 = b^2 D  =>  x^2 - 2a x + (a^2 - b^2 D) = 0
        A = Fraction(1)
        B = -2 * self.a
        C = self.a * self.a - self.b * self.b * self.D
        denom = math.lcm(A.denominator, B.denominator, C.denominator)
        ai, bi, ci = int(A * denom), int(B * denom), int(C * denom)
        g = math.gcd(math.gcd(abs(ai), abs(bi)), abs(ci)) or 1
        ai, bi, ci = ai // g, bi // g, ci // g
        if ai < 0:
            ai, bi, ci = -ai, -bi, -ci
        return ai, bi, ci

    def __float__(self) -> float:
        return float(self.a) + float(self.b) * math.sqrt(self.D)

    def __str__(self) -> str:
        if self.is_rational():
            return str(self.a)
        b = self.b
        radical = f"sqrt({self.D})"
        if b == 1:
            surd = radical
        elif b == -1:
            surd = f"-{radical}"
        else:
            surd = f"{b}*{radical}"
        if self.a == 0:
            return surd
        sign = "+" if b > 0 else "-"
        mag = surd.lstrip("-")
        return f"{self.a} {sign} {mag}"


def surd_floor(x: QuadraticSurd) -> int:
    """Exact floor of a quadratic surd — no floating point anywhere.

    Rewrites ``a + b*sqrt(D)`` as ``(P + sign(b)*sqrt(b^2 D)) / L`` over a
    common denominator ``L`` and delegates to the integer floor routine that
    powers the PQa expansion. This is the safe doorway for every expansion
    algorithm that needs ``floor(1/x)`` of an exact irrational: a floating
    floor is off by one exactly when it matters most (values a hair below an
    integer), and an off-by-one floor makes greedy expansions diverge.

    >>> surd_floor(QuadraticSurd.make(0, 1, 2))          # sqrt(2)
    1
    >>> surd_floor(QuadraticSurd.from_pqd(1, 5, 2))      # golden ratio
    1
    >>> surd_floor(QuadraticSurd.make(0, -1, 2))         # -sqrt(2)
    -2
    >>> surd_floor(QuadraticSurd.make(Fraction(7, 2), 0, 1))
    3
    """
    if x.b == 0:
        return math.floor(x.a)
    # Local import: expand builds on nothing from this module, but keeping the
    # dependency out of module load preserves the core -> doorways layering.
    from .expand import _floor_quad

    L = math.lcm(x.a.denominator, x.b.denominator)
    P = int(x.a * L)
    B = int(x.b * L)
    D2 = B * B * x.D
    if B > 0:
        return _floor_quad(P, D2, L)
    # a + b*sqrt(D) = (P - sqrt(D2)) / L = (-P + sqrt(D2)) / (-L)
    return _floor_quad(-P, D2, -L)


# --------------------------------------------------------------------------- #
#  Convergent bookkeeping used by CF.value() (kept local to avoid an import
#  cycle with the convergents module, which itself builds on CF).
# --------------------------------------------------------------------------- #

def _convergent_matrix(terms: Sequence[int]) -> tuple[int, int, int, int]:
    """Fold ``terms`` into ``(h_last, h_prev, k_last, k_prev)``.

    These are the numerator/denominator of the last two convergents, i.e. the
    entries of the product of matrices ``[[a_i, 1], [1, 0]]``.
    """
    h_prev, h_prev2 = 1, 0
    k_prev, k_prev2 = 0, 1
    for a in terms:
        h_prev, h_prev2 = a * h_prev + h_prev2, h_prev
        k_prev, k_prev2 = a * k_prev + k_prev2, k_prev
    return h_prev, h_prev2, k_prev, k_prev2


# --------------------------------------------------------------------------- #
#  The CF object.
# --------------------------------------------------------------------------- #

class CF:
    """A simple continued fraction as a re-iterable, lazily-cached term stream.

    Construct one with a classmethod rather than the raw initializer:

    >>> CF.from_fraction(Fraction(415, 93)).terms(10)
    [4, 2, 6, 7]
    >>> str(CF.from_quadratic(0, 2, 1))       # sqrt(2)
    '[1; (2)]'
    >>> CF.periodic([], [1]).value()          # golden ratio
    QuadraticSurd(a=Fraction(1, 2), b=Fraction(1, 2), D=5)
    """

    def __init__(
        self,
        source: Callable[[], Iterator[int]],
        *,
        kind: CFKind = CFKind.UNKNOWN,
        preperiod: Sequence[int] | None = None,
        period: Sequence[int] | None = None,
        surd: tuple[int, int, int] | None = None,
    ) -> None:
        self._source = source
        self._it: Iterator[int] | None = None
        self._cache: list[int] = []
        self._exhausted = False
        self._kind = kind
        self._preperiod = list(preperiod) if preperiod is not None else None
        self._period = list(period) if period is not None else None
        # When known, the exact value (P + sqrt(D)) / Q of a periodic CF. Lets
        # value() return the surd directly instead of re-deriving it from the
        # period (which produces needlessly huge discriminants to factor).
        self._surd = surd

    # -- construction ------------------------------------------------------- #

    @classmethod
    def from_stream(
        cls,
        factory: Callable[[], Iterator[int]],
        *,
        kind: CFKind = CFKind.UNKNOWN,
        preperiod: Sequence[int] | None = None,
        period: Sequence[int] | None = None,
    ) -> "CF":
        """Wrap a factory producing a fresh partial-quotient iterator."""
        return cls(factory, kind=kind, preperiod=preperiod, period=period)

    @classmethod
    def from_terms(cls, terms, *, kind: CFKind | None = None) -> "CF":
        """Snapshot an explicit (finite) iterable of partial quotients."""
        snap = tuple(terms)
        return cls(lambda: iter(snap), kind=kind or CFKind.FINITE)

    @classmethod
    def from_fraction(cls, x: Fraction | int) -> "CF":
        """The finite continued fraction of a rational number."""
        from .expand import cf_from_fraction

        snap = tuple(cf_from_fraction(Fraction(x)))
        return cls(lambda: iter(snap), kind=CFKind.FINITE)

    @classmethod
    def from_quadratic(cls, P: int, D: int, Q: int) -> "CF":
        """The continued fraction of ``(P + sqrt(D)) / Q``.

        Periodic when ``D`` is not a perfect square, finite otherwise.
        """
        from .expand import cf_from_quadratic

        pre, per = cf_from_quadratic(P, D, Q)
        if not per:
            return cls.from_terms(pre, kind=CFKind.FINITE)

        def factory() -> Iterator[int]:
            yield from pre
            while True:
                yield from per

        return cls(factory, kind=CFKind.PERIODIC, preperiod=pre, period=per,
                   surd=(P, D, Q))

    @classmethod
    def periodic(cls, preperiod: Sequence[int], period: Sequence[int]) -> "CF":
        """An eventually-periodic continued fraction from its pre-period/period."""
        pre = list(preperiod)
        per = list(period)
        if not per:
            return cls.from_terms(pre, kind=CFKind.FINITE)

        def factory() -> Iterator[int]:
            yield from pre
            while True:
                yield from per

        return cls(factory, kind=CFKind.PERIODIC, preperiod=pre, period=per)

    @classmethod
    def from_real(cls, produce_interval) -> "CF":
        """A lazy continued fraction of a real given a rigorous interval oracle.

        ``produce_interval(precision)`` must return a ``(lo, hi)`` pair of
        Fractions bracketing the value, tightening as ``precision`` grows.
        """
        from .expand import cf_from_interval

        return cls(lambda: cf_from_interval(produce_interval), kind=CFKind.UNKNOWN)

    # -- iteration ---------------------------------------------------------- #

    def _ensure(self, n: int) -> None:
        """Advance the underlying iterator until the cache holds ``n`` terms."""
        if self._it is None and not self._exhausted:
            self._it = self._source()
        while not self._exhausted and len(self._cache) < n:
            try:
                self._cache.append(next(self._it))  # type: ignore[arg-type]
            except StopIteration:
                self._exhausted = True

    def __iter__(self) -> Iterator[int]:
        i = 0
        while True:
            self._ensure(i + 1)
            if i < len(self._cache):
                yield self._cache[i]
                i += 1
            else:
                return

    def terms(self, n: int) -> list[int]:
        """The first ``n`` partial quotients (fewer if the CF is shorter)."""
        self._ensure(n)
        return self._cache[:n]

    def head(self, n: int) -> list[int]:
        """Up to ``n`` partial quotients; never raises."""
        return self.terms(n)

    # -- metadata ----------------------------------------------------------- #

    @property
    def kind(self) -> CFKind:
        return self._kind

    @property
    def period(self) -> list[int] | None:
        return list(self._period) if self._period is not None else None

    @property
    def preperiod(self) -> list[int] | None:
        return list(self._preperiod) if self._preperiod is not None else None

    def is_finite(self) -> bool | None:
        """``True``/``False`` when known, ``None`` for a genuinely open stream."""
        if self._kind is CFKind.FINITE:
            return True
        if self._kind in (CFKind.PERIODIC, CFKind.INFINITE):
            return False
        return None

    # -- evaluation --------------------------------------------------------- #

    def convergents(self) -> Iterator[Fraction]:
        """Successive convergents ``h_n / k_n`` as exact Fractions."""
        from .convergents import recurrence

        return recurrence(iter(self))

    def approx(self, terms: int = 40) -> Fraction:
        """The convergent after ``terms`` partial quotients (works for any kind)."""
        from .convergents import recurrence

        result = Fraction(0)
        for i, c in enumerate(recurrence(self.terms(terms))):
            result = c
            if i + 1 >= terms:
                break
        return result

    def value(self) -> Fraction | QuadraticSurd:
        """The exact value: ``Fraction`` if finite, ``QuadraticSurd`` if periodic.

        Raises for genuinely infinite/unknown streams — use :meth:`approx`.
        """
        if self._kind is CFKind.FINITE:
            *_, last = self.convergents()
            return last
        if self._kind is CFKind.PERIODIC:
            if self._surd is not None:
                return QuadraticSurd.from_pqd(*self._surd)
            return self._periodic_value()
        raise ValueError(
            "an infinite / unknown continued fraction has no exact finite value; "
            "use .approx(terms) for a rational approximation"
        )

    def _periodic_value(self) -> QuadraticSurd:
        assert self._period is not None
        pre = self._preperiod or []
        per = self._period
        # Pure-period tail t satisfies t = (H t + H') / (K t + K'):
        h1, h0, k1, k0 = _convergent_matrix(per)
        A = k1
        B = k0 - h1
        C = -h0
        disc = B * B - 4 * A * C
        # Positive root t = (-B + sqrt(disc)) / (2A); t > 1 for a valid CF tail.
        tail = QuadraticSurd.from_pqd(-B, disc, 2 * A)
        if float(tail) < 0:  # pick the branch that lands above 1
            tail = QuadraticSurd.from_pqd(-B, disc, 2 * A).conjugate()
        if not pre:
            return tail
        H1, H0, K1, K0 = _convergent_matrix(pre)
        return tail.homographic(H1, H0, K1, K0)

    # -- display ------------------------------------------------------------ #

    def __str__(self) -> str:
        if self._period is not None:
            return cf_to_str(self._preperiod or [], period=self._period)
        if self._kind is CFKind.FINITE:
            return cf_to_str(self.terms(1_000_000))
        head = self.terms(_DISPLAY_TERMS)
        return cf_to_str(head, truncated=True)

    def __repr__(self) -> str:
        return f"CF({self})"
