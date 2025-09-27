"""
Agent Activity Broadcaster - Component 1.2 (Refactored)

This module is responsible for simulating and broadcasting agent activities
to all connected WebSocket clients. It now imports the shared `broadcaster`
instance from the `shared` module to prevent circular dependencies.
"""

import asyncio
import json
import random
import time
from enum import Enum
from dataclasses import dataclass, asdict

# Import the shared broadcaster instance
from .shared import broadcaster

# --- Enums and Dataclasses ---
class AgentStatus(str, Enum):
    IDLE = "idle"
    EXECUTING = "executing"
    THINKING = "thinking"
    HUMAN_HANDOFF = "human_handoff"
    ERROR = "error"

class ActivityType(str, Enum):
    USER_REQUEST = "user_request"
    DATA_ANALYSIS = "data_analysis"
    SYSTEM_OPTIMIZATION = "system_optimization"
    APPOINTMENT_SCHEDULING = "appointment_scheduling"

@dataclass
class AgentActivity:
    activity_id: str
    agent_id: str
    activity_type: ActivityType
    title: str
    description: str
    timestamp: float
    confidence_score: float

# --- Agent Simulation Logic ---
AGENTS = ["dental_agent", "demo_agent", "opendental_agent"]
_agent_tasks = {}
_stop_flag = asyncio.Event()

async def _process_agent_activity(activity: AgentActivity):
    """Simulates processing an activity and broadcasts updates."""
    # 1. Broadcast "EXECUTING" status
    # 1. Update and Broadcast "EXECUTING" status
    if activity.agent_id in _agent_tasks:
        _agent_tasks[activity.agent_id]["status"] = AgentStatus.EXECUTING
    await broadcaster.broadcast({
        "type": "agent_status_update",
        "payload": {"agent_id": activity.agent_id, "status": AgentStatus.EXECUTING}
    })
    
    # Simulate work
    await asyncio.sleep(random.uniform(1, 5))
    
    # 2. Broadcast the activity itself
    await broadcaster.broadcast({
        "type": "agent_activity",
        "payload": asdict(activity)
    })
    
    # 3. Broadcast "IDLE" status
    # 3. Update and Broadcast "IDLE" status
    if activity.agent_id in _agent_tasks:
        _agent_tasks[activity.agent_id]["status"] = AgentStatus.IDLE
    await broadcaster.broadcast({
        "type": "agent_status_update",
        "payload": {"agent_id": activity.agent_id, "status": AgentStatus.IDLE}
    })

async def trigger_human_handoff(agent_id: str, reason: str, context: dict):
    """Triggers and broadcasts a human handoff event."""
    if agent_id in _agent_tasks:
        _agent_tasks[agent_id]["status"] = AgentStatus.HUMAN_HANDOFF
    await broadcaster.broadcast({
        "type": "agent_status_update",
        "payload": {"agent_id": agent_id, "status": AgentStatus.HUMAN_HANDOFF}
    })
    await broadcaster.broadcast({
        "type": "human_handoff_required",
        "payload": {"agent_id": agent_id, "reason": reason, "context": context}
    })

async def _run_agent_simulation(agent_id: str):
    """Main simulation loop for a single agent."""
    while not _stop_flag.is_set():
        await asyncio.sleep(random.uniform(5, 15)) # Wait before starting a new activity
        if _stop_flag.is_set(): break

        activity = AgentActivity(
            activity_id=f"act_{int(time.time())}_{random.randint(100,999)}",
            agent_id=agent_id,
            activity_type=random.choice(list(ActivityType)),
            title=f"Simulated {agent_id} Task",
            description="This is an automated, simulated agent activity.",
            timestamp=time.time(),
            confidence_score=random.uniform(0.8, 1.0)
        )
        await _process_agent_activity(activity)

# --- Public Lifecycle Functions ---
async def start_agent_broadcasting():
    """Starts the simulation for all agents."""
    _stop_flag.clear()
    for agent_id in AGENTS:
        # Register agent by broadcasting its initial IDLE status
        await broadcaster.broadcast({
            "type": "agent_status_update",
            "payload": {"agent_id": agent_id, "status": AgentStatus.IDLE}
        })
        # Start the simulation loop
        task = asyncio.create_task(_run_agent_simulation(agent_id))
        _agent_tasks[agent_id] = {"task": task, "status": AgentStatus.IDLE}
    print(f"Started agent broadcasting for {len(AGENTS)} agents.")

async def stop_agent_broadcasting():
    """Stops all agent simulation tasks."""
    _stop_flag.set()
    tasks = [agent_data['task'] for agent_data in _agent_tasks.values()]
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    _agent_tasks.clear()
    print("Stopped agent broadcasting.")




# --- New Function to Fix Race Condition ---
def get_all_agent_statuses() -> list:
    """Returns the current status payload for all registered agents."""
    statuses = []
    for agent_id, agent_data in _agent_tasks.items():
        statuses.append({
            "agent_id": agent_id,
            "status": agent_data.get("status", AgentStatus.IDLE) # Default to IDLE
        })
    return statuses

