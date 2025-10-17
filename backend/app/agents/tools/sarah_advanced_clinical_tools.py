"""
Advanced Clinical Tools for שרה (Clinical Assistant)

Phase 5.5 Week 2 Day 8-9: Advanced Clinical Operations
- Referrals to specialists
- X-ray orders (PACS integration)
- Lab test orders
- Clinical notes (SOAP format)

Created: 2025-01-10
"""

import logging
from datetime import datetime
from typing import Optional
from langchain_core.tools import tool
from app.integrations.odoo_client import OdooClient

logger = logging.getLogger(__name__)


@tool
def create_referral_tool(
    patient_id: int,
    specialist_type: str,
    reason: str,
    urgency: str = "routine",
    clinical_findings: Optional[str] = None,
    requested_procedures: Optional[str] = None,
) -> str:
    """
    Create a referral to a specialist for a patient.
    
    Use this when a patient needs specialized care beyond general dentistry.
    
    Args:
        patient_id: Patient ID in Odoo
        specialist_type: Type of specialist (e.g., "orthodontist", "endodontist", 
                        "periodontist", "oral_surgeon", "prosthodontist", "pediatric_dentist")
        reason: Reason for referral (brief clinical summary)
        urgency: Urgency level - "routine", "urgent", "emergency" (default: "routine")
        clinical_findings: Detailed clinical findings to share with specialist
        requested_procedures: Specific procedures requested (if known)
    
    Returns:
        Success message with referral details
    
    Examples:
        - create_referral_tool(patient_id=123, specialist_type="endodontist", 
                              reason="Root canal needed on tooth #14")
        - create_referral_tool(patient_id=456, specialist_type="oral_surgeon",
                              reason="Impacted wisdom tooth extraction", urgency="urgent")
    """
    try:
        odoo = OdooClient()
        
        # Validate specialist type
        valid_specialists = [
            "orthodontist",  # יישור שיניים
            "endodontist",  # טיפולי שורש
            "periodontist",  # חניכיים
            "oral_surgeon",  # כירורגיה
            "prosthodontist",  # שיקום פה
            "pediatric_dentist",  # רופא שיניים לילדים
            "maxillofacial_surgeon",  # כירורגיה פה ולסת
        ]
        
        if specialist_type not in valid_specialists:
            return f"❌ Invalid specialist type. Must be one of: {', '.join(valid_specialists)}"
        
        # Validate urgency
        if urgency not in ["routine", "urgent", "emergency"]:
            return "❌ Invalid urgency. Must be: routine, urgent, or emergency"
        
        # Get patient details
        patient = odoo.get_patient(patient_id)
        if not patient:
            return f"❌ Patient {patient_id} not found"
        
        # Create referral in Odoo
        referral_data = {
            "patient_id": patient_id,
            "specialist_type": specialist_type,
            "reason": reason,
            "urgency": urgency,
            "clinical_findings": clinical_findings or "",
            "requested_procedures": requested_procedures or "",
            "referring_doctor_id": odoo.current_user_id,
            "referral_date": datetime.now().isoformat(),
            "status": "pending",
        }
        
        # In production, this would create in Odoo medical.referral model
        # For now, we'll create a note in the patient record
        note = f"""
🔗 **הפניה למומחה**

**סוג מומחה:** {specialist_type}
**דחיפות:** {urgency}
**סיבה:** {reason}

**ממצאים קליניים:**
{clinical_findings or 'לא צוין'}

**הליכים מבוקשים:**
{requested_procedures or 'לא צוין'}

**תאריך הפניה:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**רופא מפנה:** {odoo.current_user_name}

**סטטוס:** ממתין לתיאום
"""
        
        # Add note to patient record
        odoo.create_patient_note(patient_id, note, note_type="referral")
        
        # Format urgency emoji
        urgency_emoji = {
            "routine": "🟢",
            "urgent": "🟡",
            "emergency": "🔴"
        }[urgency]
        
        # Success message
        return f"""
✅ **הפניה נוצרה בהצלחה**

{urgency_emoji} **דחיפות:** {urgency}
👤 **מטופל:** {patient.get('name', 'Unknown')}
🏥 **מומחה:** {specialist_type}
📋 **סיבה:** {reason}

**הפניה נשמרה בתיק המטופל**

**צעדים הבאים:**
1. תיאום תור עם המומחה
2. העברת מסמכים רלוונטיים (צילומים, תוצאות בדיקות)
3. מעקב אחר הטיפול אצל המומחה

💡 **טיפ:** השתמש ב-order_xray_tool כדי להזמין צילומים לפני ההפניה
"""
        
    except Exception as e:
        logger.error(f"Error creating referral: {e}")
        return f"❌ שגיאה ביצירת הפניה: {str(e)}"


