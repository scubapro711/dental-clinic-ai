"""
Odoo tools for AI agents to interact with dental ERP system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.integrations.odoo_client import odoo_client


@tool
def search_patient(name: Optional[str] = None, phone: Optional[str] = None) -> str:
    """
    Search for a patient by name or phone number.
    
    Args:
        name: Patient name (partial match allowed)
        phone: Patient phone number
        
    Returns:
        String with patient information or "not found" message
    """
    try:
        patient_ids = odoo_client.search_patients(name=name, phone=phone)
        
        if not patient_ids:
            return f"No patient found with name='{name}' or phone='{phone}'"
        
        # Get details of first matching patient
        patient = odoo_client.get_patient(patient_ids[0])
        if patient:
            return f"Found patient: {patient['name']}, Phone: {patient.get('phone', 'N/A')}, Email: {patient.get('email', 'N/A')}"
        else:
            return "Patient found but could not retrieve details"
    except Exception as e:
        return f"Error searching patient: {str(e)}"


@tool
def get_available_appointment_slots(days_ahead: int = 7) -> str:
    """
    Get available appointment slots for the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        
    Returns:
        String with available time slots
    """
    try:
        date_from = datetime.now()
        date_to = date_from + timedelta(days=days_ahead)
        
        slots = odoo_client.get_available_slots(date_from, date_to)
        
        if not slots:
            return "No available slots found"
        
        # Format slots for display
        slot_strings = []
        for slot in slots[:5]:  # Show first 5 slots
            slot_strings.append(slot.strftime("%A, %B %d at %I:%M %p"))
        
        return "Available slots:\n" + "\n".join(f"- {s}" for s in slot_strings)
    except Exception as e:
        return f"Error retrieving available slots: {str(e)}"


@tool
def create_appointment(
    patient_name: str,
    patient_phone: str,
    appointment_date: str,
    notes: Optional[str] = None,
) -> str:
    """
    Create a new appointment for a patient.
    
    Args:
        patient_name: Full name of the patient
        patient_phone: Patient phone number
        appointment_date: Date and time in format "YYYY-MM-DD HH:MM"
        notes: Optional notes about the appointment
        
    Returns:
        Confirmation message with appointment details
    """
    try:
        # Search for existing patient
        patient_ids = odoo_client.search_patients(name=patient_name, phone=patient_phone)
        
        if not patient_ids:
            # Create new patient
            patient_id = odoo_client.create_patient(
                name=patient_name,
                phone=patient_phone,
            )
        else:
            patient_id = patient_ids[0]
        
        # Parse appointment date
        appt_datetime = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
        
        # Create appointment
        appointment_id = odoo_client.create_appointment(
            patient_id=patient_id,
            appointment_date=appt_datetime,
            notes=notes,
        )
        
        return f"Appointment created successfully! Appointment ID: {appointment_id}, Patient: {patient_name}, Date: {appt_datetime.strftime('%A, %B %d at %I:%M %p')}"
    except Exception as e:
        return f"Error creating appointment: {str(e)}"


@tool
def get_patient_appointments(patient_name: str, patient_phone: Optional[str] = None) -> str:
    """
    Get all appointments for a patient.
    
    Args:
        patient_name: Patient name
        patient_phone: Optional patient phone for more accurate search
        
    Returns:
        String with list of appointments
    """
    try:
        # Search for patient
        patient_ids = odoo_client.search_patients(name=patient_name, phone=patient_phone)
        
        if not patient_ids:
            return f"No patient found with name '{patient_name}'"
        
        patient_id = patient_ids[0]
        
        # Get appointments
        appointment_ids = odoo_client.search_appointments(patient_id=patient_id)
        
        if not appointment_ids:
            return f"No appointments found for {patient_name}"
        
        # Get appointment details
        appointments = []
        for appt_id in appointment_ids[:5]:  # Show first 5
            appt = odoo_client.get_appointment(appt_id)
            if appt:
                appointments.append(
                    f"- {appt['appointment_date']} ({appt['state']})"
                )
        
        return f"Appointments for {patient_name}:\n" + "\n".join(appointments)
    except Exception as e:
        return f"Error retrieving appointments: {str(e)}"


@tool
def cancel_appointment(appointment_id: int, reason: Optional[str] = None) -> str:
    """
    Cancel an existing appointment.
    
    Args:
        appointment_id: ID of the appointment to cancel
        reason: Optional cancellation reason
        
    Returns:
        Confirmation message
    """
    try:
        success = odoo_client.cancel_appointment(appointment_id)
        
        if success:
            return f"Appointment {appointment_id} has been cancelled successfully."
        else:
            return f"Failed to cancel appointment {appointment_id}"
    except Exception as e:
        return f"Error cancelling appointment: {str(e)}"


# List of all Odoo tools for agent use
ODOO_TOOLS = [
    search_patient,
    get_available_appointment_slots,
    create_appointment,
    get_patient_appointments,
    cancel_appointment,
]
