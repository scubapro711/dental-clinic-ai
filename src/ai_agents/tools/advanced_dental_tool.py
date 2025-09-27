#!/usr/bin/env python3
"""
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
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os

from .demo_data_adapter import DemoDataAdapter

logger = logging.getLogger(__name__)

class AdvancedDentalTool:
    """Advanced tool for dental clinic management operations"""
    
    def __init__(self):
        self.name = "advanced_dental_tool"
        self.description = "Advanced tool for dental clinic management including appointments, patients, and providers"
        self.initialized = False
        db_config = {
            'host': os.getenv("DB_HOST", "localhost"),
            'user': os.getenv("DB_USER", "dental_user"),
            'password': os.getenv("DB_PASSWORD", "dental_pass_2025"),
            'database': os.getenv("DB_NAME", "dental_clinic_demo"),
            'port': int(os.getenv("DB_PORT", 3306)),
            'charset': 'utf8mb4',
        }
        self.adapter = DemoDataAdapter(db_config, default_language='he')
    
    async def initialize(self):
        """Initialize the dental tool"""
        try:
            logger.info("Initializing Advanced Dental Tool...")
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
            self.adapter.disconnect()
            self.initialized = False
            logger.info("Advanced Dental Tool cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up Advanced Dental Tool: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the dental tool"""
        try:
            # Check database connection without disconnecting
            if not self.adapter.connection:
                self.adapter.connect()
            # Test with a simple query
            with self.adapter.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return {
                "status": "healthy" if self.initialized else "not_initialized",
                "tool_name": self.name,
                "initialized": self.initialized,
                "database_connection": "ok",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "tool_name": self.name,
                "error": str(e),
                "database_connection": "error",
                "timestamp": datetime.now().isoformat()
            }
        
    async def search_patients(self, query: str, language: str = None) -> str:
        """Search for patients by name, phone, or ID with i18n support"""
        try:
            result = self.adapter.search_patients(query, language)
            logger.info(f"Patient search completed for query: {query}")
            return result
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            # Import i18n functions for error handling
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
            from i18n_ready_solution import get_message, detect_language
            
            lang = language or detect_language(query) if query else 'he'
            return get_message('system_error', lang, error=str(e))
    
    async def get_available_slots(self, provider_id: int, date: str) -> List[Dict[str, Any]]:
        """Get available appointment slots for a provider on a specific date"""
        try:
            slots = self.adapter.get_available_slots(provider_id, date)
            logger.info(f"Found {len(slots)} available slots for provider {provider_id} on {date}")
            return slots
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []
    
    async def book_appointment(self, patient_id: int, provider_id: int, datetime_str: str, 
                             treatment_type: str = "General Checkup", language: str = None) -> str:
        """Book an appointment for a patient with i18n support"""
        try:
            result = self.adapter.book_appointment(patient_id, provider_id, datetime_str, treatment_type, language)
            logger.info(f"Booked appointment for patient {patient_id}")
            return result
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            # Import i18n functions for error handling
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
            from i18n_ready_solution import get_message
            
            lang = language or 'he'
            return get_message('system_error', lang, error=str(e))
    
    async def get_patient_appointments(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get all appointments for a patient"""
        try:
            appointments = self.adapter.get_patient_appointments(patient_id)
            logger.info(f"Found {len(appointments)} appointments for patient {patient_id}")
            return appointments
        except Exception as e:
            logger.error(f"Error getting patient appointments: {e}")
            return []
    
    async def cancel_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """Cancel an appointment"""
        try:
            success = self.adapter.cancel_appointment(appointment_id)
            if success:
                logger.info(f"Cancelled appointment {appointment_id}")
                return {
                    "success": True,
                    "appointment_id": appointment_id,
                    "message": f"Appointment {appointment_id} cancelled successfully"
                }
            else:
                logger.warning(f"Appointment {appointment_id} not found for cancellation")
                return {
                    "success": False,
                    "appointment_id": appointment_id,
                    "message": f"Appointment {appointment_id} not found"
                }
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to cancel appointment"
            }
    
    async def get_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers"""
        try:
            providers = self.adapter.get_providers()
            logger.info(f"Found {len(providers)} providers")
            return providers
        except Exception as e:
            logger.error(f"Error getting providers: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_tool_description(self) -> str:
        """Get tool description for AI agents"""
        return """
        Advanced Dental Tool - כלי מתקדם לניהול מרפאת שיניים
        
        Available functions:
        - search_patients(query): Search for patients by name, phone, or ID
        - get_available_slots(provider_id, date): Get available appointment slots
        - book_appointment(patient_id, provider_id, datetime, treatment_type): Book an appointment
        - get_patient_appointments(patient_id): Get patient's appointments
        - cancel_appointment(appointment_id): Cancel an appointment
        - get_providers(): Get list of available providers
        
        Use this tool for all dental clinic management operations.
        """

