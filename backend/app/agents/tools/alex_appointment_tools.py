from app.integrations.odoo_client import OdooClient
"""
Fixed version of alex_appointment_tools.py with Odoo days_ahead fix
Replace: backend/app/agents/tools/alex_appointment_tools.py
"""

from langchain.tools import tool
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)


@tool
def get_available_slots_tool(
    days_ahead: int = 7,
    doctor_id: Optional[int] = None,
    duration_minutes: int = 30
) -> Dict[str, Any]:
    """
    Get available appointment slots for the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        doctor_id: Specific doctor ID (None = all doctors)
        duration_minutes: Required duration in minutes (default: 30)
    
    Returns:
        Dict with success status, available slots, and message
    """
    try:
        logger.info(f"Getting available slots: days_ahead={days_ahead}, doctor_id={doctor_id}, duration={duration_minutes}")
        
        # Initialize Odoo client
        odoo = OdooClient()
        
        # ✅ FIX: Calculate date range from days_ahead
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        # ✅ FIX: Call Odoo without days_ahead parameter
        # Pass date range instead
        slots = odoo.get_available_slots(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            doctor_id=doctor_id,
            duration_minutes=duration_minutes
        )
        
        if not slots:
            return {
                "success": True,
                "data": {
                    "slots": [],
                    "count": 0,
                    "message": f"No available slots found for the next {days_ahead} days"
                },
                "message": "No available slots found"
            }
        
        return {
            "success": True,
            "data": {
                "slots": slots,
                "count": len(slots),
                "days_ahead": days_ahead,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "message": f"Found {len(slots)} available slots"
        }
    
    except Exception as e:
        logger.error(f"Error in get_available_slots_tool: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": "Failed to get available slots"
        }


@tool
def create_appointment_tool(
    patient_id: int,
    doctor_id: int,
    appointment_date: str,
    duration_minutes: int = 30,
    appointment_type: str = "checkup",
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new appointment for a patient.
    
    Args:
        patient_id: ID of the patient
        doctor_id: ID of the doctor
        appointment_date: Date and time in ISO format (e.g., "2025-10-15T14:30:00")
        duration_minutes: Duration in minutes (default: 30)
        appointment_type: Type of appointment (checkup, cleaning, emergency, etc.)
        notes: Additional notes
    
    Returns:
        Dict with success status, appointment details, and message
    """
    try:
        logger.info(f"Creating appointment: patient={patient_id}, doctor={doctor_id}, date={appointment_date}")
        
        odoo = OdooClient()
        
        appointment = odoo.create_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            duration_minutes=duration_minutes,
            appointment_type=appointment_type,
            notes=notes
        )
        
        return {
            "success": True,
            "data": appointment,
            "message": "Appointment created successfully"
        }
    
    except Exception as e:
        logger.error(f"Error in create_appointment_tool: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": "Failed to create appointment"
        }


@tool
def update_appointment_tool(
    appointment_id: int,
    new_date: Optional[str] = None,
    new_doctor_id: Optional[int] = None,
    new_duration: Optional[int] = None,
    new_type: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing appointment.
    
    Args:
        appointment_id: ID of the appointment to update
        new_date: New date and time (ISO format)
        new_doctor_id: New doctor ID
        new_duration: New duration in minutes
        new_type: New appointment type
        notes: Additional notes
    
    Returns:
        Dict with success status, updated appointment, and message
    """
    try:
        logger.info(f"Updating appointment {appointment_id}")
        
        odoo = OdooClient()
        
        update_data = {}
        if new_date:
            update_data['appointment_date'] = new_date
        if new_doctor_id:
            update_data['doctor_id'] = new_doctor_id
        if new_duration:
            update_data['duration_minutes'] = new_duration
        if new_type:
            update_data['appointment_type'] = new_type
        if notes:
            update_data['notes'] = notes
        
        appointment = odoo.update_appointment(appointment_id, update_data)
        
        return {
            "success": True,
            "data": appointment,
            "message": "Appointment updated successfully"
        }
    
    except Exception as e:
        logger.error(f"Error in update_appointment_tool: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": "Failed to update appointment"
        }


@tool
def cancel_appointment_tool(
    appointment_id: int,
    reason: Optional[str] = None,
    send_notification: bool = True
) -> Dict[str, Any]:
    """
    Cancel an appointment.
    
    Args:
        appointment_id: ID of the appointment to cancel
        reason: Reason for cancellation
        send_notification: Whether to notify the patient
    
    Returns:
        Dict with success status, cancelled appointment, and message
    """
    try:
        logger.info(f"Cancelling appointment {appointment_id}")
        
        odoo = OdooClient()
        
        appointment = odoo.cancel_appointment(
            appointment_id=appointment_id,
            reason=reason,
            send_notification=send_notification
        )
        
        return {
            "success": True,
            "data": appointment,
            "message": "Appointment cancelled successfully"
        }
    
    except Exception as e:
        logger.error(f"Error in cancel_appointment_tool: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": "Failed to cancel appointment"
        }


@tool
def search_appointments_tool(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    appointment_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for appointments with filters.
    
    Args:
        patient_id: Filter by patient
        doctor_id: Filter by doctor
        date_from: Start date (ISO format)
        date_to: End date (ISO format)
        status: Filter by status (scheduled, completed, cancelled, no-show)
        appointment_type: Filter by type
    
    Returns:
        Dict with success status, list of appointments, and message
    """
    try:
        logger.info(f"Searching appointments with filters")
        
        odoo = OdooClient()
        
        appointments = odoo.search_appointments(
            patient_id=patient_id,
            doctor_id=doctor_id,
            date_from=date_from,
            date_to=date_to,
            status=status,
            appointment_type=appointment_type
        )
        
        return {
            "success": True,
            "data": {
                "appointments": appointments,
                "count": len(appointments)
            },
            "message": f"Found {len(appointments)} appointments"
        }
    
    except Exception as e:
        logger.error(f"Error in search_appointments_tool: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": "Failed to search appointments"
        }

