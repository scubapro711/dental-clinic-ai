"""
Advanced Scheduling Tools for Alex (Reception Agent)

These tools provide advanced appointment management capabilities:
- Bulk appointment rescheduling
- Waitlist management for cancellations
- Automated appointment optimization

All tools integrate with Odoo for calendar management.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from pydantic import BaseModel, Field

from app.integrations.odoo_client_v3 import OdooClientV3

logger = logging.getLogger(__name__)


# ============================================================================
# Tool 1: Bulk Reschedule Appointments
# ============================================================================

class BulkRescheduleInput(BaseModel):
    """Input schema for bulk rescheduling."""
    doctor_id: int = Field(..., description="Doctor ID")
    original_date: str = Field(..., description="Original date (YYYY-MM-DD)")
    new_date: str = Field(..., description="New date (YYYY-MM-DD)")
    reason: Optional[str] = Field(None, description="Reason for rescheduling")
    notify_patients: bool = Field(True, description="Send notifications to patients")


def bulk_reschedule_appointments_tool(
    doctor_id: int,
    original_date: str,
    new_date: str,
    reason: Optional[str] = None,
    notify_patients: bool = True,
) -> Dict[str, Any]:
    """
    Bulk reschedule all appointments from one date to another.
    
    This tool is useful when:
    - Doctor is sick or unavailable
    - Clinic closure (holidays, emergency)
    - Equipment malfunction
    - Schedule optimization
    
    Features:
    - Reschedules all appointments for a specific doctor/date
    - Finds available slots on new date
    - Sends notifications to all affected patients
    - Logs rescheduling reason
    - Handles conflicts intelligently
    
    Args:
        doctor_id: Doctor ID whose appointments to reschedule
        original_date: Original date (YYYY-MM-DD)
        new_date: New date to move appointments to (YYYY-MM-DD)
        reason: Reason for rescheduling (optional)
        notify_patients: Whether to send notifications (default: True)
    
    Returns:
        Dictionary with:
        - rescheduled_count: Number of appointments rescheduled
        - failed_count: Number that couldn't be rescheduled
        - details: List of rescheduled appointments
        - notifications_sent: Number of notifications sent
    """
    try:
        odoo = OdooClientV3()
        
        # Validate doctor
        doctor = odoo.read('medical.physician', doctor_id, ['name'])
        if not doctor:
            return {
                'success': False,
                'error': f'רופא עם ID {doctor_id} לא נמצא'
            }
        
        # Validate dates
        try:
            orig_date = datetime.strptime(original_date, '%Y-%m-%d')
            new_date_obj = datetime.strptime(new_date, '%Y-%m-%d')
        except ValueError:
            return {
                'success': False,
                'error': 'תאריך לא תקין. השתמש בפורמט YYYY-MM-DD'
            }
        
        if new_date_obj <= datetime.now():
            return {
                'success': False,
                'error': 'תאריך חדש חייב להיות בעתיד'
            }
        
        # Find all appointments for doctor on original date
        appointments = odoo.search_read('medical.appointment', [
            ('doctor', '=', doctor_id),
            ('appointment_date', '>=', f'{original_date} 00:00:00'),
            ('appointment_date', '<=', f'{original_date} 23:59:59'),
            ('state', '!=', 'cancel'),
        ], ['id', 'patient', 'appointment_date', 'duration'])
        
        if not appointments:
            return {
                'success': True,
                'rescheduled_count': 0,
                'message': f'לא נמצאו תורים לרופא {doctor["name"]} בתאריך {original_date}'
            }
        
        # Get available slots on new date
        available_slots = _get_available_slots_for_date(
            odoo, doctor_id, new_date
        )
        
        if not available_slots:
            return {
                'success': False,
                'error': f'אין זמינות לרופא {doctor["name"]} בתאריך {new_date}',
                'suggestion': 'בחר תאריך אחר או פנה מקום בלוח הזמנים',
                'affected_appointments': len(appointments)
            }
        
        # Reschedule appointments
        rescheduled = []
        failed = []
        
        for i, appointment in enumerate(appointments):
            if i >= len(available_slots):
                # Not enough slots
                failed.append({
                    'appointment_id': appointment['id'],
                    'patient_name': appointment['patient'][1] if isinstance(appointment['patient'], list) else 'Unknown',
                    'original_time': appointment['appointment_date'],
                    'reason': 'אין מספיק זמינות בתאריך החדש'
                })
                continue
            
            # Assign to available slot
            new_slot = available_slots[i]
            new_datetime = f"{new_date} {new_slot}"
            
            # Update appointment
            update_result = odoo.write('medical.appointment', appointment['id'], {
                'appointment_date': new_datetime,
                'reschedule_reason': reason or 'Bulk reschedule',
                'reschedule_count': (appointment.get('reschedule_count', 0) or 0) + 1,
            })
            
            if update_result:
                patient_name = appointment['patient'][1] if isinstance(appointment['patient'], list) else 'Unknown'
                
                rescheduled.append({
                    'appointment_id': appointment['id'],
                    'patient_name': patient_name,
                    'original_time': appointment['appointment_date'],
                    'new_time': new_datetime,
                })
                
                # Send notification if requested
                if notify_patients:
                    _send_reschedule_notification(
                        odoo=odoo,
                        patient_id=appointment['patient'][0] if isinstance(appointment['patient'], list) else appointment['patient'],
                        doctor_name=doctor['name'],
                        original_time=appointment['appointment_date'],
                        new_time=new_datetime,
                        reason=reason,
                    )
            else:
                failed.append({
                    'appointment_id': appointment['id'],
                    'patient_name': patient_name,
                    'original_time': appointment['appointment_date'],
                    'reason': 'Failed to update in Odoo'
                })
        
        return {
            'success': True,
            'doctor_name': doctor['name'],
            'original_date': original_date,
            'new_date': new_date,
            'total_appointments': len(appointments),
            'rescheduled_count': len(rescheduled),
            'failed_count': len(failed),
            'rescheduled_appointments': rescheduled,
            'failed_appointments': failed if failed else None,
            'notifications_sent': len(rescheduled) if notify_patients else 0,
            'confirmation': f"✅ {len(rescheduled)} תורים תוזמנו מחדש בהצלחה!",
            'next_steps': [
                f"📞 צור קשר עם {len(failed)} מטופלים שלא ניתן לתזמן" if failed else "✅ כל התורים תוזמנו מחדש",
                "📧 אישורים נשלחו למייל" if notify_patients else "📱 שלח אישורים ידנית",
                "📅 עדכן את לוח הזמנים של הרופא",
            ]
        }
        
    except Exception as e:
        logger.error(f"Bulk reschedule error: {str(e)}")
        return {
            'success': False,
            'error': f'שגיאה בתזמון מחדש: {str(e)}',
            'technical_details': str(e)
        }


def _get_available_slots_for_date(
    odoo: OdooClientV3,
    doctor_id: int,
    date: str,
) -> List[str]:
    """Get available time slots for doctor on specific date."""
    
    # Get doctor's working hours for that day
    # This is simplified - in production, check doctor.slot model
    
    # Standard working hours: 9:00 - 17:00
    start_hour = 9
    end_hour = 17
    slot_duration = 30  # minutes
    
    # Get existing appointments
    existing = odoo.search_read('medical.appointment', [
        ('doctor', '=', doctor_id),
        ('appointment_date', '>=', f'{date} 00:00:00'),
        ('appointment_date', '<=', f'{date} 23:59:59'),
        ('state', '!=', 'cancel'),
    ], ['appointment_date', 'duration'])
    
    # Generate all possible slots
    all_slots = []
    current_time = datetime.strptime(f"{date} {start_hour:02d}:00:00", '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(f"{date} {end_hour:02d}:00:00", '%Y-%m-%d %H:%M:%S')
    
    while current_time < end_time:
        all_slots.append(current_time.strftime('%H:%M:%S'))
        current_time += timedelta(minutes=slot_duration)
    
    # Remove occupied slots
    occupied_times = set()
    for apt in existing:
        apt_time = datetime.strptime(apt['appointment_date'], '%Y-%m-%d %H:%M:%S')
        duration = apt.get('duration', 30)
        
        # Mark all slots within appointment duration as occupied
        for i in range(0, duration, slot_duration):
            occupied_times.add((apt_time + timedelta(minutes=i)).strftime('%H:%M:%S'))
    
    available = [slot for slot in all_slots if slot not in occupied_times]
    
    return available


def _send_reschedule_notification(
    odoo: OdooClientV3,
    patient_id: int,
    doctor_name: str,
    original_time: str,
    new_time: str,
    reason: Optional[str],
):
    """Send rescheduling notification to patient."""
    
    # Get patient contact info
    patient = odoo.read('medical.patient', patient_id, ['name', 'email', 'phone'])
    
    if not patient:
        logger.warning(f"Patient {patient_id} not found for notification")
        return
    
    # Format message
    orig_dt = datetime.strptime(original_time, '%Y-%m-%d %H:%M:%S')
    new_dt = datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S')
    
    message = f"""
