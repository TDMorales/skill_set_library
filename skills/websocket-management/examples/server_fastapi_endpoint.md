# FastAPI WebSocket Endpoint – Auth, Capacity, and Lifecycle Wiring
Thin endpoint wiring that authenticates, enforces capacity, delegates lifecycle to the manager, and performs defensive cleanup.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)
Violations: registers before capacity checks, treats token as identity, and leaks state on disconnect/errors.

~~~python
# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/endpoint.py
# +++ b/endpoint.py
# @@
# - can_accept, reason = await manager.can_accept_connection(lobby_code)
# - if not can_accept:
# -     await websocket.close(code=4002, reason=reason)
# -     return
# - await manager.connect(websocket, lobby_code, user_id)
# + await manager.connect(websocket, lobby_code, user_id)
#   # ❌ BUG: commits connection without capacity checks.
#
# @@
# - user_id = await authenticate_token(token)
# - if not user_id: close unauthorized
# + await manager.connect(websocket, lobby_code, token)  # "user_id"
#   # ❌ BUG: treats token as identity; no authentication.
#
# @@
# - except WebSocketDisconnect: await manager.disconnect(websocket)
# + except Exception: pass
#   # ❌ BUG: leaked internal state on disconnect/exception.
# =============================================================================
~~~

### Why This Is Broken
- Registers connections before enforcing capacity, allowing limit overruns and resource pressure
- Skips authentication by treating raw tokens as user identity
- Fails to call manager cleanup on disconnect/exception, causing leaks and inconsistent state

---

## ✅ CORRECT EXAMPLE
Authenticates before registration, enforces capacity before committing state, keeps endpoint thin, and always cleans up through the manager.

~~~python
"""
FastAPI WebSocket endpoint wiring.

Rules enforced:
- Authenticate before registration
- Capacity check before registration
- Endpoint stays thin; manager owns lifecycle
"""

import json
import logging
from typing import Optional

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect

from server_fastapi_connection_manager import manager

logger = logging.getLogger(__name__)
app = FastAPI()


async def authenticate_token(token: str) -> Optional[str]:
    """
    Replace with real auth.
    Must return stable user_id or None.
    """
    if token and token.startswith("user_"):
        return token
    return None


@app.websocket("/ws/{lobby_code}")
async def websocket_endpoint(
    websocket: WebSocket,
    lobby_code: str,
    token: str = Query(...),
):
    # Accept early so we can send a close reason; but do NOT register until checks pass.
    await websocket.accept()

    user_id = await authenticate_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="unauthorized")
        return

    can_accept, reason = await manager.can_accept_connection(lobby_code)
    if not can_accept:
        await websocket.close(code=4002, reason=reason)
        return

    await manager.connect(websocket, lobby_code, user_id)
    logger.info("ws_connected user=%s lobby=%s", user_id, lobby_code)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.update_last_seen(user_id)

            # Health protocol
            if data.get("type") == "health_pong":
                await manager.record_pong(user_id)
                continue

            # App message handling (replace with your logic)
            await handle_message(lobby_code, user_id, data)

    except WebSocketDisconnect:
        logger.info("ws_disconnected user=%s lobby=%s cause=client_close", user_id, lobby_code)
        await manager.disconnect(websocket)
    except Exception as e:
        # Defensive cleanup on unexpected exceptions
        logger.exception("ws_error user=%s lobby=%s", user_id, lobby_code)
        await manager.disconnect(websocket)
        try:
            await websocket.close(code=1011, reason="server_error")
        except Exception:
            pass


async def handle_message(lobby_code: str, user_id: str, data: dict) -> None:
    """
    Replace with real routing.
    Keep thin; do not mutate manager state here beyond update_last_seen/record_pong.
    """
    # Example: broadcast message to lobby (excluding sender)
    await manager.broadcast_to_lobby(
        lobby_code,
        {"type": "message", "from": user_id, "payload": data},
        exclude_user_id=user_id,
    )
~~~

### CONTRACT
- The endpoint **must** authenticate users before registering connections with the manager.
- The endpoint **must** enforce capacity checks before committing any connection to manager state.
- The endpoint **must** route all cleanup through the manager and **must** call `disconnect()` on disconnect and unexpected errors.
- The receive loop **must** update last-seen state on every inbound message.
- Health messages (`health_pong`) **must** be handled without invoking application message routing.
- The endpoint **must** remain thin: business logic belongs in handlers, not in lifecycle/state management.

---

### Notes
Keep authentication, capacity checks, and cleanup semantics explicit. Avoid “helpful” shortcuts that weaken invariants.