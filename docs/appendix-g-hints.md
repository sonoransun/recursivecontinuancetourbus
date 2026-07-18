[← Route map](index.md) · [Appendix B — Glossary](appendix-b-glossary.md) · [Appendix D — The Express Line](appendix-d-frontier.md) · [Appendix H — The Heritage Line](appendix-h-history.md) · [Appendix I — The Branch Line](appendix-i-branches.md)

# Appendix G — Hints & selected answers

Every stop on the route ends with five graded exercises, and each carries a
one-line hint behind a fold. This appendix goes further: for the exercises with
crisp, closed-form answers it gives the **complete worked answer**, and for the
open-ended ones it gives a **genuine hint** — a real nudge, not the solution.
Items marked **Answer** are complete; items marked **Hint** leave the finish to
you. The exercises themselves live at the end of each chapter — see the
[route map](index.md) — and are numbered `1`–`5` with difficulty stars from ★
(warm-up) to ★★★ (a real climb). Wherever a result is computable, it has been
checked against the `tourbus` engine itself.

## Stop 1 — The Depot

**1. (★) Answer.** The gcd is the last nonzero remainder, `21`, and
`1071/462 = 51/22` in lowest terms. Folding the quotients back:
`[2; 3, 7] = 2 + 1/(3 + 1/7) = 2 + 7/22 = 51/22`, exactly the reduced fraction.

**2. (★) Answer.** Nine steps. `(89, 55) = (F₁₁, F₁₀)`, and the smallest pair
needing `n` steps is `(F₍ₙ₊₂₎, F₍ₙ₊₁₎)` — so `n = 9`, one more than the eight
steps `(55, 34) = (F₁₀, F₉)` took. The demo confirms it: every quotient is `1`
until the final `2`.

**3. (★★) Answer.** Back-substitute through the division ladder:
`21 = 462 − 3·147` and `147 = 1071 − 2·462`, so
`21 = 462 − 3·(1071 − 2·462) = 7·462 − 3·1071`. Hence `x = −3`, `y = 7`; check:
`1071·(−3) + 462·7 = −3213 + 3234 = 21`. ✓

**4. (★★) Answer.** Since `F₍ₙ₊₁₎ = 1·Fₙ + F₍ₙ₋₁₎` with `0 ≤ F₍ₙ₋₁₎ < Fₙ` (for
`n ≥ 3`), one division step turns the pair `(F₍ₙ₊₁₎, Fₙ)` into `(Fₙ, F₍ₙ₋₁₎)`.
The algorithm walks straight down the sequence to `gcd(F₂, F₁) = gcd(1, 1) = 1`,
so consecutive Fibonacci numbers are always coprime.

