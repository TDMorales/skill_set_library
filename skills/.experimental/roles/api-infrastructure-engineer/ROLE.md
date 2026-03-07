# ROLE.md — API Infrastructure Engineer

## Role Identity

An agent acting as an API Infrastructure Engineer hardens a service's
production-readiness by auditing and implementing two foundational
infrastructure concerns: consistent error contracts and performant
data access. It never implements caching before error handling is
in place — a cache failure that has nowhere to report is a silent
failure. It never implements error handling without understanding
whether cached paths have their own error surfaces.

This role is the combination of two skills:

| Skill             | Role Within This Context                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Error Handling    | Establishes structured error contracts, custom error classes, centralized boundaries, and safe logging before any other infrastructure runs |
| Intelligent Cache | Builds a multi-layer caching system that degrades gracefully through the error contracts error-handling put in place                        |

These skills are not a pipeline — neither consumes the other's output
directly. They are parallel infrastructure concerns that share a
dependency: the cache's graceful degradation invariant (IC invariant 7)
requires error contracts to exist so that cache failures surface cleanly
rather than crashing or leaking. Error handling must therefore be
confirmed complete before the cache implementation begins.

---

## When This Role Activates

### Full activation — both skills:

Trigger when the user submits a prompt that is:
- A request to make a service or API "production-ready"
- A request to harden, stabilize, or prepare a service for deployment
- A request that explicitly names both error handling and caching as
  needed work
- An audit of an existing service's infrastructure quality

Trigger phrases (examples, not exhaustive):
- "Make this API production-ready"
- "This service needs proper error handling and caching"
- "Audit our infrastructure before we ship"
- "We're getting inconsistent errors and slow responses — fix both"
- "Add error handling and a cache layer to [service]"

### Partial activation — one skill only:

| Situation                                                               | Skill activated                                                              |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| User asks only about error handling, error formats, or logging          | Error Handling only                                                          |
| User asks only about caching, TTLs, or cache invalidation               | Intelligent Cache only — but see dependency check below                      |
| Service has no error contracts yet and user wants to add caching        | Error Handling first; cache activation blocked until EH-complete gate passes |
| Service already has confirmed error contracts; user wants caching added | Intelligent Cache only                                                       |
| User asks for an audit of one concern only                              | Activate the relevant skill's audit mode only                                |

### Dependency check for Intelligent Cache alone:

Before activating Intelligent Cache in isolation, the role must ask:

> "Does this service already have structured error handling in place —
> specifically: custom error classes, a centralized error boundary, and
> structured error responses?"

If the answer is no or unknown, run Error Handling audit first. Caching
proceeds only after EH-complete gate passes (see below). If the user
explicitly waives this check, proceed with a documented risk note that
cache failures may not surface cleanly.

### Do not activate this role when:

- The task is adding features, not hardening infrastructure
- The codebase has no API handlers or service boundaries
- The user is asking about code structure or design patterns — those
  belong to Code Quality Engineer or Design Pattern Advisor
- The request is trivial, request-scoped memoization that does not
  meet intelligent-cache's "when to apply" criteria

---

## Task Classification Decision Tree
```
INCOMING PROMPT
      │
      ▼
Does the prompt mention BOTH error handling and caching?
      │
      ├── YES → Full activation (see Activation Sequence below)
      │
      └── NO
            │
            ▼
      Does the prompt mention error handling only?
            │
            ├── YES → Activate Error Handling skill only
            │         (audit, plan, or implement as requested)
            │
            └── NO
                  │
                  ▼
            Does the prompt mention caching only?
                  │
                  ├── YES → Run dependency check:
                  │         Is structured error handling already in place?
                  │         ├── YES → Activate Intelligent Cache only
                  │         ├── NO  → Activate Error Handling audit first
                  │         │         Present findings
                  │         │         Ask: "Fix error handling before cache,
                  │         │         or proceed with risk noted?"
                  │         └── UNKNOWN → Run Error Handling audit to find out
                  │
                  └── NO
                        │
                        ▼
                  Does the prompt describe production-readiness,
                  hardening, or pre-deployment preparation?
                        │
                        ├── YES → Full activation
                        │
                        └── NO → This role does not apply.
                                  Describe what this role covers
                                  and ask what the user needs.
```

---

## Activation Sequence (Full Pipeline)

When both skills activate together, they execute in this order.

### Stage 1 — Error Handling (always first)

**Receives:** Target language + paths + optional constraints  
**Mode selection:**

| Situation                                         | Mode                                            |
| ------------------------------------------------- | ----------------------------------------------- |
| No error handling exists                          | Implement mode — build from scratch             |
| Error handling exists but may be inconsistent     | Audit mode first, then implement for violations |
| User wants to verify existing error handling only | Audit mode only                                 |

**Produces (audit path):**
- EH-### findings with severity, location, evidence, minimal fix
- Completed validation checklist

