[← Stop 14 — The Souvenir Shop](14-souvenir-shop.md) · [Route map](index.md) · [Appendix A — Proofs →](appendix-a-proofs.md)

# Stop 15 — Terminus

> The end of the line is where the map runs out: the questions about continued fractions that no one can yet answer.

## Overview

The bus comes to rest at Terminus, and the honest thing to show you here is not
another theorem but the edge of the map — the places where the road we have been
driving simply stops, and open water begins. Continued fractions are among the
oldest objects in mathematics, and some of the most natural questions about them
remain unsolved after three centuries. This closing stop is a short catalogue of
those questions, each one a place where the tour could, in principle, continue if
only someone found the way.

### Is π "normal" in its continued fraction?

At Stop 9 we saw that `π = [3; 7, 15, 1, 292, …]` has no discernible pattern, and
at Stop 10 that a *typical* number's partial quotients obey the Gauss–Kuzmin
statistics with geometric mean tending to Khinchin's constant `K₀`. Does `π`
behave typically? Two precise questions are **open**:

- **Are the partial quotients of `π` bounded?** No one knows. Billions of terms
  have been computed, occasionally throwing up giants far larger than `292`, but
  whether arbitrarily large terms keep appearing forever is unproven. It is not
  even known whether `π` has *infinitely many* partial quotients equal to `1`.
- **Do `π`'s partial quotients obey Gauss–Kuzmin, with geometric mean `K₀`?**
  Numerically, yes to high precision — but there is no proof. `π` might be one of
  the measure-zero exceptions, like `e`. We cannot rule it out.

These are humbling. We know `π` to trillions of digits and can compute its
continued fraction as far as we like, yet cannot prove the most basic statistical
facts about the sequence we are staring at.

### Is Khinchin's constant irrational?

Khinchin's constant `K₀ = 2.6854520010…` is the universal geometric mean of
almost every number's partial quotients (Stop 10). It has been computed to
thousands of digits. And yet **it is not known whether `K₀` is rational or
irrational**, let alone whether it is transcendental. A constant that governs the
behaviour of *almost all real numbers* has a nature we cannot pin down. The same
holds for **Lévy's constant** `e^{π²/(12 ln 2)}`.

### Is the Euler–Mascheroni constant γ irrational?

The constant `γ = 0.5772156649…`, the limit of `1 + 1/2 + … + 1/n − ln n`,
appears throughout analysis and number theory. Its continued fraction has been
computed to hundreds of billions of terms. And still, **it is unknown whether `γ`
is irrational** — the single most embarrassing open problem in the subject,
because irrationality is exactly the property continued fractions are *built* to
detect (Stop 2: irrational ⇔ infinite expansion). If `γ` were rational its
denominator would have to be astronomically large, but "very probably infinite"
is not a proof.

### Zaremba's conjecture

Not every question here is about a single constant. **Zaremba's conjecture
(1972)** asks: is there a constant `A` such that every positive integer `q` is
the denominator of some fraction `p/q` whose continued fraction has all partial
quotients at most `A`? (Zaremba proposed `A = 5`.) This is a question about which
*denominators* admit "well-behaved" continued fractions, with real consequences
for pseudo-random number generation and numerical integration. Bourgain and
Kontorovich proved in 2014 that *almost all* `q` work — a spectacular near-miss —
but the full conjecture remains open.

### The Littlewood conjecture

The deepest is **Littlewood's conjecture (c. 1930)**: for *every* pair of real
numbers `α, β`,

```
lim inf_{n→∞}  n · ‖nα‖ · ‖nβ‖ = 0,
```

where `‖x‖` is the distance from `x` to the nearest integer. It says two numbers
cannot *both* resist rational approximation too stubbornly at the same
denominators — a two-dimensional cousin of Hurwitz's theorem (Stop 4).
Einsiedler, Katok, and Lindenstrauss proved in 2006, using deep ergodic theory
of the kind glimpsed at Stop 10, that the set of exceptions (if any) has
dimension zero — but whether the set is actually *empty*, and the conjecture
true, is unknown.

