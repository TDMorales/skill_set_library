---
name: factory-builder-patterns
description: "Plan, implement, and audit Factory Method + Builder patterns in an existing repo with strict invariants, validation checks, and output contracts."
version: "0.1.0"
scope: "repo"
modes:
  - audit
  - plan
  - implement
inputs:
  required:
    - target_language: "python|typescript|mixed"
    - pattern: "factory_method|builder|both"
  optional:
    - target_paths: "list of files/dirs to change or audit"
    - constraints: "e.g., no new deps, keep public API stable, match existing style"
outputs:
  artifacts:
    - "PLAN.md (plan mode)"
    - "CHANGES.md (implement mode)"
    - "AUDIT.md (audit mode)"
---

# Purpose
Implement **Factory Method** and/or **Builder** patterns (or audit an existing implementation) in a repo **without changing behavior**, while enforcing a consistent structure, clear naming, and testable contracts.

This skill is a *guard-style procedure*: short steps, explicit invariants, mandatory checks, and deterministic outputs.

---

# Operating Modes

## 1) Audit Mode (review-only)
Use when the repo already contains a Factory Method / Builder implementation, or the user wants a pattern suitability review.
- **Must not** modify code.
- **Must** produce `AUDIT.md` with findings and pass/fail checks.

## 2) Plan Mode (design-only)
Use when the user wants a concrete plan before code changes.
- **Must not** modify code.
- **Must** produce `PLAN.md` containing a step plan, file map, and validation checklist.

## 3) Implement Mode (code changes)
Use when the user wants the pattern implemented or refactored into place.
- **Must** modify code and (if present) update/extend tests.
- **Must** produce `CHANGES.md` describing what changed, why, and how to validate.

---

# Preconditions (hard gates)
Proceed only if ALL are true:
1. Repo paths are accessible in the current working directory (repo-scoped only).
2. Target language(s) is declared (`python`, `typescript`, or `mixed`).
3. Pattern selection is declared (`factory_method`, `builder`, or `both`).
4. For implement mode: there is a clearly identified seam to refactor or a new feature boundary to implement.

If any precondition fails: **stop** and output a minimal plan to gather missing info (do not guess hidden repo structure).

---

# Core Concepts (definitions you must preserve)
## Factory Method (intent)
- Encapsulate object creation in a **Creator** via a **factory method**.
- Client code depends on a **Product interface/abstract type**, not concrete products.
- Concrete creators decide which concrete product to instantiate.

## Builder (intent)
- Construct a complex object step-by-step.
- Same construction process can create different representations.
- Optional: **Director** orchestrates steps (only if it materially improves reuse/readability).

---

# Invariants (must always hold)

## Global invariants (all modes)
- **No background work**: produce results in the current response/run.
- **Repo-scoped only**: never assume home/system access.
- **KISS/DRY**: minimal abstractions; no speculative frameworks.
- **Behavioral preservation**: refactors must keep observable behavior stable unless the user explicitly requests behavior changes.

## Factory Method invariants
FM-1. A stable **Product abstraction** exists (interface / protocol / abstract base type / type alias) that client code uses.
FM-2. A **Creator** defines a factory method (e.g., `create_*()`), and client logic is written against the Product abstraction.
FM-3. **Concrete creators** override/implement the factory method to produce **concrete products**.
FM-4. Client code must not `new` / instantiate concrete products directly *at the call site that is meant to be pattern-managed*.
FM-5. Creator is not just a thin wrapper around `if/else` unless it reduces coupling at a real seam; prefer polymorphism over conditionals only where justified.

## Builder invariants
B-1. There is a dedicated **Builder** with step methods and a terminal `build()` (or equivalent) gate.
B-2. Builder steps are ordered/validated: invalid partial states must be prevented (via typing, runtime checks, or step constraints).
B-3. Built result is *coherent*: `build()` returns a fully-initialized object/value.
B-4. Optional Director is used only if it eliminates repeated construction choreography across call sites.
B-5. Builder does not become a “god object”: keep steps tight, do not embed unrelated business logic.

