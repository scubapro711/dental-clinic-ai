'''
Enhanced Mock Dental Tool for Rich Development Environment
כלי דנטלי מדומה ומשופר לסביבת פיתוח עשירה
'''

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class EnhancedMockDentalTool:
    """
    Enhanced mock dental tool with a rich, realistic dataset for development and testing.
    This tool simulates a real-world dental clinic environment without needing a database connection.
    """
    
    def __init__(self):
        self.initialized = False
        self._load_mock_data()
        logger.info("Enhanced mock dental tool created")

    def _load_mock_data(self):
        """Loads all the mock data into the instance."""
        self.mock_patients = [
            {"id": 1, "name": "Yossi", "surname": "Mizrahi", "sex": "M", "birthdate": "1985-03-15", "city": "Tel Aviv", "notes": "מטופל שיתופי, מגיע לבדיקות באופן קבוע", "allergies": [], "phone": "050-1234567", "email": "yossi.mizrahi@gmail.com"},
            {"id": 2, "name": "Miriam", "surname": "Shapiro", "sex": "F", "birthdate": "1978-07-22", "city": "Jerusalem", "notes": "מטופלת חרדה, זקוקה להרגעה לפני טיפולים", "allergies": ["Penicillin"], "phone": "052-2345678", "email": "miriam.shapiro@walla.co.il"},
            {"id": 3, "name": "Avi", "surname": "Ben-David", "sex": "M", "birthdate": "1992-11-08", "city": "Haifa", "notes": "סטודנט, מעוניין בתשלומים", "allergies": [], "phone": "054-3456789", "email": "avi.bendavid@student.technion.ac.il"},
            {"id": 4, "name": "Tamar", "surname": "Katz", "sex": "F", "birthdate": "1965-05-30", "city": "Beersheba", "notes": "מטופלת ותיקה, מגיעה עם בעלה", "allergies": [], "phone": "050-4567890", "email": "tamar.katz@hotmail.com"},
            {"id": 5, "name": "Moshe", "surname": "Friedman", "sex": "M", "birthdate": "1955-12-03", "city": "Bnei Brak", "notes": "מטופל דתי, מעדיף טיפולים בימי ראשון", "allergies": [], "phone": "052-5678901", "email": "moshe.friedman@gmail.com"},
            {"id": 6, "name": "Noa", "surname": "Golan", "sex": "F", "birthdate": "1995-09-18", "city": "Ramat Gan", "notes": "מעוניינת בטיפולים אסתטיים", "allergies": [], "phone": "054-6789012", "email": "noa.golan@outlook.com"},
            {"id": 7, "name": "Eli", "surname": "Stern", "sex": "M", "birthdate": "1970-01-25", "city": "Netanya", "notes": "מטופל עסוק, מעדיף תורים מוקדמים", "allergies": [], "phone": "050-7890123", "email": "eli.stern@company.co.il"},
            {"id": 8, "name": "Shira", "surname": "Weiss", "sex": "F", "birthdate": "1988-04-12", "city": "Herzliya", "notes": "בהריון (חודש 6), זקוקה לטיפולים עדינים", "allergies": [], "phone": "052-8901234", "email": "shira.weiss@gmail.com"},
            {"id": 9, "name": "Daniel", "surname": "Rosenberg", "sex": "M", "birthdate": "2005-08-07", "city": "Petah Tikva", "notes": "זקוק ליישור שיניים", "allergies": [], "phone": "054-9012345", "email": "daniel.rosenberg@student.edu"},
            {"id": 10, "name": "Rivka", "surname": "Goldberg", "sex": "F", "birthdate": "1943-02-14", "city": "Tel Aviv", "notes": "זקוקה לתותבת חלקית", "allergies": [], "phone": "050-0123456", "email": "rivka.goldberg@gmail.com"},
            {"id": 11, "name": "Yair", "surname": "Levi", "sex": "M", "birthdate": "1980-06-28", "city": "Ashdod", "notes": "מגיע לבדיקות תקופתיות", "allergies": [], "phone": "052-1234567", "email": "yair.levi@yahoo.com"},
            {"id": 12, "name": "Dina", "surname": "Avraham", "sex": "F", "birthdate": "1972-10-15", "city": "Eilat", "notes": "מטופלת רגישה, זקוקה לכפפות ללא טקס", "allergies": ["Latex"], "phone": "054-2345678", "email": "dina.avraham@walla.co.il"},
            {"id": 13, "name": "Ron", "surname": "Peretz", "sex": "M", "birthdate": "1990-03-03", "city": "Kfar Saba", "notes": "מעוניין במגן שיניים לספורט", "allergies": [], "phone": "050-3456789", "email": "ron.peretz@sport.co.il"},
            {"id": 14, "name": "Gila", "surname": "Mor", "sex": "F", "birthdate": "1960-11-20", "city": "Holon", "notes": "זקוקה לטיפולי חניכיים", "allergies": [], "phone": "052-4567890", "email": "gila.mor@gmail.com"},
            {"id": 15, "name": "Amir", "surname": "Segal", "sex": "M", "birthdate": "1975-07-09", "city": "Rishon LeZion", "notes": "מטופל עם חרדת שיניים, זקוק להרגעה", "allergies": [], "phone": "054-5678901", "email": "amir.segal@company.co.il"},
            {"id": 16, "name": "Maya", "surname": "Klein", "sex": "F", "birthdate": "1998-12-25", "city": "Raanana", "notes": "סטודנטית, מעוניינת בהלבנת שיניים", "allergies": [], "phone": "050-6789012", "email": "maya.klein@student.ac.il"},
            {"id": 17, "name": "Boaz", "surname": "Haim", "sex": "M", "birthdate": "1963-05-17", "city": "Bat Yam", "notes": "מטופל מעשן, זקוק לניקויים תכופים", "allergies": [], "phone": "052-7890123", "email": "boaz.haim@hotmail.com"},
            {"id": 18, "name": "Orly", "surname": "Dahan", "sex": "F", "birthdate": "1982-09-30", "city": "Kiryat Gat", "notes": "מגיעה עם הילדים לטיפולים", "allergies": [], "phone": "054-8901234", "email": "orly.dahan@gmail.com"},
            {"id": 19, "name": "Gadi", "surname": "Yosef", "sex": "M", "birthdate": "1968-01-11", "city": "Acre", "notes": "מטופל עם ברוקסיזם, זקוק למגן לילה", "allergies": [], "phone": "050-9012345", "email": "gadi.yosef@walla.co.il"},
            {"id": 20, "name": "Hila", "surname": "Barak", "sex": "F", "birthdate": "1987-08-04", "city": "Modiin", "notes": "מעוניינת בטיפולי מניעה", "allergies": [], "phone": "052-0123456", "email": "hila.barak@outlook.com"}
        ]

        self.mock_doctors = [
            {"id": 1, "name": "Dr. David Cohen", "specialty": "רופא שיניים בכיר, מומחה בטיפולי שורש ושיקום פה"},
            {"id": 2, "name": "Dr. Sarah Levy", "specialty": "רופאת שיניים מומחית ביישור שיניים וטיפולים אסתטיים"},
            {"id": 3, "name": "Dr. Michael Goldstein", "specialty": "רופא שיניים מומחה בכירורגיה וטיפולי חניכיים"},
            {"id": 4, "name": "Dr. Rachel Rosen", "specialty": "רופאת שיניים מומחית בטיפולי ילדים ומניעה"}
        ]

        self.mock_treatments = [
            {"id": 1, "name": "Dental Cleaning", "description": "ניקוי שיניים מקצועי", "price": 250},
            {"id": 2, "name": "Fluoride Treatment", "description": "טיפול פלואור", "price": 150},
            {"id": 3, "name": "Dental Examination", "description": "בדיקת שיניים", "price": 200},
            {"id": 4, "name": "X-Ray", "description": "צילום רנטגן", "price": 120},
            {"id": 5, "name": "Filling - Composite", "description": "סתימה קומפוזיט", "price": 450},
            {"id": 6, "name": "Root Canal", "description": "טיפול שורש", "price": 1800},
            {"id": 7, "name": "Teeth Whitening", "description": "הלבנת שיניים", "price": 1200}
        ]

        self.mock_appointments = [
            {"id": 1, "patient_id": 1, "doctor_id": 1, "treatment_id": 1, "datetime": "2025-09-27 09:00:00", "status": "confirmed"},
            {"id": 2, "patient_id": 6, "doctor_id": 2, "treatment_id": 3, "datetime": "2025-09-27 10:00:00", "status": "confirmed"},
            {"id": 3, "patient_id": 15, "doctor_id": 3, "treatment_id": 6, "datetime": "2025-09-27 11:30:00", "status": "confirmed"},
            {"id": 4, "patient_id": 9, "doctor_id": 4, "treatment_id": 3, "datetime": "2025-09-27 14:00:00", "status": "scheduled"},
            {"id": 5, "patient_id": 4, "doctor_id": 1, "treatment_id": 6, "datetime": "2025-09-27 15:00:00", "status": "scheduled"},
            {"id": 6, "patient_id": 16, "doctor_id": 2, "treatment_id": 7, "datetime": "2025-09-28 08:30:00", "status": "scheduled"},
            {"id": 7, "patient_id": 7, "doctor_id": 1, "treatment_id": 1, "datetime": "2025-09-28 10:00:00", "status": "scheduled"},
            {"id": 8, "patient_id": 2, "doctor_id": 1, "treatment_id": 5, "datetime": "2025-09-29 09:00:00", "status": "scheduled"}
        ]

    async def initialize(self) -> None:
        """Initialize mock dental tool."""
        try:
            await asyncio.sleep(0.1)
            self.initialized = True
            logger.info("✅ Enhanced mock dental tool initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing enhanced mock dental tool: {e}")
            raise

    async def get_patient_details(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Get patient details by ID."""
        if not self.initialized:
            raise RuntimeError("Mock dental tool not initialized")
        for patient in self.mock_patients:
            if patient["id"] == patient_id:
                return patient
        return None

    async def cleanup(self) -> None:
        """Cleanup mock dental tool."""
        try:
            self.initialized = False
            logger.info("🧹 Enhanced mock dental tool cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up enhanced mock dental tool: {e}")
            raise

    async def get_available_slots(self, start_date: str, end_date: str, doctor_id: Optional[int] = None, treatment_duration: int = 30) -> List[Dict[str, Any]]:
        """Get available appointment slots with advanced filtering."""
        if not self.initialized:
            raise RuntimeError("Mock dental tool not initialized")

        available_slots = []
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        current_dt = start_dt
        while current_dt <= end_dt:
            # Clinic hours: 9:00 - 18:00
            for hour in range(9, 18):
                for minute in [0, 30]:
                    slot_time = current_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Check if slot is in the future
                    if slot_time < datetime.now():
                        continue

                    is_booked = False
                    for app in self.mock_appointments:
                        app_time = datetime.fromisoformat(app["datetime"])
                        app_end_time = app_time + timedelta(minutes=30) # Assuming all appointments are 30 mins
                        if (app_time <= slot_time < app_end_time) and (not doctor_id or app["doctor_id"] == doctor_id):
                            is_booked = True
                            break
                    
                    if not is_booked:
                        available_slots.append({
                            "datetime": slot_time.isoformat(),
                            "doctor_id": doctor_id or 1, # Default to Dr. Cohen
                            "duration": treatment_duration
                        })
            current_dt += timedelta(days=1)
        
        return available_slots

    async def book_appointment(self, patient_id: int, doctor_id: int, datetime_str: str, treatment_id: int) -> Dict[str, Any]:
        """Book a new appointment."""
        if not self.initialized:
            raise RuntimeError("Mock dental tool not initialized")

        new_appointment = {
            "id": len(self.mock_appointments) + 1,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "treatment_id": treatment_id,
            "datetime": datetime_str,
            "status": "scheduled"
        }
        self.mock_appointments.append(new_appointment)
        return {"success": True, "appointment": new_appointment}

    async def cancel_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """Cancel an existing appointment."""
        if not self.initialized:
            raise RuntimeError("Mock dental tool not initialized")

        for i, app in enumerate(self.mock_appointments):
            if app["id"] == appointment_id:
                self.mock_appointments.pop(i)
                return {"success": True}
        return {"success": False, "error": "Appointment not found"}

    async def get_patient_appointments(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get all appointments for a specific patient."""
        if not self.initialized:
            raise RuntimeError("Mock dental tool not initialized")
        
        return [app for app in self.mock_appointments if app["patient_id"] == patient_id]

    # --- Open Dental API Simulation --- #

    async def search_patients(self, name: str) -> List[Dict[str, Any]]:
        """Simulates searching for patients in Open Dental."""
        if not self.initialized:
            raise RuntimeError("Mock dental tool not initialized")
        
        search_results = []
        for patient in self.mock_patients:
            if name.lower() in patient["name"].lower() or name.lower() in patient["surname"].lower():
                search_results.append({
                    "PatientNum": patient["id"],
                    "LName": patient["surname"],
                    "FName": patient["name"],
                    "Birthdate": patient["birthdate"],
                    "Gender": 0 if patient["sex"] == 'M' else 1, # 0 for male, 1 for female in Open Dental
                    "Address": "",
                    "City": patient["city"],
                    "State": "",
                    "Zip": "",
                    "HmPhone": patient["phone"],
                    "WkPhone": "",
                    "WirelessPhone": patient["phone"],
                    "Email": patient["email"]
                })
        return search_results

