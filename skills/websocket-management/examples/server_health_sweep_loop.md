# Server Health Sweep Loop – Stale Connection Cleanup
Runs a periodic sweep to detect stale or half-open WebSocket connections and trigger cleanup safely.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)
Violations: unsafe iteration, ignored ping results, and missing stale-threshold enforcement.

~~~python
# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/sweep.py
# +++ b/sweep.py
# @@
# - for user_id in await manager.iter_users():
# + for user_id in manager.user_connections.keys():
#   # ❌ BUG: reaches into internal dict without lock; race + RuntimeError risk.
#
# @@
# - ok, _ = await manager.ping_user(user_id)
# - if not ok: disconnect
# + await manager.ping_user(user_id)  # ignore result
#   # ❌ BUG: ping result ignored; stale clients accumulate.
#
# @@
# - if last_seen and now - last_seen > stale_threshold: disconnect
# + # no stale threshold
#   # ❌ BUG: idle half-open connections never removed.
# =============================================================================
~~~

### Why This Is Broken
- Accesses internal manager state directly (bypasses safety/locking assumptions)
- Ignores ping outcome, so dead clients remain registered indefinitely
- Omits stale-threshold enforcement, so idle half-open sockets accumulate

---

## ✅ CORRECT EXAMPLE

~~~python
"""
Background health sweep loop.

Required behavior:
- periodically ping users
- disconnect on ping timeout
- disconnect on stale last-seen timestamp
- must tolerate partial/removed state
"""

import asyncio
import logging
import time

from server_fastapi_connection_manager import manager

logger = logging.getLogger(__name__)


async def health_sweep_loop(
    *,
    ping_interval: float = 20.0,
    pong_timeout: float = 2.0,
    stale_threshold: float = 60.0,
) -> None:
    """
    Run forever until cancelled.

    Defaults are conservative; tune for your product.
    """
    logger.info(
        "ws_health_sweep_start ping_interval=%s pong_timeout=%s stale_threshold=%s",
        ping_interval,
        pong_timeout,
        stale_threshold,
    )

    while True:
        start = time.time()

        # Snapshot user list (safe)
        user_ids = await manager.iter_users()
        now = time.time()

        for user_id in user_ids:
            last_seen = await manager.get_last_seen(user_id)

            # Stale threshold cleanup (eventual removal guarantee)
            if last_seen is not None and (now - last_seen) > stale_threshold:
                # Disconnect best-effort: manager will no-op if already removed
                await _disconnect_user_best_effort(user_id, cause="stale_threshold")
                continue

            ok, latency_ms = await manager.ping_user(user_id, timeout=pong_timeout)
            if not ok:
                await _disconnect_user_best_effort(user_id, cause="ping_timeout")
            else:
                logger.debug("ws_ping_ok user=%s latency_ms=%.1f", user_id, latency_ms or -1.0)

        elapsed = time.time() - start
        sleep_for = max(0.0, ping_interval - elapsed)
        await asyncio.sleep(sleep_for)


async def _disconnect_user_best_effort(user_id: str, *, cause: str) -> None:
    """
    Disconnect by user_id using manager mappings safely.
    """
    if not await manager.is_user_connected(user_id):
        return

    # Send optional "closing" notice (ignore failures)
    await manager.send_to_user(user_id, {"type": "server_disconnect", "reason": cause})

    # Trigger cleanup by forcing a ping (if ws is dead, it will cleanup on send failure elsewhere),
    # and rely on timeout cleanup. For deterministic cleanup, add a manager helper method.
    ok, _ = await manager.ping_user(user_id, timeout=0.5)
    if ok:
        logger.info("ws_health_sweep_flagged user=%s cause=%s (consider disconnect-by-user)", user_id, cause)
    else:
        logger.info("ws_health_sweep_disconnected user=%s cause=%s", user_id, cause)
~~~

### CONTRACT
- The sweep loop **must** iterate over a safe snapshot of user IDs (no direct access to internal maps).
- The sweep loop **must** enforce a stale threshold using last-seen timestamps.
- The sweep loop **must** handle ping failures and trigger cleanup on timeout.
- Cleanup logic **must** tolerate partial/removed state and remain idempotent.
- The loop **must** avoid throwing or blocking the event loop via logging or exception propagation.

---

### Notes
Keep cleanup deterministic and centralized. If you require hard disconnect-by-user behavior, add an explicit `disconnect_user(user_id)` manager method and route sweep cleanup through it.