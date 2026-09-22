# Lecture 7 — Operating Systems and Processes

> **Question for today** — Why can dozens of programs use one computer at the same time?

*Figure labels are in Japanese; the captions here translate them.*

## Learning goals

- Explain the role of an OS from the two sides of "resource management" and "abstraction"
- Explain the mechanism of privileged mode and system calls
- Explain the difference between processes and threads from the viewpoint of memory space
- Explain the characteristics of the main scheduling policies and what each suits
- Explain file descriptors and pipes, and state what the shell's `|` is doing
- Explain why race conditions and deadlocks occur

## Time allocation

| Minutes | Content |
| --- | --- |
| 0–5 | Review of last time |
| 5–22 | 7.1 What an OS does |
| 22–47 | 7.2 Processes (including file descriptors and pipes) |
| 47–60 | 7.3 Threads and scheduling |
| 60–85 | 7.4 The pitfalls of concurrency |
| 85–90 | Exercises and summary |

---

## 7.1 What an OS does

### Two roles

Boiled down, the work of an OS is these two things.

**(1) Resource management** — apportioning finite resources among several users
and programs

- Which program gets CPU time, and how much
- How main memory is divided
- How storage, network, display and input devices are shared

**(2) Abstraction** — presenting an awkward reality in a form that is easy to handle

| Reality | The abstraction the OS shows |
| --- | --- |
| Storage as a sequence of blocks | Files and directories (Lecture 6) |
| Physically fragmented main memory | A contiguous virtual address space (Lecture 5) |
| Peripherals that differ by model | A uniform interface |
| One CPU | The illusion that each program has a CPU of its own |

**The two are two sides of one coin.** To "appear to have a dedicated CPU", CPU
time has to be switched and apportioned finely; to maintain the abstraction
"file", free blocks have to be managed.

The picture that has recurred throughout this course — "interpose a mapping and
show an illusion" — is used comprehensively in an OS.

### Why operating systems became necessary

Early computers had no OS. Programs operated the machine directly. The problem was
that computers were expensive.

If one person monopolises one computer, the machine idles while that person writes
their program on paper. **In order not to let an expensive resource idle**, a need
arose to pack several jobs into the machine.

```
Serial processing (run one at a time)
  → Batch processing (queue jobs and run them automatically)
    → Multiprogramming (run another while one waits on I/O)
      → Time sharing (TSS) (switch finely so everyone feels they are using it at once)
        → Today (large numbers of users at once, across a network)
```

**The turning point was "waiting for I/O".** While a program waits for a read from
disk, the CPU does nothing. As we saw in Lecture 6, HDD access is 150,000 times
slower than main memory. Run another program during that wait and CPU utilisation
rises dramatically.

Today the price of computers has fallen, but the machinery remains. The reason
changed — it is no longer to keep an expensive resource busy but **because users
want to do many things at once**.

### The kernel and privileged mode

The core of an OS is the **kernel**.

There is a problem. Saying the OS manages the resources is all very well, but
**management does not hold if applications can ignore the OS and touch the
hardware as they please.** Even without malice, a single bug could break other
programs.

So the **CPU is given two modes of operation**.

| Mode | Also called | What it can do |
| --- | --- | --- |
| Privileged mode | kernel mode, ring 0 | Every instruction, all memory, all devices |
| Unprivileged mode | user mode, ring 3 | Restricted instructions, only the memory allocated to it |

Applications run in unprivileged mode. Try to execute an I/O instruction directly
and the hardware refuses. Touch memory not in the page table of Lecture 5 and you
are stopped there.

> **[Figure 7-1] Privileged mode and user mode**
> Two concentric circles: the inner "kernel (privileged mode)", the outer "user
> processes (unprivileged mode)". Hardware resources (CPU, memory, storage,
> devices) are placed inside the inner circle. A single gate, "system call", is
> drawn as the one path from outside to inside, with all other arrows bouncing off
> the circle's wall.

![Figure 7-1 Privileged mode and user mode](../figures/fig-07-01.svg)

### System calls

So how does an application read a file? **It asks the kernel.** The machinery of
that request is the **system call**.

```
1. The application prepares arguments and executes a dedicated instruction
   (the syscall instruction on x86-64)
2. The CPU switches to privileged mode and jumps to a fixed entry point in the kernel
3. The kernel checks the arguments (does this process have that permission?)
4. The kernel performs the actual work
5. It returns to unprivileged mode and back into the application
```

