"""
Unit Tests for Cache Service

Tests for app.core.cache module including:
- CacheClient initialization and connection
- Get/Set/Delete operations
- Serialization and namespacing
- TTL and expiration
- List operations
- Cache decorator
- Fallback to in-memory cache
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import timedelta
import pickle

from app.core.cache import CacheClient, cached, invalidate_cache, invalidate_namespace


@pytest.fixture
def cache_client():
    """Create a CacheClient instance for testing."""
    return CacheClient()


@pytest.fixture
async def connected_cache():
    """Create a connected cache client (in-memory fallback)."""
    client = CacheClient()
    await client.connect()
    yield client
    await client.disconnect()


@pytest.mark.unit
@pytest.mark.cache
class TestCacheClientInitialization:
    """Test CacheClient initialization and connection."""
    
    def test_init_creates_empty_cache(self, cache_client):
        """Test that __init__ creates an empty cache."""
        assert cache_client.redis_client is None
        assert cache_client.memory_cache == {}
        assert cache_client._connected is False
    
    @pytest.mark.asyncio
    async def test_connect_fallback_to_memory(self, cache_client):
        """Test connection falls back to in-memory cache when Redis unavailable."""
        await cache_client.connect()
        
        # Should not be connected to Redis in test environment
        assert cache_client._connected is False
        assert cache_client.redis_client is None
        assert isinstance(cache_client.memory_cache, dict)
    
    @pytest.mark.asyncio
    async def test_disconnect_closes_redis(self, cache_client):
        """Test disconnect closes Redis connection."""
        cache_client.redis_client = AsyncMock()
        cache_client._connected = True
        
        await cache_client.disconnect()
        
        cache_client.redis_client.close.assert_called_once()
        assert cache_client._connected is False


@pytest.mark.unit
@pytest.mark.cache
class TestCacheClientSerialization:
    """Test serialization and deserialization."""
    
    def test_serialize_simple_types(self, cache_client):
        """Test serialization of simple types."""
        # String
        serialized = cache_client._serialize("test")
        assert isinstance(serialized, bytes)
        assert cache_client._deserialize(serialized) == "test"
        
        # Integer
        serialized = cache_client._serialize(42)
        assert cache_client._deserialize(serialized) == 42
        
        # Float
        serialized = cache_client._serialize(3.14)
        assert cache_client._deserialize(serialized) == 3.14
        
        # Boolean
        serialized = cache_client._serialize(True)
        assert cache_client._deserialize(serialized) is True
    
    def test_serialize_complex_types(self, cache_client):
        """Test serialization of complex types."""
        # Dict
        data = {"key": "value", "number": 42}
        serialized = cache_client._serialize(data)
        assert cache_client._deserialize(serialized) == data
        
        # List
        data = [1, 2, 3, "test"]
        serialized = cache_client._serialize(data)
        assert cache_client._deserialize(serialized) == data
        
        # Nested
        data = {"list": [1, 2, 3], "dict": {"nested": "value"}}
        serialized = cache_client._serialize(data)
        assert cache_client._deserialize(serialized) == data
    
    def test_deserialize_none(self, cache_client):
        """Test deserialize returns None for None input."""
        assert cache_client._deserialize(None) is None
    
    def test_make_key_with_namespace(self, cache_client):
        """Test key namespacing."""
        key = cache_client._make_key("test_key", "test_namespace")
        assert key == "test_namespace:test_key"
        
        key = cache_client._make_key("another_key", "default")
        assert key == "default:another_key"
    
    def test_make_key_default_namespace(self, cache_client):
        """Test default namespace is used when not specified."""
        key = cache_client._make_key("test_key")
        assert key == "default:test_key"


@pytest.mark.unit
@pytest.mark.cache
class TestCacheClientOperations:
    """Test basic cache operations (get, set, delete, exists)."""
    
    @pytest.mark.asyncio
    async def test_set_and_get_value(self, connected_cache):
        """Test setting and getting a value."""
        await connected_cache.set("test_key", "test_value")
        value = await connected_cache.get("test_key")
        
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_set_and_get_with_namespace(self, connected_cache):
        """Test setting and getting with custom namespace."""
        await connected_cache.set("key1", "value1", namespace="ns1")
        await connected_cache.set("key1", "value2", namespace="ns2")
        
        value1 = await connected_cache.get("key1", namespace="ns1")
        value2 = await connected_cache.get("key1", namespace="ns2")
        
        assert value1 == "value1"
        assert value2 == "value2"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, connected_cache):
        """Test getting a non-existent key returns None."""
        value = await connected_cache.get("nonexistent_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_delete_key(self, connected_cache):
        """Test deleting a key."""
        await connected_cache.set("test_key", "test_value")
        await connected_cache.delete("test_key")
        
        value = await connected_cache.get("test_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, connected_cache):
        """Test deleting a non-existent key doesn't raise error."""
        await connected_cache.delete("nonexistent_key")
        # Should not raise exception
    
    @pytest.mark.asyncio
    async def test_exists_returns_true_for_existing_key(self, connected_cache):
        """Test exists returns True for existing key."""
        await connected_cache.set("test_key", "test_value")
        
        exists = await connected_cache.exists("test_key")
        assert exists is True
    
    @pytest.mark.asyncio
    async def test_exists_returns_false_for_nonexistent_key(self, connected_cache):
        """Test exists returns False for non-existent key."""
        exists = await connected_cache.exists("nonexistent_key")
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_set_with_complex_data(self, connected_cache):
        """Test setting and getting complex data structures."""
        data = {
            "user_id": 123,
            "name": "Test User",
            "roles": ["admin", "user"],
            "metadata": {"created": "2025-01-01", "active": True}
        }
        
        await connected_cache.set("user_data", data)
        retrieved = await connected_cache.get("user_data")
        
        assert retrieved == data
        assert retrieved["roles"] == ["admin", "user"]
        assert retrieved["metadata"]["active"] is True