**5. (★★★) Answer sketch.** If the algorithm takes `k` steps on `(a, b)` then
`b ≥ F₍ₖ₊₁₎` (Lamé's worst case, run in reverse). Binet gives
`F₍ₖ₊₁₎ ≈ φᵏ⁺¹/√5`, so `φᵏ⁺¹ ≲ b√5` and `k < log_φ(b√5)`. For the factor of
five, sharpen to the exact bound `F₍ₖ₊₁₎ ≥ φᵏ⁻¹` (induction on the
recurrence): then `k − 1 ≤ log_φ b`, and if `b` has `D` decimal digits,
`log₁₀ b < D` gives `k − 1 < D/log₁₀ φ ≈ 4.785·D < 5D`. Since `k` is an
integer, `k − 1 < 5D` forces `k ≤ 5D` — Lamé's factor of five, with the
constant `4.785 = 1/log₁₀ φ` exactly as advertised at the Depot.

## Stop 2 — The Unfolding Road

**1. (★) Answer.** Work inside-out from the last term: `12 + 1/4 = 49/4`, then
`4 + 4/49 = 200/49`, then `3 + 49/200 = 649/200 = 3.245`. Check:
`demo cf 649/200` prints `[3; 4, 12, 4]`.

**2. (★) Answer.** `9/7 = 1 + 2/7` and `7/2 = 3 + 1/2`, so `9/7 = [1; 3, 2]`;
splitting the final term gives the twin representation `[1; 3, 1, 1]`.

**3. (★★) Answer.** `[0; a₁, a₂, …] = 0 + 1/(a₁ + 1/(a₂ + …)) = 1/[a₁; a₂, …]`
— prepending a zero *is* taking the reciprocal. So `demo cf 93/415` prints
`[0; 4, 2, 6, 7]`: the road of `415/93` with a `0` bolted on the front.

**4. (★★) Answer.** At every step the leftover `xₙ − aₙ = xₙ − ⌊xₙ⌋` lies in
`[0, 1)`. If it is zero the expansion stops; otherwise its reciprocal `xₙ₊₁`
exceeds `1`, so the next floor `aₙ₊₁ = ⌊xₙ₊₁⌋` is at least `1`. A zero quotient
after the first term is impossible.

**5. (★★★) Answer sketch.** Write `xₙ = uₙ/vₙ` in lowest terms with `vₙ > 0`.
Then `xₙ − aₙ = (uₙ mod vₙ)/vₙ`, so `xₙ₊₁ = vₙ/(uₙ mod vₙ)` — a fraction whose
denominator `uₙ mod vₙ` is a *strictly smaller* positive integer than `vₙ`. A
strictly decreasing sequence of positive integers must reach `0`, and when it
does the expansion terminates. This is Euclid's termination argument (Stop 1),
word for word.

## Stop 3 — The Engine Room

**1. (★) Answer.** `355·106 − 333·113 = 37630 − 37629 = +1`, and with `n = 3`
the predicted sign is `(−1)² = +1`. ✓

**2. (★) Answer.** `p₃ = a₃·p₂ + p₁ = 1·333 + 22 = 355` and
`q₃ = a₃·q₂ + q₁ = 1·106 + 7 = 113`.

**3. (★★) Answer.** `1/(q₃·q₄) = 1/(113·33102) = 1/3740526 ≈ 2.673e−7`, against
the table's `2.67e−07` — the bound is not merely within an order of magnitude
here, it is essentially exact, because the complete quotient `x₄` barely exceeds
`a₄ = 292`.

**4. (★★) Answer.** Base cases: `q₀ = 1 = F₁` and `q₁ = a₁ ≥ 1 = F₂`. Step:
`qₙ = aₙqₙ₋₁ + qₙ₋₂ ≥ qₙ₋₁ + qₙ₋₂ ≥ Fₙ + F₍ₙ₋₁₎ = F₍ₙ₊₁₎`, using `aₙ ≥ 1` and
the induction hypothesis twice. ∎

**5. (★★★) Answer.** The determinant identity *is* the neighbour condition:
`pₙqₙ₋₁ − pₙ₋₁qₙ = ±1` is exactly `bc − ad = 1` for the pair written in
increasing order. So consecutive convergents are Farey neighbours, and the
mediant machinery of [Stop 8](08-family-tree.md) applies to them: each
convergent is reached from the previous two by repeated mediants, which is why
descending the Stern–Brocot tree and running the expansion are the same walk.

## Stop 4 — The Golden Milestone

**1. (★) Answer.** `13·5 − 8·8 = 65 − 64 = +1`, matching `(−1)⁴` at `n = 5`. ✓

**2. (★) Answer.** `1/1.618034 ≈ 0.618034` and `1 + 0.618034 = 1.618034`. The
identity `1/φ = φ − 1` is the fixed-point equation rearranged — the same fact
that makes the golden angle `360°/φ² = 360°(2 − φ)` well defined.

**3. (★★) Answer.** From Binet,

```
F₍ₙ₊₁₎/Fₙ − φ = (φⁿ⁺¹ − ψⁿ⁺¹)/(φⁿ − ψⁿ) − φ
             = ψⁿ(φ − ψ)/(φⁿ − ψⁿ) ≈ √5·(ψ/φ)ⁿ.
```

Since `φψ = −1`, `ψ/φ = −ψ²`, so the error is `O(|ψ|²ⁿ)` with
`ψ² = (3 − √5)/2 ≈ 0.382` — each convergent multiplies the error by roughly
`0.382`, exactly the reluctant decay the worked example's table shows.

**4. (★★) Answer.** `s = 2 + 1/s` gives `s² − 2s − 1 = 0`, so
`s = 1 + √2 ≈ 2.41421`. The convergents are `2/1, 5/2, 12/5, 29/12, …`: the
denominators `1, 2, 5, 12, 29` are the Pell numbers, and the numerators are the
same sequence shifted by one — precisely as Fibonacci serves `φ`. The Pell link
is exact: for each convergent `p/q`, the pair `(p − q, q)` solves
`x² − 2y² = ±1` of [Stop 7](07-cattle-crossing.md) — `(1, 1): −1`,
`(3, 2): +1`, `(7, 5): −1`, `(17, 12): +1`, alternating forever.

**5. (★★★) Hint.** If `x` and `φ` share the same infinite tail of `1`s, each is
a homographic image of that common tail: `x = (a·t + b)/(c·t + d)` where the
matrix is a product of convergent matrices `[[aᵢ, 1], [1, 0]]`, every one of
determinant `−1`. Compose one map with the inverse of the other to relate `x`
directly to `φ` by a unimodular transformation. Then check that
`lim inf q²|x − p/q|` is invariant under such maps (compare Appendix A's error
formula before and after the change of variable) — so `x` inherits `φ`'s
extremal constant `1/√5`.

## Stop 5 — Scenic Overlook

**1. (★) Answer.** `|0.2425 − 0.2422| = 3.0e−4` but
`|8/33 − 0.2422| ≈ 2.2e−4`: the 900-year-old Jalali rule is the more accurate.
A mathematician takes `8/33`; civil society took `97/400` because "no leap year
on century boundaries except every 400" survives being taught to children.

**2. (★) Answer.** `1/(2·113²) = 1/25538 ≈ 3.9e−5`, and the actual error is
`2.67e−7` — over a hundred times smaller. Legendre's criterion is met with room
to spare, so `355/113` must be (and is) a convergent.

**3. (★★) Answer.** The convergents of `√2` are
`1, 3/2, 7/5, 17/12, 41/29, 99/70, 239/169, …`; the last with denominator at
most `100` is `99/70`, with `|√2 − 99/70| ≈ 7.2e−5`. Lagrange's theorem says no
fraction with denominator `≤ 70` comes closer in the `|qx − p|` sense — `99/70`
is unbeatable until `239/169` arrives — though in plain absolute distance the
semiconvergent `140/99` sneaks (barely) ahead: `7.21482e−5` against `99/70`'s
`7.21519e−5`.

**4. (★★) Answer.** The convergents with both parts under 50 teeth are `17/12`
and `41/29`. Errors: `|√2 − 17/12| ≈ 2.5e−3` versus `|√2 − 41/29| ≈ 4.2e−4` —
cut gears of 41 and 29 teeth, six times more accurate for the same workshop.

**5. (★★★) Hint.** Expand `p/q` as a finite continued fraction and use the
two-representations freedom (Stop 2) to choose the parity of its last index `n`
so that `x − p/q` has the sign `(−1)ⁿ`. Then define `ω` by
`x = (ω·pₙ + pₙ₋₁)/(ω·qₙ + qₙ₋₁)` and solve for `ω`; show the hypothesis
`|x − p/q| < 1/(2q²)` forces `ω > 1`. A tail value greater than `1` is exactly
what makes `pₙ/qₙ` a genuine convergent of `x`. (This is the engine of Wiener's
attack at [Stop 14](14-souvenir-shop.md).)

## Stop 6 — The Loop Road

**1. (★) Answer.** `√2 = [1; (2)]`: block `2`, empty palindrome, cap
`2 = 2⌊√2⌋`. `√3 = [1; (1, 2)]`: palindrome `1`, cap `2 = 2⌊√3⌋`.
`√7 = [2; (1, 1, 1, 4)]`: palindrome `1, 1, 1`, cap `4 = 2⌊√7⌋`. The last term
of the block of `√d` is always `2⌊√d⌋` = twice the lead-in.

**2. (★) Answer.** `[1; (1)]`: `x = 1 + 1/x`, so `x² − x − 1 = 0` and
`x = (1 + √5)/2 = φ`. `[2; (2)]`: `x = 2 + 1/x`, so `x² − 2x − 1 = 0` and
`x = 1 + √2`, the silver ratio.

**3. (★★) Answer.** `a₀ = ⌊√7⌋ = 2`. Then `P₁ = a₀Q₀ − P₀ = 2·1 − 0 = 2`,
`Q₁ = (7 − P₁²)/Q₀ = (7 − 4)/1 = 3`, and `a₁ = ⌊(2 + √7)/3⌋ = ⌊1.548⌋ = 1`.
Next `P₂ = a₁Q₁ − P₁ = 3 − 2 = 1`, `Q₂ = (7 − 1)/3 = 2`, and
`a₂ = ⌊(1 + √7)/2⌋ = ⌊1.823⌋ = 1`. Integers throughout — the division in the
`Q`-recurrence always comes out exact.

**4. (★★) Answer.** `φ ≈ 1.618 > 1`, and its conjugate `(1 − √5)/2 ≈ −0.618`
lies strictly in `(−1, 0)`. Both of Galois' conditions hold, so `φ` is reduced
and its expansion is purely periodic — indeed `[(1)]`, with no lead-in at all.

**5. (★★★) Hint.** Once the expansion is past its lead-in, show by induction
that `0 < Pₙ < √d` and `0 < Qₙ < 2√d`, using the identity
`QₙQₙ₊₁ = d − Pₙ₊₁²` to keep the signs and sizes under control. That confines
`(Pₙ, Qₙ)` to fewer than `2d` states; by pigeonhole some state recurs, and the
recurrences are deterministic, so from that point the road repeats forever.
Appendix A carries out the estimates.

## Stop 7 — The Cattle Crossing

**1. (★) Answer.** `3² − 2·2² = 9 − 8 = 1`. Squaring the unit:
`(3 + 2√2)² = 17 + 12√2`, so the next solution is `(17, 12)`, and
`17² − 2·12² = 289 − 288 = 1`. ✓

**2. (★) Answer.** `√2 = [1; (2)]` has period `ℓ = 1`, which is odd: the
convergent one term shy of the period's cap, `p₀/q₀ = 1/1`, gives the `−1`
equation (`1² − 2·1² = −1`), and completing the period at `p₁/q₁ = 3/2` —
equivalently, squaring that unit — gives the fundamental `+1` solution
`(x, y) = (3, 2)` the exercise asks to confirm.

**3. (★★) Answer.** Odd period means `x² − 13y² = −1` is solvable. The smallest
solution is `(18, 5)`: `18² − 13·5² = 324 − 325 = −1`. Squaring the unit,
`(18 + 5√13)² = 649 + 180√13`, recovers the fundamental `+1` solution
`(649, 180)` the demo prints.

**4. (★★) Answer.** `4` is a perfect square, so `√4 = 2` is rational, its
continued fraction `[2]` terminates, and there is no period to read a solution
from. Algebraically, `x² − 4y² = (x − 2y)(x + 2y) = 1` forces both factors to
be `±1`, so `(x, y) = (1, 0)` is the only non-negative solution.

**5. (★★★) Hint.** The norm `N(x + y√d) = x² − dy²` is multiplicative, so
solutions of `+1` form a group under multiplication in `ℤ[√d]`. Let
`u = x₁ + y₁√d > 1` be fundamental and `v > 1` any positive solution; choose the
integer `k` with `uᵏ ≤ v < uᵏ⁺¹` and show `v·u⁻ᵏ` is again a solution lying in
`[1, u)` — which forces `v·u⁻ᵏ = 1` by minimality of `u`. Hence `v = uᵏ`.

## Stop 8 — The Family Tree

**1. (★) Answer.** `mediant(1/2, 2/3) = (1+2)/(2+3) = 3/5`, and
`1/2 < 3/5 < 2/3`. It is automatically in lowest terms: for Farey neighbours
the unit determinant `bc − ad = 1` passes to the mediant, so no common factor
can survive.

**2. (★) Answer.** The address is `RLRL`: run-lengths `1, 1, 1, 1`. Adding one
to the final run gives `[1; 1, 1, 2]`, which is `8/5` — and equals
`[1; 1, 1, 1, 1]`, the all-ones representation, by the two-faces rule of
Stop 2. The alternating single letters are the string of `1`s made visible.

**3. (★★) Answer.** `b·c − a·d = 5·3 − 2·7 = 15 − 14 = 1`. ✓ `2/5` and `3/7`
are Farey neighbours in `F₇`, and their mediant `5/12` is the first fraction to
appear between them (in `F₁₂`).

**4. (★★) Answer.** `fusc(0..8) = 0, 1, 1, 2, 1, 3, 2, 3, 1`, so the ratios for
`n = 1, …, 7` are `1/1, 1/2, 2/1, 1/3, 3/2, 2/3, 3/1` — seven distinct
rationals, each in lowest terms, exactly the breadth-first reading of the
Calkin–Wilf tree.

**5. (★★★) Answer.** With every `aₖ = 1` the exponents in the series are the
partial sums `1, 2, 3, …`, so

```
?(1/φ) = 2·(2⁻¹ − 2⁻² + 2⁻³ − …) = 2 · (1/2)/(1 + 1/2) = 2/3,
```

a geometric series with ratio `−1/2`. The most irrational number's reciprocal
lands on the plainest of rationals — the question-mark function doing exactly
its job of rationalising quadratic irrationals.

## Stop 9 — Celebrity Sightings

**1. (★) Answer.** Euler's blocks `1, 2k, 1` continue with `k = 3, 4, 5`:
`a₈ … a₁₄ = 6, 1, 1, 8, 1, 1, 10` (indexing from `a₀ = 2`, as in the demo's
table). The printed head `[2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, …]`
confirms every one.

**2. (★) Answer.** Only rationals have finite continued fractions (Stop 2), and
Euler's pattern — even terms `2, 4, 6, …` climbing forever — manifestly never
terminates, so `e` is irrational.

**3. (★★) Answer.** Truncating Brouncker after one, two, three, four odd
squares gives `4/π ≈ 3/2, 15/13, 105/76, 315/263`, i.e.
`π ≈ 8/3 ≈ 2.667, 52/15 ≈ 3.467, 304/105 ≈ 2.895, 1052/315 ≈ 3.340`. After four
terms the error is still `0.2` — the regular convergent `22/7` (error
`1.3e−3`) beats all of them with a single division, and `355/113` is out of
reach for hundreds of Brouncker terms. Beautiful pattern, dreadful convergence.

**4. (★★) Answer.** The first convergent is `x = π/4 ≈ 0.7854`; the second is
`x/(1 − x²/3) = 3x/(3 − x²) ≈ 0.9887`. Two terms in and Lambert's fraction is
already within `1.2%` of `tan(π/4) = 1`.

**5. (★★★) Hint.** Suppose `x = p/q` is rational and nonzero. Feed it into
Lambert's fraction and clear denominators level by level: the tails satisfy an
integer recurrence whose values are forced to be nonzero yet strictly
decreasing in absolute value — an infinite descent, which is impossible. So
`tan(x)` is irrational for every rational `x ≠ 0`; since `tan(π/4) = 1` is
rational, `π/4` cannot be rational. The full argument is in the sources of
[Appendix C](appendix-c-references.md).

## Stop 10 — The Casino

**1. (★) Answer.** `log₂(1 + 1/(1·3)) = log₂(4/3) ≈ 0.4150`,
`log₂(1 + 1/(2·4)) = log₂(9/8) ≈ 0.1699`,
`log₂(1 + 1/(3·5)) = log₂(16/15) ≈ 0.0931` — matching the demo's `predict`
column digit for digit.

**2. (★) Answer.** `1/x = √2 ≈ 1.41421`, so `a₁ = 1` and
`T(x) = 0.41421…`; then `1/T(x) ≈ 2.41421`, so `a₂ = 2`. (Indeed
`1/√2 = [0; 1, 2, 2, 2, …]` — the reciprocal rule of Stop 2 applied to
`√2 = [1; (2)]`, after which the orbit is stuck on the silver tail forever.)

**3. (★★) Answer.** The first nine terms `2, 1, 2, 1, 1, 4, 1, 1, 6` multiply
to `96`, whose ninth root is `≈ 1.66`; through `a₁₁` (adding `1, 1, 8`) the mean
is already `≈ 1.74`, and it keeps climbing. The even terms `2k` grow without
bound, and `(2·4·6·…)^{1/n}` diverges, so `e`'s geometric mean goes to infinity
instead of `K₀` — `e` is a measure-zero exception, visibly.

**4. (★★) Hint.** The limit exists because `Σ log aₙ / n` obeys the ergodic
theorem, but the summands are heavy-tailed: `P(aₙ ≥ k) ≈ log₂(1 + 1/k)` decays
only like `1/k`, so `log aₙ` has large variance and rare giant terms move the
running mean for a long time. Estimate how much a single term `aₙ = 1000`
shifts the geometric mean of `n = 10⁴` terms and compare with the `1%` gap in
the demo.

**5. (★★★) Answer.** Substitute `ρ(x) = 1/(1+x)` (the normalisation `1/ln 2`
cancels from both sides):

```
Σ_{k≥1} ρ(1/(x+k)) · 1/(x+k)²
  = Σ_{k≥1} (x+k)/(x+k+1) · 1/(x+k)²
  = Σ_{k≥1} 1/((x+k)(x+k+1))
  = Σ_{k≥1} [1/(x+k) − 1/(x+k+1)]
  = 1/(x+1) = ρ(x).
```

The sum telescopes, and the Gauss density is exactly the fixed point of the
transfer operator — the same operator whose *second* eigenvalue is the
Gauss–Kuzmin–Wirsing constant of
[Appendix D, stop E6](appendix-d-frontier.md). ∎

## Stop 11 — The Infinite Assembly Line

**1. (★) Answer.** `[3, 6, 1, 5] = 3 + 1/(6 + 1/(1 + 1/5)) = 129/41 ≈ 3.14634`,
against `√2 + √3 ≈ 3.14626` — agreement to four decimal places from four terms,
exactly the quadratic accuracy Stop 3 promises.

**2. (★) Answer.** `√2·√3 = √6` is a root of `x² − 6 = 0`, a quadratic surd, so
Lagrange's theorem (Stop 6) forces a periodic expansion: `√6 = [2; (2, 4)]`,
its block capped by `4 = 2⌊√6⌋`. The machine's output
`[2, 2, 4, 2, 4, …]` is that period, discovered term by term.

**3. (★★) Answer.** The state is `(a, b, c, d) = (2, 1, 1, 3)`. Ingesting
`p = 3` maps it to `(a·p + b, a, c·p + d, c) = (7, 2, 6, 1)` — the machine now
computes `z(x′) = (7x′ + 2)/(6x′ + 1)` for the unread tail `x′`.

**4. (★★) Answer.** `√2·√2 = 2` exactly — a *rational*, hence a finite
continued fraction. To emit that final term the machine must be certain the
fractional part is exactly zero, which no finite number of input terms can
certify: every prefix of `√2`'s expansion is consistent with inputs slightly
above or below `√2`. So it ingests forever. `√2·√3 = √6` is irrational, so
there is always a next term whose value eventually becomes certain, and the
machine emits forever instead.

**5. (★★★) Answer.** The unread tail of the input is known only to lie in an
interval (for regular continued fractions, `[1, ∞)` after each ingest). A
homographic map with the machine's invariants is monotone on that interval, so
the image of the interval is again an interval whose endpoints are `z` evaluated
at the two ends — `a/c` at `∞` and `(a+b)/(c+d)` at `1`. If `⌊z⌋` agrees at both
endpoints, it is constant on the whole image: the next output digit is
determined no matter what the unread input turns out to be. That is exactly
when emitting is safe.

## Stop 12 — The Tower

**1. (★) Answer.** `A(1, 5) = 7` — unrolling `A(1, n) = A(0, A(1, n−1)) =
A(1, n−1) + 1` from `A(1, 0) = A(0, 1) = 2` gives `n + 2`. Similarly
`A(2, 2) = 2·2 + 3 = 7`. The rungs cross at small values before exploding
apart.

**2. (★) Answer.** `A(3, 7) = 2⁷⁺³ − 3 = 2¹⁰ − 3 = 1021`.

**3. (★★) Answer.**
`M(99) = M(M(110)) = M(100) = M(M(111)) = M(101) = 91`. Two levels of nesting,
then the recursion collapses — as it does for *every* start `n ≤ 100`.

**4. (★★) Hint.** For fixed `m`, write the closed form (`n+1`, `n+2`, `2n+3`,
`2ⁿ⁺³−3`) and observe each is built from the previous by a bounded iteration —
primitive recursion suffices. What fails for the two-argument function is the
*diagonal*: show by induction over the construction of primitive recursive
functions that every such `f` satisfies `f(n) < A(m, n)` for some fixed `m` and
all large `n`; then `A(n, n)` outgrows every one of them, so it can equal none.

**5. (★★★) Answer.** One β-reduction:

```
Y f = (λx. f (x x)) (λx. f (x x))
    → f ((λx. f (x x)) (λx. f (x x)))
    = f (Y f).
```

So `Y f` is a fixed point of `f` built from application alone. Give `f` the
shape "one unrolling of a recursive definition, taking *itself* as argument"
and `Y f` behaves as the infinite unrolling — recursion conjured with no named
function anywhere, the `φ = 1 + 1/φ` move performed on functions instead of
numbers.

## Stop 13 — The Hall of Mirrors

**1. (★) Answer.** The carpet is `N = 8` copies (nine cells minus the centre)
at ratio `r = 1/3`, so `d = ln 8 / ln 3 ≈ 1.8928` — denser than the Sierpiński
triangle, still thinner than the plane.

**2. (★) Answer.** Each generation replaces every segment by four segments a
third as long, multiplying total length by `4/3` — so length grows like
`(4/3)ⁿ → ∞`. The area added at generation `n` is a geometric series with
ratio `4/9 < 1` (four times as many new triangles, each `1/9` the area), which
converges. Infinite fence, finite paddock.

**3. (★★) Answer.** The Hilbert curve is `N = 4` half-scale copies of itself
(`r = 1/2`), so `d = ln 4 / ln 2 = 2` — a curve that is, in the limit, exactly
as big as the square it fills.

**4. (★★) Answer.** `f₁(x) = x/3` and `f₂(x) = x/3 + 2/3`, both contracting by
`1/3`. The attractor of `F(S) = f₁(S) ∪ f₂(S)` is the middle-thirds Cantor set:
apply `F` to `[0, 1]` once and you get exactly the two outer thirds, and
Hutchinson's theorem does the rest.

**5. (★★★) Answer.** One period of `[(2)]` gives `x = 1/(2 + x)`, so
`M(x) = 1/(2 + x)` and the fixed-point equation is `x² + 2x − 1 = 0`, whose
positive root is `x = √2 − 1`. It is attracting because
`|M′(x)| = 1/(2 + x)² = 1/(1 + √2)² = (√2 − 1)² ≈ 0.172 < 1` — iterate `M` from
any positive start and you spiral into `√2 − 1`, exactly as any shape spirals
into a fractal attractor.

## Stop 14 — The Souvenir Shop

**1. (★) Answer.** `24/41`, at `+0.484` cents — the 41-note scale is the first
to bring the fifth's error under a cent. (The piano's `7/12` sits at `−1.955`
cents, audible to nobody and playable by everybody.)

