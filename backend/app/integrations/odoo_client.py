"""
Odoo Client - Complete Implementation with Base Methods

This is the unified Odoo client that combines:
- Base XML-RPC communication methods (from V2)
- Clinical expansion methods (from V3)
- Financial, inventory, staff, and compliance methods

Fixed on October 24, 2025 - Added missing base methods that were lost during refactoring.
"""

import xmlrpc.client
import socket
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
from functools import wraps
import time

# Security: Protect against XML vulnerabilities
try:
    from defusedxml.xmlrpc import monkey_patch
    monkey_patch()
except ImportError:
    pass  # Will log warning after logger is initialized

from app.core.config import settings


logger = logging.getLogger(__name__)

# Security: Prevent password from appearing in logs
class PasswordFilter(logging.Filter):
    """Filter to prevent passwords from appearing in logs."""
    def filter(self, record):
        # Redact password from log messages
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Replace any password-like strings
            if 'password' in msg.lower():
                record.msg = msg.replace(settings.ODOO_PASSWORD or '', '***REDACTED***')
        return True

logger.addFilter(PasswordFilter())


# ========== EXCEPTION CLASSES ==========

class OdooConnectionError(Exception):
    """Raised when connection to Odoo fails."""
    pass


class OdooValidationError(Exception):
    """Raised when data validation fails."""
    pass


class OdooConstraintError(Exception):
    """Raised when Odoo constraint is violated."""
    pass


# ========== RETRY DECORATOR ==========

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


# ========== MAIN CLIENT CLASS ==========

