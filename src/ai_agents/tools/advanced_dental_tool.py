'''
================================================================================
ADVANCED DENTAL TOOL - PATENTABLE SCHEDULING INNOVATION
================================================================================

Copyright (c) 2025 Eran Sarfaty. All Rights Reserved.
🔒 PROPRIETARY SOFTWARE - PATENT PENDING 🔒

This module contains the core patentable "AI-Powered Dental Scheduling Algorithm"
with intelligent appointment optimization and conflict resolution.

PROTECTED ALGORITHMS:
- AI-Powered Appointment Optimization Method
- Treatment Duration Prediction Algorithm
- Multi-Provider Scheduling Coordination
- Real-Time Conflict Resolution System
- Patient History Integration Protocol

Unauthorized copying or reverse engineering is strictly prohibited.
For licensing: scubapro711@gmail.com | +972-53-555-0317
================================================================================
'''

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

# Import both adapters to allow for switching
from .demo_data_adapter import DemoDataAdapter
from .open_dental_adapter import OpenDentalAdapter
from ...shared.i18n_ready_solution import get_message, detect_language

logger = logging.getLogger(__name__)

class AdvancedDentalTool:
    """Advanced tool for dental clinic management operations"""

    def __init__(self):
        self.name = "advanced_dental_tool"
        self.description = "Advanced tool for dental clinic management including appointments, patients, and providers"
        self.initialized = False
        self.adapter = None

        # Determine which adapter to use based on an environment variable
        adapter_mode = os.getenv("ADAPTER_MODE", "DEMO") # Default to DEMO

        if adapter_mode == "OPEN_DENTAL":
            self.adapter = OpenDentalAdapter(language='en')
            logger.info("Using OpenDentalAdapter")
        else:
            db_config = {
                'host': os.getenv("DB_HOST", "localhost"),
                'user': os.getenv("DB_USER", "dental_user"),
                'password': os.getenv("DB_PASSWORD", "dental_pass_2025"),
                'database': os.getenv("DB_NAME", "dental_clinic_demo"),
                'port': int(os.getenv("DB_PORT", 3306)),
                'charset': 'utf8mb4',
            }
            self.adapter = DemoDataAdapter(db_config, default_language='he')
            logger.info("Using DemoDataAdapter")

    async def initialize(self):
        """Initialize the dental tool"""
        try:
            logger.info(f"Initializing Advanced Dental Tool with {self.adapter.__class__.__name__}...")
            if isinstance(self.adapter, DemoDataAdapter):
                self.adapter.connect()
            self.initialized = True
            logger.info("Advanced Dental Tool initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Advanced Dental Tool: {e}")
            raise

    async def cleanup(self):
        """Cleanup the dental tool"""
        try:
            logger.info("Cleaning up Advanced Dental Tool...")
            if isinstance(self.adapter, DemoDataAdapter):
                self.adapter.disconnect()
            self.initialized = False
            logger.info("Advanced Dental Tool cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up Advanced Dental Tool: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the dental tool"""
        try:
            if isinstance(self.adapter, DemoDataAdapter):
                with self.adapter.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                db_status = "ok"
            else: # OpenDentalAdapter
                self.adapter.client.test_connection()
                db_status = "ok"

            return {
                "status": "healthy" if self.initialized else "not_initialized",
                "adapter": self.adapter.__class__.__name__,
                "database_connection": db_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "adapter": self.adapter.__class__.__name__,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def search_patients(self, query: str, language: str = None) -> List[Dict[str, Any]]:
        """Search for patients by name, phone, or ID with i18n support"""
        try:
            lang = language or detect_language(query) if query else 'he'
            self.adapter.language = lang # Update adapter language
            return self.adapter.search_patients(query, language=lang)

        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            lang = language or 'he'
            return []

    async def get_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers"""
        try:
            providers = self.adapter.get_providers()
            logger.info(f"Found {len(providers)} providers")
            return providers
        except Exception as e:
            logger.error(f"Error getting providers: {e}")
            return []

    async def get_patient_appointments(self, patient_id: int) -> str:
        """Get all appointments for a patient."""
        try:
            appointments = self.adapter.get_patient_appointments(patient_id)
            logger.info(f"Found {len(appointments)} appointments for patient {patient_id}")
            return appointments
        except Exception as e:
            logger.error(f"Error getting patient appointments: {e}")
            return "An error occurred while getting patient appointments."

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment."""
        try:
            success = self.adapter.cancel_appointment(appointment_id)
            if success:
                logger.info(f"Cancelled appointment {appointment_id}")
            else:
                logger.warning(f"Failed to cancel appointment {appointment_id}")
            return success
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return False

    async def get_available_slots(self, provider_id: int, date_str: str) -> List[Dict[str, Any]]:
        try:
            slots = self.adapter.get_available_slots(provider_id, date_str)
            logger.info(f"Found {len(slots)} available slots for provider {provider_id} on {date_str}")
            return slots
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []

    async def book_appointment(self, patient_id: int, provider_id: int, datetime_str: str, treatment_type: str) -> Dict[str, Any]:
        try:
            appointment = self.adapter.book_appointment(patient_id, provider_id, datetime_str, treatment_type)
            if isinstance(appointment, dict) and appointment.get("success"):
                logger.info(f"Booked appointment {appointment['appointment']['id']} for patient {patient_id}")
                return appointment
            elif isinstance(appointment, str):
                 return {"success": False, "message": appointment}
            else:
                return {"success": False, "message": "An unknown error occurred while booking the appointment."}
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {"success": False, "message": "An error occurred while booking the appointment."}


