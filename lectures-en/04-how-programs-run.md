# Lecture 4 — How a Program Comes to Run

> **Question for today** — Why does a string of characters written by a human become the action of a machine?

*Figure labels are in Japanese; the captions here translate them.*

## Learning goals

- Explain the relationship between machine code, assembly language and high-level languages
- Explain the difference between compilers and interpreters, and the advantages of each
- Explain each stage from source code to execution (preprocessing, compilation, assembly, linking, loading)
- Explain what virtual machines and JIT compilation solve
- Organise programming languages along axes of classification
- Explain what version control solves
- Explain, from the undecidability of Lecture 1, why testing cannot prove the absence of bugs

## Time allocation

| Minutes | Content |
| --- | --- |
| 0–5 | Review of last time |
| 5–18 | 4.1 Machine code and assembly language |
| 18–34 | 4.2 High-level languages and their implementations |
| 34–52 | 4.3 How an executable is made |
| 52–69 | 4.4 Classifying and choosing languages |
| 69–85 | 4.5 From writing it to confirming it runs |
| 85–90 | Exercises and summary |

---

## 4.1 Machine code and assembly language

### Machine code

As we saw last time, all a CPU can execute are the instructions defined by its
ISA, and in main memory those instructions are **simply binary numbers**. This is
**machine code**.

For instance, the x86-64 instruction "put 5 into register RAX" appears in main
memory as this sequence.

```
48 C7 C0 05 00 00 00
```

Embedded at fixed positions within these seven bytes are "what to do", "which
register", and "what immediate value". The CPU's decoder reads this.

**Can a human write this directly?** Yes. Programmers in the 1950s did exactly
that, writing hexadecimal on paper from an instruction table and entering it with
switches. But there are problems.

- Looking at the numbers tells you nothing about which instruction it is
- Insert one instruction and every subsequent jump address shifts
- Finding mistakes is extremely hard

### Assembly language

So **assembly language** was created by **giving human-readable names (mnemonics)
to the machine instructions**.

```asm
        mov     rax, 5          ; put 5 into RAX
        mov     rbx, 3          ; put 3 into RBX
        add     rax, rbx        ; RAX ← RAX + RBX
        ret                     ; return to the caller
```

Assembly language and machine code correspond **almost one to one**. The program
that converts between them is an **assembler**.

What the assembler does on your behalf:

- Converts mnemonics into instruction codes
- **Converts labels into addresses** — this is the big one. Write `loop_start:`
  and the assembler redoes the address assignment for you when you insert an
  instruction
- Evaluates constants and reserves data areas

> **[Figure 4-1] Correspondence between assembly language and machine code**
> Assembly source (four lines) on the left, the corresponding machine-code bytes
> and addresses on the right, with each line joined by an arrow. On the lines
> containing a label, the replacement of the label by a concrete address is
> emphasised.

![Figure 4-1 Correspondence between assembly language and machine code](../figures/fig-04-01.svg)

### The limits of assembly language

Assembly did not solve everything.

- **It differs by CPU** — code written for x86-64 does not run on Arm
- **The level of abstraction is low** — writing "sum the elements of an array in
  order" takes more than ten lines
- **It does not match the units of human thought** — people think in "totals" and
  "customer lists", not registers

The discussion of complexity in Lecture 2 presupposes algorithms too complex to
write in assembly. We need to raise the level of abstraction one more step.

**Why being able to read assembly still matters**: writing assembly is confined to
a few situations today (OS start-up, interrupt handlers, constant-time
implementations of cryptography, places where performance is pushed to the
limit). But being able to **read** it has value. Checking the result of an
optimisation, analysing a vulnerability, chasing a crash site in a debugger — all
of these mean descending to the machine-code layer.

---

## 4.2 High-level languages and their implementations

### High-level languages

A **high-level language** lets you describe processing in a form close to human
thinking, without depending on a particular CPU. They appeared in the late 1950s.

```c
int sum = 0;
for (int i = 0; i < n; i++) {
    sum += a[i];
}
```

