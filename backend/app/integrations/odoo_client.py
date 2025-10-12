"""
Odoo XML-RPC Client for dental clinic ERP integration.

This client provides methods to interact with Odoo Dental module (Pragtech Dental Management).
Compatible with Odoo 19.0 and the patient.appointment model.
"""

import xmlrpc.client
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class OdooClient:
    """Client for Odoo XML-RPC API with Pragtech Dental Management module."""
    
    def __init__(self):
        """Initialize Odoo client with connection details."""
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.username = settings.ODOO_USERNAME
        self.password = settings.ODOO_PASSWORD
        
        # XML-RPC endpoints
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        
        # Authenticate and get UID
        self.uid = None
        self._authenticated = False
    
    def authenticate(self) -> bool:
        """
        Authenticate with Odoo and get user ID.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
            self._authenticated = self.uid is not None
            if self._authenticated:
                logger.info(f"Odoo authentication successful (UID: {self.uid})")
            else:
                logger.error("Odoo authentication failed")
            return self._authenticated
        except Exception as e:
            logger.error(f"Odoo authentication error: {e}")
            return False
    
    def _execute(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """
        Execute a method on an Odoo model.
        
        Args:
            model: Odoo model name (e.g., 'res.partner', 'patient.appointment')
            method: Method to execute (e.g., 'search', 'read', 'create', 'write')
            args: List of positional arguments for the method
            kwargs: Dictionary of keyword arguments for the method
            
        Returns:
            Result from Odoo
        """
        if not self._authenticated:
            self.authenticate()
        
        try:
            if kwargs is None:
                kwargs = {}
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
        except Exception as e:
            logger.error(f"Odoo execute error on {model}.{method}: {e}")
            raise
    
    # ============================================================================
    # PATIENT MANAGEMENT (res.partner)
    # ============================================================================
    
    def search_patients(
        self, 
        name: Optional[str] = None, 
        phone: Optional[str] = None,
        email: Optional[str] = None,
        limit: int = 100
    ) -> List[int]:
        """
        Search for patients by name, phone, or email.
        
        Args:
            name: Patient name (partial match)
            phone: Patient phone number
            email: Patient email
            limit: Maximum number of results
            
        Returns:
            List of patient IDs
        """
        domain = [('customer_rank', '>', 0)]  # Only customers (patients)
        
        if name:
            domain.append(('name', 'ilike', name))
        if phone:
            domain.append(('phone', 'ilike', phone))
        if email:
            domain.append(('email', 'ilike', email))
        
        return self._execute('res.partner', 'search', [domain], {'limit': limit})
    
    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Get patient details by ID.
        
        Args:
            patient_id: Odoo patient ID
            
        Returns:
            Patient data dictionary or None
        """
        results = self._execute(
            'res.partner', 'read',
            [[patient_id]],
            {'fields': [
                'id', 'name', 'email', 'phone',
                'street', 'city', 'zip', 'country_id'
            ]}
        )
        return results[0] if results else None
    
    def create_patient(
        self, 
        name: str, 
        email: Optional[str] = None,
        phone: Optional[str] = None,
        mobile: Optional[str] = None,
        israeli_id: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        **kwargs
    ) -> int:
        """
        Create a new patient in Odoo.
        
        Args:
            name: Patient full name
            email: Patient email
            phone: Patient phone number
            mobile: Patient mobile number
            israeli_id: Israeli ID number (Teudat Zehut)
            date_of_birth: Date of birth
            **kwargs: Additional fields
            
        Returns:
            New patient ID
        """
        patient_data = {
            'name': name,
            'customer_rank': 1,  # Mark as customer
            'is_company': False,
        }
        
        # Only add fields if they have values (not None)
        if email:
            patient_data['email'] = email
        if phone:
            patient_data['phone'] = phone
        if date_of_birth:
            patient_data['date_of_birth'] = date_of_birth.strftime('%Y-%m-%d')
        
        # Add any additional fields from kwargs, but skip None values
        for key, value in kwargs.items():
            if value is not None:
                patient_data[key] = value
        
        patient_id = self._execute('res.partner', 'create', [patient_data])
        logger.info(f"Created patient {name} with ID {patient_id}")
        return patient_id
    
    def update_patient(self, patient_id: int, **kwargs) -> bool:
        """
        Update patient information.
        
        Args:
            patient_id: Patient ID
            **kwargs: Fields to update
            
        Returns:
            True if successful
        """
        result = self._execute('res.partner', 'write', [[patient_id], kwargs])
        if result:
            logger.info(f"Updated patient {patient_id}")
        return result
    
    # ============================================================================
    # APPOINTMENT MANAGEMENT (patient.appointment)
    # ============================================================================
    
    def search_appointments(
        self,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[int]:
        """
        Search for appointments.
        
        Args:
            patient_id: Filter by patient ID
            doctor_id: Filter by doctor ID
            date_from: Start date filter
            date_to: End date filter
            state: Appointment state (draft, confirm, done, cancel)
            limit: Maximum number of results
            
        Returns:
            List of appointment IDs
        """
        domain = []
        
        if patient_id:
            domain.append(('patient_id', '=', patient_id))
        if doctor_id:
            domain.append(('doctor_id', '=', doctor_id))
        if date_from:
            domain.append(('start', '>=', date_from.strftime('%Y-%m-%d %H:%M:%S')))
        if date_to:
            domain.append(('start', '<=', date_to.strftime('%Y-%m-%d %H:%M:%S')))
        if state:
            domain.append(('state', '=', state))
        
        return self._execute('patient.appointment', 'search', [domain], {'limit': limit})
    
    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get appointment details by ID.
        
        Args:
            appointment_id: Odoo appointment ID
            
        Returns:
            Appointment data dictionary or None
        """
        results = self._execute(
            'patient.appointment', 'read',
            [[appointment_id]],
            {'fields': [
                'id', 'name', 'patient_id', 'doctor_id', 
                'start', 'stop',
                'state', 'patient_state', 'urgency',
                'operations_ids', 'inv_id', 'invoice_done'
            ]}
        )
        return results[0] if results else None
    
    def create_appointment(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_date: datetime,
        duration: float = 1.0,
        patient_state: str = 'scheduled',
        urgency: bool = False,
        **kwargs
    ) -> int:
        """
        Create a new appointment in Odoo.
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
            appointment_date: Appointment start date and time
            duration: Duration in hours
            patient_state: Patient status (scheduled, waiting, in_treatment, done)
            urgency: Urgent appointment flag
            **kwargs: Additional fields
            
        Returns:
            New appointment ID
        """
        from datetime import timedelta
        
        # Calculate end date based on duration
        end_date = appointment_date + timedelta(hours=duration)
        
        # Map patient_state to valid values: 'walkin' or 'withapt'
        valid_patient_state = 'withapt' if patient_state in ['scheduled', 'withapt'] else 'walkin'
        
        appointment_data = {
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'start': appointment_date.strftime('%Y-%m-%d %H:%M:%S'),
            'stop': end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'patient_state': valid_patient_state,
            'urgency': urgency,
        }
        
        # Add any additional fields
        appointment_data.update(kwargs)
        
        appointment_id = self._execute('patient.appointment', 'create', [appointment_data])
        logger.info(f"Created appointment {appointment_id} for patient {patient_id}")
        return appointment_id
    
    def update_appointment(self, appointment_id: int, **kwargs) -> bool:
        """
        Update an existing appointment.
        
        Args:
            appointment_id: Appointment ID
            **kwargs: Fields to update
            
        Returns:
            True if successful
        """
        result = self._execute('patient.appointment', 'write', [[appointment_id], kwargs])
        if result:
            logger.info(f"Updated appointment {appointment_id}")
        return result
    
    def cancel_appointment(self, appointment_id: int, reason: Optional[str] = None) -> bool:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: Appointment ID
            reason: Cancellation reason
            
        Returns:
            True if successful
        """
        update_data = {'state': 'cancel'}
        if reason:
            update_data['cancellation_reason'] = reason
        
        result = self.update_appointment(appointment_id, **update_data)
        if result:
            logger.info(f"Cancelled appointment {appointment_id}")
        return result
    
    def confirm_appointment(self, appointment_id: int) -> bool:
        """
        Confirm an appointment.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            True if successful
        """
        return self.update_appointment(appointment_id, state='confirm')
    
    # ============================================================================
    # DOCTOR MANAGEMENT
    # ============================================================================
    
    def get_doctors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of doctors/dentists.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of doctor records
        """
        # Doctors are hr.employee records with specific category
        doctor_ids = self._execute(
            'hr.employee', 'search',
            [[]], {'limit': limit}
        )
        
        if doctor_ids:
            return self._execute(
                'hr.employee', 'read',
                [doctor_ids],
                {'fields': ['id', 'name', 'work_email', 'work_phone', 'job_title']}
            )
        return []
    
    # ============================================================================
    # AVAILABLE TIME SLOTS
    # ============================================================================
    
    def get_available_slots(
        self,
        doctor_id: int,
        date_from: datetime,
        date_to: datetime,
        duration: float = 1.0,
    ) -> List[datetime]:
        """
        Get available appointment slots for a doctor.
        
        This is a simplified implementation. In production, this would check:
        - Doctor's working hours
        - Existing appointments
        - Breaks and holidays
        
        Args:
            doctor_id: Doctor ID
            date_from: Start date
            date_to: End date
            duration: Required duration in hours
            
        Returns:
            List of available datetime slots
        """
        # Get existing appointments for this doctor
        existing = self.search_appointments(
            doctor_id=doctor_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Get appointment times
        booked_times = []
        if existing:
            appointments = self._execute(
                'patient.appointment', 'read',
                [existing],
                {'fields': ['start', 'stop']}
            )
            for apt in appointments:
                if apt.get('start'):
                    booked_times.append(datetime.strptime(apt['start'], '%Y-%m-%d %H:%M:%S'))
        
        # Generate available slots (9 AM to 5 PM, excluding booked times)
        from datetime import timedelta
        
        slots = []
        current = date_from.replace(hour=9, minute=0, second=0, microsecond=0)
        end = date_to.replace(hour=17, minute=0, second=0, microsecond=0)
        
        while current < end:
            # Check if slot is during working hours
            if 9 <= current.hour < 17:
                # Check if slot is not booked
                is_available = True
                for booked in booked_times:
                    # Simple overlap check
                    if abs((current - booked).total_seconds()) < duration * 3600:
                        is_available = False
                        break
                
                if is_available:
                    slots.append(current)
            
            current += timedelta(hours=duration)
        
        return slots[:20]  # Return first 20 available slots


# Global Odoo client instance
odoo_client = OdooClient()
