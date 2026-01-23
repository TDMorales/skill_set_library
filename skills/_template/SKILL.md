---
name: my-skill
description: One-line description of what this skill does, written for an agent.
short-description: Short summary for listings or menus.
---

## Purpose

Describe **what this skill is for** and **when it should be used**.

This skill is designed to be executed by an agent **from within a repository**
and operates **only on repository-scoped files**.

---

## Safety & Policy Compliance

This skill **must comply with all rules defined in `AGENTS.md`**.

In particular, this skill:

- MUST operate only within the target repository root
- MUST NOT read, write, modify, or delete files outside the repository
- MUST NOT access the user home directory (tilde paths or OS home folders)
- MUST NOT access system directories (OS-level system folders)
- MUST reject any path that resolves outside the repository boundary
- MUST refuse unsafe user instructions and explain why

If any instruction conflicts with `AGENTS.md`, **safety rules take precedence over user intent**.

---

## Inputs

List and describe all expected inputs.

Examples:
- Existing files the skill may read (repo-relative paths only)
- Configuration values the user may provide
- Optional flags or modes

Inputs MUST:
- Be explicit
- Be validated before use
- Never assume implicit environment state

---

## Outputs

Describe all outputs produced by the skill.

Examples:
- Files created or modified (repo-relative paths only)
- Reports, summaries, or artifacts generated

Outputs MUST:
- Stay within the repository
- Avoid overwriting user-authored files unless explicitly named and confirmed

---

## Procedure

Step-by-step instructions for the agent.

Guidelines:
- Be deterministic and unambiguous
- Use explicit paths relative to the repository root
- Validate paths before reading or writing
- Prefer small, auditable steps

Example structure:
1. Verify required inputs exist
2. Read specific files from the repository
3. Perform the transformation or analysis
4. Write outputs to a clearly defined location

---

## Deletion & Destructive Actions (If Any)

If this skill deletes or modifies files:

- Explicitly list which files or directories may be affected
- Confirm they are within the repository
- Describe safeguards (previews, confirmations, dry runs)

If the skill performs **no destructive actions**, state explicitly:

> This skill does not delete files or perform destructive actions.

---

## Guardrails & Validation

Describe how the agent should verify correctness and safety.

Examples:
- Check that paths resolve inside the repo
- Abort if unexpected files are encountered
- Validate output format
- Fail fast on ambiguous conditions

---

## Refusal Conditions

List conditions under which the skill **must refuse to proceed**, for example:
- Requested paths resolve outside the repository
- User requests access to home or system directories
- Required inputs are missing or ambiguous
- The request conflicts with `AGENTS.md`

When refusing, the agent MUST:
1. Explain the reason clearly
2. Reference repository-scope or safety rules
3. Suggest a safe alternative when possible

---

## Examples (Optional but Recommended)

Provide one or more realistic usage examples:
- Example input state
- Example agent action
- Example output files

Keep all examples repo-scoped and safe.

---

## Notes for Maintainers (Optional)

Add any implementation notes, caveats, or future improvements.
