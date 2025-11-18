"""
Tests for OdooClientFactory - Multi-Tenancy Support

This test suite ensures:
1. Backward compatibility - existing code continues to work
2. Multi-tenancy - organization-specific clients work correctly
3. Connection pooling - clients are reused, not recreated
4. Feature flag - enforcement works as expected
5. Error handling - graceful failures with clear messages
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

from app.integrations.odoo_client_factory import OdooClientFactory
from app.integrations.odoo_client import OdooClient


class TestOdooClientFactoryBackwardCompatibility:
    """Test that existing code continues to work without organization_id."""
    
    def setup_method(self):
        """Clear pool before each test."""
        OdooClientFactory.clear_pool()
    
    def test_get_client_without_org_id_returns_default(self):
        """Test that calling get_client() without org_id returns default client."""
        client = OdooClientFactory.get_client()
        assert client is not None
        assert isinstance(client, OdooClient)
    
    def test_get_client_without_org_id_returns_same_instance(self):
        """Test that default client is a singleton."""
        client1 = OdooClientFactory.get_client()
        client2 = OdooClientFactory.get_client()
        assert client1 is client2  # Same instance
    
    def test_get_client_uses_env_vars_for_default(self):
        """Test that default client uses environment variables."""
        with patch.dict(os.environ, {
            'ODOO_URL': 'https://test.odoo.com',
            'ODOO_DB': 'test_db',
            'ODOO_USERNAME': 'test_user',
            'ODOO_PASSWORD': 'test_pass'
        }):
            client = OdooClientFactory.get_client()
            assert client.url == 'https://test.odoo.com'
            assert client.db == 'test_db'
            assert client.username == 'test_user'
            assert client.password == 'test_pass'


class TestOdooClientFactoryMultiTenancy:
    """Test organization-specific client creation."""
    
    def setup_method(self):
        """Clear pool before each test."""
        OdooClientFactory.clear_pool()
    
    @patch('app.integrations.odoo_client_factory.SessionLocal')
    def test_get_client_with_org_id_creates_org_specific_client(self, mock_session_local):
        """Test that providing org_id creates organization-specific client."""
        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock organization
        mock_org = Mock()
        mock_org.odoo_db_name = 'org1_db'
        mock_org.odoo_username = 'org1_user'
        mock_org.odoo_api_key = 'org1_key'
        
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_org
        
        client = OdooClientFactory.get_client('org1')
        
        assert client is not None
        assert client.db == 'org1_db'
        assert client.username == 'org1_user'
        assert client.password == 'org1_key'
    
    @patch('app.integrations.odoo_client_factory.SessionLocal')
    def test_get_client_pools_org_specific_clients(self, mock_session_local):
        """Test that org-specific clients are pooled and reused."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_org = Mock()
        mock_org.odoo_db_name = 'org1_db'
        mock_org.odoo_username = 'org1_user'
        mock_org.odoo_api_key = 'org1_key'
        
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_org
        
        client1 = OdooClientFactory.get_client('org1')
        client2 = OdooClientFactory.get_client('org1')
        
        assert client1 is client2  # Same instance from pool
        # Database should only be queried once
        assert mock_session_local.call_count == 1
    
    @patch('app.integrations.odoo_client_factory.SessionLocal')
    def test_different_orgs_get_different_clients(self, mock_session_local):
        """Test that different organizations get different clients."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        def first_side_effect():
            # First call returns org1, second call returns org2
            if mock_session_local.call_count == 1:
                org = Mock()
                org.odoo_db_name = 'org1_db'
                org.odoo_username = 'org1_user'
                org.odoo_api_key = 'org1_key'
                return org
            else:
                org = Mock()
                org.odoo_db_name = 'org2_db'
                org.odoo_username = 'org2_user'
                org.odoo_api_key = 'org2_key'
                return org
        
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.side_effect = first_side_effect
        
        client1 = OdooClientFactory.get_client('org1')
        client2 = OdooClientFactory.get_client('org2')
        
        assert client1 is not client2  # Different instances
        assert client1.db == 'org1_db'
        assert client2.db == 'org2_db'


class TestOdooClientFactoryFeatureFlag:
    """Test ENFORCE_MULTI_TENANCY feature flag."""
    
    def setup_method(self):
        """Clear pool before each test."""
        OdooClientFactory.clear_pool()
    
    def test_feature_flag_off_allows_no_org_id(self):
        """Test that with flag OFF, org_id is optional."""
        with patch.dict(os.environ, {'ENFORCE_MULTI_TENANCY': 'false'}):
            client = OdooClientFactory.get_client()  # No org_id
            assert client is not None
    
    def test_feature_flag_on_requires_org_id(self):
        """Test that with flag ON, org_id is required."""
        with patch.dict(os.environ, {'ENFORCE_MULTI_TENANCY': 'true'}):
            with pytest.raises(ValueError, match="organization_id is required"):
                OdooClientFactory.get_client()  # No org_id
    
    @patch('app.integrations.odoo_client_factory.SessionLocal')
    def test_feature_flag_on_allows_with_org_id(self, mock_session_local):
        """Test that with flag ON, providing org_id works."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_org = Mock()
        mock_org.odoo_db_name = 'org1_db'
        mock_org.odoo_username = 'org1_user'
        mock_org.odoo_api_key = 'org1_key'
        
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_org
        
        with patch.dict(os.environ, {'ENFORCE_MULTI_TENANCY': 'true'}):
            client = OdooClientFactory.get_client('org1')
            assert client is not None


class TestOdooClientFactoryErrorHandling:
    """Test error handling and edge cases."""
    
    def setup_method(self):
        """Clear pool before each test."""
        OdooClientFactory.clear_pool()
    
    @patch('app.integrations.odoo_client_factory.SessionLocal')
    def test_missing_organization_raises_error(self, mock_session_local):
        """Test that missing organization raises clear error."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None  # No org found
        
        with pytest.raises(ValueError, match="Odoo credentials not configured"):
            OdooClientFactory.get_client('nonexistent_org')
    
    @patch('app.integrations.odoo_client_factory.SessionLocal')
    def test_org_without_odoo_config_raises_error(self, mock_session_local):
        """Test that organization without Odoo config raises error."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_org = Mock()
        mock_org.odoo_db_name = None  # Not configured
        mock_org.odoo_api_key = None
        
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_org
        
        with pytest.raises(ValueError, match="Odoo credentials not configured"):
            OdooClientFactory.get_client('org_without_odoo')
    
    def test_clear_pool_removes_all_clients(self):
        """Test that clear_pool removes all cached clients."""
        # Create some clients
        client1 = OdooClientFactory.get_client()
        
        # Clear pool
        OdooClientFactory.clear_pool()
        
        # Get client again - should be new instance
        client2 = OdooClientFactory.get_client()
        assert client1 is not client2
