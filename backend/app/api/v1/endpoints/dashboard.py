"""
Dashboard API Endpoints

Provides data for dashboard widgets including conversations, patients, and appointments.
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import random

from app.integrations.mock_odoo_realistic import realistic_mock_odoo

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/conversations/active")
async def get_active_conversations() -> List[Dict[str, Any]]:
    """
    Get active conversations for the dashboard.
    
    Returns:
        List of active conversations
    """
    try:
        # Generate mock conversations based on recent appointments
        appointments = realistic_mock_odoo.appointments
        
        # Get recent scheduled or in-progress appointments
        recent_appointments = [
            a for a in appointments
            if a["status"] in ["scheduled", "confirmed"]
        ][:10]
        
        conversations = []
        channels = ["WhatsApp", "Telegram", "Phone"]
        priorities = ["normal", "normal", "normal", "urgent"]
        messages = [
            "שלום, אני רוצה לקבוע תור לניקוי שיניים",
            "האם אפשר לשנות את התור שלי?",
            "יש לי כאב שיניים חזק, אפשר תור דחוף?",
            "תודה על הטיפול, הכל היה מצוין!",
            "מתי אני צריך להגיע לתור?",
            "האם יש לכם זמינות השבוע?",
            "כמה עולה טיפול שורש?",
            "אני רוצה לבטל את התור",
        ]
        
        for i, appt in enumerate(recent_appointments):
            patient = realistic_mock_odoo.get_patient(appt["patient_id"])
            if not patient:
                continue
                
            priority = "urgent" if i == 0 else random.choice(priorities)
            
            conversations.append({
                "id": f"conv_{appt['id']}",
                "patient_id": patient["id"],
                "patient_name": patient["name"],
                "channel": random.choice(channels),
                "priority": priority,
                "last_message": random.choice(messages),
                "time_ago": f"{random.randint(1, 60)} minutes ago",
                "unread_count": random.randint(0, 3),
                "status": "active",
                "created_at": appt["date"],
            })
        
        # Sort by priority (urgent first)
        conversations.sort(key=lambda x: (x["priority"] != "urgent", x["time_ago"]))
        
        return conversations
    
    except Exception as e:
        logger.error(f"Error getting active conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients")
async def get_patients(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: str = Query(None),
) -> Dict[str, Any]:
    """
    Get patients list with pagination and search.
    
    Args:
        limit: Number of patients to return
        offset: Number of patients to skip
        search: Search term for patient name or phone
        
    Returns:
        Dictionary with patients list and total count
    """
    try:
        patients = realistic_mock_odoo.patients
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            patients = [
                p for p in patients
                if search_lower in p["name"].lower() or
                   search_lower in p.get("phone", "")
            ]
        
        total = len(patients)
        
        # Apply pagination
        patients_page = patients[offset:offset + limit]
        
        # Format response
        result_patients = []
        for patient in patients_page:
            result_patients.append({
                "id": patient["id"],
                "name": patient["name"],
                "phone": patient.get("phone"),
                "email": patient.get("email"),
                "date_of_birth": patient.get("date_of_birth"),
                "registration_date": patient.get("registration_date"),
                "last_visit": patient.get("last_visit"),
                "total_visits": patient.get("total_visits", 0),
                "outstanding_balance": patient.get("outstanding_balance", 0),
                "insurance_provider": patient.get("insurance_provider"),
                "active": patient.get("last_visit") is not None,
            })
        
        return {
            "patients": result_patients,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients/{patient_id}")
async def get_patient_details(patient_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific patient.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Patient details with appointments and treatment history
    """
    try:
        patient = realistic_mock_odoo.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get patient appointments
        appointments = [
            a for a in realistic_mock_odoo.appointments
            if a["patient_id"] == patient_id
        ]
        
        # Get patient invoices
        invoices = [
            i for i in realistic_mock_odoo.invoices
            if i["patient_id"] == patient_id
        ]
        
        # Get treatment records
        treatments = [
            t for t in realistic_mock_odoo.treatment_records
            if t["patient_id"] == patient_id
        ]
        
        return {
            "patient": patient,
            "appointments": appointments,
            "invoices": invoices,
            "treatments": treatments,
            "total_appointments": len(appointments),
            "total_revenue": sum(i["total_amount"] for i in invoices),
            "outstanding_balance": sum(i["outstanding_amount"] for i in invoices),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments")
async def get_appointments(
    start_date: str = Query(None),
    end_date: str = Query(None),
    status: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
) -> Dict[str, Any]:
    """
    Get appointments with optional filters.
    
    Args:
        start_date: Filter appointments from this date (YYYY-MM-DD)
        end_date: Filter appointments until this date (YYYY-MM-DD)
        status: Filter by appointment status
        limit: Maximum number of appointments to return
        
    Returns:
        Dictionary with appointments list
    """
    try:
        appointments = realistic_mock_odoo.appointments
        
        # Apply filters
        if start_date:
            appointments = [a for a in appointments if a["date"] >= start_date]
        
        if end_date:
            appointments = [a for a in appointments if a["date"] <= end_date]
        
        if status:
            appointments = [a for a in appointments if a["status"] == status]
        
        # Sort by date
        appointments = sorted(appointments, key=lambda x: x["date"], reverse=True)
        
        # Limit results
        appointments = appointments[:limit]
        
        # Enrich with patient data
        result_appointments = []
        for appt in appointments:
            patient = realistic_mock_odoo.get_patient(appt["patient_id"])
            result_appointments.append({
                **appt,
                "patient_name": patient["name"] if patient else "Unknown",
                "patient_phone": patient.get("phone") if patient else None,
            })
        
        return {
            "appointments": result_appointments,
            "total": len(result_appointments),
        }
    
    except Exception as e:
        logger.error(f"Error getting appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments/today")
async def get_today_appointments() -> Dict[str, Any]:
    """
    Get today's appointments.
    
    Returns:
        Dictionary with today's appointments
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        appointments = [
            a for a in realistic_mock_odoo.appointments
            if a["date"] == today
        ]
        
        # Sort by time
        appointments = sorted(appointments, key=lambda x: x.get("time", "00:00"))
        
        # Enrich with patient data
        result_appointments = []
        for appt in appointments:
            patient = realistic_mock_odoo.get_patient(appt["patient_id"])
            result_appointments.append({
                **appt,
                "patient_name": patient["name"] if patient else "Unknown",
                "patient_phone": patient.get("phone") if patient else None,
            })
        
        return {
            "date": today,
            "appointments": result_appointments,
            "total": len(result_appointments),
        }
    
    except Exception as e:
        logger.error(f"Error getting today's appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments/upcoming")
async def get_upcoming_appointments(days: int = Query(7, ge=1, le=30)) -> Dict[str, Any]:
    """
    Get upcoming appointments for the next N days.
    
    Args:
        days: Number of days to look ahead
        
    Returns:
        Dictionary with upcoming appointments
    """
    try:
        today = datetime.now()
        end_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        
        appointments = [
            a for a in realistic_mock_odoo.appointments
            if a["status"] in ["scheduled", "confirmed"] and
               today_str <= a["date"] <= end_date
        ]
        
        # Sort by date and time
        appointments = sorted(appointments, key=lambda x: (x["date"], x.get("time", "00:00")))
        
        # Enrich with patient data
        result_appointments = []
        for appt in appointments:
            patient = realistic_mock_odoo.get_patient(appt["patient_id"])
            result_appointments.append({
                **appt,
                "patient_name": patient["name"] if patient else "Unknown",
                "patient_phone": patient.get("phone") if patient else None,
            })
        
        return {
            "start_date": today_str,
            "end_date": end_date,
            "appointments": result_appointments,
            "total": len(result_appointments),
        }
    
    except Exception as e:
        logger.error(f"Error getting upcoming appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Appointment Actions (via LangGraph) =====

from pydantic import BaseModel as PydanticBaseModel

class RescheduleRequest(PydanticBaseModel):
    """Request to reschedule an appointment."""
    new_date: str  # YYYY-MM-DD
    new_time: str  # HH:MM
    reason: str | None = None


class CancelRequest(PydanticBaseModel):
    """Request to cancel an appointment."""
    reason: str | None = None


class AppointmentActionResponse(PydanticBaseModel):
    """Response after appointment action."""
    success: bool
    message: str
    appointment_id: int


@router.post("/appointments/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: int,
    request: RescheduleRequest,
) -> AppointmentActionResponse:
    """
    Reschedule an appointment via Sophia (Admin) Agent.
    
    ARCHITECTURE: API → LangGraph → Sophia → reschedule_appointment_tool → Odoo
    
    This uses AI reasoning to:
    - Check for conflicts
    - Validate new time slot
    - Update appointment
    - Notify patient
    """
    try:
        from app.agents.agent_graph_v3 import AgentGraphV3
        
        # Initialize LangGraph
        graph = AgentGraphV3()
        
        # Create message for Sophia
        message = f"""
        Reschedule appointment #{appointment_id} to {request.new_date} at {request.new_time}.
        Reason: {request.reason or 'Patient request'}
        
        Please:
        1. Check for scheduling conflicts
        2. Validate the new time slot is available
        3. Update the appointment
        4. Confirm the change
        """
        
        # Process through LangGraph (will route to Sophia)
        result = graph.process_message(
            message=message,
            user_id="system",
            organization_id="default",
            conversation_id=f"reschedule_{appointment_id}"
        )
        
        # Check if successful
        success = "successfully" in result.get("response", "").lower() or \
                  "rescheduled" in result.get("response", "").lower()
        
        return AppointmentActionResponse(
            success=success,
            message=result.get("response", "Appointment rescheduled"),
            appointment_id=appointment_id
        )
        
    except Exception as e:
        logger.error(f"Error rescheduling appointment: {e}")
        return AppointmentActionResponse(
            success=False,
            message=f"Failed to reschedule: {str(e)}",
            appointment_id=appointment_id
        )


@router.post("/appointments/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    request: CancelRequest,
) -> AppointmentActionResponse:
    """
    Cancel an appointment via Sophia (Admin) Agent.
    
    ARCHITECTURE: API → LangGraph → Sophia → cancel_appointment_tool → Odoo
    
    This uses AI reasoning to:
    - Validate cancellation
    - Check cancellation policy
    - Update appointment status
    - Notify patient
    - Free up the time slot
    """
    try:
        from app.agents.agent_graph_v3 import AgentGraphV3
        
        # Initialize LangGraph
        graph = AgentGraphV3()
        
        # Create message for Sophia
        message = f"""
        Cancel appointment #{appointment_id}.
        Reason: {request.reason or 'Patient request'}
        
        Please:
        1. Validate the cancellation
        2. Update the appointment status to cancelled
        3. Free up the time slot
        4. Confirm the cancellation
        """
        
        # Process through LangGraph (will route to Sophia)
        result = graph.process_message(
            message=message,
            user_id="system",
            organization_id="default",
            conversation_id=f"cancel_{appointment_id}"
        )
        
        # Check if successful
        success = "successfully" in result.get("response", "").lower() or \
                  "cancelled" in result.get("response", "").lower() or \
                  "canceled" in result.get("response", "").lower()
        
        return AppointmentActionResponse(
            success=success,
            message=result.get("response", "Appointment cancelled"),
            appointment_id=appointment_id
        )
        
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return AppointmentActionResponse(
            success=False,
            message=f"Failed to cancel: {str(e)}",
            appointment_id=appointment_id
        )