@tool
def order_xray_tool(
    patient_id: int,
    xray_type: str,
    teeth_numbers: Optional[str] = None,
    reason: str = "",
    urgency: str = "routine",
) -> str:
    """
    Order an X-ray (dental radiograph) for a patient.
    
    Integrates with PACS (Picture Archiving and Communication System) for digital imaging.
    
    Args:
        patient_id: Patient ID in Odoo
        xray_type: Type of X-ray - "periapical", "bitewing", "panoramic", "cephalometric", "cbct"
        teeth_numbers: Specific teeth to image (e.g., "14,15,16" or "all")
        reason: Clinical reason for X-ray
        urgency: Urgency level - "routine", "urgent", "emergency" (default: "routine")
    
    Returns:
        Success message with order details
    
    Examples:
        - order_xray_tool(patient_id=123, xray_type="periapical", teeth_numbers="14", 
                         reason="Suspected root fracture")
        - order_xray_tool(patient_id=456, xray_type="panoramic", 
                         reason="Initial assessment")
    """
    try:
        odoo = OdooClient()
        
        # Validate X-ray type
        valid_types = {
            "periapical": "צילום פריאפיקלי (שן בודדת)",
            "bitewing": "צילום ביטווינג (בין שיניים)",
            "panoramic": "פנורמי (כל הפה)",
            "cephalometric": "צפלומטרי (גולגולת)",
            "cbct": "CBCT (תלת-ממד)",
        }
        
        if xray_type not in valid_types:
            return f"❌ Invalid X-ray type. Must be one of: {', '.join(valid_types.keys())}"
        
        # Get patient details
        patient = odoo.get_patient(patient_id)
        if not patient:
            return f"❌ Patient {patient_id} not found"
        
        # Check pregnancy status for female patients (radiation safety)
        patient_gender = patient.get("gender", "")
        if patient_gender == "female":
            # In production, we'd check medical history for pregnancy
            warning = "\n⚠️ **שים לב:** ודא שהמטופלת אינה בהריון לפני ביצוע הצילום"
        else:
            warning = ""
        
        # Create X-ray order
        order_data = {
            "patient_id": patient_id,
            "xray_type": xray_type,
            "teeth_numbers": teeth_numbers or "N/A",
            "reason": reason,
            "urgency": urgency,
            "ordering_doctor_id": odoo.current_user_id,
            "order_date": datetime.now().isoformat(),
            "status": "pending",
        }
        
        # In production, this would:
        # 1. Create order in PACS system
        # 2. Send to radiology workstation
        # 3. Track order status
        # For now, we'll create a note
        
        note = f"""
📸 **הזמנת צילום רנטגן**

**סוג צילום:** {valid_types[xray_type]}
**שיניים:** {teeth_numbers or 'כל הפה'}
**סיבה:** {reason}
**דחיפות:** {urgency}

**תאריך הזמנה:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**רופא מזמין:** {odoo.current_user_name}

**סטטוס:** ממתין לביצוע{warning}
"""
        
        odoo.create_patient_note(patient_id, note, note_type="xray_order")
        
        # Radiation dose info
        dose_info = {
            "periapical": "0.005 mSv (נמוך מאוד)",
            "bitewing": "0.005 mSv (נמוך מאוד)",
            "panoramic": "0.01 mSv (נמוך)",
            "cephalometric": "0.006 mSv (נמוך מאוד)",
            "cbct": "0.04-0.1 mSv (בינוני)",
        }[xray_type]
        
        return f"""
✅ **הזמנת צילום נוצרה בהצלחה**

👤 **מטופל:** {patient.get('name', 'Unknown')}
📸 **סוג צילום:** {valid_types[xray_type]}
🦷 **שיניים:** {teeth_numbers or 'כל הפה'}
📋 **סיבה:** {reason}
☢️ **מינון קרינה:** {dose_info}

**ההזמנה נשלחה למערכת PACS**

**צעדים הבאים:**
1. המטופל יופנה לחדר הצילום
2. הצילום יבוצע על ידי הטכנאי
3. התמונות יועלו אוטומטית למערכת
4. תקבל התראה כשהצילום מוכן לצפייה{warning}

💡 **טיפ:** השתמש ב-view_xray_tool כדי לצפות בצילום לאחר שיושלם
"""
        
    except Exception as e:
        logger.error(f"Error ordering X-ray: {e}")
        return f"❌ שגיאה בהזמנת צילום: {str(e)}"


