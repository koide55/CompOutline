# Lecture 5 — The Memory Hierarchy and Parallelism in the Processor

> **Question for today** — Why is the speed of a computer decided by "waiting for memory"?

*Figure labels are in Japanese; the captions here translate them.*

## Learning goals

- Explain the difference between SRAM and DRAM from the structure of the cell
- Explain why a memory hierarchy is necessary, from the relationship between speed, capacity and price
- Explain locality of reference and the working of a cache, and compute effective access time from a hit rate
- Explain what problem virtual memory solves
- Explain the differences between pipelining, superscalar execution, multicore and SIMD
- Explain, from properties of the cache, the mechanism by which speculative execution made side-channel attacks possible

## Time allocation

| Minutes | Content |
| --- | --- |
| 0–5 | Review of last time |
| 5–21 | 5.1 Memory devices and the memory hierarchy |
| 21–41 | 5.2 Caches and locality of reference |
| 41–50 | 5.3 Virtual memory |
| 50–85 | 5.4 Parallelism in the processor |
| 85–90 | Exercises and summary |

---

## 5.1 Memory devices and the memory hierarchy

### Fast memory is expensive and small

Recall the latency table from Lecture 2.

| Operation | Time | Scaled so one CPU cycle is one second |
| --- | ---: | --- |
| One CPU cycle | 0.3 ns | 1 second |
| L1 cache reference | 1 ns | 3 seconds |
| Main memory reference | 80 ns | **4 minutes** |

The CPU can execute an instruction every 0.3 ns. But fetching data from main
memory takes 80 ns. **For that whole time the CPU sits idle for 250 cycles.**

You may think "then make all of main memory as fast as L1 cache". There are two
reasons that cannot be done: **price** and **physical distance**.

### SRAM and DRAM

| | SRAM | DRAM |
| --- | --- | --- |
| Composition of one bit | six transistors | one transistor + one capacitor |
| Speed | fast (around 1 ns) | slow (tens of ns) |
| Density | low | high |
| Price (same capacity) | high | low |
| Refresh | not needed | **needed** |
| Use | cache inside the CPU | main memory |

**SRAM** is exactly the flip-flop from last time. The cross-coupled circuit holds
the value continuously, so it is stable as long as there is power. But one bit
takes six transistors.

**DRAM** stores charge in a capacitor to represent 1 or 0. The parts are one
capacitor and one transistor to open and close it. **The area is less than a
sixth of SRAM's**, so many times as much fits in the same area. That is why main
memory is DRAM.

> **[Figure 5-1] An SRAM cell and a DRAM cell**
> On the left an SRAM cell (two cross-coupled inverters with access transistors on
> both sides); on the right a DRAM cell (one transistor and one capacitor). Frames
> at the same scale show how the difference in device count becomes a difference
> in area.

![Figure 5-1 An SRAM cell and a DRAM cell](../figures/fig-05-01.svg)

### DRAM refresh

Charge on a capacitor leaks. Left alone, 0 and 1 become indistinguishable within
tens of milliseconds. So **every bit is periodically read out and written back**.
This is **refresh**.

- That region of memory cannot be accessed during refresh
- It naturally vanishes when the power goes off (**volatile**)
- The D of "dynamic RAM" comes from this dynamic retention behaviour

Another characteristic of DRAM is that **reading is destructive**. Reading the
charge on a capacitor loses the charge, so it must always be written back after
reading. This is one reason DRAM access is slow.

### The memory hierarchy

Memory that is fast, large and cheap cannot be built. So **stack up memories with
different properties**.

| Level | Device | Typical capacity | Speed | Managed by |
| --- | --- | --- | --- | --- |
| Registers | flip-flops | hundreds of bytes | 0.3 ns | the compiler |
| L1 cache | SRAM | tens of KB | 1 ns | hardware |
| L2 cache | SRAM | hundreds of KB – several MB | 4 ns | hardware |
| L3 cache | SRAM | tens of MB | 15 ns | hardware |
| Main memory | DRAM | several GB – hundreds of GB | 80 ns | the OS |
| SSD | flash | hundreds of GB – tens of TB | 20 µs | the OS |
| Over the network | — | effectively unlimited | tens of ms and up | the application |

