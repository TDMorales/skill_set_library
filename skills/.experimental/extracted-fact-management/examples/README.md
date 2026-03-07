# Examples — Extracted Fact Management

## Purpose

This directory contains annotated examples demonstrating correct, broken,
and edge-case behavior for the Extracted Fact Management skill. The
examples are grounded in realistic content from actual project files in
this repository.

---

## Index

| File                          | Description                                                               |
| ----------------------------- | ------------------------------------------------------------------------- |
| `fact_management_examples.md` | Four annotated examples: broken, correct, soft interruption, and redirect |

---

## How To Use These Examples

Before executing a multi-step implementation task, an agent should:

1. Read the broken example first — recognize the failure mode before starting
2. Use the correct example's ledger format as a template
3. Reference the interruption examples when a user message breaks the
   implementation flow

These are behavioral anchors, not copy-paste templates.
The ledger format should be adapted to the specific task at hand.

---

## Audit Procedure

After completing each implementation step, the agent self-audits by
checking every invariant from SKILL.md:
```
SELF-AUDIT CHECKLIST (per step)
--------------------------------
[ ] F-1: Were all extracted facts recorded in the ledger immediately?
[ ] F-2: Did every consumed fact exist in the ledger before being used?
[ ] F-3: Was a checkpoint taken after this step completed?
[ ] F-4: If interrupted, was the ledger frozen before responding?
[ ] F-5: If resuming, was the checkpoint stated explicitly first?
[ ] F-6: Were any STALE facts used? (must be zero)
[ ] F-7: If a REDIRECT occurred, did the user confirm before ledger changes?
[ ] F-8: Are unused facts declared at closure, not silently dropped?
```

If any box cannot be checked, produce an audit finding before proceeding.

---

## Audit Schema (Quick Reference)
```
FINDING
  invariant: <F-1 through F-8>
  step: <step number where violation occurred>
  observed: <what the agent actually did>
  expected: <what the agent should have done>
  severity: <high | medium | low>
```

Severity guide:
- **high** — invariant violated, fact loss or stale fact used
- **medium** — invariant bent, task completed correctly but ledger
  integrity is questionable
- **low** — ledger format incomplete or closure summary missing

---

## Keeping Examples In Sync

If SKILL.md is updated — new interruption classes added, schema fields
changed, staleness rules modified — examples must be reviewed and updated.
An example that references a stale schema field or removed invariant ID
is considered invalid.

Sync checklist:
- Fact unit schema fields match current SKILL.md schema
- Checkpoint schema fields match current SKILL.md schema
- Interruption class names match current classification table
- Invariant IDs in findings match current F-1 through F-8