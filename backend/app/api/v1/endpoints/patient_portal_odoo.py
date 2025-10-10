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
from app.core.auth import get_current_user
from app.models.user import User
from app.integrations.odoo_client_v2 import OdooClientV2, OdooConnectionError

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Odoo client
try:
    odoo_client = OdooClientV2()
except Exception as e:
    logger.error(f"Failed to initialize Odoo client: {e}")
    odoo_client = None


def get_odoo_patient_id(user: User) -> Optional[int]:
    """
    Get Odoo patient ID for a user.
    
    For now, we'll search by email. In production, this should be stored
    in a user-patient mapping table.
    """
    if not odoo_client:
        return None
    
    try:
        # Search for patient by email
        patients = odoo_client.search_patients(email=user.email)
        if patients and len(patients) > 0:
            # patients is a list of dicts, get the ID from the first one
            patient = patients[0]
            if isinstance(patient, dict) and 'id' in patient:
                return patient['id']
            elif isinstance(patient, int):
                return patient
        return None
    except Exception as e:
        logger.error(f"Error finding patient ID for user {user.email}: {e}")
        import traceback
        traceback.print_exc()
        return None


@router.get("/patient/profile")
async def get_patient_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current patient profile from Odoo"""
    if not odoo_client:
        raise HTTPException(status_code=503, detail="Odoo service unavailable")
    
    try:
        patient_id = get_odoo_patient_id(current_user)
        
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
        patient = odoo_client.get_patient_by_id(patient_id)
        
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
        
    except Exception as e:
        logger.error(f"Error fetching patient profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")


@router.get("/patient/health-score")
async def get_health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient's dental health score
    
    This is calculated based on:
    - Appointment frequency
    - Treatment completion
    - Preventive care adherence
    """
    if not odoo_client:
        raise HTTPException(status_code=503, detail="Odoo service unavailable")
    
    try:
        patient_id = get_odoo_patient_id(current_user)
        
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
        appointments = odoo_client.get_appointments(
            patient_id=patient_id,
            limit=10
        )
        
        # Calculate score based on appointment history
        score = 70  # Base score
        factors = []
        recommendations = []
        
        # Check recent appointments
        recent_appointments = [
            apt for apt in appointments 
            if apt.get('appointment_sdate') and 
            datetime.fromisoformat(apt['appointment_sdate']) > datetime.now() - timedelta(days=180)
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
            if apt.get('appointment_sdate') and 
            datetime.fromisoformat(apt['appointment_sdate']) > datetime.now()
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
    db: Session = Depends(get_db)
):
    """Get patient's appointments from Odoo"""
    if not odoo_client:
        raise HTTPException(status_code=503, detail="Odoo service unavailable")
    
    try:
        patient_id = get_odoo_patient_id(current_user)
        
        if not patient_id:
            return {
                "appointments": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
        
        # Fetch appointments from Odoo
        all_appointments = odoo_client.get_appointments(
            patient_id=patient_id,
            limit=limit + offset  # Fetch more to handle filtering
        )
        
        # Parse and format appointments
        formatted_appointments = []
        now = datetime.now()
        
        for apt in all_appointments:
            apt_date_str = apt.get('appointment_sdate')
            if not apt_date_str:
                continue
            
            try:
                apt_datetime = datetime.fromisoformat(apt_date_str)
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
                "type": apt.get('appointment_type') or "General Checkup",
                "duration": "30 min",  # Default, could be calculated
                "status": apt_status,
                "notes": apt.get('notes') or "",
                "location": "Main Clinic"  # Could be from Odoo
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
    db: Session = Depends(get_db)
):
    """Get list of doctors from Odoo"""
    if not odoo_client:
        raise HTTPException(status_code=503, detail="Odoo service unavailable")
    
    try:
        doctors = odoo_client.get_doctors()
        
        formatted_doctors = []
        for doctor in doctors:
            formatted_doctors.append({
                "id": doctor['id'],
                "name": doctor.get('name', 'Unknown'),
                "email": doctor.get('work_email'),
                "phone": doctor.get('work_phone'),
                "specialization": "General Dentistry",  # Could be from Odoo
                "available": True,  # Could be calculated from schedule
                "image_url": None  # Could be from Odoo
            })
        
        return {
            "doctors": formatted_doctors,
            "total": len(formatted_doctors)
        }
        
    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch doctors")


@router.get("/appointments/available-slots")
async def get_available_slots(
    doctor_id: int = Query(..., description="Doctor ID"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available time slots for a doctor on a specific date
    
    This is a simplified version. In production, this should:
    1. Check doctor's working hours
    2. Check existing appointments
    3. Consider appointment duration
    4. Handle breaks and holidays
    """
    if not odoo_client:
        raise HTTPException(status_code=503, detail="Odoo service unavailable")
    
    try:
        # Parse date
        try:
            slot_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Check if date is in the past
        if slot_date < date.today():
            raise HTTPException(status_code=400, detail="Cannot book appointments in the past")
        
        # Get existing appointments for this doctor on this date
        appointments = odoo_client.get_appointments(
            doctor_id=doctor_id,
            date_from=slot_date.isoformat(),
            date_to=slot_date.isoformat()
        )
        
        # Extract booked times
        booked_times = set()
        for apt in appointments:
            apt_date_str = apt.get('appointment_sdate')
            if apt_date_str:
                try:
                    apt_time = datetime.fromisoformat(apt_date_str).time()
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