(The figures are representative orders as of 2026. They change with each
generation, but **the difference in order between levels** does not.)

> **[Figure 5-2] The memory hierarchy pyramid**
> A trapezoid, narrow at the top and wide at the bottom, divided into bands: from
> the top, registers, L1/L2/L3, main memory, SSD, network. On the left an arrow
> marks the axis from "fast, expensive, small" to "slow, cheap, large". Each band
> carries its capacity and speed, emphasising that the order changes with every
> step down.

![Figure 5-2 The memory hierarchy pyramid](../figures/fig-05-02.svg)

**This hierarchy does not work by accident.** It works because program behaviour
has a strong regularity.

---

## 5.2 Caches and locality of reference

### Locality of reference

Watch how a real program reads memory and the accesses are not scattered across
the whole; they **cluster**.

- **Temporal locality** — data used once will be used again soon (loop variables,
  frequently called functions)
- **Spatial locality** — using one datum means data near it will be used too
  (sequential scanning of an array, fields of a struct, the next instruction to
  execute)

This property is called **locality of reference**. It is empirical, but holds
extremely widely.

So we **keep recently used data and its surroundings in a small, fast memory**.
That is the **cache**.

### Cache lines and hit rate

A cache moves data in and out not one byte at a time but in units called **cache
lines** (typically 64 bytes). Because of spatial locality it pays to bring the
neighbourhood along.

- **Hit** — the requested data was in the cache
- **Miss** — it was not, so it is fetched from the level below

**Effective access time**, from hit rate h, cache reference time T_c and main
memory reference time T_m, is

```
T = h · T_c + (1 − h) · T_m
```

Let us compute concretely, with T_c = 1 ns and T_m = 80 ns.

| Hit rate | Effective access time | Ratio to everything hitting the cache |
| ---: | ---: | ---: |
| 100% | 1.0 ns | 1.0× |
| 99% | 1.8 ns | 1.8× |
| 95% | 5.0 ns | 5.0× |
| 90% | 8.9 ns | 8.9× |
| 50% | 40.5 ns | 40.5× |

**Dropping the hit rate from 99% to 95% alone makes it nearly three times
slower.** The effectiveness of a cache is extremely sensitive to small
differences in hit rate.

### Being aware of locality makes code faster

For the same computation, merely changing the order in which memory is touched
changes the speed by a factor of several.

Sum every element of a two-dimensional array. In C, arrays are laid out
**row-major** (elements of the same row are contiguous in memory).

```c
// (a) inner loop over the row — sweeping memory in order
for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++)
        sum += a[i][j];

// (b) inner loop over the column — jumping N elements at a time
for (int j = 0; j < N; j++)
    for (int i = 0; i < N; i++)
        sum += a[i][j];
```

**(a) and (b) produce the same result and perform the same number of additions.**
The complexity of both is O(N²). Yet for large N, (b) is several to more than ten
times slower than (a).

The reason: in (a), once a cache line is fetched, the elements inside it (64 bytes
÷ 8 bytes = 8 of them) can be used consecutively. Misses occur one time in eight.
In (b) a different cache line is touched every time, so **it misses on nearly
every access**.

> **[Figure 5-3] Traversal order and cache lines**
> The two-dimensional array as a grid, with its layout in memory (row-major)
> unrolled beneath the grid as a one-dimensional band. Traversal (a) is shown as
> consecutive arrows along the band; traversal (b) as arrows leaping far across
> it. Cache-line divisions are marked on the band, showing that (a) uses eight
> elements per line while (b) uses only one.

![Figure 5-3 Traversal order and cache lines](../figures/fig-05-03.svg)

**Relation to the complexity of Lecture 2**: big-O notation ignores constant
factors. But the difference between (a) and (b) is exactly that "constant
factor". **Even at the same order, actual speed can differ by an order of
magnitude.** That is what it means to need both theory and implementation.

---

## 5.3 Virtual memory

### What it solves

When writing a program, you do not want to think about the following.

- What other programs have put into main memory
- Whether your program will fit in main memory
- Whether your data can be read by other programs

