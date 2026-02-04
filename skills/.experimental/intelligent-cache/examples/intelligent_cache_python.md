# Intelligent Cache – Python Example

Minimal example showing type-specific TTLs, get-or-generate, and stampede prevention.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

Cache reads bypass get-or-generate and skip expiry enforcement.

~~~python
"""
What breaks
- Single TTL for all cache types
- No stampede prevention
- Expired entries may be returned
"""

# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/cache.py
# +++ b/cache.py
# @@
# - if item and item.expires_at > now: return item
# + if item: return item
#   # ❌ BUG: expired entries returned
#
# @@
# - return await self.get_or_generate(cache_type, key, generator)
# + cached = self._memory.get(cache_key)
# + return cached or await generator()
#   # ❌ BUG: bypasses get-or-generate, no stampede protection.
# =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~python
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, TypeVar, Generic, Callable, Awaitable
import asyncio

T = TypeVar("T")

CACHE_DURATIONS: Dict[str, timedelta] = {
    "daily_briefing": timedelta(hours=4),
    "weekly_summary": timedelta(hours=24),
}

@dataclass
class CachedItem(Generic[T]):
    cache_type: str
    cache_key: str
    content: T
    generated_at: datetime
    expires_at: datetime
    generation_time_ms: Optional[int] = None

class IntelligentCache:
    def __init__(self) -> None:
        self._memory: Dict[str, CachedItem] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    def _get_cache_key(self, cache_type: str, key: str) -> str:
        return f"{cache_type}:{key}"

    async def get_cached(self, cache_type: str, key: str) -> Optional[CachedItem]:
        cache_key = self._get_cache_key(cache_type, key)
        now = datetime.now(timezone.utc)

        item = self._memory.get(cache_key)
        if item and item.expires_at > now:
            return item
        if item:
            del self._memory[cache_key]
        return None

    async def cache_content(self, item: CachedItem) -> None:
        cache_key = self._get_cache_key(item.cache_type, item.cache_key)
        self._memory[cache_key] = item

    async def get_or_generate(
        self,
        cache_type: str,
        key: str,
        generator: Callable[[], Awaitable[T]],
    ) -> tuple[T, bool, Optional[int]]:
        cache_key = self._get_cache_key(cache_type, key)

        cached = await self.get_cached(cache_type, key)
        if cached:
            return cached.content, True, cached.generation_time_ms

        lock = self._locks.setdefault(cache_key, asyncio.Lock())
        async with lock:
            cached = await self.get_cached(cache_type, key)
            if cached:
                return cached.content, True, cached.generation_time_ms

            start = datetime.now(timezone.utc)
            value = await generator()
            generation_time_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            expires_at = start + CACHE_DURATIONS[cache_type]

            item = CachedItem(
                cache_type=cache_type,
                cache_key=key,
                content=value,
                generated_at=start,
                expires_at=expires_at,
                generation_time_ms=generation_time_ms,
            )

            await self.cache_content(item)
            return value, False, generation_time_ms
~~~

---

## ▶ EXPLICIT EXAMPLE (STAMPede PREVENTION)

Deduplicate concurrent generators with a per-key lock.

~~~python
import asyncio

_locks: dict[str, asyncio.Lock] = {}

async def with_stampede_protection(key: str, fn):
    lock = _locks.setdefault(key, asyncio.Lock())
    async with lock:
        return await fn()
~~~
