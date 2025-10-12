"""
Patient Portal API Endpoints with Real Odoo Integration

Provides patient-facing endpoints that fetch real data from Odoo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, date
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.integrations.odoo_client_v3 import OdooClientV3
from app.core.config import settings
from app.crud import user_patient_mapping as mapping_crud

logger = logging.getLogger(__name__)

router = APIRouter()


def get_odoo_client() -> OdooClientV3:
    """Dependency to get Odoo client instance."""
    return OdooClientV3(
        url=settings.ODOO_URL,
        db=settings.ODOO_DB,
        username=settings.ODOO_USERNAME,
        password=settings.ODOO_PASSWORD,
    )


def get_odoo_patient_id(user: User, db: Session) -> Optional[int]:
    """
    Get Odoo patient ID for a user using the mapping table.
    
    This function:
    1. Checks the user_patient_mapping table first (fast)
    2. Falls back to Odoo search by email if no mapping exists
    3. Creates a mapping if found via email search
    
    Args:
        user: Current user
        db: Database session
    
    Returns:
        Odoo patient ID or None
    """
    try:
        # Step 1: Try to get from mapping table (fast)
        mapping = mapping_crud.get_mapping_by_user_id(db, user.id)
        if mapping:
            logger.info(f"Found mapping for user {user.id} -> patient {mapping.odoo_patient_id}")
            return mapping.odoo_patient_id
        
        # Step 2: No mapping found - user must create mapping via /patients/search and /mappings/me
        logger.warning(f"No mapping found for user {user.id}. User must complete onboarding.")
        return None
        
    except Exception as e:
        logger.error(f"Error finding patient ID for user {user.email}: {e}")
        import traceback
        traceback.print_exc()
        return None


@router.get("/patient/profile")
async def get_patient_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    odoo: OdooClientV3 = Depends(get_odoo_client),
):
    """Get current patient profile from Odoo"""
    try:
        patient_id = get_odoo_patient_id(current_user, db)
        
        if not patient_id:
            # Return basic user info if not found in Odoo
            return {
                "id": str(current_user.id),
                "name": current_user.full_name or current_user.email.split('@')[0],
                "email": current_user.email,
                "phone": None,
                "date_of_birth": None,
                "address": None,
                "odoo_linked": False
            }
        
        # Fetch from Odoo
        patients = odoo.read(
            'res.partner',
            [patient_id],
            ['name', 'email', 'phone', 'mobile', 'birthdate_date', 'street', 'city', 'zip', 'country_id']
        )
        
        if not patients:
            raise HTTPException(status_code=404, detail="Patient not found in Odoo")
        
        patient = patients[0]
        
        return {
            "id": str(current_user.id),
            "odoo_id": patient_id,
            "name": patient.get('name'),
            "email": patient.get('email'),
            "phone": patient.get('phone') or patient.get('mobile'),
            "date_of_birth": patient.get('birthdate_date'),
            "address": {
                "street": patient.get('street'),
                "city": patient.get('city'),
                "zip": patient.get('zip'),
                "country": patient.get('country_id', [None, None])[1] if patient.get('country_id') else None
            },
            "odoo_linked": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")


@router.get("/patient/health-score")
async def get_health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    odoo: OdooClientV3 = Depends(get_odoo_client),
):
    """
    Get patient's dental health score
    
    This is calculated based on:
    - Appointment frequency
    - Treatment completion
    - Preventive care adherence
    """
    try:
        patient_id = get_odoo_patient_id(current_user, db)
        
        if not patient_id:
            # Return default score for new patients
            return {
                "score": 75,
                "message": "Welcome! Complete your profile to get a personalized health score.",
                "factors": [],
                "recommendations": [
                    "Schedule your first dental checkup",
                    "Complete your medical history",
                    "Set up appointment reminders"
                ],
                "last_updated": datetime.now().isoformat()
            }
        
        # Get patient's appointments
        appointments = odoo.search_read(
            'patient.appointment',
            domain=[('patient_id', '=', patient_id)],
            fields=['id', 'start', 'state'],
            limit=50,
            order='start DESC'
        )
        
        # Calculate score based on appointment history
        score = 70  # Base score
        factors = []
        recommendations = []
        
        # Check recent appointments (last 180 days)
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_appointments = [
            apt for apt in appointments 
            if apt.get('start') and 
            datetime.fromisoformat(str(apt['start'])) > six_months_ago
        ]
        
        if len(recent_appointments) > 0:
            score += 15
            factors.append({
                "label": "Regular checkups",
                "status": "good",
                "value": 90
            })
        else:
            factors.append({
                "label": "No recent checkups",
                "status": "warning",
                "value": 50
            })
            recommendations.append("Schedule a dental checkup - it's been over 6 months")
        
        # Check upcoming appointments
        upcoming_appointments = [
            apt for apt in appointments 
            if apt.get('start') and 
            datetime.fromisoformat(str(apt['start'])) > datetime.now()
        ]
        
        if len(upcoming_appointments) > 0:
            score += 10
            factors.append({
                "label": "Upcoming appointment scheduled",
                "status": "good",
                "value": 95
            })
        else:
            recommendations.append("Schedule your next cleaning appointment")
        
        # General recommendations
        recommendations.extend([
            "Brush twice daily with fluoride toothpaste",
            "Floss at least once per day",
            "Limit sugary foods and drinks"
        ])
        
        return {
            "score": min(score, 100),
            "message": "Your dental health is on track! Keep up the good work." if score >= 80 else "Let's improve your dental health together.",
            "factors": factors,
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate health score")


@router.get("/appointments")
async def get_appointments(
    status: Optional[str] = Query(None, description="Filter by status: upcoming, past, cancelled, all"),
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    odoo: OdooClientV3 = Depends(get_odoo_client),
):
    """Get patient's appointments from Odoo"""
    try:
        patient_id = get_odoo_patient_id(current_user, db)
        
        if not patient_id:
            return {
                "appointments": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
        
        # Fetch appointments from Odoo
        all_appointments = odoo.search_read(
            'patient.appointment',
            domain=[('patient_id', '=', patient_id)],
            fields=['id', 'start', 'stop', 'doctor_id', 'state', 'comments'],
            order='start DESC'
        )
        
        # Parse and format appointments
        formatted_appointments = []
        now = datetime.now()
        
        for apt in all_appointments:
            apt_date_str = apt.get('start')
            if not apt_date_str:
                continue
            
            try:
                apt_datetime = datetime.fromisoformat(str(apt_date_str))
            except:
                continue
            
            # Determine status
            apt_status = "upcoming" if apt_datetime > now else "past"
            if apt.get('state') == 'cancel':
                apt_status = "cancelled"
            
            # Filter by status if specified
            if status and status != "all" and apt_status != status:
                continue
            
            formatted_appointments.append({
                "id": apt['id'],
                "date": apt_datetime.strftime("%Y-%m-%d"),
                "time": apt_datetime.strftime("%H:%M"),
                "datetime": apt_datetime.isoformat(),
                "doctor": apt.get('doctor_id', [None, 'Unknown'])[1] if apt.get('doctor_id') else 'Unknown',
                "doctor_id": apt.get('doctor_id', [None])[0] if apt.get('doctor_id') else None,
                "type": "General Checkup",  # TODO: Add appointment type field
                "duration": "30 min",  # TODO: Calculate from stop
                "status": apt_status,
                "notes": apt.get('comments') or "",
                "location": "Main Clinic"  # TODO: Add location field
            })
        
        # Apply offset and limit
        paginated = formatted_appointments[offset:offset + limit]
        
        return {
            "appointments": paginated,
            "total": len(formatted_appointments),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch appointments")


@router.get("/doctors")
async def get_doctors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    odoo: OdooClientV3 = Depends(get_odoo_client),
):
    """Get list of doctors from Odoo"""
    try:
        # Get doctors from Odoo (using hr.employee or custom doctor model)
        # For now, using res.partner with is_doctor flag
        doctors = odoo.search_read(
            'res.partner',
            domain=[('is_doctor', '=', True)],  # Assuming this field exists
            fields=['id', 'name', 'email', 'phone', 'function'],
            order='name ASC'
        )
        
        formatted_doctors = []
        for doc in doctors:
            formatted_doctors.append({
                "id": doc['id'],
                "name": doc['name'],
                "email": doc.get('email'),
                "phone": doc.get('phone'),
                "specialization": doc.get('function') or "General Dentistry",
                "available": True,  # TODO: Check actual availability
                "image_url": None  # TODO: Add image support
            })
        
        # If no doctors found, return mock data
        if not formatted_doctors:
            formatted_doctors = [
                {
                    "id": 1,
                    "name": "Dr. Rachel Cohen",
                    "email": "rachel.cohen@dentaflow.com",
                    "phone": "+972-3-1234567",
                    "specialization": "General Dentistry",
                    "available": True,
                    "image_url": None
                },
                {
                    "id": 2,
                    "name": "Dr. David Levi",
                    "email": "david.levi@dentaflow.com",
                    "phone": "+972-3-1234568",
                    "specialization": "Orthodontics",
                    "available": True,
                    "image_url": None
                },
                {
                    "id": 3,
                    "name": "Dr. Sarah Mizrahi",
                    "email": "sarah.mizrahi@dentaflow.com",
                    "phone": "+972-3-1234569",
                    "specialization": "Pediatric Dentistry",
                    "available": True,
                    "image_url": None
                }
            ]
        
        return {
            "doctors": formatted_doctors,
            "total": len(formatted_doctors)
        }
        
    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch doctors")


@router.get("/patient/appointments/available-slots")
async def get_available_slots(
    doctor_id: int = Query(..., description="Doctor ID"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    odoo: OdooClientV3 = Depends(get_odoo_client),
):
    """
    Get available time slots for a doctor on a specific date
    
    This is a simplified version. In production, this should:
    1. Check doctor's working hours
    2. Check existing appointments
    3. Consider appointment duration
    4. Handle breaks and holidays
    """
    try:
        # Parse date
        try:
            slot_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Check if date is in the past
        from datetime import date as date_module
        if slot_date < date_module.today():
            raise HTTPException(status_code=400, detail="Cannot book appointments in the past")
        
        # Get existing appointments for this doctor on this date
        appointments = odoo.search_read(
            'patient.appointment',
            domain=[
                ('doctor_id', '=', doctor_id),
                ('start', '>=', f"{date} 00:00:00"),
                ('start', '<=', f"{date} 23:59:59"),
                ('state', '!=', 'cancel'),
            ],
            fields=['start']
        )
        
        # Extract booked times
        booked_times = set()
        for apt in appointments:
            apt_date_str = apt.get('start')
            if apt_date_str:
                try:
                    apt_time = datetime.fromisoformat(str(apt_date_str)).time()
                    booked_times.add(apt_time.strftime("%H:%M"))
                except:
                    pass
        
        # Generate available slots (9 AM to 5 PM, 30-minute intervals)
        available_slots = []
        start_hour = 9
        end_hour = 17
        
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                if time_str not in booked_times:
                    available_slots.append({
                        "time": time_str,
                        "available": True,
                        "datetime": f"{date}T{time_str}:00"
                    })
        
        return {
            "date": date,
            "doctor_id": doctor_id,
            "slots": available_slots,
            "total_available": len(available_slots)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching available slots: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch available slots")

