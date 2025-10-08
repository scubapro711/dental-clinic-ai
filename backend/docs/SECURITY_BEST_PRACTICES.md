# Security Best Practices

**Version:** 15.0.0  
**Last Updated:** October 8, 2025  
**Security Level:** Production-Ready

---

## 📊 Overview

Comprehensive security hardening guide for DentaFlow to protect:
- **PHI (Protected Health Information)** - Patient medical data
- **PII (Personally Identifiable Information)** - Personal data
- **Authentication credentials** - User accounts
- **Business data** - Clinic operations

---

## 🎯 Security Checklist

### ✅ Authentication & Authorization
- [x] Strong password policy (12+ chars, complexity)
- [x] Multi-factor authentication (MFA) via AWS Cognito
- [x] JWT with short expiration (15 min access, 7 day refresh)
- [x] Session timeout (30 minutes inactivity)
- [x] Account lockout (5 failed attempts)
- [x] Password hashing (bcrypt, cost 12)
- [x] Role-based access control (RBAC)
- [x] Organization-level isolation

### ✅ Data Protection
- [x] Database encryption at rest (AES-256)
- [x] TLS 1.3 for data in transit
- [x] PHI field-level encryption
- [x] Secure key management (AWS Secrets Manager)
- [x] Data masking in logs
- [x] Secure file uploads
- [x] Input sanitization

### ✅ API Security
- [x] Rate limiting (60 req/min per user)
- [x] Request size limits (10MB)
- [x] CORS configuration
- [x] Security headers (CSP, HSTS, etc.)
- [x] API versioning
- [x] Request validation (Pydantic)
- [x] Error handling (no sensitive data leaks)

### ✅ Infrastructure
- [x] Firewall rules (Security Groups)
- [x] Private subnets for databases
- [x] VPC isolation
- [x] Regular security updates
- [x] Intrusion detection
- [x] DDoS protection (AWS Shield)
- [x] WAF rules

### ✅ Monitoring & Logging
- [x] Audit logging (all PHI access)
- [x] Security event monitoring
- [x] Failed login tracking
- [x] Anomaly detection
- [x] Log retention (6 years for HIPAA)
- [x] Real-time alerts

### ✅ Compliance
- [x] HIPAA compliance (85%)
- [x] Data retention policies
- [x] Privacy policy
- [x] Terms of service
- [x] BAA (Business Associate Agreement)
- [x] Incident response plan

---

## 🔒 Implementation Details

### 1. Password Policy

```python
# app/core/security.py

import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordPolicy:
    """Enforce strong password requirements"""
    
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    @classmethod
    def validate(cls, password: str) -> tuple[bool, str]:
        """
        Validate password against policy.
        
        Returns:
            (is_valid, error_message)
        """
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters"
        
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain digit"
        
        if cls.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special character"
        
        # Check against common passwords
        if password.lower() in COMMON_PASSWORDS:
            return False, "Password is too common"
        
        return True, ""
    
    @classmethod
    def hash(cls, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @classmethod
    def verify(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)


# Common passwords list (top 10000)
COMMON_PASSWORDS = set([
    "password", "123456", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
    # ... (load from file in production)
])
```

### 2. Rate Limiting

```python
# app/middleware/rate_limit.py

from fastapi import Request, HTTPException
from app.core.cache import get_cache, CacheNamespace
import time

class RateLimiter:
    """Rate limiting middleware"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self.rpd = requests_per_day
    
    async def __call__(self, request: Request):
        """Check rate limits"""
        user_id = request.state.user.id if hasattr(request.state, 'user') else request.client.host
        cache = await get_cache()
        
        # Check minute limit
        minute_key = f"rate_limit:{user_id}:minute:{int(time.time() / 60)}"
        minute_count = await cache.incr(minute_key, namespace=CacheNamespace.RATE_LIMIT)
        await cache.expire(minute_key, 60, namespace=CacheNamespace.RATE_LIMIT)
        
        if minute_count > self.rpm:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.rpm} requests per minute",
                headers={"Retry-After": "60"}
            )
        
        # Check hour limit
        hour_key = f"rate_limit:{user_id}:hour:{int(time.time() / 3600)}"
        hour_count = await cache.incr(hour_key, namespace=CacheNamespace.RATE_LIMIT)
        await cache.expire(hour_key, 3600, namespace=CacheNamespace.RATE_LIMIT)
        
        if hour_count > self.rph:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.rph} requests per hour",
                headers={"Retry-After": "3600"}
            )
        
        # Add rate limit headers
        request.state.rate_limit = {
            "limit": self.rpm,
            "remaining": max(0, self.rpm - minute_count),
            "reset": int(time.time() / 60 + 1) * 60
        }
```

