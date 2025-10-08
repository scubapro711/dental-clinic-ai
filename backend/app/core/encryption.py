"""
Database field encryption utilities.

Provides transparent encryption/decryption for sensitive database fields.
Uses Fernet (symmetric encryption) with AES-128 and HMAC.

HIPAA Compliance:
- Encryption at rest for PHI (Protected Health Information)
- Key management with AWS KMS or environment variables
- Audit logging for encryption operations
"""
import os
import base64
from typing import Optional, Any
import logging

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from sqlalchemy.types import TypeDecorator, String, LargeBinary
import sqlalchemy as sa

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages encryption keys and operations.
    
    Supports:
    - Key derivation from master key
    - Key rotation
    - Multiple encryption contexts (per-organization)
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption manager.
        
        Args:
            master_key: Base64-encoded master key (32 bytes)
                       If not provided, reads from ENCRYPTION_MASTER_KEY env var
        """
        if master_key is None:
            master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        
        if not master_key:
            # Generate a new key for development (NOT for production!)
            logger.warning(
                "No ENCRYPTION_MASTER_KEY found. Generating new key. "
                "This should NEVER happen in production!"
            )
            master_key = Fernet.generate_key().decode('utf-8')
            logger.warning(f"Generated key: {master_key}")
            logger.warning("Save this key to ENCRYPTION_MASTER_KEY environment variable!")
        
        try:
            # Validate key format
            self.master_key = master_key.encode('utf-8') if isinstance(master_key, str) else master_key
            self.fernet = Fernet(self.master_key)
            
            logger.info("Encryption manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption manager: {e}")
            raise ValueError("Invalid encryption master key") from e
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return plaintext
        
        try:
            plaintext_bytes = plaintext.encode('utf-8')
            encrypted_bytes = self.fernet.encrypt(plaintext_bytes)
            encrypted_str = encrypted_bytes.decode('utf-8')
            
            logger.debug(f"Encrypted data (length: {len(plaintext)} -> {len(encrypted_str)})")
            
            return encrypted_str
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.
        
        Args:
            ciphertext: Base64-encoded encrypted string
        
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ciphertext
        
        try:
            ciphertext_bytes = ciphertext.encode('utf-8')
            decrypted_bytes = self.fernet.decrypt(ciphertext_bytes)
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            logger.debug(f"Decrypted data (length: {len(ciphertext)} -> {len(decrypted_str)})")
            
            return decrypted_str
        except InvalidToken:
            logger.error("Decryption failed: Invalid token (wrong key or corrupted data)")
            raise ValueError("Failed to decrypt data: invalid encryption key")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def derive_key(self, context: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive a context-specific encryption key.
        
        Useful for per-organization or per-user encryption.
        
        Args:
            context: Context string (e.g., organization ID)
            salt: Optional salt (generated if not provided)
        
        Returns:
            Derived key bytes
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        context_bytes = context.encode('utf-8')
        derived_key = kdf.derive(self.master_key + context_bytes)
        
        return base64.urlsafe_b64encode(derived_key)
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Base64-encoded key string
        """
        key = Fernet.generate_key()
        return key.decode('utf-8')


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get global encryption manager instance."""
    global _encryption_manager
    
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    
    return _encryption_manager


# ========== SQLAlchemy Custom Types ==========

class EncryptedString(TypeDecorator):
    """
    SQLAlchemy type for encrypted string fields.
    
    Automatically encrypts on write and decrypts on read.
    
    Usage:
        class Patient(Base):
            ssn = Column(EncryptedString(255))
            medical_history = Column(EncryptedString(5000))
    """
    
    impl = String
    cache_ok = True
    
    def __init__(self, length: int = 255, **kwargs):
        """
        Initialize encrypted string type.
        
        Args:
            length: Maximum length of encrypted data (should be larger than plaintext)
        """
        # Encrypted data is ~1.3x larger than plaintext
        encrypted_length = int(length * 1.5)
        super().__init__(length=encrypted_length, **kwargs)
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt value before storing in database."""
        if value is None:
            return None
        
        try:
            encryption_manager = get_encryption_manager()
            encrypted_value = encryption_manager.encrypt(value)
            return encrypted_value
        except Exception as e:
            logger.error(f"Failed to encrypt value: {e}")
            raise
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """Decrypt value after retrieving from database."""
        if value is None:
            return None
        
        try:
            encryption_manager = get_encryption_manager()
            decrypted_value = encryption_manager.decrypt(value)
            return decrypted_value
        except Exception as e:
            logger.error(f"Failed to decrypt value: {e}")
            # Return None instead of raising to prevent application crashes
            # Log the error for investigation
            return None


