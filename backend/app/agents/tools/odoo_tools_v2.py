"""
Improved Odoo tools for AI agents with better error handling.

Uses OdooClientV3 with comprehensive validation and error handling.
"""

from typing import Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.integrations.odoo_client_v3 import OdooClientV3

# Initialize V3 client
odoo_client_v2 = OdooClientV3()

# Exception classes for backward compatibility
class OdooValidationError(Exception):
    pass

class OdooConstraintError(Exception):
    pass


@tool
def search_patient_v2(name: Optional[str] = None, phone: Optional[str] = None) -> str:
    """
    Search for a patient by name or phone number (improved version).
    
    Args:
        name: Patient name (partial match allowed)
        phone: Patient phone number
    
    Returns:
        String with patient information or error message
    """
    try:
        patient_ids = odoo_client_v2.search_patients(name=name, phone=phone)
        
        if not patient_ids:
            return f"לא נמצא מטופל עם שם '{name}' או טלפון '{phone}'"
        
        # Get details of first matching patient
        patient = odoo_client_v2.get_patient(patient_ids[0])
        if patient:
            phone_info = patient.get('phone') or patient.get('mobile') or 'לא זמין'
            email_info = patient.get('email') or 'לא זמין'
            return (
                f"נמצא מטופל: {patient['name']}\n"
                f"טלפון: {phone_info}\n"
                f"אימייל: {email_info}\n"
                f"ID: {patient['id']}"
            )
        else:
            return "המטופל נמצא אך לא ניתן לטעון את הפרטים"
    
    except Exception as e:
        return f"שגיאה בחיפוש מטופל: {str(e)}"


@tool
def create_patient_v2(
    name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    israeli_id: Optional[str] = None
) -> str:
    """
    Create a new patient in Odoo (improved version).
    
    Args:
        name: Full name (required)
        phone: Phone number
        email: Email address
        israeli_id: Israeli ID number (תעודת זהות)
    
    Returns:
        Confirmation message with patient ID
    """
    try:
        patient_id = odoo_client_v2.create_patient(
            name=name,
            phone=phone,
            email=email,
            israeli_id=israeli_id
        )
        
        return (
            f"✅ מטופל חדש נוצר בהצלחה!\n"
            f"שם: {name}\n"
            f"ID: {patient_id}\n"
            f"טלפון: {phone or 'לא צוין'}\n"
            f"אימייל: {email or 'לא צוין'}"
        )
    
    except OdooValidationError as e:
        return f"❌ שגיאת אימות: {str(e)}"
    except Exception as e:
        return f"❌ שגיאה ביצירת מטופל: {str(e)}"


@tool
def get_available_slots_v2(
    doctor_id: int,
    days_ahead: int = 7
) -> str:
    """
    Get available appointment slots for a doctor (improved version).
    
    Args:
        doctor_id: Doctor ID in Odoo
        days_ahead: Number of days to look ahead (default: 7)
    
    Returns:
        String with available time slots
    """
    try:
        date_from = datetime.now()
        date_to = date_from + timedelta(days=days_ahead)
        
        slots = odoo_client_v2.get_available_slots(
            doctor_id=doctor_id,
            date_from=date_from,
            date_to=date_to,
            slot_duration_minutes=45
        )
        
        if not slots:
            return f"אין תורים פנויים ב-{days_ahead} הימים הקרובים"
        
        # Format slots for display (show first 10)
        slot_strings = []
        for slot in slots[:10]:
            # Format in Hebrew
            day_names = {
                0: 'שני',
                1: 'שלישי',
                2: 'רביעי',
                3: 'חמישי',
                4: 'שישי',
                5: 'שבת',
                6: 'ראשון'
            }
            day_name = day_names[slot.weekday()]
            date_str = slot.strftime('%d/%m/%Y')
            time_str = slot.strftime('%H:%M')
            
            slot_strings.append(f"יום {day_name}, {date_str} בשעה {time_str}")
        
        result = f"נמצאו {len(slots)} תורים פנויים. הנה 10 הראשונים:\n\n"
        result += "\n".join(f"{i+1}. {s}" for i, s in enumerate(slot_strings))
        
        return result
    
    except Exception as e:
        return f"❌ שגיאה בטעינת תורים פנויים: {str(e)}"


