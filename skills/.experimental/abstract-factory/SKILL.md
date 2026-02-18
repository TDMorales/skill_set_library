---
name: abstract-factory
description: "Plan, implement, and audit the Abstract Factory pattern in an existing repo with strict invariants, validation checks, and output contracts."
version: "0.1.0"
scope: "repo"
modes:
  - audit
  - plan
  - implement
inputs:
  required:
    - target_language: "python|typescript|mixed"
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
Implement the **Abstract Factory** pattern (or audit an existing implementation) in a repo **without changing behavior**, while enforcing a consistent structure, clear naming, and testable contracts.

Abstract Factory produces **families of related objects** without specifying their concrete classes. Each concrete factory guarantees that the products it creates are compatible with one another.

This skill is a *guard-style procedure*: short steps, explicit invariants, mandatory checks, and deterministic outputs.

---

# Operating Modes

## 1) Audit Mode (review-only)
Use when the repo already contains an Abstract Factory implementation, or the user wants a pattern suitability review.
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
3. There is a clearly identified need for **families of related objects** (≥2 product types, ≥2 variants).
4. For implement mode: there is a clearly identified seam to refactor or a new feature boundary to implement.

If any precondition fails: **stop** and output a minimal plan to gather missing info (do not guess hidden repo structure).

---

# Core Concepts (definitions you must preserve)

## Abstract Factory (intent)
- Provide an interface for creating **families of related or dependent objects** without specifying their concrete classes.
- **Abstract Products** declare interfaces for each distinct product type in the family. Client code depends on these abstractions, not concrete products.
- **Concrete Products** are variant-specific implementations of each Abstract Product, grouped by family. Products within a family are designed to collaborate.
- The **Abstract Factory** interface declares one creation method per product type. Client code calls these methods instead of constructing products directly.
- **Concrete Factories** implement the Abstract Factory interface. Each factory produces all products for exactly one variant, guaranteeing family coherence.
- The **Client** works exclusively through the Abstract Factory and Abstract Product interfaces. The concrete factory is typically selected once at initialization based on configuration, environment, or runtime conditions.

---

# Invariants (must always hold)

## Global invariants (all modes)
- **No background work**: produce results in the current response/run.
- **Repo-scoped only**: never assume home/system access.
- **KISS/DRY**: minimal abstractions; no speculative frameworks.
- **Behavioral preservation**: refactors must keep observable behavior stable unless the user explicitly requests behavior changes.

## Abstract Factory invariants
AF-1. An **Abstract Factory** interface (or ABC / protocol / abstract type) exists, declaring one creation method per product type in the family.
AF-2. **Concrete Factories** implement the Abstract Factory interface; each factory produces all products of exactly **one** variant.
AF-3. Each distinct product type has an **Abstract Product** interface (or ABC / protocol / abstract type) that client code depends on.
AF-4. **Concrete Products** implement their respective Abstract Product interface; they are instantiated **only** inside their corresponding Concrete Factory.
AF-5. All products from a single Concrete Factory are **family-coherent** — designed to work together. Products from different factories must not be mixed at a call site managed by the pattern.
AF-6. **Client code** depends only on the Abstract Factory and Abstract Product interfaces, never on concrete factory or concrete product classes.
AF-7. Adding a new product variant requires only a new Concrete Factory and its Concrete Products — existing factories, products, and client code remain **unchanged** (Open/Closed Principle).

---

# Procedure

## Audit Mode Procedure (no code changes)
1. **Locate candidates**
   - Search for factory-like classes/interfaces with multiple creation methods (`create_*`, `make_*`, `build_*`).
   - Identify product hierarchies (multiple implementations of a shared interface/abstract type).
2. **Classify pattern presence**
   - Determine whether implementation matches Abstract Factory, simpler Factory Method, or neither.
   - Look for family grouping: does a single factory produce a coherent set of related products?
3. **Run invariant checks**
   - Apply AF-* checks against code evidence.
4. **Assess suitability**
   - If pattern is used but unnecessary (only one product type, or only one variant): recommend simplification.
   - If pattern is missing but beneficial (multiple product families with variant switching): propose minimal insertion seam.
