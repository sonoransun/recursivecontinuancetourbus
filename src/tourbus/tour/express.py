"""The Express Line: nine fringe stops past the end of the main route.

These are the deeper, stranger avenues — the Markov spectrum, continuants,
algebraic irrationals, alternative continued fractions, the three-distance
theorem, the Gauss-Kuzmin-Wirsing constant, the elastic collisions that
count out the digits of pi, Conway's topograph river, and Ramanujan's
q-continued fraction. Each still computes live on the exact engine. Reached
with ``python -m tourbus frontier``.
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


def express_08_river(c: Console) -> None:
    from ..numbertheory import topograph as T
    from ..cf.expand import cf_from_quadratic

    c.paragraph("Conway drew the values of x^2 - d y^2 not as a formula but as a "
                "landscape. Each region of an infinite trivalent tree carries the "
                "value of the form on a primitive vector, and the numbers grow "
                "outward by one arithmetic rule. Running through it all is the RIVER: "
                "the unique path with positive country on one bank and negative on the "
                "other -- and the river is exactly the periodic continued fraction of "
                "sqrt(d) from Stop 6.")
    c.emit()
    d = 7
    _subhead(c, f"Live: the river of x^2 - {d} y^2")
    for row in T.topograph_strip(d):
        c.emit("   " + c.style(row, "result"))
    _subhead(c, "Live: the river IS the continued fraction of sqrt(d)")
    period = T.river_period(d)
    head, cf_period = cf_from_quadratic(0, d, 1)
    c.emit("   " + c.style(f"river period {period}", "result"))
    c.emit("   " + c.style(f"sqrt({d}) = [{head[0]}; {', '.join(str(t) for t in cf_period)}, ...] "
                           f"-- same sequence.", "result"))
    _subhead(c, "Live: a well on the river (Q = 1) is a Pell solution")
    x, y = T.pell_from_river(d)
    c.emit("   " + c.style(f"fundamental solution ({x}, {y}): {x}^2 - {d}*{y}^2 = "
                           f"{x * x - d * y * y}", "result"))
    _subhead(c, "Live: the same tree-walk runs the Markov triples")
    c.emit("   " + c.style(f"Vieta neighbors of (1,2,5): {T.markov_edge((1, 2, 5))}", "result"))
    c.emit("   " + c.style("replace one value by a linear function of the others -- the "
                           "topograph move and the Markov move (E1) are cousins.", "chrome"))
    c.emit()
    _souvenir(c, "Pell, the continued fraction of sqrt(d), and the Markov spectrum are "
                 "three views of one river through Conway's landscape of forms.")


def express_09_ramanujan(c: Console) -> None:
    from ..frontier import ramanujan as R
    from fractions import Fraction

    c.paragraph("In his first letter to Hardy in 1913, Ramanujan wrote down a "
                "continued fraction and its value, with no proof, that Hardy said "
                "'defeated me completely; I had never seen anything in the least like "
                "them before.' It is the Rogers-Ramanujan fraction -- a q-continued "
                "fraction whose partial numerators are powers of q -- and at "
                "q = e^(-2*pi) the whole infinite object collapses to the golden ratio.")
    c.emit()
    _subhead(c, "Live: the Rogers-Ramanujan fraction R(q) at q = 1/2, exact convergents")
    convs = R.rogers_ramanujan_convergents(Fraction(1, 2), 8)
    c.emit("   " + c.style("R(q)/q^(1/5) = 1/(1 + q/(1 + q^2/(1 + q^3/(1 + ...))))", "result"))
    c.emit("   " + c.style(", ".join(str(f) for f in convs[:6]) + ", ...", "result"))
    c.emit("   " + c.style(f"converging to {float(convs[-1]):.8f}", "chrome"))
    _subhead(c, "Live: Ramanujan's gift to Hardy -- R(e^(-2*pi)) is built from phi")
    cf, closed, err = R.rogers_ramanujan_golden()
    c.emit("   " + c.style(f"from the continued fraction: {cf:.12f}", "result"))
    c.emit("   " + c.style(f"closed form sqrt((5+sqrt5)/2) - phi: {closed:.12f}", "result"))
    c.emit("   " + c.style(f"agree to {err:.1e} -- the infinite fraction IS that surd.", "success"))
    _subhead(c, "Live: Ramanujan's nested radical, 3 = sqrt(1 + 2 sqrt(1 + 3 sqrt(...)))")
    rows = [[d, f"{R.ramanujan_nested_radical(d):.9f}"] for d in (1, 3, 6, 12, 24)]
    c.emit(render.table(["depth", "value -> 3"], rows, console=c, right_align=[0, 1]))
    c.emit("   " + c.style("a puzzle he posed in 1911 that the Journal left unanswered; "
                           "the general form gives x+1.", "chrome"))
    c.emit()
    _souvenir(c, "The golden ratio of Stop 4 returns as the value of an infinite "
                 "q-fraction -- Ramanujan saw the identity whole, and the proof came "
                 "later.")


EXPRESS_STOPS = [
    ("The Markov Spectrum", "The numbers that come after the golden ratio.", express_01_markov),
    ("Continuants", "The polynomial hiding inside every convergent.", express_02_continuants),
    ("Algebraic Irrationals", "Cube roots, the plastic number, and an open problem.", express_03_algebraic),
    ("Continued Fraction Variants", "Nearest-integer and Hirzebruch-Jung expansions.", express_04_variants),
    ("The Three-Distance Theorem", "A surprise in the orbit of an irrational rotation.", express_05_three_distance),
    ("The Gauss-Kuzmin-Wirsing Constant", "Computed from scratch via the transfer operator.", express_06_gkw),
    ("Physics: Colliding Blocks Count Pi", "Where arithmetic, rotation, and mechanics meet.", express_07_physics),
    ("The River", "Conway's topograph: the river is the continued fraction of sqrt(d).", express_08_river),
    ("Ramanujan's Continued Fraction", "The Rogers-Ramanujan fraction and a golden-ratio miracle.", express_09_ramanujan),
]