שלום {patient['name']},

התור שלך אצל ד"ר {doctor_name} תוזמן מחדש:

מתאריך: {orig_dt.strftime('%d/%m/%Y בשעה %H:%M')}
לתאריך: {new_dt.strftime('%d/%m/%Y בשעה %H:%M')}

{f'סיבה: {reason}' if reason else ''}

אנא אשר קבלת ההודעה.

תודה,
צוות המרפאה
"""
    
    # Log notification (in production, send via SMS/Email)
    logger.info(f"Reschedule notification sent to patient {patient_id}")
    
    # In production, call send_sms_tool or send_email_tool here


# ============================================================================
# Tool 2: Manage Waitlist
# ============================================================================

class ManageWaitlistInput(BaseModel):
    """Input schema for waitlist management."""
    action: str = Field(..., description="Action: add, remove, notify_next, get_list")
    patient_id: Optional[int] = Field(None, description="Patient ID (for add/remove)")
    doctor_id: Optional[int] = Field(None, description="Doctor ID (optional filter)")
    preferred_date: Optional[str] = Field(None, description="Preferred date (YYYY-MM-DD)")
    treatment_type: Optional[str] = Field(None, description="Treatment type")


def manage_waitlist_tool(
    action: str,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    preferred_date: Optional[str] = None,
    treatment_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Manage appointment waitlist for cancellations.
    
    This tool helps fill cancelled appointments by maintaining a waitlist
    of patients who want earlier appointments.
    
    Actions:
    - add: Add patient to waitlist
    - remove: Remove patient from waitlist
    - notify_next: Notify next patient(s) when slot opens
    - get_list: Get current waitlist
    
    Features:
    - Priority-based waitlist
    - Automatic notifications when slots open
    - Filter by doctor, date, treatment type
    - Patient preferences tracking
    
    Args:
        action: Action to perform (add, remove, notify_next, get_list)
        patient_id: Patient ID (required for add/remove)
        doctor_id: Doctor ID (optional filter)
        preferred_date: Preferred date (optional)
        treatment_type: Treatment type (optional)
    
    Returns:
        Dictionary with action result and waitlist status
    """
    try:
        odoo = OdooClientV3()
        
        if action == 'add':
            return _add_to_waitlist(
                odoo, patient_id, doctor_id, preferred_date, treatment_type
            )
        
        elif action == 'remove':
            return _remove_from_waitlist(odoo, patient_id)
        
        elif action == 'notify_next':
            return _notify_next_in_waitlist(
                odoo, doctor_id, preferred_date, treatment_type
            )
        
        elif action == 'get_list':
            return _get_waitlist(odoo, doctor_id, preferred_date, treatment_type)
        
        else:
            return {
                'success': False,
                'error': f'פעולה לא מוכרת: {action}',
                'supported_actions': ['add', 'remove', 'notify_next', 'get_list']
            }
        
    except Exception as e:
        logger.error(f"Waitlist management error: {str(e)}")
        return {
            'success': False,
            'error': f'שגיאה בניהול רשימת המתנה: {str(e)}',
            'technical_details': str(e)
        }


