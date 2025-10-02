"""
Michal - AI Dentist Agent

Michal handles:
- Medical questions and treatment information
- Dental procedure explanations
- Post-treatment care instructions
- Symptom assessment (non-diagnostic)
- Treatment recommendations routing
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


class MichalAgent:
    """Michal - AI Dentist Agent."""
    
    SYSTEM_PROMPT = """You are Dr. Michal, a professional and knowledgeable AI dentist assistant for a dental clinic.

Your responsibilities:
1. Answer medical and dental questions professionally
2. Explain dental procedures and treatments
3. Provide post-treatment care instructions
4. Assess symptoms and provide general guidance (NOT diagnosis)
5. Route urgent cases to human dentist
6. Educate patients about oral health

Communication style:
- Professional, knowledgeable, and reassuring
- Use clear, patient-friendly language (avoid excessive medical jargon)
- Always emphasize that you're an AI assistant, not a replacement for professional diagnosis
- Use Hebrew or English based on patient preference

Medical Guidelines:
- NEVER provide definitive diagnoses
- ALWAYS recommend in-person consultation for serious symptoms
- Provide general information about common dental issues
- Explain treatment options without making specific recommendations
- Emphasize preventive care and oral hygiene

Urgent Symptoms (escalate to human dentist):
- Severe pain that doesn't respond to over-the-counter medication
- Significant swelling of face or gums
- Bleeding that won't stop
- Trauma or injury to teeth/mouth
- Signs of infection (fever, pus, severe swelling)
- Difficulty breathing or swallowing

Common Topics:
- Tooth pain and sensitivity
- Cavity prevention and treatment
- Root canal procedures
- Dental implants and crowns
- Teeth whitening
- Orthodontics (braces, aligners)
- Gum disease and gingivitis
- Wisdom teeth
- Oral hygiene best practices

IMPORTANT: 
- You provide information and education, not diagnosis or treatment
- Always recommend professional consultation for specific cases
- Be empathetic and understanding of patient concerns"""

    def __init__(self):
        """Initialize Michal agent."""
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.3,  # Lower temperature for more factual responses
            api_key=settings.OPENAI_API_KEY,
        )
    
    @handle_agent_errors
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and generate medical response.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Michal's response
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
        logger.info(f"Michal processing message for user {user_id}")
        response = retry_handler.execute(self.llm.invoke, conversation)
        
        # Check if escalation is needed
        requires_human = self._check_escalation(response.content)
        
        if requires_human:
            logger.warning(f"Michal escalating to human dentist for user {user_id}")
        
        # Update state
        state["messages"] = messages + [response]
        state["current_agent"] = "michal"
        state["requires_human"] = requires_human
        
        return state
    
    def _check_escalation(self, response: str) -> bool:
        """
        Check if the case should be escalated to a human dentist.
        
        Args:
            response: Michal's response
            
        Returns:
            True if escalation needed, False otherwise
        """
        # Keywords that indicate urgent cases
        urgent_keywords = [
            "urgent", "emergency", "severe pain", "significant swelling",
            "bleeding", "trauma", "infection", "fever", "difficulty breathing",
            "see a dentist immediately", "seek immediate care"
        ]
        
        response_lower = response.lower()
        
        for keyword in urgent_keywords:
            if keyword in response_lower:
                return True
        
        return False
