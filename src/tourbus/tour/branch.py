"""The Branch Line: six stops on other ways to unfold a number.

The regular continued fraction is one machine -- take the floor, subtract,
reciprocate, repeat. Swap any part of that machine and a number unfolds
differently: the Engel and Pierce series climb by ceilings, the Egyptian
scribe subtracts the largest unit fraction it can, Zeckendorf writes integers
in Fibonacci, Ostrowski writes them against a chosen irrational, and Lochs
measures the exchange rate between decimal digits and continued-fraction
terms. Each still computes exactly on the same engine. Reached with
``python -m tourbus branch``.
"""

from __future__ import annotations

from fractions import Fraction

from .termio import Console
from . import render


def _subhead(c: Console, text: str) -> None:
    render.subhead(c, text)


def _souvenir(c: Console, text: str) -> None:
    render.souvenir(c, text)


# --------------------------------------------------------------------------- #

def branch_01_engel(c: Console) -> None:
    from ..expansions import engel as E

    c.paragraph("Stop 2 unfolds a number by flooring, subtracting, and flipping. "
                "Change 'floor' to 'ceiling' and you get the Engel expansion: every "
                "x in (0,1] is a sum 1/a1 + 1/(a1 a2) + 1/(a1 a2 a3) + ... with the "
                "integers a1 <= a2 <= a3 <= ... climbing an escalator, never a step "
                "down. Rational in, finite out -- Stop 2's headline theorem, in a new "
                "dialect.")
    c.emit()
    x = Fraction(3, 7)
    digits = E.engel_expansion(x)
    _subhead(c, f"Live: the Engel escalator of {x}")
    c.emit("   " + c.style(f"a = ceil(1/x), then x <- a*x - 1  ->  digits {digits}", "result"))
    terms = " + ".join(
        "1/" + "".join(str(d) for d in [_prod(digits[: i + 1])])
        for i in range(len(digits))
    )
    c.emit("   " + c.style(f"{x} = {terms}", "result"))
    c.emit("   " + c.style(f"check: {E.engel_eval(digits)} = {x}", "chrome"))
    _subhead(c, "Live: e is an Engel escalator you already know -- the factorial series")
    et = E.engel_e_terms(8)
    c.emit("   " + c.style(f"digits of e: {et}  (1, then 1, 2, 3, 4, ... -- the k! ladder)",
                           "result"))
    sums = E.engel_partial_sums(et)
    rows = [[k + 1, str(et[k]), f"{float(sums[k]):.7f}"] for k in range(len(et))]
    c.emit(render.table(["term", "a_k", "partial sum -> e"], rows, console=c,
                        right_align=[0, 1, 2]))
    c.emit("   " + c.style(f"e = {float(sums[-1]):.7f}...  (2.7182818...)", "chrome"))
    c.emit()
    _souvenir(c, "The Engel digits never decrease -- an expansion that only ever climbs, "
                 "and terminates precisely for the rationals.")


def _prod(xs) -> int:
    p = 1
    for x in xs:
        p *= x
    return p


def branch_02_luroth_pierce(c: Console) -> None:
    from ..expansions import luroth as L

    c.paragraph("Two more escalators, each with a twist. The Luroth series has "
                "independent, identically distributed digits -- the honest casino "
                "the Gauss map (Stop 10) never is -- but a rational's Luroth "
                "expansion is eventually PERIODIC, not finite. The Pierce series is "
                "Engel with alternating signs, its digits strictly increasing.")
    c.emit()
    x = Fraction(7, 10)
    pre, period = L.luroth_expansion(x)
    _subhead(c, f"Live: Luroth of {x} loops forever (a rational with a period)")
    c.emit("   " + c.style(
        f"preperiod {pre}, period {period}  ->  folds back to {L.luroth_eval(pre, period)}",
        "result"))
    y = Fraction(5, 17)
    pd = L.pierce_expansion(y)
    _subhead(c, f"Live: Pierce of {y} -- alternating, strictly increasing, finite")
    c.emit("   " + c.style(
        f"digits {pd}  ->  1/{pd[0]} - 1/({pd[0]}*{pd[1]}) + ...  =  {L.pierce_eval(pd)}",
        "result"))
    _subhead(c, "Live: Pierce of 1/phi -- and the Lucas numbers hiding in the gaps")
    phi_digits = L.pierce_of_reciprocal_phi(7)
    c.emit("   " + c.style(f"1/phi = {phi_digits}", "result"))
    c.paragraph(c.style(
        "not the Lucas numbers themselves: 4 = L3, then 17,19 straddle L6 = 18, "
        "then 5777,5779 straddle L18 = 5778 -- pairs around Lucas numbers of "
        "tripling index. The digits explode doubly exponentially.", "chrome"),
        indent="   ")
    c.emit()
    _souvenir(c, "Luroth's digit k occurs with probability 1/(k(k-1)) -- a casino whose "
                 "odds you can write down, unlike the continued fraction's.")


