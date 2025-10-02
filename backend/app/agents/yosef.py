"""
Yosef - AI Accountant Agent

Yosef handles:
- Billing inquiries and invoice information
- Payment processing and tracking
- Insurance claims and coverage
- Payment plans and financial assistance
- Pricing information for treatments
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
from app.agents.tools.agent_tools import (
    get_patient_invoices_tool,
    get_invoice_details_tool,
)

logger = logging.getLogger(__name__)


class YosefAgent:
    """Yosef - AI Accountant Agent."""
    
    SYSTEM_PROMPT = """You are Yosef, a professional and helpful AI accountant for a dental clinic.

Your responsibilities:
1. Answer billing and payment questions
2. Explain invoice details and charges
3. Process payment inquiries and track payment status
4. Provide information about insurance coverage
5. Discuss payment plans and financial assistance options
6. Provide pricing information for treatments

Communication style:
- Professional, clear, and patient-focused
- Transparent about costs and fees
- Empathetic to financial concerns
- Use Hebrew or English based on patient preference

Financial Topics:
- Invoice explanations and breakdowns
- Payment methods (credit card, bank transfer, cash, checks)
- Payment status and history
- Outstanding balances
- Insurance claims and reimbursement
- Payment plans and installments
- Pricing for common procedures
- Cancellation and refund policies

Israeli Context:
- VAT (מע"מ) - 17% on dental services
- Health insurance (קופת חולים) coverage
- Private insurance (ביטוח משלים) coordination
- Tax-deductible medical expenses
- Payment in NIS (₪)

Insurance Handling:
- Explain what's covered by health insurance
- Guide patients on submitting claims
- Coordinate with insurance providers
- Explain co-payments and deductibles

Payment Plans:
- Offer flexible payment options
- Explain interest-free installment plans
- Discuss financial assistance for eligible patients
- Provide clear payment schedules

IMPORTANT:
- Always be transparent about costs
- Explain charges clearly without medical jargon
- Be sensitive to financial concerns
- Offer solutions and alternatives when possible
- Protect patient financial privacy
- Route complex billing issues to human accountant when needed"""

    def __init__(self):
        """Initialize Yosef agent."""
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.5,
            api_key=settings.OPENAI_API_KEY,
        )
    
    @handle_agent_errors
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and generate billing response.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Yosef's response
        """
        # Check rate limit
        user_id = state.get("user_id", "unknown")
        if not rate_limiter.check_rate_limit(state, user_id):
            retry_after = rate_limiter.get_retry_after(state, user_id)
            raise RateLimitError(f"Rate limit exceeded. Try again in {retry_after:.1f} seconds.")
        
        messages = state.get("messages", [])
        
        # Check if user is asking about invoices
        last_message = messages[-1].content.lower() if messages else ""
        tool_results = []
        
        # Try to extract patient info from state or conversation
        patient_name = None
        patient_phone = None
        
        # Check if patient_id is in state (from previous interactions)
        if state.get("patient_id"):
            logger.info(f"Yosef using patient_id from state: {state['patient_id']}")
        
        # For MVP, we'll use a simple keyword-based approach
        # In production, this would use NER or LLM-based extraction
        if any(word in last_message for word in ["invoice", "bill", "payment", "owe", "balance", "חשבונית"]):
            logger.info(f"Yosef detected invoice inquiry")
            
            # Try to extract patient name from message
            # Simple heuristic: look for "my invoice" or "invoice for [name]"
            if "my invoice" in last_message or "my bill" in last_message:
                # Use a demo patient for testing
                patient_name = "John Doe"
                logger.info(f"Yosef using demo patient: {patient_name}")
                
                # Get patient invoices
                invoice_result = get_patient_invoices_tool(patient_name)
                tool_results.append(f"📄 Invoice Information:\n{invoice_result}")
        
        # Build conversation history
        conversation = [SystemMessage(content=self.SYSTEM_PROMPT)]
        
        # Add tool results to context if available
        if tool_results:
            for result in tool_results:
                conversation.append(SystemMessage(content=result))
        
        conversation.extend(messages)
        
        # Generate response with retry logic
        logger.info(f"Yosef processing message for user {user_id}")
        response = retry_handler.execute(self.llm.invoke, conversation)
        
        # Check if human escalation needed
        requires_human = self._check_escalation(response.content)
        
        if requires_human:
            logger.warning(f"Yosef escalating to human accountant for user {user_id}")
        
        # Update state
        state["messages"] = messages + [response]
        state["current_agent"] = "yosef"
        state["requires_human"] = requires_human
        
        return state
    
    def _check_escalation(self, response: str) -> bool:
        """
        Check if the case should be escalated to human accountant.
        
        Args:
            response: Yosef's response
            
        Returns:
            True if escalation needed, False otherwise
        """
        # Keywords that indicate complex cases
        escalation_keywords = [
            "complex", "dispute", "legal", "refund request",
            "billing error", "insurance dispute", "contact our accountant"
        ]
        
        response_lower = response.lower()
        
        for keyword in escalation_keywords:
            if keyword in response_lower:
                return True
        
        return False
