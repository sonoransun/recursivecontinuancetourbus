[← Stop 13 — The Hall of Mirrors](13-hall-of-mirrors.md) · [Route map](index.md) · [Stop 15 — Terminus →](15-terminus.md)

# Stop 14 — The Souvenir Shop

> Three things to take home: why the piano is tuned the way it is, how a careless RSA key falls in seconds, and a five-line function nobody can prove halts.

## Overview

The last working stop is a shop of applications — three souvenirs showing the
continued fraction and the recursion at work far from pure number theory. One
tunes a musical scale, one breaks a cipher, and one is a problem so simple a
child can state it and no mathematician can solve it. Each is a convergent, an
approximation, or an orbit — the tour's ideas, out in the world.

### Souvenir 1: why twelve notes?

A musical fifth — the most consonant interval after the octave — is the
frequency ratio `3/2`. An octave is a doubling, ratio `2`. To build a keyboard we
want to stack fifths and land back on an octave, i.e. we want integers `m, n`
with `(3/2)ᵐ ≈ 2ⁿ`. Taking logs, this is asking for a good rational
approximation to

```
log₂(3/2) = 0.5849625007…
```

The convergents of this number are exactly the historically important scales.
`7/12` says: twelve equal steps per octave, with the fifth at seven of them —
**12-tone equal temperament**, the tuning of the modern piano. The `12` in "the
chromatic scale has twelve notes" is a continued-fraction convergent. The fifth
it produces is off from the pure `3/2` by only `−1.955` cents (hundredths of a
semitone), imperceptibly flat — the compromise that lets you play in every key on
one set of strings. The next convergents, `24/41` and `31/53`, give
microtonal scales (41-TET, 53-TET) that are *more* accurate still and are used in
some experimental and historical instruments.

The convergents were tuning instruments long before anyone wrote them down as
convergents. Zhu Zaiyu computed the twelve exactly equal semitones —
root-extractions to nine digits, on an abacus — in Ming-dynasty China (1584),
with Simon Stevin reaching the same tuning in Europe within a few years; and
the finer 53-note convergent was anticipated by Jing Fang in the first century
BC, who counted 53 fifths against 31 octaves, then rediscovered by Nicholas
Mercator in the seventeenth century. The piano obeys `7/12`; the theory
arrived two millennia after the practice.

### Souvenir 2: breaking RSA with a continued fraction

RSA encryption uses a public modulus `N = pq` and a public exponent `e`, with a
secret exponent `d` satisfying `e·d ≡ 1 (mod φ(N))`, so that `e·d = 1 + kφ(N)`
for some integer `k`. Choosing a *small* `d` speeds up decryption — a tempting
shortcut. **Michael Wiener showed in 1990** that it is a fatal one:

> If the private exponent satisfies `d < N^{1/4}/3`, then RSA is broken. The
> fraction `k/d` appears among the **convergents of `e/N`**, so an attacker who
> knows only the public key `(e, N)` can read off `d` in seconds.

The mechanism is pure Stop 5. Because `e·d = 1 + kφ(N)` and `φ(N) ≈ N`, the
public fraction `e/N` is *extremely close* to the secret fraction `k/d` — close
enough (when `d` is small) to satisfy **Legendre's criterion** `|e/N − k/d| <
1/(2d²)`. Legendre's criterion then *guarantees* `k/d` is a convergent of `e/N`.
The attacker expands `e/N` as a continued fraction, tries each convergent's
denominator as a candidate `d`, and checks it — one of them is the key. The
secret exponent, chosen too small, betrays itself through the same
best-approximation theory that gave us `355/113`. Appendix A works through why
the bound is exactly `N^{1/4}`.

### Souvenir 3: the Collatz conjecture

Finally, the shop's cheapest and most maddening souvenir. Define, for a positive
integer `n`, the **Collatz map**:

```
n → n/2       if n is even,
n → 3n + 1    if n is odd.
```

Iterate. The conjecture — stated by Lothar Collatz around 1937 and still open —
is that **every** starting `n` eventually reaches `1` (after which it cycles
`1 → 4 → 2 → 1`). The orbit of `27` is famous: it climbs to a peak of `9232`
before finally crashing to `1` after `111` steps, a wildly erratic flight from a
tiny start. The conjecture has been verified by computer for every `n` up to
about `2⁶⁸` — and yet no proof exists. Paul Erdős said of it, "Mathematics is
not yet ready for such problems." It is a recursion whose *termination* — the
one property Euclid's algorithm wore on its sleeve at Stop 1 — is, for Collatz,
an utter mystery. The tour began with a recursion we could prove always halts; it
ends its working stops with one we cannot.

## Worked examples

The `temperament` demo lists the convergents of `log₂(3/2)` with the size of the
resulting fifth's error in cents. Read down to `7/12` and you have found the
piano:

```
$ python -m tourbus demo temperament
Equal temperament from convergents of log2(3/2):
 convergent  notes/octave  fifth error (cents)
 ----------  ------------  -------------------
 1/2                    2              -101.955
 3/5                    5              +18.045
 7/12                  12               -1.955
 24/41                 41               +0.484
 31/53                 53               -0.068
