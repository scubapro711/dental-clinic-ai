"""
Agent Tools - Simplified tool integration for agents

This module provides tools that agents can use to interact with Odoo
and other external systems.

Enhanced with RBAC (Role-Based Access Control) for data privacy and security.

Updated to use OdooClient with OdooRPC-compatible interface.
"""

from typing import Optional
from datetime import datetime, timedelta
import logging

from app.integrations.odoo_client import odoo_client
from app.agents.rbac import (
    has_permission,
    can_access_resource,
    get_permission_denied_message,
    log_access_attempt,
    Permission,
)

logger = logging.getLogger(__name__)


def search_patient_tool(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Search for a patient by name or phone number.
    
    RBAC: Patients can only search for themselves, staff can search all.
    
    Args:
        name: Patient name (partial match allowed)
        phone: Patient phone number
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with patient information or "not found" message
    """
    try:
        # RBAC Check: Patients can only search for themselves
        if requesting_user_role == "patient":
            # For patients, we assume they're searching for themselves
            # In real implementation, we'd verify the name/phone matches their record
            log_access_attempt(
                requesting_user_id,
                requesting_user_role,
                "search_patient",
                "patient",
                None,
                True
            )
        elif requesting_user_role in ["doctor", "owner"]:
            # Doctors and owners can search all patients
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
        
        # Use OdooClient instead of direct MockOdoo
        patient_ids = odoo_client.search_patients(name=name, phone=phone)
        
        if not patient_ids:
            return f"No patient found with name='{name}' or phone='{phone}'"
        
        # Get details of first matching patient
        patient = odoo_client.get_patient(patient_ids[0])
        if patient:
            # For patients, only return if it's their own record
            if requesting_user_role == "patient" and str(patient['id']) != requesting_user_id:
                return get_permission_denied_message(requesting_user_role, "view_other_patients")
            
            return f"Found patient: {patient['name']}, Phone: {patient.get('phone', 'N/A')}, Email: {patient.get('email', 'N/A')}, ID: {patient['id']}"
        else:
            return "Patient found but could not retrieve details"
    except Exception as e:
        logger.error(f"Error in search_patient_tool: {str(e)}")
        return f"Error searching patient: {str(e)}"


def get_available_slots_tool(
    days_ahead: int = 7,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Get available appointment slots for the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with available time slots
    """
    try:
        # Calculate date range
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        # Use OdooClient to get available slots
        slots = odoo_client.get_available_slots(date_from, date_to)
        
        if not slots:
            return f"No available slots found in the next {days_ahead} days."
        
        # Format slots for display
        slot_strings = []
        for slot in slots[:10]:  # Show first 10 slots
            # Parse datetime string
            slot_dt = datetime.strptime(slot['datetime'], '%Y-%m-%d %H:%M')
            slot_strings.append(slot_dt.strftime("%A, %B %d at %I:%M %p"))
        
        return "Available appointment slots:\n" + "\n".join(f"- {s}" for s in slot_strings)
    except Exception as e:
        logger.error(f"Error in get_available_slots_tool: {str(e)}")
        return f"Error retrieving available slots: {str(e)}"


def create_appointment_tool(
    patient_name: str,
    patient_phone: str,
    appointment_date: str,
    appointment_time: str,
    treatment_type: str = "General Checkup",
    notes: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Create a new appointment for a patient.
    
    Args:
        patient_name: Full name of the patient
        patient_phone: Patient phone number
        appointment_date: Date in format "YYYY-MM-DD"
        appointment_time: Time in format "HH:MM"
        treatment_type: Type of treatment (default: "General Checkup")
        notes: Optional notes about the appointment
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        Confirmation message with appointment details
    """
    try:
        # Search for existing patient using OdooClient
        patient_ids = odoo_client.search_patients(name=patient_name, phone=patient_phone)
        
        if not patient_ids:
            # Create new patient using OdooClient
            patient_id = odoo_client.create_patient(
                name=patient_name,
                phone=patient_phone,
            )
            logger.info(f"Created new patient: {patient_name} (ID: {patient_id})")
        else:
            patient_id = patient_ids[0]
            logger.info(f"Found existing patient: {patient_name} (ID: {patient_id})")
        
        # Validate date and time format
        try:
            # Validate date format
            datetime.strptime(appointment_date, "%Y-%m-%d")
            # Validate time format
            datetime.strptime(appointment_time, "%H:%M")
        except ValueError as e:
            return f"Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time. Error: {str(e)}"
        
        # Create appointment using OdooClient
        appointment_id = odoo_client.create_appointment(
            patient_id=patient_id,
            date=appointment_date,
            time=appointment_time,
            treatment_type=treatment_type,
            notes=notes,
        )
        
        # Format the datetime for display
        appt_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        
        return (
            f"✅ Appointment created successfully!\n"
            f"Appointment ID: {appointment_id}\n"
            f"Patient: {patient_name}\n"
            f"Date & Time: {appt_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
            f"Treatment: {treatment_type}\n"
            f"Phone: {patient_phone}\n"
            f"Please arrive 10 minutes early for check-in."
        )
    except Exception as e:
        logger.error(f"Error in create_appointment_tool: {str(e)}")
        return f"Error creating appointment: {str(e)}"


def get_patient_appointments_tool(
    patient_name: str,
    patient_phone: Optional[str] = None,
    status: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Get appointments for a patient.
    
    Args:
        patient_name: Patient name
        patient_phone: Patient phone (optional)
        status: Filter by status (scheduled, completed, cancelled)
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with appointment information
    """
    try:
        # Search for patient using OdooClient
        patient_ids = odoo_client.search_patients(name=patient_name, phone=patient_phone)
        
        if not patient_ids:
            return f"No patient found with name '{patient_name}'"
        
        patient_id = patient_ids[0]
        
        # Get appointments using OdooClient
        appointment_ids = odoo_client.search_appointments(patient_id=patient_id, status=status)
        
        if not appointment_ids:
            status_msg = f" with status '{status}'" if status else ""
            return f"No appointments found for {patient_name}{status_msg}"
        
        # Get appointment details
        appointments = []
        for appt_id in appointment_ids[:10]:  # Limit to 10 appointments
            appt = odoo_client.get_appointment(appt_id)
            if appt:
                appointments.append(appt)
        
        # Format appointments
        appt_strings = []
        for appt in appointments:
            date_str = appt.get('date', 'N/A')
            time_str = appt.get('time', 'N/A')
            treatment = appt.get('treatment_type', 'N/A')
            status = appt.get('status', 'unknown')
            appt_strings.append(
                f"Appointment #{appt['id']}: {date_str} at {time_str} - {treatment} ({status})"
            )
        
        return f"Appointments for {patient_name}:\n" + "\n".join(f"- {s}" for s in appt_strings)
    except Exception as e:
        logger.error(f"Error in get_patient_appointments_tool: {str(e)}")
        return f"Error retrieving appointments: {str(e)}"


def get_patient_invoices_tool(
    patient_name: str,
    patient_phone: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Get invoices for a patient.
    
    Args:
        patient_name: Patient name
        patient_phone: Patient phone (optional)
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with invoice information
    """
    try:
        # Search for patient using OdooClient
        patient_ids = odoo_client.search_patients(name=patient_name, phone=patient_phone)
        
        if not patient_ids:
            return f"No patient found with name '{patient_name}'"
        
        patient_id = patient_ids[0]
        
        # Get invoices using OdooClient
        invoice_ids = odoo_client.search_invoices(patient_id=patient_id)
        
        if not invoice_ids:
            return f"No invoices found for {patient_name}"
        
        # Get invoice details
        invoices = []
        for inv_id in invoice_ids[:10]:  # Limit to 10 invoices
            inv = odoo_client.get_invoice(inv_id)
            if inv:
                invoices.append(inv)
        
        # Format invoices
        invoice_strings = []
        for inv in invoices:
            status = inv.get('status', 'unknown')
            amount = inv.get('total_amount', 0)
            date = inv.get('issue_date', 'N/A')
            invoice_strings.append(
                f"Invoice #{inv['id']}: ₪{amount:.2f} - {status} (Date: {date})"
            )
        
        return f"Invoices for {patient_name}:\n" + "\n".join(f"- {s}" for s in invoice_strings)
    except Exception as e:
        logger.error(f"Error in get_patient_invoices_tool: {str(e)}")
        return f"Error retrieving invoices: {str(e)}"


def get_invoice_details_tool(
    invoice_id: int,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Get detailed information about an invoice.
    
    Args:
        invoice_id: Invoice ID
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with detailed invoice information
    """
    try:
        # Get invoice using OdooClient
        invoice = odoo_client.get_invoice_full(invoice_id)
        
        if not invoice:
            return f"Invoice #{invoice_id} not found"
        
        # Format invoice details
        details = (
            f"Invoice #{invoice['id']}\n"
            f"Patient ID: {invoice.get('patient_id', 'N/A')}\n"
            f"Patient Name: {invoice.get('patient_name', 'N/A')}\n"
            f"Issue Date: {invoice.get('issue_date', 'N/A')}\n"
            f"Due Date: {invoice.get('due_date', 'N/A')}\n"
            f"Status: {invoice.get('status', 'unknown')}\n"
            f"Total Amount: ₪{invoice.get('total_amount', 0):.2f}\n"
            f"Paid Amount: ₪{invoice.get('paid_amount', 0):.2f}\n"
            f"Outstanding: ₪{invoice.get('outstanding_amount', 0):.2f}\n"
        )
        
        # Add line items if available
        if invoice.get('line_items'):
            details += "\nLine Items:\n"
            for line in invoice['line_items']:
                details += f"- {line.get('description', 'N/A')}: ₪{line.get('amount', 0):.2f}\n"
        
        return details
    except Exception as e:
        logger.error(f"Error in get_invoice_details_tool: {str(e)}")
        return f"Error retrieving invoice details: {str(e)}"


def update_appointment_status_tool(
    appointment_id: int,
    status: str,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Update appointment status.
    
    Args:
        appointment_id: Appointment ID
        status: New status (scheduled, confirmed, completed, cancelled)
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        Confirmation message
    """
    try:
        # Validate status
        valid_statuses = ['scheduled', 'confirmed', 'completed', 'cancelled']
        if status not in valid_statuses:
            return f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        # Update appointment using OdooClient
        success = odoo_client.update_appointment(appointment_id, status=status)
        
        if success:
            return f"✅ Appointment #{appointment_id} status updated to '{status}'"
        else:
            return f"Failed to update appointment #{appointment_id}"
    except Exception as e:
        logger.error(f"Error in update_appointment_status_tool: {str(e)}")
        return f"Error updating appointment status: {str(e)}"


def get_patient_count_tool(
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Get total number of patients.
    
    Args:
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with patient count
    """
    try:
        count = odoo_client.count_patients()
        return f"Total number of patients: {count}"
    except Exception as e:
        logger.error(f"Error in get_patient_count_tool: {str(e)}")
        return f"Error retrieving patient count: {str(e)}"


def get_appointment_count_tool(
    status: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Get count of appointments.
    
    Args:
        status: Filter by status (optional)
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with appointment count
    """
    try:
        count = odoo_client.count_appointments(status=status)
        status_msg = f" with status '{status}'" if status else ""
        return f"Total number of appointments{status_msg}: {count}"
    except Exception as e:
        logger.error(f"Error in get_appointment_count_tool: {str(e)}")
        return f"Error retrieving appointment count: {str(e)}"


# Export all tools for easy access
__all__ = [
    'search_patient_tool',
    'get_available_slots_tool',
    'create_appointment_tool',
    'get_patient_appointments_tool',
    'get_patient_invoices_tool',
    'get_invoice_details_tool',
    'update_appointment_status_tool',
    'get_patient_count_tool',
    'get_appointment_count_tool',
]
