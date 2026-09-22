# Lecture 3 — From Logic Circuits to the Processor

> **Question for today** — How do we build a mathematical model out of electricity?

*Figure labels are in Japanese; the captions here translate them.*

## Learning goals

- Write the truth tables of the basic logic gates, and construct the others from NAND alone
- Explain the structure of half and full adders, and assemble an adder circuit
- Explain the mechanism by which a flip-flop holds memory
- Explain the components of a von Neumann machine and the instruction cycle
- Explain what Moore's law states, and what exactly has now ended

## Time allocation

| Minutes | Content |
| --- | --- |
| 0–5 | Review of last time |
| 5–25 | 3.1 Logic gates |
| 25–45 | 3.2 Circuits that compute, circuits that remember |
| 45–70 | 3.3 The structure of a processor and the execution of instructions |
| 70–85 | 3.4 The succession of devices, and Moore's law |
| 85–90 | Exercises and summary |

---

## 3.1 Logic gates

### Operations on one bit

In Lecture 2 we settled on representing information with 0 and 1. Computation
then becomes "operations producing a 0 or 1 from a set of 0s and 1s". The
circuits that perform these are **logic gates**.

| Gate | Notation | Meaning | Truth table (A,B → output) |
| --- | --- | --- | --- |
| NOT | ¬A | Inversion | 0→1, 1→0 |
| AND | A·B | 1 when both are 1 | 00→0, 01→0, 10→0, 11→1 |
| OR | A+B | 1 if either is 1 | 00→0, 01→1, 10→1, 11→1 |
| XOR | A⊕B | 1 when they differ | 00→0, 01→1, 10→1, 11→0 |
| NAND | ¬(A·B) | Negation of AND | 00→1, 01→1, 10→1, 11→0 |
| NOR | ¬(A+B) | Negation of OR | 00→1, 01→0, 10→0, 11→0 |

> **[Figure 3-1] Symbols for the basic logic gates**
> The MIL symbols for NOT, AND, OR, XOR, NAND and NOR in a row, each with a small
> truth table beneath it. The position of the small circle denoting negation
> (putting one on the output of AND makes NAND) is emphasised, so that reading the
> symbols becomes a rule rather than memorisation.

![Figure 3-1 Symbols for the basic logic gates](../figures/fig-03-01.svg)

### Everything can be built from NAND alone

Remarkably, **every logical function can be built from a single kind of gate, the
NAND** (NAND completeness, functional completeness).

- **NOT** = NAND(A, A)
  - With A=0, NAND(0,0)=1; with A=1, NAND(1,1)=0. It does invert
- **AND** = NOT(NAND(A, B)) = NAND(NAND(A,B), NAND(A,B))
- **OR** = NAND(NOT A, NOT B)
  - By De Morgan's law, ¬(¬A · ¬B) = A + B

> **[Figure 3-2] Building NOT, AND and OR from NAND**
> Three small circuit diagrams stacked vertically. From the top: NOT (the NAND's
> inputs tied together), AND (a NAND followed by a NAND acting as NOT), OR (both
> inputs inverted, then a NAND). A truth table to the right of each circuit lets
> the reader confirm it behaves as expected.

![Figure 3-2 Building NOT, AND and OR from NAND](../figures/fig-03-02.svg)

**Why this matters**: a factory need only mass-produce one kind of part. In
semiconductor manufacturing, the more the same pattern repeats the better the
yield, and inspection and design both become simpler. Inside a real LSI, NAND and
NOR are indeed the leading players.

Another reason NAND is preferred in CMOS is that **NAND takes fewer transistors
than AND**. CMOS naturally produces logic that includes negation, so building an
AND means adding an inverter after a NAND. The AND is the one with more parts.

### The staircase of abstraction

Let us step back and look at what is happening here.

```
Physical phenomena (movement of electrons)
  → Transistors (valves switched on and off by voltage)
    → Logic gates (operations on 0/1)
      → Adders and registers (arithmetic and storage of numbers)
        → Processor (execution of instructions)
          → Programs
```

At each level you can work without knowing the details of the level below. A
logic designer does not think about the behaviour of electrons, and a programmer
does not think about logic gates. **It is this layered structure that makes
computers manageable by human beings.** The same picture appears in every session
from here on.

---

## 3.2 Circuits that compute, circuits that remember

### The half adder

Consider adding one bit. 0+0=0, 0+1=1, 1+0=1, 1+1=10 (that is 2 in binary). Only
the last produces a carry. There are two outputs: the sum S and the carry C.

| A | B | S (sum) | C (carry) |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

The S column is exactly XOR and the C column exactly AND. Therefore

```
S = A ⊕ B
C = A · B
```

Two gates give us one-bit addition. This is the **half adder**.

### The full adder

