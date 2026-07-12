[← Route map](index.md) · [Stop 15 — Terminus](15-terminus.md)

# Appendix D — The Express Line: Fringe Avenues

Past the end of the main route lie six deeper, stranger stops. Each still
computes live and exactly (or rigorously) on the same engine. Ride them all with

```
python -m tourbus frontier
```

or one at a time with `python -m tourbus frontier N`, or reach the individual
demonstrations through `python -m tourbus demo <name>`.

---

## E1 — The Markov Spectrum: the numbers after the golden ratio

The Golden Milestone (Stop 4) crowned φ the hardest number to approximate, with
Hurwitz's constant √5. What is *second*-hardest? The answer is a discrete ladder
— the **Lagrange spectrum** below 3 — governed by the **Markov equation**

```
x² + y² + z² = 3·x·y·z.
```

Its positive integer solutions, the **Markov triples**, grow from `(1, 1, 1)` by
*Vieta jumping*: fix two coordinates and the third satisfies a quadratic with a
second integer root. The largest entries are the **Markov numbers** 1, 2, 5, 13,
29, 34, 89, …; each `m` gives a **Lagrange number** `L_m = √(9m² − 4)/m`, and
these are exactly the spectrum below 3, accumulating at 3.

The miracle that ties it back to continued fractions: `L_m` is the **Markov
value** of a periodic CF word in {1, 2} — the largest, over all cyclic positions,
of the forward continued fraction plus the backward one. φ = `[1;(1)]` sits at √5;
the silver ratio `1 + √2 = [2;(2)]` at √8; the word `[2,2,1,1]` at √221/5.

```
$ python -m tourbus demo markov
The Markov / Lagrange spectrum below 3:
 Markov m  L_m                    value
 --------  ------------------  --------
        1  sqrt(5)             2.236068
        2  2*sqrt(2)           2.828427
        5  1/5*sqrt(221)       2.973214
       13  1/13*sqrt(1517)     2.996053
       29  1/29*sqrt(7565)     2.999207
       34  10/17*sqrt(26)      2.999423
       89  1/89*sqrt(71285)    2.999916
      169  1/169*sqrt(257045)  2.999977
      194  2/97*sqrt(21170)    2.999982
```

Above **Freiman's constant** (≈ 4.5278) the spectrum stops being discrete and
becomes a solid ray `[F, ∞)`; the structure in between is a Cantor-like set still
under active study.

**Exercises.** (★) Verify a Markov triple satisfies the equation. (★★) Show the
silver ratio `1 + √2` achieves √8 by computing `q²·|x − p/q|` along its
convergents. (★★★) Prove Vieta jumping never leaves the positive integers.

---

## E2 — Continuants: the polynomial behind every convergent

The convergent numerators and denominators are not merely numbers; they are
values of one polynomial family, the **continuants** `K(a₁, …, aₙ)`, defined by
the *same* three-term recurrence and satisfying `pₙ = K(a₀, …, aₙ)`,
`qₙ = K(a₁, …, aₙ)`. Two gems:

- **Palindrome:** `K(a₁, …, aₙ) = K(aₙ, …, a₁)` — reversing the partial quotients
  leaves the value unchanged.
- **Euler's rule:** the continuant equals the sum, over every way of striking out
  disjoint *adjacent* pairs, of the product of what remains. So `K(1, 1, …, 1)`
  (n ones) counts domino-and-square tilings and equals the Fibonacci number
  `F_{n+1}`.

```
$ python -m tourbus demo continuant 1 2 3 4 5
Continuant K(1, 2, 3, 4, 5):
  recurrence = 225
  Euler rule = 225
  reversed   = K(5, 4, 3, 2, 1) = 225 (equal)
```

**Exercises.** (★) Compute `K(a, b, c)` by hand and match `abc + a + c`. (★★)
Prove the palindrome identity by induction. (★★★) Show `K(1,…,1)` (n ones) is
`F_{n+1}`.

---

## E3 — Algebraic irrationals: cube roots and an open problem

Quadratic irrationals have periodic continued fractions (Lagrange, Stop 6). Cube
roots do **not** — and, remarkably, *nobody knows whether their partial quotients
are bounded*. Numerically they behave like a "random" real: geometric mean near
Khinchin's constant, with occasional enormous terms.

```
$ python -m tourbus demo cbrt 2
Continued fraction of 2^(1/3):
  [1, 3, 1, 5, 1, 1, 4, 1, 1, 8, 1, 14, 1, 10, 2, 1] ...
  max term 534, geometric mean 2.763 (Khinchin-typical; boundedness OPEN)
```

The **plastic number** ρ (real root of `x³ = x + 1`, the cubic cousin of φ) is a
famous specimen — its expansion produces a `141` at position 12, out of nowhere:

