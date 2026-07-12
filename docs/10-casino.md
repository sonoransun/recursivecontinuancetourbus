[← Stop 9 — Celebrity Sightings](09-celebrity.md) · [Route map](index.md) · [Stop 11 — The Infinite Assembly Line →](11-assembly-line.md)

# Stop 10 — The Casino

> The partial quotients of a "typical" number are not patternless — they obey iron statistical laws, and the house always wins by the same constant.

## Overview

At Stop 9 the partial quotients of `π` *looked* random. This stop makes that
precise. If you pick a real number at random, its continued fraction is
unpredictable term by term — but *in aggregate* it obeys laws as rigid as a
casino's odds. Three constants govern the tables here: the Gauss–Kuzmin
distribution, Khinchin's constant, and Lévy's constant. Almost every number
pays out the same, and the exceptions (rationals, quadratic surds, and a few
famous constants like `e`) are a measure-zero set of lucky gamblers.

### The Gauss map

The dealer is the **Gauss map**:

```
T(x) = {1/x} = 1/x − ⌊1/x⌋,    for x ∈ (0, 1),
```

the fractional part of the reciprocal. Applied to `x = [0; a₁, a₂, a₃, …]` it
strips off the first partial quotient and shifts the rest forward:
`T(x) = [0; a₂, a₃, …]`. So iterating `T` deals out the partial quotients one at
a time — `a₁ = ⌊1/x⌋`, then `a₂ = ⌊1/T(x)⌋`, and so on. Studying the statistics
of continued fractions is studying the **dynamics** of this one map, which is
why this branch of the subject is called the *ergodic theory* of continued
fractions.

Gauss found (in an 1812 letter to Laplace) that `T` preserves a special
probability distribution, the **Gauss measure**

```
dμ = (1/ln 2) · 1/(1 + x) dx    on [0, 1].
```

The map spreads points out according to this density and never disturbs it — it
is the invariant "house edge." Because `T` is also *ergodic*, time averages
along one number's orbit equal space averages over all numbers: what one typical
continued fraction does over the long run is what almost every number does.

### Gauss–Kuzmin: the odds on each digit

From the invariant measure comes the distribution of the partial quotients
themselves. The **Gauss–Kuzmin theorem** (Gauss conjectured it; Kuzmin proved a
rate in 1928) states that for almost every `x`, the fraction of partial
quotients equal to `k` tends to

```
P(aₙ = k) → log₂(1 + 1/(k(k+2))).
```

The odds decay fast. A partial quotient is `1` about `log₂(4/3) ≈ 41.5%` of the
time, `2` about `17.0%`, `3` about `9.3%`, and so on. So a "typical" continued
fraction is dominated by small terms, with `1` alone accounting for over
two-fifths of them — which is why numbers like `φ` (all `1`s) and the Fibonacci
worst case of Stop 1 sit at the boundary of typical behaviour.

### Khinchin's constant

Here is the theorem that makes this a casino. **Khinchin proved in 1935** that
for almost every real `x`, the **geometric mean** of the first `n` partial
quotients converges to a single universal constant, *independent of `x`*:

```
(a₁ · a₂ · … · aₙ)^{1/n} → K₀ = 2.6854520010…
```

Read that again: the *same* number `K₀` for almost every `x`. Your number and
mine, chosen at random, produce partial quotients that multiply out to the same
average in the limit. Khinchin's constant is defined by the product
`K₀ = ∏_{k≥1} (1 + 1/(k(k+2)))^{log₂ k}`. The measure-zero exceptions are the
usual suspects — rationals (finite), quadratic surds (periodic, so their
geometric mean is the mean of one period), and, curiously, `e`, whose growing
even terms drag its geometric mean to infinity. Whether famous constants like
`π` actually hit `K₀` is, like so much of Stop 9, unknown.

### Lévy's constant

A companion law governs the *denominators*. **Lévy's constant** (Khinchin and
Lévy, 1930s) says the convergent denominators grow at a universal exponential
rate for almost every `x`:

```
qₙ^{1/n} → e^{π²/(12 ln 2)} = 3.2758229187…
```

This ties back to the error bound of Stop 3: since `|x − pₙ/qₙ| ≈ 1/qₙ²`, the
approximation error of a typical number shrinks like `e^{−π²n/(6 ln 2)}` — a
fixed exponential rate, the same for almost everybody. The house edge is a
constant, and it is spelled `π²/(12 ln 2)`.

## Worked examples

