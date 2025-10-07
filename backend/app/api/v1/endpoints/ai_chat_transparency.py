"""
AI Chat Endpoint with Transparency Events

Enhanced version of ai_chat.py that includes transparency events for the UI:
- agent_start: When an agent begins processing
- agent_progress: Progress updates
- tool_start: When a tool is called
- tool_complete: When a tool finishes
- agent_complete: When an agent finishes

Phase 1: Basic Transparency
"""

import logging
import json
import time
from typing import AsyncGenerator, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends as FastAPIDepends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.agent_graph_v3 import agent_graph_v3
from app.api.dependencies import get_current_user as get_user_obj
from app.agents.utils.guardrails import validate_input
from app.services.conversation_service import conversation_service

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_current_user(user_obj = FastAPIDepends(get_user_obj)) -> Dict[str, Any]:
    """Convert user object to dict for compatibility."""
    return {
        "user_id": str(user_obj.id),
        "organization_id": str(user_obj.organization_id) if user_obj.organization_id else "demo_org",
        "email": user_obj.email,
        "role": user_obj.role.value if hasattr(user_obj.role, 'value') else str(user_obj.role),
    }


# Request/Response Models
class Message(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model compatible with Vercel AI SDK."""
    messages: List[Message] = Field(..., description="List of chat messages")
    conversation_id: str = Field(None, description="Conversation ID for memory")
    stream: bool = Field(True, description="Enable streaming responses")


class StreamChunk(BaseModel):
    """Streaming chunk model with transparency support."""
    type: str = Field(..., description="Chunk type: text, tool_call, agent_start, agent_complete, etc.")
    content: str | None = Field(default=None, description="Text content")
    tool_name: str | None = Field(default=None, description="Tool name for tool_call chunks")
    tool_input: Dict[str, Any] | None = Field(default=None, description="Tool input")
    tool_output: Any | None = Field(default=None, description="Tool output")
    agent: str | None = Field(default=None, description="Agent name")
    task: str | None = Field(default=None, description="Task description")
    progress: int | None = Field(default=None, description="Progress percentage")
    duration: float | None = Field(default=None, description="Duration in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


async def stream_agent_response_with_transparency(
    messages: List[Message],
    conversation_id: str,
    user_id: str,
    organization_id: str,
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses with transparency events.
    
    This enhanced version emits additional events for the UI:
    - agent_start: When an agent begins work
    - tool_start: When a tool is called
    - tool_complete: When a tool finishes
    - agent_complete: When an agent finishes
    
    Args:
        messages: List of chat messages
        conversation_id: Conversation ID for memory
        user_id: User ID
        organization_id: Organization ID
        
    Yields:
        SSE-formatted chunks with transparency events
    """
    try:
        # Convert messages to LangChain format
        langchain_messages = []
        for msg in messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
        
        # Get the last user message
        last_user_message = None
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_message = msg.content
                break
        
        if not last_user_message:
            raise ValueError("No user message found")
        
        # Validate input with guardrails
        is_valid, reasons = validate_input(last_user_message)
        
        if not is_valid:
            error_message = (
                "I'm sorry, but I can't process that request. "
                "Please rephrase your message and try again."
            )
            
            error_chunk = StreamChunk(
                type="text",
                content=error_message,
                metadata={
                    "agent": "system",
                    "conversation_id": conversation_id,
                    "validation_failed": True,
                    "reasons": reasons,
                }
            )
            yield f"data: {error_chunk.model_dump_json()}\n\n"
            
            done_chunk = StreamChunk(
                type="done",
                content="",
                metadata={"conversation_id": conversation_id}
            )
            yield f"data: {done_chunk.model_dump_json()}\n\n"
            
            logger.warning(f"Input validation failed for user {user_id}: {reasons}")
            return
        
        # Setup initial state
        logger.info(f"Starting stream for conversation {conversation_id}")
        
        # Save user message to conversation history
        conversation_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=last_user_message,
            metadata={"user_id": user_id}
        )
        
        user_role = "owner"
        user_permissions = []
        
        initial_state = {
            "messages": langchain_messages,
            "current_agent": "supervisor",
            "user_id": user_id,
            "organization_id": organization_id,
            "conversation_id": conversation_id,
            "user_role": user_role,
            "user_permissions": user_permissions,
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": None,
            "tool_results": {},
            "agent_responses": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
            "escalation_level": None,
        }
        
        # Track state for transparency
        current_agent = None
        agent_start_time = None
        tool_start_times = {}
        final_state = {}
        
        # Stream the graph execution
        async for event in agent_graph_v3.graph.astream(
            initial_state,
            config={"configurable": {"thread_id": conversation_id}},
        ):
            for node_name, node_state in event.items():
                logger.debug(f"Stream event from {node_name}")
                
                # Store the latest state
                final_state = node_state
                
                # Skip supervisor routing (not a real agent response)
                if node_name == "supervisor" and node_state.get("next_agent") != "end":
                    continue
                
                # Emit agent_start event when a new agent starts
                if node_name != current_agent and node_name != "supervisor":
                    current_agent = node_name
                    agent_start_time = time.time()
                    
                    # Determine task description
                    task = "Processing your request..."
                    if node_name == "alex":
                        task = "Handling patient care inquiry..."
                    elif node_name == "cfo":
                        task = "Analyzing financial data..."
                    elif node_name == "admin":
                        task = "Managing administrative tasks..."
                    
                    start_chunk = StreamChunk(
                        type="agent_start",
                        agent=node_name,
                        task=task,
                        metadata={"conversation_id": conversation_id}
                    )
                    yield f"data: {start_chunk.model_dump_json()}\n\n"
                
                # Handle tool calls with transparency
                if "tool_results" in node_state and node_state["tool_results"]:
                    for tool_name, tool_result in node_state["tool_results"].items():
                        # Emit tool_start if we haven't seen this tool yet
                        if tool_name not in tool_start_times:
                            tool_start_times[tool_name] = time.time()
                            
                            tool_start_chunk = StreamChunk(
                                type="tool_start",
                                tool_name=tool_name,
                                metadata={
                                    "agent": node_name,
                                    "conversation_id": conversation_id,
                                }
                            )
                            yield f"data: {tool_start_chunk.model_dump_json()}\n\n"
                        
                        # Emit tool_complete
                        duration = time.time() - tool_start_times.get(tool_name, time.time())
                        
                        tool_complete_chunk = StreamChunk(
                            type="tool_complete",
                            tool_name=tool_name,
                            tool_output=tool_result,
                            duration=round(duration, 2),
                            metadata={
                                "agent": node_name,
                                "conversation_id": conversation_id,
                            }
                        )
                        yield f"data: {tool_complete_chunk.model_dump_json()}\n\n"
                
                # Stream text content
                if "messages" in node_state and node_state["messages"]:
                    latest_message = node_state["messages"][-1]
                    
                    if isinstance(latest_message, AIMessage):
                        content = latest_message.content
                        
                        text_chunk = StreamChunk(
                            type="text",
                            content=content,
                            metadata={
                                "agent": node_name,
                                "conversation_id": conversation_id,
                            }
                        )
                        yield f"data: {text_chunk.model_dump_json()}\n\n"
                        
                        # Handle suggested actions
                        if node_name != "supervisor":
                            from app.agents.utils.action_parser import parse_suggested_actions
                            from app.agents.utils.fallback_actions import generate_fallback_actions
                            
                            suggested_actions = parse_suggested_actions(content)
                            
                            if not suggested_actions and len(node_state["messages"]) >= 2:
                                user_message = node_state["messages"][-2].content if hasattr(node_state["messages"][-2], 'content') else ""
                                suggested_actions = generate_fallback_actions(user_message, content)
                            
                            if suggested_actions:
                                actions_chunk = StreamChunk(
                                    type="suggested_actions",
                                    content="",
                                    metadata={
                                        "conversation_id": conversation_id,
                                        "suggested_actions": suggested_actions
                                    }
                                )
                                yield f"data: {actions_chunk.model_dump_json()}\n\n"
                        
                        # Emit agent_complete
                        if agent_start_time:
                            duration = time.time() - agent_start_time
                            
                            complete_chunk = StreamChunk(
                                type="agent_complete",
                                agent=node_name,
                                duration=round(duration, 2),
                                metadata={
                                    "conversation_id": conversation_id,
                                    "tools_called": len(tool_start_times)
                                }
                            )
                            yield f"data: {complete_chunk.model_dump_json()}\n\n"
        
        # Save assistant response to conversation history
        if final_state and "messages" in final_state and final_state["messages"]:
            latest_message = final_state["messages"][-1]
            if isinstance(latest_message, AIMessage):
                conversation_service.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=latest_message.content,
                    agent_name=current_agent,
                    metadata={"tools_used": list(tool_start_times.keys())}
                )
        
        # Send done signal
        done_chunk = StreamChunk(
            type="done",
            content="",
            metadata={"conversation_id": conversation_id}
        )
        yield f"data: {done_chunk.model_dump_json()}\n\n"
        
        logger.info(f"Stream completed for conversation {conversation_id}")
        
    except Exception as e:
        logger.error(f"Error in stream_agent_response_with_transparency: {e}", exc_info=True)
        error_chunk = StreamChunk(
            type="error",
            content=str(e),
            metadata={"conversation_id": conversation_id}
        )
        yield f"data: {error_chunk.model_dump_json()}\n\n"


