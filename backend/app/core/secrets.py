"""
AWS Secrets Manager Integration

Manages secrets securely using AWS Secrets Manager:
- Database credentials
- API keys (OpenAI, Telegram, etc.)
- OAuth secrets
- Encryption keys

Usage:
    from app.core.secrets import secrets_manager
    
    db_creds = secrets_manager.get_database_credentials()
    openai_key = secrets_manager.get_openai_key()
"""

import boto3
import json
import logging
from functools import lru_cache
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecretsManager:
    """Manages secrets from AWS Secrets Manager."""
    
    def __init__(self, region_name: str = "us-east-1", app_env: str = "development"):
        """
        Initialize Secrets Manager client.
        
        Args:
            region_name: AWS region
            app_env: Application environment (development/staging/production)
        """
        self.region_name = region_name
        self.app_env = app_env
        self.client = None
        
        try:
            self.client = boto3.client(
                'secretsmanager',
                region_name=region_name
            )
            logger.info(f"Secrets Manager initialized for region: {region_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize Secrets Manager: {e}")
            logger.warning("Falling back to environment variables")
    
    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        Get secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            Dictionary containing secret data
            
        Raises:
            Exception if secret cannot be retrieved
        """
        if not self.client:
            raise Exception("Secrets Manager client not initialized")
        
        full_secret_name = f"dentaflow/{self.app_env}/{secret_name}"
        
        try:
            response = self.client.get_secret_value(SecretId=full_secret_name)
            
            if 'SecretString' in response:
                secret_data = json.loads(response['SecretString'])
                logger.info(f"Retrieved secret: {full_secret_name}")
                return secret_data
            else:
                raise Exception(f"Secret {full_secret_name} has no SecretString")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ResourceNotFoundException':
                logger.error(f"Secret not found: {full_secret_name}")
            elif error_code == 'InvalidRequestException':
                logger.error(f"Invalid request for secret: {full_secret_name}")
            elif error_code == 'InvalidParameterException':
                logger.error(f"Invalid parameter for secret: {full_secret_name}")
            elif error_code == 'DecryptionFailure':
                logger.error(f"Decryption failed for secret: {full_secret_name}")
            elif error_code == 'InternalServiceError':
                logger.error(f"Internal service error for secret: {full_secret_name}")
            else:
                logger.error(f"Unknown error retrieving secret: {e}")
            
            raise
        except Exception as e:
            logger.error(f"Failed to get secret {full_secret_name}: {e}")
            raise
    
    def get_database_credentials(self) -> Dict[str, str]:
        """
        Get database credentials.
        
        Returns:
            Dictionary with keys: host, port, database, username, password
        """
        return self.get_secret("database")
    
    def get_openai_key(self) -> str:
        """
        Get OpenAI API key.
        
        Returns:
            OpenAI API key string
        """
        secret = self.get_secret("openai")
        return secret['api_key']
    
    def get_telegram_token(self) -> str:
        """
        Get Telegram bot token.
        
        Returns:
            Telegram bot token string
        """
        secret = self.get_secret("telegram")
        return secret['bot_token']
    
    def get_odoo_credentials(self) -> Dict[str, str]:
        """
        Get Odoo credentials.
        
        Returns:
            Dictionary with keys: url, db, username, password
        """
        return self.get_secret("odoo")
    
    def get_aws_cognito_config(self) -> Dict[str, str]:
        """
        Get AWS Cognito configuration.
        
        Returns:
            Dictionary with keys: user_pool_id, client_id, client_secret, region
        """
        return self.get_secret("cognito")
    
    def get_encryption_key(self) -> str:
        """
        Get encryption key for database fields.
        
        Returns:
            Encryption key string
        """
        secret = self.get_secret("encryption")
        return secret['key']
    
    def get_jwt_secret(self) -> str:
        """
        Get JWT secret key.
        
        Returns:
            JWT secret string
        """
        secret = self.get_secret("jwt")
        return secret['secret_key']
    
    def create_secret(self, secret_name: str, secret_data: Dict[str, Any]) -> bool:
        """
        Create a new secret in AWS Secrets Manager.
        
        Args:
            secret_name: Name of the secret
            secret_data: Dictionary containing secret data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            raise Exception("Secrets Manager client not initialized")
        
        full_secret_name = f"dentaflow/{self.app_env}/{secret_name}"
        
        try:
            self.client.create_secret(
                Name=full_secret_name,
                SecretString=json.dumps(secret_data),
                Description=f"DentaFlow {self.app_env} - {secret_name}"
            )
            logger.info(f"Created secret: {full_secret_name}")
            
            # Clear cache
            self.get_secret.cache_clear()
            
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                logger.warning(f"Secret already exists: {full_secret_name}")
                return False
            else:
                logger.error(f"Failed to create secret: {e}")
                raise
    
    def update_secret(self, secret_name: str, secret_data: Dict[str, Any]) -> bool:
        """
        Update an existing secret.
        
        Args:
            secret_name: Name of the secret
            secret_data: Dictionary containing new secret data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            raise Exception("Secrets Manager client not initialized")
        
        full_secret_name = f"dentaflow/{self.app_env}/{secret_name}"
        
        try:
            self.client.update_secret(
                SecretId=full_secret_name,
                SecretString=json.dumps(secret_data)
            )
            logger.info(f"Updated secret: {full_secret_name}")
            
            # Clear cache
            self.get_secret.cache_clear()
            
            return True
        except ClientError as e:
            logger.error(f"Failed to update secret: {e}")
            raise
    
    def rotate_secret(self, secret_name: str) -> bool:
        """
        Trigger secret rotation.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            raise Exception("Secrets Manager client not initialized")
        
        full_secret_name = f"dentaflow/{self.app_env}/{secret_name}"
        
        try:
            self.client.rotate_secret(
                SecretId=full_secret_name,
                RotationLambdaARN=f"arn:aws:lambda:{self.region_name}:ACCOUNT_ID:function:dentaflow-secret-rotation"
            )
            logger.info(f"Triggered rotation for secret: {full_secret_name}")
            
            # Clear cache
            self.get_secret.cache_clear()
            
            return True
        except ClientError as e:
            logger.error(f"Failed to rotate secret: {e}")
            raise


# Singleton instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager(region_name: str = "us-east-1", app_env: str = "development") -> SecretsManager:
    """
    Get or create SecretsManager singleton instance.
    
    Args:
        region_name: AWS region
        app_env: Application environment
        
    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    
    if _secrets_manager is None:
        _secrets_manager = SecretsManager(region_name=region_name, app_env=app_env)
    
    return _secrets_manager


# Export singleton
secrets_manager = get_secrets_manager()
