# SKILL.md — Extracted Fact Management

## Purpose

Maintain a structured, serializable fact ledger across a multi-step
implementation task so that extracted facts survive interruptions, user
questions, direction changes, and session gaps without requiring the agent
to re-read source files.

This skill governs three things:
1. **How facts are recorded** as they are extracted during implementation
2. **How the ledger is frozen and thawed** when the user interrupts the task
3. **How the agent resumes** from the correct checkpoint after an interruption

This skill works in direct collaboration with the Lean Markdown Reading skill.
Lean Reading governs what gets read and extracted. This skill governs what
happens to extracted facts after extraction — how they are stored, tracked,
consumed, invalidated, and resumed.

---

## When To Use

Trigger this skill when:
- An implementation task spans more than 3 sequential steps
- The task requires facts extracted from 2+ source files
- There is any realistic chance the user will ask questions mid-task
- The task is expected to take more than one session to complete
- The agent needs to hand off a partially completed task to a fresh context

Do NOT trigger this skill when:
- The task is a single-step question-answer
- No source files are being read (facts are coming entirely from user input)
- The task will complete in one uninterrupted pass under ~20 exchanges

---

## Core Concepts

### The Fact Ledger
A flat, serializable record of all facts extracted during the current task.
Each entry is a fact unit — one discrete piece of extracted information
tied to its source, its step, its status, and its freshness.

The ledger is not a summary. It is not a transcript. It is a structured
store of discrete facts the agent is actively using to execute the task.

### Fact Status
Every fact in the ledger has one of three statuses:

- **PENDING** — extracted but not yet consumed by any implementation step
- **CONSUMED** — used by a completed implementation step
- **STALE** — source file has been flagged as potentially changed, or the
  fact has been superseded by a user correction

### Checkpoint
A named snapshot of the ledger taken at the completion of each
implementation step. Checkpoints are the re-entry points for resumption.
An agent never resumes from mid-step — it always resumes from the last
completed checkpoint.

### Interruption Class
The type of human intervention that paused the task. Determines the
resumption protocol:

- **SOFT** — user asked a question unrelated to the task direction.
  Agent answers, ledger unchanged, resumes from current position.
- **CLARIFY** — user provided new information that refines the task.
  Agent updates relevant PENDING facts, resumes from current checkpoint.
- **REDIRECT** — user changed direction. Agent freezes ledger, surfaces
  the last checkpoint, asks whether to resume from checkpoint or restart.
- **GATE** — user must approve before agent proceeds to next step.
  Agent surfaces the pending action, waits, proceeds or rolls back.

---

## Fact Unit Schema

Each entry in the ledger follows this structure:
```
FACT
  id:          <step-number>-<sequence> (e.g. 2-3 = step 2, third fact)
  source:      <filename> > <section heading>
  content:     <the extracted fact in plain language>
  status:      PENDING | CONSUMED | STALE
  consumed_by: <step name where this fact was used, or null>
  extracted_at: <step number when extracted>
  freshness:   <FRESH | UNVERIFIED>
  notes:       <optional: conflicts, caveats, partial confidence>
```

Freshness starts as FRESH for all newly extracted facts. It is marked
UNVERIFIED if the agent has reason to believe the source file may have
changed since extraction (e.g. the user mentions an edit, or a significant
session gap has occurred).

---

## Checkpoint Schema
```
CHECKPOINT
  name:        <step-name> (e.g. "Step 3 — BiographyScreen scaffold complete")
  step:        <step number>
  timestamp:   <when the checkpoint was taken>
  ledger_snapshot: <all current fact units and their statuses at this moment>
  completed:   <list of steps completed before this checkpoint>
  pending:     <list of steps remaining after this checkpoint>
  open_gaps:   <any declared gaps from re-entry rule that are unresolved>
```

---

## Procedure

### Phase 1 — Ledger Initialization

At the start of a task, before any implementation begins:

1. Create an empty ledger with a task header:
```
   LEDGER
     task:      <one-line task description>
     started:   <step 0>
     source_files: [<list of files in scope>]
     status:    ACTIVE
```

2. Run Lean Markdown Reading to extract facts for Step 1.
   Record each extracted fact as a PENDING fact unit in the ledger
   immediately after extraction — do not wait until the step is complete.

3. Take Checkpoint 0 (the initialized state before any step begins).

### Phase 2 — Per-Step Execution

For each implementation step:

1. **Identify which PENDING facts this step requires.**
   Do not consume facts speculatively — only consume facts the current
   step actively uses.

