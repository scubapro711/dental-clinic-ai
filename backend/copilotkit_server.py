"""
CopilotKit FastAPI Server

This server provides a CopilotKit-compatible endpoint that connects to LangGraph Platform.

Architecture:
Frontend (CopilotKit) → FastAPI (/copilotkit) → LangGraph Platform (port 8000)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ag_ui_langgraph import add_langgraph_fastapi_endpoint, LangGraphAGUIAgent
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CopilotKit Bridge Server")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "copilotkit-bridge"}

# Create LangGraph agent that connects to LangGraph Platform
agent = LangGraphAGUIAgent(
    name="dental_assistant",
    description="AI assistant for dental clinic management",
    # This will connect to LangGraph Platform running on port 8000
    graph_id="dental_assistant",
    url="http://localhost:8000",
)

# Add CopilotKit endpoint
add_langgraph_fastapi_endpoint(
    app=app,
    agent=agent,
    path="/copilotkit",
)

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting CopilotKit Bridge Server on port 8001")
    logger.info("   Connecting to LangGraph Platform at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8001)
