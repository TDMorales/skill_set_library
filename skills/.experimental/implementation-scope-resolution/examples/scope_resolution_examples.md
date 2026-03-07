# Scope Resolution Examples

Four examples: broken, correct, ambiguous file tree, and cycle detection.
All examples use the actual project files from this repository.

Assumed file tree for all examples:
```
/
├── frolicking-roaming-pillow.md
├── inherited-soaring-donut.md
├── tokens-reference.md
├── CHANGELOG.md
├── jest.config.js
└── babel.config.js
```

---

## Example 1 — BROKEN

**Scenario:**
Agent is asked to implement BiographyScreen and GalleryScreen from the
plan files in the repository.

**Sub-task:**
> "Implement BiographyScreen and the Albums screen rewrite as described
> in the plan files."

**What the agent did:**
```
[Agent opens frolicking-roaming-pillow.md immediately]
[Agent reads all 210 lines]
[Agent opens inherited-soaring-donut.md]
[Agent reads all 88 lines]
[Agent begins implementation]
```

No tree scan. No classification. No dependency graph. No scope declaration.

**Why this is broken:**
```
FINDING
  invariant: I-1
  file:      file tree
  observed:  Agent opened frolicking-roaming-pillow.md before scanning
             the file tree. No name pass was performed.
  expected:  Step 2 file tree scan must complete before any file is opened.
  severity:  high
```
```
FINDING
  invariant: I-2
  file:      file tree
  observed:  tokens-reference.md, CHANGELOG.md, jest.config.js, and
             babel.config.js were never classified. They were silently
             ignored, not explicitly excluded.
  expected:  Every file in the tree must be classified IN, OUT, or SCAN.
             Silence is not exclusion.
  severity:  medium
```
```
FINDING
  invariant: I-6
  file:      file tree
  observed:  No scope declaration was produced. Agent moved directly
             from file reads to implementation.
  expected:  Scope declaration must exist before lean reading begins.
  severity:  high
```

**Consequence:**
The agent loaded 298 lines across two files when the task only required
approximately 75 lines across targeted sections. No record exists of
what was considered and excluded. If a question arises mid-implementation
about whether `tokens-reference.md` was checked, there is no audit trail.

---

## Example 2 — CORRECT

**Scenario:**
Same file tree and sub-task as Example 1.

**Sub-task:**
> "Implement BiographyScreen and the Albums screen rewrite as described
> in the plan files."

**Step 1 — Task Parse:**
```
TASK PARSE
----------
Primary target:    BiographyScreen, Albums screen rewrite (GalleryScreen)
Named files:       none explicitly named
Named components:  BiographyScreen, GalleryScreen, Albums
Domain keywords:   screen, memorial, gallery, biography, React Native
Explicit excludes: none stated
```

**Step 2 — File Tree Scan (name pass):**
```
FILE TREE SCAN
--------------
IN    frolicking-roaming-pillow.md   — plan file, likely contains screen specs
                                       given file collection context
IN    inherited-soaring-donut.md     — plan file, likely contains component
                                       specs referenced by screen plan
SCAN  tokens-reference.md            — generic name, domain uncertain
OUT   CHANGELOG.md                   — administrative, skip zone
OUT   jest.config.js                 — test infrastructure, out of domain
OUT   babel.config.js                — build infrastructure, out of domain
```

**Step 3 — Heading pass on SCAN files:**
```
[READ HEADINGS ONLY: tokens-reference.md]
H1  Design Token Reference
H2  Color Tokens
H2  Spacing Scale
H2  Typography
H2  Border Radius
H2  Elevation

Headings confirm: design token definitions.
BiographyScreen and GalleryScreen both use token values (borderRadius,
interactive.primary). Relevant as a lazy candidate — not needed for
initial implementation but likely needed for specific values.

RECLASSIFY: tokens-reference.md → IN (lazy candidate, low urgency)
```

**Step 4 — Dependency Graph:**
```
DEPENDENCY GRAPH
----------------
frolicking-roaming-pillow.md
  └─ depends on: inherited-soaring-donut.md
       reason: Phase 1 defines Blockquote, TabBar, GalleryGrid atoms/organisms
               referenced by Phase 3 screen implementations
  └─ lazy candidate: tokens-reference.md
       reason: screen components use token values; specific values may be
               needed during implementation but not confirmed yet

inherited-soaring-donut.md
  └─ no dependencies on other in-scope files
     (depends on Thumbnail, Link, Card atoms — but those are source files,
      not plan files, so they are outside this skill's scope boundary)

tokens-reference.md
  └─ no dependencies on other in-scope files
```

