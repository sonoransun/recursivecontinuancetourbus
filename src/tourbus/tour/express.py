"""The Express Line: six fringe stops past the end of the main route.

These are the deeper, stranger avenues — the Markov spectrum, continuants,
algebraic irrationals, alternative continued fractions, the three-distance
theorem, and the Gauss-Kuzmin-Wirsing constant. Each still computes live on the
exact engine. Reached with ``python -m tourbus frontier``.
"""

from __future__ import annotations

from fractions import Fraction

from .termio import Console
from . import render


def _subhead(c: Console, text: str) -> None:
    c.emit(" " + c.style(text, "title"))


def _souvenir(c: Console, text: str) -> None:
    c.emit(" " + c.style(f"{c.glyphs.star} souvenir: ", "marker") + c.style(text, "chrome"))
    c.emit()


# --------------------------------------------------------------------------- #

def express_01_markov(c: Console) -> None:
    from ..frontier import markov as M

    c.paragraph("The golden ratio is the hardest number to approximate, guarded by "
                "Hurwitz's constant sqrt(5). But what is second-hardest? The answer is a "
                "discrete ladder -- the Lagrange spectrum below 3 -- run by the solutions "
                "of the Markov equation x^2 + y^2 + z^2 = 3xyz.")
    c.emit()
    _subhead(c, "Live: Markov triples grow from (1,1,1) by Vieta jumping")
    c.emit("   " + c.style(str(M.markov_triples(30)), "result"))
    _subhead(c, "Live: the Lagrange numbers L_m = sqrt(9m^2 - 4)/m climb toward 3")
    rows = []
    for m in M.markov_numbers(200):
        L = M.lagrange_number(m)
        rows.append([m, str(L), f"{float(L):.6f}"])
    c.emit(render.table(["Markov m", "L_m", "value"], rows, console=c, right_align=[0, 2]))
    c.emit()
    _subhead(c, "Live: the Markov value of a periodic CF word equals L_m")
    for m in (1, 2, 5):
        w = M.extremal_cf(m)
        c.emit("   " + c.style(
            f"word {w}: markov_value = {M.markov_value(w):.6f}  (= L_{m} = {float(M.lagrange_number(m)):.6f})",
            "result"))
    c.emit()
    _souvenir(c, "phi (all 1s) sits at sqrt(5); the silver ratio (all 2s) at sqrt(8); "
                 "above Freiman's constant ~4.528 the spectrum becomes a solid ray.")


def express_02_continuants(c: Console) -> None:
    from ..frontier import continuants as K

    c.paragraph("The convergent numerators and denominators are values of one family of "
                "polynomials -- the continuants K(a_1, ..., a_n) -- obeying the very same "
                "recurrence. They are palindromic and count tilings.")
    c.emit()
    _subhead(c, "Live: K(1,1,...,1) is a Fibonacci number")
    rows = [[n, "1 " * n, K.continuant([1] * n)] for n in range(1, 9)]
    c.emit(render.table(["n ones", "word", "K = F(n+1)"], rows, console=c, right_align=[0, 2]))
    _subhead(c, "Live: Euler's rule (matchings) agrees with the recurrence")
    for seq in ([3, 7], [2, 3, 4], [1, 2, 3, 4, 5]):
        c.emit("   " + c.style(
            f"K{tuple(seq)} = {K.continuant(seq)} (recurrence) = {K.continuant_euler(seq)} (Euler)",
            "result"))
    _subhead(c, "Live: the convergent 355/113 is a pair of continuants")
    p, q = K.convergent_via_continuants([3, 7, 15, 1])
    c.emit("   " + c.style(f"K(3,7,15,1) / K(7,15,1) = {p}/{q}", "result"))
    c.emit()
    _souvenir(c, "Palindrome identity: K(a_1..a_n) = K(a_n..a_1) -- reverse the quotients "
                 "and the numerator is unchanged.")


def express_03_algebraic(c: Console) -> None:
    from ..frontier import algebraic as A
    from ..cf.constants import sqrt_cf

    c.paragraph("Quadratic irrationals have periodic continued fractions. Cube roots do "
                "not -- and nobody knows whether their partial quotients stay bounded. "
                "Numerically they look like a 'random' real, unlike the tidy loop of sqrt(d).")
    c.emit()
    _subhead(c, "Live: the cube root of 2 (no pattern known)")
    c.emit("   " + c.style(str(A.cube_root_cf(2).terms(14)) + " ...", "result"))
    _subhead(c, "Live: the plastic number (root of x^3 = x + 1) and its famous 141")
    c.emit("   " + c.style(str(A.plastic_number_cf().terms(13)) + " ...", "result"))
    _subhead(c, "Live: statistics -- algebraic looks Khinchin-typical, quadratic does not")
    for name, cf in [("cbrt(2)", A.cube_root_cf(2, digits=90)),
                     ("plastic", A.plastic_number_cf(digits=90)),
                     ("sqrt(2)", sqrt_cf(2))]:
        s = A.partial_quotient_stats(cf, 40)
        c.emit("   " + c.style(
            f"{name:>8}: max term {s['max']:>4}, geometric mean {s['geometric_mean']:.3f}",
            "result"))
    c.emit()
    _souvenir(c, "Whether cbrt(2) has bounded partial quotients is OPEN -- a cousin of the "
                 "Littlewood conjecture.")


