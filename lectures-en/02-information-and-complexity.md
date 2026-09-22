# Lecture 2 — Representing Information, and Computational Complexity

> **Question for today** — What do we gain by representing information in binary? And what is a "fast algorithm"?

*Figure labels are in Japanese; the captions here translate them.*

## Learning goals

- Convert between binary and decimal, and represent negative numbers in two's complement
- Explain why floating-point numbers carry error
- Explain the difference between SI and binary prefixes, and compute the discrepancy in reported capacity
- Express the complexity of an algorithm in big-O notation and compare growth against input size
- Explain the distinction between P and NP, and what NP-completeness means
- Explain how quantum computers change the complexity classes, and what they do not change

## Time allocation

| Minutes | Content |
| --- | --- |
| 0–5 | Review of last time |
| 5–22 | 2.1 Representing information |
| 22–36 | 2.2 Representing numbers, and error |
| 36–48 | 2.3 Units and a feel for orders of magnitude |
| 48–85 | 2.4 Computational complexity |
| 85–90 | Exercises and summary |

---

## 2.1 Representing information

### Why binary?

Computers use binary not because binary is mathematically superior to decimal.
It is **because it is easy to build physically**.

Think about representing numbers with voltage. To put decimal on a single wire
you would divide 0 V to 3.3 V into ten levels, leaving only 0.33 V per level.
Given noise on the wiring, drift with temperature, and part-to-part variation,
telling "1.65 V" from "1.98 V" is not realistic.

With two states the story changes. Decide that "below 1.0 V is 0, above 2.0 V is
1, in between is undefined" and you have more than a volt of margin. Some
wobble does not cause an error.

> **[Figure 2-1] Voltage levels and distinguishing states**
> Two vertical bands with voltage (0–3.3 V) on the vertical axis. On the left,
> ten levels: each band is narrow, and vertical bars representing actual signal
> variation spill into the neighbouring level. On the right, two levels (a 0
> region, an undefined region, a 1 region), showing the same variation staying
> inside its region.

![Figure 2-1 Voltage levels and distinguishing states](../figures/fig-02-01.svg)

The consequences of that margin are large. Even if a signal degrades somewhat,
**rounding it back to 0 or 1 at the moment of reading restores it exactly**. An
analogue signal degrades every time it is copied; a digital signal does not.
Copy it ten thousand times, move it across storage media again and again, and the
information is preserved.

### Bits and bytes

The smallest unit representing one two-state choice is the **bit** (binary
digit). With n bits you can represent 2ⁿ states.

| Bits | States | Roughly |
| ---: | ---: | --- |
| 8 | 256 | One byte. One character, one colour component |
| 16 | 65,536 | One audio sample |
| 32 | about 4.3 billion | An IPv4 address, one integer |
| 64 | about 1.8×10¹⁹ | A modern pointer, a large integer |

Eight bits together are called a **byte**. There is little necessity in the
number eight; it is historical (six bits were not enough for characters, machines
with seven to nine bits proliferated, and then IBM System/360 adopted eight and
made it the de facto standard).

Where precision is needed, the term **octet** is used to make explicit that eight
bits are meant. Communication-standard documents use it almost exclusively.

### Representing characters

Characters are handled by fixing a table matching characters to numbers, and
representing the numbers in binary. Such a table is a **character encoding**.

| Scheme | Year | Characteristics |
| --- | ---: | --- |
| ASCII | 1963 | 7 bits, 128 characters. Alphanumerics and symbols only |
| JIS X 0208 | 1978 | Japanese. Kanji specified by row-cell number |
| Shift_JIS | 1982 | A Japanese encoding arranged to coexist with ASCII |
| Unicode / UTF-8 | 1991– | The world's scripts in one system. Variable length |

Today **UTF-8** is the de facto standard (over 98% of web pages). UTF-8 is a
variable-length scheme representing one character in one to four bytes, with
these properties.

