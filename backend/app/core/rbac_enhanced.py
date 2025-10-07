"""
Enhanced RBAC (Role-Based Access Control) System
With field-level permissions and advanced features
"""

from typing import List, Dict, Any, Optional, Set
from enum import Enum
from datetime import datetime, time
import logging

from app.agents.rbac import UserRole, Permission as BasePermission

logger = logging.getLogger(__name__)


class FieldPermission(str, Enum):
    """Field-level permissions for sensitive data."""
    
    # Patient sensitive fields
    READ_PATIENT_ID_NUMBER = "read:patient_id_number"  # ת.ז.
    READ_PATIENT_SSN = "read:patient_ssn"  # SSN (if applicable)
    READ_PATIENT_CREDIT_CARD = "read:patient_credit_card"
    READ_PATIENT_MEDICAL_HISTORY = "read:patient_medical_history"
    READ_PATIENT_ALLERGIES = "read:patient_allergies"
    READ_PATIENT_MEDICATIONS = "read:patient_medications"
    
    # Financial sensitive fields
    READ_INVOICE_DETAILS = "read:invoice_details"
    READ_PAYMENT_METHOD = "read:payment_method"
    READ_PROFIT_MARGINS = "read:profit_margins"
    READ_STAFF_SALARIES = "read:staff_salaries"
    
    # Export permissions
    EXPORT_PATIENT_DATA = "export:patient_data"
    EXPORT_FINANCIAL_DATA = "export:financial_data"
    EXPORT_AUDIT_LOGS = "export:audit_logs"
    
    # Delete permissions
    DELETE_PATIENT_DATA = "delete:patient_data"
    DELETE_APPOINTMENT = "delete:appointment"
    DELETE_INVOICE = "delete:invoice"
    
    # Admin permissions
    MANAGE_USERS = "manage:users"
    MANAGE_ROLES = "manage:roles"
    VIEW_AUDIT_LOGS = "view:audit_logs"
    MANAGE_SYSTEM_SETTINGS = "manage:system_settings"


# Extended role permissions
EXTENDED_ROLE_PERMISSIONS: Dict[UserRole, List[FieldPermission]] = {
    UserRole.PATIENT: [
        # Patients can see their own sensitive data
        FieldPermission.READ_PATIENT_ID_NUMBER,
        FieldPermission.READ_PATIENT_MEDICAL_HISTORY,
        FieldPermission.READ_PATIENT_ALLERGIES,
        FieldPermission.READ_PATIENT_MEDICATIONS,
        FieldPermission.READ_INVOICE_DETAILS,
        FieldPermission.EXPORT_PATIENT_DATA,  # Their own data only
    ],
    
    UserRole.DOCTOR: [
        # Doctors can see patient medical data
        FieldPermission.READ_PATIENT_ID_NUMBER,
        FieldPermission.READ_PATIENT_MEDICAL_HISTORY,
        FieldPermission.READ_PATIENT_ALLERGIES,
        FieldPermission.READ_PATIENT_MEDICATIONS,
        FieldPermission.READ_INVOICE_DETAILS,  # For treatment planning
        FieldPermission.DELETE_APPOINTMENT,  # Can cancel appointments
        FieldPermission.VIEW_AUDIT_LOGS,  # Their own actions only
    ],
    
    UserRole.OWNER: [
        # Owners have full business access
        FieldPermission.READ_INVOICE_DETAILS,
        FieldPermission.READ_PAYMENT_METHOD,
        FieldPermission.READ_PROFIT_MARGINS,
        FieldPermission.READ_STAFF_SALARIES,
        FieldPermission.EXPORT_FINANCIAL_DATA,
        FieldPermission.EXPORT_AUDIT_LOGS,
        FieldPermission.DELETE_APPOINTMENT,
        FieldPermission.DELETE_INVOICE,
        FieldPermission.MANAGE_USERS,
        FieldPermission.MANAGE_ROLES,
        FieldPermission.VIEW_AUDIT_LOGS,
        FieldPermission.MANAGE_SYSTEM_SETTINGS,
        # Note: Owners still CANNOT see patient medical records
    ],
}


class TimeBasedAccessControl:
    """
    Time-based access control.
    
    Allows restricting access based on time of day, day of week, etc.
    """
    
    @staticmethod
    def is_within_business_hours(
        current_time: datetime = None,
        start_time: time = time(8, 0),  # 8:00 AM
        end_time: time = time(20, 0)  # 8:00 PM
    ) -> bool:
        """Check if current time is within business hours."""
        if current_time is None:
            current_time = datetime.now()
        
        current_time_only = current_time.time()
        return start_time <= current_time_only <= end_time
    
    @staticmethod
    def is_weekday(current_time: datetime = None) -> bool:
        """Check if current day is a weekday (Monday-Friday)."""
        if current_time is None:
            current_time = datetime.now()
        
        return current_time.weekday() < 5  # 0-4 = Monday-Friday


class IPBasedAccessControl:
    """
    IP-based access control.
    
    Allows restricting access based on IP address.
    """
    
    # Whitelist of allowed IP addresses/ranges
    ALLOWED_IPS: Set[str] = {
        "127.0.0.1",  # Localhost
        "::1",  # IPv6 localhost
        # Add clinic IP addresses here
    }
    
    # Blacklist of blocked IP addresses
    BLOCKED_IPS: Set[str] = set()
    
    @staticmethod
    def is_ip_allowed(ip_address: str) -> bool:
        """Check if IP address is allowed."""
        if ip_address in IPBasedAccessControl.BLOCKED_IPS:
            return False
        
        # For now, allow all IPs (can be restricted later)
        return True
    
    @staticmethod
    def block_ip(ip_address: str, reason: str = None):
        """Block an IP address."""
        IPBasedAccessControl.BLOCKED_IPS.add(ip_address)
        logger.warning(f"IP blocked: {ip_address} - Reason: {reason}")
    
    @staticmethod
    def unblock_ip(ip_address: str):
        """Unblock an IP address."""
        IPBasedAccessControl.BLOCKED_IPS.discard(ip_address)
        logger.info(f"IP unblocked: {ip_address}")


