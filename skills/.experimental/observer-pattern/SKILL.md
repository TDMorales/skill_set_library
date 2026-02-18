---
name: observer-pattern
description: "Plan, implement, and audit the Observer pattern in an existing repo with strict invariants, validation checks, and output contracts."
version: "0.1.0"
scope: "repo"
modes:
  - audit
  - plan
  - implement
inputs:
  required:
    - target_language: "python|typescript|mixed"
    - variant: "basic|event_typed|both"
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
Implement the **Observer** pattern (or audit an existing implementation) in a repo **without changing behavior**, while enforcing a consistent structure, clear naming, and testable contracts.

This skill is a *guard-style procedure*: short steps, explicit invariants, mandatory checks, and deterministic outputs.

---

# Operating Modes

## 1) Audit Mode (review-only)
Use when the repo already contains an Observer implementation, or the user wants a pattern suitability review.
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
3. Variant selection is declared (`basic`, `event_typed`, or `both`).
4. For implement mode: there is a clearly identified seam where state changes must propagate to dependent objects.

If any precondition fails: **stop** and output a minimal plan to gather missing info (do not guess hidden repo structure).

---

# Core Concepts (definitions you must preserve)
## Observer / Event-Subscriber (intent)
- Define a **one-to-many dependency** so that when one object (the Subject/Publisher) changes state, all dependents (Observers/Subscribers) are notified and updated automatically.
- The Publisher communicates with Observers **only via a common interface**, never by referencing concrete observer classes.
- Observers can be **attached and detached dynamically** at runtime.

## Event-Typed Variant (intent)
- Extend the basic Observer with **event-type discrimination** so observers subscribe to specific event categories rather than receiving every notification.
- An **EventManager** (or equivalent dispatcher) manages per-type subscriber lists.
- Typed events are an additive layer on top of the core Observer contract—they do not replace it.

---

# Invariants (must always hold)

## Global invariants (all modes)
- **No background work**: produce results in the current response/run.
- **Repo-scoped only**: never assume home/system access.
- **KISS/DRY**: minimal abstractions; no speculative frameworks.
- **Behavioral preservation**: refactors must keep observable behavior stable unless the user explicitly requests behavior changes.

## Observer invariants
OB-1. A stable **Observer/Subscriber abstraction** exists (interface / protocol / abstract base type) declaring a notification method (`update` or domain equivalent) that all concrete observers implement.
OB-2. A **Subject/Publisher** owns subscription management: it provides `attach`/`detach` (or `subscribe`/`unsubscribe`) methods and maintains a subscriber list.
OB-3. The Subject notifies observers **only via the Observer abstraction**; it does not reference or depend on any concrete observer class.
OB-4. **Concrete Observers** implement the Observer interface independently; adding or removing an observer does not require changes to the Subject or other Observers (Open/Closed Principle).
OB-5. Subscription is **dynamic**: observers can be added and removed at runtime; the Subject does not assume a fixed set of observers.

## Event-Typed invariants
ET-1. An **event-type discriminator** exists (string key, enum, or type parameter) that the Subject/EventManager uses to route notifications to relevant observers only.
ET-2. Observers subscribe to **specific event types**; the Subject does not broadcast all events to all observers unless explicitly intended.
ET-3. Event-type registration does not break OB-1 through OB-5; typed events are an additive layer, not a replacement for the core Observer contract.

---

# Procedure

## Audit Mode Procedure (no code changes)
1. **Locate candidates**
   - Search for subject-like classes/functions (`subscribe`, `unsubscribe`, `attach`, `detach`, `notify`, `emit`, `on`, `off`, `addEventListener`, `removeEventListener`).
   - Identify places where state changes trigger notifications or callbacks.
2. **Classify pattern presence**
   - Determine whether implementation matches Observer (basic), Event-typed, both, or neither.
3. **Run invariant checks**
   - Apply OB-* checks if Observer is present/claimed.
   - Apply ET-* checks if Event-typed variant is present/claimed.
4. **Assess suitability**
   - If pattern is used but unnecessary: recommend simplification.
   - If pattern is missing but beneficial: propose minimal insertion seam.
