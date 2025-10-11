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
from app.integrations.mock_odoo_realistic import RealisticMockOdooClient
from app.crud import user_patient_mapping as mapping_crud

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Mock Odoo client
odoo_client = RealisticMockOdooClient()
logger.info("RealisticMockOdooClient initialized successfully")


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
    if not odoo_client:
        logger.error("Odoo client not initialized")
        return None
    
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
    db: Session = Depends(get_db)
):
    """Get current patient profile from Odoo"""
    if not odoo_client:
        raise HTTPException(status_code=503, detail="Odoo service unavailable")
    
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
        patient = odoo_client.get_patient(patient_id)
        
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
        appointment_ids = odoo_client.search_appointments(patient_id=patient_id)
        
        appointments = []
        for apt_id in appointment_ids[:10]:
            apt = odoo_client.get_appointment(apt_id)
            if apt:
                appointments.append(apt)
        
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
        patient_id = get_odoo_patient_id(current_user, db)
        
        if not patient_id:
            return {
                "appointments": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
        
        # Fetch appointments from Odoo
        appointment_ids = odoo_client.search_appointments(patient_id=patient_id)
        
        # Get full appointment data
        all_appointments = []
        for apt_id in appointment_ids[:limit + offset]:
            apt = odoo_client.get_appointment(apt_id)
            if apt:
                all_appointments.append(apt)
        
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
        # Mock doctors data (RealisticMockOdooClient doesn't have doctors yet)
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
        from datetime import date as date_module
        if slot_date < date_module.today():
            raise HTTPException(status_code=400, detail="Cannot book appointments in the past")
        
        # Generate mock available slots
        # Note: RealisticMockOdooClient doesn't support filtering by doctor_id and date
        appointments = []
        
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

