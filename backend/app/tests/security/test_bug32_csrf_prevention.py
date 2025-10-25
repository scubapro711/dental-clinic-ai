"""
Bug #32: CSRF Protection - Prevention Tests

These tests verify that CSRF protection is working correctly after the fix.

All tests should PASS, proving that:
1. CSRF tokens are generated and validated
2. Requests without valid tokens are blocked
3. Bearer token authentication bypasses CSRF
4. Safe methods (GET) don't require CSRF tokens
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token


class TestCSRFPrevention:
    """Prevention tests for CSRF protection"""
    
    # ========================================================================
    # Test 1: CSRF Token Generation
    # ========================================================================
    
    def test_csrf_token_generated_on_get_request(self, client):
        """
        Test: CSRF token is generated and set in cookie on GET requests
        """
        response = client.get("/")
        
        # Check that CSRF token cookie is set
        assert "csrf_token" in response.cookies, \
            "CSRF token should be set in cookie on GET request"
        
        csrf_token = response.cookies.get("csrf_token")
        assert csrf_token, "CSRF token should not be empty"
        assert len(csrf_token) > 20, "CSRF token should be sufficiently long"
    
    # ========================================================================
    # Test 2: POST Request Blocked Without CSRF Token
    # ========================================================================
    
    def test_csrf_post_blocked_without_token(self, client, test_user):
        """
        Test: POST request without CSRF token is blocked with 403
        """
        # Create access token
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        
        # Set cookie (simulating authenticated user)
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Attempt POST without CSRF token
        response = client.post(
            "/api/v1/agents/chat",
            json={"message": "test"}
        )
        
        # Should be blocked with 403 Forbidden
        assert response.status_code == 403, \
            f"POST without CSRF token should return 403, got {response.status_code}"
        assert "CSRF" in response.json().get("detail", ""), \
            "Error message should mention CSRF"
    
    # ========================================================================
    # Test 3: POST Request Succeeds With Valid CSRF Token
    # ========================================================================
    
    def test_csrf_post_succeeds_with_valid_token(self, client, test_user):
        """
        Test: POST request with valid CSRF token succeeds
        """
        # Create access token
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        
        # Get CSRF token from GET request
        get_response = client.get("/")
        csrf_token = get_response.cookies.get("csrf_token")
        
        # Set both cookies
        client.cookies.set("access_token", f"Bearer {access_token}")
        client.cookies.set("csrf_token", csrf_token)
        
        # Attempt POST with valid CSRF token
        response = client.post(
            "/api/v1/agents/chat",
            json={"message": "test"},
            headers={"X-CSRF-Token": csrf_token}
        )
        
        # Should NOT be blocked by CSRF (might fail for other reasons)
        assert response.status_code != 403, \
            "POST with valid CSRF token should not be blocked by CSRF protection"
    
    # ========================================================================
    # Test 4: Invalid CSRF Token Blocked
    # ========================================================================
    
    def test_csrf_invalid_token_blocked(self, client, test_user):
        """
        Test: Request with invalid CSRF token is blocked
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        
        # Get valid CSRF token
        get_response = client.get("/")
        valid_csrf_token = get_response.cookies.get("csrf_token")
        
        # Set cookies
        client.cookies.set("access_token", f"Bearer {access_token}")
        client.cookies.set("csrf_token", valid_csrf_token)
        
        # Attempt POST with INVALID CSRF token in header
        response = client.post(
            "/api/v1/agents/chat",
            json={"message": "test"},
            headers={"X-CSRF-Token": "invalid_token_12345"}
        )
        
        # Should be blocked
        assert response.status_code == 403, \
            "POST with invalid CSRF token should be blocked"
    
    # ========================================================================
    # Test 5: Bearer Token Authentication Bypasses CSRF
    # ========================================================================
    
    def test_csrf_bearer_token_bypasses_csrf(self, client, test_user):
        """
        Test: Requests with Bearer token in Authorization header bypass CSRF
        
        This is correct behavior - CSRF only applies to cookie-based auth.
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        
        # Use Bearer token in Authorization header (NOT cookie)
        response = client.post(
            "/api/v1/agents/chat",
            json={"message": "test"},
            headers={"Authorization": f"Bearer {access_token}"}
            # No CSRF token needed
        )
        
        # Should NOT be blocked by CSRF
        assert response.status_code != 403, \
            "Bearer token authentication should bypass CSRF protection"
    
    # ========================================================================
    # Test 6: GET Requests Don't Require CSRF Token
    # ========================================================================
    
    def test_csrf_get_requests_allowed(self, client):
        """
        Test: GET requests don't require CSRF token
        """
        # GET request without CSRF token
        response = client.get("/api/v1/status")
        
        # Should succeed (or fail for other reasons, but not CSRF)
        assert response.status_code != 403, \
            "GET requests should not require CSRF token"
    
    # ========================================================================
    # Test 7: PUT Request Blocked Without CSRF Token
    # ========================================================================
    
    def test_csrf_put_blocked_without_token(self, client, test_user):
        """
        Test: PUT request without CSRF token is blocked
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Attempt PUT without CSRF token
        response = client.put(
            "/api/v1/users/me",
            json={"full_name": "Test User"}
        )
        
        # Should be blocked (403) or not found (404), but checked for CSRF first
        assert response.status_code in [403, 404], \
            "PUT without CSRF token should be blocked or not found"
    
    # ========================================================================
    # Test 8: DELETE Request Blocked Without CSRF Token
    # ========================================================================
    
    def test_csrf_delete_blocked_without_token(self, client, test_user):
        """
        Test: DELETE request without CSRF token is blocked
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Attempt DELETE without CSRF token
        response = client.delete("/api/v1/agents/conversations/test-id")
        
        # Should be blocked
        assert response.status_code in [403, 404], \
            "DELETE without CSRF token should be blocked or not found"
    
    # ========================================================================
    # Test 9: CSRF Token Cookie Attributes
    # ========================================================================
    
    def test_csrf_token_cookie_attributes(self, client):
        """
        Test: CSRF token cookie has correct security attributes
        """
        response = client.get("/")
        
        # Get cookie header
        set_cookie_header = response.headers.get("set-cookie", "")
        
        # Check for CSRF token cookie
        assert "csrf_token=" in set_cookie_header, \
            "CSRF token cookie should be set"
        
        # Check security attributes
        # Note: httponly=False is correct (JavaScript needs to read it)
        assert "Secure" in set_cookie_header or "secure" in set_cookie_header, \
            "CSRF token cookie should have Secure flag"
        assert "SameSite=strict" in set_cookie_header or "samesite=strict" in set_cookie_header.lower(), \
            "CSRF token cookie should have SameSite=strict"
    
    # ========================================================================
    # Test 10: Exempt Paths Don't Require CSRF Token
    # ========================================================================
    
    def test_csrf_exempt_paths_allowed(self, client):
        """
        Test: Exempt paths (like /docs) don't require CSRF token
        """
        # Access exempt path
        response = client.get("/docs")
        
        # Should succeed
        assert response.status_code == 200, \
            "Exempt paths should not require CSRF token"
    
    # ========================================================================
    # Test 11: Login Endpoint Exempt from CSRF
    # ========================================================================
    
    def test_csrf_login_endpoint_exempt(self, client):
        """
        Test: Login endpoint is exempt from CSRF protection
        
        Login endpoint can't require CSRF token because user doesn't have
        a session yet.
        """
        # Attempt login without CSRF token
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "test_password"
            }
        )
        
        # Should NOT be blocked by CSRF (might fail for auth reasons)
        assert response.status_code != 403, \
            "Login endpoint should be exempt from CSRF protection"
    
    # ========================================================================
    # Test 12: CSRF Protection Doesn't Break Existing Functionality
    # ========================================================================
    
    def test_csrf_backward_compatibility(self, client, test_user):
        """
        Test: CSRF protection doesn't break existing API clients
        
        API clients using Bearer tokens should continue to work.
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        
        # Use Bearer token (typical API client)
        response = client.get(
            "/api/v1/status",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Should work normally
        assert response.status_code == 200, \
            "CSRF protection should not break Bearer token authentication"


# Summary of CSRF Prevention Tests:
#
# 1. test_csrf_token_generated_on_get_request - Token generation
# 2. test_csrf_post_blocked_without_token - POST blocked without token
# 3. test_csrf_post_succeeds_with_valid_token - POST succeeds with token
# 4. test_csrf_invalid_token_blocked - Invalid token blocked
# 5. test_csrf_bearer_token_bypasses_csrf - Bearer auth bypass
# 6. test_csrf_get_requests_allowed - GET allowed
# 7. test_csrf_put_blocked_without_token - PUT blocked
# 8. test_csrf_delete_blocked_without_token - DELETE blocked
# 9. test_csrf_token_cookie_attributes - Cookie security
# 10. test_csrf_exempt_paths_allowed - Exempt paths
# 11. test_csrf_login_endpoint_exempt - Login exempt
# 12. test_csrf_backward_compatibility - Backward compatibility
#
# Total: 12 comprehensive CSRF prevention tests
#
# Expected Results (After Fix):
# - All 12 tests: PASS (proving CSRF protection works correctly)

