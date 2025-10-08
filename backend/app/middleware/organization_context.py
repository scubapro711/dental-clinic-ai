"""
Organization Context Middleware.

Injects organization context into request state for multi-tenant operations.
"""
from typing import Optional
from uuid import UUID
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class OrganizationContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate organization context.
    
    Extracts organization ID from:
    1. Header: X-Organization-ID
    2. Query param: org_id
    3. Path param: org_id
    
    Stores in request.state.organization_id for use in endpoints.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request and inject organization context."""
        org_id: Optional[UUID] = None
        
        # Try to get from header
        org_id_header = request.headers.get('X-Organization-ID')
        if org_id_header:
            try:
                org_id = UUID(org_id_header)
                logger.debug(f"Organization ID from header: {org_id}")
            except ValueError:
                logger.warning(f"Invalid organization ID in header: {org_id_header}")
                return HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid organization ID format in header"
                )
        
        # Try to get from query params
        if not org_id:
            org_id_param = request.query_params.get('org_id')
            if org_id_param:
                try:
                    org_id = UUID(org_id_param)
                    logger.debug(f"Organization ID from query: {org_id}")
                except ValueError:
                    logger.warning(f"Invalid organization ID in query: {org_id_param}")
        
        # Try to get from path params (if available)
        if not org_id:
            path_params = request.path_params
            if 'org_id' in path_params:
                try:
                    org_id = UUID(path_params['org_id'])
                    logger.debug(f"Organization ID from path: {org_id}")
                except ValueError:
                    logger.warning(f"Invalid organization ID in path: {path_params['org_id']}")
        
        # Store in request state
        request.state.organization_id = org_id
        
        # Continue processing
        response = await call_next(request)
        
        # Add organization ID to response headers (for debugging)
        if org_id:
            response.headers['X-Organization-ID'] = str(org_id)
        
        return response


def get_organization_id_from_request(request: Request) -> Optional[UUID]:
    """
    Get organization ID from request state.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Organization UUID if available, None otherwise
    """
    return getattr(request.state, 'organization_id', None)