2. **Execute the step** using only the identified PENDING facts plus
   any facts newly extracted during this step via Lean Reading.

3. **Mark consumed facts.** When a fact is used, update its status
   to CONSUMED and record the step name in `consumed_by`.

4. **Extract forward-looking facts.** If during execution you discover
   a fact needed for a future step, extract it now and add it to the
   ledger as PENDING. Note which future step it is intended for.

5. **Take a checkpoint** when the step is fully complete. Record all
   current fact statuses in the snapshot.

6. **Declare the ledger state** to the user in a brief status line:
```
   ✓ Step 2 complete. Checkpoint saved.
   Ledger: 4 consumed, 3 pending, 0 stale.
   Next: Step 3 — NavigationHeader wiring.
```

### Phase 3 — Interruption Handling

When the user sends a message that is not the next implementation step:

**Step 1 — Classify the interruption.**

Ask internally: does this message change the task direction?
- No change, just a question → SOFT
- New information that refines what to build → CLARIFY
- Different direction entirely → REDIRECT
- Explicit approval request or safety gate → GATE

Do not ask the user to classify their own interruption.
The agent classifies silently and applies the correct protocol.

**Step 2 — Freeze the ledger.**

Before responding to the interruption, record the freeze point:
```
FREEZE
  at_step:       <current step number>
  at_checkpoint: <last completed checkpoint name>
  interruption:  <SOFT | CLARIFY | REDIRECT | GATE>
  trigger:       <one-line summary of what the user said>
```

**Step 3 — Handle by interruption class.**

SOFT:
```
- Answer the user's question fully
- Do not modify the ledger
- After answering, state: "Ready to continue from [checkpoint name]
  when you are."
- Wait for explicit resume signal before proceeding
```

CLARIFY:
```
- Answer or acknowledge the new information
- Identify which PENDING facts in the ledger are affected
- Update those facts (mark old version STALE, add new version as PENDING)
- Note the update in the ledger:
  CLARIFICATION
    step: <current step>
    changed_facts: [<fact IDs updated>]
    reason: <what the user said>
- State: "Updated [N] facts based on your input. Ready to continue
  from [checkpoint name]."
- Wait for explicit resume signal
```

REDIRECT:
```
- Acknowledge the direction change
- Freeze the current ledger completely
- Surface the last checkpoint:
  "I was at [checkpoint name] — [brief description of what was complete].
  Do you want to resume from that point with the new direction,
  or start fresh?"
- Wait for user decision before modifying the ledger further
- If resuming: mark all PENDING facts as STALE, re-extract facts
  relevant to the new direction, update the ledger, take a new checkpoint
- If restarting: archive the current ledger, initialize a new one
```

GATE:
```
- Surface the pending action clearly:
  "Before I proceed to [next step], I want to confirm:
  [description of what the next step will do].
  Proceed?"
- If approved: continue from current checkpoint
- If rejected: freeze at current checkpoint, ask what to do instead
```

### Phase 4 — Resumption

When the user signals they want to continue after an interruption:

1. State the resumption point explicitly:
```
   Resuming from [checkpoint name].
   Completed: [list of done steps]
   Remaining: [list of pending steps]
   Active facts: [N pending, N consumed, N stale]
```

2. If any facts are marked UNVERIFIED (due to session gap or user
   mention of file changes), flag them before proceeding:
```
   ⚠ [N] facts are unverified. Source files may have changed.
   Re-reading [section names] to confirm before continuing.
```
   Then run a targeted Lean Reading re-read on those sections only,
   and update the ledger accordingly.

3. Proceed with the next pending step.

### Phase 5 — Ledger Closure

When all steps are complete:

1. Mark the ledger status as COMPLETE.
2. Produce a final ledger summary:
```
   TASK COMPLETE
   -------------
   Steps completed: [N]
   Facts extracted: [N total]
     Consumed: [N]
     Stale:    [N] (replaced by clarifications)
     Unused:   [N] (extracted but never needed)
   Source files read: [list]
   Checkpoints taken: [N]
   Interruptions handled: [N] ([breakdown by class])
```
3. Note any unused facts — facts that were extracted but never consumed
   by any step. These indicate over-reading during Lean Reading and
   should be flagged as a calibration signal.

---

## Hard Invariants