```
$ python -m tourbus demo plastic
The plastic number (x^3 = x + 1):
  [1, 3, 12, 1, 1, 3, 2, 3, 2, 4, 2, 141, 80, 2] ...
  note the 141 at position 12 -- out of nowhere.
```

Contrast with √2 = `[1; (2)]`, whose partial quotients are eternally bounded by 2.
Whether `2^(1/3)` has bounded partial quotients is open, a relative of the
Littlewood conjecture (Stop 15). These expansions are computed rigorously: a
high-precision decimal seed becomes an interval, and only certified terms are
emitted.

**Exercises.** (★) Confirm the plastic number is a root of `x³ − x − 1`. (★★)
Compare the geometric mean of the first 40 partial quotients of `2^(1/3)` and of
`√2`. (★★★) Read about the Littlewood conjecture and its link to bounded partial
quotients.

---

## E4 — Continued-fraction variants: nearest-integer and "minus"

The floor is not the only way to unfold a number.

- The **nearest-integer continued fraction (NICF)** rounds to the *closest*
  integer at each step, allowing negative partial quotients with `|aᵢ| ≥ 2`. It
  converges faster than the regular expansion.
- The **minus (Hirzebruch–Jung) continued fraction** writes
  `a₀ − 1/(a₁ − 1/(a₂ − …))` with every `aᵢ ≥ 2`. It is the language algebraic
  geometers use to resolve cyclic quotient singularities: the `aᵢ` are the
  self-intersection numbers of the exceptional curves.

```
$ python -m tourbus demo nicf 87/32
Three continued fractions of 87/32:
  regular:         [2, 1, 2, 1, 1, 4]
  nearest-integer: [3, -4, 2, 4]
  minus (a>=2):    [3, 4, 3, 2, 2, 2]
```

Notice the NICF is shorter (fewer terms for the same number) and carries a
negative quotient where the regular expansion had a run of 1s.

**Exercises.** (★) Fold each expansion back to `87/32`. (★★) Find a fraction whose
NICF is strictly shorter than its regular CF. (★★★) Look up how the minus-CF of
`n/q` gives the resolution of the `1/n(1, q)` cyclic quotient singularity.

---

## E5 — The three-distance theorem

Scatter the points `0, α, 2α, …, (N−1)α` (mod 1) around a circle. However you
choose α and N, they cut the circle into arcs of **at most three distinct
lengths** — and when there are three, the largest is the sum of the other two.
Steinhaus conjectured it; it was proved in the 1950s.

The continued fraction of α is exactly what controls it: the gap lengths are the
quantities `‖qₖ·α‖` at the convergent denominators, so the point set's
"resolution" jumps precisely at the convergents. Rational approximation and
equidistribution turn out to be one subject.

```
$ python -m tourbus demo three-distance 8/13 12
Three-distance theorem for a=8/13, N=12:
  2 distinct gap lengths: 1/13, 2/13
  largest = sum of the others: True
```

**Exercises.** (★) Verify the three-gap property for α = 1/φ ≈ Fibonacci ratios.
(★★) Show the gap lengths total 1. (★★★) Relate the three lengths to `‖qₖα‖` for
consecutive convergent denominators.

---

## E6 — The Gauss–Kuzmin–Wirsing constant, from scratch

How fast does the Gauss–Kuzmin distribution (Stop 10) set in? The rate is the
**second eigenvalue** of the Gauss map's *transfer operator*

```
(L f)(x) = Σ_{n≥1}  1/(n+x)² · f(1/(n+x)).
```

Its largest eigenvalue is exactly 1 (with the Gauss density as eigenfunction);
the second is the **Gauss–Kuzmin–Wirsing constant** λ ≈ −0.3036300289…, and the
error in the Gauss–Kuzmin theorem decays like `|λ|ⁿ`. Wirsing computed it in 1974;
no closed form is known.

We recover it with no special functions: discretize `L` as a matrix on a grid,
then power-iterate from a **mean-zero** start (because `L` preserves the integral,
the eigenvalue-1 component of a mean-zero function is zero, so the iteration
lands on the second eigenvalue).

```
$ python -m tourbus demo gkw
Gauss-Kuzmin-Wirsing constant (from the transfer operator):
  computed  lambda = -0.3036601
  Wirsing's value  = -0.3036630 (error 2.9e-06)
```

**Exercises.** (★) Confirm the leading eigenvalue is 1 to three digits. (★★) Show
`∫₀¹ (Lf) dx = ∫₀¹ f dx` (the reason 1 is an eigenvalue). (★★★) Improve the
estimate by refining the grid, and watch the error shrink.

---

[← Route map](index.md) · [Stop 15 — Terminus](15-terminus.md)
