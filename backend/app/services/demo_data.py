"""
Demo Data Service

Provides realistic mock data for Interactive Demo mode.
This allows potential customers to try DentaFlow without creating an account.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random


class DemoDataService:
    """Generate and manage realistic demo data for Interactive Demo mode."""
    
    # Demo Clinic Information
    DEMO_CLINIC = {
        "id": "demo_clinic_1",
        "name": "DentaFlow Demo Clinic",
        "address": "123 Dental Street, Tel Aviv, Israel",
        "phone": "+972-3-123-4567",
        "email": "info@dentaflow-demo.com",
        "website": "https://dentaflow.ai",
        "hours": {
            "sunday": "08:00-18:00",
            "monday": "08:00-18:00",
            "tuesday": "08:00-18:00",
            "wednesday": "08:00-18:00",
            "thursday": "08:00-18:00",
            "friday": "08:00-13:00",
            "saturday": "Closed",
        }
    }
    
    # Demo Patients
    DEMO_PATIENTS = [
        {
            "id": "demo_patient_1",
            "name": "Sarah Johnson",
            "name_hebrew": "שרה ג'ונסון",
            "phone": "+972-50-123-4567",
            "email": "sarah.j@example.com",
            "date_of_birth": "1985-03-15",
            "last_visit": "2025-10-10",
            "next_appointment": "2025-10-25",
            "balance": 0,
            "notes": "Regular patient, no allergies",
        },
        {
            "id": "demo_patient_2",
            "name": "David Cohen",
            "name_hebrew": "דוד כהן",
            "phone": "+972-52-234-5678",
            "email": "david.c@example.com",
            "date_of_birth": "1978-07-22",
            "last_visit": "2025-09-15",
            "next_appointment": "2025-11-05",
            "balance": 450,
            "notes": "Allergic to penicillin",
        },
        {
            "id": "demo_patient_3",
            "name": "Rachel Levi",
            "name_hebrew": "רחל לוי",
            "phone": "+972-54-345-6789",
            "email": "rachel.l@example.com",
            "date_of_birth": "1992-11-08",
            "last_visit": "2025-10-12",
            "next_appointment": None,
            "balance": -200,  # Credit
            "notes": "Prefers morning appointments",
        },
        {
            "id": "demo_patient_4",
            "name": "Michael Green",
            "name_hebrew": "מיכאל גרין",
            "phone": "+972-53-456-7890",
            "email": "michael.g@example.com",
            "date_of_birth": "1965-05-30",
            "last_visit": "2025-08-20",
            "next_appointment": "2025-10-30",
            "balance": 1200,
            "notes": "Requires sedation for procedures",
        },
        {
            "id": "demo_patient_5",
            "name": "Tamar Shapiro",
            "name_hebrew": "תמר שפירא",
            "phone": "+972-50-567-8901",
            "email": "tamar.s@example.com",
            "date_of_birth": "2000-02-14",
            "last_visit": "2025-10-14",
            "next_appointment": "2025-12-01",
            "balance": 0,
            "notes": "Student, prefers afternoon appointments",
        },
    ]
    
    # Demo Doctors
    DEMO_DOCTORS = [
        {
            "id": "demo_doctor_1",
            "name": "Dr. Rachel Cohen",
            "name_hebrew": "ד״ר רחל כהן",
            "specialty": "General Dentistry",
            "phone": "+972-50-111-2222",
            "email": "dr.cohen@dentaflow-demo.com",
        },
        {
            "id": "demo_doctor_2",
            "name": "Dr. Yossi Mizrahi",
            "name_hebrew": "ד״ר יוסי מזרחי",
            "specialty": "Orthodontics",
            "phone": "+972-52-222-3333",
            "email": "dr.mizrahi@dentaflow-demo.com",
        },
        {
            "id": "demo_doctor_3",
            "name": "Dr. Maya Goldstein",
            "name_hebrew": "ד״ר מאיה גולדשטיין",
            "specialty": "Endodontics",
            "phone": "+972-54-333-4444",
            "email": "dr.goldstein@dentaflow-demo.com",
        },
    ]
    
    # Demo Appointments (next 30 days)
    @staticmethod
    def get_demo_appointments(date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get demo appointments for a specific date or all upcoming appointments.
        
        Args:
            date: Optional date string (YYYY-MM-DD). If None, returns all upcoming.
            
        Returns:
            List of appointment dictionaries
        """
        today = datetime.now()
        appointments = []
        
        # Generate appointments for next 30 days
        for i in range(30):
            appt_date = today + timedelta(days=i)
            
            # Skip Saturdays (clinic closed)
            if appt_date.weekday() == 5:
                continue
            
            # 3-5 appointments per day
            num_appts = random.randint(3, 5)
            
            for j in range(num_appts):
                # Random time between 8:00 and 17:00
                hour = random.randint(8, 16)
                minute = random.choice([0, 30])
                
                # Random patient and doctor
                patient = random.choice(DemoDataService.DEMO_PATIENTS)
                doctor = random.choice(DemoDataService.DEMO_DOCTORS)
                
                # Random appointment type
                appt_type = random.choice([
                    "Cleaning",
                    "Check-up",
                    "Filling",
                    "Root Canal",
                    "Crown",
                    "Extraction",
                    "Consultation",
                ])
                
                appointments.append({
                    "id": f"demo_appt_{i}_{j}",
                    "patient_id": patient["id"],
                    "patient_name": patient["name"],
                    "doctor_id": doctor["id"],
                    "doctor_name": doctor["name"],
                    "date": appt_date.strftime("%Y-%m-%d"),
                    "time": f"{hour:02d}:{minute:02d}",
                    "type": appt_type,
                    "duration": 30 if appt_type in ["Cleaning", "Check-up"] else 60,
                    "status": "scheduled",
                    "notes": "",
                })
        
        # Filter by date if provided
        if date:
            appointments = [a for a in appointments if a["date"] == date]
        
        return appointments
    
    # Demo Invoices
    DEMO_INVOICES = [
        {
            "id": "demo_invoice_1",
            "patient_id": "demo_patient_2",
            "patient_name": "David Cohen",
            "date": "2025-09-15",
            "amount": 450,
            "paid": 0,
            "balance": 450,
            "items": [
                {"description": "Dental Cleaning", "amount": 200},
                {"description": "X-Ray", "amount": 150},
                {"description": "Filling", "amount": 100},
            ],
            "status": "unpaid",
        },
        {
            "id": "demo_invoice_2",
            "patient_id": "demo_patient_4",
            "patient_name": "Michael Green",
            "date": "2025-08-20",
            "amount": 1200,
            "paid": 0,
            "balance": 1200,
            "items": [
                {"description": "Root Canal", "amount": 800},
                {"description": "Crown", "amount": 400},
            ],
            "status": "unpaid",
        },
        {
            "id": "demo_invoice_3",
            "patient_id": "demo_patient_1",
            "patient_name": "Sarah Johnson",
            "date": "2025-10-10",
            "amount": 200,
            "paid": 200,
            "balance": 0,
            "items": [
                {"description": "Dental Cleaning", "amount": 200},
            ],
            "status": "paid",
        },
    ]
    
    # Demo Financial Summary
    DEMO_FINANCIAL_SUMMARY = {
        "total_revenue_month": 15600,
        "total_revenue_year": 187200,
        "outstanding_balance": 1650,
        "total_patients": 5,
        "appointments_month": 42,
        "average_invoice": 520,
        "top_services": [
            {"service": "Dental Cleaning", "count": 18, "revenue": 3600},
            {"service": "Filling", "count": 12, "revenue": 1200},
            {"service": "Root Canal", "count": 5, "revenue": 4000},
            {"service": "Crown", "count": 4, "revenue": 1600},
            {"service": "Extraction", "count": 3, "revenue": 900},
        ],
    }
    
    @staticmethod
    def get_demo_patient(patient_id: Optional[str] = None, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get demo patient by ID or name.
        
        Args:
            patient_id: Patient ID to search for
            name: Patient name to search for
            
        Returns:
            Patient dictionary or None if not found
        """
        if patient_id:
            for patient in DemoDataService.DEMO_PATIENTS:
                if patient["id"] == patient_id:
                    return patient
        
        if name:
            name_lower = name.lower()
            for patient in DemoDataService.DEMO_PATIENTS:
                if (name_lower in patient["name"].lower() or 
                    name_lower in patient["name_hebrew"]):
                    return patient
        
        return None
    
    @staticmethod
    def get_demo_available_slots(date: str) -> List[Dict[str, Any]]:
        """
        Get available appointment slots for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD)
            
        Returns:
            List of available time slots
        """
        # Get existing appointments for this date
        existing_appts = DemoDataService.get_demo_appointments(date)
        booked_times = {f"{a['time']}" for a in existing_appts}
        
        # Generate all possible slots (8:00-17:00, 30-minute intervals)
        all_slots = []
        for hour in range(8, 17):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                if time_str not in booked_times:
                    all_slots.append({
                        "time": time_str,
                        "available": True,
                        "doctor": random.choice(DemoDataService.DEMO_DOCTORS)["name"],
                    })
        
        return all_slots
    
    @staticmethod
    def get_demo_clinic_info() -> Dict[str, Any]:
        """Get demo clinic information."""
        return DemoDataService.DEMO_CLINIC
    
    @staticmethod
    def get_demo_doctors() -> List[Dict[str, Any]]:
        """Get list of demo doctors."""
        return DemoDataService.DEMO_DOCTORS
    
    @staticmethod
    def get_demo_invoices(patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get demo invoices, optionally filtered by patient.
        
        Args:
            patient_id: Optional patient ID to filter by
            
        Returns:
            List of invoice dictionaries
        """
        if patient_id:
            return [inv for inv in DemoDataService.DEMO_INVOICES if inv["patient_id"] == patient_id]
        return DemoDataService.DEMO_INVOICES
    
    @staticmethod
    def get_demo_financial_summary() -> Dict[str, Any]:
        """Get demo financial summary."""
        return DemoDataService.DEMO_FINANCIAL_SUMMARY


# Singleton instance
demo_data = DemoDataService()

