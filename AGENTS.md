# AGENTS.md

## Purpose

This document defines **mandatory policies, contracts, and safety constraints**
for all agents and skills contained in or installed from the `skill_set_library`
repository.

Any agent executing a skill from this library **MUST** follow these rules.
Any skill that violates these rules is considered **invalid and unsafe**.

These rules apply regardless of:
- where the skill is installed
- which agent executes it
- whether execution is local, remote, or containerized

---

## 1. Skill Contract (Required Invariants)

Every skill in this repository **MUST**:

1. Be fully self-contained inside its skill directory.
2. Declare its behavior explicitly in `SKILL.md`.
3. Operate **only** on repository-scoped files.
4. Never assume global system access.
5. Never rely on implicit permissions or environment state.

### Required Files
Each skill folder MUST contain:
- `SKILL.md` (authoritative behavior definition)

Optional but allowed:
- `scripts/`
- `assets/`
- `references/`
- `examples/`

---

## 1A. Skill Creation Template (Required Process)

Use the same repeatable sequence for every new skill:

1. Define/verify `SKILL.md`
   - Purpose, when-to-use, definitions
   - Hard invariants
   - Procedure (audit, plan, implement)
   - Validation checklist
   - Output contracts + audit findings schema
   - Refusal conditions
2. Create minimal folder skeleton
   - `examples/README.md` (index + audit procedure + audit schema)
   - `examples/<skill>_<language>.md` (broken + correct + explicit)
   - `references/SOURCES.md`
3. Add broken/correct/explicit examples
   - Broken: violate named invariants
   - Correct: minimal compliant example
   - Explicit: a seam or edge case
4. Mirror audit mode
   - Same procedure + schema in `SKILL.md` and `examples/README.md`
5. Consistency checks
   - Invariant IDs referenced in findings schema
   - README and SKILL stay in sync

Preferred scaffold root: `skills/_template/skill/`

---

## 2. Repository-Scoped Execution Model

All skills are designed to be executed **from within a target repository**.

### Allowed File Scope
A skill MAY:
- Read files within the target repository root
- Create or modify files **inside the repository**
- Create new directories inside the repository
- Read `.codex/skills/<skill-name>/` if needed
- For `$skill-installer` only: read (no writes) its system skill directory from
  `$CODEX_HOME/skills/.system/skill-installer/` or `~/.codex/skills/.system/skill-installer/`
  to load `SKILL.md` and bundled references

### Explicitly Disallowed Scope (Hard Rule)
A skill MUST NOT:
- Read, write, modify, or delete files outside the repository root
- Access the user's home directory (`~`, `/home/*`, `/Users/*`)
- Access system directories (`/etc`, `/bin`, `/usr`, `/opt`, `/var`)
- Traverse upward via `../` beyond the repository root
- Resolve or follow symlinks that escape the repository boundary
  - Exception: `$skill-installer` may read its own system skill directory as
    described in the Allowed File Scope

These restrictions apply even if:
- the agent has OS-level permissions
- the skill is installed globally
- the user explicitly asks for it

---

## 3. Absolute Filesystem Safety Rules (Non-Negotiable)

### 🚫 Forbidden Actions
Under **no circumstances** (except the `$skill-installer` read-only exception in
Section 2) may a skill or agent:

- Delete files outside the repository
- Modify files outside the repository
- Read private user files (SSH keys, tokens, configs)
- Enumerate home directory contents
- Execute shell commands that implicitly expand to home paths
  (e.g. `~`, `$HOME`, `$USERPROFILE`)

### 🚫 Forbidden Commands (Examples)
Skills MUST NOT issue or suggest:
- `rm -rf ~`
- `rm -rf /`
- `rm -rf /home`
- `rm -rf /Users`
- `cp ~/.ssh/*`
- `cat ~/.env`
- `ls ~`
- `cd ~`

If a user explicitly requests these actions, the skill MUST refuse.

---

## 4. Path Handling Rules

Agents and skills MUST:

- Resolve all paths relative to the repository root
- Normalize paths before use
- Reject any resolved path that escapes the repo boundary
- Treat symlinks as unsafe unless explicitly verified to remain in-repo

### Safe Path Example
```text
repo-root/
  docs/output.md
```

### Unsafe Path Example
```text
.env
../secrets.txt
~/.ssh/id_rsa
/Users/alice/Documents
/etc/passwd
```

If an unsafe path is detected, the agent MUST:
- Abort the action
- Explain why the action is blocked
- Suggest a safe alternative inside the repo

## 5. Skill Behavior Constraints

Skills MUST be:
- Deterministic
- Auditable
- Reproducible

Skills MUST NOT:
- Perform background tasks
- Persist state outside the repo
- Phone home
- Download or upload data without explicit user instruction
- Modify git history unless explicitly instructed

## 6. Deletion & Destructive Actions Policy

### Destructive actions are discouraged and tightly controlled.

Allowed (With Explicit Confirmation)
- Deleting files created by the same skill
- Deleting generated artifacts inside the repo
- Cleaning build or temp directories inside the repo

Never Allowed
- Deleting user-authored files unless explicitly named
- Deleting directories without showing contents first
- Any deletion outside the repo

If deletion is requested:
- The skill MUST describe exactly what will be deleted
- The skill MUST ask for confirmation
- The skill MUST limit deletion scope to the repo

## 7. Safety Over Obedience Principle

If a user instruction conflicts with:
- this document
- filesystem safety
- repository boundaries

The agent MUST:
- Refuse the instruction
- Explain the violation clearly
- Offer a safe, repo-scoped alternative

User intent does not override safety policy.

## 8. Skill Review & Compliance

A skill is considered compliant only if:
- It follows all rules in this document
- It documents its file access behavior in SKILL.md
- It does not rely on implicit permissions

Non-compliant skills:
- MUST NOT be installed
- MUST NOT be executed
- SHOULD be removed or moved to .experimental until fixed

## 9. Enforcement Priority

When rules conflict, enforce in this order:
- Filesystem safety
- Repository boundaries
- Explicit skill contract
- User instruction
- Convenience or speed

## 10. Summary (TL;DR for Agents)
- Stay inside the repo
- Never touch the home directory
- Never touch system files
- Reject unsafe paths
- Explain refusals clearly
- Safety always wins

**Failure to follow these rules is considered a critical defect.**