No registers and no addresses appear in this code. And **the same source runs on
x86-64 and on Arm**.

Running a program written in a high-level language requires either translating it
into machine code or interpreting it as it runs. That machinery is the
**language implementation**.

### The compiler approach

A **compiler** translates the whole source into machine code in advance.

```
source ──[compiler]──> machine-code executable ──> execution
            (once, in advance)                 (fast, as often as you like)
```

- **Advantages** — no translation overhead at run time. The whole program can be
  seen and optimised. Type errors and the like are caught before running
- **Disadvantages** — it takes time to get to execution. A separate executable is
  needed per CPU and OS. Fixing one part and trying it requires recompiling

Representative examples: C, C++, Rust, Go

### The interpreter approach

An **interpreter** executes the source while interpreting it line by line.

```
source ──[interpreter reads and executes]──> result
```

- **Advantages** — runs immediately. The write-and-try cycle is fast. With an
  interpreter present, the same source runs in any environment
- **Disadvantages** — slow, since it interprets on every run. Errors are not found
  until run time

Representative examples: plain BASIC, shell scripts

### The virtual machine approach

Between the two lies the **virtual machine** (VM) approach.

```
source ──[compiler]──> intermediate representation (bytecode) ──[VM executes]──> result
```

The intermediate representation is machine code for a virtual CPU that does not
exist. Each environment's VM interprets it.

- You get **both** the optimisation of ahead-of-time compilation and independence
  from the environment
- "Write once, run anywhere"

Representative examples: Java (JVM), C# (.NET), Python (CPython converts to
bytecode internally).

> **[Figure 4-2] Comparing the three approaches**
> Three rows from the top: compiler, interpreter, virtual machine. Each row lays
> out "source", "translator", "intermediate artefact", "executor" and "result"
> horizontally, with a vertical dotted line dividing what happens before execution
> (development time) from what happens at run time. It should be obvious at a
> glance that the dotted line sits in a different place in each of the three.

![Figure 4-2 Comparing the three approaches](../figures/fig-04-02.svg)

### JIT compilation

Even in the VM approach, interpreting bytecode is slower than executing machine
code directly. So **JIT (just-in-time) compilation** is used.

**While running, translate into machine code only the parts that are travelled
often.**

Why is this effective? Most of a program's execution time is concentrated in a
very small part of the code (the inside of a loop, say). Rather than optimising
the whole, **optimising only the hot spots in earnest** is more efficient.

Moreover a JIT has information an ahead-of-time compiler does not. "In this loop,
x was always an integer"; "this branch was almost always taken" — it can optimise
using **facts obtained from actual execution**. If an assumption turns out wrong,
it can fall back to interpretation.

Adopted in: JVM (HotSpot), JavaScript engines (V8), .NET, PyPy.

**In summary**: the classification "compiled languages vs interpreted languages"
makes little sense today. **A single language has several implementations, and a
single implementation combines several approaches.** Python has both CPython
(bytecode plus interpreter) and PyPy (JIT).

---

## 4.3 How an executable is made

Taking C as the example, let us follow the stages from source to execution.

> **[Figure 4-3] The stages of a build**
> Starting from two files `main.c` and `util.c` on the left, flowing rightwards
> through preprocessing → compilation (`.s`) → assembly (`.o`) → linking
> (executable) → loading (a process in memory). Converging arrows show several
> `.o` files and libraries merging into one at the linking stage. Beneath each
> stage, one line describes the transformation that happens there.

![Figure 4-3 The stages of a build](../figures/fig-04-03.svg)

### (1) Preprocessing

Expands `#include`, substitutes `#define`, and handles conditional compilation.
The output is still C source code.

### (2) Compilation

Translates C source into assembly language. This is the main body, and internally
it divides into several stages.

1. **Lexical analysis** — split the character stream into tokens (`int`, `sum`, `=`, `0`, `;`)
2. **Syntactic analysis** — build a syntax tree from the token sequence. If it
   does not fit the grammar, a syntax error
