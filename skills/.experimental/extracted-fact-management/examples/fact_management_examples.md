# Fact Management Examples

Four examples demonstrating broken, correct, soft interruption, and
redirect behavior. All examples use content from the project files
in this repository.

---

## Example 1 — BROKEN

**Scenario:**
Agent is implementing BiographyScreen across multiple steps. It has
extracted facts from `frolicking-roaming-pillow.md` but does not
maintain a ledger. Mid-implementation, the user asks a question.
The agent answers and then cannot reliably resume.

**Sub-task:**
> "Implement BiographyScreen and wire up its navigation route."

**What the agent did:**
```
[Agent extracts facts from Phase 3 > BiographyScreen and Phase 4]

OK, I'll implement BiographyScreen. It needs a NavigationHeader,
a Blockquote for the quote, a Text for the bio, and edit mode
TextAreas. The path is apps/mobile/src/.../BiographyScreen.js
and the route is MEMORIAL_BIOGRAPHY.

[Agent begins scaffolding BiographyScreen]

[User asks: "Hey quick question — does Blockquote support dark mode?"]

The Blockquote component uses tokens.semantic.interactive.primary
for its border, so it inherits dark mode from the token system
automatically.

[User: "Great, continue please."]

Sure! So for the BiographyScreen... let me think about what we
had. It needed a NavigationHeader and some text display...
```

**Why this is broken:**
```
FINDING
  invariant: F-1
  step: 1
  observed: Facts were extracted and used directly from working memory.
            No ledger was initialized. When the soft interruption
            occurred, all fact context was at risk of being lost or
            misremembered on resumption.
  expected: Ledger initialized before Step 1 began. All extracted
            facts recorded as PENDING units immediately after
            Lean Reading pass.
  severity: high
```
```
FINDING
  invariant: F-3
  step: 1
  observed: No checkpoint was taken after any step. When the user
            asked to resume, the agent had no checkpoint to
            reference — it guessed at what had been completed.
  expected: Checkpoint taken after each completed step. Resumption
            states the checkpoint name explicitly before proceeding.
  severity: high
```
```
FINDING
  invariant: F-5
  step: resumption
  observed: Agent said "let me think about what we had" — indicating
            it was reconstructing task state from conversational
            memory rather than a checkpoint. No checkpoint was
            stated. Steps completed were not declared.
  expected: "Resuming from Checkpoint 1 — BiographyScreen scaffold.
            Completed: Step 1 (scaffold). Remaining: Step 2 (route
            wiring). Active facts: 3 pending, 2 consumed, 0 stale."
  severity: high
```

**Root failure:** No ledger, no checkpoints, no freeze on interruption.
The agent treated the task as a single conversational thread rather
than a managed stateful execution.

---

## Example 2 — CORRECT

**Scenario:**
Same task as Example 1, executed correctly with full ledger management.

**Sub-task:**
> "Implement BiographyScreen and wire up its navigation route."

**Ledger initialization:**
```
LEDGER
  task:         Implement BiographyScreen + route wiring
  started:      Step 0
  source_files: [frolicking-roaming-pillow.md, inherited-soaring-donut.md]
  status:       ACTIVE
```

**Lean Reading pass (Phase 3 > BiographyScreen + Phase 1 > Blockquote
+ Phase 4 > Route intro):**

Facts recorded immediately after extraction:
```
FACT
  id:           0-1
  source:       frolicking-roaming-pillow.md > Phase 3 > BiographyScreen
  content:      File path is apps/mobile/src/features/memorial/screens/BiographyScreen.js
  status:       PENDING
  consumed_by:  null
  extracted_at: 0
  freshness:    FRESH

FACT
  id:           0-2
  source:       frolicking-roaming-pillow.md > Phase 3 > BiographyScreen
  content:      Layout uses NavigationHeader with showBack=true, back label "Profile"
  status:       PENDING
  consumed_by:  null
  extracted_at: 0
  freshness:    FRESH

FACT
  id:           0-3
  source:       frolicking-roaming-pillow.md > Phase 3 > BiographyScreen
  content:      Read-only mode renders Blockquote for quote and Text for full bio
  status:       PENDING
  consumed_by:  null
  extracted_at: 0
  freshness:    FRESH

FACT
  id:           0-4
  source:       frolicking-roaming-pillow.md > Phase 3 > BiographyScreen
  content:      Edit mode uses TextArea for quote (300 char recommended) and TextArea for bio
  status:       PENDING
  consumed_by:  null
  extracted_at: 0
  freshness:    FRESH

FACT
  id:           0-5
  source:       frolicking-roaming-pillow.md > Phase 3 > BiographyScreen
  content:      Mutations: useUpdateMemorialMutation (subtitle) + useUpdateMemorialPersonMutation (bio)
  status:       PENDING
  consumed_by:  null
  extracted_at: 0
  freshness:    FRESH

FACT
  id:           0-6
  source:       frolicking-roaming-pillow.md > Phase 1 > Blockquote
  content:      Blockquote props: children: ReactNode, style? — renders left border accent,
                10% opacity bg, italic text, borderLeftWidth only, top/bottom-right radius
  status:       PENDING
  consumed_by:  null
  extracted_at: 0
  freshness:    FRESH

FACT
  id:           0-7
  source:       frolicking-roaming-pillow.md > Phase 4 (intro)
  content:      Route name: MEMORIAL_BIOGRAPHY = "MemorialBiography", headerShown: false
  status:       PENDING
  consumed_by:  null
  extracted_at: 0
  freshness:    FRESH
```

