# SKILL.md — Implementation Scope Resolution

## Purpose

Determine which files are relevant to an implementation task, in what order
they should be read, and what the dependency chain between them looks like —
before any file content is loaded into context.

This skill is the upstream gate to Lean Markdown Reading. It answers:
- Which files do I need?
- Which files do I definitely not need?
- In what order should they be processed?
- What dependencies exist between them?

Lean Markdown Reading answers how to read those files efficiently once this
skill has identified them. These two skills form a complete pipeline:
```
Task description + file tree
        ↓
Implementation Scope Resolution   ← this skill
        ↓
Ordered, dependency-annotated reading list
        ↓
Lean Markdown Reading
        ↓
Extracted fact set
        ↓
Implementation
```

This skill operates entirely on file names, directory structure, and
heading-level maps. It does not read file body content. Any file that
requires body content to determine relevance is flagged for a lean
heading scan — it is never fully loaded during scope resolution.

---

## When To Use

Trigger this skill when:
- Given a task description and access to a repository or file collection
  with 3 or more files
- The task is implementation-oriented and it is not immediately obvious
  which files are in scope
- Multiple files may contain overlapping or dependent information
- A build order, phase structure, or dependency table exists somewhere
  in the file collection

Do NOT trigger this skill when:
- The file set is 2 or fewer files (just begin lean reading directly)
- The relevant files are explicitly named in the task instruction
  and no dependency resolution is needed
- The task is read-only (summarization, Q&A) with no implementation output

---

## Definitions

**Scope** — the complete set of files whose content is required to complete
the task. Files outside scope are never opened.

**Primary files** — files directly named or clearly implied by the task.
These are always in scope.

**Dependency files** — files referenced by primary files. They enter scope
lazily: only when a primary file read reveals a reference that cannot be
resolved from already-extracted facts.

**Transitive dependencies** — files referenced by dependency files.
These are resolved one level at a time. The agent never pre-loads a full
transitive chain speculatively.

**Exclusion candidates** — files identified during the tree scan as
unlikely to be relevant. These are explicitly listed in the scope
declaration and never opened unless a mid-task reference forces
reconsideration.

**Scope boundary** — the line between in-scope and excluded files.
Crossing the scope boundary requires a declared reason.

---

## Core Principles

### P1 — Tree Before Files
Scan the directory structure and file names before opening any file.
A file's name, path, and location in the tree are often sufficient to
determine relevance without reading its content. Exhaust tree-level
signals before escalating to content-level signals.

### P2 — Two-Pass Relevance
Relevance is determined in two passes:
1. **Name pass** — filename, path, and directory context alone
2. **Heading pass** — H1–H3 headings only, if the name pass is inconclusive

A file that is clearly irrelevant from its name is never opened for a
heading scan. A file that is clearly relevant from its name goes directly
to the reading list without a heading scan. Only ambiguous files need
the heading pass.

### P3 — Explicit Exclusion
Every file in the tree that is not placed in scope must be explicitly
excluded. Exclusions are not silence — they are declarations. An agent
that simply ignores files it did not open has not resolved scope; it has
assumed scope. Assumptions are violations.

### P4 — Dependency Laziness
Dependencies are resolved on demand, not upfront. When scope is first
declared, only primary files are confirmed in scope. Dependency files
enter scope at the moment a primary file read reveals a reference that
needs resolution — not before. This prevents speculative loading of
entire dependency chains.

### P5 — Ordered Output
The output of this skill is not a set — it is an ordered list. Files are
ordered by dependency: files with no dependencies on other in-scope files
come first. Files that depend on earlier files come after. If a build
order or phase structure exists in any in-scope file, it takes precedence
over inferred ordering.

### P6 — Scope Is Declared Before Reading Begins
The scope declaration is produced before Lean Markdown Reading starts.
It is not updated silently mid-task. If a new file needs to enter scope
during implementation, the agent declares a scope amendment with a reason
before opening the file.

---

## File Tree Signals

Use these signals during the name pass (P2) to classify files without
opening them.

### Strong inclusion signals
- Filename directly matches a component, screen, hook, or feature named
  in the task description
- File is in a directory that matches the task domain
  (e.g. task is about screens → `screens/` directory files are candidates)
- Filename contains plan, spec, architecture, or design keywords
  when the task is implementation from a plan