**2. (★) Answer.** `demo collatz 97` reports `118` steps with peak `9232` — the
very same peak as `27`, whose flight it joins partway. Collatz orbits funnel:
many starts merge into a common trajectory and share its high-water mark.

**3. (★★) Answer.** The attack needs `k/d` to be a convergent of the public
`e/N`, and Legendre's criterion certifies that exactly when
`|e/N − k/d| < 1/(2d²)`. The gap between `e/N` and `k/d` is governed by
`N − φ(N) ≈ p + q ≈ √N`, giving `|e/N − k/d| ≈ k√N/(dN)`. That is below the
Legendre threshold only when `d ≲ N^{1/4}` — small `d` is precisely what makes
the secret fraction land among the convergents where anyone can pick it up.
Appendix A works the constants.

**4. (★★) Answer.** `12 × 701.955 = 8423.46` cents, versus
`7 × 1200 = 8400` — an overshoot of `23.46` cents, the Pythagorean comma.
Equal temperament spreads it over the twelve fifths: `23.46/12 = 1.955` cents
each, the exact flattening in the `temperament` table.

**5. (★★★) Hint.** Any cycle must consist of numbers that never reach `1`; the
verification (every start below `~2⁶⁸` reaches `1`) therefore rules out any
cycle containing a member below the bound. But a cycle living entirely *above*
the bound, or a divergent orbit, is untouched by finite checking — which is why
`2⁶⁸` starts verified is evidence, not proof. Compare the structure of the
argument with Stop 15's `π` question: no finite computation settles an
infinite-tail property.

