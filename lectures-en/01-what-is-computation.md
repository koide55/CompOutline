# Lecture 1 — What Is Computation?

> **Question for today** — What does it mean to say something "can be computed"? Are there things that cannot be computed?

*Figure labels are in Japanese; the captions here translate them.*

## Learning goals

- State the conditions an algorithm must satisfy
- Trace the operation of a Turing machine and design a simple one
- Explain what the Church–Turing thesis claims
- Explain what it means for a problem to be uncomputable
- Explain that quantum computers do not change the *range* of what is computable, as distinct from how fast it runs
- Explain that undecidability applies to generative AI and static analysers too

## Time allocation

| Minutes | Content |
| --- | --- |
| 0–10 | Course guidance (introductions, how the course runs, assessment) |
| 10–18 | 1.0 A map of this course |
| 18–33 | 1.1 Algorithms |
| 33–57 | 1.2 Turing machines |
| 57–84 | 1.3 The limits of computation |
| 84–90 | Summary and what comes next |

---

## 0 Course guidance

### Instructor

KOIDE Hiroshi
Research Institute for Information Technology, Information Systems Security Division

> **Read the attacker's next move before they make it.**

The internet, web services, IoT devices — when the systems around us come under
cyber attack, how do we keep the damage small? Can we even detect the attack in
the first place? That is what I work on.

| | |
| --- | --- |
| Research | Cyber security |
| CTF | I compete on teams with students |
| Teaching | Ninth year at Kyushu University; 24 years supervising students |

Main themes in the lab:

- **Moving Target Defense** — mechanisms that defend against cyber attack
- Development of **attack detection and defence systems**
- **Improving the safety of IoT devices** and hardening their protocols
- **Threat Trace** — behavioural analysis and tracking of cyber threats

### What we do in the lab

Research turns on these three things.

1. **Propose** — propose a system that addresses a problem, and design the method together
2. **Build and test** — actually build the proposed system and verify it by experiment
3. **Take it outside** — present at international conferences and get feedback. Some students present while still undergraduates

It is a lab where a conversation about technology and a conversation about a
favourite anime run at the same pitch. We enter CTFs as a team, run study
groups, and "it looks interesting, let's try it" is an ordinary day. From
undergraduates to doctoral students, people get on well across year groups.

