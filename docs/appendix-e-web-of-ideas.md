[← Route map](index.md) · [The Express Line](appendix-d-frontier.md)

# Appendix E — The Web of Ideas

> Recursion, continued fractions, π, and physics are not four subjects. They are
> one gesture — *the infinite defined by finite self-application* — seen from
> four directions.

The whole tour has been a single idea trying on costumes. This appendix takes
them all off. Nothing here is loose analogy for its own sake: each link is a
theorem or an experiment, and several of them you can run from the command line.

## 1. One idea: the fixed point

Ask what a continued fraction *is*, at the deepest level, and the answer is: a
**fixed point**. The golden ratio is not merely written `[1; 1, 1, …]`; it is the
solution of

```
φ = 1 + 1/φ,
```

the fixed point of the map `x ↦ 1 + 1/x`. Every purely periodic continued
fraction (Stop 6) is the fixed point of a Möbius transformation — an element of
the modular group `PSL(2, ℤ)` — and *that* is why periodic continued fractions
are exactly the quadratic irrationals.

Recursion is the same move in a different key: to define a thing in terms of
itself is to name a fixed point. But there are two kinds, and continued fractions
live on the far side of the divide:

- A **least fixed point** is built from the bottom by well-founded steps —
  ordinary recursion, induction, the factorial, the natural numbers. It
  *terminates*.
- A **greatest fixed point** is a structure you can unfold forever without ever
  reaching a base case — an infinite continued fraction, a stream, a process.
  This is **corecursion**, and its watchword is not "termination" but
  "productivity": each step must *emit* something.

The Y combinator (Stop 12) is the pure syntax of "define by self-reference";
Gosper's stream arithmetic (Stop 11) is corecursion made to compute — it produces
one certain partial quotient at a time from inputs it never finishes reading.
The same fixed-point logic runs underneath the whole map of mathematics: Banach's
contraction theorem gives fractals as fixed points of an iterated function system
(Stop 13); Tarski's theorem gives the meaning of recursive programs; Brouwer's
gives economic equilibria; Kleene's recursion theorem and Gödel's diagonal lemma
give a program that can quote itself. A continued fraction is the friendliest
member of this family — a fixed point you can hold in your hand.

## 2. Continued fractions as a microscope: renormalization

The Gauss map `T(x) = {1/x}` (Stop 10) does one thing: it throws away a number's
integer part after turning it inside out, exposing the next partial quotient. Run
it repeatedly and you *read* the continued fraction. But look again at what the
step is — invert, and rescale. It is a **renormalization**: zoom in by one level,
and describe what you see in the same language.

That is precisely the physicist's renormalization group: describe a system, change
the scale, and hunt for the fixed point of the rescaling. When such a fixed point
exists, its neighbourhood is **universal** — details wash out. Feigenbaum's
constant `δ ≈ 4.669`, the rate at which period-doubling cascades into chaos, is an
eigenvalue of the linearized renormalization operator. The Gauss–Kuzmin–Wirsing
constant of Stop E6, `λ ≈ −0.3036`, is the second eigenvalue of the Gauss map's
transfer operator, setting the rate at which random continued fractions forget
where they started. Two different operators, the same story: **a rate of
convergence is a number in an operator's spectrum.**

There is a geometric payoff. The periodic points of the Gauss map — the quadratic
irrationals — are the self-similar numbers, and they correspond one-to-one with
the **closed geodesics on the modular surface**, the quotient of the hyperbolic
plane by `PSL(2, ℤ)`. A continued fraction is the "cutting sequence" of a geodesic
crossing the tessellation of hyperbolic space (Artin, 1924; Series, 1985). Number
theory, dynamics, and hyperbolic geometry are here the same subject, and the
bridge is the humble continued fraction.

## 3. Irrationality as a physical quantity

Here is the turn that surprises people: in physics, *how irrational a number is*
is not decoration. It decides whether a system holds together.

Perturbation theory in celestial mechanics is haunted by **small divisors** —
terms like `1 / (n·ω − m)` where `ω` is a frequency ratio. If `ω` is close to a
rational (well approximated by `m/n`), the divisor is tiny and the series
explodes; Poincaré found this obstruction fatal to the naïve dream of a stable
solar system. The **KAM theorem** (Kolmogorov 1954, Arnold, Moser) rescues it: a
quasi-periodic orbit — an invariant torus — *survives* a small perturbation
provided its frequency ratio is **badly approximable**, i.e. Diophantine.