@pytest.mark.unit
@pytest.mark.cache
class TestCacheClientCounters:
    """Test counter operations (incr)."""
    
    @pytest.mark.asyncio
    async def test_incr_new_key(self, connected_cache):
        """Test incrementing a new key starts at 1."""
        count = await connected_cache.incr("counter")
        assert count == 1
    
    @pytest.mark.asyncio
    async def test_incr_existing_key(self, connected_cache):
        """Test incrementing an existing key."""
        await connected_cache.incr("counter")
        await connected_cache.incr("counter")
        count = await connected_cache.incr("counter")
        
        assert count == 3
    
    @pytest.mark.asyncio
    async def test_incr_with_namespace(self, connected_cache):
        """Test incrementing with namespace isolation."""
        count1 = await connected_cache.incr("counter", namespace="ns1")
        count2 = await connected_cache.incr("counter", namespace="ns2")
        count1_again = await connected_cache.incr("counter", namespace="ns1")
        
        assert count1 == 1
        assert count2 == 1
        assert count1_again == 2


@pytest.mark.unit
@pytest.mark.cache
class TestCacheClientListOperations:
    """Test list operations (lpush, lrange, ltrim)."""
    
    @pytest.mark.asyncio
    async def test_lpush_single_value(self, connected_cache):
        """Test pushing a single value to a list."""
        await connected_cache.lpush("my_list", "value1")
        
        values = await connected_cache.lrange("my_list", 0, -1)
        assert values == ["value1"]
    
    @pytest.mark.asyncio
    async def test_lpush_multiple_values(self, connected_cache):
        """Test pushing multiple values to a list."""
        await connected_cache.lpush("my_list", "value1")
        await connected_cache.lpush("my_list", "value2")
        await connected_cache.lpush("my_list", "value3")
        
        values = await connected_cache.lrange("my_list", 0, -1)
        # lpush adds to the left, so order is reversed
        assert values == ["value3", "value2", "value1"]
    
    @pytest.mark.asyncio
    async def test_lrange_slice(self, connected_cache):
        """Test getting a slice of a list."""
        for i in range(5):
            await connected_cache.lpush("my_list", f"value{i}")
        
        # Get first 3 items
        values = await connected_cache.lrange("my_list", 0, 2)
        assert len(values) == 3
        assert values[0] == "value4"  # Most recent
    
    @pytest.mark.asyncio
    async def test_lrange_nonexistent_list(self, connected_cache):
        """Test lrange on non-existent list returns empty list."""
        values = await connected_cache.lrange("nonexistent_list", 0, -1)
        assert values == []
    
    @pytest.mark.asyncio
    async def test_ltrim_list(self, connected_cache):
        """Test trimming a list."""
        for i in range(5):
            await connected_cache.lpush("my_list", f"value{i}")
        
        # Keep only first 3 items
        await connected_cache.ltrim("my_list", 0, 2)
        
        values = await connected_cache.lrange("my_list", 0, -1)
        assert len(values) == 3


