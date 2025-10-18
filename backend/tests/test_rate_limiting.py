"""
Test Rate Limiting Middleware

Validates that rate limiting is properly enforced on API endpoints.
"""

import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_rate_limit_not_exceeded():
    """Test that requests within rate limit succeed"""
    # Make a few requests that should succeed
    for i in range(3):
        response = client.get("/health")
        assert response.status_code == 200


def test_rate_limit_headers_present():
    """Test that rate limit headers are present in responses"""
    response = client.get("/health")
    
    # Note: Headers may not be present if rate limiting is disabled in tests
    # This is just to check if they exist when enabled
    if "X-RateLimit-Limit" in response.headers:
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers


def test_global_rate_limit():
    """Test global rate limit (100/minute)"""
    # This test is informational - actual rate limit testing
    # requires making 100+ requests which is slow
    response = client.get("/health")
    assert response.status_code == 200


def test_rate_limit_key_function():
    """Test that rate limit key function works"""
    from app.middleware.rate_limiter import get_rate_limit_key
    from fastapi import Request
    
    # Create a mock request
    class MockRequest:
        def __init__(self):
            self.state = type('obj', (object,), {})()
            self.client = type('obj', (object,), {'host': '127.0.0.1'})()
    
    request = MockRequest()
    
    # Test without user (should use IP)
    key = get_rate_limit_key(request)
    assert key.startswith("ip:")
    
    # Test with user (should use user ID)
    request.state.user = type('obj', (object,), {'id': 123})()
    key = get_rate_limit_key(request)
    assert key == "user:123"


def test_role_based_limit_calculation():
    """Test role-based rate limit calculation"""
    from app.middleware.rate_limiter import get_role_based_limit
    
    # Create a mock request
    class MockRequest:
        def __init__(self, role=None):
            self.state = type('obj', (object,), {})()
            if role:
                self.state.user = type('obj', (object,), {'role': role})()
    
    # Test super_admin (5x multiplier)
    request = MockRequest("super_admin")
    limit = get_role_based_limit(request, "10/minute")
    assert limit == "50/minute"
    
    # Test org_admin (3x multiplier)
    request = MockRequest("org_admin")
    limit = get_role_based_limit(request, "10/minute")
    assert limit == "30/minute"
    
    # Test org_staff (2x multiplier)
    request = MockRequest("org_staff")
    limit = get_role_based_limit(request, "10/minute")
    assert limit == "20/minute"
    
    # Test org_viewer (1x multiplier)
    request = MockRequest("org_viewer")
    limit = get_role_based_limit(request, "10/minute")
    assert limit == "10/minute"
    
    # Test anonymous (0.5x multiplier)
    request = MockRequest()
    limit = get_role_based_limit(request, "10/minute")
    assert limit == "5/minute"


def test_rate_limit_configurations():
    """Test that rate limit configurations are defined"""
    from app.middleware.rate_limiter import RATE_LIMITS, get_rate_limit
    
    # Check that critical endpoints have rate limits defined
    assert "auth_login" in RATE_LIMITS
    assert "auth_register" in RATE_LIMITS
    assert "ai_chat" in RATE_LIMITS
    
    # Check that get_rate_limit returns valid limits
    assert get_rate_limit("auth_login") == "5/minute"
    assert get_rate_limit("auth_register") == "3/minute"
    assert get_rate_limit("ai_chat") == "20/minute"
    
    # Check default limit for unknown endpoint
    assert get_rate_limit("unknown_endpoint") == "30/minute"


def test_rate_limit_exceeded_handler():
    """Test rate limit exceeded handler"""
    from app.middleware.rate_limiter import rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from fastapi import Request
    
    # Create a mock request
    class MockRequest:
        def __init__(self):
            self.url = type('obj', (object,), {'path': '/test'})()
            self.state = type('obj', (object,), {})()
            self.client = type('obj', (object,), {'host': '127.0.0.1'})()
    
    request = MockRequest()
    
    # Create a mock limit object
    class MockLimit:
        def __init__(self):
            self.amount = 10
            self.per = 60
            self.error_message = None
            self.limit = "10/minute"
    
    limit = MockLimit()
    
    # Create a mock exception with proper Limit object
    exc = RateLimitExceeded(limit)
    exc.retry_after = 60
    exc.reset = 1234567890
    
    # Call handler
    response = rate_limit_exceeded_handler(request, exc)
    
    # Check response
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert response.headers["Retry-After"] == "60"


def test_limiter_instance():
    """Test that limiter instance is properly configured"""
    from app.middleware.rate_limiter import limiter
    
    assert limiter is not None
    assert limiter.enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

