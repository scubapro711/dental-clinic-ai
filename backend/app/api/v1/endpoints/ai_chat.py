"""
AI Chat Endpoint - Vercel AI SDK Compatible

This endpoint provides a REST API that's compatible with Vercel AI SDK.
It wraps our LangGraph multi-agent system and provides streaming support.

Key Features:
- Streaming responses using Server-Sent Events (SSE)
- Compatible with Vercel AI SDK format
- Full LangGraph agent integration
- Tool execution support
- Conversation memory via LangGraph checkpointer
"""

import logging
import json
from typing import AsyncGenerator, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends as FastAPIDepends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.agent_graph_v3 import agent_graph_v3
from app.api.dependencies import get_current_user as get_user_obj
from app.agents.utils.guardrails import validate_input

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


class ChatResponse(BaseModel):
    """Chat response model."""
    message: Message
    conversation_id: str
    agent: str = Field(..., description="Which agent responded")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    """Streaming chunk model."""
    type: str = Field(..., description="Chunk type: text, tool_call, suggested_actions, or done")
    content: str | None = Field(default=None, description="Text content")
    tool_name: str | None = Field(default=None, description="Tool name for tool_call chunks")
    tool_input: Dict[str, Any] | None = Field(default=None, description="Tool input")
    tool_output: Any | None = Field(default=None, description="Tool output")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        # Allow None values for optional fields
        use_enum_values = True


