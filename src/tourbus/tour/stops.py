"""The fifteen stops — narrative plus live-computed demonstrations.

Every stop is a function ``stop_NN(console)`` that prints its body. The stops
import the mathematical engine lazily so that a single incomplete subpackage
never breaks the whole tour, and they perform their computations live: the
numbers you read were produced on the spot by the same functions the test suite
exercises.
"""

from __future__ import annotations

from fractions import Fraction

from .termio import Console
from . import render

# The cf core is always available; leaf packages are imported inside each stop.
from ..cf.core import CF
from ..cf.constants import phi_cf, sqrt_cf, e_cf, pi_cf, pi_cf_via_gcf
from ..cf.convergents import convergent_pairs


# --------------------------------------------------------------------------- #
#  Small shared helpers.
# --------------------------------------------------------------------------- #

def _narr(c: Console, text: str) -> None:
    c.paragraph(text)
    c.emit()


def _subhead(c: Console, text: str) -> None:
    render.subhead(c, text)


def _souvenir(c: Console, text: str) -> None:
    render.souvenir(c, text)


def _number_to_cf(text: str):
    """Parse user input into ``(label, CF)``; raises ValueError on nonsense."""
    t = text.strip().lower()
    if t in ("phi", "golden", "φ"):
        return "phi", phi_cf()
    if t == "pi":
        return "pi", pi_cf()
    if t == "e":
        return "e", e_cf()
    if t.startswith("sqrt"):
        n = int(t[4:].lstrip("(").rstrip(")"))
        return f"sqrt({n})", sqrt_cf(n)
    if "/" in t:
        p, q = t.split("/")
        f = Fraction(int(p), int(q))
        return str(f), CF.from_fraction(f)
    f = Fraction(t)  # accepts decimal strings
    return t, CF.from_fraction(f)


def _ref_float(cf: CF) -> float:
    try:
        v = cf.value()
        return float(v)
    except ValueError:
        return float(cf.approx(30))


def _convergents_table(c: Console, cf: CF, n_terms: int, *, highlight_last=False) -> str:
    terms = cf.terms(n_terms)
    ref = _ref_float(cf)
    rows = []
    hi = None
    for n, (h, k) in enumerate(convergent_pairs(terms)):
        val = h / k
        err = ref - val
        rows.append([n, terms[n], f"{h}/{k}", f"{val:.10f}", f"{err:+.2e}"])
    if highlight_last and rows:
        hi = len(rows) - 1
    return render.table(
        ["n", "a_n", "p/q", "value", "error"], rows,
        console=c, highlight=hi, right_align=[0, 1, 3, 4],
    )


def _euclid_trace(a: int, b: int) -> list[str]:
    lines = []
    while b:
        q, r = divmod(a, b)
        lines.append(f"{a} = {q} x {b} + {r}")
        a, b = b, r
    return lines


def _cf_str(terms, truncated: bool = True) -> str:
    """Render partial quotients as ``[a0; a1, a2, ...]`` with a trailing ellipsis."""
    terms = list(terms)
    if not terms:
        return "[]"
    tail = ", ".join(str(t) for t in terms[1:])
    ell = ", ..." if truncated else ""
    if tail:
        return f"[{terms[0]}; {tail}{ell}]"
    return f"[{terms[0]}{'; ...' if truncated else ''}]"


# --------------------------------------------------------------------------- #
#  Stop 1 — The Depot.
# --------------------------------------------------------------------------- #

def stop_01_depot(c: Console) -> None:
    _narr(c, "Around 300 BC, Euclid wrote down a way to find the greatest common "
             "divisor of two numbers by repeatedly replacing the larger with its "
             "remainder against the smaller. It is a recursion: gcd(a, 0) = a, and "
             "gcd(a, b) = gcd(b, a mod b). It still runs, unchanged, inside every "
             "computer today.")
    _subhead(c, "Live: gcd(1071, 462)")
    for line in _euclid_trace(1071, 462):
        c.emit("   " + c.style(line, "result"))
    c.emit("   " + c.style("gcd = 21, quotients [2, 3, 7]", "success"))
    c.emit()
    _narr(c, "How slow can it get? Gabriel Lame proved in 1844 that the worst case "
             "is a pair of consecutive Fibonacci numbers -- the first appearance of "
             "the Fibonaccis in the analysis of an algorithm.")
    _subhead(c, "Live: worst case gcd(F16, F15) = gcd(987, 610)")
    trace = _euclid_trace(987, 610)
    c.emit("   " + c.style(f"{len(trace)} steps, every quotient equal to 1", "result"))
    c.emit()

    _try_number(c, "Enter two numbers 'a b' (or one number for its CF)", "48 18")
    c.emit()
    _souvenir(c, "Keep Euclid's quotients instead of discarding them, and the next "
                 "stop begins.")


