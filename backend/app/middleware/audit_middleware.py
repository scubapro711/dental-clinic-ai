"""
Audit Logging Middleware for FastAPI.

Automatically logs all API requests for HIPAA compliance.
"""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

from app.core.database import get_db
from app.core.audit_log import log_audit_event
from app.core.jwt_utils import verify_token

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log all API requests.
    
    Logs:
    - All authenticated requests
    - PHI access (patient data)
    - Authentication events
    - Failed requests
    """
    
    # Endpoints that should be audited
    PHI_ENDPOINTS = [
        '/api/v1/patients',
        '/api/v1/medical-records',
        '/api/v1/appointments',
        '/api/v1/treatments'
    ]
    
    # Endpoints that should NOT be audited (too noisy)
    EXCLUDED_ENDPOINTS = [
        '/health',
        '/docs',
        '/openapi.json',
        '/favicon.ico'
    ]
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log audit event."""
        start_time = time.time()
        
        # Skip excluded endpoints
        if any(request.url.path.startswith(endpoint) for endpoint in self.EXCLUDED_ENDPOINTS):
            return await call_next(request)
        
        # Extract user info from JWT token
        user_id = None
        user_email = None
        organization_id = None
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            token_data = verify_token(token)
            
            if token_data:
                user_id = token_data.sub
                user_email = token_data.email
                organization_id = token_data.organization_id
        
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('User-Agent')
        
        # Process request
        response = await call_next(request)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Determine if this is a PHI access
        is_phi_access = any(request.url.path.startswith(endpoint) for endpoint in self.PHI_ENDPOINTS)
        
        # Only log if user is authenticated or it's a failed auth attempt
        if user_id or request.url.path.startswith('/api/v1/auth'):
            try:
                # Get database session
                db = next(get_db())
                
                # Determine action from method and path
                action = self._determine_action(request.method, request.url.path, response.status_code)
                
                # Determine resource type and ID
                resource_type, resource_id = self._extract_resource_info(request.url.path)
                
                # Determine status
                status = 'success' if response.status_code < 400 else 'failure'
                
                # Log audit event
                if user_id and user_email:
                    log_audit_event(
                        db_session=db,
                        user_id=user_id,
                        user_email=user_email,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        endpoint=str(request.url.path),
                        method=request.method,
                        metadata={
                            'duration_ms': int(duration * 1000),
                            'status_code': response.status_code,
                            'is_phi_access': is_phi_access
                        },
                        organization_id=organization_id,
                        status=status
                    )
                
                db.close()
            
            except Exception as e:
                logger.error(f"Failed to log audit event: {e}")
                # Don't fail the request if audit logging fails
        
        return response
    
    def _determine_action(self, method: str, path: str, status_code: int) -> str:
        """Determine action from HTTP method and path."""
        if path.startswith('/api/v1/auth/signin'):
            return 'LOGIN' if status_code < 400 else 'LOGIN_FAILED'
        elif path.startswith('/api/v1/auth/signout'):
            return 'LOGOUT'
        elif method == 'POST':
            return 'CREATE'
        elif method == 'GET':
            return 'READ' if '/patients/' in path else 'LIST'
        elif method in ['PUT', 'PATCH']:
            return 'UPDATE'
        elif method == 'DELETE':
            return 'DELETE'
        else:
            return 'UNKNOWN'
    
    def _extract_resource_info(self, path: str) -> tuple[str, str | None]:
        """Extract resource type and ID from path."""
        parts = path.split('/')
        
        # Remove empty parts and 'api', 'v1'
        parts = [p for p in parts if p and p not in ['api', 'v1']]
        
        if not parts:
            return 'unknown', None
        
        resource_type = parts[0]
        resource_id = parts[1] if len(parts) > 1 and not parts[1].startswith('?') else None
        
        return resource_type, resource_id
