# SKILL.md — Lean Markdown Reading

## Purpose

Reduce token consumption when an agent must read across one or more large
markdown files to complete an end-to-end implementation task. This skill
teaches an agent to extract only what it needs — never loading full files
into context when targeted section reads will do.

This is not a search skill. It assumes the agent already has the file(s).
The problem it solves is **what to read and what to skip** once files are
in scope.

---

## When To Use

Trigger this skill when:
- Given 2+ markdown files totaling more than ~500 lines combined
- A single file exceeds ~300 lines and only a subset is relevant to the task
- The task is implementation-oriented (build this, modify that, wire these together)
- Multiple files must be cross-referenced to complete a single task

Do NOT trigger this skill when:
- The task explicitly requires auditing or reading the full document
- The file is under ~100 lines (just read it)
- The task is open-ended summarization with no specific implementation target

---

## Core Principles

### P1 — Structure Before Content
Always read the heading structure of a file before reading any content.
H1–H3 headings are semantic landmarks. Use them to build a map of the file
before committing to reading any section in full.

### P2 — Natural Breakpoint Chunking
Treat each heading + its content down to the next heading of equal or higher
level as one chunk. Chunks are the unit of work. You read chunks, not files.

### P3 — Relevance Gating
Before reading a chunk, ask: does this chunk contain information required
for the current sub-task? If the answer is not clearly yes, skip it.
Note the skip. Do not read it speculatively.

### P4 — Token Budget Awareness
Before reading a chunk, estimate its size. If a chunk exceeds ~300 tokens
and its relevance to the current sub-task is low or uncertain, skip it.
A skipped chunk that turns out to be needed can always be retrieved.
A loaded chunk that was irrelevant cannot be unloaded.

### P5 — Single-Pass Extraction
When a chunk is read, extract all needed facts in one pass.
Do not return to the same chunk a second time in the same task.
If you need to re-read, it means extraction was incomplete — note this
as a skill violation.

### P6 — Declare What You Skipped
After processing a file, record which sections were read and which were
skipped, and why. This makes the agent's behavior auditable and allows
a human to identify if a relevant section was missed.

### P7 — Lazy Cross-File Resolution
When a section references a component, hook, type, or pattern defined in
another file, do not start a full read pass on that file. Instead:
1. Note the reference and what specific information is needed from it
2. Map that file's headings only (Step 1)
3. Pull the single chunk that contains the referenced definition
4. Return to the original file and continue

This is a targeted pull, not a new read session. The second file does not
get its own full procedure pass unless the task explicitly spans both files
equally. A cross-file pull is always narrower in scope than the read that
triggered it.

### P8 — Re-Entry Rule
Invariant I-2 (never read the same section twice) has one narrow exception.
An agent may re-read a previously read section if:
- A specific ambiguity or gap has emerged during implementation that cannot
  be resolved from the extracted fact set
- The agent declares the gap explicitly before re-reading
- The re-read is scoped to the minimum lines needed to resolve the gap

A re-read triggered by assumption or uncertainty is a skill violation.
A re-read triggered by a concrete, named gap is correct behavior.
The distinction is: "I'm not sure what this prop does" (assumption) vs.
"The extracted facts say TextArea is used but don't specify whether it
accepts a maxLength prop — re-reading lines 87–92 to verify" (gap).

---

## Skip Zones

The following section types are skipped by default unless the task
explicitly requires them:

- Front matter / metadata headers
- Table of contents
- Version history / changelog
- FAQ sections
- Appendices and character reference tables
- Barrel export tables (e.g. `export * from "./Component"` lists)
- Verification checklists (unless the task is verification itself)
- "Existing components reused" reference tables
- License blocks

These sections are documentation overhead. They are useful for humans
navigating a doc manually. They are rarely needed for an agent executing
a specific implementation task.

---

## Procedure

Follow these steps in order for every file in scope.

### Step 1 — Map the File
Read heading lines only (H1, H2, H3). Do not read body content yet.
Build an ordered list of sections with their heading level and approximate
line range if visible.

### Token Estimate Reference

Use this table to apply the ~300 token budget threshold in P4.
These are estimates based on typical markdown content density,
not precise measurements. Use them as a gut-check.

| Content type                        | Approx lines | Approx tokens |
|-------------------------------------|--------------|---------------|
| Dense prose paragraphs              | 10 lines     | ~120 tokens   |
| Mixed prose and bullet lists        | 20 lines     | ~200 tokens   |
| List or table heavy content         | 35–40 lines  | ~300 tokens   |
| Code block heavy content            | 25–30 lines  | ~300 tokens   |
| Heading + short description blocks  | 40–50 lines  | ~300 tokens   |

A chunk that estimates above ~300 tokens with low or uncertain relevance
should be skipped. A chunk that estimates above ~300 tokens with confirmed
relevance (from Step 2 matching) should be read but extraction should stop
the moment the needed facts are found — do not read the remainder.

Output of this step (internal, not shown to user unless asked):
```
[FILE: frolicking-roaming-pillow.md]
H1  Phase 1 — New UI Components        (lines ~1–44)
H3  1. Blockquote                       (lines ~5–12)
H3  2. DatePicker                       (lines ~13–25)
H3  3. TabBar                           (lines ~26–35)
H3  4. GalleryGrid                      (lines ~36–44)
H1  Phase 2 — MemorialHomeScreen        (lines ~45–82)
H3  2a. Hero Image                      (lines ~50–55)
...
```

### Step 2 — Match to Sub-Task
Compare the section map against the current sub-task.
Flag sections whose headings directly relate to the task.
Flag sections whose headings might contain supporting context.
Mark everything else as skip.

