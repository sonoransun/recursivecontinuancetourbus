[← Appendix A — Proofs](appendix-a-proofs.md) · [Route map](index.md) · [Appendix C — References →](appendix-c-references.md)

# Appendix B — Glossary

The vocabulary of the tour, in alphabetical order. Each entry links to the stop
where the term is introduced.

### Anthyphairesis

The Greek name — 'reciprocal subtraction' — for Euclid's mutual measuring of two
magnitudes: subtract the smaller from the larger until it no longer fits, swap,
repeat. Elements X.2 makes it a test: the process ends iff the magnitudes are
commensurable, which is the continued-fraction termination criterion in ancient
dress. *([Stop 1](01-depot.md); [Appendix H](appendix-h-history.md).)*

### Base-φ (phi) numeration

A positional numeral system in the irrational base `φ`, with digits `0` and `1`
and the carry rule given by the golden identity `φ² = φ + 1`. Every non-negative
integer has a finite representation in which no two consecutive `1`s occur — the
base-φ form of Zeckendorf's idea, promoting the golden ratio of
[Stop 4](04-golden.md) from a number to be measured into the ruler itself.
*([Appendix I](appendix-i-branches.md).)*

### Best approximation of the first kind

A fraction `p/q` that minimises the *absolute* distance `|x − p/q|` among all
fractions with denominator at most `q`. These include the convergents **and**
certain semiconvergents. Contrast with the second kind. *([Stop 5](05-scenic-overlook.md).)*

### Best approximation of the second kind

A fraction `p/q` that minimises `|q·x − p|` — the distance weighted by the
denominator — among all fractions with denominator at most `q`. By **Lagrange's
theorem**, these are *exactly* the continued-fraction convergents. This is the
stronger, cleaner notion, and the one usually meant by "best rational
approximation." *([Stop 5](05-scenic-overlook.md).)*

### Bhāvanā (bhavana)

Brahmagupta's composition law (628 CE): from `a² − d·b² = k` and `c² − d·e² = l`,
the pair `(ac + d·be, ae + bc)` satisfies `x² − d·y² = k·l`. Composing
near-solutions of Pell's equation is the engine inside the chakravala.
*([Stop 7](07-cattle-crossing.md); [Appendix H](appendix-h-history.md).)*

### Bihomographic transform

A function of two variables `z(x, y) = (a·xy + b·x + c·y + d)/(e·xy + f·x + g·y +
h)` with an eight-integer state, used by Gosper's algorithm to compute `x + y`,
`x · y`, and other binary operations directly on continued-fraction streams. It
has three moves — ingest from `x`, ingest from `y`, or emit an output term.
*([Stop 11](11-assembly-line.md).)*

### Binary gcd

