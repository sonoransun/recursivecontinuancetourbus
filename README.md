<h1 align="center">Recursive Continuance Tour Bus</h1>

<p align="center"><em>A guided ride through recursion and continued fractions — from Euclid's
leftovers to the research frontier, every result computed exactly by one small engine.</em></p>

<p align="center">
  <a href="https://sonoransun.github.io/recursivecontinuancetourbus/"><b>Ride the tour online</b></a>
  &nbsp;·&nbsp;
  <a href="https://sonoransun.github.io/recursivecontinuancetourbus/explore.html">Live exposition</a>
  &nbsp;·&nbsp;
  <a href="docs/index.md">Docs on GitHub</a>
  &nbsp;·&nbsp;
  <a href="docs/syllabus.md">Syllabus</a>
</p>

<p align="center">
  <a href="https://github.com/sonoransun/recursivecontinuancetourbus/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/sonoransun/recursivecontinuancetourbus/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python 3.10 to 3.13" src="https://img.shields.io/badge/python-3.10%E2%80%933.13-3776AB">
  <img alt="Zero runtime dependencies" src="https://img.shields.io/badge/runtime%20dependencies-0-1baf7a">
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-b5751a">
</p>

![The network: a fifteen-stop main line from the Depot to the Terminus, with the Heritage Line leaving the Depot for history, the Branch Line leaving the Unfolding Road for the other ways to expand a number, the Cross-Domain Line leaving the Engine Room for the sciences, and the Express Line running on past the Terminus to the research frontier.](docs/assets/fig-network.svg)

> This project explores the concepts of recursion and continued fractions. We
> start with foundational mathematical constructs and expand out into the limits
> of human comprehension and complexity.
>
> From the basic to conceptual, to the theoretical and applied mathematical, this
> exposition will fuel the fire of your curiosity toward the ever onward
> structures of logic.

A continued fraction is what you get when you run Euclid's 2,300-year-old gcd
algorithm on a real number and keep the quotients. That one idea reaches
surprisingly far: it chose the gears of Huygens' planetarium, sets the rules of
the calendar, tunes the piano, breaks careless RSA keys, sits in the final step
of Shor's quantum factoring algorithm, and runs straight into problems nobody
can solve — is Euler's constant irrational? do `π`'s partial quotients stay
bounded? This project rides that road end to end, three ways, from one rigorous
exact-arithmetic engine.

## Three ways to ride

