"""
================================================================================
DEMO DATA ADAPTER - DATABASE INTERACTION LAYER
================================================================================

Copyright (c) 2025 Eran Sarfaty. All Rights Reserved.
🔒 PROPRIETARY SOFTWARE - PATENT PENDING 🔒

This module provides a data adapter for the demo database.
It implements the database interaction logic, separating it from the main tool.

Unauthorized copying or reverse engineering is strictly prohibited.
For licensing: scubapro711@gmail.com | +972-53-555-0317
================================================================================
"""

import pymysql
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from i18n_ready_solution import get_message, detect_language
from security_validators import SecurityValidator, DataSanitizer

logger = logging.getLogger(__name__)

class DemoDataAdapter:
    """Adapter for interacting with the demo database with i18n support."""

    def __init__(self, db_config, default_language='he'):
        self.db_config = db_config
        self.connection = None
        self.default_language = default_language

    def connect(self):
        """Connect to the database."""
        try:
            self.connection = pymysql.connect(**self.db_config)
            logger.info("Successfully connected to the demo database.")
        except pymysql.MySQLError as e:
            logger.error(f"Error connecting to the demo database: {e}")
            raise

    def disconnect(self):
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from the demo database.")

    def search_patients(self, query: str, language: str = None) -> str:
        """Search for patients in the database with i18n support."""
        query = DataSanitizer.sanitize_input(query)
        if not SecurityValidator.validate_patient_name(query):
            return get_message('invalid_input', language, field='patient name')

        if language is None:
            language = detect_language(query) if query else self.default_language

        if not self.connection:
            self.connect()

        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT patients_id as id, patients_name as name, patients_surname as surname, 
                           patients_sex as sex, patients_birthdate as birthdate
                    FROM patients 
                    WHERE patients_name LIKE %s OR patients_surname LIKE %s OR patients_id = %s
                """
                search_query = f"%{query}%"
                cursor.execute(sql, (search_query, search_query, query))
                results = cursor.fetchall()

                if not results:
                    return get_message('patient_not_found', language)

                if len(results) == 1:
                    patient = results[0]
                    full_name = f"{patient['name']} {patient['surname']}"
                    age = "N/A"
                    if patient['birthdate']:
                        try:
                            birth_year = patient['birthdate'].year
                            age = datetime.now().year - birth_year
                        except:
                            pass
                    return get_message('patient_found', language, name=full_name, age=age)
                else:
                    return get_message('search_results', language, count=len(results))

        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            return get_message('system_error', language, error=str(e))

    def get_available_slots(self, provider_id: int, date: str) -> List[Dict[str, Any]]:
        """Get available appointment slots from the database."""
        if not self.connection:
            self.connect()
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """ 
                SELECT appointments_from, appointments_to 
                FROM appointments 
                WHERE doctors_id = %s AND DATE(appointments_from) = %s
            """
            cursor.execute(sql, (provider_id, date))
            booked_slots = cursor.fetchall()

            available_slots = []
            day_start = datetime.strptime(f"{date} 09:00", "%Y-%m-%d %H:%M")
            for hour in range(9, 17):
                for minute in [0, 30]:
                    slot_time = day_start.replace(hour=hour, minute=minute)
                    is_booked = any(
                        slot["appointments_from"] <= slot_time < slot["appointments_to"]
                        for slot in booked_slots
                    )
                    if not is_booked:
                        available_slots.append({
                            "time": slot_time.strftime("%H:%M"),
                            "datetime": slot_time.isoformat(),
                            "available": True,
                            "duration": 30
                        })
            return available_slots

    def book_appointment(self, patient_id: int, provider_id: int, datetime_str: str, treatment_type: str, language: str = None) -> str:
        """Book an appointment in the database with i18n support."""
        if not SecurityValidator.validate_patient_name(treatment_type):
            return get_message('invalid_input', language, field='treatment type')

        if language is None:
            language = self.default_language

        if not self.connection:
            self.connect()

        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                appointment_time = datetime.fromisoformat(datetime_str)
                sql = """
                    INSERT INTO appointments (doctors_id, patients_id, rooms_id, appointments_from, appointments_to, appointments_title, appointments_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (provider_id, patient_id, 1, appointment_time, appointment_time + timedelta(minutes=30), treatment_type, 'scheduled'))
                self.connection.commit()

                date_str = appointment_time.strftime("%Y-%m-%d")
                time_str = appointment_time.strftime("%H:%M")

                return get_message('appointment_booked', language, date=date_str, time=time_str)

        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return get_message('system_error', language, error=str(e))

    def get_patient_appointments(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get all appointments for a patient from the database."""
        if not self.connection:
            self.connect()
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM appointments WHERE patients_id = %s"
            cursor.execute(sql, (patient_id,))
            return cursor.fetchall()

    def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment in the database."""
        if not self.connection:
            self.connect()
        with self.connection.cursor() as cursor:
            sql = "UPDATE appointments SET appointments_status = 'cancelled' WHERE appointments_id = %s"
            result = cursor.execute(sql, (appointment_id,))
            self.connection.commit()
            return result > 0

    def get_providers(self) -> List[Dict[str, Any]]:
        """Get a list of providers from the database."""
        if not self.connection:
            self.connect()
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT doctors_id as id, doctors_name as name, doctors_surname as surname, doctors_doctext as specialty FROM doctors"
            cursor.execute(sql)
            return cursor.fetchall()

