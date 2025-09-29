#!/usr/bin/env python3
"""
Busy Day Simulation Engine for Dental Clinic AI System
Simulates a realistic busy day with 1500 patients and 10 doctors
"""

import asyncio
import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

from tools.large_scale_mock_tool import get_large_scale_mock_tool

class BusyDaySimulator:
    """Simulates a busy day in a large dental clinic"""
    
    def __init__(self):
        self.mock_tool = get_large_scale_mock_tool()
        self.simulation_active = False
        self.simulation_stats = {
            "start_time": None,
            "total_interactions": 0,
            "successful_bookings": 0,
            "failed_bookings": 0,
            "emergency_calls": 0,
            "cancellations": 0,
            "confirmations": 0,
            "inquiries": 0,
            "avg_response_time": 0,
            "peak_concurrent_users": 0,
            "current_concurrent_users": 0,
            "system_load": 0,
            "errors": 0
        }
        self.active_sessions = {}
        self.interaction_log = []
        
    def generate_realistic_scenarios(self) -> List[Dict[str, Any]]:
        """Generate realistic patient interaction scenarios for a busy day"""
        
        scenarios = [
            # Morning rush (8:00-10:00) - Appointment bookings
            {
                "type": "appointment_booking",
                "priority": "normal",
                "message_templates": [
                    "שלום, אני רוצה לקבוע תור לבדיקה כללית",
                    "היי, אפשר תור לניקוי אבנית השבוע?",
                    "בוקר טוב, צריך תור דחוף לכאב שן",
                    "Hello, I need an appointment for teeth cleaning",
                    "אני צריכה תור לילד שלי לבדיקה"
                ],
                "expected_response_time": 1.2,
                "success_rate": 0.85,
                "weight": 30
            },
            
            # Emergency calls (throughout the day)
            {
                "type": "emergency",
                "priority": "high",
                "message_templates": [
                    "יש לי כאב שן נורא! צריך תור דחוף היום!",
                    "נשברה לי שן, מה לעשות?",
                    "כאב חזק בלסת, אי אפשר לסבול",
                    "Emergency! Severe tooth pain!",
                    "ילד שלי נפל ונשברה לו שן"
                ],
                "expected_response_time": 0.5,
                "success_rate": 0.95,
                "weight": 15
            },
            
            # Appointment confirmations
            {
                "type": "confirmation",
                "priority": "normal",
                "message_templates": [
                    "אני מאשר את התור מחר ב-14:00",
                    "כן, אגיע לתור ביום רביעי",
                    "התור בסדר, אהיה שם",
                    "Confirming my appointment tomorrow",
                    "אישור תור לילדה שלי"
                ],
                "expected_response_time": 0.8,
                "success_rate": 0.98,
                "weight": 20
            },
            
            # Cancellations and rescheduling
            {
                "type": "cancellation",
                "priority": "normal",
                "message_templates": [
                    "צריך לבטל את התור מחר",
                    "אי אפשר להגיע, אפשר לדחות?",
                    "רוצה לשנות את התור לשבוע הבא",
                    "Need to cancel my appointment",
                    "משהו דחוף קרה, צריך לדחות"
                ],
                "expected_response_time": 1.0,
                "success_rate": 0.92,
                "weight": 12
            },
            
            # General inquiries
            {
                "type": "inquiry",
                "priority": "low",
                "message_templates": [
                    "כמה עולה ניקוי אבנית?",
                    "איזה רופאים יש אצלכם?",
                    "מה השעות של המרפאה?",
                    "What are your prices for teeth whitening?",
                    "יש לכם חניה?"
                ],
                "expected_response_time": 1.5,
                "success_rate": 0.88,
                "weight": 15
            },
            
            # Follow-up calls
            {
                "type": "follow_up",
                "priority": "normal",
                "message_templates": [
                    "איך אני מרגיש אחרי הטיפול אתמול?",
                    "יש לי שאלה על התרופה שקיבלתי",
                    "מתי לחזור לבדיקת המשך?",
                    "Follow-up question about my treatment",
                    "הכאב לא עובר, מה לעשות?"
                ],
                "expected_response_time": 1.3,
                "success_rate": 0.90,
                "weight": 8
            }
        ]
        
        return scenarios
    
    def simulate_patient_interaction(self, scenario: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """Simulate a single patient interaction"""
        
        start_time = time.time()
        session_id = f"session_{int(start_time)}_{random.randint(1000, 9999)}"
        
        # Add to active sessions
        self.active_sessions[session_id] = {
            "patient_id": patient_id,
            "scenario_type": scenario["type"],
            "start_time": start_time,
            "status": "processing"
        }
        
        # Update concurrent users
        self.simulation_stats["current_concurrent_users"] = len(self.active_sessions)
        if self.simulation_stats["current_concurrent_users"] > self.simulation_stats["peak_concurrent_users"]:
            self.simulation_stats["peak_concurrent_users"] = self.simulation_stats["current_concurrent_users"]
        
        try:
            # Get patient data
            patient = self.mock_tool.get_patient_by_id(patient_id)
            if not patient:
                patient = random.choice(self.mock_tool.patients)
            
            # Select message template
            message = random.choice(scenario["message_templates"])
            
            # Simulate AI processing time
            processing_time = random.uniform(
                scenario["expected_response_time"] * 0.7,
                scenario["expected_response_time"] * 1.3
            )
            time.sleep(processing_time)
            
            # Determine success based on scenario success rate
            success = random.random() < scenario["success_rate"]
            
            # Generate response based on scenario type
            response = self._generate_ai_response(scenario["type"], patient, success)
            
            # Update statistics
            self.simulation_stats["total_interactions"] += 1
            
            if scenario["type"] == "appointment_booking":
                if success:
                    self.simulation_stats["successful_bookings"] += 1
                else:
                    self.simulation_stats["failed_bookings"] += 1
            elif scenario["type"] == "emergency":
                self.simulation_stats["emergency_calls"] += 1
            elif scenario["type"] == "cancellation":
                self.simulation_stats["cancellations"] += 1
            elif scenario["type"] == "confirmation":
                self.simulation_stats["confirmations"] += 1
            elif scenario["type"] == "inquiry":
                self.simulation_stats["inquiries"] += 1
            
            # Calculate response time
            total_time = time.time() - start_time
            current_avg = self.simulation_stats["avg_response_time"]
            total_interactions = self.simulation_stats["total_interactions"]
            self.simulation_stats["avg_response_time"] = (
                (current_avg * (total_interactions - 1) + total_time) / total_interactions
            )
            
            # Log interaction
            interaction_log = {
                "session_id": session_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "patient_id": patient["patient_id"],
                "patient_name": patient["name"],
                "scenario_type": scenario["type"],
                "priority": scenario["priority"],
                "message": message,
                "response": response,
                "processing_time": round(total_time, 2),
                "success": success,
                "language": patient.get("preferred_language", "עברית")
            }
            
            self.interaction_log.append(interaction_log)
            
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            self.simulation_stats["current_concurrent_users"] = len(self.active_sessions)
            
            return interaction_log
            
        except Exception as e:
            self.simulation_stats["errors"] += 1
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            return {
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _generate_ai_response(self, scenario_type: str, patient: Dict[str, Any], success: bool) -> str:
        """Generate realistic AI responses"""
        
        patient_name = patient["name"].split()[0]  # First name
        
        if scenario_type == "appointment_booking":
            if success:
                return f"שלום {patient_name}! מצאתי לך תור פנוי ביום רביעי ב-14:30 אצל ד\"ר כהן. האם זה מתאים לך?"
            else:
                return f"שלום {patient_name}, מצטער אבל אין תורים פנויים השבוע. האם שבוע הבא מתאים?"
        
        elif scenario_type == "emergency":
            return f"שלום {patient_name}, אני מבין שיש לך כאב חזק. אני מזמין לך תור דחוף היום ב-16:00. בינתיים, קח משכך כאבים."
        
        elif scenario_type == "confirmation":
            return f"תודה {patient_name}! התור שלך מאושר למחר ב-14:00 אצל ד\"ר לוי. נשלח לך תזכורת SMS."
        
        elif scenario_type == "cancellation":
            if success:
                return f"בסדר {patient_name}, ביטלתי את התור. האם תרצה לקבוע תור חדש לתאריך אחר?"
            else:
                return f"שלום {patient_name}, התור כבר לא ניתן לביטול. אנא התקשר למרפאה."
        
        elif scenario_type == "inquiry":
            return f"שלום {patient_name}! ניקוי אבנית עולה 280 ש\"ח. יש לנו 10 רופאים מומחים. השעות: א'-ה' 8:00-18:00."
        
        elif scenario_type == "follow_up":
            return f"שלום {patient_name}, שמח לשמוע שהטיפול עבר בהצלחה. אם יש כאב קל זה נורמלי. תחזור לבדיקה בעוד שבוע."
        
        return "תודה על פנייתך, נחזור אליך בהקדם."
    
    def simulate_busy_day(self, duration_minutes: int = 60, concurrent_users: int = 50, speed_multiplier: float = 10.0):
        """Simulate a busy day with multiple concurrent users"""
        
        print(f"🚀 Starting busy day simulation...")
        print(f"📊 Parameters: {duration_minutes} minutes, {concurrent_users} concurrent users, {speed_multiplier}x speed")
        
        self.simulation_active = True
        self.simulation_stats["start_time"] = datetime.now()
        
        scenarios = self.generate_realistic_scenarios()
        
        # Calculate interaction frequency
        interactions_per_minute = concurrent_users * speed_multiplier / 2  # Realistic frequency
        interaction_interval = 60.0 / interactions_per_minute  # Seconds between interactions
        
        print(f"⚡ Generating {interactions_per_minute:.1f} interactions per minute")
        print(f"🎯 Target: {duration_minutes * interactions_per_minute:.0f} total interactions")
        print("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60 / speed_multiplier)  # Adjusted for speed
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            while time.time() < end_time and self.simulation_active:
                # Select scenario based on weights
                scenario = random.choices(
                    scenarios,
                    weights=[s["weight"] for s in scenarios]
                )[0]
                
                # Select random patient
                patient_id = random.choice(self.mock_tool.patients)["patient_id"]
                
                # Submit interaction to thread pool
                future = executor.submit(self.simulate_patient_interaction, scenario, patient_id)
                futures.append(future)
                
                # Print real-time stats every 10 interactions
                if self.simulation_stats["total_interactions"] % 10 == 0:
                    self._print_realtime_stats()
                
                # Wait for next interaction
                time.sleep(interaction_interval / speed_multiplier)
            
            # Wait for all interactions to complete
            print("\n⏳ Waiting for all interactions to complete...")
            for future in futures:
                try:
                    future.result(timeout=30)
                except Exception as e:
                    print(f"❌ Interaction error: {e}")
        
        self.simulation_active = False
        
        # Final statistics
        print("\n" + "=" * 60)
        print("🎉 BUSY DAY SIMULATION COMPLETED!")
        self._print_final_stats()
        
        return self.get_simulation_summary()
    
    def _print_realtime_stats(self):
        """Print real-time simulation statistics"""
        stats = self.simulation_stats
        elapsed = (datetime.now() - stats["start_time"]).total_seconds()
        
        print(f"⏱️  {elapsed:.0f}s | "
              f"📞 {stats['total_interactions']} interactions | "
              f"👥 {stats['current_concurrent_users']} active | "
              f"⚡ {stats['avg_response_time']:.2f}s avg | "
              f"✅ {stats['successful_bookings']} bookings | "
              f"🚨 {stats['emergency_calls']} emergencies")
    
    def _print_final_stats(self):
        """Print final simulation statistics"""
        stats = self.simulation_stats
        elapsed = (datetime.now() - stats["start_time"]).total_seconds()
        
        print(f"📊 FINAL STATISTICS:")
        print(f"   ⏱️  Total Duration: {elapsed:.1f} seconds")
        print(f"   📞 Total Interactions: {stats['total_interactions']}")
        print(f"   👥 Peak Concurrent Users: {stats['peak_concurrent_users']}")
        print(f"   ⚡ Average Response Time: {stats['avg_response_time']:.2f} seconds")
        print(f"   ✅ Successful Bookings: {stats['successful_bookings']}")
        print(f"   ❌ Failed Bookings: {stats['failed_bookings']}")
        print(f"   🚨 Emergency Calls: {stats['emergency_calls']}")
        print(f"   📅 Confirmations: {stats['confirmations']}")
        print(f"   ❌ Cancellations: {stats['cancellations']}")
        print(f"   ❓ Inquiries: {stats['inquiries']}")
        print(f"   🐛 Errors: {stats['errors']}")
        
        # Calculate success rate
        total_bookings = stats['successful_bookings'] + stats['failed_bookings']
        if total_bookings > 0:
            success_rate = (stats['successful_bookings'] / total_bookings) * 100
            print(f"   📈 Booking Success Rate: {success_rate:.1f}%")
        
        # Calculate throughput
        throughput = stats['total_interactions'] / (elapsed / 60)
        print(f"   🚀 Throughput: {throughput:.1f} interactions/minute")
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get comprehensive simulation summary"""
        stats = self.simulation_stats
        
        if stats["start_time"]:
            elapsed = (datetime.now() - stats["start_time"]).total_seconds()
        else:
            elapsed = 0
        
        # Calculate derived metrics
        total_bookings = stats['successful_bookings'] + stats['failed_bookings']
        success_rate = (stats['successful_bookings'] / total_bookings * 100) if total_bookings > 0 else 0
        throughput = stats['total_interactions'] / (elapsed / 60) if elapsed > 0 else 0
        
        # Get system stats
        system_stats = self.mock_tool.get_system_stats()
        
        return {
            "simulation_summary": {
                "duration_seconds": round(elapsed, 1),
                "total_interactions": stats['total_interactions'],
                "peak_concurrent_users": stats['peak_concurrent_users'],
                "average_response_time": round(stats['avg_response_time'], 2),
                "throughput_per_minute": round(throughput, 1),
                "success_rate_percentage": round(success_rate, 1),
                "errors": stats['errors']
            },
            "interaction_breakdown": {
                "successful_bookings": stats['successful_bookings'],
                "failed_bookings": stats['failed_bookings'],
                "emergency_calls": stats['emergency_calls'],
                "confirmations": stats['confirmations'],
                "cancellations": stats['cancellations'],
                "inquiries": stats['inquiries']
            },
            "system_performance": {
                "total_patients": system_stats['total_patients'],
                "active_patients": system_stats['active_patients'],
                "total_doctors": system_stats['total_doctors'],
                "today_appointments": system_stats['today_appointments'],
                "system_load": system_stats['system_load'],
                "database_size": system_stats['database_size']
            },
            "recent_interactions": self.interaction_log[-10:] if self.interaction_log else []
        }
    
    def stop_simulation(self):
        """Stop the current simulation"""
        self.simulation_active = False
        print("🛑 Simulation stopped by user")

# Global instance
busy_day_simulator = BusyDaySimulator()

def get_busy_day_simulator():
    """Get the global busy day simulator instance"""
    return busy_day_simulator
