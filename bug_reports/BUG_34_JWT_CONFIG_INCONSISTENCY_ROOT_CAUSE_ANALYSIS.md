# Bug #34: JWT Configuration Inconsistency - Root Cause Analysis

**Date:** 2025-01-25  
**Severity:** Medium (CVSS 5.3)  
**Category:** Configuration Management & Session Security  
**HIPAA Impact:** §164.312(a)(2)(iii) - Session Timeout

---

## Executive Summary

The application has **two conflicting configurations** for JWT token expiration times. The `config.py` module defines token lifetimes (30 minutes for access tokens, 7 days for refresh tokens), but `jwt_utils.py` **ignores these settings** and uses hardcoded values (60 minutes for access tokens, 30 days for refresh tokens).

**Impact:**
- ⚠️ **Configuration ignored** - Changes to `config.py` have no effect
- ⚠️ **Inconsistent behavior** - Tokens live longer than intended
- ⚠️ **Security risk** - Access tokens valid for 2x intended duration
- ⚠️ **HIPAA concern** - Session timeout not properly enforced

---

## Problem Statement

### Configuration Mismatch

**File 1:** `app/core/config.py` (lines 57-58)
```python
class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)  # 30 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)     # 7 days
```

**File 2:** `app/core/jwt_utils.py` (lines 21-22)
```python
# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30    # 30 days
```

**Problem:** `jwt_utils.py` does NOT import or use the settings from `config.py`!

### Actual Token Lifetimes

**Expected (from config.py):**
- Access Token: 30 minutes
- Refresh Token: 7 days

**Actual (from jwt_utils.py):**
- Access Token: 60 minutes (2x longer!)
- Refresh Token: 30 days (4.3x longer!)

---

## Root Cause Analysis

### Why Did This Happen?

1. **Duplicate Configuration**
   - Settings defined in two places
   - No single source of truth
   - No validation that they match

2. **Missing Import**
   - `jwt_utils.py` doesn't import `Settings` from `config.py`
   - Uses hardcoded constants instead
   - Configuration system not utilized

3. **No Configuration Tests**
   - No tests verify configuration is used
   - No tests check for configuration consistency
   - No validation at startup

4. **Legacy Code**
   - `jwt_utils.py` likely created before `config.py`
   - Configuration system added later
   - Migration incomplete

---

## Impact Assessment

### Security Impact

| Aspect | Expected | Actual | Risk |
|--------|----------|--------|------|
| Access Token Lifetime | 30 min | 60 min | Medium |
| Refresh Token Lifetime | 7 days | 30 days | Medium |
| Session Timeout | 30 min | 60 min | Medium |
| Configuration Control | Centralized | Ignored | High |

### HIPAA Compliance

**§164.312(a)(2)(iii) - Automatic Logoff** ⚠️
- **Requirement:** Implement automatic logoff after predetermined time of inactivity
- **Issue:** Session timeout is 2x longer than configured (60 min vs 30 min)
- **Impact:** Users remain authenticated longer than intended

### Business Impact

- **User Experience:** Inconsistent session behavior
- **Security Posture:** Reduced (longer token lifetimes)
- **Configuration Management:** Broken (changes ignored)
- **Compliance:** Potential HIPAA violation

---

## Attack Scenarios

### Scenario 1: Extended Session Hijacking Window

**Without Fix:**
1. User logs in, gets access token (60 min lifetime)
2. Attacker steals token (e.g., via XSS, network sniffing)
3. Attacker has 60 minutes to use stolen token
4. User thinks session expires after 30 minutes (per config)

**With Fix:**
1. User logs in, gets access token (30 min lifetime)
2. Attacker steals token
3. Attacker has only 30 minutes to use stolen token
4. Risk window reduced by 50%

### Scenario 2: Configuration Change Ignored

**Without Fix:**
1. Security team decides to reduce token lifetime to 15 minutes
2. Updates `config.py`: `ACCESS_TOKEN_EXPIRE_MINUTES = 15`
3. Deploys application
4. **Nothing changes!** Tokens still valid for 60 minutes
5. Security team thinks they've improved security, but they haven't

**With Fix:**
1. Security team updates `config.py`
2. Application uses new value
3. Tokens now expire after 15 minutes
4. Configuration works as expected

---

## Technical Details

### Current Implementation

**jwt_utils.py:**
```python
# Hardcoded values (WRONG)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_access_token(...):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Uses hardcoded value
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
```

**config.py:**
```python
# Correct values (IGNORED)
class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
```

### Where Configuration is Used

**Files that import Settings:**
- `app/core/security.py` - Uses `settings.ACCESS_TOKEN_EXPIRE_MINUTES` ✅
- `app/api/v1/endpoints/auth.py` - May use settings ✅

**Files that DON'T import Settings:**
- `app/core/jwt_utils.py` - Uses hardcoded values ❌

**Result:** Inconsistent token lifetimes depending on which module creates the token!

---

## Affected Components

### Direct Impact

1. **JWT Token Creation** - `jwt_utils.py`
   - `create_access_token()` - Uses hardcoded 60 minutes
   - `create_refresh_token()` - Uses hardcoded 30 days

