# Recursive Continuance Tour Bus

> This project explores the concepts of recursion and continued fractions. We
> start with foundational mathematical constructs and expand out into the limits
> of human comprehension and complexity.
>
> From the basic to conceptual, to the theoretical and applied mathematical, this
> exposition will fuel the fire of your curiosity toward the ever onward
> structures of logic.

**GitHub Pages site → [Recursive Continuance Tour Bus](https://sonoransun.github.io/recursivecontinuancetourbus/)** — See how far down the recursion goes!

A guided tour through recursion and continued fractions — from Euclid's
algorithm to Gosper's exact stream arithmetic and the open problems at the
frontier — delivered three ways from one rigorous, exact-arithmetic engine.

```
 ●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●━━●
 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
```

## What's inside

- **`tourbus`** — a standard-library-only Python package that computes
  continued fractions *exactly* (via `fractions.Fraction` and integer
  recurrences): expansion, convergents, best approximation, periodic quadratic
  surds, Pell's equation, the Stern–Brocot tree, the Gauss map, Khinchin's
  constant, and Gosper's homographic/bihomographic stream arithmetic.
- **The guided tour** — an interactive command-line journey of 15 numbered
  stops, each mixing narrative, live-computed demonstrations, and "try this"
  prompts. Run `python -m tourbus`.
- **The interactive exposition** — a self-contained single-page web showpiece
  (`site/index.html`) with fifteen interactive widgets: expand any number's
  continued fraction, descend the Stern–Brocot tree, solve Pell's equation,
  draw fractals, break a weak RSA key, compare five expansion systems side by
  side, and more.
- **The docs** — a chapter per stop in [`docs/`](docs/index.md), with worked
  examples, exercises, embedded engine-drawn figures and diagrams, and further
  reading.
- **The syllabus** — a curriculum map for instructors: prerequisite graph,
  15-week pacing, learning objectives ([`docs/syllabus.md`](docs/syllabus.md)).

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

| # | Stop | What you'll see |
|---|------|-----------------|
| 1 | The Depot | Euclid's algorithm as the ur-recursion; gcd, Bézout, Lamé's theorem |
| 2 | The Unfolding Road | Continued fractions = Euclid on the reals; `[a₀; a₁, a₂, …]` |
| 3 | The Engine Room | Convergents, the fundamental recurrence, the determinant identity |
| 4 | The Golden Milestone | φ = [1;1,1,…], Fibonacci, Hurwitz, the "most irrational" number |
| 5 | Scenic Overlook | Best approximation: calendars, Huygens' gears, π → 355/113 |
| 6 | The Loop Road | Periodic CFs ⇔ quadratic irrationals; the √d algorithm |
| 7 | The Cattle Crossing | Pell's equation x² − d·y² = 1 via the period of √d |
| 8 | The Family Tree | Stern–Brocot tree, Farey sequences, the question-mark function |
| 9 | Celebrity Sightings | The continued fractions of e and π; generalized CFs |
| 10 | The Casino | The Gauss map, Gauss–Kuzmin, Khinchin's and Lévy's constants |
| 11 | The Infinite Assembly Line | Gosper's exact continued-fraction stream arithmetic |
| 12 | The Tower | Ackermann, hyperoperations, the Y combinator, McCarthy 91 |
| 13 | The Hall of Mirrors | Fractals, self-similarity, and their link to continued fractions |
| 14 | The Souvenir Shop | Musical temperament, Wiener's RSA attack, the Collatz conjecture |
| 15 | Terminus | Open problems and further reading |

Each stop has a chapter in [`docs/`](docs/index.md) and a section in
`site/index.html`.

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
[Appendix H](docs/appendix-h-history.md).

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

## Website (GitHub Pages)

The whole tour is also a browsable website under [`docs/`](docs/index.html):
a landing page, every stop and appendix as a styled page, the Express Line, and
the full interactive exposition at `docs/explore.html` — all sharing the
transit-diagram design, light/dark aware, with a sidebar route-rail.

To publish it: in your repo **Settings → Pages**, choose **Deploy from a branch**
and set the folder to **`/docs`**. The site is static HTML (a `.nojekyll` file is
included), so it serves as-is with no build step. It regenerates from the
Markdown chapters with:

```bash
python build_site.py     # stdlib only; writes docs/*.html + docs/assets/ + docs/explore.html
```

## Requirements

- Python 3.10 or newer. **No runtime dependencies** — the core is pure standard
  library.
- Development/testing uses `pytest` and `hypothesis`:
  `pip install -e ".[test]"`.

## Development

```bash
# Fast test suite (property tests + doctests)
python -m pytest -m "not slow"
python -m pytest --doctest-modules src/tourbus

# The smoke test: the whole tour must run non-interactively and deterministically
python -m tourbus --all --no-color --seed 1 --width 80
```

## License

MIT — see [LICENSE](LICENSE).
