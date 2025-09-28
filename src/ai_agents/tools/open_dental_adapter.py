'''
================================================================================
OPEN DENTAL ADAPTER - REAL DATA INTERACTION LAYER
================================================================================

Copyright (c) 2025 Eran Sarfaty. All Rights Reserved.
🔒 PROPRIETARY SOFTWARE - PATENT PENDING 🔒

This module provides a data adapter for the Open Dental API.
It implements the interaction logic with the real Open Dental system.

Unauthorized copying or reverse engineering is strictly prohibited.
For licensing: scubapro711@gmail.com | +972-53-555-0317
================================================================================
'''

import logging
from typing import Dict, Any, List, Optional

from .open_dental_client import OpenDentalClient
from ...shared.i18n_ready_solution import get_message

logger = logging.getLogger(__name__)

class OpenDentalAdapter:
    """Adapter for interacting with the Open Dental API."""

    def __init__(self, language: str = 'en'):
        self.client = OpenDentalClient()
        self.language = language

    def search_patients(self, query: str) -> List[Dict[str, Any]]:
        """Search for patients using the Open Dental API."""
        try:
            patients = self.client.get_patients(LName=query)
            if not patients:
                return []
            
            # Format the patient data
            formatted_patients = []
            for patient in patients:
                formatted_patients.append(
                    {
                        "id": patient.get('PatNum', 'N/A'),
                        "name": patient.get('FName', ''),
                        "surname": patient.get('LName', ''),
                        "age": patient.get('Age', 'N/A')
                    }
                )
            return formatted_patients
        except Exception as e:
            logger.error(f"Error in search_patients: {e}")
            return []

    def get_providers(self) -> str:
        """Get a list of providers from the Open Dental API."""
        try:
            providers = self.client.get_providers()
            if not providers:
                return get_message('no_providers_found', self.language)
            
            provider_list = "\n".join([f"{p.get('ProvNum')}: {p.get('FName')} {p.get('LName')}" for p in providers])
            return get_message('providers_list', self.language, providers=provider_list)
        except Exception as e:
            return get_message('api_error', self.language, error=str(e))

    def get_available_slots(self, date: str, provider_num: Optional[int] = None) -> str:
        """Get available appointment slots from the Open Dental API."""
        try:
            slots = self.client.get_available_slots(date=date, provider_num=provider_num)
            if not slots:
                return get_message('no_slots_found', self.language, date=date)
            
            slot_list = "\n".join([f"{s.get('start')} - {s.get('end')}" for s in slots])
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

    def get_patient_appointments(self, patient_num: int) -> str:
        """Get all appointments for a patient from the Open Dental API."""
        try:
            appointments = self.client.get_appointments(PatNum=patient_num)
            if not appointments:
                return get_message('no_appointments_found', self.language, patient_num=patient_num)
            
            appointment_list = "\n".join([f"{a.get('AptDateTime')} - {a.get('ProcDescs')}" for a in appointments])
            return get_message('appointments_list', self.language, appointments=appointment_list)
        except Exception as e:
            return get_message('api_error', self.language, error=str(e))

    def cancel_appointment(self, appointment_id: int) -> str:
        """Cancel an appointment using the Open Dental API."""
        try:
            self.client.update_appointment(appointment_id, {'AptStatus': 'Cancelled'})
            return get_message('appointment_cancelled', self.language, appointment_id=appointment_id)
        except Exception as e:
            return get_message('api_error', self.language, error=str(e))

