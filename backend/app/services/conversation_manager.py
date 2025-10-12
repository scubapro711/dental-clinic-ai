"""
Advanced Conversation Manager with Memory and Context.

Provides multi-turn conversation support with:
- Conversation history tracking
- Context preservation across turns
- Memory management
- Agent handoff
- Proactive suggestions
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import json
import logging

from sqlalchemy.orm import Session
from langgraph.checkpoint.postgres import PostgresSaver

from app.models.conversation import Conversation, ConversationStatus, ConversationChannel
from app.models.message import Message, MessageRole
from app.core.database import get_db

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages multi-turn conversations with memory and context.
    
    Features:
    - Create and load conversations
    - Track message history
    - Preserve context across turns
    - Generate summaries
    - Handle agent handoffs
    - Provide proactive suggestions
    """
    
    def __init__(self, db: Session):
        """
        Initialize conversation manager.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_conversation(
        self,
        organization_id: UUID,
        channel: ConversationChannel = ConversationChannel.WEB_CHAT,
        primary_agent: str = "alex",
        patient_name: Optional[str] = None,
        patient_email: Optional[str] = None,
        patient_phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            organization_id: Organization UUID
            channel: Communication channel
            primary_agent: Primary agent name
            patient_name: Patient name (optional)
            patient_email: Patient email (optional)
            patient_phone: Patient phone (optional)
            metadata: Additional metadata
        
        Returns:
            Created Conversation object
        """
        # Generate unique thread ID for LangGraph
        thread_id = f"conv_{uuid4()}"
        
        conversation = Conversation(
            organization_id=organization_id,
            channel=channel,
            primary_agent=primary_agent,
            patient_name=patient_name,
            patient_email=patient_email,
            patient_phone=patient_phone,
            langgraph_thread_id=thread_id,
            langgraph_state={
                "metadata": metadata or {},
                "context": {},
                "history_summary": ""
            },
            status=ConversationStatus.ACTIVE
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation.id} for org {organization_id}")
        
        return conversation
    
    def get_conversation(
        self,
        conversation_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> Optional[Conversation]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: Conversation UUID
            organization_id: Organization UUID (for access control)
        
        Returns:
            Conversation object or None
        """
        query = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None)
        )
        
        if organization_id:
            query = query.filter(Conversation.organization_id == organization_id)
        
        return query.first()
    
    def get_or_create_conversation(
        self,
        organization_id: UUID,
        patient_phone: Optional[str] = None,
        patient_email: Optional[str] = None,
        channel: ConversationChannel = ConversationChannel.WEB_CHAT,
        **kwargs
    ) -> Conversation:
        """
        Get existing active conversation or create new one.
        
        Useful for channels like Telegram/WhatsApp where we want to continue
        existing conversations.
        
        Args:
            organization_id: Organization UUID
            patient_phone: Patient phone (for matching)
            patient_email: Patient email (for matching)
            channel: Communication channel
            **kwargs: Additional arguments for create_conversation
        
        Returns:
            Conversation object
        """
        # Try to find existing active conversation
        query = self.db.query(Conversation).filter(
            Conversation.organization_id == organization_id,
            Conversation.channel == channel,
            Conversation.status == ConversationStatus.ACTIVE,
            Conversation.deleted_at.is_(None)
        )
        
        if patient_phone:
            query = query.filter(Conversation.patient_phone == patient_phone)
        elif patient_email:
            query = query.filter(Conversation.patient_email == patient_email)
        
        # Get most recent conversation
        conversation = query.order_by(Conversation.updated_at.desc()).first()
        
        if conversation:
            # Check if conversation is still recent (within 24 hours)
            if datetime.utcnow() - conversation.updated_at < timedelta(hours=24):
                logger.info(f"Continuing existing conversation {conversation.id}")
                return conversation
        
        # Create new conversation
        return self.create_conversation(
            organization_id=organization_id,
            channel=channel,
            patient_phone=patient_phone,
            patient_email=patient_email,
            **kwargs
        )
    
    def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        agent_name: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Add message to conversation.
        
        Args:
            conversation_id: Conversation UUID
            role: Message role (user, assistant, system, tool)
            content: Message content
            agent_name: Agent name (for assistant messages)
            tool_calls: List of tool calls made
            metadata: Additional metadata
        
        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name,
            tool_calls=tool_calls,
            metadata=metadata or {}
        )
        
        self.db.add(message)
        
        # Update conversation timestamp
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        logger.debug(f"Added {role} message to conversation {conversation_id}")
        
        return message
    
    def get_conversation_history(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None,
        include_system: bool = False
    ) -> List[Message]:
        """
        Get conversation message history.
        
        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages (most recent)
            include_system: Include system messages
        
        Returns:
            List of Message objects
        """
        query = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        )
        
        if not include_system:
            query = query.filter(Message.role != MessageRole.SYSTEM)
        
        query = query.order_by(Message.created_at.asc())
        
        if limit:
            # Get last N messages
            query = query.limit(limit)
        
        return query.all()
    
    def get_context_window(
        self,
        conversation_id: UUID,
        window_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent conversation context for agent.
        
        Args:
            conversation_id: Conversation UUID
            window_size: Number of recent messages to include
        
        Returns:
            List of message dictionaries
        """
        messages = self.get_conversation_history(
            conversation_id=conversation_id,
            limit=window_size,
            include_system=False
        )
        
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "agent_name": msg.agent_name,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    def update_conversation_state(
        self,
        conversation_id: UUID,
        state_update: Dict[str, Any]
    ) -> Conversation:
        """
        Update conversation LangGraph state.
        
        Args:
            conversation_id: Conversation UUID
            state_update: State updates to merge
        
        Returns:
            Updated Conversation object
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Merge state updates
        current_state = conversation.langgraph_state or {}
        current_state.update(state_update)
        conversation.langgraph_state = current_state
        
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.debug(f"Updated state for conversation {conversation_id}")
        
        return conversation
    
    def generate_summary(
        self,
        conversation_id: UUID,
        force: bool = False
    ) -> str:
        """
        Generate AI summary of conversation.
        
        Args:
            conversation_id: Conversation UUID
            force: Force regeneration even if summary exists
        
        Returns:
            Summary text
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Return existing summary if available
        if conversation.summary and not force:
            return conversation.summary
        
        # Get conversation history
        messages = self.get_conversation_history(conversation_id)
        
        if not messages:
            return "No messages yet"
        
        # Generate summary (simplified - in production use LLM)
        user_messages = [m for m in messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in messages if m.role == MessageRole.ASSISTANT]
        
        summary = (
            f"Conversation with {conversation.patient_name or 'anonymous patient'}. "
            f"{len(user_messages)} user messages, {len(assistant_messages)} assistant responses. "
            f"Primary agent: {conversation.primary_agent}. "
            f"Status: {conversation.status.value}."
        )
        
        # TODO: Use LLM to generate better summary
        # summary = await llm.generate_summary(messages)
        
        # Save summary
        conversation.summary = summary
        self.db.commit()
        
        logger.info(f"Generated summary for conversation {conversation_id}")
        
        return summary
    
    def complete_conversation(
        self,
        conversation_id: UUID,
        reason: Optional[str] = None
    ) -> Conversation:
        """
        Mark conversation as completed.
        
        Args:
            conversation_id: Conversation UUID
            reason: Completion reason
        
        Returns:
            Updated Conversation object
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation.status = ConversationStatus.COMPLETED
        conversation.completed_at = datetime.utcnow()
        
        # Generate final summary
        self.generate_summary(conversation_id, force=True)
        
        # Add completion reason to state
        if reason:
            state = conversation.langgraph_state or {}
            state["completion_reason"] = reason
            conversation.langgraph_state = state
        
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Completed conversation {conversation_id}: {reason}")
        
        return conversation
    
    def escalate_conversation(
        self,
        conversation_id: UUID,
        to_agent: str,
        reason: str
    ) -> Conversation:
        """
        Escalate conversation to another agent or human.
        
        Args:
            conversation_id: Conversation UUID
            to_agent: Target agent name
            reason: Escalation reason
        
        Returns:
            Updated Conversation object
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation.status = ConversationStatus.ESCALATED
        conversation.escalated_to_agent = to_agent
        
        # Add escalation info to state
        state = conversation.langgraph_state or {}
        state["escalation"] = {
            "from_agent": conversation.primary_agent,
            "to_agent": to_agent,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        conversation.langgraph_state = state
        
        # Add system message
        self.add_message(
            conversation_id=conversation_id,
            role=MessageRole.SYSTEM,
            content=f"Conversation escalated from {conversation.primary_agent} to {to_agent}. Reason: {reason}"
        )
        
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Escalated conversation {conversation_id} to {to_agent}")
        
        return conversation
    
    def get_proactive_suggestions(
        self,
        conversation_id: UUID
    ) -> List[str]:
        """
        Get proactive suggestions based on conversation context.
        
        Args:
            conversation_id: Conversation UUID
        
        Returns:
            List of suggestion strings
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            return []
        
        messages = self.get_conversation_history(conversation_id, limit=5)
        
        if not messages:
            return [
                "שלום! איך אני יכול לעזור לך היום?",
                "האם תרצה לקבוע תור?",
                "יש לך שאלות על טיפולים?"
            ]
        
        # Analyze recent messages for context
        recent_content = " ".join([m.content.lower() for m in messages[-3:]])
        
        suggestions = []
        
        # Appointment-related suggestions
        if any(word in recent_content for word in ["תור", "appointment", "schedule"]):
            suggestions.extend([
                "האם תרצה לראות תורים פנויים?",
                "מתי נוח לך להגיע?",
                "האם תרצה תזכורת לפני התור?"
            ])
        
        # Billing-related suggestions
        elif any(word in recent_content for word in ["מחיר", "כמה עולה", "price", "cost"]):
            suggestions.extend([
                "האם תרצה לראות את מחירון הטיפולים המלא?",
                "יש לנו הנחות למבוטחים",
                "האם תרצה לקבל הצעת מחיר?"
            ])
        
        # General suggestions
        else:
            suggestions.extend([
                "יש לך שאלות נוספות?",
                "האם תרצה לדבר עם רופא?",
                "אני כאן לעזור!"
            ])
        
        return suggestions[:3]  # Return top 3
    
    def delete_conversation(
        self,
        conversation_id: UUID,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete conversation (soft or hard).
        
        Args:
            conversation_id: Conversation UUID
            hard_delete: Permanently delete from database
        
        Returns:
            True if successful
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            return False
        
        if hard_delete:
            # Hard delete (not recommended for compliance)
            self.db.delete(conversation)
            logger.warning(f"Hard deleted conversation {conversation_id}")
        else:
            # Soft delete
            conversation.deleted_at = datetime.utcnow()
            logger.info(f"Soft deleted conversation {conversation_id}")
        
        self.db.commit()
        
        return True


# Convenience function
def get_conversation_manager(db: Session = None) -> ConversationManager:
    """
    Get ConversationManager instance.
    
    Args:
        db: Database session (optional, will create if not provided)
    
    Returns:
        ConversationManager instance
    """
    if db is None:
        db = next(get_db())
    
    return ConversationManager(db)