def express_04_variants(c: Console) -> None:
    from ..frontier import variants as V

    c.paragraph("The floor is not the only way to unfold a number. The nearest-integer "
                "continued fraction rounds to the closest integer (allowing negatives) and "
                "converges faster; the 'minus' continued fraction uses only a_i >= 2 and is "
                "the language of resolving singularities.")
    c.emit()
    x = Fraction(87, 32)
    _subhead(c, f"Live: three expansions of {x}")
    c.emit("   " + c.style(f"regular:          {V.regular_cf(x)}", "result"))
    c.emit("   " + c.style(f"nearest-integer:  {V.nearest_integer_cf(x)}  (shorter, with a negative)", "result"))
    c.emit("   " + c.style(f"minus (a_i>=2):   {V.minus_cf(x)}", "result"))
    _subhead(c, "Live: every expansion folds back to the same number")
    for name, terms, ev in [
        ("regular", V.regular_cf(x), V.eval_regular_cf),
        ("NICF", V.nearest_integer_cf(x), V.eval_nearest_integer_cf),
        ("minus", V.minus_cf(x), V.eval_minus_cf),
    ]:
        c.emit("   " + c.style(f"{name:>7}: {ev(terms)}", "result"))
    c.emit()
    _souvenir(c, "The minus-CF partial quotients are the self-intersection numbers of the "
                 "curves that resolve a cyclic quotient singularity.")


def express_05_three_distance(c: Console) -> None:
    from ..frontier import three_distance as T

    c.paragraph("Scatter the points 0, a, 2a, ..., (N-1)a around a circle (mod 1). However "
                "you choose a and N, they cut the circle into arcs of at most THREE distinct "
                "lengths -- and the largest is the sum of the other two. The continued "
                "fraction of a is what controls it.")
    c.emit()
    for alpha, N in [(Fraction(5, 8), 6), (Fraction(8, 13), 12), (Fraction(13, 21), 20)]:
        rep = T.three_distance_report(alpha, N)
        lengths = ", ".join(str(g) for g in rep["distinct_lengths"])
        c.emit("   " + c.style(
            f"a={alpha}, N={N}: {rep['num_distinct']} gap lengths [{lengths}], "
            f"largest = sum of others: {rep['largest_is_sum']}", "result"))
    c.emit()
    _souvenir(c, "Steinhaus conjectured it; the gaps are ||q_k * a|| at the convergent "
                 "denominators -- approximation and equidistribution, the same story.")


def express_06_gkw(c: Console) -> None:
    from ..frontier import gkw

    c.paragraph("How fast does Gauss-Kuzmin converge? The rate is the second eigenvalue of "
                "the Gauss map's transfer operator (Lf)(x) = sum 1/(n+x)^2 f(1/(n+x)) -- the "
                "Gauss-Kuzmin-Wirsing constant, with no known closed form.")
    c.emit()
    _subhead(c, "Live: computing it from scratch (power iteration on the operator)")
    lead = gkw.leading_eigenvalue(grid=200, terms=1000, iters=45)
    lam = gkw.second_eigenvalue(grid=280, terms=1500, iters=70)
    c.emit("   " + c.style(f"leading eigenvalue  = {lead:.6f}   (exactly 1, a sanity check)", "result"))
    c.emit("   " + c.style(f"GKW constant lambda = {lam:.7f}", "result"))
    c.emit("   " + c.style(f"Wirsing's value     = {gkw.GKW_CONSTANT:.7f}   "
                           f"(error {abs(lam - gkw.GKW_CONSTANT):.1e})", "chrome"))
    c.emit()
    _souvenir(c, "The error in the Gauss-Kuzmin theorem shrinks like |lambda|^n ~ 0.30^n -- "
                 "and that 0.30 is still not known in closed form.")


def express_07_physics(c: Console) -> None:
    from ..frontier import physics as P

    c.paragraph("A closing bridge from arithmetic to the physical world. Put a small "
                "block between a wall and a big one; send the big block in; count every "
                "elastic collision. Galperin's theorem: if the mass ratio is 100^n, the "
                "number of collisions is the first n+1 digits of pi.")
    c.emit()
    _subhead(c, "Live: two blocks, counted collisions = the digits of pi")
    rows = []
    for n in range(6):
        rows.append([f"100^{n}", str(P.galperin_collisions(n)), str(P.pi_prefix(n))])
    c.emit(render.table(["mass ratio", "collisions (simulated)", "digits of pi"],
                        rows, console=c, right_align=[1, 2]))
    c.emit("   " + c.style("The dynamics is a billiard in a wedge of angle arctan(sqrt(m/M)); "
                           "the collision count is a rotation number, and pi is the half-turn.",
                           "chrome"))
    c.emit()
    _souvenir(c, "Recursion, rotation, and pi meet in a mechanics problem you could build "
                 "from two bricks -- see Appendix E for the whole web of ideas.")


EXPRESS_STOPS = [
    ("The Markov Spectrum", "The numbers that come after the golden ratio.", express_01_markov),
    ("Continuants", "The polynomial hiding inside every convergent.", express_02_continuants),
    ("Algebraic Irrationals", "Cube roots, the plastic number, and an open problem.", express_03_algebraic),
    ("Continued Fraction Variants", "Nearest-integer and Hirzebruch-Jung expansions.", express_04_variants),
    ("The Three-Distance Theorem", "A surprise in the orbit of an irrational rotation.", express_05_three_distance),
    ("The Gauss-Kuzmin-Wirsing Constant", "Computed from scratch via the transfer operator.", express_06_gkw),
    ("Physics: Colliding Blocks Count Pi", "Where arithmetic, rotation, and mechanics meet.", express_07_physics),
]
