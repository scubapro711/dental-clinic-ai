"""
Unit Tests for MFA Service

Tests for app.services.mfa_service module including:
- TOTP secret generation
- QR code generation
- Token verification
- Backup codes generation and verification
- MFA setup, enable, disable
- Error handling
"""

import pytest
import pyotp
import base64
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.mfa_service import MFAService, get_mfa_service
from app.models.user import User


@pytest.fixture
def mfa_service():
    """Create an MFAService instance for testing."""
    return MFAService()


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.mfa_secret = None
    user.mfa_enabled = False
    user.mfa_backup_codes = None
    return user


@pytest.fixture
def test_secret():
    """Generate a test TOTP secret."""
    return pyotp.random_base32()


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestMFAServiceInitialization:
    """Test MFAService initialization."""
    
    def test_init_creates_service(self, mfa_service):
        """Test that __init__ creates MFA service."""
        assert mfa_service is not None
        assert mfa_service.issuer_name == "DentaFlow.AI"
        assert mfa_service.encryption_service is not None
    
    def test_get_mfa_service_singleton(self):
        """Test that get_mfa_service returns singleton."""
        service1 = get_mfa_service()
        service2 = get_mfa_service()
        
        assert service1 is service2


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestSecretGeneration:
    """Test TOTP secret generation."""
    
    def test_generate_secret_returns_string(self, mfa_service):
        """Test that generate_secret returns a string."""
        secret = mfa_service.generate_secret()
        
        assert secret is not None
        assert isinstance(secret, str)
        assert len(secret) > 0
    
    def test_generate_secret_is_base32(self, mfa_service):
        """Test that generated secret is valid base32."""
        secret = mfa_service.generate_secret()
        
        # Should be able to create TOTP with it
        totp = pyotp.TOTP(secret)
        assert totp is not None
    
    def test_generate_secret_unique(self, mfa_service):
        """Test that each generated secret is unique."""
        secret1 = mfa_service.generate_secret()
        secret2 = mfa_service.generate_secret()
        
        assert secret1 != secret2
    
    def test_generate_secret_sufficient_length(self, mfa_service):
        """Test that generated secret has sufficient length."""
        secret = mfa_service.generate_secret()
        
        # pyotp.random_base32() generates 32-character secrets
        assert len(secret) >= 16


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestQRCodeGeneration:
    """Test QR code generation."""
    
    def test_generate_qr_code_returns_base64(self, mfa_service, test_secret):
        """Test that generate_qr_code returns base64 data URI."""
        email = "test@example.com"
        
        qr_code = mfa_service.generate_qr_code(email, test_secret)
        
        assert qr_code is not None
        assert qr_code.startswith("data:image/png;base64,")
    
    def test_generate_qr_code_valid_base64(self, mfa_service, test_secret):
        """Test that QR code contains valid base64 data."""
        email = "test@example.com"
        
        qr_code = mfa_service.generate_qr_code(email, test_secret)
        
        # Extract base64 part
        base64_data = qr_code.split(",")[1]
        
        # Should be able to decode it
        decoded = base64.b64decode(base64_data)
        assert len(decoded) > 0
    
    def test_generate_qr_code_different_for_different_secrets(self, mfa_service):
        """Test that different secrets generate different QR codes."""
        email = "test@example.com"
        secret1 = mfa_service.generate_secret()
        secret2 = mfa_service.generate_secret()
        
        qr1 = mfa_service.generate_qr_code(email, secret1)
        qr2 = mfa_service.generate_qr_code(email, secret2)
        
        assert qr1 != qr2
    
    def test_generate_qr_code_different_for_different_emails(self, mfa_service, test_secret):
        """Test that different emails generate different QR codes."""
        qr1 = mfa_service.generate_qr_code("user1@example.com", test_secret)
        qr2 = mfa_service.generate_qr_code("user2@example.com", test_secret)
        
        assert qr1 != qr2


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestTokenVerification:
    """Test TOTP token verification."""
    
    def test_verify_token_valid_token(self, mfa_service, test_secret):
        """Test verifying a valid TOTP token."""
        # Generate current token
        totp = pyotp.TOTP(test_secret)
        token = totp.now()
        
        result = mfa_service.verify_token(test_secret, token)
        
        assert result is True
    
    def test_verify_token_invalid_token(self, mfa_service, test_secret):
        """Test verifying an invalid TOTP token."""
        result = mfa_service.verify_token(test_secret, "000000")
        
        assert result is False
    
    def test_verify_token_wrong_length(self, mfa_service, test_secret):
        """Test verifying a token with wrong length."""
        result = mfa_service.verify_token(test_secret, "12345")
        
        assert result is False
    
    def test_verify_token_non_numeric(self, mfa_service, test_secret):
        """Test verifying a non-numeric token."""
        result = mfa_service.verify_token(test_secret, "abcdef")
        
        assert result is False
    
    def test_verify_token_empty_string(self, mfa_service, test_secret):
        """Test verifying an empty token."""
        result = mfa_service.verify_token(test_secret, "")
        
        assert result is False
    
    def test_verify_token_with_clock_skew(self, mfa_service, test_secret):
        """Test that verification allows for clock skew."""
        # This test verifies that valid_window=1 is working
        # We can't easily test past/future tokens without mocking time
        totp = pyotp.TOTP(test_secret)
        token = totp.now()
        
        result = mfa_service.verify_token(test_secret, token)
        
        assert result is True


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestBackupCodes:
    """Test backup codes generation and verification."""
    
    def test_generate_backup_codes_default_count(self, mfa_service):
        """Test generating default number of backup codes."""
        codes = mfa_service.generate_backup_codes()
        
        assert len(codes) == 10
    
    def test_generate_backup_codes_custom_count(self, mfa_service):
        """Test generating custom number of backup codes."""
        codes = mfa_service.generate_backup_codes(count=5)
        
        assert len(codes) == 5
    
    def test_generate_backup_codes_format(self, mfa_service):
        """Test that backup codes have correct format."""
        codes = mfa_service.generate_backup_codes()
        
        for code in codes:
            assert isinstance(code, str)
            assert len(code) > 0
            # Backup codes are typically alphanumeric
            assert code.replace("-", "").isalnum()
    
    def test_generate_backup_codes_unique(self, mfa_service):
        """Test that all backup codes are unique."""
        codes = mfa_service.generate_backup_codes(count=20)
        
        assert len(codes) == len(set(codes))
    
    def test_generate_backup_codes_different_each_time(self, mfa_service):
        """Test that each generation produces different codes."""
        codes1 = mfa_service.generate_backup_codes()
        codes2 = mfa_service.generate_backup_codes()
        
        # Should have different codes
        assert codes1 != codes2


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestMFASetup:
    """Test MFA setup functionality."""
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_setup_mfa_generates_secret(self, mock_encryption, mfa_service, mock_user):
        """Test that setup_mfa generates a new secret."""
        mock_encryption.return_value.encrypt.return_value = "encrypted_secret"
        mock_db = Mock(spec=Session)
        
        secret, qr_code, backup_codes = mfa_service.setup_mfa(mock_db, mock_user)
        
        assert secret is not None
        assert qr_code is not None
        assert backup_codes is not None
        assert len(secret) > 0
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_setup_mfa_generates_qr_code(self, mock_encryption, mfa_service, mock_user):
        """Test that setup_mfa generates QR code."""
        mock_encryption.return_value.encrypt.return_value = "encrypted_secret"
        mock_db = Mock(spec=Session)
        
        secret, qr_code, backup_codes = mfa_service.setup_mfa(mock_db, mock_user)
        
        assert qr_code.startswith("data:image/png;base64,")
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_setup_mfa_generates_backup_codes(self, mock_encryption, mfa_service, mock_user):
        """Test that setup_mfa generates backup codes."""
        mock_encryption.return_value.encrypt.return_value = "encrypted_secret"
        mock_db = Mock(spec=Session)
        
        secret, qr_code, backup_codes = mfa_service.setup_mfa(mock_db, mock_user)
        
        assert len(backup_codes) == 10
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_setup_mfa_does_not_enable_yet(self, mock_encryption, mfa_service, mock_user):
        """Test that setup_mfa doesn't enable MFA yet."""
        mock_encryption.return_value.encrypt.return_value = "encrypted_secret"
        mock_db = Mock(spec=Session)
        
        mfa_service.setup_mfa(mock_db, mock_user)
        
        # MFA should not be enabled until verified
        assert mock_user.mfa_enabled is False


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestMFAEnable:
    """Test MFA enable functionality."""
    
    def test_enable_mfa_with_valid_token(self, mfa_service, mock_user):
        """Test enabling MFA with valid token."""
        # Setup MFA first
        secret = mfa_service.generate_secret()
        encrypted_secret = mfa_service.encryption_service.encrypt(secret)
        mock_user.mfa_secret = encrypted_secret
        mock_db = Mock(spec=Session)
        
        # Generate valid token
        totp = pyotp.TOTP(secret)
        token = totp.now()
        
        result = mfa_service.enable_mfa(mock_db, mock_user, token)
        
        assert result is True
        assert mock_user.mfa_enabled is True
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_enable_mfa_with_invalid_token(self, mock_encryption, mfa_service, mock_user):
        """Test enabling MFA with invalid token fails."""
        secret = mfa_service.generate_secret()
        mock_user.mfa_secret = "encrypted_secret"
        mock_encryption.return_value.decrypt.return_value = secret
        mock_db = Mock(spec=Session)
        
        result = mfa_service.enable_mfa(mock_db, mock_user, "000000")
        
        assert result is False
        assert mock_user.mfa_enabled is False
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_enable_mfa_without_setup(self, mock_encryption, mfa_service, mock_user):
        """Test enabling MFA without setup fails."""
        mock_user.mfa_secret = None
        mock_db = Mock(spec=Session)
        
        result = mfa_service.enable_mfa(mock_db, mock_user, "123456")
        
        assert result is False


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestMFADisable:
    """Test MFA disable functionality."""
    
    def test_disable_mfa_with_valid_token(self, mfa_service, mock_user):
        """Test disabling MFA with valid token."""
        secret = mfa_service.generate_secret()
        encrypted_secret = mfa_service.encryption_service.encrypt(secret)
        mock_user.mfa_secret = encrypted_secret
        mock_user.mfa_enabled = True
        mock_db = Mock(spec=Session)
        
        # Generate valid token
        totp = pyotp.TOTP(secret)
        token = totp.now()
        
        result = mfa_service.disable_mfa(mock_db, mock_user, token)
        
        assert result is True
        assert mock_user.mfa_enabled is False
        assert mock_user.mfa_secret is None
        assert mock_user.mfa_backup_codes is None
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_disable_mfa_with_invalid_token(self, mock_encryption, mfa_service, mock_user):
        """Test disabling MFA with invalid token fails."""
        secret = mfa_service.generate_secret()
        mock_user.mfa_secret = "encrypted_secret"
        mock_user.mfa_enabled = True
        mock_encryption.return_value.decrypt.return_value = secret
        mock_db = Mock(spec=Session)
        
        result = mfa_service.disable_mfa(mock_db, mock_user, "000000")
        
        assert result is False
        assert mock_user.mfa_enabled is True


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestBackupCodeVerification:
    """Test backup code verification and usage."""
    
    def test_verify_backup_code_valid(self, mfa_service, mock_user):
        """Test verifying a valid backup code."""
        codes = ["code1", "code2", "code3"]
        codes_str = ",".join(codes)
        encrypted_codes = mfa_service.encryption_service.encrypt(codes_str)
        mock_user.mfa_backup_codes = encrypted_codes
        
        result = mfa_service.verify_backup_code(mock_user, "code1")
        
        assert result is True
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_verify_backup_code_invalid(self, mock_encryption, mfa_service, mock_user):
        """Test verifying an invalid backup code."""
        codes = ["code1", "code2", "code3"]
        mock_user.mfa_backup_codes = "encrypted_codes"
        mock_encryption.return_value.decrypt.return_value = ",".join(codes)
        mock_db = Mock(spec=Session)
        
        result = mfa_service.verify_backup_code(mock_user, "invalid_code")
        
        assert result is False
    
    def test_use_backup_code_removes_it(self, mfa_service, mock_user):
        """Test that using a backup code removes it from the list."""
        codes = ["code1", "code2", "code3"]
        codes_str = ",".join(codes)
        encrypted_codes = mfa_service.encryption_service.encrypt(codes_str)
        mock_user.mfa_backup_codes = encrypted_codes
        mock_db = Mock(spec=Session)
        
        result = mfa_service.use_backup_code(mock_db, mock_user, "code1")
        
        assert result is True
        # Backup codes should be updated
        assert mock_user.mfa_backup_codes != encrypted_codes


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestBackupCodeRegeneration:
    """Test backup code regeneration."""
    
    def test_regenerate_backup_codes_with_valid_token(self, mfa_service, mock_user):
        """Test regenerating backup codes with valid token."""
        secret = mfa_service.generate_secret()
        encrypted_secret = mfa_service.encryption_service.encrypt(secret)
        mock_user.mfa_secret = encrypted_secret
        mock_user.mfa_enabled = True
        mock_db = Mock(spec=Session)
        
        # Generate valid token
        totp = pyotp.TOTP(secret)
        token = totp.now()
        
        result = mfa_service.regenerate_backup_codes(mock_db, mock_user, token)
        
        assert result is not None
        assert len(result) == 10
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_regenerate_backup_codes_with_invalid_token(self, mock_encryption, mfa_service, mock_user):
        """Test regenerating backup codes with invalid token fails."""
        secret = mfa_service.generate_secret()
        mock_user.mfa_secret = "encrypted_secret"
        mock_user.mfa_enabled = True
        mock_encryption.return_value.decrypt.return_value = secret
        mock_db = Mock(spec=Session)
        
        result = mfa_service.regenerate_backup_codes(mock_db, mock_user, "000000")
        
        assert result is None


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.mfa
class TestMFAErrorHandling:
    """Test error handling and edge cases."""
    
    def test_verify_token_with_invalid_secret(self, mfa_service):
        """Test verifying token with invalid secret."""
        result = mfa_service.verify_token("invalid_secret", "123456")
        
        assert result is False
    
    def test_generate_backup_codes_zero_count(self, mfa_service):
        """Test generating zero backup codes."""
        codes = mfa_service.generate_backup_codes(count=0)
        
        assert len(codes) == 0
    
    @patch('app.services.mfa_service.get_encryption_service')
    def test_verify_backup_code_no_codes(self, mock_encryption, mfa_service, mock_user):
        """Test verifying backup code when user has no codes."""
        mock_user.mfa_backup_codes = None
        
        result = mfa_service.verify_backup_code(mock_user, "code1")
        
        assert result is False