5. **Output contract**
   - Write `AUDIT.md` with:
     - Summary (what exists, what's missing)
     - Findings mapped to invariants (pass/fail with evidence)
     - Risks (behavior changes, API churn, overengineering)
     - Recommendations (ranked: must/should/could)
     - Minimal next-step plan (if changes are recommended)

## Audit Mode (Repo Scanning Procedure)
Use Audit Mode when asked to scan a repo and identify violations of Observer rules.

The assistant **must** follow this exact sequence:

1. **Identify pattern surfaces**
   - Observer: subjects/publishers, observer interfaces, subscription methods, notification calls.
   - Event-typed: event managers, event-type registries, filtered dispatch logic.
2. **Locate call sites**
   - Trace notification trigger points and observer registration points.
3. **Map flows**
   - Observer: state change → notify → observer.update → side effect.
   - Event-typed: state change → event type → filtered dispatch → observer.update → side effect.
4. **Check invariants**
   - Evaluate OB-* and/or ET-* items against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.
5. **Produce findings using the required schema**
   - Every violation or missing requirement **must** be reported as a finding.
   - If a rule is satisfied, it may be listed as "verified" (optional).
6. **Propose minimal fixes**
   - Fixes must be scoped, behavior-preserving, and aligned with constraints.
   - Prefer small diffs over rewrites unless architecture is fundamentally missing.

Audit Mode **must not** end without:
- at least one pass over the relevant notification seams
- a completed findings list (even if empty)

## Plan Mode Procedure (design-only)
1. **Identify the seam**
   - Observer: where state changes must propagate to multiple dependents (UI updates, logging, cache invalidation, cross-module sync).
   - Event-typed: where different consumers need different event categories from the same source.
2. **Propose minimal structure**
   - Observer: Observer interface + Subject + Concrete observers.
   - Event-typed: Observer interface + EventManager + Subject (delegates to EventManager) + Concrete observers.
3. **Define interfaces and names**
   - Choose names aligned with domain language (not "Observer" everywhere).
4. **Map files**
   - Prefer colocating with feature module; avoid global "patterns/" dump.
5. **Validation plan**
   - Which tests must be added/updated; what behavior must remain unchanged.
6. **Output contract**
   - Write `PLAN.md` containing:
     - Target files to add/modify
     - Public API impact statement (must be "none" unless required)
     - Pattern-specific structure diagram (text)
     - Step-by-step implementation sequence
     - Validation checklist (the one below, customized)

## Implement Mode Procedure (code changes)
1. **Create/adjust types first**
   - Add Observer interface (basic) or EventManager + Observer interface (event-typed).
2. **Refactor call sites gradually**
   - Replace direct coupling with subscription-based notification; keep behavior stable by introducing adapter layers if needed.
3. **Minimize diff blast radius**
   - Avoid touching unrelated modules; prefer small PR-like steps.
4. **Add/extend tests**
   - Lock in expected behavior at the seam (subscription, notification delivery, unsubscription, event filtering).
5. **Self-review with invariants**
   - Verify OB-* and/or ET-* items.
6. **Output contract**
   - Write `CHANGES.md` with:
     - What changed (files + key symbols)
     - Why it changed (coupling reduced, notification formalized)
     - How to validate (commands, tests)
     - Behavioral equivalence notes (what was preserved)

---

# Mandatory Validation Checklist (must include in every mode output)
## Repo safety
- [ ] Changes (if any) are repo-scoped; no external/system assumptions.
- [ ] No new dependencies added unless explicitly approved.
- [ ] Naming matches existing conventions.

## Observer checks (if applicable)
- [ ] OB-1 Observer abstraction exists and declares a notification method.
- [ ] OB-2 Subject owns subscription management with attach/detach methods.
- [ ] OB-3 Subject notifies via Observer abstraction only; no concrete observer references.
- [ ] OB-4 Concrete observers are independent; adding/removing one requires no changes to others.
- [ ] OB-5 Subscription is dynamic; observers attach/detach at runtime.

## Event-Typed checks (if applicable)
- [ ] ET-1 Event-type discriminator exists and routes notifications.
- [ ] ET-2 Observers subscribe to specific event types.
- [ ] ET-3 Event typing is additive; core OB-* invariants still hold.

## Behavioral checks
- [ ] Existing tests still pass (or audit/plan explains gaps).
- [ ] New/updated tests cover the seam (subscription, notification, unsubscription).
- [ ] Public API changes are documented and minimized.

---

# Output Contracts (strict)

## AUDIT.md (Audit Mode)
Must contain, in this order:
1. Scope (paths reviewed, language, variant target)
2. Findings (by invariant ID, pass/fail + evidence)
3. Risk assessment (what could break if refactored)
4. Recommendations (must/should/could)
5. Proposed next steps (minimal)

## Required Output Schema (Audit Findings)
When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- variant target:
- constraints:
- scope (paths reviewed):

### Findings
For each finding, include:

- **ID:** `OP-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of OB-* or ET-* invariants)
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
- Do not introduce Observer abstractions where a simple callback or direct call suffices.
- Do not create an EventManager for single-event-type subjects; use it only when there are ≥2 distinct event categories.
- Do not centralize all observers into a global registry unless the repo already follows that convention.
- Do not change runtime behavior silently; if behavior must change, state it explicitly in the plan/changes.
- Do not use the Observer pattern to mask control flow; notification should supplement, not replace, explicit method calls in critical paths.

---

# Refusal Conditions
Refuse (or switch to Plan/Audit) if:
- The user requests hidden/system access, secrets, or non-repo operations.
- The request requires altering behavior in a high-risk domain without tests or acceptance criteria.
- The request is "add observers everywhere" without a concrete seam or justification (offer an audit instead).

---

# "When to use Observer" decision rule (fast)
- Choose **Observer (basic)** when the pain is *one object changing state needs to notify N dependents* and the set of dependents is open-ended or dynamic.
- Choose **Event-Typed** when the pain is *different consumers care about different categories of change* from the same source, and broadcasting everything to everyone is wasteful or confusing.
- Choose **Both** only when both concerns exist independently—a subject with typed events and generic subscribers.
- Choose **Neither** if there is only one consumer, the relationship is static, or a simple callback/promise suffices.

---
