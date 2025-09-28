"""
Production FastAPI Server for Dental Clinic Management System
Serves the React frontend and provides WebSocket functionality
"""

import os
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Dental Clinic Management System",
    description="Agentic UX Dental Clinic Management with Real-time Agent Monitoring",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.agent_status = {
            "status": "active",
            "current_task": "מזמן תור למטופל חדש",
            "tasks_completed": 47,
            "active_calls": 3,
            "last_activity": datetime.now().isoformat()
        }
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send current status to new connection
        await websocket.send_text(json.dumps({
            "type": "agent_status",
            "data": self.agent_status
        }))
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_activity_update(self, activity: Dict[str, Any]):
        message = json.dumps({
            "type": "activity_update",
            "data": activity
        })
        await self.broadcast(message)
    
    async def update_agent_status(self, status_update: Dict[str, Any]):
        self.agent_status.update(status_update)
        self.agent_status["last_activity"] = datetime.now().isoformat()
        
        message = json.dumps({
            "type": "agent_status",
            "data": self.agent_status
        })
        await self.broadcast(message)

manager = ConnectionManager()

# Sample activities for demo
SAMPLE_ACTIVITIES = [
    {
        "id": 1,
        "agent_id": "dental_agent_1",
        "type": "appointment",
        "status": "completed",
        "title": "תור חדש נקבע לרופא שיניים",
        "description": "תור למטופל חדש נקבע ליום ראשון בשעה 10:00",
        "timestamp": "2024-09-28T14:32:00",
        "duration": 2.3
    },
    {
        "id": 2,
        "agent_id": "dental_agent_1", 
        "type": "patient",
        "status": "in_progress",
        "title": "עדכון יומן רופא",
        "description": "מעדכן זמינות רופא לשבוע הבא",
        "timestamp": "2024-09-28T14:30:00",
        "duration": 1.8
    },
    {
        "id": 3,
        "agent_id": "dental_agent_2",
        "type": "system", 
        "status": "completed",
        "title": "שליחת תזכורת SMS",
        "description": "נשלחה תזכורת למטופל על תור מחר",
        "timestamp": "2024-09-28T14:28:00",
        "duration": 0.5
    },
    {
        "id": 4,
        "agent_id": "dental_agent_1",
        "type": "patient",
        "status": "completed", 
        "title": "ניתוח נתוני ביצועים",
        "description": "הושלם ניתוח ביצועי המרפאה לשבוע האחרון",
        "timestamp": "2024-09-28T14:25:00",
        "duration": 5.2
    },
    {
        "id": 5,
        "agent_id": "dental_agent_2",
        "type": "error",
        "status": "failed",
        "title": "שגיאה בחיבור למערכת חיצונית", 
        "description": "נכשל חיבור למערכת ביטוח חולים",
        "timestamp": "2024-09-28T14:20:00",
        "duration": 0.1
    }
]

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "get_activities":
                await websocket.send_text(json.dumps({
                    "type": "activities",
                    "data": SAMPLE_ACTIVITIES
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API endpoints
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "websocket": "active",
            "database": "connected",
            "agent": "running"
        }
    }

@app.get("/api/agent/status")
async def get_agent_status():
    return manager.agent_status

@app.get("/api/activities")
async def get_activities():
    return {"activities": SAMPLE_ACTIVITIES}

@app.get("/api/statistics")
async def get_statistics():
    return {
        "appointments_today": 56,
        "appointments_change": 12,
        "success_rate": 98.5,
        "success_rate_change": 0.2,
        "avg_treatment_time": "3:05",
        "treatment_time_change": -15,
        "active_calls": 3,
        "total_calls_today": 47,
        "patient_satisfaction": 94,
        "satisfaction_change": 2
    }

# Background task to simulate agent activity
async def simulate_agent_activity():
    """Simulate real-time agent activity for demo purposes"""
    activity_counter = len(SAMPLE_ACTIVITIES) + 1
    
    while True:
        await asyncio.sleep(30)  # Send update every 30 seconds
        
        # Create new activity
        new_activity = {
            "id": activity_counter,
            "agent_id": f"dental_agent_{(activity_counter % 2) + 1}",
            "type": ["appointment", "patient", "system"][activity_counter % 3],
            "status": "completed",
            "title": f"פעילות חדשה #{activity_counter}",
            "description": f"תיאור פעילות אוטומטית מספר {activity_counter}",
            "timestamp": datetime.now().isoformat(),
            "duration": round(1 + (activity_counter % 5), 1)
        }
        
        # Add to activities list (keep only last 20)
        SAMPLE_ACTIVITIES.insert(0, new_activity)
        if len(SAMPLE_ACTIVITIES) > 20:
            SAMPLE_ACTIVITIES.pop()
        
        # Broadcast new activity
        await manager.send_activity_update(new_activity)
        
        # Update agent status
        await manager.update_agent_status({
            "current_task": new_activity["title"],
            "tasks_completed": manager.agent_status["tasks_completed"] + 1
        })
        
        activity_counter += 1

# Startup event
@app.on_event("startup")
async def startup_event():
    # Start background task for agent simulation
    asyncio.create_task(simulate_agent_activity())

# Serve static files (React build)
frontend_path = Path(__file__).parent / "static"
fallback_path = Path(__file__).parent.parent / "dental-clinic-frontend" / "dist"

# Try production static path first, then fallback to dev build
if frontend_path.exists():
    static_path = frontend_path
elif fallback_path.exists():
    static_path = fallback_path
else:
    static_path = None

if static_path:
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(str(static_path / "index.html"))
    
    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        # For SPA routing, always serve index.html for non-API routes
        if not path.startswith("api/") and not path.startswith("ws") and not path.startswith("assets/"):
            return FileResponse(str(static_path / "index.html"))
        raise HTTPException(status_code=404, detail="Not found")

else:
    @app.get("/")
    async def root():
        return {
            "message": "Dental Clinic Management System API",
            "status": "Frontend not built yet",
            "instructions": "Run 'npm run build' in dental-clinic-frontend directory",
            "available_endpoints": [
                "/api/health",
                "/api/agent/status", 
                "/api/activities",
                "/api/statistics",
                "/ws"
            ]
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
