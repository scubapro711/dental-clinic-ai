"""
Unit Tests for Encryption Service

Tests for app.core.encryption module including:
- EncryptionManager initialization and key management
- Encrypt/Decrypt operations
- Key derivation
- SQLAlchemy TypeDecorators (EncryptedString, EncryptedText, EncryptedBinary)
- Helper functions
- Error handling
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from cryptography.fernet import Fernet, InvalidToken
import base64

from app.core.encryption import (
    EncryptionManager,
    EncryptedString,
    EncryptedText,
    EncryptedBinary,
    encrypt_field,
    decrypt_field,
    generate_encryption_key,
    get_encryption_manager,
)


@pytest.fixture
def test_key():
    """Generate a test encryption key."""
    return Fernet.generate_key().decode('utf-8')


@pytest.fixture
def encryption_manager(test_key):
    """Create an EncryptionManager with test key."""
    return EncryptionManager(master_key=test_key)


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.encryption
class TestEncryptionManagerInitialization:
    """Test EncryptionManager initialization."""
    
    def test_init_with_provided_key(self, test_key):
        """Test initialization with provided master key."""
        manager = EncryptionManager(master_key=test_key)
        
        assert manager.master_key is not None
        assert manager.fernet is not None
    
    def test_init_with_env_key(self, test_key, monkeypatch):
        """Test initialization with key from environment variable."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        manager = EncryptionManager()
        
        assert manager.master_key is not None
        assert manager.fernet is not None
    
    def test_init_generates_key_if_missing(self, monkeypatch):
        """Test that a key is generated if none provided (dev mode)."""
        monkeypatch.delenv('ENCRYPTION_MASTER_KEY', raising=False)
        
        with patch('app.core.encryption.logger') as mock_logger:
            manager = EncryptionManager()
            
            assert manager.master_key is not None
            assert manager.fernet is not None
            # Should log warnings
            assert mock_logger.warning.call_count >= 2
    
    def test_init_with_invalid_key_raises_error(self):
        """Test that invalid key raises ValueError."""
        with pytest.raises(ValueError, match="Invalid encryption master key"):
            EncryptionManager(master_key="invalid-key")


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.encryption
class TestEncryptionManagerEncryptDecrypt:
    """Test encryption and decryption operations."""
    
    def test_encrypt_simple_string(self, encryption_manager):
        """Test encrypting a simple string."""
        plaintext = "Hello, World!"
        
        ciphertext = encryption_manager.encrypt(plaintext)
        
        assert ciphertext != plaintext
        assert len(ciphertext) > len(plaintext)
        assert isinstance(ciphertext, str)
    
    def test_decrypt_encrypted_string(self, encryption_manager):
        """Test decrypting an encrypted string."""
        plaintext = "Secret message"
        
        ciphertext = encryption_manager.encrypt(plaintext)
        decrypted = encryption_manager.decrypt(ciphertext)
        
        assert decrypted == plaintext
    
    def test_encrypt_empty_string(self, encryption_manager):
        """Test encrypting empty string returns empty string."""
        result = encryption_manager.encrypt("")
        assert result == ""
    
    def test_encrypt_none(self, encryption_manager):
        """Test encrypting None returns None."""
        result = encryption_manager.encrypt(None)
        assert result is None
    
    def test_decrypt_empty_string(self, encryption_manager):
        """Test decrypting empty string returns empty string."""
        result = encryption_manager.decrypt("")
        assert result == ""
    
    def test_decrypt_none(self, encryption_manager):
        """Test decrypting None returns None."""
        result = encryption_manager.decrypt(None)
        assert result is None
    
    def test_encrypt_unicode_characters(self, encryption_manager):
        """Test encrypting Unicode characters."""
        plaintext = "שלום עולם! 你好世界! مرحبا بالعالم!"
        
        ciphertext = encryption_manager.encrypt(plaintext)
        decrypted = encryption_manager.decrypt(ciphertext)
        
        assert decrypted == plaintext
    
    def test_encrypt_long_text(self, encryption_manager):
        """Test encrypting long text."""
        plaintext = "A" * 10000  # 10KB of text
        
        ciphertext = encryption_manager.encrypt(plaintext)
        decrypted = encryption_manager.decrypt(ciphertext)
        
        assert decrypted == plaintext
    
    def test_encrypt_special_characters(self, encryption_manager):
        """Test encrypting special characters."""
        plaintext = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        
        ciphertext = encryption_manager.encrypt(plaintext)
        decrypted = encryption_manager.decrypt(ciphertext)
        
        assert decrypted == plaintext
    
    def test_decrypt_with_wrong_key_raises_error(self, test_key):
        """Test that decrypting with wrong key raises error."""
        manager1 = EncryptionManager(master_key=test_key)
        manager2 = EncryptionManager(master_key=Fernet.generate_key().decode('utf-8'))
        
        ciphertext = manager1.encrypt("secret")
        
        with pytest.raises(Exception):  # InvalidToken or similar
            manager2.decrypt(ciphertext)
    
    def test_encrypt_decrypt_multiple_values(self, encryption_manager):
        """Test encrypting and decrypting multiple different values."""
        values = [
            "short",
            "a longer string with spaces",
            "123456789",
            "email@example.com",
            "+972-50-1234567",
        ]
        
        for value in values:
            ciphertext = encryption_manager.encrypt(value)
            decrypted = encryption_manager.decrypt(ciphertext)
            assert decrypted == value


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.encryption
class TestEncryptionManagerKeyDerivation:
    """Test key derivation functionality."""
    
    def test_derive_key_with_context(self, encryption_manager):
        """Test deriving a key with context."""
        context = "organization_123"
        
        derived_key = encryption_manager.derive_key(context)
        
        assert derived_key is not None
        assert isinstance(derived_key, bytes)
        # Key is base64-encoded, so 32 bytes becomes 44 bytes
        assert len(derived_key) == 44
    
    def test_derive_key_same_context_with_same_salt(self, encryption_manager):
        """Test that same context and salt produces same derived key."""
        context = "organization_123"
        salt = b"fixed_salt_12345"
        
        key1 = encryption_manager.derive_key(context, salt=salt)
        key2 = encryption_manager.derive_key(context, salt=salt)
        
        assert key1 == key2
    
    def test_derive_key_different_context_different_key(self, encryption_manager):
        """Test that different contexts produce different keys."""
        key1 = encryption_manager.derive_key("org_1")
        key2 = encryption_manager.derive_key("org_2")
        
        assert key1 != key2
    
    def test_derive_key_with_custom_salt(self, encryption_manager):
        """Test deriving key with custom salt."""
        context = "test"
        salt = b"custom_salt_1234"
        
        key = encryption_manager.derive_key(context, salt=salt)
        
        assert key is not None
        assert isinstance(key, bytes)
    
    def test_generate_key_returns_valid_key(self):
        """Test that generate_key returns a valid Fernet key."""
        key = EncryptionManager.generate_key()
        
        assert key is not None
        assert isinstance(key, str)
        
        # Should be able to create EncryptionManager with it
        manager = EncryptionManager(master_key=key)
        assert manager is not None


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.encryption
class TestEncryptedStringTypeDecorator:
    """Test EncryptedString SQLAlchemy TypeDecorator."""
    
    def test_encrypted_string_init(self):
        """Test EncryptedString initialization."""
        encrypted_type = EncryptedString(length=255)
        
        # EncryptedString adjusts length for encrypted data overhead
        assert encrypted_type.length > 255
    
    def test_process_bind_param_encrypts_value(self, test_key, monkeypatch):
        """Test that process_bind_param encrypts the value."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        encrypted_type = EncryptedString()
        plaintext = "sensitive data"
        
        encrypted = encrypted_type.process_bind_param(plaintext, None)
        
        assert encrypted != plaintext
        assert encrypted is not None
    
    def test_process_bind_param_none(self, test_key, monkeypatch):
        """Test that process_bind_param handles None."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        encrypted_type = EncryptedString()
        
        result = encrypted_type.process_bind_param(None, None)
        
        assert result is None
    
    def test_process_result_value_decrypts_value(self, test_key, monkeypatch):
        """Test that process_result_value decrypts the value."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        encrypted_type = EncryptedString()
        plaintext = "sensitive data"
        
        # Encrypt first
        encrypted = encrypted_type.process_bind_param(plaintext, None)
        
        # Then decrypt
        decrypted = encrypted_type.process_result_value(encrypted, None)
        
        assert decrypted == plaintext
    
    def test_process_result_value_none(self, test_key, monkeypatch):
        """Test that process_result_value handles None."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        encrypted_type = EncryptedString()
        
        result = encrypted_type.process_result_value(None, None)
        
        assert result is None


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.encryption
class TestEncryptedTextTypeDecorator:
    """Test EncryptedText SQLAlchemy TypeDecorator."""
    
    def test_encrypted_text_encrypts_long_text(self, test_key, monkeypatch):
        """Test EncryptedText can handle long text."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        encrypted_type = EncryptedText()
        plaintext = "A" * 5000  # 5KB of text
        
        encrypted = encrypted_type.process_bind_param(plaintext, None)
        decrypted = encrypted_type.process_result_value(encrypted, None)
        
        assert decrypted == plaintext


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.encryption
class TestEncryptedBinaryTypeDecorator:
    """Test EncryptedBinary SQLAlchemy TypeDecorator."""
    
    def test_encrypted_binary_encrypts_bytes(self, test_key, monkeypatch):
        """Test EncryptedBinary can handle binary data."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        encrypted_type = EncryptedBinary()
        plaintext = b"binary data \x00\x01\x02\x03"
        
        encrypted = encrypted_type.process_bind_param(plaintext, None)
        decrypted = encrypted_type.process_result_value(encrypted, None)
        
        assert decrypted == plaintext
    
    def test_encrypted_binary_none(self, test_key, monkeypatch):
        """Test EncryptedBinary handles None."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        encrypted_type = EncryptedBinary()
        
        encrypted = encrypted_type.process_bind_param(None, None)
        decrypted = encrypted_type.process_result_value(None, None)
        
        assert encrypted is None
        assert decrypted is None


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.encryption
class TestHelperFunctions:
    """Test helper functions."""
    
    def test_encrypt_field(self, test_key, monkeypatch):
        """Test encrypt_field helper function."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        plaintext = "sensitive data"
        
        encrypted = encrypt_field(plaintext)
        
        assert encrypted != plaintext
        assert encrypted is not None
    
    def test_decrypt_field(self, test_key, monkeypatch):
        """Test decrypt_field helper function."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        plaintext = "sensitive data"
        
        encrypted = encrypt_field(plaintext)
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == plaintext
    
    def test_generate_encryption_key(self):
        """Test generate_encryption_key helper function."""
        key = generate_encryption_key()
        
        assert key is not None
        assert isinstance(key, str)
        
        # Should be a valid Fernet key
        manager = EncryptionManager(master_key=key)
        test_data = "test"
        encrypted = manager.encrypt(test_data)
        decrypted = manager.decrypt(encrypted)
        assert decrypted == test_data
    
    def test_get_encryption_manager_singleton(self, test_key, monkeypatch):
        """Test that get_encryption_manager returns singleton."""
        monkeypatch.setenv('ENCRYPTION_MASTER_KEY', test_key)
        
        manager1 = get_encryption_manager()
        manager2 = get_encryption_manager()
        
        # Should be the same instance
        assert manager1 is manager2


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.encryption
class TestEncryptionErrorHandling:
    """Test error handling and edge cases."""
    
    def test_decrypt_invalid_ciphertext(self, encryption_manager):
        """Test that decrypting invalid ciphertext raises error."""
        invalid_ciphertext = "not-a-valid-ciphertext"
        
        with pytest.raises(Exception):
            encryption_manager.decrypt(invalid_ciphertext)
    
    def test_decrypt_corrupted_ciphertext(self, encryption_manager):
        """Test that decrypting corrupted ciphertext raises error."""
        plaintext = "secret"
        ciphertext = encryption_manager.encrypt(plaintext)
        
        # Corrupt the ciphertext
        corrupted = ciphertext[:-10] + "corrupted!"
        
        with pytest.raises(Exception):
            encryption_manager.decrypt(corrupted)
    
    def test_encrypt_very_long_text(self, encryption_manager):
        """Test encrypting very long text (100KB)."""
        plaintext = "A" * 100000  # 100KB
        
        ciphertext = encryption_manager.encrypt(plaintext)
        decrypted = encryption_manager.decrypt(ciphertext)
        
        assert decrypted == plaintext
    
    def test_encrypt_newlines_and_tabs(self, encryption_manager):
        """Test encrypting text with newlines and tabs."""
        plaintext = "Line 1\nLine 2\tTabbed\r\nWindows newline"
        
        ciphertext = encryption_manager.encrypt(plaintext)
        decrypted = encryption_manager.decrypt(ciphertext)
        
        assert decrypted == plaintext

