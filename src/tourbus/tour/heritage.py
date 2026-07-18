"""The Heritage Line: nine historical stops, computed on the modern engine.

From Euclid's mutual measuring to Gosper's stream arithmetic, each stop
replays a primary source live — Elements X.2, Brahmagupta's d = 92, Bombelli's
sqrt(13), Huygens' gear train, Lambert's tangent, Liouville's built-to-order
transcendental, the tree of Stern and Brocot, the factorization of F7, and
HAKMEM item 101 — on the same exact engine the rest of the tour uses. Reached
with ``python -m tourbus heritage``.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import islice

from .termio import Console
from . import render


def _subhead(c: Console, text: str) -> None:
    render.subhead(c, text)


def _souvenir(c: Console, text: str) -> None:
    render.souvenir(c, text)


# --------------------------------------------------------------------------- #

def heritage_01_euclid(c: Console) -> None:
    from .stops import _cf_str, _euclid_trace
    from ..cf.constants import sqrt_cf
    from ..cf.expand import cf_from_fraction

    c.paragraph("Two lengths measured against each other until nothing remains -- the "
                "tour's oldest engine, in its original packaging.")
    c.emit()
    c.paragraph("Elements VII, Propositions 1 and 2 find a greatest common measure by "
                "mutual measuring -- anthyphairesis. Book X, Proposition 2 states the "
                "converse nobody expects from 300 BC: if the measuring never ends, the "
                "two magnitudes share no common measure. The Greeks owned the "
                "continued-fraction irrationality test two millennia before "
                "'irrational number' was a phrase. Stop 1 runs this as an algorithm; "
                "this stop runs it as an artifact.")
    c.emit()
    _subhead(c, "Live: Elements VII, Props. 1-2 -- 1071 measured against 462")
    for line in _euclid_trace(1071, 462):
        c.emit("   " + c.style(line, "result"))
    _subhead(c, "Live: keep the quotients and Euclid has already invented the "
                "continued fraction")
    terms = list(cf_from_fraction(Fraction(1071, 462)))
    c.emit("   " + c.style(
        f"quotients {terms}  ->  1071/462 = {_cf_str(terms, truncated=False)}",
        "result"))
    _subhead(c, "Live: Elements X.2 -- a measuring that never ends")
    c.emit("   " + c.style(f"sqrt(2) = {_cf_str(sqrt_cf(2).terms(12))}", "result"))
    c.emit("   " + c.style(
        "by X.2 the side and diagonal of a square share no common measure.", "chrome"))
    c.emit()
    _souvenir(c, "Euclid never wrote 'irrational' -- he wrote 'the measuring never "
                 "ends.' Same theorem, twenty-three centuries between wordings.")


def heritage_02_chakravala(c: Console) -> None:
    from ..cf.expand import cf_from_quadratic
    from ..numbertheory import pell
    from ..numbertheory.chakravala import chakravala_steps

    c.paragraph("Fermat's hardest challenge had been answered in Sanskrit verse five "
                "hundred years before he posed it.")
    c.emit()
    c.paragraph("Brahmagupta's bhavana (628 CE) composes two near-solutions of "
                "x^2 - d y^2 = k into a better one; the chakravala -- Jayadeva, then "
                "Bhaskara II, around 1150 -- turns composition into a wheel that "
                "drives k to 1. Bhaskara's showcase was exactly d = 61, the case "
                "Fermat, unknowingly, posed to the English in 1657. No continued "
                "fraction appears anywhere in the method, and yet it lands on the "
                "same convergents Stop 7 computes.")
    c.emit()
    _subhead(c, "Live: Brahmagupta's own case, d = 92 (628 CE)")
    steps = chakravala_steps(92)
    rows = [[i, s.a, s.b, s.k, "-" if s.m is None else s.m]
            for i, s in enumerate(steps)]
    c.emit(render.table(["turn", "a", "b", "k", "m"], rows, console=c,
                        right_align=[0, 1, 2, 3, 4]))
    a, b = steps[-1].a, steps[-1].b
    c.emit("   " + c.style(f"check: {a}^2 - 92 x {b}^2 = {a * a - 92 * b * b}",
                           "success"))
    _subhead(c, "Live: the wheel turns for d = 61")
    steps = chakravala_steps(61)
    rows = [[i, s.a, s.b, s.k, "-" if s.m is None else s.m]
            for i, s in enumerate(steps)]
    c.emit(render.table(["turn", "a", "b", "k", "m"], rows, console=c,
                        highlight=len(rows) - 1, right_align=[0, 1, 2, 3, 4]))
    _subhead(c, "Live: the loop road agrees")
    sol = pell.fundamental_solution(61)
    c.emit("   " + c.style(
        f"pell.fundamental_solution(61) = ({sol.x}, {sol.y})", "result"))
    head, period = cf_from_quadratic(0, 61, 1)
    c.emit("   " + c.style(
        f"sqrt(61) = [{head[0]}; {', '.join(str(t) for t in period)}, ...]  "
        f"period length {len(period)}", "result"))
    c.emit("   " + c.style(
        "odd period -> x^2 - 61 y^2 = -1 first, at (29718, 3805) -- the wheel's "
        "own k = -1 station.", "chrome"))
    c.emit()
    _souvenir(c, "The chakravala reaches x = 1766319049 in a handful of turns, no "
                 "continued fraction in sight -- two roads up the same mountain.")


def heritage_03_print(c: Console) -> None:
    from ..cf.constants import pi_cf, sqrt_cf
    from ..cf.convergents import convergent_pairs
    from ..cf.gcf import GCFTerm, brouncker_gcf, gcf_convergents

    c.paragraph("Pi's first continued fraction never ends -- found in 1655, before "
                "the thing it is made of had a name.")
    c.emit()
    c.paragraph("Bombelli (1572) approximates sqrt(13) by feeding a fraction into "
                "itself; Cataldi (1613) does sqrt(18) and invents a notation for the "
                "dangling 'and so on'; Brouncker (1655) produces the first continued "
                "fraction for pi, recorded by Wallis -- who later christens the object "
                "'continued fraction'. Order beneath chaos, the theme Stop 9 states, "
                "began here.")
    c.emit()
    _subhead(c, "Live: Bombelli's sqrt(13), 1572")

    def bombelli():
        yield GCFTerm(3, 1)
        while True:
            yield GCFTerm(6, 4)

    convs = list(islice(gcf_convergents(bombelli()), 6))
    c.emit("   " + c.style(
        "3 + 4/(6 + 4/(6 + ...))  ->  " + ", ".join(str(f) for f in convs) + ", ...",
        "result"))
    c.emit("   " + c.style(
        f"last = {float(convs[-1]):.7f}   sqrt(13) = "
        f"{float(sqrt_cf(13).approx(20)):.7f}", "result"))
    _subhead(c, "Live: Cataldi's sqrt(18), 1613")

    def cataldi():
        yield GCFTerm(4, 1)
        while True:
            yield GCFTerm(8, 2)

    convs = list(islice(gcf_convergents(cataldi()), 5))
    c.emit("   " + c.style(
        "4 + 2/(8 + 2/(8 + ...))  ->  " + ", ".join(str(f) for f in convs) + ", ...",
        "result"))
    c.emit("   " + c.style(
        f"last = {float(convs[-1]):.7f}   sqrt(18) = "
        f"{float(sqrt_cf(18).approx(20)):.7f}", "result"))
    _subhead(c, "Live: Brouncker's 4/pi, 1655 -- beautiful, and beautifully slow")
    c.emit("   " + c.style("4/pi = 1 + 1^2/(2 + 3^2/(2 + 5^2/(2 + ...)))", "result"))
    convs = list(islice(gcf_convergents(brouncker_gcf()), 8))
    rows = [[n, str(f), f"{4 / float(f):.6f}"] for n, f in enumerate(convs)]
    c.emit(render.table(["n", "convergent of 4/pi", "4/convergent"], rows,
                        console=c, right_align=[0, 2]))
    h, k = list(convergent_pairs(pi_cf().terms(4)))[-1]
    c.emit("   " + c.style(
        f"eight of Brouncker's terms give pi ~ {4 / float(convs[-1]):.6f}; four "
        f"simple terms give {h}/{k} = {h / k:.7f}.", "chrome"))
    c.emit()
    _souvenir(c, "Brouncker's fraction is lawful and strolls; the simple fraction of "
                 "pi looks lawless and sprints. Beauty and speed are different "
                 "virtues.")


def heritage_04_huygens(c: Console) -> None:
    from .stops import _cf_str
    from ..applications import gears
    from ..cf.convergents import convergent_pairs
    from ..cf.expand import cf_from_fraction

    c.paragraph("You cannot cut a gear with 77 million teeth; Huygens' convergent "
                "needed only 206.")
    c.emit()
    c.paragraph("Christiaan Huygens, designing a clockwork solar system, needs "
                "Saturn's year over Earth's: 77708431/2640858. A gear pair realizes "
                "only a rational ratio with cuttable teeth counts -- best rational "
                "approximation with a bounded denominator, the exact problem of Stop "
                "5. His posthumous Descriptio automati planetarii (1703) lays out "
                "convergent-truncation as the design rule: the first engineering "
                "application of the theory, a century before Legendre proved the "
                "criterion.")
    c.emit()
    _subhead(c, "Live: Saturn's year over Earth's, unfolded")
    target = gears.HUYGENS_TARGET
    terms = list(islice(cf_from_fraction(target), 8))
    c.emit("   " + c.style(f"{target} = {_cf_str(terms)}", "result"))
    _subhead(c, "Live: the convergent ladder, and the wheel he cut")
    rows = []
    for n, (h, k) in enumerate(convergent_pairs(terms)):
        err = float(Fraction(h, k) - target)
        rows.append([n, f"{h}/{k}", f"{h / k:.6f}", f"{err:+.1e}"])
    c.emit(render.table(["n", "p/q", "value", "error"], rows, console=c,
                        highlight=3, right_align=[0, 2, 3]))
    wheel, pinion = gears.huygens_gear()
    rel = abs(Fraction(wheel, pinion) - target) / target
    c.emit("   " + c.style(
        f"huygens_gear() = ({wheel}, {pinion}): a {wheel}-tooth wheel driving a "
        f"{pinion}-tooth pinion,", "result"))
    c.emit("   " + c.style(
        f"off by one part in {int(1 / rel):,}.", "result"))
    _subhead(c, "Live: the same rule under a modern tooth budget")
    wheel, pinion = gears.gear_ratio(Fraction(355, 113))
    c.emit("   " + c.style(
        f"gear_ratio(355/113) = ({wheel}, {pinion}): pi as a gear, "
        f"{wheel}/{pinion} = {wheel / pinion:.6f} -- an echo of Stop 5.", "result"))
    c.emit()
    _souvenir(c, "One part in nine thousand, from two wheels a clockmaker could "
                 "actually cut -- the first machine ever built out of a convergent.")


def heritage_05_lambert(c: Console) -> None:
    from .stops import _cf_str
    from ..cf.constants import tan1_cf
    from ..cf.gcf import GCFTerm, gcf_convergents

    c.paragraph("The first man to prove pi irrational did it by cross-examining the "
                "tangent function.")
    c.emit()
    c.paragraph("Lambert's memoir (presented to the Berlin Academy in 1761) expands "
                "tan x as a continued fraction; for rational x != 0 the expansion "
                "cannot terminate or repeat rationally, so tan x is irrational. But "
                "tan(pi/4) = 1 is rational -- therefore pi/4, and pi, is not. Stop 9 "
                "states the formula; here the fraction runs live, and the pattern "
                "that carries the proof appears on screen.")
    c.emit()
    _subhead(c, "Live: Lambert's fraction at x = 1")

    def lambert():
        yield GCFTerm(0, 1)
        yield GCFTerm(1, 1)
        odd = 3
        while True:
            yield GCFTerm(odd, -1)
            odd += 2

    c.emit("   " + c.style("tan 1 = 1/(1 - 1/(3 - 1/(5 - 1/(7 - ...))))", "result"))
    convs = list(islice(gcf_convergents(lambert()), 1, 6))
    c.emit("   " + c.style(
        "convergents " + ", ".join(str(f) for f in convs)
        + f", ...  ->  {float(convs[-1]):.6f}", "result"))
    _subhead(c, "Live: the certified simple continued fraction of tan(1)")
    c.emit("   " + c.style(f"tan(1) = {_cf_str(tan1_cf().terms(10))}", "result"))
    c.emit("   " + c.style("the odd numbers stand up in court.", "chrome"))
    c.emit()
    _souvenir(c, "tan(1) = [1; 1, 1, 3, 1, 5, 1, 7, ...] -- a rational tangent would "
                 "have to end; this one visibly never will.")


def heritage_06_liouville(c: Console) -> None:
    from ..numbertheory import liouville as LV

    c.paragraph("In 1844 Liouville built a number on purpose to be transcendental -- "
                "the first ever proved so, thirty years before anyone showed e or pi "
                "were.")
    c.emit()
    c.paragraph("The idea is Stop 4 turned upside down. An algebraic irrational cannot "
                "be approximated by rationals much better than 1/q^2 (Liouville's "
                "inequality; Hurwitz's sqrt(5) is the sharp golden case). So a number "
                "that IS approximated far too well cannot be algebraic. Liouville's "
                "constant L = sum 10^(-n!) = 0.11000100000000000000000100... places its "
                "1s at the factorial positions, and each long run of 0s is a rational "
                "that hugs L absurdly tightly. In the continued fraction that shows up "
                "as partial quotients that explode.")
    c.emit()
    k = 4
    _subhead(c, "Live: the constant, truncated to its first four factorial terms")
    trunc = LV.liouville_truncation(k)
    places = len(str(trunc.denominator)) - 1  # denominator is 10^(k!)
    exact = "0." + str(trunc.numerator).rjust(places, "0")
    c.emit("   " + c.style(f"L ~ {exact}...", "result"))
    c.emit("   " + c.style(f"    (exact; the 1s sit at positions 1, 2, 6, 24 = 1!, 2!, 3!, 4!; "
                           f"rigorous tail < {float(LV.liouville_tail_bound(k)):.0e})", "chrome"))
    _subhead(c, "Live: the certified continued fraction -- and its explosions")
    terms = LV.liouville_cf_terms(k, max_terms=14)
    c.emit("   " + c.style(f"{terms}", "result"))
    peaks = LV.partial_quotient_peaks(terms)
    biggest = max(peaks, key=lambda ia: ia[1])
    c.emit("   " + c.style(
        f"a[{biggest[0]}] = {biggest[1]} -- a partial quotient with twelve digits, the "
        "signature of a rational hugging L far too tightly to be algebraic.", "chrome"))
    _subhead(c, "Live: Liouville's inequality holds for the algebraic sqrt(2)")
    report = LV.liouville_inequality_report(1, 0, -2, cf_prefix_len=6)
    c.emit("   " + c.style(
        f"|sqrt(2) - p/q| > c/q^2 on its own convergents: all {all(ok for *_, ok in report)}",
        "result"))
    c.emit()
    _souvenir(c, "Approximate a number too well and you prove it transcendental. Roth "
                 "(1955) later showed the algebraics allow no exponent past 2 at all -- "
                 "a Fields Medal for one sharp inequality.")


def heritage_07_stern_brocot(c: Console) -> None:
    from ..numbertheory import stern_brocot as sb

    c.paragraph("Two men, a blackboard and a workbench, grew the same tree of all "
                "fractions three years apart -- and one of them was a clockmaker "
                "picking gear trains.")
    c.emit()
    c.paragraph("Moritz Stern (1858), a mathematician, and Achille Brocot (1861), a "
                "Parisian clockmaker, independently described the mediant tree of "
                "Stop 8: between p/q and r/s sits (p+r)/(q+s), and iterating reaches "
                "every rational in lowest terms exactly once. Brocot did not want a "
                "theorem; he wanted gear ratios he could cut, and his published table "
                "let a workshop read off the nearest achievable ratio -- Huygens' "
                "problem at H4, now a lookup table.")
    c.emit()
    _subhead(c, "Live: the tree locates 355/113 by a path of mediants")
    frac = Fraction(355, 113)
    path = sb.rational_to_path(frac)
    c.emit("   " + c.style(f"355/113 -> address {path}", "result"))
    c.emit("   " + c.style(f"round-trips to {sb.path_to_rational(path)} (pi's gear, to a part in 10^7)",
                           "result"))
    _subhead(c, "Live: Brocot's workshop lookup -- best gear ratio near 7/2 under 30 teeth")
    target = Fraction(7, 2)
    best = None
    for q in range(1, 31):
        for p in range(1, 61):
            f = Fraction(p, q)
            if f.numerator <= 60 and f.denominator <= 30:
                err = abs(f - target)
                if best is None or err < best[0]:
                    best = (err, p, q)
    c.emit("   " + c.style(f"target {target}: closest cuttable ratio {best[1]}/{best[2]} "
                           f"(error {float(best[0]):.4g})", "result"))
    _subhead(c, "Live: mediants build the Farey sequence, order 6")
    c.emit("   " + c.style(", ".join(str(f) for f in sb.farey(6)), "result"))
    c.emit()
    _souvenir(c, "The tree of every fraction was discovered twice in three years -- once "
                 "for its theorems, once to cut brass. Same tree; Stop 8 rides it whole.")


def heritage_08_morrison_brillhart(c: Console) -> None:
    from ..applications import cfrac

    c.paragraph("In 1970 a continued fraction did what no one had managed by hand: it "
                "cracked the seventh Fermat number, and taught modern cryptanalysis how "
                "to factor.")
    c.emit()
    c.paragraph("Fermat guessed every 2^(2^n)+1 was prime; Euler killed F5 in 1732. F7 "
                "= 2^128 + 1 held out until Morrison and Brillhart ran CFRAC on an "
                "IBM 360 in 1970. The trick: the convergents of sqrt(N) leave small "
                "residues Q, so small they often factor over a tiny prime base; combine "
                "enough of them and you build X^2 = Y^2 (mod N), and gcd(X-Y, N) splits "
                "N. The same convergents Wiener (Stop 14) later turned against RSA.")
    c.emit()
    n = 13290059
    _subhead(c, f"Live: CFRAC factors {n} from the convergents of its square root")
    trace = cfrac.cfrac_demo_trace(n)
    c.emit("   " + c.style(f"smoothness base (primes where N is a QR): {trace['base'][:8]}...",
                           "chrome"))
    c.emit("   " + c.style(f"built {trace['n_relations']} smooth relations A^2 = Q (mod N)",
                           "result"))
    p, q = trace["factors"]
    c.emit("   " + c.style(f"congruence of squares -> gcd splits N: {n} = {p} x {q}", "success"))
    _subhead(c, "Live: the very number it was built for, F7 = 2^128 + 1")
    c.emit("   " + c.style(f"F7 = {cfrac.FERMAT_F7}", "result"))
    c.emit("   " + c.style(f"   = {cfrac.F7_FACTORS[0]} x {cfrac.F7_FACTORS[1]}", "result"))
    c.emit("   " + c.style(f"verified: {cfrac.verify_f7()}", "success"))
    c.emit()
    _souvenir(c, "The quadratic sieve and the number field sieve are CFRAC's children; "
                 "the continued fraction of sqrt(N) is where modern factoring began.")


def heritage_09_gosper(c: Console) -> None:
    from .stops import _cf_str
    from ..cf import gosper
    from ..cf.constants import e_cf, phi_cf, sqrt_cf

    c.paragraph("A photocopied memo from 1972 teaches arithmetic to run forever -- "
                "and the heritage line arrives back at the depot.")
    c.emit()
    c.paragraph("HAKMEM, MIT AI Memo 239 (February 1972), is a grab-bag of hacks "
                "from the AI Lab; item 101 is Gosper's continued-fraction "
                "arithmetic. Never a journal paper, it passed hand to hand for "
                "decades until Vuillemin (1990) gave it formal foundations. The arc "
                "closes: Euclid's loop discards quotients, Gosper's loop streams "
                "them. Stop 11 teaches the machine; this stop places it in time and "
                "runs three demos Stop 11 doesn't.")
    c.emit()
    _subhead(c, "Live: the machine turns sqrt(5) into the golden ratio")
    t = gosper.affine(sqrt_cf(5), Fraction(1, 2), Fraction(1, 2)).terms(12)
    c.emit("   " + c.style(f"sqrt(5)/2 + 1/2 = {_cf_str(t)} = phi", "result"))
    _subhead(c, "Live: e upside down, without ever computing e")
    t = gosper.reciprocal(e_cf()).terms(12)
    c.emit("   " + c.style(f"1/e = {_cf_str(t)}", "result"))
    _subhead(c, "Live: phi + phi rediscovers the loop road")
    t = gosper.add(phi_cf(), phi_cf()).terms(10)
    c.emit("   " + c.style(f"phi + phi = {_cf_str(t)} = 1 + sqrt(5)", "result"))
    c.emit()
    _souvenir(c, "From a subtraction loop in the Elements to a stream machine in a "
                 "memo -- one recurrence, twenty-three centuries of mileage.")


HERITAGE_STOPS = [
    ("The Ladder of Euclid",
     "Anthyphairesis: the continued fraction, three centuries before Christ and "
     "two millennia before its name.",
     heritage_01_euclid),
    ("The Cyclic Method",
     "Fermat's challenge, solved in Sanskrit verse five hundred years early.",
     heritage_02_chakravala),
    ("First Fractions in Print",
     "Bombelli, Cataldi, Brouncker: a notation, a name, and pi's first continued fraction.",
     heritage_03_print),
    ("The Planetarium",
     "Huygens cuts Saturn's orbit into 206 brass teeth.",
     heritage_04_huygens),
    ("Lambert's Trial of Pi",
     "The tangent testifies, and pi is proved irrational.",
     heritage_05_lambert),
    ("The Skyscraper of Liouville",
     "A number built to be approximated: the first proven transcendental.",
     heritage_06_liouville),
    ("The Tree in the Workshop",
     "Stern's blackboard and Brocot's gears grow the same tree of fractions.",
     heritage_07_stern_brocot),
    ("The Factoring Machine",
     "CFRAC cracks F7: convergents turned against the integers.",
     heritage_08_morrison_brillhart),
    ("Item 101",
     "Gosper's memo teaches arithmetic to stream forever.",
     heritage_09_gosper),
]