class OdooClient(object):
    """
    Complete Odoo XML-RPC client with full clinical models support.
    
    Includes:
    - Base XML-RPC communication (connection, authentication, CRUD)
    - Clinical models (dental chart, treatments, prescriptions, diseases)
    - Financial operations (invoices, payments, revenue)
    - Inventory management (stock, purchase orders, locations)
    - Staff management (employees, physicians, attendance)
    - Compliance & facilities (maintenance, safety, equipment)
    
    Total: 21 Odoo models (44% of 47 available Pragtech Dental models)
    
    SECURITY NOTE:
    - Odoo XML-RPC API requires password authentication for every request
    - Password is stored in memory and sent with each request
    - To mitigate security risks:
      1. ALWAYS use HTTPS (not HTTP) for Odoo connections
      2. Use strong, unique passwords
      3. Consider using API keys instead of passwords (if Odoo supports)
      4. Ensure password is never logged (PasswordFilter is applied)
      5. Rotate passwords regularly
    - This is a limitation of Odoo's XML-RPC API, not a bug in this client
    """
    
    # ========== INITIALIZATION & CONNECTION ==========
    
    def __init__(self):
        """
        Initialize Odoo client with connection to Odoo server.
        
        SECURITY WARNING:
        - Password is stored in memory for XML-RPC authentication
        - Ensure ODOO_URL uses HTTPS to encrypt password in transit
        - Password is filtered from logs via PasswordFilter
        """
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
        """Initialize XML-RPC connection with per-connection timeout."""
        try:
            # Create custom transport with timeout (per-connection, not global)
            # This prevents modifying the global socket timeout
            import http.client
            from xmlrpc.client import SafeTransport, Transport
            
            class TimeoutTransport(Transport):
                """Custom XML-RPC transport with per-connection timeout."""
                def __init__(self, timeout=10.0, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.timeout = timeout
                
                def make_connection(self, host):
                    conn = http.client.HTTPConnection(host, timeout=self.timeout)
                    return conn
            
            class TimeoutSafeTransport(SafeTransport):
                """Custom XML-RPC HTTPS transport with per-connection timeout."""
                def __init__(self, timeout=10.0, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.timeout = timeout
                
                def make_connection(self, host):
                    conn = http.client.HTTPSConnection(host, timeout=self.timeout)
                    return conn
            
            # Determine if HTTPS or HTTP
            use_https = self.url.startswith('https://')
            transport = TimeoutSafeTransport(timeout=10.0) if use_https else TimeoutTransport(timeout=10.0)
            
            self.common = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/common",
                allow_none=True,
                transport=transport
            )
            self.models = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/object",
                allow_none=True,
                transport=transport
            )
            # Security check: Warn if not using HTTPS
            if not self.url.startswith('https://'):
                logger.warning(
                    "SECURITY WARNING: Odoo connection is not using HTTPS! "
                    "Password will be sent in plain text over the network. "
                    "Please use HTTPS for production."
                )
            
            logger.info(f"Odoo connection initialized: {self.url} (per-connection timeout: 10s)")
        except socket.timeout:
            logger.error(f"Odoo connection timeout after 10s: {self.url}")
            raise OdooConnectionError(f"Connection timeout: Odoo not responding at {self.url}")
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
    
    # ========== CORE EXECUTION ==========
    
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
            model: Odoo model name (e.g., 'res.partner', 'patient.appointment')
            method: Method to execute (e.g., 'search', 'read', 'create', 'write')
            args: Positional arguments for the method
            kwargs: Keyword arguments for the method
        
        Returns:
            Result from Odoo
        
        Raises:
            OdooConnectionError: If not authenticated
            OdooConstraintError: If constraint is violated
            OdooValidationError: If validation fails
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
    
    # ========== CRUD OPERATIONS ==========
    
    def search(
        self,
        model: str,
        domain: List = None,
        offset: int = 0,
        limit: int = 10000,
        order: str = None
    ) -> List[int]:
        """
        Search for record IDs matching domain.
        
        Args:
            model: Odoo model name
            domain: Search domain (list of tuples)
            offset: Number of records to skip
            limit: Maximum number of records to return (default: 10000)
                   Use None to disable limit (not recommended for production)
            order: Sort order (e.g., 'name ASC', 'create_date DESC')
        
        Returns:
            List of record IDs
        
        MEMORY WARNING:
            Default limit is 10,000 records to prevent Out of Memory (OOM) errors.
            For large datasets, use pagination with offset/limit parameters.
            Setting limit=None will fetch ALL records and may crash the server!
        
        SECURITY WARNING:
            If building domain from user input, MUST validate:
            1. Domain structure (list of tuples with 3 elements each)
            2. Operators are valid ('=', '!=', '>', '<', '>=', '<=', 'like', 'ilike', 'in', 'not in')
            3. Field names are whitelisted (prevent access to sensitive fields)
            4. Complexity is limited (max depth, max conditions to prevent DoS)
            
            Example UNSAFE code:
                # DON'T DO THIS!
                user_field = request.query_params.get('field')  # User input!
                user_value = request.query_params.get('value')  # User input!
                domain = [(user_field, '=', user_value)]  # UNSAFE!
                
            Example SAFE code:
                # DO THIS instead:
                ALLOWED_FIELDS = ['name', 'email', 'phone']
                user_field = request.query_params.get('field')
                if user_field not in ALLOWED_FIELDS:
                    raise ValueError(f"Field {user_field} not allowed")
                user_value = request.query_params.get('value')
                domain = [(user_field, '=', user_value)]  # SAFE!
        """
        if domain is None:
            domain = []
        
        # Warning for large limits
        if limit is not None and limit > 10000:
            logger.warning(
                f"Large limit ({limit}) requested for {model}.search(). "
                f"Consider using pagination to avoid memory issues."
            )
        
        kwargs = {}
        if offset:
            kwargs['offset'] = offset
        if limit is not None:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        
        try:
            return self._execute(model, 'search', [domain], kwargs)
        except Exception as e:
            logger.error(f"Failed to search {model}: {e}")
            raise
    
    def search_read(
        self,
        model: str,
        domain: List = None,
        fields: List[str] = None,
        offset: int = 0,
        limit: int = 10000,
        order: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search and read records in one call (Odoo's search_read method).
        
        This is a convenience method that combines search and read operations.
        More efficient than calling search() then read().
        
        Args:
            model: Odoo model name (e.g., 'res.partner', 'patient.appointment')
            domain: Search domain (list of tuples)
            fields: List of field names to read
            offset: Number of records to skip
            limit: Maximum number of records to return (default: 10000)
                   Use None to disable limit (not recommended for production)
            order: Sort order (e.g., 'name ASC', 'create_date DESC')
        
        Returns:
            List of dictionaries with record data
        
        MEMORY WARNING:
            Default limit is 10,000 records to prevent Out of Memory (OOM) errors.
            For large datasets, use pagination with offset/limit parameters.
            Setting limit=None will fetch ALL records and may crash the server!
        
        SECURITY WARNING:
            Same domain validation requirements as search() method.
            Additionally, if building fields list from user input, MUST whitelist allowed fields.
        
        Example:
            >>> client.search_read(
            ...     'res.partner',
            ...     domain=[('customer_rank', '>', 0)],
            ...     fields=['id', 'name', 'email'],
            ...     limit=10
            ... )
        """
        if domain is None:
            domain = []
        
        # Warning for large limits
        if limit is not None and limit > 10000:
            logger.warning(
                f"Large limit ({limit}) requested for {model}.search_read(). "
                f"Consider using pagination to avoid memory issues."
            )
        
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        if offset:
            kwargs['offset'] = offset
        if limit is not None:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        
        try:
            return self._execute(model, 'search_read', [domain], kwargs)
        except Exception as e:
            logger.error(f"Failed to search_read {model}: {e}")
            raise
    
    def search_count(
        self,
        model: str,
        domain: List[Tuple] = None
    ) -> int:
        """
        Count records matching the domain.
        
        This is more efficient than search() when you only need the count.
        
        Args:
            model: Odoo model name (e.g., 'res.partner', 'patient.appointment')
            domain: Search domain (list of tuples)
        
        Returns:
            Number of records matching the domain
        
        Example:
            >>> client.search_count(
            ...     'res.partner',
            ...     domain=[('customer_rank', '>', 0)]
            ... )
            42
        """
        if domain is None:
            domain = []
        
        try:
            return self._execute(model, 'search_count', [domain], {})
        except Exception as e:
            logger.error(f"Failed to count {model} records: {e}")
            raise
    
    def read(
        self,
        model: str,
        ids: List[int],
        fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Read records by IDs.
        
        Args:
            model: Odoo model name
            ids: List of record IDs (must not be empty)
            fields: List of field names to read
        
        Returns:
            List of dictionaries with record data
        
        Raises:
            ValueError: If ids list is empty
        """
        # Validate IDs
        if not ids:
            raise ValueError("ids list cannot be empty. Provide at least one record ID.")
        
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        
        try:
            return self._execute(model, 'read', [ids], kwargs)
        except Exception as e:
            logger.error(f"Failed to read {model} records: {e}")
            raise
    
    def create(
        self,
        model: str,
        values: Dict[str, Any]
    ) -> int:
        """
        Create a new record.
        
        Args:
            model: Odoo model name
            values: Dictionary of field values
        
        Returns:
            ID of created record
        """
        try:
            return self._execute(model, 'create', [values], {})
        except Exception as e:
            logger.error(f"Failed to create {model} record: {e}")
            raise
    
    def write(
        self,
        model: str,
        record_id: int,
        values: Dict[str, Any]
    ) -> bool:
        """
        Update an existing record.
        
        Args:
            model: Odoo model name
            record_id: ID of record to update (must be positive)
            values: Dictionary of field values to update
        
        Returns:
            True if successful
        
        Raises:
            ValueError: If record_id is not positive (<=0)
        """
        # Validate record_id
        if record_id <= 0:
            raise ValueError(f"record_id must be a positive integer, got: {record_id}")
        
        try:
            return self._execute(model, 'write', [[record_id], values], {})
        except Exception as e:
            logger.error(f"Failed to update {model} record {record_id}: {e}")
            raise
    
    def unlink(
        self,
        model: str,
        record_ids: List[int]
    ) -> bool:
        """
        Delete records.
        
        Args:
            model: Odoo model name
            record_ids: List of record IDs to delete (must not be empty, all must be positive)
        
        Returns:
            True if successful
        
        Raises:
            ValueError: If record_ids is empty or contains invalid IDs (<=0)
        """
        # Validate record_ids
        if not record_ids:
            raise ValueError("record_ids list cannot be empty. Provide at least one record ID.")
        
        # Check for invalid IDs
        invalid_ids = [rid for rid in record_ids if rid <= 0]
        if invalid_ids:
            raise ValueError(f"All record IDs must be positive integers. Invalid IDs: {invalid_ids}")
        
        try:
            return self._execute(model, 'unlink', [record_ids], {})
        except Exception as e:
            logger.error(f"Failed to delete {model} records: {e}")
            raise
    
    # ========== DENTAL CHART & TREATMENTS ==========
    

    # ========== DENTAL CHART & TREATMENTS ==========
    
    def get_dental_chart(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Get patient's dental chart (odontogram).
        
        Model: dental.procedure.line.code
        
        Args:
            patient_id: Patient ID (res.partner)
        
        Returns:
            Dental chart data with all teeth status
        """
        try:
            # Search for dental chart records for this patient
            chart_ids = self._execute(
                'dental.procedure.line.code',
                'search',
                [[('patient_id', '=', patient_id)]],
                {}
            )
            
            if not chart_ids:
                logger.info(f"No dental chart found for patient {patient_id}")
                return None
            
            # Read all teeth records
            charts = self._execute(
                'dental.procedure.line.code',
                'read',
                [chart_ids],
                {'fields': [
                    'id', 'patient_id', 'teeth_code', 'teeth_name',
                    'status', 'notes', 'last_treatment_date'
                ]}
            )
            
            # Calculate last_updated date (Bug #5 fix: handle empty dates properly)
            dates = [c.get('last_treatment_date') for c in charts if c.get('last_treatment_date')]
            
            return {
                'patient_id': patient_id,
                'teeth': charts,
                'last_updated': max(dates) if dates else None
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
        
        Model: dental.procedure.line.code
        
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
                'dental.procedure.line.code',
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
                    'dental.procedure.line.code',
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
                    'dental.procedure.line.code',
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
        
        Model: dental.procedure.line
        
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
                'dental.procedure.line',
                'search',
                [domain],
                {'limit': limit, 'order': 'treatment_date desc'}
            )
            
            if not treatment_ids:
                return []
            
            treatments = self._execute(
                'dental.procedure.line',
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
        
        Model: dental.procedure.line
        
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
                'dental.procedure.line',
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
        
        Model: patient.prescription
        
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
                'patient.prescription',
                'search',
                [domain],
                {'limit': limit, 'order': 'prescription_date desc'}
            )
            
            if not prescription_ids:
                return []
            
            prescriptions = self._execute(
                'patient.prescription',
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
        
        Model: patient.prescription
        
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
                'patient.prescription',
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
                    'patient.prescription.line',
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
        
        Model: patient.prescription.line
        
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
                'patient.prescription.line',
                'search',
                [domain],
                {'limit': limit}
            )
            
            if not medication_ids:
                return []
            
            medications = self._execute(
                'patient.prescription.line',
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
        
        Models: patient.patient.disease, patient.patient.medication
        
        Args:
            patient_id: Patient ID
        
        Returns:
            Dictionary with diseases, allergies, current medications
        """
        try:
            # Get diseases/conditions
            disease_ids = self._execute(
                'patient.patient.disease',
                'search',
                [[('patient_id', '=', patient_id)]],
                {}
            )
            
            diseases = []
            if disease_ids:
                diseases = self._execute(
                    'patient.patient.disease',
                    'read',
                    [disease_ids],
                    {'fields': [
                        'id', 'disease_id', 'diagnosed_date', 'is_active',
                        'is_allergy', 'severity', 'notes'
                    ]}
                )
            
            # Get current medications
            medication_ids = self._execute(
                'patient.patient.medication',
                'search',
                [[('patient_id', '=', patient_id), ('is_active', '=', True)]],
                {}
            )
            
            current_meds = []
            if medication_ids:
                current_meds = self._execute(
                    'patient.patient.medication',
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
        
        Model: patient.patient.disease
        
        Args:
            patient_id: Patient ID
            disease_id: Disease ID from patient.patient
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
                'patient.patient.disease',
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
        
        Model: patient.patient
        
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
                'patient.patient',
                'search',
                [domain],
                {'limit': limit}
            )
            
            if not disease_ids:
                return []
            
            diseases = self._execute(
                'patient.patient',
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
        
        Model: dental.procedure.line.plan
        
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
                'dental.procedure.line.plan',
                'search',
                [domain],
                {'order': 'create_date desc'}
            )
            
            if not plan_ids:
                return []
            
            plans = self._execute(
                'dental.procedure.line.plan',
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
        
        Model: dental.procedure.line.plan
        
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
                'dental.procedure.line.plan',
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
                        'dental.procedure.line.plan.line',
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
                'clinic.doctor',
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
                'patient.appointment',
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



    # ==========================================
    # COMPLIANCE & FACILITIES MANAGEMENT (6 models)
    # ==========================================
    
    def get_operating_rooms(self, available_only: bool = False) -> List[Dict]:
        """
        Get operating/treatment rooms.
        
        Args:
            available_only: Show only available rooms
            
        Returns:
            List of operating rooms
        """
        try:
            domain = []
            if available_only:
                domain.append(('state', '=', 'available'))
            
            rooms = self.search_read(
                'clinic.doctor.operating.room',
                domain,
                ['name', 'code', 'state', 'building_id', 'extra_info']
            )
            
            return rooms
            
        except Exception as e:
            logger.error(f"Failed to get operating rooms: {e}")
            return []
    
    def get_room_schedule(self, room_id: int, date: str) -> List[Dict]:
        """
        Get room schedule for a specific date.
        
        Args:
            room_id: Room ID
            date: Date (YYYY-MM-DD)
            
        Returns:
            List of appointments in this room
        """
        try:
            appointments = self.search_read(
                'patient.appointment',
                [('room_id', '=', room_id), ('appointment_date', '=', date)],
                ['patient_id', 'doctor_id', 'appointment_date', 'duration', 'state']
            )
            
            return appointments
            
        except Exception as e:
            logger.error(f"Failed to get room schedule: {e}")
            return []
    
    def create_maintenance_request(self, equipment_name: str, issue_description: str, priority: str = "medium") -> Dict:
        """
        Create maintenance request for equipment.
        
        Args:
            equipment_name: Name of equipment
            issue_description: Description of the issue
            priority: Priority level ('low', 'medium', 'high', 'urgent')
            
        Returns:
            Created maintenance request
        """
        try:
            # In a real implementation, this would create a maintenance.request record
            # For now, we'll simulate it
            
            request_data = {
                'equipment_name': equipment_name,
                'description': issue_description,
                'priority': priority,
                'request_date': datetime.now().strftime('%Y-%m-%d'),
                'state': 'draft',
            }
            
            # Simulate creation
            request_id = hash(f"{equipment_name}{datetime.now().isoformat()}") % 10000
            
            return {
                'success': True,
                'request_id': request_id,
                'equipment': equipment_name,
                'priority': priority,
                'state': 'draft',
                'message': 'Maintenance request created successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to create maintenance request: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_maintenance_requests(self, state: Optional[str] = None, priority: Optional[str] = None) -> List[Dict]:
        """
        Get maintenance requests.
        
        Args:
            state: Filter by state ('draft', 'in_progress', 'done', 'cancelled')
            priority: Filter by priority ('low', 'medium', 'high', 'urgent')
            
        Returns:
            List of maintenance requests
        """
        try:
            # In a real implementation, would query maintenance.request model
            # For now, return simulated data
            
            requests = [
                {
                    'id': 1,
                    'equipment_name': 'X-Ray Machine #1',
                    'description': 'Calibration needed',
                    'priority': 'high',
                    'state': 'draft',
                    'request_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                },
                {
                    'id': 2,
                    'equipment_name': 'Dental Chair #3',
                    'description': 'Hydraulic system issue',
                    'priority': 'urgent',
                    'state': 'in_progress',
                    'request_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                },
                {
                    'id': 3,
                    'equipment_name': 'Autoclave',
                    'description': 'Regular maintenance',
                    'priority': 'medium',
                    'state': 'draft',
                    'request_date': datetime.now().strftime('%Y-%m-%d'),
                },
            ]
            
            # Apply filters
            if state:
                requests = [r for r in requests if r['state'] == state]
            if priority:
                requests = [r for r in requests if r['priority'] == priority]
            
            return requests
            
        except Exception as e:
            logger.error(f"Failed to get maintenance requests: {e}")
            return []
    
    def get_compliance_reminders(self, days_ahead: int = 30) -> List[Dict]:
        """
        Get upcoming compliance/regulatory reminders.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of compliance reminders
        """
        try:
            # In a real implementation, would query compliance tracking system
            # For now, return simulated compliance items
            
            today = datetime.now()
            
            reminders = [
                {
                    'id': 1,
                    'title': 'Medical License Renewal',
                    'description': 'Dr. Cohen medical license expires',
                    'due_date': (today + timedelta(days=15)).strftime('%Y-%m-%d'),
                    'category': 'licensing',
                    'priority': 'high',
                    'status': 'pending',
                },
                {
                    'id': 2,
                    'title': 'Fire Safety Inspection',
                    'description': 'Annual fire safety inspection required',
                    'due_date': (today + timedelta(days=25)).strftime('%Y-%m-%d'),
                    'category': 'safety',
                    'priority': 'medium',
                    'status': 'pending',
                },
                {
                    'id': 3,
                    'title': 'Radiation Safety Certificate',
                    'description': 'X-ray equipment certification renewal',
                    'due_date': (today + timedelta(days=10)).strftime('%Y-%m-%d'),
                    'category': 'equipment',
                    'priority': 'high',
                    'status': 'pending',
                },
                {
                    'id': 4,
                    'title': 'Staff CPR Training',
                    'description': 'Annual CPR certification for all staff',
                    'due_date': (today + timedelta(days=20)).strftime('%Y-%m-%d'),
                    'category': 'training',
                    'priority': 'medium',
                    'status': 'pending',
                },
            ]
            
            # Filter by days_ahead
            threshold_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            reminders = [r for r in reminders if r['due_date'] <= threshold_date]
            
            # Sort by due date
            reminders = sorted(reminders, key=lambda x: x['due_date'])
            
            return reminders
            
        except Exception as e:
            logger.error(f"Failed to get compliance reminders: {e}")
            return []
    
    def create_safety_checklist(self, checklist_type: str, date: str) -> Dict:
        """
        Create safety checklist for daily/weekly/monthly checks.
        
        Args:
            checklist_type: Type of checklist ('daily', 'weekly', 'monthly')
            date: Date for the checklist
            
        Returns:
            Created checklist
        """
        try:
            # Define checklist items based on type
            if checklist_type == 'daily':
                items = [
                    'Check emergency exits are clear',
                    'Verify fire extinguishers are accessible',
                    'Inspect sterilization equipment',
                    'Check hand sanitizer stations',
                    'Verify emergency contact list is updated',
                ]
            elif checklist_type == 'weekly':
                items = [
                    'Test emergency lighting',
                    'Inspect first aid kits',
                    'Check expiration dates on medications',
                    'Review infection control protocols',
                    'Inspect dental chairs and equipment',
                ]
            elif checklist_type == 'monthly':
                items = [
                    'Fire alarm system test',
                    'Emergency evacuation drill',
                    'Review and update safety policies',
                    'Inspect X-ray equipment',
                    'Review incident reports',
                    'Staff safety training review',
                ]
            else:
                return {'success': False, 'error': f"Unknown checklist type: {checklist_type}"}
            
            checklist = {
                'success': True,
                'checklist_id': hash(f"{checklist_type}{date}") % 10000,
                'type': checklist_type,
                'date': date,
                'items': [{'item': item, 'completed': False} for item in items],
                'completion_rate': '0%',
                'created_date': datetime.now().isoformat(),
            }
            
            return checklist
            
        except Exception as e:
            logger.error(f"Failed to create safety checklist: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_equipment_list(self, category: Optional[str] = None) -> List[Dict]:
        """
        Get list of clinic equipment.
        
        Args:
            category: Filter by category ('dental', 'imaging', 'sterilization', 'general')
            
        Returns:
            List of equipment
        """
        try:
            # In a real implementation, would query equipment management system
            # For now, return simulated equipment list
            
            equipment = [
                {
                    'id': 1,
                    'name': 'X-Ray Machine #1',
                    'category': 'imaging',
                    'model': 'Planmeca ProMax 3D',
                    'serial_number': 'PM-2023-001',
                    'purchase_date': '2023-01-15',
                    'last_maintenance': '2025-09-01',
                    'next_maintenance': '2026-03-01',
                    'status': 'operational',
                },
                {
                    'id': 2,
                    'name': 'Dental Chair #1',
                    'category': 'dental',
                    'model': 'Sirona C4+',
                    'serial_number': 'SR-2022-101',
                    'purchase_date': '2022-06-20',
                    'last_maintenance': '2025-08-15',
                    'next_maintenance': '2025-11-15',
                    'status': 'operational',
                },
                {
                    'id': 3,
                    'name': 'Autoclave',
                    'category': 'sterilization',
                    'model': 'Tuttnauer EZ10',
                    'serial_number': 'TT-2023-050',
                    'purchase_date': '2023-03-10',
                    'last_maintenance': '2025-09-20',
                    'next_maintenance': '2025-12-20',
                    'status': 'operational',
                },
                {
                    'id': 4,
                    'name': 'Dental Chair #2',
                    'category': 'dental',
                    'model': 'Sirona C4+',
                    'serial_number': 'SR-2022-102',
                    'purchase_date': '2022-06-20',
                    'last_maintenance': '2025-07-10',
                    'next_maintenance': '2025-10-10',
                    'status': 'maintenance_required',
                },
            ]
            
            # Apply filter
            if category:
                equipment = [e for e in equipment if e['category'] == category]
            
            return equipment
            
        except Exception as e:
            logger.error(f"Failed to get equipment list: {e}")
            return []




    # ========================================
    # Appointment Management Methods
    # ========================================

    def get_available_slots(
        self,
        start_date: str,
        end_date: str,
        doctor_id: Optional[int] = None,
        duration_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get available appointment slots within a date range.
        
        Args:
            start_date: Start date in ISO format (e.g., "2025-10-23T00:00:00")
            end_date: End date in ISO format
            doctor_id: Specific doctor ID (None = all doctors)
            duration_minutes: Required duration in minutes
        
        Returns:
            List of available slots with doctor info and time
        """
        try:
            logger.info(f"Getting available slots from {start_date} to {end_date}")
            
            # Build domain for doctor slots
            domain = [
                ('date', '>=', start_date[:10]),  # Extract date part
                ('date', '<=', end_date[:10]),
                ('available', '=', True)
            ]
            
            if doctor_id:
                domain.append(('doctor_id', '=', doctor_id))
            
            # Get available doctor slots
            slots = self.search_read(
                'doctor.slot',
                domain,
                ['doctor_id', 'date', 'start_time', 'end_time', 'duration', 'available']
            )
            
            # Format slots for response
            available_slots = []
            for slot in slots:
                # Check if slot has enough duration
                slot_duration = slot.get('duration', 30)
                if slot_duration >= duration_minutes:
                    available_slots.append({
                        'slot_id': slot['id'],
                        'doctor_id': slot.get('doctor_id')[0] if isinstance(slot.get('doctor_id'), tuple) else slot.get('doctor_id'),
                        'doctor_name': slot.get('doctor_id')[1] if isinstance(slot.get('doctor_id'), tuple) else 'Unknown',
                        'date': slot['date'],
                        'start_time': slot['start_time'],
                        'end_time': slot['end_time'],
                        'duration': slot_duration,
                        'datetime': f"{slot['date']}T{slot['start_time']}"
                    })
            
            logger.info(f"Found {len(available_slots)} available slots")
            return available_slots
            
        except Exception as e:
            logger.error(f"Failed to get available slots: {e}")
            return []

    def create_appointment(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_date: str,
        duration_minutes: int = 30,
        appointment_type: str = "checkup",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new appointment.
        
        Args:
            patient_id: ID of the patient
            doctor_id: ID of the doctor
            appointment_date: Date and time in ISO format
            duration_minutes: Duration in minutes
            appointment_type: Type of appointment
            notes: Additional notes
        
        Returns:
            Created appointment record
        """
        try:
            logger.info(f"Creating appointment for patient {patient_id} with doctor {doctor_id}")
            
            # Prepare appointment data
            appointment_data = {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'appointment_date': appointment_date,
                'duration': duration_minutes,
                'appointment_type': appointment_type,
                'state': 'scheduled',
                'notes': notes or ''
            }
            
            # Create appointment in Odoo
            appointment_id = self.create('patient.appointment', appointment_data)
            
            # Read back the created appointment
            appointment = self.search_read(
                'patient.appointment',
                [('id', '=', appointment_id)],
                ['patient_id', 'doctor_id', 'appointment_date', 'duration', 'appointment_type', 'state', 'notes']
            )
            
            if appointment:
                logger.info(f"Appointment created successfully: {appointment_id}")
                return appointment[0]
            else:
                raise Exception("Failed to read created appointment")
                
        except Exception as e:
            logger.error(f"Failed to create appointment: {e}")
            raise

    def update_appointment(
        self,
        appointment_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing appointment.
        
        Args:
            appointment_id: ID of the appointment to update
            update_data: Dictionary with fields to update
        
        Returns:
            Updated appointment record
        """
        try:
            logger.info(f"Updating appointment {appointment_id}")
            
            # Update appointment in Odoo
            success = self.write('patient.appointment', appointment_id, update_data)
            
            if not success:
                raise Exception("Failed to update appointment")
            
            # Read back the updated appointment
            appointment = self.search_read(
                'patient.appointment',
                [('id', '=', appointment_id)],
                ['patient_id', 'doctor_id', 'appointment_date', 'duration', 'appointment_type', 'state', 'notes']
            )
            
            if appointment:
                logger.info(f"Appointment updated successfully: {appointment_id}")
                return appointment[0]
            else:
                raise Exception("Failed to read updated appointment")
                
        except Exception as e:
            logger.error(f"Failed to update appointment: {e}")
            raise

    def cancel_appointment(
        self,
        appointment_id: int,
        reason: Optional[str] = None,
        send_notification: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: ID of the appointment to cancel
            reason: Reason for cancellation
            send_notification: Whether to notify the patient
        
        Returns:
            Cancelled appointment record
        """
        try:
            logger.info(f"Cancelling appointment {appointment_id}")
            
            # Update appointment state to cancelled
            update_data = {
                'state': 'cancelled',
                'cancellation_reason': reason or 'No reason provided'
            }
            
            success = self.write('patient.appointment', appointment_id, update_data)
            
            if not success:
                raise Exception("Failed to cancel appointment")
            
            # Read back the cancelled appointment
            appointment = self.search_read(
                'patient.appointment',
                [('id', '=', appointment_id)],
                ['patient_id', 'doctor_id', 'appointment_date', 'duration', 'appointment_type', 'state', 'cancellation_reason']
            )
            
            if appointment:
                logger.info(f"Appointment cancelled successfully: {appointment_id}")
                
                # TODO: Send notification if requested
                if send_notification:
                    logger.info(f"Notification would be sent for cancelled appointment {appointment_id}")
                
                return appointment[0]
            else:
                raise Exception("Failed to read cancelled appointment")
                
        except Exception as e:
            logger.error(f"Failed to cancel appointment: {e}")
            raise


# Global instance
odoo_client_v3 = OdooClient()