def _try_number(c: Console, prompt: str, default: str):
    """Prompt for a number or 'a b' pair; echo a gcd trace or CF. Returns None."""
    raw = c.ask(prompt, default, parse=str)
    parts = raw.split()
    if len(parts) == 2 and all(p.lstrip("-").isdigit() for p in parts):
        a, b = int(parts[0]), int(parts[1])
        if b != 0 or a != 0:
            trace = _euclid_trace(max(abs(a), abs(b)), min(abs(a), abs(b)))
            for line in trace[:6]:
                c.emit("   " + c.style(line, "result"))
    else:
        try:
            label, cf = _number_to_cf(raw)
            c.emit("   " + c.style(f"{label} = ", "chrome")
                   + c.style(str(cf), "result"))
        except (ValueError, ZeroDivisionError):
            c.emit("   " + c.style("(could not parse that; try 415/93 or 3.14159)", "warn"))
    return None


# --------------------------------------------------------------------------- #
#  Stop 2 — The Unfolding Road.
# --------------------------------------------------------------------------- #

def stop_02_unfolding(c: Console) -> None:
    _narr(c, "A continued fraction writes a number as an integer plus one-over "
             "(an integer plus one-over (...)). We write it [a0; a1, a2, ...]. For a "
             "rational p/q the partial quotients are exactly the quotients Euclid "
             "produces -- the continued fraction IS Euclid on the reals.")
    _subhead(c, "Live: 415/93")
    for line in _euclid_trace(415, 93):
        c.emit("   " + c.style(line, "result"))
    cf = CF.from_fraction(Fraction(415, 93))
    c.emit("   " + c.style("continued fraction: " + str(cf), "success"))
    c.emit()
    c.emit(render.stacked_fraction(cf.terms(4), console=c))
    c.emit()
    _narr(c, "Fold it back up with exact fractions and you recover 415/93 exactly. "
             "A number's continued fraction is finite precisely when the number is "
             "rational; irrational numbers unfold forever.")
    _try_number(c, "Enter a number to expand (e.g. 3.14159, 22/7, sqrt2)", "2.71828")
    c.emit()
    _souvenir(c, "Rational <-> finite. Irrational <-> infinite. No exceptions.")


# --------------------------------------------------------------------------- #
#  Stop 3 — The Engine Room.
# --------------------------------------------------------------------------- #

def stop_03_engine(c: Console) -> None:
    _narr(c, "Truncate a continued fraction and you get a convergent p_n/q_n -- the "
             "best rational approximations there are. All of them come from one "
             "recurrence: p_n = a_n p_(n-1) + p_(n-2), and the same for q. Successive "
             "convergents satisfy p_n q_(n-1) - p_(n-1) q_n = (-1)^(n-1).")
    _subhead(c, "Live: convergents of pi")
    c.emit(_convergents_table(c, pi_cf(), 6, highlight_last=False))
    c.emit()
    p = pi_cf().terms(4)
    pairs = list(convergent_pairs(p))
    (h3, k3), (h2, k2) = pairs[3], pairs[2]
    c.emit("   " + c.style(
        f"determinant check: {h3}*{k2} - {h2}*{k3} = {h3*k2 - h2*k3}", "result"))
    c.emit("   " + c.style(
        "the huge partial quotient 292 is why 355/113 is so astonishingly good.", "chrome"))
    c.emit()
    _narr(c, "Because q_n grows at least like the Fibonacci numbers, the error "
             "|x - p_n/q_n| < 1/q_n^2 collapses exponentially fast.")
    _try_number(c, "Enter a number to see its convergents", "sqrt2")
    c.emit()
    _souvenir(c, "Every irrational has infinitely many p/q with |x - p/q| < 1/q^2.")


# --------------------------------------------------------------------------- #
#  Stop 4 — The Golden Milestone.
# --------------------------------------------------------------------------- #