---

# Procedure

## Audit Mode Procedure (no code changes)
1. **Locate candidates**
   - Search for creator-like classes/functions (`create`, `factory`, `make`, `build`, `builder`).
   - Identify call sites that instantiate concrete types directly.
2. **Classify pattern presence**
   - Determine whether implementation matches Factory Method, Builder, both, or neither.
3. **Run invariant checks**
   - Apply FM-* checks if Factory Method is present/claimed.
   - Apply B-* checks if Builder is present/claimed.
4. **Assess suitability**
   - If pattern is used but unnecessary: recommend simplification.
   - If pattern is missing but beneficial: propose minimal insertion seam.
5. **Output contract**
   - Write `AUDIT.md` with:
     - Summary (what exists, what’s missing)
     - Findings mapped to invariants (pass/fail with evidence)
     - Risks (behavior changes, API churn, overengineering)
     - Recommendations (ranked: must/should/could)
     - Minimal next-step plan (if changes are recommended)

## Audit Mode (Repo Scanning Procedure)
Use Audit Mode when asked to scan a repo and identify violations of Factory Method and/or Builder rules.

The assistant **must** follow this exact sequence:

1. **Identify pattern surfaces**
   - Factory Method: creators, factory methods, product abstractions, creation seams.
   - Builder: builders, step methods, build() gates, optional directors.
2. **Locate call sites**
   - Trace instantiation points for concrete products or built results.
3. **Map flows**
   - Factory Method: selection seam → creator → product → client usage.
   - Builder: step ordering → validation → build() → result usage.
4. **Check invariants**
   - Evaluate FM-* and/or B-* items against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.
5. **Produce findings using the required schema**
   - Every violation or missing requirement **must** be reported as a finding.
   - If a rule is satisfied, it may be listed as “verified” (optional).
6. **Propose minimal fixes**
   - Fixes must be scoped, behavior-preserving, and aligned with constraints.
   - Prefer small diffs over rewrites unless architecture is fundamentally missing.

Audit Mode **must not** end without:
- at least one pass over the relevant creation seams
- a completed findings list (even if empty)

## Plan Mode Procedure (design-only)
1. **Identify the seam**
   - Factory Method: where object creation causes coupling (feature switches, environment, platform, vendor selection).
   - Builder: where construction has many parameters/optional parts, or multiple representations.
2. **Propose minimal structure**
   - Factory Method: Product abstraction + Creator + Concrete creators.
   - Builder: Builder + Product/Result + (optional) Director.
3. **Define interfaces and names**
   - Choose names aligned with domain language (not “Factory” everywhere).
4. **Map files**
   - Prefer colocating with feature module; avoid global “patterns/” dump.
5. **Validation plan**
   - Which tests must be added/updated; what behavior must remain unchanged.
6. **Output contract**
   - Write `PLAN.md` containing:
     - Target files to add/modify
     - Public API impact statement (must be “none” unless required)
     - Pattern-specific structure diagram (text)
     - Step-by-step implementation sequence
     - Validation checklist (the one below, customized)

## Implement Mode Procedure (code changes)
1. **Create/adjust types first**
   - Add Product abstraction (FM) or Builder + Result type (B).
2. **Refactor call sites gradually**
   - Keep behavior stable by introducing adapter layers if needed.
3. **Minimize diff blast radius**
   - Avoid touching unrelated modules; prefer small PR-like steps.
4. **Add/extend tests**
   - Lock in expected behavior at the seam (factory selection, builder state validation, output correctness).
5. **Self-review with invariants**
   - Verify FM-* and/or B-* items.
6. **Output contract**
   - Write `CHANGES.md` with:
     - What changed (files + key symbols)
     - Why it changed (coupling reduced, readability improved)
     - How to validate (commands, tests)
     - Behavioral equivalence notes (what was preserved)