- The ASCII range (alphanumerics) stays one byte. Compatible with existing systems
- Japanese hiragana and kanji take three bytes
- Emoji take four bytes

**This is where practice trips people up**: "number of characters" and "number of
bytes" do not agree. `"あ"` is one character but three bytes in UTF-8. Confusing
the two in a database column limit, a password length limit, or a traffic
estimate produces a bug where only Japanese fails.

Further, some emoji combine several code points into one picture (skin-tone
modifiers, family emoji). Counting "one character as seen" is different again
from counting bytes and from counting code points.

---

## 2.2 Representing numbers, and error

### Negative numbers: two's complement

The naive way to represent negative numbers is to use the top bit as a sign
(sign-and-magnitude), but this has the awkward property that +0 and −0 exist
separately. It also means building separate adder and subtractor circuits.

What is actually used is **two's complement**. In n bits, the negative number −x
is represented as 2ⁿ − x.

An 8-bit example:

| Decimal | Binary |
| ---: | --- |
| 3 | 0000 0011 |
| 2 | 0000 0010 |
| 1 | 0000 0001 |
| 0 | 0000 0000 |
| −1 | 1111 1111 |
| −2 | 1111 1110 |
| −3 | 1111 1101 |

To obtain −x, "invert every bit and add one".
3 = `00000011` → invert `11111100` → +1 → `11111101` = −3.

**The advantage of two's complement**: no subtraction is needed. a − b can be
computed as a + (−b) using **the adder alone**. And there is no need to worry
about signs; overflow is simply discarded. The hardware becomes dramatically
simpler.

The range in n bits is −2ⁿ⁻¹ to 2ⁿ⁻¹−1. In 8 bits, −128 to +127. There is one
more on the negative side because 0 sits on the positive side.

**Overflow**: 127 + 1 is `01111111 + 00000001 = 10000000` = −128. This behaviour —
"I added to a large number and got a negative one" — has caused real accidents.

### Fractions: floating-point numbers

There are infinitely many real numbers, but finitely many bits can represent only
finitely many. The floating-point numbers defined by **IEEE 754** do scientific
notation directly in binary.

```
value = (−1)^sign × 1.mantissa × 2^exponent
```

| Format | Total | Sign | Exponent | Mantissa | Significant decimal digits |
| --- | ---: | ---: | ---: | ---: | ---: |
| Single precision (float) | 32 | 1 | 8 | 23 | about 7 |
| Double precision (double) | 64 | 1 | 11 | 52 | about 15–16 |