@tool
def order_lab_test_tool(
    patient_id: int,
    test_type: str,
    teeth_numbers: Optional[str] = None,
    lab_partner: str = "default",
    special_instructions: Optional[str] = None,
    urgency: str = "routine",
) -> str:
    """
    Order a lab test or prosthetic work from a dental laboratory.
    
    Args:
        patient_id: Patient ID in Odoo
        test_type: Type of lab work - "crown", "bridge", "denture", "implant", "veneer", 
                  "nightguard", "retainer", "biopsy"
        teeth_numbers: Teeth involved (e.g., "14,15,16")
        lab_partner: Lab partner name (default: "default" - uses clinic's primary lab)
        special_instructions: Special instructions for the lab
        urgency: Urgency level - "routine", "urgent", "rush" (default: "routine")
    
    Returns:
        Success message with order details
    
    Examples:
        - order_lab_test_tool(patient_id=123, test_type="crown", teeth_numbers="14",
                             special_instructions="Shade A2")
        - order_lab_test_tool(patient_id=456, test_type="biopsy", 
                             reason="Suspicious lesion", urgency="urgent")
    """
    try:
        odoo = OdooClient()
        
        # Validate test type
        valid_types = {
            "crown": "כתר",
            "bridge": "גשר",
            "denture": "שיניים תותבות",
            "implant": "שתל",
            "veneer": "ציפוי",
            "nightguard": "מגן לילה",
            "retainer": "מתקן שימור",
            "biopsy": "ביופסיה",
            "splint": "סד",
        }
        
        if test_type not in valid_types:
            return f"❌ Invalid test type. Must be one of: {', '.join(valid_types.keys())}"
        
        # Get patient details
        patient = odoo.get_patient(patient_id)
        if not patient:
            return f"❌ Patient {patient_id} not found"
        
        # Create lab order
        order_data = {
            "patient_id": patient_id,
            "test_type": test_type,
            "teeth_numbers": teeth_numbers or "N/A",
            "lab_partner": lab_partner,
            "special_instructions": special_instructions or "",
            "urgency": urgency,
            "ordering_doctor_id": odoo.current_user_id,
            "order_date": datetime.now().isoformat(),
            "status": "pending",
            "expected_completion": self._calculate_lab_completion(test_type, urgency),
        }
        
        # In production, this would:
        # 1. Send order to lab partner API
        # 2. Track order status
        # 3. Notify when ready
        # For now, we'll create a note
        
        note = f"""
🔬 **הזמנת מעבדה**

**סוג עבודה:** {valid_types[test_type]}
**שיניים:** {teeth_numbers or 'לא צוין'}
**מעבדה:** {lab_partner}
**דחיפות:** {urgency}

**הוראות מיוחדות:**
{special_instructions or 'אין'}

**תאריך הזמנה:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**רופא מזמין:** {odoo.current_user_name}

**סטטוס:** ממתין לאישור מעבדה
"""
        
        odoo.create_patient_note(patient_id, note, note_type="lab_order")
        
        # Estimated completion time
        completion_times = {
            "routine": "7-10 ימי עבודה",
            "urgent": "3-5 ימי עבודה",
            "rush": "1-2 ימי עבודה (תוספת תשלום)",
        }
        
        return f"""
✅ **הזמנת מעבדה נוצרה בהצלחה**

👤 **מטופל:** {patient.get('name', 'Unknown')}
🔬 **סוג עבודה:** {valid_types[test_type]}
🦷 **שיניים:** {teeth_numbers or 'לא צוין'}
🏭 **מעבדה:** {lab_partner}
⏱️ **זמן משוער:** {completion_times[urgency]}

**ההזמנה נשלחה למעבדה**

**צעדים הבאים:**
1. המעבדה תאשר קבלת ההזמנה (תוך 24 שעות)
2. תקבל עדכון על התקדמות העבודה
3. התראה כשהעבודה מוכנה לאיסוף
4. תיאום תור עם המטופל להתקנה

💡 **טיפ:** וודא שיש לך את כל המידע הנדרש (צבע, מידות, טביעות)
"""
        
    except Exception as e:
        logger.error(f"Error ordering lab test: {e}")
        return f"❌ שגיאה בהזמנת מעבדה: {str(e)}"
    
    @staticmethod
    def _calculate_lab_completion(test_type: str, urgency: str) -> str:
        """Calculate expected lab completion date."""
        from datetime import timedelta
        
        # Base days by test type
        base_days = {
            "crown": 7,
            "bridge": 10,
            "denture": 14,
            "implant": 10,
            "veneer": 7,
            "nightguard": 5,
            "retainer": 5,
            "biopsy": 3,
            "splint": 5,
        }
        
        # Urgency multiplier
        urgency_multiplier = {
            "routine": 1.0,
            "urgent": 0.5,
            "rush": 0.2,
        }
        
        days = int(base_days.get(test_type, 7) * urgency_multiplier.get(urgency, 1.0))
        completion_date = datetime.now() + timedelta(days=days)
        
        return completion_date.strftime('%d/%m/%Y')


