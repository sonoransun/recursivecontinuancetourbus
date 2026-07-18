[← Stop 6 — The Loop Road](06-loop-road.md) · [Route map](index.md) · [Stop 8 — The Family Tree →](08-family-tree.md)

# Stop 7 — The Cattle Crossing

> A herd blocks the road, and the toll is an ancient equation: x² − d·y² = 1, whose solutions fall straight out of the loop we just drove.

## Overview

The looping road of Stop 6 was not just pretty; it is a solution machine. The
period of `√d` hands us, for free, the smallest solution of **Pell's equation**

```
x² − d·y² = ±1,
```

for any non-square positive integer `d`. This equation is one of the oldest in
number theory — studied in India by Brahmagupta (7th century) and Bhāskara II
(12th century), rediscovered by Fermat, and misnamed after John Pell by Euler in
a footnote that stuck. It is also, thanks to Archimedes, the reason there is a
cattle crossing at this stop at all.

### Convergents solve Pell

Here is the connection. Suppose `√d` has period length `ℓ`, so
`√d = [a₀; (a₁, …, aℓ)]`. Let `p/q = p₍ℓ₋₁₎/q₍ℓ₋₁₎` be the convergent taken at
the **end of the first period**. Then `(x, y) = (p, q)` is the **fundamental
solution** — the smallest positive solution — of Pell's equation. Which sign it
solves depends on the **parity of the period**:

- If `ℓ` is **even**, then `p² − d q² = +1`. The equation `x² − d y² = −1` has
  **no solution** at all.
- If `ℓ` is **odd**, then `p² − d q² = −1`. Squaring this *unit* — that is,
  taking `(p + q√d)²` — produces the fundamental solution of the `+1` equation.

The reason is the palindrome of Stop 6: the convergent at the period boundary
satisfies `pₙ² − d qₙ² = (−1)ⁿ` by the determinant identity of Stop 3, evaluated
right where the road closes its loop. All larger solutions are powers of the
fundamental one: if `x₁ + y₁√d` is fundamental, then
`xₖ + yₖ√d = (x₁ + y₁√d)ᵏ` runs through *all* positive solutions. One convergent
unlocks infinitely many.

### The wild growth of solutions

Small `d` can hide enormous fundamental solutions. For `d = 2` the answer is a
gentle `(3, 2)`: `3² − 2·2² = 9 − 8 = 1`. For `d = 13` it is already
`(649, 180)`. And `d = 61` — the case **Fermat posed as a challenge in 1657** to
the English mathematicians, knowing full well how brutal it is — has fundamental
solution

```
x = 1766319049,   y = 226153980,
```

a ten-digit `x` for a two-digit `d`. There is no smooth relationship between the
size of `d` and the size of its smallest solution; it depends entirely on the
length of the period of `√d`, which behaves erratically. This is what makes
Pell's equation a genuine test of method rather than patience — brute-force
search over `y` would never reach `226153980`, but the continued fraction walks
straight to it.

### The chakravala comes first

Bhāskara II did not merely study `d = 61` — he solved it, around 1150, by the
**chakravala** ("cyclic") method: compose trial solutions of `x² − d·y² = k`
using Brahmagupta's 628 CE **bhāvanā** identity, and turn the wheel until `k`
lands on `1`. Fermat's 1657 challenge was, unknowingly, a rerun of a
five-hundred-year-old exercise. The chakravala never mentions a continued
fraction, yet it arrives at exactly the convergents of `√61` — two roads, one
summit. Watch it run at Heritage stop H2 (Appendix H).

### Archimedes' cattle

The most famous Pell equation is disguised as a poem. **Archimedes' cattle
problem** (c. 250 BC) asks for the number of bulls and cows of the Sun god's
herd, in four colours, subject to a list of ratio and square/triangular
constraints. Reduced, it becomes a Pell equation `x² − 4729494·y² = 1`. Its
**smallest solution has 206,545 digits** — the total herd is a number so vast it
would fill a book. Archimedes almost certainly could not have computed it (it was
first fully evaluated in 1965 with a computer), but the fact that the problem is
*well-posed* and has a definite, finite, astronomically large answer is itself a
triumph of the continued-fraction method. The herd exists; it just does not fit
in the universe.

### Units in quadratic fields

