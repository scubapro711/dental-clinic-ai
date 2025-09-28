"""
Main WebSocket Server Application - Definitive Version (Race Condition Fixed)

This version resolves the race condition by ensuring that every newly connected
client receives the current status of all registered agents immediately upon
connection. This prevents clients from missing initial status updates.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
import time

from src.websocket.shared import broadcaster
from .agent_broadcaster import (
    start_agent_broadcasting,
    stop_agent_broadcasting,
    get_all_agent_statuses, # New function to get current state
    _process_agent_activity, 
    trigger_human_handoff, 
    AgentActivity, 
    ActivityType
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting up, initializing broadcaster...")
    await start_agent_broadcasting()
    yield
    print("Server shutting down, stopping broadcaster...")
    await stop_agent_broadcasting()

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Subscribe first
    await broadcaster.subscribe(websocket)
    
    # --- RACE CONDITION FIX ---
    # Get current agent statuses and send them to the new client
    current_statuses = get_all_agent_statuses()
    for status_payload in current_statuses:
        await websocket.send_json({
            "type": "agent_status_update",
            "payload": status_payload
        })
    # --- END FIX ---

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"Client disconnected: {websocket.client.host}")
    finally:
        await broadcaster.unsubscribe(websocket)

test_router = APIRouter()

@test_router.post("/trigger-activity")
async def trigger_activity_endpoint(activity: dict):
    mock_activity = AgentActivity(
        activity_id=activity.get("activity_id", "test-id"),
        agent_id=activity.get("agent_id", "demo_agent"),
        activity_type=ActivityType[activity.get("activity_type", "USER_REQUEST")],
        title=activity.get("title", "Test Activity"),
        description=activity.get("description", "Triggered by test endpoint"),
        timestamp=time.time(),
        confidence_score=activity.get("confidence_score", 0.95)
    )
    await _process_agent_activity(mock_activity)
    return {"status": "activity_triggered"}

@test_router.post("/trigger-handoff")
async def trigger_handoff_endpoint(handoff_data: dict):
    await trigger_human_handoff(
        agent_id=handoff_data.get("agent_id", "demo_agent"),
        reason=handoff_data.get("reason", "Test handoff reason"),
        context=handoff_data.get("context", {"test": True})
    )
    return {"status": "handoff_triggered"}

app.include_router(test_router, prefix="/testing")