**Virtual memory** is machinery that shows each process the illusion that it
alone has a vast main memory to itself.

- The addresses a process uses are **virtual addresses**
- The addresses in actual main memory are **physical addresses**
- The OS manages the mapping between them (the **page table**), and the
  translation is performed by hardware (the MMU, memory management unit)

The unit of management is the **page** (typically 4 KB).

> **[Figure 5-4] Translation from virtual to physical addresses**
> Above, the virtual address spaces of two processes as tall boxes side by side;
> below, physical memory as a single box. Arrows run from each process's pages to
> scattered frames in physical memory, showing that contiguous virtual addresses
> need not be physically contiguous. Some pages are not in physical memory, with
> arrows pointing to a swap area on the SSD.

![Figure 5-4 Translation from virtual to physical addresses](../figures/fig-05-04.svg)

### What it gives us

1. **Protection** — without a mapping entry pointing at another process's physical
   page, it cannot be accessed at all. This is the foundation of Lectures 7 and 12
2. **The illusion of contiguity** — though physically scattered, it appears
   contiguous in virtual addresses
3. **Programs larger than main memory** — unused pages can be evacuated to SSD
   (**swapping**, **paging out**)
4. **Sharing** — the physical pages of the same library can be shared among
   several processes

### The price

- Consulting the mapping on every translation is slow, so a cache of the mapping
  itself (the **TLB**, translation lookaside buffer) is provided
- If a needed page is not in main memory a **page fault** occurs and it is read
  from SSD (a stall of tens of thousands of cycles)
- If page replacement happens constantly, computation stops making progress at all
  (**thrashing**)

The experience of "it suddenly got fast after I added memory" is usually
swapping having stopped.

---

## 5.4 Parallelism in the processor

As we saw in Lecture 3, clock frequency stopped rising around 2005. Performance
has kept growing nonetheless, because machines came to **do several things at
once**.

Parallelism has levels.

### (1) Pipelining — parallelism within instructions

Divide instruction execution into five stages — fetch, decode, execute, memory,
write-back — and have **each stage handle a different instruction at the same
time**. The same idea as a factory conveyor belt.

> **[Figure 5-5] Pipeline operation**
> A table with instructions I1–I5 down the side and clock cycles across the top.
> Each instruction passes through the five stages (F/D/E/M/W) offset by one cycle,
> shown as cells arranged in a staircase. An arrow at the right edge emphasises
> that in steady state one instruction completes every cycle.

![Figure 5-5 Pipeline operation](../figures/fig-05-05.svg)

The time taken per instruction (latency) does not change, but **the number
completed per unit time (throughput) becomes five times greater**.

**What disturbs a pipeline (hazards)**:

- **Data hazard** — the next instruction uses the result of the previous one. It
  must wait for the result
- **Control hazard** — a branch instruction. Which instruction to fetch next is
  not determined

The countermeasure for control hazards is **branch prediction**. "This loop's
branch was taken last time and the time before; it will be taken this time too" —
predict, run ahead, and redo it if wrong. The prediction accuracy of modern
processors reaches over 95%.

### The hole speculative execution opened: Spectre and Meltdown

The next move after branch prediction is **speculative execution**. The
instructions in the predicted direction are executed before it is known whether
the prediction was right. If wrong, the results are discarded.

**Only the computed results are discarded.** The state of the cache does not
return. **Spectre and Meltdown**, disclosed in 2018, struck exactly here.

#### How the cache leaks information

As we saw in 5.2, access time differs by an order of magnitude depending on
whether the cache hits or misses (1 ns against 80 ns). Which means:

> **Measure the access time and you learn whether that data was in the cache.**

Information is taken not from the **result** of a computation but from its **side
effects**. This is a **side-channel attack**.

A representative technique is **Flush+Reload**.

| Step | What the attacker does |
| ---: | --- |
| 1 | Evict the address of interest from the cache (flush) |
| 2 | Let the victim's code run |
| 3 | Read again and time it (reload). **If it is fast, the victim touched it** |

#### The skeleton of Spectre

Get branch prediction to leap over a bounds check.

```c
if (i < array1_size)              /* (1) call repeatedly with in-range i,      */
    y = array2[array1[i] * 512];  /*     training the prediction towards "true" */
```

