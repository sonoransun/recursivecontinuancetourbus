[← Route map](index.md) · [The Web of Ideas](appendix-e-web-of-ideas.md)

# Appendix F — The Same Recurrence Everywhere

> One three-term recurrence — the continuant that produces every continued-fraction
> convergent — turns out to be the secular determinant of a molecule, the spectrum
> of an electron in a magnetic field, the impedance of a circuit, the stability of
> a control system, and the best rational summary of a divergent series. The
> golden ratio, meanwhile, is quietly optimizing sunflowers, quasicrystals, and
> planetary orbits. This appendix follows the same object across the sciences, and
> computes it in each.

The Express Line (Appendix D) and the Web of Ideas (Appendix E) argued that
recursion and continued fractions are one idea in many costumes. Here we take the
argument into the laboratory. Every claim below is *computed* by
`python -m tourbus crossdomain` — the same exact engine, wearing lab coats.

## The one recurrence

Recall the **continuant** from the Express Line: `K(a₁,…,aₙ)` obeys the three-term
recurrence `K_k = a_k·K_{k-1} + K_{k-2}`, and it is exactly the numerator of a
continued-fraction convergent. Change the sign to `K_k = x·K_{k-1} − K_{k-2}` and
you have the characteristic polynomial of a tridiagonal matrix. That single
switch is the seam along which continued fractions stitch themselves into physics,
chemistry, and engineering — because *tridiagonal* is what you get whenever a
system is a chain of nearest-neighbour couplings, and almost everything, locally,
is.

## Chemistry — a molecule's energy levels are a continuant

In simple **Hückel theory**, the π-electron energy levels of a conjugated molecule
are `E = α + xβ`, where the `x` are eigenvalues of the molecular graph. For a
linear polyene (a chain of carbons) the secular determinant is *literally the
continuant* with the minus sign, so the levels are `x_k = 2cos(kπ/(n+1))`. Two
payoffs fall out for free. **Benzene** (a six-carbon ring) has energy levels
`2, 1, 1, −1, −1, −2` in units of β — closed-shell, large gap, **aromatic** — and
sweeping the ring size reproduces Hückel's **4n+2 rule** exactly. And **butadiene**
(four carbons) has levels `±φ` and `±1/φ`: the golden ratio, sitting in a
molecule. (`demo huckel`.)

```
$ python -m tourbus demo huckel
Huckel MO energies of the C6 annulene (units of beta):
  [2.0, 1.0, 1.0, -1.0, -1.0, -2.0]
  verdict: aromatic (Huckel 4n+2 rule)
```

## Condensed matter — a solid's density of states is a continued fraction

The **recursion method** (Haydock; Lanczos) computes the local Green's function of
a tight-binding solid or molecule as

    G₀₀(z) = 1/(z − a₀ − b₁²/(z − a₁ − b₂²/(z − a₂ − …))),

a continued fraction whose coefficients come from a three-term recursion, and
whose imaginary part is the local density of states. A molecule's electronic
structure, in other words, *is* a continued fraction. On the **Bethe lattice** —
a self-similar tree — the continued fraction closes on itself into a quadratic,
giving the density of states in exact closed form. (`demo dos`.)

```
$ python -m tourbus demo dos
Green's function of a 4-site chain as a continued fraction:
  Lanczos a = ['0', '0', '0', '0']
          b^2 = ['1', '1', '1']
  eigenvalue poles = [-1.618, -0.618, 0.618, 1.618]
```

## Spectra — the Hofstadter butterfly is drawn with continuants

Put an electron on a lattice in a magnetic field and its allowed energies, plotted
against the magnetic flux, form the self-similar fractal called the **Hofstadter
butterfly**. To compute the spectrum for a rational flux `p/q` you count
eigenvalues with the **Sturm sequence** `d_k = (a_k−E)d_{k-1} − d_{k-2}` — which is
the continuant again. The butterfly's gaps are labelled by the **continued-fraction
convergents** of the flux; at irrational flux the spectrum is a Cantor set. The
number-theory of continued fractions is drawn directly onto a material's energy
levels. (The band spectrum is symmetric about `E = 0` for every flux; for even
`q` the two central bands kiss at a Dirac point.) (`demo butterfly`.)

```
$ python -m tourbus demo butterfly
Hofstadter butterfly: bands vs magnetic flux p/q
 flux  bands
 ----  -----
 1/2       1
 1/3       3
 2/3       3
 1/4       3
 3/4       3
 1/5       5
 2/5       5
 3/5       5
 4/5       5
 1/6       5
 5/6       5
 1/7       7
 2/7       7
 3/7       7
 4/7       7
 5/7       7
 6/7       7
  flux 1/2: Delta(E)=E^2-4, edges +/-2sqrt2; the spectrum is fractal.
```

