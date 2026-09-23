# Recursive Continuance Tour Bus — Documentation

A chapter for each of the fifteen stops on the tour, and an appendix for each of
the four lines that branch off it. Every chapter pairs a narrative overview with
reproducible worked examples (each showing the exact `python -m tourbus …`
command and its output), a **Then, now, next** section — the idea's history,
where it is at work today, and the open road ahead — graded exercises, a link to
its live widget, and further reading. The same route drives the command-line
tour (`python -m tourbus`) and the web exposition (`site/index.html`).

The rendered site, with search, dark mode, and the interactive exposition, is at
**<https://sonoransun.github.io/recursivecontinuancetourbus/>**.

![The network: the fifteen-stop main line, the Heritage Line leaving the Depot for history, the Branch Line leaving the Unfolding Road for the other expansions, the Cross-Domain Line leaving the Engine Room for the sciences, and the Express Line running on past the Terminus to the frontier.](assets/fig-network.svg)

## The route

| # | Chapter | Then, now, next — a taste | Demo |
|---|---------|---------------------------|------|
| 1 | [The Depot](01-depot.md) | Euclid → constant-time gcd in Bitcoin's crypto library | `demo euclid 1071 462` |
| 2 | [The Unfolding Road](02-unfolding-road.md) | anthyphairesis → `Fraction.limit_denominator` → Hermite's problem | `demo cf 415/93` |
| 3 | [The Engine Room](03-engine-room.md) | Cataldi's ledger → Lentz's method in statistics libraries | `demo cf pi` |
| 4 | [The Golden Milestone](04-golden.md) | Euclid's pentagon → Fibonacci hashing → Fibonacci anyons | `demo cf phi` |
| 5 | [Scenic Overlook](05-scenic-overlook.md) | Meton's 235/19 → the end of the leap second | `demo calendar` |
| 6 | [The Loop Road](06-loop-road.md) | Galois at seventeen → class numbers → Gauss's open problem | `demo cf sqrt7` |
| 7 | [The Cattle Crossing](07-cattle-crossing.md) | Brahmagupta → Hilbert's tenth problem → quantum Pell | `demo pell 61` |
| 8 | [The Family Tree](08-family-tree.md) | Brocot's clocks → the black hole Farey tail → the Riemann hypothesis | `demo stern-brocot 355/113` |
| 9 | [Celebrity Sightings](09-celebrity.md) | Lambert and Lindemann → irrationality measures → machine conjectures | `demo cf e` |
| 10 | [The Casino](10-casino.md) | Gauss's letter to Laplace → the Big Bang → Duffin–Schaeffer | `demo khinchin` |
| 11 | [The Infinite Assembly Line](11-assembly-line.md) | HAKMEM → the Android calculator → Richardson's theorem | `demo gosper --op add sqrt2 sqrt3` |
| 12 | [The Tower](12-tower.md) | Hilbert's program → union–find → the busy beaver | `demo ackermann 3 5` |
| 13 | [The Hall of Mirrors](13-hall-of-mirrors.md) | Koch's monster → Google's Hilbert curves → Siegel disks | `demo dragon --depth 10` |
| 14 | [The Souvenir Shop](14-souvenir-shop.md) | Zhu Zaiyu → Shor's algorithm → post-quantum cryptography | `demo wiener --bits 128` |
| 15 | [Terminus](15-terminus.md) | Apéry → Zaremba → is γ irrational? | `demo collatz 27` |

## The Express Line

Past the terminus lie nine deeper, stranger stops — the Markov spectrum,
continuants, algebraic irrationals, alternative continued fractions, the
three-distance theorem, the Gauss–Kuzmin–Wirsing constant, the colliding blocks
that count π, Conway's topograph river, and Ramanujan's continued fraction. Ride
them with `python -m tourbus frontier`.

- [Appendix D — The Express Line: Fringe Avenues](appendix-d-frontier.md)

## The Web of Ideas

Recursion, continued fractions, π, and physics are one gesture seen from four
directions — fixed points, renormalization, the golden ratio as the most stable
orbit, the Hofstadter butterfly, and two blocks that collide π times.

- [Appendix E — The Web of Ideas](appendix-e-web-of-ideas.md)

## The Cross-Domain Line

The same three-term recurrence — the continuant behind every convergent — is the
energy levels of a molecule, the Hofstadter butterfly, the impedance of a
circuit, the stability of a control loop, and a resummed divergent series; the
golden ratio, meanwhile, optimizes sunflowers and quasicrystals. Every claim is
computed live with `python -m tourbus crossdomain`.

- [Appendix F — The Same Recurrence Everywhere](appendix-f-cross-domain.md)

## The Heritage Line

The same road, driven through time — Euclid's ladder, the chakravala, Huygens'
brass Saturn, Lambert's trial of π, Liouville's built-to-order transcendental,
the tree of Stern and Brocot, CFRAC cracking the Fermat number F₇, and a 1972
memo, each computed live with `python -m tourbus heritage`. Its timeline now
runs from the *Elements* to the results of the last few years.

- [Appendix H — The Heritage Line: A History in Convergents](appendix-h-history.md)

## The Branch Line

Six other ways to unfold a number, each an alternative to the continued fraction
and each exact on the same engine — the Engel and Pierce staircases, the greedy
Egyptian scribe and the Erdős–Straus conjecture, Zeckendorf and base-φ, Sturmian
cutting sequences, and the digit/term exchange rate of Lochs' theorem. Ride them
with `python -m tourbus branch`.

- [Appendix I — The Branch Line: Other Ways to Unfold a Number](appendix-i-branches.md)

## Appendices

- [Appendix A — Proofs](appendix-a-proofs.md): the convergent recurrence,
  Lagrange's periodicity theorem, Hurwitz's theorem, and the Wiener bound.
- [Appendix B — Glossary](appendix-b-glossary.md): the vocabulary of the tour.
- [Appendix C — References](appendix-c-references.md): where to read more,
  from Euclid to the papers behind every "Then, now, next".
- [Appendix G — Hints & selected answers](appendix-g-hints.md): a hint or a
  full worked answer for every exercise on the route.
- [Appendix H — The Heritage Line: A History in Convergents](appendix-h-history.md):
  the chronology from Euclid to the present, with nine stops computed live.
- [Appendix I — The Branch Line: Other Ways to Unfold a Number](appendix-i-branches.md):
  Engel, Lüroth, Pierce, Egyptian, Zeckendorf, Ostrowski, and Lochs — the
  expansions that are not the continued fraction.

## For instructors

The tour rides well as a one-semester course: the [syllabus](syllabus.md) maps
the prerequisite graph, a fifteen-week pace, learning objectives for every
stop, and a discussion prompt for each "Then, now, next".

## How to read along

Every worked example in these chapters is a real command. Try them as you go:

```bash
python -m tourbus stop 1      # the same material, interactively
python -m tourbus demo --list # every runnable demonstration
python -m tourbus heritage    # the history, computed
python -m tourbus branch      # the other expansions
```
