# websocket-management

Production-grade WebSocket connection management with strict invariants:
capacity limits, user-to-connection mapping, ping/pong health verification, and stale connection cleanup.

This skill is designed to be **copied into an existing app** (backend + frontend).
It is not a standalone framework.

---

## What You Get

Backend (server):
- Deterministic connection registration + cleanup
- Global + per-lobby capacity enforcement
- User-to-connection mapping (single active session per user by default)
- Send-failure cleanup (prevents leaks)
- Ping/pong health tracking
- Periodic stale-connection cleanup loop

Frontend (client):
- Minimal ping/pong compliance
- Defensive frame parsing
- Clean separation between transport and message handling

---

## How to Consume This Skill (Backend)

### 1) Add the manager
- Copy the **CORRECT EXAMPLE** from:
  - `examples/server_fastapi_connection_manager.md`

Integrate it as a module/class in your backend. Treat it as the single source of truth for:
- connect/register
- disconnect/cleanup
- broadcast/send
- health ping tracking

### 2) Wire the endpoint
- Copy the **CORRECT EXAMPLE** from:
  - `examples/server_fastapi_endpoint.md`

Then replace:
- `authenticate_token()` with your auth provider
- `handle_message()` with your routing logic (keep it thin)

### 3) Start the health sweep loop
- Copy the **CORRECT EXAMPLE** from:
  - `examples/server_health_sweep_loop.md`

Start it using your framework’s startup mechanism (examples):
- FastAPI lifespan/startup hook
- Task group / background task runner
- Container entrypoint background coroutine

The sweep loop is required to guarantee stale connection cleanup.

---

## How to Consume This Skill (Frontend)

### 1) Add the client transport
- Copy the **CORRECT EXAMPLE** from:
  - `examples/client_websocket_client.md`

Then:
- Override `handleMessage()` to route application messages
- Keep reconnect logic outside the minimal transport class (app-owned)

### 2) Ensure ping/pong compliance
Your client must:
- Respond immediately to `health_ping`
- Avoid blocking `onmessage`
- Serialize outbound messages using JSON

---

## Example: Expected Skill Response

Below is a representative “good response” when an agent applies this skill to implement or review a WebSocket setup.

~~~markdown
### Decisions
- Server framework: FastAPI (ASGI)
- User policy: single active connection per user (new replaces old)
- Limits: max_connections=500, max_per_lobby=10
- Health: ping_interval=20s, pong_timeout=2s, stale_threshold=60s

### Backend Changes
- Added ConnectionManager with:
  - idempotent disconnect
  - snapshot iteration for broadcasts
  - cleanup on send failure
  - leak-free ping tracking (finally cleanup)
- Wired `/ws/{lobby_code}` endpoint:
  - authenticate before register
  - capacity check before register
  - update_last_seen on every inbound message
  - record_pong on `health_pong`
  - manager.disconnect on WebSocketDisconnect and exceptions
- Started background `health_sweep_loop` at app startup

### Frontend Changes
- Updated client to:
  - parse `event.data` defensively
  - respond immediately to `health_ping` with `health_pong`
  - serialize outbound messages with JSON.stringify

### Validation Checklist
- [x] Explicit user-to-connection policy (no silent overwrite)
- [x] Disconnect is idempotent
- [x] All maps cleaned on disconnect
- [x] Broadcast uses snapshot iteration
- [x] Send failures trigger cleanup
- [x] Pending pings cannot leak
- [x] Stale connections are eventually removed (sweep loop running)
- [x] Capacity checks occur before registration
- [x] Observability hooks present
- [x] Security checks applied
~~~

---

## File Map

- `SKILL.md`  
  The contract: invariants, procedure, and validation checklist.

- `examples/*.md`  
  Copy/paste reference implementations with **BROKEN vs CORRECT** examples.

- `references/SOURCES.md`  
  Context anchors (protocol + runtime realities). Not required for usage.

---

## Notes

- These examples assume **single active connection per user**.
- If you need multi-device support, you must update the user mapping strategy consistently across:
  - manager
  - direct messaging semantics
  - validation checklist