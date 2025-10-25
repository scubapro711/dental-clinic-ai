"""
Bug #32: Missing CSRF Protection - Reproduction Tests

These tests demonstrate that the application is vulnerable to CSRF attacks
by attempting to perform state-changing operations without CSRF tokens.

All tests should FAIL initially (proving vulnerability exists).
After fix, tests should PASS (proving CSRF protection works).
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.core.security import create_access_token
from app.core.rbac import Role


class TestCSRFReproduction:
    """Reproduction tests for CSRF vulnerability"""
    
    # ========================================================================
    # Test 1: POST Request Without CSRF Token (Should Be Blocked)
    # ========================================================================
    
    def test_csrf_post_appointment_without_token(self, client, test_user, test_organization):
        """
        Test: POST request without CSRF token should be blocked
        Current: ❌ Request succeeds (VULNERABLE!)
        Expected: ✅ Request blocked with 403 Forbidden
        """
        # Create access token
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        
        # Set cookie (simulating authenticated user)
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Attempt to create appointment WITHOUT CSRF token
        response = client.post(
            "/api/v1/appointments/",
            json={
                "patient_id": str(test_user.id),
                "doctor_id": str(test_user.id),
                "date": "2025-02-01",
                "time": "10:00",
                "reason": "Checkup"
            }
            # ❌ No X-CSRF-Token header!
        )
        
        # Current behavior: Request succeeds (VULNERABLE!)
        # Expected behavior: 403 Forbidden
        
        # This test will FAIL initially (proving vulnerability)
        # After fix, it should PASS (proving protection works)
        assert response.status_code == 403, \
            f"Expected 403 Forbidden (CSRF protection), got {response.status_code}"
        assert "CSRF" in response.json().get("detail", ""), \
            "Error message should mention CSRF"
    
    # ========================================================================
    # Test 2: PUT Request Without CSRF Token
    # ========================================================================
    
    def test_csrf_put_patient_without_token(self, client, test_user):
        """
        Test: PUT request without CSRF token should be blocked
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Attempt to update patient WITHOUT CSRF token
        response = client.put(
            f"/api/v1/patients/{test_user.id}",
            json={
                "full_name": "Hacked Name",
                "email": "hacked@evil.com"
            }
        )
        
        assert response.status_code == 403, \
            "PUT request without CSRF token should be blocked"
    
    # ========================================================================
    # Test 3: DELETE Request Without CSRF Token
    # ========================================================================
    
    def test_csrf_delete_appointment_without_token(self, client, test_user):
        """
        Test: DELETE request without CSRF token should be blocked
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Attempt to delete appointment WITHOUT CSRF token
        response = client.delete("/api/v1/appointments/123")
        
        assert response.status_code == 403, \
            "DELETE request without CSRF token should be blocked"
    
    # ========================================================================
    # Test 4: PATCH Request Without CSRF Token
    # ========================================================================
    
    def test_csrf_patch_user_without_token(self, client, test_user):
        """
        Test: PATCH request without CSRF token should be blocked
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Attempt to patch user WITHOUT CSRF token
        response = client.patch(
            f"/api/v1/users/{test_user.id}",
            json={"email": "hacked@evil.com"}
        )
        
        # Note: This might return 404 if PATCH endpoint doesn't exist
        # But it should still check CSRF before checking route
        assert response.status_code in [403, 404], \
            "PATCH request without CSRF token should be blocked or not found"
    
    # ========================================================================
    # Test 5: Cross-Origin Request Simulation
    # ========================================================================
    
    def test_csrf_cross_origin_attack(self, client, test_user):
        """
        Test: Simulate CSRF attack from malicious website
        
        Scenario:
        1. User is logged into DentaFlow
        2. User visits malicious website
        3. Malicious website sends POST request to DentaFlow
        4. Browser automatically includes cookies
        5. DentaFlow should reject request (no CSRF token)
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Simulate cross-origin request (malicious website)
        response = client.post(
            "/api/v1/appointments/",
            json={
                "patient_id": str(test_user.id),
                "doctor_id": str(test_user.id),
                "date": "2025-02-01",
                "time": "10:00",
                "reason": "Fake appointment from attacker"
            },
            headers={
                "Origin": "https://evil.com",  # Malicious origin
                "Referer": "https://evil.com/attack.html"
            }
        )
        
        # Should be blocked by CSRF protection
        assert response.status_code == 403, \
            "Cross-origin request without CSRF token should be blocked"
    
    # ========================================================================
    # Test 6: Invalid CSRF Token
    # ========================================================================
    
    def test_csrf_invalid_token(self, client, test_user):
        """
        Test: Request with invalid CSRF token should be blocked
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # Attempt with INVALID CSRF token
        response = client.post(
            "/api/v1/appointments/",
            json={
                "patient_id": str(test_user.id),
                "doctor_id": str(test_user.id),
                "date": "2025-02-01",
                "time": "10:00"
            },
            headers={
                "X-CSRF-Token": "invalid_token_12345"  # Invalid token
            }
        )
        
        assert response.status_code == 403, \
            "Request with invalid CSRF token should be blocked"
    
    # ========================================================================
    # Test 7: Reused CSRF Token (Should Be Blocked)
    # ========================================================================
    
    @pytest.mark.skip(reason="CSRF tokens not implemented yet")
    def test_csrf_token_reuse_attack(self, client, test_user):
        """
        Test: Reusing CSRF token from previous request should be blocked
        
        Note: This test is skipped until CSRF tokens are implemented
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # First request (should succeed with valid token)
        response1 = client.get("/api/v1/csrf-token")
        csrf_token = response1.json()["csrf_token"]
        
        # Use token for first POST
        response2 = client.post(
            "/api/v1/appointments/",
            json={"patient_id": str(test_user.id), "date": "2025-02-01"},
            headers={"X-CSRF-Token": csrf_token}
        )
        assert response2.status_code == 200
        
        # Try to reuse same token (should be blocked)
        response3 = client.post(
            "/api/v1/appointments/",
            json={"patient_id": str(test_user.id), "date": "2025-02-02"},
            headers={"X-CSRF-Token": csrf_token}  # Reused token
        )
        assert response3.status_code == 403, \
            "Reused CSRF token should be blocked"
    
    # ========================================================================
    # Test 8: Google OAuth State Parameter Not Validated
    # ========================================================================
    
    def test_csrf_google_oauth_state_not_validated(self, client):
        """
        Test: Google OAuth callback doesn't validate state parameter
        
        This is a specific CSRF vulnerability in the OAuth flow.
        """
        # Simulate OAuth callback with INVALID state
        response = client.get(
            "/api/v1/auth/google/callback",
            params={
                "code": "fake_auth_code",
                "state": "attacker_controlled_state"  # Invalid state
            }
        )
        
        # Current behavior: Might accept invalid state (VULNERABLE!)
        # Expected behavior: Should reject with 403 or 400
        
        # This test documents the vulnerability
        # After fix, should return 403 or 400
        assert response.status_code in [400, 403, 500], \
            "OAuth callback should validate state parameter"
    
    # ========================================================================
    # Test 9: GET Request Should Not Require CSRF Token
    # ========================================================================
    
    def test_csrf_get_request_allowed_without_token(self, client, test_user):
        """
        Test: GET requests should NOT require CSRF token
        
        CSRF protection should only apply to state-changing operations.
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        client.cookies.set("access_token", f"Bearer {access_token}")
        
        # GET request WITHOUT CSRF token (should succeed)
        response = client.get("/api/v1/appointments/")
        
        # GET requests should succeed without CSRF token
        assert response.status_code in [200, 404], \
            "GET requests should not require CSRF token"
    
    # ========================================================================
    # Test 10: CSRF Protection Should Not Break API Clients
    # ========================================================================
    
    def test_csrf_api_client_with_bearer_token(self, client, test_user):
        """
        Test: API clients using Bearer tokens in headers should work
        
        CSRF protection should only apply to cookie-based authentication.
        Requests with Bearer tokens in Authorization header should bypass CSRF.
        """
        access_token = create_access_token(
            data={"sub": str(test_user.id), "role": test_user.role.value}
        )
        
        # Use Bearer token in Authorization header (NOT cookie)
        response = client.post(
            "/api/v1/appointments/",
            json={
                "patient_id": str(test_user.id),
                "doctor_id": str(test_user.id),
                "date": "2025-02-01",
                "time": "10:00"
            },
            headers={
                "Authorization": f"Bearer {access_token}"
                # No CSRF token needed for Bearer auth
            }
        )
        
        # Should succeed (Bearer auth bypasses CSRF)
        # Note: Might fail due to missing data, but shouldn't fail due to CSRF
        assert response.status_code != 403, \
            "Bearer token authentication should bypass CSRF protection"


# Summary of CSRF Reproduction Tests:
#
# 1. test_csrf_post_appointment_without_token - POST without token
# 2. test_csrf_put_patient_without_token - PUT without token
# 3. test_csrf_delete_appointment_without_token - DELETE without token
# 4. test_csrf_patch_user_without_token - PATCH without token
# 5. test_csrf_cross_origin_attack - Cross-origin attack simulation
# 6. test_csrf_invalid_token - Invalid token rejection
# 7. test_csrf_token_reuse_attack - Token reuse prevention (skipped)
# 8. test_csrf_google_oauth_state_not_validated - OAuth state validation
# 9. test_csrf_get_request_allowed_without_token - GET requests allowed
# 10. test_csrf_api_client_with_bearer_token - Bearer auth bypass
#
# Total: 10 tests (9 active, 1 skipped)
#
# Expected Results (Before Fix):
# - Tests 1-6, 8: FAIL (proving vulnerability exists)
# - Tests 9-10: PASS (correct behavior)
#
# Expected Results (After Fix):
# - All 10 tests: PASS (proving CSRF protection works)

