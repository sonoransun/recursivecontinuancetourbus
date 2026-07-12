[← Appendix B — Glossary](appendix-b-glossary.md) · [Route map](index.md)

# Appendix C — References

An annotated reading list, grouped by theme. The stops that lean on each source
are noted in brackets. Where a book has a single canonical chapter for our
purposes, it is called out.

## Continued fractions: the core books

- **A. Ya. Khinchin, *Continued Fractions* (1935; Dover reprint).** The classic,
  and still the best short book on the subject — barely a hundred pages, moving
  from the definition to the metric theory (Gauss–Kuzmin, Khinchin's constant)
  that bears his name. If you read one book from this list, read this one.
  *[Stops 2, 3, 5, 6, 10.]*

- **G. H. Hardy & E. M. Wright, *An Introduction to the Theory of Numbers*
  (6th ed., 2008).** Chapter X is a complete, rigorous treatment of continued
  fractions: convergents, the determinant identity, Lagrange's and Galois'
  periodicity theorems, Hurwitz's theorem (§11.8), and Pell's equation. The
  reference standard. *[Stops 1–7, 9.]*

- **C. D. Olds, *Continued Fractions* (MAA New Mathematical Library, 1963).** The
  gentlest book-length introduction, aimed at motivated beginners; excellent on
  best approximation and the expansions of `e`. *[Stops 2, 5, 9.]*

- **A. M. Rockett & P. Szüsz, *Continued Fractions* (1992).** A modern graduate
  treatment strong on the palindrome law for `√d`, reduced surds, and the
  ergodic theory of the Gauss map. *[Stops 6, 10.]*

- **J. Borwein, A. van der Poorten, J. Shallit & W. Zudilin, *Neverending
  Fractions: An Introduction to Continued Fractions* (2014).** A lively modern
  survey that carries the reader right up to the open problems of the last stop.
  *[Stops 9, 15.]*

## Number theory, approximation, and Pell

- **Euclid, *Elements*, Book VII, Props. 1–2.** The original algorithm, c. 300
  BC. Readable in Heath's translation. *[Stop 1.]*

- **D. E. Knuth, *The Art of Computer Programming*, Vol. 2 (*Seminumerical
  Algorithms*), §4.5.3.** Euclid's algorithm, Lamé's theorem, and the Fibonacci
  worst case, with Knuth's account of Lamé (1844) as the first complexity result.
  *[Stop 1.]*

- **H. W. Lenstra, Jr., "Solving the Pell Equation," *Notices of the AMS* 49
  (2002).** A superb, self-contained modern survey — how the continued fraction
  of `√d` yields the fundamental solution, and how the numbers explode.
  *[Stop 7.]*

- **I. Vardi, "Archimedes' Cattle Problem," *American Mathematical Monthly* 105
  (1998).** The reduction of the cattle problem to a Pell equation and the
  206,545-digit answer. *[Stop 7.]*

## Rationals, the Stern–Brocot tree, and Farey

- **R. L. Graham, D. E. Knuth & O. Patashnik, *Concrete Mathematics*
  (2nd ed., 1994), §4.5.** The definitive modern account of the Stern–Brocot tree,
  its L/R addressing, and Stern's diatomic sequence (`fusc`). *[Stop 8.]*

- **N. Calkin & H. S. Wilf, "Recounting the Rationals," *American Mathematical
  Monthly* 107 (2000).** The four-page paper introducing the Calkin–Wilf
  enumeration of the positive rationals. *[Stop 8.]*

## Dynamics, ergodic theory, and the metric constants

- **D. H. Bailey, J. M. Borwein & R. E. Crandall, "On the Khintchine Constant,"
  *Mathematics of Computation* 66 (1997).** High-precision computation of `K₀`
  and the theory behind it. *[Stop 10.]*

- **P. Lévy, *Théorie de l'addition des variables aléatoires* (1937).** The
  source of Lévy's constant for the growth of convergent denominators.
  *[Stop 10.]*

- **C. Series, "The Modular Surface and Continued Fractions," *J. London Math.
  Soc.* (1985).** The geometric/dynamical link between quadratic surds, Möbius
  maps, and self-similarity. *[Stops 6, 13.]*

## Exact arithmetic and recursion

- **R. W. Gosper, "Continued Fraction Arithmetic," in M. Beeler, R. W. Gosper &
  R. Schroeppel, *HAKMEM* (MIT AI Memo 239, 1972), item 101.** The origin of
  exact homographic and bihomographic stream arithmetic. *[Stop 11.]*

- **J. Vuillemin, "Exact Real Computer Arithmetic with Continued Fractions,"
  *IEEE Transactions on Computers* 39 (1990).** A rigorous modern development of
  Gosper's ideas. *[Stop 11.]*

- **H. P. Barendregt, *The Lambda Calculus: Its Syntax and Semantics* (1984).**
  The Y combinator and fixed-point theory in full. *[Stop 12.]*

- **Z. Manna & J. McCarthy, "Properties of Programs and Partial Function Logic"
  (1970), and the folklore of the 91 function.** For recursion induction and the
  proof that `M(n) = 91`. *[Stop 12.]*

## Fractals

- **K. Falconer, *Fractal Geometry: Mathematical Foundations and Applications*
  (3rd ed., 2014).** The standard graduate text — similarity dimension, Hausdorff
  dimension, and iterated function systems. *[Stop 13.]*

- **J. E. Hutchinson, "Fractals and Self Similarity," *Indiana Univ. Math. J.* 30
  (1981).** The paper proving that every contracting IFS has a unique attractor —
  a fractal is a fixed point. *[Stop 13.]*

- **M. Barnsley, *Fractals Everywhere* (2nd ed., 1993).** The IFS / attractor
  viewpoint, with the "chaos game" and the collage theorem. *[Stop 13.]*

## Applications

- **M. J. Wiener, "Cryptanalysis of Short RSA Secret Exponents," *IEEE
  Transactions on Information Theory* 36 (1990).** The original attack recovering
  a small private exponent from the convergents of `e/N`. *[Stop 14.]*

- **D. J. Benson, *Music: A Mathematical Offering* (2007).** Equal temperament,
  the Pythagorean comma, and the continued-fraction derivation of the 12-note
  scale. *[Stop 14.]*

- **J. C. Lagarias, ed., *The Ultimate Challenge: The 3x+1 Problem* (AMS, 2010).**
  The definitive survey of the Collatz conjecture. *[Stops 14, 15.]*

- **M. Livio, *The Golden Ratio* (2002).** A readable cultural and mathematical
  history of `φ`. *[Stop 4.]*

## Open problems

- **M. Einsiedler, A. Katok & E. Lindenstrauss, "Invariant measures and the set
  of exceptions to Littlewood's conjecture," *Annals of Mathematics* 164 (2006).**
  The measure-zero result on Littlewood's conjecture. *[Stop 15.]*

- **J. Bourgain & A. Kontorovich, "On Zaremba's conjecture," *Annals of
  Mathematics* 180 (2014).** The density-one theorem toward Zaremba's conjecture.
  *[Stop 15.]*

---

Every worked example in these chapters was produced by the `tourbus` package
itself; to reproduce any of them, run the printed command with
`python -m tourbus demo …`. The route map is at [index.md](index.md).

[← Appendix B — Glossary](appendix-b-glossary.md) · [Route map](index.md)
