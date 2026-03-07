# Lean Reading Examples

Three examples demonstrating broken, correct, and edge-case behavior.
All examples use realistic content modeled on actual project files.

---

## Example 1 — BROKEN

**Scenario:**
Agent is asked to implement `BiographyScreen` based on the implementation
plan in `frolicking-roaming-pillow.md`. The file is 210 lines and covers
five phases of a React Native feature build.

**Sub-task:**
> "Implement BiographyScreen as described in the plan."

**What the agent did:**
```
[Agent loads frolicking-roaming-pillow.md — all 210 lines]

Now I have the full file. Let me find the BiographyScreen section...

The file covers:
- Phase 1: Four new UI components (Blockquote, DatePicker, TabBar, GalleryGrid)
- Phase 2: MemorialHomeScreen edit affordances
- Phase 3: New screens including BiographyScreen and GalleryScreen rewrite
- Phase 4: Route registration
- Phase 5: Barrel export updates

For BiographyScreen, I can see in Phase 3...
```

**Why this is broken:**
```
FINDING
  invariant: I-1
  file: frolicking-roaming-pillow.md
  observed: Agent loaded all 210 lines before identifying the relevant
            section. Phases 1, 2, 4, and 5 were never needed and
            consumed context space unnecessarily.
  expected: Agent should have mapped headings first (Step 1), matched
            "BiographyScreen" to Phase 3 only (Step 2), and read
            ~40 lines instead of 210.
  severity: high
```
```
FINDING
  invariant: I-5
  file: frolicking-roaming-pillow.md
  observed: Relevance was determined after loading, not before. The agent
            loaded first and scanned second.
  expected: Heading map built first, relevance established per section,
            then targeted read of flagged sections only.
  severity: high
```

**Token waste:** ~170 lines of irrelevant content loaded unnecessarily.
At average prose density this represents roughly 60–70% of the file
consumed with zero extraction value for the task.

---

## Example 2 — CORRECT

**Scenario:**
Same file, same sub-task as Example 1.

**Sub-task:**
> "Implement BiographyScreen as described in the plan."

**What the agent did:**

**Step 1 — Map the file (headings only):**
```
[FILE: frolicking-roaming-pillow.md]
H2  Phase 1 — New UI Components           (~lines 10–44)
H3    1. Blockquote                        (~lines 12–18)
H3    2. DatePicker                        (~lines 19–28)
H3    3. TabBar                            (~lines 29–36)
H3    4. GalleryGrid                       (~lines 37–44)
H2  Phase 2 — MemorialHomeScreen Edits    (~lines 46–82)
H3    2a. Hero Image                       (~lines 50–56)
H3    2b. Profile Header                   (~lines 57–66)
H3    2c. Section Title Edit Icons         (~lines 67–74)
H3    2d. EditModeToolbar                  (~lines 75–82)
H2  Phase 3 — New Screens                 (~lines 84–122)
H3    5. BiographyScreen                  (~lines 86–103)
H3    6. GalleryScreen Rewrite            (~lines 104–122)
H2  Phase 4 — Route Registration          (~lines 124–136)
H2  Phase 5 — Barrel Export Updates       (~lines 138–148)
     [table]
     Build Order                           (~lines 150–162)
     Key Files to Modify                   (~lines 164–180)
     Existing Components Reused            (~lines 182–196)
     Verification                          (~lines 198–210)
```

**Step 2 — Match to sub-task:**
```
Sub-task: implement BiographyScreen

Phase 1 — New UI Components    → SKIP (component definitions, not screen)
  Exception: Blockquote        → FLAG (BiographyScreen uses Blockquote atom)

Phase 2 — MemorialHomeScreen   → SKIP (different screen, not in scope)
  Exception: 2c pencil icon    → FLAG (navigation trigger for BiographyScreen)

Phase 3 — New Screens
  BiographyScreen              → READ (direct match)
  GalleryScreen Rewrite        → SKIP (sibling screen, different task)

Phase 4 — Route Registration   → READ introduction only (MEMORIAL_BIOGRAPHY route needed)
Phase 5 — Barrel Exports       → SKIP (skip zone: barrel export table)
Build Order                    → SKIP (skip zone: reference table)
Key Files to Modify            → SKIP (skip zone: reference table)
Existing Components Reused     → SKIP (skip zone: reference table)
Verification                   → SKIP (skip zone: verification checklist)
```

