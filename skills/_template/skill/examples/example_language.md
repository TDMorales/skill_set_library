# __SKILL_NAME__ (Language)

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

## CORRECT EXAMPLE

~~~text
TODO: Add minimal correct example.
~~~

## EXPLICIT EXAMPLE (EDGE CASE)

~~~text
TODO: Add explicit edge case example.
~~~
