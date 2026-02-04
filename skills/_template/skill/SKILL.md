---
name: __SKILL_NAME__
description: __SKILL_DESCRIPTION__
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
    - "AUDIT.md (audit mode)"
    - "PLAN.md (plan mode)"
    - "CHANGES.md (implement mode)"
---

# Purpose
One paragraph describing the skill's goal and scope.

---

# When to Use
List the conditions that should trigger this skill.

---

# Definitions
Short, precise definitions of domain terms used in the skill.

---

# Invariants (must always hold)
- INV-1: ...
- INV-2: ...

---

# Procedure

## Audit Mode (repo scanning)
1. Identify relevant surfaces.
2. Map flows and call sites.
3. Check invariants with code evidence.
4. Produce findings using required schema.
5. Propose minimal fixes.

## Plan Mode (design-only)
1. Identify the seam.
2. Propose minimal structure.
3. Map files and interfaces.
4. Define validation plan.

## Implement Mode (code changes)
1. Introduce core types.
2. Refactor call sites safely.
3. Add or update tests.
4. Self-review against invariants.

---

# Validation Checklist
- [ ] Item 1
- [ ] Item 2

---

# Output Contracts

## AUDIT.md
1. Scope
2. Findings mapped to invariants
3. Risks
4. Recommendations
5. Next steps

## PLAN.md
1. Goal + constraints
2. Proposed structure
3. Implementation steps
4. Validation plan
5. Rollback strategy

## CHANGES.md
1. Summary of changes
2. File-by-file breakdown
3. Invariant mapping
4. How to validate
5. Notes

---

# Required Output Schema (Audit Findings)

### Assumptions
- target language:
- constraints:
- scope (paths reviewed):

### Findings
- **ID:** `__SKILL_ID__-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (invariant ID)
- **Location:** `path/to/file.ext:Lx-Ly`
- **Evidence:** short excerpt (1–8 lines)
- **Impact:** what breaks or becomes harder to change
- **Minimal Fix:** concrete change
- **Confidence:** `high | medium | low`

If there are no violations, output:
- **Findings:** `none`

### Validation Checklist Summary
- [x] verified
- [ ] not verified / missing
- [!] violated (link to finding IDs)

---

# Refusal Conditions
List the exact conditions that block execution.