Estimate Khinchin's constant by sampling random numbers, expanding each, and
taking the geometric mean of all their partial quotients. With several thousand
terms the estimate is already close to `K₀ = 2.68545…` (convergence is famously
slow, so it will not be exact):

```
$ python -m tourbus demo khinchin
geometric mean of 11849 partial quotients:
  2.65801   (Khinchin's constant = 2.68545...)
```

The estimate `2.65801` lands within about 1% of the true value from a few
thousand terms — remarkable, given that these partial quotients came from
*unrelated* random numbers yet conspire to the same mean, exactly as Khinchin's
theorem demands.

Now the digit distribution. The `gauss` demo tallies how often each partial
quotient value appears across many random expansions and compares it to the
Gauss–Kuzmin prediction:

```
$ python -m tourbus demo gauss
Gauss-Kuzmin digit frequencies (observed vs predicted):
   1 ██████████████████████████████ 0.5094   (predict 0.4150)
   2 █████████████ 0.2124   (predict 0.1699)
   3 ███████ 0.1164   (predict 0.0931)
   4 ████ 0.0721   (predict 0.0589)
   5 ███ 0.0514   (predict 0.0406)
   6 ██ 0.0383   (predict 0.0297)
```

The *shape* is unmistakable — a steep decay with `1` the most common value by
far, each successive value roughly halving — and it tracks the Gauss–Kuzmin law
across the board. (The observed frequencies here sit a little above the
predictions because the sample draws finite truncations of dyadic rationals, a
mild bias; with longer, less structured expansions the two columns converge.)
The dealer's odds are visible even in a rough sample.

## Exercises

1. **(★)** Compute the Gauss–Kuzmin probabilities for `k = 1, 2, 3` by hand and
   confirm they match the `predict` column above.
   <details><summary>Hint</summary>`log₂(1 + 1/(1·3)) = log₂(4/3) ≈ 0.415`;
   `log₂(1 + 1/(2·4)) = log₂(9/8) ≈ 0.170`.</details>

2. **(★)** Apply the Gauss map to `x = 1/√2 ≈ 0.7071` twice by hand and read off
   the first two partial quotients.
   <details><summary>Hint</summary>`1/x ≈ 1.414`, so `a₁ = 1` and
   `T(x) = 0.414…`; then `1/0.414 ≈ 2.414`, so `a₂ = 2`.</details>

3. **(★★)** Why is `e` an exception to Khinchin's theorem? Estimate the
   geometric mean of `e`'s first nine partial quotients and note the trend.
   <details><summary>Hint</summary>The even terms `2, 4, 6, …` grow without
   bound, so the geometric mean diverges to infinity rather than to `K₀`.</details>

4. **(★★)** Run `demo khinchin` a few times (the sample is seeded) and note how
   close the estimate stays to `2.685`. Why is convergence so slow?
   <details><summary>Hint</summary>The geometric mean is dominated by rare large
   partial quotients, whose contribution has heavy-tailed variance — the sum
   `Σ log aₙ` converges slowly.</details>

5. **(★★★)** Derive that `T` preserves the Gauss measure: show that the density
   `1/(1+x)` satisfies the transfer-operator fixed-point equation
   `ρ(x) = Σ_{k≥1} ρ(1/(x+k)) · 1/(x+k)²`.
   <details><summary>Hint</summary>Substitute `ρ(x) = 1/(1+x)` and telescope the
   sum `Σ_k [1/(x+k) − 1/(x+k+1)]`.</details>

## See it move

Open the **Casino** widget:
[`site/index.html#stop-10-casino`](../site/index.html#stop-10-casino). Spin up
thousands of random continued fractions and watch the Gauss–Kuzmin histogram
fill in and the running geometric mean settle toward Khinchin's constant.

## Further reading

- Khinchin, *Continued Fractions*, §§14–16 — the source, including the proof of
  Khinchin's theorem. See Appendix C.
- Rockett & Szüsz, *Continued Fractions*, Chapters IV–V, on the Gauss map and
  ergodic theory; Appendix C.
- D. H. Bailey, J. M. Borwein & R. Crandall, "On the Khintchine Constant,"
  *Math. Comp.* (1997), for high-precision computation of `K₀`.
- P. Lévy, *Théorie de l'addition des variables aléatoires* (1937), for Lévy's
  constant.

[← Stop 9 — Celebrity Sightings](09-celebrity.md) · [Route map](index.md) · [Stop 11 — The Infinite Assembly Line →](11-assembly-line.md)