| | What it is | Start here |
|---|---|---|
| **In the terminal** | An interactive tour of 15 stops plus four branch lines, mixing narrative, live-computed demonstrations, and "try this" prompts. Standard-library Python, no dependencies. | `python -m tourbus` |
| **On the web** | A documentation site — a chapter per stop, each with worked examples, a **Then, now, next** section (history, today's applications, open problems), exercises with hints, and further reading — plus a self-contained interactive exposition with 15 live widgets. | [the tour online](https://sonoransun.github.io/recursivecontinuancetourbus/) |
| **In the classroom** | A one-semester syllabus with a prerequisite map, fifteen-week pacing, learning objectives, and a discussion prompt for every stop. | [`docs/syllabus.md`](docs/syllabus.md) |

## Quickstart

Zero dependencies, Python ≥ 3.10:

```bash
# Ride the interactive tour from the first stop
python -m tourbus

# In a hurry? Print the whole tour as a transcript
python -m tourbus --all

# Jump to one stop, or the route map
python -m tourbus stop 7
python -m tourbus list

# Run a single demonstration
python -m tourbus demo pell 61
python -m tourbus demo cf pi
python -m tourbus demo gosper --op add sqrt2 sqrt3
python -m tourbus demo --list

# Ride the Express Line — nine fringe stops past the terminus
python -m tourbus frontier
python -m tourbus demo gkw          # the Gauss-Kuzmin-Wirsing constant, from scratch
python -m tourbus demo ramanujan    # the Rogers-Ramanujan fraction and a golden-ratio miracle

# Ride the Heritage Line — nine historical stops, computed live
python -m tourbus heritage

# Ride the Branch Line — six other ways to unfold a number
python -m tourbus branch
python -m tourbus demo cfrac        # factor an integer the way CFRAC cracked F7

# Open the web exposition
open site/index.html      # (or just double-click it)
```

## The route

| # | Stop | What you'll see | Then, now, next |
|---|------|-----------------|-----------------|
| 1 | [The Depot](docs/01-depot.md) | Euclid's algorithm as the ur-recursion; gcd, Bézout, Lamé's theorem | constant-time gcd in cryptography; lattice reduction |
| 2 | [The Unfolding Road](docs/02-unfolding-road.md) | Continued fractions = Euclid on the reals; `[a₀; a₁, a₂, …]` | rational reconstruction; Hermite's problem |
| 3 | [The Engine Room](docs/03-engine-room.md) | Convergents, the fundamental recurrence, the determinant identity | Lentz's method in statistics libraries; Padé approximants |
| 4 | [The Golden Milestone](docs/04-golden.md) | φ = [1;1,1,…], Fibonacci, Hurwitz, the "most irrational" number | Fibonacci hashing; quasicrystals; Fibonacci anyons |
| 5 | [Scenic Overlook](docs/05-scenic-overlook.md) | Best approximation: calendars, Huygens' gears, π → 355/113 | the Metonic cycle; the end of the leap second |
| 6 | [The Loop Road](docs/06-loop-road.md) | Periodic CFs ⇔ quadratic irrationals; the √d algorithm | class numbers and regulators; Gauss's open problem |
| 7 | [The Cattle Crossing](docs/07-cattle-crossing.md) | Pell's equation x² − d·y² = 1 via the period of √d | Hilbert's tenth problem; quantum Pell solving |
| 8 | [The Family Tree](docs/08-family-tree.md) | Stern–Brocot tree, Farey sequences, the question-mark function | the circle method; the Riemann hypothesis in Farey form |
| 9 | [Celebrity Sightings](docs/09-celebrity.md) | The continued fractions of e and π; generalized CFs | irrationality measures; machine-found conjectures |
| 10 | [The Casino](docs/10-casino.md) | The Gauss map, Gauss–Kuzmin, Khinchin's and Lévy's constants | why gcd is fast on average; the Big Bang; Duffin–Schaeffer |
| 11 | [The Infinite Assembly Line](docs/11-assembly-line.md) | Gosper's exact continued-fraction stream arithmetic | the Android calculator; Richardson's theorem |
| 12 | [The Tower](docs/12-tower.md) | Ackermann, hyperoperations, the Y combinator, McCarthy 91 | union–find; the busy beaver frontier |
| 13 | [The Hall of Mirrors](docs/13-hall-of-mirrors.md) | Fractals, self-similarity, and their link to continued fractions | Hilbert-curve indexes; Siegel disks and Brjuno numbers |
| 14 | [The Souvenir Shop](docs/14-souvenir-shop.md) | Musical temperament, Wiener's RSA attack, the Collatz conjecture | Shor's algorithm; post-quantum standards; 3x + 1 |
| 15 | [Terminus](docs/15-terminus.md) | Open problems and further reading | doors that opened, and how the next may open |

Each stop has a chapter in [`docs/`](docs/index.md), a section in the
interactive exposition, and a live demonstration in the terminal.

### The Express Line (fringe avenues)

Nine deeper stops past the terminus, each still computed exactly (or rigorously)
on the same engine — `python -m tourbus frontier`:

| Stop | Topic |
|------|-------|
| E1 | The Markov spectrum — the numbers *after* the golden ratio |
| E2 | Continuants — the polynomial hiding inside every convergent |
| E3 | Algebraic irrationals — cube roots, the plastic number, and an open problem |
| E4 | CF variants — nearest-integer and Hirzebruch–Jung "minus" expansions |
| E5 | The three-distance theorem |
| E6 | The Gauss–Kuzmin–Wirsing constant, computed from scratch |
| E7 | Colliding blocks count π — mechanics reduced to rotation |
| E8 | The River — Conway's topograph, where √d's period solves Pell |
| E9 | Ramanujan's continued fraction — a *q*-fraction that collapses to the golden ratio |

See [Appendix D](docs/appendix-d-frontier.md).

### The Web of Ideas

Recursion, continued fractions, π, and physics turn out to be one gesture —
*the infinite defined by finite self-application* — seen from four directions:
fixed points and the Y combinator, the Gauss map as renormalization, the golden
ratio as the most stable orbit in KAM theory, mode-locking and the devil's
staircase, the Hofstadter butterfly, and two elastic blocks that collide exactly
**π** times (`python -m tourbus demo blocks`). See
[Appendix E — The Web of Ideas](docs/appendix-e-web-of-ideas.md).

### The Cross-Domain Line

The same three-term recurrence — the continuant behind every convergent — turns
out to be a molecule's energy levels, the Hofstadter butterfly of an electron in
a magnetic field, the impedance of a circuit, the stability of a control loop,
and a resummed divergent series; the golden ratio, meanwhile, optimizes
sunflowers and quasicrystals. Ride the whole line with `python -m tourbus
crossdomain`, or run a single stop (`python -m tourbus demo huckel`,
`python -m tourbus demo butterfly`). See
[Appendix F — The Same Recurrence Everywhere](docs/appendix-f-cross-domain.md).

### The Heritage Line (history, computed)

Nine historical stops — the same road, driven through time, from Euclid's ladder
to a 1972 memo — `python -m tourbus heritage`:

| Stop | Year | Topic |
|------|------|-------|
| H1 | c. 300 BC | Euclid's ladder — the algorithm before the notation |
| H2 | 628–1150 | Brahmagupta and Bhāskara — the chakravala solves Pell |
| H3 | 1572–1655 | Bombelli, Cataldi, Brouncker — first fractions in print |
| H4 | 1682 | Huygens' planetarium — gears cut to a convergent |
| H5 | 1761 | Lambert — π proved irrational through tan x |
| H6 | 1844 | Liouville — the first number *proved* transcendental |
| H7 | 1858–1861 | Stern and Brocot — the tree of all fractions, twice |
| H8 | 1970 | Morrison–Brillhart — CFRAC factors the Fermat number F₇ |
| H9 | 1972 | Gosper's Item 101 — arithmetic learns to stream |

Every claim is computed live on the same engine. See
[Appendix H](docs/appendix-h-history.md), whose timeline now runs from the
*Elements* to the results of the 2020s.

### The Branch Line (other ways to unfold a number)

Six stops on the alternatives to the continued fraction — every one exact on the
same engine — `python -m tourbus branch`:

| Stop | Topic |
|------|-------|
| B1 | Engel expansions — an ascending staircase of ceilings; the factorial series of *e* |
| B2 | Lüroth and Pierce series — an honest casino, and a rational that loops forever |
| B3 | Egyptian fractions — the greedy scribe and the Erdős–Straus conjecture |
| B4 | Zeckendorf and base-φ — integers written in Fibonacci |
| B5 | Cutting sequences — Ostrowski numeration and the Sturmian Fibonacci word |
| B6 | Lochs' theorem — the exchange rate between decimal digits and CF terms |

See [Appendix I](docs/appendix-i-branches.md).

## Where this mathematics lives today

Every chapter closes with **Then, now, next**. A sampler:

- **Inside every secure connection** — the extended Euclidean algorithm
  computes the modular inverses behind RSA and elliptic-curve keys, now in
  constant time to defeat timing attacks ([Stop 1](docs/01-depot.md#then-now-next)).
- **The last step of a quantum algorithm** — Shor's factoring algorithm
  recovers its period as a continued-fraction convergent, by a theorem of
  Legendre from 1798 ([Stop 14](docs/14-souvenir-shop.md#then-now-next)).
- **Quantum-easy, classically hard** — Pell's equation is one of the few
  problems with a known exponential quantum speed-up
  ([Stop 7](docs/07-cattle-crossing.md#then-now-next)).
- **In your calendar and your clocks** — leap-year rules are rational
  approximations, from Meton's 19-year cycle to the retirement of the leap
  second ([Stop 5](docs/05-scenic-overlook.md#then-now-next)).
- **In the data structures you use** — union–find runs in inverse-Ackermann
  time, and Fibonacci hashing spreads keys by the golden ratio
  ([Stop 12](docs/12-tower.md#then-now-next), [Stop 4](docs/04-golden.md#then-now-next)).
- **Near the Big Bang** — the Gauss map governs the chaotic oscillations of the
  BKL cosmological singularity ([Stop 10](docs/10-casino.md#then-now-next)).
- **At the frontier** — the Duffin–Schaeffer conjecture fell in 2019, `BB(5)`
  in 2024; the irrationality of Euler's constant and Zaremba's conjecture still
  stand ([Stop 15](docs/15-terminus.md#then-now-next)).

## Using the engine directly

```python
from fractions import Fraction
from tourbus import CF, gosper
from tourbus.cf.constants import pi_cf, sqrt_cf

CF.from_fraction(Fraction(415, 93))          # [4; 2, 6, 7]
pi_cf().terms(6)                             # [3, 7, 15, 1, 292, 1]
CF.from_quadratic(0, 7, 1)                   # sqrt(7) = [2; (1, 1, 1, 4)]
gosper.add(sqrt_cf(2), sqrt_cf(3)).terms(6)  # sqrt(2) + sqrt(3), exactly
```

Everything is exact: rationals are `fractions.Fraction`; quadratic surds use
exact integer arithmetic; other irrationals come from known patterns or are
certified term by term from interval enclosures; and every figure in the docs
is drawn by the engine itself.

## Project layout

```
recursivecontinuancetourbus/
├── src/tourbus/           the engine — standard library only
│   ├── cf/                expansion, convergents, generalized CFs, Gosper arithmetic
│   ├── numbertheory/      Pell, chakravala, Stern–Brocot, Minkowski ?, Liouville, topograph
│   ├── dynamics/          the Gauss map and its statistics
│   ├── applications/      calendars, gears, temperament, Wiener's attack, Collatz, CFRAC
│   ├── recursion/         Ackermann, hyperoperations, the Y combinator, McCarthy 91
│   ├── fractals/          L-systems, space-filling curves, call trees (SVG)
│   ├── frontier/          the Express Line: Markov, continuants, GKW, Ramanujan, …
│   ├── crossdomain/       the Cross-Domain Line: Hückel, Hofstadter, Cauer, Padé, Apéry, …
│   ├── expansions/        the Branch Line: Engel, Lüroth, Egyptian, Zeckendorf, Ostrowski, Lochs
│   ├── figures/           the engine-drawn documentation figures
│   └── tour/              the command-line tour: stops, lines, demos, renderer
├── docs/                  the GitHub Pages site: Markdown chapters + generated HTML
├── site/index.html        the interactive exposition (15 widgets, one self-contained file)
├── build_site.py          Markdown → site generator (standard library only)
├── build_mermaid.py       mermaid timelines and flowcharts → inline SVG
└── tests/                 property-based tests, doctests, and site contracts
```

## Website (GitHub Pages)

The whole tour is also a browsable website under [`docs/`](docs/index.html): a
landing page with the network map, every stop and appendix as a styled page
with a station-sign header, an "on this page" rail, typeset formulas, terminal
transcripts, callouts, and prev/next navigation; client-side search (press
`/`); light and dark themes; and the full interactive exposition at
`docs/explore.html`.

To publish it: in your repo **Settings → Pages**, choose **Deploy from a branch**
and set the folder to **`/docs`**. The site is static HTML (a `.nojekyll` file is
included), so it serves as-is with no build step. It regenerates from the
Markdown chapters with:

```bash
python build_site.py     # stdlib only; writes docs/*.html + docs/assets/ + docs/explore.html
```

The Markdown is written to read well on GitHub too: `> [!TIP]`-style alerts
become callouts on the site, ```` ```mermaid ```` timelines are drawn to SVG at
build time, and `![caption](assets/fig-*.svg)` figures are inlined and themed.

## Requirements

- Python 3.10 or newer. **No runtime dependencies** — the core is pure standard
  library.
- Development/testing uses `pytest` and `hypothesis`:
  `pip install -e ".[test]"`.

## Development

```bash
# Fast test suite (property tests + site contracts)
python -m pytest -m "not slow"
python -m pytest --doctest-modules src/tourbus

# Slow / statistical tests
python -m pytest -m slow

# The smoke test: the whole tour must run non-interactively and deterministically
python -m tourbus --all --no-color --seed 1 --width 80

# Rebuild the site; CI checks that the committed HTML matches the Markdown
python build_site.py
```

## License

MIT — see [LICENSE](LICENSE).
