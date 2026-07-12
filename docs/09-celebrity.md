[← Stop 8 — The Family Tree](08-family-tree.md) · [Route map](index.md) · [Stop 10 — The Casino →](10-casino.md)

# Stop 9 — Celebrity Sightings

> Two famous constants ride this road: e, whose continued fraction hides a perfect pattern, and π, whose continued fraction hides nothing we can see.

## Overview

The tour now meets its celebrities. The quadratic surds of Stop 6 loop; the
rationals of Stop 2 terminate. But the two most famous transcendental numbers,
`e` and `π`, do neither — and the *contrast* between them is the lesson of this
stop. One wears its structure openly; the other guards it so well that basic
questions about it remain unanswered to this day.

### e: order in plain sight

Euler computed the continued fraction of `e` in **1737** and found a startlingly
regular pattern:

```
e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, …].
```

After the initial `2`, the terms come in blocks of three: `1, 2k, 1` for
`k = 1, 2, 3, …`. Every third partial quotient is an even number `2, 4, 6, 8, …`
climbing without bound; the rest are `1`s. This is not a coincidence but a
theorem — the expansion can be derived from the continued fraction of the
function `tanh` or from properties of the exponential integral.

The pattern does real mathematical work: **it proves that `e` is irrational.**
A continued fraction is finite exactly when its number is rational (Stop 2).
Since Euler's pattern manifestly never terminates — the even entries grow
forever — `e` cannot be rational. This is arguably the cleanest irrationality
proof in mathematics: exhibit the infinite continued fraction and you are done.
(A closely related expansion, `(e−1)/(e+1) = [0; 2, 6, 10, 14, …]`, is even
simpler and gives the same conclusion.)

### π: structure we cannot find

Now `π`:

```
π = [3; 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, …].
```

There is **no known pattern**. The terms wander — mostly small, but with the
occasional giant like `292` (which, recall from Stop 5, is why `355/113` is so
good). Worse, some of the most basic questions are *open problems*:

- Is the sequence of partial quotients of `π` **bounded**, or do arbitrarily
  large terms keep appearing? Unknown.
- Do the partial quotients follow the Gauss–Kuzmin statistics of a "random"
  number (Stop 10)? Believed yes, unproven.

We have computed billions of terms and they *look* random, but "looks random"
is not a theorem. The regular continued fraction of `π`, unlike `e`'s, has never
revealed a usable structure — a humbling fact given how much we know about `π`
in every other respect. This gap is the seed of Stop 15's open-problems chapter.

### Generalized continued fractions: order restored

If the *regular* continued fraction of `π` is chaos, we can recover order by
relaxing the rules. A **generalized continued fraction** allows numerators other
than `1`:

```
b₀ + a₁/(b₁ + a₂/(b₂ + a₃/(b₃ + …))).
```

Give up the requirement that numerators be `1`, and `π` becomes beautifully
patterned. **Lord Brouncker (1655)**, the first president of the Royal Society,
found

```
4/π = 1 + 1²/(2 + 3²/(2 + 5²/(2 + 7²/(2 + …)))),
```

with the odd squares `1², 3², 5², …` marching up the numerators. There is also
the classical `π/4 = 1 − 1/3 + 1/5 − …` (Leibniz), which a generalized continued
fraction converges far faster than.

The deepest of these is **Lambert's continued fraction for the tangent** (1761):

```
tan(x) = x / (1 − x²/(3 − x²/(5 − x²/(7 − …)))).
```

From it, Johann Lambert gave the **first proof that `π` is irrational**: he
showed `tan(x)` is irrational whenever `x ≠ 0` is rational, and since
`tan(π/4) = 1` is rational, `π/4` — and hence `π` — cannot be. The regular
continued fraction hides `π`'s nature; the generalized one exposes it. The two
faces of the continued fraction — the self-organising `e` and the inscrutable
`π` — are why this stop is called "celebrity sightings": you can see the stars,
but only one of them will tell you how it works.

## Worked examples

Expand `e` and watch Euler's `1, 2k, 1` blocks emerge. The `tourbus` engine
prints enough terms to see the pattern lock in — `2; 1, 2, 1, 1, 4, 1, 1, 6, …`:

```
$ python -m tourbus demo cf e
continued fraction of e:
  [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, ...]

 n  a_n  p/q            value      error
 -  ---  ------  ------------  ---------
 0    2  2/1     2.0000000000  +7.18e-01
 1    1  3/1     3.0000000000  -2.82e-01
 2    2  8/3     2.6666666667  +5.16e-02
 3    1  11/4    2.7500000000  -3.17e-02
 4    1  19/7    2.7142857143  +4.00e-03
 5    4  87/32   2.7187500000  -4.68e-04
 6    1  106/39  2.7179487179  +3.33e-04
 7    1  193/71  2.7183098592  -2.80e-05
```

The even terms `2, 4, 6, …` appear at positions `2, 5, 8, …` — every third slot —
exactly Euler's pattern, and each one (being larger than 1) marks a convergent
of above-average accuracy, which is why the error drops sharply right after
`a₅ = 4`.

Now the contrast. Expand `π` and there is no such regularity — small terms,
then a sudden `292`, then no discernible law:

```
$ python -m tourbus demo cf pi
continued fraction of pi:
  [3; 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, ...]

 n  a_n  p/q                  value      error
 -  ---  ------------  ------------  ---------
 0    3  3/1           3.0000000000  +1.42e-01
 1    7  22/7          3.1428571429  -1.26e-03
 2   15  333/106       3.1415094340  +8.32e-05
 3    1  355/113       3.1415929204  -2.67e-07
 4  292  103993/33102  3.1415926530  +5.78e-10
 5    1  104348/33215  3.1415926539  -3.32e-10
 6    1  208341/66317  3.1415926535  +1.22e-10
 7    1  312689/99532  3.1415926536  -2.91e-11
```

Put the two tables side by side: `e`'s terms are a machine you can predict; `π`'s
are, for all anyone can prove, a coin toss.

## Exercises

1. **(★)** From the `e` demo, write down partial quotients `a₈` through `a₁₄`
   predicted by Euler's pattern, then check them against the printed head of the
   expansion.
   <details><summary>Hint</summary>The blocks continue `1, 8, 1, 1, 10, 1, 1,
   …`; the even terms are `8` at position 8 and `10` at position 11.</details>

2. **(★)** Explain, in one sentence, why Euler's pattern proves `e` is
   irrational.
   <details><summary>Hint</summary>The expansion never terminates, and only
   rationals have terminating continued fractions.</details>

3. **(★★)** Compute the first four convergents of Brouncker's formula for `4/π`
   and compare their accuracy to the regular convergents `22/7` and `355/113`.
   <details><summary>Hint</summary>Generalized CFs of `π` converge much more
   slowly than the regular one; that is exactly why the *regular* expansion is
   the powerful tool for approximation.</details>

4. **(★★)** Using Lambert's `tan(x)` continued fraction, evaluate the first two
   convergents at `x = π/4` and see them approach `tan(π/4) = 1`.
   <details><summary>Hint</summary>The first convergent is `x`; the second is
   `x/(1 − x²/3) = 3x/(3 − x²)`.</details>

5. **(★★★)** Sketch Lambert's argument that `tan(x)` is irrational for nonzero
   rational `x`, and hence that `π` is irrational.
   <details><summary>Hint</summary>Assume `x = p/q` rational and derive a
   contradiction from the infinitely-descending integer structure of the
   continued fraction's remainders; the irrationality of `tan(1)` is the crux.
   See Appendix C.</details>

## See it move

Open the **Celebrity Sightings** widget:
[`site/index.html#stop-9-celebrity`](../site/index.html#stop-9-celebrity).
Toggle between `e` and `π` and watch one expansion fall into lockstep while the
other refuses to, with Brouncker's generalized fraction rendered alongside.

## Further reading

- Euler, *De fractionibus continuis dissertatio* (1737) — the original
  computation of `e`'s continued fraction; Appendix C.
- Lambert (1761), the first irrationality proof of `π`; see the modern account
  in Appendix C.
- Hardy & Wright, §§11.6–11.7, on the continued fractions of `e` and `π`.
- C. D. Olds, "The Simple Continued Fraction Expansion of e," *Amer. Math.
  Monthly* (1970).

[← Stop 8 — The Family Tree](08-family-tree.md) · [Route map](index.md) · [Stop 10 — The Casino →](10-casino.md)