Now pass an out-of-range `i`.

1. Prediction is biased towards "true", so the CPU executes the body without
   waiting for the check
2. It builds an address from `array1[i]` — **a value it should not be able to
   read** — and reads `array2`
3. The check completes and the prediction is found to be wrong. The results are
   cancelled
4. But **that one position in `array2` remains in the cache**
5. If the attacker reads through `array2` in order and times it, they learn which
   position was loaded. **That is the secret value**

> **[Figure 5-6] The side channel of speculative execution: a time difference leaks a secret**
> The upper part contrasts the time taken by the same read as two horizontal bars.
> "Cache hit (about 1 ns)" is a short bar and "miss (about 80 ns)" a long one, so
> the difference in order is obvious at a glance. **That this difference is
> measurable is the starting point.** The lower part is a bar chart with the
> indices 0–15 of `array2` on the horizontal axis and access time on the vertical.
> Most bars are long (misses) and exactly one is extremely short (a hit), with a
> note pointing at that one: "this index is the secret value".

![Figure 5-6 The side channel of speculative execution](../figures/fig-05-06.svg)

**If you can read "only one is fast", one value leaks.** Repeat it and you can
siphon out memory you should not be able to read, one byte at a time.

**Meltdown goes one level deeper.** Where Spectre leaps over a bounds check within
one process, Meltdown crosses **the privilege boundary** to read kernel memory
(anticipating the privileged mode of Lecture 7, this is a read the hardware ought
to reject). The impact was large and countermeasures were needed on the OS side.

#### Why it is hard to fix

**This is not an implementation bug.** Speculative execution is the design for
performance itself, and stopping it makes things much slower. As we saw in Lecture
3, clock frequency stopped around 2005, and every performance gain since has
depended on devices like this.

Every countermeasure pays a price.

| Countermeasure | Price |
| --- | --- |
| Insert speculation-barrier instructions at key points | Those places become slower |
| Separate kernel and user page tables (KPTI) | System calls become heavier |
| Have the compiler avoid dangerous shapes | Less room for optimisation |

#### What to take from this

It is about layers of abstraction. Seen from the program, "cancelled execution"
was supposed not to exist. But a trace of it remained in the layer below (the
cache).

> **Abstraction sometimes leaks the circumstances of the layer below for the sake
> of performance. That leak can become a leak of information.**

There are other attacks that guess secrets by measuring time. If, in a
cryptographic implementation, "the processing time varies with the value of the
key", the key leaks from the time. That is why cryptographic libraries are written
to run in **constant time**. This is one of the situations listed in Lecture 4
under "why being able to read assembly matters".

Attacks that guess keys from power consumption, electromagnetic emissions, or
operating noise are also known. **A computer does things other than computing.**
We return to this in Lecture 12.

### (2) Superscalar — instruction-level parallelism

Have several execution units and **issue instructions with no dependency between
them at the same time**.

```
a = b + c;    ← these two are independent of each other,
d = e * f;    ← so they can execute simultaneously
```

Going further, **out-of-order execution** reorders instructions to execute them.
Even if an earlier instruction is stalled waiting on memory, later independent
instructions are dealt with first. The books are balanced so that results appear
in program order.

### (3) SIMD — data-level parallelism

**One instruction performs the same operation on several data**
(single instruction, multiple data).

```
normal: a[0]+b[0], a[1]+b[1], a[2]+b[2], a[3]+b[3]  … 4 instructions
SIMD:   [a0,a1,a2,a3] + [b0,b1,b2,b3]              … 1 instruction
```

It pays off wherever "the same processing is applied to a great deal of data":
image processing, audio processing, matrix arithmetic. x86's AVX and Arm's NEON
are of this kind.

The **GPU** pushes this idea to an extreme. Where a CPU has "a few clever cores",
a GPU has "thousands to tens of thousands of simple ones". It is poor at complex
processing full of branches, but orders of magnitude faster at applying the same
computation to a great deal of data. The deep learning of Lecture 13 uses GPUs
because its computation is **multiplication of enormous matrices**.

### (4) Multicore — thread-level parallelism

