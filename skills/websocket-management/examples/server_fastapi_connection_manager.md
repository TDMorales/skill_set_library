# FastAPI Connection Manager – Capacity, Mapping, and Health Invariants
Production-grade connection manager that enforces strict invariants for capacity limits, user-to-connection mapping, ping/pong health tracking, and leak-free cleanup.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)
Violations: unsafe broadcast iteration, silent user overwrite, non-idempotent disconnect, and leaking pending pings.

~~~python
# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# The following illustrates common mistakes that violate SKILL.md invariants.
#
# --- a/manager.py
# +++ b/manager.py
# @@
# - for ws in self.active_connections[lobby_code]:
# + for ws in self.active_connections[lobby_code]:
#       await ws.send_text(data)
#   # ❌ BUG: iterating a live set; disconnect() during send failure can mutate it.
#
# @@
# - self.user_connections[user_id] = websocket
# + self.user_connections[user_id] = websocket
#   # ❌ BUG: silently overwrites previous ws without disconnecting/cleaning old ws.
#
# @@
# - def disconnect(self, websocket): ...
# + def disconnect(self, websocket):
# +     del self.connection_info[websocket]
#   # ❌ BUG: not idempotent; KeyError on double-disconnect; leaks other maps.
#
# @@
# - try: ... finally: self._pending_pings.pop(user_id, None)
# + await asyncio.wait_for(ping_event.wait(), timeout=timeout)
#   # ❌ BUG: pending ping can leak forever on timeout/cancel/exception.
# =============================================================================
~~~

### Why This Is Broken
- Broadcast iterates a live mutable set, risking runtime errors and inconsistent cleanup during send failures
- User mapping silently overwrites prior connections, leaving old sockets registered and leaking state
- Disconnect is not idempotent, causing KeyErrors and incomplete cleanup on repeated calls
- Pending ping state can leak on timeouts/cancellation, causing unbounded growth and false health tracking

---

## ✅ CORRECT EXAMPLE
Implements deterministic single-session-per-user behavior, idempotent cleanup, safe broadcast iteration via snapshots, and leak-free ping tracking with `finally` cleanup.

