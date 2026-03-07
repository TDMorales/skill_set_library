# SOURCES.md — Implementation Scope Resolution: Reference Origins

## Purpose

Documents the external projects, techniques, and design decisions that
informed the Implementation Scope Resolution skill. Every agent or
maintainer can trace why a specific rule exists back to a concrete source.

---

## Source 1 — Aider Repomap (aider-chat/aider)

**Project:** https://github.com/paul-gauthier/aider  
**Technique:** Repository map for context-efficient code editing  
**Relevance:** Primary inspiration for the two-pass relevance model (P2)
and the tree-before-files principle (P1)

### Principles borrowed

**Repository map as a lightweight index**
Aider constructs a map of the entire repository using ctags — extracting
file names, class names, function signatures, and call relationships —
without loading file body content. This map is fed to the agent instead
of raw source files, dramatically reducing tokens while preserving enough
structural signal to reason about which files are relevant.

The skill's name pass (Step 2) is a direct adaptation: classify files
from their names and paths before opening any of them. The insight is
identical — structural metadata is often sufficient for relevance
decisions, and body content should only be loaded when structural
metadata is inconclusive.

**Graph-based file ranking**
Aider uses a graph ranking algorithm (similar to PageRank) over the
call graph to surface the most relevant files for a given task. Files
that are heavily referenced by other files rank higher. The skill's
dependency graph (Step 4) adapts this: files referenced by primary
files are dependency candidates, and the reference count informs
confidence in the dependency relationship.

**Repomap is regenerated per task**
Aider regenerates its repomap for each editing session rather than
caching a global index. This maps to the skill's P6 (scope is declared
before reading begins, per task) — scope is resolved fresh for each
implementation task, not inherited from a previous session.

### What was not borrowed

Aider's repomap relies on ctags parsing of source code syntax trees.
This skill operates on markdown plan files and documentation, not source
code. The ctags mechanism is replaced by heading-level scanning (H1–H3)
as the structural metadata equivalent. The ranking algorithm is replaced
by explicit dependency declaration, which is more auditable for
prose-based planning documents.

---

## Source 2 — Agentless Two-Stage Localization (UIUC / SWE-bench)

**Paper:** Agentless: Demystifying LLM-based Software Engineering Agents  
**Authors:** Xia et al., University of Illinois Urbana-Champaign  
**Relevance:** Direct model for the two-pass relevance procedure and the
concept of explicit exclusion (P3)

### Principles borrowed

**Localization before repair**
The Agentless framework separates the task of finding relevant files
(localization) from the task of fixing them (repair). Localization runs
first and produces a ranked file list. Repair only operates on that list.
This separation is the foundational design decision behind this skill
existing as a distinct upstream step from Lean Markdown Reading.

**Two-stage localization: file then function**
Agentless localizes in two stages: first to relevant files, then to
relevant functions within those files. The skill adapts this as: first
to relevant files (scope resolution), then to relevant sections within
files (Lean Markdown Reading). The two skills together are a direct
implementation of this two-stage pattern at the documentation level.

**Explicit candidate sets with confidence**
Agentless produces a ranked candidate list with explicit confidence
scores rather than a binary in/out classification. The skill adapts
this as the `SCAN` classification and the "low confidence" flag in
Step 3 — files that are ambiguous are not forced into a binary
classification until a heading scan provides enough signal.

**Exclusion is as important as inclusion**
The Agentless paper notes that false positives (irrelevant files
included in scope) are as damaging as false negatives (relevant files
excluded) because they consume context that could be used for the
actual repair. This directly motivates P3 (Explicit Exclusion) and
I-9 (exclusion list is explicit — silence is not exclusion).

### What was not borrowed

Agentless operates on code repositories with well-defined syntax trees
and test suites that can validate localization decisions. This skill
operates on markdown plan files with no automated validation. The
confidence scoring mechanism is replaced by the three-tier classification
(IN / OUT / SCAN) which is simpler and does not require a scoring model.

---

## Source 3 — Topological Sort as Dependency Ordering