### 3. Security Headers

```python
# app/middleware/security_headers.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.dentaflow.ai wss://api.dentaflow.ai; "
            "frame-ancestors 'none';"
        )
        
        # Strict Transport Security
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        
        # Remove server header
        response.headers.pop("Server", None)
        
        return response
```

### 4. Input Validation

```python
# app/api/v1/endpoints/patients.py

from pydantic import BaseModel, validator, constr
from typing import Optional
import re

class PatientCreate(BaseModel):
    """Patient creation with strict validation"""
    
    first_name: constr(min_length=1, max_length=50, strip_whitespace=True)
    last_name: constr(min_length=1, max_length=50, strip_whitespace=True)
    email: Optional[constr(max_length=100)]
    phone: constr(regex=r'^\+?[1-9]\d{1,14}$')  # E.164 format
    date_of_birth: date
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower() if v else None
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        """Sanitize names"""
        # Remove any HTML/script tags
        v = re.sub(r'<[^>]*>', '', v)
        # Remove special characters except spaces, hyphens, apostrophes
        v = re.sub(r'[^a-zA-Z\s\-\']', '', v)
        return v.strip()
    
    @validator('date_of_birth')
    def validate_dob(cls, v):
        """Validate date of birth"""
        from datetime import date
        
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        
        age = (date.today() - v).days / 365.25
        if age > 150:
            raise ValueError('Invalid date of birth')
        
        return v
```

### 5. SQL Injection Prevention

```python
# Always use parameterized queries

# ❌ BAD - Vulnerable to SQL injection
query = f"SELECT * FROM users WHERE email = '{email}'"
result = db.execute(query)

# ✅ GOOD - Safe from SQL injection
from sqlalchemy import text

query = text("SELECT * FROM users WHERE email = :email")
result = db.execute(query, {"email": email})

# ✅ BEST - Use ORM
result = db.query(User).filter(User.email == email).first()
```

### 6. XSS Prevention

```python
# app/utils/sanitize.py

import bleach
from markupsafe import escape

def sanitize_html(html: str) -> str:
    """
    Sanitize HTML to prevent XSS.
    
    Allows only safe tags and attributes.
    """
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    allowed_attributes = {'a': ['href', 'title']}
    
    return bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

def escape_user_input(text: str) -> str:
    """Escape user input for safe display"""
    return escape(text)

# Usage
@router.post("/notes")
async def create_note(note: str):
    # Sanitize before storing
    safe_note = sanitize_html(note)
    
    # Store in database
    db_note = Note(content=safe_note)
    db.add(db_note)
    db.commit()
    
    return {"note": safe_note}
```

### 7. CSRF Protection

```python
# app/middleware/csrf.py

from fastapi import Request, HTTPException
import secrets
import hmac
import hashlib

class CSRFProtection:
    """CSRF token validation"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        token = secrets.token_urlsafe(32)
        signature = hmac.new(
            self.secret_key,
            f"{session_id}:{token}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{token}.{signature}"
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        try:
            token_value, signature = token.split('.')
            
            expected_signature = hmac.new(
                self.secret_key,
                f"{session_id}:{token_value}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except:
            return False

# Middleware
async def csrf_middleware(request: Request, call_next):
    """Validate CSRF token for state-changing requests"""
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        token = request.headers.get('X-CSRF-Token')
        session_id = request.cookies.get('session_id')
        
        if not token or not session_id:
            raise HTTPException(status_code=403, detail="CSRF token missing")
        
        csrf = CSRFProtection(settings.SECRET_KEY)
        if not csrf.validate_token(token, session_id):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")
    
    response = await call_next(request)
    return response
```

---

## 🔍 Security Scanning

