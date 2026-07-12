[← Stop 1 — The Depot](01-depot.md) · [Route map](index.md) · [Stop 3 — The Engine Room →](03-engine-room.md)

# Stop 2 — The Unfolding Road

> The road ahead is a fraction that never quite closes: the continued fraction, Euclid's algorithm let loose on the real numbers.

## Overview

Leaving the depot, the algorithm we just watched reduce two integers now runs
on a single real number, and the quotients it produces unfold into a road
called a **continued fraction**. Where an ordinary decimal writes a number as a
sum of tenths, hundredths, and thousandths — a base chosen by our ten fingers —
a continued fraction writes it as a tower of nested reciprocals, a
representation the number chooses for itself.

### Notation

A **simple continued fraction** is written

```
[a₀; a₁, a₂, a₃, …] = a₀ + 1/(a₁ + 1/(a₂ + 1/(a₃ + …))).
```

The numbers `aₙ` are the **partial quotients**. By convention `a₀` is an integer
(possibly negative or zero), and every later `aₙ` is a positive integer,
`aₙ ≥ 1`. The semicolon after `a₀` marks the boundary between the integer part
and the fractional tail; the commas separate the rest. This tour writes finite
expansions as `[a₀; a₁, …, aₙ]` and periodic ones — coming at Stop 6 — with a
parenthesised repeating block, as in `[1; (2)]` for `√2`.

### How the road is paved

To expand any real `x`, take its floor and invert the leftover:

1. Set `a₀ = ⌊x⌋`. If `x = a₀`, stop.
2. Otherwise let `x₁ = 1/(x − a₀)` (a number greater than 1) and repeat with
   `x₁`.

This is Euclid's algorithm again. If `x = p/q` is rational, then `a₀ = ⌊p/q⌋` is
Euclid's first quotient, `x − a₀ = (p mod q)/q`, and inverting gives
`q/(p mod q)` — exactly the next division Euclid would perform. **The partial
quotients of a rational `p/q` are precisely the quotients Euclid produces while
computing `gcd(p, q).`** That is why Stop 1 kept the quotients: they were the
road all along.

### Rational if and only if finite

Because Euclid's algorithm terminates on integers, **a number is rational
exactly when its continued fraction is finite**, and irrational exactly when it
is infinite. A finite expansion halts when some `x − aₙ` hits zero; an
irrational never gives a zero remainder, so the road runs forever. This is a
cleaner rational/irrational test than decimals offer: `1/3 = 0.333…` looks
infinite in base ten but is just `[0; 3]`, while `√2` is genuinely unending in
both.

### The two faces of a rational

There is one small ambiguity. Every rational has **exactly two** finite
continued-fraction representations, related by splitting off the last term:

```
[a₀; a₁, …, aₙ]  with aₙ ≥ 2   equals   [a₀; a₁, …, aₙ − 1, 1].
```

For example `[4; 2, 6, 7] = [4; 2, 6, 6, 1]`, because `7 = 6 + 1/1`. To make
the expansion unique we adopt the standard convention that the last partial
quotient is at least `2` (equivalently, an expansion of length greater than one
never ends in `1`). This tie has real consequences at Stop 8, where the two
forms are the two ways to walk the last step of the Stern–Brocot tree, and at
Stop 3, where they explain why convergents come in over-and-under pairs.

### Why bother?

Decimals are convenient for arithmetic but terrible at revealing a number's
approximation-theoretic character. Continued fractions are the opposite:
awkward to add (Stop 11 is entirely about fixing that) but supreme at answering
"what is the best simple fraction close to `x`?" Truncating a decimal gives you
the best fraction with a *power-of-ten* denominator; truncating a continued
fraction gives you the best fraction with *any* denominator that small — the
**convergents** of Stop 3. The road is unfolding toward the best possible
rational approximations, and it does so with denominators far smaller than
decimals would demand.

## Worked examples