def branch_03_egyptian(c: Console) -> None:
    from ..expansions import egyptian as G

    c.paragraph("A scribe on the Rhind papyrus wrote every fraction as a sum of "
                "distinct unit fractions. Fibonacci's greedy rule (1202) always "
                "finishes -- subtract the largest 1/n you can, repeat -- but the "
                "denominators can double their digit-count at every step, a price no "
                "continued fraction ever pays.")
    c.emit()
    x = Fraction(5, 121)
    greedy = G.fibonacci_sylvester(x)
    _subhead(c, f"Live: the greedy scribe on {x} -- watch the denominators explode")
    c.emit("   " + c.style(f"{x} = " + " + ".join(f"1/{d}" for d in greedy), "result"))
    c.emit("   " + c.style(
        f"digit counts {[len(str(d)) for d in greedy]}; a shorter answer exists: "
        "1/33 + 1/121 + 1/363.", "chrome"))
    _subhead(c, "Live: Sylvester's sequence -- greedy on 1 itself")
    syl = G.sylvester_sequence(6)
    c.emit("   " + c.style(f"1 = 1/2 + 1/3 + 1/7 + 1/43 + ...  ->  {syl}", "result"))
    c.emit("   " + c.style("each term is s_{k+1} = s_k^2 - s_k + 1 -- the fastest an "
                           "Egyptian expansion can grow.", "chrome"))
    _subhead(c, "Live: the Erdos-Straus conjecture, 4/n = 1/a + 1/b + 1/c (open since 1948)")
    rows = []
    for n in (5, 7, 11, 13, 101, 1009):
        t = G.erdos_straus(n)
        rows.append([n, f"1/{t[0]} + 1/{t[1]} + 1/{t[2]}" if t else "(search exhausted)"])
    c.emit(render.table(["n", "4/n as three unit fractions"], rows, console=c,
                        right_align=[0]))
    c.emit("   " + c.style("a solution is known for every n ever tested; that one always "
                           "exists is unproved.", "chrome"))
    c.emit()
    _souvenir(c, "Greedy always terminates, but greed is expensive: the denominators of "
                 "5/121 reach twenty-five digits where a cleverer scribe needs three.")


def branch_04_zeckendorf(c: Console) -> None:
    from ..expansions.zeckendorf import (
        zeckendorf, is_zeckendorf, from_zeckendorf, base_phi_digits,
    )

    c.paragraph("Stop 4's golden ratio wears a numeration system here. Every positive "
                "integer is uniquely a sum of non-consecutive Fibonacci numbers "
                "(Zeckendorf), and every integer has a positional expansion in the "
                "irrational base phi -- with the Fibonacci recurrence as its carry rule.")
    c.emit()
    for n in (100, 2026):
        summands = zeckendorf(n)
        _subhead(c, f"Live: Zeckendorf of {n}")
        c.emit("   " + c.style(f"{n} = " + " + ".join(str(s) for s in summands)
                               + "   (no two consecutive Fibonacci numbers)", "result"))
        c.emit("   " + c.style(
            f"legal Zeckendorf: {is_zeckendorf(summands)}; "
            f"folds back to {from_zeckendorf(summands)}", "chrome"))
    _subhead(c, "Live: the same integers written in base phi")
    rows = [[n, base_phi_digits(n)] for n in (1, 2, 3, 4, 7, 11)]
    c.emit(render.table(["n", "n in base phi"], rows, console=c, right_align=[0]))
    c.emit("   " + c.style("phi^2 = phi + 1 is the carry rule; no representation ever "
                           "has two 1s in a row.", "chrome"))
    c.emit()
    _souvenir(c, "Fibonacci coding, the '11'-free codes of data compression, and base phi "
                 "are one idea: the golden ratio as a way to write numbers down.")


