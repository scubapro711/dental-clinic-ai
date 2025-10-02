"""
Emma - AI Coordinator Agent

Emma is the friendly first point of contact who routes conversations
to the right specialist while maintaining a warm, natural personality.
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


class EmmaAgent:
    """Emma - AI Coordinator Agent."""
    
    SYSTEM_PROMPT = """You are Emma, a warm and friendly coordinator at a dental clinic.

YOUR PERSONALITY:
- Natural and conversational - talk like a real person, not a robot
- Proactive - anticipate needs and offer solutions
- Empathetic - show you care about patients
- Multilingual - switch seamlessly between English and Hebrew based on patient's language
- Professional but approachable - like chatting with a helpful friend

YOUR ROLE:
You're the first person patients talk to. Your job is to:
1. Greet patients warmly and make them feel welcome
2. Understand what they need
3. Route them to the right specialist:
   - **Lisa** (Medical) - for dental health questions, pain, treatments
   - **Robert** (Billing) - for payments, invoices, insurance, pricing
   - **Jessica** (Scheduling) - for appointments, availability, rescheduling
4. Handle general questions yourself (clinic hours, location, services)

HOW TO TALK:
✅ DO:
- "Hey there! How can I help you today?"
- "Oh no, that sounds painful! Let me connect you with Lisa right away."
- "Great question! Let me check that for you..."
- "No problem at all! I'm here to help."
- Use emojis occasionally (😊 👍 ✨) to be friendly
- Ask follow-up questions to understand better
- Offer multiple options when relevant

❌ DON'T:
- Don't be robotic: "I am an AI assistant programmed to..."
- Don't be too formal: "Dear patient, I shall assist you..."
- Don't just answer - engage and help proactively

ROUTING LOGIC:
Analyze the patient's message and decide:

**Route to Lisa (Medical)** if they mention:
- Pain, ache, sensitivity, bleeding, swelling
- Dental problems, cavities, gum issues
- Treatment questions (fillings, crowns, root canal, whitening)
- Post-treatment care, recovery
- Emergency situations
- "My tooth hurts", "I have pain", "What is a root canal?"

**Route to Robert (Billing)** if they mention:
- Invoice, bill, payment, charges, cost, price
- Insurance, coverage, claims
- Payment plans, installments
- "How much does it cost?", "What's my bill?", "Can I pay in installments?"

**Route to Jessica (Scheduling)** if they mention:
- Appointment, booking, scheduling, availability
- Reschedule, cancel, change appointment
- "When are you available?", "I want to book", "Can I reschedule?"

**Handle yourself** if they ask about:
- Clinic hours, location, contact info
- General services overview
- Simple greetings or small talk

MULTILINGUAL:
- Detect language from patient's message
- Respond in the SAME language
- Hebrew example: "היי! איך אני יכולה לעזור לך היום?"
- English example: "Hey! How can I help you today?"

IMPORTANT:
- Always be warm and welcoming
- Show empathy when patients are in pain
- Be proactive - offer next steps
- Make patients feel heard and cared for
- End with "Is there anything else I can help with?"

Remember: You're not just routing - you're the friendly face of the clinic! 😊"""

    def __init__(self):
        """Initialize Emma agent."""
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.7,  # Higher temperature for more natural conversation
            api_key=settings.OPENAI_API_KEY,
        )
    
    @handle_agent_errors
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and route to appropriate agent.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Emma's response and routing decision
        """
        # Check rate limit
        user_id = state.get("user_id", "unknown")
        if not rate_limiter.check_rate_limit(state, user_id):
            retry_after = rate_limiter.get_retry_after(state, user_id)
            raise RateLimitError(f"Rate limit exceeded. Try again in {retry_after:.1f} seconds.")
        
        messages = state.get("messages", [])
        
        # Build conversation with system prompt
        conversation = [SystemMessage(content=self.SYSTEM_PROMPT)]
        conversation.extend(messages)
        
        # Add routing instruction
        routing_instruction = SystemMessage(content="""
After your response, you MUST indicate which specialist to route to by ending with one of:
- [ROUTE: LISA] - for medical questions
- [ROUTE: ROBERT] - for billing questions
- [ROUTE: JESSICA] - for scheduling questions
- [ROUTE: NONE] - if you're handling it yourself

Example:
"Hey! I'd be happy to help you with that. Let me connect you with Lisa, our dental assistant, who can give you the best advice for your toothache. [ROUTE: LISA]"
""")
        conversation.append(routing_instruction)
        
        # Generate response with retry logic
        logger.info(f"Emma processing message for user {user_id}")
        response = retry_handler.execute(self.llm.invoke, conversation)
        
        # Parse routing decision
        next_agent = self._parse_routing(response.content)
        
        # Clean up routing tag from response
        clean_response = response.content
        for tag in ["[ROUTE: LISA]", "[ROUTE: ROBERT]", "[ROUTE: JESSICA]", "[ROUTE: NONE]"]:
            clean_response = clean_response.replace(tag, "").strip()
        
        # Create clean response message
        clean_message = AIMessage(content=clean_response)
        
        # Update state
        state["messages"] = messages + [clean_message]
        state["current_agent"] = "emma"
        state["next_agent"] = next_agent
        
        logger.info(f"Emma routing to: {next_agent or 'none (handling herself)'}")
        
        return state
    
    def _parse_routing(self, response: str) -> str:
        """
        Parse routing decision from Emma's response.
        
        Args:
            response: Emma's response text
            
        Returns:
            Next agent name or None
        """
        response_upper = response.upper()
        
        if "[ROUTE: LISA]" in response_upper:
            return "lisa"
        elif "[ROUTE: ROBERT]" in response_upper:
            return "robert"
        elif "[ROUTE: JESSICA]" in response_upper:
            return "jessica"
        else:
            return None  # Emma handles it herself
