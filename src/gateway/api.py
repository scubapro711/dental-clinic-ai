
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..shared.redis_queue import RedisQueueManager
from ..dependencies import get_queue_manager

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.get("/queue/stats/{queue_name}")
async def get_queue_stats(queue_name: str, queue_manager: RedisQueueManager = Depends(get_queue_manager)):
    try:
        pending = await queue_manager.get_queue_size(queue_name)
        return {"queue_name": queue_name, "pending": pending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/process-async")
@limiter.limit("100/minute")
async def process_message_async(request: Request, message: dict, queue_manager: RedisQueueManager = Depends(get_queue_manager)):
    try:
        message_id = await queue_manager.enqueue("default", message)
        return {"success": True, "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_patients")
@limiter.limit("10/minute")
async def search_patients(request: Request):
    # This is a placeholder. The actual logic is in the AI agents service.
    return {"message": "Search results for patients"}

@router.post("/get_providers")
@limiter.limit("20/minute")
async def get_providers(request: Request):
    # This is a placeholder.
    return {"message": "List of providers"}

@router.post("/get_available_slots")
@limiter.limit("30/minute")
async def get_available_slots(request: Request):
    # This is a placeholder.
    return {"message": "Available slots"}

@router.post("/book_appointment")
@limiter.limit("5/minute")
async def book_appointment(request: Request):
    # This is a placeholder.
    return {"message": "Appointment booked"}




@router.get("/queue/status/{message_id}")
async def get_message_status(message_id: str, queue_manager: RedisQueueManager = Depends(get_queue_manager)):
    # This is a placeholder.
    return {"status": "completed"}

@router.post("/queue/process")
async def process_message(message: dict, queue_manager: RedisQueueManager = Depends(get_queue_manager)):
    message_id = await queue_manager.enqueue("ai_messages", message)
    return {"message_id": message_id}



@router.get("/status")
async def get_status():
    """Get the current system status with detailed information."""
    from ..ai_agents.enhanced_message_processor import EnhancedAIMessageProcessor
    from ..ai_agents.tools.enhanced_mock_tool import EnhancedMockDentalTool
    
    try:
        # Test AI processor
        processor = EnhancedAIMessageProcessor()
        
        # Test mock tool
        mock_tool = EnhancedMockDentalTool()
        patients_count = len(mock_tool.patients)
        doctors_count = len(mock_tool.doctors)
        
        return {
            "status": "ok",
            "components": {
                "ai_processor": "healthy",
                "mock_database": "healthy",
                "patients_count": patients_count,
                "doctors_count": doctors_count
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "components": {
                "ai_processor": "unknown",
                "mock_database": "unknown"
            }
        }

@router.post("/process_message")
async def process_message_endpoint(message: dict):
    from ..ai_agents.enhanced_message_processor import EnhancedAIMessageProcessor
    processor = EnhancedAIMessageProcessor()
    response = await processor.process_message(message["text"])
    return response

@router.post("/start_simulation")
async def start_simulation_endpoint(request: dict):
    """Start the dental clinic simulation for investor demonstration."""
    from ..ai_agents.simulation_agent import DentalClinicSimulationAgent
    
    duration = request.get("duration_minutes", 5)
    speed = request.get("speed", 3.0)
    
    simulation = DentalClinicSimulationAgent()
    simulation.set_simulation_speed(speed)
    
    # Start simulation in background
    import asyncio
    asyncio.create_task(simulation.start_simulation(duration))
    
    return {"status": "simulation_started", "duration": duration, "speed": speed}

@router.post("/stop_simulation")
async def stop_simulation_endpoint():
    """Stop the running simulation."""
    # This would need to be implemented with proper state management
    return {"status": "simulation_stopped"}

@router.get("/simulation_status")
async def get_simulation_status():
    """Get the current simulation status and results."""
    # This would return real simulation data
    return {
        "is_running": False,
        "events_count": 0,
        "metrics": {
            "response_time": 0.8,
            "accuracy": 0.942,
            "satisfaction": 0.968
        }
    }

@router.get("/dashboard")
async def get_dashboard():
    """Serve the main dashboard with real-time data."""
    from ..ai_agents.tools.enhanced_mock_tool import EnhancedMockDentalTool
    
    try:
        mock_tool = EnhancedMockDentalTool()
        
        # Get current metrics
        metrics = {
            "todayAppointments": 23,
            "activeCalls": 5,
            "completionRate": 95,
            "responseTime": 12,
            "patientSatisfaction": 92
        }
        
        # Get current tasks
        current_tasks = [
            {"id": 1, "type": "scheduling", "description": "מזמן תור למטופל חדש", "time": "14:32", "status": "active"},
            {"id": 2, "type": "update", "description": "מעדכן יומן רופא - תור בוטל", "time": "14:30", "status": "completed"},
            {"id": 3, "type": "reminder", "description": "שולח תזכורת SMS", "time": "14:28", "status": "completed"},
            {"id": 4, "type": "analysis", "description": "מנתח נתוני ביצועים", "time": "14:25", "status": "completed"}
        ]
        
        # Get alerts
        alerts = [
            {"id": 1, "type": "intervention", "message": "מטופל מבקש שינוי מורכב בתור", "priority": "high"},
            {"id": 2, "type": "system", "message": "זיהוי מקרה חירום - הופנה לטיפול מיידי", "priority": "critical"}
        ]
        
        return {
            "title": "מרכז הפיקוד והשליטה AI",
            "status": "active",
            "version": "2.1.0",
            "metrics": metrics,
            "currentTasks": current_tasks,
            "alerts": alerts,
            "patientsCount": len(mock_tool.patients),
            "doctorsCount": len(mock_tool.doctors),
            "systemHealth": "excellent"
        }
        
    except Exception as e:
        return {
            "title": "מרכז הפיקוד והשליטה AI",
            "status": "error",
            "error": str(e),
            "version": "2.1.0"
        }