```

`2` notes per octave is useless, `5` (the pentatonic scale) is crude at `+18`
cents, but `12` brings the error down to a nearly inaudible `−1.955` cents — the
sweet spot of accuracy versus playability that the world settled on. The finer
scales `41` and `53` are more accurate but need far more keys.

Now break a weak RSA key. The `wiener` demo builds a 128-bit modulus with a
deliberately small `d`, then recovers `d` from the public `(e, N)` alone by
walking the convergents of `e/N`:

```
$ python -m tourbus demo wiener --bits 128
vulnerable RSA key (128-bit):
  n = 112744406089147775988680812810091346007
  e = 68144262240283900109239142501105545933
  recovered d = 265862677 (true d = 265862677)
  attack succeeded
```

The recovered `d` matches the true secret exactly — extracted from public data
in the time it takes to expand one continued fraction, because the key's owner
chose `d` below Wiener's `N^{1/4}/3` threshold.

Finally, the Collatz flight of `27` — a small number that soars before it falls:

```
$ python -m tourbus demo collatz 27
Collatz flight of 27:
  111 steps, peak 9232
```

One hundred and eleven steps and a peak of `9232`, from a start of `27`, with no
theorem to say why it ever comes down at all.

## Exercises

1. **(★)** From the `temperament` table, which scale first brings the fifth's
   error under 1 cent? How many notes per octave does it need?
   <details><summary>Hint</summary>`24/41` gives `+0.484` cents — the 41-note
   scale.</details>

2. **(★)** Run `demo collatz 97` and compare its peak to `27`'s. Do different
   starts share a peak?
   <details><summary>Hint</summary>`97` also peaks at `9232`, because its orbit
   merges into `27`'s — many trajectories funnel through the same high point.</details>

3. **(★★)** Explain, using Legendre's criterion (Stop 5), why Wiener's attack
   requires `d` to be *small*.
   <details><summary>Hint</summary>Only when `d` is small enough is
   `|e/N − k/d| < 1/(2d²)`, the bound that forces `k/d` to be a convergent.</details>

4. **(★★)** The pure fifth is `3/2 = 701.955` cents; a stack of twelve fifths is
   `12 × 701.955` cents. By how much does it overshoot seven octaves (the
   "Pythagorean comma")?
   <details><summary>Hint</summary>`12 × 701.955 − 7 × 1200 = 23.46` cents —
   which spread over twelve fifths is the `1.955`-cent flattening of each.</details>

5. **(★★★)** Show that the Collatz map cannot have a cycle other than
   `1 → 4 → 2 → 1` among numbers below the verified bound, and explain why this
   does *not* prove the conjecture.
   <details><summary>Hint</summary>Verification checks each starting value
   reaches 1, ruling out small cycles; but "no counterexample below `2⁶⁸`" says
   nothing about arbitrarily large `n`.</details>

## See it move

Open the **Souvenir Shop** widget:
[`site/index.html#stop-14-souvenir`](../site/index.html#stop-14-souvenir). Tune a
scale by dragging the note count, watch a weak RSA key crack as its convergents
scroll past, and trace any Collatz flight as a rising-and-falling graph.

**Try it live:** [just intonation versus equal temperament](../site/index.html#w10?t=just), or watch [a 128-bit weak key break itself](../site/index.html#w11?b=128&auto=1).
## Further reading

- M. Wiener, "Cryptanalysis of Short RSA Secret Exponents," *IEEE Trans.
  Information Theory* (1990) — the original attack. See Appendix C.
- J. C. Lagarias, ed., *The Ultimate Challenge: The 3x+1 Problem* (2010) — the
  definitive Collatz survey; Appendix C.
- D. Benson, *Music: A Mathematical Offering*, for temperament and the
  continued-fraction derivation of 12-TET.
- Appendix A of this tour for the derivation of Wiener's `N^{1/4}` bound.

[← Stop 13 — The Hall of Mirrors](13-hall-of-mirrors.md) · [Route map](index.md) · [Stop 15 — Terminus →](15-terminus.md)
