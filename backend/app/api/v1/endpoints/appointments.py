"""
Appointments API endpoints
Provides access to appointment data from Odoo with enriched statistics
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.api.dependencies import get_current_membership
from app.core.database import get_db
from app.models.organization_membership import OrganizationMembership
from app.integrations.odoo_client import OdooClient
from app.shared.odoo_queries import (
    get_appointments_today,
    get_appointments_count_by_status,
    get_upcoming_appointments,
    get_new_patients_by_period,
    get_patient_count
)
from sqlalchemy.orm import Session

router = APIRouter()


def get_odoo_client() -> OdooClient:
    """Dependency to get Odoo client instance."""
    return OdooClient()


class AppointmentResponse(BaseModel):
    """Appointment data for frontend widgets"""
    id: int
    patient_name: str
    time: str
    treatment: str
    status: str
    is_first_visit: bool = False
    
    class Config:
        from_attributes = True


class AppointmentSummary(BaseModel):
    """Summary statistics for appointments"""
    total: int
    confirmed: int
    pending: int
    cancelled: int
    first_visits: int
    upcoming_week: int
    new_patients_this_month: int


class EnrichedAppointmentsResponse(BaseModel):
    """Enriched response with appointments and statistics"""
    appointments: List[AppointmentResponse]
    summary: AppointmentSummary
    upcoming: List[AppointmentResponse]


@router.get("/today", response_model=List[AppointmentResponse])
async def get_todays_appointments(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db),
    odoo: OdooClient = Depends(get_odoo_client)
):
    """
    Get today's appointments for the organization
    
    Returns appointments from Odoo for the current day
    """
    try:
        # Get appointments from Odoo
        appointments = get_appointments_today(odoo)
        
        if not appointments:
            return []
        
        # Transform to response format
        return _transform_appointments(appointments)
        
    except Exception as e:
        # Log error but don't expose internal details
        print(f"Error fetching appointments: {str(e)}")
        # Return empty list instead of error to avoid breaking frontend
        return []


@router.get("/today-enriched", response_model=EnrichedAppointmentsResponse)
async def get_todays_appointments_enriched(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db),
    odoo: OdooClient = Depends(get_odoo_client)
):
    """
    Get today's appointments with enriched statistics
    
    Returns:
    - Today's appointments
    - Summary statistics (confirmed, pending, cancelled, etc.)
    - Upcoming appointments for next 7 days
    - New patients this month
    
    This endpoint maximizes value by using ALL available backend functions
    """
    try:
        # Get today's date
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Get today's appointments
        today_appointments = get_appointments_today(odoo)
        
        # Get appointment counts by state
        counts_by_status = get_appointments_count_by_status(odoo, today_str, today_str)
        
        # Get upcoming appointments (next 7 days)
        upcoming_appointments = get_upcoming_appointments(odoo, days_ahead=7)
        
        # Get new patients this month
        new_patients = get_new_patients_by_period(odoo, period='month')
        
        # Count first visits in today's appointments
        first_visits_count = sum(
            1 for apt in today_appointments 
            if apt.get('is_first_visit', False)
        )
        
        # Build summary
        summary = AppointmentSummary(
            total=len(today_appointments),
            confirmed=counts_by_status.get('confirm', 0),
            pending=counts_by_status.get('draft', 0),
            cancelled=counts_by_status.get('cancelled', 0),
            first_visits=first_visits_count,
            upcoming_week=len(upcoming_appointments),
            new_patients_this_month=len(new_patients) if new_patients else 0
        )
        
        # Transform appointments
        transformed_today = _transform_appointments(today_appointments)
        transformed_upcoming = _transform_appointments(upcoming_appointments[:5])  # Top 5
        
        return EnrichedAppointmentsResponse(
            appointments=transformed_today,
            summary=summary,
            upcoming=transformed_upcoming
        )
        
    except Exception as e:
        print(f"Error fetching enriched appointments: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return empty data structure
        return EnrichedAppointmentsResponse(
            appointments=[],
            summary=AppointmentSummary(
                total=0,
                confirmed=0,
                pending=0,
                cancelled=0,
                first_visits=0,
                upcoming_week=0,
                new_patients_this_month=0
            ),
            upcoming=[]
        )


@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments_endpoint(
    days: int = 7,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db),
    odoo: OdooClient = Depends(get_odoo_client)
):
    """
    Get upcoming appointments for the next N days
    
    Args:
        days: Number of days to look ahead (default: 7)
    """
    try:
        appointments = get_upcoming_appointments(odoo, days=days)
        
        if not appointments:
            return []
        
        return _transform_appointments(appointments)
        
    except Exception as e:
        print(f"Error fetching upcoming appointments: {str(e)}")
        return []


def _transform_appointments(appointments: List[Dict[str, Any]]) -> List[AppointmentResponse]:
    """
    Transform Odoo appointment data to API response format
    
    Args:
        appointments: List of appointment dicts from Odoo
        
    Returns:
        List of AppointmentResponse objects
    """
    result = []
    
    for apt in appointments:
        # Parse patient name
        patient_name = apt.get('partner_id', ['Unknown'])[1] if isinstance(apt.get('partner_id'), list) else 'Unknown'
        
        # Format time
        start_datetime = apt.get('start_datetime')
        if isinstance(start_datetime, str):
            try:
                dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                time_str = dt.strftime('%I:%M %p')
            except:
                time_str = start_datetime
        else:
            time_str = 'TBD'
        
        # Get treatment type
        treatment = apt.get('treatment_type', 'General')
        if isinstance(treatment, list):
            treatment = treatment[1] if len(treatment) > 1 else 'General'
        
        # Map Odoo status to widget status
        status_map = {
            'draft': 'pending',
            'confirmed': 'confirmed',
            'done': 'completed',
            'cancel': 'cancelled'
        }
        status = status_map.get(apt.get('state', 'draft'), 'pending')
        
        # Check if first visit
        is_first_visit = apt.get('is_first_visit', False)
        
        result.append(AppointmentResponse(
            id=apt.get('id', 0),
            patient_name=patient_name,
            time=time_str,
            treatment=treatment,
            status=status,
            is_first_visit=is_first_visit
        ))
    
    return result
