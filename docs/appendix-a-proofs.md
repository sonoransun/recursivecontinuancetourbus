[← Stop 15 — Terminus](15-terminus.md) · [Route map](index.md) · [Appendix B — Glossary →](appendix-b-glossary.md)

# Appendix A — Proofs

The tour keeps the narrative moving by stating theorems and pointing here for the
arguments. These are proof *sketches* — complete enough to follow and to
reconstruct, but written for a curious reader rather than a referee. Each is
keyed to the stop where the result appears.

Throughout, `pₙ/qₙ = [a₀; a₁, …, aₙ]` denotes the convergents built by the
**fundamental recurrence** (Stop 3):

```
pₙ = aₙ·pₙ₋₁ + pₙ₋₂,      p₋₁ = 1,  p₋₂ = 0,
qₙ = aₙ·qₙ₋₁ + qₙ₋₂,      q₋₁ = 0,  q₋₂ = 1.
```

## A.1 The determinant identity (Stop 3)

**Claim.** For all `n ≥ 0`, `pₙ·qₙ₋₁ − pₙ₋₁·qₙ = (−1)ⁿ⁻¹`.

**Proof (induction).** For `n = 0`: `p₀ q₋₁ − p₋₁ q₀ = a₀·0 − 1·1 = −1 = (−1)⁻¹`.
Now assume the identity for `n − 1`. Substitute the recurrences for `pₙ` and
`qₙ`:

```
pₙ qₙ₋₁ − pₙ₋₁ qₙ
  = (aₙ pₙ₋₁ + pₙ₋₂) qₙ₋₁ − pₙ₋₁ (aₙ qₙ₋₁ + qₙ₋₂)
  = aₙ pₙ₋₁ qₙ₋₁ + pₙ₋₂ qₙ₋₁ − aₙ pₙ₋₁ qₙ₋₁ − pₙ₋₁ qₙ₋₂
  = pₙ₋₂ qₙ₋₁ − pₙ₋₁ qₙ₋₂
  = −(pₙ₋₁ qₙ₋₂ − pₙ₋₂ qₙ₋₁)
  = −(−1)ⁿ⁻² = (−1)ⁿ⁻¹.
```

The `aₙ` terms cancel, and what remains is the *previous* determinant with a
sign flip. ∎

**Corollaries.** (i) `gcd(pₙ, qₙ) = 1`: any common divisor divides the
right-hand side `±1`, so convergents are automatically in lowest terms. (ii)
Dividing by `qₙ qₙ₋₁` gives the consecutive-convergent gap

```
pₙ/qₙ − pₙ₋₁/qₙ₋₁ = (−1)ⁿ⁻¹/(qₙ qₙ₋₁),
```

whose sign alternates — the source of the straddle in A.2. A parallel induction,
using `pₙ = aₙ pₙ₋₁ + pₙ₋₂`, gives the two-step identity
`pₙ qₙ₋₂ − pₙ₋₂ qₙ = (−1)ⁿ aₙ`.

## A.2 The straddle and the error bound (Stops 3, 5)

**Claim.** The convergents alternate around `x`, with the even ones below and the
odd ones above, and `|x − pₙ/qₙ| < 1/(qₙ qₙ₊₁) ≤ 1/qₙ²`.

**Proof sketch.** Write `x` itself as a "convergent" by using the *complete
quotient* `xₙ₊₁ = [aₙ₊₁; aₙ₊₂, …] ≥ 1` in place of the final term:

```
x = (xₙ₊₁ pₙ + pₙ₋₁)/(xₙ₊₁ qₙ + qₙ₋₁).
```

(This is the recurrence with the real tail folded back in.) Subtract `pₙ/qₙ` and
use the determinant identity in the numerator:

```
x − pₙ/qₙ = (pₙ₋₁ qₙ − pₙ qₙ₋₁) / (qₙ (xₙ₊₁ qₙ + qₙ₋₁))
          = (−1)ⁿ / (qₙ (xₙ₊₁ qₙ + qₙ₋₁)).
```

The sign `(−1)ⁿ` proves the **straddle**: consecutive convergents lie on opposite
sides of `x`. For the **size**, since `xₙ₊₁ ≥ aₙ₊₁` we have
`xₙ₊₁ qₙ + qₙ₋₁ ≥ aₙ₊₁ qₙ + qₙ₋₁ = qₙ₊₁`, hence

```
|x − pₙ/qₙ| = 1/(qₙ (xₙ₊₁ qₙ + qₙ₋₁)) ≤ 1/(qₙ qₙ₊₁) ≤ 1/qₙ²,
```

the last step because `qₙ₊₁ ≥ qₙ`. A larger `aₙ₊₁` makes `qₙ₊₁` larger and the
bound sharper — the quantitative reason `355/113` (followed by `292`) is so
extraordinarily good. ∎

## A.3 Fibonacci ratios converge to φ (Stop 4)

**Claim.** `F₍ₙ₊₁₎/Fₙ → φ = (1 + √5)/2`.

