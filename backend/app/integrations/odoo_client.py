"""
Odoo Client for dental clinic ERP integration.

This client provides a high-level interface to interact with Odoo (or MockOdoo).
It uses OdooWrapper which provides an OdooRPC-compatible interface.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.integrations.odoo_wrapper import get_odoo_client


class OdooClient:
    """
    High-level client for Odoo operations.
    
    This client wraps OdooWrapper and provides convenient methods
    for common dental clinic operations.
    """
    
    def __init__(self):
        """Initialize Odoo client."""
        self._odoo = get_odoo_client()
    
    # Patient Management
    
    def search_patients(self, name: Optional[str] = None, phone: Optional[str] = None) -> List[int]:
        """
        Search for patients by name or phone.
        
        Args:
            name: Patient name (partial match)
            phone: Patient phone number
            
        Returns:
            List of patient IDs
            
        Example:
            >>> client = OdooClient()
            >>> patient_ids = client.search_patients(name="John")
            >>> print(patient_ids)
            [1, 5, 12]
        """
        # Use customer_rank for Odoo 19 (replaces is_patient)
        domain = [('customer_rank', '>', 0)]
        
        if name:
            domain.append(('name', 'ilike', name))
        if phone:
            domain.append(('phone', '=', phone))
        
        return self._odoo.env['res.partner'].search(domain)
    
    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Get patient details by ID.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Patient data dictionary or None
            
        Example:
            >>> client = OdooClient()
            >>> patient = client.get_patient(1)
            >>> print(patient['name'])
            'John Doe'
        """
        results = self._odoo.env['res.partner'].read(
            [patient_id],
            ['name', 'email', 'phone', 'street', 'city']
        )
        return results[0] if results else None
    
    def get_patient_full(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full patient details including all fields.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Complete patient data dictionary or None
        """
        results = self._odoo.env['res.partner'].read([patient_id])
        return results[0] if results else None
    
    def create_patient(self, name: str, email: Optional[str] = None, 
                      phone: Optional[str] = None, **kwargs) -> int:
        """
        Create a new patient.
        
        Args:
            name: Patient full name
            email: Patient email
            phone: Patient phone number
            **kwargs: Additional patient fields
            
        Returns:
            New patient ID
            
        Example:
            >>> client = OdooClient()
            >>> patient_id = client.create_patient(
            ...     name="Jane Doe",
            ...     email="jane@example.com",
            ...     phone="+972501234567"
            ... )
            >>> print(patient_id)
            1501
        """
        patient_data = {
            'name': name,
            'is_patient': True,
        }
        
        if email:
            patient_data['email'] = email
        if phone:
            patient_data['phone'] = phone
        
        # Add any additional fields
        patient_data.update(kwargs)
        
        return self._odoo.env['res.partner'].create(patient_data)
    
    def update_patient(self, patient_id: int, **kwargs) -> bool:
        """
        Update patient information.
        
        Args:
            patient_id: Patient ID
            **kwargs: Fields to update
            
        Returns:
            True if successful
            
        Example:
            >>> client = OdooClient()
            >>> success = client.update_patient(1, email="newemail@example.com")
            >>> print(success)
            True
        """
        return self._odoo.env['res.partner'].write([patient_id], kwargs)
    
    def count_patients(self) -> int:
        """
        Count total number of patients.
        
        Returns:
            Number of patients
        """
        return self._odoo.env['res.partner'].search_count([('customer_rank', '>', 0)])
    
    # Appointment Management
    
    def search_appointments(
        self,
        patient_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[int]:
        """
        Search for appointments.
        
        Args:
            patient_id: Filter by patient ID
            date_from: Start date filter (YYYY-MM-DD)
            date_to: End date filter (YYYY-MM-DD)
            status: Appointment status (scheduled, completed, cancelled)
            
        Returns:
            List of appointment IDs
            
        Example:
            >>> client = OdooClient()
            >>> appt_ids = client.search_appointments(patient_id=1, status="scheduled")
            >>> print(appt_ids)
            [10, 25, 42]
        """
        domain = []
        
        if patient_id:
            domain.append(('patient_id', '=', patient_id))
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        if status:
            domain.append(('status', '=', status))
        
        return self._odoo.env['dental.appointment'].search(domain)
    
    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get appointment details by ID.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Appointment data dictionary or None
            
        Example:
            >>> client = OdooClient()
            >>> appt = client.get_appointment(10)
            >>> print(f"{appt['date']} at {appt['time']}")
            '2025-10-15 at 14:00'
        """
        results = self._odoo.env['dental.appointment'].read(
            [appointment_id],
            ['patient_id', 'patient_name', 'date', 'time', 'datetime', 
             'treatment_type', 'duration_minutes', 'dentist', 'status', 'notes']
        )
        return results[0] if results else None
    
    def get_appointment_full(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full appointment details including all fields.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Complete appointment data dictionary or None
        """
        results = self._odoo.env['dental.appointment'].read([appointment_id])
        return results[0] if results else None
    
    def create_appointment(
        self,
        patient_id: int,
        date: str,
        time: str,
        treatment_type: str,
        duration_minutes: int = 60,
        notes: Optional[str] = None,
    ) -> int:
        """
        Create a new appointment.
        
        Args:
            patient_id: Patient ID
            date: Appointment date (YYYY-MM-DD)
            time: Appointment time (HH:MM)
            treatment_type: Type of treatment
            duration_minutes: Duration in minutes (default: 60)
            notes: Appointment notes
            
        Returns:
            New appointment ID
            
        Example:
            >>> client = OdooClient()
            >>> appt_id = client.create_appointment(
            ...     patient_id=1,
            ...     date="2025-10-15",
            ...     time="14:00",
            ...     treatment_type="Checkup"
            ... )
            >>> print(appt_id)
            12125
        """
        appointment_data = {
            'patient_id': patient_id,
            'date': date,
            'time': time,
            'treatment_type': treatment_type,
            'duration_minutes': duration_minutes,
        }
        
        if notes:
            appointment_data['notes'] = notes
        
        return self._odoo.env['dental.appointment'].create(appointment_data)
    
    def update_appointment(self, appointment_id: int, **kwargs) -> bool:
        """
        Update an existing appointment.
        
        Args:
            appointment_id: Appointment ID
            **kwargs: Fields to update
            
        Returns:
            True if successful
            
        Example:
            >>> client = OdooClient()
            >>> success = client.update_appointment(10, status="completed")
            >>> print(success)
            True
        """
        return self._odoo.env['dental.appointment'].write([appointment_id], kwargs)
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            True if successful
            
        Example:
            >>> client = OdooClient()
            >>> success = client.cancel_appointment(10)
            >>> print(success)
            True
        """
        return self.update_appointment(appointment_id, status='cancelled')
    
    def confirm_appointment(self, appointment_id: int) -> bool:
        """
        Confirm an appointment.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            True if successful
        """
        return self.update_appointment(appointment_id, status='confirmed')
    
    def complete_appointment(self, appointment_id: int) -> bool:
        """
        Mark an appointment as completed.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            True if successful
        """
        return self.update_appointment(appointment_id, status='completed')
    
    def count_appointments(self, status: Optional[str] = None) -> int:
        """
        Count appointments.
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            Number of appointments
        """
        domain = []
        if status:
            domain.append(('status', '=', status))
        
        return self._odoo.env['dental.appointment'].search_count(domain)
    
    # Invoice Management
    
    def search_invoices(
        self,
        patient_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[int]:
        """
        Search for invoices.
        
        Args:
            patient_id: Filter by patient ID
            status: Invoice status (draft, paid, cancelled)
            
        Returns:
            List of invoice IDs
        """
        domain = []
        
        if patient_id:
            domain.append(('patient_id', '=', patient_id))
        if status:
            domain.append(('status', '=', status))
        
        return self._odoo.env['account.move'].search(domain)
    
    def get_invoice(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """
        Get invoice details by ID.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Invoice data dictionary or None
        """
        results = self._odoo.env['account.move'].read(
            [invoice_id],
            ['patient_id', 'patient_name', 'issue_date', 'due_date',
             'total_amount', 'paid_amount', 'outstanding_amount', 'status']
        )
        return results[0] if results else None
    
    def get_invoice_full(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full invoice details including all fields.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Complete invoice data dictionary or None
        """
        results = self._odoo.env['account.move'].read([invoice_id])
        return results[0] if results else None
    
    def count_invoices(self, status: Optional[str] = None) -> int:
        """
        Count invoices.
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            Number of invoices
        """
        domain = []
        if status:
            domain.append(('status', '=', status))
        
        return self._odoo.env['account.move'].search_count(domain)
    
    # Available time slots
    
    def get_available_slots(
        self,
        date_from: str,
        date_to: str,
        duration_minutes: int = 60,
    ) -> List[Dict[str, str]]:
        """
        Get available appointment slots (simplified version).
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            duration_minutes: Required duration in minutes
            
        Returns:
            List of available slots with date and time
            
        Example:
            >>> client = OdooClient()
            >>> slots = client.get_available_slots("2025-10-15", "2025-10-16")
            >>> print(slots[0])
            {'date': '2025-10-15', 'time': '09:00'}
        """
        # This is a simplified implementation
        # In production, this would check dentist availability and existing appointments
        
        from datetime import datetime, timedelta
        
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        
        slots = []
        current = start_date.replace(hour=9, minute=0, second=0)
        
        while current < end_date:
            # Working hours: 9 AM to 5 PM
            if 9 <= current.hour < 17:
                slots.append({
                    'date': current.strftime('%Y-%m-%d'),
                    'time': current.strftime('%H:%M'),
                    'datetime': current.strftime('%Y-%m-%d %H:%M')
                })
            
            current += timedelta(minutes=duration_minutes)
            
            # Move to next day at 5 PM
            if current.hour >= 17:
                current = current.replace(hour=9, minute=0) + timedelta(days=1)
        
        return slots[:20]  # Return first 20 slots for MVP


# Global Odoo client instance
odoo_client = OdooClient()
