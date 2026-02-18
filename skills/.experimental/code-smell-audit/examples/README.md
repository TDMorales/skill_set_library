# Examples

Concrete before/after examples for every code smell invariant. Each example shows the smell in context and the refactored version that eliminates it. Adapt names and structures to your domain.

---

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

---

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
- **Recommended Refactoring:** named technique(s)
- **Confidence:** `high | medium | low`

If there are no violations, output:
- **Findings:** `none`

### Validation Checklist Summary
- A copy of the checklist with each item marked:
  - `[x]` verified (no smell detected)
  - `[ ]` not verified / not scanned
  - `[!]` violated (must link to finding IDs)

---

## Example Files Index

### Bloaters (BL-1 through BL-5)
- `bloaters_python.md` — Long Method, Large Class, Primitive Obsession, Long Parameter List, Data Clumps
- `bloaters_typescript.md`

### Object-Orientation Abusers (OA-1 through OA-4)
- `oo_abusers_python.md` — Switch Statements, Temporary Field, Refused Bequest, Alt Classes w/ Different Interfaces
- `oo_abusers_typescript.md`

### Change Preventers (CP-1 through CP-3)
- `change_preventers_python.md` — Divergent Change, Shotgun Surgery, Parallel Inheritance Hierarchies
- `change_preventers_typescript.md`

### Dispensables (DS-1 through DS-6)
- `dispensables_python.md` — Comments, Duplicate Code, Lazy Class, Data Class, Dead Code, Speculative Generality
- `dispensables_typescript.md`

### Couplers (CL-1 through CL-5)
- `couplers_python.md` — Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man, Incomplete Library Class
- `couplers_typescript.md`
