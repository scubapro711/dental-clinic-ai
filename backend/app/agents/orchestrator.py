"""
Agent Orchestrator - Simplified MVP version

This orchestrator manages the flow between AI agents without LangGraph for MVP.
"""

from typing import Dict, Any, List
from uuid import UUID

from langchain_core.messages import HumanMessage, AIMessage

from app.agents.dana import DanaAgent
from app.agents.michal import MichalAgent
from app.agents.yosef import YosefAgent
from app.agents.sarah import SarahAgent
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from sqlalchemy.orm import Session


class AgentOrchestrator:
    """Orchestrates conversation flow between AI agents."""
    
    def __init__(self):
        """Initialize orchestrator with all 4 agents."""
        self.dana = DanaAgent()
        self.michal = MichalAgent()
        self.yosef = YosefAgent()
        self.sarah = SarahAgent()
        
    async def process_message(
        self,
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        conversation_id: UUID,
        message_content: str,
    ) -> Dict[str, Any]:
        """
        Process user message and generate AI response.
        
        Args:
            db: Database session
            user_id: User ID
            organization_id: Organization ID
            conversation_id: Conversation ID
            message_content: User's message content
            
        Returns:
            Response dict with agent reply
        """
        # Get conversation history
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Get recent messages for context
        recent_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        # Build message history (reverse to chronological order)
        message_history = []
        for msg in reversed(recent_messages):
            if msg.role == MessageRole.USER:
                message_history.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                message_history.append(AIMessage(content=msg.content))
        
        # Add current user message
        message_history.append(HumanMessage(content=message_content))
        
        # Save user message to database
        user_message = Message(
            conversation_id=conversation_id,
            organization_id=organization_id,
            role=MessageRole.USER,
            content=message_content,
        )
        db.add(user_message)
        db.commit()
        
        # Determine which agent to use based on conversation context
        # For MVP, Dana routes to appropriate agent
        state = {
            "messages": message_history,
            "user_id": str(user_id),
            "organization_id": str(organization_id),
            "conversation_id": str(conversation_id),
            "current_agent": "dana",
            "next_agent": None,
            "extracted_data": {},
            "tool_results": {},
            "final_response": None,
            "requires_human": False,
        }
        
        # Process with Dana first (coordinator)
        updated_state = self.dana.process(state)
        
        # Check if Dana wants to route to another agent
        next_agent = updated_state.get("next_agent")
        
        if next_agent == "michal":
            # Route to medical agent
            updated_state = self.michal.process(updated_state)
        elif next_agent == "yosef":
            # Route to billing agent
            updated_state = self.yosef.process(updated_state)
        elif next_agent == "sarah":
            # Route to scheduling agent
            updated_state = self.sarah.process(updated_state)
        
        # Get AI response
        ai_response = updated_state["messages"][-1].content
        current_agent = updated_state.get("current_agent", "dana")
        
        # Save AI response to database
        ai_message = Message(
            conversation_id=conversation_id,
            organization_id=organization_id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
            agent_name=current_agent,
        )
        db.add(ai_message)
        db.commit()
        
        return {
            "response": ai_response,
            "agent": current_agent,
            "next_agent": updated_state.get("next_agent"),
            "requires_human": updated_state.get("requires_human", False),
        }