But adding multi-digit numbers requires adding the carry from the digit below.
Making it three inputs (A, B, and the incoming carry Cin) and two outputs (S,
Cout) gives the **full adder**.

```
S    = A ⊕ B ⊕ Cin
Cout = (A · B) + (Cin · (A ⊕ B))
```

Cout reads as "A and B are both 1" or "one of A and B is 1 and a carry came in
from below".

> **[Figure 3-3] The full adder and a 4-bit adder**
> The upper part shows the inside of a full adder (two half adders and one OR
> gate). The lower part shows four full adders side by side with each stage's Cout
> connected to the next stage's Cin, forming a 4-bit adder. Arrows emphasise the
> carry propagating in order from right to left.

![Figure 3-3 The full adder and a 4-bit adder](../figures/fig-03-03.svg)

Connect n full adders and you have an n-bit adder. As we saw in Lecture 2,
negative numbers are represented in two's complement, so **no subtractor is
needed**. `A − B` can be computed as `A + (¬B) + 1`, which merely means inverting
each bit of B and feeding 1 into the lowest Cin. The adder is used as it stands.

**The carry-propagation problem**: in this arrangement (a ripple-carry adder) the
carry travels in order from the lowest bit to the highest, so 64 bits means 64
stages of delay. Real processors deal with this using circuits that anticipate
the carry (carry look-ahead). "To go faster, add extra circuitry" — another theme
that recurs.

### Circuits that remember: the flip-flop

Every circuit so far changes its output as soon as its input changes
(**combinational circuits**). To remember, you must **feed the output back into
the input**.

The simplest example is the **SR latch**, two NOR gates cross-coupled.

> **[Figure 3-4] The SR latch**
> Two NOR gates one above the other, with the output of the upper wired to an
> input of the lower and the output of the lower to an input of the upper. The
> external inputs S (set) and R (reset) and the outputs Q and ¬Q are drawn. A
> state table notes that S=1 gives Q=1, R=1 gives Q=0, and with S=R=0 **the
> previous state is preserved**.

![Figure 3-4 The SR latch](../figures/fig-03-04.svg)

When S=R=0, if Q is 1 it stays 1, and if 0 it stays 0. **As long as the power is
on, it remembers one bit.** That is what memory really is.

Real circuits use a **D flip-flop**, which adds a clock signal to control when the
value is written. It takes in the input D only at the instant the clock rises, and
holds its value otherwise.

Line up n flip-flops and you have an n-bit **register**. A great many registers
lined up is an SRAM, and that is the cache inside a CPU (Lecture 5).

### The clock

The output of a combinational circuit takes time to settle after its inputs
change (gate delays accumulate). If the next stage reads before it settles, the
circuit misbehaves.

So a periodic signal, the **clock**, is distributed throughout, and we fix the
rule that values are only taken as final on the rising edge of the clock. The
clock period must be long enough for the slowest path in the circuit (the
critical path) to settle.

For a 3 GHz processor one period is 0.33 ns. Light travels only 10 cm in a vacuum
in that time. **The signal cannot reach from one edge of the chip to the other** —
one of the reasons clock frequency cannot simply be raised.

---

## 3.3 The structure of a processor and the execution of instructions

### The von Neumann machine

The arrangement that realises in electronic circuits the universal Turing machine
of Lecture 1 — a machine that receives a rule table as data and interprets and
executes it — is the **von Neumann architecture** (the stored-program design).

> **[Figure 3-5] The structure of a von Neumann machine**
> A rectangle for "main memory" in the centre, drawn as cells with addresses. A
> CPU box on the left, divided into "control unit", "arithmetic logic unit (ALU)"
> and "registers (PC, IR, general purpose)". Main memory and CPU are joined by an
> address bus (CPU→memory), a data bus (bidirectional) and a control bus. I/O
> devices on the right join the same buses. A note — not colour — marks that
> **instructions and data sit side by side in main memory without distinction**.

![Figure 3-5 The structure of a von Neumann machine](../figures/fig-03-05.svg)

The components:

- **Main memory** — a sequence of addressed storage. **Instructions and data are
  held in the same place in the same form**
- **Control unit** — fetches instructions, decodes them, and directs the other parts
- **Arithmetic logic unit (ALU)** — performs arithmetic and logical operations.
  The adder from 3.2 lives here
- **Registers** — a small number of fast stores inside the CPU
  - **Program counter (PC)** — the address of the next instruction to execute
  - **Instruction register (IR)** — the instruction currently executing
  - **General-purpose registers** — temporary holding for the values being operated on
- **I/O devices** — exchange with the outside world (Lecture 8)

The consequences of not distinguishing instructions from data are large. A
program can rewrite itself, and one can write a compiler — a program that takes a
program as input and produces a program as output. On the other hand it also
makes possible attacks that get a region written as data executed as instructions
(buffer overflow). We cover that in Lecture 12.