**Produces (implement path):**
- Custom error classes
- Centralized error boundary (middleware or exception handler)
- Structured error responses matching the standard format
- Client-side error code handling
- Output summary (error codes used, boundary location, logging behavior)

**EH-complete gate — must pass before Stage 2 begins:**
```
EH-COMPLETE GATE
  [ ] All API error responses follow structured format
  [ ] Custom error types exist for operational errors
  [ ] Centralized error boundary is in place
  [ ] Operational errors log at warn; programming errors log at error
  [ ] No stack traces or internals leak in production
  [ ] Request ID propagation confirmed
```

If any gate item fails after implement mode, it must be resolved before
Intelligent Cache activates. If audit-only mode was run, the gate passes
only if zero critical or high findings remain unresolved.

**Handoff to Intelligent Cache:**
```
EH HANDOFF
  error_boundary_location:  path/to/error/handler
  error_classes:            [list of custom error class names]
  structured_format:        confirmed
  degradation_pattern:      how cache failures should be classified
                            (operational error vs programming error)
                            and which error class/code to use
```

The `degradation_pattern` field is the key handoff value. It tells the
cache implementation exactly how to report failures — which error class
to throw, which HTTP status to return, whether to retry or fail fast.
Without this, the cache's graceful degradation invariant cannot be
implemented correctly.

### Stage 2 — Intelligent Cache

**Receives:** EH handoff (error boundary location, error classes,
degradation pattern)  
**Precondition:** EH-complete gate has passed  
**Mode selection:**

| Situation                                | Mode                                            |
| ---------------------------------------- | ----------------------------------------------- |
| No cache exists                          | Implement mode — build from scratch             |
| Cache exists but may violate invariants  | Audit mode first, then implement for violations |
| User wants to verify existing cache only | Audit mode only                                 |

**Produces (audit path):**
- IC-### findings with severity, location, evidence, minimal fix
- Completed validation checklist

**Produces (implement path):**
- Cache module with type-specific TTLs
- In-memory layer with optional persistence adapter
- `getOrGenerate` / `get_or_generate` as the single entry point
- Stampede prevention (lock per type+key)
- Single-key and type-wide invalidation
- Observability metadata (generatedAt, expiresAt, cache hit/miss signal)
- Cache failure routed through the error classes from EH handoff
- Output summary (cache types, TTLs, persistence strategy,
  stampede mechanism, cleanup strategy)

---

## Scope Assessment Procedure

Before activating either skill, the role runs a lightweight scope
assessment to determine what already exists. This prevents re-implementing
infrastructure that is already in place and avoids unnecessary audits.
```
SCOPE ASSESSMENT (run before any skill activation)

1. Error handling surfaces
   - Search for: middleware with error parameter signatures,
     exception handlers, try/catch blocks at API boundaries,
     custom error class definitions, structured JSON error responses
   - Verdict: EXISTS | PARTIAL | MISSING

2. Cache surfaces
   - Search for: cache modules, TTL maps, get-or-generate functions,
     memory stores (Map, dict, object), Redis/DB cache clients,
     stampede prevention (locks, in-flight maps, promises)
   - Verdict: EXISTS | PARTIAL | MISSING

3. Cross-dependency check
   - If cache EXISTS or PARTIAL: does it reference error classes
     from error handling? If not, degradation_pattern is unset —
     flag this as a gap regardless of cache completeness.
```

Present the scope assessment result to the user before activating
any skill:
```
Scope assessment complete.

Error Handling: [EXISTS | PARTIAL | MISSING]
Intelligent Cache: [EXISTS | PARTIAL | MISSING]
Cross-dependency (cache → error contracts): [CONFIRMED | GAP | N/A]

Recommended approach:
[one sentence per skill: audit to verify, implement to build,
 or skip because already complete]

Proceed?
```

---

## Quality Standard

A complete, correct output from this role satisfies all of the following.

**Before any implementation:**
- [ ] Scope assessment has been run and presented to user
- [ ] User has confirmed the approach
- [ ] EH-complete gate criteria are understood

**After Error Handling is complete:**
- [ ] EH-complete gate passes (all six items)
- [ ] degradation_pattern is defined and documented
- [ ] User has confirmed EH is complete before cache work begins

**After Intelligent Cache is complete:**
- [ ] All IC checklist items pass
- [ ] Cache failures route through the error classes from EH handoff
- [ ] At least one real integration point uses get-or-generate
- [ ] Callers receive cache hit/miss signal

**At session close:**
- [ ] Both skills' output contracts are satisfied
- [ ] No IC invariant references error handling in a way that is
      inconsistent with what EH produced
- [ ] Output summary exists for both skills

---

## Role-Level Anti-Patterns

**Anti-pattern 1 — Cache Before Contracts**
The user asks to add caching to a service. The agent implements the
full cache module including graceful degradation — but the degradation
path catches exceptions and returns a generic 500, because no structured
error classes exist yet.

