"""
Bug #34: JWT Configuration Inconsistency - Reproduction Tests

These tests demonstrate that jwt_utils.py ignores configuration from config.py
and uses hardcoded values instead.

Severity: Medium (CVSS 5.3)
Category: Configuration Management & Session Security
HIPAA Impact: §164.312(a)(2)(iii) - Session Timeout
"""
import pytest
from datetime import datetime, timezone
from app.core.config import Settings
from app.core.jwt_utils import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    verify_token
)


class TestBug34ConfigurationMismatch:
    """Test suite demonstrating JWT configuration inconsistency."""
    
    def test_config_defines_token_lifetimes(self):
        """
        Test that config.py defines token lifetime settings.
        
        This verifies that the configuration exists and has specific values.
        """
        settings = Settings()
        
        assert hasattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES'), \
            "Settings should have ACCESS_TOKEN_EXPIRE_MINUTES"
        
        assert hasattr(settings, 'REFRESH_TOKEN_EXPIRE_DAYS'), \
            "Settings should have REFRESH_TOKEN_EXPIRE_DAYS"
        
        # Default values from config.py
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30, \
            "Default access token lifetime should be 30 minutes"
        
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7, \
            "Default refresh token lifetime should be 7 days"
    
    def test_jwt_utils_has_different_values(self):
        """
        Test that jwt_utils.py has different hardcoded values.
        
        VULNERABILITY: jwt_utils.py doesn't use config.py values!
        """
        settings = Settings()
        
        # jwt_utils.py has hardcoded values
        assert JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 60, \
            "jwt_utils uses 60 minutes (hardcoded)"
        
        assert JWT_REFRESH_TOKEN_EXPIRE_DAYS == 30, \
            "jwt_utils uses 30 days (hardcoded)"
        
        # They don't match!
        if JWT_ACCESS_TOKEN_EXPIRE_MINUTES != settings.ACCESS_TOKEN_EXPIRE_MINUTES:
            pytest.fail(
                f"CONFIGURATION MISMATCH: "
                f"config.py says {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes, "
                f"but jwt_utils.py uses {JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes!"
            )
    
    def test_access_token_lifetime_mismatch(self):
        """
        Test that access tokens have longer lifetime than configured.
        
        VULNERABILITY: Tokens live 2x longer than intended!
        """
        settings = Settings()
        
        # Create access token
        token = create_access_token(subject='test_user')
        
        # Verify and check expiration
        token_data = verify_token(token)
        
        assert token_data is not None, "Token should be valid"
        
        # Calculate actual lifetime
        iat = token_data.iat
        exp = token_data.exp
        actual_lifetime_seconds = exp - iat
        actual_lifetime_minutes = actual_lifetime_seconds / 60
        
        # Expected lifetime from config
        expected_lifetime_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
        # Actual lifetime from jwt_utils
        hardcoded_lifetime_minutes = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        
        # Check if token uses hardcoded value instead of config
        assert abs(actual_lifetime_minutes - hardcoded_lifetime_minutes) < 1, \
            f"Token uses hardcoded value ({hardcoded_lifetime_minutes} min)"
        
        # This proves the bug
        if abs(actual_lifetime_minutes - expected_lifetime_minutes) > 1:
            pytest.fail(
                f"CONFIGURATION IGNORED: "
                f"Token lifetime is {actual_lifetime_minutes:.0f} minutes, "
                f"but config says {expected_lifetime_minutes} minutes!"
            )
    
    def test_refresh_token_lifetime_mismatch(self):
        """
        Test that refresh tokens have longer lifetime than configured.
        
        VULNERABILITY: Refresh tokens live 4.3x longer than intended!
        """
        settings = Settings()
        
        # Create refresh token
        token = create_refresh_token(subject='test_user')
        
        # Verify and check expiration
        token_data = verify_token(token, token_type='refresh')
        
        assert token_data is not None, "Token should be valid"
        
        # Calculate actual lifetime
        iat = token_data.iat
        exp = token_data.exp
        actual_lifetime_seconds = exp - iat
        actual_lifetime_days = actual_lifetime_seconds / (60 * 60 * 24)
        
        # Expected lifetime from config
        expected_lifetime_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        
        # Actual lifetime from jwt_utils
        hardcoded_lifetime_days = JWT_REFRESH_TOKEN_EXPIRE_DAYS
        
        # Check if token uses hardcoded value instead of config
        assert abs(actual_lifetime_days - hardcoded_lifetime_days) < 1, \
            f"Token uses hardcoded value ({hardcoded_lifetime_days} days)"
        
        # This proves the bug
        if abs(actual_lifetime_days - expected_lifetime_days) > 1:
            pytest.fail(
                f"CONFIGURATION IGNORED: "
                f"Token lifetime is {actual_lifetime_days:.0f} days, "
                f"but config says {expected_lifetime_days} days!"
            )
    
    def test_configuration_change_has_no_effect(self):
        """
        Test that changing configuration has no effect.
        
        VULNERABILITY: Configuration is completely ignored!
        """
        # This test documents the issue
        # In a real scenario, you would:
        # 1. Change ACCESS_TOKEN_EXPIRE_MINUTES in config
        # 2. Restart application
        # 3. Create token
        # 4. Verify token still uses old hardcoded value
        
        settings = Settings()
        
        # Simulate configuration change (via environment variable)
        import os
        original_value = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
        
        try:
            # Set new value
            os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '15'
            
            # Reload settings
            new_settings = Settings()
            assert new_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15, \
                "Configuration should reflect new value"
            
            # Create token
            token = create_access_token(subject='test_user')
            token_data = verify_token(token)
            
            # Check actual lifetime
            actual_lifetime_minutes = (token_data.exp - token_data.iat) / 60
            
            # Token should use new config value (15 minutes)
            # But it doesn't! It still uses hardcoded 60 minutes
            if abs(actual_lifetime_minutes - 60) < 1:
                pytest.fail(
                    f"CONFIGURATION IGNORED: "
                    f"Changed config to 15 minutes, but token still uses 60 minutes!"
                )
        
        finally:
            # Restore original value
            if original_value:
                os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = original_value
            else:
                os.environ.pop('ACCESS_TOKEN_EXPIRE_MINUTES', None)
    
    def test_security_risk_extended_session_window(self):
        """
        Test that extended token lifetime increases security risk.
        
        SECURITY IMPACT: Stolen tokens valid for 2x longer than intended.
        """
        settings = Settings()
        
        # Expected session window (from config)
        expected_window_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # 30
        
        # Actual session window (from jwt_utils)
        actual_window_minutes = JWT_ACCESS_TOKEN_EXPIRE_MINUTES  # 60
        
        # Calculate risk increase
        risk_multiplier = actual_window_minutes / expected_window_minutes
        
        assert risk_multiplier > 1, \
            f"Token lifetime is {risk_multiplier}x longer than configured"
        
        if risk_multiplier >= 2:
            pytest.fail(
                f"SECURITY RISK: "
                f"Stolen tokens valid for {risk_multiplier}x longer than intended! "
                f"({actual_window_minutes} min vs {expected_window_minutes} min)"
            )
    
    def test_hipaa_compliance_concern(self):
        """
        Test HIPAA automatic logoff requirement.
        
        HIPAA §164.312(a)(2)(iii): Implement automatic logoff after 
        predetermined time of inactivity.
        
        COMPLIANCE ISSUE: Session timeout is 2x longer than configured.
        """
        settings = Settings()
        
        # HIPAA requires automatic logoff
        # Organization configured 30 minutes
        configured_timeout = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
        # But actual timeout is 60 minutes
        actual_timeout = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        
        # This violates HIPAA if organization policy says 30 minutes
        if actual_timeout > configured_timeout:
            pytest.fail(
                f"HIPAA COMPLIANCE CONCERN: "
                f"Session timeout is {actual_timeout} minutes, "
                f"but organization policy (config) says {configured_timeout} minutes. "
                f"This violates §164.312(a)(2)(iii) - Automatic Logoff."
            )


