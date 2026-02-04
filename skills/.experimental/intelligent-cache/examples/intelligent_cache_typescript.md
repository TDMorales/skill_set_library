# Intelligent Cache – TypeScript Example

Minimal example showing type-specific TTLs, get-or-generate, and stampede prevention.

---

## ❌ BROKEN EXAMPLE (DO NOT COPY)

Cache reads bypass get-or-generate and use a single TTL for all types.

~~~typescript
/**
 * What breaks
 * - Single TTL for all cache types
 * - No stampede prevention
 * - Cache reads bypass get-or-generate
 */

// =============================================================================
// BROKEN DIFF (DO NOT COPY)
// =============================================================================
// --- a/cache.ts
// +++ b/cache.ts
// @@
// - const ttl = CACHE_DURATIONS[type];
// + const ttl = 60 * 60 * 1000; // ❌ BUG: single TTL for all types
//
// @@
// - return await getOrGenerate(type, key, generator);
// + const cached = memoryCache.get(key);
// + if (cached) return cached;
// + return await generator();
//   // ❌ BUG: bypasses get-or-generate, no stampede protection.
// =============================================================================
~~~

---

## ✅ CORRECT EXAMPLE

~~~typescript
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
~~~

---

## ▶ EXPLICIT EXAMPLE (STAMPede PREVENTION)

Use an in-flight map keyed by `(type:key)` to deduplicate concurrent requests.

~~~typescript
const inFlight = new Map<string, Promise<CachedItem<unknown>>>();

async function withStampedeProtection<T>(
  cacheKey: string,
  task: () => Promise<CachedItem<T>>
): Promise<CachedItem<T>> {
  if (inFlight.has(cacheKey)) {
    return (await inFlight.get(cacheKey)) as CachedItem<T>;
  }
  const run = task();
  inFlight.set(cacheKey, run as Promise<CachedItem<unknown>>);
  try {
    return await run;
  } finally {
    inFlight.delete(cacheKey);
  }
}
~~~
