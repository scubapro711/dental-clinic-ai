"""
API dependencies for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

# HTTP Bearer token security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    token_data = AuthService.verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = AuthService.get_user_by_id(db, token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(UserRole.SUPER_ADMIN))):
            ...
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Role hierarchy: SUPER_ADMIN > ORG_ADMIN > ORG_STAFF > ORG_VIEWER
        role_hierarchy = {
            UserRole.SUPER_ADMIN: 4,
            UserRole.ORG_ADMIN: 3,
            UserRole.ORG_STAFF: 2,
            UserRole.ORG_VIEWER: 1,
        }

        if role_hierarchy.get(current_user.role, 0) < role_hierarchy.get(
            required_role, 0
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker


async def get_current_organization_id(
    current_user: User = Depends(get_current_user),
) -> Optional[str]:
    """Get current user's organization ID."""
    return str(current_user.organization_id) if current_user.organization_id else None
