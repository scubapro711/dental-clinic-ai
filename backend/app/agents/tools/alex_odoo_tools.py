"""
Alex Agent Tools - Real Odoo Integration

This module provides tools for Alex (receptionist agent) to interact with
the real Odoo dental management system.

Tools focus on patient management and basic information retrieval.
"""

from typing import Optional, Dict, Any
from datetime import datetime, date
import logging
import os

from app.agents.rbac import (
    has_permission,
    can_access_resource,
    get_permission_denied_message,
    log_access_attempt,
    Permission,
)

logger = logging.getLogger(__name__)

# Initialize client (mock in tests, real in production)
if os.getenv("TESTING") == "1" or os.getenv("APP_ENV") == "test":
    from app.integrations.mock_odoo_realistic import RealisticMockOdooClient
    odoo_client = RealisticMockOdooClient()
    logger.info("Using Mock Odoo Client for testing")
else:
    from app.integrations.odoo_client import OdooClient
    odoo_client = OdooClient()
    logger.info("Using Real Odoo Client")


def search_patient_odoo(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Search for a patient in Odoo by name, phone, or email.
    
    RBAC: Patients can only search for themselves, staff can search all.
    
    Args:
        name: Patient name (partial match allowed)
        phone: Patient phone number
        email: Patient email
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with patient information or "not found" message
    """
    try:
        # RBAC Check
        if requesting_user_role == "patient":
            log_access_attempt(
                requesting_user_id,
                requesting_user_role,
                "search_patient",
                "patient",
                None,
                True
            )
        elif requesting_user_role in ["doctor", "owner", "admin"]:
            log_access_attempt(
                requesting_user_id,
                requesting_user_role,
                "search_patient",
                "patient",
                None,
                True
            )
        else:
            log_access_attempt(
                requesting_user_id or "unknown",
                requesting_user_role or "unknown",
                "search_patient",
                "patient",
                None,
                False
            )
            return get_permission_denied_message(requesting_user_role or "unknown", "search_patients")
        
        # Search in Odoo
        patient_ids = odoo_client.search_patients(name=name, phone=phone, email=email, limit=5)
        
        if not patient_ids:
            search_terms = []
            if name:
                search_terms.append(f"name='{name}'")
            if phone:
                search_terms.append(f"phone='{phone}'")
            if email:
                search_terms.append(f"email='{email}'")
            return f"No patient found with {' or '.join(search_terms)}"
        
        # Get details of matching patients
        results = []
        for patient_id in patient_ids[:3]:  # Limit to 3 results
            patient = odoo_client.get_patient(patient_id)
            if patient:
                # For patients, only return if it's their own record
                if requesting_user_role == "patient" and str(patient['id']) != requesting_user_id:
                    continue
                
                results.append(
                    f"- {patient['name']} (ID: {patient['id']})\n"
                    f"  Phone: {patient.get('phone', 'N/A')}\n"
                    f"  Email: {patient.get('email', 'N/A')}\n"
                    f"  City: {patient.get('city', 'N/A')}"
                )
        
        if not results:
            return "No matching patients found or access denied"
        
        return f"Found {len(results)} patient(s):\n\n" + "\n\n".join(results)
        
    except Exception as e:
        logger.error(f"Error in search_patient_odoo: {str(e)}")
        return f"Error searching patient: {str(e)}"


def get_patient_details_odoo(
    patient_id: int,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Get detailed information about a specific patient from Odoo.
    
    RBAC: Patients can only view their own details, staff can view all.
    
    Args:
        patient_id: Odoo patient ID
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with detailed patient information
    """
    try:
        # RBAC Check
        if requesting_user_role == "patient":
            if str(patient_id) != requesting_user_id:
                log_access_attempt(
                    requesting_user_id,
                    requesting_user_role,
                    "get_patient_details",
                    "patient",
                    patient_id,
                    False
                )
                return get_permission_denied_message(requesting_user_role, "view_other_patients")
        elif requesting_user_role not in ["doctor", "owner", "admin"]:
            log_access_attempt(
                requesting_user_id or "unknown",
                requesting_user_role or "unknown",
                "get_patient_details",
                "patient",
                patient_id,
                False
            )
            return get_permission_denied_message(requesting_user_role or "unknown", "view_patients")
        
        log_access_attempt(
            requesting_user_id,
            requesting_user_role,
            "get_patient_details",
            "patient",
            patient_id,
            True
        )
        
        # Get patient from Odoo
        patient = odoo_client.get_patient(patient_id)
        
        if not patient:
            return f"Patient with ID {patient_id} not found"
        
        # Format patient details
        details = f"""
Patient Details:
================
Name: {patient.get('name', 'N/A')}
ID: {patient.get('id', 'N/A')}
Email: {patient.get('email', 'N/A')}
Phone: {patient.get('phone', 'N/A')}

Address:
--------
Street: {patient.get('street', 'N/A')}
City: {patient.get('city', 'N/A')}
ZIP: {patient.get('zip', 'N/A')}
Country: {patient.get('country_id', ['N/A', 'N/A'])[1] if isinstance(patient.get('country_id'), list) else 'N/A'}
"""
        
        return details.strip()
        
    except Exception as e:
        logger.error(f"Error in get_patient_details_odoo: {str(e)}")
        return f"Error retrieving patient details: {str(e)}"


def create_patient_odoo(
    name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    street: Optional[str] = None,
    city: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Create a new patient in Odoo.
    
    RBAC: Only staff (doctor, admin, owner) can create patients.
    
    Args:
        name: Patient full name (required)
        phone: Patient phone number
        email: Patient email
        street: Street address
        city: City
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String confirming patient creation with new ID
    """
    try:
        # RBAC Check - only staff can create patients
        if requesting_user_role not in ["doctor", "owner", "admin"]:
            log_access_attempt(
                requesting_user_id or "unknown",
                requesting_user_role or "unknown",
                "create_patient",
                "patient",
                None,
                False
            )
            return get_permission_denied_message(requesting_user_role or "unknown", "create_patients")
        
        log_access_attempt(
            requesting_user_id,
            requesting_user_role,
            "create_patient",
            "patient",
            None,
            True
        )
        
        # Create patient in Odoo
        patient_id = odoo_client.create_patient(
            name=name,
            phone=phone,
            email=email,
            street=street,
            city=city
        )
        
        return f"Successfully created patient '{name}' with ID: {patient_id}"
        
    except Exception as e:
        logger.error(f"Error in create_patient_odoo: {str(e)}")
        return f"Error creating patient: {str(e)}"


def update_patient_odoo(
    patient_id: int,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    street: Optional[str] = None,
    city: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Update patient information in Odoo.
    
    RBAC: Patients can update their own info, staff can update all.
    
    Args:
        patient_id: Odoo patient ID
        phone: New phone number
        email: New email
        street: New street address
        city: New city
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String confirming update
    """
    try:
        # RBAC Check
        if requesting_user_role == "patient":
            if str(patient_id) != requesting_user_id:
                log_access_attempt(
                    requesting_user_id,
                    requesting_user_role,
                    "update_patient",
                    "patient",
                    patient_id,
                    False
                )
                return get_permission_denied_message(requesting_user_role, "update_other_patients")
        elif requesting_user_role not in ["doctor", "owner", "admin"]:
            log_access_attempt(
                requesting_user_id or "unknown",
                requesting_user_role or "unknown",
                "update_patient",
                "patient",
                patient_id,
                False
            )
            return get_permission_denied_message(requesting_user_role or "unknown", "update_patients")
        
        log_access_attempt(
            requesting_user_id,
            requesting_user_role,
            "update_patient",
            "patient",
            patient_id,
            True
        )
        
        # Build update data
        update_data = {}
        if phone:
            update_data['phone'] = phone
        if email:
            update_data['email'] = email
        if street:
            update_data['street'] = street
        if city:
            update_data['city'] = city
        
        if not update_data:
            return "No fields to update"
        
        # Update patient in Odoo
        success = odoo_client.update_patient(patient_id, **update_data)
        
        if success:
            updated_fields = ", ".join(update_data.keys())
            return f"Successfully updated patient {patient_id}. Updated fields: {updated_fields}"
        else:
            return f"Failed to update patient {patient_id}"
        
    except Exception as e:
        logger.error(f"Error in update_patient_odoo: {str(e)}")
        return f"Error updating patient: {str(e)}"


def get_doctors_list_odoo(
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Get list of available doctors from Odoo.
    
    RBAC: All authenticated users can view doctors list.
    
    Args:
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with list of doctors
    """
    try:
        # RBAC Check - all authenticated users can view doctors
        if not requesting_user_role:
            return get_permission_denied_message("unknown", "view_doctors")
        
        log_access_attempt(
            requesting_user_id,
            requesting_user_role,
            "get_doctors_list",
            "doctor",
            None,
            True
        )
        
        # Get doctors from Odoo
        doctors = odoo_client.get_doctors(limit=20)
        
        if not doctors:
            return "No doctors found in the system"
        
        # Format doctors list
        results = []
        for doctor in doctors:
            results.append(
                f"- Dr. {doctor.get('name', 'N/A')} (ID: {doctor.get('id')})\n"
                f"  Email: {doctor.get('work_email', 'N/A')}\n"
                f"  Phone: {doctor.get('work_phone', 'N/A')}"
            )
        
        return f"Available Doctors ({len(results)}):\n\n" + "\n\n".join(results)
        
    except Exception as e:
        logger.error(f"Error in get_doctors_list_odoo: {str(e)}")
        return f"Error retrieving doctors list: {str(e)}"


# Tool registry for Alex agent
ALEX_ODOO_TOOLS = {
    "search_patient": search_patient_odoo,
    "get_patient_details": get_patient_details_odoo,
    "create_patient": create_patient_odoo,
    "update_patient": update_patient_odoo,
    "get_doctors_list": get_doctors_list_odoo,
}