**Step 5 — Ordered Reading List:**
```
ORDERED READING LIST
--------------------
1. inherited-soaring-donut.md
   type:             primary
   reason:           no in-scope dependencies; defines components
                     referenced by frolicking-roaming-pillow.md
   expected sections: SectionHeader, MediaGrid (may be relevant to
                      GalleryScreen / Albums rewrite)

2. frolicking-roaming-pillow.md
   type:             primary
   reason:           main plan file; depends on inherited-soaring-donut.md
   expected sections: Phase 3 > BiographyScreen,
                      Phase 3 > GalleryScreen Rewrite,
                      Phase 1 > Blockquote (cross-ref from BiographyScreen)

LAZY CANDIDATES (open only if referenced during implementation):
  - tokens-reference.md
    trigger condition: implementation requires specific token values
                       not available in extracted facts

EXCLUSION LIST
--------------
- CHANGELOG.md      — administrative, skip zone
- jest.config.js    — test infrastructure
- babel.config.js   — build infrastructure
```

**Step 6 — Scope Declaration:**
```
SCOPE DECLARATION
-----------------
Task:    Implement BiographyScreen and Albums screen rewrite
Status:  Resolved

In scope (ordered):
  1. inherited-soaring-donut.md   [primary — no deps]
  2. frolicking-roaming-pillow.md [primary — depends on #1]

Lazy candidates:
  - tokens-reference.md           [open only if token values needed]

Excluded:
  - CHANGELOG.md                  [administrative]
  - jest.config.js                [infrastructure]
  - babel.config.js               [infrastructure]

Handoff to: Lean Markdown Reading
  Begin with inherited-soaring-donut.md.
  Target: SectionHeader and MediaGrid sections.
  Then frolicking-roaming-pillow.md.
  Target: Phase 3 screens, Phase 1 Blockquote.
```

**Self-audit:**
```
SELF-AUDIT CHECKLIST
--------------------
[x] I-1: File tree scanned before any file opened — heading scan on
         tokens-reference.md was the first file access, after name pass
[x] I-2: All 6 files classified: 3 IN (2 primary + 1 lazy), 3 OUT
[x] I-3: tokens-reference.md resolved from SCAN to IN(lazy) via heading pass
[x] I-4: Dependency graph built (Step 4) before reading order (Step 5)
[x] I-5: inherited-soaring-donut.md (no deps) listed before
         frolicking-roaming-pillow.md (depends on it)
[x] I-6: Scope declaration produced before lean reading begins
[x] I-7: tokens-reference.md kept as lazy candidate — not pre-loaded
[x] I-8: No mid-task scope expansions occurred during resolution
[x] I-9: Exclusion list names all 3 excluded files explicitly
```

All invariants satisfied. Handing off to Lean Markdown Reading.

---

## Example 3 — AMBIGUOUS TREE (Edge Case: Flat Generic Names)

**Scenario:**
Agent is working in a repository where all markdown files have generic
names and the directory structure provides no domain signal.
```
/docs
├── plan-a.md
├── plan-b.md
├── reference-1.md
├── reference-2.md
└── notes.md
```

**Sub-task:**
> "Implement the TabBar component as described in the docs."

**Step 1 — Task Parse:**
```
TASK PARSE
----------
Primary target:    TabBar component
Named files:       none
Named components:  TabBar
Domain keywords:   tab, bar, navigation, component, organism
Explicit excludes: none
```

**Step 2 — File Tree Scan (name pass):**
```
FILE TREE SCAN
--------------
SCAN  plan-a.md       — generic name, content unknown
SCAN  plan-b.md       — generic name, content unknown
SCAN  reference-1.md  — generic name, content unknown
SCAN  reference-2.md  — generic name, content unknown
SCAN  notes.md        — generic name, content unknown
```

All files are SCAN. Name pass is inconclusive across the board.
Proceed immediately to Step 3 for all files.