For the algebraically inclined: solving `x² − d y² = ±1` is the same as finding
the **units** of the ring `ℤ[√d]` — the elements with a multiplicative inverse.
The fundamental solution is the *fundamental unit*, and Dirichlet's unit theorem
guarantees exactly this infinite cyclic structure. Pell's equation is the
first place the continued fraction reaches out of arithmetic and into the
algebra of number fields, a thread that runs through much of modern number
theory.

## Worked examples

Solve Fermat's challenge case, `d = 61`, and watch a two-digit input produce a
ten-digit answer — the fundamental solution the continued fraction of `√61`
delivers at the end of its (odd) period, then squared to reach `+1`:

```
$ python -m tourbus demo pell 61
x^2 - 61 y^2 = 1  fundamental solution:
  x = 1766319049
  y = 226153980
  verifies: True
```

Check it by hand if you dare: `1766319049² − 61·226153980² = 1`, exactly. For
contrast, the gentle cases `d = 2` and `d = 13` show how wildly the difficulty
swings with `d`:

```
$ python -m tourbus demo pell 2
x^2 - 2 y^2 = 1  fundamental solution:
  x = 3
  y = 2
  verifies: True
```

```
$ python -m tourbus demo pell 13
x^2 - 13 y^2 = 1  fundamental solution:
  x = 649
  y = 180
  verifies: True
```

`d = 2` (period 1, `√2 = [1; (2)]`) gives `(3, 2)` from the very first
convergent; `d = 13` needs a longer period and lands on `(649, 180)`; `d = 61`
explodes. The size of the answer is the length of the loop road, nothing else.

## Exercises

1. **(★)** Verify the `d = 2` solution by hand, and find the *next* solution
   after `(3, 2)` by computing `(3 + 2√2)²`.
   <details><summary>Hint</summary>`(3 + 2√2)² = 17 + 12√2`, so the next
   solution is `(17, 12)`; check `17² − 2·12² = 1`.</details>

2. **(★)** From `demo cf sqrt2`, read off the convergent at the end of the first
   period and confirm it is the Pell solution `(3, 2)`.
   <details><summary>Hint</summary>The period of `√2` has length 1, so the
   fundamental solution is the convergent `p₁/q₁ = 3/2`.</details>

3. **(★★)** The period of `√13` is odd. Predict whether `x² − 13 y² = −1` has a
   solution, and find the smallest one.
   <details><summary>Hint</summary>Odd period means `−1` *is* solvable;
   `18² − 13·5² = 324 − 325 = −1`, so `(18, 5)` works, and its square gives
   `(649, 180)`.</details>

4. **(★★)** Explain why `x² − 4 y² = 1` has no interesting solutions, connecting
   to Stop 6.
   <details><summary>Hint</summary>`4` is a perfect square, so `√4 = 2` is
   rational and its continued fraction does not loop — there is no period to
   read a solution from.</details>

5. **(★★★)** Show that if `(x₁, y₁)` is the fundamental solution of `+1`, then
   every positive solution is `(xₖ, yₖ)` with `xₖ + yₖ√d = (x₁ + y₁√d)ᵏ`.
   <details><summary>Hint</summary>The solutions form a group under
   multiplication in `ℤ[√d]`; a fundamental unit generates the whole positive
   cone. See Appendix A / C on units.</details>

## See it move

Open the **Cattle Crossing** widget:
[`site/index.html#stop-7-cattle`](../site/index.html#stop-7-cattle). Enter a `d`
and watch the convergents of `√d` scroll by until the one at the period boundary
lights up as the Pell solution, with a running check of `x² − d y²`.

**Try it live:** the Pell Playground preset to [Fermat's d = 61](../site/index.html#w7?d=61).
## Further reading

- H. W. Lenstra, "Solving the Pell Equation," *Notices of the AMS* (2002) — a
  superb modern survey; Appendix C.
- Hardy & Wright, §§10.11–10.12 on Pell's equation via continued fractions.
- I. Vardi, "Archimedes' Cattle Problem," *American Mathematical Monthly* (1998).
- Appendix A of this tour for the parity-of-period argument.

[← Stop 6 — The Loop Road](06-loop-road.md) · [Route map](index.md) · [Stop 8 — The Family Tree →](08-family-tree.md)
