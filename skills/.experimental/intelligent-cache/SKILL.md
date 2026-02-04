---
name: intelligent-cache
description: Implement and validate a multi-layer intelligent caching system with type-specific TTLs, get-or-generate semantics, and graceful invalidation.
license: MIT
compatibility: TypeScript/JavaScript, Python
category: performance
time: 5h
source: drift-masterguide
---

# Intelligent Cache Skill

## 1. Purpose

Implement a production-safe caching system that:
- Supports **type-specific TTLs**
- Uses **memory-first with optional persistence**
- Enforces a **single get-or-generate entry point**
- Prevents **cache stampedes**
- Exposes **observability signals** for optimization

This skill produces **working cache infrastructure**, not abstractions.

---

## 2. When to Apply

Apply this skill when **all** are true:
- Cached data varies in freshness requirements
- Generation cost is non-trivial (AI, aggregation, external calls)
- Repeated reads are expected
- Cache invalidation must be explicit and controlled

Do **not** apply for trivial, request-scoped memoization.

---

## 3. Definitions

- **Cache Type**: A named content category with its own TTL policy.
- **Cache Key**: A deterministic identifier within a cache type.
- **TTL**: Time-to-live, enforced per cache type.
- **Memory Layer**: In-process cache for fastest access.
- **Persistence Layer**: Optional durable store (DB, Redis, etc.).
- **Get-or-Generate**: A single API that returns cached data or generates and stores it.
- **Stampede**: Concurrent cache misses causing duplicate generation.

---

## 4. Hard Invariants

The following invariants are mandatory and non-negotiable:

1. **Type-Specific TTLs**
   - Every cache type MUST map to a TTL.
   - A default TTL is only allowed if explicitly declared.

2. **Single Entry Point**
   - All reads MUST go through `getOrGenerate` / `get_or_generate`.

3. **Two-Layer Semantics**
   - Memory is checked first.
   - Persistence is checked second (if enabled).
   - Persistence hits MUST be promoted to memory.

4. **Expiry Enforcement**
   - Expired entries MUST NOT be returned.
   - Expired memory entries MUST be deleted on access.

5. **Stampede Prevention**
   - Concurrent requests for the same `(type, key)` MUST share one generator execution.

6. **Observability**
   - Cache entries MUST record:
     - `generatedAt`
     - `expiresAt`
     - `generationTimeMs` (optional but preferred)
   - Callers MUST be told whether data came from cache.

7. **Graceful Degradation**
   - If persistence fails or is unavailable, memory caching MUST continue.
   - Hard failure is only allowed if explicitly required by the repo.

8. **Explicit Invalidation**
   - Support invalidating:
     - A single cache key
     - All keys of a cache type

---

## 5. Required Data Model

Each cached item MUST contain at minimum:

- Unique identifier
- Cache type
- Cache key
- Cached content (raw + structured if applicable)
- Generation timestamp
- Expiry timestamp
- Optional generation duration

Exact field names may vary by language.

---

## 6. Procedure

Follow these steps in order:

1. Identify all cacheable content types in the repo.
2. Define a TTL mapping covering every cache type.
3. Implement an in-memory cache keyed by `type:key`.
4. Define a persistence adapter interface (optional but supported).
5. Implement read flow:
   - Check memory
   - Check persistence
   - Reject expired entries
6. Implement get-or-generate:
   - Lock per `(type,key)`
   - Deduplicate concurrent generation
   - Measure generation time
7. Promote persistence hits into memory.
8. Implement invalidation methods.
9. Implement expired-entry cleanup.
10. Expose cache metadata to callers.

---

## Audit Mode (Repo Scanning Procedure)

Use Audit Mode when asked to scan a repo and identify violations of the Intelligent Cache rules.

The assistant **must** follow this exact sequence:

1. **Identify cache surfaces**
   - Cache modules, cache helpers, and any get-or-generate functions.
   - Call sites that read/write cached data.
2. **Map cache types**
   - List every cache type and its TTL mapping.
   - Confirm a default TTL is declared only if explicitly allowed.
3. **Trace read/write flows**
   - Memory check → persistence check → promotion to memory.
   - Expiry handling and cleanup.
4. **Check invariants**
   - Evaluate each checklist item against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.
5. **Produce findings using the required schema**
   - Every violation or missing requirement **must** be reported as a finding.
   - If a rule is satisfied, it may be listed as “verified” (optional).
6. **Propose minimal fixes**
   - Fixes must be scoped, behavior-preserving, and aligned with constraints.
   - Prefer small diffs over rewrites unless architecture is fundamentally missing.

Audit Mode **must not** end without:
- at least one pass over a cache read path and a write path
- a completed findings list (even if empty)

---

## 7. Validation Checklist

All items below MUST pass:

- [ ] Every cache type has a TTL
- [ ] No code path bypasses get-or-generate
- [ ] Expired entries are never returned
- [ ] Persistence hits populate memory
- [ ] Concurrent misses do not duplicate generation
- [ ] Single-key invalidation works
- [ ] Type-wide invalidation works
- [ ] Expired memory entries are removed
- [ ] Persistence cleanup exists or TTL is enforced
- [ ] Cache failures do not crash the system
- [ ] Callers receive cache hit/miss signal

Failure of any item blocks completion.

---

## 8. Output Contract

When this skill is executed, the agent MUST produce:

- A cache module implementing all invariants
- At least one real integration point using get-or-generate
- A short summary describing:
  - Cache types and TTL choices
  - Persistence strategy
  - Stampede-prevention mechanism
  - Cleanup strategy

---

## Required Output Schema (Audit Findings)

When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- cache surfaces (paths reviewed):
- persistence strategy:
- constraints:

### Findings
For each finding, include:

- **ID:** `IC-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of the invariants or checklist items)
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

---

## 9. Refusal Conditions

The skill MUST refuse execution if:

- Persistence is required but no storage mechanism is permitted
- Cache TTLs are undefined or intentionally unbounded
- Sensitive or secret data is requested to be cached insecurely
- The repo forbids shared state but requires caching

In refusal cases, the agent MUST explain the blocking condition and list viable alternatives.
