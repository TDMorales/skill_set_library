# Examples

Concrete, copy/paste-ready examples that match the SKILL invariants.

---

## Audit Mode (Repo Scanning Procedure)

Use Audit Mode when asked to scan a repo and identify violations of __SKILL_NAME__ rules.

The assistant **must** follow this exact sequence:

1. Identify relevant surfaces.
2. Map flows and call sites.
3. Check invariants with code evidence.
4. Produce findings using the required schema.
5. Propose minimal fixes.

Audit Mode **must not** end without:
- at least one pass over the key flows
- a completed findings list (even if empty)

---

## Required Output Schema (Audit Findings)
When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- scope (paths reviewed):
- constraints:

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

## Example Index

- `example_language.md`
