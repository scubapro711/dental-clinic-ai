"""
Appointments API Endpoints

Provides appointment data for dashboard widgets
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
import logging

from app.core.database import get_db
from app.integrations.odoo_client import OdooClient
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_odoo_client() -> OdooClient:
    """Dependency to get Odoo client instance."""
    return OdooClient()


@router.get("/today")
async def get_todays_appointments(
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    odoo_client: OdooClient = Depends(get_odoo_client)
):
    """
    Get today's appointments from Odoo
    
    Returns list of appointments with patient info
    """
    try:
        # Get today's date range
        today = date.today()
        start_datetime = datetime.combine(today, datetime.min.time())
        end_datetime = datetime.combine(today, datetime.max.time())
        
        # Search for today's appointments using V3 API
        appointments = odoo_client.search_read(
            'patient.appointment',
            domain=[
                ('start', '>=', start_datetime.strftime('%Y-%m-%d %H:%M:%S')),
                ('start', '<=', end_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            ],
            fields=[
                'id',
                'patient_id',
                'doctor_id',
                'start',
                'stop',
                'duration',
                'appointment_status'
            ]
        )
        
        if not appointments:
            logger.info("No appointments found for today")
            return []
        
        # Transform to frontend format
        result = []
        for apt in appointments:
            # Extract patient info (V3 returns [id, name] for Many2one fields)
            patient_id = None
            patient_name = "Unknown"
            if apt.get('patient_id'):
                if isinstance(apt['patient_id'], list):
                    patient_id = apt['patient_id'][0]
                    patient_name = apt['patient_id'][1] if len(apt['patient_id']) > 1 else "Unknown"
                else:
                    patient_id = apt['patient_id']
            
            # Extract doctor info
            doctor_name = "Unknown"
            if apt.get('doctor_id'):
                if isinstance(apt['doctor_id'], list):
                    doctor_name = apt['doctor_id'][1] if len(apt['doctor_id']) > 1 else "Unknown"
            
            result.append({
                'id': apt['id'],
                'patient_id': patient_id,
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'appointment_start': apt.get('start'),
                'appointment_end': apt.get('stop'),
                'duration': apt.get('duration'),
                'status': apt.get('appointment_status', 'draft'),
                'patient_status': apt.get('appointment_status', 'pending'),
                'treatment_type': 'General',  # TODO: Add treatment type field
                'is_first_visit': apt.get('appointment_status') == 'new'
            })
        
        logger.info(f"Found {len(result)} appointments for today")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching today's appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: int,
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    odoo_client: OdooClient = Depends(get_odoo_client)
):
    """
    Get specific appointment details
    """
    try:
        # Use V3 search_read for single appointment
        appointments = odoo_client.search_read(
            'patient.appointment',
            domain=[('id', '=', appointment_id)],
            fields=[
                'id',
                'patient_id',
                'doctor_id',
                'start',
                'stop',
                'duration',
                'state',
                'patient_status',
                'urgency',
                'comments'
            ],
            limit=1
        )
        
        if not appointments:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        apt = appointments[0]
        
        # Format response
        result = {
            'id': apt['id'],
            'patient_id': apt['patient_id'][0] if isinstance(apt.get('patient_id'), list) else apt.get('patient_id'),
            'patient_name': apt['patient_id'][1] if isinstance(apt.get('patient_id'), list) and len(apt['patient_id']) > 1 else "Unknown",
            'doctor_id': apt['doctor_id'][0] if isinstance(apt.get('doctor_id'), list) else apt.get('doctor_id'),
            'doctor_name': apt['doctor_id'][1] if isinstance(apt.get('doctor_id'), list) and len(apt['doctor_id']) > 1 else "Unknown",
            'appointment_start': apt.get('start'),
            'appointment_end': apt.get('stop'),
            'duration': apt.get('duration'),
            'state': apt.get('state', 'draft'),
            'patient_status': apt.get('patient_status'),
            'urgency': apt.get('urgency', False),
            'comments': apt.get('comments')
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching appointment {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