**Proof (Binet).** The Fibonacci recurrence `Fₙ = Fₙ₋₁ + Fₙ₋₂` has characteristic
equation `t² = t + 1`, with roots `φ = (1+√5)/2` and `ψ = (1−√5)/2`. Every
solution is a combination `Fₙ = Aφⁿ + Bψⁿ`; the initial conditions `F₀ = 0`,
`F₁ = 1` fix `A = 1/√5`, `B = −1/√5`, giving **Binet's formula**

```
Fₙ = (φⁿ − ψⁿ)/√5.
```

Then

```
F₍ₙ₊₁₎/Fₙ = (φⁿ⁺¹ − ψⁿ⁺¹)/(φⁿ − ψⁿ) = φ · (1 − (ψ/φ)ⁿ⁺¹)/(1 − (ψ/φ)ⁿ).
```

Since `|ψ/φ| = |ψ|/φ ≈ 0.382 < 1`, the `(ψ/φ)ⁿ` terms vanish and the ratio tends
to `φ`. Because `φ = [1; 1, 1, …]` and its convergents are exactly `F₍ₙ₊₁₎/Fₙ`
(the recurrence with every `aₙ = 1` reproduces the Fibonacci numbers), this is
the slowest convergence any continued fraction achieves — the analytic face of
`φ` being the *most irrational* number (Hurwitz, Stop 4). ∎

## A.4 Lagrange's periodicity theorem (Stop 6)

**Claim.** The continued fraction of a quadratic irrational is eventually
periodic.

**Proof sketch (finite state space).** Let `x₀ = (P₀ + √d)/Q₀` be a quadratic
surd, with `Q₀ | (d − P₀²)` (arrange this by clearing denominators). Run the
expansion. One checks by induction that every complete quotient keeps the form

```
xₙ = (Pₙ + √d)/Qₙ,   with integer Pₙ, Qₙ,
```

evolving by `Pₙ₊₁ = aₙ Qₙ − Pₙ` and `Qₙ₊₁ = (d − Pₙ₊₁²)/Qₙ` (and `Qₙ | (d −
Pₙ²)` is preserved). The heart of the argument is that, once past the pre-period,
these integers are **bounded**:

```
0 < Qₙ < 2√d      and      0 < Pₙ < √d.
```

The bound on `Pₙ` follows from `0 < xₙ` and `−1 < x̄ₙ < 0` (the conjugate
becomes and stays reduced); the bound on `Qₙ` then follows from
`Qₙ Qₙ₊₁ = d − Pₙ₊₁² > 0` together with the `Pₙ` bound. So each `(Pₙ, Qₙ)` lives
in a **finite** set — at most about `2d` pairs. An infinite sequence drawn from a
finite set must repeat a value; and the moment `(Pₘ, Qₘ) = (Pₙ, Qₙ)` for some
`m < n`, the entire tail from index `m` equals the tail from index `n`, so the
expansion is periodic from index `m` on. ∎

This is the same pigeonhole principle that underlies every "bounded recursion on
a finite state must cycle" argument on the tour, from the loop road to the fractal
attractors of Stop 13.

## A.5 Why Wiener's attack works (Stops 5, 14)

**Claim.** If the RSA private exponent satisfies `d < N^{1/4}/3`, then `k/d` is a
convergent of `e/N`, so `d` is recoverable from the public key `(e, N)`.

**Proof sketch.** By construction `e·d = 1 + k·φ(N)` for some positive integer
`k`, so `k/d` and `e/φ(N)` are related by `|e/φ(N) − k/d| = 1/(d·φ(N))`. We only
know `N`, not `φ(N)`, but for `N = pq` we have
`φ(N) = N − (p + q) + 1`, and `p + q < 3√N`, so `N` and `φ(N)` differ by less
than `3√N`. Estimating the public fraction `e/N` against the secret `k/d`:

```
|e/N − k/d| = |e·d − k·N| / (N·d).
```

Using `e·d = 1 + kφ(N)`, the numerator is `|1 + k(φ(N) − N)| = |1 − k(N − φ(N))|
< 3k√N` (since `k < d < √N` and `N − φ(N) < 3√N`). Therefore

```
|e/N − k/d| < 3k√N/(N·d) = 3k/(d√N) < 3/√N,
```

and pushing the estimate a little (`k < d`, `d < N^{1/4}/3`) yields the sharper

```
|e/N − k/d| < 1/(2d²).
```

That is exactly **Legendre's criterion** (Stop 5): any fraction approximating `x`
to within `1/(2q²)` is a convergent of `x`. Hence `k/d` appears among the
convergents of `e/N`. The attacker expands `e/N` as a continued fraction, and for
each convergent's denominator tests whether it works as a decryption exponent —
one of them is `d`. The threshold `d < N^{1/4}/3` is precisely what makes the
error small enough to trip Legendre's bound. ∎

## See also

- Appendix B for the definitions used above (complete quotient, reduced surd,
  best approximation).
- Appendix C for book-length treatments with full proofs.

[← Stop 15 — Terminus](15-terminus.md) · [Route map](index.md) · [Appendix B — Glossary →](appendix-b-glossary.md)