- Filename is referenced by name in the task description itself

### Strong exclusion signals
- Filename indicates infrastructure unrelated to task domain
  (e.g. `jest.config.js`, `babel.config.js` for a UI implementation task)
- File is in a directory clearly outside task domain
  (e.g. `scripts/deploy/` for a component implementation task)
- Filename indicates generated or compiled output
  (e.g. `.lock`, `.map`, `dist/`, `build/`)
- Filename indicates changelog, license, or administrative content

### Ambiguous signals requiring heading pass
- Filename is generic (`utils.md`, `helpers.ts`, `constants.md`)
- File is in a shared directory that serves multiple domains
- Filename partially matches the task domain but the match is uncertain
- File has no extension or an unfamiliar extension

---

## Procedure

### Step 1 — Parse the Task Description
Before touching the file tree, extract from the task description:
```
TASK PARSE
----------
Primary target:    <the thing being built or modified>
Named files:       <any files explicitly mentioned>
Named components:  <components, hooks, screens, or features mentioned>
Domain keywords:   <technical terms that indicate relevant directories>
Explicit excludes: <anything the task says not to touch>
```

This parse drives the name pass. Do not open the file tree until
the task parse is complete.

### Step 2 — Scan the File Tree (Name Pass)
Walk the directory structure. For each file, classify as:
- `IN` — strong inclusion signal, goes to reading list
- `OUT` — strong exclusion signal, goes to exclusion list
- `SCAN` — ambiguous, needs heading pass

Do not open any file during this step. Classification is name-only.

Output format:
```
FILE TREE SCAN
--------------
IN    frolicking-roaming-pillow.md   — plan file, matches primary target
IN    inherited-soaring-donut.md     — plan file, domain match
SCAN  tokens-reference.md            — generic name, domain uncertain
OUT   jest.config.js                 — test infrastructure, out of domain
OUT   CHANGELOG.md                   — administrative, skip zone
```

### Step 3 — Heading Pass on SCAN Files
For each file marked `SCAN`, read headings only (H1–H3).
Reclassify as `IN` or `OUT` based on heading content.

If headings confirm domain relevance → `IN`
If headings are unrelated to task domain → `OUT`
If headings are still ambiguous → `IN` with a note: "low confidence,
  watch for confirmation or disconfirmation during lean read"

### Step 4 — Build the Dependency Graph
For all `IN` files, identify dependency relationships from:
- Explicit references ("see `file.md`", "defined in `component.tsx`")
  found during heading scans
- Directory structure conventions (atoms before molecules before organisms)
- Build order or phase structure sections visible in headings
- Naming conventions (a file named `BiographyScreen` depends on atoms
  it renders — check heading maps for atom names that match task context)

Output format:
```
DEPENDENCY GRAPH
----------------
frolicking-roaming-pillow.md
  └─ depends on: inherited-soaring-donut.md (SectionHeader, MediaGrid)
  └─ depends on: [tokens-reference.md] (uncertain — flagged for lazy pull)

inherited-soaring-donut.md
  └─ no dependencies on other in-scope files
```

### Step 5 — Produce the Ordered Reading List
Topologically sort the dependency graph: files with no in-scope
dependencies first, files that depend on them next.

If a cycle is detected (file A depends on B, B depends on A):
- Flag the cycle explicitly
- Default to alphabetical order within the cycle
- Note that the cycle may indicate a false dependency — verify
  during lean reading

Output format:
```
ORDERED READING LIST
--------------------
1. inherited-soaring-donut.md
   type: primary
   reason: no dependencies on other in-scope files; defines components
           referenced by frolicking-roaming-pillow.md
   expected sections: SectionHeader, MediaGrid definitions

2. frolicking-roaming-pillow.md
   type: primary
   reason: main plan file; depends on inherited-soaring-donut.md
   expected sections: Phase 3 (BiographyScreen), Phase 1 (Blockquote)
   lazy candidates: tokens-reference.md (pull only if token values needed)

EXCLUSION LIST
--------------
- jest.config.js        — test infrastructure
- CHANGELOG.md          — administrative
- tokens-reference.md   — low confidence; excluded from primary pass,
                          available for lazy cross-file pull if needed
```

