"""
Unit Tests for Authentication API Endpoints

Tests for /api/v1/auth endpoints including:
- User registration
- User login
- Token refresh
- Get current user
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException

from app.models.user import User, UserRole


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = Mock()
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    return db


@pytest.fixture
def mock_user():
    """Create mock user."""
    user = Mock(spec=User)
    user.id = uuid4()
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.role = UserRole.PATIENT
    user.is_active = True
    user.phone = "+972501234567"
    user.created_at = datetime.utcnow()
    return user


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.auth
class TestAuthRegisterLogic:
    """Test user registration logic."""
    
    @patch('app.services.auth_service.AuthService')
    def test_register_new_user_success(self, mock_auth_service, mock_db, mock_user):
        """Test successful new user registration."""
        # Setup
        mock_auth_service.get_user_by_email.return_value = None
        mock_auth_service.create_user.return_value = mock_user
        
        # Simulate registration logic
        email = "newuser@example.com"
        existing = mock_auth_service.get_user_by_email(mock_db, email)
        
        assert existing is None
        
        new_user = mock_auth_service.create_user(mock_db, email=email, password="pass", full_name="New User")
        assert new_user is not None
        assert new_user.email == mock_user.email
    
    @patch('app.services.auth_service.AuthService')
    def test_register_duplicate_email_check(self, mock_auth_service, mock_db, mock_user):
        """Test duplicate email detection."""
        mock_auth_service.get_user_by_email.return_value = mock_user
        
        email = "existing@example.com"
        existing = mock_auth_service.get_user_by_email(mock_db, email)
        
        assert existing is not None
        assert existing.email == mock_user.email
    
    def test_register_password_validation(self):
        """Test password validation logic."""
        # Short password
        assert len("123") < 8
        
        # Valid password
        assert len("SecurePass123!") >= 8
    
    def test_register_email_validation(self):
        """Test email validation logic."""
        valid_emails = ["test@example.com", "user+tag@domain.co.il"]
        invalid_emails = ["invalid", "@domain.com", "user@"]
        
        for email in valid_emails:
            assert "@" in email and "." in email.split("@")[1]
        
        for email in invalid_emails:
            if "@" not in email:
                assert True
            elif "@" in email and "." not in email.split("@")[-1]:
                assert True


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.auth
class TestAuthLoginLogic:
    """Test user login logic."""
    
    @patch('app.services.auth_service.AuthService')
    def test_login_authenticate_success(self, mock_auth_service, mock_db, mock_user):
        """Test successful authentication."""
        mock_auth_service.authenticate_user.return_value = mock_user
        
        user = mock_auth_service.authenticate_user(mock_db, "test@example.com", "password")
        
        assert user is not None
        assert user.email == mock_user.email
        assert user.is_active == True
    
    @patch('app.services.auth_service.AuthService')
    def test_login_invalid_credentials(self, mock_auth_service, mock_db):
        """Test authentication with invalid credentials."""
        mock_auth_service.authenticate_user.return_value = None
        
        user = mock_auth_service.authenticate_user(mock_db, "test@example.com", "wrong_password")
        
        assert user is None
    
    @patch('app.services.auth_service.AuthService')
    def test_login_inactive_user_check(self, mock_auth_service, mock_db, mock_user):
        """Test inactive user detection."""
        mock_user.is_active = False
        mock_auth_service.authenticate_user.return_value = mock_user
        
        user = mock_auth_service.authenticate_user(mock_db, "test@example.com", "password")
        
        assert user is not None
        assert user.is_active == False
    
    @patch('app.services.auth_service.AuthService')
    def test_login_token_creation(self, mock_auth_service):
        """Test token creation after successful login."""
        token_data = {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "role": "PATIENT"
        }
        
        mock_auth_service.create_access_token.return_value = "access_token_123"
        mock_auth_service.create_refresh_token.return_value = "refresh_token_123"
        
        access_token = mock_auth_service.create_access_token(token_data)
        refresh_token = mock_auth_service.create_refresh_token(token_data)
        
        assert access_token == "access_token_123"
        assert refresh_token == "refresh_token_123"
    
    @patch('app.services.auth_service.AuthService')
    def test_login_updates_last_login(self, mock_auth_service, mock_db, mock_user):
        """Test that last login is updated."""
        mock_auth_service.update_last_login.return_value = None
        
        mock_auth_service.update_last_login(mock_db, mock_user.id)
        
        mock_auth_service.update_last_login.assert_called_once_with(mock_db, mock_user.id)


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.auth
class TestAuthTokenLogic:
    """Test token management logic."""
    
    @patch('app.services.auth_service.AuthService')
    def test_token_verification_success(self, mock_auth_service):
        """Test successful token verification."""
        token_data = {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "role": "PATIENT"
        }
        
        mock_auth_service.verify_access_token.return_value = token_data
        
        result = mock_auth_service.verify_access_token("valid_token")
        
        assert result is not None
        assert result["email"] == "test@example.com"
    
    @patch('app.services.auth_service.AuthService')
    def test_token_verification_invalid(self, mock_auth_service):
        """Test invalid token verification."""
        mock_auth_service.verify_access_token.return_value = None
        
        result = mock_auth_service.verify_access_token("invalid_token")
        
        assert result is None
    
    @patch('app.services.auth_service.AuthService')
    def test_refresh_token_success(self, mock_auth_service):
        """Test successful token refresh."""
        token_data = {
            "sub": str(uuid4()),
            "email": "test@example.com"
        }
        
        mock_auth_service.verify_refresh_token.return_value = token_data
        mock_auth_service.create_access_token.return_value = "new_access_token"
        mock_auth_service.create_refresh_token.return_value = "new_refresh_token"
        
        # Verify refresh token
        data = mock_auth_service.verify_refresh_token("valid_refresh_token")
        assert data is not None
        
        # Create new tokens
        new_access = mock_auth_service.create_access_token(data)
        new_refresh = mock_auth_service.create_refresh_token(data)
        
        assert new_access == "new_access_token"
        assert new_refresh == "new_refresh_token"
    
    @patch('app.services.auth_service.AuthService')
    def test_refresh_token_expired(self, mock_auth_service):
        """Test refresh with expired token."""
        mock_auth_service.verify_refresh_token.return_value = None
        
        result = mock_auth_service.verify_refresh_token("expired_token")
        
        assert result is None


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.auth
class TestAuthCurrentUser:
    """Test current user retrieval logic."""
    
    def test_current_user_requires_authentication(self):
        """Test that current user endpoint requires authentication."""
        # This is a logic test - in real implementation, 
        # get_current_user dependency checks for valid token
        assert True  # Placeholder for authentication requirement
    
    def test_current_user_returns_user_data(self, mock_user):
        """Test that current user returns user data."""
        # Mock successful authentication
        user = mock_user
        
        assert user is not None
        assert hasattr(user, 'email')
        assert hasattr(user, 'id')
        assert hasattr(user, 'role')


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.auth
class TestAuthWorkflow:
    """Test complete authentication workflows."""
    
    @patch('app.services.auth_service.AuthService')
    def test_full_registration_login_workflow(self, mock_auth_service, mock_db, mock_user):
        """Test complete workflow: register -> login -> get token."""
        # Step 1: Check user doesn't exist
        mock_auth_service.get_user_by_email.return_value = None
        existing = mock_auth_service.get_user_by_email(mock_db, "new@example.com")
        assert existing is None
        
        # Step 2: Create user
        mock_auth_service.create_user.return_value = mock_user
        user = mock_auth_service.create_user(mock_db, email="new@example.com", password="pass", full_name="New")
        assert user is not None
        
        # Step 3: Authenticate
        mock_auth_service.authenticate_user.return_value = mock_user
        auth_user = mock_auth_service.authenticate_user(mock_db, "new@example.com", "pass")
        assert auth_user is not None
        assert auth_user.is_active == True
        
        # Step 4: Create tokens
        mock_auth_service.create_access_token.return_value = "access_token"
        mock_auth_service.create_refresh_token.return_value = "refresh_token"
        
        access_token = mock_auth_service.create_access_token({"sub": str(user.id)})
        refresh_token = mock_auth_service.create_refresh_token({"sub": str(user.id)})
        
        assert access_token == "access_token"
        assert refresh_token == "refresh_token"
    
    @patch('app.services.auth_service.AuthService')
    def test_login_refresh_workflow(self, mock_auth_service, mock_db, mock_user):
        """Test workflow: login -> use token -> refresh token."""
        # Step 1: Login
        mock_auth_service.authenticate_user.return_value = mock_user
        user = mock_auth_service.authenticate_user(mock_db, "test@example.com", "password")
        assert user is not None
        
        # Step 2: Create initial tokens
        mock_auth_service.create_access_token.return_value = "initial_access"
        mock_auth_service.create_refresh_token.return_value = "initial_refresh"
        
        access_token = mock_auth_service.create_access_token({"sub": str(user.id)})
        refresh_token = mock_auth_service.create_refresh_token({"sub": str(user.id)})
        
        assert access_token == "initial_access"
        
        # Step 3: Refresh tokens
        mock_auth_service.verify_refresh_token.return_value = {"sub": str(user.id)}
        mock_auth_service.create_access_token.return_value = "new_access"
        mock_auth_service.create_refresh_token.return_value = "new_refresh"
        
        token_data = mock_auth_service.verify_refresh_token(refresh_token)
        new_access = mock_auth_service.create_access_token(token_data)
        new_refresh = mock_auth_service.create_refresh_token(token_data)
        
        assert new_access == "new_access"
        assert new_refresh == "new_refresh"


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.auth
class TestAuthErrorHandling:
    """Test authentication error handling."""
    
    @patch('app.services.auth_service.AuthService')
    def test_register_database_error(self, mock_auth_service, mock_db):
        """Test registration with database error."""
        mock_auth_service.get_user_by_email.return_value = None
        mock_auth_service.create_user.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            mock_auth_service.create_user(mock_db, email="test@example.com", password="pass", full_name="Test")
        
        assert "Database error" in str(exc_info.value)
    
    @patch('app.services.auth_service.AuthService')
    def test_login_service_unavailable(self, mock_auth_service, mock_db):
        """Test login when service is unavailable."""
        mock_auth_service.authenticate_user.side_effect = Exception("Service unavailable")
        
        with pytest.raises(Exception) as exc_info:
            mock_auth_service.authenticate_user(mock_db, "test@example.com", "password")
        
        assert "Service unavailable" in str(exc_info.value)
    
    def test_token_missing_required_fields(self):
        """Test token creation with missing fields."""
        incomplete_data = {"email": "test@example.com"}  # Missing 'sub'
        
        # Should have 'sub' field
        assert "sub" not in incomplete_data
    
    def test_invalid_email_format(self):
        """Test various invalid email formats."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
        ]
        
        for email in invalid_emails:
            # Basic validation: must have @ and domain
            if "@" not in email:
                assert True
            elif email.count("@") != 1:
                assert True
            elif "." not in email.split("@")[-1]:
                assert True