@router.post("/chat/transparency")
async def chat_with_transparency(
    request: ChatRequest,
    current_user: Dict[str, Any] = FastAPIDepends(get_current_user)
):
    """
    Chat endpoint with transparency events.
    
    This endpoint provides enhanced streaming with transparency events
    for the UI to display real-time agent activity.
    """
    try:
        conversation_id = request.conversation_id or f"conv_{int(time.time())}"
        
        return StreamingResponse(
            stream_agent_response_with_transparency(
                messages=request.messages,
                conversation_id=conversation_id,
                user_id=current_user["user_id"],
                organization_id=current_user["organization_id"],
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        logger.error(f"Error in chat_with_transparency: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/conversations")
async def list_conversations(
    limit: int = 50,
    current_user: Dict[str, Any] = FastAPIDepends(get_current_user)
):
    """
    List conversations for the current user.
    
    Returns a list of conversation summaries.
    """
    try:
        conversations = conversation_service.list_conversations(
            user_id=current_user["user_id"],
            limit=limit
        )
        
        # Get summaries
        summaries = [
            conversation_service.get_conversation_summary(conv["id"])
            for conv in conversations
        ]
        
        return {"conversations": summaries}
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    current_user: Dict[str, Any] = FastAPIDepends(get_current_user)
):
    """
    Get full conversation history including all messages.
    
    This allows resuming a conversation from where it left off.
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check if user has access
        if conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        messages = conversation_service.get_messages(conversation_id)
        
        return {
            "conversation": conversation,
            "messages": messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = FastAPIDepends(get_current_user)
):
    """
    Delete a conversation.
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check if user has access
        if conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        conversation_service.update_conversation_status(conversation_id, "deleted")
        
        return {"success": True, "message": "Conversation deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
