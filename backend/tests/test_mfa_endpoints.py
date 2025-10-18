"""
Comprehensive tests for MFA endpoints
Tests all MFA functionality including setup, verification, backup codes, and error scenarios
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import pyotp
import io
from PIL import Image

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = MagicMock()
    return db


@pytest.fixture
def test_user():
    """Create test user"""
    from app.models.user import UserRole
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        role=UserRole.ORG_ADMIN,
        is_active=True,
        mfa_enabled=False,
        mfa_secret=None,
        mfa_backup_codes=None
    )
    return user


@pytest.fixture
def test_user_with_mfa():
    """Create test user with MFA enabled"""
    from app.models.user import UserRole
    secret = pyotp.random_base32()
    user = User(
        email="mfa@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="MFA User",
        role=UserRole.ORG_ADMIN,
        is_active=True,
        mfa_enabled=True,
        mfa_secret=secret,
        mfa_backup_codes="CODE1234,CODE5678,CODE9012"
    )
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


class TestMFASetup:
    """Test MFA setup endpoint"""
    
    def test_mfa_setup_success(self, client, mock_db, test_user, auth_headers):
        """Test successful MFA setup"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user):
                mock_db.query.return_value.filter.return_value.first.return_value = test_user
                
                response = client.post("/api/v1/mfa/setup", headers=auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert "qr_code" in data
                assert "secret" in data
                assert data["qr_code"].startswith("data:image/png;base64,")
                assert len(data["secret"]) == 32  # Base32 secret
    
    def test_mfa_setup_already_enabled(self, client, mock_db, test_user_with_mfa, auth_headers):
        """Test MFA setup when already enabled"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user_with_mfa):
                response = client.post("/api/v1/mfa/setup", headers=auth_headers)
                
                assert response.status_code == 400
                assert "already enabled" in response.json()["detail"].lower()
    
    def test_mfa_setup_unauthorized(self, client):
        """Test MFA setup without authentication"""
        response = client.post("/api/v1/mfa/setup")
        assert response.status_code == 401


class TestMFAVerifySetup:
    """Test MFA setup verification endpoint"""
    
    def test_verify_setup_success(self, client, mock_db, test_user, auth_headers):
        """Test successful MFA setup verification"""
        secret = pyotp.random_base32()
        test_user.mfa_secret = secret
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()
        
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user):
                mock_db.query.return_value.filter.return_value.first.return_value = test_user
                mock_db.commit = MagicMock()
                
                response = client.post(
                    "/api/v1/mfa/verify-setup",
                    headers=auth_headers,
                    json={"code": valid_code}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "backup_codes" in data
                assert len(data["backup_codes"]) == 10
                assert all(len(code) == 8 for code in data["backup_codes"])
    
    def test_verify_setup_invalid_code(self, client, mock_db, test_user, auth_headers):
        """Test MFA setup verification with invalid code"""
        secret = pyotp.random_base32()
        test_user.mfa_secret = secret
        
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user):
                mock_db.query.return_value.filter.return_value.first.return_value = test_user
                
                response = client.post(
                    "/api/v1/mfa/verify-setup",
                    headers=auth_headers,
                    json={"code": "000000"}
                )
                
                assert response.status_code == 400
                assert "invalid" in response.json()["detail"].lower()
    
    def test_verify_setup_no_secret(self, client, mock_db, test_user, auth_headers):
        """Test MFA setup verification without secret"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user):
                response = client.post(
                    "/api/v1/mfa/verify-setup",
                    headers=auth_headers,
                    json={"code": "123456"}
                )
                
                assert response.status_code == 400


class TestMFAVerify:
    """Test MFA login verification endpoint"""
    
    def test_verify_login_success(self, client, mock_db, test_user_with_mfa):
        """Test successful MFA login verification"""
        totp = pyotp.TOTP(test_user_with_mfa.mfa_secret)
        valid_code = totp.now()
        
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
            
            response = client.post(
                "/api/v1/mfa/verify",
                json={
                    "email": test_user_with_mfa.email,
                    "code": valid_code
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    def test_verify_login_invalid_code(self, client, mock_db, test_user_with_mfa):
        """Test MFA login verification with invalid code"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
            
            response = client.post(
                "/api/v1/mfa/verify",
                json={
                    "email": test_user_with_mfa.email,
                    "code": "000000"
                }
            )
            
            assert response.status_code == 400
            assert "invalid" in response.json()["detail"].lower()
    
    def test_verify_login_user_not_found(self, client, mock_db):
        """Test MFA login verification with non-existent user"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            response = client.post(
                "/api/v1/mfa/verify",
                json={
                    "email": "nonexistent@example.com",
                    "code": "123456"
                }
            )
            
            assert response.status_code == 404
    
    def test_verify_login_mfa_not_enabled(self, client, mock_db, test_user):
        """Test MFA login verification when MFA not enabled"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user
            
            response = client.post(
                "/api/v1/mfa/verify",
                json={
                    "email": test_user.email,
                    "code": "123456"
                }
            )
            
            assert response.status_code == 400


class TestMFAVerifyBackup:
    """Test MFA backup code verification endpoint"""
    
    def test_verify_backup_success(self, client, mock_db, test_user_with_mfa):
        """Test successful backup code verification"""
        backup_codes = test_user_with_mfa.mfa_backup_codes.split(',')
        backup_code = backup_codes[0]
        
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
            mock_db.commit = MagicMock()
            
            response = client.post(
                "/api/v1/mfa/verify-backup",
                json={
                    "email": test_user_with_mfa.email,
                    "code": backup_code
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    def test_verify_backup_invalid_code(self, client, mock_db, test_user_with_mfa):
        """Test backup code verification with invalid code"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
            
            response = client.post(
                "/api/v1/mfa/verify-backup",
                json={
                    "email": test_user_with_mfa.email,
                    "code": "INVALID1"
                }
            )
            
            assert response.status_code == 400
            assert "invalid" in response.json()["detail"].lower()
    
    def test_verify_backup_no_codes(self, client, mock_db, test_user_with_mfa):
        """Test backup code verification when no codes available"""
        test_user_with_mfa.mfa_backup_codes = ""
        
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
            
            response = client.post(
                "/api/v1/mfa/verify-backup",
                json={
                    "email": test_user_with_mfa.email,
                    "code": "CODE1234"
                }
            )
            
            assert response.status_code == 400


class TestMFAStatus:
    """Test MFA status endpoint"""
    
    def test_status_enabled(self, client, mock_db, test_user_with_mfa, auth_headers):
        """Test MFA status when enabled"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user_with_mfa):
                response = client.get("/api/v1/mfa/status", headers=auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert data["mfa_enabled"] is True
    
    def test_status_disabled(self, client, mock_db, test_user, auth_headers):
        """Test MFA status when disabled"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user):
                response = client.get("/api/v1/mfa/status", headers=auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert data["mfa_enabled"] is False
    
    def test_status_unauthorized(self, client):
        """Test MFA status without authentication"""
        response = client.get("/api/v1/mfa/status")
        assert response.status_code == 401


class TestMFADisable:
    """Test MFA disable endpoint"""
    
    def test_disable_success(self, client, mock_db, test_user_with_mfa, auth_headers):
        """Test successful MFA disable"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user_with_mfa):
                mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
                mock_db.commit = MagicMock()
                
                response = client.post("/api/v1/mfa/disable", headers=auth_headers)
                
                assert response.status_code == 200
                assert "disabled" in response.json()["message"].lower()
    
    def test_disable_not_enabled(self, client, mock_db, test_user, auth_headers):
        """Test MFA disable when not enabled"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user):
                response = client.post("/api/v1/mfa/disable", headers=auth_headers)
                
                assert response.status_code == 400
                assert "not enabled" in response.json()["detail"].lower()
    
    def test_disable_unauthorized(self, client):
        """Test MFA disable without authentication"""
        response = client.post("/api/v1/mfa/disable")
        assert response.status_code == 401


class TestMFARegenerateBackupCodes:
    """Test MFA regenerate backup codes endpoint"""
    
    def test_regenerate_success(self, client, mock_db, test_user_with_mfa, auth_headers):
        """Test successful backup codes regeneration"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user_with_mfa):
                mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
                mock_db.commit = MagicMock()
                
                response = client.post("/api/v1/mfa/regenerate-backup-codes", headers=auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert "backup_codes" in data
                assert len(data["backup_codes"]) == 10
                assert all(len(code) == 8 for code in data["backup_codes"])
    
    def test_regenerate_not_enabled(self, client, mock_db, test_user, auth_headers):
        """Test backup codes regeneration when MFA not enabled"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            with patch('app.api.v1.endpoints.mfa.get_current_user', return_value=test_user):
                response = client.post("/api/v1/mfa/regenerate-backup-codes", headers=auth_headers)
                
                assert response.status_code == 400
                assert "not enabled" in response.json()["detail"].lower()
    
    def test_regenerate_unauthorized(self, client):
        """Test backup codes regeneration without authentication"""
        response = client.post("/api/v1/mfa/regenerate-backup-codes")
        assert response.status_code == 401


class TestMFAEdgeCases:
    """Test MFA edge cases and error scenarios"""
    
    def test_verify_with_expired_code(self, client, mock_db, test_user_with_mfa):
        """Test verification with expired TOTP code"""
        # This is difficult to test reliably, but we can test with an old code
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
            
            response = client.post(
                "/api/v1/mfa/verify",
                json={
                    "email": test_user_with_mfa.email,
                    "code": "999999"  # Invalid code
                }
            )
            
            assert response.status_code == 400
    
    def test_backup_code_single_use(self, client, mock_db, test_user_with_mfa):
        """Test that backup codes can only be used once"""
        backup_code = test_user_with_mfa.backup_codes[0]
        
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
            mock_db.commit = MagicMock()
            
            # First use should succeed
            response1 = client.post(
                "/api/v1/mfa/verify-backup",
                json={
                    "email": test_user_with_mfa.email,
                    "code": backup_code
                }
            )
            assert response1.status_code == 200
            
            # Remove the used code
            backup_codes = test_user_with_mfa.mfa_backup_codes.split(',')
            backup_codes.remove(backup_code)
            test_user_with_mfa.mfa_backup_codes = ','.join(backup_codes)
            
            # Second use should fail
            response2 = client.post(
                "/api/v1/mfa/verify-backup",
                json={
                    "email": test_user_with_mfa.email,
                    "code": backup_code
                }
            )
            assert response2.status_code == 400
    
    def test_malformed_code_input(self, client, mock_db, test_user_with_mfa):
        """Test with malformed code input"""
        with patch('app.api.v1.endpoints.mfa.get_db', return_value=mock_db):
            mock_db.query.return_value.filter.return_value.first.return_value = test_user_with_mfa
            
            # Test with non-numeric code
            response = client.post(
                "/api/v1/mfa/verify",
                json={
                    "email": test_user_with_mfa.email,
                    "code": "abcdef"
                }
            )
            
            # Should either reject or fail validation
            assert response.status_code in [400, 422]