def stop_04_golden(c: Console) -> None:
    _narr(c, "The golden ratio phi = (1+sqrt5)/2 satisfies phi = 1 + 1/phi, so its "
             "continued fraction is [1; 1, 1, 1, ...] -- nothing but ones. Its "
             "convergents are ratios of consecutive Fibonacci numbers.")
    _subhead(c, "Live: convergents of phi are Fibonacci ratios")
    rows = []
    for n, (h, k) in enumerate(convergent_pairs(phi_cf().terms(9))):
        q2err = k * k * abs(float(phi_cf().value()) - h / k)
        rows.append([n, f"{h}/{k}", f"{h/k:.8f}", f"{q2err:.5f}"])
    c.emit(render.table(["n", "F/F", "value", "q^2*err"], rows,
                        console=c, right_align=[0, 2, 3]))
    c.emit()
    _narr(c, "Small partial quotients mean slow convergence: q^2 times the error "
             "hovers at 1/sqrt5 ~ 0.4472 and never does better. Hurwitz proved in "
             "1891 that sqrt5 is the best possible constant, and phi is the number "
             "that achieves it -- the 'most irrational' number there is.")
    _subhead(c, "Live: how close do the convergents get? (q^2 * error)")
    demo = []
    for name, cf in [("phi", phi_cf()), ("sqrt2", sqrt_cf(2)), ("pi", pi_cf())]:
        ref = _ref_float(cf)
        vals = []
        for h, k in list(convergent_pairs(cf.terms(10)))[2:]:
            vals.append(k * k * abs(ref - h / k))
        demo.append((name, min(vals)))
    c.emit(render.hbars(demo, console=c))
    c.emit()
    _souvenir(c, "Sunflowers pack seeds at the golden angle precisely because phi "
                 "resists rational approximation better than any other number.")


# --------------------------------------------------------------------------- #
#  Stop 5 — Scenic Overlook.
# --------------------------------------------------------------------------- #

def stop_05_overlook(c: Console) -> None:
    from ..applications import calendar as cal
    from ..applications import gears

    _narr(c, "Every convergent is a best rational approximation, and that single "
             "theorem does a lot of engineering. The tropical year is about 365.2422 "
             "days; the convergents of 0.2422 are the great calendar reforms.")
    _subhead(c, "Live: leap-year rules from the convergents of 0.2422")
    rows = []
    for frac in cal.tropical_year_convergents(max_denominator=500):
        rows.append([f"{frac.numerator}/{frac.denominator}",
                     f"{float(frac):.6f}", cal.leap_rule_description(frac)])
    c.emit(render.table(["rule", "value", "meaning"], rows, console=c))
    greg = cal.GREGORIAN
    c.emit("   " + c.style(
        f"Gregorian {greg.numerator}/{greg.denominator} = {float(greg):.6f} is NOT a "
        "convergent -- accuracy traded for a tidy 400-year cycle.", "chrome"))
    c.emit()
    _subhead(c, "Live: Huygens' planetarium gear (Saturn/Earth ~ 29.43)")
    d, dn = gears.huygens_gear()
    c.emit("   " + c.style(f"best small gear pair: {d}/{dn} teeth", "result"))
    c.emit()
    _narr(c, "The same idea gives pi its famous approximations: 22/7 (Archimedes) "
             "and 355/113 (Zu Chongzhi, 5th century), unbeaten until denominators "
             "exceed 16,000.")
    _souvenir(c, "Legendre: if |x - p/q| < 1/(2q^2), then p/q must be a convergent.")


# --------------------------------------------------------------------------- #
#  Stop 6 — The Loop Road.
# --------------------------------------------------------------------------- #

def stop_06_loop(c: Console) -> None:
    from ..cf.expand import cf_from_quadratic

    _narr(c, "Which numbers have a continued fraction that eventually repeats? "
             "Lagrange proved the answer in 1770: exactly the quadratic irrationals, "
             "the roots of integer quadratics. It is the continued-fraction echo of "
             "'a decimal repeats exactly when the number is rational.'")
    _subhead(c, "Live: the period of sqrt(d)")
    rows = []
    for d in (2, 3, 7, 13, 23, 94):
        pre, per = cf_from_quadratic(0, d, 1)
        rows.append([d, str(sqrt_cf(d)), len(per)])
    c.emit(render.table(["d", "sqrt(d)", "period"], rows, console=c, right_align=[0, 2]))
    c.emit()
    _narr(c, "The period of sqrt(d) is always a palindrome that ends in twice the "
             "integer part. Small changes in d make wild changes in the period: "
             "sqrt(94) has period 16 while sqrt(95) has period 4.")
    raw = c.ask("Enter a non-square integer d for sqrt(d)", "61",
                parse=lambda s: int(s))
    try:
        d = int(raw)
        c.emit("   " + c.style(f"sqrt({d}) = {sqrt_cf(d)}", "result"))
    except (ValueError, TypeError):
        pass
    c.emit()
    _souvenir(c, "Periodic <-> quadratic. The metallic means [n; n, n, ...] are the "
                 "simplest examples, with phi the very first.")