class EnhancedRBAC:
    """
    Enhanced RBAC with field-level, time-based, and IP-based access control.
    """
    
    @staticmethod
    def has_field_permission(
        user_role: str,
        field_permission: FieldPermission,
        user_id: str = None,
        resource_owner_id: str = None
    ) -> bool:
        """
        Check if user has permission to access a specific field.
        
        Args:
            user_role: User's role
            field_permission: Field permission to check
            user_id: User's ID (for own data check)
            resource_owner_id: Owner of the resource
            
        Returns:
            True if user has permission
        """
        try:
            role = UserRole(user_role)
            
            # Users can always access their own data
            if user_id and resource_owner_id and user_id == resource_owner_id:
                return True
            
            # Check role permissions
            permissions = EXTENDED_ROLE_PERMISSIONS.get(role, [])
            return field_permission in permissions
            
        except ValueError:
            logger.error(f"Invalid user role: {user_role}")
            return False
    
    @staticmethod
    def filter_fields(
        user_role: str,
        data: Dict[str, Any],
        field_permissions_map: Dict[str, FieldPermission],
        user_id: str = None,
        resource_owner_id: str = None
    ) -> Dict[str, Any]:
        """
        Filter out fields that user doesn't have permission to see.
        
        Args:
            user_role: User's role
            data: Original data dictionary
            field_permissions_map: Map of field names to required permissions
            user_id: User's ID
            resource_owner_id: Owner of the resource
            
        Returns:
            Filtered data dictionary
        """
        filtered_data = {}
        
        for field, value in data.items():
            # Check if field requires special permission
            required_permission = field_permissions_map.get(field)
            
            if required_permission is None:
                # No special permission required
                filtered_data[field] = value
            else:
                # Check if user has permission
                if EnhancedRBAC.has_field_permission(
                    user_role,
                    required_permission,
                    user_id,
                    resource_owner_id
                ):
                    filtered_data[field] = value
                else:
                    # Mask sensitive data
                    filtered_data[field] = "***REDACTED***"
        
        return filtered_data
    
    @staticmethod
    def check_access(
        user_role: str,
        user_id: str,
        ip_address: str,
        required_permission: str,
        resource_owner_id: str = None,
        check_time: bool = False,
        check_ip: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Comprehensive access check.
        
        Args:
            user_role: User's role
            user_id: User's ID
            ip_address: User's IP address
            required_permission: Required permission
            resource_owner_id: Owner of the resource
            check_time: Whether to check business hours
            check_ip: Whether to check IP whitelist
            
        Returns:
            Tuple of (allowed: bool, reason: Optional[str])
        """
        # Check IP-based access
        if check_ip and not IPBasedAccessControl.is_ip_allowed(ip_address):
            return False, f"Access denied from IP: {ip_address}"
        
        # Check time-based access
        if check_time and not TimeBasedAccessControl.is_within_business_hours():
            return False, "Access denied outside business hours"
        
        # Check role-based permission
        from app.agents.rbac import has_permission, can_access_resource
        
        if not has_permission(user_role, required_permission):
            return False, f"Role '{user_role}' does not have permission '{required_permission}'"
        
        # Check resource ownership if applicable
        if resource_owner_id and user_id != resource_owner_id:
            resource_type = required_permission.split(":")[1] if ":" in required_permission else "resource"
            if not can_access_resource(user_role, user_id, resource_type, resource_owner_id):
                return False, f"Cannot access other user's {resource_type}"
        
        return True, None


# Example field permissions map for Patient model
PATIENT_FIELD_PERMISSIONS = {
    "id_number": FieldPermission.READ_PATIENT_ID_NUMBER,
    "ssn": FieldPermission.READ_PATIENT_SSN,
    "credit_card": FieldPermission.READ_PATIENT_CREDIT_CARD,
    "medical_history": FieldPermission.READ_PATIENT_MEDICAL_HISTORY,
    "allergies": FieldPermission.READ_PATIENT_ALLERGIES,
    "medications": FieldPermission.READ_PATIENT_MEDICATIONS,
}


# Example field permissions map for Invoice model
INVOICE_FIELD_PERMISSIONS = {
    "payment_method": FieldPermission.READ_PAYMENT_METHOD,
    "profit_margin": FieldPermission.READ_PROFIT_MARGINS,
}


# Example usage
if __name__ == "__main__":
    # Test field-level permissions
    patient_data = {
        "id": 123,
        "name": "John Doe",
        "phone": "555-1234",
        "id_number": "123456789",
        "medical_history": "Diabetes, Hypertension",
        "allergies": "Penicillin"
    }
    
    # Patient viewing their own data
    filtered = EnhancedRBAC.filter_fields(
        user_role="patient",
        data=patient_data,
        field_permissions_map=PATIENT_FIELD_PERMISSIONS,
        user_id="123",
        resource_owner_id="123"
    )
    print("Patient viewing own data:", filtered)
    
    # Owner trying to view patient medical data
    filtered = EnhancedRBAC.filter_fields(
        user_role="owner",
        data=patient_data,
        field_permissions_map=PATIENT_FIELD_PERMISSIONS,
        user_id="999",
        resource_owner_id="123"
    )
    print("Owner viewing patient data:", filtered)