**What matters here is the check at (3).** The structure "there is exactly one
entrance, and everything is checked there" underpins the safety of the whole
system.

The main system calls (Linux as the example):

| Category | Examples |
| --- | --- |
| Files | `open`, `read`, `write`, `close` |
| Processes | `fork`, `execve`, `exit`, `wait` |
| Memory | `mmap`, `brk` |
| Communication | `socket`, `connect`, `send`, `recv` |
| Information | `getpid`, `stat` |

Even the everyday `print("hello")`, traced down, arrives at the `write` system
call.

**System calls are expensive.** Mode switching, saving and restoring registers,
and the effect on the cache make them cost tens to hundreds of times an ordinary
function call. That is why libraries accumulate writes in a buffer and issue them
as a single `write`.

### Examples of operating systems

| Family | Main OSes | Uses |
| --- | --- | --- |
| Unix-like | Linux | Servers, supercomputers, embedded, the base of Android |
| | macOS, iOS | Apple's products (from Darwin/BSD) |
| | FreeBSD, NetBSD | Servers, network equipment |
| Windows | Windows 11, Windows Server | PCs, enterprise systems |
| Mainframe | IBM z/OS | Core systems in finance and government |
| Embedded / RTOS | FreeRTOS, Zephyr, the TRON family | Device control, where response time must be guaranteed |

**Where Linux sits**: servers, cloud, supercomputers (every system in the TOP500),
and the base of Android — it runs more widely than anything else, out of sight.
Knowing the conventions of Linux system calls therefore applies broadly.

---

## 7.2 Processes

### What a process is

A **process** is a program in execution.

A program (an executable file on disk) and a process (the running entity) are
different things. Several processes can be made from the same program. A separate
process running for each browser tab is an example.

What a process holds:

| Element | Content |
| --- | --- |
| An independent address space | The text, data, heap and stack of Lecture 4 |
| Process ID (PID) | An identifying number |
| State | Running / ready / blocked |
| Register contents | PC, general-purpose registers, stack pointer |
| Open files | The file descriptor table |
| Permissions | Owner, group |
| Resource usage | CPU time, memory |

The structure recording all this is the **PCB** (process control block).

**Processes cannot see each other's memory.** The virtual memory of Lecture 5
guarantees this. If one runs amok, the other is unharmed.

### Process state transitions

> **[Figure 7-2] Process state transitions**
> Three states — "ready", "running", "blocked" — drawn as circles and joined by
> arrows. Ready→Running is labelled "dispatch (the scheduler selects it)";
> Running→Ready "time slice expired, pre-empted"; Running→Blocked "I/O request";
> Blocked→Ready "I/O complete". The **absence** of a direct Blocked→Running arrow
> is emphasised (even when the wait ends, one must queue for a turn).

![Figure 7-2 Process state transitions](../figures/fig-07-02.svg)

| State | Meaning |
| --- | --- |
| Running | Currently using the CPU |
| Ready | Able to run, but waiting its turn for the CPU |
| Blocked | Waiting for something such as I/O completion and unable to run |

More processes than there are cores cannot be "running" at once. The rest queue
in the ready list.

### Context switching

Switching the CPU from one process to another is a **context switch**.

```
1. Save all of the current process's registers into its PCB
2. Restore the registers from the next process's PCB
3. Switch the page table (the virtual memory mapping)
4. Resume execution at the instruction the next process's PC points to
```

**This cost is not small.** The direct switching time is a few microseconds, but
what really bites is the indirect effect.

- After switching, the cache (Lecture 5) still holds the previous process's
  contents. The new process misses on almost everything at first (**cache
  pollution**)
- The TLB (the cache of address translations) likewise stops helping

So the switching rate must be tuned to be "not too frequent, not too coarse".

### Creating a process

On Unix-like systems a process is created in two steps.

- **`fork`** — make a copy of yourself. Parent and child end up in nearly identical states
- **`execve`** — replace your own memory space with the specified program

When a shell runs a command, it `fork`s to make a child process, and the child
transforms itself into that command with `execve`. The parent waits for the child
with `wait`.

**Does `fork` copy all of memory?** Done naively it would, but that would be far
too heavy. In practice **copy-on-write** is used. Parent and child share the same
physical pages, marked read-only. Only at the instant one of them tries to write
is that page duplicated.

If they only read, no duplication happens. And when `execve` follows `fork`
immediately, memory that will be thrown away anyway is never copied. The virtual
memory of Lecture 5 is what makes such tricks possible.

### File descriptors and pipes