Put several CPU cores on one chip and **execute separate programs (threads)
simultaneously**.

Items (1) to (3) are done by the hardware without being asked, but **multicore
cannot be used unless the person writing the program does something about it**. A
program with only one thread uses only one core even if there are a hundred.

### Amdahl's law

Parallelising does not make things arbitrarily fast. With p the fraction of the
program that can be parallelised and n the number of cores, the overall speed-up
is

```
S = 1 / ((1 − p) + p/n)
```

However large n grows, S never exceeds **1/(1−p)**.

| Fraction parallelisable p | Upper limit as cores go to infinity |
| ---: | ---: |
| 50% | 2× |
| 90% | 10× |
| 95% | 20× |
| 99% | 100× |

> **[Figure 5-7] Amdahl's law**
> Number of cores on a logarithmic horizontal axis (1–1024), speed-up on the
> vertical, with five curves for p = 50%, 75%, 90%, 95%, 99%. All flatten early
> and cling to a horizontal asymptote. The ideal line y = x is overlaid dashed to
> show the divergence from reality.

![Figure 5-7 Amdahl's law](../figures/fig-05-07.svg)

**If 10% remains sequential, lining up a thousand cores gives only a tenfold
speed-up.** This is the fundamental difficulty of parallel computing.

### Why parallel programs are hard

- **Dependencies** — which computation needs the result of which
- **Sharing and contention** — two threads writing the same variable at once
  corrupt it
- **The cost of synchronisation** — waiting for each other itself takes time
- **Deadlock** — each waits forever for a resource the other holds
- **Bugs that do not reproduce** — timing-dependent faults appear and vanish from
  run to run

Dealing with these is the subject of Lecture 7 (processes and threads).

---

## Exercises

> **Submission**: through Moodle. For **essay questions**, write out your reasoning
> and working. For **numerical and cloze questions**, enter only the answer (no
> working needed).

**5-1.** Explain how the difference in per-bit device composition between SRAM and
DRAM bears on "speed" and "density".

**5-2.** A system has a cache reference time of 2 ns and a main memory reference
time of 100 ns. Find the effective access time for hit rates of (a) 98% and
(b) 90%. Also, how many times slower does it get going from (a) to (b)?

**5-3.** For the two loops (a) and (b) in 5.2, take N=1024, 8 bytes per element and
a 64-byte cache line. Estimate how many cache misses occur in each (assume the
cache is too small to hold the whole array).

**5-4.** Name three benefits virtual memory brings, and for each state what would
be troublesome if virtual memory did not exist.

**5-5.** Of a program's execution time, 80% can be parallelised and 20% can only
run sequentially.
(a) What is the speed-up when run on 4 cores?
(b) What is the upper limit as the number of cores goes to infinity?

**5-6.** In a Spectre attack, why does information leak even though the prediction
is wrong and the results of execution are cancelled? State which property of the
cache is used.

**5-7.** Stopping speculative execution entirely would prevent Spectre. Why is
this not regarded as a practical countermeasure? Explain with reference to
Lecture 3.

**5-8.** Why does the claim "double the CPU core count and the processing time
halves" not generally hold? Give two reasons.

---

## Summary

- SRAM is fast but large and expensive; DRAM is cheap and dense but slow and needs refresh
- Memory that is fast, large and cheap cannot be built, so memories with
  different properties are stacked into a hierarchy
- The hierarchy works because programs have locality of reference
- A small drop in hit rate badly damages effective speed. At the same complexity,
  speed can differ by an order of magnitude according to how memory is touched
- Virtual memory brings protection, the illusion of contiguity, expanded capacity
  and sharing
- Parallelism forms a hierarchy of pipelining, superscalar execution, SIMD and
  multicore. The first three are left to hardware, but multicore requires the
  program side to act
- By Amdahl's law, the sequential portion sets the upper limit on speed-up
- Speculative execution can cancel results but cannot cancel traces in the cache.
  Measuring access time reveals whether something was touched (Spectre /
  Meltdown). Abstraction leaks the circumstances of the layer below for the sake
  of performance, and that leak can become a leak of information

**Next time**: memory that does not vanish when the power goes off — into the
world of storage.
