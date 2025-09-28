"""
Data Simulator Agent - External AI Agent for Clinic Simulation
Manages realistic patient interactions and clinic scenarios using OpenAI API
"""

import os
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import openai
from openai import AsyncOpenAI

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PatientType(Enum):
    ANXIOUS = "anxious"
    URGENT = "urgent"
    CONFUSED = "confused"
    EXPERIENCED = "experienced"
    ELDERLY = "elderly"
    YOUNG_PARENT = "young_parent"
    BUSINESS_PERSON = "business_person"
    STUDENT = "student"

class CallType(Enum):
    NEW_APPOINTMENT = "new_appointment"
    RESCHEDULE = "reschedule"
    CANCEL = "cancel"
    EMERGENCY = "emergency"
    INQUIRY = "inquiry"
    COMPLAINT = "complaint"
    FOLLOW_UP = "follow_up"

@dataclass
class VirtualPatient:
    """Virtual patient with AI-generated personality and needs"""
    id: str
    name: str
    age: int
    patient_type: PatientType
    background: str
    current_need: str
    urgency_level: int  # 1-10
    communication_style: str
    medical_history: List[str]
    preferred_times: List[str]
    insurance_info: Dict[str, str]
    
class DataSimulatorAgent:
    """AI-powered data simulator for realistic clinic interactions"""
    
    def __init__(self):
        self.is_running = False
        self.simulation_speed = 1.0  # 1.0 = normal speed
        self.active_scenarios = []
        self.patient_database = []
        self.interaction_history = []
        self.performance_metrics = {
            "total_calls": 0,
            "successful_bookings": 0,
            "patient_satisfaction": 0.0,
            "average_call_duration": 0.0,
            "peak_hours": {},
            "common_issues": {}
        }
        
    async def initialize_patient_database(self, count: int = 50):
        """Generate a database of virtual patients using AI"""
        print(f"🤖 Generating {count} virtual patients...")
        
        for i in range(count):
            patient = await self._generate_virtual_patient(f"patient_{i+1}")
            self.patient_database.append(patient)
            
        print(f"✅ Generated {len(self.patient_database)} virtual patients")
        
    async def _generate_virtual_patient(self, patient_id: str) -> VirtualPatient:
        """Generate a realistic virtual patient using OpenAI"""
        
        patient_type = random.choice(list(PatientType))
        
        prompt = f"""
        Create a realistic virtual patient for a dental clinic simulation with the following characteristics:
        - Patient Type: {patient_type.value}
        - Generate a Hebrew name, age, and background
        - Create realistic medical history and current dental needs
        - Define communication style and preferences
        
        Return ONLY a JSON object with these exact fields:
        {{
            "name": "Hebrew name",
            "age": number,
            "background": "brief background in Hebrew",
            "current_need": "current dental need in Hebrew",
            "urgency_level": number 1-10,
            "communication_style": "communication style in Hebrew",
            "medical_history": ["list of medical history items in Hebrew"],
            "preferred_times": ["list of preferred appointment times"],
            "insurance_info": {{"provider": "insurance provider", "policy": "policy number"}}
        }}
        """
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=500
            )
            
            patient_data = json.loads(response.choices[0].message.content)
            
            return VirtualPatient(
                id=patient_id,
                patient_type=patient_type,
                **patient_data
            )
            
        except Exception as e:
            print(f"Error generating patient: {e}")
            # Fallback to default patient
            return self._create_default_patient(patient_id, patient_type)
    
    def _create_default_patient(self, patient_id: str, patient_type: PatientType) -> VirtualPatient:
        """Create a default patient if AI generation fails"""
        names = ["דוד כהן", "שרה לוי", "משה אברהם", "רחל ישראלי", "יוסף דוד"]
        
        return VirtualPatient(
            id=patient_id,
            name=random.choice(names),
            age=random.randint(18, 80),
            patient_type=patient_type,
            background="מטופל רגיל במרפאה",
            current_need="בדיקת שיניים שגרתיית",
            urgency_level=random.randint(1, 5),
            communication_style="ידידותי ושיתופי",
            medical_history=["בריא"],
            preferred_times=["בוקר", "אחר הצהריים"],
            insurance_info={"provider": "כללית", "policy": "123456789"}
        )
    
    async def generate_realistic_call(self) -> Dict[str, Any]:
        """Generate a realistic phone call scenario"""
        
        if not self.patient_database:
            await self.initialize_patient_database(20)
        
        # Select random patient and call type
        patient = random.choice(self.patient_database)
        call_type = random.choice(list(CallType))
        
        # Generate call scenario using AI
        scenario = await self._generate_call_scenario(patient, call_type)
        
        # Create call data
        call_data = {
            "id": f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "patient": asdict(patient),
            "call_type": call_type.value,
            "scenario": scenario,
            "status": "incoming",
            "duration": 0,
            "outcome": None
        }
        
        return call_data
    
    async def _generate_call_scenario(self, patient: VirtualPatient, call_type: CallType) -> Dict[str, Any]:
        """Generate a realistic call scenario using AI"""
        
        prompt = f"""
        Create a realistic phone call scenario for a dental clinic:
        
        Patient: {patient.name}, Age: {patient.age}
        Patient Type: {patient.patient_type.value}
        Background: {patient.background}
        Current Need: {patient.current_need}
        Communication Style: {patient.communication_style}
        Call Type: {call_type.value}
        Urgency: {patient.urgency_level}/10
        
        Generate a realistic conversation scenario in Hebrew including:
        1. Patient's opening statement
        2. Likely questions they'll ask
        3. Potential complications or special requests
        4. Expected outcome
        
        Return ONLY a JSON object:
        {{
            "opening_statement": "what patient says when calling",
            "key_questions": ["list of questions patient might ask"],
            "special_requests": ["any special requests or complications"],
            "expected_outcome": "likely result of the call",
            "estimated_duration": number in minutes,
            "difficulty_level": number 1-10
        }}
        """
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating scenario: {e}")
            return {
                "opening_statement": f"שלום, אני {patient.name}, אני רוצה לקבוע תור",
                "key_questions": ["מתי יש מקום?", "כמה זה עולה?"],
                "special_requests": [],
                "expected_outcome": "קביעת תור",
                "estimated_duration": 3,
                "difficulty_level": 3
            }
    
    async def simulate_patient_agent_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a full conversation between patient AI and clinic AI"""
        
        patient = call_data["patient"]
        scenario = call_data["scenario"]
        
        # Create patient AI persona
        patient_prompt = f"""
        You are {patient['name']}, a {patient['age']}-year-old patient calling a dental clinic.
        
        Your characteristics:
        - Type: {patient['patient_type']}
        - Background: {patient['background']}
        - Current need: {patient['current_need']}
        - Communication style: {patient['communication_style']}
        - Urgency level: {patient['urgency_level']}/10
        
        Scenario: {scenario['opening_statement']}
        
        Behave naturally as this patient would. Respond in Hebrew.
        Ask relevant questions and express concerns appropriate to your character.
        """
        
        # Create clinic AI persona
        clinic_prompt = """
        You are a professional dental clinic receptionist AI.
        You are helpful, efficient, and knowledgeable about dental services.
        
        Your tasks:
        - Schedule appointments
        - Answer questions about treatments
        - Handle insurance inquiries
        - Provide excellent customer service
        
        Respond professionally in Hebrew.
        """
        
        # Simulate conversation
        conversation = []
        conversation_rounds = random.randint(3, 8)
        
        # Patient starts the call
        patient_message = scenario["opening_statement"]
        conversation.append({"speaker": "patient", "message": patient_message})
        
        for round_num in range(conversation_rounds):
            try:
                # Clinic AI responds
                clinic_response = await self._get_ai_response(
                    clinic_prompt,
                    conversation,
                    "clinic_agent"
                )
                conversation.append({"speaker": "clinic", "message": clinic_response})
                
                # Patient AI responds (if not last round)
                if round_num < conversation_rounds - 1:
                    patient_response = await self._get_ai_response(
                        patient_prompt,
                        conversation,
                        "patient_agent"
                    )
                    conversation.append({"speaker": "patient", "message": patient_response})
                    
            except Exception as e:
                print(f"Error in conversation round {round_num}: {e}")
                break
        
        # Analyze conversation outcome
        outcome = await self._analyze_conversation_outcome(conversation, scenario)
        
        # Update call data
        call_data.update({
            "conversation": conversation,
            "outcome": outcome,
            "duration": len(conversation) * 0.5,  # Estimate duration
            "status": "completed"
        })
        
        return call_data
    
    async def _get_ai_response(self, system_prompt: str, conversation: List[Dict], agent_type: str) -> str:
        """Get AI response for either patient or clinic agent"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for turn in conversation[-6:]:  # Last 6 messages for context
            role = "user" if turn["speaker"] != agent_type.split("_")[0] else "assistant"
            messages.append({"role": role, "content": turn["message"]})
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return "מצטער, יש לי בעיה טכנית. אוכל לעזור לך במשהו אחר?"
    
    async def _analyze_conversation_outcome(self, conversation: List[Dict], scenario: Dict) -> Dict[str, Any]:
        """Analyze the conversation outcome using AI"""
        
        conversation_text = "\n".join([f"{turn['speaker']}: {turn['message']}" for turn in conversation])
        
        prompt = f"""
        Analyze this dental clinic phone conversation and determine the outcome:
        
        Expected outcome: {scenario['expected_outcome']}
        
        Conversation:
        {conversation_text}
        
        Return ONLY a JSON object:
        {{
            "successful": true/false,
            "outcome_type": "appointment_booked/rescheduled/cancelled/inquiry_answered/complaint_resolved",
            "patient_satisfaction": number 1-10,
            "issues_resolved": ["list of issues that were resolved"],
            "follow_up_needed": true/false,
            "notes": "brief summary in Hebrew"
        }}
        """
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error analyzing outcome: {e}")
            return {
                "successful": True,
                "outcome_type": "inquiry_answered",
                "patient_satisfaction": 7,
                "issues_resolved": ["בירור כללי"],
                "follow_up_needed": False,
                "notes": "שיחה הושלמה בהצלחה"
            }
    
    async def start_simulation(self, calls_per_hour: int = 12):
        """Start the continuous simulation"""
        self.is_running = True
        print(f"🚀 Starting Data Simulator Agent - {calls_per_hour} calls/hour")
        
        if not self.patient_database:
            await self.initialize_patient_database()
        
        call_interval = 3600 / calls_per_hour  # seconds between calls
        
        while self.is_running:
            try:
                # Generate and process a call
                call_data = await self.generate_realistic_call()
                print(f"📞 Incoming call: {call_data['patient']['name']} - {call_data['call_type']}")
                
                # Simulate the full conversation
                completed_call = await self.simulate_patient_agent_call(call_data)
                
                # Store interaction
                self.interaction_history.append(completed_call)
                
                # Update metrics
                self._update_performance_metrics(completed_call)
                
                # Broadcast to WebSocket (if connected)
                await self._broadcast_call_update(completed_call)
                
                print(f"✅ Call completed: {completed_call['outcome']['outcome_type']}")
                
                # Wait for next call
                await asyncio.sleep(call_interval / self.simulation_speed)
                
            except Exception as e:
                print(f"Error in simulation loop: {e}")
                await asyncio.sleep(10)
    
    def _update_performance_metrics(self, call_data: Dict[str, Any]):
        """Update performance metrics based on completed call"""
        self.performance_metrics["total_calls"] += 1
        
        if call_data["outcome"]["successful"]:
            self.performance_metrics["successful_bookings"] += 1
        
        # Update satisfaction average
        satisfaction = call_data["outcome"]["patient_satisfaction"]
        total_calls = self.performance_metrics["total_calls"]
        current_avg = self.performance_metrics["patient_satisfaction"]
        
        self.performance_metrics["patient_satisfaction"] = (
            (current_avg * (total_calls - 1) + satisfaction) / total_calls
        )
        
        # Update average call duration
        duration = call_data["duration"]
        current_avg_duration = self.performance_metrics["average_call_duration"]
        
        self.performance_metrics["average_call_duration"] = (
            (current_avg_duration * (total_calls - 1) + duration) / total_calls
        )
    
    async def _broadcast_call_update(self, call_data: Dict[str, Any]):
        """Broadcast call update to WebSocket clients"""
        # This would integrate with the main WebSocket manager
        activity_data = {
            "id": call_data["id"],
            "agent_id": "clinic_agent",
            "type": "phone_call",
            "status": "completed" if call_data["outcome"]["successful"] else "failed",
            "title": f"שיחה עם {call_data['patient']['name']}",
            "description": call_data["outcome"]["notes"],
            "timestamp": call_data["timestamp"],
            "duration": call_data["duration"],
            "metadata": {
                "call_type": call_data["call_type"],
                "patient_satisfaction": call_data["outcome"]["patient_satisfaction"],
                "outcome_type": call_data["outcome"]["outcome_type"]
            }
        }
        
        # Here we would send to the main WebSocket manager
        print(f"📡 Broadcasting: {activity_data['title']}")
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        print("🛑 Data Simulator Agent stopped")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "metrics": self.performance_metrics,
            "recent_calls": self.interaction_history[-10:],
            "patient_count": len(self.patient_database),
            "simulation_status": "running" if self.is_running else "stopped"
        }
    
    def set_simulation_speed(self, speed: float):
        """Set simulation speed (1.0 = normal, 2.0 = 2x faster, 0.5 = half speed)"""
        self.simulation_speed = max(0.1, min(10.0, speed))
        print(f"⚡ Simulation speed set to {self.simulation_speed}x")

# Example usage and testing
async def main():
    """Test the Data Simulator Agent"""
    simulator = DataSimulatorAgent()
    
    print("🧪 Testing Data Simulator Agent...")
    
    # Generate a single call for testing
    call_data = await simulator.generate_realistic_call()
    print(f"Generated call: {call_data['patient']['name']}")
    
    # Simulate the conversation
    completed_call = await simulator.simulate_patient_agent_call(call_data)
    print(f"Conversation completed: {completed_call['outcome']['outcome_type']}")
    
    # Print conversation
    print("\n📞 Conversation:")
    for turn in completed_call['conversation']:
        speaker = "🧑‍⚕️" if turn['speaker'] == 'clinic' else "👤"
        print(f"{speaker} {turn['speaker']}: {turn['message']}")
    
    print(f"\n📊 Outcome: {completed_call['outcome']}")

if __name__ == "__main__":
    asyncio.run(main())