@pytest.mark.unit
@pytest.mark.cache
class TestCacheClientNamespaces:
    """Test namespace operations."""
    
    @pytest.mark.asyncio
    async def test_clear_namespace(self, connected_cache):
        """Test clearing all keys in a namespace."""
        # Add keys to different namespaces
        await connected_cache.set("key1", "value1", namespace="ns1")
        await connected_cache.set("key2", "value2", namespace="ns1")
        await connected_cache.set("key3", "value3", namespace="ns2")
        
        # Clear ns1
        await connected_cache.clear_namespace("ns1")
        
        # ns1 keys should be gone
        assert await connected_cache.get("key1", namespace="ns1") is None
        assert await connected_cache.get("key2", namespace="ns1") is None
        
        # ns2 keys should still exist
        assert await connected_cache.get("key3", namespace="ns2") == "value3"


@pytest.mark.unit
@pytest.mark.cache
class TestCacheDecorator:
    """Test the @cached decorator."""
    
    @pytest.mark.asyncio
    async def test_cached_decorator_caches_result(self, connected_cache):
        """Test that @cached decorator caches function results."""
        call_count = 0
        
        @cached(ttl=60, namespace="test")
        async def expensive_function(arg1: str):
            nonlocal call_count
            call_count += 1
            return f"result_{arg1}"
        
        # First call - should execute function
        result1 = await expensive_function("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Second call - should use cache
        result2 = await expensive_function("test")
        assert result2 == "result_test"
        assert call_count == 1  # Not incremented!
    
    @pytest.mark.asyncio
    async def test_cached_decorator_different_args(self, connected_cache):
        """Test that @cached decorator uses different cache keys for different args."""
        call_count = 0
        
        @cached(ttl=60, namespace="test")
        async def expensive_function(arg1: str):
            nonlocal call_count
            call_count += 1
            return f"result_{arg1}"
        
        result1 = await expensive_function("arg1")
        result2 = await expensive_function("arg2")
        
        assert result1 == "result_arg1"
        assert result2 == "result_arg2"
        assert call_count == 2  # Called twice for different args


@pytest.mark.unit
@pytest.mark.cache
class TestCacheErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_set_none_value(self, connected_cache):
        """Test setting None as a value."""
        await connected_cache.set("test_key", None)
        value = await connected_cache.get("test_key")
        
        # None should be cached and retrieved
        assert value is None
        assert await connected_cache.exists("test_key") is True
    
    @pytest.mark.asyncio
    async def test_set_empty_string(self, connected_cache):
        """Test setting empty string as a value."""
        await connected_cache.set("test_key", "")
        value = await connected_cache.get("test_key")
        
        assert value == ""
        assert await connected_cache.exists("test_key") is True
    
    @pytest.mark.asyncio
    async def test_set_zero(self, connected_cache):
        """Test setting zero as a value."""
        await connected_cache.set("test_key", 0)
        value = await connected_cache.get("test_key")
        
        assert value == 0
        assert await connected_cache.exists("test_key") is True

