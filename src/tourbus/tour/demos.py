"""Single-shot demonstrations reachable via ``tourbus demo <name> [args]``.

Each demo is a small function that computes something live and prints it. They
share the tour's rendering helpers but stand alone, so ``tourbus demo pell 61``
works without walking the whole tour.
"""

from __future__ import annotations

import random
from fractions import Fraction

from .termio import Console
from . import render
from ..cf.core import CF
from ..cf.constants import sqrt_cf, pi_cf, e_cf, phi_cf
from ..cf.convergents import convergent_pairs


def _flag(args, name, default=None, cast=str):
    """Pull ``--name value`` out of an arg list; returns (value, remaining)."""
    args = list(args)
    if name in args:
        i = args.index(name)
        try:
            val = cast(args[i + 1])
            del args[i:i + 2]
            return val, args
        except (IndexError, ValueError):
            del args[i:i + 1]
    return default, args


def demo_cf(c: Console, args) -> int:
    from .stops import _number_to_cf, _convergents_table

    target = args[0] if args else "pi"
    try:
        label, cf = _number_to_cf(target)
    except (ValueError, ZeroDivisionError):
        c.emit(c.style(f"could not parse {target!r}", "warn"))
        return 1
    c.emit(c.style(f"continued fraction of {label}:", "title"))
    c.emit("  " + c.style(str(cf), "result"))
    c.emit()
    c.emit(_convergents_table(c, cf, 8))
    return 0


def demo_euclid(c: Console, args) -> int:
    from .stops import _euclid_trace

    if len(args) < 2:
        c.emit(c.style("usage: demo euclid A B", "warn"))
        return 1
    a, b = int(args[0]), int(args[1])
    for line in _euclid_trace(max(a, b), min(a, b)):
        c.emit("  " + c.style(line, "result"))
    c.emit("  " + c.style("continued fraction = " + str(CF.from_fraction(Fraction(a, b))),
                          "success"))
    return 0


def demo_pell(c: Console, args) -> int:
    from ..numbertheory.pell import fundamental_solution

    d = int(args[0]) if args else 61
    sol = fundamental_solution(d, 1)
    if sol is None:
        c.emit(c.style(f"d = {d} has no nontrivial Pell solution (a perfect square?)", "warn"))
        return 0
    c.emit(c.style(f"x^2 - {d} y^2 = 1  fundamental solution:", "title"))
    c.emit("  " + c.style(f"x = {sol.x}", "result"))
    c.emit("  " + c.style(f"y = {sol.y}", "result"))
    c.emit("  " + c.style(f"verifies: {sol.verify(1)}", "success"))
    return 0


def demo_stern_brocot(c: Console, args) -> int:
    from ..numbertheory import stern_brocot as sb

    target = args[0] if args else "355/113"
    p, q = target.split("/")
    frac = Fraction(int(p), int(q))
    path = sb.rational_to_path(frac)
    c.emit(c.style(f"Stern-Brocot address of {frac}:", "title"))
    c.emit("  " + c.style(path or "(root)", "result"))
    c.emit("  " + c.style(f"round-trips to {sb.path_to_rational(path)}", "success"))
    return 0


def demo_gauss(c: Console, args) -> int:
    from ..dynamics import gauss

    seed, args = _flag(args, "--seed", 0, int)
    rng = random.Random(seed)
    terms = []
    for _ in range(200):
        terms.extend(CF.from_fraction(Fraction(rng.getrandbits(48) + 1, 1 << 48)).terms(25)[1:])
    emp = gauss.kuzmin_empirical(terms, max_bucket=6)
    pred = {k: gauss.kuzmin_theoretical(k) for k in range(1, 7)}
    c.emit(c.style("Gauss-Kuzmin digit frequencies (observed vs predicted):", "title"))
    c.emit(render.histogram(emp, console=c, predicted=pred))
    return 0