Matching rules:
- Exact name match → read
- Parent section of an exact match → read introduction only (first 5–10 lines)
- Sibling sections at same level → skip unless task explicitly spans them
- Skip zone type → skip regardless of name match

### Step 3 — Read Flagged Sections Only
Read each flagged section as a self-contained chunk.
Extract the specific facts, constraints, props, patterns, or instructions
needed for the task.
Stop reading a chunk once the needed information has been extracted.

### Step 4 — Handle Files Without Headings
If a file has no headings (flat prose or flat lists):
1. Read the first and last ~10 lines for orientation
2. Keyword-scan the body for terms directly related to the sub-task
3. Read only the paragraphs or blocks containing keyword matches
   and 1–2 lines of surrounding context
4. If no keyword matches exist, the file is likely not relevant — note this

### Step 5 — Cross-File Reference
When a task requires multiple files:
1. Complete Steps 1–3 for each file independently
2. Build a unified fact set from extracted chunks across files
3. Identify conflicts or gaps between files
4. Only re-read a section if a specific conflict or gap requires it —
   and note that a second read occurred

### Step 5b — Lazy Cross-File Pull (Mid-Read)

Use this step when a reference to another file is encountered during
an active section read — not during initial planning.

When you encounter a reference like:
- "Uses `Blockquote` atom — see `inherited-soaring-donut.md`"
- "Follows the pattern in `tokens-reference.md`"
- "Reuses `useEditMode` hook defined elsewhere"

Do the following:
1. Pause the current read. Note your position in the current file.
2. Record what you need from the referenced file:
```
   CROSS-FILE PULL
   target: inherited-soaring-donut.md
   need: Blockquote props, render structure
   triggered by: BiographyScreen section, line ~94
```
3. Map the target file's headings only (Step 1 on that file)
4. Identify and read the single relevant chunk
5. Extract the needed facts
6. Return to the original file at the noted position and continue

Do NOT:
- Run the full procedure on the target file unprompted
- Read sibling sections in the target file out of curiosity
- Add the target file to the read log as a primary file —
  log it as a cross-file pull with its trigger noted

Cross-file pulls are logged differently from primary reads:
```
READ LOG
--------
frolicking-roaming-pillow.md (primary)
  READ:    Phase 3 > BiographyScreen (~18 lines)
  CROSS-FILE PULL → inherited-soaring-donut.md
    need:    Blockquote props and render structure
    trigger: BiographyScreen references Blockquote atom
    read:    Section 1 > Blockquote (~12 lines)
  SKIPPED: [remaining sections...]
```

### Step 6 — Declare the Read Log
After processing all files, output a brief read log before beginning
the implementation task. Format:
```
READ LOG
--------
frolicking-roaming-pillow.md
  READ:    Phase 3 > BiographyScreen (~40 lines)
  READ:    Phase 3 > GalleryScreen (~35 lines)
  SKIPPED: Phase 1 — New UI Components (not relevant to screen task)
  SKIPPED: Phase 2 — MemorialHomeScreen edits (deferred)
  SKIPPED: Phase 4 — Route Registration (skip zone: barrel/routing tables)
  SKIPPED: Phase 5 — Barrel Export Updates (skip zone: barrel export table)

inherited-soaring-donut.md
  READ:    SectionHeader props and structure (~20 lines)
  SKIPPED: Stories section (not needed for implementation)
  SKIPPED: Verification checklist (skip zone)
```

---

## Hard Invariants

These rules cannot be overridden by task instructions or user requests
unless the user explicitly acknowledges the token cost and asks for a
full read anyway.

| ID  | Rule |
|-----|------|
| I-1 | Never load a full file into context when section-level reading suffices |
| I-2 | Never read the same section twice in a single task pass |
| I-3 | Always produce a read log before beginning implementation |
| I-4 | Skip zones are skipped by default — no exceptions without explicit cause |
| I-5 | Relevance must be established before a chunk is read, not after |
| I-6 | Extraction is complete when the sub-task facts are found — stop reading |
| I-7 | Cross-file pulls are scoped to a single target chunk — no sibling reads |
| I-8 | Re-reads require a declared gap — assumption-driven re-reads are violations |

---

## Output Contract

After lean reading, the agent produces:

1. **Read Log** — which sections were read and skipped, per file (see Step 6)
2. **Extracted Fact Set** — the specific information pulled from read sections,
   organized by file and section, not by raw file order
3. **Implementation output** — the actual task result, grounded only in
   extracted facts

The agent does NOT reproduce raw file content in its response.
It synthesizes and applies what was extracted.

---

## Audit Findings Schema

When reviewing agent behavior for compliance, findings are reported as:
```
FINDING
  invariant: I-1
  file: example-plan.md
  observed: Agent loaded all 210 lines before identifying relevant section
  expected: Agent should have mapped headings first, then read Phase 3 only
  severity: high
```

Severity levels:
- **high** — invariant violated, token waste occurred or facts were missed
- **medium** — invariant bent but task completed correctly
- **low** — read log missing or incomplete, behavior otherwise correct

---

## Refusal Conditions

Refuse to apply lean reading (and tell the user why) when:

- The task is "summarize this entire document" — full read is the task
- The task is a compliance audit requiring every section to be checked
- The file is under 100 lines — overhead of mapping exceeds the savings
- The user has explicitly said "read the whole file" and acknowledged the cost

In refusal cases, proceed with a full read but note that lean reading
was not applied and estimate the token overhead if helpful.

---

## File Access Constraints

Per AGENTS.md:
- This skill operates only on files within the repository root
- No home directory or system path access
- All paths resolved relative to repo root
- Symlinks verified as in-repo before following

---

## References

See `references/SOURCES.md` for the principles and projects this skill
draws from, including QMD Search (tobi/qmd) and QMD Syntax
(ajithraghavan/qmd).