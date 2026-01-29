---
name: websocket-management
description: Enforces production-grade WebSocket connection management with strict invariants for capacity limits, user-to-connection mapping, health verification, and stale connection cleanup.
compatibility: TypeScript/JavaScript, Python
short-description: Enforce WebSocket connection implementation/management.
---

# WebSocket Connection Management

This skill enforces **correct, resilient, and leak-free WebSocket connection management**.  
It is designed to prevent silent failures such as stale connections, capacity overruns, inconsistent state, and undetected half-open sockets.

This skill is **prescriptive**, not advisory.

---

## When to Use This Skill

Use this skill whenever:

- Building real-time features over WebSockets
- Managing multiple users, rooms, or lobbies
- Enforcing connection limits
- Requiring reliable presence, direct messaging, or broadcasts
- Operating in environments where clients may disconnect ungracefully

---

## Required Inputs / Assumptions

Before applying this skill, the assistant **must determine or explicitly assume**:

1. **Server framework** (e.g. FastAPI/Starlette, ws, Socket.IO-like abstraction)
2. **User connection model**
   - Single active connection per user **OR**
   - Multiple concurrent connections per user (multi-device)
3. **Capacity limits**
   - Global max connections
   - Per-room / per-lobby max connections
4. **Health policy**
   - Ping interval
   - Pong timeout
   - Stale threshold
5. **Cleanup trigger**
   - Background sweep loop **or**
   - Event-driven cleanup only

If any item is unknown, the assistant must choose a sane default and state it explicitly.

---

## Non-Negotiable Invariants

These conditions **must always hold**:

### Connection State
- A WebSocket registered as active **must** have corresponding metadata.
- No internal mapping may reference a disconnected WebSocket.
- `disconnect()` is **idempotent** and safe to call multiple times.

### User Mapping
- The user-to-connection policy is explicit and enforced.
- Duplicate user connections are either:
  - Rejected, or
  - Replaced, or
  - Tracked as a set  
  (Silent overwrites are forbidden.)

### Capacity
- Capacity checks occur **before** a connection is committed to internal state.
- Reject reasons are stable, machine-readable strings.

### Health
- Pending pings are always cleaned up (no leaks).
- Any inbound message updates last-seen state.
- Stale connections are eventually removed.

---

## Procedure (Mandatory)

When implementing or reviewing WebSocket management, the assistant must follow this exact sequence:

1. Define connection and user mapping strategy
2. Define capacity limits and rejection semantics
3. Implement connection registration
4. Implement idempotent disconnection
5. Implement broadcast and direct messaging with send-failure cleanup
6. Implement ping/pong health verification
7. Implement stale connection cleanup mechanism
8. Add observability hooks
9. Apply security constraints
10. Run the validation checklist

Steps may not be skipped.

---

## Audit Mode (Repo Scanning Procedure)

Use Audit Mode when asked to **scan a repo** containing WebSocket usage and identify violations of this skill.

The assistant **must** follow this exact sequence:

1. **Identify WebSocket surfaces**
   - Server entry points (routes, handlers, consumers, gateways)
   - Client connection points (browser `WebSocket`, mobile, node clients)

2. **Identify the state owner**
   - Locate the component responsible for:
     - connection registration
     - connection storage (maps/sets)
     - disconnection cleanup
     - broadcast/direct messaging
   - If no centralized owner exists, treat this as a finding.

3. **Map flows**
   - Trace (at minimum):
     - connect flow (auth → capacity → registration)
     - receive flow (message handling + last-seen updates)
     - send flow (broadcast/direct send + failure handling)
     - disconnect flow (explicit and implicit paths)
     - health flow (ping/pong + stale enforcement)
     - background cleanup flow (scheduler / startup integration)

4. **Check invariants**
   - Evaluate each of the Validation Checklist items against code evidence.
   - Prefer concrete evidence (file paths + line ranges) over assumptions.

5. **Produce findings using the required schema**
   - Every violation or missing requirement **must** be reported as a finding.
   - If a rule is satisfied, it may be listed as “verified” (optional).

6. **Propose minimal fixes**
   - Fixes must be:
     - scoped
     - consistent with the stated user connection model
     - safe under partial failure
   - Prefer small diffs over rewrites unless architecture is fundamentally missing.

Audit Mode **must not** end without:
- at least one pass over server + client surfaces (if both exist)
- a completed findings list (even if empty)

---

## Required Output Schema (Audit Findings)

When in Audit Mode, output **must** follow this format:

### Assumptions
- server framework:
- user connection model:
- capacity limits:
- health policy:
- cleanup trigger:

### Findings
For each finding, include:

- **ID:** `WS-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of the Validation Checklist items or named invariant)
- **Location:** `path/to/file.ext:Lx-Ly`
- **Evidence:** short excerpt (1–8 lines)
- **Impact:** what breaks in production
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

## Reference Implementation

Concrete implementations **must** be placed in `examples/` and include:

- Server connection manager
- Server WebSocket endpoint
- Client ping/pong handling

`SKILL.md` must not embed large code blocks.

---

## Background Cleanup Loop

Automatic cleanup is required.

At least one of the following must exist:

- Periodic health sweep:
  - Ping active users
  - Disconnect on timeout
  - Disconnect on stale last-seen timestamp
- Equivalent framework-native lifecycle hook

Cleanup logic must tolerate partial or already-removed state.

---

## Observability Requirements

Implementations must expose:

- Connection accepted / rejected (with reason)
- Disconnect events (with cause)
- Ping timeout counts
- Current connection counts
- Capacity utilization

Logging must not throw or block the event loop.

---

## Security Notes

At minimum:

- Authenticate users **before** registering connections
- Validate room/lobby access
- Enforce origin checks where applicable
- Apply message rate limiting or backpressure
- Never trust client-supplied identifiers without verification

---

## Validation Checklist (Mandatory)

Before producing a final answer, the assistant must confirm:

- [ ] User-to-connection policy is explicit and enforced
- [ ] Disconnect logic is idempotent
- [ ] All internal maps are cleaned on disconnect
- [ ] Broadcast iteration cannot mutate during iteration
- [ ] Send failures trigger cleanup
- [ ] Pending pings cannot leak
- [ ] Stale connections are eventually removed
- [ ] Capacity checks occur before registration
- [ ] Observability is present
- [ ] Security checks are applied

If any item fails, the implementation is incomplete.

---

## Common Mistakes (Forbidden)

- Accepting connections before capacity checks
- Overwriting user connections implicitly
- Relying solely on TCP/WebSocket close events
- Never pinging idle clients
- Ignoring send failures
- Letting cleanup logic throw

---

## Related Patterns

- sse-streaming
- graceful-shutdown
- rate-limiting
- connection-pooling