3. **Semantic analysis** — check that types agree and variables are declared
4. **Intermediate representation and optimisation** — in a machine-independent
   form, remove unnecessary computation, transform loops, fold constants
5. **Code generation** — emit assembly for the target CPU. Register allocation
   happens here too

**Examples of optimisation**: `x = 3 * 4;` becomes `x = 12;` at compile time
(constant folding). Computations inside a loop whose value does not change are
moved outside it (loop-invariant code motion). Computations of unused variables
disappear (dead code elimination).

Optimisation is powerful, but constrained by the requirement that **the meaning of
the program must not change**. The C language, however, has "undefined
behaviour", and there the constraint is lifted. Accidents where an optimisation
assuming "signed integers do not overflow" produces a bug originate here.

### (3) Assembly

Converts assembly language into machine code, producing an **object file**
(`.o`). This still cannot be executed, because the addresses of functions defined
in other files (`printf` and so on) have not been fixed.

### (4) Linking

Combines multiple object files and libraries, fills in the previously unresolved
references with actual addresses, and produces the **executable**.

- **Static linking** — the contents of the library are pulled into the executable.
  It runs on its own but grows large. Updating the library requires relinking
- **Dynamic linking** — libraries are loaded at run time. The executable is small,
  and updating a library takes effect across every program. But it will not run if
  the libraries it depends on are absent

Linux `.so`, Windows `.dll` and macOS `.dylib` are dynamic libraries. The classic
error "DLL not found" is a consequence of dynamic linking.

### (5) Loading and execution

The OS reads the executable into main memory, reserves the areas it needs, and
transfers control to the first instruction. From here on we are in the territory
of Lecture 7 (processes).

### The memory layout at run time

A process's memory space is divided roughly as follows.

| Region | Contents | How it is allocated |
| --- | --- | --- |
| Text | The machine-code instructions | Fixed at load time. Normally not writable |
| Data | Global variables with initial values | Fixed at load time |
| BSS | Global variables without initial values | Allocated and zeroed at load time |
| Heap | Regions allocated during execution | Explicitly, via `malloc` and so on. Grows from low addresses |
| Stack | Local variables, return addresses, arguments | Automatically on function call. Grows from high addresses |

> **[Figure 4-4] The memory layout of a process**
> A tall rectangle divided top to bottom, stacking from the bottom (low
> addresses): text, data, BSS, heap (arrow pointing up), … free space …, stack
> (arrow pointing down). The arrows show heap and stack growing towards each
> other. To the right of each region, a note on what is placed there.

![Figure 4-4 The memory layout of a process](../figures/fig-04-04.svg)

**Why it matters to know where a variable lives**:

- Variables on the stack disappear when the function returns. Returning their
  address is a mistake
- Regions on the heap persist until explicitly freed (memory leak)
- The text region is not writable, so writing to it terminates the program abnormally

The buffer overflow attack covered in Lecture 12 writes beyond the capacity of an
array on the stack and **overwrites the return address, which is on the same
stack**, seizing control. Without knowing the memory layout you cannot understand
why that works.

---

## 4.4 Classifying and choosing languages

### The axes of classification

Ranking languages as "good" and "bad" is meaningless. Position them along several
axes instead.

**(1) Method of execution** (as in 4.2) — compiled / interpreted / VM / JIT

**(2) Treatment of types**

| | Description | Examples |
| --- | --- | --- |
| Static typing | Types are fixed and checked at compile time | C, Java, Rust, Go, TypeScript |
| Dynamic typing | Types are determined at run time | Python, JavaScript, Ruby |
| Strong typing | Almost no implicit conversion | Python, Rust |
| Weak typing | Converts implicitly | JavaScript, C |

Static typing finds errors early and favours large-scale development and
optimisation. Dynamic typing is quicker to start writing and suits trial and
error. In recent years there has been a strong movement to add type annotations
retroactively to dynamically typed languages (Python type hints, TypeScript).

**(3) Paradigm**

