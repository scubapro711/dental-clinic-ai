#!/usr/bin/env python3
"""
Large Scale Mock Data Tool for Dental Clinic AI System
Generates 1500 patients and 10 doctors for stress testing
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

class LargeScaleMockTool:
    """Enhanced mock data tool with 1500 patients and 10 doctors"""
    
    def __init__(self):
        self.patients = self._generate_patients(1500)
        self.doctors = self._generate_doctors(10)
        self.appointments = self._generate_appointments(2000)
        self.treatments = self._generate_treatments(3000)
        
    def _generate_patients(self, count: int) -> List[Dict[str, Any]]:
        """Generate realistic Israeli patient data"""
        
        # Israeli first names
        hebrew_first_names = [
            "דוד", "משה", "יוסף", "אברהם", "דניאל", "מיכאל", "אליהו", "יעקב", "שמואל", "רפאל",
            "שרה", "רחל", "לאה", "רבקה", "מרים", "אסתר", "רות", "נעמי", "דינה", "חנה",
            "אמיר", "רון", "גיל", "עמית", "תומר", "יונתן", "אורי", "נתן", "איתי", "עידו",
            "נועה", "מיכל", "שירה", "תמר", "יעל", "ליאור", "מאיה", "ענת", "דנה", "אורית",
            "אלון", "בועז", "גדעון", "חיים", "טל", "יאיר", "כפיר", "לירון", "מתן", "נדב",
            "אביגיל", "בת-שבע", "גליה", "דליה", "הדס", "ורד", "זהבה", "חוה", "טליה", "יפה"
        ]
        
        # Israeli last names
        hebrew_last_names = [
            "כהן", "לוי", "מזרחי", "פרץ", "ביטון", "דהן", "אברהם", "אזולאי", "מלכה", "חדד",
            "בן דוד", "אוחנה", "שמעון", "אמסלם", "אלבז", "סעדון", "מועלם", "בוחבוט", "עמר", "אטיאס",
            "רוזן", "שפירא", "גולדברג", "פרידמן", "קפלן", "ברק", "אור", "נור", "זהבי", "כסף",
            "אבני", "בר", "גל", "דור", "הראל", "ויס", "זכאי", "חן", "טוב", "יפה",
            "קדוש", "לבן", "מור", "נחום", "סגל", "עוז", "פז", "צור", "קמחי", "רם"
        ]
        
        # Phone prefixes in Israel
        phone_prefixes = ["050", "052", "053", "054", "055", "058", "02", "03", "04", "08", "09"]
        
        # Cities in Israel
        cities = [
            "תל אביב", "ירושלים", "חיפה", "ראשון לציון", "אשדוד", "נתניה", "באר שבע", "בני ברק",
            "חולון", "רמת גן", "אשקלון", "רחובות", "בת ים", "כפר סבא", "הרצליה", "חדרה",
            "מודיעין", "נצרת", "לוד", "רעננה", "אילת", "טבריה", "קריית גת", "דימונה",
            "עכו", "נהריה", "קריית שמונה", "בית שמש", "מעלה אדומים", "כרמיאל"
        ]
        
        patients = []
        
        for i in range(count):
            patient_id = f"P{str(i+1).zfill(4)}"
            first_name = random.choice(hebrew_first_names)
            last_name = random.choice(hebrew_last_names)
            
            # Generate realistic age distribution
            age = random.choices(
                range(5, 85),
                weights=[1 if 18 <= age <= 65 else 0.3 for age in range(5, 85)]
            )[0]
            
            # Generate phone number
            prefix = random.choice(phone_prefixes)
            if prefix in ["02", "03", "04", "08", "09"]:
                phone = f"{prefix}-{random.randint(1000000, 9999999)}"
            else:
                phone = f"{prefix}-{random.randint(1000000, 9999999)}"
            
            # Generate medical history
            conditions = []
            if random.random() < 0.3:  # 30% have dental conditions
                dental_conditions = ["עששת", "מחלת חניכיים", "רגישות שיניים", "בעיות נשיכה", "שחיקת שיניים"]
                conditions.extend(random.sample(dental_conditions, random.randint(1, 2)))
            
            if random.random() < 0.2:  # 20% have medical conditions
                medical_conditions = ["סכרת", "לחץ דם גבוה", "אלרגיות", "מחלות לב", "אסטמה"]
                conditions.extend(random.sample(medical_conditions, random.randint(1, 2)))
            
            # Generate visit frequency (realistic distribution)
            last_visit_days_ago = random.choices(
                range(1, 730),  # 1 day to 2 years
                weights=[10 if days <= 180 else 1 for days in range(1, 730)]
            )[0]
            
            patient = {
                "patient_id": patient_id,
                "name": f"{first_name} {last_name}",
                "first_name": first_name,
                "last_name": last_name,
                "age": age,
                "phone": phone,
                "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
                "address": f"{random.choice(cities)}, ישראל",
                "medical_history": conditions,
                "last_visit": (datetime.now() - timedelta(days=last_visit_days_ago)).strftime("%Y-%m-%d"),
                "insurance": random.choice(["כללית", "מכבי", "מאוחדת", "לאומית", "פרטי"]),
                "emergency_contact": f"{random.choice(phone_prefixes)}-{random.randint(1000000, 9999999)}",
                "preferred_language": random.choices(["עברית", "אנגלית", "ערבית", "רוסית"], weights=[70, 20, 7, 3])[0],
                "status": random.choices(["פעיל", "לא פעיל", "חדש"], weights=[85, 10, 5])[0],
                "notes": f"מטופל {'קבוע' if random.random() < 0.7 else 'מזדמן'}"
            }
            
            patients.append(patient)
        
        return patients
    
    def _generate_doctors(self, count: int) -> List[Dict[str, Any]]:
        """Generate 10 diverse doctors with specializations"""
        
        doctor_names = [
            ("ד\"ר יוסי כהן", "רופא שיניים כללי", "20 שנות ניסיון"),
            ("ד\"ר שרה לוי", "אורתודונטית", "מומחית ליישור שיניים"),
            ("ד\"ר מיכאל רוזן", "כירורג פה ולסת", "מומחה להשתלות"),
            ("ד\"ר רחל אברהם", "אנדודונטית", "מומחית לטיפולי שורש"),
            ("ד\"ר דוד מזרחי", "פריודונטולוג", "מומחה למחלות חניכיים"),
            ("ד\"ר נועה גולדברג", "רופאת שיניים ילדים", "מומחית לטיפול בילדים"),
            ("ד\"ר אמיר ביטון", "פרוסטודונטיסט", "מומחה לשיקום הפה"),
            ("ד\"ר תמר שפירא", "רופאת שיניים אסתטית", "מומחית לחיוך יפה"),
            ("ד\"ר רון דהן", "כירורג פה", "מומחה לעקירות מורכבות"),
            ("ד\"ר מיכל אזולאי", "רופאת שיניים כללי", "מומחית לטיפולים מונעים")
        ]
        
        specializations = [
            "רפואת שיניים כללית", "אורתודונטיה", "כירורגיה", "אנדודונטיה", 
            "פריודונטולוגיה", "רפואת שיניים ילדים", "פרוסטודונטיה", 
            "רפואת שיניים אסתטית", "כירורגיית פה ולסת", "רפואה מונעת"
        ]
        
        doctors = []
        
        for i, (name, specialty, description) in enumerate(doctor_names):
            doctor_id = f"D{str(i+1).zfill(3)}"
            
            # Generate realistic schedule
            working_days = random.sample(["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי"], 
                                       random.randint(4, 6))
            
            # Generate patient load (realistic distribution)
            daily_patients = random.randint(15, 35)
            monthly_patients = daily_patients * len(working_days) * 4
            
            doctor = {
                "doctor_id": doctor_id,
                "name": name,
                "specialty": specialty,
                "description": description,
                "specialization": specializations[i],
                "experience_years": random.randint(5, 30),
                "working_days": working_days,
                "daily_capacity": daily_patients,
                "monthly_patients": monthly_patients,
                "rating": round(random.uniform(4.2, 4.9), 1),
                "languages": random.sample(["עברית", "אנגלית", "ערבית", "רוסית"], random.randint(2, 3)),
                "phone": f"03-{random.randint(1000000, 9999999)}",
                "email": f"dr.{name.split()[-1].lower()}@clinic.co.il",
                "room": f"חדר {i+1}",
                "status": "פעיל",
                "next_available": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d")
            }
            
            doctors.append(doctor)
        
        return doctors
    
    def _generate_appointments(self, count: int) -> List[Dict[str, Any]]:
        """Generate realistic appointment data"""
        
        appointments = []
        treatment_types = [
            "בדיקה כללית", "ניקוי אבנית", "סתימה", "עקירה", "טיפול שורש",
            "כתר", "גשר", "השתלה", "יישור שיניים", "הלבנה", "טיפול חניכיים",
            "בדיקת רנטגן", "טיפול דחוף", "ייעוץ", "בדיקת בקרה"
        ]
        
        statuses = ["מתוזמן", "הושלם", "בוטל", "לא הגיע", "דחוי"]
        
        for i in range(count):
            appointment_id = f"A{str(i+1).zfill(4)}"
            patient = random.choice(self.patients)
            doctor = random.choice(self.doctors)
            
            # Generate appointment date (past, present, future)
            days_offset = random.randint(-90, 30)  # 3 months back to 1 month forward
            appointment_date = datetime.now() + timedelta(days=days_offset)
            
            # Generate realistic time slots
            hour = random.choice([8, 9, 10, 11, 13, 14, 15, 16, 17])
            minute = random.choice([0, 15, 30, 45])
            appointment_time = appointment_date.replace(hour=hour, minute=minute)
            
            # Determine status based on date
            if appointment_date < datetime.now():
                status = random.choices(statuses, weights=[0, 70, 15, 10, 5])[0]
            else:
                status = random.choices(statuses, weights=[85, 0, 10, 0, 5])[0]
            
            treatment = random.choice(treatment_types)
            duration = random.choice([30, 45, 60, 90, 120])  # minutes
            
            appointment = {
                "appointment_id": appointment_id,
                "patient_id": patient["patient_id"],
                "patient_name": patient["name"],
                "doctor_id": doctor["doctor_id"],
                "doctor_name": doctor["name"],
                "date": appointment_date.strftime("%Y-%m-%d"),
                "time": appointment_time.strftime("%H:%M"),
                "datetime": appointment_time.strftime("%Y-%m-%d %H:%M"),
                "treatment_type": treatment,
                "duration_minutes": duration,
                "status": status,
                "notes": f"טיפול {treatment} - {duration} דקות",
                "cost": random.randint(200, 2000),
                "room": doctor["room"],
                "created_at": (appointment_time - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M")
            }
            
            appointments.append(appointment)
        
        return appointments
    
    def _generate_treatments(self, count: int) -> List[Dict[str, Any]]:
        """Generate treatment history data"""
        
        treatments = []
        treatment_categories = {
            "מניעה": ["ניקוי אבנית", "פלואור", "איטום חריצים", "הדרכת היגיינה"],
            "שימורי": ["סתימה לבנה", "סתימה כסופה", "כתר", "גשר", "ציפוי"],
            "אנדודונטיה": ["טיפול שורש", "אפקטומיה", "טיפול חוזר"],
            "כירורגיה": ["עקירה פשוטה", "עקירה מורכבת", "השתלה", "ניתוח חניכיים"],
            "אורתודונטיה": ["יישור שיניים", "מכשיר נשלף", "מכשיר קבוע", "שמירת מקום"],
            "אסתטיקה": ["הלבנה", "ציפוי חרסינה", "בונדינג", "עיצוב חיוך"]
        }
        
        for i in range(count):
            treatment_id = f"T{str(i+1).zfill(4)}"
            patient = random.choice(self.patients)
            doctor = random.choice(self.doctors)
            
            category = random.choice(list(treatment_categories.keys()))
            treatment_name = random.choice(treatment_categories[category])
            
            # Generate treatment date (mostly in the past)
            days_ago = random.randint(1, 365)
            treatment_date = datetime.now() - timedelta(days=days_ago)
            
            treatment = {
                "treatment_id": treatment_id,
                "patient_id": patient["patient_id"],
                "patient_name": patient["name"],
                "doctor_id": doctor["doctor_id"],
                "doctor_name": doctor["name"],
                "date": treatment_date.strftime("%Y-%m-%d"),
                "category": category,
                "treatment_name": treatment_name,
                "tooth_number": random.choice([None, random.randint(11, 48)]),
                "cost": random.randint(150, 3000),
                "duration_minutes": random.randint(30, 180),
                "status": random.choices(["הושלם", "בתהליך", "מתוכנן"], weights=[80, 15, 5])[0],
                "notes": f"טיפול {treatment_name} בוצע בהצלחה",
                "follow_up_needed": random.choice([True, False]),
                "follow_up_date": (treatment_date + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
            }
            
            treatments.append(treatment)
        
        return treatments
    
    def search_patients(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search patients by name, phone, or ID"""
        query = query.lower().strip()
        results = []
        
        for patient in self.patients:
            if (query in patient["name"].lower() or 
                query in patient["phone"] or 
                query in patient["patient_id"].lower() or
                query in patient["email"].lower()):
                results.append(patient)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by ID"""
        for patient in self.patients:
            if patient["patient_id"] == patient_id:
                return patient
        return None
    
    def get_doctor_by_id(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        """Get doctor by ID"""
        for doctor in self.doctors:
            if doctor["doctor_id"] == doctor_id:
                return doctor
        return None
    
    def get_appointments_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get appointments for a specific date"""
        return [apt for apt in self.appointments if apt["date"] == date]
    
    def get_patient_appointments(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all appointments for a patient"""
        return [apt for apt in self.appointments if apt["patient_id"] == patient_id]
    
    def get_doctor_schedule(self, doctor_id: str, date: str) -> List[Dict[str, Any]]:
        """Get doctor's schedule for a specific date"""
        return [apt for apt in self.appointments 
                if apt["doctor_id"] == doctor_id and apt["date"] == date]
    
    def get_available_slots(self, doctor_id: str, date: str) -> List[str]:
        """Get available time slots for a doctor on a specific date"""
        doctor = self.get_doctor_by_id(doctor_id)
        if not doctor:
            return []
        
        # Generate all possible slots
        all_slots = []
        for hour in range(8, 18):  # 8 AM to 6 PM
            for minute in [0, 15, 30, 45]:
                all_slots.append(f"{hour:02d}:{minute:02d}")
        
        # Get booked slots
        booked_appointments = self.get_doctor_schedule(doctor_id, date)
        booked_slots = [apt["time"] for apt in booked_appointments]
        
        # Return available slots
        return [slot for slot in all_slots if slot not in booked_slots]
    
    def book_appointment(self, patient_id: str, doctor_id: str, date: str, time: str, treatment_type: str) -> Dict[str, Any]:
        """Book a new appointment"""
        appointment_id = f"A{len(self.appointments) + 1:04d}"
        patient = self.get_patient_by_id(patient_id)
        doctor = self.get_doctor_by_id(doctor_id)
        
        if not patient or not doctor:
            return {"success": False, "error": "Patient or doctor not found"}
        
        # Check if slot is available
        available_slots = self.get_available_slots(doctor_id, date)
        if time not in available_slots:
            return {"success": False, "error": "Time slot not available"}
        
        appointment = {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "patient_name": patient["name"],
            "doctor_id": doctor_id,
            "doctor_name": doctor["name"],
            "date": date,
            "time": time,
            "datetime": f"{date} {time}",
            "treatment_type": treatment_type,
            "duration_minutes": 60,
            "status": "מתוזמן",
            "notes": f"תור חדש - {treatment_type}",
            "cost": random.randint(200, 1000),
            "room": doctor["room"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.appointments.append(appointment)
        return {"success": True, "appointment": appointment}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Today's appointments
        today_appointments = self.get_appointments_by_date(today)
        
        # Active patients (visited in last 6 months)
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        active_patients = [p for p in self.patients if p["last_visit"] >= six_months_ago]
        
        # Treatment statistics
        completed_treatments = [t for t in self.treatments if t["status"] == "הושלם"]
        
        return {
            "total_patients": len(self.patients),
            "active_patients": len(active_patients),
            "total_doctors": len(self.doctors),
            "total_appointments": len(self.appointments),
            "today_appointments": len(today_appointments),
            "completed_treatments": len(completed_treatments),
            "average_daily_appointments": len(self.appointments) // 90,  # Assuming 3 months of data
            "patient_satisfaction": round(random.uniform(4.3, 4.8), 1),
            "system_load": f"{random.randint(15, 35)}%",
            "database_size": f"{len(self.patients) + len(self.doctors) + len(self.appointments) + len(self.treatments)} records"
        }

# Global instance
large_scale_mock_tool = LargeScaleMockTool()

def get_large_scale_mock_tool():
    """Get the global large scale mock tool instance"""
    return large_scale_mock_tool
