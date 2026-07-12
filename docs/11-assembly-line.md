[← Stop 10 — The Casino](10-casino.md) · [Route map](index.md) · [Stop 12 — The Tower →](12-tower.md)

# Stop 11 — The Infinite Assembly Line

> Continued fractions are miserable to add — unless you build a machine that consumes and produces them one term at a time, forever.

## Overview

Continued fractions are the best tool for *approximating* numbers (Stop 5) but a
notoriously bad tool for *computing* with them. There is no simple rule for the
continued fraction of `x + y` in terms of the continued fractions of `x` and `y`.
For two centuries this was the subject's embarrassing weakness. Then in **1972**
**Bill Gosper**, in the legendary MIT memo **HAKMEM (item 101)**, showed how to
do exact arithmetic on continued fractions directly — and in doing so gave one
of the purest examples of **corecursion**: a program that does not consume a
finite input and halt, but *produces* an infinite stream on demand, forever.

### Homographic functions

The building block is the **homographic** (or Möbius) function of one variable

```
z(x) = (a·x + b)/(c·x + d),
```

with integer state `(a, b, c, d)`. This single form is remarkably expressive:
`x + n` is `(x + n)/1`, `n·x` is `(n·x)/1`, `1/x` is `(0·x + 1)/(1·x + 0)`, and
the identity is `(x)/(1)`. Gosper's insight is that we can compute the continued
fraction of `z(x)` while reading the continued fraction of `x`, using two moves:

- **Ingest** the next partial quotient `p` of `x`. Substituting
  `x ← p + 1/x′` transforms the state by
  `(a, b, c, d) ← (a·p + b, a, c·p + d, c)`. This folds one input term into the
  machine.
- **Emit** a partial quotient `q` of the output. This is allowed *only when the
  machine is sure*: when the floor of `z` agrees at both ends of the remaining
  input range — i.e. `⌊a/c⌋ = ⌊(a+b)/(c+d)⌋`. Then output `q = ⌊a/c⌋` and
  transform the state by `(a, b, c, d) ← (c, d, a − q·c, b − q·d)` (subtract `q`,
  then invert).

The machine alternates: emit whenever it can prove the next output digit,
otherwise ingest another input digit to narrow the uncertainty. It never rounds
and never approximates — every emitted term is exact.

### Bihomographic: two inputs at once

To add or multiply *two* continued fractions we need the **bihomographic** form

```
z(x, y) = (a·x·y + b·x + c·y + d)/(e·x·y + f·x + g·y + h),
```

with an eight-integer state. Addition is `(x·y·0 + x + y + 0)/(1)`, i.e.
`(b, c) = (1, 1)` and denominator `1`; multiplication is `(x·y)/(1)`, i.e.
`a = 1`; and so on for subtraction and division. The machine now has *three*
moves — ingest from `x`, ingest from `y`, or emit — and a rule for choosing
which input to read (whichever is contributing more uncertainty). Everything
else is the same alternation of ingest and provably-safe emit. This is exactly
the engine behind `tourbus.cf.gosper` and the `demo gosper` command.

### Corecursion, and a limit

Note what kind of program this is. Ordinary recursion (the rest of the tour)
breaks a problem into smaller pieces and bottoms out at a base case. Gosper's
algorithm has **no base case** — its inputs are infinite streams and its output
is an infinite stream. It is **corecursion**: defined not by how it terminates
but by how it *keeps going*, producing one more term whenever asked. The
correctness condition is not "it halts" but "each emitted term is forced." This
is the same shift in viewpoint that separates the fixed points of Stop 6 from the
descending recursions of Stop 1.

Corecursion has a famous limitation: **stream equality is undecidable**.
Consider `√2 · √2`, which equals exactly `2`. The machine would love to emit the
finite continued fraction `[2]` and stop — but to *prove* the output is exactly
`2` it would have to rule out an infinitesimally small fractional part, which
requires reading infinitely many input terms. It never gains enough certainty to
emit, so it **stalls forever**, ingesting term after term of `√2` without ever
producing output. `tourbus` guards against this with a safety cutoff and reports
the stall honestly. This is not a bug; it is a shadow of the halting problem
falling across arithmetic itself. A machine that produces exact answers cannot,
in general, *know* when its answer has become rational.

## Worked examples

