"""
Unit Tests for AWS Cognito Authentication API

Tests for auth_cognito endpoints including:
- Sign up
- Confirm sign up
- Sign in
- Token refresh
- Password reset
- User info
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

from app.main import app
from app.core.cognito import CognitoUser


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.mark.unit
@pytest.mark.api
class TestCognitoSignUp:
    """Test Cognito sign up endpoint."""
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_signup_success(self, mock_get_cognito, client):
        """Test successful user sign up."""
        # Mock Cognito client
        mock_cognito = Mock()
        mock_cognito.sign_up.return_value = {
            'user_sub': 'test-sub-123',
            'user_confirmed': False,
            'code_delivery_details': {
                'Destination': 't***@example.com',
                'DeliveryMedium': 'EMAIL'
            }
        }
        mock_get_cognito.return_value = mock_cognito
        
        # Test request
        response = client.post("/api/v1/cognito/signup", json={
            "email": "test@example.com",
            "password": "Test123!@#",
            "given_name": "Test",
            "family_name": "User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data['user_sub'] == 'test-sub-123'
        assert data['user_confirmed'] is False
        assert 'confirmation code' in data['message'].lower()
        
        # Verify Cognito was called correctly
        mock_cognito.sign_up.assert_called_once()
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_signup_auto_confirmed(self, mock_get_cognito):
        """Test sign up with auto-confirmation."""
        mock_cognito = Mock()
        mock_cognito.sign_up.return_value = {
            'user_sub': 'test-sub-456',
            'user_confirmed': True
        }
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/signup", json={
            "email": "test2@example.com",
            "password": "Test456!@#"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data['user_confirmed'] is True
        assert 'confirmation code' not in data['message'].lower()
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_signup_duplicate_email(self, mock_get_cognito):
        """Test sign up with existing email."""
        mock_cognito = Mock()
        mock_cognito.sign_up.side_effect = ClientError(
            {'Error': {'Code': 'UsernameExistsException', 'Message': 'User exists'}},
            'SignUp'
        )
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/signup", json={
            "email": "existing@example.com",
            "password": "Test789!@#"
        })
        
        assert response.status_code == 409
        assert 'already exists' in response.json()['detail'].lower()
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_signup_invalid_password(self, mock_get_cognito):
        """Test sign up with invalid password."""
        mock_cognito = Mock()
        mock_cognito.sign_up.side_effect = ClientError(
            {'Error': {'Code': 'InvalidPasswordException', 'Message': 'Password too weak'}},
            'SignUp'
        )
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/signup", json={
            "email": "test@example.com",
            "password": "weak"
        })
        
        assert response.status_code == 400
        assert 'password' in response.json()['detail'].lower()
    
    def test_signup_invalid_email(self):
        """Test sign up with invalid email format."""
        response = client.post("/api/v1/cognito/signup", json={
            "email": "not-an-email",
            "password": "Test123!@#"
        })
        
        assert response.status_code == 422  # Validation error


@pytest.mark.unit
@pytest.mark.api
class TestCognitoConfirmSignUp:
    """Test Cognito confirm sign up endpoint."""
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_confirm_signup_success(self, mock_get_cognito):
        """Test successful sign up confirmation."""
        mock_cognito = Mock()
        mock_cognito.confirm_sign_up.return_value = {}
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/confirm-signup", json={
            "email": "test@example.com",
            "confirmation_code": "123456"
        })
        
        assert response.status_code == 200
        assert 'confirmed successfully' in response.json()['message'].lower()
        mock_cognito.confirm_sign_up.assert_called_once()
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_confirm_signup_invalid_code(self, mock_get_cognito):
        """Test confirmation with invalid code."""
        mock_cognito = Mock()
        mock_cognito.confirm_sign_up.side_effect = ClientError(
            {'Error': {'Code': 'CodeMismatchException', 'Message': 'Invalid code'}},
            'ConfirmSignUp'
        )
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/confirm-signup", json={
            "email": "test@example.com",
            "confirmation_code": "wrong"
        })
        
        assert response.status_code == 400
    
    def test_confirm_signup_invalid_code_format(self):
        """Test confirmation with wrong code format."""
        response = client.post("/api/v1/cognito/confirm-signup", json={
            "email": "test@example.com",
            "confirmation_code": "12345"  # Too short
        })
        
        assert response.status_code == 422


@pytest.mark.unit
@pytest.mark.api
class TestCognitoSignIn:
    """Test Cognito sign in endpoint."""
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_signin_success(self, mock_get_cognito):
        """Test successful sign in."""
        mock_cognito = Mock()
        mock_cognito.sign_in.return_value = {
            'access_token': 'access-token-123',
            'id_token': 'id-token-123',
            'refresh_token': 'refresh-token-123',
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/signin", json={
            "email": "test@example.com",
            "password": "Test123!@#"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'id_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'Bearer'
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_signin_wrong_password(self, mock_get_cognito):
        """Test sign in with wrong password."""
        mock_cognito = Mock()
        mock_cognito.sign_in.side_effect = ClientError(
            {'Error': {'Code': 'NotAuthorizedException', 'Message': 'Incorrect password'}},
            'InitiateAuth'
        )
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/signin", json={
            "email": "test@example.com",
            "password": "WrongPassword"
        })
        
        assert response.status_code == 401
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_signin_user_not_found(self, mock_get_cognito):
        """Test sign in with non-existent user."""
        mock_cognito = Mock()
        mock_cognito.sign_in.side_effect = ClientError(
            {'Error': {'Code': 'UserNotFoundException', 'Message': 'User not found'}},
            'InitiateAuth'
        )
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/signin", json={
            "email": "nonexistent@example.com",
            "password": "Test123!@#"
        })
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.api
class TestCognitoTokenRefresh:
    """Test Cognito token refresh endpoint."""
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_refresh_token_success(self, mock_get_cognito):
        """Test successful token refresh."""
        mock_cognito = Mock()
        mock_cognito.refresh_token.return_value = {
            'access_token': 'new-access-token',
            'id_token': 'new-id-token',
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/refresh", json={
            "refresh_token": "valid-refresh-token"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'id_token' in data
        assert 'refresh_token' not in data  # Refresh token not returned
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_refresh_token_invalid(self, mock_get_cognito):
        """Test refresh with invalid token."""
        mock_cognito = Mock()
        mock_cognito.refresh_token.side_effect = ClientError(
            {'Error': {'Code': 'NotAuthorizedException', 'Message': 'Invalid refresh token'}},
            'InitiateAuth'
        )
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/refresh", json={
            "refresh_token": "invalid-token"
        })
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.api
class TestCognitoPasswordReset:
    """Test Cognito password reset endpoints."""
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_forgot_password_success(self, mock_get_cognito):
        """Test forgot password request."""
        mock_cognito = Mock()
        mock_cognito.forgot_password.return_value = {
            'code_delivery_details': {
                'Destination': 't***@example.com',
                'DeliveryMedium': 'EMAIL'
            }
        }
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/forgot-password", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 200
        assert 'code' in response.json()['message'].lower()
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_confirm_forgot_password_success(self, mock_get_cognito):
        """Test password reset confirmation."""
        mock_cognito = Mock()
        mock_cognito.confirm_forgot_password.return_value = {}
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/confirm-forgot-password", json={
            "email": "test@example.com",
            "confirmation_code": "123456",
            "new_password": "NewPassword123!@#"
        })
        
        assert response.status_code == 200
        assert 'reset successfully' in response.json()['message'].lower()
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_confirm_forgot_password_invalid_code(self, mock_get_cognito):
        """Test password reset with invalid code."""
        mock_cognito = Mock()
        mock_cognito.confirm_forgot_password.side_effect = ClientError(
            {'Error': {'Code': 'CodeMismatchException', 'Message': 'Invalid code'}},
            'ConfirmForgotPassword'
        )
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/confirm-forgot-password", json={
            "email": "test@example.com",
            "confirmation_code": "wrong",
            "new_password": "NewPassword123!@#"
        })
        
        assert response.status_code == 400


@pytest.mark.unit
@pytest.mark.api
class TestCognitoUserInfo:
    """Test Cognito user info endpoint."""
    
    @patch('app.api.v1.endpoints.auth_cognito.get_current_cognito_user')
    def test_get_user_info_success(self, mock_get_user):
        """Test getting user info."""
        mock_user = CognitoUser(
            username='test@example.com',
            email='test@example.com',
            email_verified=True,
            sub='test-sub-123',
            given_name='Test',
            family_name='User',
            phone_number='+972501234567',
            phone_number_verified=True
        )
        mock_get_user.return_value = mock_user
        
        response = client.get(
            "/api/v1/cognito/user-info",
            headers={"Authorization": "Bearer valid-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['email'] == 'test@example.com'
        assert data['email_verified'] is True
        assert data['given_name'] == 'Test'
    
    def test_get_user_info_unauthorized(self):
        """Test getting user info without token."""
        response = client.get("/api/v1/cognito/user-info")
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.api
class TestCognitoEdgeCases:
    """Test edge cases and error handling."""
    
    def test_signup_missing_required_fields(self):
        """Test sign up with missing required fields."""
        response = client.post("/api/v1/cognito/signup", json={
            "email": "test@example.com"
            # Missing password
        })
        
        assert response.status_code == 422
    
    def test_signup_password_too_short(self):
        """Test sign up with short password."""
        response = client.post("/api/v1/cognito/signup", json={
            "email": "test@example.com",
            "password": "short"
        })
        
        assert response.status_code == 422
    
    @patch('app.api.v1.endpoints.auth_cognito.get_cognito_client')
    def test_cognito_service_unavailable(self, mock_get_cognito):
        """Test handling of Cognito service errors."""
        mock_cognito = Mock()
        mock_cognito.sign_up.side_effect = ClientError(
            {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Service down'}},
            'SignUp'
        )
        mock_get_cognito.return_value = mock_cognito
        
        response = client.post("/api/v1/cognito/signup", json={
            "email": "test@example.com",
            "password": "Test123!@#"
        })
        
        assert response.status_code == 500

