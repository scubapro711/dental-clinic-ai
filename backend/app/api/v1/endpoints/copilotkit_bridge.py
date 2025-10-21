"""
CopilotKit to AG-UI Bridge Endpoint

This module provides a bridge between CopilotKit frontend and AG-UI LangGraph backend.
It translates CopilotKit's protocol to AG-UI's RunAgentInput format.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import json

from app.agents.agent_graph_v5 import agent_graph_v5
from app.agents.graph_state import AgentState
from langchain_core.messages import HumanMessage

router = APIRouter()


class CopilotKitMessage(BaseModel):
    """CopilotKit message format"""
    role: str
    content: str
    id: Optional[str] = None


class CopilotKitRequest(BaseModel):
    """CopilotKit request format"""
    messages: List[CopilotKitMessage]
    threadId: Optional[str] = None


class CopilotKitResponse(BaseModel):
    """CopilotKit response format"""
    messages: List[CopilotKitMessage]
    threadId: str


@router.post("/copilotkit")
async def copilotkit_endpoint(request: dict):
    """
    CopilotKit compatible endpoint that bridges to LangGraph agent.
    
    This endpoint:
    1. Receives CopilotKit format messages
    2. Converts to LangGraph format
    3. Invokes the agent graph
    4. Returns response in CopilotKit format
    """
    print(f"[CopilotKit] Received raw request: {json.dumps(request, indent=2)}")
    try:
        # Parse the request
        messages = request.get("messages", [])
        thread_id = request.get("threadId") or f"thread_{uuid.uuid4().hex[:8]}"
        
        print(f"[CopilotKit] Messages: {messages}")
        print(f"[CopilotKit] Thread ID: {thread_id}")
        
        # Get the last user message
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_message = user_messages[-1].get("content", "")
        
        # Prepare LangGraph input
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        # Create initial state for LangGraph
        initial_state: AgentState = {
            "messages": [HumanMessage(content=last_message)],
            "current_agent": "supervisor",
            "next_agent": None,
            "context": {},
        }
        
        # Invoke the agent graph
        result = agent_graph_v5.graph.invoke(initial_state, config)
        
        # Extract the response
        if result and "messages" in result:
            # Get the last AI message
            ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == "ai"]
            if ai_messages:
                response_content = ai_messages[-1].content
            else:
                response_content = "I'm processing your request..."
        else:
            response_content = "I'm here to help! What would you like to know?"
        
        # Return in CopilotKit format
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": response_content,
                    "id": f"msg_{uuid.uuid4().hex[:8]}"
                }
            ],
            "threadId": thread_id
        }
        
    except Exception as e:
        print(f"Error in copilotkit endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilotkit/stream")
async def copilotkit_stream_endpoint(request: CopilotKitRequest):
    """
    CopilotKit compatible streaming endpoint.
    
    Streams responses from LangGraph agent in real-time.
    """
    try:
        # Generate thread_id if not provided
        thread_id = request.threadId or f"thread_{uuid.uuid4().hex[:8]}"
        
        # Get the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_message = user_messages[-1].content
        
        # Prepare LangGraph input
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        # Create initial state for LangGraph
        initial_state: AgentState = {
            "messages": [HumanMessage(content=last_message)],
            "current_agent": "supervisor",
            "next_agent": None,
            "context": {},
        }
        
        async def event_generator():
            """Generate SSE events for streaming"""
            try:
                # Stream from the agent graph
                async for event in agent_graph_v5.graph.astream(
                    initial_state,
                    config=config
                ):
                    # Extract content from event
                    if isinstance(event, dict):
                        # Check for messages in the event
                        if "messages" in event:
                            messages = event["messages"]
                            if messages:
                                last_msg = messages[-1]
                                if hasattr(last_msg, 'content'):
                                    content = last_msg.content
                                    # Send as SSE
                                    yield f"data: {json.dumps({'content': content, 'threadId': thread_id})}\\n\\n"
                
                # Send completion event
                yield f"data: {json.dumps({'done': True, 'threadId': thread_id})}\\n\\n"
                
            except Exception as e:
                print(f"Error in stream generator: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        print(f"Error in copilotkit stream endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/copilotkit/health")
async def copilotkit_health():
    """Health check for CopilotKit bridge"""
    return {
        "status": "healthy",
        "service": "copilotkit-bridge",
        "agent": "dental_assistant",
        "endpoints": [
            "/api/v1/copilotkit",
            "/api/v1/copilotkit/stream",
            "/api/v1/copilotkit/health"
        ]
    }


@router.get("/copilotkit/info")
async def copilotkit_info():
    """
    CopilotKit info endpoint.
    This is required by CopilotKit frontend to discover the API.
    """
    return {
        "version": "1.0.0",
        "agent": "dental_assistant",
        "capabilities": {
            "streaming": True,
            "threading": True,
            "actions": []
        },
        "endpoints": {
            "chat": "/api/v1/copilotkit",
            "stream": "/api/v1/copilotkit/stream",
            "health": "/api/v1/copilotkit/health"
        }
    }