# --------------------------------------------------------------------------- #
#  Stop 7 — The Cattle Crossing.
# --------------------------------------------------------------------------- #

def stop_07_pell(c: Console) -> None:
    from ..numbertheory.pell import fundamental_solution

    _narr(c, "Pell's equation asks for integers with x^2 - d*y^2 = 1. The convergents "
             "of sqrt(d) hand you the answer: the convergent at the end of the first "
             "period is the fundamental solution (up to a parity twist). Fermat threw "
             "d = 61 at his colleagues in 1657 as a taunt.")
    _subhead(c, "Live: fundamental solutions of x^2 - d*y^2 = 1")
    rows = []
    for d in (2, 3, 13, 61):
        sol = fundamental_solution(d, 1)
        rows.append([d, str(sol.x), str(sol.y),
                     "yes" if sol.verify(1) else "NO"])
    c.emit(render.table(["d", "x", "y", "verifies"], rows, console=c, right_align=[0]))
    c.emit()
    neg = fundamental_solution(2, -1)
    c.emit("   " + c.style(
        f"negative Pell x^2 - 2 y^2 = -1 has ({neg.x}, {neg.y}); it is solvable "
        "exactly when the period of sqrt(d) is odd.", "chrome"))
    c.emit()
    raw = c.ask("Enter a non-square d for its fundamental solution", "94",
                parse=lambda s: int(s))
    try:
        d = int(raw)
        sol = fundamental_solution(d, 1)
        if sol:
            c.emit("   " + c.style(f"x = {sol.x}, y = {sol.y}", "result"))
    except (ValueError, TypeError):
        pass
    c.emit()
    _souvenir(c, "Archimedes' cattle problem is a Pell equation whose smallest "
                 "solution has 206,545 digits.")


# --------------------------------------------------------------------------- #
#  Stop 8 — The Family Tree.
# --------------------------------------------------------------------------- #

def stop_08_tree(c: Console) -> None:
    from ..numbertheory import stern_brocot as sb
    from ..numbertheory import minkowski as mk

    _narr(c, "Start with 0/1 and 1/0. Between any two neighbours insert their "
             "mediant (a+c)/(b+d). Repeat forever and you build the Stern-Brocot "
             "tree, in which every positive fraction appears exactly once, already "
             "in lowest terms. A clockmaker, Achille Brocot, built it to choose gear "
             "ratios.")
    _subhead(c, "Live: the address of 355/113 in the tree")
    path = sb.rational_to_path(Fraction(355, 113))
    c.emit("   " + c.style("path: " + (path[:40] + ("..." if len(path) > 40 else "")), "result"))
    c.emit("   " + c.style(f"round-trips to {sb.path_to_rational(path)}", "success"))
    c.emit()
    _subhead(c, "Live: the Farey sequence F7 (denominators up to 7)")
    fs = list(sb.farey(7))
    c.emit("   " + c.style(", ".join(f"{f.numerator}/{f.denominator}" for f in fs), "result"))
    c.emit()
    _subhead(c, "Live: Minkowski's question-mark function sends surds to rationals")
    for label, val in [("?(1/3)", mk.question_mark(Fraction(1, 3))),
                       ("?(2/3)", mk.question_mark(Fraction(2, 3)))]:
        c.emit("   " + c.style(f"{label} = {val}", "result"))
    qphi = mk.question_mark_of_quadratic(-1, 5, 2)  # ?(1/phi)
    c.emit("   " + c.style(f"?(1/phi) = {qphi}  (a quadratic irrational becomes rational)", "result"))
    c.emit()
    _souvenir(c, "Consecutive Farey neighbours a/b < c/d always satisfy bc - ad = 1 "
                 "-- the determinant identity from the Engine Room, again.")


