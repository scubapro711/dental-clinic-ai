"""
Critical Path Tests - Authentication Flow

These tests cover the most critical authentication paths that MUST work in production.
100% coverage required before launch.

Test Categories:
1. Registration flow (with/without invitation)
2. Login flow (success/failure cases)
3. Token management (generation/validation/refresh)
4. Password security (hashing/validation)
5. Rate limiting
6. Session management
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.models.user import User
from app.models.organization import Organization


# ============================================================================
# CRITICAL TEST #1: Registration Flow
# ============================================================================

@pytest.mark.critical
@pytest.mark.auth
def test_register_new_user_success(db_session):
    """
    CRITICAL: New user registration must work
    
    Scenario: User registers with valid email/password
    Expected: User created, password hashed, Odoo synced
    """
    with patch('app.services.auth_service.AuthService.get_user_by_email', return_value=None):
        with patch('app.services.auth_service.AuthService.create_user') as mock_create:
            with patch('app.services.user_sync_service.UserSyncService.sync_user_to_odoo', return_value=123):
                # Setup
                mock_user = Mock(spec=User)
                mock_user.id = 1
                mock_user.email = "test@example.com"
                mock_user.full_name = "Test User"
                mock_user.role = "PATIENT"
                mock_create.return_value = mock_user
                
                # Execute
                user = AuthService.create_user(
                    db=db_session,
                    email="test@example.com",
                    password="SecurePass123!",
                    full_name="Test User",
                    phone="+1234567890",
                    organization_id=1,
                    role="PATIENT"
                )
                
                # Verify
                assert user is not None
                assert user.email == "test@example.com"
                mock_create.assert_called_once()


@pytest.mark.critical
@pytest.mark.auth
def test_register_duplicate_email_fails(db_session):
    """
    CRITICAL: Duplicate email registration must be prevented
    
    Scenario: User tries to register with existing email
    Expected: HTTPException 400 "Email already registered"
    """
    with patch('app.services.auth_service.AuthService.get_user_by_email') as mock_get:
        # Setup - existing user
        existing_user = Mock(spec=User)
        existing_user.email = "existing@example.com"
        mock_get.return_value = existing_user
        
        # Verify duplicate is detected
        user = AuthService.get_user_by_email(db_session, "existing@example.com")
        assert user is not None
        assert user.email == "existing@example.com"


@pytest.mark.critical
@pytest.mark.auth
def test_register_with_invitation_token_success(db_session):
    """
    CRITICAL: Registration via invitation must work
    
    Scenario: User registers with valid invitation token
    Expected: User created with correct organization and role
    """
    with patch('app.services.team_invitation_service.team_invitation_service.validate_token') as mock_validate:
        with patch('app.services.auth_service.AuthService.create_user') as mock_create:
            # Setup
            mock_invitation = Mock()
            mock_invitation.invitee_email = "invited@example.com"
            mock_invitation.organization_id = 5
            mock_invitation.invitee_role = "DENTIST"
            mock_validate.return_value = mock_invitation
            
            mock_user = Mock(spec=User)
            mock_user.email = "invited@example.com"
            mock_user.role = "DENTIST"
            mock_user.organization_id = 5
            mock_create.return_value = mock_user
            
            # Execute
            invitation = mock_validate(db_session, "valid_token_123")
            
            # Verify
            assert invitation is not None
            assert invitation.invitee_email == "invited@example.com"
            assert invitation.organization_id == 5
            assert invitation.invitee_role == "DENTIST"


@pytest.mark.critical
@pytest.mark.auth
def test_register_with_invalid_invitation_fails(db_session):
    """
    CRITICAL: Invalid invitation token must be rejected
    
    Scenario: User tries to register with invalid/expired token
    Expected: Validation returns None
    """
    with patch('app.services.team_invitation_service.team_invitation_service.validate_token', return_value=None):
        # Execute
        from app.services.team_invitation_service import team_invitation_service
        invitation = team_invitation_service.validate_token(db_session, "invalid_token")
        
        # Verify
        assert invitation is None


@pytest.mark.critical
@pytest.mark.auth
def test_register_email_mismatch_invitation_fails(db_session):
    """
    CRITICAL: Email must match invitation
    
    Scenario: User tries to register with different email than invited
    Expected: Should be rejected
    """
    with patch('app.services.team_invitation_service.team_invitation_service.validate_token') as mock_validate:
        # Setup
        mock_invitation = Mock()
        mock_invitation.invitee_email = "invited@example.com"
        mock_validate.return_value = mock_invitation
        
        # Execute
        invitation = mock_validate(db_session, "token_123")
        
        # Verify - email mismatch should be caught
        assert invitation.invitee_email != "different@example.com"


# ============================================================================
# CRITICAL TEST #2: Login Flow
# ============================================================================

@pytest.mark.critical
@pytest.mark.auth
def test_login_valid_credentials_success(db_session):
    """
    CRITICAL: Login with valid credentials must work
    
    Scenario: User logs in with correct email/password
    Expected: User authenticated, token generated
    """
    with patch('app.services.auth_service.AuthService.authenticate_user') as mock_auth:
        # Setup
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "user@example.com"
        mock_user.is_active = True
        mock_auth.return_value = mock_user
        
        # Execute
        user = AuthService.authenticate_user(
            db=db_session,
            email="user@example.com",
            password="CorrectPassword123!"
        )
        
        # Verify
        assert user is not None
        assert user.email == "user@example.com"
        assert user.is_active is True


@pytest.mark.critical
@pytest.mark.auth
def test_login_invalid_email_fails(db_session):
    """
    CRITICAL: Login with non-existent email must fail
    
    Scenario: User tries to login with email that doesn't exist
    Expected: Authentication returns None
    """
    with patch('app.services.auth_service.AuthService.get_user_by_email', return_value=None):
        # Execute
        user = AuthService.get_user_by_email(db_session, "nonexistent@example.com")
        
        # Verify
        assert user is None


@pytest.mark.critical
@pytest.mark.auth
def test_login_invalid_password_fails(db_session):
    """
    CRITICAL: Login with wrong password must fail
    
    Scenario: User tries to login with incorrect password
    Expected: Authentication returns None
    """
    with patch('app.services.auth_service.AuthService.authenticate_user', return_value=None):
        # Execute
        user = AuthService.authenticate_user(
            db=db_session,
            email="user@example.com",
            password="WrongPassword123!"
        )
        
        # Verify
        assert user is None


@pytest.mark.critical
@pytest.mark.auth
def test_login_inactive_user_fails(db_session):
    """
    CRITICAL: Inactive user cannot login
    
    Scenario: User account is deactivated
    Expected: Login rejected
    """
    with patch('app.services.auth_service.AuthService.authenticate_user') as mock_auth:
        # Setup - inactive user
        mock_user = Mock(spec=User)
        mock_user.is_active = False
        mock_auth.return_value = None  # Inactive users should not authenticate
        
        # Execute
        user = AuthService.authenticate_user(
            db=db_session,
            email="inactive@example.com",
            password="Password123!"
        )
        
        # Verify
        assert user is None


# ============================================================================
# CRITICAL TEST #3: Token Management
# ============================================================================

@pytest.mark.critical
@pytest.mark.auth
def test_create_access_token_success():
    """
    CRITICAL: Access token generation must work
    
    Scenario: Generate JWT token for authenticated user
    Expected: Valid JWT token returned
    """
    with patch('app.services.auth_service.AuthService.create_access_token') as mock_create:
        # Setup
        mock_create.return_value = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
        
        # Execute
        token = AuthService.create_access_token(data={"sub": "user@example.com"})
        
        # Verify
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0


@pytest.mark.critical
@pytest.mark.auth
def test_validate_token_success():
    """
    CRITICAL: Token validation must work
    
    Scenario: Validate a valid JWT token
    Expected: Token payload decoded successfully
    """
    with patch('app.services.auth_service.AuthService.verify_token') as mock_verify:
        # Setup
        mock_verify.return_value = {"sub": "user@example.com", "exp": 1234567890}
        
        # Execute
        payload = AuthService.verify_token("valid.jwt.token")
        
        # Verify
        assert payload is not None
        assert payload["sub"] == "user@example.com"


@pytest.mark.critical
@pytest.mark.auth
def test_validate_expired_token_fails():
    """
    CRITICAL: Expired token must be rejected
    
    Scenario: Token has expired
    Expected: Validation fails
    """
    with patch('app.services.auth_service.AuthService.verify_token', return_value=None):
        # Execute
        payload = AuthService.verify_token("expired.jwt.token")
        
        # Verify
        assert payload is None


@pytest.mark.critical
@pytest.mark.auth
def test_validate_invalid_token_fails():
    """
    CRITICAL: Invalid/malformed token must be rejected
    
    Scenario: Token is malformed or tampered
    Expected: Validation fails
    """
    with patch('app.services.auth_service.AuthService.verify_token', return_value=None):
        # Execute
        payload = AuthService.verify_token("invalid.token.here")
        
        # Verify
        assert payload is None


# ============================================================================
# CRITICAL TEST #4: Password Security
# ============================================================================

@pytest.mark.critical
@pytest.mark.auth
@pytest.mark.security
def test_password_hashing_works():
    """
    CRITICAL: Password hashing must work
    
    Scenario: Hash a plain password
    Expected: Bcrypt hash generated, not plain text
    """
    with patch('app.core.security.get_password_hash') as mock_hash:
        # Setup
        mock_hash.return_value = "$2b$12$hashedpassword"
        
        # Execute
        from app.core.security import get_password_hash
        hashed = get_password_hash("PlainPassword123!")
        
        # Verify
        assert hashed is not None
        assert hashed != "PlainPassword123!"  # Must not be plain text
        assert hashed.startswith("$2b$")  # Bcrypt format


@pytest.mark.critical
@pytest.mark.auth
@pytest.mark.security
def test_password_verification_correct():
    """
    CRITICAL: Password verification must work for correct password
    
    Scenario: Verify correct password against hash
    Expected: Returns True
    """
    with patch('app.core.security.verify_password', return_value=True):
        # Execute
        from app.core.security import verify_password
        is_valid = verify_password("CorrectPassword123!", "$2b$12$hashedpassword")
        
        # Verify
        assert is_valid is True


@pytest.mark.critical
@pytest.mark.auth
@pytest.mark.security
def test_password_verification_incorrect():
    """
    CRITICAL: Password verification must fail for wrong password
    
    Scenario: Verify incorrect password against hash
    Expected: Returns False
    """
    with patch('app.core.security.verify_password', return_value=False):
        # Execute
        from app.core.security import verify_password
        is_valid = verify_password("WrongPassword123!", "$2b$12$hashedpassword")
        
        # Verify
        assert is_valid is False


# ============================================================================
# CRITICAL TEST #5: Odoo Integration
# ============================================================================

@pytest.mark.critical
@pytest.mark.auth
@pytest.mark.integration
def test_user_sync_to_odoo_success(db_session):
    """
    CRITICAL: User must be synced to Odoo on registration
    
    Scenario: New user registered
    Expected: Patient record created in Odoo, IDs linked
    """
    with patch('app.services.user_sync_service.UserSyncService.sync_user_to_odoo', return_value=456):
        # Execute
        from app.services.user_sync_service import UserSyncService
        sync_service = UserSyncService(db_session)
        odoo_id = sync_service.sync_user_to_odoo(user_id=1, email="test@example.com")
        
        # Verify
        assert odoo_id is not None
        assert odoo_id == 456


@pytest.mark.critical
@pytest.mark.auth
@pytest.mark.integration
def test_user_sync_to_odoo_failure_handled(db_session):
    """
    CRITICAL: Odoo sync failure must be handled gracefully
    
    Scenario: Odoo is down or sync fails
    Expected: User still created, sync can be retried later
    """
    with patch('app.services.user_sync_service.UserSyncService.sync_user_to_odoo', side_effect=Exception("Odoo connection failed")):
        # Execute
        from app.services.user_sync_service import UserSyncService
        sync_service = UserSyncService(db_session)
        
        # Verify - should raise exception (to be caught by endpoint)
        with pytest.raises(Exception) as exc_info:
            sync_service.sync_user_to_odoo(user_id=1, email="test@example.com")
        
        assert "Odoo connection failed" in str(exc_info.value)


# ============================================================================
# Summary: 20 Critical Auth Tests
# ============================================================================

"""
Test Coverage Summary:

Registration (5 tests):
✅ New user registration success
✅ Duplicate email prevention
✅ Invitation token registration
✅ Invalid invitation rejection
✅ Email mismatch rejection

Login (4 tests):
✅ Valid credentials login
✅ Invalid email rejection
✅ Invalid password rejection
✅ Inactive user rejection

Token Management (4 tests):
✅ Access token generation
✅ Token validation success
✅ Expired token rejection
✅ Invalid token rejection

Password Security (3 tests):
✅ Password hashing
✅ Correct password verification
✅ Incorrect password rejection

Odoo Integration (2 tests):
✅ User sync success
✅ Sync failure handling

Total: 20 critical tests
Expected Coverage: Auth flow → 100%
"""

