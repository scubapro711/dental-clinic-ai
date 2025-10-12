"""
Clinical Tools for שרה (Clinical Assistant Agent)

These tools provide שרה with the ability to:
1. Manage dental charts and treatment records
2. Handle prescriptions and medications
3. Access and update medical history
4. Create and manage treatment plans

Reference: AGENT_ARCHITECTURE_ANALYSIS.md, ODOO_DENTAL_MODULE_ANALYSIS.md
"""

from typing import Dict, Any, List, Optional
from langchain.tools import tool
import logging

from app.integrations.odoo_client_v3 import odoo_client_v3

logger = logging.getLogger(__name__)


# ========== DENTAL CHART & TREATMENTS ==========

@tool
def get_patient_dental_chart(patient_id: int) -> Dict[str, Any]:
    """
    Get patient's dental chart (odontogram) showing status of all teeth.
    
    Use this to:
    - View current dental status
    - Check treatment history per tooth
    - Plan new treatments
    
    Args:
        patient_id: Patient ID in Odoo
    
    Returns:
        Dental chart with all teeth status and last update date
    """
    try:
        result = odoo_client_v3.get_dental_chart(patient_id)
        
        if not result:
            return {
                "success": False,
                "message": f"No dental chart found for patient {patient_id}. Patient may be new."
            }
        
        return {
            "success": True,
            "data": result,
            "message": f"Retrieved dental chart with {len(result.get('teeth', []))} teeth records"
        }
    except Exception as e:
        logger.error(f"Error getting dental chart: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve dental chart"
        }


