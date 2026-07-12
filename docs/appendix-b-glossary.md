[← Appendix A — Proofs](appendix-a-proofs.md) · [Route map](index.md) · [Appendix C — References →](appendix-c-references.md)

# Appendix B — Glossary

The vocabulary of the tour, in alphabetical order. Each entry names the stop
where the term is introduced.

### Best approximation of the first kind

A fraction `p/q` that minimises the *absolute* distance `|x − p/q|` among all
fractions with denominator at most `q`. These include the convergents **and**
certain semiconvergents. Contrast with the second kind. *(Stop 5.)*

### Best approximation of the second kind

A fraction `p/q` that minimises `|q·x − p|` — the distance weighted by the
denominator — among all fractions with denominator at most `q`. By **Lagrange's
theorem**, these are *exactly* the continued-fraction convergents. This is the
stronger, cleaner notion, and the one usually meant by "best rational
approximation." *(Stop 5.)*

### Bihomographic transform

A function of two variables `z(x, y) = (a·xy + b·x + c·y + d)/(e·xy + f·x + g·y +
h)` with an eight-integer state, used by Gosper's algorithm to compute `x + y`,
`x · y`, and other binary operations directly on continued-fraction streams. It
has three moves — ingest from `x`, ingest from `y`, or emit an output term.
*(Stop 11.)*

### Complete quotient

The value `xₙ = [aₙ; aₙ₊₁, aₙ₊₂, …]` of the entire tail of a continued fraction
from position `n` onward. Always `≥ 1` for `n ≥ 1`, and satisfies
`x = (xₙ pₙ₋₁ + pₙ₋₂)/(xₙ qₙ₋₁ + qₙ₋₂)`. The tool of the error-bound proof in
Appendix A. *(Stop 3.)*

### Convergent

The rational `pₙ/qₙ = [a₀; a₁, …, aₙ]` obtained by truncating a continued
fraction after `n + 1` terms. Convergents are automatically in lowest terms,
straddle the true value in alternation, and are the best approximations of the
second kind. *(Stop 3.)*

### Corecursion

A definition scheme that *produces* an infinite structure on demand, rather than
consuming a finite input down to a base case (ordinary recursion). Gosper's
stream arithmetic is corecursive: it has no base case and is judged correct by
how it keeps emitting valid terms forever, not by how it halts. *(Stop 11.)*

### Farey sequence `Fₙ`

The ascending list of all fractions in `[0, 1]` with denominator at most `n`, in
lowest terms. Adjacent fractions `a/b < c/d` satisfy the neighbour relation
`bc − ad = 1`, and the mediant of two neighbours is the next fraction to appear
between them. Closely tied to the Stern–Brocot tree. *(Stop 8.)*

### Gauss map

The transformation `T(x) = {1/x} = 1/x − ⌊1/x⌋` on `(0, 1)`, which strips the
first partial quotient off a continued fraction and shifts the rest forward. It
preserves the **Gauss measure** `dμ = (1/ln 2)·1/(1+x) dx` and is ergodic; the
statistics of continued fractions are the dynamics of this one map. *(Stop 10.)*

### Homographic transform

A function of one variable `z(x) = (a·x + b)/(c·x + d)` with integer state
`(a, b, c, d)` — also called a Möbius or fractional-linear transform. The
one-input building block of Gosper's algorithm, with two moves: ingest an input
term or emit an output term when the floor is determined. A **purely periodic**
continued fraction is a fixed point of such a map. *(Stops 11, 13.)*

### Mediant

The fraction `(a + c)/(b + d)` formed from `a/b` and `c/d` by adding numerators
and denominators separately. It lies strictly between two neighbours and is the
generating operation of the Stern–Brocot tree and the Farey sequences.
*(Stop 8.)*

### Partial quotient

One of the terms `aₙ` in `[a₀; a₁, a₂, …]`. The first, `a₀`, is any integer;
every later one is a positive integer `aₙ ≥ 1`. For a rational, the partial
quotients are exactly the quotients produced by Euclid's algorithm. *(Stops 1,
2.)*

### Primitive recursion

The class of functions built from basic functions (zero, successor, projection)
by composition and *bounded* recursion — essentially, everything computable with
`for`-loops whose bounds are known in advance. The Ackermann function is total
and computable but **not** primitive recursive: it grows faster than any function
in this class. *(Stop 12.)*

### Quadratic irrational (quadratic surd)

An irrational root of an integer quadratic `ax² + bx + c = 0`, equivalently a
number of the form `(P + √d)/Q` with `d` a non-square positive integer. By
**Lagrange's theorem**, these are exactly the numbers with eventually periodic
continued fractions. *(Stop 6.)*

### Reduced surd

A quadratic irrational `x` with `x > 1` whose conjugate `x̄` (the other root,
`√d ↦ −√d`) lies strictly in `(−1, 0)`. By **Galois' theorem**, a surd's
continued fraction is *purely* periodic (periodic from the very first term) if
and only if it is reduced. *(Stop 6.)*

### Semiconvergent

An intermediate fraction obtained by using a partial quotient `1 ≤ k < aₙ` in the
convergent recurrence: `(k·pₙ₋₁ + pₙ₋₂)/(k·qₙ₋₁ + qₙ₋₂)`. Semiconvergents fill
the gaps between successive convergents and appear among the best approximations
of the first kind, though not the second. *(Stop 5.)*

### Similarity dimension

For a self-similar set made of `N` copies of itself each scaled by `r < 1`, the
number `d = ln N / ln(1/r)`. It generalises ordinary dimension to fractional
values: Cantor set `≈ 0.6309`, Koch curve `≈ 1.2619`, Sierpiński triangle
`≈ 1.5850`, and space-filling curves (dragon, Hilbert) exactly `2`. *(Stop 13.)*

### Stern–Brocot tree

The infinite binary tree of all positive rationals, each appearing exactly once
in lowest terms, generated by repeatedly inserting mediants between `0/1` and
`1/0`. A node's Left/Right address has run-lengths equal to its continued
fraction's partial quotients (last run off by one). *(Stop 8.)*

## See also

- Appendix A for the proofs that use these terms.
- Appendix C for the sources where each is developed in full.

[← Appendix A — Proofs](appendix-a-proofs.md) · [Route map](index.md) · [Appendix C — References →](appendix-c-references.md)
