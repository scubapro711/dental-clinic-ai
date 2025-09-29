"""
CrewAI Agent Wrapper
עטיפת סוכן CrewAI
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..interfaces.ai_agent_interface import AIAgentInterface
from ..tools.advanced_dental_tool import AdvancedDentalTool

logger = logging.getLogger(__name__)

class CrewAIAgentWrapper(AIAgentInterface):
    """Wrapper for CrewAI agents that implements the standard AI agent interface"""
    
    def __init__(self, agent_config: Dict[str, Any], engine_config: Dict[str, Any]):
        self.agent_config = agent_config
        self.engine_config = engine_config
        self.agent_name = agent_config.get("name", "default_agent")
        self.role = agent_config.get("role", "AI Assistant")
        self.goal = agent_config.get("goal", "Help users with their requests")
        self.backstory = agent_config.get("backstory", "You are a helpful AI assistant")
        
        use_mock = engine_config.get("use_mock_tools", False)
        if use_mock:
            from ..tools.mock_dental_tool import MockDentalTool
            self.dental_tool = MockDentalTool()
        else:
            self.dental_tool = AdvancedDentalTool()
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the CrewAI agent"""
        try:
            await self.dental_tool.initialize()
            self.initialized = True
            logger.info(f"CrewAI agent '{self.agent_name}' initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CrewAI agent '{self.agent_name}': {e}")
            raise
    
    async def process_message(self, text: str, sender_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message using CrewAI logic"""
        try:
            if not self.initialized:
                raise RuntimeError("Agent not initialized")
            
            # Determine intent and route to appropriate handler
            intent = await self._analyze_intent(text)
            
            if intent == "appointment_scheduling":
                return await self._handle_appointment_request(text, sender_id, context)
            elif intent == "patient_inquiry":
                return await self._handle_patient_inquiry(text, sender_id, context)
            elif intent == "appointment_confirmation":
                return await self._handle_appointment_confirmation(text, sender_id, context)
            else:
                return await self._handle_general_inquiry(text, sender_id, context)
                
        except Exception as e:
            logger.error(f"Error processing message in agent '{self.agent_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "engine": "crewai",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_intent(self, text: str) -> str:
        """Analyze message intent"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["appointment", "schedule", "book", "תור", "לקבוע"]):
            return "appointment_scheduling"
        elif any(word in text_lower for word in ["confirm", "reminder", "אישור", "תזכורת"]):
            return "appointment_confirmation"
        elif any(word in text_lower for word in ["patient", "medical", "treatment", "מטופל", "טיפול"]):
            return "patient_inquiry"
        else:
            return "general_inquiry"
    
    async def _handle_appointment_request(self, text: str, sender_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle appointment scheduling requests"""
        try:
            # Get available slots
            available_slots = await self.dental_tool.get_available_slots(
                start_date="2025-09-27",
                end_date="2025-10-04"
            )
            
            response_text = f"שלום! אני כאן לעזור לך לקבוע תור.\n\n"
            
            if available_slots:
                response_text += "הזמנים הפנויים הקרובים:\n"
                for slot in available_slots[:3]:  # Show first 3 slots
                    response_text += f"• {slot['date']} בשעה {slot['time']}\n"
                response_text += "\nאיזה זמן מתאים לך?"
            else:
                response_text += "מצטער, אין זמנים פנויים השבוע. האם תרצה לבדוק שבוע הבא?"
            
            return {
                "success": True,
                "response": response_text,
                "intent": "appointment_scheduling",
                "available_slots": available_slots[:5],
                "agent": self.agent_name,
                "engine": "crewai",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling appointment request: {e}")
            return {
                "success": False,
                "response": "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
                "error": str(e),
                "agent": self.agent_name,
                "engine": "crewai",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_patient_inquiry(self, text: str, sender_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle patient inquiries"""
        try:
            # Get patient details if available
            patient_details = await self.dental_tool.get_patient_details(sender_id)
            
            response_text = "שלום! "
            if patient_details:
                response_text += f"איך אפשר לעזור לך היום, {patient_details.get('name', '')}?"
            else:
                response_text += "איך אפשר לעזור לך היום?"
            
            response_text += "\n\nאני יכול לעזור עם:\n"
            response_text += "• קביעת תורים\n"
            response_text += "• מידע על טיפולים\n"
            response_text += "• שאלות כלליות על המרפאה"
            
            return {
                "success": True,
                "response": response_text,
                "intent": "patient_inquiry",
                "patient_details": patient_details,
                "agent": self.agent_name,
                "engine": "crewai",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling patient inquiry: {e}")
            return {
                "success": False,
                "response": "שלום! איך אפשר לעזור לך היום?",
                "error": str(e),
                "agent": self.agent_name,
                "engine": "crewai",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_appointment_confirmation(self, text: str, sender_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle appointment confirmations"""
        try:
            # Get upcoming appointments for patient
            appointments = await self.dental_tool.get_patient_appointments(sender_id)
            
            response_text = "בדיקת תורים קרובים:\n\n"
            
            if appointments:
                for apt in appointments[:2]:  # Show next 2 appointments
                    response_text += f"• {apt['date']} בשעה {apt['time']} - {apt['treatment_type']}\n"
                response_text += "\nהאם התורים מתאימים לך?"
            else:
                response_text += "לא נמצאו תורים קרובים. האם תרצה לקבוע תור חדש?"
            
            return {
                "success": True,
                "response": response_text,
                "intent": "appointment_confirmation",
                "appointments": appointments,
                "agent": self.agent_name,
                "engine": "crewai",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling appointment confirmation: {e}")
            return {
                "success": False,
                "response": "מצטער, לא הצלחתי לבדוק את התורים שלך כרגע.",
                "error": str(e),
                "agent": self.agent_name,
                "engine": "crewai",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_general_inquiry(self, text: str, sender_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle general inquiries"""
        response_text = f"שלום! אני {self.role} של המרפאה.\n\n"
        response_text += "איך אפשר לעזור לך היום?\n\n"
        response_text += "אני יכול לעזור עם:\n"
        response_text += "• קביעת תורים\n"
        response_text += "• מידע על המרפאה\n"
        response_text += "• שאלות כלליות"
        
        return {
            "success": True,
            "response": response_text,
            "intent": "general_inquiry",
            "agent": self.agent_name,
            "engine": "crewai",
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "appointment_scheduling",
            "patient_inquiries", 
            "appointment_confirmation",
            "general_assistance",
            "hebrew_support",
            "dental_pms_integration"
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        try:
            tool_health = await self.dental_tool.health_check()
            
            return {
                "agent_name": self.agent_name,
                "status": "healthy" if self.initialized else "not_initialized",
                "initialized": self.initialized,
                "tool_health": tool_health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent_name": self.agent_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        try:
            await self.dental_tool.cleanup()
            self.initialized = False
            logger.info(f"CrewAI agent '{self.agent_name}' cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up CrewAI agent '{self.agent_name}': {e}")
            raise
