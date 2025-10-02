"""
Dana - AI Receptionist Agent

Dana handles:
- Appointment scheduling and management
- Patient registration and basic info
- General inquiries and routing
- WhatsApp/Telegram integration
"""

import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import settings
from app.agents.error_handler import (
    handle_agent_errors,
    retry_handler,
    rate_limiter,
    RateLimitError,
)

logger = logging.getLogger(__name__)


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
   - Scheduling questions → Sarah (scheduler)

Communication style:
- Warm, professional, and empathetic
- Use Hebrew or English based on patient preference
- Keep responses concise and clear
- Always confirm important details (dates, times, names)

When handling general inquiries:
- Provide helpful information about the clinic
- Answer questions about services offered
- Explain clinic policies and procedures
- Route specialized questions to appropriate agents

IMPORTANT: If you don't have access to real-time data, acknowledge this and offer to help in other ways."""

    def __init__(self):
        """Initialize Dana agent."""
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
        )
    
    @handle_agent_errors
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and generate response.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Dana's response
        """
        # Check rate limit
        user_id = state.get("user_id", "unknown")
        if not rate_limiter.check_rate_limit(state, user_id):
            retry_after = rate_limiter.get_retry_after(state, user_id)
            raise RateLimitError(f"Rate limit exceeded. Try again in {retry_after:.1f} seconds.")
        
        messages = state.get("messages", [])
        
        # Build conversation history
        conversation = [SystemMessage(content=self.SYSTEM_PROMPT)]
        conversation.extend(messages)
        
        # Generate response with retry logic
        logger.info(f"Dana processing message for user {user_id}")
        response = retry_handler.execute(self.llm.invoke, conversation)
        
        # Determine if routing is needed
        next_agent = self._determine_routing(response.content)
        
        if next_agent:
            logger.info(f"Dana routing to {next_agent}")
        
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
        
        if any(word in response_lower for word in ["medical", "treatment", "pain", "diagnosis", "dentist", "tooth", "teeth"]):
            return "michal"
        elif any(word in response_lower for word in ["billing", "insurance", "payment", "invoice", "cost", "price"]):
            return "yosef"
        elif any(word in response_lower for word in ["schedule", "appointment", "book", "reschedule", "cancel", "availability"]):
            return "sarah"
        
        return None
