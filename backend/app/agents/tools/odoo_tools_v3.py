"""
Odoo tools for AI agents - V3 with User Sync

These tools use UserSyncService to ensure a link between PostgreSQL users
and Odoo patients. They are designed to be used by authenticated users.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.integrations.odoo_client import odoo_client
from app.services.user_sync_service import UserSyncService
from app.core.database import get_db

# Helper to get a DB session in a thread-safe way for tools
def _get_db_session() -> Session:
    db_gen = get_db()
    try:
        db = next(db_gen)
        yield db
    finally:
        db.close()

@tool
def get_my_appointments(user_id: str, organization_id: str) -> str:
    """
    Get all upcoming appointments for the current authenticated user.
    
    Args:
        user_id: The UUID of the authenticated user.
        organization_id: The UUID of the user's current organization.
        
    Returns:
        A string with a list of the user's appointments.
    """
    db = next(_get_db_session())
    try:
        sync_service = UserSyncService(db)
        
        # Get the Odoo partner ID for the user
        odoo_partner_id = sync_service.get_odoo_partner_id(
            user_id=UUID(user_id),
            organization_id=UUID(organization_id)
        )
        
        if not odoo_partner_id:
            return "Could not find a linked patient record for your user. Please contact support."
        
        # Get appointments from Odoo
        appointment_ids = odoo_client.search_appointments(patient_id=odoo_partner_id)
        
        if not appointment_ids:
            return "You have no upcoming appointments."
        
        # Get appointment details
        appointments = []
        for appt_id in appointment_ids[:5]:  # Show first 5
            appt = odoo_client.get_appointment(appt_id)
            if appt and appt.get("state") != "cancel":
                appointments.append(
                    f"- On {appt.get('appointment_date')}, status: {appt.get('state')}"
                )
        
        if not appointments:
            return "You have no upcoming appointments."
            
        return "Your upcoming appointments:\n" + "\n".join(appointments)
    except Exception as e:
        return f"Error retrieving your appointments: {str(e)}"

@tool
def book_appointment(user_id: str, organization_id: str, appointment_date: str, notes: Optional[str] = None) -> str:
    """
    Book a new appointment for the current authenticated user.
    
    Args:
        user_id: The UUID of the authenticated user.
        organization_id: The UUID of the user's current organization.
        appointment_date: The desired date and time in "YYYY-MM-DD HH:MM" format.
        notes: Optional notes for the appointment.
        
    Returns:
        A confirmation message with the appointment details.
    """
    db = next(_get_db_session())
    try:
        sync_service = UserSyncService(db)
        
        # Get the Odoo partner ID for the user
        odoo_partner_id = sync_service.get_odoo_partner_id(
            user_id=UUID(user_id),
            organization_id=UUID(organization_id)
        )
        
        if not odoo_partner_id:
            return "Could not find a linked patient record to book an appointment. Please contact support."
        
        # Parse appointment date
        appt_datetime = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
        
        # Create appointment in Odoo
        appointment_id = odoo_client.create_appointment(
            patient_id=odoo_partner_id,
            appointment_date=appt_datetime,
            notes=notes,
        )
        
        patient = odoo_client.get_patient(odoo_partner_id)
        patient_name = patient.get("name", "")
        
        return f"Appointment booked successfully! ID: {appointment_id}, For: {patient_name}, Date: {appt_datetime.strftime('%A, %B %d at %I:%M %p')}"
    except Exception as e:
        return f"Error booking appointment: {str(e)}"

# --- Other general-purpose tools ---

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


# List of all V3 Odoo tools for agent use
ODOO_TOOLS_V3 = [
    get_my_appointments,
    book_appointment,
    get_available_appointment_slots,
]

