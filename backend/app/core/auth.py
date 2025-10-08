"""
Authentication dependencies for FastAPI.

Provides:
- JWT token validation
- Current user extraction
- Organization context
- Role-based access control
"""
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
import logging

from app.core.database import get_db
from app.core.cognito import get_cognito_client, CognitoUser
from app.models.user import User
from app.models.organization_membership import OrganizationMembership

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


async def get_current_cognito_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CognitoUser:
    """
    Get current user from Cognito JWT token.
    
    Validates token and extracts user information.
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        cognito_client = get_cognito_client()
        cognito_user = cognito_client.get_user_from_token(token)
        
        return cognito_user
    
    except JWTError as e:
        logger.error(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    cognito_user: CognitoUser = Depends(get_current_cognito_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current DentaFlow user from database.
    
    Links Cognito user to DentaFlow User model.
    Creates user if doesn't exist (auto-registration).
    
    Raises:
        HTTPException: If user cannot be found or created
    """
    # Find user by Cognito sub (UUID)
    user = db.query(User).filter(User.cognito_sub == cognito_user.sub).first()
    
    if not user:
        # Auto-register user from Cognito
        logger.info(f"Auto-registering user from Cognito: {cognito_user.email}")
        
        user = User(
            email=cognito_user.email,
            full_name=f"{cognito_user.given_name or ''} {cognito_user.family_name or ''}".strip(),
            cognito_sub=cognito_user.sub,
            is_active=True,
            email_verified=cognito_user.email_verified
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Alias for get_current_user (already checks is_active).
    """
    return current_user


class OrganizationContext:
    """
    Organization context for multi-tenant operations.
    
    Extracts organization from:
    1. Header: X-Organization-ID
    2. Query param: org_id
    3. User's default organization
    """
    
    def __init__(self, required: bool = True):
        """
        Initialize organization context.
        
        Args:
            required: Whether organization is required (raises 400 if missing)
        """
        self.required = required
    
    async def __call__(
        self,
        org_id: Optional[UUID] = None,  # From query param or path
        x_organization_id: Optional[str] = None,  # From header
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Optional[OrganizationMembership]:
        """
        Get organization membership for current user.
        
        Returns:
            OrganizationMembership if found, None if not required
        
        Raises:
            HTTPException: If organization required but not found
        """
        # Try to get org_id from header first
        if x_organization_id:
            try:
                org_id = UUID(x_organization_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid organization ID in header"
                )
        
        # If no org_id provided, use user's default (first membership)
        if not org_id:
            membership = db.query(OrganizationMembership).filter(
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.is_active == True
            ).first()
            
            if not membership and self.required:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization ID required but not provided"
                )
            
            return membership
        
        # Get specific organization membership
        membership = db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == current_user.id,
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.is_active == True
        ).first()
        
        if not membership:
            if self.required:
                logger.warning(
                    f"User {current_user.email} attempted access to org {org_id} without membership"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a member of this organization"
                )
            return None
        
        return membership


# Dependency instances
get_organization = OrganizationContext(required=True)
get_optional_organization = OrganizationContext(required=False)


class RoleChecker:
    """
    Role-based access control checker.
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(
            user: User = Depends(get_current_user),
            _: None = Depends(RoleChecker(["owner", "admin"]))
        ):
            ...
    """
    
    def __init__(self, allowed_roles: list[str]):
        """
        Initialize role checker.
        
        Args:
            allowed_roles: List of allowed organization roles
        """
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self,
        membership: OrganizationMembership = Depends(get_organization)
    ) -> None:
        """
        Check if user has required role.
        
        Raises:
            HTTPException: If user doesn't have required role
        """
        if membership.organization_role not in self.allowed_roles:
            logger.warning(
                f"User {membership.user_id} with role {membership.organization_role} "
                f"attempted access requiring {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(self.allowed_roles)}"
            )


class FunctionalRoleChecker:
    """
    Functional role-based access control checker.
    
    Usage:
        @router.get("/dentist-only")
        async def dentist_endpoint(
            user: User = Depends(get_current_user),
            _: None = Depends(FunctionalRoleChecker(["dentist", "specialist"]))
        ):
            ...
    """
    
    def __init__(self, allowed_roles: list[str]):
        """
        Initialize functional role checker.
        
        Args:
            allowed_roles: List of allowed functional roles
        """
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self,
        membership: OrganizationMembership = Depends(get_organization)
    ) -> None:
        """
        Check if user has required functional role.
        
        Raises:
            HTTPException: If user doesn't have required functional role
        """
        if membership.functional_role not in self.allowed_roles:
            logger.warning(
                f"User {membership.user_id} with functional role {membership.functional_role} "
                f"attempted access requiring {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required functional role: {', '.join(self.allowed_roles)}"
            )


# Common role checkers
require_owner = RoleChecker(["owner"])
require_admin = RoleChecker(["owner", "admin"])
require_staff = RoleChecker(["owner", "admin", "staff"])

require_dentist = FunctionalRoleChecker(["dentist", "specialist"])
require_receptionist = FunctionalRoleChecker(["receptionist", "office_manager"])
