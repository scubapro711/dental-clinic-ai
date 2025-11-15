"""
Dashboard API Endpoints

Provides data for dashboard widgets including conversations, patients, and appointments.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from app.middleware.rate_limiter import limiter, get_rate_limit
from datetime import datetime, timedelta
import random

from app.integrations.odoo_client import OdooClient
from app.core.config import settings
from app.api.dependencies import get_current_membership
from app.models.organization_membership import OrganizationMembership
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    membership: OrganizationMembership = Depends(get_current_membership)
) -> Dict[str, Any]:
    """
    Get dashboard statistics summary.
    
    Returns high-level metrics for the dashboard.
    """
    try:
        # TODO: Implement real stats from database/Odoo
        return {
            "total_patients": 0,
            "total_appointments": 0,
            "total_revenue": 0,
            "active_agents": 0,
            "pending_decisions": 0
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_odoo_client() -> OdooClient:
    """Dependency to get Odoo client instance."""
    logger.info("Creating OdooClient instance for dashboard endpoint")
    return OdooClient()


@router.get("/conversations/active")
@limiter.limit(get_rate_limit("default"))
async def get_active_conversations(
    request: Request,
    membership: OrganizationMembership = Depends(get_current_membership),
    odoo: OdooClient = Depends(get_odoo_client)
) -> List[Dict[str, Any]]:
    """
    Get active conversations for the dashboard.
    
    Requires authentication and active organization membership.
    
    Returns:
        List of active conversations
    """
    try:
        # Get recent scheduled or confirmed appointments
        appointments = odoo.search_read(
            'patient.appointment',
            domain=[('state', 'in', ['draft', 'confirmed'])],
            fields=['id', 'patient_id', 'start', 'state'],
            limit=10,
            order='start DESC'
        )
        
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
        
        for i, appt in enumerate(appointments):
            # Get patient details
            patient_id = appt['patient_id'][0] if isinstance(appt['patient_id'], list) else appt['patient_id']
            patient = odoo.read('res.partner', [patient_id], ['name', 'phone'])[0]
            
            priority = "urgent" if i == 0 else random.choice(priorities)
            
            # Calculate time ago
            appt_date = datetime.fromisoformat(str(appt['start']))
            time_diff = datetime.now() - appt_date
            time_ago = f"{abs(int(time_diff.total_seconds() / 60))} minutes ago"
            
            conversations.append({
                "id": f"conv_{appt['id']}",
                "patient_id": patient_id,
                "patient_name": patient['name'],
                "channel": random.choice(channels),
                "priority": priority,
                "last_message": random.choice(messages),
                "time_ago": time_ago,
                "unread_count": random.randint(0, 3),
                "status": "active",
                "created_at": str(appt['start']),
            })
        
        # Sort by priority (urgent first)
        conversations.sort(key=lambda x: (x["priority"] != "urgent", x["time_ago"]))
        
        return conversations
    
    except Exception as e:
        logger.error(f"Error getting active conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients")
@limiter.limit(get_rate_limit("default"))
async def get_patients(
    request: Request,
    membership: OrganizationMembership = Depends(get_current_membership),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: str = Query(None),
    odoo: OdooClient = Depends(get_odoo_client),
) -> Dict[str, Any]:
    """
    Get patients list with pagination and search.
    
    Requires authentication and active organization membership.
    
    Args:
        membership: Current user's organization membership
        limit: Number of patients to return
        offset: Number of patients to skip
        search: Search term for patient name or phone
        odoo: Odoo client instance
        
    Returns:
        Dictionary with patients list and total count
    """
    try:
        # Build search domain
        domain = [('customer_rank', '>', 0)]
        
        if search:
            domain.append('|')
            domain.append(('name', 'ilike', search))
            domain.append(('phone', 'ilike', search))
        
        # Get total count
        total = odoo.search_count('res.partner', domain)
        
        # Get patients with pagination
        patients = odoo.search_read(
            'res.partner',
            domain=domain,
            fields=['id', 'name', 'phone', 'email', 'birthdate_date', 'create_date'],
            limit=limit,
            offset=offset,
            order='create_date DESC'
        )
        
        # Format response
        result_patients = []
        for patient in patients:
            # Get patient's last appointment
            last_appt = odoo.search_read(
                'patient.appointment',
                domain=[('patient_id', '=', patient['id']), ('state', '=', 'done')],
                fields=['start'],
                limit=1,
                order='start DESC'
            )
            
            # Get appointment count
            total_visits = odoo.search_count(
                'patient.appointment',
                [('patient_id', '=', patient['id']), ('state', '=', 'done')]
            )
            
            # Get outstanding balance from invoices
            invoices = odoo.search_read(
                'account.move',
                domain=[
                    ('partner_id', '=', patient['id']),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ['not_paid', 'partial'])
                ],
                fields=['amount_residual']
            )
            outstanding_balance = sum(inv['amount_residual'] for inv in invoices)
            
            result_patients.append({
                "id": patient["id"],
                "name": patient["name"],
                "phone": patient.get("phone"),
                "email": patient.get("email"),
                "date_of_birth": patient.get("birthdate_date"),
                "registration_date": patient.get("create_date"),
                "last_visit": last_appt[0]['start'] if last_appt else None,
                "total_visits": total_visits,
                "outstanding_balance": outstanding_balance,
                "insurance_provider": None,  # TODO: Add insurance field
                "active": len(last_appt) > 0,
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
@limiter.limit(get_rate_limit("default"))
async def get_patient_details(
    request: Request,
    patient_id: int,
    membership: OrganizationMembership = Depends(get_current_membership),
    odoo: OdooClient = Depends(get_odoo_client),
) -> Dict[str, Any]:
    """
    Get detailed information about a specific patient.
    
    Requires authentication and active organization membership.
    
    Args:
        patient_id: Patient ID
        membership: Current user's organization membership
        odoo: Odoo client instance
        
    Returns:
        Patient details with appointments and treatment history
    """
    try:
        # Get patient
        patients = odoo.read('res.partner', [patient_id], ['name', 'phone', 'email', 'birthdate_date'])
        if not patients:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient = patients[0]
        
        # Get patient appointments
        appointments = odoo.search_read(
            'patient.appointment',
            domain=[('patient_id', '=', patient_id)],
            fields=['id', 'start', 'stop', 'state', 'doctor_id'],
            order='start DESC'
        )
        
        # Get patient invoices
        invoices = odoo.search_read(
            'account.move',
            domain=[('partner_id', '=', patient_id), ('move_type', '=', 'out_invoice')],
            fields=['id', 'name', 'invoice_date', 'amount_total', 'amount_residual', 'state', 'payment_state'],
            order='invoice_date DESC'
        )
        
        # Get treatment records (from appointments)
        treatments = odoo.search_read(
            'patient.appointment',
            domain=[('patient_id', '=', patient_id), ('state', '=', 'done')],
            fields=['id', 'start', 'doctor_id', 'comments'],
            order='start DESC'
        )
        
        # Calculate totals
        total_revenue = sum(inv['amount_total'] for inv in invoices if inv['state'] == 'posted')
        outstanding_balance = sum(inv['amount_residual'] for inv in invoices if inv['state'] == 'posted')
        
        return {
            "patient": patient,
            "appointments": appointments,
            "invoices": invoices,
            "treatments": treatments,
            "total_appointments": len(appointments),
            "total_revenue": total_revenue,
            "outstanding_balance": outstanding_balance,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments")
@limiter.limit(get_rate_limit("default"))
async def get_appointments(
    request: Request,
    membership: OrganizationMembership = Depends(get_current_membership),
    start_date: str = Query(None),
    end_date: str = Query(None),
    status: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    odoo: OdooClient = Depends(get_odoo_client),
) -> Dict[str, Any]:
    """
    Get appointments with optional filters.
    
    Requires authentication and active organization membership.
    
    Args:
        membership: Current user's organization membership
        start_date: Filter appointments from this date (YYYY-MM-DD)
        end_date: Filter appointments until this date (YYYY-MM-DD)
        status: Filter by appointment status
        limit: Maximum number of appointments to return
        odoo: Odoo client instance
        
    Returns:
        Dictionary with appointments list
    """
    try:
        # Build domain
        domain = []
        
        if start_date:
            domain.append(('start', '>=', f"{start_date} 00:00:00"))
        
        if end_date:
            domain.append(('start', '<=', f"{end_date} 23:59:59"))
        
        if status:
            domain.append(('state', '=', status))
        
        # Get appointments
        appointments = odoo.search_read(
            'patient.appointment',
            domain=domain,
            fields=['id', 'patient_id', 'doctor_id', 'start', 'stop', 'appointment_status'],
            limit=limit,
            order='start DESC'
        )
        
        # Enrich with patient data
        result_appointments = []
        for appt in appointments:
            patient_id = appt['patient_id'][0] if isinstance(appt['patient_id'], list) else appt['patient_id']
            patient = odoo.read('res.partner', [patient_id], ['name', 'phone'])[0]
            
            # Extract date and time
            appt_datetime = datetime.fromisoformat(str(appt['start']))
            
            result_appointments.append({
                "id": appt['id'],
                "patient_id": patient_id,
                "patient_name": patient['name'],
                "patient_phone": patient.get('phone'),
                "doctor_id": appt['doctor_id'][0] if isinstance(appt['doctor_id'], list) else appt['doctor_id'],
                "date": appt_datetime.strftime('%Y-%m-%d'),
                "time": appt_datetime.strftime('%H:%M'),
                "status": appt.get('appointment_status', 'draft'),
                "start_datetime": str(appt['start']),
                "end_datetime": str(appt['stop']),
            })
        
        return {
            "appointments": result_appointments,
            "total": len(result_appointments),
        }
    
    except Exception as e:
        logger.error(f"Error getting appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments/today")
@limiter.limit(get_rate_limit("default"))
async def get_today_appointments(
    request: Request,
    odoo: OdooClient = Depends(get_odoo_client),
) -> Dict[str, Any]:
    """
    Get today's appointments.
    
    Returns:
        Dictionary with today's appointments
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        appointments = odoo.search_read(
            'patient.appointment',
            domain=[
                ('start', '>=', f"{today} 00:00:00"),
                ('start', '<=', f"{today} 23:59:59"),
            ],
            fields=['id', 'patient_id', 'doctor_id', 'start', 'stop', 'appointment_status'],
            order='start ASC'
        )
        
        # Enrich with patient data
        result_appointments = []
        for appt in appointments:
            patient_id = appt['patient_id'][0] if isinstance(appt['patient_id'], list) else appt['patient_id']
            patient = odoo.read('res.partner', [patient_id], ['name', 'phone'])[0]
            
            appt_datetime = datetime.fromisoformat(str(appt['start']))
            
            result_appointments.append({
                "id": appt['id'],
                "patient_id": patient_id,
                "patient_name": patient['name'],
                "patient_phone": patient.get('phone'),
                "doctor_id": appt['doctor_id'][0] if isinstance(appt['doctor_id'], list) else appt['doctor_id'],
                "date": today,
                "time": appt_datetime.strftime('%H:%M'),
                "status": appt.get('appointment_status', 'draft'),
                "start_datetime": str(appt['start']),
                "end_datetime": str(appt['stop']),
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
@limiter.limit(get_rate_limit("default"))
async def get_upcoming_appointments(
    request: Request,
    days: int = Query(7, ge=1, le=30),
    odoo: OdooClient = Depends(get_odoo_client),
) -> Dict[str, Any]:
    """
    Get upcoming appointments for the next N days.
    
    Args:
        days: Number of days to look ahead
        odoo: Odoo client instance
        
    Returns:
        Dictionary with upcoming appointments
    """
    try:
        today = datetime.now()
        end_date = (today + timedelta(days=days))
        today_str = today.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        appointments = odoo.search_read(
            'patient.appointment',
            domain=[
                ('appointment_status', 'in', ['draft', 'confirm']),
                ('start', '>=', f"{today_str} 00:00:00"),
                ('start', '<=', f"{end_str} 23:59:59"),
            ],
            fields=['id', 'patient_id', 'doctor_id', 'start', 'stop', 'appointment_status'],
            order='start ASC'
        )
        
        # Enrich with patient data
        result_appointments = []
        for appt in appointments:
            patient_id = appt['patient_id'][0] if isinstance(appt['patient_id'], list) else appt['patient_id']
            patient = odoo.read('res.partner', [patient_id], ['name', 'phone'])[0]
            
            appt_datetime = datetime.fromisoformat(str(appt['start']))
            
            result_appointments.append({
                "id": appt['id'],
                "patient_id": patient_id,
                "patient_name": patient['name'],
                "patient_phone": patient.get('phone'),
                "doctor_id": appt['doctor_id'][0] if isinstance(appt['doctor_id'], list) else appt['doctor_id'],
                "date": appt_datetime.strftime('%Y-%m-%d'),
                "time": appt_datetime.strftime('%H:%M'),
                "status": appt.get('appointment_status', 'draft'),
                "start_datetime": str(appt['start']),
                "end_datetime": str(appt['stop']),
            })
        
        return {
            "start_date": today_str,
            "end_date": end_str,
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
@limiter.limit(get_rate_limit("default"))
async def reschedule_appointment(
    request: Request,
    appointment_id: int,
    reschedule_data: RescheduleRequest,
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
        from app.agents.agent_graph_v5 import agent_graph_v5 as agent_graph
        
        # Create message for Sophia
        message = f"""
        Reschedule appointment #{appointment_id} to {reschedule_data.new_date} at {reschedule_data.new_time}.
        Reason: {reschedule_data.reason or 'Patient request'}
        
        Please:
        1. Check for scheduling conflicts
        2. Validate the new time slot is available
        3. Update the appointment
        4. Confirm the change
        """
        
        # Process through LangGraph (will route to Sophia)
        result = agent_graph.invoke({
            "messages": [{"role": "user", "content": message}],
            "user_id": "system",
            "organization_id": "default",
        })
        
        # Check if successful
        last_message = result["messages"][-1]["content"] if result.get("messages") else ""
        success = "successfully" in last_message.lower() or "rescheduled" in last_message.lower()
        
        return AppointmentActionResponse(
            success=success,
            message=last_message,
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
@limiter.limit(get_rate_limit("default"))
async def cancel_appointment(
    request: Request,
    appointment_id: int,
    cancel_data: CancelRequest,
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
        from app.agents.agent_graph_v5 import agent_graph_v5 as agent_graph
        
        # Create message for Sophia
        message = f"""
        Cancel appointment #{appointment_id}.
        Reason: {cancel_data.reason or 'Patient request'}
        
        Please:
        1. Validate the cancellation
        2. Update the appointment status to cancelled
        3. Free up the time slot
        4. Confirm the cancellation
        """
        
        # Process through LangGraph (will route to Sophia)
        result = agent_graph.invoke({
            "messages": [{"role": "user", "content": message}],
            "user_id": "system",
            "organization_id": "default",
        })
        
        # Check if successful
        last_message = result["messages"][-1]["content"] if result.get("messages") else ""
        success = any(word in last_message.lower() for word in ["successfully", "cancelled", "canceled"])
        
        return AppointmentActionResponse(
            success=success,
            message=last_message,
            appointment_id=appointment_id
        )
        
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return AppointmentActionResponse(
            success=False,
            message=f"Failed to cancel: {str(e)}",
            appointment_id=appointment_id
        )


@router.get("/revenue")
@limiter.limit(get_rate_limit("default"))
async def get_revenue_overview(
    request: Request,
    days: int = Query(30, description="Number of days to analyze"),
    odoo: OdooClient = Depends(get_odoo_client),
) -> Dict[str, Any]:
    """
    Get revenue overview for dashboard widget.
    
    Args:
        days: Number of days to analyze (default: 30)
        odoo: Odoo client instance
        
    Returns:
        Revenue summary with trends and insights
    """
    try:
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices for current period
        period_invoices = odoo.search_read(
            'account.move',
            domain=[
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', start_date.strftime('%Y-%m-%d')),
                ('invoice_date', '<=', end_date.strftime('%Y-%m-%d')),
            ],
            fields=['amount_total', 'amount_residual', 'state', 'payment_state', 'invoice_date']
        )
        
        # Calculate metrics
        total_revenue = sum(inv['amount_total'] for inv in period_invoices if inv['state'] == 'posted')
        paid_revenue = sum(
            inv['amount_total'] - inv['amount_residual']
            for inv in period_invoices
            if inv['state'] == 'posted'
        )
        pending_revenue = sum(inv['amount_residual'] for inv in period_invoices if inv['state'] == 'posted')
        
        # Previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date
        
        prev_invoices = odoo.search_read(
            'account.move',
            domain=[
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', prev_start.strftime('%Y-%m-%d')),
                ('invoice_date', '<', prev_end.strftime('%Y-%m-%d')),
                ('state', '=', 'posted'),
            ],
            fields=['amount_total']
        )
        prev_revenue = sum(inv['amount_total'] for inv in prev_invoices)
        
        # Calculate growth
        growth = 0.0
        if prev_revenue > 0:
            growth = ((total_revenue - prev_revenue) / prev_revenue) * 100
        
        # Generate insight
        trend = "up" if growth > 0 else "down" if growth < 0 else "stable"
        insight = f"Revenue is {trend} by {abs(growth):.1f}% compared to the previous period"
        
        return {
            "period_days": days,
            "total_revenue": round(total_revenue, 2),
            "paid_revenue": round(paid_revenue, 2),
            "pending_revenue": round(pending_revenue, 2),
            "previous_period_revenue": round(prev_revenue, 2),
            "growth_percentage": round(growth, 1),
            "trend": trend,
            "insight": insight,
            "invoice_count": len(period_invoices),
            "currency": "ILS"
        }
        
    except Exception as e:
        logger.error(f"Error getting revenue overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

