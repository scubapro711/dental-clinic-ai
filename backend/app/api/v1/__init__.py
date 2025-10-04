"""
API v1 router configuration.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, chat, telegram, statistics, monitoring, websocket, dashboard, handoff, conversations, dashboard_metrics, agents, alerts, logs

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(conversations.router, tags=["conversations"])
api_router.include_router(agents.router, tags=["agents"])
api_router.include_router(alerts.router, tags=["alerts"])
api_router.include_router(logs.router, tags=["logs"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(dashboard_metrics.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(handoff.router, prefix="/handoff", tags=["handoff"])

__all__ = ["api_router"]
