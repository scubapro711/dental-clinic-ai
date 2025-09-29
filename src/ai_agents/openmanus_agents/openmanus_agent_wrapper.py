"""
OpenManus Agent Wrapper
עטיפת סוכן OpenManus
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..interfaces.ai_agent_interface import AIAgentInterface
from ..tools.advanced_dental_tool import AdvancedDentalTool
from ..tools.mock_dental_tool import MockDentalTool

logger = logging.getLogger(__name__)

class OpenManusAgentWrapper(AIAgentInterface):
    """Wrapper for OpenManus agents that implements the standard AI agent interface"""
    
    def __init__(self, agent_config: Dict[str, Any], engine_config: Dict[str, Any]):
        self.agent_config = agent_config
        self.engine_config = engine_config
        self.agent_name = agent_config.get("name", "default_agent")
        self.role = agent_config.get("role", "AI Assistant")
        self.goal = agent_config.get("goal", "Help users with their requests")
        self.backstory = agent_config.get("backstory", "You are a helpful AI assistant")
        
        # OpenManus specific configuration
        self.system_prompt = self._build_system_prompt()
        self.max_steps = agent_config.get("max_steps", 10)
        self.temperature = agent_config.get("temperature", 0.1)
        
        # Use mock tool for testing, real tool for production
        use_mock = engine_config.get("use_mock_tools", True)
        if use_mock:
            self.dental_tool = MockDentalTool()
        else:
            self.dental_tool = AdvancedDentalTool()
        
        self.initialized = False
        
        logger.info(f"🤖 OpenManus agent '{self.agent_name}' created with role: {self.role}")
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for OpenManus agent"""
        base_prompt = f"""
You are {self.role} for a dental clinic management system.

ROLE: {self.role}
GOAL: {self.goal}
BACKSTORY: {self.backstory}

CAPABILITIES:
- Process patient inquiries in Hebrew and English
- Schedule and manage appointments
- Access patient information and treatment history
- Provide dental information and guidance
- Handle confirmations and cancellations

INSTRUCTIONS:
- Always respond professionally and empathetically
- Use Hebrew when the patient writes in Hebrew
- Be concise but thorough in your responses
- If you need to perform actions (like booking appointments), use the available tools
- Always confirm important actions with the patient

DENTAL CLINIC CONTEXT:
- This is a professional dental clinic
- Maintain patient privacy and confidentiality
- Follow medical ethics and guidelines
- Provide accurate information about treatments and procedures
"""
        return base_prompt
    
    async def initialize(self) -> None:
        """Initialize the OpenManus agent"""
        try:
            await self.dental_tool.initialize()
            self.initialized = True
            logger.info(f"✅ OpenManus agent '{self.agent_name}' initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenManus agent '{self.agent_name}': {e}")
            raise
    
    async def process_message(self, text: str, sender_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message using OpenManus advanced capabilities"""
        try:
            if not self.initialized:
                raise RuntimeError("Agent not initialized")
            
            logger.info(f"🔄 Processing message with OpenManus agent '{self.agent_name}'")
            
            # Analyze intent using OpenManus capabilities
            intent = await self._analyze_intent_advanced(text)
            
            # Route to specialized handler based on agent type and intent
            if self.agent_name == "receptionist":
                return await self._handle_receptionist_task(text, sender_id, context, intent)
            elif self.agent_name == "scheduler":
                return await self._handle_scheduler_task(text, sender_id, context, intent)
            elif self.agent_name == "confirmation":
                return await self._handle_confirmation_task(text, sender_id, context, intent)
            else:
                return await self._handle_general_task(text, sender_id, context, intent)
                
        except Exception as e:
            logger.error(f"Error processing message in OpenManus agent '{self.agent_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "engine": "openmanus",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_intent_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced intent analysis using OpenManus capabilities"""
        text_lower = text.lower()
        
        # Enhanced intent detection with confidence scores
        intents = {
            "appointment_scheduling": 0.0,
            "appointment_confirmation": 0.0,
            "patient_inquiry": 0.0,
            "emergency": 0.0,
            "general_inquiry": 0.0
        }
        
        # Appointment scheduling keywords
        scheduling_keywords = ["appointment", "schedule", "book", "תור", "לקבוע", "זמן פנוי", "מתי אפשר"]
        for keyword in scheduling_keywords:
            if keyword in text_lower:
                intents["appointment_scheduling"] += 0.3
        
        # Confirmation keywords
        confirmation_keywords = ["confirm", "reminder", "אישור", "תזכורת", "לאשר", "ביטול", "cancel"]
        for keyword in confirmation_keywords:
            if keyword in text_lower:
                intents["appointment_confirmation"] += 0.3
        
        # Emergency keywords
        emergency_keywords = ["emergency", "urgent", "pain", "חירום", "כאב", "דחוף", "מיידי"]
        for keyword in emergency_keywords:
            if keyword in text_lower:
                intents["emergency"] += 0.5
        
        # Patient inquiry keywords
        inquiry_keywords = ["treatment", "cost", "price", "טיפול", "מחיר", "עלות", "ביטוח"]
        for keyword in inquiry_keywords:
            if keyword in text_lower:
                intents["patient_inquiry"] += 0.2
        
        # Default to general inquiry
        if max(intents.values()) < 0.1:
            intents["general_inquiry"] = 1.0
        
        # Find highest confidence intent
        primary_intent = max(intents, key=intents.get)
        confidence = intents[primary_intent]
        
        return {
            "primary_intent": primary_intent,
            "confidence": confidence,
            "all_intents": intents,
            "is_emergency": intents["emergency"] > 0.3
        }
    
    async def _handle_receptionist_task(self, text: str, sender_id: str, context: Optional[Dict[str, Any]], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle receptionist-specific tasks with OpenManus"""
        try:
            if intent["is_emergency"]:
                response_text = "🚨 אני מבין שזה דחוף. אני מעביר אותך מיד לטיפול חירום.\n"
                response_text += "אנא התקשר מיד: 03-555-0123\n"
                response_text += "או הגע למרפאה: רחוב יוסף לפיד 1, נתניה"
                
                return {
                    "success": True,
                    "response": response_text,
                    "intent": "emergency",
                    "priority": "critical",
                    "agent": self.agent_name,
                    "engine": "openmanus",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Handle general reception tasks
            if intent["primary_intent"] == "appointment_scheduling":
                available_slots = await self.dental_tool.get_available_slots(
                    start_date="2025-09-29",
                    end_date="2025-10-06"
                )
                
                response_text = f"שלום! אני כאן לעזור לך לקבוע תור.\n\n"
                if available_slots:
                    response_text += "הזמנים הפנויים הקרובים:\n"
                    for slot in available_slots[:3]:
                        response_text += f"• {slot['date']} בשעה {slot['time']}\n"
                    response_text += "\nאיזה זמן מתאים לך?"
                else:
                    response_text += "מצטער, אין זמנים פנויים השבוע. האם תרצה לבדוק שבוע הבא?"
            
            else:
                response_text = f"שלום! אני {self.role} של המרפאה.\n\n"
                response_text += "איך אפשר לעזור לך היום?\n\n"
                response_text += "אני יכול לעזור עם:\n"
                response_text += "• קביעת תורים\n"
                response_text += "• מידע על המרפאה\n"
                response_text += "• שאלות כלליות\n"
                response_text += "• חירום - התקשר: 03-555-0123"
            
            return {
                "success": True,
                "response": response_text,
                "intent": intent["primary_intent"],
                "confidence": intent["confidence"],
                "agent": self.agent_name,
                "engine": "openmanus",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in receptionist task: {e}")
            return {
                "success": False,
                "response": "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
                "error": str(e),
                "agent": self.agent_name,
                "engine": "openmanus",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_scheduler_task(self, text: str, sender_id: str, context: Optional[Dict[str, Any]], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scheduler-specific tasks with OpenManus"""
        try:
            available_slots = await self.dental_tool.get_available_slots(
                start_date="2025-09-29",
                end_date="2025-10-13"
            )
            
            response_text = "📅 מערכת תיאום התורים של המרפאה\n\n"
            
            if available_slots:
                response_text += "זמנים פנויים לשבועיים הקרובים:\n\n"
                for i, slot in enumerate(available_slots[:7], 1):
                    response_text += f"{i}. {slot['date']} בשעה {slot['time']}\n"
                
                response_text += f"\nסה\"כ {len(available_slots)} זמנים פנויים.\n"
                response_text += "אנא בחר מספר או ציין זמן מועדף."
            else:
                response_text += "מצטער, אין זמנים פנויים בתקופה הקרובה.\n"
                response_text += "האם תרצה שאבדוק תאריכים מאוחרים יותר?"
            
            return {
                "success": True,
                "response": response_text,
                "intent": "appointment_scheduling",
                "available_slots": available_slots[:10],
                "agent": self.agent_name,
                "engine": "openmanus",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in scheduler task: {e}")
            return {
                "success": False,
                "response": "מצטער, לא הצלחתי לגשת ללוח הזמנים כרגע.",
                "error": str(e),
                "agent": self.agent_name,
                "engine": "openmanus",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_confirmation_task(self, text: str, sender_id: str, context: Optional[Dict[str, Any]], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle confirmation-specific tasks with OpenManus"""
        try:
            appointments = await self.dental_tool.get_patient_appointments(sender_id)
            
            response_text = "✅ מערכת אישור התורים\n\n"
            
            if appointments:
                response_text += "התורים שלך:\n\n"
                for i, apt in enumerate(appointments[:3], 1):
                    status_emoji = "✅" if apt.get('confirmed') else "⏳"
                    response_text += f"{status_emoji} {apt['date']} בשעה {apt['time']}\n"
                    response_text += f"   טיפול: {apt['treatment_type']}\n\n"
                
                response_text += "פעולות זמינות:\n"
                response_text += "• לאישור תור - כתב 'אישור'\n"
                response_text += "• לביטול תור - כתב 'ביטול'\n"
                response_text += "• לשינוי תור - כתב 'שינוי'"
            else:
                response_text += "לא נמצאו תורים קרובים.\n"
                response_text += "האם תרצה לקבוע תור חדש?"
            
            return {
                "success": True,
                "response": response_text,
                "intent": "appointment_confirmation",
                "appointments": appointments[:5],
                "agent": self.agent_name,
                "engine": "openmanus",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in confirmation task: {e}")
            return {
                "success": False,
                "response": "מצטער, לא הצלחתי לבדוק את התורים שלך כרגע.",
                "error": str(e),
                "agent": self.agent_name,
                "engine": "openmanus",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_general_task(self, text: str, sender_id: str, context: Optional[Dict[str, Any]], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general tasks with OpenManus"""
        response_text = f"שלום! אני {self.role} מופעל על ידי OpenManus.\n\n"
        response_text += "איך אפשר לעזור לך היום?\n\n"
        response_text += "יכולות מתקדמות:\n"
        response_text += "• ניתוח טקסט חכם\n"
        response_text += "• עיבוד שפה טבעית\n"
        response_text += "• אינטגרציה עם מערכות\n"
        response_text += "• תמיכה רב-לשונית"
        
        return {
            "success": True,
            "response": response_text,
            "intent": intent["primary_intent"],
            "agent": self.agent_name,
            "engine": "openmanus",
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_capabilities(self) -> List[str]:
        """Get OpenManus agent capabilities"""
        return [
            "advanced_nlp_processing",
            "multi_language_support", 
            "intent_analysis_with_confidence",
            "emergency_detection",
            "appointment_scheduling",
            "patient_inquiries",
            "appointment_confirmation",
            "dental_pms_integration",
            "hebrew_english_support",
            "context_awareness"
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenManus agent health"""
        try:
            tool_health = await self.dental_tool.health_check()
            
            return {
                "agent_name": self.agent_name,
                "status": "healthy" if self.initialized else "not_initialized",
                "engine": "openmanus",
                "initialized": self.initialized,
                "tool_health": tool_health,
                "capabilities_count": len(await self.get_capabilities()),
                "system_prompt_length": len(self.system_prompt),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent_name": self.agent_name,
                "status": "unhealthy",
                "engine": "openmanus",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self) -> None:
        """Cleanup OpenManus agent resources"""
        try:
            await self.dental_tool.cleanup()
            self.initialized = False
            logger.info(f"🧹 OpenManus agent '{self.agent_name}' cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up OpenManus agent '{self.agent_name}': {e}")
            raise