**Step 3 — Read flagged sections:**
```
[READ: Phase 3 > BiographyScreen — ~18 lines]
Extracted:
- Path: apps/mobile/src/features/memorial/screens/BiographyScreen.js
- Design ref: docs/ui_design/ios_design/ui_issues/BiographyScreen.jpg
- Layout: NavigationHeader (showBack, back label "Profile")
- Read-only mode: Blockquote for quote + Text for bio
- Edit mode: TextArea for quote (300 char recommended) + TextArea for bio
- Save/Cancel at bottom
- Data: receives memorial via route params
- Mutations: useUpdateMemorialMutation (subtitle) +
             useUpdateMemorialPersonMutation (bio)
- On save: navigation.goBack()
- Note: no DB char limits, show count for UX

[READ: Phase 1 > Blockquote — ~7 lines]
Extracted:
- Path: packages/ui/src/atoms/Blockquote/Blockquote.native.tsx
- Props: children: ReactNode, style?
- Renders: View with left border accent, light brand bg 10% opacity,
           italic text, borderLeftWidth only, top-right/bottom-right radius

[READ: Phase 2 > 2c pencil icon — ~4 lines, intro only]
Extracted:
- Biography pencil navigates to ROUTES.MEMORIAL_BIOGRAPHY
  with { memorial, editMode: isEditMode }

[READ: Phase 4 — first 3 lines only]
Extracted:
- New route: MEMORIAL_BIOGRAPHY: "MemorialBiography"
- Register in MainNavigation.js with headerShown: false
```

**Read Log (produced before implementation):**
```
READ LOG
--------
frolicking-roaming-pillow.md
  READ:    Phase 3 > BiographyScreen (~18 lines)
  READ:    Phase 1 > Blockquote (~7 lines) — used by BiographyScreen
  READ:    Phase 2 > 2c Section Title Edit Icons (~4 lines) — nav trigger
  READ:    Phase 4 intro (~3 lines) — route name needed
  SKIPPED: Phase 1 > DatePicker, TabBar, GalleryGrid (not used by BiographyScreen)
  SKIPPED: Phase 2 > Hero Image, Profile Header, EditModeToolbar (different scope)
  SKIPPED: Phase 3 > GalleryScreen Rewrite (sibling task, not in scope)
  SKIPPED: Phase 5 Barrel Exports (skip zone: barrel export table)
  SKIPPED: Build Order, Key Files, Existing Components (skip zone: reference tables)
  SKIPPED: Verification (skip zone: checklist)

Total read: ~32 lines of ~210 (15%)
```

**Self-audit:**
```
SELF-AUDIT CHECKLIST
--------------------
[x] I-1: Full file was not loaded — headings mapped first, 32/210 lines read
[x] I-2: No section read twice
[x] I-3: Read log produced before implementation output
[x] I-4: All skip-zone sections skipped (barrel tables, checklists, ref tables)
[x] I-5: Relevance established during Step 2 mapping, before any content read
[x] I-6: Each chunk read stopped at point of extraction completion
```

All invariants satisfied. Proceed to implementation.

---

## Example 3 — EXPLICIT (Edge Case: No Headings)

**Scenario:**
Agent is given a flat markdown file with no headings. The file is a
dense prose description of a component's token system — approximately
180 lines of flat paragraphs describing color tokens, spacing scales,
and typography rules. The agent needs to extract only the border-radius
token values relevant to implementing the Blockquote atom.

**Sub-task:**
> "Find the border-radius token values from the token reference file."

**What the agent did:**

---

## Example 4 — CROSS-FILE REFERENCE (Lazy Pull)

**Scenario:**
Agent is implementing `BiographyScreen` from `frolicking-roaming-pillow.md`.
Mid-read, the BiographyScreen section references the `Blockquote` atom
which is defined in `inherited-soaring-donut.md`. The agent needs the
Blockquote props and render structure to implement the read-only display
mode correctly.

**Sub-task:**
> "Implement the read-only mode of BiographyScreen including the Blockquote
> display at the top."

**What the agent did:**