Let us confirm what all this machinery is good for, with a familiar example.

A Unix-like process starts with **three file descriptors** already open. A file
descriptor is a small integer referring to an open file or channel.

| Number | Name | Default connection |
| ---: | --- | --- |
| 0 | Standard input | Keyboard |
| 1 | Standard output | Screen |
| 2 | Standard error | Screen |

A program does not "write to the screen"; it merely "writes to number 1".
**What number 1 is actually connected to, the program itself does not know.** That
ignorance makes the following trick possible.

What happens when you write this in a shell?

```
% ls -l /usr/include | wc
```

`ls` and `wc` know nothing whatever of each other. Yet the output of `ls` becomes
the input of `wc`. The mechanism is this.

1. The shell creates a one-way channel with the **`pipe`** system call. Two file
   descriptors are returned: a read end and a write end
2. It `fork`s twice, making two child processes
3. In the first child it moves the pipe's write end **onto descriptor 1** with
   **`dup`** (duplicating a descriptor). Then it `execve`s and becomes `ls`
4. In the second child it moves the pipe's read end **onto descriptor 0** and
   `execve`s to become `wc`
5. `ls` "writes to 1" and `wc` "reads from 0" — and that alone joins the two

> **[Figure 7-6] Inter-process communication through a pipe**
> The `ls -l /usr/include` process as a box on top and the `wc` process below,
> each with descriptors 0/1/2 as small cells on its left. A pipe between them is
> drawn as a conduit, with an arrow from `ls`'s descriptor 1 into the pipe's write
> end, and from the pipe's read end into `wc`'s descriptor 0. That `ls`'s
> descriptor 0 remains connected to the keyboard and `wc`'s descriptor 1 to the
> screen is also shown, making clear that only one side was redirected. Beneath the
> figure, the shell's procedure (pipe → fork → dup → execve) appears as four bands.

![Figure 7-6 Inter-process communication through a pipe](../figures/fig-07-06.svg)

**The design at work here**:

- **I/O was abstracted as numbers** (the "everything is a file" of Lecture 8), so
  whether the other end is a keyboard, a file or a pipe, the same `read`/`write`
  suffice
- **`fork` and `execve` were kept separate**, which creates a gap in between for
  redirecting descriptors. If "create a process" and "transform into a program"
  were one operation, this insertion would be impossible

Unix's design became a culture of "combining small tools" because this machinery
is supplied cheaply. Behind the single character `|`, four kinds of system call
are at work.

---

## 7.3 Threads and scheduling

### Threads

Sometimes you want several activities to proceed concurrently within one process —
a browser drawing the screen while communicating and playing video at the same
time.

You could create several processes, but if they handle the same data, **having the
memory separated gets in the way instead**.

So we use **threads**. A thread is **a separately executing flow that shares the
same address space**.

| | Process | Thread |
| --- | --- | --- |
| Address space | Independent for each | **Shared** |
| Stack | One | **One per thread** |
| Registers and PC | One set | **One per thread** |
| Open files | Independent | Shared |
| Cost to create | Heavy | Light |
| Cost to switch | Heavy (includes switching the page table) | Light |
| If one terminates abnormally | The others are unharmed | **The whole process goes down** |
| Ease of sharing data | Requires explicit machinery | **Shared directly (which is also dangerous)** |

> **[Figure 7-3] Memory layout of processes and threads**
> On the left, "three processes" as independent rectangles side by side (each
> containing text/data/heap/stack). On the right, "three threads inside one
> process", with text, data and heap as a single shared region and only the stack
> split into three. Three arrows reaching into the shared region simultaneously
> are emphasised, foreshadowing the discussion of contention in 7.4.

![Figure 7-3 Memory layout of processes and threads](../figures/fig-07-03.svg)

**"Shared directly" is the advantage and the greatest danger both.** That is the
subject of 7.4.

### Scheduling

The **scheduler** chooses which of the ready processes or threads to run next.

What is optimised varies with the use.

| Metric | Meaning | Where it is valued |
| --- | --- | --- |
| Throughput | Completions per unit time | Batch processing |
| Response time | From request to reaction | Interactive use |
| Fairness | No particular one starves | Systems shared by many |
| Meeting deadlines | Finishing by a fixed time | Control systems |

**They cannot all be optimised at once.** Improving response time requires
switching finely, but every switch costs a context switch, and throughput falls.

### The main policies