def demo_khinchin(c: Console, args) -> int:
    from ..dynamics import gauss

    n, args = _flag(args, "--samples", 500, int)
    seed, args = _flag(args, "--seed", 0, int)
    rng = random.Random(seed)
    terms = []
    for _ in range(n):
        terms.extend(CF.from_fraction(Fraction(rng.getrandbits(48) + 1, 1 << 48)).terms(25)[1:])
    est = gauss.khinchin_estimate(terms)
    c.emit(c.style(f"geometric mean of {len(terms)} partial quotients:", "title"))
    c.emit("  " + c.style(f"{est:.5f}   (Khinchin's constant = 2.68545...)", "result"))
    return 0


def demo_gosper(c: Console, args) -> int:
    from ..cf import gosper

    op, args = _flag(args, "--op", "add", str)
    names = args or ["sqrt2", "sqrt3"]
    from .stops import _number_to_cf

    xs = [_number_to_cf(n)[1] for n in names[:2]]
    fn = {"add": gosper.add, "sub": gosper.sub, "mul": gosper.mul, "div": gosper.div}[op]
    result = fn(xs[0], xs[1])
    c.emit(c.style(f"{names[0]} {op} {names[1]} (as a continued fraction):", "title"))
    c.emit("  " + c.style(str(result.terms(12)), "result"))
    return 0


def demo_ackermann(c: Console, args) -> int:
    from ..recursion.classics import ackermann

    m = int(args[0]) if args else 3
    n = int(args[1]) if len(args) > 1 else 4
    if m >= 4 and n >= 2:
        c.emit(c.style("A(4,2) = 2^65536 - 3 has 19729 digits; refusing to print it all.",
                       "warn"))
        return 0
    c.emit(c.style(f"A({m}, {n}) = {ackermann(m, n)}", "result"))
    return 0


def _fractal_demo(name):
    def run(c: Console, args) -> int:
        from .. import fractals

        depth, args = _flag(args, "--depth", 4, int)
        fn = getattr(fractals, name)
        svg = fn(depth)
        c.emit(c.style(f"{name}(depth={depth}) -> {len(svg)} bytes of SVG", "title"))
        c.emit("  " + c.style("(open site/index.html for the drawn version)", "chrome"))
        return 0
    return run


def demo_calendar(c: Console, args) -> int:
    from ..applications import calendar as cal

    c.emit(c.style("Leap-year rules from the convergents of 0.2422:", "title"))
    rows = [[f"{f.numerator}/{f.denominator}", f"{float(f):.6f}", cal.leap_rule_description(f)]
            for f in cal.tropical_year_convergents(max_denominator=500)]
    c.emit(render.table(["rule", "value", "meaning"], rows, console=c))
    return 0


def demo_temperament(c: Console, args) -> int:
    from ..applications import music

    c.emit(c.style("Equal temperament from convergents of log2(3/2):", "title"))
    rows = [[f"{f.numerator}/{f.denominator}", f.denominator, f"{music.cents_error(f):+.3f}"]
            for f in music.equal_temperament_convergents()]
    c.emit(render.table(["convergent", "notes/octave", "fifth error (cents)"],
                        rows, console=c, right_align=[1, 2]))
    return 0


def demo_wiener(c: Console, args) -> int:
    from ..applications.wiener import make_vulnerable_key, wiener_attack

    bits, args = _flag(args, "--bits", 128, int)
    seed, args = _flag(args, "--seed", 7, int)
    key = make_vulnerable_key(bits, rng=random.Random(seed))
    recovered = wiener_attack(key.e, key.n)
    c.emit(c.style(f"vulnerable RSA key ({bits}-bit):", "title"))
    c.emit("  " + c.style(f"n = {key.n}", "chrome"))
    c.emit("  " + c.style(f"e = {key.e}", "chrome"))
    c.emit("  " + c.style(f"recovered d = {recovered} (true d = {key.d})", "result"))
    c.emit("  " + c.style("attack succeeded" if recovered == key.d else "attack failed",
                          "success" if recovered == key.d else "warn"))
    return 0