**Primary read in progress (frolicking-roaming-pillow.md):**
```
[READING: Phase 3 > BiographyScreen]

Extracted so far:
- Path: apps/mobile/src/features/memorial/screens/BiographyScreen.js
- Layout: NavigationHeader with showBack, back label "Profile"
- Read-only mode: <Blockquote> showing quote + <Text> showing full bio

↳ "Blockquote" is referenced but its props and render behavior
  are not defined in this file. Cross-file pull required.
```

**Pause and declare the pull:**
```
CROSS-FILE PULL
target:      inherited-soaring-donut.md
need:        Blockquote props, render structure, visual behavior
triggered:   frolicking-roaming-pillow.md > Phase 3 > BiographyScreen
             — read-only mode uses <Blockquote> with no props defined here
```

**Step 1 on target file (headings only):**
```
[FILE: inherited-soaring-donut.md]
H2  Context                              (~lines 1–4)
H2  New Files                            (~lines 6–13)  [table]
H2  1. SectionHeader (Molecule)          (~lines 15–33)
H2  2. MediaGrid (Organism)              (~lines 35–67)
H3    Uniform variant                    (~lines 51–55)
H3    Featured variant                   (~lines 56–67)
     Implementation Order               (~lines 69–73)
     Key Files Referenced               (~lines 75–80)
     Verification                       (~lines 82–88)
```

**Step 2 on target file — match to pull need:**
```
Pull need: Blockquote props and render structure

Context               → SKIP (project background, not component spec)
New Files table       → SKIP (skip zone: reference table)
SectionHeader         → SKIP (different component)
MediaGrid             → SKIP (different component)
Implementation Order  → SKIP (skip zone: reference table)
Key Files Referenced  → SKIP (skip zone: reference table)
Verification          → SKIP (skip zone: checklist)
```

No direct Blockquote section found in `inherited-soaring-donut.md`.
```
GAP DETECTED
inherited-soaring-donut.md does not contain a Blockquote definition.
The Blockquote atom is referenced in frolicking-roaming-pillow.md
Phase 1 > Section 1. Returning to primary file to pull from there.
```

**Revised pull — back to primary file, targeted section:**
```
CROSS-FILE PULL (revised — pull from primary file Phase 1)
target:   frolicking-roaming-pillow.md > Phase 1 > 1. Blockquote
need:     Blockquote props, render structure
note:     Definition is in the primary file, not a second file.
          This is a within-file lazy pull, not a cross-file pull.
          Applying re-entry rule — declaring gap before re-read.

GAP: BiographyScreen section references Blockquote but does not
     define its props. Phase 1 > Blockquote contains the definition.
     Re-reading that section (~7 lines) to resolve.
```
```
[READ: Phase 1 > 1. Blockquote — ~7 lines]
Extracted:
- Path: packages/ui/src/atoms/Blockquote/Blockquote.native.tsx
- Props: children: ReactNode, style?
- Renders: View with left border accent using tokens.semantic.interactive.primary
           light brand background at 10% opacity
           italic text
           borderLeftWidth only (left side border)
           top-right and bottom-right border radius
```

**Return to primary read and continue:**
```
[RESUMING: Phase 3 > BiographyScreen]
Continuing from after Blockquote reference...

Extracted (continued):
- Edit mode: TextArea for quote (300 char recommended) + TextArea for bio
- Save/Cancel at bottom or EditModeToolbar pattern
- Mutations: useUpdateMemorialMutation + useUpdateMemorialPersonMutation
- On save: navigation.goBack()
```

**Read Log:**
```
READ LOG
--------
frolicking-roaming-pillow.md (primary)
  READ:    Phase 3 > BiographyScreen (~18 lines)
  RE-ENTRY Phase 1 > Blockquote (~7 lines)
    gap:     BiographyScreen references Blockquote props not defined
             in Phase 3. Re-read scoped to Phase 1 > Blockquote only.
  SKIPPED: Phase 1 > DatePicker, TabBar, GalleryGrid (not in scope)
  SKIPPED: Phase 2 (different screen scope)
  SKIPPED: Phase 3 > GalleryScreen Rewrite (sibling, not in scope)
  SKIPPED: Phase 4, Phase 5, all reference tables and checklists (skip zones)

inherited-soaring-donut.md (cross-file pull attempt)
  MAPPED:  Headings only — no Blockquote section found
  READ:    0 lines — pull redirected back to primary file
  SKIPPED: All sections (none matched pull need)

Total read: ~25 lines across both files
```