# --------------------------------------------------------------------------- #
#  Stop 9 — Celebrity Sightings.
# --------------------------------------------------------------------------- #

def stop_09_celebrity(c: Console) -> None:
    _narr(c, "Euler found in 1737 that e = [2; 1, 2, 1, 1, 4, 1, 1, 6, ...] -- a clean "
             "pattern of ones with every third term stepping up by two. This alone "
             "proves e is irrational. pi, by contrast, shows no pattern at all.")
    _subhead(c, "Live: e has a pattern")
    c.emit("   " + c.style("e  = " + _cf_str(e_cf().terms(14)), "result"))
    _subhead(c, "Live: pi does not")
    c.emit("   " + c.style("pi = " + _cf_str(pi_cf().terms(14)), "result"))
    c.emit()
    _narr(c, "It is not even known whether pi's partial quotients stay bounded. Order "
             "returns only if you allow generalized continued fractions with numerators "
             "other than 1 -- Brouncker's and Lambert's formulas -- from which Lambert "
             "gave the first proof that pi is irrational in 1761.")
    _subhead(c, "Live: pi rebuilt from a generalized continued fraction")
    c.emit("   " + c.style("via GCF: " + _cf_str(pi_cf_via_gcf().terms(5)), "result"))
    c.emit()
    _souvenir(c, "e's regularity makes it, oddly, an EXCEPTION to the statistical laws "
                 "that govern almost every other number -- next stop.")


# --------------------------------------------------------------------------- #
#  Stop 10 — The Casino.
# --------------------------------------------------------------------------- #

def stop_10_casino(c: Console) -> None:
    from ..dynamics import gauss

    _narr(c, "The Gauss map T(x) = {1/x} chops off a number's integer part after "
             "inverting it -- it is the shift that reads continued-fraction digits one "
             "at a time. Iterate it on a random real and the digits behave like loaded "
             "dice whose bias we know exactly.")
    _subhead(c, "Live: Gauss-Kuzmin -- how often each partial quotient appears")
    sample_terms = []
    rng = c.rng
    for _ in range(400):
        num = rng.getrandbits(64) + 1
        den = 1 << 64
        sample_terms.extend(CF.from_fraction(Fraction(num, den)).terms(30)[1:])
    emp = gauss.kuzmin_empirical(sample_terms, max_bucket=6)
    pred = {k: gauss.kuzmin_theoretical(k) for k in range(1, 7)}
    c.emit(render.histogram(emp, console=c, predicted=pred))
    c.emit()
    _subhead(c, "Live: Khinchin's constant -- a universal geometric mean")
    est = gauss.khinchin_estimate(sample_terms)
    c.emit("   " + c.style(f"geometric mean of sampled digits ~ {est:.4f}", "result"))
    c.emit("   " + c.style("Khinchin's constant K0 = 2.6854520...  (the same for almost "
                           "every real)", "chrome"))
    c.emit("   " + c.style(f"but sqrt(2), all 2s, gives exactly 2.0; and phi gives 1.0 "
                           "(the measure-zero exceptions).", "chrome"))
    c.emit()
    _souvenir(c, "Almost every number shares one geometric mean of its digits -- yet "
                 "not a single natural constant is proven to obey the law.")


# --------------------------------------------------------------------------- #
#  Stop 11 — The Infinite Assembly Line.
# --------------------------------------------------------------------------- #

def stop_11_gosper(c: Console) -> None:
    from ..cf import gosper
    from ..cf.gosper import GosperStall

    _narr(c, "Bill Gosper's 1972 algorithm does arithmetic directly on continued-"
             "fraction streams: it ingests a term when the answer is uncertain and "
             "emits a term when every possibility agrees. You can add sqrt(2) to e "
             "without ever computing a single decimal digit of either.")
    _subhead(c, "Live: 1 + sqrt(2) as a stream (the silver ratio, all 2s)")
    silver = gosper.affine(sqrt_cf(2), 1, 1)
    c.emit("   " + c.style(str(silver.terms(10)), "result"))
    _subhead(c, "Live: sqrt(2) + sqrt(3), a stream with no known formula")
    s = gosper.add(sqrt_cf(2), sqrt_cf(3))
    c.emit("   " + c.style(str(s.terms(10)), "result"))
    _subhead(c, "Live: e + pi, computed exactly to ten terms")
    ep = gosper.add(e_cf(), pi_cf())
    c.emit("   " + c.style(str(ep.terms(10)), "result"))
    c.emit()
    _subhead(c, "Live: sqrt(2) * sqrt(2) -- the machine stalls on purpose")
    try:
        val = gosper.mul(sqrt_cf(2), sqrt_cf(2), stall_limit=300).terms(6)
        c.emit("   " + c.style(str(val), "result"))
    except GosperStall:
        c.emit("   " + c.style("STALLED: the true answer is exactly 2, but no finite "
                               "prefix of the inputs can prove it -- stream equality is "
                               "undecidable.", "warn"))
    c.emit()
    _souvenir(c, "Recursion consumes structure; Gosper's corecursion produces it, "
                 "one certain digit at a time.")