def demo_collatz(c: Console, args) -> int:
    from ..applications import collatz

    n = int(args[0]) if args else 27
    stats = collatz.collatz_stats(n)
    c.emit(c.style(f"Collatz flight of {n}:", "title"))
    c.emit("  " + c.style(f"{stats['steps']} steps, peak {stats['max']}", "result"))
    return 0


# -- Express Line (frontier) demos ------------------------------------------ #

def demo_markov(c: Console, args) -> int:
    from ..frontier import markov as M

    c.emit(c.style("The Markov / Lagrange spectrum below 3:", "title"))
    rows = [[m, str(M.lagrange_number(m)), f"{float(M.lagrange_number(m)):.6f}"]
            for m in M.markov_numbers(200)]
    c.emit(render.table(["Markov m", "L_m", "value"], rows, console=c, right_align=[0, 2]))
    return 0


def demo_continuant(c: Console, args) -> int:
    from ..frontier import continuants as K

    seq = [int(a) for a in args] if args else [1, 2, 3, 4, 5]
    c.emit(c.style(f"Continuant K{tuple(seq)}:", "title"))
    c.emit("  " + c.style(f"recurrence = {K.continuant(seq)}", "result"))
    c.emit("  " + c.style(f"Euler rule = {K.continuant_euler(seq)}", "result"))
    c.emit("  " + c.style(f"reversed   = K{tuple(reversed(seq))} = {K.continuant(list(reversed(seq)))} (equal)", "chrome"))
    return 0


def demo_cbrt(c: Console, args) -> int:
    from ..frontier import algebraic as A

    n = int(args[0]) if args else 2
    cf = A.cube_root_cf(n, digits=90)
    c.emit(c.style(f"Continued fraction of {n}^(1/3):", "title"))
    c.emit("  " + c.style(str(cf.terms(16)) + " ...", "result"))
    s = A.partial_quotient_stats(cf, 40)
    c.emit("  " + c.style(f"max term {s['max']}, geometric mean {s['geometric_mean']:.3f} "
                          "(Khinchin-typical; boundedness OPEN)", "chrome"))
    return 0


def demo_plastic(c: Console, args) -> int:
    from ..frontier import algebraic as A

    c.emit(c.style("The plastic number (x^3 = x + 1):", "title"))
    c.emit("  " + c.style(str(A.plastic_number_cf().terms(14)) + " ...", "result"))
    c.emit("  " + c.style("note the 141 at position 12 -- out of nowhere.", "chrome"))
    return 0


def demo_nicf(c: Console, args) -> int:
    from ..frontier import variants as V

    target = args[0] if args else "87/32"
    p, q = target.split("/") if "/" in target else (target, "1")
    x = Fraction(int(p), int(q))
    c.emit(c.style(f"Three continued fractions of {x}:", "title"))
    c.emit("  " + c.style(f"regular:         {V.regular_cf(x)}", "result"))
    c.emit("  " + c.style(f"nearest-integer: {V.nearest_integer_cf(x)}", "result"))
    c.emit("  " + c.style(f"minus (a>=2):    {V.minus_cf(x)}", "result"))
    return 0


def demo_three_distance(c: Console, args) -> int:
    from ..frontier import three_distance as T

    alpha = Fraction(args[0]) if args else Fraction(8, 13)
    n = int(args[1]) if len(args) > 1 else 12
    rep = T.three_distance_report(alpha, n)
    c.emit(c.style(f"Three-distance theorem for a={alpha}, N={n}:", "title"))
    c.emit("  " + c.style(f"{rep['num_distinct']} distinct gap lengths: "
                          + ", ".join(str(g) for g in rep["distinct_lengths"]), "result"))
    c.emit("  " + c.style(f"largest = sum of the others: {rep['largest_is_sum']}", "chrome"))
    return 0


