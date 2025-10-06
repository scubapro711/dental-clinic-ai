"""
RBAC (Role-Based Access Control) System

This module defines roles, permissions, and access control logic
for the dental clinic AI system.

Roles:
- patient: End users who book appointments and view their own data
- doctor: Medical professionals who treat patients
- owner: Clinic owner/manager with full access to business data

Security Principles:
1. Defense in Depth - Multiple layers of security
2. Least Privilege - Users get minimum necessary permissions
3. Explicit Deny - Default deny, explicit allow
4. Audit Trail - Log all access attempts
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """User roles in the system."""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    OWNER = "owner"


class Permission(str, Enum):
    """Granular permissions for different actions."""
    
    # Appointment permissions
    READ_OWN_APPOINTMENTS = "read:own_appointments"
    WRITE_OWN_APPOINTMENTS = "write:own_appointments"
    READ_ALL_APPOINTMENTS = "read:all_appointments"
    WRITE_ALL_APPOINTMENTS = "write:all_appointments"
    
    # Invoice/Billing permissions
    READ_OWN_INVOICES = "read:own_invoices"
    READ_ALL_INVOICES = "read:all_invoices"
    
    # Financial data permissions
    READ_REVENUE_SUMMARY = "read:revenue_summary"
    READ_DETAILED_FINANCIALS = "read:detailed_financials"
    
    # Patient data permissions
    READ_OWN_MEDICAL_RECORDS = "read:own_medical_records"
    READ_PATIENT_MEDICAL_RECORDS = "read:patient_medical_records"
    WRITE_MEDICAL_RECORDS = "write:medical_records"
    
    # Staff/Operations permissions
    READ_OWN_SCHEDULE = "read:own_schedule"
    READ_ALL_SCHEDULES = "read:all_schedules"
    WRITE_SCHEDULES = "write:schedules"
    MANAGE_STAFF = "manage:staff"
    
    # Agent access permissions
    ACCESS_ALEX = "access:alex"
    ACCESS_CFO = "access:cfo"
    ACCESS_ADMIN = "access:admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.PATIENT: [
        # Patients can only see their own data
        Permission.READ_OWN_APPOINTMENTS,
        Permission.WRITE_OWN_APPOINTMENTS,
        Permission.READ_OWN_INVOICES,
        Permission.READ_OWN_MEDICAL_RECORDS,
        # Patients can only talk to Alex (receptionist)
        Permission.ACCESS_ALEX,
    ],
    
    UserRole.DOCTOR: [
        # Doctors can see their patients' data
        Permission.READ_OWN_APPOINTMENTS,
        Permission.READ_ALL_APPOINTMENTS,  # Can see all to coordinate
        Permission.WRITE_ALL_APPOINTMENTS,  # Can book for patients
        Permission.READ_PATIENT_MEDICAL_RECORDS,  # Their patients only
        Permission.WRITE_MEDICAL_RECORDS,
        Permission.READ_OWN_SCHEDULE,
        Permission.READ_ALL_SCHEDULES,  # View only
        # Doctors can access all agents
        Permission.ACCESS_ALEX,
        Permission.ACCESS_CFO,  # For treatment profitability stats
        Permission.ACCESS_ADMIN,  # For schedule management
    ],
    
    UserRole.ADMIN: [
        # Admins manage operations and scheduling
        Permission.READ_ALL_APPOINTMENTS,
        Permission.WRITE_ALL_APPOINTMENTS,
        Permission.READ_ALL_SCHEDULES,
        Permission.WRITE_SCHEDULES,
        Permission.MANAGE_STAFF,
        # Admins can access operational agents
        Permission.ACCESS_ALEX,
        Permission.ACCESS_ADMIN,
        # Note: Admins CANNOT see financial data or medical records
    ],
    
    UserRole.OWNER: [
        # Owners have full business access
        Permission.READ_ALL_APPOINTMENTS,
        Permission.WRITE_ALL_APPOINTMENTS,
        Permission.READ_ALL_INVOICES,
        Permission.READ_REVENUE_SUMMARY,
        Permission.READ_DETAILED_FINANCIALS,
        Permission.READ_ALL_SCHEDULES,
        Permission.WRITE_SCHEDULES,
        Permission.MANAGE_STAFF,
        # Owners can access all agents
        Permission.ACCESS_ALEX,
        Permission.ACCESS_CFO,
        Permission.ACCESS_ADMIN,
        # Note: Owners CANNOT see individual patient medical records
        # This is for privacy compliance (HIPAA/GDPR)
    ],
}


def get_permissions_for_role(role: UserRole) -> List[str]:
    """
    Get list of permissions for a given role.
    
    Args:
        role: User role
        
    Returns:
        List of permission strings
    """
    return [p.value for p in ROLE_PERMISSIONS.get(role, [])]


def has_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if a user role has a specific permission.
    
    Args:
        user_role: User's role (patient/doctor/owner)
        required_permission: Permission to check
        
    Returns:
        True if user has permission, False otherwise
    """
    try:
        role = UserRole(user_role)
        permissions = get_permissions_for_role(role)
        return required_permission in permissions
    except ValueError:
        logger.error(f"Invalid user role: {user_role}")
        return False