A gcd algorithm that uses only subtraction, halving, and parity tests instead of
division: if both numbers are even, halve both; if one is even, halve it;
otherwise subtract the smaller from the larger. Published by Josef Stein in 1967
and foreshadowed by the "halve if you can" rule of the Chinese *Nine Chapters*,
it suits binary hardware and underlies constant-time variants used in
cryptography. *([Stop 1](01-depot.md#then-now-next).)*

### Brjuno number

An irrational `α` whose convergent denominators `qₙ` satisfy
`Σ log(qₙ₊₁)/qₙ < ∞` — the partial quotients may be large, but not too large
too often. Brjuno (1971) showed that such rotation numbers produce *Siegel
disks*, regions of rigid rotation, in complex dynamics; Yoccoz (1988) showed
the condition is exactly right for quadratic polynomials. Every number with
bounded partial quotients, such as `φ`, is a Brjuno number.
*([Stop 13](13-hall-of-mirrors.md#then-now-next).)*

### Busy beaver

`BB(n)`: the largest number of steps any `n`-state Turing machine takes before
halting, among those that do halt. It grows faster than every computable
function — faster than Ackermann's — and is known exactly only for tiny `n`;
`BB(5) = 47,176,870` was proved in 2024 with a computer-checked proof.
*([Stop 12](12-tower.md#then-now-next).)*

### CFRAC (continued-fraction factorization)

The factoring algorithm of Morrison and Brillhart (1970) that reads the small
residues `Qₖ = pₖ² − N·qₖ²` dropping out of the convergents of `√(kN)`. Because
each residue has size about `√N`, many factor completely over a small fixed prime
base; combining enough of them into a congruence of squares `X² ≡ Y² (mod N)`
yields a factor as `gcd(X − Y, N)`. It cracked the seventh Fermat number and is
the ancestor of the quadratic sieve and the number field sieve.
*([Appendix H](appendix-h-history.md).)*

### Chakravala

The 'cyclic' method of Jayadeva and Bhāskara II (1150) for Pell's equation:
compose a trial triple with a chosen auxiliary solution by bhāvanā, scale down,
and repeat until the residue k reaches 1. It solves `x² − 61·y² = 1` in a
handful of turns — with no continued fraction in sight, though it lands on the
same convergents. *([Stop 7](07-cattle-crossing.md); [Appendix H](appendix-h-history.md).)*

### Complete quotient

The value `xₙ = [aₙ; aₙ₊₁, aₙ₊₂, …]` of the entire tail of a continued fraction
from position `n` onward. Always `≥ 1` for `n ≥ 1`, and satisfies
`x = (xₙ pₙ₋₁ + pₙ₋₂)/(xₙ qₙ₋₁ + qₙ₋₂)`. The tool of the error-bound proof in
Appendix A. *([Appendix A](appendix-a-proofs.md).)*

### Constructive (computable) real

A real number presented as a program that, asked for any precision, returns an
approximation guaranteed to that precision — Turing's 1936 notion of a
computable number. Arithmetic on such streams, like Gosper's arithmetic on
continued fractions, can emit certified digits forever but cannot always decide
equality. *([Stop 11](11-assembly-line.md#then-now-next).)*

### Convergent

The rational `pₙ/qₙ = [a₀; a₁, …, aₙ]` obtained by truncating a continued
fraction after `n + 1` terms. Convergents are automatically in lowest terms,
straddle the true value in alternation, and are the best approximations of the
second kind. *([Stop 3](03-engine-room.md).)*

### Corecursion

A definition scheme that *produces* an infinite structure on demand, rather than
consuming a finite input down to a base case (ordinary recursion). Gosper's
stream arithmetic is corecursive: it has no base case and is judged correct by
how it keeps emitting valid terms forever, not by how it halts. *([Stop 11](11-assembly-line.md).)*

### Duffin–Schaeffer theorem

For a function `ψ ≥ 0`, almost every real `x` has infinitely many fractions
`p/q` in lowest terms with `|x − p/q| < ψ(q)/q` exactly when
`Σ φ(q)ψ(q)/q` diverges (`φ` here is Euler's totient). Conjectured by Duffin and
Schaeffer in 1941, proved by Koukoulopoulos and Maynard in 2019.
*([Stop 10](10-casino.md#then-now-next).)*

### Egyptian fraction

A representation of a rational as a sum of *distinct* unit fractions `1/n`, in the
manner of the Rhind papyrus scribes. The Fibonacci–Sylvester greedy algorithm
produces one by repeatedly subtracting the largest unit fraction that still fits;
it always terminates for a rational, but can drive the denominators to roughly
square at every step. *([Appendix I](appendix-i-branches.md).)*

### Engel expansion

The unique representation `x = 1/a₁ + 1/(a₁a₂) + 1/(a₁a₂a₃) + …` of a number in
`(0, 1]` with non-decreasing integer digits `1 ≤ a₁ ≤ a₂ ≤ …`. It is the
ceiling-and-affine cousin of the regular continued fraction — set `a = ⌈1/x⌉`,
replace `x` by `a·x − 1`, and repeat — and terminates exactly for the rationals.
The factorial series makes `e − 1` its cleanest specimen, with digits
`1, 2, 3, …`. *([Appendix I](appendix-i-branches.md).)*

### Erdős–Straus conjecture

The claim (1948) that `4/n = 1/x + 1/y + 1/z` is solvable in positive integers
for every `n ≥ 2`. It has been verified to enormous bounds and reduced by
congruences to a few stubborn residue classes, yet remains open — one of the
Egyptian-fraction questions the tour can pose but not answer.
*([Appendix I](appendix-i-branches.md); [Stop 15](15-terminus.md).)*

### Farey sequence `Fₙ`

The ascending list of all fractions in `[0, 1]` with denominator at most `n`, in
lowest terms. Adjacent fractions `a/b < c/d` satisfy the neighbour relation
`bc − ad = 1`, and the mediant of two neighbours is the next fraction to appear
between them. Closely tied to the Stern–Brocot tree. *([Stop 8](08-family-tree.md).)*

### Gauss map

The transformation `T(x) = {1/x} = 1/x − ⌊1/x⌋` on `(0, 1)`, which strips the
first partial quotient off a continued fraction and shifts the rest forward. It
preserves the **Gauss measure** `dμ = (1/ln 2)·1/(1+x) dx` and is ergodic; the
statistics of continued fractions are the dynamics of this one map. *([Stop 10](10-casino.md).)*

### Generalized continued fraction

A continued fraction whose numerators need not be 1:
`b₀ + a₁/(b₁ + a₂/(b₂ + …))`. Chaotic simple expansions can become perfectly
patterned in generalized form — Brouncker's 4/π and Lambert's tan x are the
classic cases. *([Stop 9](09-celebrity.md).)*

### Half-gcd

A divide-and-conquer gcd algorithm that computes the `2×2` matrix product of
the first half of Euclid's quotients recursively, reaching quasi-linear time
(Schönhage, 1971, after Knuth). It is how big-integer libraries compute gcds
and continued fractions of numbers with millions of digits.
*([Stop 3](03-engine-room.md#the-engine-as-a-product-of-matrices).)*

### Hermite's problem

Hermite's 1848 question to Jacobi: find an algorithm that expands real numbers
so that the cubic irrationals, and only they, become periodic — the analogue of
Lagrange's theorem one degree up. Settled for totally real cubics by Karpenkov
(2022); open in general. *([Stop 2](02-unfolding-road.md#then-now-next).)*

### Homographic transform

A function of one variable `z(x) = (a·x + b)/(c·x + d)` with integer state
`(a, b, c, d)` — also called a Möbius or fractional-linear transform. The
one-input building block of Gosper's algorithm, with two moves: ingest an input
term or emit an output term when the floor is determined. A **purely periodic**
continued fraction is a fixed point of such a map. *(Stops [11](11-assembly-line.md), [13](13-hall-of-mirrors.md).)*

### Inverse Ackermann function

`α(n)`, the number of rungs of the Ackermann ladder needed to exceed `n`. It
grows so slowly that it never exceeds 4 for any input that fits in the
universe, yet it is unbounded — and it is exactly the amortised cost per
operation of the union–find data structure (Tarjan, 1975).
*([Stop 12](12-tower.md#then-now-next).)*

### Irrationality measure

The supremum `μ(x)` of the exponents `μ` for which `|x − p/q| < 1/q^μ` has
infinitely many solutions. Every irrational has `μ ≥ 2`; algebraic irrationals
have exactly `2` (Roth, 1955), as does `e`; Liouville numbers have `μ = ∞`; and
`μ(π) ≤ 7.1032…` is the best bound known (2020).
*([Stop 9](09-celebrity.md#then-now-next).)*

### Kuṭṭaka (kuttaka)

Āryabhaṭa's 'pulverizer' (499 CE): solve `a·x − b·y = c` in integers by running
Euclid's quotients backward — the same arithmetic as the Bézout step of Stop 1,
a thousand years earlier. *([Stop 1](01-depot.md); [Appendix H](appendix-h-history.md).)*

### Lattice reduction

Finding a basis of short, nearly orthogonal vectors for a lattice. In two
dimensions it is Euclid's algorithm on vectors (Lagrange and Gauss); in any
dimension the LLL algorithm (1982) and its descendants do it approximately. It
breaks weak cryptosystems and sets the security margins of lattice-based
post-quantum cryptography. *([Stop 1](01-depot.md#then-now-next).)*

### Liouville number

A real number approximable by rationals beyond every polynomial rate: for each
`m` there is a `p/q` with `0 < |α − p/q| < 1/qᵐ`. Liouville's inequality forbids
this of any algebraic irrational, so every such number is transcendental —
`L = Σ 10^(−n!)` was the first quantity ever proved transcendental (1844).
Liouville numbers have infinite irrationality measure and betray themselves in
the continued fraction through partial quotients that explode.
*([Appendix H](appendix-h-history.md).)*

### Lochs' theorem

The result (1964) that for almost every real number the first `n` decimal digits
pin down about `m ≈ 0.9703·n` correct continued-fraction terms, at the exchange
rate `6 ln 2 ln 10 / π²`. The continued fraction is thus the marginally denser
currency, packing slightly more information per symbol than the decimal
expansion; the constant is `ln 10` divided by twice Lévy's constant, the entropy
of the Gauss map. *([Appendix I](appendix-i-branches.md); [Stop 10](10-casino.md).)*

### Lüroth series

The expansion `x = 1/a₁ + 1/(a₁(a₁−1)a₂) + …` (Lüroth, 1883) whose digits are
genuinely **independent and identically distributed**, with
`P(digit = k) = 1/(k(k−1))`. Unlike the correlated Gauss–Kuzmin digits of the
regular continued fraction, Lüroth's are a memoryless fair wheel; the price of
that honesty is that a rational's Lüroth expansion is eventually periodic rather
than finite. *([Appendix I](appendix-i-branches.md); [Stop 10](10-casino.md).)*

### Mediant

The fraction `(a + c)/(b + d)` formed from `a/b` and `c/d` by adding numerators
and denominators separately. It lies strictly between two neighbours and is the
generating operation of the Stern–Brocot tree and the Farey sequences.
*([Stop 8](08-family-tree.md).)*

### Metonic cycle

The coincidence that 19 tropical years are almost exactly 235 lunar months —
the convergent `235/19` of the ratio of year to month. Used in Babylon, brought
to Athens by Meton in 432 BC, and still fixing the Hebrew calendar and the
Christian date of Easter. *([Stop 5](05-scenic-overlook.md#then-now-next).)*

### Negative Pell equation

`x² − d·y² = −1`, solvable exactly when the period of `√d` is odd. How often
that happens as `d` varies was predicted by Stevenhagen (1993) and proved by
Koymans and Pagano (2022). *([Stop 7](07-cattle-crossing.md#then-now-next).)*

### Nested radical

An expression continuing under infinitely many radical signs, such as Ramanujan's
`3 = √(1 + 2√(1 + 3√(1 + 4√(…))))`. Its general form
`x + 1 = √(1 + x√(1 + (x+1)√(…)))` converges to `x + 1` for every `x`, and like a
continued fraction it is evaluated as the limit of its finite truncations.
*([Appendix D](appendix-d-frontier.md).)*

### Ostrowski numeration

A positional number system built on the convergent denominators `q₀, q₁, q₂, …`
of a fixed irrational `α`: every non-negative integer has a unique mixed-radix
representation against those `qₖ`, with the partial quotients setting each digit's
range. It is the continued fraction turned into a numeral system; for `α = 1/φ`
the denominators are the Fibonacci numbers and it collapses onto the Zeckendorf
representation. *([Appendix I](appendix-i-branches.md).)*

### Partial quotient

One of the terms `aₙ` in `[a₀; a₁, a₂, …]`. The first, `a₀`, is any integer;
every later one is a positive integer `aₙ ≥ 1`. For a rational, the partial
quotients are exactly the quotients produced by Euclid's algorithm. *([Stop 2](02-unfolding-road.md).)*

### Pierce expansion

The alternating-sign cousin of the Engel expansion,
`x = 1/a₁ − 1/(a₁a₂) + 1/(a₁a₂a₃) − …`, whose digits are **strictly increasing**
and finite for every rational. The alternating sign accelerates the sum while
keeping Engel's clean termination; the Pierce digits of `1/φ` come in pairs
straddling the Lucas numbers and grow doubly exponentially.
*([Appendix I](appendix-i-branches.md).)*

### Primitive recursion

The class of functions built from basic functions (zero, successor, projection)
by composition and *bounded* recursion — essentially, everything computable with
`for`-loops whose bounds are known in advance. The Ackermann function is total
and computable but **not** primitive recursive: it grows faster than any function
in this class. *([Stop 12](12-tower.md).)*

### Quadratic irrational (quadratic surd)

An irrational root of an integer quadratic `ax² + bx + c = 0`, equivalently a
number of the form `(P + √d)/Q` with `d` a non-square positive integer. By
**Lagrange's theorem**, these are exactly the numbers with eventually periodic
continued fractions. *([Stop 6](06-loop-road.md).)*

### Rational reconstruction

Recovering a fraction `u/v` with small numerator and denominator from its
residue modulo a large number `m`, by running the extended Euclidean algorithm
on `(m, residue)` and stopping halfway (Wang, 1981). It lets computer algebra
work with small modular numbers and still return exact rational answers.
*([Stop 2](02-unfolding-road.md#then-now-next).)*

### Reduced surd

A quadratic irrational `x` with `x > 1` whose conjugate `x̄` (the other root,
`√d ↦ −√d`) lies strictly in `(−1, 0)`. By **Galois' theorem**, a surd's
continued fraction is *purely* periodic (periodic from the very first term) if
and only if it is reduced. *([Stop 6](06-loop-road.md).)*

### Regulator

For a real quadratic field `ℚ(√d)`, the logarithm `R = log(x₁ + y₁√d)` of its
fundamental unit — a measure of how large the smallest Pell solution is. It can
be exponentially large in digits, so algorithms compute `R` rather than the
solution itself; a quantum computer can do so in polynomial time (Hallgren,
2002). *([Stop 7](07-cattle-crossing.md#then-now-next); [Stop 6](06-loop-road.md).)*

### Rogers–Ramanujan continued fraction

The `q`-continued fraction `R(q) = q^(1/5)/(1 + q/(1 + q²/(1 + q³/(1 + …))))`,
whose partial numerators are the powers `q, q², q³, …` rather than the constant
`1` of a simple continued fraction. Ramanujan sent it to Hardy in 1913 with the
astonishing value `R(e^(−2π)) = √((5 + √5)/2) − φ`, an infinite fraction
collapsing to a surd built entirely from the golden ratio.
*([Appendix D](appendix-d-frontier.md); [Appendix H](appendix-h-history.md).)*

### Semiconvergent

An intermediate fraction obtained by using a partial quotient `1 ≤ k < aₙ` in the
convergent recurrence: `(k·pₙ₋₁ + pₙ₋₂)/(k·qₙ₋₁ + qₙ₋₂)`. Semiconvergents fill
the gaps between successive convergents and appear among the best approximations
of the first kind, though not the second. *([Stop 5](05-scenic-overlook.md).)*

### Shor's algorithm

Peter Shor's 1994 quantum algorithm for factoring integers and computing
discrete logarithms in polynomial time. The quantum part estimates a fraction
`s/r` whose denominator is a period; the classical last step recovers `r` as a
continued-fraction convergent of the measurement, by Legendre's criterion.
*([Stop 14](14-souvenir-shop.md#then-now-next).)*

### Similarity dimension

For a self-similar set made of `N` copies of itself each scaled by `r < 1`, the
number `d = ln N / ln(1/r)`. It generalises ordinary dimension to fractional
values: Cantor set `≈ 0.6309`, Koch curve `≈ 1.2619`, Sierpiński triangle
`≈ 1.5850`, and space-filling curves (dragon, Hilbert) exactly `2`. *([Stop 13](13-hall-of-mirrors.md).)*

### Stern–Brocot tree

The infinite binary tree of all positive rationals, each appearing exactly once
in lowest terms, generated by repeatedly inserting mediants between `0/1` and
`1/0`. A node's Left/Right address has run-lengths equal to its continued
fraction's partial quotients (last run off by one). *([Stop 8](08-family-tree.md).)*

### Sturmian word (and the Fibonacci word)

An infinite binary sequence of the lowest complexity still compatible with being
aperiodic — exactly `n + 1` distinct factors of each length `n`. The **Fibonacci
word** `a b a a b a b a a b …` is the canonical example, read off as the cutting
sequence of a line of slope `1/φ` across the integer grid: the most balanced
aperiodic word there is. *([Appendix I](appendix-i-branches.md).)*

### Three-distance theorem

For any `α` and `N`, the points `0, α, 2α, …, (N−1)α` taken modulo 1 cut the
circle into gaps of at most three different lengths, the largest being the sum
of the other two. Conjectured by Steinhaus and proved in 1957–58 by Sós,
Surányi, and Świerczkowski; the gap lengths are governed by the convergents of
`α`. *([Appendix D](appendix-d-frontier.md#e5-the-three-distance-theorem);
[Stop 4](04-golden.md#then-now-next).)*

### Topograph (Conway's)

John Conway's picture of a binary quadratic form, its values arranged on the
infinite trivalent tree of superbases and grown by one arithmetic rule across
each edge (`r + r' = 2(p + q)`). For an indefinite form `x² − d·y²` a single
periodic path — the **river** — separates the positive values from the negative,
and that river is the periodic continued fraction of `√d`, each `+1` well a
solution of Pell's equation.
*([Appendix D](appendix-d-frontier.md); [Stop 6](06-loop-road.md).)*

### Zeckendorf representation

The unique way to write a positive integer as a sum of Fibonacci numbers with no
two *consecutive* Fibonacci numbers used, found by the greedy algorithm. Writing
a `1` for each Fibonacci used and a `0` for each skipped gives Fibonacci coding, a
self-synchronizing variable-length code in which the string `11` never occurs
inside a codeword. *([Appendix I](appendix-i-branches.md); [Stop 4](04-golden.md).)*

## See also

- Appendix A for the proofs that use these terms.
- Appendix C for the sources where each is developed in full.

[← Appendix A — Proofs](appendix-a-proofs.md) · [Route map](index.md) · [Appendix C — References →](appendix-c-references.md)
