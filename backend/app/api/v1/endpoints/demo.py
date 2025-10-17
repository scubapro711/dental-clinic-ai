"""
Demo Chat API Endpoints

Provides Interactive Demo mode for potential customers to try DentaFlow
without creating an account.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime, timedelta

from app.agents.agent_graph_v4 import AgentGraphV4
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

router = APIRouter()


# Demo session storage (in-memory for now, move to Redis in production)
demo_sessions: Dict[str, Dict[str, Any]] = {}


class DemoSessionCreate(BaseModel):
    """Request to create a new demo session."""
    pass


class DemoSessionResponse(BaseModel):
    """Response with demo session information."""
    session_id: str = Field(..., description="Unique demo session ID")
    expires_at: datetime = Field(..., description="Session expiration time")
    message: str = Field(..., description="Welcome message")


class DemoChatMessage(BaseModel):
    """Demo chat message from user."""
    session_id: str = Field(..., description="Demo session ID")
    message: str = Field(..., description="User message")


class DemoChatResponse(BaseModel):
    """Response from demo chat."""
    session_id: str
    message: str
    suggested_actions: Optional[List[str]] = None
    session_active: bool = True
    time_remaining: Optional[int] = None  # seconds


def cleanup_expired_sessions():
    """Remove expired demo sessions."""
    now = datetime.now()
    expired = [sid for sid, session in demo_sessions.items() 
               if session['expires_at'] < now]
    for sid in expired:
        del demo_sessions[sid]
        logger.info(f"Cleaned up expired demo session: {sid}")


@router.post("/session/create", response_model=DemoSessionResponse)
async def create_demo_session():
    """
    Create a new Interactive Demo session.
    
    Demo sessions last 30 minutes and require no authentication.
    Perfect for potential customers to try DentaFlow.
    
    Returns:
        DemoSessionResponse with session ID and expiration
    """
    try:
        # Cleanup expired sessions first
        cleanup_expired_sessions()
        
        # Create new session
        session_id = f"demo_{uuid.uuid4().hex[:12]}"
        expires_at = datetime.now() + timedelta(minutes=30)
        
        # Initialize demo agent graph with in-memory storage (faster, no DB dependency)
        memory_saver = MemorySaver()
        demo_graph = AgentGraphV4(memory=memory_saver, demo_mode=True)
        
        # Store session
        demo_sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.now(),
            'expires_at': expires_at,
            'graph': demo_graph,
            'message_count': 0,
            'conversation_history': [],
        }
        
        logger.info(f"Created demo session: {session_id}")
        
        return DemoSessionResponse(
            session_id=session_id,
            expires_at=expires_at,
            message="Welcome to DentaFlow Interactive Demo! I'm Alex, your AI dental assistant. Try asking me about appointments, patients, or DentaFlow features!"
        )
        
    except Exception as e:
        logger.error(f"Error creating demo session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create demo session: {str(e)}")


@router.post("/chat", response_model=DemoChatResponse)
async def demo_chat(request: DemoChatMessage):
    """
    Send a message in Interactive Demo mode.
    
    Args:
        request: Demo chat message with session ID
        
    Returns:
        DemoChatResponse with Alex's response
    """
    try:
        # Cleanup expired sessions
        cleanup_expired_sessions()
        
        # Validate session
        if request.session_id not in demo_sessions:
            raise HTTPException(status_code=404, detail="Demo session not found or expired. Please create a new session.")
        
        session = demo_sessions[request.session_id]
        
        # Check if session expired
        if session['expires_at'] < datetime.now():
            del demo_sessions[request.session_id]
            raise HTTPException(status_code=410, detail="Demo session expired. Please create a new session.")
        
        # Rate limiting (max 50 messages per session)
        if session['message_count'] >= 50:
            raise HTTPException(status_code=429, detail="Message limit reached for this demo session. Please create a new session.")
        
        # Get agent graph
        demo_graph = session['graph']
        
        # Prepare state
        from app.agents.graph_state import AgentState
        
        state: AgentState = {
            'messages': [HumanMessage(content=request.message)],
            'current_agent': 'supervisor',
            'user_id': f"demo_user_{request.session_id}",
            'organization_id': 'demo_org',
            'conversation_id': request.session_id,
            'patient_id': None,
            'appointment_id': None,
            'invoice_id': None,
            'intent': None,
            'next_agent': None,
            'tool_results': {},
            'errors': [],
            'rate_limit_counters': {},
            'requires_human': False,
            'escalation_level': None,
            'demo_mode': True,  # IMPORTANT!
            'demo_session_id': request.session_id,
        }
        
        # Invoke agent graph
        config = {"configurable": {"thread_id": request.session_id}}
        
        logger.info(f"Demo session {request.session_id}: User message: {request.message}")
        
        result = demo_graph.graph.invoke(state, config)
        
        # Extract response
        if result and 'messages' in result and len(result['messages']) > 0:
            last_message = result['messages'][-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_text = "I'm having trouble processing that. Could you try rephrasing?"
        
        # Update session
        session['message_count'] += 1
        session['conversation_history'].append({
            'user': request.message,
            'alex': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Calculate time remaining
        time_remaining = int((session['expires_at'] - datetime.now()).total_seconds())
        
        # Suggested actions based on conversation
        suggested_actions = []
        if session['message_count'] == 1:
            suggested_actions = [
                "Schedule an appointment",
                "Check patient information",
                "Ask about DentaFlow features",
                "See financial dashboard"
            ]
        elif session['message_count'] > 5 and 'pricing' not in request.message.lower():
            suggested_actions = [
                "Ask about pricing",
                "Learn about the pilot program",
                "Start free trial"
            ]
        
        # Warn if session expiring soon (5 minutes left)
        if time_remaining < 300:
            response_text += f"\n\n⏰ Note: Your demo session expires in {time_remaining // 60} minutes. You can start a free 30-day trial to keep exploring!"
        
        logger.info(f"Demo session {request.session_id}: Alex response: {response_text[:100]}...")
        
        return DemoChatResponse(
            session_id=request.session_id,
            message=response_text,
            suggested_actions=suggested_actions if suggested_actions else None,
            session_active=True,
            time_remaining=time_remaining
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in demo chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/session/{session_id}/status")
async def get_demo_session_status(session_id: str):
    """
    Get status of a demo session.
    
    Args:
        session_id: Demo session ID
        
    Returns:
        Session status information
    """
    try:
        cleanup_expired_sessions()
        
        if session_id not in demo_sessions:
            raise HTTPException(status_code=404, detail="Demo session not found or expired")
        
        session = demo_sessions[session_id]
        time_remaining = int((session['expires_at'] - datetime.now()).total_seconds())
        
        return {
            'session_id': session_id,
            'active': True,
            'created_at': session['created_at'].isoformat(),
            'expires_at': session['expires_at'].isoformat(),
            'time_remaining': time_remaining,
            'message_count': session['message_count'],
            'messages_remaining': 50 - session['message_count']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def end_demo_session(session_id: str):
    """
    End a demo session early.
    
    Args:
        session_id: Demo session ID
        
    Returns:
        Confirmation message
    """
    try:
        if session_id in demo_sessions:
            del demo_sessions[session_id]
            logger.info(f"Demo session ended: {session_id}")
            return {"message": "Demo session ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Demo session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_demo_stats():
    """
    Get demo usage statistics (for internal monitoring).
    
    Returns:
        Demo usage stats
    """
    try:
        cleanup_expired_sessions()
        
        total_sessions = len(demo_sessions)
        total_messages = sum(s['message_count'] for s in demo_sessions.values())
        
        return {
            'active_sessions': total_sessions,
            'total_messages': total_messages,
            'average_messages_per_session': total_messages / total_sessions if total_sessions > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting demo stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

