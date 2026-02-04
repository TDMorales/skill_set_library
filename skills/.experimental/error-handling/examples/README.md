# Examples

Concrete, copy/paste-ready examples that match the SKILL invariants. Keep these minimal and adapt names to your domain.

---

## Audit Mode (Repo Scanning Procedure)

Use Audit Mode when asked to scan a repo and identify violations of error-handling rules.

The assistant **must** follow this exact sequence:

1. **Identify error surfaces**
   - API handlers, middleware, background jobs, and client error layers.
2. **Trace response formatting**
   - Confirm all error responses follow the standard format.
3. **Check error types**
   - Locate custom error classes and their usage.
4. **Inspect logging behavior**
   - Distinguish operational vs programming errors.
5. **Check invariants**
   - Evaluate EH-* items against code evidence.
6. **Produce findings using the required schema**
   - Every violation or missing requirement MUST be reported as a finding.
7. **Propose minimal fixes**
   - Prefer scoped changes over rewrites.

Audit Mode **must not** end without:
- at least one pass over an error path
- a completed findings list (even if empty)

---

## Required Output Schema (Audit Findings)

When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- constraints:
- scope (paths reviewed):

### Findings
For each finding, include:

- **ID:** `EH-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of EH-* invariants)
- **Location:** `path/to/file.ext:Lx-Ly`
- **Evidence:** short excerpt (1-8 lines)
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

---

## Example Index

- `error_handling_typescript.md`
- `error_handling_python.md`
