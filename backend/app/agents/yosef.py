"""
Yosef - AI Accountant Agent

Yosef handles:
- Billing inquiries and invoice information
- Payment processing and tracking
- Insurance claims and coverage
- Payment plans and financial assistance
- Pricing information for treatments
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import settings


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
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and generate billing response.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Yosef's response
        """
        messages = state.get("messages", [])
        
        # Build conversation history
        conversation = [SystemMessage(content=self.SYSTEM_PROMPT)]
        conversation.extend(messages)
        
        # Generate response
        response = self.llm.invoke(conversation)
        
        # Check if human escalation needed
        requires_human = self._check_escalation(response.content)
        
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