2. **Configuration System** - `config.py`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` - Ignored
   - `REFRESH_TOKEN_EXPIRE_DAYS` - Ignored

### Indirect Impact

1. **Authentication Endpoints** - May create tokens with inconsistent lifetimes
2. **Session Management** - Unpredictable session behavior
3. **Security Monitoring** - Incorrect assumptions about token lifetimes
4. **Compliance Audits** - Configuration doesn't match actual behavior

---

## Detection Methods

### How to Detect

1. **Code Review**
   ```bash
   # Check if jwt_utils imports Settings
   grep -n "from app.core.config import" app/core/jwt_utils.py
   # (Should find nothing - that's the bug!)
   ```

2. **Configuration Test**
   ```python
   # Set environment variable
   os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '15'
   
   # Create token
   token = create_access_token(subject='test')
   
   # Decode and check expiration
   payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
   exp_time = payload['exp'] - payload['iat']
   
   # Should be 15 minutes (900 seconds)
   assert exp_time == 900, f"Expected 900, got {exp_time}"
   # (This test would FAIL - proving the bug)
   ```

3. **Runtime Inspection**
   ```python
   from app.core.config import Settings
   from app.core.jwt_utils import JWT_ACCESS_TOKEN_EXPIRE_MINUTES
   
   settings = Settings()
   
   print(f"Config: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
   print(f"JWT Utils: {JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
   
   # Output:
   # Config: 30 minutes
   # JWT Utils: 60 minutes
   # (Mismatch - that's the bug!)
   ```

---

## Comparison with Best Practices

### Industry Standards

**OWASP Recommendations:**
- Access tokens: 5-15 minutes
- Refresh tokens: 7-30 days
- Configuration: Centralized, environment-specific

**Current Implementation:**
- Access tokens: 60 minutes (too long)
- Refresh tokens: 30 days (acceptable)
- Configuration: Duplicated, inconsistent

### Similar Issues

**CVE-2021-12345 (Example):**
- Application ignored session timeout configuration
- Sessions remained active longer than intended
- Fixed by centralizing configuration

**Lesson:** Always use centralized configuration, never hardcode security-sensitive values

---

## Systemic Issues

### 1. Configuration Management

**Problem:** No single source of truth for configuration

**Evidence:**
- Settings defined in multiple places
- No validation that they match
- No tests for configuration consistency

### 2. Code Organization

**Problem:** Modules don't follow dependency hierarchy

**Evidence:**
- `jwt_utils.py` should depend on `config.py`
- Instead, it duplicates configuration
- No clear module boundaries

### 3. Testing Gap

**Problem:** No tests for configuration usage

**Evidence:**
- No tests verify settings are actually used
- No tests check for configuration consistency
- No integration tests for token lifetimes

### 4. Documentation

**Problem:** Configuration not documented

**Evidence:**
- No documentation explaining which settings are used where
- No deployment guide mentioning configuration
- No examples of how to change token lifetimes

---

## Recommended Immediate Actions

### 1. Fix Configuration Usage (NOW)

```python
# jwt_utils.py
from app.core.config import Settings

settings = Settings()

# Use settings instead of hardcoded values
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
JWT_REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
```

### 2. Add Configuration Tests (ASAP)

```python
def test_jwt_uses_config_settings():
    """Test that jwt_utils uses settings from config."""
    from app.core.config import Settings
    from app.core.jwt_utils import JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    settings = Settings()
    
    assert JWT_ACCESS_TOKEN_EXPIRE_MINUTES == settings.ACCESS_TOKEN_EXPIRE_MINUTES
```

### 3. Validate at Startup (Within 24 hours)

```python
# startup.py
def validate_configuration():
    """Validate configuration consistency at startup."""
    from app.core.config import Settings
    from app.core.jwt_utils import JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    settings = Settings()
    
    if JWT_ACCESS_TOKEN_EXPIRE_MINUTES != settings.ACCESS_TOKEN_EXPIRE_MINUTES:
        raise RuntimeError("JWT configuration mismatch!")
```

### 4. Document Configuration (Within 48 hours)

- Update README with configuration options
- Add deployment guide
- Document token lifetime settings

---

## Long-Term Recommendations

### 1. Centralize Configuration

- Single `Settings` class for all configuration
- No hardcoded values in modules
- Environment-specific overrides

### 2. Configuration Validation

- Startup validation for all critical settings
- Fail-fast if misconfigured
- Clear error messages

### 3. Comprehensive Testing

- Unit tests for configuration usage
- Integration tests for token lifetimes
- End-to-end tests for session management

### 4. Monitoring & Alerting

- Monitor actual token lifetimes in production
- Alert if they don't match configuration
- Dashboard for configuration status

---

## Lessons Learned

### 1. Single Source of Truth

**Lesson:** Configuration should have one authoritative source

**Action:** Always import from `config.py`, never duplicate

### 2. Validate Configuration Usage

**Lesson:** Configuration must be actually used, not just defined

**Action:** Add tests that verify configuration is used

### 3. Fail Fast

**Lesson:** Configuration errors should be caught at startup

**Action:** Validate all critical settings at startup

### 4. Document Configuration

**Lesson:** Developers need to know what configuration exists

**Action:** Maintain up-to-date configuration documentation

---

## Conclusion

Bug #34 (JWT Configuration Inconsistency) is a **medium-severity issue** that causes JWT tokens to have longer lifetimes than configured. This reduces security posture and creates HIPAA compliance concerns.

**Immediate Action Required:**
1. Make `jwt_utils.py` use settings from `config.py`
2. Add tests for configuration usage
3. Validate configuration at startup
4. Update documentation

**Severity:** Medium (CVSS 5.3)  
**Priority:** P1 (High)  
**Remediation:** Within 1 week

---

**Prepared by:** Manus AI Security Analysis  
**Date:** 2025-01-25  
**Next Steps:** Implement fix with comprehensive testing

---

## References

- **OWASP Session Management Cheat Sheet:** https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- **NIST SP 800-63B:** Digital Identity Guidelines (Session Management)
- **HIPAA Security Rule:** §164.312(a)(2)(iii) - Automatic Logoff
- **JWT Best Practices:** https://tools.ietf.org/html/rfc8725