class TestBug34ConfigurationSystem:
    """Test configuration system usage."""
    
    def test_jwt_utils_does_not_import_settings(self):
        """
        Test that jwt_utils.py doesn't import Settings.
        
        This is the root cause of the bug.
        """
        import app.core.jwt_utils as jwt_utils_module
        import inspect
        
        source = inspect.getsource(jwt_utils_module)
        
        # Check if Settings is imported
        has_settings_import = (
            'from app.core.config import Settings' in source or
            'from .config import Settings' in source or
            'import app.core.config' in source
        )
        
        if not has_settings_import:
            pytest.fail(
                "ROOT CAUSE: jwt_utils.py doesn't import Settings from config.py! "
                "This is why configuration is ignored."
            )
    
    def test_jwt_utils_uses_hardcoded_constants(self):
        """
        Test that jwt_utils.py uses hardcoded constants.
        
        This is the symptom of the bug.
        """
        import app.core.jwt_utils as jwt_utils_module
        import inspect
        
        source = inspect.getsource(jwt_utils_module)
        
        # Check for hardcoded values
        has_hardcoded_access = 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60' in source
        has_hardcoded_refresh = 'JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30' in source
        
        if has_hardcoded_access or has_hardcoded_refresh:
            pytest.fail(
                "SYMPTOM: jwt_utils.py has hardcoded token lifetime values! "
                "Should use Settings from config.py instead."
            )
    
    def test_configuration_values_are_different(self):
        """
        Test that config.py and jwt_utils.py have different values.
        
        This proves the inconsistency.
        """
        settings = Settings()
        
        discrepancies = []
        
        if settings.ACCESS_TOKEN_EXPIRE_MINUTES != JWT_ACCESS_TOKEN_EXPIRE_MINUTES:
            discrepancies.append(
                f"ACCESS_TOKEN_EXPIRE_MINUTES: "
                f"config.py={settings.ACCESS_TOKEN_EXPIRE_MINUTES}, "
                f"jwt_utils.py={JWT_ACCESS_TOKEN_EXPIRE_MINUTES}"
            )
        
        if settings.REFRESH_TOKEN_EXPIRE_DAYS != JWT_REFRESH_TOKEN_EXPIRE_DAYS:
            discrepancies.append(
                f"REFRESH_TOKEN_EXPIRE_DAYS: "
                f"config.py={settings.REFRESH_TOKEN_EXPIRE_DAYS}, "
                f"jwt_utils.py={JWT_REFRESH_TOKEN_EXPIRE_DAYS}"
            )
        
        if discrepancies:
            pytest.fail(
                "CONFIGURATION INCONSISTENCY:\n" + "\n".join(discrepancies)
            )