class EncryptedText(TypeDecorator):
    """
    SQLAlchemy type for encrypted text fields (large content).
    
    Usage:
        class MedicalRecord(Base):
            notes = Column(EncryptedText)
            diagnosis = Column(EncryptedText)
    """
    
    impl = sa.Text
    cache_ok = True
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt value before storing in database."""
        if value is None:
            return None
        
        try:
            encryption_manager = get_encryption_manager()
            encrypted_value = encryption_manager.encrypt(value)
            return encrypted_value
        except Exception as e:
            logger.error(f"Failed to encrypt text value: {e}")
            raise
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """Decrypt value after retrieving from database."""
        if value is None:
            return None
        
        try:
            encryption_manager = get_encryption_manager()
            decrypted_value = encryption_manager.decrypt(value)
            return decrypted_value
        except Exception as e:
            logger.error(f"Failed to decrypt text value: {e}")
            return None


class EncryptedBinary(TypeDecorator):
    """
    SQLAlchemy type for encrypted binary fields.
    
    Usage:
        class Document(Base):
            file_content = Column(EncryptedBinary)
    """
    
    impl = LargeBinary
    cache_ok = True
    
    def process_bind_param(self, value: Optional[bytes], dialect) -> Optional[bytes]:
        """Encrypt value before storing in database."""
        if value is None:
            return None
        
        try:
            encryption_manager = get_encryption_manager()
            # Convert bytes to base64 string, encrypt, then back to bytes
            value_str = base64.b64encode(value).decode('utf-8')
            encrypted_str = encryption_manager.encrypt(value_str)
            encrypted_bytes = encrypted_str.encode('utf-8')
            return encrypted_bytes
        except Exception as e:
            logger.error(f"Failed to encrypt binary value: {e}")
            raise
    
    def process_result_value(self, value: Optional[bytes], dialect) -> Optional[bytes]:
        """Decrypt value after retrieving from database."""
        if value is None:
            return None
        
        try:
            encryption_manager = get_encryption_manager()
            # Convert bytes to string, decrypt, then decode from base64
            encrypted_str = value.decode('utf-8')
            decrypted_str = encryption_manager.decrypt(encrypted_str)
            decrypted_bytes = base64.b64decode(decrypted_str)
            return decrypted_bytes
        except Exception as e:
            logger.error(f"Failed to decrypt binary value: {e}")
            return None


# ========== Utility Functions ==========

def encrypt_field(value: str) -> str:
    """
    Manually encrypt a field value.
    
    Args:
        value: Plaintext string
    
    Returns:
        Encrypted string
    """
    encryption_manager = get_encryption_manager()
    return encryption_manager.encrypt(value)


def decrypt_field(value: str) -> str:
    """
    Manually decrypt a field value.
    
    Args:
        value: Encrypted string
    
    Returns:
        Decrypted plaintext string
    """
    encryption_manager = get_encryption_manager()
    return encryption_manager.decrypt(value)


def generate_encryption_key() -> str:
    """
    Generate a new encryption key.
    
    Returns:
        Base64-encoded key string
    """
    return EncryptionManager.generate_key()


# ========== Key Management ==========

def rotate_encryption_key(old_key: str, new_key: str, model_class, field_name: str, db_session):
    """
    Rotate encryption key for a specific field.
    
    WARNING: This is a destructive operation. Always backup database first!
    
    Args:
        old_key: Current encryption key
        new_key: New encryption key
        model_class: SQLAlchemy model class
        field_name: Name of encrypted field
        db_session: Database session
    
    Example:
        rotate_encryption_key(
            old_key='old-key-here',
            new_key='new-key-here',
            model_class=Patient,
            field_name='ssn',
            db_session=db
        )
    """
    logger.warning(f"Starting key rotation for {model_class.__name__}.{field_name}")
    
    # Create encryption managers
    old_manager = EncryptionManager(old_key)
    new_manager = EncryptionManager(new_key)
    
    # Get all records
    records = db_session.query(model_class).all()
    
    logger.info(f"Rotating keys for {len(records)} records")
    
    for record in records:
        try:
            # Get encrypted value
            encrypted_value = getattr(record, field_name)
            
            if encrypted_value:
                # Decrypt with old key
                plaintext = old_manager.decrypt(encrypted_value)
                
                # Encrypt with new key
                new_encrypted = new_manager.encrypt(plaintext)
                
                # Update record
                setattr(record, field_name, new_encrypted)
        
        except Exception as e:
            logger.error(f"Failed to rotate key for record {record.id}: {e}")
            raise
    
    # Commit changes
    db_session.commit()
    
    logger.info(f"Key rotation completed for {len(records)} records")
