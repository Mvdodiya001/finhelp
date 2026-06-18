"""Tests for the InMemoryCacheService."""
import time
import pytest
from src.core.cache import InMemoryCacheService


class TestInMemoryCacheService:
    def test_set_and_get(self):
        cache = InMemoryCacheService()
        cache.set("key1", {"data": "test"}, ttl_seconds=60)
        assert cache.get("key1") == {"data": "test"}

    def test_get_missing_key_returns_none(self):
        cache = InMemoryCacheService()
        assert cache.get("nonexistent") is None

    def test_expired_key_returns_none(self):
        cache = InMemoryCacheService()
        cache.set("key1", "value", ttl_seconds=0)
        time.sleep(0.01)
        assert cache.get("key1") is None

    def test_invalidate(self):
        cache = InMemoryCacheService()
        cache.set("key1", "value")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_stats_tracking(self):
        cache = InMemoryCacheService()
        cache.set("k", "v")
        cache.get("k")       # hit
        cache.get("k")       # hit
        cache.get("missing") # miss

        stats = cache.stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_invalidate_nonexistent_key_no_error(self):
        cache = InMemoryCacheService()
        cache.invalidate("does_not_exist")  # Should not raise