Lab introduction video:
[Koide Lab introduction video, 2026-01-20](https://youtu.be/SszCCza6PEM)

**Rather than learning the theory and then getting your hands dirty, deepen the
theory while your hands are already dirty.** The reason every session of this
course includes one problem where you work out a number by hand is the same idea.

Of the thirteen sessions, the weight falls on Lecture 12 (Information Security)
and Lecture 13 (From Machine Learning to LLMs and Agentic AI). The others are
arranged to lead there.

(The descriptions of the research and the lab are based on the Kyushu University
Faculty of Engineering
[lab introduction page](https://www.eng.kyushu-u.ac.jp/research-education/labs/lab-post-2630/)
and on the profile in the KOSEN career support system, both consulted
2026-09-21. **No images have been reproduced**, in keeping with this
repository's rule of using no third-party copyrighted work.)

Introductions as time allows; how long we spend depends on how the day runs.

### How this course runs

90 minutes × 13 sessions. Every session follows this shape.

| | |
| --- | --- |
| Opening | Review of the previous session, and **today's question** (one question this 90 minutes will answer) |
| Body | Three blocks. Each block has a figure and a worked example |
| Close | Summary and a look ahead |

Every session has exercises. **Each set contains at least one problem where you
work out a number by hand.** Computer science does not stick until you have a
feel for orders of magnitude. The point is not to memorise answers but to become
able to estimate the size of things.

### Submissions, assessment, attendance

**All submissions go through Moodle.**

| | |
| --- | --- |
| Submit each week | A **portfolio** and **answers to the exercises** |
| Where | Moodle |
| Deadline | Within one week of being set |
| Assessment | Based on the weekly submissions |
| Attendance | **Submitting counts as attending** |
| Contact and questions | Through Moodle |

**Submit every week. That is your grade, and it is your attendance.**

### What goes in the portfolio

Write these two things every week, and submit them together with your answers to
the exercises.

**1. Answer today's question in your own words**

Each session opens with one "question for today". For Lecture 1 it is *What does
it mean to say something "can be computed"? Are there things that cannot be
computed?* **Do not echo the phrasing used in the lecture — put it in your own
words.**

**2. What you did not understand**

Writing "I did not understand this" will never cost you marks. Knowing where you
got stuck is what helps me build the next session.

**Thirteen weeks of this becomes a record of your own learning.** Every session
of this course is held together by its question for today. Line up thirteen
answers and you have a single thread running from the definition of computation
to generative AI. In the final session we will look back over it.

**At least 200 characters.**

No textbook or reading list is assigned. The lecture materials and the exercises
are self-contained.

---

## 1.0 A map of this course

This course is called "An Outline of Computer Systems", but it is not a subject
for reading equipment catalogues. CPU model numbers and the figures attached to
communication standards turn over in a few years. Memorising them is worth little.

What these thirteen sessions chase instead is **the part that does not change**.

The performance of computers has changed by orders of magnitude over that time.
ENIAC, in 1946, performed roughly five thousand additions per second. A 2026
laptop performs several trillion floating-point operations per second — **about a
billion times more** (and accelerators built for AI are another two orders above
that).

But the definition of *what kind of machine it is* has barely changed since the
paper Alan Turing wrote in 1936. Generative AI sits inside that definition too.

So Lecture 1 starts in 1936.

### Why learn the principles in an age when AI writes the code

Let me answer up front the doubt many of you must be holding.

> Generative AI will write the code. Is there any point in learning the principles?

It will write it. But **it is a human being who evaluates what was written**.

- Is that code correct?
- Why is it slow? What would you change to make it fast?
- Why did it break? At which layer did that happen?

None of these can be judged without knowing which layer you are on and what kind
of machinery is underneath. **Someone who cannot read the code the AI wrote
cannot notice when the AI got it wrong.**

And, as we will see in the second half of today, **it is impossible in principle
for a machine to decide completely whether a given program is correct**. So in
the end a human has to judge. This is not the kind of problem that goes away as
the technology improves.

What this course is trying to build is not a skill that competes with AI, but
**an eye that can evaluate what AI produces**.

---

## 1.1 Algorithms

### Definition

An **algorithm** is a procedure for solving a problem that satisfies the
following conditions.

1. **Finiteness** — it always terminates in a finite number of steps
2. **Definiteness** — each step is fixed without ambiguity
3. **Input** — it takes zero or more inputs
4. **Output** — it returns one or more outputs
5. **Effectiveness** — each step can be carried out mechanically

The demand for definiteness is stricter than it sounds. "A pinch of salt" in a
recipe does not satisfy the conditions for an algorithm. **There must be no room
for the judgement of whoever is carrying it out.**

### Example: the Euclidean algorithm

A procedure for finding the greatest common divisor of two natural numbers a and
b. Descriptions of it survive from around 300 BC.

```
Input: natural numbers a, b (a ≥ b > 0)
1. Let r be the remainder of a divided by b
2. If r = 0, output b and stop
3. Set a ← b, b ← r and return to 1
```

Let us follow it with a=1071, b=462.

| Round | a | b | r |
| ---: | ---: | ---: | ---: |
| 1 | 1071 | 462 | 147 |
| 2 | 462 | 147 | 21 |
| 3 | 147 | 21 | 0 |

The answer is 21, reached in three rounds. Factorising both numbers and looking
for common factors takes far more work (and for large numbers it does not finish
in any practical time — a fact that pays off in the public-key cryptography of
Lecture 12).

> **[Figure 1-1] The steps of the Euclidean algorithm**
> A geometric rendering in which a and b are the sides of a rectangle and squares
> are cut away. Cutting two 462×462 squares from a 1071×462 rectangle leaves
> 462×147, and so on, shrinking until a 21×21 square divides what is left. Drawn
> as nested rectangles, showing that the greatest common divisor is the side of
> the last square remaining.

![Figure 1-1 The steps of the Euclidean algorithm](../figures/fig-01-01.svg)

**What to notice here**: nowhere in this procedure does a computer appear. An
algorithm can be carried out with paper and pencil. A computer is merely a device
that carries it out quickly.

### Finiteness is not a trivial condition

Checking condition 1 — that it always terminates — is in fact not easy. In the
Euclidean algorithm the remainder r strictly decreases each round, and a
non-negative integer cannot decrease forever, so it terminates. That argument is
clean, but it is not always available.

Consider the following procedure (the Collatz procedure).

```
Input: natural number n
1. If n = 1, stop
2. If n is even, n ← n/2; if odd, n ← 3n+1
3. Return to 1
```

Starting from n=7 it runs 7→22→11→34→17→52→26→13→40→20→10→5→16→8→4→2→1 and
finishes in 16 steps. But **whether it terminates for every n has still not been
proved as of 2026**. It has been open since it was posed in 1937.

A procedure whose termination is unknown can be written down this easily. Holding
on to that feeling makes 1.3 land properly.

---

## 1.2 Turing machines

### Why think about such a thing

We want to define "can be computed". But defining it as "there is an algorithm"
leaves the vague phrase "can be carried out mechanically" sitting inside the
definition of *algorithm*. We are going in circles.

**And there was a real need to settle this.** In 1928 David Hilbert had posed the
**decision problem** (*Entscheidungsproblem*) — can we decide by a mechanical
procedure whether a mathematical proposition is provable? If what "mechanical
procedure" refers to is not fixed, the question cannot be answered at all.

The approach Alan Turing (1912–1954) took in 1936 was this.

> When a human being computes with paper and pencil, what is that person
> actually doing? Build a machine that simplifies it to the limit, and what that
> machine can do *is* computation.

Watch a person computing with paper and pencil, and what they do amounts to this.

- Look at one spot on the paper and read the symbol written there
- Decide what to do next, from what is in their head ("what I am in the middle of
  doing") — the state — together with the symbol they read
- Write a symbol there (possibly erasing and rewriting)
- Shift their gaze to the neighbouring spot

Turn that into a machine and you have the **Turing machine**.

### Construction

> **[Figure 1-2] The construction of a Turing machine**
> A tape extending infinitely to left and right, drawn as a row of cells with a
> symbol in each. A head pointing at one cell is shown as an upward arrow, with
> the box of the "finite control" above it. The current state q is written inside
> the control. Arrows run from the control to the head ("symbol to write,
> direction to move") and from the head to the control ("symbol read"), showing
> that read → write → move → change state is one step.

![Figure 1-2 The construction of a Turing machine](../figures/fig-01-02.svg)

- **Tape** — paper divided into cells, extending infinitely left and right. One
  symbol can be written in each cell
- **Head** — points at one cell of the tape. It can read and write that cell and
  move one cell left or right
- **Finite control** — holds one of a finite number of states. The state
  corresponds to "what I am in the middle of doing"

The behaviour is completely determined by a table of **transition rules**.

```
(current state, symbol read) → (symbol to write, direction, next state)
```

That is all. Apart from the infinite tape, there are only finitely many parts.

### Example: a machine that adds one

Build a machine that takes a tape with a binary number on it and adds one. The
tape holds `1011` (11 in decimal), and the head points at the rightmost `1`.
Blank is written `␣`.

Just as in pencil-and-paper arithmetic, look from the right end: if you see 1,
make it 0 and carry to the left; if you see 0, make it 1 and stop.

| State | Symbol read | Symbol written | Move | Next state |
| --- | --- | --- | --- | --- |
| carry | 1 | 0 | left | carry |
| carry | 0 | 1 | — | halt |
| carry | ␣ | 1 | — | halt |

Following it on `1011` (the underline marks the head).

| Step | Tape | State |
| ---: | --- | --- |
| 0 | 1 0 1 <u>1</u> | carry |
| 1 | 1 0 <u>1</u> 0 | carry |
| 2 | 1 <u>0</u> 0 0 | carry |
| 3 | 1 <u>1</u> 0 0 | halt |

`1100` = 12. Correct. There are two states and three rules, but this works for a
binary number of any length. With `111` it reads a blank and produces `1000`.

> **[Figure 1-3] State transition diagram of the "add one" machine**
> States carry and halt drawn as circles, with a self-loop on carry labelled
> `1/0,L`, and arrows from carry to halt labelled `0/1,-` and `␣/1,-`. Showing
> the same content as the table as a diagram impresses on the reader what the
> control really is: finitely many states and arrows.

![Figure 1-3 State transition diagram of the "add one" machine](../figures/fig-01-03.svg)

### How to design one: a state is something you can remember

In building that machine we in fact used one design pattern:
**make each state correspond to something you want to remember**.

The state `carry` was exactly the note "I am still holding a carry". Without
writing it on the tape, one state remembers it.

A Turing machine has no variables. The only places it can store anything are the
tape and the state, and **there are only finitely many states**. So design
proceeds in this order.

1. **Decide what you need to remember** — the number of kinds is the number of states
2. **For each state, write what happens on reading each symbol** — symbol to
   write, direction to move, next state
3. **Decide when to stop**

If there is nothing to remember, one state is enough. For instance a machine that
rewrites every 0 on the tape to 1 and stops on meeting a blank needs only one
state, because the head's position remembers how far it has got.

On the other hand, **deciding whether the number of 1s is even or odd takes two
states**: one for having read an even number, one for odd. The count itself
cannot be remembered (that would take infinitely many states), but **parity alone
needs only two**. Exercise 1-2 asks you to build this.

**The number of things to remember determines the number of states.** That is
very nearly the only trick in designing a Turing machine.

### The universal Turing machine

Every machine so far is dedicated to one job — adding one. But Turing showed that
one can build **a machine that, given the transition table of another Turing
machine written on its tape, interprets it and imitates that machine**. This is
the **universal Turing machine**.

This is decisive. Rather than building a separate machine for each job, you
**give one machine "what to do" as data**.

- The rule table written on the tape = the **program**
- The universal machine that interprets and runs it = the **CPU**
- The input placed on the same tape = the **data**

The basic design of today's computers — program and data held in the same place
in the same form (the von Neumann architecture of Lecture 3) — has its prototype
here. In 1936, when not a single electronic computer yet existed.

---

## 1.3 The limits of computation

Back to Hilbert's decision problem, touched on in 1.2. The title of Turing's 1936
paper is "On Computable Numbers, **with an Application to the
Entscheidungsproblem**".

**Answering the decision problem was the point; the Turing machine was the tool
for it.** Now let us look at that answer.

### The Church–Turing thesis

The Turing machine is astonishingly simple, and astonishingly strong. In fact,
models of computation proposed from entirely different starting points have all
been shown to have the same power as the Turing machine.

| Model | Proposed | Starting point |
| --- | --- | --- |
| Turing machine | Turing, 1936 | Mechanise pencil-and-paper computation |
| λ-calculus | Church, 1936 | Express computation with function application alone |
| Recursive functions | Gödel, Kleene, 1930s | Build functions from basic functions and recursion |
| Register machine | Shepherdson–Sturgis, 1963 | Operate on infinitely many numbered registers |
| Cellular automata | von Neumann, 1940s | A lattice updated by simple rules |

The starting points are unrelated, yet the sets of computable functions coincide
exactly. From this fact the following claim is widely accepted.

> **The Church–Turing thesis**
> The functions that are "intuitively computable" coincide with the functions
> computable by a Turing machine.

It is a *thesis*, not a theorem. As long as "intuitively computable" has no
mathematical definition, it cannot be proved. But in ninety years no model of
computation that breaks it has been found.

**The modern implication**: changing the language or the hardware you use *does
not widen the range of problems that can be computed*. There is nothing you can
do in Python that you cannot do in C, and lining up ten thousand GPUs does not
make something computable that was not computable in principle.

### Do quantum computers change this?

No. At least not as regards **what can be computed**.

The quantum Turing machine, the mathematical formulation of a quantum computer,
has been shown to **compute the same range of functions** as an ordinary Turing
machine. The Church–Turing thesis remains unbroken so far.

**What changes is speed.**

| Algorithm | What it does | How it helps |
| --- | --- | --- |
| Shor (1994) | Integer factorisation | Solves it in polynomial time. No efficient classical method is known |
| Grover (1996) | Brute-force search | Reduces a search taking n steps to about √n |

**"Solvable quickly" and "solvable" are different things.** Today we are talking
about range. How to measure speed comes in Lecture 2 (computational complexity).

The consequence of Shor working is serious. **Today's public-key cryptography
entrusts its security to the fact that no efficient method of factorisation is
known** (Lecture 12). That is why a worldwide migration to cryptography that
quantum computers cannot break is under way.

**But the halting problem is unaffected by this.** It is a question of range, not
of speed. However fast a machine you build, what lies outside the range cannot be
computed. Exercise 1-3 asks about this.

### The halting problem

So, are there things that cannot be computed? There are — and for a natural
problem at that.

> **The halting problem** — given a program P and an input x, decide whether
> running P on x ever halts.

A program `halts(P, x)` that decides this **does not exist**. The proof is short.
Assume it exists and derive a contradiction.

Suppose `halts(P, x)` exists. Write the following program `trouble`.

```
trouble(P):
    if halts(P, P):       # does P halt when given itself as input?
        while True: pass  # if it halts, deliberately loop forever
    else:
        return            # if it does not halt, halt immediately
```

Now consider `trouble(trouble)`.

- Suppose `trouble(trouble)` **halts**. Then `halts(trouble, trouble)` returns
  true, so `trouble` enters an infinite loop and does not halt. Contradiction.
- Suppose `trouble(trouble)` **does not halt**. Then `halts(trouble, trouble)`
  returns false, so `trouble` returns immediately and halts. Contradiction.

Either way we get a contradiction. So the assumption is false, and `halts` does
not exist. ∎

> **[Figure 1-4] The diagonal argument for the halting problem**
> An infinite table with programs P1, P2, P3, … down the side and inputs x1, x2,
> x3, … across the top. Each cell holds "halts" or "does not halt", with the
> diagonal cells (Pi, xi) highlighted. Inverting every diagonal entry gives the
> behaviour of `trouble`, which therefore differs from every row in at least one
> cell and so cannot appear anywhere in the table.

![Figure 1-4 The diagonal argument for the halting problem](../figures/fig-01-04.svg)

This casts some light on why the Collatz procedure from "finiteness is not
trivial" has been open for ninety years. **There is no general mechanical method
for deciding whether something halts in the first place.**

### There are other undecidable problems

The halting problem is not a special case. Many practical problems run into the
same wall.

- Whether two programs compute the same function (program equivalence)
- Whether a given program can cause a particular bug (division by zero, memory corruption)
- Whether a given program behaves as a virus

Rice's theorem gathers these up: **every non-trivial property of the
input–output behaviour of a program is undecidable**.

That is why compiler warnings miss things, why antivirus software never becomes
perfect, and why testing cannot prove the absence of bugs. **Not because the
technology is immature, but as a matter of principle.**

In practice this limit is worked around as follows.

- **Approximate** — over-report "this might be dangerous" (false positives in static analysers)
- **Narrow the domain** — restrict the subject to a decidable range (type systems, regular expressions)
- **Put a human in** — leave the judgement to a person

### So is generative AI solving the halting problem?

The obvious question follows.

> Ask a generative AI "does this program halt?" and an answer comes back. Static
> analysers tell us "a null dereference can happen here". Does that not amount to
> solving the halting problem?

**It does not.** An answer coming back and a correct decision being made are
different things.

What a generative AI does is form a guess, from the large body of code it has
learned from, that "loops shaped like this usually terminate". It is often right.
But

- when it is wrong it does not say "I don't know" (why that is comes in Lecture 13)
- **nothing anywhere guarantees that it is right for every input**

Rice's theorem says **no method whatsoever can provide that guarantee**. More
training data will not move this wall, nor will a bigger model. Not because the
technology is immature, but as a matter of principle.

So generative AI and static analysers alike are doing only the first of the
workarounds listed above — **approximating**. **Being useful as a tool and being
able to decide are different things.**

This distinction becomes the stance of the whole course.

> **That a machine can produce an answer, and that you may trust that answer, are
> two different things.**

In Lecture 13 we return to the same question about generative AI.

---

## Exercises

> **Submission**: through Moodle. For **essay questions**, write out your reasoning
> and working. For **numerical and cloze questions**, enter only the answer (no
> working needed).

**1-1.** Run the Euclidean algorithm with a=252, b=105 and write the (a, b, r) of
each step.

**1-2.** A tape holds a string of `0`s and `1`s. Build the transition table of a
Turing machine that writes `Y` if the number of `1`s in the string is even and
`N` if it is odd, then halts. The head starts at the left end of the string and
moves right. **It writes `Y` or `N` in the blank cell just past the right end of
the string and halts.**
(Hint: two states suffice — "an even number of 1s read so far" and "an odd
number". The table can take the same shape as the "add one" machine in 1.2.)

**Answer format**: write one rule per line, in this form.
`(even, 0) → write 0, move right, even`

**1-3.** Is the following claim correct? Answer with reasons.
"Once quantum computers become practical, the halting problem will become
solvable too."

**1-4.** Name one behaviour in software you use regularly that you believe errs
on the safe side in order to avoid undecidability, and explain why you think so.

**1-5.** Ask a generative AI "does this program halt?" and an answer comes back.
Does this mean the halting problem has been solved? Answer with reasons.

---

## Summary

- An algorithm is a procedure satisfying finiteness, definiteness and
  effectiveness. Confirming that it terminates is often hard
- A Turing machine simplifies pencil-and-paper computation to the limit. Its only
  parts are a tape, a head, and finitely many states
- A universal Turing machine takes another machine's rule table as data and runs
  it. The prototype of the stored-program computer is here
- By the Church–Turing thesis, changing the model of computation does not widen
  the range of what can be computed
- Quantum computers do not change the range either. They change speed, and the
  consequence of that lands on the public-key cryptography of Lecture 12
- The halting problem is uncomputable. And every non-trivial property of a
  program's behaviour is uncomputable
- Generative AI and static analysers alike only work around this limit by
  approximating. That a machine can produce an answer, and that you may trust
  that answer, are different things

**Next time**: granting that something can be computed, does it finish in any
practical time? And how should information be represented for a computer to
handle it at all?