**Concept:** Topological sort (Kahn's algorithm / DFS-based)  
**Context:** Standard computer science algorithm for ordering nodes
in a directed acyclic graph by dependency  
**Relevance:** Foundation for Step 5 (ordered reading list) and I-5
(files with no in-scope dependencies read first)

### Principles borrowed

**Dependency-respecting order**
A topological sort of a dependency graph produces an ordering where
every node appears before the nodes that depend on it. Applied to
file reading: a file that defines components used by another file
should be read before the file that uses those components. This is
exactly what Step 5 produces.

In the project files that motivated this skill:
- `inherited-soaring-donut.md` defines SectionHeader and MediaGrid
- `frolicking-roaming-pillow.md` references those components
- Topological order: `inherited-soaring-donut.md` first

**Cycle detection as a diagnostic signal**
A topological sort fails on cycles. The skill's cycle detection rule
in Step 5 (flag the cycle, default to alphabetical, note possible
false dependency) is drawn from standard topological sort failure
handling. A cycle in a documentation dependency graph usually means
one of the dependency edges was inferred incorrectly — it is a signal
to verify, not a hard error.

**Lazy dependency resolution is compatible with topological order**
Topological sort can be run incrementally: sort the known graph, then
extend as new edges are discovered. This is the basis for P4 (Dependency
Laziness) — the initial sort covers primary files, and lazy additions
are inserted at the correct position when they are discovered.

### What was not borrowed

Full topological sort implementations operate on complete graphs known
upfront. This skill uses a simplified version: primary files are sorted
first, dependency files are inserted lazily as they are discovered.
The full algorithm is not required because the file sets in scope are
small enough that insertion-order reasoning suffices.

---

## Source 4 — Nx / Turborepo Task Dependency Graph Conventions

**Projects:** https://nx.dev, https://turbo.build  
**Relevance:** Conventions for expressing and reading build dependency
graphs that informed the dependency graph output format (Step 4) and
the build order recognition heuristics in P2

### Principles borrowed

**Explicit dependency declaration over inference**
Both Nx and Turborepo require tasks to explicitly declare their
dependencies rather than inferring them from import statements alone.
The skill's I-4 (dependency graph built before reading order determined)
and the explicit dependency graph format in Step 4 follow this convention.
Inferred dependencies are flagged as uncertain; explicit ones (referenced
by name in a plan file) are treated as confirmed.

**Build order sections are authoritative**
Both tools treat the task graph as the authoritative source for execution
order — it overrides any other ordering signal. The skill's Step 5 rule
("if a build order or phase structure exists in any in-scope file, it
takes precedence over inferred ordering") directly reflects this. The
Build Order section in `inherited-soaring-donut.md` is a Turborepo-style
task graph expressed in prose, and the skill treats it as authoritative.

**Tasks vs. artifacts**
Nx distinguishes between tasks (things to run) and artifacts (things
produced). The skill applies this distinction between primary files
(plan files that define what to do) and dependency files (reference
files that define what things are). Primary files drive the task;
dependency files provide the artifact definitions the task depends on.

### What was not borrowed

Nx and Turborepo operate on monorepo package graphs with explicit
`project.json` or `turbo.json` configuration files. This skill operates
on implicit dependency relationships expressed in prose plan documents.
The configuration file mechanism is replaced by heading-level scanning
and explicit reference detection.

---

## Source 5 — Project Context (skill_set_library AGENTS.md)

**Path:** AGENTS.md in the skill_set_library repository  
**Type:** Mandatory policy and skill contract for all skills in this library

### Constraints applied

The repository-scoped execution model and filesystem safety rules from
AGENTS.md sections 2 and 3 are incorporated into SKILL.md's File Access
Constraints section. The skill creation template from AGENTS.md section
1A drove the structure of this file and the examples directory.

---

## Source 6 — Lean Markdown Reading (this library)

**Path:** `lean-markdown-reading/SKILL.md`  
**Type:** Companion skill in this library

### Relationship

Implementation Scope Resolution is the upstream gate to Lean Markdown
Reading. The output contract of this skill (scope declaration + ordered
reading list) is the input contract of Lean Markdown Reading. The two
skills were designed together and their interfaces are intentionally
coupled:

- Scope declaration → Lean Markdown Reading's file sequence
- Exclusion list → Lean Markdown Reading's do-not-open list
- Lazy candidates → Lean Markdown Reading's cross-file pull candidates
- Dependency graph → Lean Markdown Reading's cross-file reference map

The skip zone list in Lean Markdown Reading and the exclusion signal
list in this skill were derived from the same source material and are
intentionally consistent. If one is updated, the other should be
reviewed for alignment.

---

## Pending Research

The following sources were recommended during skill design but had not
been fully reviewed at time of authoring. SOURCES.md should be updated
once these are read:

- SWE-agent file localization techniques (Princeton / SWE-bench)
- Agent context budget allocation literature
- RAG vs full-context tradeoff analysis for agentic coding tasks
- Cursor and Aline context resolution internals (if publicly documented)

Any updates to the skill procedure or invariants that result from
reviewing these sources should be reflected here with the source
credited and the principle borrowed noted explicitly.

---

## Versioning Note

Review this file any time a new classification signal is added to Step 2,
a new invariant is added to SKILL.md, or the dependency graph format
changes. The sources here should always explain why the current rules
exist — if a rule exists with no source, that is a documentation gap.