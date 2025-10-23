"""Unit Tests for Odoo Cache Service"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import redis

from app.services.odoo_cache import OdooCache


@pytest.mark.unit
@pytest.mark.services
class TestOdooCache:
    """Test Odoo Cache service."""
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_init_success(self, mock_redis):
        """Test successful cache initialization."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = OdooCache()
        
        assert cache.enabled is True
        assert cache.redis_client is not None
        mock_client.ping.assert_called_once()
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_init_failure(self, mock_redis):
        """Test cache initialization failure."""
        mock_redis.side_effect = redis.ConnectionError("Connection failed")
        
        cache = OdooCache()
        
        assert cache.enabled is False
        assert cache.redis_client is None
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_make_key_simple(self, mock_redis):
        """Test cache key generation."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = OdooCache()
        key = cache._make_key("patient_profile", 123)
        
        assert key.startswith("odoo:patient_profile")
        assert "123" in key
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_make_key_with_kwargs(self, mock_redis):
        """Test cache key with keyword arguments."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = OdooCache()
        key = cache._make_key("appointments", clinic_id=5, date="2025-01-01")
        
        assert "odoo:appointments" in key
        assert "clinic_id" in key or "5" in key
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_get_cache_hit(self, mock_redis):
        """Test getting value from cache (hit)."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = '{"name": "John"}'
        mock_redis.return_value = mock_client
        
        cache = OdooCache()
        key = cache._make_key("patient_profile", 123)
        value = cache.get(key)
        
        assert value == {"name": "John"}
        mock_client.get.assert_called_once()
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_get_cache_miss(self, mock_redis):
        """Test getting value from cache (miss)."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_redis.return_value = mock_client
        
        cache = OdooCache()
        key = cache._make_key("patient_profile", 999)
        value = cache.get(key)
        
        assert value is None
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_set_cache(self, mock_redis):
        """Test setting value in cache."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = OdooCache()
        cache.set("patient_profile", {"name": "Jane"}, 123)
        
        mock_client.setex.assert_called_once()
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_delete_cache(self, mock_redis):
        """Test deleting value from cache."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        cache = OdooCache()
        key = cache._make_key("patient_profile", 123)
        cache.delete(key)
        
        mock_client.delete.assert_called_once()
    
    @patch('app.services.odoo_cache.redis.from_url')
    def test_cache_disabled_get(self, mock_redis):
        """Test get when cache is disabled."""
        mock_redis.side_effect = redis.ConnectionError()
        
        cache = OdooCache()
        key = cache._make_key("patient_profile", 123)
        value = cache.get(key)
        
        assert value is None
    
    def test_ttl_configuration(self):
        """Test TTL configuration exists."""
        assert OdooCache.TTL['patient_profile'] == 300
        assert OdooCache.TTL['appointments'] == 120
        assert OdooCache.TTL['treatments'] == 3600

