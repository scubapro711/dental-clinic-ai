"""
GCP Secret Manager Service for DentaFlow.AI
Handles secure storage and retrieval of secrets from Google Cloud Secret Manager
"""

import os
import logging
from typing import Optional, Dict
from google.cloud import secretmanager
from google.api_core import exceptions

logger = logging.getLogger(__name__)


class GCPSecretManager:
    """
    Service for managing secrets in Google Cloud Secret Manager.
    
    Provides secure storage and retrieval of encryption keys, API keys,
    and other sensitive configuration data.
    
    Environment Variables:
        GCP_PROJECT_ID: Google Cloud project ID
        GOOGLE_APPLICATION_CREDENTIALS: Path to service account key file (optional, uses default credentials if not set)
    """
    
    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize GCP Secret Manager client.
        
        Args:
            project_id: GCP project ID. If None, reads from GCP_PROJECT_ID env var.
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID environment variable not set")
        
        try:
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info(f"GCP Secret Manager initialized for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize GCP Secret Manager: {e}")
            raise
    
    def create_secret(self, secret_id: str, labels: Optional[Dict[str, str]] = None) -> str:
        """
        Create a new secret (without version/value).
        
        Args:
            secret_id: Unique identifier for the secret
            labels: Optional labels for the secret
            
        Returns:
            Secret name
        """
        parent = f"projects/{self.project_id}"
        
        try:
            secret = self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {
                        "replication": {"automatic": {}},
                        "labels": labels or {},
                    },
                }
            )
            logger.info(f"Created secret: {secret.name}")
            return secret.name
        except exceptions.AlreadyExists:
            logger.info(f"Secret already exists: {secret_id}")
            return f"{parent}/secrets/{secret_id}"
        except Exception as e:
            logger.error(f"Failed to create secret {secret_id}: {e}")
            raise
    
    def add_secret_version(self, secret_id: str, payload: str) -> str:
        """
        Add a new version to an existing secret.
        
        Args:
            secret_id: Secret identifier
            payload: Secret value (will be encoded to bytes)
            
        Returns:
            Version name
        """
        parent = f"projects/{self.project_id}/secrets/{secret_id}"
        
        try:
            version = self.client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": payload.encode("UTF-8")},
                }
            )
            logger.info(f"Added secret version: {version.name}")
            return version.name
        except Exception as e:
            logger.error(f"Failed to add secret version for {secret_id}: {e}")
            raise
    
    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Retrieve a secret value.
        
        Args:
            secret_id: Secret identifier
            version: Version to retrieve (default: "latest")
            
        Returns:
            Secret value as string
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
        
        try:
            response = self.client.access_secret_version(request={"name": name})
            payload = response.payload.data.decode("UTF-8")
            logger.info(f"Retrieved secret: {secret_id} (version: {version})")
            return payload
        except exceptions.NotFound:
            logger.error(f"Secret not found: {secret_id}")
            raise ValueError(f"Secret not found: {secret_id}")
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_id}: {e}")
            raise
    
    def update_secret(self, secret_id: str, payload: str) -> str:
        """
        Update a secret by adding a new version.
        
        Args:
            secret_id: Secret identifier
            payload: New secret value
            
        Returns:
            Version name
        """
        return self.add_secret_version(secret_id, payload)
    
    def delete_secret(self, secret_id: str) -> None:
        """
        Delete a secret and all its versions.
        
        Args:
            secret_id: Secret identifier
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}"
        
        try:
            self.client.delete_secret(request={"name": name})
            logger.info(f"Deleted secret: {secret_id}")
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_id}: {e}")
            raise
    
    def list_secrets(self) -> list:
        """
        List all secrets in the project.
        
        Returns:
            List of secret names
        """
        parent = f"projects/{self.project_id}"
        
        try:
            secrets = []
            for secret in self.client.list_secrets(request={"parent": parent}):
                secrets.append(secret.name)
            logger.info(f"Listed {len(secrets)} secrets")
            return secrets
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            raise
    
    def destroy_secret_version(self, secret_id: str, version: str) -> None:
        """
        Destroy a specific secret version (irreversible).
        
        Args:
            secret_id: Secret identifier
            version: Version to destroy
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
        
        try:
            self.client.destroy_secret_version(request={"name": name})
            logger.info(f"Destroyed secret version: {secret_id}/{version}")
        except Exception as e:
            logger.error(f"Failed to destroy secret version {secret_id}/{version}: {e}")
            raise