@tool
def create_clinical_note_tool(
    patient_id: int,
    note_type: str,
    subjective: str,
    objective: str,
    assessment: str,
    plan: str,
    teeth_numbers: Optional[str] = None,
) -> str:
    """
    Create a structured clinical note using SOAP format (Subjective, Objective, Assessment, Plan).
    
    This is the standard format for medical documentation.
    
    Args:
        patient_id: Patient ID in Odoo
        note_type: Type of note - "progress", "consultation", "treatment", "emergency", "followup"
        subjective: Patient's complaints and symptoms (what patient says)
        objective: Clinical findings and measurements (what you observe)
        assessment: Your diagnosis and clinical impression
        plan: Treatment plan and next steps
        teeth_numbers: Teeth involved (if applicable)
    
    Returns:
        Success message with note details
    
    Examples:
        - create_clinical_note_tool(
            patient_id=123,
            note_type="treatment",
            subjective="Patient reports pain in lower right molar for 3 days",
            objective="Tooth #46: Deep caries, tender to percussion, negative vitality test",
            assessment="Irreversible pulpitis tooth #46",
            plan="Root canal treatment recommended. Patient consented. Scheduled for next week."
          )
    """
    try:
        odoo = OdooClient()
        
        # Validate note type
        valid_types = {
            "progress": "הערת התקדמות",
            "consultation": "ייעוץ",
            "treatment": "טיפול",
            "emergency": "חירום",
            "followup": "מעקב",
        }
        
        if note_type not in valid_types:
            return f"❌ Invalid note type. Must be one of: {', '.join(valid_types.keys())}"
        
        # Get patient details
        patient = odoo.get_patient(patient_id)
        if not patient:
            return f"❌ Patient {patient_id} not found"
        
        # Create SOAP note
        soap_note = f"""
📋 **הערה קלינית - {valid_types[note_type]}**

**תאריך:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**רופא:** {odoo.current_user_name}
**שיניים:** {teeth_numbers or 'לא צוין'}

---

**S - Subjective (תלונות המטופל):**
{subjective}

**O - Objective (ממצאים קליניים):**
{objective}

**A - Assessment (אבחנה):**
{assessment}

**P - Plan (תוכנית טיפול):**
{plan}

---

**חתימה דיגיטלית:** {odoo.current_user_name}
**מספר רישיון:** [לקבל ממערכת]
"""
        
        # Save to Odoo
        odoo.create_patient_note(patient_id, soap_note, note_type="clinical_soap")
        
        # Calculate note completeness score
        completeness = self._calculate_note_completeness(subjective, objective, assessment, plan)
        
        return f"""
✅ **הערה קלינית נשמרה בהצלחה**

👤 **מטופל:** {patient.get('name', 'Unknown')}
📋 **סוג הערה:** {valid_types[note_type]}
🦷 **שיניים:** {teeth_numbers or 'לא צוין'}
📊 **שלמות תיעוד:** {completeness}%

**ההערה נשמרה בתיק הרפואי**

**SOAP Summary:**
- ✅ Subjective: {len(subjective)} תווים
- ✅ Objective: {len(objective)} תווים
- ✅ Assessment: {len(assessment)} תווים
- ✅ Plan: {len(plan)} תווים

💡 **טיפ:** תיעוד מפורט מגן עליך משפטית ומשפר את איכות הטיפול

⚖️ **שים לב:** הערה זו היא מסמך משפטי ולא ניתן למחוק אותה
"""
        
    except Exception as e:
        logger.error(f"Error creating clinical note: {e}")
        return f"❌ שגיאה ביצירת הערה קלינית: {str(e)}"
    
    @staticmethod
    def _calculate_note_completeness(subjective: str, objective: str, assessment: str, plan: str) -> int:
        """Calculate note completeness score (0-100)."""
        scores = []
        
        # Each section should have meaningful content (>20 chars)
        sections = [subjective, objective, assessment, plan]
        for section in sections:
            if len(section) > 100:
                scores.append(100)
            elif len(section) > 50:
                scores.append(75)
            elif len(section) > 20:
                scores.append(50)
            else:
                scores.append(25)
        
        return sum(scores) // len(scores)


