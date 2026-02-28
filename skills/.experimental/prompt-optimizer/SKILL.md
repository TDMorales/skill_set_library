---
name: prompt-optimizer
description: Use when the user's request is vague, ambiguous, or underspecified and needs to be rewritten into an agent-ready specification with clear scope, context, and acceptance criteria. Produces implementation-ready markdown files that any agent can execute without guessing. Trigger this skill whenever a user says things like "build me a...", "I want to add...", "make this faster", "can you create...", or any request that lacks enough detail for an agent to begin work immediately. Also trigger when the user explicitly asks to "optimize a prompt", "flesh out an idea", or "write a spec".
short-description: Rewrite vague asks into agent-ready specs.
version: "0.2.0"
scope: repo
compatibility: Any LLM-based agent (Claude, Codex, GPT, Gemini, custom agents)
---

# Purpose

Turn vague or underspecified user requests into **implementation-ready markdown
specifications** that any agent can pick up and execute without guessing.

This skill has two phases:
1. **Gather** — conversationally extract the context an agent would need.
2. **Produce** — output a structured markdown file in one of two formats.

This skill is designed to be executed by any agent **from within a repository**
and operates **only on repository-scoped files**.

---

# Safety & Policy Compliance

This skill **must comply with all rules defined in `AGENTS.md`**.

In particular, this skill:

- MUST operate only within the target repository root
- MUST NOT read, write, modify, or delete files outside the repository
- MUST NOT access the user home directory (tilde paths or OS home folders)
- MUST NOT access system directories (OS-level system folders)
- MUST reject any path that resolves outside the repository boundary
- MUST refuse unsafe user instructions and explain why

If any instruction conflicts with `AGENTS.md`, **safety rules take precedence
over user intent**.

---

# When to Apply

Apply this skill when **any** of the following are true:

- The user's request is too vague for an agent to begin implementation
- The user wants to "flesh out" or "spec out" an idea
- The user asks to build, create, add, or implement something without
  providing enough detail about what exists, what to create, or how
  it should behave
- The user explicitly asks for a prompt to be optimized or rewritten

Do **not** apply when:

- The user's request is already specific and actionable
- The user provides a complete spec and just wants it executed
- The task is a simple one-step action (rename a file, run a command)

---

# Definitions

- **Creation Spec**: An implementation blueprint for building new things
  (components, screens, modules, features). Contains per-item specs with
  Create/From/Props/Renders blocks, build order, and file maps.
- **Task Spec**: A lighter action plan for non-creation work (refactors,
  performance fixes, investigations, migrations). Contains goal, context,
  constraints, execution steps, and acceptance criteria.
- **Context**: Everything the agent needs to know about the current state
  of the codebase, what exists, what's wired, what's dormant, and what
  the user has decided.
- **Gap**: A piece of information the agent needs but does not yet have.

---

# Inputs

The user's original request and any clarifying answers provided during the
gathering phase.

Inputs MUST:
- Be explicit
- Be validated before use
- Never assume implicit environment state

---

# Outputs

A single markdown file in one of two formats (Creation Spec or Task Spec),
ready for any agent to execute.

Outputs MUST:
- Stay within the repository
- Avoid overwriting user-authored files unless explicitly named and confirmed
- Be saved to a location the user confirms (suggested default:
  `docs/specs/<spec-name>.md` or a path the user prefers)

---

# Procedure

## Phase 1: Gather (conversational)

When invoked, the agent MUST follow this sequence:

### Step 1 — Acknowledge and identify gaps

Read the user's request. Identify what is known and what is missing.
Do NOT begin producing output yet.

### Step 2 — Ask for output format

Before gathering detailed context, ask the user which output format they need.
Present both options with a one-line definition:

> **Which format fits your need?**
>
> 1. **Creation Spec** — A full implementation blueprint for building new
>    components, screens, or features (includes per-item Create/From/Props/Renders
>    blocks, build order, and file maps).
> 2. **Task Spec** — A lighter action plan for non-creation work like refactors,
>    performance fixes, investigations, or migrations.

If the user's intent clearly implies one format (e.g., "build me a date picker"
→ Creation Spec), the agent MAY skip this question and state its choice with a
brief explanation. The user can override.

### Step 3 — Gather context (gap-driven)

The agent works through the following information areas. It does NOT ask all
questions at once — it asks only what is missing, in natural conversation,
grouping related questions where possible.

**For both formats:**

| Information area | What to find out |
|---|---|
| Current state | What exists today? What's already wired or built? What's dormant or stubbed? |
| User intent | What is the user trying to achieve? What problem does this solve? |
| Scope boundaries | What's in scope vs. explicitly deferred? |
| Constraints | Reuse existing components? Match existing patterns? No new deps? Framework/version locks? |
| Design references | Figma files, screenshots, existing components to mimic, prior art? |
| User decisions | Any decisions the user has already made (naming, behavior, layout)? |

**Additional questions for Creation Spec only:**

| Information area | What to find out |
|---|---|
| Items to create | How many components/screens/modules? What are they? |
| Source/origin | Is each item new from scratch, or ported/adapted from an existing file? |
| Props/params | What inputs does each item accept? Types, defaults, required vs. optional? |
| Rendering behavior | What does each item render? Layout, structure, visual behavior? |
| Token/pattern swaps | Any theming, token, or pattern migrations needed during creation? |
| Barrel exports | Does the project use barrel exports that need updating? |
| Existing reuse | Which existing components/hooks are reused without modification? |

**Additional questions for Task Spec only:**