**Step 3 — Heading pass on all SCAN files:**
```
[READ HEADINGS ONLY: plan-a.md]
H1  Edit Mode Integration — Phase 1
H2  Phase 1 — New UI Components
H3    TabBar (organism)       ← direct match
H3    Blockquote, DatePicker, GalleryGrid
H2  Phase 2 — MemorialHomeScreen Edit Affordances
RECLASSIFY: plan-a.md → IN (primary — contains TabBar spec)

[READ HEADINGS ONLY: plan-b.md]
H1  Plan: SectionHeader + MediaGrid Components
H2  SectionHeader (Molecule)
H2  MediaGrid (Organism)
H2  Implementation Order
No TabBar reference. Domain is UI components — adjacent but not primary.
RECLASSIFY: plan-b.md → IN (lazy candidate — may define patterns TabBar follows)

[READ HEADINGS ONLY: reference-1.md]
H1  Design Token Reference
H2  Color Tokens, Spacing, Typography, Border Radius
RECLASSIFY: reference-1.md → IN (lazy candidate — token values for TabBar)

[READ HEADINGS ONLY: reference-2.md]
H1  API Endpoint Reference
H2  Authentication, Users, Memorials, Media
No UI relevance.
RECLASSIFY: reference-2.md → OUT (API docs, outside UI component domain)

[READ HEADINGS ONLY: notes.md]
H1  Meeting Notes — Q3 Planning
H2  Roadmap discussion, team assignments
RECLASSIFY: notes.md → OUT (planning notes, no implementation content)
```

**Note on ambiguous trees:**
When all files require a heading scan, the heading pass becomes the
primary classification mechanism rather than a fallback. This is more
expensive (5 heading reads vs. 0 in Example 2) but still far cheaper
than loading full file content. The invariants hold — no body content
was loaded during scope resolution.

**Resulting scope declaration:**
```
SCOPE DECLARATION
-----------------
Task:    Implement TabBar component
Status:  Resolved (via full heading pass — flat file tree)

In scope (ordered):
  1. plan-b.md      [lazy candidate — component pattern reference]
  2. plan-a.md      [primary — contains TabBar spec; depends on patterns
                     from plan-b.md if organism conventions are consistent]

Lazy candidates:
  - reference-1.md  [token values if needed during implementation]

Excluded:
  - reference-2.md  [API docs, no UI relevance]
  - notes.md        [meeting notes, no implementation content]

Note: Full heading pass was required due to flat generic file tree.
      5 heading reads performed during scope resolution.
      No body content loaded.
```

---

## Example 4 — CYCLE DETECTION (Edge Case)

**Scenario:**
During dependency graph construction, the agent detects what appears
to be a circular dependency between two plan files.

**Observed during Step 4:**
```
DEPENDENCY GRAPH (initial pass)
--------------------------------
screen-plan.md
  └─ depends on: component-plan.md
       reason: references Blockquote, TabBar defined in component-plan

component-plan.md
  └─ depends on: screen-plan.md
       reason: "Implementation Order" section says
               "see screen-plan.md for usage context"
```

File A depends on file B. File B appears to depend on file A.
Cycle detected.

**How the agent handles it:**
```
CYCLE DETECTED
--------------
files:   screen-plan.md ↔ component-plan.md
type:    apparent bidirectional dependency

Analysis:
  screen-plan.md → component-plan.md:
    CONFIRMED dependency — screen plan references component definitions.
    Component must be understood before screen can be implemented.

  component-plan.md → screen-plan.md:
    SUSPECTED false dependency — "see screen-plan.md for usage context"
    is a cross-reference for human readers, not a definition dependency.
    The component plan does not require screen plan content to be
    implemented. This is an informational link, not a build dependency.

Resolution:
  Treat component-plan.md → screen-plan.md edge as informational only.
  Remove from dependency graph.
  Order: component-plan.md first, screen-plan.md second.

Note: If during lean reading it becomes clear this resolution was wrong
      and component-plan.md genuinely requires screen-plan.md content,
      declare a scope amendment and re-evaluate order.
```

**Revised dependency graph:**
```
DEPENDENCY GRAPH (revised)
--------------------------
screen-plan.md
  └─ depends on: component-plan.md [confirmed]

component-plan.md
  └─ informational reference: screen-plan.md [not a build dependency]
  └─ no build dependencies on other in-scope files
```

**Key lesson from this example:**
Cycles in documentation dependency graphs almost always indicate
an informational cross-reference being misread as a build dependency.
The default resolution is to identify which direction is informational
and remove that edge. Only flag as a genuine cycle if both directions
are clearly definitional — in practice this should not occur in
well-structured plan files.