def branch_05_ostrowski(c: Console) -> None:
    from ..expansions.ostrowski import (
        ostrowski, from_ostrowski, is_legal_ostrowski, beatty, characteristic_word,
    )
    from ..cf.core import QuadraticSurd

    c.paragraph("Zeckendorf writes integers against the Fibonacci numbers. Ostrowski "
                "generalises it to ANY irrational: write n against the convergent "
                "denominators of alpha's continued fraction. Choose alpha = 1/phi and "
                "you get Zeckendorf back; choose a line of golden slope across the "
                "integer grid and the crossings spell the Fibonacci word -- the "
                "canonical Sturmian sequence, the arithmetic behind the three-distance "
                "theorem (E5) and the Fibonacci quasicrystal (Cross-Domain).")
    c.emit()
    fib_cf = [0] + [1] * 20
    _subhead(c, "Live: Ostrowski digits against 1/phi rebuild Zeckendorf")
    rows = []
    for n in (10, 20, 50, 100):
        digits = ostrowski(n, fib_cf)
        rows.append([n, str(digits), from_ostrowski(digits, fib_cf),
                     is_legal_ostrowski(digits, fib_cf)])
    c.emit(render.table(["n", "Ostrowski digits (b1..)", "rebuilt", "legal"],
                        rows, console=c, right_align=[0, 2]))
    _subhead(c, "Live: a line of golden slope cutting the grid -- the Fibonacci word")
    word = characteristic_word(fib_cf, 34)
    c.emit("   " + c.style(word, "result"))
    c.paragraph(c.style("read a per vertical crossing, b per horizontal: it never "
                        "repeats and it is never random.", "chrome"), indent="   ")
    _subhead(c, "Live: the Beatty sequence of sqrt(2) -- floor(k*sqrt2)")
    beat = beatty(QuadraticSurd.make(0, 1, 2), 12)
    c.emit("   " + c.style(f"{beat}", "result"))
    c.paragraph(c.style("its complement floor(k*(2+sqrt2)) covers every integer it "
                        "misses -- Rayleigh's theorem.", "chrome"), indent="   ")
    c.emit()
    _souvenir(c, "One irrational, one continued fraction, one way to number the integers -- "
                 "and out falls the word every quasicrystal is built from.")


def branch_06_lochs(c: Console) -> None:
    from ..expansions import lochs as L
    from ..cf.constants import pi_cf

    c.paragraph("How many continued-fraction terms is one decimal digit worth? Lochs "
                "(1964): almost surely the exchange rate settles to "
                "6 ln2 ln10 / pi^2 = 0.9703 -- one decimal digit buys about 0.97 "
                "continued-fraction terms, so one term is worth about 1.03 digits. The "
                "continued fraction is the denser currency, and the rate is the entropy "
                "of the Gauss map (Stop 10), the same physics as Levy's constant.")
    c.emit()
    _subhead(c, "Live: expanding pi, decimals pinned per continued-fraction term")
    terms = pi_cf().terms(14)
    exp = L.lochs_experiment(terms, max_terms=12)
    rows = [[r["n"], r["digits"], f"{r['ratio']:.4f}"] for r in exp]
    c.emit(render.table(["CF terms n", "decimals pinned", "digits / term"],
                        rows, console=c, right_align=[0, 1, 2]))
    ratio = L.lochs_ratio(terms, max_terms=12)
    c.emit("   " + c.style(
        f"this finite pi sample: ~{ratio:.3f} digits per term; the almost-sure "
        f"limit is 1/{L.lochs_constant():.4f} = {1 / L.lochs_constant():.4f}", "result"))
    c.emit()
    _souvenir(c, "The exchange rate is fixed by the arithmetic itself: pi^2/(6 ln2) is the "
                 "entropy of the continued-fraction map, and Lochs' constant is its "
                 "receipt.")


BRANCH_STOPS = [
    ("The Ascending Staircase",
     "Engel expansions: ceilings where the continued fraction takes floors.",
     branch_01_engel),
    ("The Honest Casino",
     "Luroth and Pierce: independent digits, and a rational that loops forever.",
     branch_02_luroth_pierce),
    ("The Greedy Scribe",
     "Egyptian fractions and the Erdos-Straus conjecture, still open.",
     branch_03_egyptian),
    ("The Fibonacci Register",
     "Zeckendorf's non-consecutive sums and the base-phi number system.",
     branch_04_zeckendorf),
    ("The Ticker Tape",
     "Ostrowski numeration, Sturmian words, and Beatty sequences.",
     branch_05_ostrowski),
    ("The Exchange Rate",
     "Lochs' theorem: decimal digits into continued-fraction terms.",
     branch_06_lochs),
]
