"""
Mock Odoo Service for MVP Development

This provides the same interface as the real Odoo client but with in-memory data.
Use this for MVP development and testing when Odoo is not available.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4


class MockOdooClient:
    """Mock Odoo client with in-memory data storage."""
    
    def __init__(self):
        """Initialize mock client with sample data."""
        self.patients = {}
        self.appointments = {}
        self.invoices = {}
        
        # Add some sample patients
        self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample patients and appointments for testing."""
        # Sample patients
        patients_data = [
            {"name": "David Cohen", "email": "david.cohen@example.com", "phone": "+972501234567"},
            {"name": "Sarah Levi", "email": "sarah.levi@example.com", "phone": "+972502345678"},
            {"name": "Michael Goldstein", "email": "michael.g@example.com", "phone": "+972503456789"},
        ]
        
        for patient_data in patients_data:
            patient_id = len(self.patients) + 1
            self.patients[patient_id] = {
                "id": patient_id,
                **patient_data,
                "created_at": datetime.now()
            }
    
    def authenticate(self) -> bool:
        """Mock authentication - always succeeds."""
        return True
    
    # Patient Management
    
    def search_patients(self, name: Optional[str] = None, phone: Optional[str] = None) -> List[int]:
        """Search for patients by name or phone."""
        results = []
        
        for patient_id, patient in self.patients.items():
            if name and name.lower() in patient["name"].lower():
                results.append(patient_id)
            elif phone and phone in patient["phone"]:
                results.append(patient_id)
        
        return results
    
    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Get patient details by ID."""
        return self.patients.get(patient_id)
    
    def create_patient(self, name: str, email: Optional[str] = None, 
                      phone: Optional[str] = None) -> int:
        """Create a new patient."""
        patient_id = len(self.patients) + 1
        self.patients[patient_id] = {
            "id": patient_id,
            "name": name,
            "email": email,
            "phone": phone,
            "created_at": datetime.now()
        }
        return patient_id
    
    # Appointment Management
    
    def search_appointments(
        self,
        patient_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        state: Optional[str] = None,
    ) -> List[int]:
        """Search for appointments."""
        results = []
        
        for appt_id, appt in self.appointments.items():
            if patient_id and appt["patient_id"] != patient_id:
                continue
            if date_from and appt["appointment_date"] < date_from:
                continue
            if date_to and appt["appointment_date"] > date_to:
                continue
            if state and appt["state"] != state:
                continue
            results.append(appt_id)
        
        return results
    
    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """Get appointment details by ID."""
        return self.appointments.get(appointment_id)
    
    def create_appointment(
        self,
        patient_id: int,
        appointment_date: datetime,
        duration: float = 1.0,
        notes: Optional[str] = None,
    ) -> int:
        """Create a new appointment."""
        appointment_id = len(self.appointments) + 1
        self.appointments[appointment_id] = {
            "id": appointment_id,
            "patient_id": patient_id,
            "appointment_date": appointment_date,
            "duration": duration,
            "notes": notes,
            "state": "confirmed",
            "created_at": datetime.now()
        }
        return appointment_id
    
    def update_appointment(self, appointment_id: int, **kwargs) -> bool:
        """Update an existing appointment."""
        if appointment_id in self.appointments:
            self.appointments[appointment_id].update(kwargs)
            return True
        return False
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel an appointment."""
        return self.update_appointment(appointment_id, state="cancelled")
    
    # Available time slots
    
    def get_available_slots(
        self,
        date_from: datetime,
        date_to: datetime,
        duration: float = 1.0,
    ) -> List[datetime]:
        """Get available appointment slots."""
        slots = []
        current = date_from.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current < date_to:
            # Skip weekends
            if current.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current += timedelta(days=1)
                continue
            
            # Working hours: 9 AM to 5 PM
            if 9 <= current.hour < 17:
                # Check if slot is available (not booked)
                is_available = True
                for appt in self.appointments.values():
                    if appt["state"] != "cancelled":
                        appt_time = appt["appointment_date"]
                        if abs((current - appt_time).total_seconds()) < 3600:  # Within 1 hour
                            is_available = False
                            break
                
                if is_available:
                    slots.append(current)
                
                current += timedelta(hours=1)
            else:
                # Move to next day
                current = current.replace(hour=9, minute=0) + timedelta(days=1)
        
        return slots[:20]  # Return first 20 available slots


# Global mock Odoo client instance
mock_odoo_client = MockOdooClient()
