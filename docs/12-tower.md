[← Stop 11 — The Infinite Assembly Line](11-assembly-line.md) · [Route map](index.md) · [Stop 13 — The Hall of Mirrors →](13-hall-of-mirrors.md)

# Stop 12 — The Tower

> A recursion so powerful it outruns every loop you could ever write: the Ackermann function, and the combinator that conjures recursion from nothing.

## Overview

Every recursion on the tour so far has been *tame*: Euclid descends to a base
case, convergents build up term by term, Gosper's machine emits on demand. This
stop climbs a tower of recursions so steep that ordinary iteration cannot keep
up — and then asks the vertiginous question of where recursion itself comes
from. It is the most computer-science-flavoured stop, and the least about
continued fractions, but it is where "recursive continuance" is pushed to its
logical extreme.

### Hyperoperations

Start with a ladder of operations, each defined by iterating the one below:

```
addition:        a + n   = a + 1 + 1 + … + 1   (n times)
multiplication:  a · n   = a + a + … + a       (n times)
exponentiation:  aⁿ      = a · a · … · a        (n times)
tetration:       ⁿa      = a^(a^(a^…))          (n times, a tower of a's)
```

and onward. **Knuth's up-arrow notation** names them: `a↑n = aⁿ`,
`a↑↑n` is tetration, `a↑↑↑n` the next rung. Each level is defined by recursion
over the previous, and the values explode: `3↑↑3 = 3^27 ≈ 7.6 trillion`, while
`3↑↑↑3` is a tower of threes `3↑↑3 ≈ 7.6 trillion` levels high — a number with
no meaningful decimal representation.

### The Ackermann–Péter function

The **Ackermann function** packages this whole ladder into one two-argument
recursion. In Rózsa Péter's tidy form:

```
A(0, n)     = n + 1
A(m+1, 0)   = A(m, 1)
A(m+1, n+1) = A(m, A(m+1, n)).
```

The `m` coordinate selects the rung of the hyperoperation ladder:
`A(1, n) = n + 2`, `A(2, n) = 2n + 3`, `A(3, n) = 2ⁿ⁺³ − 3`, and
`A(4, n) = 2↑↑(n+3) − 3` is tetrational. The function is **total** (it halts for
every input) and **computable** (the definition above is a program), yet it is
**not primitive recursive** — it grows faster than any function you can build
from bounded `for`-loops alone. Ackermann's 1928 function was the first concrete
example proving that the total computable functions strictly *contain* the
primitive recursive ones: some things are computable only with unbounded
recursion (`while`), not mere iteration.

The double recursion in the third line is the whole story: to compute
`A(m+1, n+1)` you must first compute `A(m+1, n)` and feed the result *back in as
an argument* to `A(m, ·)`. That inner-value-as-outer-argument nesting is what
makes it outrun the primitive recursive functions. It also makes it explode:
`A(4, 2) = 2↑↑5 − 3 = 2^65536 − 3`, a number with **19,729 decimal digits** —
which is why the `tourbus` demo politely refuses to print it in full.

The function has a purpose as well as a punchline: Wilhelm Ackermann was David
Hilbert's student, and the 1928 paper ("Zum Hilbertschen Aufbau der reellen
Zahlen") served Hilbert's program of building analysis from finitary
recursions — the function was evidence about what recursion *is*. The tidy
two-argument form used here is due to Rózsa Péter (1935), whose work made
recursion theory a discipline of its own. The name "Ackermann–Péter function"
credits them both.

### The Y combinator: recursion from nothing

If recursion is a function calling itself *by name*, where does the name come
from? In the pure lambda calculus there are no names — only anonymous functions.
Yet recursion is still available, through a **fixed-point combinator**. The most
famous is Curry's **Y combinator**:

```
Y = λf. (λx. f (x x)) (λx. f (x x)),      with the property   Y f = f (Y f).
```

Applied to a function `f` that *describes one unrolling* of a recursive
definition, `Y f` is the fixed point — the fully recursive function — with no
self-reference anywhere in sight. `Y` manufactures the loop from a function that
only knows how to take one step. It is the Stop 4 fixed-point idea (`φ = 1 + 1/φ`)
lifted to the level of *functions*: `Y f` is to `f` what `φ` is to `x ↦ 1 + 1/x`.
Recursion, it turns out, is not a primitive; it is a fixed point you can build.

### McCarthy's 91 function

A gentler puzzle closes the tower. John McCarthy's **91 function** is