5. **Output contract**
   - Write `AUDIT.md` with:
     - Summary (what exists, what's missing)
     - Findings mapped to invariants (pass/fail with evidence)
     - Risks (behavior changes, API churn, overengineering)
     - Recommendations (must/should/could)
     - Minimal next-step plan (if changes are recommended)

## Audit Mode (Repo Scanning Procedure)
Use Audit Mode when asked to scan a repo and identify violations of Abstract Factory rules.

The assistant **must** follow this exact sequence:

1. **Identify pattern surfaces**
   - Abstract Factory interfaces, concrete factories, abstract product interfaces, concrete products.
2. **Locate call sites**
   - Trace where factories are obtained and where products are created.
   - Check whether client code references concrete types directly.
3. **Map flows**
   - Selection seam → concrete factory → product family → client usage.
   - Verify that each factory produces a complete, coherent family.
4. **Check invariants**
   - Evaluate AF-* items against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.
5. **Produce findings using the required schema**
   - Every violation or missing requirement **must** be reported as a finding.
   - If a rule is satisfied, it may be listed as "verified" (optional).
6. **Propose minimal fixes**
   - Fixes must be scoped, behavior-preserving, and aligned with constraints.
   - Prefer small diffs over rewrites unless architecture is fundamentally missing.

Audit Mode **must not** end without:
- at least one pass over the relevant creation seams
- a completed findings list (even if empty)

## Plan Mode Procedure (design-only)
1. **Identify the seam**
   - Where does the code need to produce families of related objects that must be consistent with each other?
   - Common triggers: platform/theme/environment switching, vendor abstraction, multi-format export.
2. **Propose minimal structure**
   - Abstract Product interfaces (one per product type).
   - Abstract Factory interface (one creation method per product type).
   - Concrete Products grouped by variant.
   - Concrete Factories (one per variant).
3. **Define interfaces and names**
   - Choose names aligned with domain language (not "AbstractFactory1" everywhere).
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
1. **Create Abstract Product interfaces first**
   - One interface per product type in the family.
2. **Create Concrete Products grouped by variant**
   - Each variant's products implement their respective Abstract Product interface.
3. **Create the Abstract Factory interface**
   - One creation method per product type, returning the Abstract Product type.
4. **Create Concrete Factories**
   - One per variant; each returns only its variant's concrete products.
5. **Refactor call sites gradually**
   - Replace direct instantiation with factory calls.
   - Ensure client code depends only on abstract interfaces.
   - Keep behavior stable by introducing adapter layers if needed.
6. **Add/extend tests**
   - Verify family coherence (products from one factory work together).
   - Verify variant isolation (switching factory changes all products consistently).
   - Verify client code uses only abstract interfaces.
7. **Self-review with invariants**
   - Verify AF-* items.
8. **Output contract**
   - Write `CHANGES.md` with:
     - What changed (files + key symbols)
     - Why it changed (coupling reduced, family coherence enforced)
     - How to validate (commands, tests)
     - Behavioral equivalence notes (what was preserved)

---

# Mandatory Validation Checklist (must include in every mode output)
## Repo safety
- [ ] Changes (if any) are repo-scoped; no external/system assumptions.
- [ ] No new dependencies added unless explicitly approved.
- [ ] Naming matches existing conventions.

## Abstract Factory checks
- [ ] AF-1 Abstract Factory interface exists with one creation method per product type.
- [ ] AF-2 Concrete Factories implement Abstract Factory; each produces one variant's products.
- [ ] AF-3 Abstract Product interfaces exist for each product type; clients depend on them.
- [ ] AF-4 Concrete Products implement Abstract Products; instantiated only inside Concrete Factories.
- [ ] AF-5 Products from one factory are family-coherent; no cross-family mixing at managed call sites.
- [ ] AF-6 Client code depends only on Abstract Factory + Abstract Product interfaces.
- [ ] AF-7 New variants can be added without modifying existing factories, products, or client code.

## Behavioral checks
- [ ] Existing tests still pass (or audit/plan explains gaps).
- [ ] New/updated tests cover the seam (family coherence / variant isolation).
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

- **ID:** `AF-F-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of AF-* invariants)
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
- Do not introduce Abstract Factory when only one product type exists (Factory Method suffices).
- Do not introduce Abstract Factory when only one variant exists (no family switching needed).
- Do not centralize all factories into a global module unless the repo already does so.
- Do not add product types to the factory that are not genuinely part of the same family.
- Do not change runtime behavior silently; if behavior must change, state it explicitly in the plan/changes.

---

# Refusal Conditions
Refuse (or switch to Plan/Audit) if:
- The user requests hidden/system access, secrets, or non-repo operations.
- The request requires altering behavior in a high-risk domain without tests or acceptance criteria.
- The request is "implement pattern everywhere" without a concrete seam or justification (offer an audit instead).
- There is only one product type or one variant — suggest Factory Method or direct instantiation instead.

---

# "When to choose Abstract Factory" decision rule (fast)
- Choose **Abstract Factory** when the pain is *producing families of related objects that must be used together*, and you need to switch entire families at once (e.g., themes, platforms, vendors).
- Choose **Factory Method** instead when the pain is *which single concrete type to create* — only one product type varies.
- Choose **Builder** instead when the pain is *how to construct a single complex object safely* with many optional/ordered parts.
- Avoid Abstract Factory if there is only one product type or one variant — it adds indirection without benefit.

---