**This is the important part**: only some decimal fractions can be written as a
finite binary fraction. In binary, 0.1 recurs as `0.0001100110011…` and cannot be
represented exactly in finitely many bits. The result is this.

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
```

This is not a bug in the implementation; it is **unavoidable so long as binary
floating point is used**.

> **[Figure 2-2] The real line and the distribution of floating-point numbers**
> The real line on the horizontal axis, with vertical bars marking the positions
> of representable floating-point values. Near 0 the bars are dense; the larger
> the value, the sparser they become (the spacing doubles with each increment of
> the exponent). Makes it obvious at a glance that the representable numbers are
> not evenly spaced.

![Figure 2-2 The real line and the distribution of floating-point numbers](../figures/fig-02-02.svg)

What to do about it in practice:

- Do not handle money in floating point. Use integers (in the smallest unit) or a decimal type
- Do not test for equality. Judge with `abs(a - b) < ε`
- Adding a small number to a large one loses the small one (loss of significance), so when summing, add from smallest to largest

---

## 2.3 Units and a feel for orders of magnitude

### SI prefixes and binary prefixes

Is "one kilobyte" 1000 bytes or 1024? **Both conventions exist**, and that is the
source of the confusion.

| Binary prefix | Value | SI prefix | Value | Discrepancy |
| --- | ---: | --- | ---: | ---: |
| Ki (kibi) | 2¹⁰ = 1,024 | k (kilo) | 10³ = 1,000 | +2.4% |
| Mi (mebi) | 2²⁰ = 1,048,576 | M (mega) | 10⁶ | +4.9% |
| Gi (gibi) | 2³⁰ | G (giga) | 10⁹ | +7.4% |
| Ti (tebi) | 2⁴⁰ | T (tera) | 10¹² | +10.0% |
| Pi (pebi) | 2⁵⁰ | P (peta) | 10¹⁵ | +12.6% |

**Why reported capacities disagree**: storage manufacturers use SI prefixes
(1 TB = 10¹² bytes), while many operating systems count in powers of two and
display "TB".

Buy a 1 TB drive and you have 10¹² bytes = 0.909 TiB. If the OS divides by 2⁴⁰
and displays "TB", it reads **0.91 TB**. It looks as though 9% has vanished, but
nobody has lied.

Note that communication speeds have always used SI prefixes. "1 Gbps" is 10⁹ bits
per second. And bit and byte are easy to confuse: **b is bit, B is byte**.
Sending a 1 GB file over a 1 Gbps link takes 8 Gbit ÷ 1 Gbps = 8 seconds (in theory).

### Acquire a feel for orders of magnitude

In computer science, being able to estimate "how many digits" on the spot pays
off. Useful approximations:

- 2¹⁰ ≈ 10³ (2.4% error), hence 2²⁰ ≈ 10⁶ and 2³⁰ ≈ 10⁹
- one day ≈ 10⁵ seconds (86,400 exactly)
- one year ≈ π × 10⁷ seconds

**Orders of magnitude for latency** (representative values as of 2026; remember
only the order):

| Operation | Time | Scaled so one CPU cycle is one second |
| --- | ---: | --- |
| One CPU cycle | 0.3 ns | 1 second |
| L1 cache reference | 1 ns | 3 seconds |
| Main memory reference | 80 ns | 4 minutes |
| NVMe SSD read | 20 µs | 18 hours |
| Round trip within one data centre | 0.5 ms | 20 days |
| Round trip Tokyo–US West Coast | 100 ms | 11 years |

This table is referred back to repeatedly in Lectures 5, 6 and 9. **Most of the
design philosophy of computers is about how to hide these differences in order of
magnitude.**

---

## 2.4 Computational complexity

### Measuring "fast" without depending on the machine

Which is faster, algorithm A or algorithm B? Measure them and the answer changes
with the machine, the language, and the load that day. What we want to know is
not the skill of the implementation but **a property of the algorithm itself**.

So we measure **how the number of basic operations grows with the size n of the
input**, ignoring constant factors and lower-order terms. We write this in
**big-O notation**.

If for sufficiently large n there is a constant c with f(n) ≤ c·g(n), we write
f(n) = O(g(n)).

Why is it acceptable to ignore constant factors? **Because a constant factor
shrinks when you buy a new machine, while the order shrinks no matter what you buy.**

### The common orders

| Order | Name | Example |
| --- | --- | --- |
| O(1) | constant | Reading the nth element of an array, a hash table lookup |
| O(log n) | logarithmic | Binary search, lookup in a balanced tree |
| O(n) | linear | Scanning an array, finding the maximum |
| O(n log n) | linearithmic | Merge sort, quicksort (average) |
| O(n²) | quadratic | Selection sort, comparing all pairs |
| O(2ⁿ) | exponential | Enumerating all subsets |
| O(n!) | factorial | Enumerating all permutations (naive travelling salesman) |

**What it feels like as n grows** (taking one operation as 1 ns):

| n | O(n) | O(n log n) | O(n²) | O(2ⁿ) |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 10 ns | 33 ns | 100 ns | 1 µs |
| 100 | 100 ns | 664 ns | 10 µs | 4×10¹³ years |
| 10,000 | 10 µs | 133 µs | 100 ms | — |
| 1,000,000 | 1 ms | 20 ms | 11.6 days | — |

> **[Figure 2-3] How the orders grow**
> n on the horizontal axis, operation count on a logarithmic vertical axis, with
> six curves: O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ). Where n is small the
> ordering can swap, but as n grows they separate decisively. Each curve is
> labelled directly rather than through a legend.

![Figure 2-3 How the orders grow](../figures/fig-02-03.svg)

**What to take from it**: at n=100 the gap between O(n²) and O(2ⁿ) is "ten
microseconds" versus "a thousand times the age of the universe". Make the
computer a million times faster and an O(2ⁿ) problem only becomes tractable for
about twenty more units of n.

### An example of searching: linear and binary search

Find a value in a sorted array.

**Linear search** — look from the front in order. At worst n steps. O(n).
**Binary search** — look at the middle; if it is larger than the target narrow to
the left half, if smaller to the right. It halves every time, so log₂ n steps.
O(log n).

At n = one billion, linear search takes a billion steps at worst, binary search
about 30. **A factor of thirty million.** No cleverness of implementation closes
that gap.

But binary search demands a sorted array. If you are only searching once, sorting
costs O(n log n), so linear search is faster. **Judge by the whole use, not the
order alone.**

### P and NP

So far we have discussed individual algorithms. Next we classify **the problems
themselves**.

- **Class P** — problems for which an algorithm running in polynomial time, that
  is O(nᵏ), exists. Taken as the theoretical definition of "solvable in practice"
- **Class NP** — problems for which, given a candidate answer, it can be
  **verified** in polynomial time whether it is correct

An example. "Is there a route of length at most L visiting all n cities?" (the
travelling salesman problem).

- Given a route, checking that it visits every city and has length at most L takes
  only n additions → **it is in NP**
- But no polynomial-time algorithm for **finding** such a route is known

P ⊆ NP is obvious (if you can solve it you can verify it). So **is P = NP?** This
remains open as of 2026, and is one of the Clay Mathematics Institute's Millennium
Prize Problems (a million dollars).

### NP-completeness

Within NP there is a group of especially hard problems with the property that
**if any one of them can be solved in polynomial time, then every problem in NP
can be**. These are the **NP-complete** problems.

Representative examples: the satisfiability problem (SAT), the travelling salesman
problem, the knapsack problem, graph colouring, generalised Sudoku.

**What it means in practice**: once you know a problem is NP-complete, you may
essentially give up on continuing to look for an efficient algorithm. Your chance
of finding by the deadline what researchers worldwide have failed to find in half
a century is slim. Take one of these roads instead.

- **Approximate** — it need not be optimal; guarantee, say, within twice the optimum
- **Restrict the problem** — exploit properties of the inputs that actually arise
- **Use heuristics** — methods with no guarantee that work well in practice (simulated annealing, genetic algorithms)
- **Settle for a small enough n**

### How do quantum computers change this classification?

In Lecture 1 we said that quantum computers do not change the **range** of what
can be computed but do change the **speed**. Now that we have the vocabulary of
complexity, let us restate that precisely.

The class of problems solvable in polynomial time on a classical computer was
**P**. The class solvable in polynomial time on a quantum computer is called
**BQP**.

- **P ⊆ BQP** — anything a quantum computer can do, a classical computer can do
  too (slowly). That is why Lecture 1's "the range does not widen" holds
- **There are problems in BQP not known to be in P** — the leading example is
  **integer factorisation**. Shor's algorithm solves it in polynomial time on a
  quantum computer

**This is the most widely misunderstood point.**

> "With a quantum computer we can solve NP-complete problems too" — this is wrong.

Quantum computers are not believed to solve NP-complete problems in polynomial
time. **Grover's algorithm**, which speeds up brute-force search, reduces a search
over n possibilities to about √n steps. But for an exponential-time problem n is
2ᵏ, so **2ᵏ merely becomes 2^(k/2)**. It is still exponential time.

It is an acceleration of the order that lengthening a symmetric key by one bit
restores the original strength.

### Where does factorisation sit?

So why does Shor work? **Because factorisation is not NP-complete.**

- Factorisation is in NP (given the answer, you can multiply and check)
- But it is not believed to be NP-complete. It is seen as sitting **in between** P
  and NP-complete
- The region where quantum computers are known to help is this middle ground

In other words the strength of a quantum computer is not "solving any hard
problem quickly" but **biting into problems with a particular structure**.
Factorisation and the discrete logarithm have the structure of "find the period",
and Shor attacks exactly that.

**Foreshadowing Lecture 12**: today's public-key cryptography (RSA, elliptic-curve
cryptography) entrusts its security to precisely these middle-ground problems.
That is why Shor breaks them. What is being migrated to are different problems
(lattice problems and others) that quantum computers do not appear able to solve
efficiently either.

### Relation to Lecture 1

Lecture 1 dealt with "can it be computed" (**computability**); today with "can it
be computed in a practical time" (**computational complexity**).

```
All problems
├── Uncomputable (the halting problem)                  ← Lecture 1
└── Computable
    ├── Only exponential time known
    │    ├── NP-complete (SAT, travelling salesman)   still exponential on a quantum computer
    │    └── In between (factorisation, discrete log) polynomial on a quantum computer → Lecture 12
    └── Solvable in polynomial time (P ⊆ BQP)
