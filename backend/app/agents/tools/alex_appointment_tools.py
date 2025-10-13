
"""
Basic Appointment Management Tools for Alex (Reception Agent)

These tools provide the core functionality for managing appointments:
- Create a new appointment
- Update an existing appointment
- Cancel an appointment
- Search for appointments

All tools integrate with Odoo for calendar management.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from pydantic import BaseModel, Field

from app.integrations.odoo_client_v3 import OdooClientV3

logger = logging.getLogger(__name__)

# ============================================================================
# Tool 1: Create Appointment
# ============================================================================

class CreateAppointmentInput(BaseModel):
    """Input schema for creating an appointment."""
    patient_id: int = Field(..., description="Patient ID")
    doctor_id: int = Field(..., description="Doctor ID")
    start_time: str = Field(..., description="Start time in YYYY-MM-DD HH:MM:SS format")
    duration_minutes: int = Field(30, description="Duration in minutes")
    subject: Optional[str] = Field(None, description="Subject of the appointment")
    notes: Optional[str] = Field(None, description="Additional notes")

def create_appointment_tool(
    patient_id: int,
    doctor_id: int,
    start_time: str,
    duration_minutes: int = 30,
    subject: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new appointment for a patient."""
    try:
        odoo = OdooClientV3()
        appointment_id = odoo.create_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            start_time=start_time,
            duration_minutes=duration_minutes,
            subject=subject,
            notes=notes,
        )
        return {
            "success": True,
            "appointment_id": appointment_id,
            "message": f"Appointment created successfully with ID: {appointment_id}"
        }
    except Exception as e:
        logger.error(f"Error in create_appointment_tool: {str(e)}")
        return {"success": False, "error": f"Error creating appointment: {str(e)}"}

# ============================================================================
# Tool 2: Update Appointment
# ============================================================================

class UpdateAppointmentInput(BaseModel):
    """Input schema for updating an appointment."""
    appointment_id: int = Field(..., description="Appointment ID to update")
    start_time: Optional[str] = Field(None, description="New start time in YYYY-MM-DD HH:MM:SS format")
    duration_minutes: Optional[int] = Field(None, description="New duration in minutes")
    doctor_id: Optional[int] = Field(None, description="New doctor ID")
    subject: Optional[str] = Field(None, description="New subject")
    notes: Optional[str] = Field(None, description="New notes")
    status: Optional[str] = Field(None, description="New status (e.g., confirmed, done, cancel)")

def update_appointment_tool(
    appointment_id: int,
    start_time: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    doctor_id: Optional[int] = None,
    subject: Optional[str] = None,
    notes: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates an existing appointment."""
    try:
        odoo = OdooClientV3()
        success = odoo.update_appointment(
            appointment_id=appointment_id,
            start_time=start_time,
            duration_minutes=duration_minutes,
            doctor_id=doctor_id,
            subject=subject,
            notes=notes,
            status=status,
        )
        return {
            "success": success,
            "message": f"Appointment {appointment_id} updated successfully." if success else f"Failed to update appointment {appointment_id}."
        }
    except Exception as e:
        logger.error(f"Error in update_appointment_tool: {str(e)}")
        return {"success": False, "error": f"Error updating appointment: {str(e)}"}

# ============================================================================
# Tool 3: Cancel Appointment
# ============================================================================

class CancelAppointmentInput(BaseModel):
    """Input schema for cancelling an appointment."""
    appointment_id: int = Field(..., description="Appointment ID to cancel")
    reason: str = Field("Cancelled by user", description="Reason for cancellation")

def cancel_appointment_tool(appointment_id: int, reason: str = "Cancelled by user") -> Dict[str, Any]:
    """Cancels an appointment."""
    try:
        odoo = OdooClientV3()
        success = odoo.cancel_appointment(appointment_id=appointment_id, reason=reason)
        return {
            "success": success,
            "message": f"Appointment {appointment_id} cancelled successfully." if success else f"Failed to cancel appointment {appointment_id}."
        }
    except Exception as e:
        logger.error(f"Error in cancel_appointment_tool: {str(e)}")
        return {"success": False, "error": f"Error cancelling appointment: {str(e)}"}

# ============================================================================
# Tool 4: Search Appointments
# ============================================================================

class SearchAppointmentsInput(BaseModel):
    """Input schema for searching appointments."""
    patient_id: Optional[int] = Field(None, description="Filter by patient ID")
    doctor_id: Optional[int] = Field(None, description="Filter by doctor ID")
    start_date: Optional[str] = Field(None, description="Start of the date range (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End of the date range (YYYY-MM-DD)")
    status: Optional[str] = Field(None, description="Filter by appointment status")
    limit: int = Field(100, description="Maximum number of appointments to return")

def search_appointments_tool(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Searches for appointments with various filters."""
    try:
        odoo = OdooClientV3()
        appointments = odoo.search_appointments(
            patient_id=patient_id,
            doctor_id=doctor_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            limit=limit,
        )
        return {"success": True, "appointments": appointments}
    except Exception as e:
        logger.error(f"Error in search_appointments_tool: {str(e)}")
        return {"success": False, "error": f"Error searching appointments: {str(e)}"}

