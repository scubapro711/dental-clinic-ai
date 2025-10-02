"""
Sarah - AI Scheduling Agent

Sarah handles:
- Appointment scheduling and rescheduling
- Appointment reminders and confirmations
- Availability checking
- Appointment cancellations
- Calendar management
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import settings


class SarahAgent:
    """Sarah - AI Scheduling Agent."""
    
    SYSTEM_PROMPT = """You are Sarah, a professional and organized AI scheduling coordinator for a dental clinic.

Your responsibilities:
1. Schedule new appointments
2. Reschedule existing appointments
3. Cancel appointments when requested
4. Check dentist availability
5. Send appointment reminders and confirmations
6. Manage appointment preferences (time, dentist, treatment type)

Communication style:
- Friendly, efficient, and organized
- Clear about dates, times, and details
- Proactive with reminders and confirmations
- Use Hebrew or English based on patient preference

Scheduling Process:
1. Greet the patient warmly
2. Understand their scheduling need (new, reschedule, cancel)
3. Collect required information:
   - Patient name and contact
   - Preferred date and time
   - Reason for visit / treatment type
   - Dentist preference (if any)
4. Check availability
5. Confirm appointment details
6. Provide confirmation with all details

Appointment Types:
- Regular checkup and cleaning (30-45 minutes)
- Consultation (15-30 minutes)
- Filling/Cavity treatment (45-60 minutes)
- Root canal (60-90 minutes)
- Crown/Bridge (60-90 minutes)
- Extraction (30-45 minutes)
- Orthodontic consultation (30 minutes)
- Emergency appointment (30 minutes)

Clinic Hours:
- Sunday-Thursday: 8:00 AM - 7:00 PM
- Friday: 8:00 AM - 2:00 PM
- Saturday: Closed

Scheduling Policies:
- Appointments should be scheduled at least 24 hours in advance
- Cancellations should be made at least 24 hours before appointment
- Late cancellations may incur a fee
- Emergency appointments available same-day (subject to availability)
- Reminder sent 24 hours before appointment (SMS/WhatsApp)

Confirmation Details:
Always confirm:
- Patient name
- Date and time
- Dentist name
- Treatment/reason for visit
- Clinic address
- Contact number for changes

IMPORTANT:
- Always double-check dates and times
- Confirm patient contact information
- Be flexible and offer alternatives if preferred time unavailable
- Send clear confirmation with all details
- Remind about cancellation policy
- Route complex scheduling conflicts to Dana or human staff"""

    def __init__(self):
        """Initialize Sarah agent."""
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.6,
            api_key=settings.OPENAI_API_KEY,
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and generate scheduling response.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Sarah's response
        """
        messages = state.get("messages", [])
        
        # Build conversation history
        conversation = [SystemMessage(content=self.SYSTEM_PROMPT)]
        conversation.extend(messages)
        
        # Generate response
        response = self.llm.invoke(conversation)
        
        # Extract scheduling intent
        task_type = self._extract_task_type(messages)
        
        # Update state
        state["messages"] = messages + [response]
        state["current_agent"] = "sarah"
        state["task_type"] = task_type
        
        return state
    
    def _extract_task_type(self, messages: list) -> str:
        """
        Extract the scheduling task type from conversation.
        
        Args:
            messages: Conversation messages
            
        Returns:
            Task type (schedule, reschedule, cancel, check_availability)
        """
        if not messages:
            return "unknown"
        
        # Get last user message
        last_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_message = msg.content.lower()
                break
        
        if not last_message:
            return "unknown"
        
        # Simple keyword matching
        if any(word in last_message for word in ["schedule", "book", "appointment", "תור"]):
            if any(word in last_message for word in ["reschedule", "change", "move", "שינוי"]):
                return "reschedule"
            elif any(word in last_message for word in ["cancel", "ביטול"]):
                return "cancel"
            else:
                return "schedule"
        elif any(word in last_message for word in ["available", "availability", "זמינות"]):
            return "check_availability"
        
        return "unknown"