```
M(n) = n − 10           if n > 100,
M(n) = M(M(n + 11))     if n ≤ 100.
```

The nested `M(M(…))` looks alarming, but the astonishing fact is that
`M(n) = 91` for **every** `n ≤ 100`, and `n − 10` for `n > 100`. It is a
textbook case of a recursion whose *behaviour* is far simpler than its
*definition* — a reminder that a nested recursion can hide a trivial function,
just as Gosper's stall (Stop 11) hid a trivial answer. Proving `M(n) = 91`
requires reasoning about the *total* function, not tracing any single call, and
is a classic exercise in program verification. McCarthy posed it around 1970,
in the first wave of proving programs correct rather than merely running them.

## Worked examples

Evaluate `A(3, 5)`. By the formula `A(3, n) = 2ⁿ⁺³ − 3`, this should be
`2⁸ − 3 = 253` — and the recursion, unwound through hundreds of nested calls,
agrees exactly:

```
$ python -m tourbus demo ackermann 3 5
A(3, 5) = 253
```

Smaller inputs show the ladder's rungs. `A(2, 4) = 2·4 + 3 = 11` sits on the
"multiplication" rung, and `A(3, 3) = 2⁶ − 3 = 61` on the "exponentiation" rung:

```
$ python -m tourbus demo ackermann 2 4
A(2, 4) = 11
```

```
$ python -m tourbus demo ackermann 3 3
A(3, 3) = 61
```

Step up to the tetrational rung and the values leave the printable universe.
`A(4, 2) = 2^65536 − 3` has nearly twenty thousand digits, so the demo names it
rather than printing it:

```
$ python -m tourbus demo ackermann 4 2
A(4,2) = 2^65536 - 3 has 19729 digits; refusing to print it all.
```

That single guard is the whole point of the tower: `A(4, 2)` is a perfectly
definite, computable integer, and it is already too large to write down. Climb
one more rung to `A(4, 3)` and the number of *digits* itself becomes
astronomical.

## Exercises

1. **(★)** Compute `A(1, 5)` and `A(2, 2)` by hand from the recurrence and check
   the formulas `A(1, n) = n + 2`, `A(2, n) = 2n + 3`.
   <details><summary>Hint</summary>`A(1, 5) = 7` and `A(2, 2) = 7` as well —
   the ladder rungs cross at small values.</details>

2. **(★)** Using `A(3, n) = 2ⁿ⁺³ − 3`, predict `A(3, 7)` before running the
   demo.
   <details><summary>Hint</summary>`2¹⁰ − 3 = 1021`.</details>

3. **(★★)** Trace `M(99)` for McCarthy's function and confirm it returns `91`.
   <details><summary>Hint</summary>`M(99) = M(M(110)) = M(100) = M(M(111)) =
   M(101) = 91`.</details>

4. **(★★)** Show that `A(2, n)` *is* primitive recursive but `A(m, n)` as a
   function of both arguments is not. What breaks the primitive-recursive
   bound?
   <details><summary>Hint</summary>Fixing `m` gives a simple closed form; it is
   the recursion *on `m`* (the diagonal `A(n, n)`) that outgrows every primitive
   recursive function.</details>

5. **(★★★)** Verify the fixed-point property `Y f = f (Y f)` by β-reducing
   `Y f` one step, and explain how it yields recursion without a named function.
   <details><summary>Hint</summary>Reduce `(λx. f (x x)) (λx. f (x x))` to
   `f ((λx. f (x x)) (λx. f (x x)))`, which is `f (Y f)`.</details>

## See it move

Open the **Tower** widget:
[`site/index.html#stop-12-tower`](../site/index.html#stop-12-tower). Watch the
Ackermann call tree unfold — the nested `A(m, A(m+1, n))` calls fanning out —
and see the digit count of `A(4, n)` outrun the screen.

## Further reading

- W. Ackermann (1928) and R. Péter's simplified two-argument form; see the
  historical account in Appendix C.
- Graham, Knuth & Patashnik, *Concrete Mathematics*, on hyperoperations and
  fast-growing functions. See Appendix C.
- H. P. Barendregt, *The Lambda Calculus*, for the Y combinator and fixed-point
  theory.
- Z. Manna & J. McCarthy on the 91 function and recursion induction.

[← Stop 11 — The Infinite Assembly Line](11-assembly-line.md) · [Route map](index.md) · [Stop 13 — The Hall of Mirrors →](13-hall-of-mirrors.md)
