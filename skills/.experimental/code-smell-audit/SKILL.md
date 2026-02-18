---
name: code-smell-audit
description: "Audit a codebase for code smells across all five canonical categories, produce structured findings with severity and refactoring recommendations, and optionally plan remediation."
version: "0.1.0"
scope: "repo"
modes:
  - audit
  - plan
inputs:
  required:
    - target_language: "python|typescript|mixed"
  optional:
    - target_paths: "list of files/dirs to audit"
    - categories: "bloaters|oo_abusers|change_preventers|dispensables|couplers|all (default: all)"
    - constraints: "e.g., no new deps, keep public API stable, match existing style"
outputs:
  artifacts:
    - "AUDIT.md (audit mode)"
    - "PLAN.md (plan mode)"
---

# Purpose
Detect **code smells** in a repository and produce structured, actionable findings. Each smell is mapped to a numbered invariant, graded by severity, and paired with a concrete refactoring recommendation.

This skill covers all five canonical smell categories from Fowler/Beck (as cataloged by [Refactoring.Guru](https://refactoring.guru/refactoring/catalog)):
**Bloaters**, **Object-Orientation Abusers**, **Change Preventers**, **Dispensables**, and **Couplers**.

This skill is *audit-first*: it detects and reports. Plan mode extends the audit by producing a prioritized refactoring roadmap. Actual refactoring is left to the developer or a dedicated refactoring skill.

---

# Operating Modes

## 1) Audit Mode (review-only)
Scan the repo (or specified paths) for code smells across all or selected categories.
- **Must not** modify code.
- **Must** produce `AUDIT.md` with findings and a completed validation checklist.

## 2) Plan Mode (design-only)
Extend an audit with a prioritized refactoring plan.
- **Must not** modify code.
- **Must** produce `PLAN.md` containing ranked refactoring steps, file map, risk notes, and validation strategy.
- If no audit has been performed yet, run Audit Mode first, then produce the plan.

---

# Preconditions (hard gates)
Proceed only if ALL are true:
1. Repo paths are accessible in the current working directory (repo-scoped only).
2. Target language(s) is declared (`python`, `typescript`, or `mixed`).
3. At least one file or directory is available to scan.

If any precondition fails: **stop** and explain what is missing.

---

# Core Concepts

## What is a Code Smell?
A code smell is a surface-level indicator that *usually* corresponds to a deeper problem in the code. Smells are not bugs — the code works — but they signal increased risk of defects, harder maintenance, and slower development.

## Categories
| Category | Core problem | Smell count |
|---|---|---|
| **Bloaters** | Code that has grown too large to manage | 5 |
| **OO Abusers** | Incomplete or incorrect use of OO principles | 4 |
| **Change Preventers** | A single change forces edits across many locations | 3 |
| **Dispensables** | Pointless code whose removal makes things cleaner | 6 |
| **Couplers** | Excessive coupling between classes | 5 |

## Refactoring Relationship
Each smell maps to one or more refactoring techniques (Extract Method, Move Field, etc.). This skill *identifies* smells and *recommends* techniques. It does not perform the refactoring itself.

---

# Invariants (must always hold)

## Global invariants (all modes)
- **No background work**: produce results in the current response/run.
- **Repo-scoped only**: never assume home/system access.
- **No code changes in audit**: audit and plan modes are strictly read-only.
- **Evidence-based**: every finding must cite a file path and line range; no guessing.
- **Severity-graded**: every finding must include a severity level.

## Bloaters (BL-*)
BL-1. **Long Method** — a method/function contains too many lines or mixes multiple responsibilities. Remedy: Extract Method, Decompose Conditional, Replace Temp with Query.
BL-2. **Large Class** — a class has too many fields, methods, or lines, indicating multiple responsibilities. Remedy: Extract Class, Extract Subclass, Extract Interface.
BL-3. **Primitive Obsession** — primitives are used where small value objects would be clearer (money, ranges, phone numbers, zip codes). Remedy: Replace Data Value with Object, Replace Type Code with Class/Subclasses/State-Strategy, Introduce Parameter Object.
BL-4. **Long Parameter List** — a method takes more than 3–4 parameters, making calls hard to read and maintain. Remedy: Replace Parameter with Method Call, Preserve Whole Object, Introduce Parameter Object.
BL-5. **Data Clumps** — the same group of variables or parameters appears together in multiple places. Remedy: Extract Class, Introduce Parameter Object, Preserve Whole Object.

## Object-Orientation Abusers (OA-*)
OA-1. **Switch Statements** — complex switch/if-else chains dispatch on type codes where polymorphism would be more extensible. Remedy: Replace Conditional with Polymorphism, Replace Type Code with Subclasses/State-Strategy.
OA-2. **Temporary Field** — an object field is only set or used under certain conditions, being empty/null otherwise. Remedy: Extract Class, Introduce Null Object.
OA-3. **Refused Bequest** — a subclass inherits methods or data it does not use or actively overrides to no-op. Remedy: Replace Inheritance with Delegation, Extract Superclass.
OA-4. **Alternative Classes with Different Interfaces** — two classes perform the same role but expose different method signatures. Remedy: Rename Method, Extract Superclass, merge the classes.

## Change Preventers (CP-*)
CP-1. **Divergent Change** — a single class is modified for multiple unrelated reasons (SRP violation). Remedy: Extract Class to separate each axis of change.
CP-2. **Shotgun Surgery** — a single logical change requires many small edits scattered across many classes. Remedy: Move Method, Move Field, Inline Class to consolidate the scattered logic.
CP-3. **Parallel Inheritance Hierarchies** — creating a subclass in one hierarchy forces creating a matching subclass in another. Remedy: Move Method, Move Field to collapse one hierarchy into the other.

## Dispensables (DS-*)
DS-1. **Comments** — excessive or narrating comments compensate for unclear code instead of explaining genuine complexity or intent. Remedy: Extract Method, Rename Method, Introduce Assertion to make code self-documenting.
DS-2. **Duplicate Code** — identical or near-identical logic exists in multiple locations. Remedy: Extract Method, Extract Superclass, Form Template Method.
DS-3. **Lazy Class** — a class does too little to justify its maintenance cost. Remedy: Inline Class, Collapse Hierarchy.
DS-4. **Data Class** — a class has only fields and getters/setters with no meaningful behavior. Remedy: Encapsulate Field/Collection, Move Method into the class to give it responsibility.
DS-5. **Dead Code** — unreachable or unused variables, parameters, methods, or classes. Remedy: delete the dead code.
DS-6. **Speculative Generality** — abstractions, hooks, or parameters exist "just in case" but serve no current purpose. Remedy: Collapse Hierarchy, Inline Class, Remove Parameter.

## Couplers (CL-*)
CL-1. **Feature Envy** — a method accesses more data or methods from another class than from its own. Remedy: Move Method, Extract Method.
CL-2. **Inappropriate Intimacy** — two classes access each other's internal fields and methods excessively. Remedy: Move Method, Move Field, Extract Class, Hide Delegate, Change Bidirectional Association to Unidirectional.
CL-3. **Message Chains** — client navigates a chain of objects to reach data: `a.b().c().d()`. Remedy: Hide Delegate, Extract Method, Move Method.
CL-4. **Middle Man** — a class delegates almost all its work to another class, adding no value of its own. Remedy: Remove Middle Man, Inline Method, Replace Delegation with Inheritance.
CL-5. **Incomplete Library Class** — a third-party class is missing needed functionality that cannot be added by modifying the library. Remedy: Introduce Foreign Method, Introduce Local Extension.

---

# Procedure

## Audit Mode Procedure
1. **Scope the scan**
   - Confirm target language(s) and paths.
   - Confirm which categories to scan (default: all).
2. **Scan for smells by category**
   - For each active category, walk the target files and check each invariant.
   - Bloaters: measure method length, class size, parameter counts, repeated parameter groups, primitive-heavy signatures.
   - OO Abusers: find switch/if-else chains on type codes, fields used only conditionally, unused inherited members, duplicate-role classes with different signatures.
   - Change Preventers: identify classes changed for multiple reasons, changes that fan out across many files, mirrored inheritance hierarchies.
   - Dispensables: flag narrating comments, duplicated blocks, thin classes, data-only classes, unreachable code, unused abstractions.
   - Couplers: detect methods that reach into other classes, mutual field access, long navigation chains, pass-through delegators, missing library functionality.
3. **Classify each finding**
   - Assign invariant ID, severity, location, evidence, impact, and recommended refactoring.
4. **Produce AUDIT.md**
   - Follow the Required Output Schema below.

## Audit Mode (Repo Scanning Procedure)
Use Audit Mode when asked to scan a repo and identify code smell violations.

The assistant **must** follow this exact sequence:

1. **Identify smell surfaces**
   - Methods, classes, inheritance hierarchies, parameter lists, field usage patterns, call chains, delegation patterns.
2. **Locate hotspots**
   - Files or classes that exhibit multiple smells are high-priority targets.
3. **Map flows**
   - Trace how smelly code propagates: a Large Class often causes Shotgun Surgery; Data Clumps often accompany Long Parameter Lists.
4. **Check invariants**
   - Evaluate BL-*, OA-*, CP-*, DS-*, CL-* items against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.
5. **Produce findings using the required schema**
   - Every violation **must** be reported as a finding.
   - If a rule is satisfied across the scanned scope, it may be listed as "verified" (optional).
6. **Prioritize**
   - Rank findings by severity and blast radius (how many other smells or files are affected).

Audit Mode **must not** end without:
- at least one pass over the target files/directories
- a completed findings list (even if empty)

## Plan Mode Procedure
1. **Start from audit findings**
   - If no AUDIT.md exists, run Audit Mode first.
2. **Group related smells**
   - Smells in the same file or class should be addressed together.
3. **Rank refactoring steps**
   - Prioritize by: severity, blast radius, ease of fix, risk of behavior change.
4. **Propose refactoring sequence**
   - Each step names the technique, target file(s), and expected invariant(s) resolved.
5. **Define validation strategy**
   - Which tests must pass, what behavior must remain unchanged.
6. **Output contract**
   - Write `PLAN.md` containing:
     - Audit summary (findings count by category and severity)
     - Prioritized refactoring steps (numbered)
     - File map (which files are touched by which steps)
     - Risk notes (behavior-change potential per step)
     - Validation checklist

---

# Mandatory Validation Checklist (must include in every mode output)

## Repo safety
- [ ] Scan is repo-scoped; no external/system assumptions.
- [ ] No code was modified (audit/plan modes are read-only).

## Bloater checks
- [ ] BL-1 No long methods without justification.
- [ ] BL-2 No large classes without justification.
- [ ] BL-3 No primitive obsession at key domain boundaries.
- [ ] BL-4 No long parameter lists (>3–4 params) without justification.
- [ ] BL-5 No repeated data clumps across signatures/fields.

## OO Abuser checks
- [ ] OA-1 No complex switch/if-else chains on type codes where polymorphism applies.
- [ ] OA-2 No temporary fields that are conditionally set/used.
- [ ] OA-3 No refused bequests (unused inherited members).
- [ ] OA-4 No alternative classes with different interfaces for the same role.

## Change Preventer checks
- [ ] CP-1 No divergent change (class modified for unrelated reasons).
- [ ] CP-2 No shotgun surgery (one change scattered across many files).
- [ ] CP-3 No parallel inheritance hierarchies.

## Dispensable checks
- [ ] DS-1 No excessive narrating comments substituting for clarity.
- [ ] DS-2 No duplicate code blocks.
- [ ] DS-3 No lazy classes that add no value.
- [ ] DS-4 No data-only classes without behavior.
- [ ] DS-5 No dead code (unused variables, methods, classes).
- [ ] DS-6 No speculative generality (unused abstractions/hooks).

## Coupler checks
- [ ] CL-1 No feature envy (methods more intimate with other classes).
- [ ] CL-2 No inappropriate intimacy between classes.
- [ ] CL-3 No long message chains.
- [ ] CL-4 No middle-man classes that only delegate.
- [ ] CL-5 No incomplete library class workarounds needed.

---

# Output Contracts (strict)

## AUDIT.md (Audit Mode)
Must contain, in this order:
1. Scope (paths scanned, language, categories audited)
2. Summary (total findings by category and severity)
3. Findings (by invariant ID, using the schema below)
4. Hotspots (files/classes with the most smells)
5. Recommendations (ranked: must/should/could)
6. Validation checklist (completed)

## Required Output Schema (Audit Findings)
When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- categories audited:
- constraints:
- scope (paths scanned):

### Findings
For each finding, include:

- **ID:** `CS-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of BL-*, OA-*, CP-*, DS-*, CL-* invariants)
- **Location:** `path/to/file.ext:Lx-Ly`
- **Evidence:** short excerpt (1–8 lines)
- **Impact:** what becomes harder to change, test, or understand
- **Recommended Refactoring:** named technique(s) from the invariant's remedy list
- **Confidence:** `high | medium | low`

If there are no violations, output:
- **Findings:** `none`

### Validation Checklist Summary
- A copy of the checklist with each item marked:
  - `[x]` verified (no smell detected)
  - `[ ]` not verified / not scanned
  - `[!]` violated (must link to finding IDs)

## PLAN.md (Plan Mode)
Must contain, in this order:
1. Audit summary (findings count by category + severity)
2. Prioritized refactoring steps (numbered, with technique + target + invariants resolved)
3. File map (files touched per step)
4. Risk notes (behavior-change potential per step)
5. Validation strategy (tests + checklist)
6. Rollback strategy (how to revert safely)

---

# Severity Classification Guide
Use these thresholds as defaults; adjust for project context:

| Severity | Criteria |
|---|---|
| **critical** | Smell actively causes bugs, data loss, or security issues (rare for smells alone — usually combined with a defect) |
| **high** | Smell blocks testability, forces shotgun surgery on every change, or hides significant complexity |
| **medium** | Smell increases maintenance cost or cognitive load but does not block progress |
| **low** | Smell is a minor style issue or affects rarely-touched code |

---

# Guardrails (what not to do)
- Do not flag every long method — apply judgment; sequential setup code or test methods may be acceptably long.
- Do not flag data classes that are intentional DTOs, API response models, or configuration objects.
- Do not flag comments that explain *why* or document public APIs — only flag narrating comments that restate the code.
- Do not recommend refactoring stable, well-tested code solely because it exhibits a smell — weigh risk vs. benefit.
- Do not produce findings without file paths and line ranges; vague findings are not actionable.
- Do not modify code in audit or plan mode.

---

# Refusal Conditions
Refuse (or explain limitation) if:
- The user requests hidden/system access, secrets, or non-repo operations.
- The target files are binary, generated, or vendor-bundled (node_modules, dist, build artifacts).
- The user requests "fix all smells" without review — offer an audit first.
- The codebase has no source files in the declared language within the target paths.

---