~~~python
"""
Production-grade WebSocket connection manager (FastAPI/Starlette WebSocket).

Policy: SINGLE active connection per user.
- New connection replaces old connection deterministically.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional, Set, Tuple, Iterable

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ConnInfo:
    lobby_code: str
    user_id: str


class ConnectionManager:
    """
    Enforces invariants:
    - Idempotent disconnect
    - Snapshot iteration for broadcast
    - Deterministic duplicate user handling (replace old)
    - Pending pings never leak
    - Send failures trigger cleanup
    """

    def __init__(self, max_connections: int = 500, max_per_lobby: int = 10):
        self.max_connections = max_connections
        self.max_per_lobby = max_per_lobby

        # lobby_code -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # websocket -> ConnInfo
        self.connection_info: Dict[WebSocket, ConnInfo] = {}

        # user_id -> websocket (single-session policy)
        self.user_connections: Dict[str, WebSocket] = {}

        # Health monitoring
        self._pending_pings: Dict[str, asyncio.Event] = {}
        self._last_seen: Dict[str, float] = {}

        # Minimal concurrency guard (prevents racey map mutations)
        self._lock = asyncio.Lock()

    async def can_accept_connection(self, lobby_code: str) -> Tuple[bool, str]:
        async with self._lock:
            total = sum(len(conns) for conns in self.active_connections.values())
            if total >= self.max_connections:
                return False, "server_full"

            lobby_count = len(self.active_connections.get(lobby_code, set()))
            if lobby_count >= self.max_per_lobby:
                return False, "lobby_full"

            return True, ""

    async def connect(self, websocket: WebSocket, lobby_code: str, user_id: str) -> None:
        """
        Registers a WebSocket after it has been accepted by the endpoint.
        Duplicate user connections are replaced deterministically.
        """
        async with self._lock:
            # Replace existing session deterministically (no silent overwrite).
            old_ws = self.user_connections.get(user_id)
            if old_ws is not None and old_ws is not websocket:
                # Best-effort close; cleanup via disconnect()
                try:
                    await old_ws.close(code=4000)
                except Exception:
                    pass
                self._disconnect_nolock(old_ws)

            self.active_connections.setdefault(lobby_code, set()).add(websocket)
            self.connection_info[websocket] = ConnInfo(lobby_code=lobby_code, user_id=user_id)
            self.user_connections[user_id] = websocket
            self._last_seen[user_id] = time.time()

    async def disconnect(self, websocket: WebSocket) -> Optional[ConnInfo]:
        """Idempotent: safe to call multiple times."""
        async with self._lock:
            return self._disconnect_nolock(websocket)

    def _disconnect_nolock(self, websocket: WebSocket) -> Optional[ConnInfo]:
        info = self.connection_info.pop(websocket, None)
        if info is None:
            return None

        # Remove from lobby set
        lobby_set = self.active_connections.get(info.lobby_code)
        if lobby_set is not None:
            lobby_set.discard(websocket)
            if not lobby_set:
                self.active_connections.pop(info.lobby_code, None)

        # Remove user mapping iff it points to this websocket
        if self.user_connections.get(info.user_id) is websocket:
            self.user_connections.pop(info.user_id, None)

        self._last_seen.pop(info.user_id, None)
        self._pending_pings.pop(info.user_id, None)

        return info

    async def broadcast_to_lobby(
        self,
        lobby_code: str,
        message: dict,
        exclude_user_id: Optional[str] = None,
    ) -> int:
        data = json.dumps(message)
        sent = 0
        disconnected: list[WebSocket] = []

        async with self._lock:
            targets = list(self.active_connections.get(lobby_code, set()))

        for ws in targets:
            if exclude_user_id:
                info = self.connection_info.get(ws)
                if info and info.user_id == exclude_user_id:
                    continue
            try:
                await ws.send_text(data)
                sent += 1
            except Exception:
                disconnected.append(ws)

        # Cleanup failures
        for ws in disconnected:
            await self.disconnect(ws)

        return sent

    async def send_to_user(self, user_id: str, message: dict) -> bool:
        data = json.dumps(message)
        async with self._lock:
            ws = self.user_connections.get(user_id)

        if ws is None:
            return False

        try:
            await ws.send_text(data)
            return True
        except Exception:
            await self.disconnect(ws)
            return False

    async def ping_user(self, user_id: str, timeout: float = 2.0) -> Tuple[bool, Optional[float]]:
        async with self._lock:
            ws = self.user_connections.get(user_id)
            if ws is None:
                return False, None

            ping_event = asyncio.Event()
            # Replace any previous pending ping deterministically.
            self._pending_pings[user_id] = ping_event

        start = time.time()
        try:
            await ws.send_text(json.dumps({"type": "health_ping", "timestamp": start}))
            await asyncio.wait_for(ping_event.wait(), timeout=timeout)
            latency_ms = (time.time() - start) * 1000.0
            return True, latency_ms
        except asyncio.TimeoutError:
            return False, None
        except Exception:
            return False, None
        finally:
            # Pending pings never leak.
            async with self._lock:
                self._pending_pings.pop(user_id, None)

    async def record_pong(self, user_id: str) -> None:
        async with self._lock:
            self._last_seen[user_id] = time.time()
            evt = self._pending_pings.get(user_id)
            if evt:
                evt.set()

    async def update_last_seen(self, user_id: str) -> None:
        async with self._lock:
            self._last_seen[user_id] = time.time()

    async def is_user_connected(self, user_id: str) -> bool:
        async with self._lock:
            return user_id in self.user_connections

    async def get_lobby_users(self, lobby_code: str) -> Set[str]:
        async with self._lock:
            users: Set[str] = set()
            for ws in self.active_connections.get(lobby_code, set()):
                info = self.connection_info.get(ws)
                if info:
                    users.add(info.user_id)
            return users

    async def iter_users(self) -> Iterable[str]:
        async with self._lock:
            return list(self.user_connections.keys())

    async def get_last_seen(self, user_id: str) -> Optional[float]:
        async with self._lock:
            return self._last_seen.get(user_id)

    async def get_stats(self) -> dict:
        async with self._lock:
            total = sum(len(conns) for conns in self.active_connections.values())
            cap = self.max_connections or 1
            return {
                "total_connections": total,
                "max_connections": self.max_connections,
                "capacity_percent": round(total / cap * 100.0, 1),
                "active_lobbies": len(self.active_connections),
            }


manager = ConnectionManager()
~~~

### CONTRACT
- The manager **must** enforce a single-session-per-user policy without silent overwrites (new connections replace old deterministically).
- The manager **must** keep internal mappings consistent: active sockets **must** have metadata and disconnected sockets **must not** remain referenced.
- `disconnect()` **must** be idempotent and safe under repeated calls and partial state.
- Broadcast logic **must** iterate over a snapshot to avoid mutation during iteration.
- Send failures **must** trigger cleanup via disconnect.
- Ping tracking **must** use `finally` cleanup so pending ping state cannot leak.
- Capacity checks **must** be performed via `can_accept_connection()` before registration by the endpoint.

---

### Notes
Keep lifecycle ownership centralized in the manager and keep the endpoint thin. Any deviation should be treated as an invariant violation.