**Self-audit:**
```
SELF-AUDIT CHECKLIST
--------------------
[x] I-1: No full file loaded — headings mapped, targeted reads only
[x] I-2: Phase 1 > Blockquote was read twice — but re-entry rule applied:
         gap was declared explicitly before re-read, scoped to minimum lines
[x] I-3: Read log produced before implementation output
[x] I-4: All skip zones respected across both files
[x] I-5: Relevance established before each chunk read
[x] I-6: Each read stopped at extraction completion
[x] I-7: Cross-file pull on inherited-soaring-donut.md was scoped to
         single target chunk — no sibling sections read
[x] I-8: Re-entry on Phase 1 > Blockquote declared gap explicitly:
         "BiographyScreen references Blockquote props not defined in Phase 3"
```

**What this example demonstrates:**

- Cross-file pulls don't always find what they're looking for — the agent
  correctly mapped the target file, found no match, and redirected without
  reading irrelevant sections
- Re-entry rule is not a loophole — the gap must be named and specific
  before the re-read happens, not after
- Within-file lazy pulls follow the same discipline as cross-file pulls:
  declare the gap, scope the read, stop at extraction
- I-2 and I-8 work together: I-2 is the default, I-8 is the narrow
  named exception. An agent that re-reads without declaring a gap
  has violated I-2 with no valid I-8 defense.

**Step 4 — No-heading fallback:**

The file contains no H1–H3 headings. Standard Steps 1–2 cannot be applied.
Falling back to Step 4 procedure.
```
[READ: first 10 lines of tokens-reference.md]
Extracted orientation:
- File describes the full design token system
- Organized as flat paragraphs by token category
- Categories appear to be: color, spacing, typography, border, elevation
- No section markers or anchors visible

[READ: last 10 lines of tokens-reference.md]
Extracted orientation:
- File ends with elevation/shadow tokens
- No index or TOC present
- Confirms flat structure throughout
```
```
[KEYWORD SCAN for: "radius", "border-radius", "rounded", "borderRadius"]
Matches found at approximately:
- Line 94:  "...borderRadius scale uses four steps..."
- Line 95:  "...sm: 4px, md: 8px, lg: 16px, xl: 24px..."
- Line 96:  "...components use lg (16px) as the default radius..."
- Line 97:  "...Blockquote specifically uses lg top-right and bottom-right..."
- Line 112: "...full-rounded variant uses 9999px..."
```
```
[READ: lines 93–99 — keyword match block + 1 line context each side]
Extracted:
- Border radius scale: sm=4px, md=8px, lg=16px, xl=24px
- Default component radius: lg (16px)
- Blockquote: lg applied to top-right and bottom-right corners only
- Full-rounded variant: 9999px (not relevant to Blockquote)
```

**Read Log:**
```
READ LOG
--------
tokens-reference.md (flat file — no headings, Step 4 fallback applied)
  READ:    Lines 1–10 (orientation — first block)
  READ:    Lines 171–180 (orientation — last block)
  READ:    Lines 93–99 (keyword match: borderRadius, 7 lines)
  SKIPPED: Lines 11–92 (pre-match content — no keyword hits)
  SKIPPED: Lines 100–170 (post-match content — extraction complete at line 99)

Total read: ~27 lines of ~180 (15%)
```

**Self-audit:**
```
SELF-AUDIT CHECKLIST
--------------------
[x] I-1: Full file not loaded — orientation reads + keyword-targeted block only
[x] I-2: No section read twice
[x] I-3: Read log produced before implementation output
[x] I-4: No skip zones apply (flat file has no structural sections to skip)
[x] I-5: Keyword scan established relevance before line-level reads
[x] I-6: Reading stopped at line 99 once border-radius facts were complete
```

**Note on flat files:**
Keyword scanning is less precise than heading-based targeting. There is a
higher risk of missing relevant content in flat files. If the keyword scan
returns no matches and the task clearly requires content from this file,
escalate to a full sequential read and note the fallback in the read log.
This is not an invariant violation — it is the correct fallback behavior
when Step 4 exhausts its options without finding a match.