And which number is worst approximated by rationals? The golden ratio (Stop 4,
Hurwitz's theorem), because its continued fraction is all 1s. So the **most robust
orbit is the golden one.** In the Chirikov standard map, as you crank up the
coupling, the very last invariant curve to break is the golden-mean curve, at the
critical value `K_c ≈ 0.9716` (Greene's residue criterion, 1979). The "most
irrational number" of Stop 4 is, physically, the most stable rhythm. When
irrationality fails — at resonances — you get the Kirkwood gaps swept clean in the
asteroid belt where orbital periods hit simple ratios with Jupiter, and the locked
Laplace resonance 1:2:4 of Io, Europa, and Ganymede.

## 4. Mode-locking, Arnold tongues, and the devil's staircase

Drive an oscillator and it will try to **lock** its rhythm to a rational multiple
of the drive — a heartbeat entrains to a pacemaker, a Josephson junction to a
microwave, Saturn's ring particles to a moon. The mathematical skeleton is the
**circle map**, and its **winding number** (the average rotation per step) locks
onto rationals over whole intervals of the parameter. The interval where the
winding number equals `p/q` is an **Arnold tongue**, and the tongues are arranged
by exactly the structure of Stop 8: between the tongues for `a/b` and `c/d` sits
the tongue for the mediant `(a+c)/(b+d)` — the Stern–Brocot tree, drawn in a
physics experiment.

Plot the winding number against the drive and you get a **devil's staircase**:
constant on every rational, rising only on the irrational dust between. Its shape
is governed by **Minkowski's question-mark function** (Stop 8), the singular,
strictly increasing function that maps quadratic irrationals to rationals and has
derivative zero almost everywhere. The staircase of a driven heart and the
question-mark function of number theory are the same curve.

## 5. Fractal spectra: the butterfly and the quasicrystal

Put an electron on a two-dimensional crystal in a magnetic field. Whether the
magnetic flux through a unit cell is a *rational* or *irrational* multiple of the
flux quantum changes everything (Harper's equation, the almost-Mathieu operator).
Plot the allowed energies against the flux and a self-similar fractal appears —
the **Hofstadter butterfly** (1976). Its gaps are labeled by the continued-fraction
convergents of the flux ratio, and at irrational flux the spectrum is a Cantor set
of measure zero — the "Ten Martini Problem," settled by Avila and Jitomirskaya
(2009). The badly-approximable numbers of Stop E1, the Cantor sets of Stop 13, and
the continued fractions of the whole tour are drawn directly onto the energy levels
of a real material.

The same golden thread runs through **quasicrystals** (Shechtman's Nobel-winning
1982 discovery of five-fold symmetry, forbidden to any periodic crystal). The
one-dimensional model is the **Fibonacci chain**, built by the substitution
`a → ab`, `b → a` — whose growth ratio is, once more, the golden ratio. Aperiodic
order, its sharp diffraction spots, and its singular spectrum are all organized by
`φ` and its continued fraction.

## 6. π, and two places it meets recursion and physics

Why is π everywhere? Because it is the constant of **rotation** (radians), of the
**Gaussian** (`∫e^{-x²} dx = √π`), and of the **Basel sum** `ζ(2) = π²/6`. From
these three springs it floods physics: `ħ = h/2π` is action per radian; Coulomb's
law carries `1/4πε₀`; Einstein's field equations carry `8πG/c⁴`; the Casimir force
between plates is `−π²ħc/240a⁴`; blackbody radiation carries `π⁴` through
`ζ(4) = π⁴/90`; and even the entropy of the Gauss map is `π²/(6 ln 2)`. π is not a
geometry fact that leaked into physics; it is the signature of anything circular,
Gaussian, or summed over the integers.

Two gems tie π back to the tour's own themes:

**The hydrogen atom knows Wallis's product.** In 2015 Friedmann and Hagen found
that the standard variational calculation of the hydrogen atom's energy levels
reproduces — exactly — Wallis's 1655 infinite product `π/2 = (2·2·4·4·6·6…)/(1·3·3·5·5·7…)`.
A seventeenth-century formula for π fell out of a quantum-mechanical calculation,
unbidden.

**Colliding blocks count π.** Put a light block between a wall and a heavy one,
send the heavy one in, and count every elastic collision. Galperin's theorem
(2003): with mass ratio `100^n`, the number of collisions is the first `n+1`
digits of π. Run the experiment:

```
$ python -m tourbus demo blocks 6
Galperin's colliding blocks: physics counts the digits of pi
 mass ratio  collisions (sim)  digits of pi
 ----------  ----------------  ------------
 100^0                      3             3
 100^1                     31            31
 100^2                    314           314
 100^3                   3141          3141
 100^4                  31415         31415
 100^5                 314159        314159
 100^6                3141592       3141592
```

And here the whole tour closes its loop. The two-block system, in the right
coordinates, is a billiard bouncing inside a **wedge** of angle `arctan(√(m/M))`;
the number of bounces is `⌊π/θ⌋`, a **rotation number** — the very quantity that
continued fractions were invented to measure (Stops 8 and §4 above). π appears
because it is the half-turn. Recursion, continued fractions, rotation, and π are
not adjacent here. They are identical.

## 7. The throughline

Pull the thread and everything comes with it. To read a number's continued
fraction is to renormalize it. To ask how irrational it is, is to ask how stable
an orbit is. To find `φ` in a sunflower, a quasicrystal, and the last surviving
torus is to find the same badly-approximable number doing the same job. To count
collisions and get π is to measure a rotation number. The Gauss map, the Y
combinator, the KAM torus, the Hofstadter butterfly, the devil's staircase, and
two bricks on a frictionless floor are all one sentence: **the infinite, defined
by finite self-application.** The tour bus never really left Euclid's algorithm.
It just kept discovering it, wearing new clothes, at every stop.

## Further reading

- C. Series, "The modular surface and continued fractions," *J. London Math. Soc.*
  (1985) — continued fractions as geodesics.
- V. I. Arnold, *Mathematical Methods of Classical Mechanics* — small divisors and
  KAM; and J. Greene, "A method for determining a stochastic transition" (1979).
- D. Hofstadter, "Energy levels and wave functions of Bloch electrons…" (1976);
  A. Avila & S. Jitomirskaya, "The Ten Martini Problem," *Ann. of Math.* (2009).
- M. Baake & U. Grimm, *Aperiodic Order* — the Fibonacci chain and quasicrystals.
- T. Friedmann & C. R. Hagen, "Quantum mechanical derivation of the Wallis formula
  for π," *J. Math. Phys.* 56 (2015).
- G. Galperin, "Playing pool with π," *Regular and Chaotic Dynamics* 8 (2003).
- M. Feigenbaum, "Quantitative universality for a class of nonlinear
  transformations" (1978) — renormalization and universality.

---

[← Route map](index.md) · [The Express Line](appendix-d-frontier.md) · [Terminus](15-terminus.md)
