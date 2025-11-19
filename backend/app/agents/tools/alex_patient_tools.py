"""
Patient Management Tools for Alex (Reception Agent)

These tools enable Alex to perform complete patient lifecycle management:
- Registration of new patients
- Updating patient information
- Retrieving comprehensive patient context
- Adding quick notes

All tools integrate with Odoo ERP via OdooClient.
"""

from typing import Dict, Any, Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field

from langchain_core.tools import tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig
from app.agents.context import DentaFlowContext
from app.integrations.odoo_client_factory import OdooClientFactory
from app.integrations.odoo_client import OdooClient


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


@tool
def create_patient_tool(
    first_name: str,
    last_name: str,
    phone: str,
    email: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None,
    insurance_provider: Optional[str] = None,
    insurance_number: Optional[str] = None,
    notes: Optional[str] = None,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> Dict[str, Any]:
    """
    Register a new patient in the system.
    
    This tool creates both a partner record (res.partner) and a medical patient
    record (patient.patient) in Odoo. It handles GDPR/HIPAA compliance by
    marking sensitive data appropriately.
    
    Args:
        first_name: Patient's first name
        last_name: Patient's last name
        phone: Patient's phone number (Israeli format)
        clinic_id: Clinic ID (organization ID)
        email: Patient's email address (optional)
        date_of_birth: Date of birth in YYYY-MM-DD format (optional)
        gender: Gender (male/female/other) (optional)
        address: Full address (optional)
        city: City (optional)
        zip_code: Postal code (optional)
        emergency_contact_name: Emergency contact name (optional)
        emergency_contact_phone: Emergency contact phone (optional)
        insurance_provider: Insurance company name (optional)
        insurance_number: Insurance policy number (optional)
        notes: Initial notes about the patient (optional)
    
    Returns:
        Dictionary with:
        - patient_id: Newly created patient ID
        - partner_id: Odoo partner ID
        - full_name: Patient's full name
        - confirmation: Success message
        - next_steps: Suggested next actions
    """
    # Extract context

    organization_id = context.organization_id if context else None

    

    try:

        # Get organization-specific OdooClient

        odoo = OdooClientFactory.get_client(organization_id)
        
        # Step 1: Create partner (res.partner)
        partner_data = {
            'name': f"{first_name} {last_name}",
            'phone': phone,
            'email': email,
            'street': address,
            'city': city,
            'zip': zip_code,
            'customer_rank': 1,
            'company_id': clinic_id,
        }
        
        partner_id = odoo.create('res.partner', partner_data)
        
        if not partner_id:
            return {
                'success': False,
                'error': 'Failed to create partner record',
                'suggestion': 'Please check Odoo connection and try again'
            }
        
        # Step 2: Create medical patient (patient.patient)
        patient_data = {
            'partner_id': partner_id,
            'name': f"{first_name} {last_name}",
            'dob': date_of_birth,
            'gender': gender,
            'emergency_contact': emergency_contact_name,
            'emergency_phone': emergency_contact_phone,
            'insurance_company': insurance_provider,
            'insurance_number': insurance_number,
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
        
        # Step 3: Add initial note if provided
        if notes:
            note_data = {
                'patient_id': patient_id,
                'note': notes,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': odoo.uid,  # Current user
            }
            odoo.create('patient.patient.note', note_data)
        
        # Step 4: Return success with next steps
        return {
            'success': True,
            'patient_id': patient_id,
            'partner_id': partner_id,
            'full_name': f"{first_name} {last_name}",
            'phone': phone,
            'email': email or 'לא סופק',
            'confirmation': f"✅ המטופל {first_name} {last_name} נרשם בהצלחה!",
            'next_steps': [
                "📅 תזמן תור ראשון",
                "📋 אסוף היסטוריה רפואית",
                "💳 הגדר אמצעי תשלום",
                "📱 שלח הודעת ברוכים הבאים",
            ],
            'patient_summary': {
                'id': patient_id,
                'name': f"{first_name} {last_name}",
                'phone': phone,
                'email': email,
                'insurance': insurance_provider or 'לא סופק',
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


@tool
def update_patient_info_tool(
    patient_id: int,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None,
    insurance_provider: Optional[str] = None,
    insurance_number: Optional[str] = None,

    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> Dict[str, Any]:
    """
    Update patient information.
    
    This tool updates both the partner record and medical patient record.
    Only provided fields will be updated; others remain unchanged.
    
    Args:
        patient_id: Patient ID to update
        phone: New phone number (optional)
        email: New email address (optional)
        address: New address (optional)
        city: New city (optional)
        zip_code: New postal code (optional)
        emergency_contact_name: New emergency contact name (optional)
        emergency_contact_phone: New emergency contact phone (optional)
        insurance_provider: New insurance company (optional)
        insurance_number: New insurance policy number (optional)
    
    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - updated_fields: List of fields that were updated
        - patient_name: Patient's name
        - confirmation: Success message
    """
    # Extract context

    organization_id = context.organization_id if context else None

    

    try:

        # Get organization-specific OdooClient

        odoo = OdooClientFactory.get_client(organization_id)
        
        # Get patient record to find partner_id
        patient = odoo.read('patient.patient', patient_id, ['partner_id', 'name'])
        
        if not patient:
            return {
                'success': False,
                'error': f'מטופל עם ID {patient_id} לא נמצא',
                'suggestion': 'אנא בדוק את מספר המטופל ונסה שוב'
            }
        
        partner_id = patient['partner_id'][0] if isinstance(patient['partner_id'], list) else patient['partner_id']
        patient_name = patient['name']
        
        updated_fields = []
        
        # Update partner fields (res.partner)
        partner_updates = {}
        if phone:
            partner_updates['phone'] = phone
            updated_fields.append('טלפון')
        if email:
            partner_updates['email'] = email
            updated_fields.append('אימייל')
        if address:
            partner_updates['street'] = address
            updated_fields.append('כתובת')
        if city:
            partner_updates['city'] = city
            updated_fields.append('עיר')
        if zip_code:
            partner_updates['zip'] = zip_code
            updated_fields.append('מיקוד')
        
        if partner_updates:
            success = odoo.update('res.partner', partner_id, partner_updates)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to update partner information',
                    'suggestion': 'Please check Odoo connection and try again'
                }
        
        # Update medical patient fields
        patient_updates = {}
        if emergency_contact_name:
            patient_updates['emergency_contact'] = emergency_contact_name
            updated_fields.append('איש קשר לחירום')
        if emergency_contact_phone:
            patient_updates['emergency_phone'] = emergency_contact_phone
            updated_fields.append('טלפון חירום')
        if insurance_provider:
            patient_updates['insurance_company'] = insurance_provider
            updated_fields.append('חברת ביטוח')
        if insurance_number:
            patient_updates['insurance_number'] = insurance_number
            updated_fields.append('מספר פוליסה')
        
        if patient_updates:
            success = odoo.update('patient.patient', patient_id, patient_updates)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to update medical patient information',
                    'suggestion': 'Please check patient data and try again'
                }
        
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

@tool
def get_patient_full_context_tool(
    patient_id: int,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> Dict[str, Any]:
    """
    Get comprehensive patient context in a single call.
    
    This tool consolidates multiple queries into one, following Anthropic's
    best practice of "consolidate tools". It retrieves:
    - Patient demographics
    - Medical history
    - Upcoming appointments
    - Past appointments
    - Outstanding invoices
    - Recent notes
    
    Args:
        patient_id: Patient ID to retrieve context for
    
    Returns:
        Dictionary with comprehensive patient information including:
        - demographics: Basic patient info
        - medical_history: Allergies, conditions, medications
        - appointments: Upcoming and past appointments
        - financial: Outstanding balance, recent invoices
        - notes: Recent notes and communications
        - summary: High-level patient snapshot
    """
    # Extract context

    organization_id = context.organization_id if context else None

    

    try:

        # Get organization-specific OdooClient

        odoo = OdooClientFactory.get_client(organization_id)
        
        # Get patient and partner data
        patient = odoo.read('patient.patient', patient_id, [
            'name', 'partner_id', 'dob', 'gender', 'emergency_contact',
            'emergency_phone', 'insurance_company', 'insurance_number'
        ])
        
        if not patient:
            return {
                'success': False,
                'error': f'מטופל עם ID {patient_id} לא נמצא'
            }
        
        partner_id = patient['partner_id'][0] if isinstance(patient['partner_id'], list) else patient['partner_id']
        
        partner = odoo.read('res.partner', partner_id, [
            'phone', 'email', 'street', 'city', 'zip'
        ])
        
        # Get medical history
        allergies = odoo.search_read('patient.patient.allergy', [
            ('patient_id', '=', patient_id)
        ], ['allergen', 'severity', 'notes'])
        
        medications = odoo.search_read('patient.patient.medication', [
            ('patient_id', '=', patient_id),
            ('active', '=', True)
        ], ['medication_id', 'dosage', 'frequency', 'start_date'])
        
        # Get appointments
        today = datetime.now().strftime('%Y-%m-%d')
        upcoming_appointments = odoo.search_read('patient.appointment', [
            ('patient_id', '=', patient_id),
            ('appointment_date', '>=', today),
            ('status', 'in', ['draft', 'confirmed'])
        ], ['appointment_date', 'doctor_id', 'treatment_id', 'status'], limit=5)
        
        past_appointments = odoo.search_read('patient.appointment', [
            ('patient_id', '=', patient_id),
            ('appointment_date', '<', today),
            ('status', '=', 'done')
        ], ['appointment_date', 'doctor_id', 'treatment_id'], limit=10, order='appointment_date desc')
        
        # Get financial info
        invoices = odoo.search_read('account.invoice', [
            ('partner_id', '=', partner_id),
            ('state', 'in', ['open', 'paid'])
        ], ['number', 'date_invoice', 'amount_total', 'residual', 'state'], limit=10, order='date_invoice desc')
        
        outstanding_balance = sum(inv['residual'] for inv in invoices if inv['state'] == 'open')
        
        # Get recent notes
        notes = odoo.search_read('patient.patient.note', [
            ('patient_id', '=', patient_id)
        ], ['note', 'date', 'user_id'], limit=5, order='date desc')
        
        # Compile comprehensive context
        return {
            'success': True,
            'patient_id': patient_id,
            'demographics': {
                'name': patient['name'],
                'date_of_birth': patient.get('dob'),
                'gender': patient.get('gender'),
                'phone': partner.get('phone'),
                'email': partner.get('email'),
                'address': {
                    'street': partner.get('street'),
                    'city': partner.get('city'),
                    'zip': partner.get('zip')
                },
                'emergency_contact': {
                    'name': patient.get('emergency_contact'),
                    'phone': patient.get('emergency_phone')
                },
                'insurance': {
                    'provider': patient.get('insurance_company'),
                    'number': patient.get('insurance_number')
                }
            },
            'medical_history': {
                'allergies': [
                    {
                        'allergen': a['allergen'],
                        'severity': a.get('severity', 'unknown'),
                        'notes': a.get('notes')
                    }
                    for a in allergies
                ],
                'current_medications': [
                    {
                        'medication': m['medication_id'][1] if isinstance(m['medication_id'], list) else m['medication_id'],
                        'dosage': m.get('dosage'),
                        'frequency': m.get('frequency'),
                        'since': m.get('start_date')
                    }
                    for m in medications
                ]
            },
            'appointments': {
                'upcoming': [
                    {
                        'date': a['appointment_date'],
                        'doctor': a['doctor_id'][1] if isinstance(a['doctor_id'], list) else a['doctor_id'],
                        'treatment': a['treatment_id'][1] if isinstance(a['treatment_id'], list) else a['treatment_id'],
                        'status': a['status']
                    }
                    for a in upcoming_appointments
                ],
                'past': [
                    {
                        'date': a['appointment_date'],
                        'doctor': a['doctor_id'][1] if isinstance(a['doctor_id'], list) else a['doctor_id'],
                        'treatment': a['treatment_id'][1] if isinstance(a['treatment_id'], list) else a['treatment_id']
                    }
                    for a in past_appointments
                ]
            },
            'financial': {
                'outstanding_balance': outstanding_balance,
                'currency': 'ILS',
                'recent_invoices': [
                    {
                        'number': inv['number'],
                        'date': inv['date_invoice'],
                        'total': inv['amount_total'],
                        'remaining': inv['residual'],
                        'status': 'ממתין לתשלום' if inv['state'] == 'open' else 'שולם'
                    }
                    for inv in invoices
                ]
            },
            'notes': [
                {
                    'date': n['date'],
                    'note': n['note'],
                    'by': n['user_id'][1] if isinstance(n['user_id'], list) else n['user_id']
                }
                for n in notes
            ],
            'summary': {
                'name': patient['name'],
                'age': _calculate_age(patient.get('dob')) if patient.get('dob') else 'לא ידוע',
                'allergies_count': len(allergies),
                'medications_count': len(medications),
                'upcoming_appointments_count': len(upcoming_appointments),
                'outstanding_balance': outstanding_balance,
                'last_visit': past_appointments[0]['appointment_date'] if past_appointments else 'אין רישום',
                'risk_flags': _identify_risk_flags(allergies, outstanding_balance, upcoming_appointments)
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


def _identify_risk_flags(allergies, outstanding_balance, upcoming_appointments) -> list:
    """Identify risk flags for patient summary."""
    flags = []
    
    if allergies:
        severe_allergies = [a for a in allergies if a.get('severity') == 'severe']
        if severe_allergies:
            flags.append('⚠️ אלרגיות חמורות')
    
    if outstanding_balance > 1000:
        flags.append('💰 יתרת חוב גבוהה')
    
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
    
    Args:
        patient_id: Patient ID
        note: Note content
        note_type: Type of note (general, allergy, preference, complaint)
    
    Returns:
        Dictionary with:
        - note_id: Created note ID
        - confirmation: Success message
        - timestamp: When the note was created
    """
    # Extract context

    organization_id = context.organization_id if context else None

    

    try:

        # Get organization-specific OdooClient

        odoo = OdooClientFactory.get_client(organization_id)
        
        # Get patient name
        patient = odoo.read('patient.patient', patient_id, ['name'])
        
        if not patient:
            return {
                'success': False,
                'error': f'מטופל עם ID {patient_id} לא נמצא'
            }
        
        # Create note
        note_data = {
            'patient_id': patient_id,
            'note': f"[{note_type.upper()}] {note}",
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': odoo.uid,
        }
        
        note_id = odoo.create('patient.patient.note', note_data)
        
        if not note_id:
            return {
                'success': False,
                'error': 'Failed to create note',
                'suggestion': 'Please check Odoo connection and try again'
            }
        
        return {
            'success': True,
            'note_id': note_id,
            'patient_name': patient['name'],
            'note_type': note_type,
            'confirmation': f"✅ הערה נוספה למטופל {patient['name']}",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note_preview': note[:50] + '...' if len(note) > 50 else note
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