## Stop 15 — Terminus

**1. (★) Answer.** No. Any single term, however enormous, is compatible with
the tail being bounded thereafter; unboundedness is a claim about infinitely
many terms. (The largest known early term of `π` is a curiosity, not a
theorem.)

**2. (★) Answer.** A number is irrational exactly when its simple continued
fraction is infinite (Stop 2), so proving `γ` irrational "only" requires
proving its expansion never terminates — the one property continued fractions
are purpose-built to detect. That no one can do it for `γ` is the
embarrassment.

**3. (★★) Answer.** `3/7 = [0; 2, 3]`, all quotients `≤ 3`; and
`7/12 = [0; 1, 1, 2, 2]`, all quotients `≤ 2`. Both denominators have Zaremba
partners well inside `A = 5`.

**4. (★★) Answer.** Dirichlet (via the convergents of Stop 3) gives each `α`
infinitely many `n` with `n·‖nα‖ < 1` — one number at a time. Littlewood asks
for a *single* sequence of `n` along which the product `n·‖nα‖·‖nβ‖` tends to
`0` for **every** pair `α, β` simultaneously: two numbers may each resist, but
(conjecturally) never both at the same denominators. It is Hurwitz's
one-dimensional extremal story (Stop 4) asked in two dimensions.

**5. (★★★) Hint.** There is no single answer — pick the frontier nearest your
favourite stop. The Khinchin, Gauss–Kuzmin, and Littlewood questions extend the
ergodic theory of [Stop 10](10-casino.md); the `π` and `γ` questions extend
[Stop 2](02-unfolding-road.md) and [Stop 9](09-celebrity.md); Zaremba extends
the denominator structure of [Stop 8](08-family-tree.md) and the numerical
applications of [Stop 14](14-souvenir-shop.md). A good paragraph names the
theorem you would need and the obstacle that has stopped everyone so far.

## The Express Line (Appendix D)

The nine express stops carry a compact `**Exercises.**` line each; hints and
answers here follow the same ★ grading.