**Checkpoint 0 taken.**
```
CHECKPOINT
  name:             Step 0 — Ledger initialized
  step:             0
  completed:        []
  pending:          [Step 1 — Scaffold, Step 2 — Route wiring]
  open_gaps:        []
  ledger_snapshot:  0-1 PENDING, 0-2 PENDING, 0-3 PENDING,
                    0-4 PENDING, 0-5 PENDING, 0-6 PENDING, 0-7 PENDING
```

**Step 1 — BiographyScreen scaffold:**

Consumed facts: 0-1 (path), 0-2 (NavigationHeader), 0-3 (read-only
layout), 0-4 (edit mode), 0-5 (mutations), 0-6 (Blockquote props)
```
[Agent writes BiographyScreen.js using only the above facts]
```

Facts updated after step:
```
0-1 → CONSUMED (consumed_by: Step 1 — Scaffold)
0-2 → CONSUMED (consumed_by: Step 1 — Scaffold)
0-3 → CONSUMED (consumed_by: Step 1 — Scaffold)
0-4 → CONSUMED (consumed_by: Step 1 — Scaffold)
0-5 → CONSUMED (consumed_by: Step 1 — Scaffold)
0-6 → CONSUMED (consumed_by: Step 1 — Scaffold)
0-7 → PENDING  (reserved for Step 2)
```

**Checkpoint 1 taken:**
```
CHECKPOINT
  name:             Step 1 — BiographyScreen scaffold complete
  step:             1
  completed:        [Step 1 — Scaffold]
  pending:          [Step 2 — Route wiring]
  open_gaps:        []
  ledger_snapshot:  0-1 CONSUMED, 0-2 CONSUMED, 0-3 CONSUMED,
                    0-4 CONSUMED, 0-5 CONSUMED, 0-6 CONSUMED,
                    0-7 PENDING
```

**Status line declared to user:**
```
✓ Step 1 complete. Checkpoint saved.
Ledger: 6 consumed, 1 pending, 0 stale.
Next: Step 2 — Route wiring (routes.js + MainNavigation.js).
```

**Step 2 — Route wiring:**

Consumed facts: 0-7 (route name and headerShown)
```
[Agent updates routes.js and MainNavigation.js]
```
```
0-7 → CONSUMED (consumed_by: Step 2 — Route wiring)
```

**Checkpoint 2 — Final:**
```
CHECKPOINT
  name:             Step 2 — Route wiring complete
  step:             2
  completed:        [Step 1 — Scaffold, Step 2 — Route wiring]
  pending:          []
  open_gaps:        []
  ledger_snapshot:  0-1..0-7 all CONSUMED
```

**Closure summary:**
```
TASK COMPLETE
-------------
Steps completed:    2
Facts extracted:    7
  Consumed:         7
  Stale:            0
  Unused:           0
Source files read:  frolicking-roaming-pillow.md, inherited-soaring-donut.md
Checkpoints taken:  3 (0, 1, 2)
Interruptions:      0
```

**Self-audit:**
```
SELF-AUDIT CHECKLIST
--------------------
[x] F-1: All facts recorded in ledger immediately after extraction
[x] F-2: All consumed facts existed in ledger before use
[x] F-3: Checkpoint taken after every completed step (0, 1, 2)
[x] F-4: No interruptions occurred — N/A
[x] F-5: No resumptions required — N/A
[x] F-6: No STALE facts — nothing to check
[x] F-7: No REDIRECT — N/A
[x] F-8: Zero unused facts — nothing to declare
```

---

## Example 3 — SOFT INTERRUPTION

**Scenario:**
Agent is mid-implementation on Step 2 (route wiring) when the user
asks an unrelated question. The ledger is at Checkpoint 1.

**State at interruption:**
```
Current checkpoint: Step 1 — BiographyScreen scaffold complete
Active step:        Step 2 — Route wiring (in progress, not complete)
Facts 0-1..0-6:     CONSUMED
Fact 0-7:           PENDING (being used in current step)
```

**User message:**
> "Quick question — what's the difference between Stack.Screen and
> Tab.Screen in React Navigation? Nothing to do with what we're building,
> just curious."

**Interruption classification (silent):**
```
FREEZE
  at_step:       2
  at_checkpoint: Step 1 — BiographyScreen scaffold complete
  interruption:  SOFT
  trigger:       User asked general React Navigation question unrelated
                 to task direction
```

