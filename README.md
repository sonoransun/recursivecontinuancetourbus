# Recursive Continuance Tour Bus

> This project explores the concepts of recursion and continued fractions. We
> start with foundational mathematical constructs and expand out into the limits
> of human comprehension and complexity.
>
> From the basic to conceptual, to the theoretical and applied mathematical, this
> exposition will fuel the fire of your curiosity toward the ever onward
> structures of logic.

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
  (`site/index.html`) with twelve interactive widgets: expand any number's
  continued fraction, descend the Stern–Brocot tree, solve Pell's equation,
  draw fractals, break a weak RSA key, and more.
- **The docs** — a chapter per stop in [`docs/`](docs/index.md), with worked
  examples, exercises, and further reading.

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

# Ride the Express Line — six fringe stops past the terminus
python -m tourbus frontier
python -m tourbus demo gkw          # the Gauss-Kuzmin-Wirsing constant, from scratch

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

Six deeper stops past the terminus, each still computed exactly (or rigorously)
on the same engine — `python -m tourbus frontier`:

| Stop | Topic |
|------|-------|
| E1 | The Markov spectrum — the numbers *after* the golden ratio |
| E2 | Continuants — the polynomial hiding inside every convergent |
| E3 | Algebraic irrationals — cube roots, the plastic number, and an open problem |
| E4 | CF variants — nearest-integer and Hirzebruch–Jung "minus" expansions |
| E5 | The three-distance theorem |
| E6 | The Gauss–Kuzmin–Wirsing constant, computed from scratch |

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
