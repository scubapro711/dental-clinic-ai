"""
Security Headers Middleware

Adds comprehensive security headers to all HTTP responses.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    Headers added:
    - Content-Security-Policy
    - Strict-Transport-Security
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # Content Security Policy
        self.csp = self._build_csp()
    
    def _build_csp(self) -> str:
        """Build Content Security Policy"""
        directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # TODO: Remove unsafe-* in production
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests",
        ]
        
        # Add connect-src with API URL if available
        if hasattr(settings, 'API_URL') and settings.API_URL:
            api_url = settings.API_URL
            wss_url = api_url.replace('https://', '').replace('http://', '')
            directives.insert(5, f"connect-src 'self' {api_url} wss://{wss_url}")
        else:
            directives.insert(5, "connect-src 'self'")
        
        return "; ".join(directives) + ";"
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)
        
        # Content Security Policy
        if not response.headers.get("Content-Security-Policy"):
            response.headers["Content-Security-Policy"] = self.csp
        
        # Strict Transport Security (HSTS)
        # Only add if using HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # X-Frame-Options
        # Prevents clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options
        # Prevents MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection
        # Enable browser XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy (formerly Feature-Policy)
        # Disable unnecessary browser features
        permissions = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "speaker=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)
        
        # Remove server header to avoid information disclosure
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Add rate limit headers if available
        if hasattr(request.state, "rate_limit"):
            rl = request.state.rate_limit
            response.headers["X-RateLimit-Limit"] = str(rl["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rl["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rl["reset"])
        
        return response
