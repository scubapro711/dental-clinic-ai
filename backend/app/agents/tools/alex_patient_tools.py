"""
Patient Management Tools for Alex (Reception Agent)

These tools enable Alex to perform complete patient lifecycle management:
- Registration of new patients
- Updating patient information
- Retrieving comprehensive patient context
- Adding quick notes

All tools integrate with Odoo ERP via OdooClientV3.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.integrations.odoo_client_v3 import OdooClientV3


# ============================================================================
# Tool 1: Create Patient
# ============================================================================

class CreatePatientInput(BaseModel):
    """Input schema for creating a new patient."""
    first_name: str = Field(..., description="Patient's first name")
    last_name: str = Field(..., description="Patient's last name")
    phone: str = Field(..., description="Patient's phone number (Israeli format: 05X-XXXXXXX)")
    email: Optional[str] = Field(None, description="Patient's email address")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    gender: Optional[str] = Field(None, description="Gender: male, female, other")
    address: Optional[str] = Field(None, description="Full address")
    city: Optional[str] = Field(None, description="City")
    zip_code: Optional[str] = Field(None, description="Postal code")
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    insurance_provider: Optional[str] = Field(None, description="Insurance company name")
    insurance_number: Optional[str] = Field(None, description="Insurance policy number")
    notes: Optional[str] = Field(None, description="Initial notes about the patient")
    clinic_id: int = Field(..., description="Clinic ID (organization ID)")


def create_patient_tool(
    first_name: str,
    last_name: str,
    phone: str,
    clinic_id: int = 1,
    email: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    blood_type: Optional[str] = None,
    marital_status: Optional[str] = None,
    occupation: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    notes: Optional[str] = None,
    patient_serial: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Register a new patient in the system.
    
    This tool creates both a partner record (res.partner) and a medical patient
    record (patient.patient) in Odoo using the correct field names.
    
    Args:
        first_name: Patient's first name
        last_name: Patient's last name
        phone: Patient's phone number (Israeli format)
        clinic_id: Clinic ID (organization ID)
        email: Patient's email address (optional)
        date_of_birth: Date of birth in YYYY-MM-DD format (optional)
        gender: Gender (male/female/other) (optional)
        blood_type: Blood type (a+, a-, b+, b-, o+, o-, ab+, ab-) (optional)
        marital_status: Marital status (single, married, divorced, widowed) (optional)
        occupation: Patient's occupation (optional)
        address: Full address (optional)
        city: City (optional)
        zip_code: Postal code (optional)
        notes: Initial notes about the patient (optional)
    
    Returns:
        Dictionary with:
        - patient_id: Newly created patient ID
        - partner_id: Odoo partner ID
        - full_name: Patient's full name
        - confirmation: Success message
        - next_steps: Suggested next actions
    """
    try:
        odoo = OdooClientV3()
        
        # Step 1: Create partner (res.partner)
        partner_data = {
            'name': f"{first_name} {last_name}",
            'phone': phone,
            'email': email,
            'street': address,
            'city': city,
            'zip': zip_code,
            'company_id': clinic_id,
        }
        
        # Remove None values
        partner_data = {k: v for k, v in partner_data.items() if v is not None}
        
        partner_id = odoo.create('res.partner', partner_data)
        
        if not partner_id:
            return {
                'success': False,
                'error': 'Failed to create partner record',
                'suggestion': 'Please check Odoo connection and try again'
            }
        
        # Step 2: Generate patient serial number
        if not patient_serial:
            # Get the highest existing serial number
            existing_patients = odoo.search_read(
                'patient.patient',
                domain=[],
                fields=['patient_serial'],
                order='patient_serial desc',
                limit=1
            )
            
            if existing_patients and existing_patients[0].get('patient_serial'):
                last_serial = existing_patients[0]['patient_serial']
                # Extract number from PAT000001 format
                try:
                    last_num = int(last_serial.replace('PAT', ''))
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            
            patient_serial = f"PAT{new_num:06d}"
        
        # Step 3: Create medical patient (patient.patient)
        patient_data = {
            'patient_serial': patient_serial,  # REQUIRED!
            'patient_name': f"{first_name} {last_name}",
            'contact_number': phone,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'blood_type': blood_type,
            'marital_status': marital_status,
            'occupation': occupation,
        }
        
        # Remove None values
        patient_data = {k: v for k, v in patient_data.items() if v is not None}
        
        patient_id = odoo.create('patient.patient', patient_data)
        
        if not patient_id:
            # Rollback: delete partner if patient creation failed
            odoo.delete('res.partner', partner_id)
            return {
                'success': False,
                'error': 'Failed to create medical patient record',
                'suggestion': 'Please check patient data and try again'
            }
        
        # Step 4: Link partner to patient via message (for tracking)
        if notes:
            try:
                odoo.execute(
                    'patient.patient',
                    'message_post',
                    [patient_id],
                    {
                        'body': f"<p><strong>Initial Notes:</strong></p><p>{notes}</p>",
                        'message_type': 'comment',
                        'subtype_xmlid': 'mail.mt_note',
                    }
                )
            except Exception as e:
                # Don't fail if note creation fails
                pass
        
        # Step 5: Return success with next steps
        return {
            'success': True,
            'patient_id': patient_id,
            'partner_id': partner_id,
            'patient_serial': patient_serial,
            'full_name': f"{first_name} {last_name}",
            'phone': phone,
            'email': email or 'לא סופק',
            'confirmation': f"✅ המטופל {first_name} {last_name} נרשם בהצלחה! מספר מטופל: {patient_serial}",
            'next_steps': [
                "📅 תזמן תור ראשון",
                "📋 אסוף היסטוריה רפואית",
                "💳 הגדר אמצעי תשלום",
                "📱 שלח הודעת ברוכים הבאים",
            ],
            'patient_summary': {
                'id': patient_id,
                'serial': patient_serial,
                'name': f"{first_name} {last_name}",
                'phone': phone,
                'email': email,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'blood_type': blood_type,
                'registered_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'שגיאה ביצירת מטופל: {str(e)}',
            'suggestion': 'אנא בדוק את החיבור ל-Odoo ונסה שוב',
            'technical_details': str(e)
        }


# ============================================================================
# Tool 2: Update Patient Info
# ============================================================================

class UpdatePatientInfoInput(BaseModel):
    """Input schema for updating patient information."""
    patient_id: int = Field(..., description="Patient ID to update")
    phone: Optional[str] = Field(None, description="New phone number")
    email: Optional[str] = Field(None, description="New email address")
    address: Optional[str] = Field(None, description="New address")
    city: Optional[str] = Field(None, description="New city")
    zip_code: Optional[str] = Field(None, description="New postal code")
    emergency_contact_name: Optional[str] = Field(None, description="New emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="New emergency contact phone")
    insurance_provider: Optional[str] = Field(None, description="New insurance company")
    insurance_number: Optional[str] = Field(None, description="New insurance policy number")


def update_patient_info_tool(
    patient_id: int,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    blood_type: Optional[str] = None,
    marital_status: Optional[str] = None,
    occupation: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update patient information.
    
    This tool updates the patient.patient record with correct field names.
    It also attempts to update the related res.partner record (found by phone).
    Only provided fields will be updated; others remain unchanged.
    
    Args:
        patient_id: Patient ID to update
        phone: New phone number (optional)
        email: New email address (optional)
        date_of_birth: New date of birth YYYY-MM-DD (optional)
        gender: New gender (male/female/other) (optional)
        blood_type: New blood type (a+, a-, b+, b-, o+, o-, ab+, ab-) (optional)
        marital_status: New marital status (single, married, divorced, widowed) (optional)
        occupation: New occupation (optional)
        address: New address (optional)
        city: New city (optional)
    
    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - updated_fields: List of fields that were updated
        - patient_name: Patient's name
        - confirmation: Success message
    """
    try:
        odoo = OdooClientV3()
        
        # Get patient record
        patient_records = odoo.read('patient.patient', [patient_id], ['patient_name', 'contact_number'])
        
        if not patient_records:
            return {
                'success': False,
                'error': f'מטופל עם ID {patient_id} לא נמצא'
            }
        
        patient = patient_records[0]
        
        if not patient:
            return {
                'success': False,
                'error': f'מטופל עם ID {patient_id} לא נמצא',
                'suggestion': 'אנא בדוק את מספר המטופל ונסה שוב'
            }
        
        patient_name = patient.get('patient_name', 'Unknown')
        old_phone = patient.get('contact_number')
        
        updated_fields = []
        
        # Update patient.patient fields
        patient_updates = {}
        
        if phone:
            patient_updates['contact_number'] = phone
            updated_fields.append('טלפון')
        if date_of_birth:
            patient_updates['date_of_birth'] = date_of_birth
            updated_fields.append('תאריך לידה')
        if gender:
            patient_updates['gender'] = gender
            updated_fields.append('מגדר')
        if blood_type:
            patient_updates['blood_type'] = blood_type
            updated_fields.append('סוג דם')
        if marital_status:
            patient_updates['marital_status'] = marital_status
            updated_fields.append('מצב משפחתי')
        if occupation:
            patient_updates['occupation'] = occupation
            updated_fields.append('מקצוע')
        
        if patient_updates:
            success = odoo.update('patient.patient', [patient_id], patient_updates)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to update patient information',
                    'suggestion': 'Please check patient data and try again'
                }
        
        # Try to update related res.partner (if exists)
        # Find partner by old phone number
        if old_phone and (phone or email or address or city):
            partners = odoo.search_read(
                'res.partner',
                domain=[('phone', '=', old_phone)],
                fields=['id'],
                limit=1
            )
            
            if partners:
                partner_id = partners[0]['id']
                partner_updates = {}
                
                if phone:
                    partner_updates['phone'] = phone
                if email:
                    partner_updates['email'] = email
                if address:
                    partner_updates['street'] = address
                    updated_fields.append('כתובת')
                if city:
                    partner_updates['city'] = city
                    updated_fields.append('עיר')
                
                if partner_updates:
                    odoo.update('res.partner', [partner_id], partner_updates)
                    # Don't fail if partner update fails
        
        if not updated_fields:
            return {
                'success': False,
                'error': 'לא סופקו שדות לעדכון',
                'suggestion': 'אנא ספק לפחות שדה אחד לעדכון'
            }
        
        return {
            'success': True,
            'patient_id': patient_id,
            'patient_name': patient_name,
            'updated_fields': updated_fields,
            'confirmation': f"✅ פרטי המטופל {patient_name} עודכנו בהצלחה!",
            'updated_count': len(updated_fields),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'שגיאה בעדכון פרטי מטופל: {str(e)}',
            'suggestion': 'אנא בדוק את החיבור ל-Odoo ונסה שוב',
            'technical_details': str(e)
        }


# ============================================================================
# Tool 3: Get Patient Full Context
# ============================================================================

def get_patient_full_context_tool(patient_id: int) -> Dict[str, Any]:
    """
    Get comprehensive patient context in a single call.
    
    This tool consolidates multiple queries into one, following Anthropic's
    best practice of "consolidate tools". It retrieves:
    - Patient demographics
    - Medical questions (qstn_1, qstn_2)
    - Prescriptions (medications)
    - Dental procedures history
    - Upcoming and past appointments
    - Recent notes (via mail.message)
    
    Args:
        patient_id: Patient ID to retrieve context for
    
    Returns:
        Dictionary with comprehensive patient information including:
        - demographics: Basic patient info
        - medical_info: Medical questions and prescriptions
        - procedures: Dental procedures history
        - appointments: Upcoming and past appointments
        - notes: Recent notes and communications
        - summary: High-level patient snapshot
    """
    try:
        odoo = OdooClientV3()
        
        # Get patient data
        patient_records = odoo.read('patient.patient', [patient_id], [
            'patient_name', 'patient_serial', 'contact_number', 'date_of_birth',
            'gender', 'blood_type', 'marital_status', 'occupation', 'age',
            'qstn_1', 'qstn_2'
        ])
        
        if not patient_records:
            return {
                'success': False,
                'error': f'מטופל עם ID {patient_id} לא נמצא'
            }
        
        patient = patient_records[0]  # Extract first record from list
        
        # Try to find related res.partner by phone (for email/address)
        partner = None
        if patient.get('contact_number'):
            partners = odoo.search_read('res.partner', [
                ('phone', '=', patient['contact_number'])
            ], ['email', 'street', 'city'], limit=1)
            if partners:
                partner = partners[0]
        
        # Get prescriptions (medications)
        prescriptions = odoo.search_read('patient.prescription', [
            ('patient_id', '=', patient_id)
        ], ['prescription_date', 'notes'], limit=10, order='prescription_date desc')
        
        # Get prescription lines (actual medications)
        prescription_lines = []
        for prescription in prescriptions:
            lines = odoo.search_read('patient.prescription.line', [
                ('prescription_id', '=', prescription['id'])
            ], ['medicine_name', 'dosage', 'frequency', 'duration'])
            prescription_lines.extend(lines)
        
        # Get dental procedures history
        procedures = odoo.search_read('dental.procedure.line', [
            ('patient_id', '=', patient_id)
        ], ['appointment_id', 'service_item_id', 'tooth_no', 'cost'], limit=20, order='create_date desc')
        
        # Get appointments
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        upcoming_appointments = odoo.search_read('patient.appointment', [
            ('patient_id', '=', patient_id),
            ('start', '>=', today)
        ], ['start', 'stop', 'doctor_id', 'name', 'appointment_status'], limit=5, order='start asc')
        
        past_appointments = odoo.search_read('patient.appointment', [
            ('patient_id', '=', patient_id),
            ('start', '<', today)
        ], ['start', 'stop', 'doctor_id', 'name'], limit=10, order='start desc')
        
        # Get recent notes (via mail.message)
        notes = odoo.search_read('mail.message', [
            ('model', '=', 'patient.patient'),
            ('res_id', '=', patient_id),
            ('message_type', '=', 'comment')
        ], ['body', 'date', 'author_id'], limit=10, order='date desc')
        
        # Compile comprehensive context
        return {
            'success': True,
            'patient_id': patient_id,
            'demographics': {
                'serial': patient.get('patient_serial'),
                'name': patient.get('patient_name'),
                'date_of_birth': patient.get('date_of_birth'),
                'age': patient.get('age', 'לא ידוע'),
                'gender': patient.get('gender'),
                'blood_type': patient.get('blood_type'),
                'marital_status': patient.get('marital_status'),
                'occupation': patient.get('occupation'),
                'phone': patient.get('contact_number'),
                'email': partner.get('email') if partner else None,
                'address': {
                    'street': partner.get('street') if partner else None,
                    'city': partner.get('city') if partner else None
                }
            },
            'medical_info': {
                'medical_questions': {
                    'question_1': patient.get('qstn_1'),
                    'question_2': patient.get('qstn_2')
                },
                'prescriptions': [
                    {
                        'date': p.get('prescription_date'),
                        'notes': p.get('notes')
                    }
                    for p in prescriptions
                ],
                'medications': [
                    {
                        'medicine': m.get('medicine_name'),
                        'dosage': m.get('dosage'),
                        'frequency': m.get('frequency'),
                        'duration': m.get('duration')
                    }
                    for m in prescription_lines
                ]
            },
            'procedures': [
                {
                    'appointment_id': p.get('appointment_id'),
                    'service': p['service_item_id'][1] if isinstance(p.get('service_item_id'), list) else p.get('service_item_id'),
                    'tooth': p.get('tooth_no'),
                    'cost': p.get('cost')
                }
                for p in procedures
            ],
            'appointments': {
                'upcoming': [
                    {
                        'start': a.get('start'),
                        'stop': a.get('stop'),
                        'doctor': a['doctor_id'][1] if isinstance(a.get('doctor_id'), list) else a.get('doctor_id'),
                        'subject': a.get('name'),
                        'status': a.get('appointment_status')
                    }
                    for a in upcoming_appointments
                ],
                'past': [
                    {
                        'start': a.get('start'),
                        'stop': a.get('stop'),
                        'doctor': a['doctor_id'][1] if isinstance(a.get('doctor_id'), list) else a.get('doctor_id'),
                        'subject': a.get('name')
                    }
                    for a in past_appointments
                ]
            },
            'notes': [
                {
                    'date': n.get('date'),
                    'note': n.get('body', '').replace('<p>', '').replace('</p>', '').strip(),
                    'by': n['author_id'][1] if isinstance(n.get('author_id'), list) else n.get('author_id')
                }
                for n in notes
            ],
            'summary': {
                'name': patient.get('patient_name'),
                'serial': patient.get('patient_serial'),
                'age': patient.get('age', 'לא ידוע'),
                'prescriptions_count': len(prescriptions),
                'procedures_count': len(procedures),
                'upcoming_appointments_count': len(upcoming_appointments),
                'last_visit': past_appointments[0].get('start') if past_appointments else 'אין רישום',
                'risk_flags': _identify_risk_flags(prescription_lines, upcoming_appointments)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'שגיאה בקבלת קונטקסט מטופל: {str(e)}',
            'suggestion': 'אנא בדוק את החיבור ל-Odoo ונסה שוב',
            'technical_details': str(e)
        }


def _calculate_age(dob_str: str) -> int:
    """Calculate age from date of birth string (YYYY-MM-DD)."""
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except:
        return 0


def _identify_risk_flags(medications, upcoming_appointments) -> list:
    """Identify risk flags for patient summary."""
    flags = []
    
    if len(medications) > 5:
        flags.append('💊 מספר רב של תרופות')
    
    if not upcoming_appointments:
        flags.append('📅 אין תורים קרובים')
    
    return flags if flags else ['✅ אין התראות']


# ============================================================================
# Tool 4: Add Patient Note
# ============================================================================

class AddPatientNoteInput(BaseModel):
    """Input schema for adding a patient note."""
    patient_id: int = Field(..., description="Patient ID")
    note: str = Field(..., description="Note content")
    note_type: Optional[str] = Field('general', description="Note type: general, allergy, preference, complaint")


def add_patient_note_tool(
    patient_id: int,
    note: str,
    note_type: str = 'general'
) -> Dict[str, Any]:
    """
    Add a quick note to patient record.
    
    This tool allows adding timestamped notes for:
    - Allergies discovered during conversation
    - Patient preferences (e.g., prefers morning appointments)
    - Complaints or special requests
    - General observations
    
    Uses mail.message system (message_post) to add notes to patient records.
    
    Args:
        patient_id: Patient ID
        note: Note content
        note_type: Type of note (general, allergy, preference, complaint)
    
    Returns:
        Dictionary with:
        - message_id: Created message ID
        - confirmation: Success message
        - timestamp: When the note was created
    """
    try:
        odoo = OdooClientV3()
        
        # Get patient name
        patient_records = odoo.read('patient.patient', [patient_id], ['patient_name'])
        
        if not patient_records:
            return {
                'success': False,
                'error': f'מטופל עם ID {patient_id} לא נמצא'
            }
        
        patient = patient_records[0]
        patient_name = patient.get('patient_name', 'Unknown')
        
        # Create note using mail.message system
        # Format note with type indicator
        note_emoji = {
            'allergy': '⚠️',
            'preference': '⭐',
            'complaint': '📢',
            'general': '📝'
        }.get(note_type.lower(), '📝')
        
        formatted_note = f"<p><strong>{note_emoji} {note_type.upper()}</strong></p><p>{note}</p>"
        
        try:
            # Use message_post to add note
            message_id = odoo.execute(
                'patient.patient',
                'message_post',
                [patient_id],
                {
                    'body': formatted_note,
                    'message_type': 'comment',
                    'subtype_xmlid': 'mail.mt_note',
                }
            )
            
            return {
                'success': True,
                'message_id': message_id,
                'patient_name': patient_name,
                'note_type': note_type,
                'confirmation': f"✅ הערה נוספה למטופל {patient_name}",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note_preview': note[:50] + '...' if len(note) > 50 else note
            }
            
        except Exception as msg_error:
            # If message_post fails, return error with details
            return {
                'success': False,
                'error': f'Failed to create note via message_post: {str(msg_error)}',
                'suggestion': 'The mail.message system may not be available. Consider storing notes in a custom field or external database.',
                'technical_details': str(msg_error)
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'שגיאה בהוספת הערה: {str(e)}',
            'suggestion': 'אנא בדוק את החיבור ל-Odoo ונסה שוב',
            'technical_details': str(e)
        }


# ============================================================================
# Tool Registry
# ============================================================================

ALEX_PATIENT_TOOLS = [
    create_patient_tool,
    update_patient_info_tool,
    get_patient_full_context_tool,
    add_patient_note_tool,
]

