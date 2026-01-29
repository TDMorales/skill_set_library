# WebSocket Management – Examples

This directory contains **reference implementations** that satisfy the requirements defined in `SKILL.md`.

These files are **examples**, not a framework.  
They are intended to be copied, adapted, and integrated into an existing application.

Do not embed large code blocks directly into `SKILL.md`.

---

## Example Files Overview

### Server-Side (Python / FastAPI)

| File | Purpose |
|----|----|
| `server_fastapi_connection_manager.md` | Core connection manager enforcing invariants |
| `server_fastapi_endpoint.md` | WebSocket endpoint wiring auth, lifecycle, and messaging |
| `server_health_sweep_loop.md` | Background stale-connection cleanup loop |

### Client-Side (TypeScript)

| File | Purpose |
|----|----|
| `client_websocket_client.md` | Client ping/pong handling and message dispatch |

---

## server_fastapi_connection_manager.md

This file contains the **authoritative connection manager**.

It demonstrates:

- Explicit user-to-connection policy (single session per user)
- Idempotent `disconnect()` logic
- Capacity enforcement (global + per-lobby)
- Safe broadcast iteration
- Send-failure cleanup
- Ping tracking without leaks

### Key Guarantees

- No stale WebSocket references remain after disconnect
- Duplicate user connections are handled deterministically
- Internal state remains consistent under partial failures

This file satisfies:
- Non-Negotiable Invariants
- Connection State Management
- Messaging Semantics

---

## server_fastapi_endpoint.md

This file demonstrates **correct WebSocket lifecycle wiring**.

It shows:

- Authentication before registration
- Capacity checks before committing state
- Main receive loop with:
  - `health_pong` handling
  - application message handling
- Safe disconnect handling on:
  - client disconnect
  - unexpected exceptions

### Important Notes

- Accepting a WebSocket does not imply it is registered
- All cleanup flows through the manager
- Endpoint code remains thin and declarative

This file satisfies:
- Required Procedure steps
- Security requirements
- Correct lifecycle integration

---

## server_health_sweep_loop.md

This file demonstrates **automatic stale connection cleanup**.

It includes:

- Periodic ping scheduling
- Pong timeout handling
- Last-seen timestamp enforcement
- Defensive cleanup (safe even if state already removed)

### Integration Points

This loop should be started via:
- FastAPI startup event, or
- Application task group, or
- Framework-native background task system

This file satisfies:
- Background Cleanup Loop requirement
- Health invariants
- Leak prevention

---

## client_websocket_client.md

This file demonstrates **minimal client responsibilities**.

It includes:

- Immediate response to `health_ping`
- Message dispatch separation
- No server-specific assumptions beyond protocol

### Client Contract

Clients must:
- Respond to health pings immediately
- Avoid blocking the message handler
- Treat reconnects as normal behavior

This file satisfies:
- Health verification contract
- Client/server symmetry

---

## Policy Variations

These examples assume:

- **Single active connection per user**
- New connections replace old ones deterministically

If multi-device support is required:
- Change `user_id -> WebSocket` to `user_id -> Set<WebSocket>`
- Update direct messaging semantics accordingly
- Re-run the Validation Checklist in `SKILL.md`

Do not mix policies implicitly.

---

## Required Validation

Before adapting any example:

- Review the Validation Checklist in `SKILL.md`
- Confirm the user connection policy matches your use case
- Confirm cleanup logic is integrated and running
- Confirm observability hooks exist

If any requirement is missing, the implementation is incomplete.

---

## What These Examples Do NOT Include

Intentionally excluded:

- Business logic
- Authorization rules beyond basic authentication
- Application-specific message schemas
- Persistence or horizontal scaling strategies

These concerns are application-specific and must not weaken the core invariants.

---

## Final Rule

If you copy code from this directory and remove:
- Cleanup logic
- Capacity checks
- Health verification

You are no longer implementing this skill.