# Examples

Before/after examples for each prioritized refactoring technique. Each example shows the code before, the mechanical steps, and the result after applying the technique. Adapt names and structures to your domain.

---

## Implement Mode Procedure (summary)

The assistant **must** follow this sequence when applying a refactoring:

1. **Identify technique and target**
   - Confirm which invariant ID applies and where (file + symbol/line range).
2. **Verify preconditions**
   - Ensure the technique's preconditions are met (e.g., block is self-contained for Extract Method).
3. **Apply mechanical steps in order**
   - Follow the canonical sequence; do not skip steps.
4. **Update call sites**
   - Find every reference to the refactored symbol and update it.
5. **Preserve or add tests**
   - Existing tests must still pass; add tests at the new seam if none exist.
6. **Self-review with invariants**
   - Verify the technique's post-conditions hold.

Implement Mode **must not** end without:
- verification that behavior is preserved
- a completed CHANGES.md

---

## Example Files Index

### Composing Methods (CM-1, CM-2)
- `composing_methods_python.md` — Extract Method, Decompose Conditional
- `composing_methods_typescript.md`

### Moving Features between Objects (MF-1 through MF-7)
- `moving_features_python.md` — Move Method, Move Field, Extract Class, Inline Class, Hide Delegate, Remove Middle Man, Introduce Foreign Method / Local Extension
- `moving_features_typescript.md`

### Organizing Data (OD-1, OD-2, OD-3)
- `organizing_data_python.md` — Replace Data Value with Object, Encapsulate Field/Collection, Replace Type Code with Subclasses
- `organizing_data_typescript.md`

### Simplifying Conditional Expressions (SC-1)
- `simplifying_conditionals_python.md` — Replace Conditional with Polymorphism
- `simplifying_conditionals_typescript.md`

### Simplifying Method Calls (SM-1, SM-2, SM-3)
- `simplifying_method_calls_python.md` — Rename Method, Introduce Parameter Object, Preserve Whole Object
- `simplifying_method_calls_typescript.md`

### Dealing with Generalization (DG-1, DG-2, DG-3)
- `generalization_python.md` — Extract Superclass/Interface, Collapse Hierarchy, Replace Inheritance with Delegation
- `generalization_typescript.md`
