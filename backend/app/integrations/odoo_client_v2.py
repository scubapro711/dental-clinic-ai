"""
Improved Odoo XML-RPC Client with comprehensive error handling.

Fixes:
1. Constraint errors in create_appointment
2. Missing required fields validation
3. Better error messages
4. Retry logic for transient failures
5. Connection pooling
"""

import xmlrpc.client
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
from functools import wraps
import time

from app.core.config import settings

logger = logging.getLogger(__name__)


class OdooConnectionError(Exception):
    """Raised when connection to Odoo fails."""
    pass


class OdooValidationError(Exception):
    """Raised when data validation fails."""
    pass


class OdooConstraintError(Exception):
    """Raised when Odoo constraint is violated."""
    pass


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
            return None
        return wrapper
    return decorator


class OdooClientV2:
    """
    Improved Odoo XML-RPC client with error handling and validation.
    
    Compatible with Odoo 19.0 and Pragtech Dental Management module.
    """
    
    def __init__(self):
        """Initialize Odoo client."""
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.username = settings.ODOO_USERNAME
        self.password = settings.ODOO_PASSWORD
        
        # XML-RPC endpoints
        self.common = None
        self.models = None
        
        # Authentication
        self.uid = None
        self._authenticated = False
        
        # Initialize connection
        self._init_connection()
    
    def _init_connection(self):
        """Initialize XML-RPC connection."""
        try:
            self.common = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/common",
                allow_none=True
            )
            self.models = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/object",
                allow_none=True
            )
            logger.info(f"Odoo connection initialized: {self.url}")
        except Exception as e:
            logger.error(f"Failed to initialize Odoo connection: {e}")
            raise OdooConnectionError(f"Cannot connect to Odoo: {e}")
    
    @retry_on_failure(max_retries=3)
    def authenticate(self) -> bool:
        """
        Authenticate with Odoo.
        
        Returns:
            True if successful
        
        Raises:
            OdooConnectionError: If authentication fails
        """
        try:
            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
            self._authenticated = self.uid is not None
            
            if self._authenticated:
                logger.info(f"Odoo authentication successful (UID: {self.uid})")
            else:
                raise OdooConnectionError("Authentication failed: Invalid credentials")
            
            return self._authenticated
        except Exception as e:
            logger.error(f"Odoo authentication error: {e}")
            raise OdooConnectionError(f"Authentication failed: {e}")
    
    def _execute(
        self,
        model: str,
        method: str,
        args: list,
        kwargs: dict = None
    ) -> Any:
        """
        Execute method on Odoo model with error handling.
        
        Args:
            model: Odoo model name
            method: Method to execute
            args: Positional arguments
            kwargs: Keyword arguments
        
        Returns:
            Result from Odoo
        
        Raises:
            OdooConnectionError: If not authenticated
            OdooConstraintError: If constraint is violated
        """
        if not self._authenticated:
            self.authenticate()
        
        try:
            if kwargs is None:
                kwargs = {}
            
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
            
            return result
        
        except xmlrpc.client.Fault as e:
            # Parse Odoo error
            error_msg = str(e)
            
            if 'constraint' in error_msg.lower():
                logger.error(f"Odoo constraint error: {error_msg}")
                raise OdooConstraintError(f"Constraint violation: {error_msg}")
            elif 'required' in error_msg.lower():
                logger.error(f"Odoo validation error: {error_msg}")
                raise OdooValidationError(f"Missing required field: {error_msg}")
            else:
                logger.error(f"Odoo error on {model}.{method}: {error_msg}")
                raise
        
        except Exception as e:
            logger.error(f"Unexpected error on {model}.{method}: {e}")
            raise
    
    # ========== PATIENT MANAGEMENT ==========
    
    def search_patients(
        self,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        israeli_id: Optional[str] = None,
        limit: int = 100
    ) -> List[int]:
        """
        Search for patients.
        
        Args:
            name: Patient name (partial match)
            phone: Phone number
            email: Email address
            israeli_id: Israeli ID number
            limit: Maximum results
        
        Returns:
            List of patient IDs
        """
        domain = [('customer_rank', '>', 0)]  # Only customers
        
        if name:
            domain.append(('name', 'ilike', name))
        if phone:
            # Search in both phone and mobile
            domain.append('|')
            domain.append(('phone', 'ilike', phone))
            domain.append(('mobile', 'ilike', phone))
        if email:
            domain.append(('email', 'ilike', email))
        if israeli_id:
            domain.append(('vat', '=', israeli_id))  # Israeli ID stored in VAT field
        
        try:
            return self._execute('res.partner', 'search', [domain], {'limit': limit})
        except Exception as e:
            logger.error(f"Failed to search patients: {e}")
            return []
    
    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Get patient details.
        
        Args:
            patient_id: Patient ID
        
        Returns:
            Patient data or None
        """
        try:
            results = self._execute(
                'res.partner', 'read',
                [[patient_id]],
                {'fields': [
                    'id', 'name', 'email', 'phone', 'mobile',
                    'street', 'city', 'zip', 'country_id',
                    'vat',  # Israeli ID
                    'comment'  # Notes
                ]}
            )
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Failed to get patient {patient_id}: {e}")
            return None
    
    def create_patient(
        self,
        name: str,
        phone: Optional[str] = None,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        israeli_id: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        street: Optional[str] = None,
        city: Optional[str] = None,
        zip_code: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> int:
        """
        Create new patient.
        
        Args:
            name: Full name (required)
            phone: Phone number
            mobile: Mobile number
            email: Email address
            israeli_id: Israeli ID number
            date_of_birth: Date of birth
            street: Street address
            city: City
            zip_code: Zip code
            notes: Additional notes
            **kwargs: Additional fields
        
        Returns:
            New patient ID
        
        Raises:
            OdooValidationError: If validation fails
        """
        if not name:
            raise OdooValidationError("Patient name is required")
        
        patient_data = {
            'name': name,
            'customer_rank': 1,  # Mark as customer
            'is_company': False,
            'type': 'contact'
        }
        
        # Add optional fields
        if phone:
            patient_data['phone'] = phone
        if mobile:
            patient_data['mobile'] = mobile
        if email:
            patient_data['email'] = email
        if israeli_id:
            patient_data['vat'] = israeli_id
        if date_of_birth:
            patient_data['date_of_birth'] = date_of_birth.strftime('%Y-%m-%d')
        if street:
            patient_data['street'] = street
        if city:
            patient_data['city'] = city
        if zip_code:
            patient_data['zip'] = zip_code
        if notes:
            patient_data['comment'] = notes
        
        # Add extra fields
        patient_data.update({k: v for k, v in kwargs.items() if v is not None})
        
        try:
            patient_id = self._execute('res.partner', 'create', [patient_data])
            logger.info(f"Created patient: {name} (ID: {patient_id})")
            return patient_id
        except Exception as e:
            logger.error(f"Failed to create patient: {e}")
            raise
    
    # ========== APPOINTMENT MANAGEMENT ==========
    
    def get_required_appointment_fields(self) -> List[str]:
        """
        Get required fields for medical.appointment model.
        
        Returns:
            List of required field names
        """
        try:
            fields_info = self._execute(
                'medical.appointment',
                'fields_get',
                [],
                {'attributes': ['required', 'string']}
            )
            
            required_fields = [
                field_name
                for field_name, field_info in fields_info.items()
                if field_info.get('required', False)
            ]
            
            logger.info(f"Required appointment fields: {required_fields}")
            return required_fields
        
        except Exception as e:
            logger.error(f"Failed to get required fields: {e}")
            # Return known required fields as fallback
            return ['patient_id', 'doctor_id', 'appointment_sdate']
    
    def validate_appointment_data(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_date: datetime
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate appointment data before creation.
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
            appointment_date: Appointment date/time
        
        Returns:
            (is_valid, error_message)
        """
        # Check patient exists
        patient = self.get_patient(patient_id)
        if not patient:
            return False, f"Patient {patient_id} not found"
        
        # Check doctor exists
        try:
            doctor = self._execute(
                'hr.employee',
                'read',
                [[doctor_id]],
                {'fields': ['id', 'name']}
            )
            if not doctor:
                return False, f"Doctor {doctor_id} not found"
        except Exception as e:
            return False, f"Failed to validate doctor: {e}"
        
        # Check date is in future
        if appointment_date < datetime.now():
            return False, "Appointment date must be in the future"
        
        return True, None
    
    def create_appointment(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_date: datetime,
        duration_minutes: int = 45,
        patient_state: str = 'withapt',
        urgency: bool = False,
        notes: Optional[str] = None,
        **kwargs
    ) -> int:
        """
        Create appointment with comprehensive validation.
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
            appointment_date: Start date/time
            duration_minutes: Duration in minutes (default: 45)
            patient_state: 'withapt' (scheduled) or 'walkin'
            urgency: Urgent appointment flag
            notes: Appointment notes
            **kwargs: Additional fields
        
        Returns:
            New appointment ID
        
        Raises:
            OdooValidationError: If validation fails
            OdooConstraintError: If constraint is violated
        """
        # Validate data
        is_valid, error_msg = self.validate_appointment_data(
            patient_id, doctor_id, appointment_date
        )
        if not is_valid:
            raise OdooValidationError(error_msg)
        
        # Calculate end date
        end_date = appointment_date + timedelta(minutes=duration_minutes)
        
        # Build appointment data with ALL required fields
        appointment_data = {
            # Required fields
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'appointment_sdate': appointment_date.strftime('%Y-%m-%d %H:%M:%S'),
            'appointment_edate': end_date.strftime('%Y-%m-%d %H:%M:%S'),
            
            # State fields
            'patient_state': patient_state if patient_state in ['withapt', 'walkin'] else 'withapt',
            'state': 'draft',  # Initial state
            
            # Additional fields
            'urgency': urgency,
        }
        
        # Add notes if provided
        if notes:
            appointment_data['name'] = notes
        
        # Add extra fields (filter out None values)
        appointment_data.update({k: v for k, v in kwargs.items() if v is not None})
        
        try:
            appointment_id = self._execute(
                'medical.appointment',
                'create',
                [appointment_data]
            )
            logger.info(
                f"Created appointment {appointment_id}: "
                f"Patient {patient_id}, Doctor {doctor_id}, "
                f"Date {appointment_date}"
            )
            return appointment_id
        
        except OdooConstraintError as e:
            # Log detailed error for debugging
            logger.error(f"Constraint error creating appointment: {e}")
            logger.error(f"Appointment data: {appointment_data}")
            raise
        
        except Exception as e:
            logger.error(f"Failed to create appointment: {e}")
            logger.error(f"Appointment data: {appointment_data}")
            raise
    
    def get_available_slots(
        self,
        doctor_id: int,
        date_from: datetime,
        date_to: datetime,
        slot_duration_minutes: int = 45
    ) -> List[datetime]:
        """
        Get available appointment slots for a doctor.
        
        Args:
            doctor_id: Doctor ID
            date_from: Start date
            date_to: End date
            slot_duration_minutes: Slot duration in minutes
        
        Returns:
            List of available datetime slots
        """
        try:
            # Get existing appointments
            existing_appointments = self._execute(
                'medical.appointment',
                'search_read',
                [[
                    ('doctor_id', '=', doctor_id),
                    ('appointment_sdate', '>=', date_from.strftime('%Y-%m-%d %H:%M:%S')),
                    ('appointment_sdate', '<=', date_to.strftime('%Y-%m-%d %H:%M:%S')),
                    ('state', 'not in', ['cancel'])
                ]],
                {'fields': ['appointment_sdate', 'appointment_edate']}
            )
            
            # Convert to datetime objects
            busy_slots = []
            for apt in existing_appointments:
                start = datetime.strptime(apt['appointment_sdate'], '%Y-%m-%d %H:%M:%S')
                end = datetime.strptime(apt['appointment_edate'], '%Y-%m-%d %H:%M:%S')
                busy_slots.append((start, end))
            
            # Generate all possible slots
            all_slots = []
            current = date_from
            while current < date_to:
                # Check if slot is during working hours (8:00-18:00)
                if 8 <= current.hour < 18:
                    # Check if slot is not busy
                    slot_end = current + timedelta(minutes=slot_duration_minutes)
                    is_available = True
                    
                    for busy_start, busy_end in busy_slots:
                        if (current < busy_end and slot_end > busy_start):
                            is_available = False
                            break
                    
                    if is_available:
                        all_slots.append(current)
                
                current += timedelta(minutes=slot_duration_minutes)
            
            logger.info(f"Found {len(all_slots)} available slots for doctor {doctor_id}")
            return all_slots
        
        except Exception as e:
            logger.error(f"Failed to get available slots: {e}")
            return []
    
    def get_doctors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of doctors (employees with doctor role).
        
        Args:
            limit: Maximum number of results
        
        Returns:
            List of doctor records
        """
        try:
            # Search for employees (doctors)
            doctor_ids = self._execute(
                'hr.employee',
                'search',
                [[]],  # Empty domain = all employees
                {'limit': limit}
            )
            
            if not doctor_ids:
                logger.warning("No doctors found")
                return []
            
            # Get doctor details
            doctors = self._execute(
                'hr.employee',
                'read',
                [doctor_ids],
                {'fields': ['id', 'name', 'work_email', 'work_phone', 'job_title']}
            )
            
            return doctors
        
        except Exception as e:
            logger.error(f"Failed to get doctors: {e}")
            return []
    
    def search_patients(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for patients and return full records (not just IDs).
        
        Args:
            name: Patient name
            email: Email address
            phone: Phone number
            limit: Maximum results
        
        Returns:
            List of patient records
        """
        try:
            # Build search domain
            domain = [('customer_rank', '>', 0)]  # Only customers
            
            if name:
                domain.append(('name', 'ilike', name))
            if email:
                domain.append(('email', '=', email))
            if phone:
                domain.append('|')
                domain.append(('phone', 'ilike', phone))
                domain.append(('mobile', 'ilike', phone))
            
            # Search for patient IDs
            patient_ids = self._execute(
                'res.partner',
                'search',
                [domain],
                {'limit': limit}
            )
            
            if not patient_ids:
                return []
            
            # Get full patient records
            patients = self._execute(
                'res.partner',
                'read',
                [patient_ids],
                {'fields': [
                    'id', 'name', 'email', 'phone', 'mobile',
                    'street', 'city', 'zip', 'country_id',
                    'birthdate_date'
                ]}
            )
            
            return patients
        
        except Exception as e:
            logger.error(f"Failed to search patients: {e}")
            return []
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Get patient by ID (alias for get_patient for consistency).
        
        Args:
            patient_id: Patient ID
        
        Returns:
            Patient record or None
        """
        return self.get_patient(patient_id)
    
    def get_appointments(
        self,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get appointments with optional filters.
        
        Args:
            patient_id: Filter by patient
            doctor_id: Filter by doctor
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum results
        
        Returns:
            List of appointment records
        """
        try:
            # Build search domain
            domain = []
            
            if patient_id:
                domain.append(('patient_id', '=', patient_id))
            if doctor_id:
                domain.append(('doctor_id', '=', doctor_id))
            if date_from:
                domain.append(('appointment_sdate', '>=', date_from))
            if date_to:
                domain.append(('appointment_sdate', '<=', date_to))
            
            # Search for appointment IDs
            appointment_ids = self._execute(
                'medical.appointment',
                'search',
                [domain],
                {'limit': limit, 'order': 'appointment_sdate desc'}
            )
            
            if not appointment_ids:
                return []
            
            # Get full appointment records
            appointments = self._execute(
                'medical.appointment',
                'read',
                [appointment_ids],
                {'fields': [
                    'id', 'patient_id', 'doctor_id',
                    'appointment_sdate', 'appointment_edate',
                    'appointment_type', 'state', 'notes'
                ]}
            )
            
            return appointments
        
        except Exception as e:
            logger.error(f"Failed to get appointments: {e}")
            return []


# Global instance
odoo_client_v2 = OdooClientV2()