| Information area | What to find out |
|---|---|
| Baseline | What is the current measurable state (for optimization tasks)? |
| Target | What does "done" look like? Measurable acceptance criteria? |
| Risk areas | What should NOT change? What is fragile? |

The agent stops gathering when it has enough information to fill every
required section of the chosen output format confidently. There is no fixed
question limit — gathering is driven by gaps, not by a count.

### Step 4 — Confirm before producing

Before writing the final spec, the agent MUST summarize what it knows and
what it will produce, and ask the user to confirm or correct. This prevents
wasted effort on a misunderstood request.

---

## Phase 2: Produce (structured output)

Once the user confirms, produce the spec in the chosen format.

---

# Output Contracts

## Creation Spec (required sections, in this order)

```markdown
# <Feature/Component Name> — <Short Description>

## Context
<What exists, what's wired, what's dormant, what the user indicated.
This section should give any agent enough background to understand the
codebase state without reading every file.>

---

## <Phase/Section N> — <Group Name>

### <Item Number>. <Item Name> (<atom/molecule/organism/screen/module>)
- **Create:** `<file path to create>`
- **From:** `<source file if porting, or "new" if from scratch>`
- **Props/Params:** `<prop name>: <type>` — <description> (for each prop)
- **Renders:** <What this item renders — layout, structure, behavior.
  Be specific: mention wrapper elements, conditional rendering,
  visual states, animations.>
- **Token/Pattern Swaps:** <Any theming or pattern migrations, or "none">
- **Barrel Export:** `<export line to add>` in `<barrel file path>`

(Repeat for each item)

---

## Implementation Order
1. <Item> (reason for ordering, e.g., "no deps" or "depends on X")
2. ...

---

## Key Files

| File | Change |
|---|---|
| `path/to/file` | Create / Modify / Rewrite |
| ... | ... |

## Existing Components/Hooks Reused (no modifications needed)

| Component/Hook | Location | Used For |
|---|---|---|
| `Name` | `path/` | <purpose> |
| ... | ... | ... |

---

## Verification
1. <Concrete check — what to run, what to see, what to confirm>
2. ...
```

### Creation Spec invariants:
- Every item MUST have Create, From, Props/Params, and Renders fields.
- Implementation Order MUST respect dependency chains.
- Key Files table MUST list every file created or modified.
- Verification MUST be concrete and testable, not vague ("it works").

---

## Task Spec (required sections, in this order)

```markdown
# Task Spec: <Short Title>

## Goal
<One sentence describing what this task accomplishes.>

## Context
<What exists, what the current state is, what the user indicated.
Same depth as Creation Spec context — give any agent enough background.>

## Constraints
- **Languages/frameworks/versions:** ...
- **Do not change:** ...
- **Performance/latency targets:** ...
- **Security/compliance constraints:** ...

## Execution Plan
1. <Step — specific, actionable, scoped>
2. ...

## Acceptance Criteria
- <Concrete, testable criterion>
- ...
```

### Task Spec additions for optimization tasks:
If the user mentions "optimize", "make faster", "improve performance", or
similar, the Task Spec MUST also include:

```markdown
## Baseline Measurement
<What to measure and how, before making changes.>

## Proposed Optimization
<What to change and why it should help.>

## Verification
<How to measure improvement after changes.>
```

### Task Spec invariants:
- Goal MUST be a single sentence.
- Context MUST be substantive, not a placeholder.
- Execution Plan steps MUST be specific enough that an agent does not
  need to guess.
- Acceptance Criteria MUST be testable.

---

# Validation Checklist

Before delivering the final spec, the agent MUST verify:

- [ ] Output format matches what the user requested (Creation Spec or Task Spec)
- [ ] Context section is substantive and reflects gathered information
- [ ] No information was fabricated — only what the user stated or the agent
      observed in the repo
- [ ] All required sections are present and non-empty
- [ ] (Creation Spec) Every item has Create/From/Props/Renders
- [ ] (Creation Spec) Implementation Order respects dependency chains
- [ ] (Creation Spec) Key Files table is complete
- [ ] (Task Spec) Goal is a single sentence
- [ ] (Task Spec) Execution Plan steps are actionable without guessing
- [ ] Acceptance Criteria / Verification steps are concrete and testable
- [ ] No references to files or paths outside the repository
- [ ] User confirmed the summary before the spec was produced

---

# Guardrails

- Do NOT infer technologies, versions, or constraints the user did not state
  or imply.
- Do NOT fabricate component names, file paths, or prop types — ask if unknown.
- Do NOT skip the gathering phase and jump straight to output.
- Do NOT produce a spec without the user confirming the summary first.
- Do NOT combine both formats in a single output — pick one.
- Do NOT assume any specific agent runtime, tool API, or execution environment.
  The spec must be readable and executable by any agent.

---

# Deletion & Destructive Actions

This skill does not delete files or perform destructive actions.

---

# Refusal Conditions

The skill MUST refuse to proceed if:

- The user requests access outside the repository boundary
- The user requests access to home or system directories
- The request conflicts with `AGENTS.md`

When refusing, the agent MUST:
1. Explain the reason clearly
2. Reference repository-scope or safety rules
3. Suggest a safe alternative when possible

---

# Agent-Agnostic Design Notes

This skill is intentionally agent-agnostic. It:

- Uses plain English procedures, not agent-specific prompt syntax
- References no specific tool APIs, CLI commands, or sandbox models
- Produces standard markdown that any agent can parse and follow
- Makes no assumptions about conversation flow mechanics
- Delegates file-save location to the user, not to an agent convention

Any agent that can read markdown instructions and interact conversationally
with a user can execute this skill.