def demo_gkw(c: Console, args) -> int:
    from ..frontier import gkw

    c.emit(c.style("Gauss-Kuzmin-Wirsing constant (from the transfer operator):", "title"))
    lam = gkw.second_eigenvalue(grid=280, terms=1500, iters=70)
    c.emit("  " + c.style(f"computed  lambda = {lam:.7f}", "result"))
    c.emit("  " + c.style(f"Wirsing's value  = {gkw.GKW_CONSTANT:.7f} "
                          f"(error {abs(lam - gkw.GKW_CONSTANT):.1e})", "chrome"))
    return 0


def demo_blocks(c: Console, args) -> int:
    from ..frontier import physics as P

    up_to = int(args[0]) if args else 5
    up_to = max(0, min(up_to, 12))
    c.emit(c.style("Galperin's colliding blocks: physics counts the digits of pi", "title"))
    rows = []
    for n in range(up_to + 1):
        sim = P.galperin_collisions(n) if n <= 6 else None
        exact = P.pi_prefix(n)
        rows.append([f"100^{n}", str(sim) if sim is not None else "-", str(exact)])
    c.emit(render.table(["mass ratio", "collisions (sim)", "digits of pi"],
                        rows, console=c, right_align=[1, 2]))
    c.emit("  " + c.style("two elastic blocks, count every collision -> the digits of pi.",
                          "chrome"))
    return 0


# -- Cross-Domain Line demos ------------------------------------------------ #

def demo_huckel(c: Console, args) -> int:
    from ..crossdomain import huckel as H

    n = int(args[0]) if args else 6
    c.emit(c.style(f"Huckel MO energies of the C{n} annulene (units of beta):", "title"))
    c.emit("  " + c.style(str([round(e, 4) for e in H.annulene_energies(n)]), "result"))
    c.emit("  " + c.style(f"verdict: {H.is_aromatic(n, n)} (Huckel 4n+2 rule)", "chrome"))
    return 0


def demo_dos(c: Console, args) -> int:
    from ..crossdomain import recursion_method as RM
    from fractions import Fraction

    n = int(args[0]) if args else 4
    a, b2 = RM.lanczos_coefficients(RM.chain_hamiltonian(n), 0)
    c.emit(c.style(f"Green's function of a {n}-site chain as a continued fraction:", "title"))
    c.emit("  " + c.style(f"Lanczos a = {[str(x) for x in a]}", "result"))
    c.emit("  " + c.style(f"        b^2 = {[str(x) for x in b2]}", "result"))
    c.emit("  " + c.style(f"eigenvalue poles = "
                          f"{sorted(round(float(p),4) for p in RM.spectral_poles(a,b2))}", "result"))
    return 0


def demo_butterfly(c: Console, args) -> int:
    from ..crossdomain import hofstadter as HF

    c.emit(c.style("Hofstadter butterfly: bands vs magnetic flux p/q", "title"))
    rows = []
    for q in range(2, 8):
        for p in range(1, q):
            from math import gcd
            if gcd(p, q) == 1:
                rows.append([f"{p}/{q}", len(HF.harper_bands(p, q))])
    c.emit(render.table(["flux", "bands"], rows, console=c, right_align=[1]))
    c.emit("  " + c.style("flux 1/2: Delta(E)=E^2-4, edges +/-2sqrt2; the spectrum is fractal.",
                          "chrome"))
    return 0


def demo_staircase(c: Console, args) -> int:
    from ..crossdomain import circle_map as CM

    c.emit(c.style("Circle map: winding numbers lock onto rationals (K=1)", "title"))
    rows = [[f"{Om:.2f}", f"{CM.winding_number(Om, 1.0):.4f}"]
            for Om in (0.0, 0.15, 0.33, 0.5, 0.66, 0.85, 1.0)]
    c.emit(render.table(["drive Omega", "winding number"], rows, console=c, right_align=[1]))
    c.emit("  " + c.style(f"the 0/1 tongue has width {CM.tongue_width(0,1,1.0):.4f} = 1/pi.", "chrome"))
    return 0