### Where the road goes

Every stop on this tour touched one of these frontiers. The depot's Euclidean
descent (Stop 1) becomes the ergodic Gauss map (Stop 10) whose invariant
constant `K₀` we cannot classify. The golden ratio's extremal irrationality
(Stop 4) becomes Littlewood's multidimensional question. The pattern in `e`
(Stop 9) throws the patternlessness of `π` into relief, and that patternlessness
is itself the open problem. The tour is a loop road of its own: the elementary
beginning and the unsolved end are the same questions asked at different depths.

## Worked example

There is nothing new to compute at Terminus — only something to sit with. Run the
Collatz flight of `27` one more time, and read it now as a parable for the whole
tour: a recursion with the simplest possible rule, whose behaviour we can watch
in complete detail and still cannot explain.

```
$ python -m tourbus demo collatz 27
Collatz flight of 27:
  111 steps, peak 9232
```

We can compute the orbit exactly. We can compute a billion orbits exactly. What
we cannot do is *prove* the one thing we most want to know — that it always comes
home. That gap, between what a recursion *does* and what we can *prove* it does,
is the country beyond Terminus. The bus stops here; the mathematics does not.

## Exercises

1. **(★)** Look up the largest known partial quotient of `π` among the first
   million terms. Does its existence prove the partial quotients are unbounded?
   <details><summary>Hint</summary>No — a single large term, however large, says
   nothing about whether they grow *without bound*. Unboundedness is a statement
   about the whole infinite tail.</details>

2. **(★)** State, in one sentence each, why proving `γ` irrational would be a
   natural use of continued fractions.
   <details><summary>Hint</summary>A number is irrational exactly when its
   simple continued fraction is infinite; a proof might exhibit or bound that
   expansion.</details>

3. **(★★)** Zaremba's conjecture with `A = 5` claims every `q` has a partner `p`
   with all partial quotients `≤ 5`. Find such a `p/q` for `q = 7` and `q = 12`.
   <details><summary>Hint</summary>`3/7 = [0; 2, 3]` (quotients ≤ 3);
   `7/12 = [0; 1, 1, 2, 2]` (quotients ≤ 2).</details>

4. **(★★)** Explain how Littlewood's conjecture generalises the one-dimensional
   fact that `‖nα‖` can be made small (Dirichlet's theorem) to two numbers at
   once.
   <details><summary>Hint</summary>Dirichlet gives `n·‖nα‖ < 1` infinitely
   often for one `α`; Littlewood asks the *product* of two such quantities to be
   driven to zero simultaneously.</details>

5. **(★★★)** Pick any open problem above and write a paragraph on which stop of
   this tour it most directly extends, and what a solution might look like.
   <details><summary>Hint</summary>There is no single answer — this is an
   invitation to synthesise the tour. The Khinchin, Gauss–Kuzmin, and Littlewood
   problems all extend Stop 10; the `π` and `γ` questions extend Stops 2 and 9.</details>

## See it move

Open the **Terminus** panel:
[`site/index.html#stop-15-terminus`](../site/index.html#stop-15-terminus). It
gathers the open problems with live links to the relevant widgets from earlier
stops — a map of the frontier, with the roads that lead to it lit up.

## Further reading

- The full reading list of the tour is in
  [Appendix C — References](appendix-c-references.md).
- J. Borwein, A. van der Poorten, et al., *Neverending Fractions* (2014) — a
  modern tour of exactly these open questions; Appendix C.
- J. C. Lagarias, "Continued Fractions and the Riemann Zeta Function" and
  related surveys, for where the subject reaches into modern research.
- On Littlewood: Einsiedler, Katok & Lindenstrauss, *Annals of Mathematics*
  (2006); Appendix C.

Thank you for riding the Recursive Continuance Tour Bus. The route map is always
at [index.md](index.md); the engine is always a single `python -m tourbus` away.

[← Stop 14 — The Souvenir Shop](14-souvenir-shop.md) · [Route map](index.md) · [Appendix A — Proofs →](appendix-a-proofs.md)
