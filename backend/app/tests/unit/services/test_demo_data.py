"""Unit Tests for Demo Data Service"""

import pytest
from datetime import datetime

from app.services.demo_data import DemoDataService


@pytest.mark.unit
@pytest.mark.services
class TestDemoDataService:
    """Test Demo Data service."""
    
    def test_get_demo_appointments(self):
        """Test getting demo appointments."""
        appointments = DemoDataService.get_demo_appointments()
        assert isinstance(appointments, list)
        assert len(appointments) > 0
    
    def test_get_demo_appointments_with_date(self):
        """Test getting appointments for specific date."""
        appointments = DemoDataService.get_demo_appointments(date="2025-10-25")
        assert isinstance(appointments, list)
    
    def test_get_demo_patient_by_id(self):
        """Test getting specific demo patient by ID."""
        patient = DemoDataService.get_demo_patient(patient_id="demo_patient_1")
        assert patient is not None
        assert "name" in patient
    
    def test_get_demo_available_slots(self):
        """Test getting available time slots."""
        slots = DemoDataService.get_demo_available_slots(date="2025-10-25")
        assert isinstance(slots, list)
    
    def test_get_demo_clinic_info(self):
        """Test getting demo clinic information."""
        clinic = DemoDataService.get_demo_clinic_info()
        assert isinstance(clinic, dict)
        assert "name" in clinic
    
    def test_get_demo_doctors(self):
        """Test getting demo doctors list."""
        doctors = DemoDataService.get_demo_doctors()
        assert isinstance(doctors, list)
        assert len(doctors) > 0
    
    def test_get_demo_invoices(self):
        """Test getting demo invoices."""
        invoices = DemoDataService.get_demo_invoices()
        assert isinstance(invoices, list)
    
    def test_get_demo_financial_summary(self):
        """Test getting financial summary."""
        summary = DemoDataService.get_demo_financial_summary()
        assert isinstance(summary, dict)



    def test_get_demo_patient_by_name(self):
        """Test getting patient by name search."""
        patient = DemoDataService.get_demo_patient(name="Sarah")
        assert patient is not None
        assert "Sarah" in patient["name"]
    
    def test_get_demo_patient_by_hebrew_name(self):
        """Test getting patient by Hebrew name search."""
        patient = DemoDataService.get_demo_patient(name="דוד")
        assert patient is not None
        assert patient["id"] == "demo_patient_2"
    
    def test_get_demo_patient_not_found(self):
        """Test getting non-existent patient returns None."""
        patient = DemoDataService.get_demo_patient(patient_id="non_existent")
        assert patient is None
    
    def test_get_demo_patient_name_not_found(self):
        """Test searching for non-existent name returns None."""
        patient = DemoDataService.get_demo_patient(name="NonExistentName")
        assert patient is None
    
    def test_demo_appointments_skip_saturdays(self):
        """Test that appointments don't include Saturdays (clinic closed)."""
        appointments = DemoDataService.get_demo_appointments()
        for appt in appointments:
            appt_date = datetime.strptime(appt["date"], "%Y-%m-%d")
            # Saturday is weekday 5
            assert appt_date.weekday() != 5, f"Found appointment on Saturday: {appt['date']}"
    
    def test_demo_appointments_structure(self):
        """Test appointment data structure is complete."""
        appointments = DemoDataService.get_demo_appointments()
        required_fields = ["id", "patient_id", "patient_name", "doctor_id", 
                          "doctor_name", "date", "time", "type", "duration", "status"]
        for appt in appointments[:5]:  # Check first 5
            for field in required_fields:
                assert field in appt, f"Missing field {field} in appointment"
    
    def test_get_demo_invoices_filtered_by_patient(self):
        """Test getting invoices filtered by patient ID."""
        invoices = DemoDataService.get_demo_invoices(patient_id="demo_patient_2")
        assert len(invoices) > 0
        for invoice in invoices:
            assert invoice["patient_id"] == "demo_patient_2"
    
    def test_demo_financial_summary_structure(self):
        """Test financial summary contains all required fields."""
        summary = DemoDataService.get_demo_financial_summary()
        required_fields = ["total_revenue_month", "total_revenue_year", 
                          "outstanding_balance", "total_patients", 
                          "appointments_month", "average_invoice", "top_services"]
        for field in required_fields:
            assert field in summary, f"Missing field {field} in financial summary"
        assert isinstance(summary["top_services"], list)
        assert len(summary["top_services"]) > 0
    
    def test_demo_available_slots_exclude_booked(self):
        """Test that available slots exclude already booked times."""
        date = "2025-10-25"
        appointments = DemoDataService.get_demo_appointments(date=date)
        slots = DemoDataService.get_demo_available_slots(date=date)
        
        booked_times = {appt["time"] for appt in appointments}
        available_times = {slot["time"] for slot in slots}
        
        # No overlap between booked and available
        overlap = booked_times & available_times
        assert len(overlap) == 0, f"Found overlapping times: {overlap}"
    
    def test_demo_clinic_info_structure(self):
        """Test clinic info contains all required fields."""
        clinic = DemoDataService.get_demo_clinic_info()
        required_fields = ["id", "name", "address", "phone", "email", "website", "hours"]
        for field in required_fields:
            assert field in clinic, f"Missing field {field} in clinic info"
        assert isinstance(clinic["hours"], dict)
        assert "sunday" in clinic["hours"]

