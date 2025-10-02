"""
Dana - AI Receptionist Agent

Dana handles:
- Appointment scheduling and management
- Patient registration and basic info
- General inquiries and routing
- WhatsApp/Telegram integration
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import settings


class DanaAgent:
    """Dana - AI Receptionist Agent."""
    
    SYSTEM_PROMPT = """You are Dana, a professional and friendly AI receptionist for a dental clinic.

Your responsibilities:
1. Greet patients warmly and professionally
2. Schedule, reschedule, and cancel appointments
3. Collect basic patient information for new registrations
4. Answer general questions about the clinic
5. Route complex questions to appropriate specialists:
   - Medical questions → Dr. Michal (dentist)
   - Billing/insurance → Yosef (accountant)
   - HR/staff questions → Sarah (HR manager)

Communication style:
- Warm, professional, and empathetic
- Use Hebrew or English based on patient preference
- Keep responses concise and clear
- Always confirm important details (dates, times, names)

When scheduling appointments:
- Ask for: patient name, phone, preferred date/time, reason for visit
- Offer alternative times if requested slot is unavailable
- Send confirmation with appointment details

IMPORTANT: If you don't have access to real-time data, acknowledge this and offer to help in other ways."""

    def __init__(self):
        """Initialize Dana agent."""
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and generate response.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Dana's response
        """
        messages = state.get("messages", [])
        
        # Build conversation history
        conversation = [SystemMessage(content=self.SYSTEM_PROMPT)]
        conversation.extend(messages)
        
        # Generate response
        response = self.llm.invoke(conversation)
        
        # Determine if routing is needed
        next_agent = self._determine_routing(response.content)
        
        # Update state
        state["messages"] = messages + [response]
        state["current_agent"] = "dana"
        state["next_agent"] = next_agent
        
        return state
    
    def _determine_routing(self, response: str) -> str:
        """
        Determine if message should be routed to another agent.
        
        Args:
            response: Dana's response
            
        Returns:
            Next agent name or None
        """
        # Simple keyword-based routing (can be enhanced with LLM)
        response_lower = response.lower()
        
        if any(word in response_lower for word in ["medical", "treatment", "pain", "diagnosis"]):
            return "michal"
        elif any(word in response_lower for word in ["billing", "insurance", "payment", "invoice"]):
            return "yosef"
        elif any(word in response_lower for word in ["hr", "staff", "employee", "payroll"]):
            return "sarah"
        
        return None
