import os
from typing import List, Dict, Any, Optional
from .open_dental_client import OpenDentalAPIClient
from .i18n_ready_solution import get_message

class OpenDentalAdapter:
    """Adapter for the Open Dental API to be used by the AdvancedDentalTool."""

    def __init__(self, language: str = 'en'):
        self.client = OpenDentalAPIClient()
        self.language = language

    def search_patients(self, query: str) -> str:
        """Search for patients using the Open Dental API."""
        try:
            patients = self.client.get_patients(LName=query)
            if not patients:
                return get_message('no_patients_found', self.language, query=query)
            
            # For simplicity, returning the first match
            patient = patients[0]
            return get_message('patient_found', self.language, name=f"{patient['FName']} {patient['LName']}", age=patient.get('Age', 'N/A'))
        except Exception as e:
            return get_message('api_error', self.language, error=str(e))

    def get_providers(self) -> str:
        """Get a list of providers from the Open Dental API."""
        try:
            providers = self.client.get_providers()
            if not providers:
                return get_message('no_providers_found', self.language)
            
            provider_list = "\n".join([f"{p['ProvNum']}: {p['FName']} {p['LName']}" for p in providers])
            return get_message('providers_list', self.language, providers=provider_list)
        except Exception as e:
            return get_message('api_error', self.language, error=str(e))

    def get_available_slots(self, date: str, provider_num: Optional[int] = None) -> str:
        """Get available appointment slots from the Open Dental API."""
        try:
            slots = self.client.get_available_slots(date=date, provider_num=provider_num)
            if not slots:
                return get_message('no_slots_found', self.language, date=date)
            
            slot_list = "\n".join([f"{s['start']} - {s['end']}" for s in slots])
            return get_message('slots_list', self.language, date=date, slots=slot_list)
        except Exception as e:
            return get_message('api_error', self.language, error=str(e))

    def book_appointment(self, patient_num: int, provider_num: int, start_time: str, end_time: str) -> str:
        """Book an appointment using the Open Dental API."""
        try:
            appointment_data = {
                "PatNum": patient_num,
                "ProvNum": provider_num,
                "AptDateTime": start_time,
                "AptLength": 60 # Assuming 60 minutes for now
            }
            created_appointment = self.client.create_appointment(appointment_data)
            return get_message('appointment_booked', self.language, date=start_time.split('T')[0], time=start_time.split('T')[1])
        except Exception as e:
            return get_message('api_error', self.language, error=str(e))