**Agent response:**
```
Stack.Screen is for stack-based navigation where screens push onto
a stack with back button support — this is what BiographyScreen uses.
Tab.Screen is for tab bar navigation where screens are always mounted
and switched between without stack history.

Ready to continue from Step 1 checkpoint (route wiring) when you are.
```

**What happened to the ledger:**
Nothing. Fact 0-7 remains PENDING. No checkpoint was taken because
Step 2 was not complete. The freeze record was noted internally. The
agent did not begin Step 2 outputs during the interruption response.

**User:** "Got it, continue please."

**Resumption:**
```
Resuming from Step 1 — BiographyScreen scaffold complete.
Completed: Step 1 (scaffold)
Remaining: Step 2 (route wiring)
Active facts: 1 pending (0-7 — route name), 6 consumed, 0 stale.

Continuing Step 2 — updating routes.js and MainNavigation.js.
```

**Self-audit for interruption handling:**
```
[x] F-4: Ledger frozen before responding — SOFT freeze recorded
[x] F-5: Resumption stated checkpoint explicitly before proceeding
[x] F-6: No stale facts — SOFT did not modify ledger
[x] F-7: No REDIRECT — N/A
```

**What this example demonstrates:**
SOFT interruptions are the lowest-friction class. The agent answers
fully, declares readiness to resume, and waits. It does not begin
the next step mid-answer, does not modify the ledger, and does not
require the user to re-explain the task on resumption.

---

## Example 4 — REDIRECT INTERRUPTION

**Scenario:**
Agent has completed Step 1 (BiographyScreen scaffold) and is about
to begin Step 2 (route wiring). The user changes direction.

**State at interruption:**
```
Current checkpoint: Step 1 — BiographyScreen scaffold complete
Active step:        Step 2 — about to begin, no output yet
Facts 0-1..0-6:     CONSUMED
Fact 0-7:           PENDING
```

**User message:**
> "Actually, let's pause on BiographyScreen. The design changed —
> the quote section is being removed entirely. Can we switch to
> implementing the GalleryScreen rewrite instead? I'll come back
> to Biography later."

**Interruption classification (silent):**
```
FREEZE
  at_step:       2 (not yet started)
  at_checkpoint: Step 1 — BiographyScreen scaffold complete
  interruption:  REDIRECT
  trigger:       Design change removes quote section; user wants to
                 switch to GalleryScreen implementation task
```

**Agent response (surfaces checkpoint, asks for decision):**
```
Understood — quote section removed, switching focus to GalleryScreen.

I was at Step 1 checkpoint — BiographyScreen scaffold is written
(BiographyScreen.js exists), but route wiring has not been done yet.

Two options:
A) Keep the current BiographyScreen scaffold, pause this task here,
   and start a fresh ledger for GalleryScreen now.
B) Discard the BiographyScreen scaffold and start fresh on
   GalleryScreen with no carried state.

Which do you prefer?
```

**User:** "Option A — keep the scaffold, start fresh on GalleryScreen."

**Ledger actions after user confirmation:**
```
Current ledger → archived as:
  LEDGER (PAUSED)
    task:    Implement BiographyScreen + route wiring
    status:  PAUSED at Step 1 — scaffold complete, route wiring pending
    note:    Design change — quote section removed. Resume requires
             re-extraction of BiographyScreen facts with updated design.
    facts:   0-1..0-6 CONSUMED, 0-7 PENDING (route wiring not done)
```

New ledger initialized:
```
LEDGER
  task:         Implement GalleryScreen rewrite (AlbumsScreen)
  started:      Step 0
  source_files: [frolicking-roaming-pillow.md]
  status:       ACTIVE
```

**Lean Reading pass for GalleryScreen:**
```
[Reads Phase 3 > GalleryScreen Rewrite + Phase 1 > TabBar + GalleryGrid]
[Records new fact units 1-1 through 1-N as PENDING]
```

**Checkpoint 0 for new task taken. Status declared:**
```
✓ New task initialized: GalleryScreen rewrite.
Previous BiographyScreen task paused at Step 1 (scaffold written,
route wiring pending).

GalleryScreen ledger: [N] facts extracted, ready to begin Step 1.
```

**Self-audit for redirect handling:**
```
[x] F-4: Ledger frozen before responding to redirect
[x] F-7: User explicitly confirmed Option A before ledger was modified.
         Ledger was not changed during the interruption response —
         only after user decision was received.
[x] F-1: New ledger initialized with immediate fact recording from
         fresh Lean Reading pass
[x] F-3: Checkpoint 0 taken for new task before Step 1 begins
```

**What this example demonstrates:**
REDIRECT interruptions are the highest-stakes class. The critical
rule is F-7: the ledger is never silently modified during a redirect.
The agent surfaces the last checkpoint, presents options, and waits.
Only after the user has made an explicit decision does the ledger
change. The paused ledger is archived with enough state to resume
later — it is not discarded unless the user explicitly chooses
Option B.