Add `√2` and `√3` as continued fractions — no decimal ever computed, just term
in and term out. The result is the continued fraction of `√2 + √3 ≈ 3.1463`,
produced twelve terms deep by the bihomographic machine:

```
$ python -m tourbus demo gosper --op add sqrt2 sqrt3
sqrt2 add sqrt3 (as a continued fraction):
  [3, 6, 1, 5, 7, 1, 1, 4, 1, 38, 43, 1]
```

Multiply the same two and something tidier appears — `√2 · √3 = √6`, a quadratic
surd, so by Stop 6 its continued fraction must be periodic. The machine
discovers the period `[2; (2, 4)]` without ever being told the answer is `√6`:

```
$ python -m tourbus demo gosper --op mul sqrt2 sqrt3
sqrt2 mul sqrt3 (as a continued fraction):
  [2, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2]
```

Now the cautionary tale. Multiply `√2` by *itself*. The true answer is exactly
`2`, but the machine cannot ever prove the fractional part has vanished, so it
ingests forever and `tourbus` trips its safety cutoff rather than loop
endlessly:

```
$ python -m tourbus demo gosper --op mul sqrt2 sqrt2
sqrt2 mul sqrt2 (as a continued fraction):
demo error: bihomographic ingested too long without emitting (the exact result is likely rational)
```

That error message *is* the theorem: exact stream arithmetic cannot decide, in
finite time, that its output has become rational. The assembly line runs
forever, and sometimes forever is the honest answer.

## Exercises

1. **(★)** Verify numerically that the `add` result is right: evaluate the
   continued fraction `[3, 6, 1, 5]` and compare to `√2 + √3 ≈ 3.14626`.
   <details><summary>Hint</summary>Use the engine-room recurrence; the fourth
   convergent already agrees to several places.</details>

2. **(★)** Confirm `√2 · √3 = √6` is a quadratic surd and predict, from Stop 6,
   that its continued fraction is periodic. What is the period?
   <details><summary>Hint</summary>`√6 = [2; (2, 4)]`; the block ends in
   `2·⌊√6⌋ = 4`.</details>

3. **(★★)** Write the homographic state `(a, b, c, d)` for the function
   `z(x) = (2x + 1)/(x + 3)` and perform one ingest of the partial quotient
   `p = 3`.
   <details><summary>Hint</summary>Start `(2, 1, 1, 3)`; ingesting `p = 3` gives
   `(2·3+1, 2, 1·3+3, 1) = (7, 2, 6, 1)`.</details>

4. **(★★)** Explain precisely why `demo gosper --op mul sqrt2 sqrt2` stalls,
   while `--op mul sqrt2 sqrt3` does not.
   <details><summary>Hint</summary>The first output is rational (`2`, a finite
   CF) and the machine cannot prove finiteness; the second is an irrational surd,
   whose infinite output it can keep emitting.</details>

5. **(★★★)** Give the emit condition `⌊a/c⌋ = ⌊(a+b)/(c+d)⌋` a geometric reading:
   why does agreement of the floor at the two ends of the input interval
   certify the next output digit?
   <details><summary>Hint</summary>A homographic map is monotone on the input
   range `[1, ∞)`, so if the floor of `z` agrees at both endpoints it is constant
   across the whole interval — the output digit is determined regardless of the
   unread input.</details>

## See it move

Open the **Assembly Line** widget:
[`site/index.html#stop-11-assembly`](../site/index.html#stop-11-assembly). Pick
two numbers and an operation and watch the eight-integer state update as terms
are ingested and emitted, with the machine visibly stalling when you ask it for
`√2 · √2`.

## Further reading

- R. W. Gosper, "Continued Fraction Arithmetic," HAKMEM item 101 (1972) — the
  original algorithm. See Appendix C.
- M. Beeler, R. W. Gosper & R. Schroeppel, *HAKMEM*, MIT AI Memo 239.
- J. Vuillemin, "Exact Real Computer Arithmetic with Continued Fractions,"
  *IEEE Trans. Computers* (1990).
- Appendix B of this tour for the definitions of *homographic*, *bihomographic*,
  and *corecursion*.

[← Stop 10 — The Casino](10-casino.md) · [Route map](index.md) · [Stop 12 — The Tower →](12-tower.md)