- **Procedural** — write the steps in order (C, Pascal)
- **Object-oriented** — bundle data with operations (Java, C++, Python)
- **Functional** — build computation from function application, avoiding side
  effects (Haskell, OCaml, Lisp)
- **Logic** — write facts and rules, and the implementation infers (Prolog)

Almost every major modern language **combines several paradigms**. Python can be
written object-oriented, procedural or functional. Rather than classifying "this
language is functional", it is more practical to look at which style can be
written naturally in it.

**(4) Memory management**

| | Description | Examples |
| --- | --- | --- |
| Manual | The programmer writes allocation and release | C |
| Garbage collection | The implementation reclaims unused regions automatically | Java, Python, Go, C# |
| Ownership | Lifetimes are determined at compile time | Rust |

Manual is fast but error-prone (forgetting to free, double free, use after free).
GC is safe but execution pauses while it collects. Rust's ownership is an attempt
to guarantee safety with no run-time cost.

### Representative examples through history

| Language | Year | What it brought |
| --- | ---: | --- |
| FORTRAN | 1957 | The first practical high-level language. Formulae written as they are |
| LISP | 1958 | Functional style, recursion, lists, program = data |
| COBOL | 1959 | For business processing. Close to English. Still running core systems |
| C | 1972 | A high-level language yet close to the machine. Spread with UNIX |
| C++ | 1983 | Object orientation added to C |
| Python | 1991 | Readability above all. Now the standard for scientific computing and AI |
| Java | 1995 | Environment independence through a VM, and GC |
| JavaScript | 1995 | Spread as the only language running in the browser |
| Go | 2009 | Concurrency built into the language. Simplicity prized |
| Rust | 2010 | Memory safety guaranteed without GC |

**Why LISP matters**: a language from 1958, yet it represents programs as lists,
so a program can generate and manipulate programs. It can be seen as carrying
Lecture 1's "a universal Turing machine treats programs as data" into the design
of a language.

### How to choose

The question to ask is not "which language is best" but these three.

1. **Where is the ecosystem for this domain?** — choose the language where the
   libraries and the accumulated knowledge are. Python for machine learning,
   JavaScript/TypeScript for web front ends, C/C++/Rust for embedded work
2. **Where are the performance requirements?** — execution speed is a problem in
   only a small part of the whole. Building first in a language that is easy to
   write and replacing only the slow parts in another language is an ordinary
   arrangement (calling a C extension from Python, for instance)
3. **Who will maintain it?** — will it be readable to whoever reads it in three years?

---

## 4.5 From writing it to confirming it runs

So far we have followed the path by which source code becomes machine code. In
practice there is another loop around it: **write → record → confirm**. Unlike
the story of language implementations, this one is **machinery on the human side**.

### Version control

Source code is not written once and finished. It is corrected, reverted, and
touched by several people at once. A **version control system** handles that
history.

| What it does | Why it is needed |
| --- | --- |
| Keeps a history of changes | "Why was it written this way" can be traced afterwards |
| Returns to any point | You can back out when you break something |
| Merges changes from several people | Nothing is lost when the same file is touched at once |
| Branches for experiments | You can experiment without breaking the main line |

The unit of record is the **commit**. A coherent set of changes is kept as one.
As with the transactions of Lecture 11, the point is **never to record a
half-finished state**.

The mainstream today is **git**, which is **distributed**. Everyone holds a
complete copy of the history, and work continues even if the central server goes
down. The same idea as the packet switching of Lecture 9 — a structure that does
not depend on a centre.

**"When did it break" can be pinned down by binary search.** It does not work now
but it worked a month ago, and there are 100 commits in between. Try the middle
commit: if it works the cause is in the later half, if not, in the earlier.
**Seven tries narrow it to one** (the binary search of Lecture 2; `git bisect`
automates it).

### Testing

**Testing** is the work of confirming that a program behaves as expected.

| Kind | What it confirms |
| --- | --- |
| Unit test | Whether a function or component works correctly on its own |
| Integration test | Whether components work correctly when combined |
| Regression test | **Whether something fixed earlier has broken again** |