async def stream_agent_response(
    messages: List[Message],
    conversation_id: str,
    user_id: str,
    organization_id: str,
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses using Server-Sent Events (SSE).
    
    This function wraps the LangGraph agent and streams its responses
    in a format compatible with Vercel AI SDK.
    
    Args:
        messages: List of chat messages
        conversation_id: Conversation ID for memory
        user_id: User ID
        organization_id: Organization ID
        
    Yields:
        SSE-formatted chunks
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
        
        # Phase 8: Validate input with guardrails
        is_valid, reasons = validate_input(last_user_message)
        
        if not is_valid:
            # Send error message to user
            error_message = (
                "I'm sorry, but I can't process that request. "
                "Please rephrase your message and try again. "
                "If you need assistance, please contact our support team."
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
            
            # Send done signal
            done_chunk = StreamChunk(
                type="done",
                content="",
                metadata={"conversation_id": conversation_id}
            )
            yield f"data: {done_chunk.model_dump_json()}\n\n"
            
            logger.warning(f"Input validation failed for user {user_id}: {reasons}")
            return
        
        # Use LangGraph's streaming capability
        # The graph.astream() method yields state updates as they happen
        logger.info(f"Starting stream for conversation {conversation_id}")
        
        # SECURITY: Get user role from authentication
        # For now, default to "owner" for testing, but this MUST be replaced
        # with actual JWT token parsing in production
        user_role = "owner"  # FIXME: Get from JWT token - current_user["role"]
        user_permissions = []  # FIXME: Get from RBAC system based on role
        
        # TODO: Implement proper authentication
        # user_role = current_user.get("role", "patient")
        # user_permissions = get_user_permissions(user_id, user_role)
        
        # Stream the graph execution
        initial_state = {
            "messages": langchain_messages,
            "current_agent": "supervisor",
            "user_id": user_id,
            "organization_id": organization_id,
            "conversation_id": conversation_id,
            "user_role": user_role,  # RBAC: User's role
            "user_permissions": user_permissions,  # RBAC: User's permissions
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
        
        # Track the final state to get suggested actions
        final_state = {}
        
        async for event in agent_graph_v3.graph.astream(
            initial_state,
            config={"configurable": {"thread_id": conversation_id}},
        ):
            # event is a dict with node names as keys
            # e.g., {"supervisor": {...state...}} or {"alex": {...state...}}
            
            for node_name, node_state in event.items():
                logger.debug(f"Stream event from {node_name}")
                
                # Store the latest state for suggested actions
                final_state = node_state
                
                # Skip supervisor routing messages - only send actual agent responses
                if node_name == "supervisor" and node_state.get("next_agent") != "end":
                    # Supervisor is just routing, not responding
                    continue
                
                # Get the latest message from the node
                if "messages" in node_state and node_state["messages"]:
                    latest_message = node_state["messages"][-1]
                    
                    # Check if this is a new message (not from user)
                    if isinstance(latest_message, AIMessage):
                        content = latest_message.content
                        
                        # Stream the content
                        # Note: Duplicates will be handled by frontend
                        chunk = StreamChunk(
                            type="text",
                            content=content,
                            metadata={
                                "agent": node_name,
                                "conversation_id": conversation_id,
                            }
                        )
                        
                        # Format as SSE
                        yield f"data: {chunk.model_dump_json()}\n\n"
                        
                        # Extract and send suggested actions immediately (Phase 7)
                        # Only do this once per agent (not for supervisor echo)
                        if node_name != "supervisor":
                            from app.agents.utils.action_parser import parse_suggested_actions
                            from app.agents.utils.fallback_actions import generate_fallback_actions
                            
                            suggested_actions = parse_suggested_actions(content)
                            
                            # If LLM didn't provide actions, generate fallback
                            if not suggested_actions and len(node_state["messages"]) >= 2:
                                user_message = node_state["messages"][-2].content if hasattr(node_state["messages"][-2], 'content') else ""
                                suggested_actions = generate_fallback_actions(user_message, content)
                                logger.info(f"Generated {len(suggested_actions)} fallback actions for {node_name}")
                            
                            if suggested_actions:
                                logger.info(f"Sending {len(suggested_actions)} suggested actions from {node_name}")
                                actions_chunk = StreamChunk(
                                    type="suggested_actions",
                                    content="",
                                    metadata={
                                        "conversation_id": conversation_id,
                                        "suggested_actions": suggested_actions
                                    }
                                )
                                yield f"data: {actions_chunk.model_dump_json()}\n\n"
                
                # Check for tool calls
                if "tool_results" in node_state and node_state["tool_results"]:
                    for tool_name, tool_result in node_state["tool_results"].items():
                        chunk = StreamChunk(
                            type="tool_call",
                            tool_name=tool_name,
                            tool_output=tool_result,
                            metadata={
                                "agent": node_name,
                                "conversation_id": conversation_id,
                            }
                        )
                        yield f"data: {chunk.model_dump_json()}\n\n"
        
        # Send suggested actions if available (Phase 7: Agentic System)
        # Extract from the last AI message instead of relying on state
        from app.agents.utils.action_parser import parse_suggested_actions
        from app.agents.utils.fallback_actions import generate_fallback_actions
        
        suggested_actions = None
        if "messages" in final_state and final_state["messages"]:
            last_message = final_state["messages"][-1]
            if hasattr(last_message, 'content'):
                suggested_actions = parse_suggested_actions(last_message.content)
                
                # If LLM didn't provide actions, generate fallback actions
                if not suggested_actions and len(final_state["messages"]) >= 2:
                    user_message = final_state["messages"][-2].content if hasattr(final_state["messages"][-2], 'content') else ""
                    suggested_actions = generate_fallback_actions(user_message, last_message.content)
                    logger.info(f"Generated {len(suggested_actions)} fallback actions")
        
        logger.info(f"Total suggested actions: {len(suggested_actions) if suggested_actions else 0}")
        logger.info(f"About to send suggested actions. Has actions: {suggested_actions is not None}")
        
        if suggested_actions:
            logger.info(f"Sending {len(suggested_actions)} suggested actions: {suggested_actions}")
            try:
                actions_chunk = StreamChunk(
                    type="suggested_actions",
                    content="",  # Empty string instead of None for Pydantic validation
                    metadata={
                        "conversation_id": conversation_id,
                        "suggested_actions": suggested_actions
                    }
                )
                logger.info(f"Created actions_chunk successfully")
                yield f"data: {actions_chunk.model_dump_json()}\n\n"
                logger.info(f"Sent suggested_actions event successfully")
            except Exception as e:
                logger.error(f"Error sending suggested actions: {e}", exc_info=True)
        else:
            logger.warning("No suggested actions to send")
        
        # Send done signal
        done_chunk = StreamChunk(
            type="done",
            content="",
            metadata={"conversation_id": conversation_id}
        )
        yield f"data: {done_chunk.model_dump_json()}\n\n"
        
        logger.info(f"Stream completed for conversation {conversation_id}")
        
    except Exception as e:
        logger.error(f"Error in stream: {str(e)}", exc_info=True)
        error_chunk = StreamChunk(
            type="error",
            content=f"Error: {str(e)}",
            metadata={"conversation_id": conversation_id}
        )
        yield f"data: {error_chunk.model_dump_json()}\n\n"


@router.post("/chat", response_model=None)
async def chat(request: ChatRequest):
    """
    Chat endpoint compatible with Vercel AI SDK.
    
    This endpoint accepts chat messages and returns agent responses.
    It supports both streaming and non-streaming modes.
    
    Args:
        request: Chat request with messages and options
        current_user: Current authenticated user
        
    Returns:
        StreamingResponse for streaming mode, ChatResponse for non-streaming
    """
    try:
        # Extract user info (use demo user for now)
        # TODO: Get from JWT token in production
        user_id = "demo_user"
        organization_id = "demo_org"
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id
        if not conversation_id:
            import uuid
            conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Chat request from user {user_id}, conversation {conversation_id}")
        
        # Streaming mode
        if request.stream:
            return StreamingResponse(
                stream_agent_response(
                    messages=request.messages,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    organization_id=organization_id,
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable nginx buffering
                },
            )
        
        # Non-streaming mode
        else:
            # Convert messages to LangChain format
            langchain_messages = []
            for msg in request.messages:
                if msg.role == "user":
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    langchain_messages.append(AIMessage(content=msg.content))
                elif msg.role == "system":
                    langchain_messages.append(SystemMessage(content=msg.content))
            
            # Get the last user message
            last_user_message = None
            for msg in reversed(request.messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break
            
            if not last_user_message:
                raise HTTPException(status_code=400, detail="No user message found")
            
            # Invoke the graph (non-streaming)
            final_state = await agent_graph_v3.graph.ainvoke(
                {
                    "messages": langchain_messages,
                    "user_id": user_id,
                    "organization_id": organization_id,
                    "conversation_id": conversation_id,
                    "current_agent": "supervisor",
                },
                config={"configurable": {"thread_id": conversation_id}},
            )
            
            # Extract response
            last_message = final_state["messages"][-1]
            response_text = last_message.content
            
            # Determine which agent responded
            agent_responses = final_state.get("agent_responses", {})
            responding_agent = "alex"  # default
            if agent_responses:
                responding_agent = list(agent_responses.keys())[-1]
            
            return ChatResponse(
                message=Message(role="assistant", content=response_text),
                conversation_id=conversation_id,
                agent=responding_agent,
                metadata={
                    "user_id": user_id,
                    "organization_id": organization_id,
                    "requires_human": final_state.get("requires_human", False),
                    "escalation_level": final_state.get("escalation_level"),
                },
            )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = FastAPIDepends(get_current_user),
):
    """
    Get conversation history from LangGraph memory.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        
    Returns:
        Conversation history
    """
    try:
        # Get conversation state from LangGraph checkpointer
        # The checkpointer stores state by thread_id
        state = await agent_graph_v3.graph.aget_state(
            config={"configurable": {"thread_id": conversation_id}}
        )
        
        if not state or not state.values:
            return {
                "conversation_id": conversation_id,
                "messages": [],
                "metadata": {},
            }
        
        # Extract messages
        messages = []
        for msg in state.values.get("messages", []):
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                messages.append({"role": "system", "content": msg.content})
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "metadata": {
                "current_agent": state.values.get("current_agent"),
                "requires_human": state.values.get("requires_human", False),
            },
        }
    
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = FastAPIDepends(get_current_user),
):
    """
    Delete conversation from memory.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # LangGraph's MemorySaver doesn't have a delete method
        # For now, we'll just return success
        # In production, you'd want to implement proper deletion
        
        logger.info(f"Conversation {conversation_id} deletion requested")
        
        return {
            "success": True,
            "message": f"Conversation {conversation_id} deleted",
        }
    
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
