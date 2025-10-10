"""
Role-Based Access Control (RBAC) Module

Provides decorators and utilities for role-based access control.
"""

from functools import wraps
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Callable
import logging

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)


# Role definitions
class Role:
    """Role constants."""
    ADMIN = "admin"
    OWNER = "owner"
    STAFF = "staff"
    PATIENT = "patient"
    
    # Role hierarchy (higher number = more permissions)
    HIERARCHY = {
        ADMIN: 4,
        OWNER: 3,
        STAFF: 2,
        PATIENT: 1
    }
    
    @classmethod
    def has_permission(cls, user_role: str, required_role: str) -> bool:
        """
        Check if user role has permission for required role.
        
        Uses role hierarchy - higher roles have all permissions of lower roles.
        
        Args:
            user_role: User's current role
            required_role: Required role for the operation
        
        Returns:
            True if user has permission, False otherwise
        """
        user_level = cls.HIERARCHY.get(user_role, 0)
        required_level = cls.HIERARCHY.get(required_role, 0)
        return user_level >= required_level


def require_role(required_role: str):
    """
    Decorator to require a specific role for an endpoint.
    
    Usage:
        @router.get("/admin/users")
        @require_role(Role.ADMIN)
        async def get_all_users(current_user: User = Depends(get_current_user)):
            ...
    
    Args:
        required_role: The role required to access the endpoint
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                # Try to find it in args (for positional arguments)
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                logger.error("No current_user found in endpoint arguments")
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error: user authentication failed"
                )
            
            # Check user role
            user_role = getattr(current_user, 'role', None)
            
            if not user_role:
                logger.warning(f"User {current_user.id} has no role assigned")
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: no role assigned"
                )
            
            # Check permission
            if not Role.has_permission(user_role, required_role):
                logger.warning(
                    f"User {current_user.id} with role '{user_role}' "
                    f"attempted to access endpoint requiring '{required_role}'"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied: {required_role} role required"
                )
            
            # User has permission, proceed
            logger.info(
                f"User {current_user.id} with role '{user_role}' "
                f"accessed endpoint requiring '{required_role}'"
            )
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_roles(required_roles: List[str]):
    """
    Decorator to require one of multiple roles for an endpoint.
    
    Usage:
        @router.get("/staff/dashboard")
        @require_roles([Role.ADMIN, Role.OWNER, Role.STAFF])
        async def get_dashboard(current_user: User = Depends(get_current_user)):
            ...
    
    Args:
        required_roles: List of roles, user must have at least one
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                # Try to find it in args
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                logger.error("No current_user found in endpoint arguments")
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error: user authentication failed"
                )
            
            # Check user role
            user_role = getattr(current_user, 'role', None)
            
            if not user_role:
                logger.warning(f"User {current_user.id} has no role assigned")
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: no role assigned"
                )
            
            # Check if user has any of the required roles
            has_permission = any(
                Role.has_permission(user_role, required_role)
                for required_role in required_roles
            )
            
            if not has_permission:
                logger.warning(
                    f"User {current_user.id} with role '{user_role}' "
                    f"attempted to access endpoint requiring one of {required_roles}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied: one of {required_roles} roles required"
                )
            
            # User has permission, proceed
            logger.info(
                f"User {current_user.id} with role '{user_role}' "
                f"accessed endpoint requiring one of {required_roles}"
            )
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def check_resource_ownership(user: User, resource_user_id: str) -> bool:
    """
    Check if user owns a resource.
    
    Admins and owners can access all resources.
    Other users can only access their own resources.
    
    Args:
        user: Current user
        resource_user_id: User ID of the resource owner
    
    Returns:
        True if user has access, False otherwise
    """
    # Admins and owners can access everything
    if user.role in [Role.ADMIN, Role.OWNER]:
        return True
    
    # Other users can only access their own resources
    return str(user.id) == str(resource_user_id)


def require_ownership(resource_user_id_param: str = "user_id"):
    """
    Decorator to require resource ownership or admin/owner role.
    
    Usage:
        @router.get("/users/{user_id}/profile")
        @require_ownership("user_id")
        async def get_user_profile(
            user_id: str,
            current_user: User = Depends(get_current_user)
        ):
            ...
    
    Args:
        resource_user_id_param: Name of the parameter containing the resource user ID
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user
            current_user = kwargs.get('current_user')
            
            if not current_user:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error: user authentication failed"
                )
            
            # Extract resource user ID
            resource_user_id = kwargs.get(resource_user_id_param)
            
            if not resource_user_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required parameter: {resource_user_id_param}"
                )
            
            # Check ownership
            if not check_resource_ownership(current_user, resource_user_id):
                logger.warning(
                    f"User {current_user.id} attempted to access "
                    f"resource owned by {resource_user_id}"
                )
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: you can only access your own resources"
                )
            
            # User has access, proceed
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