def demo_feigenbaum(c: Console, args) -> int:
    from ..crossdomain import feigenbaum as FB

    c.emit(c.style("Feigenbaum: period doubling and universality", "title"))
    ladder = FB.superstable_ladder(5)
    c.emit("  " + c.style(f"superstable parameters R_n = {[round(r,5) for r in ladder]}", "result"))
    c.emit("  " + c.style(f"delta ~ {FB.feigenbaum_delta(5):.5f}  "
                          f"(Feigenbaum {FB.FEIGENBAUM_DELTA:.5f})", "result"))
    return 0


def demo_cauer(c: Console, args) -> int:
    from ..crossdomain import cauer

    c.emit(c.style("Cauer ladder synthesis of Z(s) = (24s^3+6s)/(12s^2+1):", "title"))
    el = cauer.cauer_ladder([24, 0, 6, 0], [12, 0, 1])
    c.emit("  " + c.style(f"element values = {[str(x) for x in el]}  (L1, C1, L2, ...)", "result"))
    return 0


def demo_routh(c: Console, args) -> int:
    from ..crossdomain import routh

    c.emit(c.style("Routh-Hurwitz stability as a continued fraction:", "title"))
    for p in ([1, 1, 1], [1, 2, 2, 1], [1, 2, 2, 40], [1, 0, 1]):
        verdict = "stable" if routh.is_hurwitz_stable(p) else "UNSTABLE"
        c.emit("  " + c.style(f"{p}: quotients {[str(q) for q in routh.routh_cf(p)]} -> {verdict}",
                              "result"))
    return 0


def demo_pade(c: Console, args) -> int:
    from ..crossdomain import pade
    from math import factorial
    from fractions import Fraction

    exp = [Fraction(1, factorial(k)) for k in range(9)]
    c.emit(c.style("Pade resummation of e^x from its C-fraction:", "title"))
    c.emit("  " + c.style(f"C-fraction coeffs = {[str(a) for a in pade.series_to_cfrac(exp)]}",
                          "result"))
    num, den = pade.pade(exp, 2, 2)
    c.emit("  " + c.style(f"[2/2] Pade num={[str(x) for x in num]} den={[str(x) for x in den]}",
                          "result"))
    return 0


def demo_phyllotaxis(c: Console, args) -> int:
    from ..crossdomain import phyllotaxis as PH

    c.emit(c.style("Phyllotaxis: the golden angle in plants", "title"))
    c.emit("  " + c.style(f"golden angle = {PH.golden_angle_degrees():.5f} degrees", "result"))
    for n in (200, 400, 600):
        c.emit("  " + c.style(f"n={n} seeds -> parastichy spirals {PH.parastichy_counts(n)} "
                              "(consecutive Fibonacci)", "result"))
    return 0


def demo_apery(c: Console, args) -> int:
    from ..crossdomain import apery

    c.emit(c.style("Apery: recursion proves zeta(3) irrational", "title"))
    a, b = apery.apery_sequences(6)
    c.emit("  " + c.style(f"integer sequence a_n = {[int(x) for x in a]}", "result"))
    c.emit("  " + c.style(f"b_n/a_n -> {float(apery.apery_zeta3_bounds(8)[-1])} = zeta(3)", "result"))
    return 0


def demo_quasicrystal(c: Console, args) -> int:
    from ..crossdomain import fibonacci_chain as FC

    c.emit(c.style("The Fibonacci quasicrystal:", "title"))
    for k in range(6):
        c.emit("  " + c.style(f"inflation {k}: {FC.fibonacci_word(k)}", "result"))
    c.emit("  " + c.style(f"brightest diffraction peaks: {[t[:2] for t in FC.fibonacci_peak_ladder(5)]}"
                          " = golden-ratio convergents", "chrome"))
    return 0