# --------------------------------------------------------------------------- #
#  Stop 12 — The Tower.
# --------------------------------------------------------------------------- #

def stop_12_tower(c: Console) -> None:
    from ..recursion.classics import ackermann, hyperoperation, y_combinator, mccarthy91

    _narr(c, "We have ridden one gentle recursion the whole way. Now meet the "
             "recursions that outrun every tower you can build. The Ackermann "
             "function is total and computable, yet grows faster than any primitive-"
             "recursive function can.")
    _subhead(c, "Live: the Ackermann function A(m, n)")
    rows = []
    for m in range(4):
        row = [m]
        for n in range(6):
            row.append(ackermann(m, n))
        rows.append(row)
    c.emit(render.table(["m\\n", "0", "1", "2", "3", "4", "5"], rows,
                        console=c, right_align=[1, 2, 3, 4, 5, 6]))
    big = pow(2, 65536) - 3  # A(4, 2)
    import sys
    old_limit = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(22000)  # 2^65536 - 3 has 19,729 digits
    try:
        s = str(big)
    finally:
        sys.set_int_max_str_digits(old_limit)
    c.emit("   " + c.style(f"A(4, 2) = 2^65536 - 3 has {len(s)} digits, beginning "
                           f"{s[:20]}...", "result"))
    c.emit()
    _subhead(c, "Live: recursion without a name -- the Y combinator")
    y = y_combinator()
    fac = y(lambda f: lambda k: 1 if k == 0 else k * f(k - 1))
    c.emit("   " + c.style(f"factorial(10) via a fixed-point combinator = {fac(10)}", "result"))
    _subhead(c, "Live: McCarthy's 91 function")
    vals = {mccarthy91(n) for n in range(0, 101)}
    c.emit("   " + c.style(f"M(n) for every n from 0 to 100 equals {vals.pop()}", "result"))
    c.emit("   " + c.style(f"and 3 tetrated, 3^^3 = hyperoperation(4,3,3) = {hyperoperation(4,3,3)}", "result"))
    c.emit()
    _souvenir(c, "An infinite continued fraction is itself a fixed point: "
                 "phi = fix(x -> 1 + 1/x).")


# --------------------------------------------------------------------------- #
#  Stop 13 — The Hall of Mirrors.
# --------------------------------------------------------------------------- #

def stop_13_fractals(c: Console) -> None:
    _narr(c, "A fractal is recursion you can see: a shape built from smaller copies "
             "of itself. Its dimension need not be a whole number. The Koch curve has "
             "dimension log4/log3 ~ 1.262; the Sierpinski triangle log3/log2 ~ 1.585.")
    _subhead(c, "Live: the Sierpinski triangle as Pascal's triangle mod 2")
    rows = 16
    for n in range(rows):
        line = "".join(c.glyphs.route_done if (k & (n - k)) == 0 else " "
                       for k in range(n + 1))
        pad = " " * (rows - n)
        c.emit("   " + pad + " ".join(line))
    c.emit()
    _subhead(c, "Live: the Cantor set, removing middle thirds")
    seg = "#" * 27
    for depth in range(4):
        chunk = len(seg) // (3 ** depth) if 3 ** depth <= len(seg) else 1
        out = []
        for i, ch in enumerate(seg):
            block = i // chunk if chunk else 0
            out.append(ch if (block % 3 != 1) else " ")
        c.emit("   " + "".join(out))
    c.emit()
    _narr(c, "The link to this tour: a purely periodic continued fraction is the fixed "
             "point of a Mobius map, so quadratic irrationals are the self-similar "
             "points of the continued-fraction world -- and the Gauss map's inverse "
             "branches form an infinite fractal system whose attractor is the whole "
             "interval.")
    _souvenir(c, "Every fractal is a fixed point of a contraction (Hutchinson, 1981) "
                 "-- the same idea as a repeating continued fraction. See the web "
                 "exposition for Koch, dragon, and Hilbert curves drawn live.")


