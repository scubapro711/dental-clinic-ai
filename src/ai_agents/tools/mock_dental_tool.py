"""
Mock Dental Tool for Testing
כלי דנטלי מדומה לבדיקות
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class MockDentalTool:
    """Mock dental tool that doesn't require database connection"""
    
    def __init__(self):
        self.initialized = False
        self.mock_appointments = [
            {
                "id": 1,
                "patient_id": "test_user_1",
                "date": "2025-09-30",
                "time": "10:00",
                "treatment_type": "ניקוי שיניים",
                "confirmed": True
            },
            {
                "id": 2,
                "patient_id": "test_user_2", 
                "date": "2025-10-01",
                "time": "14:30",
                "treatment_type": "בדיקה שגרתית",
                "confirmed": False
            }
        ]
        
        self.mock_available_slots = [
            {"date": "2025-09-30", "time": "09:00"},
            {"date": "2025-09-30", "time": "11:00"},
            {"date": "2025-10-01", "time": "10:00"},
            {"date": "2025-10-01", "time": "15:00"},
            {"date": "2025-10-02", "time": "09:30"},
            {"date": "2025-10-02", "time": "13:00"},
            {"date": "2025-10-03", "time": "10:30"},
        ]
        
        logger.info("Mock dental tool created")
    
    async def initialize(self) -> None:
        """Initialize mock dental tool"""
        try:
            # Simulate initialization delay
            await asyncio.sleep(0.1)
            self.initialized = True
            logger.info("✅ Mock dental tool initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing mock dental tool: {e}")
            raise
    
    async def get_available_slots(
        self, 
        start_date: str, 
        end_date: str, 
        treatment_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get available appointment slots (mock data)"""
        try:
            if not self.initialized:
                raise RuntimeError("Mock dental tool not initialized")
            
            # Filter slots by date range
            available_slots = []
            for slot in self.mock_available_slots:
                if start_date <= slot["date"] <= end_date:
                    available_slots.append({
                        **slot,
                        "treatment_type": treatment_type or "כללי",
                        "duration": 30,
                        "available": True
                    })
            
            logger.info(f"Found {len(available_slots)} available slots")
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []
    
    async def get_patient_appointments(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient appointments (mock data)"""
        try:
            if not self.initialized:
                raise RuntimeError("Mock dental tool not initialized")
            
            patient_appointments = [
                apt for apt in self.mock_appointments 
                if apt["patient_id"] == patient_id
            ]
            
            # Add some default appointments if none found
            if not patient_appointments and patient_id.startswith("test_"):
                patient_appointments = [
                    {
                        "id": 999,
                        "patient_id": patient_id,
                        "date": "2025-10-05",
                        "time": "10:00",
                        "treatment_type": "בדיקה שגרתית",
                        "confirmed": False
                    }
                ]
            
            logger.info(f"Found {len(patient_appointments)} appointments for {patient_id}")
            return patient_appointments
            
        except Exception as e:
            logger.error(f"Error getting patient appointments: {e}")
            return []
    
    async def book_appointment(
        self, 
        patient_id: str, 
        date: str, 
        time: str, 
        treatment_type: str
    ) -> Dict[str, Any]:
        """Book appointment (mock implementation)"""
        try:
            if not self.initialized:
                raise RuntimeError("Mock dental tool not initialized")
            
            # Simulate booking
            new_appointment = {
                "id": len(self.mock_appointments) + 1,
                "patient_id": patient_id,
                "date": date,
                "time": time,
                "treatment_type": treatment_type,
                "confirmed": False,
                "created_at": datetime.now().isoformat()
            }
            
            self.mock_appointments.append(new_appointment)
            
            logger.info(f"Booked appointment for {patient_id} on {date} at {time}")
            return {
                "success": True,
                "appointment": new_appointment,
                "message": f"תור נקבע בהצלחה ל-{date} בשעה {time}"
            }
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "שגיאה בקביעת התור"
            }
    
    async def confirm_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """Confirm appointment (mock implementation)"""
        try:
            if not self.initialized:
                raise RuntimeError("Mock dental tool not initialized")
            
            # Find and confirm appointment
            for apt in self.mock_appointments:
                if apt["id"] == appointment_id:
                    apt["confirmed"] = True
                    apt["confirmed_at"] = datetime.now().isoformat()
                    
                    logger.info(f"Confirmed appointment {appointment_id}")
                    return {
                        "success": True,
                        "appointment": apt,
                        "message": "התור אושר בהצלחה"
                    }
            
            return {
                "success": False,
                "error": "Appointment not found",
                "message": "התור לא נמצא"
            }
            
        except Exception as e:
            logger.error(f"Error confirming appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "שגיאה באישור התור"
            }
    
    async def cancel_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """Cancel appointment (mock implementation)"""
        try:
            if not self.initialized:
                raise RuntimeError("Mock dental tool not initialized")
            
            # Find and remove appointment
            for i, apt in enumerate(self.mock_appointments):
                if apt["id"] == appointment_id:
                    cancelled_apt = self.mock_appointments.pop(i)
                    
                    logger.info(f"Cancelled appointment {appointment_id}")
                    return {
                        "success": True,
                        "appointment": cancelled_apt,
                        "message": "התור בוטל בהצלחה"
                    }
            
            return {
                "success": False,
                "error": "Appointment not found",
                "message": "התור לא נמצא"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "שגיאה בביטול התור"
            }
    
    async def get_clinic_info(self) -> Dict[str, Any]:
        """Get clinic information (mock data)"""
        return {
            "name": "מרפאת שיניים דמו",
            "address": "רחוב יוסף לפיד 1, נתניה",
            "phone": "03-555-0123",
            "email": "info@dental-demo.co.il",
            "hours": {
                "sunday": "08:00-18:00",
                "monday": "08:00-18:00", 
                "tuesday": "08:00-18:00",
                "wednesday": "08:00-18:00",
                "thursday": "08:00-18:00",
                "friday": "08:00-13:00",
                "saturday": "סגור"
            },
            "services": [
                "בדיקות שגרתיות",
                "ניקוי שיניים",
                "טיפולי שורש",
                "עקירות",
                "השתלות",
                "יישור שיניים"
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for mock dental tool"""
        return {
            "status": "healthy",
            "initialized": self.initialized,
            "type": "mock",
            "appointments_count": len(self.mock_appointments),
            "available_slots_count": len(self.mock_available_slots),
            "timestamp": datetime.now().isoformat()
        }
    
    async def cleanup(self) -> None:
        """Cleanup mock dental tool"""
        try:
            self.initialized = False
            logger.info("🧹 Mock dental tool cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up mock dental tool: {e}")
            raise
