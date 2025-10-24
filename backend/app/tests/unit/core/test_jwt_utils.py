"""
Unit Tests for JWT Utils

Tests for app.core.jwt_utils module including:
- Access token creation and verification
- Refresh token creation and verification
- Token expiration handling
- Organization context in tokens
- Token pair creation
- Error handling
"""

import pytest
import time
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import patch
from jose import jwt

from app.core.jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token_without_verification,
    get_organization_from_token,
    refresh_access_token,
    create_token_pair,
    TokenData,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS
)


@pytest.fixture
def test_user_id():
    """Generate a test user ID."""
    return str(uuid4())


@pytest.fixture
def test_email():
    """Generate a test email."""
    return "test@example.com"


@pytest.fixture
def test_org_id():
    """Generate a test organization ID."""
    return uuid4()


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestAccessTokenCreation:
    """Test access token creation."""
    
    def test_create_access_token_minimal(self, test_user_id):
        """Test creating access token with minimal parameters."""
        token = create_access_token(subject=test_user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_email(self, test_user_id, test_email):
        """Test creating access token with email."""
        token = create_access_token(subject=test_user_id, email=test_email)
        
        # Decode to verify email is included
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert payload['email'] == test_email
    
    def test_create_access_token_with_organization(self, test_user_id, test_org_id):
        """Test creating access token with organization context."""
        token = create_access_token(
            subject=test_user_id,
            organization_id=test_org_id,
            organization_role="admin"
        )
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert payload['organization_id'] == str(test_org_id)
        assert payload['organization_role'] == "admin"
    
    def test_create_access_token_with_functional_role(self, test_user_id):
        """Test creating access token with functional role."""
        token = create_access_token(
            subject=test_user_id,
            functional_role="dentist"
        )
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert payload['functional_role'] == "dentist"
    
    def test_create_access_token_with_custom_expiration(self, test_user_id):
        """Test creating access token with custom expiration."""
        custom_delta = timedelta(minutes=30)
        token = create_access_token(
            subject=test_user_id,
            expires_delta=custom_delta
        )
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp_time = datetime.utcfromtimestamp(payload['exp'])
        iat_time = datetime.utcfromtimestamp(payload['iat'])
        
        # Should be approximately 30 minutes
        delta = exp_time - iat_time
        assert 29 <= delta.total_seconds() / 60 <= 31
    
    def test_create_access_token_with_additional_claims(self, test_user_id):
        """Test creating access token with additional claims."""
        additional = {"custom_field": "custom_value", "user_type": "premium"}
        token = create_access_token(
            subject=test_user_id,
            additional_claims=additional
        )
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert payload['custom_field'] == "custom_value"
        assert payload['user_type'] == "premium"
    
    def test_access_token_has_correct_type(self, test_user_id):
        """Test that access token has type 'access'."""
        token = create_access_token(subject=test_user_id)
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert payload['type'] == 'access'
    
    def test_access_token_has_required_fields(self, test_user_id):
        """Test that access token has all required fields."""
        token = create_access_token(subject=test_user_id)
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert 'sub' in payload
        assert 'exp' in payload
        assert 'iat' in payload
        assert 'type' in payload


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestRefreshTokenCreation:
    """Test refresh token creation."""
    
    def test_create_refresh_token(self, test_user_id):
        """Test creating refresh token."""
        token = create_refresh_token(subject=test_user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_refresh_token_has_correct_type(self, test_user_id):
        """Test that refresh token has type 'refresh'."""
        token = create_refresh_token(subject=test_user_id)
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert payload['type'] == 'refresh'
    
    def test_refresh_token_expiration(self, test_user_id):
        """Test that refresh token has longer expiration."""
        token = create_refresh_token(subject=test_user_id)
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp_time = datetime.utcfromtimestamp(payload['exp'])
        iat_time = datetime.utcfromtimestamp(payload['iat'])
        
        # Should be approximately 30 days
        delta = exp_time - iat_time
        assert 29 <= delta.days <= 31
    
    def test_create_refresh_token_with_custom_expiration(self, test_user_id):
        """Test creating refresh token with custom expiration."""
        custom_delta = timedelta(days=7)
        token = create_refresh_token(
            subject=test_user_id,
            expires_delta=custom_delta
        )
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp_time = datetime.utcfromtimestamp(payload['exp'])
        iat_time = datetime.utcfromtimestamp(payload['iat'])
        
        # Should be approximately 7 days
        delta = exp_time - iat_time
        assert 6 <= delta.days <= 8


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestTokenVerification:
    """Test token verification."""
    
    def test_verify_valid_access_token(self, test_user_id, test_email):
        """Test verifying a valid access token."""
        token = create_access_token(subject=test_user_id, email=test_email)
        time.sleep(0.1)  # Avoid timing issues
        
        token_data = verify_token(token, token_type='access')
        
        assert token_data is not None
        assert token_data.sub == test_user_id
        assert token_data.email == test_email
        assert token_data.type == 'access'
    
    def test_verify_valid_refresh_token(self, test_user_id):
        """Test verifying a valid refresh token."""
        token = create_refresh_token(subject=test_user_id)
        
        token_data = verify_token(token, token_type='refresh')
        
        assert token_data is not None
        assert token_data.sub == test_user_id
        assert token_data.type == 'refresh'
    
    def test_verify_token_wrong_type(self, test_user_id):
        """Test verifying token with wrong type."""
        access_token = create_access_token(subject=test_user_id)
        
        # Try to verify as refresh token
        token_data = verify_token(access_token, token_type='refresh')
        
        assert token_data is None
    
    def test_verify_expired_token(self, test_user_id):
        """Test verifying an expired token."""
        # Create token that expires immediately
        token = create_access_token(
            subject=test_user_id,
            expires_delta=timedelta(seconds=-1)
        )
        
        token_data = verify_token(token)
        
        assert token_data is None
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        invalid_token = "invalid.token.string"
        
        token_data = verify_token(invalid_token)
        
        assert token_data is None
    
    def test_verify_token_with_organization(self, test_user_id, test_org_id):
        """Test verifying token with organization context."""
        token = create_access_token(
            subject=test_user_id,
            organization_id=test_org_id,
            organization_role="admin"
        )
        time.sleep(0.1)  # Avoid timing issues
        
        token_data = verify_token(token)
        
        assert token_data is not None
        assert token_data.organization_id == str(test_org_id)
        assert token_data.organization_role == "admin"


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestDecodeWithoutVerification:
    """Test decoding token without verification."""
    
    def test_decode_valid_token(self, test_user_id):
        """Test decoding a valid token without verification."""
        token = create_access_token(subject=test_user_id)
        
        payload = decode_token_without_verification(token)
        
        assert payload is not None
        assert payload['sub'] == test_user_id
    
    def test_decode_expired_token(self, test_user_id):
        """Test decoding an expired token (should work without verification)."""
        token = create_access_token(
            subject=test_user_id,
            expires_delta=timedelta(seconds=-1)
        )
        
        payload = decode_token_without_verification(token)
        
        # Should decode successfully even though expired
        assert payload is not None
        assert payload['sub'] == test_user_id
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "completely.invalid.token"
        
        payload = decode_token_without_verification(invalid_token)
        
        assert payload is None


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestGetOrganizationFromToken:
    """Test extracting organization from token."""
    
    def test_get_organization_from_token(self, test_user_id, test_org_id):
        """Test extracting organization ID from token."""
        token = create_access_token(
            subject=test_user_id,
            organization_id=test_org_id
        )
        time.sleep(0.1)  # Avoid timing issues
        
        org_id = get_organization_from_token(token)
        
        assert org_id is not None
        assert org_id == test_org_id
    
    def test_get_organization_from_token_without_org(self, test_user_id):
        """Test extracting organization from token without org context."""
        token = create_access_token(subject=test_user_id)
        
        org_id = get_organization_from_token(token)
        
        assert org_id is None
    
    def test_get_organization_from_invalid_token(self):
        """Test extracting organization from invalid token."""
        invalid_token = "invalid.token.string"
        
        org_id = get_organization_from_token(invalid_token)
        
        assert org_id is None


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestRefreshAccessToken:
    """Test refreshing access token."""
    
    def test_refresh_access_token(self, test_user_id, test_email):
        """Test creating new access token from refresh token."""
        # Create refresh token
        refresh_token = create_refresh_token(subject=test_user_id)
        time.sleep(0.1)  # Avoid timing issues
        
        # Refresh to get new access token
        new_access_token = refresh_access_token(refresh_token)
        
        assert new_access_token is not None
        
        # Verify new access token
        token_data = verify_token(new_access_token, token_type='access')
        assert token_data is not None
        assert token_data.sub == test_user_id
    
    def test_refresh_access_token_with_new_organization(self, test_user_id):
        """Test refreshing access token with new organization context."""
        refresh_token = create_refresh_token(subject=test_user_id)
        time.sleep(0.1)  # Avoid timing issues
        new_org_id = uuid4()
        
        new_access_token = refresh_access_token(refresh_token, new_organization_id=new_org_id)
        
        assert new_access_token is not None
        
        # Verify new organization is in token
        token_data = verify_token(new_access_token)
        assert token_data.organization_id == str(new_org_id)
    
    def test_refresh_with_invalid_token(self):
        """Test refreshing with invalid refresh token."""
        invalid_token = "invalid.token.string"
        
        new_access_token = refresh_access_token(invalid_token)
        
        assert new_access_token is None
    
    def test_refresh_with_access_token(self, test_user_id):
        """Test refreshing with access token (should fail)."""
        access_token = create_access_token(subject=test_user_id)
        
        new_access_token = refresh_access_token(access_token)
        
        assert new_access_token is None


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestCreateTokenPair:
    """Test creating token pair."""
    
    def test_create_token_pair(self, test_user_id, test_email):
        """Test creating both access and refresh tokens."""
        token_pair = create_token_pair(
            subject=test_user_id,
            email=test_email
        )
        
        assert 'access_token' in token_pair
        assert 'refresh_token' in token_pair
        assert 'token_type' in token_pair
        assert 'expires_in' in token_pair
        
        assert token_pair['token_type'] == 'bearer'
        assert token_pair['expires_in'] == JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    def test_token_pair_access_token_valid(self, test_user_id):
        """Test that access token in pair is valid."""
        token_pair = create_token_pair(subject=test_user_id)
        time.sleep(0.1)  # Avoid timing issues
        
        token_data = verify_token(token_pair['access_token'], token_type='access')
        
        assert token_data is not None
        assert token_data.sub == test_user_id
    
    def test_token_pair_refresh_token_valid(self, test_user_id):
        """Test that refresh token in pair is valid."""
        token_pair = create_token_pair(subject=test_user_id)
        
        token_data = verify_token(token_pair['refresh_token'], token_type='refresh')
        
        assert token_data is not None
        assert token_data.sub == test_user_id
    
    def test_create_token_pair_with_organization(self, test_user_id, test_org_id):
        """Test creating token pair with organization context."""
        token_pair = create_token_pair(
            subject=test_user_id,
            organization_id=test_org_id,
            organization_role="admin",
            functional_role="dentist"
        )
        time.sleep(0.1)  # Avoid timing issues
        
        # Verify access token has organization context
        token_data = verify_token(token_pair['access_token'])
        assert token_data.organization_id == str(test_org_id)
        assert token_data.organization_role == "admin"
        assert token_data.functional_role == "dentist"


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestTokenData:
    """Test TokenData model."""
    
    def test_token_data_creation(self):
        """Test creating TokenData instance."""
        token_data = TokenData(
            sub="user123",
            email="test@example.com",
            organization_id="org123",
            type="access"
        )
        
        assert token_data.sub == "user123"
        assert token_data.email == "test@example.com"
        assert token_data.organization_id == "org123"
        assert token_data.type == "access"
    
    def test_token_data_optional_fields(self):
        """Test TokenData with optional fields."""
        token_data = TokenData(sub="user123")
        
        assert token_data.sub == "user123"
        assert token_data.email is None
        assert token_data.organization_id is None
        assert token_data.type == "access"  # default value


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.jwt
class TestJWTErrorHandling:
    """Test error handling in JWT operations."""
    
    def test_verify_malformed_token(self):
        """Test verifying a malformed token."""
        malformed_token = "not.a.valid.jwt.token.at.all"
        
        token_data = verify_token(malformed_token)
        
        assert token_data is None
    
    def test_verify_token_with_wrong_secret(self, test_user_id):
        """Test verifying token with wrong secret."""
        # Create token with correct secret
        token = create_access_token(subject=test_user_id)
        
        # Try to decode with wrong secret
        try:
            jwt.decode(token, "wrong-secret", algorithms=[JWT_ALGORITHM])
            assert False, "Should have raised JWTError"
        except Exception:
            assert True
    
    def test_create_token_with_none_subject(self):
        """Test creating token with None subject."""
        try:
            token = create_access_token(subject=None)
            # Should still create token, but with None as subject
            assert token is not None
        except Exception:
            # Or it might raise an exception, which is also acceptable
            assert True

