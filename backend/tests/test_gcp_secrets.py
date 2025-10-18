"""
Tests for GCP Secret Manager Integration
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from google.api_core import exceptions

from app.core.gcp_secrets import (
    GCPSecretManager,
    get_gcp_secret_manager,
    get_encryption_key,
    get_jwt_secret,
    get_odoo_api_key,
    get_stripe_secret_key,
)


@pytest.fixture
def mock_secret_manager_client():
    """Mock Secret Manager client."""
    with patch('app.core.gcp_secrets.secretmanager.SecretManagerServiceClient') as mock:
        yield mock


@pytest.fixture
def gcp_manager(mock_secret_manager_client):
    """Create GCP Secret Manager instance with mocked client."""
    os.environ['GCP_PROJECT_ID'] = 'test-project'
    manager = GCPSecretManager()
    return manager


class TestGCPSecretManager:
    """Test GCP Secret Manager service."""
    
    def test_init_without_project_id(self, mock_secret_manager_client):
        """Test initialization without project ID raises error."""
        if 'GCP_PROJECT_ID' in os.environ:
            del os.environ['GCP_PROJECT_ID']
        
        with pytest.raises(ValueError, match="GCP_PROJECT_ID environment variable not set"):
            GCPSecretManager()
    
    def test_init_with_project_id(self, mock_secret_manager_client):
        """Test successful initialization with project ID."""
        manager = GCPSecretManager(project_id='test-project')
        assert manager.project_id == 'test-project'
        assert manager.client is not None
    
    def test_create_secret_success(self, gcp_manager, mock_secret_manager_client):
        """Test creating a new secret."""
        mock_secret = Mock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        gcp_manager.client.create_secret.return_value = mock_secret
        
        result = gcp_manager.create_secret('test-secret', labels={'env': 'test'})
        
        assert result == mock_secret.name
        gcp_manager.client.create_secret.assert_called_once()
    
    def test_create_secret_already_exists(self, gcp_manager, mock_secret_manager_client):
        """Test creating a secret that already exists."""
        gcp_manager.client.create_secret.side_effect = exceptions.AlreadyExists('Secret exists')
        
        result = gcp_manager.create_secret('existing-secret')
        
        assert result == 'projects/test-project/secrets/existing-secret'
    
    def test_add_secret_version(self, gcp_manager, mock_secret_manager_client):
        """Test adding a new version to a secret."""
        mock_version = Mock()
        mock_version.name = 'projects/test-project/secrets/test-secret/versions/1'
        gcp_manager.client.add_secret_version.return_value = mock_version
        
        result = gcp_manager.add_secret_version('test-secret', 'secret-value')
        
        assert result == mock_version.name
        gcp_manager.client.add_secret_version.assert_called_once()
    
    def test_get_secret_success(self, gcp_manager, mock_secret_manager_client):
        """Test retrieving a secret value."""
        mock_response = Mock()
        mock_response.payload.data = b'secret-value'
        gcp_manager.client.access_secret_version.return_value = mock_response
        
        result = gcp_manager.get_secret('test-secret')
        
        assert result == 'secret-value'
        gcp_manager.client.access_secret_version.assert_called_once()
    
    def test_get_secret_not_found(self, gcp_manager, mock_secret_manager_client):
        """Test retrieving a non-existent secret."""
        gcp_manager.client.access_secret_version.side_effect = exceptions.NotFound('Secret not found')
        
        with pytest.raises(ValueError, match="Secret not found: test-secret"):
            gcp_manager.get_secret('test-secret')
    
    def test_update_secret(self, gcp_manager, mock_secret_manager_client):
        """Test updating a secret (adds new version)."""
        mock_version = Mock()
        mock_version.name = 'projects/test-project/secrets/test-secret/versions/2'
        gcp_manager.client.add_secret_version.return_value = mock_version
        
        result = gcp_manager.update_secret('test-secret', 'new-value')
        
        assert result == mock_version.name
    
    def test_delete_secret(self, gcp_manager, mock_secret_manager_client):
        """Test deleting a secret."""
        gcp_manager.delete_secret('test-secret')
        
        gcp_manager.client.delete_secret.assert_called_once()
    
    def test_list_secrets(self, gcp_manager, mock_secret_manager_client):
        """Test listing all secrets."""
        mock_secrets = [
            Mock(name='projects/test-project/secrets/secret1'),
            Mock(name='projects/test-project/secrets/secret2'),
        ]
        gcp_manager.client.list_secrets.return_value = mock_secrets
        
        result = gcp_manager.list_secrets()
        
        assert len(result) == 2
        assert result[0] == 'projects/test-project/secrets/secret1'
        assert result[1] == 'projects/test-project/secrets/secret2'
    
    def test_destroy_secret_version(self, gcp_manager, mock_secret_manager_client):
        """Test destroying a specific secret version."""
        gcp_manager.destroy_secret_version('test-secret', '1')
        
        gcp_manager.client.destroy_secret_version.assert_called_once()


class TestHelperFunctions:
    """Test helper functions for common secrets."""
    
    @patch('app.core.gcp_secrets.get_gcp_secret_manager')
    def test_get_encryption_key_from_gcp(self, mock_get_manager):
        """Test getting encryption key from GCP Secret Manager."""
        mock_manager = Mock()
        mock_manager.get_secret.return_value = 'gcp-encryption-key'
        mock_get_manager.return_value = mock_manager
        
        result = get_encryption_key()
        
        assert result == 'gcp-encryption-key'
        mock_manager.get_secret.assert_called_once_with('encryption-key')
    
    @patch('app.core.gcp_secrets.get_gcp_secret_manager')
    def test_get_encryption_key_fallback_to_env(self, mock_get_manager):
        """Test falling back to environment variable if GCP fails."""
        mock_manager = Mock()
        mock_manager.get_secret.side_effect = Exception('GCP error')
        mock_get_manager.return_value = mock_manager
        
        os.environ['ENCRYPTION_KEY'] = 'env-encryption-key'
        
        result = get_encryption_key()
        
        assert result == 'env-encryption-key'
    
    @patch('app.core.gcp_secrets.get_gcp_secret_manager')
    def test_get_encryption_key_not_found(self, mock_get_manager):
        """Test error when encryption key not found anywhere."""
        mock_manager = Mock()
        mock_manager.get_secret.side_effect = Exception('GCP error')
        mock_get_manager.return_value = mock_manager
        
        if 'ENCRYPTION_KEY' in os.environ:
            del os.environ['ENCRYPTION_KEY']
        
        with pytest.raises(ValueError, match="ENCRYPTION_KEY not found"):
            get_encryption_key()
    
    @patch('app.core.gcp_secrets.get_gcp_secret_manager')
    def test_get_jwt_secret_from_gcp(self, mock_get_manager):
        """Test getting JWT secret from GCP Secret Manager."""
        mock_manager = Mock()
        mock_manager.get_secret.return_value = 'gcp-jwt-secret'
        mock_get_manager.return_value = mock_manager
        
        result = get_jwt_secret()
        
        assert result == 'gcp-jwt-secret'
        mock_manager.get_secret.assert_called_once_with('jwt-secret-key')
    
    @patch('app.core.gcp_secrets.get_gcp_secret_manager')
    def test_get_odoo_api_key_from_gcp(self, mock_get_manager):
        """Test getting Odoo API key from GCP Secret Manager."""
        mock_manager = Mock()
        mock_manager.get_secret.return_value = 'gcp-odoo-key'
        mock_get_manager.return_value = mock_manager
        
        result = get_odoo_api_key()
        
        assert result == 'gcp-odoo-key'
        mock_manager.get_secret.assert_called_once_with('odoo-api-key')
    
    @patch('app.core.gcp_secrets.get_gcp_secret_manager')
    def test_get_stripe_secret_key_from_gcp(self, mock_get_manager):
        """Test getting Stripe secret key from GCP Secret Manager."""
        mock_manager = Mock()
        mock_manager.get_secret.return_value = 'gcp-stripe-key'
        mock_get_manager.return_value = mock_manager
        
        result = get_stripe_secret_key()
        
        assert result == 'gcp-stripe-key'
        mock_manager.get_secret.assert_called_once_with('stripe-secret-key')


class TestEncryptionServiceIntegration:
    """Test encryption service integration with GCP Secret Manager."""
    
    @patch('app.core.encryption_service.get_encryption_key')
    def test_encryption_service_uses_gcp(self, mock_get_key):
        """Test that encryption service uses GCP Secret Manager."""
        from app.core.encryption_service import EncryptionService
        
        mock_get_key.return_value = 'test-encryption-key'
        
        service = EncryptionService()
        
        # Verify it tried to get key from GCP
        mock_get_key.assert_called_once()
    
    @patch('app.core.encryption_service.get_encryption_key')
    def test_encryption_service_fallback_to_env(self, mock_get_key):
        """Test that encryption service falls back to env var."""
        from app.core.encryption_service import EncryptionService
        
        mock_get_key.side_effect = Exception('GCP error')
        os.environ['ENCRYPTION_KEY'] = 'env-key'
        
        service = EncryptionService()
        
        # Should have tried GCP first, then fallen back to env
        assert service is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