### Step 6 — Declare the Scope
Produce the final scope declaration before handing off to Lean Markdown
Reading. This declaration is the contract for the implementation task.
```
SCOPE DECLARATION
-----------------
Task:    Implement BiographyScreen read-only and edit modes
Status:  Resolved

In scope (ordered):
  1. inherited-soaring-donut.md   [primary]
  2. frolicking-roaming-pillow.md [primary]

Lazy candidates (open only if referenced during implementation):
  - tokens-reference.md

Excluded:
  - jest.config.js, babel.config.js  [infrastructure]
  - CHANGELOG.md, LICENSE.md         [administrative]

Handoff to: Lean Markdown Reading
  Pass the ordered reading list above as the file sequence.
  Primary sections to target are noted per file in Step 5.
```

---

## Scope Amendment Protocol

If a file outside the declared scope needs to be opened during
implementation, the agent must:

1. Stop the current implementation step
2. Declare the amendment:
```
SCOPE AMENDMENT
---------------
file:    tokens-reference.md
reason:  BiographyScreen edit mode requires specific borderRadius token
         values not present in extracted facts. Lazy candidate promoted
         to in-scope.
action:  Lean cross-file pull — heading map then single section read
```
3. Execute a lean cross-file pull (not a full read)
4. Update the scope declaration with the amendment noted
5. Resume implementation

Amendments are not failures. Undeclared scope expansions are violations.

---

## Hard Invariants

| ID   | Rule |
|------|------|
| I-1  | Tree scan precedes all file opens — no file is opened before Step 2 completes |
| I-2  | Every file in the tree is classified IN, OUT, or SCAN — no silent ignores |
| I-3  | SCAN files get a heading pass before final classification — never left as SCAN |
| I-4  | Dependency graph is built before reading order is determined |
| I-5  | Reading list is ordered by dependency — files with no in-scope deps read first |
| I-6  | Scope declaration is produced before Lean Markdown Reading begins |
| I-7  | Dependency files are resolved lazily — never pre-loaded speculatively |
| I-8  | Scope expansions during implementation require a declared amendment |
| I-9  | Exclusion list is explicit — silence is not exclusion |

---

## Output Contract

This skill produces four artifacts, in order:

1. **Task Parse** — extracted signals from the task description (Step 1)
2. **File Tree Scan** — IN / OUT / SCAN classification for every file (Step 2)
3. **Dependency Graph** — relationships between in-scope files (Step 4)
4. **Scope Declaration** — ordered reading list + exclusion list (Step 6)

These four artifacts are handed to Lean Markdown Reading as its input.
The agent does not begin implementation until the scope declaration exists.

---

## Audit Findings Schema
```
FINDING
  invariant: <I-1 through I-9>
  file:      <filename or "file tree">
  observed:  <what the agent actually did>
  expected:  <what the agent should have done>
  severity:  <high | medium | low>
```

Severity guide:
- **high** — invariant violated, wrong files in scope or relevant files
              excluded, implementation may be incorrect as a result
- **medium** — invariant bent, scope is probably correct but was reached
               through undeclared steps
- **low** — output format incomplete, classification noted but not declared

---

## Refusal Conditions

Refuse to apply this skill (and tell the user why) when:

- Fewer than 3 files exist — overhead exceeds value, begin lean reading
  directly
- All relevant files are explicitly named in the task with no ambiguity —
  skip to scope declaration directly, note that Steps 1–3 were bypassed
- The task is exploratory with no implementation target — scope resolution
  requires a concrete target to drive classification

---

## Relationship to Other Skills

**Lean Markdown Reading** (downstream)
Receives the ordered reading list from this skill's scope declaration.
The two skills are designed to be run in sequence. Do not run Lean
Markdown Reading without a scope declaration unless the file set is
trivially small (2 or fewer files).

**Extracted Fact Management** (downstream of Lean Markdown Reading)
Receives the extracted fact set produced by Lean Markdown Reading.
The scope declaration produced here becomes the provenance record
for the fact ledger — every extracted fact can be traced back to
a file that was explicitly in-scope.

**AGENTS.md constraints**
All file access is repository-scoped. Scope resolution operates only
on files within the repository root. No home directory or system path
access. All paths resolved relative to repo root per AGENTS.md
sections 2 and 3.

---

## References

See `references/SOURCES.md` for the projects and techniques this skill
draws from, including Aider's repomap approach, the Agentless two-stage
localization method, and topological sort as a dependency ordering
primitive.
