"""
Odoo Data Caching Service

Provides caching layer for Odoo data to improve performance and reduce load.
Uses Redis for distributed caching with configurable TTL.
"""

import json
import logging
from typing import Any, Optional, Callable
from datetime import timedelta
from functools import wraps

import redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class OdooCache:
    """
    Redis-based caching service for Odoo data.
    
    Features:
    - Configurable TTL per data type
    - Automatic serialization/deserialization
    - Cache invalidation
    - Fallback to direct Odoo calls on cache miss
    """
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            # Parse Redis URL
            redis_url = str(settings.REDIS_URL)
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis cache unavailable: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    # Cache TTL configuration (in seconds)
    TTL = {
        'patient_profile': 300,      # 5 minutes
        'patient_list': 60,           # 1 minute
        'appointments': 120,          # 2 minutes
        'doctors': 600,               # 10 minutes
        'available_slots': 180,       # 3 minutes
        'health_score': 300,          # 5 minutes
        'invoices': 300,              # 5 minutes
        'treatments': 3600,           # 1 hour (rarely changes)
    }
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and parameters.
        
        Args:
            prefix: Cache key prefix (e.g., 'patient_profile')
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Cache key string
        """
        parts = [f"odoo:{prefix}"]
        
        # Add positional args
        for arg in args:
            if arg is not None:
                parts.append(str(arg))
        
        # Add keyword args (sorted for consistency)
        for key in sorted(kwargs.keys()):
            value = kwargs[key]
            if value is not None:
                parts.append(f"{key}:{value}")
        
        return ":".join(parts)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., 'odoo:patient:*')
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                count = self.redis_client.delete(*keys)
                logger.info(f"Cache DELETE PATTERN: {pattern} ({count} keys)")
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def invalidate_patient(self, patient_id: int):
        """
        Invalidate all cache entries for a patient.
        
        Args:
            patient_id: Patient ID
        """
        patterns = [
            f"odoo:patient_profile:{patient_id}:*",
            f"odoo:appointments:*patient_id:{patient_id}*",
            f"odoo:health_score:{patient_id}:*",
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)
    
    def invalidate_doctor(self, doctor_id: int):
        """
        Invalidate all cache entries for a doctor.
        
        Args:
            doctor_id: Doctor ID
        """
        patterns = [
            f"odoo:appointments:*doctor_id:{doctor_id}*",
            f"odoo:available_slots:{doctor_id}:*",
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)
    
    def cached(self, cache_type: str, ttl: Optional[int] = None):
        """
        Decorator for caching function results.
        
        Args:
            cache_type: Type of cache (must be in TTL dict)
            ttl: Optional custom TTL (overrides default)
        
        Usage:
            @odoo_cache.cached('patient_profile')
            def get_patient(patient_id: int):
                return odoo_client.get_patient(patient_id)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                key = self._make_key(cache_type, *args, **kwargs)
                
                # Try to get from cache
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # Call original function
                result = func(*args, **kwargs)
                
                # Cache the result
                if result is not None:
                    cache_ttl = ttl if ttl is not None else self.TTL.get(cache_type, 300)
                    self.set(key, result, cache_ttl)
                
                return result
            
            return wrapper
        return decorator


# Global cache instance
odoo_cache = OdooCache()


# Convenience functions for common operations
def cache_patient_profile(patient_id: int, data: Any) -> bool:
    """Cache patient profile data."""
    key = odoo_cache._make_key('patient_profile', patient_id)
    return odoo_cache.set(key, data, odoo_cache.TTL['patient_profile'])


def get_cached_patient_profile(patient_id: int) -> Optional[Any]:
    """Get cached patient profile data."""
    key = odoo_cache._make_key('patient_profile', patient_id)
    return odoo_cache.get(key)


def cache_appointments(patient_id: int, status: str, data: Any) -> bool:
    """Cache appointments data."""
    key = odoo_cache._make_key('appointments', patient_id=patient_id, status=status)
    return odoo_cache.set(key, data, odoo_cache.TTL['appointments'])


def get_cached_appointments(patient_id: int, status: str) -> Optional[Any]:
    """Get cached appointments data."""
    key = odoo_cache._make_key('appointments', patient_id=patient_id, status=status)
    return odoo_cache.get(key)


def cache_doctors(data: Any) -> bool:
    """Cache doctors list."""
    key = odoo_cache._make_key('doctors')
    return odoo_cache.set(key, data, odoo_cache.TTL['doctors'])


def get_cached_doctors() -> Optional[Any]:
    """Get cached doctors list."""
    key = odoo_cache._make_key('doctors')
    return odoo_cache.get(key)


def invalidate_patient_cache(patient_id: int):
    """Invalidate all cache for a patient."""
    odoo_cache.invalidate_patient(patient_id)


def invalidate_doctor_cache(doctor_id: int):
    """Invalidate all cache for a doctor."""
    odoo_cache.invalidate_doctor(doctor_id)