@tool
def update_tooth_status(
    patient_id: int,
    tooth_code: str,
    status: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update the status of a specific tooth in patient's dental chart.
    
    Common tooth statuses:
    - healthy: No issues
    - cavity: Cavity detected
    - filled: Filled/restored
    - crown: Has crown
    - root_canal: Root canal treatment
    - missing: Tooth missing
    - implant: Dental implant
    
    Tooth codes: Use FDI notation (11-18, 21-28, 31-38, 41-48)
    
    Args:
        patient_id: Patient ID
        tooth_code: Tooth code (e.g., '11', '21', '31', '41')
        status: New status for the tooth
        notes: Optional notes about the update
    
    Returns:
        Success status and record ID
    """
    try:
        record_id = odoo_client_v3.update_tooth_status(
            patient_id=patient_id,
            tooth_code=tooth_code,
            status=status,
            notes=notes
        )
        
        if not record_id:
            return {
                "success": False,
                "message": f"Failed to update tooth {tooth_code}"
            }
        
        return {
            "success": True,
            "record_id": record_id,
            "message": f"Updated tooth {tooth_code} to status '{status}'"
        }
    except Exception as e:
        logger.error(f"Error updating tooth status: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update tooth status"
        }


@tool
def get_treatment_history(
    patient_id: int,
    tooth_code: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get patient's dental treatment history.
    
    Use this to:
    - Review past treatments
    - Check treatment outcomes
    - Plan follow-up care
    
    Args:
        patient_id: Patient ID
        tooth_code: Optional - filter by specific tooth
        limit: Maximum number of records (default 50)
    
    Returns:
        List of treatment records with dates, types, and outcomes
    """
    try:
        treatments = odoo_client_v3.get_treatment_history(
            patient_id=patient_id,
            tooth_code=tooth_code,
            limit=limit
        )
        
        return {
            "success": True,
            "data": treatments,
            "count": len(treatments),
            "message": f"Retrieved {len(treatments)} treatment records"
        }
    except Exception as e:
        logger.error(f"Error getting treatment history: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve treatment history"
        }


@tool
def create_treatment_record(
    patient_id: int,
    treatment_type: str,
    tooth_code: Optional[str] = None,
    doctor_id: Optional[int] = None,
    description: Optional[str] = None,
    cost: Optional[float] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new dental treatment record after completing a procedure.
    
    Common treatment types:
    - filling: Dental filling
    - extraction: Tooth extraction
    - cleaning: Professional cleaning
    - root_canal: Root canal treatment
    - crown: Crown placement
    - implant: Dental implant
    - whitening: Teeth whitening
    - orthodontics: Braces/aligners
    
    Args:
        patient_id: Patient ID
        treatment_type: Type of treatment performed
        tooth_code: Tooth code if applicable
        doctor_id: Doctor who performed treatment
        description: Detailed description
        cost: Treatment cost in ILS
        notes: Additional notes
    
    Returns:
        Success status and treatment record ID
    """
    try:
        record_id = odoo_client_v3.create_treatment_record(
            patient_id=patient_id,
            treatment_type=treatment_type,
            tooth_code=tooth_code,
            doctor_id=doctor_id,
            description=description,
            cost=cost,
            notes=notes
        )
        
        if not record_id:
            return {
                "success": False,
                "message": "Failed to create treatment record"
            }
        
        return {
            "success": True,
            "record_id": record_id,
            "message": f"Created treatment record for {treatment_type}"
        }
    except Exception as e:
        logger.error(f"Error creating treatment record: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create treatment record"
        }


# ========== PRESCRIPTIONS & MEDICATIONS ==========

@tool
def get_patient_prescriptions(
    patient_id: int,
    active_only: bool = False
) -> Dict[str, Any]:
    """
    Get patient's prescription history.
    
    Use this to:
    - Review current medications
    - Check prescription history
    - Avoid drug interactions
    
    Args:
        patient_id: Patient ID
        active_only: If True, return only active prescriptions
    
    Returns:
        List of prescription records
    """
    try:
        prescriptions = odoo_client_v3.get_patient_prescriptions(
            patient_id=patient_id,
            active_only=active_only
        )
        
        return {
            "success": True,
            "data": prescriptions,
            "count": len(prescriptions),
            "message": f"Retrieved {len(prescriptions)} prescriptions"
        }
    except Exception as e:
        logger.error(f"Error getting prescriptions: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve prescriptions"
        }


@tool
def create_prescription(
    patient_id: int,
    doctor_id: int,
    medications: str,
    diagnosis: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new prescription for patient.
    
    IMPORTANT: medications parameter should be a JSON string with this format:
    [
        {
            "medication_id": 123,
            "dosage": "500mg",
            "frequency": "3 times daily",
            "duration": "7 days"
        }
    ]
    
    Use search_medications tool first to find medication IDs.
    
    Args:
        patient_id: Patient ID
        doctor_id: Prescribing doctor ID
        medications: JSON string of medications list
        diagnosis: Diagnosis/reason for prescription
        notes: Additional notes
    
    Returns:
        Success status and prescription ID
    """
    try:
        import json
        medications_list = json.loads(medications)
        
        prescription_id = odoo_client_v3.create_prescription(
            patient_id=patient_id,
            doctor_id=doctor_id,
            medications=medications_list,
            diagnosis=diagnosis,
            notes=notes
        )
        
        if not prescription_id:
            return {
                "success": False,
                "message": "Failed to create prescription"
            }
        
        return {
            "success": True,
            "prescription_id": prescription_id,
            "message": f"Created prescription with {len(medications_list)} medications"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "Invalid medications format",
            "message": "medications must be a valid JSON string"
        }
    except Exception as e:
        logger.error(f"Error creating prescription: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create prescription"
        }


@tool
def search_medications(
    name: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search for medications in the database.
    
    Use this before creating prescriptions to find medication IDs.
    
    Common categories:
    - antibiotic: Antibiotics
    - painkiller: Pain relievers
    - anti_inflammatory: Anti-inflammatory drugs
    - anesthetic: Local anesthetics
    
    Args:
        name: Medication name (partial match)
        category: Medication category
        limit: Maximum results (default 20)
    
    Returns:
        List of matching medications with IDs and details
    """
    try:
        medications = odoo_client_v3.search_medications(
            name=name,
            category=category,
            limit=limit
        )
        
        return {
            "success": True,
            "data": medications,
            "count": len(medications),
            "message": f"Found {len(medications)} medications"
        }
    except Exception as e:
        logger.error(f"Error searching medications: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search medications"
        }


# ========== MEDICAL HISTORY ==========

@tool
def get_patient_medical_history(patient_id: int) -> Dict[str, Any]:
    """
    Get comprehensive medical history for patient.
    
    Returns:
    - Allergies
    - Chronic conditions
    - Current medications
    
    CRITICAL: Always check this before prescribing or treating!
    
    Args:
        patient_id: Patient ID
    
    Returns:
        Complete medical history including allergies and conditions
    """
    try:
        history = odoo_client_v3.get_patient_medical_history(patient_id)
        
        return {
            "success": True,
            "data": history,
            "allergies_count": len(history.get('allergies', [])),
            "conditions_count": len(history.get('chronic_conditions', [])),
            "medications_count": len(history.get('current_medications', [])),
            "message": "Retrieved complete medical history"
        }
    except Exception as e:
        logger.error(f"Error getting medical history: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve medical history"
        }


@tool
def add_patient_allergy(
    patient_id: int,
    disease_id: int,
    severity: str = "moderate",
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add an allergy to patient's medical history.
    
    Severity levels:
    - mild: Minor reaction
    - moderate: Significant reaction
    - severe: Life-threatening reaction
    
    Use search_diseases tool first to find disease_id for the allergen.
    
    Args:
        patient_id: Patient ID
        disease_id: Disease/allergen ID from medical.disease
        severity: Severity level
        notes: Additional notes about the allergy
    
    Returns:
        Success status and record ID
    """
    try:
        record_id = odoo_client_v3.add_patient_disease(
            patient_id=patient_id,
            disease_id=disease_id,
            is_allergy=True,
            severity=severity,
            notes=notes
        )
        
        if not record_id:
            return {
                "success": False,
                "message": "Failed to add allergy"
            }
        
        return {
            "success": True,
            "record_id": record_id,
            "message": f"Added allergy with severity: {severity}"
        }
    except Exception as e:
        logger.error(f"Error adding allergy: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add allergy"
        }


@tool
def add_patient_condition(
    patient_id: int,
    disease_id: int,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a chronic condition or disease to patient's medical history.
    
    Use search_diseases tool first to find disease_id.
    
    Args:
        patient_id: Patient ID
        disease_id: Disease ID from medical.disease
        notes: Additional notes about the condition
    
    Returns:
        Success status and record ID
    """
    try:
        record_id = odoo_client_v3.add_patient_disease(
            patient_id=patient_id,
            disease_id=disease_id,
            is_allergy=False,
            notes=notes
        )
        
        if not record_id:
            return {
                "success": False,
                "message": "Failed to add condition"
            }
        
        return {
            "success": True,
            "record_id": record_id,
            "message": "Added chronic condition to medical history"
        }
    except Exception as e:
        logger.error(f"Error adding condition: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add condition"
        }


@tool
def search_diseases(
    name: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search for diseases/conditions/allergens in the database.
    
    Use this before adding allergies or conditions to find disease IDs.
    
    Args:
        name: Disease name (partial match)
        category: Disease category
        limit: Maximum results (default 20)
    
    Returns:
        List of matching diseases with IDs and details
    """
    try:
        diseases = odoo_client_v3.search_diseases(
            name=name,
            category=category,
            limit=limit
        )
        
        return {
            "success": True,
            "data": diseases,
            "count": len(diseases),
            "message": f"Found {len(diseases)} diseases"
        }
    except Exception as e:
        logger.error(f"Error searching diseases: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search diseases"
        }


# ========== TREATMENT PLANNING ==========

@tool
def get_treatment_plans(
    patient_id: int,
    active_only: bool = True
) -> Dict[str, Any]:
    """
    Get treatment plans for patient.
    
    Use this to:
    - Review planned treatments
    - Check treatment progress
    - Estimate costs
    
    Args:
        patient_id: Patient ID
        active_only: If True, return only active plans
    
    Returns:
        List of treatment plans
    """
    try:
        plans = odoo_client_v3.get_treatment_plans(
            patient_id=patient_id,
            active_only=active_only
        )
        
        return {
            "success": True,
            "data": plans,
            "count": len(plans),
            "message": f"Retrieved {len(plans)} treatment plans"
        }
    except Exception as e:
        logger.error(f"Error getting treatment plans: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve treatment plans"
        }


@tool
def create_treatment_plan(
    patient_id: int,
    name: str,
    doctor_id: int,
    description: Optional[str] = None,
    treatments: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new treatment plan for patient.
    
    IMPORTANT: treatments parameter should be a JSON string with this format:
    [
        {
            "treatment_type": "filling",
            "tooth_code": "16",
            "description": "Composite filling",
            "cost": 500.0,
            "priority": "high"
        }
    ]
    
    Args:
        patient_id: Patient ID
        name: Plan name/title
        doctor_id: Doctor creating the plan
        description: Plan description
        treatments: JSON string of treatments list
        notes: Additional notes
    
    Returns:
        Success status and treatment plan ID
    """
    try:
        treatments_list = None
        if treatments:
            import json
            treatments_list = json.loads(treatments)
        
        plan_id = odoo_client_v3.create_treatment_plan(
            patient_id=patient_id,
            name=name,
            doctor_id=doctor_id,
            description=description,
            treatments=treatments_list,
            notes=notes
        )
        
        if not plan_id:
            return {
                "success": False,
                "message": "Failed to create treatment plan"
            }
        
        return {
            "success": True,
            "plan_id": plan_id,
            "message": f"Created treatment plan: {name}"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "Invalid treatments format",
            "message": "treatments must be a valid JSON string"
        }
    except Exception as e:
        logger.error(f"Error creating treatment plan: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create treatment plan"
        }


@tool
def get_dentist_schedule(
    doctor_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get dentist's schedule and availability.
    
    Use this to:
    - Check dentist availability
    - Schedule appointments
    - Plan treatments
    
    Args:
        doctor_id: Doctor ID
        date_from: Start date (YYYY-MM-DD format)
        date_to: End date (YYYY-MM-DD format)
    
    Returns:
        List of time slots with availability status
    """
    try:
        slots = odoo_client_v3.get_dentist_schedule(
            doctor_id=doctor_id,
            date_from=date_from,
            date_to=date_to
        )
        
        available_slots = [s for s in slots if s.get('is_available')]
        
        return {
            "success": True,
            "data": slots,
            "total_slots": len(slots),
            "available_slots": len(available_slots),
            "message": f"Found {len(available_slots)} available slots"
        }
    except Exception as e:
        logger.error(f"Error getting dentist schedule: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve dentist schedule"
        }


# Export all tools as a list
CLINICAL_TOOLS = [
    get_patient_dental_chart,
    update_tooth_status,
    get_treatment_history,
    create_treatment_record,
    get_patient_prescriptions,
    create_prescription,
    search_medications,
    get_patient_medical_history,
    add_patient_allergy,
    add_patient_condition,
    search_diseases,
    get_treatment_plans,
    create_treatment_plan,
    get_dentist_schedule
]