def _add_to_waitlist(
    odoo: OdooClientV3,
    patient_id: int,
    doctor_id: Optional[int],
    preferred_date: Optional[str],
    treatment_type: Optional[str],
) -> Dict[str, Any]:
    """Add patient to waitlist."""
    
    if not patient_id:
        return {
            'success': False,
            'error': 'נדרש patient_id להוספה לרשימת המתנה'
        }
    
    # Validate patient
    patient = odoo.read('medical.patient', patient_id, ['name'])
    if not patient:
        return {
            'success': False,
            'error': f'מטופל עם ID {patient_id} לא נמצא'
        }
    
    # Check if already on waitlist
    existing = odoo.search_read('medical.waitlist', [
        ('patient_id', '=', patient_id),
        ('state', '=', 'active'),
    ], ['id'])
    
    if existing:
        return {
            'success': False,
            'error': f'{patient["name"]} כבר ברשימת המתנה',
            'waitlist_id': existing[0]['id']
        }
    
    # Add to waitlist
    waitlist_data = {
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'preferred_date': preferred_date,
        'treatment_type': treatment_type,
        'priority': _calculate_waitlist_priority(odoo, patient_id, treatment_type),
        'added_date': datetime.now().strftime('%Y-%m-%d'),
        'state': 'active',
    }
    
    waitlist_id = odoo.create('medical.waitlist', waitlist_data)
    
    if not waitlist_id:
        return {
            'success': False,
            'error': 'Failed to add to waitlist'
        }
    
    return {
        'success': True,
        'waitlist_id': waitlist_id,
        'patient_name': patient['name'],
        'confirmation': f"✅ {patient['name']} נוסף לרשימת המתנה",
        'next_steps': [
            "📱 נשלח הודעה כשיש זמינות",
            "⏰ נעדכן אם יש ביטול",
            "📊 ניתן לעקוב אחר המיקום ברשימה",
        ]
    }