### The instruction cycle

The CPU repeats the following steps, endlessly.

1. **Fetch** — read the instruction at the address in the PC into the IR, and advance the PC
2. **Decode** — decode the instruction and determine what to do
3. **Execute** — compute in the ALU, read or write memory, or rewrite the PC

> **[Figure 3-6] The instruction cycle**
> A ring: fetch → decode → execute → back to fetch. Beside each stage, the parts
> active at that point (PC, main memory, IR, control unit, ALU, registers) are
> placed small, with arrows showing the flow of data.

![Figure 3-6 The instruction cycle](../figures/fig-03-06.svg)

### A worked example

Suppose the following instructions sit in main memory from address 100 (a
hypothetical instruction set, for exposition).

| Address | Instruction | Meaning |
| ---: | --- | --- |
| 100 | LOAD R1, 200 | Load the value at address 200 into R1 |
| 101 | LOAD R2, 201 | Load the value at address 201 into R2 |
| 102 | ADD R1, R2 | R1 ← R1 + R2 |
| 103 | STORE R1, 202 | Write the value of R1 to address 202 |
| 104 | HALT | Stop |

Suppose address 200 holds 5 and address 201 holds 3.

| Stage | PC | Action | R1 | R2 |
| --- | ---: | --- | ---: | ---: |
| start | 100 | | – | – |
| 1 | 101 | 5 from address 200 into R1 | 5 | – |
| 2 | 102 | 3 from address 201 into R2 | 5 | 3 |
| 3 | 103 | The ALU computes 5+3 into R1 | 8 | 3 |
| 4 | 104 | The 8 in R1 goes to address 202 | 8 | 3 |
| 5 | – | Halt | | |

Five instructions were executed for the single line `c = a + b`.

**What to notice**: all the CPU does is read, compute, write, and advance the PC.
It has the same shape as the Turing machine's read → write → move → change state
from Lecture 1.

### The instruction set architecture

The set of instructions a CPU understands, together with their formats, is the
**ISA** (instruction set architecture). The ISA is **the contract between hardware
and software**. Given the same ISA, the same program runs regardless of how
differently the insides are built.

| ISA | Family | Main uses (as of 2026) |
| --- | --- | --- |
| x86-64 | CISC | PCs, servers |
| Arm (AArch64) | RISC | Smartphones, Apple Silicon, servers |
| RISC-V | RISC | Embedded, research; adoption expanding. Open specification |

- **CISC** (complex instruction set computer) — one instruction does something
  complex. Variable instruction length
- **RISC** (reduced instruction set computer) — instructions are kept simple and
  of fixed length, and the savings go into speed and parallel execution

Modern x86-64 processors internally break CISC instructions into RISC-like
internal operations to execute them. In other words **the ISA as seen from
outside and the implementation inside may be entirely different things**. Again
the abstraction "keep to the contract and the inside is free" is at work.

---

## 3.4 The succession of devices, and Moore's law

### What they have been built from

A logic gate can be built from any valve that switches on and off under voltage.
What that valve has been has changed with the times.

| Device | Period | Size of one | Switching time | Notes |
| --- | --- | --- | --- | --- |
| Relay | 1930s | several cm | ms | Mechanical contacts. Slow, and they wear |
| Vacuum tube | 1940s | ten-odd cm | µs | Hot, and they burn out often |
| Transistor | 1950s | mm | ns | Small, robust, low power |
| Integrated circuit (IC) | 1960s– | many on one chip | ns–ps | Devices and wiring fabricated together |

The decisive one was the **integrated circuit**. Rather than making individual
devices and wiring them together, **the devices and the wiring are printed
together onto a slab of silicon**. Shrinking the devices makes them faster,
cheaper and lower-powered all at once.

### Moore's law

In 1965 Gordon Moore stated that the number of devices integrated on one chip
would double every year, and revised this in 1975 to "double every two years".

This is not a law of physics but **an empirical rule of the industry, and at the
same time a target**. Because the semiconductor industry planned its investment to
match this pace, it came true for more than fifty years.

Doubling every two years means:

| Period | Factor |
| --- | ---: |
| 10 years | 32× |
| 20 years | about 1,000× |
| 40 years | about 1,000,000× |

> **[Figure 3-7] The trend in integration**
> Year (1970–2025) on the horizontal axis, transistor count on a logarithmic
> vertical axis, with points for representative processors showing a straight-line
> rise. Overlaid in a different line style: from around 2005 the **clock frequency**
> curve flattens while the **core count** curve takes off. The data are to be
> produced from published specifications.

![Figure 3-7 The trend in integration](../figures/fig-03-07.svg)

### What a factor of a thousand brings

There is a view that once a quantitative change exceeds a thousandfold it becomes
a qualitative change.

