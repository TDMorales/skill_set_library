# Examples

Concrete, copy/paste-ready examples that match the SKILL invariants. Keep these minimal and adapt names to your domain.

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

## Intelligent Cache (TypeScript)

```ts
const CACHE_DURATIONS: Record<string, number> = {
  daily_briefing: 4 * 60 * 60 * 1000,
  weekly_summary: 24 * 60 * 60 * 1000,
};

type CacheType = keyof typeof CACHE_DURATIONS;

type CachedItem<T> = {
  cacheType: CacheType;
  cacheKey: string;
  content: T;
  generatedAt: string;
  expiresAt: string;
  generationTimeMs?: number;
};

const memoryCache = new Map<string, CachedItem<unknown>>();
const inFlight = new Map<string, Promise<CachedItem<unknown>>>();

function getCacheKey(type: CacheType, key: string): string {
  return `${type}:${key}`;
}

async function getCached<T>(type: CacheType, key: string): Promise<CachedItem<T> | null> {
  const cacheKey = getCacheKey(type, key);
  const now = new Date();

  const mem = memoryCache.get(cacheKey) as CachedItem<T> | undefined;
  if (mem) {
    if (new Date(mem.expiresAt) > now) return mem;
    memoryCache.delete(cacheKey);
  }

  return null;
}

async function cacheContent<T>(item: CachedItem<T>): Promise<void> {
  memoryCache.set(getCacheKey(item.cacheType, item.cacheKey), item as CachedItem<unknown>);
}

async function getOrGenerate<T>(
  type: CacheType,
  key: string,
  generator: () => Promise<T>
): Promise<{ value: T; fromCache: boolean; generationTimeMs?: number }> {
  const cacheKey = getCacheKey(type, key);

  const cached = await getCached<T>(type, key);
  if (cached) {
    return { value: cached.content, fromCache: true, generationTimeMs: cached.generationTimeMs };
  }

  if (inFlight.has(cacheKey)) {
    const existing = (await inFlight.get(cacheKey)) as CachedItem<T>;
    return { value: existing.content, fromCache: true, generationTimeMs: existing.generationTimeMs };
  }

  const task = (async () => {
    const start = Date.now();
    const value = await generator();
    const generationTimeMs = Date.now() - start;
    const now = new Date();
    const expiresAt = new Date(now.getTime() + CACHE_DURATIONS[type]);

    const item: CachedItem<T> = {
      cacheType: type,
      cacheKey: key,
      content: value,
      generatedAt: now.toISOString(),
      expiresAt: expiresAt.toISOString(),
      generationTimeMs,
    };

    await cacheContent(item);
    return item;
  })();

  inFlight.set(cacheKey, task as Promise<CachedItem<unknown>>);
  try {
    const item = (await task) as CachedItem<T>;
    return { value: item.content, fromCache: false, generationTimeMs: item.generationTimeMs };
  } finally {
    inFlight.delete(cacheKey);
  }
}
```

---

## Intelligent Cache (Python)

```python
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, TypeVar, Generic, Callable, Awaitable
import asyncio
import uuid

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
```