**E1 — The Markov spectrum.** (★) *Answer.* Take `(1, 2, 5)`:
`1 + 4 + 25 = 30 = 3·1·2·5`. ✓ (★★) *Answer.* For `x = 1 + √2` the convergents
are `2/1, 5/2, 12/5, 29/12, 70/29`, and `q²·|x − p/q|` runs
`0.414, 0.343, 0.355, 0.353, 0.354 → 1/√8 ≈ 0.3536` — so the sharpest constant
is `√8`, the second Lagrange number `L₂ = 2√2`. (★★★) *Hint.* Fix `y, z`: the
Markov equation is a quadratic in `x`, and its two roots satisfy
`x + x′ = 3yz` and `x·x′ = y² + z²`. The second root `x′ = 3yz − x` is an
integer by the sum, and positive by the product — Vieta jumping cannot escape
the positive integers.

**E2 — Continuants.** (★) *Answer.*
`K(a, b, c) = c·K(a, b) + K(a) = c(ab + 1) + a = abc + a + c`. (★★) *Hint.*
Induct on `n` using the *mirror* recurrence
`K(a₁, …, aₙ) = a₁·K(a₂, …, aₙ) + K(a₃, …, aₙ)` — prove that one first, by
expanding the ordinary recurrence from the other end. (★★★) *Answer.* With all
`aᵢ = 1` the recurrence is `Kₙ = Kₙ₋₁ + Kₙ₋₂` with `K(∅) = 1 = F₁` and
`K(1) = 1 = F₂`, so `K(n ones) = F₍ₙ₊₁₎` — and Euler's rule reads it as the
count of domino-and-square tilings of a strip.

**E3 — Algebraic irrationals.** (★) *Answer.* `ρ ≈ 1.324718`, and
`ρ³ ≈ 2.324718 = ρ + 1` to the shown precision; algebraically, `x³ − x − 1` is
irreducible with a single real root, which is `ρ` by definition. (★★) *Answer.*
`cbrt(2)`'s first 40 partial quotients `a₁ … a₄₀` (the demo drops `a₀`) have
geometric mean `≈ 2.76` (Khinchin-typical), while `√2`'s `a₁ … a₄₀` are forty
`2`s: geometric mean exactly `2`, pinned there forever. A quadratic surd can
never be Khinchin-typical — its period fixes the mean. (★★★) *Hint.* Start
with the survey literature on the Littlewood conjecture (Stop 15); the link is
that badly approximable numbers are exactly those with bounded partial
quotients.

**E4 — Continued-fraction variants.** (★) *Answer.* All three fold back to
`87/32`. For the minus expansion, fold from the right with `a − 1/x`:
`2 − 1/2 = 3/2`, `2 − 2/3 = 4/3`, `3 − 3/4 = 9/4`, `4 − 4/9 = 32/9`,
`3 − 9/32 = 87/32`. ✓ (★★) *Answer.* `87/32` itself is one: its regular
expansion `[2, 1, 2, 1, 1, 4]` has six terms, its NICF `[3, −4, 2, 4]` only
four. Any regular expansion with a run of `1`s among `a₁, a₂, …` shortens,
because the NICF swallows each run into a rounding choice. (A leading `a₀ = 1`
does not count: `4/3 = [1; 3]` and `3/2 = [1; 2]` gain nothing.) (★★★) *Hint.*
Look up Hirzebruch–Jung resolution: expand `n/q` as a minus-CF and match each
`aᵢ ≥ 2` with an exceptional curve of self-intersection `−aᵢ` in the
resolution graph of the `1/n(1, q)` singularity.

**E5 — The three-distance theorem.** (★) *Answer.*
`demo three-distance 8/13 12` (a Fibonacci ratio, `8/13 ≈ 1/φ`) yields just
*two* gap lengths, `1/13` and `2/13`, with the largest the sum of the others —
here because `α = 8/13` is rational: the `12` points fill `12` of the `13`
lattice sites `k/13`, leaving eleven gaps of `1/13` and one doubled gap of
`2/13` at the missing site. For the irrational `1/φ` itself, `N = 12` gives
three lengths; the degeneracy to fewer happens exactly at the Fibonacci values
`N = 1, 2, 3, 5, 8, 13, …` — the golden ratio's signature evenness.
(★★) *Answer.* The `N` points cut the circle into exactly `N` arcs, and the
arcs partition it: their lengths — counted with multiplicity — sum to the
whole circumference, `1`. (★★★) *Hint.* Show the two shortest gap lengths
are `‖qₖα‖` and `‖qₖ₋₁α‖` for the consecutive convergent denominators with
`qₖ ≤ N < qₖ₊₁`, and the third (when present) is their sum — then the
determinant identity of Stop 3 explains why no fourth length can appear.

**E6 — The Gauss–Kuzmin–Wirsing constant.** (★) *Answer.* Power-iterating the
discretised operator from a *positive* start converges to `≈ 0.9986` on the
default grid — the true eigenvalue `1`, the Gauss density's eigenvalue, up to
discretisation error — which the frontier stop prints as its sanity check.
(★★) *Answer.* Substitute `u = 1/(n + x)` in each term:
`∫₀¹ 1/(n+x)²·f(1/(n+x)) dx = ∫_{1/(n+1)}^{1/n} f(u) du`, and the intervals
`(1/(n+1), 1/n]` tile `(0, 1]`, so the sum is `∫₀¹ f` — the operator preserves
the integral, which is precisely why `1` is an eigenvalue and why a mean-zero
start isolates the second one. (★★★) *Hint.* Double the grid and re-run;
compare successive estimates against Wirsing's `−0.3036630` and estimate the
discretisation order from the ratio of errors.

**E7 — Colliding blocks.** (★) *Answer.* Equal elastic masses exchange
velocities. Start: small at rest, big incoming at `−1`. Collision 1 (blocks):
small `−1`, big `0`. Collision 2 (wall): small `+1`. Collision 3 (blocks):
small `0`, big `+1`. The big block departs, the small one is at rest — three
collisions, `⌊π⌋ = 3`. (★★) *Answer.* `θ = arctan(√(m/M)) = arctan(1) = π/4`,
so `π/θ = 4` exactly and the count is `⌈4⌉ − 1 = 3` — a case where `π/θ` is an
integer, so the ceiling form gives the right `3` while the naive floor
`⌊π/θ⌋ = 4` would overcount by one. (★★★) *Hint.* `arctan(10⁻ⁿ) = 10⁻ⁿ − 10⁻³ⁿ/3 + …`, so
`π/arctan(10⁻ⁿ)` exceeds `π·10ⁿ` by roughly `π·10⁻ⁿ/3`. The two formulas can
only disagree if an integer falls in that sliver — i.e. if the digits of π just
after position `n` were a run of about `n` consecutive `9`s. None has ever been
found, and Galperin's theorem is stated with that (empirically safe, still
unproved-in-general) caveat.

