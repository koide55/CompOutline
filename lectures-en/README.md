# An Outline of Computer Systems — English edition

English translation of the lecture notes for the Kyushu University undergraduate
course *An Outline of Computer Systems* (コンピュータシステム通論).

90 minutes × 13 sessions, running as a single thread from the principles of
computation (the Turing machine) to large language models and agentic AI.

**日本語版はこちら → [../README.md](../README.md)**

## The thirteen sessions

| № | Title | Question for today |
| ---: | --- | --- |
| 1 | [What Is Computation?](01-what-is-computation.md) | What does it mean to say something "can be computed"? Are there things that cannot be computed? |
| 2 | [Representing Information, and Computational Complexity](02-information-and-complexity.md) | What do we gain by representing information in binary? And what is a "fast algorithm"? |
| 3 | [From Logic Circuits to the Processor](03-logic-to-processor.md) | How do we build a mathematical model out of electricity? |
| 4 | [How a Program Comes to Run](04-how-programs-run.md) | Why does a string of characters written by a human become the action of a machine? |
| 5 | [The Memory Hierarchy and Parallelism in the Processor](05-memory-hierarchy-and-parallelism.md) | Why is the speed of a computer decided by "waiting for memory"? |
| 6 | [Storage and File Systems](06-storage-and-filesystems.md) | How is data that survives the power being switched off actually laid down? |
| 7 | [Operating Systems and Processes](07-os-and-processes.md) | Why can dozens of programs use one computer at the same time? |
| 8 | [Input/Output, Virtualisation and the Cloud](08-io-virtualization-cloud.md) | How do we come to terms with devices a million times slower than the CPU? |
| 9 | [Fundamentals of Networking](09-network-fundamentals.md) | Why do computers all over the world connect as a single net? |
| 10 | [The Internet and the Web](10-internet-and-web.md) | Over a path that may lose things, how do we exchange anything reliably, and safely, with a party of whom we know only the name? |
| 11 | [Databases and Data Processing](11-databases.md) | How do we accumulate data without breaking it and without contradiction? |
| 12 | [Information Security](12-information-security.md) | How do we trust a party whose face we cannot see? |
| 13 | [From Machine Learning to LLMs and Agentic AI](13-machine-learning-llm-agents.md) | What kind of computation is it when a machine "learns"? |

Each session follows the shape: learning goals → time allocation → body →
exercises → summary. The body carries both the **specification** of each figure (as
a block quote) and **the figure itself** (SVG). The specifications are kept so that
the intent is not lost if a figure is ever redrawn.

## Notes on this translation

- **The figures are shared with the Japanese edition.** All 60 figures
  (`../figures/fig-NN-MM.svg`) carry Japanese labels. The caption above each figure
  translates what it shows, so the notes can be read without reading the figure's
  own text.
- **Identifiers in code examples are in English.** In Lecture 11 in particular, the
  table and column names appear in Japanese in the figures and in English in the
  SQL. The structure is the same.
- **Cross-references are by lecture number**, exactly as in the Japanese edition.
  "Lecture 5" here is the same session as 「第5回」 there.
- **The submission arrangements** described in Lecture 1 (Moodle, weekly portfolio,
  attendance by submission) are those of the course as actually taught.

## The single thread

The same ideas recur through the thirteen sessions in different guises. Lecture 13
gathers them into six:

1. **Abstraction and layering** — each layer works without knowing the one below
2. **Interpose a mapping and show an illusion** — virtual memory, SSD translation, file systems, DNS, NAT, virtualisation
3. **Locality and hierarchical caching** — put what is used often close by, at every scale
4. **Put the cleverness at the endpoints** — TCP's reliability and congestion control
5. **The boundary between data and code** — the power and the peril of the von Neumann architecture, from buffer overflow to prompt injection
6. **Know the limits and work around them** — the halting problem, NP-completeness, Amdahl's law, the CAP theorem

## Source and licence

The Japanese edition under [`../lectures/`](../lectures/) is the source of record.
When the two disagree, the Japanese is authoritative.

All figures are original work; no third-party copyrighted material is included.
