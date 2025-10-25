"""
Bug #33: Insecure JWT Secret - Reproduction Tests

These tests demonstrate the vulnerability of using a hardcoded default JWT secret.
They prove that an attacker can forge JWT tokens if the default secret is in use.

Severity: Critical (CVSS 9.8)
Category: Authentication & Session Management
HIPAA Impact: §164.312(a)(1) Access Control, §164.312(d) Authentication
"""
import pytest
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.jwt_utils import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    verify_token,
    create_access_token,
    create_refresh_token
)


class TestBug33JWTSecretVulnerability:
    """Test suite demonstrating JWT secret vulnerability."""
    
    def test_default_secret_is_predictable(self):
        """
        Test that the default JWT secret is predictable.
        
        VULNERABILITY: If JWT_SECRET_KEY env var is not set, the application
        uses 'your-secret-key-change-in-production' as the default secret.
        
        This is a well-known placeholder that attackers can easily discover.
        """
        # Check if using default secret
        default_secret = 'your-secret-key-change-in-production'
        
        # If JWT_SECRET_KEY env var is not set, it will use the default
        if 'JWT_SECRET_KEY' not in os.environ:
            assert JWT_SECRET_KEY == default_secret, \
                "Default secret should be the predictable placeholder"
        
        # This test PASSES if the vulnerability exists (default secret in use)
        # It should FAIL after the fix (no default secret allowed)
    
    def test_attacker_can_forge_admin_token(self):
        """
        Test that an attacker can forge a JWT token with admin privileges.
        
        ATTACK SCENARIO:
        1. Attacker knows the default secret
        2. Attacker creates a forged token with organization_role='owner'
        3. Forged token is accepted by the application
        4. Attacker has full admin access
        """
        # Attacker creates forged token
        forged_payload = {
            'sub': 'attacker_user_id',
            'email': 'attacker@evil.com',
            'organization_id': 'target_org_id',
            'organization_role': 'owner',  # Admin access!
            'functional_role': 'dentist',
            'exp': int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),
            'iat': int(datetime.now(timezone.utc).timestamp()),
            'type': 'access'
        }
        
        # Use the default secret (known to attacker)
        default_secret = 'your-secret-key-change-in-production'
        forged_token = jwt.encode(forged_payload, default_secret, algorithm=JWT_ALGORITHM)
        
        # If the application is using the default secret, the forged token will verify!
        if JWT_SECRET_KEY == default_secret:
            token_data = verify_token(forged_token)
            
            # VULNERABILITY: Forged token is accepted!
            assert token_data is not None, "Forged token should be accepted (vulnerability)"
            assert token_data.organization_role == 'owner', "Attacker has admin access!"
            
            # This proves the vulnerability exists
            pytest.fail("SECURITY VULNERABILITY: Forged admin token was accepted!")
    
    def test_attacker_can_impersonate_any_user(self):
        """
        Test that an attacker can impersonate any user.
        
        ATTACK SCENARIO:
        1. Attacker knows a legitimate user's email
        2. Attacker creates forged token for that user
        3. Attacker gains access to user's data
        """
        # Target user
        target_email = 'doctor@dentaflow.com'
        target_user_id = 'legitimate_user_id'
        
        # Attacker creates forged token
        forged_payload = {
            'sub': target_user_id,
            'email': target_email,
            'organization_id': 'target_org_id',
            'organization_role': 'staff',
            'functional_role': 'dentist',
            'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            'iat': int(datetime.now(timezone.utc).timestamp()),
            'type': 'access'
        }
        
        default_secret = 'your-secret-key-change-in-production'
        forged_token = jwt.encode(forged_payload, default_secret, algorithm=JWT_ALGORITHM)
        
        if JWT_SECRET_KEY == default_secret:
            token_data = verify_token(forged_token)
            
            # VULNERABILITY: Forged token is accepted!
            assert token_data is not None
            assert token_data.email == target_email
            assert token_data.sub == target_user_id
            
            pytest.fail("SECURITY VULNERABILITY: Attacker can impersonate any user!")
    
    def test_attacker_can_create_long_lived_tokens(self):
        """
        Test that an attacker can create tokens with arbitrary expiration.
        
        ATTACK SCENARIO:
        1. Attacker creates token with 10-year expiration
        2. Token remains valid indefinitely
        3. Attacker has persistent access
        """
        # Attacker creates token with 10-year expiration
        forged_payload = {
            'sub': 'attacker_user_id',
            'email': 'attacker@evil.com',
            'organization_role': 'owner',
            'exp': int((datetime.now(timezone.utc) + timedelta(days=3650)).timestamp()),  # 10 years!
            'iat': int(datetime.now(timezone.utc).timestamp()),
            'type': 'access'
        }
        
        default_secret = 'your-secret-key-change-in-production'
        forged_token = jwt.encode(forged_payload, default_secret, algorithm=JWT_ALGORITHM)
        
        if JWT_SECRET_KEY == default_secret:
            token_data = verify_token(forged_token)
            
            # VULNERABILITY: Long-lived token is accepted!
            assert token_data is not None
            
            # Check expiration is in the far future
            exp_datetime = datetime.fromtimestamp(token_data.exp, tz=timezone.utc)
            years_from_now = (exp_datetime - datetime.now(timezone.utc)).days / 365
            
            assert years_from_now > 5, "Token expires more than 5 years from now!"
            
            pytest.fail("SECURITY VULNERABILITY: Attacker can create long-lived tokens!")
    
    def test_attacker_can_forge_refresh_token(self):
        """
        Test that an attacker can forge refresh tokens.
        
        ATTACK SCENARIO:
        1. Attacker creates forged refresh token
        2. Attacker uses it to get new access tokens indefinitely
        3. Attacker has persistent access
        """
        # Attacker creates forged refresh token
        forged_payload = {
            'sub': 'attacker_user_id',
            'exp': int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),
            'iat': int(datetime.now(timezone.utc).timestamp()),
            'type': 'refresh'
        }
        
        default_secret = 'your-secret-key-change-in-production'
        forged_refresh_token = jwt.encode(forged_payload, default_secret, algorithm=JWT_ALGORITHM)
        
        if JWT_SECRET_KEY == default_secret:
            token_data = verify_token(forged_refresh_token, token_type='refresh')
            
            # VULNERABILITY: Forged refresh token is accepted!
            assert token_data is not None
            assert token_data.type == 'refresh'
            
            pytest.fail("SECURITY VULNERABILITY: Attacker can forge refresh tokens!")
    
    def test_no_validation_of_secret_strength(self):
        """
        Test that there's no validation of JWT secret strength.
        
        VULNERABILITY: The application doesn't check if the secret is strong enough.
        Even if a custom secret is set, it might be weak (e.g., "password123").
        """
        # Check if there's any validation of secret strength
        # (There isn't in the current implementation)
        
        # The secret should be at least 32 bytes (256 bits) for HS256
        min_secret_length = 32
        
        if len(JWT_SECRET_KEY) < min_secret_length:
            pytest.fail(f"JWT secret is too short ({len(JWT_SECRET_KEY)} bytes). "
                       f"Should be at least {min_secret_length} bytes for security.")
    
    def test_no_startup_validation_for_production(self):
        """
        Test that there's no startup validation to ensure production-ready config.
        
        VULNERABILITY: The application starts normally even with insecure configuration.
        There should be a check that fails if the default secret is in use.
        """
        default_secret = 'your-secret-key-change-in-production'
        
        if JWT_SECRET_KEY == default_secret:
            pytest.fail("SECURITY VULNERABILITY: Application is using default JWT secret! "
                       "This should cause a startup failure in production.")
    
    def test_no_secret_rotation_mechanism(self):
        """
        Test that there's no mechanism for JWT secret rotation.
        
        BEST PRACTICE: Secrets should be rotated periodically.
        Current implementation has no support for secret rotation.
        """
        # Check if there's any secret rotation mechanism
        # (There isn't in the current implementation)
        
        # This is a design limitation, not a direct vulnerability
        # But it increases risk if secret is ever compromised
        
        # For now, just document this limitation
        assert True, "No secret rotation mechanism exists (design limitation)"
    
    def test_legitimate_token_still_works(self):
        """
        Test that legitimate tokens created by the application still work.
        
        This ensures that the vulnerability is in the predictable secret,
        not in the token creation/verification logic itself.
        """
        # Create legitimate token
        legitimate_token = create_access_token(
            subject='legitimate_user_id',
            email='user@dentaflow.com',
            organization_role='staff'
        )
        
        # Verify it works
        token_data = verify_token(legitimate_token)
        
        assert token_data is not None
        assert token_data.sub == 'legitimate_user_id'
        assert token_data.email == 'user@dentaflow.com'
    
    def test_token_type_validation_works(self):
        """
        Test that token type validation works correctly.
        
        This ensures that access tokens can't be used as refresh tokens and vice versa.
        """
        # Create access token
        access_token = create_access_token(subject='user_id')
        
        # Try to verify as refresh token (should fail)
        token_data = verify_token(access_token, token_type='refresh')
        
        assert token_data is None, "Access token should not verify as refresh token"
        
        # Create refresh token
        refresh_token = create_refresh_token(subject='user_id')
        
        # Try to verify as access token (should fail)
        token_data = verify_token(refresh_token, token_type='access')
        
        assert token_data is None, "Refresh token should not verify as access token"


