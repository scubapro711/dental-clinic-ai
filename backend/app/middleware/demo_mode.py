"""
Demo Mode Middleware

Enforces read-only mode for demo sessions to prevent data modifications.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_access_token
import logging

logger = logging.getLogger(__name__)


class DemoModeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce read-only mode for demo sessions.
    
    Demo tokens have a special `demo_mode: true` flag.
    This middleware blocks all write operations (POST, PUT, PATCH, DELETE)
    except for whitelisted endpoints.
    """
    
    # Endpoints that are allowed even in demo mode
    ALLOWED_WRITE_PATHS = [
        "/api/v1/demo/",  # Demo endpoints themselves
        "/api/v1/conversations/messages",  # Chatting with Alex is OK
        "/api/v1/auth/",  # Auth endpoints
    ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce read-only mode if demo token detected.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response from next handler or 403 error
        """
        # Get token from header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            
            # Check if demo mode
            if payload and payload.get("demo_mode"):
                # Check if this is a write operation
                if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                    # Check if path is whitelisted
                    path = request.url.path
                    is_allowed = any(path.startswith(allowed) for allowed in self.ALLOWED_WRITE_PATHS)
                    
                    if not is_allowed:
                        logger.warning(
                            f"Demo mode: Blocked {request.method} request to {path} "
                            f"from lead {payload.get('lead_email')}"
                        )
                        raise HTTPException(
                            status_code=403,
                            detail={
                                "error": "demo_mode_read_only",
                                "message": "Demo mode is read-only. Sign up to make changes!",
                                "upgrade_url": "/register"
                            }
                        )
                
                # Log demo mode access
                logger.info(
                    f"Demo mode: {request.method} {request.url.path} "
                    f"by lead {payload.get('lead_email')}"
                )
        
        # Continue to next handler
        response = await call_next(request)
        return response