def can_access_agent(user_role: str, agent_name: str) -> bool:
    """
    Check if a user can access a specific agent.
    
    Args:
        user_role: User's role
        agent_name: Name of agent (alex/cfo/admin)
        
    Returns:
        True if user can access agent, False otherwise
    """
    agent_permission_map = {
        "alex": Permission.ACCESS_ALEX.value,
        "cfo": Permission.ACCESS_CFO.value,
        "admin": Permission.ACCESS_ADMIN.value,
    }
    
    required_permission = agent_permission_map.get(agent_name.lower())
    if not required_permission:
        logger.error(f"Unknown agent: {agent_name}")
        return False
    
    return has_permission(user_role, required_permission)


def can_access_resource(
    user_role: str,
    user_id: str,
    resource_type: str,
    resource_owner_id: str,
) -> bool:
    """
    Check if a user can access a specific resource.
    
    This implements row-level security.
    
    Args:
        user_role: User's role
        user_id: User's ID
        resource_type: Type of resource (appointment/invoice/medical_record)
        resource_owner_id: ID of the resource owner
        
    Returns:
        True if user can access resource, False otherwise
    """
    # Users can always access their own resources
    if user_id == resource_owner_id:
        return True
    
    # Check role-based permissions
    role = UserRole(user_role)
    
    if resource_type == "appointment":
        # Doctors and owners can see all appointments
        return role in [UserRole.DOCTOR, UserRole.OWNER]
    
    elif resource_type == "invoice":
        # Only owners can see other people's invoices
        return role == UserRole.OWNER
    
    elif resource_type == "medical_record":
        # Only doctors can see patient medical records
        # Owners cannot see medical records (privacy compliance)
        return role == UserRole.DOCTOR
    
    elif resource_type == "schedule":
        # Doctors and owners can see schedules
        return role in [UserRole.DOCTOR, UserRole.OWNER]
    
    # Default deny
    return False


def get_permission_denied_message(user_role: str, requested_action: str) -> str:
    """
    Get a user-friendly permission denied message.
    
    Args:
        user_role: User's role
        requested_action: What the user tried to do
        
    Returns:
        Friendly error message
    """
    messages = {
        UserRole.PATIENT: {
            "access_cfo": "I'm sorry, but financial information is only available to clinic management. Is there anything else I can help you with regarding your appointments or billing?",
            "access_admin": "I'm sorry, but operational information is only available to clinic staff. Is there anything else I can help you with?",
            "view_other_appointments": "I can only show you your own appointments. Would you like to see your upcoming appointments?",
            "view_other_invoices": "I can only show you your own invoices and billing information. Would you like to see your billing history?",
        },
        UserRole.DOCTOR: {
            "view_detailed_financials": "Detailed financial information is only available to clinic management. I can show you treatment profitability statistics if that would help.",
            "manage_staff": "Staff management is handled by clinic administration. I can help you with your schedule or patient appointments instead.",
        },
        UserRole.OWNER: {
            "view_medical_records": "Individual patient medical records are confidential and only accessible to treating physicians. I can show you aggregate statistics instead.",
        },
    }
    
    try:
        role = UserRole(user_role)
        return messages.get(role, {}).get(
            requested_action,
            "I'm sorry, but you don't have permission to access this information."
        )
    except ValueError:
        return "I'm sorry, but you don't have permission to access this information."


def log_access_attempt(
    user_id: str,
    user_role: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    granted: bool,
) -> None:
    """
    Log an access attempt for audit trail.
    
    Args:
        user_id: User's ID
        user_role: User's role
        action: Action attempted
        resource_type: Type of resource
        resource_id: ID of resource (if applicable)
        granted: Whether access was granted
    """
    logger.info(
        f"Access {'GRANTED' if granted else 'DENIED'}: "
        f"user={user_id} role={user_role} action={action} "
        f"resource={resource_type}:{resource_id or 'N/A'}"
    )