# Test execution summary
def test_bug34_summary():
    """
    Summary of Bug #34 vulnerability.
    
    This test always passes but documents the issue.
    """
    summary = """
    BUG #34: JWT CONFIGURATION INCONSISTENCY
    
    Severity: Medium (CVSS 5.3)
    
    Problem:
    - config.py defines token lifetimes (30 min, 7 days)
    - jwt_utils.py uses hardcoded values (60 min, 30 days)
    - jwt_utils.py doesn't import Settings from config.py
    - Configuration is completely ignored
    
    Impact:
    - Access tokens live 2x longer than configured (60 vs 30 min)
    - Refresh tokens live 4.3x longer than configured (30 vs 7 days)
    - Configuration changes have no effect
    - Security risk: Extended window for stolen tokens
    - HIPAA concern: Session timeout not properly enforced
    
    Root Cause:
    - jwt_utils.py doesn't import Settings
    - Uses hardcoded constants instead
    - No validation that configuration is used
    
    Remediation:
    1. Make jwt_utils.py import and use Settings
    2. Remove hardcoded constants
    3. Add tests for configuration usage
    4. Validate configuration at startup
    
    Tests in this file:
    - test_config_defines_token_lifetimes
    - test_jwt_utils_has_different_values
    - test_access_token_lifetime_mismatch
    - test_refresh_token_lifetime_mismatch
    - test_configuration_change_has_no_effect
    - test_security_risk_extended_session_window
    - test_hipaa_compliance_concern
    - test_jwt_utils_does_not_import_settings
    - test_jwt_utils_uses_hardcoded_constants
    - test_configuration_values_are_different
    """
    
    print(summary)
    assert True, "Bug #34 vulnerability documented"