**E8 — The River (Conway's topograph).** (★) *Answer.* Use the
arithmetic-progression rule that across any edge separating regions of values
`p` and `q`, the two regions `r, r'` at its ends satisfy `r + r' = 2(p + q)`.
In the `d = 7` figure the `+1` and `+2` upper regions flank the river opposite a
`−3` region, so the region one step further out is `2(1 + 2) − (−3) = 9`, larger
than both `+1` and `+2` — off the river the terrain only climbs, which is the
climbing lemma read at one node. (★★) *Answer.* The river's `Q = 1` well sits at
the convergent `8/3` of `√7 = [2; (1, 1, 1, 4)]`, and `8² − 7·3² = 64 − 63 = 1`.
✓ The well hands back the fundamental Pell solution `(8, 3)` with no fraction
folded by hand. (★★★) *Hint.* There are only finitely many reduced binary
quadratic forms of a given discriminant (Gauss), and the river passes through
reduced forms only; a deterministic walk through a finite set must eventually
revisit a state, and from the first repeat it is periodic. This is exactly
Lagrange's periodicity of `√d`'s continued fraction ([Stop 6](06-loop-road.md))
— the confinement of `(Pₙ, Qₙ)` to fewer than `2d` states, drawn as a landscape.

**E9 — Ramanujan's continued fraction.** (★) *Answer.* Truncating
`R(q)/q^{1/5} = 1/(1 + q/(1 + q²/(1 + q³/…)))` at `q = 1/2` gives
`2/3, 5/7, 22/31, 93/131 = 0.6667, 0.7143, 0.70968, 0.70992`, straddling the
limit `0.70983…` — odd convergents below, even above, the usual alternating
bracket, matching `demo ramanujan`. (★★) *Answer.* Evaluating
`√(1 + 2√(1 + 3√(1 + 4√(…))))` inside-out with the deepest radical closed off at
`1` gives `√3, √5, 2.560, 2.755, … = 1.732, 2.236, 2.560, 2.755`, rising
monotonically toward `3` — the value Ramanujan's identity
`x + 1 = √(1 + x√(1 + (x+1)√(…)))` predicts at `x = 2`. (★★★) *Hint.* Sixteen
agreeing digits rule out any gap larger than `~10⁻¹⁶`, but distinct closed forms
can agree far longer — Ramanujan's own `e^{π√163}` is an integer to twelve
places and is *not* one — so a numerical match never certifies exact equality. A
proof needs the modular theory of `R(q)`: the modular equation relating `R(q)`
and `R(q⁵)`, evaluated at `q = e^{−2π}` (that is `τ = i`, a fixed point of the
relevant transformation), forces `R(e^{−2π})` to be the golden surd
`√((5 + √5)/2) − φ`. It is an identity between modular functions, not an
inference from decimals.

## The Heritage Line (Appendix H)

The nine heritage stops carry a compact `**Exercises.**` line each; hints and
answers here follow the same ★ grading, and every computed value has been
checked against the engine.

**H1 — The ladder of Euclid.** (★) *Answer.* `89/55 = [1; 1, 1, 1, 1, 1, 1, 1,
2]` — nine divisions, every quotient `1` until the final `2`, because
`(89, 55) = (F₁₁, F₁₀)` and the Fibonacci recurrence `F₍ₙ₊₁₎ = 1·Fₙ + F₍ₙ₋₁₎`
makes each step of the ladder slide exactly one rung down the sequence.
(★★) *Answer.* If the expansion terminates, folding finitely many integer
additions and reciprocals yields a rational. Conversely, running the expansion
on `p/q` *is* Euclid on `(p, q)`: each complete quotient is a fraction whose
denominator is the previous step's remainder, and the remainders strictly
decrease, so the ladder — and the expansion — must end. In Euclid's dress: the
measuring terminates exactly for commensurable magnitudes, which is X.2 read
contrapositively. (★★★) *Hint.* Reverse Lamé: if Euclid takes `k` steps, build
the *smallest* possible inputs from the bottom up — the last pair is at least
`(2, 1)`, and each step up adds at least the two below it, so `b ≥ F₍ₖ₊₁₎`.
Consecutive Fibonacci numbers achieve every bound with equality; the full
constant-chasing is worked in Stop 1's answer 5 above.

**H2 — The cyclic method.** (★) *Answer.* `1151² = 1324801` and
`92·120² = 92·14400 = 1324800`; the difference is `1`. ✓ (★★) *Answer.*
`|k| = 3` and `−a ≡ −8 ≡ 1 (mod 3)`, so `m ∈ {1, 4, 7, 10, …}`; among these,
`m = 7` has `m² = 49` nearest `61`. Compose and divide by `|k| = 3`:
`a′ = (8·7 + 61·1)/3 = 39`, `b′ = (8 + 1·7)/3 = 5`,
`k′ = (7² − 61)/3 = −4` — the next triple is `(39, 5, −4)`, and indeed
`39² − 61·5² = 1521 − 1525 = −4`, exactly turn 1 of the transcript's wheel.
(★★★) *Answer.* Expand both squares:
`(ac + d·be)² − d·(ae + bc)² = a²c² + 2d·abce + d²b²e² − d·a²e² − 2d·abce −
d·b²c²`. The cross terms cancel, and the rest factors:
`a²(c² − d·e²) − d·b²(c² − d·e²) = (a² − d·b²)(c² − d·e²) = k·l`. ∎

**H3 — First fractions in print.** (★) *Answer.* `4`, then `4 + 2/8 = 17/4 =
4.25`, then `4 + 2/(8 + 2/8) = 4 + 8/33 = 140/33 = 4.24242…` — already within
`2.2e−4` of `√18 = 4.24264…`, and the next convergent `577/136` lands within
`7e−6` on the other side. (★★) *Hint.* From the convergent recurrence,
`Cₙ₊₁ − Cₙ = (−1)ⁿ·(a₁a₂⋯aₙ₊₁)/(BₙBₙ₊₁)`, where the `aᵢ = (2i − 1)²` are the
partial numerators. All numerators and all `Bₙ` are positive, so consecutive
differences alternate in sign and the convergents straddle the limit — the
engine's `1, 3/2, 15/13, 105/76, …` land alternately below and above
`4/π = 1.27324…`, which is exactly the bracket `gcf_to_simple` relies on.
(★★★) *Answer.* Write `√13 = 3 + x` with `x > 0`. Squaring,
`9 + 6x + x² = 13`, so `x(6 + x) = 4` and `x = 4/(6 + x)`. Substituting the
equation into its own right-hand side forever gives
`√13 = 3 + 4/(6 + 4/(6 + …))` — Bombelli's repeating `(6, 4)` block.

**H4 — The planetarium.** (★) *Answer.*
`77708431 = 29·2640858 + 1123549`, `2640858 = 2·1123549 + 393760`,
`1123549 = 2·393760 + 336029` — quotients `29, 2, 2`, convergents
`29, 59/2, 147/5`, the top of the transcript's ladder. (★★) *Answer.* Wheels
of `m·h` and `m·k` teeth mesh in the identical ratio `h/k`: scaling by a
common integer changes nothing about the approximation. What it buys is
manufacturability — a real wheel needs some minimum number of teeth, and
scaling lifts a too-small pair (the convergent `29/1`, say) into the cuttable
range while keeping the error identical. (★★★) *Answer.* The calendar
fraction is `0.2422` (Stop 5), and
`gear_ratio(Fraction(2422, 10000), max_teeth=100)` returns `(23, 95)`:
`23/95 = 0.24211`, off by `9.5e−5`. That beats the Jalali convergent `8/33`
(off by `2.2e−4`) because the tooth budget admits the *semiconvergent*
`23/95`, and it beats the Gregorian `97/400 = 0.2425` (off by `3.0e−4`), which
would need a 400-tooth wheel anyway. As a leap-year rule, though, "23 leap
years every 95" would never survive being taught to children — gears only have
to mesh, calendars have to be remembered.

**H5 — Lambert puts π on trial.** (★) *Answer.* `1/1 = 1`, then
`1/(1 − 1/3) = 3/2`, then `1/(1 − 1/(3 − 1/5)) = 1/(1 − 5/14) = 14/9 =
1.5556…` — closing on `tan(1) = 1.55741…`, with `95/61` next and closer
still. (★★) *Hint.* Suppose `x = p/q` with `q ≥ 1`. Clear denominators level
by level in `tan x = x/(1 − x²/(3 − x²/(5 − …)))`: the tails satisfy an
integer recurrence whose values must all be nonzero (else the fraction would
terminate) yet strictly decrease in absolute value — an infinite descent no
integer sequence survives. The same skeleton is sketched in Stop 9's answer 5
above. (★★★) *Answer.* Euler *proved* the pattern of
`e = [2; 1, 2, 1, 1, 4, …]` continues forever, and an infinite simple
continued fraction is automatically irrational — for `e`, the expansion itself
is the proof. For `π` the simple expansion `[3; 7, 15, 1, 292, …]` has no
known pattern, so nothing can be proved from it directly; Lambert's detour
trades the patternless simple fraction for a patterned *generalized* one,
where the descent can grip. `e` wears its order on the surface; `π` keeps its
order one representation away.

**H6 — The Skyscraper of Liouville.** (★) *Answer.* After four terms
`L ≈ 10⁻¹ + 10⁻² + 10⁻⁶ + 10⁻²⁴ = 0.110001000000000000000001`, which over
`10²⁴` is `p/q` with `p = 10²³ + 10²² + 10¹⁸ + 1 = 110001000000000000000001`.
The numerator ends in `1`, so it is coprime to `10²⁴ = 2²⁴·5²⁴`, and the reduced
denominator is exactly `10²⁴`. (★★) *Hint.* A large partial quotient `aₙ₊₁`
makes its preceding convergent unusually good:
`|α − pₙ/qₙ| ≈ 1/(aₙ₊₁·qₙ²) ≈ 1/(qₙ·qₙ₊₁)`, so if `aₙ₊₁ ≥ qₙ^δ` then
`|α − pₙ/qₙ| < 1/qₙ^{2+δ}`. Unbounded partial quotients drive `δ` up without
limit, forcing the irrationality measure above `2` — a twelve-digit `aₙ` at
modest `qₙ` already witnesses it. (★★★) *Answer sketch.* Let `α` be algebraic of
degree `d` with integer minimal polynomial `f`; irreducibility gives
`f(p/q) ≠ 0`, a rational with denominator dividing `q^d`, so `|f(p/q)| ≥ 1/q^d`.
The mean value theorem gives `f(p/q) = f(p/q) − f(α) = f′(ξ)·(p/q − α)`, whence
`|α − p/q| ≥ 1/(M·q^d)` with `M = max|f′|` near `α`; take `c = 1/(2M)`. For `L`,
the truncation `pₖ/qₖ` has `qₖ = 10^{k!}` and
`|L − pₖ/qₖ| < 2·10^{−(k+1)!} = 2·qₖ^{−(k+1)}`. Once `k + 1 > d` this beats
`c/qₖ^d` for every `c > 0`, contradicting the inequality at every degree — so
`L` is algebraic of no degree, i.e. transcendental. ∎

**H7 — The Tree in the Workshop.** (★) *Answer.* From the boundaries `0/1` and
`1/0`, insert `1/1`; `3/5 < 1` sends you left to `1/2` (record **L**);
`3/5 > 1/2` sends you right to the mediant `2/3` (record **R**); `3/5 < 2/3`
sends you left to the mediant `3/5` (record **L**) — found, at address **LRL**,
whose run-lengths `1, 1, 1` are the continued fraction `3/5 = [0; 1, 1, 2]` with
the last run off by one. (★★) *Answer.* The seeds satisfy `|0·0 − 1·1| = 1`, and
each mediant step preserves it: `|p(q+s) − q(p+r)| = |ps − qr|` and
`|(p+r)s − (q+s)r| = |ps − qr|`, so `|ps − qr| = 1` propagates to every adjacent
pair by induction (and the converse pins neighbours down uniquely). Any common
divisor of `p+r` and `q+s` divides `(p+r)s − (q+s)r = ±1`, so the mediant is
automatically in lowest terms — Stop 8's Farey argument exactly. (★★★) *Hint.*
Walk the tree toward `π ≈ 3.14159`, turning L/R by comparison, until a numerator
or denominator would pass `30`: the last fraction with both teeth `≤ 30` is
`22/7 = 3.142857` (error `1.3e−3`). The tree reproduces the convergent `22/7`;
the next convergent `333/106` needs `106` teeth, out of the workshop's reach, so
under a 30-tooth cap `22/7` is the best — the convergent-truncation rule Huygens
used at [Appendix H, H4](appendix-h-history.md#h4-1682-the-planetarium), read off
the tree instead of the ladder.

**H8 — The Factoring Machine.** (★) *Answer.*
`59649589127497217 × 5704689200685129054721 = 340282366920938463463374607431768211457`,
and `2¹²⁸ + 1 = 340282366920938463463374607431768211457` — equal, so the split
is genuine. (★★) *Hint.* Expand `√13290059 = [3645; …]` and form its convergents
`pₖ/qₖ`; each residue `Qₖ = pₖ² − 13290059·qₖ²` has size about `√N ≈ 3645`, small
enough to factor over `{−1, 2, 5, 13, …}`. Scan the first several convergents for
one whose `Qₖ` is that-smooth — those are the relations `A² ≡ Qₖ (mod N)` the
method collects. (★★★) *Hint.* If `X² ≡ Y² (mod N)` then `N | (X−Y)(X+Y)`, so
`gcd(X − Y, N)` collects whatever primes of `N` divide `X − Y`; when `X ≢ ±Y` it
is neither `1` nor `N`, hence a proper factor. It fails about half the time
because, for `N` with two prime factors, a random square root of `Y²` splits its
sign independently at each prime — two of the four combinations give `X ≡ ±Y` and
a trivial gcd, the other two split `N`.

**H9 — Item 101.** (★) *Answer.* The convergents of `√5 = [2; 4, 4, …]` are
`2, 9/4, 38/17`; the map `x ↦ (x + 1)/2` sends them to `3/2, 13/8, 55/34` —
every one a convergent of `φ` (the Fibonacci ratios `F₄/F₃, F₇/F₆, F₁₀/F₉`).
The machine's all-ones output is this convergence performed term by term.
(★★) *Answer.* `1/x = (0·x + 1)/(1·x + 0)`, so the state is
`(a, b, c, d) = (0, 1, 1, 0)`. For an input greater than `1` the reciprocal
lies in `(0, 1)`, so the leading `0` can be emitted at once, and the emit
transform turns the state into `(1, 0, 0, 1)` — the identity, which simply
re-emits each ingested term unchanged. Every later output digit is forced the
moment its input term arrives, so no look-ahead is ever needed:
`1/e = [0; 2, 1, 2, 1, 1, 4, …]`, `e`'s own road behind a `0` — the
reciprocal rule of Stop 2, mechanized. (★★★) *Answer.* Let `x = 1 + √5`, so
`⌊x⌋ = 3` and `x − 3 = √5 − 2`. Since `(√5 − 2)(√5 + 2) = 1`, the reciprocal
of the leftover is `√5 + 2 = 4.236…`: the next term is `4`, and the new
leftover is `√5 + 2 − 4 = √5 − 2` — the same as before. The expansion locks
into `4` forever: `2φ = 1 + √5 = [3; (4)]`, exactly what
`add(phi_cf(), phi_cf())` streams. ∎

## The Branch Line (Appendix I)

The six branch stops carry a compact `**Exercises.**` line each; hints and
answers here follow the same ★ grading, and every computed value has been
checked against the engine.

**B1 — Engel expansions.** (★) *Answer.* `⌈8/5⌉ = 2` and `2·(5/8) − 1 = 1/4`;
then `⌈4⌉ = 4` and `4·(1/4) − 1 = 0`. The digits `[2, 4]` do not decrease, and
`5/8 = 1/2 + 1/(2·4) = 1/2 + 1/8`. ✓ (★★) *Answer.* Write `x = p/q` in lowest
terms; with `a = ⌈q/p⌉` the map sends it to `a·x − 1 = (ap − q)/q`, and
`(a−1)p < q ≤ ap` forces `0 ≤ ap − q < p`. The numerator strictly decreases while
positive — a descending chain of non-negative integers that must reach `0`, so
the expansion terminates exactly for rationals (Euclid's descent, Stop 2, once
more); an irrational keeps a never-zero irrational remainder forever.
(★★★) *Answer.* `e − 1 = Σ_{k≥1} 1/k! = 1/1! + 1/2! + 1/3! + …`, and
`1/k! = 1/(1·2·⋯·k)` is exactly the Engel term `1/(a₁a₂⋯aₖ)` when `aₖ = k`. The
digits `1, 2, 3, …` are non-decreasing, so the factorial series *is* the Engel
expansion of `e − 1`, read straight off — the serene cousin of `e`'s own
staircase `1, 1, 2, 3, 4, …`.

**B2 — Lüroth and Pierce.** (★) *Answer.* With `[4, 2, 17]` the Lüroth terms are
`1/4`, `1/(4·3·2) = 1/24`, and `1/(4·3·2·1·17) = 1/408`; summing,
`1/4 + 1/24 + 1/408 = (102 + 17 + 1)/408 = 120/408 = 5/17`. ✓ (★★) *Hint.* The
first Lüroth digit equals `k` exactly on the interval `Iₖ = (1/k, 1/(k−1)]`, of
length `1/(k−1) − 1/k = 1/(k(k−1))`; the Lüroth map sends each `Iₖ` affinely onto
all of `(0, 1]` (slope `k(k−1)`), making it a full-branch Bernoulli map whose
digits are i.i.d. with `P(digit = k) = |Iₖ| = 1/(k(k−1))`. (★★★) *Answer.* Pierce
sets `aₙ = ⌊1/xₙ₋₁⌋` and `xₙ = 1 − aₙxₙ₋₁`. From `aₙ = ⌊1/xₙ₋₁⌋` you get
`1/xₙ₋₁ < aₙ + 1`, i.e. `xₙ₋₁ > 1/(aₙ+1)`, so
`xₙ = 1 − aₙxₙ₋₁ < 1 − aₙ/(aₙ+1) = 1/(aₙ+1)`. Hence `1/xₙ > aₙ + 1`, forcing
`aₙ₊₁ = ⌊1/xₙ⌋ ≥ aₙ + 1 > aₙ` — strictly increasing.

**B3 — Egyptian fractions.** (★) *Answer.* Greedy on `4/17`: `⌈17/4⌉ = 5`,
`4/17 − 1/5 = 3/85`; `⌈85/3⌉ = 29`, `3/85 − 1/29 = 2/2465`; `⌈2465/2⌉ = 1233`,
`2/2465 − 1/1233 = 1/3039345`. So `4/17 = 1/5 + 1/29 + 1/1233 + 1/3039345`, the
numerators `4 → 3 → 2 → 1` falling one at each step. (★★) *Answer.* For `p/q` with
`0 < p < q`, greedy takes `n = ⌈q/p⌉`, and `(n−1)p < q ≤ np` gives the new
numerator `np − q ∈ [0, p)` — strictly below the old `p`. A descending chain of
positive integers halts in at most `p` steps: termination for every rational, the
same descent as B1 and Stop 1. (★★★) *Hint.* It suffices to check *primes* `n` (a
triple for a divisor scales to any multiple). For `n ≡ 3 (mod 4)`, write
`n = 4t + 3` and use the one-line identity `4/n = 1/(t+1) + 1/(n(t+1))` (split one
unit fraction to reach three); even `n` reduce through `4/n = 2/(n/2)`. That
leaves only the primes `n ≡ 1 (mod 4)` up to `97` —
`5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97` — each cleared by a short search,
e.g. `4/5 = 1/2 + 1/4 + 1/20`.

**B4 — Zeckendorf and the golden base.** (★) *Answer.* Greedily subtract the
largest Fibonacci `≤ 2026`: `2026 = 1597 + 377 + 34 + 13 + 5`
(`F₁₆ + F₁₃ + F₈ + F₆ + F₄`), indices `16, 13, 8, 6, 4` — no two consecutive.
(★★) *Answer.* If greedy picks `Fₖ` (the largest `≤ n`), the remainder is
`n − Fₖ < Fₖ₊₁ − Fₖ = Fₖ₋₁`, so the next Fibonacci taken is `≤ Fₖ₋₂` — at least
two indices down. Consecutive indices therefore never both appear, which is the
uniqueness-forcing rule of Zeckendorf. (★★★) *Hint.* Start from `n` copies of
`φ⁰` and apply the golden rewrite rules `φᵏ + φᵏ⁺¹ = φᵏ⁺²` (merge adjacent `1`s)
and `2φᵏ = φᵏ⁺¹ + φᵏ⁻²` (clear a digit `≥ 2`), both consequences of `φ² = φ + 1`.
Each rewrite lowers a well-founded weight, so the process halts at a finite
standard string with no two adjacent `1`s — a *terminating* base-φ numeral. The
deep reason it must terminate is that `φ` is a Pisot number (its conjugate
`−1/φ` has modulus `< 1`), so every element of `ℤ[φ]`, integers included, has a
finite base-φ expansion.

**B5 — Cutting sequences (Ostrowski and Sturmian).** (★) *Answer.* Along
`y = x/φ`, vertical grid lines are crossed at `x = 1, 2, 3, …` (write `a`) and
horizontal ones at `x = φ, 2φ, 3φ, … ≈ 1.618, 3.236, 4.854, 6.472, 8.090, …`
(write `b`); merging by increasing `x` gives `a b a a b a b a a b a a b` — the
first `13` letters of the Fibonacci word. (★★) *Answer.* Per unit of `x` there is
one vertical crossing and `1/φ` horizontal crossings, so the asymptotic frequency
of `a` is `1/(1 + 1/φ) = 1/φ ≈ 0.618`, an *irrational* number. An eventually
periodic word has a rational letter-frequency (the count within its period), so
the Fibonacci word cannot be eventually periodic. (★★★) *Hint.* Fix the
convergent denominators with `qₖ ≤ N < qₖ₊₁`. In Ostrowski numeration the points
`{jα}` for `j < N` fall at spacings governed by the top two active digits, and
the gaps come out to exactly `‖qₖ₋₁α‖` and `‖qₖα‖`, with the third length (when
present) their sum. That is E5's three-distance dissection; the determinant
identity of [Stop 3](03-engine-room.md) explains why no fourth length can appear.
See [Appendix D, E5](appendix-d-frontier.md#e5-the-three-distance-theorem).

**B6 — Lochs' theorem.** (★) *Answer.* Lévy's constant is
`β = lim (1/n)·ln qₙ = π²/(12 ln 2)`. Matching decimal precision `10⁻ⁿ` to
continued-fraction precision `qₘ⁻² ≈ e^{−2βm}` gives `n·ln 10 = 2βm`, so
`m/n = ln 10/(2β) = ln 10·(12 ln 2)/(2π²) = 6 ln 2 ln 10/π² ≈ 0.9703` — Lochs'
constant is `ln 10` over twice Lévy's. (★★) *Hint.* Run `demo lochs` on the
decimals of `e` and watch `m/n`: it hovers near `0.97` (about `1.03` decimals per
term), but `e`'s partial quotients `2, 4, 6, …` grow, so convergents advance in
bursts and the empirical rate wobbles more than for a Khinchin-typical number —
`e` is a measure-zero point the almost-sure limit need not pin down, yet it still
tracks it. (★★★) *Hint.* Lochs' proof runs on Lévy's almost-everywhere growth
`qₙ ≈ e^{βn}`, valid on a full-measure set. A quadratic irrational has an
eventually periodic expansion, so its `qₙ` grow like `λⁿ` for the period's
fundamental unit `λ` — a rate generally unequal to `e^β`. The quadratic surds
form a measure-zero set the "almost every" clause is entitled to skip; the
exchange rate for `√2` is fixed by its own `λ`, not by `6 ln 2 ln 10/π²`.

## See also

- [Appendix A — Proofs](appendix-a-proofs.md) for the full arguments the ★★★
  items sketch.
- [Appendix B — Glossary](appendix-b-glossary.md) for every term used here,
  each linked to the stop that introduces it.
- [Appendix C — References](appendix-c-references.md) for where the open-ended
  reading exercises lead.

[← Route map](index.md) · [Appendix B — Glossary](appendix-b-glossary.md) · [Appendix D — The Express Line](appendix-d-frontier.md) · [Appendix H — The Heritage Line](appendix-h-history.md) · [Appendix I — The Branch Line](appendix-i-branches.md)
