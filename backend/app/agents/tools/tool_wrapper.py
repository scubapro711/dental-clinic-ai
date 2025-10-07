"""
Tool Wrapper for Automatic RBAC Enforcement

This module provides a decorator that automatically adds RBAC checks
to all tool functions, ensuring consistent security across the system.

Usage:
    @rbac_protected(required_permission=Permission.READ_OWN_APPOINTMENTS)
    def get_appointments_tool(...):
        ...
"""

from functools import wraps
from typing import Callable, Optional, Any
import logging

from app.agents.rbac import (
    has_permission,
    can_access_resource,
    get_permission_denied_message,
    log_access_attempt,
    Permission,
)

logger = logging.getLogger(__name__)


def rbac_protected(
    required_permission: Optional[str] = None,
    resource_type: Optional[str] = None,
    allow_self_access: bool = True,
):
    """
    Decorator to add RBAC protection to tool functions.
    
    This decorator:
    1. Extracts user_id and user_role from function arguments
    2. Checks if user has required permission
    3. Logs access attempt
    4. Returns permission denied message if unauthorized
    
    Args:
        required_permission: Permission required to use this tool
        resource_type: Type of resource being accessed (for row-level security)
        allow_self_access: If True, users can always access their own resources
        
    Example:
        @rbac_protected(
            required_permission=Permission.READ_ALL_APPOINTMENTS.value,
            resource_type="appointment"
        )
        def get_appointments_tool(
            patient_id: str,
            requesting_user_id: str,
            requesting_user_role: str
        ):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract RBAC parameters from kwargs
            requesting_user_id = kwargs.get('requesting_user_id')
            requesting_user_role = kwargs.get('requesting_user_role')
            
            if not requesting_user_id or not requesting_user_role:
                logger.warning(f"Tool {func.__name__} called without RBAC context")
                # For backward compatibility, allow calls without RBAC
                # In production, this should raise an error
                return func(*args, **kwargs)
            
            # Check permission if required
            if required_permission:
                if not has_permission(requesting_user_role, required_permission):
                    # Check if user is accessing their own resource
                    if allow_self_access and resource_type:
                        resource_owner_id = kwargs.get('patient_id') or kwargs.get('user_id')
                        if resource_owner_id and str(resource_owner_id) == str(requesting_user_id):
                            # User is accessing their own resource - allow
                            log_access_attempt(
                                requesting_user_id,
                                requesting_user_role,
                                func.__name__,
                                resource_type,
                                resource_owner_id,
                                True
                            )
                            return func(*args, **kwargs)
                    
                    # Permission denied
                    log_access_attempt(
                        requesting_user_id,
                        requesting_user_role,
                        func.__name__,
                        resource_type or "unknown",
                        None,
                        False
                    )
                    
                    action_name = func.__name__.replace('_tool', '').replace('_', ' ')
                    return get_permission_denied_message(requesting_user_role, action_name)
            
            # Check resource-level access if resource_type specified
            if resource_type and not required_permission:
                resource_owner_id = kwargs.get('patient_id') or kwargs.get('user_id')
                if resource_owner_id:
                    can_access = can_access_resource(
                        requesting_user_role,
                        requesting_user_id,
                        resource_type,
                        resource_owner_id
                    )
                    
                    if not can_access:
                        log_access_attempt(
                            requesting_user_id,
                            requesting_user_role,
                            func.__name__,
                            resource_type,
                            resource_owner_id,
                            False
                        )
                        return get_permission_denied_message(
                            requesting_user_role,
                            f"view_other_{resource_type}s"
                        )
            
            # Access granted - log and execute
            log_access_attempt(
                requesting_user_id,
                requesting_user_role,
                func.__name__,
                resource_type or "unknown",
                kwargs.get('patient_id') or kwargs.get('user_id'),
                True
            )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def inject_user_context(state: dict) -> dict:
    """
    Extract user context from state and return as kwargs for tools.
    
    This helper function makes it easy to pass RBAC context to tools.
    
    Args:
        state: AgentState dictionary
        
    Returns:
        Dictionary with requesting_user_id and requesting_user_role
    """
    return {
        'requesting_user_id': state.get('user_id'),
        'requesting_user_role': state.get('user_role'),
    }