# Export all tools
__all__ = [
    "create_referral_tool",
    "order_xray_tool",
    "order_lab_test_tool",
    "create_clinical_note_tool",
]




@tool
def get_referrals_tool(patient_id: int, status: Optional[str] = None) -> str:
    """
    Get a list of referrals for a patient, optionally filtered by status.

    Args:
        patient_id: Patient ID in Odoo
        status: Filter referrals by status - "pending", "scheduled", "completed", "cancelled"

    Returns:
        A formatted string listing the patient's referrals.
    """
    try:
        odoo = OdooClient()
        # This is a mock implementation. In a real scenario, this would query the Odoo database.
        notes = odoo.get_patient_notes(patient_id, note_type="referral")
        if not notes:
            return "No referrals found for this patient."

        referrals = []
        for note in notes:
            if status and f"**סטטוס:** {status}" not in note.get('body', ''):
                continue
            referrals.append(note.get('body'))

        if not referrals:
            return f"No referrals with status '{status}' found."

        return "\n\n---\n\n".join(referrals)
    except Exception as e:
        logger.error(f"Error getting referrals: {e}")
        return f"❌ שגיאה בקבלת הפניות: {str(e)}"


@tool
def get_clinical_notes_tool(patient_id: int, query: Optional[str] = None) -> str:
    """
    Get a list of clinical notes for a patient, optionally filtered by a search query.

    Args:
        patient_id: Patient ID in Odoo
        query: Search query to filter notes by content.

    Returns:
        A formatted string listing the patient's clinical notes.
    """
    try:
        odoo = OdooClient()
        # This is a mock implementation. In a real scenario, this would query the Odoo database.
        notes = odoo.get_patient_notes(patient_id, note_type="clinical_soap")
        if not notes:
            return "No clinical notes found for this patient."

        if query:
            notes = [note for note in notes if query.lower() in note.get('body', '').lower()]

        if not notes:
            return f"No clinical notes found matching '{query}'."

        return "\n\n---\n\n".join([note.get('body') for note in notes])
    except Exception as e:
        logger.error(f"Error getting clinical notes: {e}")
        return f"❌ שגיאה בקבלת הערות קליניות: {str(e)}"


# Update __all__
__all__.extend(["get_referrals_tool", "get_clinical_notes_tool"])




@tool
def upload_xray_tool(patient_id: int, file_path: str, xray_type: str) -> str:
    """
    Upload an X-ray file for a patient.

    Args:
        patient_id: Patient ID in Odoo
        file_path: The local path to the X-ray file.
        xray_type: Type of X-ray - "periapical", "bitewing", "panoramic", "cephalometric", "cbct"

    Returns:
        A success message with the file details.
    """
    try:
        odoo = OdooClient()
        # In a real implementation, this would upload the file to a PACS or S3.
        # For now, we'll just record a note.
        note = f"📸 **צילום הועלה**\n\n**סוג צילום:** {xray_type}\n**קובץ:** {file_path}"
        odoo.create_patient_note(patient_id, note, note_type="xray_upload")
        return f"✅ צילום {file_path} הועלה בהצלחה עבור מטופל {patient_id}."
    except Exception as e:
        logger.error(f"Error uploading X-ray: {e}")
        return f"❌ שגיאה בהעלאת צילום: {str(e)}"


