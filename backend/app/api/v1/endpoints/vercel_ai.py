"""
Vercel AI SDK compatible endpoint for LangGraph agents
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.agent_graph_v5 import agent_graph_v5

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str
    id: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    thread_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    role: str
    content: str
    id: str


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint compatible with Vercel AI SDK
    
    Receives messages in Vercel AI SDK format and returns agent response
    """
    try:
        # Convert Vercel AI SDK messages to LangGraph format
        langgraph_messages = []
        for msg in request.messages:
            if msg.role == "user":
                langgraph_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langgraph_messages.append(AIMessage(content=msg.content))
        
        # Invoke LangGraph agent
        config = {"configurable": {"thread_id": request.thread_id}}
        result = agent_graph_v5.graph.invoke(
            {"messages": langgraph_messages},
            config=config
        )
        
        # Extract the last message (agent response)
        last_message = result["messages"][-1]
        
        # Return in Vercel AI SDK format
        return ChatResponse(
            role="assistant",
            content=last_message.content,
            id=f"msg_{len(request.messages)}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint compatible with Vercel AI SDK
    
    Streams agent responses token by token
    """
    async def generate():
        try:
            # Convert messages
            langgraph_messages = []
            for msg in request.messages:
                if msg.role == "user":
                    langgraph_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    langgraph_messages.append(AIMessage(content=msg.content))
            
            # Stream from LangGraph
            config = {"configurable": {"thread_id": request.thread_id}}
            
            async for event in agent_graph_v5.graph.astream(
                {"messages": langgraph_messages},
                config=config
            ):
                # Extract agent messages
                if "messages" in event:
                    messages = event["messages"]
                    if messages:
                        last_message = messages[-1]
                        if isinstance(last_message, AIMessage):
                            # Stream in Vercel AI SDK format
                            chunk = {
                                "type": "text",
                                "content": last_message.content
                            }
                            yield f"data: {json.dumps(chunk)}\n\n"
            
            # End of stream
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_chunk = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "vercel-ai-endpoint"}