## Engineering — ladders and stability

Two staples of electrical and control engineering are continued fractions in
disguise. The impedance of a **Cauer LC ladder** is a continued fraction in the
frequency variable, so expanding a rational impedance as a continued fraction
*synthesizes the circuit* — the partial quotients are the component values.
(`demo cauer`.)

```
$ python -m tourbus demo cauer
Cauer ladder synthesis of Z(s) = (24s^3+6s)/(12s^2+1):
  element values = ['2', '3', '4']  (L1, C1, L2, ...)
```

And a control system is **stable** (Routh–Hurwitz) precisely when
the continued fraction of its characteristic polynomial's even and odd parts has
*all positive quotients* — the polynomial echo of a real number's regular
continued fraction. (`demo routh`.)

## Analysis — Padé resummation

The convergents of Stop 3 are the best rational approximations of a *number*. Do
the same to a *power series* and you get the **Padé approximants**: the C-fraction
of a series has convergents that are the Padé table, and truncating it resums even
a divergent series into a rational function that converges far better than the
series ever did. The `[1/1]` Padé of `eˣ` is `(2+x)/(2−x)`. (`demo pade`.)

## Nonlinear dynamics — mode-locking and the devil's staircase

Drive an oscillator and its rhythm **locks** to rational ratios of the drive over
whole intervals — Arnold tongues, organized by the **Stern–Brocot/Farey** mediants
of Stop 8. The locked winding number, plotted against the drive, is a **devil's
staircase**: constant on the rationals, and shaped by Minkowski's question-mark
function. Push the same period-doubling logic in the logistic map and you meet the
**Feigenbaum constant** δ ≈ 4.669 — a renormalization rate, the exact cousin of
the Gauss–Kuzmin–Wirsing constant we computed on the Express Line. (`demo staircase`.)

## Biology & materials — the golden thread

The second thread is a single number. Plants place each seed at the **golden
angle**, `360°·(2−φ) ≈ 137.5°`, because φ is the *most badly approximable* number
(Stop 4) — so seeds never fall into radial spokes, and the visible spiral counts
are consecutive **Fibonacci numbers**, the denominators of φ's convergents.
(`demo phyllotaxis`.)

```
$ python -m tourbus demo phyllotaxis
Phyllotaxis: the golden angle in plants
  golden angle = 137.50776 degrees
  n=200 seeds -> parastichy spirals (21, 34) (consecutive Fibonacci)
  n=400 seeds -> parastichy spirals (21, 34) (consecutive Fibonacci)
  n=600 seeds -> parastichy spirals (34, 55) (consecutive Fibonacci)
```

The same golden ratio inflates the **Fibonacci quasicrystal**,
whose sharpest diffraction peaks are indexed, once again, by φ's convergents.
(`demo quasicrystal`.)

## The frontier — Apéry's ζ(3)

And at the edge of the known: Apéry proved `ζ(3) = Σ 1/n³` irrational with a
recurrence whose two solutions are the convergents of a continued fraction,
racing to ζ(3) faster than the denominators can keep up. Recursion and continued
fractions, meeting at a place mathematics still cannot fully map — whether ζ(5) is
irrational remains open. (`demo apery`.)

## The throughline

A molecule, a magnetic spectrum, a circuit, a control loop, a resummed series, a
mode-locked rhythm, a sunflower, a quasicrystal, an irrationality proof — all the
same recurrence, the same nested self-application. Continued fractions are not a
corner of number theory; they are the shape that any *chain of couplings* takes
when you write it down. The tour bus turns out to run everywhere.

## Further reading

- R. Haydock, "The recursive solution of the Schrödinger equation," *Solid State
  Physics* 35 (1980) — Green's functions as continued fractions.
- D. Hofstadter, *Phys. Rev. B* 14 (1976); Avila & Jitomirskaya, *Ann. of Math.*
  (2009) — the butterfly and the Ten Martini Problem.
- W. Cauer, *Synthesis of Linear Communication Networks* (1958) — ladder networks.
- G. A. Baker & P. Graves-Morris, *Padé Approximants* (1996).
- P. Prusinkiewicz & A. Lindenmayer, *The Algorithmic Beauty of Plants* (1990) —
  phyllotaxis.
- A. van der Poorten, "A proof that Euler missed… Apéry's proof of the
  irrationality of ζ(3)," *Math. Intelligencer* 1 (1979).

---

[← Route map](index.md) · [The Web of Ideas](appendix-e-web-of-ideas.md) · [The Express Line](appendix-d-frontier.md)