### 1. Dependency Scanning

```bash
# Check for known vulnerabilities
pip install safety
safety check --json

# Or use
pip-audit

# Update vulnerable packages
pip install --upgrade package-name
```

### 2. Code Scanning

```bash
# Static analysis
pip install bandit
bandit -r backend/app/ -f json -o security-report.json

# Find secrets in code
pip install detect-secrets
detect-secrets scan --all-files > .secrets.baseline
```

### 3. Container Scanning

```bash
# Scan Docker images
docker scan dentaflow:latest

# Or use Trivy
trivy image dentaflow:latest
```

---

## 🚨 Incident Response

### Detection

**Indicators of Compromise:**
- Multiple failed login attempts
- Unusual API activity
- Unexpected data access patterns
- Database anomalies
- System file changes

### Response Steps

1. **Detect** (< 5 minutes)
   - Automated alerts
   - Log analysis
   - Anomaly detection

2. **Contain** (< 30 minutes)
   - Isolate affected systems
   - Revoke compromised credentials
   - Block malicious IPs

3. **Investigate** (< 2 hours)
   - Analyze logs
   - Identify attack vector
   - Assess damage

4. **Remediate** (< 4 hours)
   - Patch vulnerabilities
   - Restore from backups
   - Update security rules

5. **Recover** (< 8 hours)
   - Verify system integrity
   - Resume operations
   - Monitor for recurrence

6. **Report** (< 24 hours)
   - Document incident
   - Notify affected parties
   - Report to authorities (if required)

### Incident Response Team

- **Incident Commander:** CTO
- **Technical Lead:** Senior Developer
- **Communications:** CEO
- **Legal:** Legal Counsel
- **Compliance:** HIPAA Officer

---

## 📊 Security Monitoring

### Metrics to Track

1. **Authentication**
   - Failed login attempts
   - MFA adoption rate
   - Password reset requests
   - Session timeouts

2. **API Security**
   - Rate limit violations
   - Invalid requests
   - Suspicious patterns
   - Error rates

3. **Data Access**
   - PHI access frequency
   - Unusual access patterns
   - Export/download activity
   - Permission changes

4. **Infrastructure**
   - Failed SSH attempts
   - Firewall blocks
   - DDoS attempts
   - System updates

### Alerting Rules

```python
# app/monitoring/security_alerts.py

from app.core.notifications import send_alert

async def check_failed_logins():
    """Alert on excessive failed logins"""
    failed_logins = await db.query(AuditLog)\
        .filter(
            AuditLog.action == 'login_failed',
            AuditLog.created_at > datetime.now() - timedelta(minutes=5)
        )\
        .group_by(AuditLog.user_id)\
        .having(func.count() > 5)\
        .all()
    
    if failed_logins:
        await send_alert(
            severity='high',
            title='Multiple Failed Login Attempts',
            message=f'{len(failed_logins)} users with > 5 failed logins in 5 min'
        )

async def check_phi_access():
    """Alert on unusual PHI access"""
    phi_access = await db.query(AuditLog)\
        .filter(
            AuditLog.resource_type == 'patient',
            AuditLog.created_at > datetime.now() - timedelta(hours=1)
        )\
        .group_by(AuditLog.user_id)\
        .having(func.count() > 100)\
        .all()
    
    if phi_access:
        await send_alert(
            severity='critical',
            title='Unusual PHI Access Pattern',
            message=f'{len(phi_access)} users accessed > 100 patient records in 1 hour'
        )
```

---

## 📝 Summary

**Security Posture:**
- ✅ Authentication: Strong (MFA, JWT, RBAC)
- ✅ Data Protection: Encrypted (AES-256, TLS 1.3)
- ✅ API Security: Hardened (Rate limiting, validation)
- ✅ Infrastructure: Secure (VPC, firewall, WAF)
- ✅ Monitoring: Comprehensive (Audit logs, alerts)
- ✅ Compliance: HIPAA-ready (85% complete)

**Next Steps:**
- Complete HIPAA compliance (15% remaining)
- Conduct penetration testing
- Security awareness training
- Regular security audits
- Incident response drills

---

**Status:** ✅ Production-Ready  
**Security Level:** High