Expand the rational `415/93`. The partial quotients are `4, 2, 6, 7` — and if
you run `demo euclid 415 93` you will see those same four numbers fall out of
the division ladder:

```
$ python -m tourbus demo cf 415/93
continued fraction of 415/93:
  [4; 2, 6, 7]

 n  a_n  p/q            value      error
 -  ---  ------  ------------  ---------
 0    4  4/1     4.0000000000  +4.62e-01
 1    2  9/2     4.5000000000  -3.76e-02
 2    6  58/13   4.4615384615  +8.27e-04
 3    7  415/93  4.4623655914  +0.00e+00
```

The final convergent equals `415/93` exactly and the error hits zero — the
hallmark of a rational's finite road. Compare Euclid on the same pair, whose
quotients match term for term:

```
$ python -m tourbus demo euclid 415 93
  415 = 4 x 93 + 43
  93 = 2 x 43 + 7
  43 = 6 x 7 + 1
  7 = 7 x 1 + 0
  continued fraction = [4; 2, 6, 7]
```

The tool always reduces to lowest terms first, so an unreduced fraction and its
reduced form share a road. Feeding it `1071/462`, which reduces to `51/22`,
gives the depot's quotients back again:

```
$ python -m tourbus demo cf 1071/462
continued fraction of 51/22:
  [2; 3, 7]

 n  a_n  p/q           value      error
 -  ---  -----  ------------  ---------
 0    2  2/1    2.0000000000  +3.18e-01
 1    3  7/3    2.3333333333  -1.52e-02
 2    7  51/22  2.3181818182  +0.00e+00
```

## Exercises

1. **(★)** Expand `[3; 4, 12, 4]` back into an ordinary fraction by hand, then
   check with `demo cf` on your answer.
   <details><summary>Hint</summary>Work inside-out: `4 + 1/4 = 17/4`, then
   `12 + 4/17 = 208/17`, and so on.</details>

2. **(★)** Write both continued-fraction representations of `9/7`.
   <details><summary>Hint</summary>One ends in a term ≥ 2; split that last term
   into `(term − 1) + 1/1`.</details>

3. **(★★)** Show that `[0; a₁, a₂, …]` is the reciprocal of `[a₁; a₂, …]`
   whenever the latter exceeds 1. What does this say about `demo cf 93/415`?
   <details><summary>Hint</summary>Prepending a `0` and inverting are the same
   operation; the road of `93/415` is `415/93`'s road with a `0` bolted on the
   front.</details>

4. **(★★)** Explain why no continued fraction has a partial quotient of `0`
   after the first term.
   <details><summary>Hint</summary>At each step `x − aₙ` lies in `[0, 1)`, so
   its reciprocal is `> 1`, forcing the next floor to be at least 1.</details>

5. **(★★★)** Prove that the continued fraction of a rational is finite by
   arguing that the sequence of remainders is strictly decreasing in the
   integers.
   <details><summary>Hint</summary>Each `xₙ = 1/(xₙ₋₁ − aₙ₋₁)` has a denominator
   that is a strictly smaller positive integer than the previous one; a
   decreasing sequence of positive integers cannot be infinite.</details>

## See it move

Open the **Unfolding Road** widget:
[`site/index.html#stop-2-road`](../site/index.html#stop-2-road). Type any
rational or a named constant and watch the fraction unfold one nested reciprocal
at a time, with each partial quotient peeled off as it is computed.

## Further reading

- Khinchin, *Continued Fractions*, §§1–3 for the definition and the
  rational/irrational dichotomy. See Appendix C.
- Hardy & Wright, *An Introduction to the Theory of Numbers*, Chapter X, §§10.1–10.5.
- C. D. Olds, *Continued Fractions* (MAA New Mathematical Library), an
  approachable book-length introduction; Appendix C.

[← Stop 1 — The Depot](01-depot.md) · [Route map](index.md) · [Stop 3 — The Engine Room →](03-engine-room.md)
