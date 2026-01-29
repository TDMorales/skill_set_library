# WebSocket Management – Reference Sources

This document provides **contextual references** that explain why the
invariants enforced by `websocket-management` exist.

These sources are **informational only**.
The skill does **not** require internet access to function correctly.

---

## Protocol Standards

### RFC 6455 – The WebSocket Protocol
WebSockets operate over TCP and do not guarantee reliable disconnect
notification. Clients may disappear without sending a close frame.

Relevant implications:
- Connections can appear “open” while being unusable
- Ping/pong is the only reliable liveness signal
- TCP half-open connections are common in real networks

---

## Runtime & Framework Behavior

### ASGI / FastAPI / Starlette WebSockets
- WebSocket disconnect events are not guaranteed to fire in all failure modes
- Send operations often fail before receive operations
- Exceptions during send/receive are the most reliable cleanup trigger

These behaviors justify:
- Cleanup on send failure
- Idempotent disconnect logic
- Snapshot iteration during broadcasts

---

## Browser WebSocket Clients

- Browsers require outbound messages to be serialized
- `event.data` arrives as a string, Blob, or ArrayBuffer
- Clients may suspend or background tabs without closing sockets

These realities justify:
- Defensive frame parsing
- Immediate ping/pong responses
- Stale connection thresholds

---

## Operational Lessons (Non-Authoritative)

The following are practical observations from production systems:

- Ignoring ping results leads to silent connection leaks
- Relying on close events alone is insufficient
- Explicit cleanup is safer than implicit lifecycle assumptions
- Background health sweeps are required at scale

---

## Design Philosophy

This skill prioritizes:
- Deterministic cleanup over optimistic lifecycle assumptions
- Explicit invariants over “best-effort” behavior
- Server authority over client-reported state

If these assumptions change, the skill must be revised accordingly.