# --------------------------------------------------------------------------- #
#  Stop 14 — The Souvenir Shop.
# --------------------------------------------------------------------------- #

def stop_14_souvenir(c: Console) -> None:
    from ..applications import music, collatz
    from ..applications.wiener import make_vulnerable_key, wiener_attack
    import random

    _narr(c, "Three souvenirs from the applied world, all powered by convergents.")
    _subhead(c, "Music: equal temperament from the convergents of log2(3/2)")
    rows = []
    for frac in music.equal_temperament_convergents():
        rows.append([f"{frac.numerator}/{frac.denominator}",
                     frac.denominator, f"{music.cents_error(frac):+.3f}"])
    c.emit(render.table(["convergent", "notes/octave", "fifth error (cents)"],
                        rows, console=c, right_align=[1, 2]))
    c.emit("   " + c.style("7/12 gives the familiar 12-tone piano; its fifth is off by "
                           "under two cents.", "chrome"))
    c.emit()
    _subhead(c, "Broken crypto: Wiener's attack recovers a small RSA exponent")
    key = make_vulnerable_key(128, rng=random.Random(7))
    recovered = wiener_attack(key.e, key.n)
    ok = recovered == key.d
    c.emit("   " + c.style(f"generated n with a small secret d; convergents of e/n "
                           f"recover d = {recovered}", "result"))
    c.emit("   " + c.style("attack succeeded" if ok else "attack failed",
                           "success" if ok else "warn"))
    c.emit()
    _subhead(c, "The 3n+1 problem: the simplest unsolved question in mathematics")
    stats = collatz.collatz_stats(27)
    c.emit("   " + c.style(f"starting at 27: {stats['steps']} steps, peak {stats['max']}", "result"))
    raw = c.ask("Enter a starting number for its Collatz flight", "97", parse=lambda s: int(s))
    try:
        st = collatz.collatz_stats(int(raw))
        c.emit("   " + c.style(f"{raw}: {st['steps']} steps, peak {st['max']}", "result"))
    except (ValueError, TypeError):
        pass
    c.emit()
    _souvenir(c, "The same convergents that tune a piano also break a lazy RSA key.")


# --------------------------------------------------------------------------- #
#  Stop 15 — Terminus.
# --------------------------------------------------------------------------- #

def stop_15_terminus(c: Console) -> None:
    from ..dynamics import gauss
    from ..cf.constants import catalan_cf

    _narr(c, "Continued fractions are old, but they are not finished. Some of the "
             "most basic questions about the numbers on this tour are still open.")
    _subhead(c, "Open problems")
    for line in [
        "Is pi's continued fraction 'normal'? Even boundedness of its terms is open.",
        "Is Khinchin's constant K0 = 2.6854520... irrational? Unknown.",
        "Is the Euler-Mascheroni constant gamma irrational? Unknown.",
        "Zaremba's conjecture: every denominator hosts a fraction with small partial quotients.",
        "The Littlewood conjecture on simultaneous approximation -- still open since ~1930.",
    ]:
        c.emit("   " + c.style(c.glyphs.bullet + " ", "marker") + line)
    c.emit()
    _subhead(c, "Live: Catalan's constant looks Khinchin-typical, but no proof exists")
    terms = catalan_cf().terms(30)
    est = gauss.khinchin_estimate(terms[1:])
    c.emit("   " + c.style(f"geometric mean of its known digits ~ {est:.3f}   "
                           "(PROOF: none)", "result"))
    c.emit()
    _subhead(c, "Further reading")
    for ref in [
        "A. Ya. Khinchin, Continued Fractions",
        "Graham, Knuth & Patashnik, Concrete Mathematics (section 4.5, the Stern-Brocot tree)",
        "Gosper, Continued Fraction Arithmetic (HAKMEM item 101)",
        "Hardy & Wright, An Introduction to the Theory of Numbers (chapter X)",
    ]:
        c.emit("   " + c.style(c.glyphs.bullet + " ", "chrome") + ref)
    c.emit()
    _souvenir(c, "End of the line. The structures of logic run ever onward; thank you "
                 "for riding the Recursive Continuance Tour Bus.")
