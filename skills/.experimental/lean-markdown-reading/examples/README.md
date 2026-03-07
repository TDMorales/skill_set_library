# Examples — Lean Markdown Reading

## Purpose

This directory contains annotated examples that demonstrate correct, broken,
and edge-case behavior for the Lean Markdown Reading skill. Examples are the
primary calibration tool for agents learning this skill — the anti-patterns
are as important as the correct patterns.

---

## Index

| File                       | Description                                                       |
| -------------------------- | ----------------------------------------------------------------- |
| `lean_reading_examples.md` | Three annotated examples: broken, correct, and explicit edge case |

---

## How To Use These Examples

Before executing a lean reading task, an agent should:

1. Recall the broken example — recognize the failure mode before starting
2. Follow the correct example's step sequence as a template
3. Check the explicit example if the file has no headings or unusual structure

These are not templates to copy. They are behavioral anchors.

---

## Audit Procedure

After completing a lean reading pass, the agent self-audits by checking
each invariant from SKILL.md against its own behavior.

Run through this checklist before producing implementation output:
```
SELF-AUDIT CHECKLIST
--------------------
[ ] I-1: Did I avoid loading any full file into context?
[ ] I-2: Did I avoid reading any section more than once?
[ ] I-3: Did I produce a read log before beginning implementation?
[ ] I-4: Did I skip all skip-zone sections without reading them?
[ ] I-5: Did I establish relevance before reading each chunk, not after?
[ ] I-6: Did I stop reading each chunk once needed facts were extracted?
```

If any box cannot be checked, produce an audit finding using the schema
in SKILL.md before proceeding.

---

## Audit Schema (Quick Reference)
```
FINDING
  invariant: <I-1 through I-6>
  file: <filename>
  observed: <what the agent actually did>
  expected: <what the agent should have done>
  severity: <high | medium | low>
```

Severity guide:
- **high** — invariant violated, token waste occurred or facts were missed
- **medium** — invariant bent but task completed correctly
- **low** — read log missing or incomplete, behavior otherwise correct

---

## Keeping Examples In Sync

If SKILL.md is updated — new invariants added, skip zones changed,
procedure steps modified — the examples in this directory must be reviewed
and updated to match. An example that references a stale invariant ID
or outdated procedure step is considered invalid.

Checklist for sync:
- Invariant IDs in findings match current SKILL.md IDs
- Skip zone examples reflect current skip zone list
- Procedure step numbers in annotations match current SKILL.md steps