DEMOS = {
    "cf": ("expand a number's continued fraction", demo_cf),
    "euclid": ("trace Euclid's algorithm on two integers", demo_euclid),
    "pell": ("solve x^2 - d y^2 = 1", demo_pell),
    "stern-brocot": ("find a fraction's address in the tree", demo_stern_brocot),
    "gauss": ("Gauss-Kuzmin digit statistics", demo_gauss),
    "khinchin": ("estimate Khinchin's constant", demo_khinchin),
    "gosper": ("exact stream arithmetic (--op add|sub|mul|div)", demo_gosper),
    "ackermann": ("evaluate the Ackermann function", demo_ackermann),
    "koch": ("Koch curve SVG (--depth)", _fractal_demo("koch")),
    "dragon": ("dragon curve SVG (--depth)", _fractal_demo("dragon")),
    "hilbert": ("Hilbert curve SVG (--depth)", _fractal_demo("hilbert")),
    "sierpinski": ("Sierpinski arrowhead SVG (--depth)", _fractal_demo("sierpinski_arrowhead")),
    "calendar": ("leap-year rules from continued fractions", demo_calendar),
    "temperament": ("musical equal temperament", demo_temperament),
    "wiener": ("break a weak RSA key (--bits)", demo_wiener),
    "collatz": ("Collatz orbit statistics", demo_collatz),
    # --- Express Line (fringe topics) ---
    "markov": ("the Markov / Lagrange spectrum below 3", demo_markov),
    "continuant": ("continuant polynomial K(a1,...,an)", demo_continuant),
    "cbrt": ("continued fraction of a cube root (open problem)", demo_cbrt),
    "plastic": ("the plastic number's continued fraction", demo_plastic),
    "nicf": ("nearest-integer & minus continued fractions", demo_nicf),
    "three-distance": ("the three-distance theorem", demo_three_distance),
    "gkw": ("the Gauss-Kuzmin-Wirsing constant from scratch", demo_gkw),
    "blocks": ("colliding blocks that count the digits of pi", demo_blocks),
    # --- Cross-Domain Line (the sciences) ---
    "huckel": ("Huckel MO energies = a continuant (chemistry)", demo_huckel),
    "dos": ("density of states as a continued fraction (condensed matter)", demo_dos),
    "butterfly": ("the Hofstadter butterfly's bands (spectra)", demo_butterfly),
    "staircase": ("circle-map mode-locking / devil's staircase (dynamics)", demo_staircase),
    "feigenbaum": ("the Feigenbaum constant from period doubling", demo_feigenbaum),
    "cauer": ("synthesize an LC ladder from an impedance (engineering)", demo_cauer),
    "routh": ("Routh-Hurwitz stability as a continued fraction (control)", demo_routh),
    "pade": ("Pade resummation of a series (analysis)", demo_pade),
    "phyllotaxis": ("the golden angle in plants (biology)", demo_phyllotaxis),
    "apery": ("Apery's proof that zeta(3) is irrational", demo_apery),
    "quasicrystal": ("the Fibonacci quasicrystal (materials)", demo_quasicrystal),
}


def list_demos(console: Console) -> None:
    console.emit(console.style("Available demos:", "title"))
    for name, (help_text, _) in DEMOS.items():
        console.emit(f"  {console.style(name.ljust(14), 'result')} {help_text}")
    console.emit()
    console.emit(console.style("example: python -m tourbus demo pell 61", "chrome"))


def run_demo(console: Console, name: str, args) -> int:
    if name not in DEMOS:
        console.emit(console.style(f"unknown demo {name!r}; try 'demo --list'", "warn"))
        return 1
    _, fn = DEMOS[name]
    # Global valueless flags may land in the demo's args via REMAINDER capture
    # (e.g. `demo huckel --no-color`); drop them so demos see only their own args.
    _GLOBAL = {"--no-color", "--color", "--ascii", "--fast"}
    args = [a for a in args if a not in _GLOBAL]
    try:
        return fn(console, list(args))
    except Exception as exc:  # keep the CLI robust for any single demo
        console.emit(console.style(f"demo error: {exc}", "warn"))
        return 1
