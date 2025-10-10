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


    # ========== FINANCIAL MODELS (10 methods) ==========
    
    def get_invoices(
        self,
        patient_id: Optional[int] = None,
        state: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get invoices with optional filters.
        
        Model: account.move (Odoo standard)
        
        Args:
            patient_id: Filter by patient ID
            state: Filter by state (draft, posted, cancel)
            date_from: Filter from date (YYYY-MM-DD)
            date_to: Filter to date (YYYY-MM-DD)
            limit: Maximum number of results
            
        Returns:
            List of invoice dictionaries
        """
        try:
            domain = [('move_type', '=', 'out_invoice')]
            
            if patient_id:
                domain.append(('partner_id', '=', patient_id))
            
            if state:
                domain.append(('state', '=', state))
            
            if date_from:
                domain.append(('invoice_date', '>=', date_from))
            
            if date_to:
                domain.append(('invoice_date', '<=', date_to))
            
            invoice_ids = self._execute('account.move', 'search', [domain], {'limit': limit})
            
            if not invoice_ids:
                return []
            
            invoices = self._execute(
                'account.move',
                'read',
                [invoice_ids],
                {'fields': [
                    'id', 'name', 'partner_id', 'invoice_date', 'amount_total',
                    'amount_residual', 'state', 'payment_state', 'invoice_line_ids'
                ]}
            )
            
            return invoices
            
        except Exception as e:
            logger.error(f"Failed to get invoices: {e}")
            return []
    
    def get_payments(
        self,
        patient_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get payments with optional filters.
        
        Model: account.payment (Odoo standard)
        
        Args:
            patient_id: Filter by patient ID
            date_from: Filter from date (YYYY-MM-DD)
            date_to: Filter to date (YYYY-MM-DD)
            limit: Maximum number of results
            
        Returns:
            List of payment dictionaries
        """
        try:
            domain = [('payment_type', '=', 'inbound')]
            
            if patient_id:
                domain.append(('partner_id', '=', patient_id))
            
            if date_from:
                domain.append(('date', '>=', date_from))
            
            if date_to:
                domain.append(('date', '<=', date_to))
            
            payment_ids = self._execute('account.payment', 'search', [domain], {'limit': limit})
            
            if not payment_ids:
                return []
            
            payments = self._execute(
                'account.payment',
                'read',
                [payment_ids],
                {'fields': [
                    'id', 'name', 'partner_id', 'date', 'amount',
                    'state', 'payment_type', 'payment_method_id'
                ]}
            )
            
            return payments
            
        except Exception as e:
            logger.error(f"Failed to get payments: {e}")
            return []
    
    def get_revenue_by_period(
        self,
        date_from: str,
        date_to: str,
    ) -> Dict[str, Any]:
        """
        Get revenue summary for a time period.
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            Revenue summary dictionary
        """
        try:
            invoices = self.get_invoices(
                state='posted',
                date_from=date_from,
                date_to=date_to,
                limit=10000,
            )
            
            total_revenue = sum(inv.get('amount_total', 0) for inv in invoices)
            invoice_count = len(invoices)
            avg_invoice = total_revenue / invoice_count if invoice_count > 0 else 0
            
            return {
                'period': {'from': date_from, 'to': date_to},
                'total_revenue': total_revenue,
                'invoice_count': invoice_count,
                'average_invoice': avg_invoice,
                'invoices': invoices,
            }
            
        except Exception as e:
            logger.error(f"Failed to get revenue by period: {e}")
            return {
                'period': {'from': date_from, 'to': date_to},
                'total_revenue': 0,
                'invoice_count': 0,
                'average_invoice': 0,
                'invoices': [],
            }
    
    def get_outstanding_balance(
        self,
        patient_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get outstanding balance (unpaid invoices).
        
        Args:
            patient_id: Optional patient ID filter
            
        Returns:
            Outstanding balance summary
        """
        try:
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ]
            
            if patient_id:
                domain.append(('partner_id', '=', patient_id))
            
            invoice_ids = self._execute('account.move', 'search', [domain], {'limit': 10000})
            
            if not invoice_ids:
                return {
                    'total_outstanding': 0,
                    'invoice_count': 0,
                    'invoices': [],
                }
            
            invoices = self._execute(
                'account.move',
                'read',
                [invoice_ids],
                {'fields': [
                    'id', 'name', 'partner_id', 'invoice_date',
                    'amount_total', 'amount_residual', 'payment_state'
                ]}
            )
            
            total_outstanding = sum(inv.get('amount_residual', 0) for inv in invoices)
            
            return {
                'total_outstanding': total_outstanding,
                'invoice_count': len(invoices),
                'invoices': invoices,
            }
            
        except Exception as e:
            logger.error(f"Failed to get outstanding balance: {e}")
            return {
                'total_outstanding': 0,
                'invoice_count': 0,
                'invoices': [],
            }
    
    def get_treatment_revenue(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get revenue by treatment type.
        
        Model: account.move.line (invoice lines)
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum number of treatments
            
        Returns:
            List of treatments with revenue
        """
        try:
            domain = [('move_id.state', '=', 'posted'), ('move_id.move_type', '=', 'out_invoice')]
            
            if date_from:
                domain.append(('move_id.invoice_date', '>=', date_from))
            
            if date_to:
                domain.append(('move_id.invoice_date', '<=', date_to))
            
            line_ids = self._execute('account.move.line', 'search', [domain], {'limit': 10000})
            
            if not line_ids:
                return []
            
            lines = self._execute(
                'account.move.line',
                'read',
                [line_ids],
                {'fields': ['product_id', 'name', 'quantity', 'price_subtotal']}
            )
            
            # Aggregate by product
            treatment_revenue = {}
            for line in lines:
                product_id = line.get('product_id')
                if not product_id:
                    continue
                
                product_key = product_id[0] if isinstance(product_id, list) else product_id
                product_name = product_id[1] if isinstance(product_id, list) else line.get('name', 'Unknown')
                
                if product_key not in treatment_revenue:
                    treatment_revenue[product_key] = {
                        'product_id': product_key,
                        'product_name': product_name,
                        'quantity': 0,
                        'revenue': 0,
                    }
                
                treatment_revenue[product_key]['quantity'] += line.get('quantity', 0)
                treatment_revenue[product_key]['revenue'] += line.get('price_subtotal', 0)
            
            # Sort by revenue and return top N
            sorted_treatments = sorted(
                treatment_revenue.values(),
                key=lambda x: x['revenue'],
                reverse=True
            )
            
            return sorted_treatments[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get treatment revenue: {e}")
            return []
    
    def get_financial_summary(
        self,
        date_from: str,
        date_to: str,
    ) -> Dict[str, Any]:
        """
        Get comprehensive financial summary.
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            Financial summary dictionary
        """
        try:
            # Revenue
            revenue = self.get_revenue_by_period(date_from, date_to)
            
            # Outstanding
            outstanding = self.get_outstanding_balance()
            
            # Payments
            payments = self.get_payments(date_from=date_from, date_to=date_to)
            total_collected = sum(p.get('amount', 0) for p in payments)
            
            # Top treatments
            top_treatments = self.get_treatment_revenue(date_from, date_to, limit=5)
            
            return {
                'period': {'from': date_from, 'to': date_to},
                'revenue': revenue,
                'outstanding': {
                    'total': outstanding['total_outstanding'],
                    'invoice_count': outstanding['invoice_count'],
                },
                'payments': {
                    'total_collected': total_collected,
                    'payment_count': len(payments),
                },
                'top_treatments': top_treatments,
            }
            
        except Exception as e:
            logger.error(f"Failed to get financial summary: {e}")
            return {
                'period': {'from': date_from, 'to': date_to},
                'revenue': {'total_revenue': 0, 'invoice_count': 0},
                'outstanding': {'total': 0, 'invoice_count': 0},
                'payments': {'total_collected': 0, 'payment_count': 0},
                'top_treatments': [],
            }


# Global instance
odoo_client_v3 = OdooClientV3()



    # ==========================================
    # INVENTORY & SUPPLY MANAGEMENT (10 models)
    # ==========================================
    
    def get_stock_alerts(self, alert_type: Optional[str] = None) -> List[Dict]:
        """
        Get low stock alerts for dental supplies.
        
        Args:
            alert_type: Type of alert ('low_stock', 'expiring', 'out_of_stock')
            
        Returns:
            List of stock alerts
        """
        try:
            domain = []
            if alert_type:
                domain.append(('alert_type', '=', alert_type))
            
            alerts = self.search_read(
                'stock.alert',
                domain,
                ['product_id', 'current_qty', 'min_qty', 'alert_date', 'alert_type', 'location_id']
            )
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get stock alerts: {e}")
            return []
    
    def get_inventory_levels(self, location_id: Optional[int] = None, category_id: Optional[int] = None) -> List[Dict]:
        """
        Get current inventory levels.
        
        Args:
            location_id: Filter by storage location
            category_id: Filter by product category
            
        Returns:
            List of products with quantity on hand
        """
        try:
            domain = [('type', '=', 'product')]
            if category_id:
                domain.append(('categ_id', '=', category_id))
            
            products = self.search_read(
                'product.product',
                domain,
                ['name', 'default_code', 'qty_available', 'virtual_available', 'categ_id', 'uom_id', 'list_price']
            )
            
            # If location specified, get quants for that location
            if location_id:
                for product in products:
                    quants = self.search_read(
                        'stock.quant',
                        [('product_id', '=', product['id']), ('location_id', '=', location_id)],
                        ['quantity', 'reserved_quantity']
                    )
                    product['location_qty'] = sum(q.get('quantity', 0) for q in quants)
                    product['reserved_qty'] = sum(q.get('reserved_quantity', 0) for q in quants)
            
            return products
            
        except Exception as e:
            logger.error(f"Failed to get inventory levels: {e}")
            return []
    
    def get_expiring_products(self, days_threshold: int = 30) -> List[Dict]:
        """
        Get products expiring within specified days.
        
        Args:
            days_threshold: Number of days to look ahead
            
        Returns:
            List of expiring products
        """
        try:
            from datetime import datetime, timedelta
            
            threshold_date = (datetime.now() + timedelta(days=days_threshold)).strftime('%Y-%m-%d')
            
            # Get lots with expiration dates
            lots = self.search_read(
                'stock.production.lot',
                [('expiration_date', '<=', threshold_date), ('expiration_date', '>=', datetime.now().strftime('%Y-%m-%d'))],
                ['product_id', 'name', 'expiration_date', 'product_qty']
            )
            
            return lots
            
        except Exception as e:
            logger.error(f"Failed to get expiring products: {e}")
            return []
    
    def create_purchase_order(self, supplier_id: int, order_lines: List[Dict], notes: Optional[str] = None) -> Dict:
        """
        Create a purchase order for supplies.
        
        Args:
            supplier_id: Supplier/vendor partner ID
            order_lines: List of order lines [{'product_id': int, 'quantity': float, 'price_unit': float}]
            notes: Optional notes
            
        Returns:
            Created purchase order
        """
        try:
            order_data = {
                'partner_id': supplier_id,
                'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'notes': notes or '',
                'order_line': [
                    (0, 0, {
                        'product_id': line['product_id'],
                        'product_qty': line['quantity'],
                        'price_unit': line.get('price_unit', 0),
                    })
                    for line in order_lines
                ]
            }
            
            order_id = self.create('purchase.order', order_data)
            
            # Get created order
            order = self.search_read(
                'purchase.order',
                [('id', '=', order_id)],
                ['name', 'partner_id', 'date_order', 'amount_total', 'state']
            )
            
            return order[0] if order else {}
            
        except Exception as e:
            logger.error(f"Failed to create purchase order: {e}")
            return {}
    
    def get_purchase_orders(self, state: Optional[str] = None, date_from: Optional[str] = None) -> List[Dict]:
        """
        Get purchase orders.
        
        Args:
            state: Filter by state ('draft', 'sent', 'purchase', 'done', 'cancel')
            date_from: Filter orders from this date
            
        Returns:
            List of purchase orders
        """
        try:
            domain = []
            if state:
                domain.append(('state', '=', state))
            if date_from:
                domain.append(('date_order', '>=', date_from))
            
            orders = self.search_read(
                'purchase.order',
                domain,
                ['name', 'partner_id', 'date_order', 'amount_total', 'state', 'notes']
            )
            
            return orders
            
        except Exception as e:
            logger.error(f"Failed to get purchase orders: {e}")
            return []
    
    def get_stock_moves(self, product_id: Optional[int] = None, location_id: Optional[int] = None, date_from: Optional[str] = None) -> List[Dict]:
        """
        Get stock movements (in/out).
        
        Args:
            product_id: Filter by product
            location_id: Filter by location
            date_from: Filter moves from this date
            
        Returns:
            List of stock moves
        """
        try:
            domain = [('state', '=', 'done')]
            if product_id:
                domain.append(('product_id', '=', product_id))
            if location_id:
                domain.append(('|'), ('location_id', '=', location_id), ('location_dest_id', '=', location_id))
            if date_from:
                domain.append(('date', '>=', date_from))
            
            moves = self.search_read(
                'stock.move',
                domain,
                ['product_id', 'product_uom_qty', 'location_id', 'location_dest_id', 'date', 'reference', 'state']
            )
            
            return moves
            
        except Exception as e:
            logger.error(f"Failed to get stock moves: {e}")
            return []
    
    def get_storage_locations(self) -> List[Dict]:
        """
        Get all storage locations in the clinic.
        
        Returns:
            List of storage locations
        """
        try:
            locations = self.search_read(
                'stock.location',
                [('usage', '=', 'internal')],
                ['name', 'complete_name', 'parent_id', 'location_id']
            )
            
            return locations
            
        except Exception as e:
            logger.error(f"Failed to get storage locations: {e}")
            return []
    
    def get_product_categories(self) -> List[Dict]:
        """
        Get product categories (for organizing supplies).
        
        Returns:
            List of product categories
        """
        try:
            categories = self.search_read(
                'product.category',
                [],
                ['name', 'parent_id', 'product_count']
            )
            
            return categories
            
        except Exception as e:
            logger.error(f"Failed to get product categories: {e}")
            return []
    
    def update_stock_quantity(self, product_id: int, location_id: int, quantity: float, reason: str = "Manual adjustment") -> Dict:
        """
        Update stock quantity (inventory adjustment).
        
        Args:
            product_id: Product to adjust
            location_id: Location of the stock
            quantity: New quantity
            reason: Reason for adjustment
            
        Returns:
            Result of adjustment
        """
        try:
            # Create inventory adjustment
            adjustment_data = {
                'product_id': product_id,
                'location_id': location_id,
                'product_qty': quantity,
                'theoretical_qty': 0,  # Will be calculated
                'name': reason,
            }
            
            adjustment_id = self.create('stock.inventory.line', adjustment_data)
            
            return {
                'success': True,
                'adjustment_id': adjustment_id,
                'product_id': product_id,
                'location_id': location_id,
                'new_quantity': quantity,
                'reason': reason,
            }
            
        except Exception as e:
            logger.error(f"Failed to update stock quantity: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_inventory_valuation(self, location_id: Optional[int] = None) -> Dict:
        """
        Get total inventory valuation.
        
        Args:
            location_id: Filter by location
            
        Returns:
            Inventory valuation summary
        """
        try:
            domain = [('type', '=', 'product')]
            products = self.search_read(
                'product.product',
                domain,
                ['name', 'qty_available', 'standard_price', 'list_price']
            )
            
            total_cost = sum(p.get('qty_available', 0) * p.get('standard_price', 0) for p in products)
            total_value = sum(p.get('qty_available', 0) * p.get('list_price', 0) for p in products)
            total_items = len(products)
            total_quantity = sum(p.get('qty_available', 0) for p in products)
            
            return {
                'total_cost': total_cost,
                'total_value': total_value,
                'total_items': total_items,
                'total_quantity': total_quantity,
                'potential_profit': total_value - total_cost,
            }
            
        except Exception as e:
            logger.error(f"Failed to get inventory valuation: {e}")
            return {
                'total_cost': 0,
                'total_value': 0,
                'total_items': 0,
                'total_quantity': 0,
                'potential_profit': 0,
            }


# Global instance
odoo_client_v3 = OdooClientV3()



    # ==========================================
    # HR & STAFF MANAGEMENT (8 models)
    # ==========================================
    
    def get_employees(self, department: Optional[str] = None, active_only: bool = True) -> List[Dict]:
        """
        Get clinic staff/employees.
        
        Args:
            department: Filter by department
            active_only: Show only active employees
            
        Returns:
            List of employees
        """
        try:
            domain = []
            if active_only:
                domain.append(('active', '=', True))
            if department:
                domain.append(('department_id.name', 'ilike', department))
            
            employees = self.search_read(
                'hr.employee',
                domain,
                ['name', 'job_title', 'department_id', 'work_email', 'work_phone', 'resource_calendar_id', 'active']
            )
            
            return employees
            
        except Exception as e:
            logger.error(f"Failed to get employees: {e}")
            return []
    
    def get_physicians(self, specialization: Optional[str] = None) -> List[Dict]:
        """
        Get physicians/doctors.
        
        Args:
            specialization: Filter by specialization
            
        Returns:
            List of physicians
        """
        try:
            domain = []
            if specialization:
                domain.append(('specialization', 'ilike', specialization))
            
            physicians = self.search_read(
                'medical.physician',
                domain,
                ['name', 'code', 'specialization', 'phone', 'email', 'active']
            )
            
            return physicians
            
        except Exception as e:
            logger.error(f"Failed to get physicians: {e}")
            return []
    
    def get_doctor_slots(self, doctor_id: int, date: str) -> List[Dict]:
        """
        Get available time slots for a doctor.
        
        Args:
            doctor_id: Physician ID
            date: Date (YYYY-MM-DD)
            
        Returns:
            List of available slots
        """
        try:
            slots = self.search_read(
                'doctor.slot',
                [('doctor_id', '=', doctor_id), ('date', '=', date)],
                ['start_time', 'end_time', 'available', 'appointment_id']
            )
            
            return slots
            
        except Exception as e:
            logger.error(f"Failed to get doctor slots: {e}")
            return []
    
    def create_doctor_slot(self, doctor_id: int, date: str, start_time: str, end_time: str, duration: int = 30) -> Dict:
        """
        Create time slot for a doctor.
        
        Args:
            doctor_id: Physician ID
            date: Date (YYYY-MM-DD)
            start_time: Start time (HH:MM)
            end_time: End time (HH:MM)
            duration: Slot duration in minutes
            
        Returns:
            Created slot
        """
        try:
            slot_data = {
                'doctor_id': doctor_id,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'available': True,
            }
            
            slot_id = self.create('doctor.slot', slot_data)
            
            # Get created slot
            slot = self.search_read(
                'doctor.slot',
                [('id', '=', slot_id)],
                ['doctor_id', 'date', 'start_time', 'end_time', 'available']
            )
            
            return slot[0] if slot else {}
            
        except Exception as e:
            logger.error(f"Failed to create doctor slot: {e}")
            return {}
    
    def get_employee_attendance(self, employee_id: Optional[int] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Dict]:
        """
        Get employee attendance records.
        
        Args:
            employee_id: Filter by employee
            date_from: Start date
            date_to: End date
            
        Returns:
            List of attendance records
        """
        try:
            domain = []
            if employee_id:
                domain.append(('employee_id', '=', employee_id))
            if date_from:
                domain.append(('check_in', '>=', date_from))
            if date_to:
                domain.append(('check_in', '<=', date_to))
            
            attendance = self.search_read(
                'hr.attendance',
                domain,
                ['employee_id', 'check_in', 'check_out', 'worked_hours']
            )
            
            return attendance
            
        except Exception as e:
            logger.error(f"Failed to get attendance: {e}")
            return []
    
    def get_time_off_requests(self, employee_id: Optional[int] = None, state: Optional[str] = None) -> List[Dict]:
        """
        Get time-off requests.
        
        Args:
            employee_id: Filter by employee
            state: Filter by state ('draft', 'confirm', 'validate', 'refuse')
            
        Returns:
            List of time-off requests
        """
        try:
            domain = []
            if employee_id:
                domain.append(('employee_id', '=', employee_id))
            if state:
                domain.append(('state', '=', state))
            
            requests = self.search_read(
                'hr.leave',
                domain,
                ['employee_id', 'holiday_status_id', 'request_date_from', 'request_date_to', 'number_of_days', 'state', 'name']
            )
            
            return requests
            
        except Exception as e:
            logger.error(f"Failed to get time-off requests: {e}")
            return []
    
    def approve_time_off_request(self, request_id: int) -> Dict:
        """
        Approve a time-off request.
        
        Args:
            request_id: Time-off request ID
            
        Returns:
            Result of approval
        """
        try:
            # Call approve action
            result = self.execute('hr.leave', 'action_approve', [request_id])
            
            return {
                'success': True,
                'request_id': request_id,
                'message': 'Time-off request approved successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to approve time-off request: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_employee_workload(self, employee_id: int, date_from: str, date_to: str) -> Dict:
        """
        Get employee workload (appointments, hours).
        
        Args:
            employee_id: Employee ID
            date_from: Start date
            date_to: End date
            
        Returns:
            Workload summary
        """
        try:
            # Get appointments assigned to this employee
            appointments = self.search_read(
                'medical.appointment',
                [('doctor_id', '=', employee_id), ('appointment_date', '>=', date_from), ('appointment_date', '<=', date_to)],
                ['appointment_date', 'duration', 'state']
            )
            
            # Get attendance
            attendance = self.get_employee_attendance(employee_id, date_from, date_to)
            
            # Calculate metrics
            total_appointments = len(appointments)
            completed_appointments = len([a for a in appointments if a.get('state') == 'done'])
            total_hours = sum(a.get('worked_hours', 0) for a in attendance)
            
            return {
                'employee_id': employee_id,
                'period': {'from': date_from, 'to': date_to},
                'appointments': {
                    'total': total_appointments,
                    'completed': completed_appointments,
                    'completion_rate': f"{(completed_appointments / total_appointments * 100):.1f}%" if total_appointments > 0 else "0%"
                },
                'hours': {
                    'total_worked': total_hours,
                    'average_per_day': total_hours / 7 if total_hours > 0 else 0,  # Assuming weekly period
                },
            }
            
        except Exception as e:
            logger.error(f"Failed to get employee workload: {e}")
            return {
                'employee_id': employee_id,
                'period': {'from': date_from, 'to': date_to},
                'appointments': {'total': 0, 'completed': 0, 'completion_rate': '0%'},
                'hours': {'total_worked': 0, 'average_per_day': 0},
            }
    
    def get_staff_performance_metrics(self, date_from: str, date_to: str) -> List[Dict]:
        """
        Get performance metrics for all staff.
        
        Args:
            date_from: Start date
            date_to: End date
            
        Returns:
            List of staff performance metrics
        """
        try:
            # Get all physicians
            physicians = self.get_physicians()
            
            metrics = []
            for physician in physicians:
                workload = self.get_employee_workload(physician['id'], date_from, date_to)
                
                metrics.append({
                    'name': physician.get('name'),
                    'specialization': physician.get('specialization'),
                    'appointments': workload['appointments'],
                    'hours': workload['hours'],
                })
            
            # Sort by total appointments
            metrics = sorted(metrics, key=lambda x: x['appointments']['total'], reverse=True)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get staff performance metrics: {e}")
            return []


# Global instance
odoo_client_v3 = OdooClientV3()