# Global instance
_gcp_secret_manager: Optional[GCPSecretManager] = None


def get_gcp_secret_manager() -> GCPSecretManager:
    """Get or create global GCP Secret Manager instance."""
    global _gcp_secret_manager
    
    if _gcp_secret_manager is None:
        _gcp_secret_manager = GCPSecretManager()
    
    return _gcp_secret_manager


# Helper functions for common secrets
def get_encryption_key() -> str:
    """Get encryption key from GCP Secret Manager or fallback to env var."""
    try:
        manager = get_gcp_secret_manager()
        return manager.get_secret("encryption-key")
    except Exception as e:
        logger.warning(f"Failed to get encryption key from GCP Secret Manager: {e}")
        logger.warning("Falling back to ENCRYPTION_KEY environment variable")
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY not found in GCP Secret Manager or environment variables")
        return key


def get_jwt_secret() -> str:
    """Get JWT secret key from GCP Secret Manager or fallback to env var."""
    try:
        manager = get_gcp_secret_manager()
        return manager.get_secret("jwt-secret-key")
    except Exception as e:
        logger.warning(f"Failed to get JWT secret from GCP Secret Manager: {e}")
        logger.warning("Falling back to SECRET_KEY environment variable")
        key = os.getenv('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY not found in GCP Secret Manager or environment variables")
        return key


def get_odoo_api_key() -> str:
    """Get Odoo API key from GCP Secret Manager or fallback to env var."""
    try:
        manager = get_gcp_secret_manager()
        return manager.get_secret("odoo-api-key")
    except Exception as e:
        logger.warning(f"Failed to get Odoo API key from GCP Secret Manager: {e}")
        logger.warning("Falling back to ODOO_API_KEY environment variable")
        key = os.getenv('ODOO_API_KEY')
        if not key:
            raise ValueError("ODOO_API_KEY not found in GCP Secret Manager or environment variables")
        return key


def get_stripe_secret_key() -> str:
    """Get Stripe secret key from GCP Secret Manager or fallback to env var."""
    try:
        manager = get_gcp_secret_manager()
        return manager.get_secret("stripe-secret-key")
    except Exception as e:
        logger.warning(f"Failed to get Stripe secret key from GCP Secret Manager: {e}")
        logger.warning("Falling back to STRIPE_SECRET_KEY environment variable")
        key = os.getenv('STRIPE_SECRET_KEY')
        if not key:
            raise ValueError("STRIPE_SECRET_KEY not found in GCP Secret Manager or environment variables")
        return key


# Example usage
if __name__ == "__main__":
    import sys
    
    # Set project ID
    os.environ['GCP_PROJECT_ID'] = 'dentaflow-ai'
    
    try:
        manager = GCPSecretManager()
        
        # Create a test secret
        print("Creating test secret...")
        manager.create_secret("test-secret", labels={"env": "development"})
        
        # Add a version
        print("Adding secret version...")
        manager.add_secret_version("test-secret", "my-secret-value-123")
        
        # Retrieve the secret
        print("Retrieving secret...")
        value = manager.get_secret("test-secret")
        print(f"Secret value: {value}")
        
        # List all secrets
        print("\nListing all secrets...")
        secrets = manager.list_secrets()
        for secret in secrets:
            print(f"  - {secret}")
        
        # Clean up
        print("\nDeleting test secret...")
        manager.delete_secret("test-secret")
        
        print("\n✅ GCP Secret Manager test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