**Automation pays off most in regression testing.** A human never checks again
something they have already fixed once. A machine checks every time.

### But testing does not prove the absence of bugs

As stated in Lecture 1.

> By Rice's theorem, every non-trivial property of the input–output behaviour of a
> program is undecidable.

Testing only tries finitely many inputs, so **it says nothing about the inputs it
did not try**. "The tests passed" means "no bug was found", not "there is no bug".

> **Testing can show the presence of bugs, but never their absence.**

**And the three workarounds from Lecture 1 become the tooling of development,
directly.**

| Workaround from Lecture 1 | Corresponding tool | What it is doing |
| --- | --- | --- |
| **Approximate** | Testing, static analysis | Try finitely many inputs. Over-report risky places |
| **Narrow the domain** | Type systems (4.4) | Guarantee only decidable properties, mechanically, for all inputs |
| **Put a human in** | Code review | A person looks at what a machine cannot decide |

**Type checking and testing do not compete.** Types guarantee "an error of a
certain kind is absent" for every input. Tests show "it works correctly on a
particular input". **The kind of guarantee differs, so use both.**

### Continuous integration

Machinery that automatically builds and runs the tests on every commit is called
**continuous integration** (CI).

The aim is single. **Learn early that it broke.**

The longer between breaking and noticing, the more candidate causes there are.
Check on every commit and there is always exactly one candidate, so **you do not
even need the binary search**.

---

## Exercises

> **Submission**: through Moodle. For **essay questions**, write out your reasoning
> and working. For **numerical and cloze questions**, enter only the answer (no
> working needed).

**4-1.** Why can a program written in a high-level language not be executed by the
CPU as it stands? Explain with reference to Lecture 3.

**4-2.** Compare the compiler and interpreter approaches on three points:
(a) execution speed (b) ease of trial and error during development
(c) when errors are found.

**Answer format**: one line per point, in this form.
`(a) Execution speed: the compiler approach … / the interpreter approach …`

**4-3.** Give one reason JIT compilation can beat ahead-of-time compilation.
Include a concrete example of "information available only at run time".

**4-4.** Give one situation in which static linking is advantageous and one in
which dynamic linking is.

**4-5.** The following C function contains an error. Explain what the problem is,
referring to the memory layout table in 4.3.

```c
char *make_message(void) {
    char buf[64];
    sprintf(buf, "hello");
    return buf;
}
```

**4-6.** Rebut the claim "all the tests passed, so this program has no bugs".
Refer to Lecture 1.

**4-7.** A program that worked a month ago does not work now. There are 100
commits in between. At minimum, how many trials are needed to identify the commit
responsible? Describe the method as well.

**4-8.** If you use a statically typed language, are tests unnecessary? Answer
with reference to the difference in what type checking and testing guarantee.

**4-9.** If you were to learn one language over the next year, which would you
choose? Give your reasons following the three questions in 4.4.

---

## Summary

- Machine code is a sequence of binary instructions. Assembly language gives them
  names and corresponds to them almost one to one
- High-level languages allow description close to human thinking, independent of
  the CPU
- Implementations include compilers, interpreters, virtual machines and JIT, and
  modern languages combine several
- From source to execution the stages are preprocessing → compilation → assembly →
  linking → loading
- A process's memory divides into text, data, heap and stack. This layout
  determines both the character of bugs and whether attacks succeed
- Languages are positioned along the axes of execution method, typing, paradigm
  and memory management. The choice is decided by ecosystem, performance
  requirements and maintainability
- Version control handles history and branching. A commit is the unit that "never
  records a half-finished state". "When did it break" can be pinned down by binary
  search (Lecture 2)
- Testing can show the presence of bugs but never their absence (Rice's theorem,
  Lecture 1). The three workarounds of Lecture 1 correspond to testing, type
  systems and review

**Next time**: the program now runs. But it is slow. Why is it slow? The answer
lies not in the CPU but in the memory devices.