---

# Mandatory Validation Checklist (must include in every mode output)
## Repo safety
- [ ] Changes (if any) are repo-scoped; no external/system assumptions.
- [ ] No new dependencies added unless explicitly approved.
- [ ] Naming matches existing conventions.

## Factory Method checks (if applicable)
- [ ] FM-1 Product abstraction exists and is used by clients.
- [ ] FM-2 Creator owns factory method; client logic uses Product abstraction.
- [ ] FM-3 Concrete creators produce concrete products.
- [ ] FM-4 Target call sites no longer instantiate concrete products directly.
- [ ] FM-5 Conditional logic reduced at seam OR explicitly justified.

## Builder checks (if applicable)
- [ ] B-1 Builder has step methods and a `build()` gate.
- [ ] B-2 Invalid partial states are prevented or rejected with clear errors.
- [ ] B-3 `build()` returns a complete, coherent result.
- [ ] B-4 Director used only if it removes repetition; otherwise omitted.
- [ ] B-5 Builder stays focused; no unrelated business logic added.

## Behavioral checks
- [ ] Existing tests still pass (or audit/plan explains gaps).
- [ ] New/updated tests cover the seam (creation selection / build correctness).
- [ ] Public API changes are documented and minimized.

---

# Output Contracts (strict)

## AUDIT.md (Audit Mode)
Must contain, in this order:
1. Scope (paths reviewed, language, pattern target)
2. Findings (by invariant ID, pass/fail + evidence)
3. Risk assessment (what could break if refactored)
4. Recommendations (must/should/could)
5. Proposed next steps (minimal)

## Required Output Schema (Audit Findings)
When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- pattern target:
- constraints:
- scope (paths reviewed):

### Findings
For each finding, include:

- **ID:** `FB-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of FM-* or B-* invariants)
- **Location:** `path/to/file.ext:Lx-Ly`
- **Evidence:** short excerpt (1–8 lines)
- **Impact:** what breaks or becomes harder to change
- **Minimal Fix:** concrete change (describe or patch snippet)
- **Confidence:** `high | medium | low`

If there are no violations, output:
- **Findings:** `none`

### Validation Checklist Summary
- A copy of the checklist with each item marked:
  - `[x]` verified
  - `[ ]` not verified / missing
  - `[!]` violated (must link to finding IDs)

## PLAN.md (Plan Mode)
Must contain, in this order:
1. Goal + constraints
2. Proposed structure (symbols + file locations)
3. Implementation steps (numbered, minimal)
4. Validation plan (tests + checklist)
5. Rollback strategy (how to revert safely)

## CHANGES.md (Implement Mode)
Must contain, in this order:
1. Summary of changes
2. File-by-file breakdown
3. Pattern mapping (which invariant items are satisfied and how)
4. How to validate (commands/tests)
5. Notes (tradeoffs, follow-ups)

---

# Guardrails (what not to do)
- Do not introduce abstract layers “because patterns”.
- Do not create a Director for Builder unless there are ≥2 repeated construction choreographies.
- Do not centralize factories/builders into a global module unless the repo already does so.
- Do not change runtime behavior silently; if behavior must change, state it explicitly in the plan/changes.

---

# Refusal Conditions
Refuse (or switch to Plan/Audit) if:
- The user requests hidden/system access, secrets, or non-repo operations.
- The request requires altering behavior in a high-risk domain without tests or acceptance criteria.
- The request is “implement pattern everywhere” without a concrete seam or justification (offer an audit instead).

---

# “When to choose which pattern” decision rule (fast)
- Choose **Factory Method** when the pain is *which concrete type to create* at runtime and clients shouldn’t know the details.
- Choose **Builder** when the pain is *how to construct a complex object safely* with many optional/ordered parts.
- Choose **Both** when factories produce builders or when creation selection and complex construction both exist—only if each solves a distinct pain point.

---
