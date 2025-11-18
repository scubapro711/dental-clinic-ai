"""
API dependencies for authentication and authorization.
"""

from typing import Optional, Union, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
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


def require_role(required_role: Union[UserRole, List[str]]):
    """
    Dependency factory for role-based access control.
    
    Supports both single role and list of allowed roles.
    
    Usage:
        # Single role
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(UserRole.SUPER_ADMIN))):
            ...
        
        # Multiple roles (any of them)
        @router.get("/multi-role")
        async def multi_endpoint(user: User = Depends(require_role(["clinic_admin", "super_admin"]))):
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
        
        # String to UserRole mapping for list-based roles
        role_mapping = {
            "super_admin": UserRole.SUPER_ADMIN,
            "clinic_admin": UserRole.ORG_ADMIN,
            "org_admin": UserRole.ORG_ADMIN,
            "org_staff": UserRole.ORG_STAFF,
            "org_viewer": UserRole.ORG_VIEWER,
        }
        
        # Handle list of roles (user needs to have ANY of them)
        if isinstance(required_role, list):
            allowed_roles = [role_mapping.get(r.lower(), r) for r in required_role]
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        # Handle single role (hierarchical check)
        else:
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


async def get_current_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Organization:
    """
    Get current user's organization.
    
    Raises:
        HTTPException: If user has no organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization"
        )
    
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization


async def get_current_membership(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMembership:
    """
    Get current user's active organization membership.
    
    This is the primary way to get organization context for authenticated requests.
    Returns the user's first active membership.
    
    Raises:
        HTTPException: If user has no active organization membership
    """
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization. Please contact support."
        )
    
    return membership



async def require_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require Super Admin role.
    
    Usage:
        @router.get("/super-admin-only")
        async def super_admin_endpoint(user: User = Depends(require_super_admin)):
            ...
    
    Raises:
        HTTPException: If user is not a super admin
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


