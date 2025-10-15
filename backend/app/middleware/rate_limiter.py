"""
Rate Limiting Middleware for DentaFlow API.

This module provides comprehensive rate limiting to protect against abuse
and ensure fair usage of API resources.

Features:
- Per-endpoint rate limits
- Role-based limits (higher for admins)
- IP-based tracking
- Redis backend for distributed systems
- Graceful error responses

Reference: ARCHITECTURE_DEEP_REVIEW_V20.4.0.md - Security Analysis
"""

import logging
from typing import Callable
from fastapi import Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

logger = logging.getLogger(__name__)


def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key based on user authentication.
    
    Uses user ID if authenticated, otherwise falls back to IP address.
    This allows authenticated users to have consistent rate limits
    across different IPs.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Rate limit key (user_id or ip_address)
    """
    # Check if user is authenticated
    if hasattr(request.state, "user") and request.state.user:
        user_id = getattr(request.state.user, "id", None)
        if user_id:
            return f"user:{user_id}"
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


def get_role_based_limit(request: Request, default_limit: str) -> str:
    """
    Get rate limit based on user role.
    
    Higher roles get higher limits:
    - super_admin: 5x default
    - org_admin: 3x default
    - org_staff: 2x default
    - org_viewer: 1x default
    - patient: 1x default
    - anonymous: 0.5x default
    
    Args:
        request: FastAPI request object
        default_limit: Default rate limit (e.g., "10/minute")
        
    Returns:
        str: Role-based rate limit
    """
    # Parse default limit
    parts = default_limit.split("/")
    if len(parts) != 2:
        return default_limit
    
    try:
        count = int(parts[0])
        period = parts[1]
    except ValueError:
        return default_limit
    
    # Get user role
    role = "anonymous"
    if hasattr(request.state, "user") and request.state.user:
        role = getattr(request.state.user, "role", "org_viewer")
    
    # Apply role multiplier
    multipliers = {
        "super_admin": 5.0,
        "org_admin": 3.0,
        "org_staff": 2.0,
        "org_viewer": 1.0,
        "patient": 1.0,
        "anonymous": 0.5
    }
    
    multiplier = multipliers.get(role, 1.0)
    new_count = int(count * multiplier)
    
    return f"{new_count}/{period}"


# Create rate limiter instance
# Uses in-memory storage by default, can be configured to use Redis
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=["100/minute"],  # Global default
    storage_uri="memory://",  # Can be changed to redis://localhost:6379
    strategy="fixed-window",  # Can be "moving-window" for more accurate limiting
    headers_enabled=False,  # Disabled to prevent errors with HTTPException responses
    swallow_errors=True,  # Continue even if rate limiting fails
)


# Rate limit configurations for different endpoint types
RATE_LIMITS = {
    # Authentication endpoints (strict limits to prevent brute force)
    "auth_login": "5/minute",
    "auth_register": "3/minute",
    "auth_password_reset": "3/minute",
    "auth_token_refresh": "10/minute",
    "auth_verify_email": "5/minute",
    "auth_verify_sms": "5/minute",
    
    # AI endpoints (moderate limits for resource-intensive operations)
    "ai_chat": "20/minute",
    "ai_chat_stream": "20/minute",
    "decision_queue": "30/minute",
    "finetuning": "10/minute",
    
    # Data read endpoints (higher limits for read operations)
    "read_patients": "50/minute",
    "read_appointments": "50/minute",
    "read_dashboard": "30/minute",
    "read_statistics": "30/minute",
    
    # Data write endpoints (moderate limits to prevent spam)
    "write_patient": "20/minute",
    "write_appointment": "20/minute",
    "write_treatment": "20/minute",
    
    # Admin endpoints (higher limits for administrators)
    "admin_operations": "50/minute",
    "admin_monitoring": "100/minute",
    
    # Public endpoints (strict limits for unauthenticated access)
    "public_api": "10/minute",
    "public_docs": "30/minute",
}


def get_rate_limit(endpoint_type: str) -> str:
    """
    Get rate limit for specific endpoint type.
    
    Args:
        endpoint_type: Type of endpoint (e.g., "auth_login")
        
    Returns:
        str: Rate limit string (e.g., "5/minute")
    """
    return RATE_LIMITS.get(endpoint_type, "30/minute")


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    
    Provides user-friendly error messages and includes retry-after header.
    
    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception
        
    Returns:
        Response: JSON response with error details
    """
    from fastapi.responses import JSONResponse
    
    logger.warning(
        f"Rate limit exceeded: {request.url.path} "
        f"from {get_rate_limit_key(request)}"
    )
    
    return JSONResponse(
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.retry_after if hasattr(exc, "retry_after") else 60
        },
        status_code=429,
        headers={
            "Retry-After": str(exc.retry_after if hasattr(exc, "retry_after") else 60),
            "X-RateLimit-Limit": str(exc.limit) if hasattr(exc, "limit") else "unknown",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(exc.reset) if hasattr(exc, "reset") else "unknown"
        }
    )


# Export limiter and handler
__all__ = [
    "limiter",
    "rate_limit_exceeded_handler",
    "get_rate_limit",
    "get_role_based_limit",
    "SlowAPIMiddleware"
]

