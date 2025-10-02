"""
Odoo XML-RPC Client for dental clinic ERP integration.

This client provides methods to interact with Odoo Dental module.
"""

import xmlrpc.client
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings


class OdooClient:
    """Client for Odoo XML-RPC API."""
    
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
            return self.uid is not None
        except Exception as e:
            print(f"Odoo authentication failed: {e}")
            return False
    
    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """
        Execute a method on an Odoo model.
        
        Args:
            model: Odoo model name (e.g., 'res.partner')
            method: Method to execute (e.g., 'search', 'read')
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method
            
        Returns:
            Result from Odoo
        """
        if not self.uid:
            self.authenticate()
        
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    # Patient Management
    
    def search_patients(self, name: Optional[str] = None, phone: Optional[str] = None) -> List[int]:
        """
        Search for patients by name or phone.
        
        Args:
            name: Patient name (partial match)
            phone: Patient phone number
            
        Returns:
            List of patient IDs
        """
        domain = []
        if name:
            domain.append(('name', 'ilike', name))
        if phone:
            domain.append(('phone', '=', phone))
        
        return self._execute('res.partner', 'search', domain)
    
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
            [patient_id],
            {'fields': ['name', 'email', 'phone', 'mobile', 'street', 'city']}
        )
        return results[0] if results else None
    
    def create_patient(self, name: str, email: Optional[str] = None, 
                      phone: Optional[str] = None) -> int:
        """
        Create a new patient in Odoo.
        
        Args:
            name: Patient full name
            email: Patient email
            phone: Patient phone number
            
        Returns:
            New patient ID
        """
        patient_data = {
            'name': name,
            'customer_rank': 1,  # Mark as customer
        }
        if email:
            patient_data['email'] = email
        if phone:
            patient_data['phone'] = phone
        
        return self._execute('res.partner', 'create', patient_data)
    
    # Appointment Management
    
    def search_appointments(
        self,
        patient_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        state: Optional[str] = None,
    ) -> List[int]:
        """
        Search for appointments.
        
        Args:
            patient_id: Filter by patient ID
            date_from: Start date filter
            date_to: End date filter
            state: Appointment state (draft, confirmed, done, cancelled)
            
        Returns:
            List of appointment IDs
        """
        domain = []
        if patient_id:
            domain.append(('partner_id', '=', patient_id))
        if date_from:
            domain.append(('appointment_date', '>=', date_from.strftime('%Y-%m-%d %H:%M:%S')))
        if date_to:
            domain.append(('appointment_date', '<=', date_to.strftime('%Y-%m-%d %H:%M:%S')))
        if state:
            domain.append(('state', '=', state))
        
        # Note: This assumes dental.appointment model exists in Odoo Dental
        return self._execute('dental.appointment', 'search', domain)
    
    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get appointment details by ID.
        
        Args:
            appointment_id: Odoo appointment ID
            
        Returns:
            Appointment data dictionary or None
        """
        results = self._execute(
            'dental.appointment', 'read',
            [appointment_id],
            {'fields': ['partner_id', 'appointment_date', 'duration', 'state', 'notes']}
        )
        return results[0] if results else None
    
    def create_appointment(
        self,
        patient_id: int,
        appointment_date: datetime,
        duration: float = 1.0,
        notes: Optional[str] = None,
    ) -> int:
        """
        Create a new appointment in Odoo.
        
        Args:
            patient_id: Patient ID
            appointment_date: Appointment date and time
            duration: Duration in hours
            notes: Appointment notes
            
        Returns:
            New appointment ID
        """
        appointment_data = {
            'partner_id': patient_id,
            'appointment_date': appointment_date.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': duration,
            'state': 'draft',
        }
        if notes:
            appointment_data['notes'] = notes
        
        return self._execute('dental.appointment', 'create', appointment_data)
    
    def update_appointment(self, appointment_id: int, **kwargs) -> bool:
        """
        Update an existing appointment.
        
        Args:
            appointment_id: Appointment ID
            **kwargs: Fields to update
            
        Returns:
            True if successful
        """
        return self._execute('dental.appointment', 'write', [appointment_id], kwargs)
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            True if successful
        """
        return self.update_appointment(appointment_id, state='cancelled')
    
    # Available time slots
    
    def get_available_slots(
        self,
        date_from: datetime,
        date_to: datetime,
        duration: float = 1.0,
    ) -> List[datetime]:
        """
        Get available appointment slots (simplified version).
        
        Args:
            date_from: Start date
            date_to: End date
            duration: Required duration in hours
            
        Returns:
            List of available datetime slots
        """
        # This is a simplified implementation
        # In production, this would check dentist availability and existing appointments
        
        # For MVP, return mock slots
        from datetime import timedelta
        
        slots = []
        current = date_from
        while current < date_to:
            # Working hours: 9 AM to 5 PM
            if 9 <= current.hour < 17:
                slots.append(current)
            current += timedelta(hours=duration)
        
        return slots[:10]  # Return first 10 slots for MVP


# Global Odoo client instance
odoo_client = OdooClient()