| Policy | Content | Problem |
| --- | --- | --- |
| FCFS (arrival order) | Run each to completion in the order it arrived | Anything behind a long job waits |
| SJF (shortest job first) | Short jobs first | Execution time is not known in advance. Long jobs starve |
| Round robin | Fixed time slice each, in turn | The length of the slice is hard to set |
| Priority | Highest priority first | Low priority may never run (**starvation**) |
| Multilevel feedback queue | Priority changes dynamically with behaviour | Complex |

Whether **pre-emption** is available matters. Can the CPU be taken by force from a
running process? Without pre-emption, one runaway program freezes the whole system.

Every modern general-purpose OS is pre-emptive, regaining control periodically
through the **timer interrupt** (Lecture 8).

### Priority inversion

The priority approach has a famous pitfall.

1. A low-priority thread L takes a lock on some resource
2. A high-priority thread H requests the same resource and waits for L to release it
3. A **medium-priority** thread M appears. M has higher priority than L, so it
   pre-empts L
4. L does not run, so the lock is not released, and H waits indefinitely

The result is that **the high-priority H loses to the medium-priority M**. The
Mars Pathfinder probe repeatedly rebooting because of this problem in 1997 is a
well-known case.

The countermeasure is **priority inheritance** — while holding a lock, temporarily
inherit the priority of whoever is being made to wait.

---

## 7.4 The pitfalls of concurrency

### Race conditions

Threads share the same memory. That is where the problem arises.

Two threads increment the shared variable `count` by one.

```c
count = count + 1;
```

It looks like one line, but in machine code it becomes three instructions
(Lectures 3 and 4).

```
LOAD  R1, count    ; read the value of count
ADD   R1, 1        ; add one
STORE R1, count    ; write it back
```

Suppose threads A and B execute this with `count` starting at 5. With bad luck it
proceeds as follows.

| Time | Thread A | Thread B | count |
| ---: | --- | --- | ---: |
| 1 | LOAD R1 ← 5 | | 5 |
| 2 | | LOAD R1 ← 5 | 5 |
| 3 | ADD R1 = 6 | | 5 |
| 4 | | ADD R1 = 6 | 5 |
| 5 | STORE 6 | | 6 |
| 6 | | STORE 6 | **6** |

Two increments and yet it is 6, not 7. **One update was lost.**

A state in which **the result changes with the timing of execution** like this is
a **race condition**.

> **[Figure 7-4] The timeline of a race condition**
> Time on the horizontal axis, with LOAD/ADD/STORE boxes placed on two horizontal
> bands (thread A, thread B). The correct case (A's three instructions finish
> before B begins) and the broken case (they interleave) are contrasted in two
> rows. The progression of the shared variable count is added below as a line.

![Figure 7-4 The timeline of a race condition](../figures/fig-07-04.svg)

**Why race conditions are troublesome**:

- They work correctly most of the time. They break only at particular timings
- They do not reproduce under test. They occur only under load, or only in
  production
- Attaching a debugger changes the timing and they stop reproducing

### Mutual exclusion

A section that several threads must not touch at once is a **critical section**.
Arranging that only one thread executes it at a time is **mutual exclusion**.

| Mechanism | Content |
| --- | --- |
| Mutex | Only the one that took the lock proceeds. The others wait |
| Semaphore | Limits the number that may enter at once to n |
| Condition variable | Wait until a condition holds, and be woken when it does |
| Atomic operation | The hardware performs "read then write" indivisibly |

**Atomic operations** are special instructions provided by the CPU.
`compare-and-swap` (indivisibly: rewrite the value if it is as expected) and
others, used to implement locks themselves. The ISA we called "the contract
between hardware and software" in Lecture 3 is the foundation of concurrency here
too.

### Deadlock

Introduce mutual exclusion and a different problem arises.

Thread A holds resource X and waits for Y. Thread B holds resource Y and waits for
X. **Neither ever proceeds.** This is **deadlock**.

> **[Figure 7-5] The resource graph of a deadlock**
> Threads A and B as circles, resources X and Y as squares. Four arrows —
> "A→Y (request)", "Y→B (held)", "B→X (request)", "X→A (held)" — form a ring. The
> existence of this **cycle** is stated to be the deadlock. Beside it, a diagram
> in which the order of acquisition has been unified and the cycle has vanished.

![Figure 7-5 The resource graph of a deadlock](../figures/fig-07-05.svg)

Deadlock requires all four of the following to hold (the Coffman conditions).

