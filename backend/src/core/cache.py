"""
Cache Service — In-memory key-value cache with TTL expiration and statistics.

Implements the ICacheService interface from src.core.interfaces with a simple dict-based
store.  Each entry is stored as ``{key: (value, expiry_timestamp)}`` so that
expired entries are lazily evicted on read.

Thread-safety note:
    This implementation is intended for single-process / single-worker deployments.
    For multi-worker production setups, swap in a Redis-backed implementation that
    satisfies the same ICacheService contract.
"""

import time
from typing import Any, Optional

from src.core.interfaces import ICacheService
from src.core.logger import get_logger

logger = get_logger(__name__)


class InMemoryCacheService(ICacheService):
    """In-memory TTL cache backed by a plain Python dict.

    Attributes:
        _store: Internal dict mapping keys to ``(value, expiry_timestamp)`` tuples.
        _hits:  Running counter of cache hits (key found and not expired).
        _misses: Running counter of cache misses (key absent or expired).
    """

    def __init__(self) -> None:
        """Initialise an empty cache with zeroed-out statistics."""
        self._store: dict[str, tuple[Any, float]] = {}
        self._hits: int = 0
        self._misses: int = 0
        logger.info("InMemoryCacheService initialised")

    # ------------------------------------------------------------------
    # ICacheService interface
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value by *key*.

        If the key exists but its TTL has elapsed the entry is silently removed
        and ``None`` is returned (counted as a miss).

        Args:
            key: The cache key to look up.

        Returns:
            The cached value, or ``None`` if the key is missing / expired.
        """
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            logger.debug("Cache MISS (absent): %s", key)
            return None

        value, expiry = entry
        if time.time() > expiry:
            # Lazy eviction of expired entry
            del self._store[key]
            self._misses += 1
            logger.debug("Cache MISS (expired): %s", key)
            return None

        self._hits += 1
        logger.debug("Cache HIT: %s", key)
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Store *value* under *key* with an expiry of *ttl_seconds*.

        If *key* already exists it is silently overwritten.

        Args:
            key: The cache key.
            value: Arbitrary value to cache.
            ttl_seconds: Time-to-live in seconds (default 300 = 5 min).
        """
        expiry = time.time() + ttl_seconds
        self._store[key] = (value, expiry)
        logger.debug("Cache SET: %s (ttl=%ds)", key, ttl_seconds)

    def invalidate(self, key: str) -> None:
        """Remove *key* from the cache if it exists.

        No error is raised when the key is absent.

        Args:
            key: The cache key to invalidate.
        """
        removed = self._store.pop(key, None)
        if removed is not None:
            logger.debug("Cache INVALIDATE: %s", key)
        else:
            logger.debug("Cache INVALIDATE (no-op, key absent): %s", key)

    def stats(self) -> dict[str, int]:
        """Return aggregate cache statistics.

        Returns:
            A dict with ``hits``, ``misses``, and ``size`` (current entry count,
            including entries that may be expired but not yet evicted).
        """
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._store),
        }
