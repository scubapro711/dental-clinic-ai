"""
HIPAA Compliance Middleware

Automatically enforces HIPAA requirements:
- Logs all PHI access
- Monitors suspicious activities
- Enforces access controls
- Tracks session timeouts
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from typing import Optional
import re

from app.core.audit_log import log_audit, AuditAction
from app.core.database import get_db
from app.models.user import User
from app.services.hipaa_metrics import hipaa_metrics

# PHI-sensitive endpoints (regex patterns)
PHI_ENDPOINTS = [
    r"/api/v1/patients/.*",
    r"/api/v1/appointments/.*",
    r"/api/v1/treatments/.*",
    r"/api/v1/medical-records/.*",
    r"/api/v1/prescriptions/.*",
]

# Business hours (for suspicious activity detection)
BUSINESS_HOURS_START = 7  # 7 AM
BUSINESS_HOURS_END = 20   # 8 PM

# Rate limiting for PHI access
MAX_PHI_REQUESTS_PER_MINUTE = 60
MAX_PHI_REQUESTS_PER_HOUR = 500


class HIPAAMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HIPAA compliance requirements.
    
    Features:
    - Automatic PHI access logging
    - Suspicious activity detection
    - Rate limiting for PHI endpoints
    - Session timeout enforcement
    - Security header injection
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = datetime.utcnow()
        
        # Check if endpoint handles PHI
        is_phi_endpoint = self._is_phi_endpoint(request.url.path)
        
        # Get current user (if authenticated)
        user = await self._get_current_user(request)
        
        # Pre-request checks
        if is_phi_endpoint and user:
            # Check rate limiting
            if not await self._check_rate_limit(user, request):
                return Response(
                    content="Rate limit exceeded for PHI access",
                    status_code=429
                )
            
            # Check for suspicious activity
            if await self._is_suspicious_activity(user, request):
                await self._alert_security_team(user, request, "SUSPICIOUS_ACTIVITY")
        
        # Process request
        response = await call_next(request)
        
        # Post-request logging
        if is_phi_endpoint and user:
            # Log PHI access
            await self._log_phi_access(
                user=user,
                request=request,
                response=response,
                duration=(datetime.utcnow() - start_time).total_seconds()
            )
        
        # Add security headers
        response = self._add_security_headers(response)
        
        return response
    
    def _is_phi_endpoint(self, path: str) -> bool:
        """Check if endpoint handles PHI"""
        for pattern in PHI_ENDPOINTS:
            if re.match(pattern, path):
                return True
        return False
    
    async def _get_current_user(self, request: Request) -> Optional[User]:
        """Extract current user from request"""
        # Get from request state (set by auth dependency)
        return getattr(request.state, "user", None)
    
    async def _check_rate_limit(self, user: User, request: Request) -> bool:
        """Check if user has exceeded PHI access rate limits"""
        from app.core.cache import get_cache
        
        cache = get_cache()
        
        # Check per-minute limit
        minute_key = f"phi_access:{user.id}:minute:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        minute_count = await cache.get(minute_key) or 0
        
        if int(minute_count) >= MAX_PHI_REQUESTS_PER_MINUTE:
            return False
        
        # Check per-hour limit
        hour_key = f"phi_access:{user.id}:hour:{datetime.utcnow().strftime('%Y%m%d%H')}"
        hour_count = await cache.get(hour_key) or 0
        
        if int(hour_count) >= MAX_PHI_REQUESTS_PER_HOUR:
            return False
        
        # Increment counters
        await cache.incr(minute_key)
        await cache.expire(minute_key, 60)  # Expire after 1 minute
        
        await cache.incr(hour_key)
        await cache.expire(hour_key, 3600)  # Expire after 1 hour
        
        return True
    
    async def _is_suspicious_activity(self, user: User, request: Request) -> bool:
        """Detect suspicious PHI access patterns"""
        suspicions = []
        
        # Check 1: Access outside business hours
        current_hour = datetime.utcnow().hour
        if not (BUSINESS_HOURS_START <= current_hour <= BUSINESS_HOURS_END):
            suspicions.append("ACCESS_OUTSIDE_BUSINESS_HOURS")
        
        # Check 2: Bulk data export
        if "export" in request.url.path.lower():
            suspicions.append("BULK_EXPORT")
        
        # Check 3: Rapid sequential access
        from app.core.cache import get_cache
        cache = get_cache()
        
        recent_key = f"recent_phi_access:{user.id}"
        recent_accesses = await cache.lrange(recent_key, 0, -1)
        
        if len(recent_accesses) > 10:  # More than 10 in last minute
            suspicions.append("RAPID_SEQUENTIAL_ACCESS")
        
        # Check 4: Access to many different patients
        if len(set(recent_accesses)) > 20:  # More than 20 different patients
            suspicions.append("ACCESS_TO_MANY_PATIENTS")
        
        # Check 5: Unusual IP address
        user_ips = await self._get_user_typical_ips(user)
        if request.client.host not in user_ips:
            suspicions.append("UNUSUAL_IP_ADDRESS")
        
        # Record this access
        await cache.lpush(recent_key, request.url.path)
        await cache.ltrim(recent_key, 0, 99)  # Keep last 100
        await cache.expire(recent_key, 3600)  # Expire after 1 hour
        
        return len(suspicions) > 0
    
    async def _get_user_typical_ips(self, user: User) -> list[str]:
        """Get user's typical IP addresses from audit log"""
        from app.core.database import get_db
        from app.models.audit_log import AuditLog
        
        db = next(get_db())
        
        # Get IPs from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        ips = db.query(AuditLog.ip_address).filter(
            AuditLog.user_id == user.id,
            AuditLog.created_at >= thirty_days_ago
        ).distinct().all()
        
        return [ip[0] for ip in ips]
    
    async def _log_phi_access(
        self,
        user: User,
        request: Request,
        response: Response,
        duration: float
    ):
        """Log PHI access to audit trail"""
        # Extract resource info from path
        resource_type, resource_id = self._extract_resource_info(request.url.path)
        
        # Determine action from HTTP method
        action_map = {
            "GET": AuditAction.READ,
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE,
        }
        action = action_map.get(request.method, AuditAction.ACCESS)
        
        # Log to audit trail
        await log_audit(
            user_id=user.id,
            organization_id=user.organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=(200 <= response.status_code < 300),
            duration_ms=int(duration * 1000),
            metadata={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            }
        )
        
        # Export metrics to GCP Cloud Monitoring
        action_type_map = {
            AuditAction.READ: "read",
            AuditAction.CREATE: "write",
            AuditAction.UPDATE: "write",
            AuditAction.DELETE: "delete",
            AuditAction.ACCESS: "read",
        }
        
        hipaa_metrics.record_phi_access(
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            action_type=action_type_map.get(action, "other"),
            resource_type=resource_type.lower(),
            authorized=(200 <= response.status_code < 300)
        )
        
        hipaa_metrics.record_audit_log_entry(
            log_type=action_type_map.get(action, "other"),
            severity="info" if (200 <= response.status_code < 300) else "error",
            user_id=str(user.id),
            organization_id=str(user.organization_id)
        )
    
    def _extract_resource_info(self, path: str) -> tuple[str, Optional[int]]:
        """Extract resource type and ID from path"""
        # Example: /api/v1/patients/123 -> ("Patient", 123)
        parts = path.split("/")
        
        if len(parts) >= 4:
            resource_type = parts[3].rstrip("s").capitalize()  # "patients" -> "Patient"
            resource_id = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else None
            return resource_type, resource_id
        
        return "Unknown", None
    
    async def _alert_security_team(self, user: User, request: Request, alert_type: str):
        """Send alert to security team"""
        from app.core.notifications import send_security_alert
        
        await send_security_alert(
            alert_type=alert_type,
            user_id=user.id,
            user_email=user.email,
            ip_address=request.client.host,
            path=request.url.path,
            timestamp=datetime.utcnow(),
            details={
                "user_agent": request.headers.get("user-agent", ""),
                "method": request.method,
            }
        )
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        # HSTS - Force HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' wss: https:;"
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        
        return response


