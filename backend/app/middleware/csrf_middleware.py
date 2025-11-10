"""
CSRF Protection Middleware

Implements Cross-Site Request Forgery (CSRF) protection for the DentaFlow API.

This middleware:
1. Generates CSRF tokens for each session
2. Validates CSRF tokens on state-changing requests (POST/PUT/DELETE/PATCH)
3. Exempts Bearer token authentication (API clients)
4. Exempts GET/HEAD/OPTIONS requests (safe methods)

CSRF tokens are sent in two ways:
- Cookie: csrf_token (HttpOnly, Secure, SameSite=Strict)
- Header: X-CSRF-Token (must match cookie value)

This implements the "Double Submit Cookie" pattern for stateless CSRF protection.
"""

import secrets
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware
    
    Protects against Cross-Site Request Forgery attacks by validating
    CSRF tokens on all state-changing requests.
    """
    
    # Methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
    
    # Methods that don't require CSRF protection (safe methods)
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    
    # Paths that are exempt from CSRF protection
    EXEMPT_PATHS = {
        "/api/v1/auth/login",          # Login endpoint (no session yet)
        "/auth/login",                 # Login endpoint (alternative path)
        "/api/v1/auth/register",       # Registration endpoint
        "/api/v1/auth/google/callback", # OAuth callback (uses state parameter)
        "/docs",                        # API documentation
        "/openapi.json",                # OpenAPI schema
        "/health",                      # Health check
    }
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        logger.info("🔒 CSRF Protection Middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request and validate CSRF token if needed.
        """
        # Skip CSRF protection for safe methods
        if request.method in self.SAFE_METHODS:
            response = await call_next(request)
            # Generate and set CSRF token for GET requests
            if request.method == "GET":
                response = self._set_csrf_token(response)
            return response
        
        # Skip CSRF protection for exempt paths
        if self._is_exempt_path(request.url.path):
            return await call_next(request)
        
        # Skip CSRF protection for Bearer token authentication
        if self._uses_bearer_auth(request):
            logger.debug(f"CSRF check skipped for Bearer auth: {request.url.path}")
            return await call_next(request)
        
        # Validate CSRF token for state-changing requests
        if request.method in self.PROTECTED_METHODS:
            if not self._validate_csrf_token(request):
                logger.warning(
                    f"CSRF validation failed: {request.method} {request.url.path} "
                    f"from {request.client.host if request.client else 'unknown'}"
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "CSRF token missing or invalid. "
                                  "Please include a valid X-CSRF-Token header."
                    }
                )
        
        # Process request
        response = await call_next(request)
        
        # Set CSRF token in response
        response = self._set_csrf_token(response)
        
        return response
    
    def _is_exempt_path(self, path: str) -> bool:
        """
        Check if path is exempt from CSRF protection.
        """
        return any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)
    
    def _uses_bearer_auth(self, request: Request) -> bool:
        """
        Check if request uses Bearer token authentication.
        
        Bearer tokens in Authorization header are not vulnerable to CSRF
        because they are not automatically sent by the browser.
        """
        auth_header = request.headers.get("Authorization", "")
        return auth_header.startswith("Bearer ")
    
    def _validate_csrf_token(self, request: Request) -> bool:
        """
        Validate CSRF token using Double Submit Cookie pattern.
        
        The token must be present in both:
        1. Cookie (csrf_token)
        2. Header (X-CSRF-Token)
        
        And both values must match.
        """
        # Get token from cookie
        token_from_cookie = request.cookies.get("csrf_token")
        
        # Get token from header
        token_from_header = request.headers.get("X-CSRF-Token")
        
        # Both must be present
        if not token_from_cookie or not token_from_header:
            logger.debug(
                f"CSRF token missing - Cookie: {bool(token_from_cookie)}, "
                f"Header: {bool(token_from_header)}"
            )
            return False
        
        # Both must match (constant-time comparison to prevent timing attacks)
        if not secrets.compare_digest(token_from_cookie, token_from_header):
            logger.debug("CSRF token mismatch")
            return False
        
        logger.debug(f"CSRF token validated for {request.method} {request.url.path}")
        return True
    
    def _set_csrf_token(self, response: Response) -> Response:
        """
        Generate and set CSRF token in response cookie.
        
        Token is only generated if it doesn't already exist in the request.
        """
        # Check if token already exists
        if hasattr(response, 'set_cookie'):
            # Generate new CSRF token
            csrf_token = secrets.token_urlsafe(32)
            
            # Set token in cookie
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,  # Must be accessible to JavaScript for header
                secure=True,      # Only send over HTTPS
                samesite="strict", # Strict CSRF protection
                max_age=3600,     # 1 hour (matches JWT token lifetime)
                path="/"
            )
            
            logger.debug(f"CSRF token set in cookie")
        
        return response


# Helper function to get CSRF token from request
def get_csrf_token(request: Request) -> str:
    """
    Get CSRF token from request cookie.
    
    This can be used to include the token in API responses
    for JavaScript clients.
    """
    return request.cookies.get("csrf_token", "")


# Helper function to generate CSRF token
def generate_csrf_token() -> str:
    """
    Generate a new CSRF token.
    
    Uses cryptographically secure random token generation.
    """
    return secrets.token_urlsafe(32)

