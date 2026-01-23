---
name: prompt-optimizer
description: Use when the user’s request is ambiguous and needs to be rewritten into an agent-ready task spec with clear scope, constraints, and acceptance criteria.
short-description: Rewrite vague asks into agent-ready specs.
---

## Purpose

Define how to rewrite vague user requests into agent-ready task specifications with clear scope, constraints, and acceptance criteria.

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

The user’s original request and any clarifying answers provided during the interaction.

Inputs MUST:
- Be explicit
- Be validated before use
- Never assume implicit environment state

---

## Outputs

A single "Task Spec" response in the exact required format.

Outputs MUST:
- Stay within the repository
- Avoid overwriting user-authored files unless explicitly named and confirmed

---

## Procedure

When invoked:
1. Ask up to 3 targeted clarifying questions if critical details are missing.
2. Otherwise, produce a "Task Spec" that the agent can execute without guessing.

Output EXACTLY this format:

## Task Spec
### Goal
- (one sentence)

### Context (what we know)
- …

### Assumptions (what we are inferring)
- …

### Constraints
- Languages/frameworks/versions:
- Do not change:
- Performance/latency targets:
- Security/compliance constraints:

### Deliverables
- …

### Execution Plan (agent steps)
1) …
2) …

### Acceptance Criteria
- …

### Required Inputs (from user, if any)
- …

If the user mentions “optimize”, include:
- a measurement step (baseline)
- a proposed optimization
- a verification step (after)

---

## Deletion & Destructive Actions (If Any)

This skill does not delete files or perform destructive actions.

---

## Guardrails & Validation

- Ask clarifying questions only when needed; keep it to 3 or fewer.
- Do not infer technologies, versions or constraints that the user did not imply.
- Ensure the output matches the exact Task Spec structure.

---

## Refusal Conditions

The skill MUST refuse to proceed if:
- The user requests access outside the repository boundary
- The user requests access to home or system directories
- The request conflicts with `AGENTS.md`

When refusing, the agent MUST:
1. Explain the reason clearly
2. Reference repository-scope or safety rules
3. Suggest a safe alternative when possible

---

## Examples (Optional but Recommended)

Input: "make this faster"
Output: Task Spec with a baseline measurement step, proposed optimization, and verification step.
See `skills/prompt-optimizer/examples/README.md` for detailed examples.