1. **Mutual exclusion** — only one thread can use a resource at a time
2. **Hold and wait** — holding a resource while waiting for another
3. **No pre-emption** — a resource cannot be forcibly taken from another thread
4. **Circular wait** — the waiting relation forms a ring

**Break any one of them and deadlock cannot occur.** The most commonly used in
practice is breaking (4).

> **Fix an order on the resources and always acquire them in that order.**

Decide on the order X → Y and B will also try to take X first, so the state "A has
X, B has Y" never arises and no ring forms. It costs nothing but discipline, and
the implementation is simple.

### Modern tools for writing concurrency

Shared memory and locks are hard to get right. So safer abstractions have come
into use.

| Approach | Idea | Examples |
| --- | --- | --- |
| Message passing | Do not share memory; send values to each other | Go channels, Erlang |
| Immutable data | Nothing is rewritten, so nothing contends | The style of functional languages |
| async/await | Write the waits explicitly and confine the switching points | JavaScript, Python, Rust |
| Ownership | The compiler guarantees only one writable reference at a time | Rust |

Go's motto, "Do not communicate by sharing memory; instead, share memory by
communicating", expresses this shift well.

---

## Exercises

> **Submission**: through Moodle. For **essay questions**, write out your reasoning
> and working. For **numerical and cloze questions**, enter only the answer (no
> working needed).

**7-1.** Why are applications prevented from operating the hardware directly? Give
two problems that would arise if they were not.

**7-2.** Why is a system call expensive compared with a function call? Give three
factors.

**7-3.** Explain the difference between processes and threads on the following
points. (a) Memory space (b) Cost of creation and switching (c) The effect when
one terminates abnormally (d) Ease and danger of sharing data

**7-4.** Explain the mechanism by which `fork` avoids copying all of memory. Also
describe a typical usage in which that mechanism is particularly effective.

**7-5.** List, in order, the system calls the shell issues when you run
`cat data.txt | sort | uniq -c` in a shell. Also answer how many pipes are needed.

**7-6.** `ls` and `wc` know nothing of each other, yet `ls | wc` joins them. Give
two design decisions that make this possible.

**7-7.** Two threads A and B each increment a shared variable `count` (initially
10) five times. There is no mutual exclusion. Answer bearing in mind that an
increment divides into three stages, **read → add one → write back** (see the
table in 7.4).

(a) If everything is reflected correctly, what is the final value?

(b) For the execution order below, give the value of `count` **after time 5** and
    **after time 6**. Also answer by how much `count` increased, given that A and
    B each incremented once.

| Time | A | B | count |
| ---: | --- | --- | ---: |
| 1 | read (obtains 10) | | 10 |
| 2 | | read (obtains 10) | 10 |
| 3 | add one (holds 11) | | 10 |
| 4 | | add one (holds 11) | 10 |
| 5 | write back | | ? |
| 6 | | write back | ? |

(c) If the same discrepancy as (b) occurs on all five occasions, what is the final
value?

(In fact it can fall as low as 12 if one side holds an old value for longer still.
Here you need only consider the case where the pattern in (b) repeats.)

**7-8.** State the four conditions for deadlock, and give one concrete way of
breaking each.

**7-9.** Two threads called `withdraw(600)` at the same time on an account with a
balance of 1000, and **both returned `True`, leaving the balance at −200.** Show
after which line another thread must interrupt for this to happen, and describe how
you would fix it.

```python
balance = 1000

def withdraw(amount):
    global balance
    if balance >= amount:            # (1) check the balance
        balance = balance - amount   # (2) withdraw
        return True
    return False
```

---

## Summary

- The roles of an OS are resource management and abstraction, and the two are two
  sides of one coin
- Privileged mode and system calls create a structure of "narrow the entrance to
  one and always check there"
- Processes have independent address spaces and cannot interfere with each other
- I/O is abstracted as numbered file descriptors. Because `fork` and `execve` are
  separate, a gap exists between them in which descriptors can be redirected, and
  inter-process communication by pipe becomes possible
- Threads share an address space. They are light, but dangerous precisely because
  of that sharing
- Scheduling cannot optimise throughput, response time and fairness at once. The
  ability to pre-empt is essential to the stability of the system
- Race conditions are timing-dependent, hard to reproduce, and slip past tests
- Of the four deadlock conditions, breaking circular wait (unifying the order of
  acquisition) is the practical choice

**Next time**: a continuation of how the OS marshals the hardware — how to come to
terms with devices a million times slower than the CPU. And on to virtualisation
and the cloud, which abstract "the computer itself".