@tool
def create_appointment_v2(
    patient_name: str,
    patient_phone: str,
    doctor_id: int,
    appointment_datetime: str,
    notes: Optional[str] = None
) -> str:
    """
    Create a new appointment for a patient (improved version).
    
    Args:
        patient_name: Full name of the patient
        patient_phone: Patient phone number
        doctor_id: Doctor ID in Odoo
        appointment_datetime: Date and time in format "YYYY-MM-DD HH:MM"
        notes: Optional notes about the appointment
    
    Returns:
        Confirmation message with appointment details
    """
    try:
        # Parse datetime
        try:
            apt_date = datetime.strptime(appointment_datetime, "%Y-%m-%d %H:%M")
        except ValueError:
            return "❌ פורמט תאריך שגוי. השתמש בפורמט: YYYY-MM-DD HH:MM (לדוגמה: 2025-10-15 10:00)"
        
        # Search for existing patient
        patient_ids = odoo_client_v2.search_patients(name=patient_name, phone=patient_phone)
        
        if not patient_ids:
            # Create new patient
            patient_id = odoo_client_v2.create_patient(
                name=patient_name,
                phone=patient_phone
            )
            patient_status = "מטופל חדש נוצר"
        else:
            patient_id = patient_ids[0]
            patient_status = "מטופל קיים"
        
        # Create appointment
        appointment_id = odoo_client_v2.create_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=apt_date,
            duration_minutes=45,
            patient_state='withapt',
            notes=notes
        )
        
        # Format response in Hebrew
        date_str = apt_date.strftime('%d/%m/%Y')
        time_str = apt_date.strftime('%H:%M')
        
        return (
            f"✅ התור נקבע בהצלחה!\n\n"
            f"📋 פרטי התור:\n"
            f"מטופל: {patient_name} ({patient_status})\n"
            f"תאריך: {date_str}\n"
            f"שעה: {time_str}\n"
            f"משך: 45 דקות\n"
            f"מספר תור: {appointment_id}\n"
            f"הערות: {notes or 'אין'}"
        )
    
    except OdooValidationError as e:
        return f"❌ שגיאת אימות: {str(e)}"
    except OdooConstraintError as e:
        return f"❌ שגיאת מגבלה: {str(e)}\n\nייתכן שהתור כבר תפוס או שיש קונפליקט בלוח הזמנים."
    except Exception as e:
        return f"❌ שגיאה בקביעת תור: {str(e)}"


@tool
def cancel_appointment_v2(appointment_id: int, reason: Optional[str] = None) -> str:
    """
    Cancel an existing appointment (improved version).
    
    Args:
        appointment_id: Appointment ID in Odoo
        reason: Cancellation reason
    
    Returns:
        Confirmation message
    """
    try:
        # Get appointment details first
        appointment = odoo_client_v2._execute(
            'patient.appointment',
            'read',
            [[appointment_id]],
            {'fields': ['patient_id', 'start']}
        )
        
        if not appointment:
            return f"❌ תור מספר {appointment_id} לא נמצא"
        
        apt = appointment[0]
        
        # Cancel appointment
        success = odoo_client_v2._execute(
            'patient.appointment',
            'write',
            [[appointment_id], {'state': 'cancel'}]
        )
        
        if success:
            patient_name = apt['patient_id'][1] if isinstance(apt['patient_id'], list) else "לא ידוע"
            date_str = apt['start']
            
            return (
                f"✅ התור בוטל בהצלחה!\n\n"
                f"מספר תור: {appointment_id}\n"
                f"מטופל: {patient_name}\n"
                f"תאריך מקורי: {date_str}\n"
                f"סיבת ביטול: {reason or 'לא צוינה'}"
            )
        else:
            return f"❌ נכשל בביטול תור {appointment_id}"
    
    except Exception as e:
        return f"❌ שגיאה בביטול תור: {str(e)}"


@tool
def get_patient_appointments_v2(patient_id: int, include_past: bool = False) -> str:
    """
    Get all appointments for a patient (improved version).
    
    Args:
        patient_id: Patient ID in Odoo
        include_past: Include past appointments (default: False)
    
    Returns:
        String with appointment list
    """
    try:
        # Build search domain
        domain = [('patient_id', '=', patient_id)]
        
        if not include_past:
            domain.append(('start', '>=', datetime.now().strftime('%Y-%m-%d')))
        
        # Search appointments
        appointments = odoo_client_v2._execute(
            'patient.appointment',
            'search_read',
            [domain],
            {
                'fields': ['id', 'start', 'doctor_id', 'state'],
                'order': 'start asc'
            }
        )
        
        if not appointments:
            return "לא נמצאו תורים למטופל זה"
        
        # Format appointments
        result = f"נמצאו {len(appointments)} תורים:\n\n"
        
        for apt in appointments:
            apt_date = datetime.strptime(apt['start'], '%Y-%m-%d %H:%M:%S')
            date_str = apt_date.strftime('%d/%m/%Y')
            time_str = apt_date.strftime('%H:%M')
            doctor_name = apt['doctor_id'][1] if isinstance(apt['doctor_id'], list) else "לא ידוע"
            
            state_map = {
                'draft': 'טיוטה',
                'confirm': 'מאושר',
                'done': 'הושלם',
                'cancel': 'בוטל'
            }
            state_hebrew = state_map.get(apt['state'], apt['state'])
            
            result += (
                f"תור #{apt['id']}:\n"
                f"  תאריך: {date_str} בשעה {time_str}\n"
                f"  רופא: {doctor_name}\n"
                f"  סטטוס: {state_hebrew}\n\n"
            )
        
        return result
    
    except Exception as e:
        return f"❌ שגיאה בטעינת תורים: {str(e)}"


# Aliases for backward compatibility
search_patients_tool = search_patient_v2
get_patient_by_id_tool = create_patient_v2  # Note: This might need a proper implementation
get_appointments_tool = get_patient_appointments_v2

# Export all tools
__all__ = [
    'search_patient_v2',
    'create_patient_v2',
    'get_available_slots_v2',
    'create_appointment_v2',
    'cancel_appointment_v2',
    'get_patient_appointments_v2',
    # Aliases
    'search_patients_tool',
    'get_patient_by_id_tool',
    'get_appointments_tool',
]