class TestBug33EnvironmentConfiguration:
    """Test environment configuration for JWT secret."""
    
    def test_jwt_secret_key_environment_variable(self):
        """
        Test that JWT_SECRET_KEY can be set via environment variable.
        
        This is the correct way to configure the secret in production.
        """
        # Check if environment variable is set
        env_secret = os.getenv('JWT_SECRET_KEY')
        
        if env_secret:
            assert JWT_SECRET_KEY == env_secret, \
                "JWT_SECRET_KEY should match environment variable"
        else:
            # If not set, it will use the default (vulnerable)
            assert JWT_SECRET_KEY == 'your-secret-key-change-in-production', \
                "Default secret is in use (vulnerable)"
    
    def test_jwt_algorithm_is_secure(self):
        """
        Test that JWT algorithm is secure.
        
        HS256 is acceptable if the secret is strong.
        RS256 would be better (asymmetric) but requires key management.
        """
        assert JWT_ALGORITHM == 'HS256', "JWT algorithm should be HS256"
        
        # Note: RS256 would be more secure but requires public/private key pair
        # For now, HS256 is acceptable if the secret is strong


# Test execution summary
def test_bug33_summary():
    """
    Summary of Bug #33 vulnerability.
    
    This test always passes but documents the vulnerability.
    """
    summary = """
    BUG #33: INSECURE JWT SECRET
    
    Severity: Critical (CVSS 9.8)
    
    Vulnerability:
    - Hardcoded default JWT secret: 'your-secret-key-change-in-production'
    - If JWT_SECRET_KEY env var not set, application uses predictable default
    - Attacker can forge JWT tokens with any privileges
    
    Impact:
    - Full system compromise
    - Admin account takeover
    - PHI data breach
    - HIPAA violations
    
    Attack Scenarios:
    1. Forge admin token (organization_role='owner')
    2. Impersonate any user
    3. Create long-lived tokens (10+ years)
    4. Forge refresh tokens for persistent access
    
    Remediation:
    1. Remove default secret
    2. Require JWT_SECRET_KEY env var
    3. Validate secret strength at startup
    4. Implement secret rotation
    5. Add comprehensive tests
    
    Tests in this file:
    - test_default_secret_is_predictable
    - test_attacker_can_forge_admin_token
    - test_attacker_can_impersonate_any_user
    - test_attacker_can_create_long_lived_tokens
    - test_attacker_can_forge_refresh_token
    - test_no_validation_of_secret_strength
    - test_no_startup_validation_for_production
    - test_no_secret_rotation_mechanism
    - test_legitimate_token_still_works
    - test_token_type_validation_works
    """
    
    print(summary)
    assert True, "Bug #33 vulnerability documented"

