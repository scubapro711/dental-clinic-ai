"""
Appointments API Endpoints

Provides appointment data for dashboard widgets
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
import logging

from app.database import get_db
from app.integrations.odoo_client_v2 import OdooClientV2
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Odoo client
odoo_client = OdooClientV2(
    url=settings.ODOO_URL,
    db=settings.ODOO_DB,
    username=settings.ODOO_USERNAME,
    password=settings.ODOO_PASSWORD
)


@router.get("/today")
async def get_todays_appointments(
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get today's appointments from Odoo
    
    Returns list of appointments with patient info
    """
    try:
        # Connect to Odoo
        if not odoo_client.authenticate():
            raise HTTPException(status_code=500, detail="Failed to connect to Odoo")
        
        # Get today's date range
        today = date.today()
        start_datetime = datetime.combine(today, datetime.min.time())
        end_datetime = datetime.combine(today, datetime.max.time())
        
        # Search for today's appointments
        appointment_ids = odoo_client.models.execute_kw(
            odoo_client.db,
            odoo_client.uid,
            odoo_client.password,
            'medical.appointment',
            'search',
            [[
                ('appointment_sdate', '>=', start_datetime.strftime('%Y-%m-%d %H:%M:%S')),
                ('appointment_sdate', '<=', end_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            ]]
        )
        
        if not appointment_ids:
            logger.info("No appointments found for today")
            return []
        
        # Read appointment details
        appointments = odoo_client.models.execute_kw(
            odoo_client.db,
            odoo_client.uid,
            odoo_client.password,
            'medical.appointment',
            'read',
            [appointment_ids],
            {'fields': [
                'id',
                'patient_id',
                'doctor_id',
                'appointment_sdate',
                'appointment_edate',
                'duration',
                'patient_status',
                'room',
                'clinic_center'
            ]}
        )
        
        # Transform to frontend format
        result = []
        for apt in appointments:
            # Get patient name
            patient_name = "Unknown"
            if apt.get('patient_id'):
                patient_id = apt['patient_id'][0] if isinstance(apt['patient_id'], list) else apt['patient_id']
                try:
                    patient = odoo_client.models.execute_kw(
                        odoo_client.db,
                        odoo_client.uid,
                        odoo_client.password,
                        'medical.patient',
                        'read',
                        [patient_id],
                        {'fields': ['partner_id']}
                    )
                    if patient and patient[0].get('partner_id'):
                        partner_id = patient[0]['partner_id'][0] if isinstance(patient[0]['partner_id'], list) else patient[0]['partner_id']
                        partner = odoo_client.models.execute_kw(
                            odoo_client.db,
                            odoo_client.uid,
                            odoo_client.password,
                            'res.partner',
                            'read',
                            [partner_id],
                            {'fields': ['name']}
                        )
                        if partner:
                            patient_name = partner[0]['name']
                except Exception as e:
                    logger.error(f"Error fetching patient name: {e}")
            
            # Get doctor name
            doctor_name = "Unknown"
            if apt.get('doctor_id'):
                doctor_id = apt['doctor_id'][0] if isinstance(apt['doctor_id'], list) else apt['doctor_id']
                try:
                    doctor = odoo_client.models.execute_kw(
                        odoo_client.db,
                        odoo_client.uid,
                        odoo_client.password,
                        'medical.physician',
                        'read',
                        [doctor_id],
                        {'fields': ['name']}
                    )
                    if doctor:
                        doctor_name = doctor[0]['name']
                except Exception as e:
                    logger.error(f"Error fetching doctor name: {e}")
            
            result.append({
                'id': apt['id'],
                'patient_id': apt.get('patient_id', [None])[0] if isinstance(apt.get('patient_id'), list) else apt.get('patient_id'),
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'appointment_start': apt.get('appointment_sdate'),
                'appointment_end': apt.get('appointment_edate'),
                'duration': apt.get('duration'),
                'status': apt.get('patient_status', 'pending'),
                'treatment_type': 'General',  # TODO: Add treatment type field
                'is_first_visit': False,  # TODO: Add first visit detection
                'room': apt.get('room'),
                'clinic_center': apt.get('clinic_center')
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
    db: Session = Depends(get_db)
):
    """
    Get specific appointment details
    """
    try:
        if not odoo_client.authenticate():
            raise HTTPException(status_code=500, detail="Failed to connect to Odoo")
        
        appointment = odoo_client.models.execute_kw(
            odoo_client.db,
            odoo_client.uid,
            odoo_client.password,
            'medical.appointment',
            'read',
            [appointment_id],
            {'fields': [
                'id',
                'patient_id',
                'doctor_id',
                'appointment_sdate',
                'appointment_edate',
                'duration',
                'patient_status',
                'room',
                'clinic_center'
            ]}
        )
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return appointment[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching appointment {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