```

**These two walls show their faces again and again in the sessions that follow.**
The public-key cryptography of Lecture 12 entrusts its security to factorisation
*not* being known to be in P, and the machine learning of Lecture 13 is machinery
for forcing through, by approximation, problems that cannot be solved exactly.

---

## Exercises

> **Submission**: through Moodle. For **essay questions**, write out your reasoning
> and working. For **numerical and cloze questions**, enter only the answer (no
> working needed).

**2-1.** Represent the decimal number 173 as an 8-bit binary number. Also
represent −45 in 8-bit two's complement.

**2-2.** You buy an SSD labelled 2 TB. If the OS treats 2⁴⁰ as one TB, what
capacity does it display? Give the answer to two decimal places.

**2-3.** Explain why `0.1 + 0.2 == 0.3` is false, referring to binary
representation.

**2-4.** A process took 1 second at n=1,000. If the process is O(n²), how many
seconds does it take at n=10,000? What if it is O(n log n)?

**2-5.** Of the four below, the one known to be NP-complete is **(b), Sudoku**
(generalised to n×n). For each of the remaining three, explain why it is not
NP-complete, referring to how long it takes to solve as a function of the input
size n.

(a) Sorting an array (c) Binary search
(d) Shortest path in a graph (the kind Dijkstra's algorithm solves)

**2-6.** Is the claim "once quantum computers become practical, the travelling
salesman problem will become solvable in a practical time" correct? Answer with
reference to how much of a speed-up Grover's algorithm provides.

**2-7.** Name one service you use that you believe returns an approximate rather
than an exactly optimal answer, and explain why you think so.
(Examples: route guidance, product recommendation, ride matching.)

---

## Summary

- Binary is used because it is robust against noise. The fact that digital
  information does not degrade follows from this property
- Negative numbers are represented in two's complement, so that subtraction needs
  only the adder
- Floating-point numbers carry error in principle. Do not test equality; do not
  use them for money
- The difference between SI prefixes (10³) and binary prefixes (2¹⁰) produces the
  discrepancy in reported capacity
- Complexity is measured by growth against input size. Constant factors shrink
  when you buy new hardware; the order does not
- P is the class solvable in polynomial time, NP the class verifiable in
  polynomial time. P = NP is open
- On meeting an NP-complete problem, give up on an exact solution and turn to
  approximation, restriction or heuristics
- Quantum computers satisfy P ⊆ BQP, so they do not change the range of what is
  computable. NP-complete problems remain exponential. Where they help is on
  "in-between" problems such as factorisation — and today's public-key
  cryptography rides on exactly those (Lecture 12)

**Next time**: so far this has been mathematics. How do we build it out of
electrical circuits?
