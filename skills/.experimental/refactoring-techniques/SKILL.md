---
name: refactoring-techniques
description: "Plan and apply behavior-preserving refactoring techniques to improve code structure, reduce coupling, and eliminate code smells."
version: "0.1.0"
scope: "repo"
modes:
  - plan
  - implement
inputs:
  required:
    - target_language: "python|typescript|mixed"
    - technique: "one of CM-*, MF-*, OD-*, SC-*, SM-*, DG-* or a named technique"
    - target_location: "file path + symbol or line range to refactor"
  optional:
    - target_paths: "additional files affected by the refactoring"
    - constraints: "e.g., no new deps, keep public API stable, match existing style"
    - smell_finding: "CS-### finding ID from a code-smell-audit AUDIT.md"
outputs:
  artifacts:
    - "PLAN.md (plan mode)"
    - "CHANGES.md (implement mode)"
---

# Purpose
Apply **behavior-preserving refactoring techniques** to improve code structure. This skill is the *implement* counterpart to `code-smell-audit`: the audit skill detects smells, this skill applies the named fix.

Each technique has strict preconditions, mechanical steps, and post-conditions. The goal is always the same: **change structure without changing behavior**.

This skill covers the ~19 most impactful techniques from the [Refactoring.Guru catalog](https://refactoring.guru/refactoring/techniques) — specifically the ones referenced as remedies by `code-smell-audit` invariants. The remaining ~47 techniques are documented in `references/SOURCES.md` for manual reference.

---

# Operating Modes

## 1) Plan Mode (design-only)
Use when the user wants a step-by-step transformation plan before code changes.
- **Must not** modify code.
- **Must** produce `PLAN.md` with mechanical steps, affected files, risk notes, and validation strategy.

## 2) Implement Mode (code changes)
Use when the user wants the refactoring applied.
- **Must** modify code following the technique's mechanical steps.
- **Must** produce `CHANGES.md` describing what changed, why, and how to validate.
- **Must** preserve observable behavior unless the user explicitly requests behavior changes.

---

# Preconditions (hard gates)
Proceed only if ALL are true:
1. Repo paths are accessible in the current working directory (repo-scoped only).
2. Target language(s) is declared (`python`, `typescript`, or `mixed`).
3. A specific technique is named (by invariant ID or canonical name).
4. A target location is identified (file path + symbol or line range).
5. For implement mode: the target code is readable and the technique's preconditions are met.

If any precondition fails: **stop** and explain what is missing.

---

# Core Concepts

## What is Refactoring?
A disciplined technique for restructuring existing code — altering its internal structure **without changing its external behavior**. Each refactoring is a small, well-defined transformation that makes the codebase easier to understand, cheaper to modify, or both.

## Relationship to Code Smells
Every code smell has one or more refactoring techniques as its remedy. The `code-smell-audit` skill detects smells (the *what*); this skill applies the fix (the *how*). A `smell_finding` input can link a specific audit finding to the technique being applied.

## Behavioral Preservation
The cardinal rule: **tests that passed before must pass after**. If no tests exist at the refactoring seam, the plan must note this risk and recommend adding tests first.

---

# Invariants (must always hold)

## Global invariants (all modes)
- **No background work**: produce results in the current response/run.
- **Repo-scoped only**: never assume home/system access.
- **Behavior preservation**: observable behavior must remain unchanged unless explicitly agreed.
- **Minimal blast radius**: touch only the files necessary for the technique; avoid unrelated cleanups.
- **Test continuity**: existing tests must still pass; new tests should lock in the refactored structure.

## Composing Methods (CM-*)
CM-1. **Extract Method** — isolate a coherent code block into a named method; the original site calls the new method. Preserve all side effects, return values, and variable assignments. Resolves: BL-1, DS-1, DS-2, CL-1, CL-3.
CM-2. **Decompose Conditional** — extract the condition, then-branch, and else-branch of a complex conditional into named methods. Each method name documents the intent. Resolves: BL-1.

## Moving Features between Objects (MF-*)
MF-1. **Move Method** — relocate a method to the class it uses most; update all call sites. Resolves: CP-2, CP-3, CL-1, CL-2, CL-3.
MF-2. **Move Field** — relocate a field to the class that uses it most; update all accessors. Resolves: CP-2, CP-3, CL-2.
MF-3. **Extract Class** — split a class with multiple responsibilities into two or more classes, each with a single cohesive purpose. Resolves: BL-2, BL-5, CP-1, OA-2, CL-2.
MF-4. **Inline Class** — fold a class that does too little back into the class that uses it. Resolves: CP-2, DS-3, DS-6.
MF-5. **Hide Delegate** — create a wrapper method on the server object so the client does not navigate through a chain of delegates. Resolves: CL-2, CL-3.
MF-6. **Remove Middle Man** — remove a class that only delegates calls and have the client call the delegate directly. Resolves: CL-4.
MF-7. **Introduce Foreign Method / Local Extension** — add missing functionality to a library class via a standalone helper method (foreign method) or a wrapper/subclass (local extension). Resolves: CL-5.

## Organizing Data (OD-*)
OD-1. **Replace Data Value with Object** — replace a primitive that carries domain meaning with a value object that encapsulates validation and behavior. Resolves: BL-3.
OD-2. **Encapsulate Field / Collection** — replace direct field access with getter/setter methods; for collections, return defensive copies to prevent external mutation. Resolves: DS-4.
OD-3. **Replace Type Code with Subclasses / State-Strategy** — replace a type-code field with polymorphic subclasses or a Strategy/State object to eliminate conditionals dispatching on the code. Resolves: BL-3, OA-1.

## Simplifying Conditional Expressions (SC-*)
SC-1. **Replace Conditional with Polymorphism** — replace a switch/if-else chain that dispatches on type with polymorphic method dispatch; each branch becomes a subclass/implementation. Resolves: OA-1.

## Simplifying Method Calls (SM-*)
SM-1. **Rename Method** — change a method name to clearly communicate its purpose; update all call sites. Resolves: OA-4, DS-1.
SM-2. **Introduce Parameter Object** — replace a recurring group of parameters with a single object that bundles them. Resolves: BL-3, BL-4, BL-5.
SM-3. **Preserve Whole Object** — pass an entire object instead of extracting multiple fields from it as separate arguments. Resolves: BL-4, BL-5.

## Dealing with Generalization (DG-*)
DG-1. **Extract Superclass / Extract Interface** — pull shared members from two or more classes into a new base class or interface. Resolves: OA-3, OA-4, DS-2.
DG-2. **Collapse Hierarchy** — merge a superclass and subclass that are no longer different enough to justify separate classes. Resolves: DS-3, DS-6.
DG-3. **Replace Inheritance with Delegation** — replace an inheritance relationship with a field reference and forwarding methods when the subclass does not truly specialize the superclass. Resolves: OA-3.

---

# Procedure

## Plan Mode Procedure (design-only)
1. **Identify technique and target**
   - Confirm which invariant ID (e.g., CM-1) applies and where (file + symbol/line range).
   - If linked to a `smell_finding`, verify the smell is still present.
2. **Verify technique preconditions**
   - CM-1 (Extract Method): the block is self-contained or its dependencies can be passed as parameters.
   - MF-1 (Move Method): the target class exists and the method uses more of the target's data.
   - MF-3 (Extract Class): responsibilities can be cleanly separated without circular dependencies.
   - OD-3 (Replace Type Code): the type code is used in conditionals that can become polymorphic.
   - (Apply analogous checks for other techniques.)
3. **Draft mechanical steps**
   - List each transformation in order (create target, move/copy code, update references, remove original).
4. **Map affected files**
   - Every file that will be created, modified, or deleted.
5. **Assess risk**
   - Does the target have tests? If not, flag this and recommend adding characterization tests first.
   - Will the public API change? If so, document the breaking change.
6. **Output contract**
   - Write `PLAN.md` containing:
     - Technique name + invariant ID
     - Target location (file + symbol)
     - Mechanical steps (numbered)
     - Affected files map
     - Risk notes (test coverage, API stability)
     - Validation checklist

## Implement Mode Procedure (code changes)
1. **Verify preconditions** (same as Plan step 2)
2. **Apply mechanical steps in order**
   - Follow the technique's canonical sequence; do not skip steps.
   - Prefer small, incremental commits over one large transformation.
3. **Update call sites**
   - Find every reference to the refactored symbol and update it.
4. **Preserve or add tests**
   - Existing tests must still pass.
   - Add tests at the new seam if none exist.
5. **Self-review with invariants**
   - Verify the technique's post-conditions hold.
   - Verify global invariants (behavior preservation, minimal blast radius).
6. **Output contract**
   - Write `CHANGES.md` with:
     - Technique applied (name + invariant ID)
     - What changed (files + key symbols)
     - Why it changed (smell resolved, coupling reduced)
     - How to validate (commands, tests)
     - Behavioral equivalence notes

---

# Mandatory Validation Checklist (must include in every mode output)

## Repo safety
- [ ] Changes (if any) are repo-scoped; no external/system assumptions.
- [ ] No new dependencies added unless explicitly approved.
- [ ] Naming matches existing conventions.

## Behavioral preservation
- [ ] All existing tests still pass.
- [ ] No observable behavior change (or change is explicitly documented and approved).
- [ ] New tests cover the refactored seam.

## Composing Methods checks (if applicable)
- [ ] CM-1 Extracted method has a clear name reflecting its purpose.
- [ ] CM-1 All variables needed by the extracted block are passed as parameters or are accessible in scope.
- [ ] CM-2 Condition, then-branch, and else-branch are each a named method.

## Moving Features checks (if applicable)
- [ ] MF-1 Method moved to the class it uses most; all call sites updated.
- [ ] MF-2 Field moved to the class that owns its usage; all accessors updated.
- [ ] MF-3 Extracted class has a single cohesive responsibility; no circular deps with the original.
- [ ] MF-4 Inlined class is fully absorbed; no orphan references remain.
- [ ] MF-5 Delegate is hidden behind a wrapper method; client no longer navigates chains.
- [ ] MF-6 Middle man removed; client calls delegate directly.
- [ ] MF-7 Foreign method or local extension encapsulates the missing library functionality.

## Organizing Data checks (if applicable)
- [ ] OD-1 Value object encapsulates validation; primitives no longer carry domain meaning at call sites.
- [ ] OD-2 Field access goes through getters/setters; collections return defensive copies.
- [ ] OD-3 Type code replaced with subclasses or State/Strategy; conditionals eliminated.

## Simplifying checks (if applicable)
- [ ] SC-1 Switch/if-else chain replaced with polymorphic dispatch; each branch is a subclass/implementation.
- [ ] SM-1 Method renamed; all call sites updated; name communicates purpose.
- [ ] SM-2 Parameter group replaced with a parameter object; all call sites updated.
- [ ] SM-3 Whole object passed instead of extracted fields; call sites simplified.

## Generalization checks (if applicable)
- [ ] DG-1 Shared members pulled into a superclass/interface; subclasses use inheritance.
- [ ] DG-2 Hierarchy collapsed; merged class retains all needed behavior.
- [ ] DG-3 Inheritance replaced with delegation; forwarding methods preserve the public API.

---

# Output Contracts (strict)

## PLAN.md (Plan Mode)
Must contain, in this order:
1. Technique name + invariant ID
2. Target location (file + symbol/line range)
3. Mechanical steps (numbered, in execution order)
4. Affected files map
5. Risk notes (test gaps, API changes, behavior-change potential)
6. Validation checklist (customized from above)
7. Rollback strategy (how to revert safely)

## CHANGES.md (Implement Mode)
Must contain, in this order:
1. Summary of changes (technique applied + target)
2. File-by-file breakdown
3. Invariant mapping (which technique post-conditions are satisfied)
4. How to validate (commands/tests)
5. Behavioral equivalence notes
6. Follow-up recommendations (if additional refactorings are warranted)

---

# Guardrails (what not to do)
- Do not apply a technique if its preconditions are not met — stop and explain.
- Do not refactor without verifying test coverage at the seam; recommend adding tests first.
- Do not combine multiple techniques in a single step — apply them sequentially so each can be validated.
- Do not touch unrelated code, even if it also has smells — scope to the named technique and target.
- Do not change public API unless the user explicitly approves.
- Do not delete code that might be used dynamically (reflection, string-based lookups) without verification.

---

# Refusal Conditions
Refuse (or switch to Plan) if:
- The user requests hidden/system access, secrets, or non-repo operations.
- No tests exist at the refactoring seam and the user declines to add them first (offer Plan instead).
- The technique's preconditions are not met (explain which precondition fails and what to do).
- The requested technique would fundamentally change behavior without explicit acknowledgment.

---

# Cross-Reference to code-smell-audit
This skill is designed to consume findings from `code-smell-audit`. The mapping:

| Smell finding | Recommended technique(s) |
|---|---|
| BL-1 Long Method | CM-1 Extract Method, CM-2 Decompose Conditional |
| BL-2 Large Class | MF-3 Extract Class |
| BL-3 Primitive Obsession | OD-1 Replace Data Value with Object, OD-3 Replace Type Code, SM-2 Introduce Parameter Object |
| BL-4 Long Parameter List | SM-2 Introduce Parameter Object, SM-3 Preserve Whole Object |
| BL-5 Data Clumps | MF-3 Extract Class, SM-2 Introduce Parameter Object, SM-3 Preserve Whole Object |
| OA-1 Switch Statements | SC-1 Replace Conditional with Polymorphism, OD-3 Replace Type Code |
| OA-2 Temporary Field | MF-3 Extract Class |
| OA-3 Refused Bequest | DG-3 Replace Inheritance with Delegation, DG-1 Extract Superclass |
| OA-4 Alt Classes / Diff Interfaces | SM-1 Rename Method, DG-1 Extract Superclass |
| CP-1 Divergent Change | MF-3 Extract Class |
| CP-2 Shotgun Surgery | MF-1 Move Method, MF-2 Move Field, MF-4 Inline Class |
| CP-3 Parallel Inheritance | MF-1 Move Method, MF-2 Move Field |
| DS-1 Comments | CM-1 Extract Method, SM-1 Rename Method |
| DS-2 Duplicate Code | CM-1 Extract Method, DG-1 Extract Superclass |
| DS-3 Lazy Class | MF-4 Inline Class, DG-2 Collapse Hierarchy |
| DS-4 Data Class | OD-2 Encapsulate Field/Collection |
| DS-5 Dead Code | (delete — no technique needed) |
| DS-6 Speculative Generality | MF-4 Inline Class, DG-2 Collapse Hierarchy |
| CL-1 Feature Envy | MF-1 Move Method, CM-1 Extract Method |
| CL-2 Inappropriate Intimacy | MF-1 Move Method, MF-2 Move Field, MF-3 Extract Class, MF-5 Hide Delegate |
| CL-3 Message Chains | MF-5 Hide Delegate, CM-1 Extract Method |
| CL-4 Middle Man | MF-6 Remove Middle Man |
| CL-5 Incomplete Library Class | MF-7 Introduce Foreign Method / Local Extension |

---
