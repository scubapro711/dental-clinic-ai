"""
Encryption Service for DentaFlow.AI
Handles encryption/decryption of sensitive data
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Service for encrypting/decrypting sensitive data.
    
    Uses Fernet (symmetric encryption) with AES-128 in CBC mode.
    Key is derived from ENCRYPTION_KEY environment variable using PBKDF2.
    """
    
    def __init__(self, key: Optional[str] = None):
        """
        Initialize encryption service.
        
        Args:
            key: Encryption key (base64 encoded). If None, tries GCP Secret Manager first,
                 then falls back to ENCRYPTION_KEY env var.
        """
        if key is None:
            # Try GCP Secret Manager first
            try:
                from .gcp_secrets import get_encryption_key
                key = get_encryption_key()
                logger.info("Using encryption key from GCP Secret Manager")
            except Exception as e:
                logger.warning(f"Failed to get encryption key from GCP Secret Manager: {e}")
                logger.warning("Falling back to ENCRYPTION_KEY environment variable")
                key = os.getenv('ENCRYPTION_KEY')
        
        if not key:
            raise ValueError("ENCRYPTION_KEY not found in GCP Secret Manager or environment variables")
        
        # Derive Fernet key from provided key using PBKDF2
        self.cipher = Fernet(self._derive_key(key))
        logger.info("Encryption service initialized")
    
    def _derive_key(self, password: str) -> bytes:
        """
        Derive a Fernet key from password using PBKDF2.
        
        Args:
            password: Password/key string
            
        Returns:
            Base64-encoded Fernet key
        """
        # Use a fixed salt for deterministic key derivation
        # In production, consider using a per-field salt stored with the data
        salt = b'dentaflow-salt-v1'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string.
        
        Args:
            data: Plain text string
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not data:
            return data
        
        try:
            encrypted_bytes = self.cipher.encrypt(data.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string.
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            Decrypted plain text string
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary with data
            fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary with encrypted data
            fields: List of field names to decrypt
            
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt(str(decrypted_data[field]))
        
        return decrypted_data


# Global instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create global encryption service instance."""
    global _encryption_service
    
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    
    return _encryption_service


# Example usage
if __name__ == "__main__":
    # Generate a new key (do this once and store securely)
    # key = Fernet.generate_key().decode()
    # print(f"Generated key: {key}")
    
    # Set environment variable
    os.environ['ENCRYPTION_KEY'] = 'test-key-for-development-only'
    
    # Test encryption
    service = get_encryption_service()
    
    # Encrypt sensitive data
    ssn = "123-45-6789"
    credit_card = "4111-1111-1111-1111"
    
    encrypted_ssn = service.encrypt(ssn)
    encrypted_cc = service.encrypt(credit_card)
    
    print(f"Original SSN: {ssn}")
    print(f"Encrypted SSN: {encrypted_ssn}")
    print(f"Decrypted SSN: {service.decrypt(encrypted_ssn)}")
    print()
    print(f"Original CC: {credit_card}")
    print(f"Encrypted CC: {encrypted_cc}")
    print(f"Decrypted CC: {service.decrypt(encrypted_cc)}")
    
    # Test dict encryption
    patient_data = {
        "name": "John Doe",
        "ssn": "123-45-6789",
        "credit_card": "4111-1111-1111-1111",
        "phone": "555-1234"
    }
    
    encrypted_patient = service.encrypt_dict(patient_data, ["ssn", "credit_card"])
    print(f"\nEncrypted patient data: {encrypted_patient}")
    
    decrypted_patient = service.decrypt_dict(encrypted_patient, ["ssn", "credit_card"])
    print(f"Decrypted patient data: {decrypted_patient}")
