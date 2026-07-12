# Recursive Continuance Tour Bus — Documentation

A chapter for each of the fifteen stops on the tour. Every chapter pairs a
narrative overview with reproducible worked examples (each showing the exact
`python -m tourbus demo …` command and its output), a set of graded exercises,
and pointers for further reading. The same route drives the command-line tour
(`python -m tourbus`) and the web exposition (`site/index.html`).

## The route

| # | Chapter | Demo | Web section |
|---|---------|------|-------------|
| 1 | [The Depot](01-depot.md) | `demo euclid 1071 462` | `#stop-1-depot` |
| 2 | [The Unfolding Road](02-unfolding-road.md) | `demo cf 415/93` | `#stop-2-road` |
| 3 | [The Engine Room](03-engine-room.md) | `demo cf pi` | `#stop-3-engine` |
| 4 | [The Golden Milestone](04-golden.md) | `demo cf phi` | `#stop-4-golden` |
| 5 | [Scenic Overlook](05-scenic-overlook.md) | `demo calendar` | `#stop-5-overlook` |
| 6 | [The Loop Road](06-loop-road.md) | `demo cf sqrt7` | `#stop-6-loop` |
| 7 | [The Cattle Crossing](07-cattle-crossing.md) | `demo pell 61` | `#stop-7-cattle` |
| 8 | [The Family Tree](08-family-tree.md) | `demo stern-brocot 355/113` | `#stop-8-family` |
| 9 | [Celebrity Sightings](09-celebrity.md) | `demo cf e` | `#stop-9-celebrity` |
| 10 | [The Casino](10-casino.md) | `demo khinchin` | `#stop-10-casino` |
| 11 | [The Infinite Assembly Line](11-assembly-line.md) | `demo gosper --op add sqrt2 sqrt3` | `#stop-11-assembly` |
| 12 | [The Tower](12-tower.md) | `demo ackermann 3 5` | `#stop-12-tower` |
| 13 | [The Hall of Mirrors](13-hall-of-mirrors.md) | `demo dragon --depth 10` | `#stop-13-mirrors` |
| 14 | [The Souvenir Shop](14-souvenir-shop.md) | `demo wiener --bits 128` | `#stop-14-souvenir` |
| 15 | [Terminus](15-terminus.md) | `demo collatz 27` | `#stop-15-terminus` |

## The Express Line

Past the terminus lie six deeper, stranger stops — the Markov spectrum,
continuants, algebraic irrationals, alternative continued fractions, the
three-distance theorem, and the Gauss–Kuzmin–Wirsing constant. Ride them with
`python -m tourbus frontier`.

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

## Appendices

- [Appendix A — Proofs](appendix-a-proofs.md): the convergent recurrence,
  Lagrange's periodicity theorem, Hurwitz's theorem, and the Wiener bound.
- [Appendix B — Glossary](appendix-b-glossary.md): the vocabulary of the tour.
- [Appendix C — References](appendix-c-references.md): where to read more.

## How to read along

Every worked example in these chapters is a real command. Try them as you go:

```bash
python -m tourbus stop 1      # the same material, interactively
python -m tourbus demo --list # every runnable demonstration
```
