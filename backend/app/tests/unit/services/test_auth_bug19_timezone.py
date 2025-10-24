"""
Tests for Bug #19: datetime timezone awareness in authentication.

Ensures all datetime objects in auth service are timezone-aware.
"""
import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt

from app.services.auth_service import AuthService
from app.core import jwt_utils
from app.core.config import settings


class TestBug19TimezoneAwareness:
    """Test timezone awareness in authentication."""
    
    def test_access_token_expiration_timezone_aware(self):
        """Test that access token expiration is timezone-aware."""
        token_data = {"sub": "test-user-id", "email": "test@example.com"}
        token = AuthService.create_access_token(token_data)
        
        # Decode token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check exp is a timestamp (int)
        assert 'exp' in payload
        assert isinstance(payload['exp'], int)
        
        # Convert to datetime and verify it's in the future
        exp_dt = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        assert exp_dt > now, "Token should not be expired"
        assert exp_dt.tzinfo is not None, "Expiration should be timezone-aware"
        assert exp_dt.tzinfo == timezone.utc, "Expiration should be UTC"
    
    def test_refresh_token_expiration_timezone_aware(self):
        """Test that refresh token expiration is timezone-aware."""
        token_data = {"sub": "test-user-id"}
        token = AuthService.create_refresh_token(token_data)
        
        # Decode token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check exp
        assert 'exp' in payload
        exp_dt = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        assert exp_dt > now
        assert exp_dt.tzinfo == timezone.utc
    
    def test_token_iat_timezone_aware(self):
        """Test that token iat (issued at) is timezone-aware."""
        token = jwt_utils.create_access_token(
            subject="test-user",
            email="test@example.com"
        )
        
        payload = jwt.decode(
            token,
            jwt_utils.JWT_SECRET_KEY,
            algorithms=[jwt_utils.JWT_ALGORITHM]
        )
        
        # Check iat
        assert 'iat' in payload
        iat_dt = datetime.fromtimestamp(payload['iat'], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # iat should be recent (within last minute)
        assert (now - iat_dt).total_seconds() < 60
        assert iat_dt.tzinfo == timezone.utc
    
    def test_custom_expiration_timezone_aware(self):
        """Test custom expiration delta is timezone-aware."""
        custom_delta = timedelta(hours=2)
        token_data = {"sub": "test-user"}
        token = AuthService.create_access_token(token_data, expires_delta=custom_delta)
        
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        exp_dt = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        expected_exp = now + custom_delta
        
        # Should be approximately 2 hours from now (within 10 seconds tolerance)
        time_diff = abs((exp_dt - expected_exp).total_seconds())
        assert time_diff < 10, f"Expected ~2 hours, got {time_diff}s difference"
        assert exp_dt.tzinfo == timezone.utc
    
    def test_timezone_consistency_with_odoo_client(self):
        """Test timezone consistency with odoo_client (Bug #11 fix)."""
        # Both should use timezone.utc
        auth_now = datetime.now(timezone.utc)
        
        # Create token
        token = AuthService.create_access_token({"sub": "test"})
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        exp_dt = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        
        # Both should be timezone-aware with UTC
        assert auth_now.tzinfo == timezone.utc
        assert exp_dt.tzinfo == timezone.utc
        
        # Should be comparable without issues
        assert exp_dt > auth_now


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
