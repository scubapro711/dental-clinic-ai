"""
Redis Caching Layer

Provides caching functionality for:
- API responses
- Database queries
- Agent responses
- Session data
- Rate limiting
"""

from typing import Optional, Any
import json
import pickle
from datetime import timedelta
from functools import wraps
import hashlib

try:
    import redis.asyncio as redis
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

from app.core.config import settings


class CacheClient:
    """
    Redis cache client with fallback to in-memory cache.
    
    Features:
    - Automatic serialization/deserialization
    - TTL support
    - Key namespacing
    - Fallback to in-memory cache
    """
    
    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.memory_cache: dict = {}
        self._connected = False
        
    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            print("⚠️  Redis not available, using in-memory cache")
            return
        
        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False,  # We'll handle serialization
                max_connections=50,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            
            # Test connection
            await self.redis_client.ping()
            self._connected = True
            print("✅ Connected to Redis")
            
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}, using in-memory cache")
            self.redis_client = None
            self._connected = False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        return pickle.dumps(value)
    
    def _deserialize(self, value: bytes) -> Any:
        """Deserialize value from storage"""
        if value is None:
            return None
        return pickle.loads(value)
    
    def _make_key(self, key: str, namespace: str = "default") -> str:
        """Create namespaced key"""
        return f"{namespace}:{key}"
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            namespace: Key namespace
        
        Returns:
            Cached value or None
        """
        full_key = self._make_key(key, namespace)
        
        if self._connected and self.redis_client:
            try:
                value = await self.redis_client.get(full_key)
                return self._deserialize(value)
            except Exception as e:
                print(f"Redis get error: {e}")
                return None
        else:
            return self.memory_cache.get(full_key)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default"
    ):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            namespace: Key namespace
        """
        full_key = self._make_key(key, namespace)
        serialized = self._serialize(value)
        
        if self._connected and self.redis_client:
            try:
                if ttl:
                    await self.redis_client.setex(full_key, ttl, serialized)
                else:
                    await self.redis_client.set(full_key, serialized)
            except Exception as e:
                print(f"Redis set error: {e}")
        else:
            self.memory_cache[full_key] = value
    
    async def delete(self, key: str, namespace: str = "default"):
        """Delete key from cache"""
        full_key = self._make_key(key, namespace)
        
        if self._connected and self.redis_client:
            try:
                await self.redis_client.delete(full_key)
            except Exception as e:
                print(f"Redis delete error: {e}")
        else:
            self.memory_cache.pop(full_key, None)
    
    async def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists"""
        full_key = self._make_key(key, namespace)
        
        if self._connected and self.redis_client:
            try:
                return await self.redis_client.exists(full_key) > 0
            except Exception as e:
                print(f"Redis exists error: {e}")
                return False
        else:
            return full_key in self.memory_cache
    
    async def incr(self, key: str, namespace: str = "default") -> int:
        """Increment counter"""
        full_key = self._make_key(key, namespace)
        
        if self._connected and self.redis_client:
            try:
                return await self.redis_client.incr(full_key)
            except Exception as e:
                print(f"Redis incr error: {e}")
                return 0
        else:
            current = self.memory_cache.get(full_key, 0)
            self.memory_cache[full_key] = current + 1
            return current + 1
    
    async def expire(self, key: str, ttl: int, namespace: str = "default"):
        """Set TTL on existing key"""
        full_key = self._make_key(key, namespace)
        
        if self._connected and self.redis_client:
            try:
                await self.redis_client.expire(full_key, ttl)
            except Exception as e:
                print(f"Redis expire error: {e}")
    
    async def lpush(self, key: str, value: Any, namespace: str = "default"):
        """Push to list (left)"""
        full_key = self._make_key(key, namespace)
        serialized = self._serialize(value)
        
        if self._connected and self.redis_client:
            try:
                await self.redis_client.lpush(full_key, serialized)
            except Exception as e:
                print(f"Redis lpush error: {e}")
        else:
            if full_key not in self.memory_cache:
                self.memory_cache[full_key] = []
            self.memory_cache[full_key].insert(0, value)
    
    async def lrange(self, key: str, start: int, end: int, namespace: str = "default") -> list:
        """Get range from list"""
        full_key = self._make_key(key, namespace)
        
        if self._connected and self.redis_client:
            try:
                values = await self.redis_client.lrange(full_key, start, end)
                return [self._deserialize(v) for v in values]
            except Exception as e:
                print(f"Redis lrange error: {e}")
                return []
        else:
            lst = self.memory_cache.get(full_key, [])
            if end == -1:
                return lst[start:]
            return lst[start:end+1]
    
    async def ltrim(self, key: str, start: int, end: int, namespace: str = "default"):
        """Trim list to range"""
        full_key = self._make_key(key, namespace)
        
        if self._connected and self.redis_client:
            try:
                await self.redis_client.ltrim(full_key, start, end)
            except Exception as e:
                print(f"Redis ltrim error: {e}")
        else:
            if full_key in self.memory_cache:
                if end == -1:
                    self.memory_cache[full_key] = self.memory_cache[full_key][start:]
                else:
                    self.memory_cache[full_key] = self.memory_cache[full_key][start:end+1]
    
    async def clear_namespace(self, namespace: str):
        """Clear all keys in namespace"""
        if self._connected and self.redis_client:
            try:
                pattern = f"{namespace}:*"
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            except Exception as e:
                print(f"Redis clear_namespace error: {e}")
        else:
            keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"{namespace}:")]
            for key in keys_to_delete:
                del self.memory_cache[key]


# Global cache instance
_cache_client: Optional[CacheClient] = None


async def get_cache() -> CacheClient:
    """Get cache client instance"""
    global _cache_client
    
    if _cache_client is None:
        _cache_client = CacheClient()
        await _cache_client.connect()
    
    return _cache_client


# Decorator for caching function results
def cached(
    ttl: int = 300,
    namespace: str = "function",
    key_prefix: str = ""
):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        namespace: Cache namespace
        key_prefix: Prefix for cache key
    
    Example:
        @cached(ttl=600, namespace="api", key_prefix="treatments")
        async def get_treatments(org_id: int):
            return db.query(Treatment).filter_by(organization_id=org_id).all()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            # Use SHA256 instead of MD5 for security
            cache_key = hashlib.sha256(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cache = await get_cache()
            cached_value = await cache.get(cache_key, namespace)
            
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl, namespace)
            
            return result
        
        return wrapper
    return decorator


# Cache invalidation helpers
async def invalidate_cache(key: str, namespace: str = "default"):
    """Invalidate specific cache key"""
    cache = await get_cache()
    await cache.delete(key, namespace)


async def invalidate_namespace(namespace: str):
    """Invalidate all keys in namespace"""
    cache = await get_cache()
    await cache.clear_namespace(namespace)


# Common cache namespaces
class CacheNamespace:
    """Cache namespace constants"""
    API = "api"
    DATABASE = "database"
    AGENT = "agent"
    SESSION = "session"
    RATE_LIMIT = "rate_limit"
    PHI_ACCESS = "phi_access"
    PERFORMANCE = "performance"