| ID  | Rule |
|-----|------|
| F-1 | Facts are recorded in the ledger immediately after extraction — never held in working memory only |
| F-2 | No step consumes a fact that has not been recorded in the ledger |
| F-3 | A checkpoint is taken after every completed step — no exceptions |
| F-4 | The ledger is frozen before any interruption response is generated |
| F-5 | Resumption always states the checkpoint explicitly before proceeding |
| F-6 | STALE facts are never used — they must be replaced before the consuming step runs |
| F-7 | REDIRECT interruptions never silently modify the ledger — user must confirm resumption vs restart |
| F-8 | Unused facts at ledger closure are declared, not silently dropped |

---

## Interruption Classification Reference

Use this table when classifying an interruption in Phase 3 Step 1:

| Signal | Class | Example |
|--------|-------|---------|
| Question about something outside the task | SOFT | "What does BM25 stand for?" |
| Question about current task progress | SOFT | "How far along are we?" |
| New constraint that refines the current plan | CLARIFY | "Actually the DatePicker should also accept null" |
| Correction to a previously extracted fact | CLARIFY | "That component path is wrong, it moved to /atoms" |
| New feature added to scope | REDIRECT | "Also add a delete button to the gallery screen" |
| Complete change of task | REDIRECT | "Forget BiographyScreen, let's do the TabBar first" |
| Explicit confirmation request | GATE | "Check with me before writing to any files" |
| Implicit approval gate | GATE | Step involves irreversible action (file write, route registration) |

When a message contains signals from multiple classes, apply the
highest-impact class: REDIRECT > GATE > CLARIFY > SOFT.

---

## Collaboration With Lean Markdown Reading

This skill depends on the Lean Markdown Reading skill for all fact
extraction. The integration points are:

- **Lean Reading produces facts → this skill records them**
  Every fact extracted during a Lean Reading pass is immediately
  entered into the ledger as a PENDING fact unit before any step begins.

- **This skill triggers Lean Reading re-reads**
  When facts are marked UNVERIFIED, this skill instructs Lean Reading
  to re-read the specific sections those facts came from.
  Lean Reading's re-entry rule applies: the gap must be declared
  before the re-read occurs.

- **Unused facts at closure feed back to Lean Reading calibration**
  Unused facts indicate that Lean Reading extracted more than the task
  required. These are reported in the Phase 5 closure summary as a
  signal to tighten future reading passes.

---

## Staleness Rules

A fact becomes STALE under these conditions:

1. The user explicitly corrects it (CLARIFY interruption)
2. The user mentions that a source file has changed
3. A session gap of significant length has occurred and the source
   file is mutable (i.e. it is a plan or spec file, not a stable
   reference)
4. A later step produces output that directly contradicts the fact
5. A REDIRECT interruption causes a plan change that makes the fact
   irrelevant to the new direction

A fact does NOT become stale simply because time has passed. Staleness
requires a concrete trigger, not just age.

---

## Token Efficiency Notes

The ledger itself consumes tokens. Keep it lean:

- Fact content should be a single sentence or a short list — not a
  paragraph reproduction of the source
- Checkpoint ledger snapshots record fact IDs and statuses, not full
  fact content — full content lives in the running ledger only
- When resuming after a long gap, reconstruct only the PENDING facts
  into active context — CONSUMED facts are archived, not re-loaded
- The closure summary is the only time CONSUMED facts are counted
  in aggregate — they are never individually re-surfaced after consumption

---

## Output Contract

At any point during an active task, the agent can produce:

1. **Current ledger state** — all fact units with current statuses
2. **Current checkpoint** — last completed step and snapshot
3. **Freeze record** — the interruption classification and trigger
4. **Resumption statement** — checkpoint, completed steps, remaining steps
5. **Closure summary** — full task statistics at completion

The agent does NOT reproduce source file content in ledger entries.
Facts are the agent's own extracted statements, not quotations.

---

## Refusal Conditions

Do not apply this skill when:
- The user explicitly says they want to start fresh after a REDIRECT —
  archive the ledger and initialize a new one without protest
- The task is abandoned mid-way — produce a partial closure summary
  with all current statuses and stop
- The session context is too far gone to reconstruct a valid checkpoint —
  declare this honestly, produce what ledger state is recoverable,
  and ask the user whether to continue or restart

---

## File Access Constraints

Per AGENTS.md:
- The ledger exists only within the current session and repository scope
- No ledger data is written outside the repository root
- Ledger entries reference only repository-scoped file paths
- All source file references in fact units are repo-relative paths

---

## References

See `references/SOURCES.md` for the principles and implementations
this skill draws from, including LangGraph interrupt/persistence,
OpenAI Agents SDK RunState, and the state management architecture
from real-world LangGraph systems.