| Subject | 1990s | 2026 | Factor | Qualitative change |
| --- | --- | --- | ---: | --- |
| Computing speed | tens of GFLOPS on a supercomputer | several TFLOPS on a laptop | about 100×+ | Trained models run on your own machine |
| Communication speed | 56 kbps modem | over 1 Gbps on fibre and 5G | about 20,000× | Design now presumes video delivery |
| Secondary storage | 1.44 MB floppy | several TB SSD | about 1,000,000× | "Never delete" becomes the default practice |

By analogy: when travel speed goes from a bicycle (10 km/h) to an aeroplane
(900 km/h), you do not merely arrive sooner — **a whole mode of behaviour, foreign
travel, comes into existence**. A factor of a thousand changes what kinds of
things are possible.

### And what has ended

**The rise in clock frequency stopped around 2005.** The cause is power.

Power consumption in a CMOS circuit is roughly P ∝ C · V² · f (C: capacitance,
V: voltage, f: frequency). Shrinking devices once allowed the voltage to be
lowered at the same time, so raising the frequency did not increase the power
(**Dennard scaling**). But there is a limit to how far the voltage can be lowered,
and it flattened out in the mid-2000s. Since then, raising the frequency raises
power and heat directly.

As a result the industry turned towards **increasing core count rather than
frequency**. This leads into the themes of Lectures 5 and 7 (parallelism, and the
software that has to handle it).

**The situation as of 2026**: shrinking itself is approaching physical limits, and
the "double every two years" pace has slowed. The prevailing directions instead
are these.

- **Chiplets** — package several small chips together rather than one large one
- **3D stacking** — stack vertically rather than laying out flat (stacked memory, 3D NAND)
- **Dedicated circuits** — circuits specialised to a purpose rather than a
  general-purpose CPU (GPUs, neural network accelerators, video codec circuits)

We are moving from an era of "make the general-purpose computer faster" to one of
"put a different circuit on board for each purpose". The fact that the generative
AI of Lecture 13 needs GPUs sits in this context.

---

## Exercises

> **Submission**: through Moodle. For **essay questions**, write out your reasoning
> and working. For **numerical and cloze questions**, enter only the answer (no
> working needed).

**3-1.** Construct an XOR using NAND gates only. Four gates suffice.

**Answer format**: write one gate per line in the form `n1 = NAND(a, b)`. Name
intermediate signals `n1`, `n2`, … and make the left-hand side of the last line
`out`. You may instead draw the diagram by hand and attach a photograph.

**3-2.** Using a 4-bit adder made of four full adders, compute `0110 + 1011`.
Give the Cin, S and Cout of each stage. Does the result fit in four bits?

**Answer format**: write one stage per line, four lines, in the form
`stage 0: Cin=0, S=1, Cout=1`.

**3-3.** What happens in an SR latch when S=1 and R=1? Reason from the truth table
and explain why this input is forbidden.

**3-4.** The speed at which a signal travels through wiring is about 60% of the
speed of light in vacuum (**1.8×10⁸ m/s**).

(a) For a processor with a clock frequency of **5 GHz**, find the distance a
    signal can travel in one period (mm is fine).
(b) Suppose the chip is a square 20 mm on a side. Can a signal reach between
    circuits at opposite ends of the diagonal (about **28 mm**) within one period?
    Compute and answer.
(c) As the frequency rises, (b) eventually fails to hold. Find **the frequency in
    GHz above which** it no longer reaches.

**3-5.** In the worked example of 3.3, `c = a + b` took five instructions. How
many instructions does `d = (a + b) * (a - b)` take in the same instruction set?
Write the instruction sequence and give the count. Assume the following.

- a is at address 200 and b at address 201; the result d is written to address 202
- The general-purpose registers are **R1 to R4, four in all**
- Arithmetic instructions may be used on any two of them (`ADD Rx, Ry` means
  Rx ← Rx + Ry). Multiply `MUL` and subtract `SUB` take the same form
- `HALT` counts as one instruction

**3-6.** Although people say Moore's law has ended, computer performance is still
improving. Name three things that are improving.

---

## Summary

- A logic gate is a circuit performing operations on 0/1. Every logical function
  can be built from NAND alone
- Adders are assembled from XOR and AND. Thanks to two's complement, no
  subtractor is needed
- Feeding the output back to the input produces memory. The flip-flop is the basis
  of registers and memory
- A von Neumann machine holds instructions and data in the same memory. It is the
  implemented form of Lecture 1's universal Turing machine
- A CPU is a machine that does nothing but repeat fetch, decode and execute
- The ISA is the contract between hardware and software. The implementation inside
  is free
- Moore's law is an empirical rule about integration. The rise in clock frequency
  stopped around 2005 at the power wall, and since then it has been the era of
  core counts and dedicated circuits

**Next time**: all a CPU understands is machine code. So how does the Python a
human wrote become machine code?