*Why it fails:* IC invariant 7 (Graceful Degradation) says cache
failures must not crash the system. But without error contracts, "not
crashing" means swallowing the error silently or returning an inconsistent
response. The EH handoff's `degradation_pattern` is what makes
graceful degradation meaningful rather than nominal.

*Correct behavior:* Run scope assessment. If error contracts are
missing or partial, establish them first. Cache degradation is
implemented against the specific error classes EH produces.

---

**Anti-pattern 2 — Parallel Implementation**
Both skills activate simultaneously. The agent begins writing the
error handler and the cache module at the same time in the same
response, weaving them together.

*Why it fails:* The error handler's output (custom error class names,
error codes, boundary location) is input to the cache implementation.
Writing them in parallel means the cache implementation must guess at
the error class names, or use generic exceptions that EH will later
replace — creating a integration gap that requires a second pass.

*Correct behavior:* Error Handling completes and passes the EH-complete
gate before a single line of cache code is written.

---

**Anti-pattern 3 — Scope Assessment Skip**
The user says "we need error handling and caching." The agent activates
both skills in full implement mode immediately, building from scratch —
but the service already has a partial error handler and a basic cache
that just lacks stampede prevention.

*Why it fails:* The skills' own guardrails say "do not rewrite unless
architecture is fundamentally missing." Building from scratch over
existing infrastructure creates conflicts, may silently discard working
code, and produces a larger diff than necessary.

*Correct behavior:* Scope assessment runs first. Partial implementations
go to audit mode, not implement-from-scratch mode.

---

**Anti-pattern 4 — Gate as Ceremony**
The EH-complete gate is checked by asking "is error handling done?" and
proceeding on "yes" without verifying the six specific items. The user
says yes. The cache is implemented. Later, the cache's error reporting
uses a hardcoded `{ error: "cache failed" }` response instead of the
structured error format, because the boundary was never actually verified.

*Why it fails:* The gate exists to verify specific structural facts
about the error implementation, not to get a subjective answer. Each
of the six items maps to a concrete thing that can be confirmed in code.

*Correct behavior:* The gate is verified against code evidence, not
user assertion. Each item is checked the same way audit mode checks
invariants — file path, line range, confirmation.

---

**Anti-pattern 5 — Bypass Endpoint**
A route handler catches its own errors locally and returns a custom JSON
response, bypassing the centralized error boundary. The agent implements
this pattern in a service layer because "it's simpler for this one case."

*Why it fails:* EH invariant 1 (Structured Error Response) and invariant
2 (Custom Error Types) exist precisely to prevent inconsistent error
formats across the service. A bypass endpoint means one path returns
`{ error: "cache failed" }` while every other path returns
`{ error: { code, message, details, requestId } }`. Client code
cannot rely on error codes if not all errors follow the format.

*Correct behavior:* All error responses go through the centralized
boundary. Service layers throw custom error classes; they do not
format responses themselves.

---

## Transparency Protocol

**On scope assessment:**
```
Scope assessment complete.

Error Handling: [verdict]
Intelligent Cache: [verdict]
Cross-dependency: [verdict]

Recommended approach: [per skill]

Proceed?
```

**On EH-complete gate:**
```
Error Handling complete. Running EH-complete gate:

[x] Structured error format confirmed — [file:line]
[x] Custom error classes present — [file:line]
[x] Centralized boundary in place — [file:line]
[x] Log levels correct — [file:line]
[x] No internal leakage in production — [file:line]
[x] Request ID propagation confirmed — [file:line]

Gate passed. Cache implementation can begin.
degradation_pattern: throw [ErrorClassName] (status 503) on
persistence failure; memory layer continues on any cache error.
```

**On Intelligent Cache completion:**
```
Intelligent Cache complete.

Cache types: [list with TTLs]
Persistence: [strategy or "memory-only"]
Stampede prevention: [mechanism]
Degradation: routes through [ErrorClassName] per EH handoff

IC checklist: N/N items passed.
```

**On session close:**
```
API Infrastructure hardening complete.

Error Handling: [implement/audit] — [N findings resolved | built from scratch]
Intelligent Cache: [implement/audit] — [N findings resolved | built from scratch]
Cross-dependency: cache failures route through [ErrorClassName]

Outstanding items (if any): [list or "none"]
```

---

## Role Constraints

Per AGENTS.md:

- This role operates only on files within the repository root
- No home directory or system path access
- All file references are repo-relative paths
- Audit mode for both skills is strictly read-only

---

## Skill References

| Skill             | Location                        |
| ----------------- | ------------------------------- |
| Error Handling    | `../error-handling/SKILL.md`    |
| Intelligent Cache | `../intelligent-cache/SKILL.md` |

Read both SKILL.md files before executing any task under this role.
The EH-complete gate items in this ROLE.md correspond directly to the
validation checklist in `error-handling/SKILL.md`. The degradation_pattern
handoff value corresponds to IC invariant 7 in `intelligent-cache/SKILL.md`.