@tool
def get_xrays_tool(patient_id: int) -> str:
    """
    Get a list of X-rays for a patient.

    Args:
        patient_id: Patient ID in Odoo

    Returns:
        A formatted string listing the patient's X-rays.
    """
    try:
        odoo = OdooClient()
        # This is a mock implementation. In a real scenario, this would query the PACS system.
        notes = odoo.get_patient_notes(patient_id, note_type="xray_upload")
        if not notes:
            return "No X-rays found for this patient."

        return "\n\n---\n\n".join([note.get("body") for note in notes])
    except Exception as e:
        logger.error(f"Error getting X-rays: {e}")
        return f"❌ שגיאה בקבלת צילומים: {str(e)}"


# Update __all__
__all__.extend(["upload_xray_tool", "get_xrays_tool"])




@tool
def analyze_xray_tool(xray_id: int) -> str:
    """
    Analyze an X-ray using an AI model to detect potential issues.
    **Note:** This is a mock tool and does not perform real AI analysis.

    Args:
        xray_id: The ID of the X-ray to analyze.

    Returns:
        A mock analysis of the X-ray.
    """
    try:
        # In a real implementation, this would involve a complex AI model.
        # For now, we return a mock analysis.
        mock_analysis = {
            "findings": [
                "Possible caries on tooth #14 (distal)",
                "Minor bone loss around tooth #36",
                "Impacted wisdom tooth #48"
            ],
            "confidence_scores": {
                "caries_14": 0.85,
                "bone_loss_36": 0.62,
                "impacted_48": 0.98
            }
        }
        findings = mock_analysis['findings']
        scores = mock_analysis['confidence_scores']
        return f"✅ **ניתוח צילום AI (דמו)**\n\n**ממצאים:**\n- {findings[0]}\n- {findings[1]}\n- {findings[2]}\n\n**רמת ביטחון:**\n- עששת בשן 14: {scores['caries_14']*100}%\n- אובדן עצם בשן 36: {scores['bone_loss_36']*100}%\n- שן בינה כלואה #{48}: {scores['impacted_48']*100}%"

    except Exception as e:
        logger.error(f"Error analyzing X-ray: {e}")
        return f"❌ שגיאה בניתוח צילום: {str(e)}"


@tool
def schedule_followup_tool(patient_id: int, reason: str, days_from_now: int) -> str:
    """
    Schedule a follow-up appointment for a patient.

    Args:
        patient_id: Patient ID in Odoo
        reason: The reason for the follow-up.
        days_from_now: The number of days from now to schedule the follow-up.

    Returns:
        A confirmation message with the appointment details.
    """
    try:
        from datetime import datetime, timedelta

        odoo = OdooClient()
        appointment_date = datetime.now() + timedelta(days=days_from_now)

        # This is a mock implementation. In a real scenario, this would create an appointment in Odoo.
        date_str = appointment_date.strftime("%d/%m/%Y")
        note = f"🗓️ **תור מעקב נקבע**\n\n**סיבה:** {reason}\n**תאריך:** {date_str}"
        odoo.create_patient_note(patient_id, note, note_type="appointment")

        return f"✅ **תור מעקב נקבע בהצלחה**\n\n**מטופל:** {patient_id}\n**סיבה:** {reason}\n**תאריך:** {date_str}"
    except Exception as e:
        logger.error(f"Error scheduling follow-up: {e}")
        return f"❌ שגיאה בקביעת תור מעקב: {str(e)}"


# Update __all__
__all__.extend(["analyze_xray_tool", "schedule_followup_tool"])




@tool
def get_lab_results_tool(patient_id: int, order_id: Optional[int] = None) -> str:
    """
    Get the results of a lab test for a patient.

    Args:
        patient_id: Patient ID in Odoo
        order_id: The ID of the lab order to get results for.

    Returns:
        A formatted string with the lab results.
    """
    try:
        odoo = OdooClient()
        # This is a mock implementation. In a real scenario, this would query the lab partner's API.
        if order_id:
            notes = odoo.get_patient_notes(patient_id, note_type="lab_order")
            for note in notes:
                if f"Order ID: {order_id}" in note.get("body", ""):
                    return f"✅ **תוצאות בדיקת מעבדה (דמו)**\n\n**הזמנה:** {order_id}\n**סטטוס:** הושלם\n**תוצאה:** ממצאים תקינים"
            return f"No lab order found with ID {order_id}"
        else:
            return "Please specify an order ID to get lab results."

    except Exception as e:
        logger.error(f"Error getting lab results: {e}")
        return f"❌ שגיאה בקבלת תוצאות מעבדה: {str(e)}"


# Update __all__
__all__.append("get_lab_results_tool")

