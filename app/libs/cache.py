import asyncio
import time
from typing import Any, Dict, Optional


class SimpleCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if time.time() < item["expires_at"]:
                    return item["value"]
                else:
                    del self._cache[key]
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        async with self._lock:
            expires_at = time.time() + (ttl or self._default_ttl)
            self._cache[key] = {"value": value, "expires_at": expires_at}

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()


# Global cache instance
cache = SimpleCache(default_ttl=60)  # 1 minute cache