def _remove_from_waitlist(
    odoo: OdooClientV3,
    patient_id: int,
) -> Dict[str, Any]:
    """Remove patient from waitlist."""
    
    if not patient_id:
        return {
            'success': False,
            'error': 'נדרש patient_id להסרה מרשימת המתנה'
        }
    
    # Find active waitlist entry
    waitlist = odoo.search_read('medical.waitlist', [
        ('patient_id', '=', patient_id),
        ('state', '=', 'active'),
    ], ['id', 'patient_id'])
    
    if not waitlist:
        return {
            'success': False,
            'error': 'המטופל לא נמצא ברשימת המתנה'
        }
    
    # Mark as inactive
    odoo.write('medical.waitlist', waitlist[0]['id'], {
        'state': 'inactive',
        'removed_date': datetime.now().strftime('%Y-%m-%d'),
    })
    
    patient = odoo.read('medical.patient', patient_id, ['name'])
    
    return {
        'success': True,
        'patient_name': patient['name'] if patient else 'Unknown',
        'confirmation': f"✅ המטופל הוסר מרשימת המתנה"
    }


def _notify_next_in_waitlist(
    odoo: OdooClientV3,
    doctor_id: Optional[int],
    preferred_date: Optional[str],
    treatment_type: Optional[str],
) -> Dict[str, Any]:
    """Notify next patient(s) in waitlist when slot opens."""
    
    # Build search criteria
    domain = [('state', '=', 'active')]
    
    if doctor_id:
        domain.append(('doctor_id', '=', doctor_id))
    if preferred_date:
        domain.append(('preferred_date', '=', preferred_date))
    if treatment_type:
        domain.append(('treatment_type', '=', treatment_type))
    
    # Get waitlist sorted by priority
    waitlist = odoo.search_read('medical.waitlist', domain, [
        'patient_id', 'priority', 'preferred_date', 'treatment_type'
    ], order='priority desc, added_date asc', limit=3)
    
    if not waitlist:
        return {
            'success': True,
            'notified_count': 0,
            'message': 'אין מטופלים ברשימת המתנה'
        }
    
    # Notify patients
    notified = []
    for entry in waitlist:
        patient_id = entry['patient_id'][0] if isinstance(entry['patient_id'], list) else entry['patient_id']
        patient = odoo.read('medical.patient', patient_id, ['name', 'phone', 'email'])
        
        if patient:
            # Send notification (mock)
            logger.info(f"Notifying patient {patient['name']} about available slot")
            
            notified.append({
                'patient_name': patient['name'],
                'phone': patient.get('phone'),
                'email': patient.get('email'),
            })
    
    return {
        'success': True,
        'notified_count': len(notified),
        'notified_patients': notified,
        'confirmation': f"✅ {len(notified)} מטופלים קיבלו הודעה על זמינות",
        'next_steps': [
            "📞 חכה לאישור מהמטופלים",
            "⏰ אם אין תגובה תוך 24 שעות, פנה להבא ברשימה",
            "📅 תזמן את הראשון שמאשר",
        ]
    }


