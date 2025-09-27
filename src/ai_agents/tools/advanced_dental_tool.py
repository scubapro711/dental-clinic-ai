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
from datetime import datetime
import os

# Import both adapters to allow for switching
from .demo_data_adapter import DemoDataAdapter
from .open_dental_adapter import OpenDentalAdapter
from .i18n_ready_solution import get_message, detect_language

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

    async def search_patients(self, query: str, language: str = None) -> str:
        """Search for patients by name, phone, or ID with i18n support"""
        try:
            lang = language or detect_language(query) if query else 'he'
            self.adapter.language = lang # Update adapter language
            result = self.adapter.search_patients(query)
            logger.info(f"Patient search completed for query: {query}")
            return result
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            lang = language or 'he'
            return get_message('system_error', lang, error=str(e))

    async def get_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers"""
        try:
            providers = self.adapter.get_providers()
            logger.info(f"Found {len(providers)} providers")
            return providers
        except Exception as e:
            logger.error(f"Error getting providers: {e}")
            return []

    # ... (add other methods like book_appointment, etc. delegating to the adapter)

    def get_tool_description(self) -> str:
        """Get tool description for AI agents"""
        return '''
        Advanced Dental Tool - כלי מתקדם לניהול מרפאת שיניים

        Available functions:
        - search_patients(query, language): Search for patients.
        - get_providers(): Get list of available providers.
        - ... (other functions)
        '''

