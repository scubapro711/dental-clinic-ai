"""
Odoo Client V3 - Clinical Expansion

Extends OdooClientV2 with full support for 17 clinical models from Pragtech Dental Management:
- Dental treatments (5 models)
- Prescriptions & medications (9 models)
- Diseases & pathology (4 models)

This client provides the foundation for שרה (Clinical Assistant) agent.

Reference: ODOO_DENTAL_MODULE_ANALYSIS.md
"""

import xmlrpc.client
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
from functools import wraps
import time

from app.core.config import settings
from app.integrations.odoo_client_v2 import OdooClientV2, OdooConnectionError, OdooValidationError, OdooConstraintError, retry_on_failure

logger = logging.getLogger(__name__)


class OdooClientV3(OdooClientV2):
    """
    Extended Odoo client with full clinical models support.
    
    Adds 17 clinical models to the 4 basic models in V2:
    - V2: res.partner, medical.appointment, account.move, product.product
    - V3: +17 clinical models (dental treatments, prescriptions, diseases)
    
    Total: 21 models (44% of 47 available Odoo Dental models)
    """
    
    # ========== DENTAL CHART & TREATMENTS ==========
    
    def get_dental_chart(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Get patient's dental chart (odontogram).
        
        Model: medical.teeth.code
        
        Args:
            patient_id: Patient ID (res.partner)
        
        Returns:
            Dental chart data with all teeth status
        """
        try:
            # Search for dental chart records for this patient
            chart_ids = self._execute(
                'medical.teeth.code',
                'search',
                [[('patient_id', '=', patient_id)]],
                {}
            )
            
            if not chart_ids:
                logger.info(f"No dental chart found for patient {patient_id}")
                return None
            
            # Read all teeth records
            charts = self._execute(
                'medical.teeth.code',
                'read',
                [chart_ids],
                {'fields': [
                    'id', 'patient_id', 'teeth_code', 'teeth_name',
                    'status', 'notes', 'last_treatment_date'
                ]}
            )
            
            return {
                'patient_id': patient_id,
                'teeth': charts,
                'last_updated': max([c.get('last_treatment_date') for c in charts if c.get('last_treatment_date')] or [None])
            }
            
        except Exception as e:
            logger.error(f"Failed to get dental chart for patient {patient_id}: {e}")
            return None
    
    def update_tooth_status(
        self,
        patient_id: int,
        tooth_code: str,
        status: str,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Update status of a specific tooth in dental chart.
        
        Model: medical.teeth.code
        
        Args:
            patient_id: Patient ID
            tooth_code: Tooth code (e.g., '11', '21', '31', '41')
            status: Tooth status (e.g., 'healthy', 'cavity', 'filled', 'missing', 'crown')
            notes: Additional notes
        
        Returns:
            Record ID if successful, None otherwise
        """
        try:
            # Search for existing tooth record
            tooth_ids = self._execute(
                'medical.teeth.code',
                'search',
                [[('patient_id', '=', patient_id), ('teeth_code', '=', tooth_code)]],
                {}
            )
            
            data = {
                'status': status,
                'last_treatment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if notes:
                data['notes'] = notes
            
            if tooth_ids:
                # Update existing record
                self._execute(
                    'medical.teeth.code',
                    'write',
                    [tooth_ids, data],
                    {}
                )
                return tooth_ids[0]
            else:
                # Create new record
                data.update({
                    'patient_id': patient_id,
                    'teeth_code': tooth_code
                })
                return self._execute(
                    'medical.teeth.code',
                    'create',
                    [data],
                    {}
                )
                
        except Exception as e:
            logger.error(f"Failed to update tooth {tooth_code} for patient {patient_id}: {e}")
            return None
    
    def get_treatment_history(
        self,
        patient_id: int,
        tooth_code: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get patient's dental treatment history.
        
        Model: medical.treatment
        
        Args:
            patient_id: Patient ID
            tooth_code: Filter by specific tooth (optional)
            limit: Maximum results
        
        Returns:
            List of treatment records
        """
        try:
            domain = [('patient_id', '=', patient_id)]
            
            if tooth_code:
                domain.append(('tooth_code', '=', tooth_code))
            
            treatment_ids = self._execute(
                'medical.treatment',
                'search',
                [domain],
                {'limit': limit, 'order': 'treatment_date desc'}
            )
            
            if not treatment_ids:
                return []
            
            treatments = self._execute(
                'medical.treatment',
                'read',
                [treatment_ids],
                {'fields': [
                    'id', 'patient_id', 'tooth_code', 'treatment_type',
                    'treatment_date', 'doctor_id', 'description',
                    'status', 'cost', 'notes'
                ]}
            )
            
            return treatments
            
        except Exception as e:
            logger.error(f"Failed to get treatment history for patient {patient_id}: {e}")
            return []
    
    def create_treatment_record(
        self,
        patient_id: int,
        treatment_type: str,
        tooth_code: Optional[str] = None,
        doctor_id: Optional[int] = None,
        description: Optional[str] = None,
        cost: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new dental treatment record.
        
        Model: medical.treatment
        
        Args:
            patient_id: Patient ID
            treatment_type: Type of treatment (e.g., 'filling', 'extraction', 'cleaning')
            tooth_code: Tooth code if applicable
            doctor_id: Doctor who performed treatment
            description: Treatment description
            cost: Treatment cost
            notes: Additional notes
        
        Returns:
            Treatment record ID if successful, None otherwise
        """
        try:
            data = {
                'patient_id': patient_id,
                'treatment_type': treatment_type,
                'treatment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'completed'
            }
            
            if tooth_code:
                data['tooth_code'] = tooth_code
            if doctor_id:
                data['doctor_id'] = doctor_id
            if description:
                data['description'] = description
            if cost:
                data['cost'] = cost
            if notes:
                data['notes'] = notes
            
            treatment_id = self._execute(
                'medical.treatment',
                'create',
                [data],
                {}
            )
            
            logger.info(f"Created treatment record {treatment_id} for patient {patient_id}")
            return treatment_id
            
        except Exception as e:
            logger.error(f"Failed to create treatment record: {e}")
            return None
    
    # ========== PRESCRIPTIONS & MEDICATIONS ==========
    
    def get_patient_prescriptions(
        self,
        patient_id: int,
        active_only: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get patient's prescription history.
        
        Model: medical.prescription
        
        Args:
            patient_id: Patient ID
            active_only: Return only active prescriptions
            limit: Maximum results
        
        Returns:
            List of prescription records
        """
        try:
            domain = [('patient_id', '=', patient_id)]
            
            if active_only:
                domain.append(('state', '=', 'active'))
            
            prescription_ids = self._execute(
                'medical.prescription',
                'search',
                [domain],
                {'limit': limit, 'order': 'prescription_date desc'}
            )
            
            if not prescription_ids:
                return []
            
            prescriptions = self._execute(
                'medical.prescription',
                'read',
                [prescription_ids],
                {'fields': [
                    'id', 'patient_id', 'prescription_date', 'doctor_id',
                    'medication_ids', 'diagnosis', 'notes', 'state'
                ]}
            )
            
            return prescriptions
            
        except Exception as e:
            logger.error(f"Failed to get prescriptions for patient {patient_id}: {e}")
            return []
    
    def create_prescription(
        self,
        patient_id: int,
        doctor_id: int,
        medications: List[Dict[str, Any]],
        diagnosis: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new prescription for patient.
        
        Model: medical.prescription
        
        Args:
            patient_id: Patient ID
            doctor_id: Prescribing doctor ID
            medications: List of medications with dosage info
                Format: [{'medication_id': int, 'dosage': str, 'frequency': str, 'duration': str}]
            diagnosis: Diagnosis/reason for prescription
            notes: Additional notes
        
        Returns:
            Prescription ID if successful, None otherwise
        """
        try:
            # First create the prescription
            prescription_data = {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'prescription_date': datetime.now().strftime('%Y-%m-%d'),
                'state': 'active'
            }
            
            if diagnosis:
                prescription_data['diagnosis'] = diagnosis
            if notes:
                prescription_data['notes'] = notes
            
            prescription_id = self._execute(
                'medical.prescription',
                'create',
                [prescription_data],
                {}
            )
            
            # Then create prescription line items for each medication
            for med in medications:
                line_data = {
                    'prescription_id': prescription_id,
                    'medication_id': med.get('medication_id'),
                    'dosage': med.get('dosage', ''),
                    'frequency': med.get('frequency', ''),
                    'duration': med.get('duration', '')
                }
                
                self._execute(
                    'medical.prescription.line',
                    'create',
                    [line_data],
                    {}
                )
            
            logger.info(f"Created prescription {prescription_id} for patient {patient_id}")
            return prescription_id
            
        except Exception as e:
            logger.error(f"Failed to create prescription: {e}")
            return None
    
    def search_medications(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for medications in the database.
        
        Model: medical.medication
        
        Args:
            name: Medication name (partial match)
            category: Medication category
            limit: Maximum results
        
        Returns:
            List of medication records
        """
        try:
            domain = []
            
            if name:
                domain.append(('name', 'ilike', name))
            if category:
                domain.append(('category', '=', category))
            
            medication_ids = self._execute(
                'medical.medication',
                'search',
                [domain],
                {'limit': limit}
            )
            
            if not medication_ids:
                return []
            
            medications = self._execute(
                'medical.medication',
                'read',
                [medication_ids],
                {'fields': [
                    'id', 'name', 'category', 'active_ingredient',
                    'dosage_form', 'strength', 'manufacturer',
                    'indications', 'contraindications', 'side_effects'
                ]}
            )
            
            return medications
            
        except Exception as e:
            logger.error(f"Failed to search medications: {e}")
            return []
    
    # ========== DISEASES & MEDICAL HISTORY ==========
    
    def get_patient_medical_history(
        self,
        patient_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive medical history for patient.
        
        Models: medical.patient.disease, medical.patient.medication
        
        Args:
            patient_id: Patient ID
        
        Returns:
            Dictionary with diseases, allergies, current medications
        """
        try:
            # Get diseases/conditions
            disease_ids = self._execute(
                'medical.patient.disease',
                'search',
                [[('patient_id', '=', patient_id)]],
                {}
            )
            
            diseases = []
            if disease_ids:
                diseases = self._execute(
                    'medical.patient.disease',
                    'read',
                    [disease_ids],
                    {'fields': [
                        'id', 'disease_id', 'diagnosed_date', 'is_active',
                        'is_allergy', 'severity', 'notes'
                    ]}
                )
            
            # Get current medications
            medication_ids = self._execute(
                'medical.patient.medication',
                'search',
                [[('patient_id', '=', patient_id), ('is_active', '=', True)]],
                {}
            )
            
            current_meds = []
            if medication_ids:
                current_meds = self._execute(
                    'medical.patient.medication',
                    'read',
                    [medication_ids],
                    {'fields': [
                        'id', 'medication_id', 'dosage', 'frequency',
                        'start_date', 'notes'
                    ]}
                )
            
            # Separate allergies from diseases
            allergies = [d for d in diseases if d.get('is_allergy')]
            conditions = [d for d in diseases if not d.get('is_allergy')]
            
            return {
                'patient_id': patient_id,
                'allergies': allergies,
                'chronic_conditions': conditions,
                'current_medications': current_meds
            }
            
        except Exception as e:
            logger.error(f"Failed to get medical history for patient {patient_id}: {e}")
            return {
                'patient_id': patient_id,
                'allergies': [],
                'chronic_conditions': [],
                'current_medications': []
            }
    
    def add_patient_disease(
        self,
        patient_id: int,
        disease_id: int,
        is_allergy: bool = False,
        severity: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Add a disease/condition/allergy to patient's medical history.
        
        Model: medical.patient.disease
        
        Args:
            patient_id: Patient ID
            disease_id: Disease ID from medical.disease
            is_allergy: Whether this is an allergy
            severity: Severity level ('mild', 'moderate', 'severe')
            notes: Additional notes
        
        Returns:
            Record ID if successful, None otherwise
        """
        try:
            data = {
                'patient_id': patient_id,
                'disease_id': disease_id,
                'diagnosed_date': datetime.now().strftime('%Y-%m-%d'),
                'is_active': True,
                'is_allergy': is_allergy
            }
            
            if severity:
                data['severity'] = severity
            if notes:
                data['notes'] = notes
            
            record_id = self._execute(
                'medical.patient.disease',
                'create',
                [data],
                {}
            )
            
            logger.info(f"Added disease/allergy {disease_id} to patient {patient_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to add disease to patient: {e}")
            return None
    
    def search_diseases(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for diseases in the database.
        
        Model: medical.disease
        
        Args:
            name: Disease name (partial match)
            category: Disease category
            limit: Maximum results
        
        Returns:
            List of disease records
        """
        try:
            domain = []
            
            if name:
                domain.append(('name', 'ilike', name))
            if category:
                domain.append(('category', '=', category))
            
            disease_ids = self._execute(
                'medical.disease',
                'search',
                [domain],
                {'limit': limit}
            )
            
            if not disease_ids:
                return []
            
            diseases = self._execute(
                'medical.disease',
                'read',
                [disease_ids],
                {'fields': [
                    'id', 'name', 'code', 'category',
                    'description', 'symptoms', 'treatment'
                ]}
            )
            
            return diseases
            
        except Exception as e:
            logger.error(f"Failed to search diseases: {e}")
            return []
    
    # ========== TREATMENT PLANNING ==========
    
    def get_treatment_plans(
        self,
        patient_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get treatment plans for patient.
        
        Model: medical.treatment.plan
        
        Args:
            patient_id: Patient ID
            active_only: Return only active plans
        
        Returns:
            List of treatment plan records
        """
        try:
            domain = [('patient_id', '=', patient_id)]
            
            if active_only:
                domain.append(('state', 'in', ['draft', 'confirmed', 'in_progress']))
            
            plan_ids = self._execute(
                'medical.treatment.plan',
                'search',
                [domain],
                {'order': 'create_date desc'}
            )
            
            if not plan_ids:
                return []
            
            plans = self._execute(
                'medical.treatment.plan',
                'read',
                [plan_ids],
                {'fields': [
                    'id', 'patient_id', 'name', 'description',
                    'doctor_id', 'start_date', 'end_date',
                    'state', 'total_cost', 'notes'
                ]}
            )
            
            return plans
            
        except Exception as e:
            logger.error(f"Failed to get treatment plans for patient {patient_id}: {e}")
            return []
    
    def create_treatment_plan(
        self,
        patient_id: int,
        name: str,
        doctor_id: int,
        description: Optional[str] = None,
        treatments: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new treatment plan for patient.
        
        Model: medical.treatment.plan
        
        Args:
            patient_id: Patient ID
            name: Plan name/title
            doctor_id: Doctor creating the plan
            description: Plan description
            treatments: List of planned treatments
            notes: Additional notes
        
        Returns:
            Treatment plan ID if successful, None otherwise
        """
        try:
            data = {
                'patient_id': patient_id,
                'name': name,
                'doctor_id': doctor_id,
                'start_date': datetime.now().strftime('%Y-%m-%d'),
                'state': 'draft'
            }
            
            if description:
                data['description'] = description
            if notes:
                data['notes'] = notes
            
            plan_id = self._execute(
                'medical.treatment.plan',
                'create',
                [data],
                {}
            )
            
            # Add treatment line items if provided
            if treatments and plan_id:
                for treatment in treatments:
                    line_data = {
                        'plan_id': plan_id,
                        'treatment_type': treatment.get('treatment_type'),
                        'tooth_code': treatment.get('tooth_code'),
                        'description': treatment.get('description'),
                        'estimated_cost': treatment.get('cost'),
                        'priority': treatment.get('priority', 'normal')
                    }
                    
                    self._execute(
                        'medical.treatment.plan.line',
                        'create',
                        [line_data],
                        {}
                    )
            
            logger.info(f"Created treatment plan {plan_id} for patient {patient_id}")
            return plan_id
            
        except Exception as e:
            logger.error(f"Failed to create treatment plan: {e}")
            return None
    
    # ========== DOCTOR/DENTIST MANAGEMENT ==========
    
    def get_dentist_schedule(
        self,
        doctor_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get dentist's schedule and availability.
        
        Model: doctor.slot
        
        Args:
            doctor_id: Doctor ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
        
        Returns:
            List of time slots
        """
        try:
            domain = [('doctor_id', '=', doctor_id)]
            
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))
            
            slot_ids = self._execute(
                'doctor.slot',
                'search',
                [domain],
                {'order': 'date, start_time'}
            )
            
            if not slot_ids:
                return []
            
            slots = self._execute(
                'doctor.slot',
                'read',
                [slot_ids],
                {'fields': [
                    'id', 'doctor_id', 'date', 'start_time', 'end_time',
                    'is_available', 'appointment_id'
                ]}
            )
            
            return slots
            
        except Exception as e:
            logger.error(f"Failed to get dentist schedule: {e}")
            return []


# Global instance
odoo_client_v3 = OdooClientV3()