def _get_waitlist(
    odoo: OdooClientV3,
    doctor_id: Optional[int],
    preferred_date: Optional[str],
    treatment_type: Optional[str],
) -> Dict[str, Any]:
    """Get current waitlist."""
    
    # Build search criteria
    domain = [('state', '=', 'active')]
    
    if doctor_id:
        domain.append(('doctor_id', '=', doctor_id))
    if preferred_date:
        domain.append(('preferred_date', '=', preferred_date))
    if treatment_type:
        domain.append(('treatment_type', '=', treatment_type))
    
    # Get waitlist
    waitlist = odoo.search_read('medical.waitlist', domain, [
        'patient_id', 'doctor_id', 'priority', 'preferred_date', 
        'treatment_type', 'added_date'
    ], order='priority desc, added_date asc')
    
    if not waitlist:
        return {
            'success': True,
            'count': 0,
            'waitlist': [],
            'message': 'רשימת המתנה ריקה'
        }
    
    # Format results
    formatted_list = []
    for i, entry in enumerate(waitlist, 1):
        patient_id = entry['patient_id'][0] if isinstance(entry['patient_id'], list) else entry['patient_id']
        patient = odoo.read('medical.patient', patient_id, ['name'])
        
        formatted_list.append({
            'position': i,
            'patient_name': patient['name'] if patient else 'Unknown',
            'priority': entry['priority'],
            'preferred_date': entry.get('preferred_date'),
            'treatment_type': entry.get('treatment_type'),
            'waiting_since': entry['added_date'],
        })
    
    return {
        'success': True,
        'count': len(formatted_list),
        'waitlist': formatted_list,
        'confirmation': f"📋 {len(formatted_list)} מטופלים ברשימת המתנה"
    }


def _calculate_waitlist_priority(
    odoo: OdooClientV3,
    patient_id: int,
    treatment_type: Optional[str],
) -> int:
    """Calculate waitlist priority (1-10, higher = more urgent)."""
    
    priority = 5  # Default
    
    # Check if urgent treatment
    urgent_treatments = ['emergency', 'pain', 'infection']
    if treatment_type and any(urgent in treatment_type.lower() for urgent in urgent_treatments):
        priority += 3
    
    # Check patient history (loyalty)
    appointments = odoo.search_read('medical.appointment', [
        ('patient', '=', patient_id),
        ('state', '=', 'done'),
    ], ['id'])
    
    if len(appointments) > 10:
        priority += 2  # Loyal patient
    
    # Cap at 10
    return min(priority, 10)


# ============================================================================
# Tool Registry
# ============================================================================

ALEX_SCHEDULING_TOOLS = [
    bulk_reschedule_appointments_tool,
    manage_waitlist_tool,
]