# Session timeout enforcement
class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    """
    Enforce HIPAA-compliant session timeouts.
    
    Requirements:
    - Automatic logoff after 30 minutes of inactivity
    - Warning before timeout
    """
    
    SESSION_TIMEOUT_MINUTES = 30
    WARNING_BEFORE_TIMEOUT_MINUTES = 5
    
    async def dispatch(self, request: Request, call_next):
        user = await self._get_current_user(request)
        
        if user:
            # Check last activity
            last_activity = await self._get_last_activity(user)
            
            if last_activity:
                inactive_minutes = (datetime.utcnow() - last_activity).total_seconds() / 60
                
                # Session expired
                if inactive_minutes >= self.SESSION_TIMEOUT_MINUTES:
                    return Response(
                        content="Session expired due to inactivity",
                        status_code=401,
                        headers={"X-Session-Expired": "true"}
                    )
                
                # Warning threshold
                if inactive_minutes >= (self.SESSION_TIMEOUT_MINUTES - self.WARNING_BEFORE_TIMEOUT_MINUTES):
                    # Add warning header
                    response = await call_next(request)
                    response.headers["X-Session-Warning"] = "Session will expire soon"
                    response.headers["X-Session-Expires-In"] = str(
                        int((self.SESSION_TIMEOUT_MINUTES - inactive_minutes) * 60)
                    )
                    await self._update_last_activity(user)
                    return response
            
            # Update last activity
            await self._update_last_activity(user)
        
        return await call_next(request)
    
    async def _get_current_user(self, request: Request) -> Optional[User]:
        """Extract current user from request"""
        return getattr(request.state, "user", None)
    
    async def _get_last_activity(self, user: User) -> Optional[datetime]:
        """Get user's last activity timestamp"""
        from app.core.cache import get_cache
        
        cache = get_cache()
        timestamp = await cache.get(f"last_activity:{user.id}")
        
        if timestamp:
            return datetime.fromisoformat(timestamp)
        
        return None
    
    async def _update_last_activity(self, user: User):
        """Update user's last activity timestamp"""
        from app.core.cache import get_cache
        
        cache = get_cache()
        await cache.set(
            f"last_activity:{user.id}",
            datetime.utcnow().isoformat(),
            ex=self.SESSION_TIMEOUT_MINUTES * 60
        )
