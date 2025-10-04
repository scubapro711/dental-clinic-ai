"""
Logs API - System and agent activity logs

Provides access to system logs and agent activity for monitoring and debugging.

Architecture: Widget → API → Database/Log Store
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from enum import Enum

from app.api.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs", tags=["Logs"])


# ===== Enums =====

class LogLevel(str, Enum):
    """Log severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogSource(str, Enum):
    """Log source."""
    ALEX = "alex"
    MARCUS = "marcus"
    SOPHIA = "sophia"
    SUPERVISOR = "supervisor"
    SYSTEM = "system"
    API = "api"


# ===== Schemas =====

class LogEntry(BaseModel):
    """Log entry model."""
    id: str
    timestamp: str
    level: LogLevel
    source: LogSource
    message: str
    details: Dict[str, Any] | None = None
    user_id: str | None = None
    conversation_id: str | None = None
    
    class Config:
        from_attributes = True


# ===== Endpoints =====

@router.get("/recent", response_model=List[LogEntry])
async def get_recent_logs(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=500),
    level: LogLevel | None = None,
    source: LogSource | None = None,
):
    """
    Get recent system logs.
    
    Args:
        limit: Maximum number of logs to return
        level: Filter by log level
        source: Filter by log source
        
    Returns:
        List of recent log entries
    """
    try:
        # Mock log entries
        # TODO: Replace with real log aggregation from database/logging system
        
        now = datetime.utcnow()
        
        mock_logs = [
            # Alex logs
            LogEntry(
                id="log_001",
                timestamp=(now - timedelta(minutes=2)).isoformat(),
                level=LogLevel.INFO,
                source=LogSource.ALEX,
                message="Processed patient inquiry about appointment availability",
                details={"patient_id": "patient_001", "conversation_id": "conv_123"},
                conversation_id="conv_123"
            ),
            LogEntry(
                id="log_002",
                timestamp=(now - timedelta(minutes=5)).isoformat(),
                level=LogLevel.WARNING,
                source=LogSource.ALEX,
                message="Patient escalation detected - severe pain reported",
                details={"patient_id": "patient_002", "escalation_level": "urgent"},
                conversation_id="conv_124"
            ),
            
            # Marcus logs
            LogEntry(
                id="log_003",
                timestamp=(now - timedelta(minutes=10)).isoformat(),
                level=LogLevel.INFO,
                source=LogSource.MARCUS,
                message="Generated monthly revenue report",
                details={"revenue": 125000, "period": "2025-10"}
            ),
            LogEntry(
                id="log_004",
                timestamp=(now - timedelta(minutes=15)).isoformat(),
                level=LogLevel.WARNING,
                source=LogSource.MARCUS,
                message="Outstanding payments threshold exceeded",
                details={"count": 15, "total_amount": 8450}
            ),
            
            # Sophia logs
            LogEntry(
                id="log_005",
                timestamp=(now - timedelta(minutes=20)).isoformat(),
                level=LogLevel.ERROR,
                source=LogSource.SOPHIA,
                message="Scheduling conflict detected - double booking",
                details={"doctor": "Dr. Smith", "time": "14:00", "date": "2025-10-04"}
            ),
            LogEntry(
                id="log_006",
                timestamp=(now - timedelta(minutes=25)).isoformat(),
                level=LogLevel.INFO,
                source=LogSource.SOPHIA,
                message="Appointment rescheduled successfully",
                details={"appointment_id": 123, "new_date": "2025-10-10"}
            ),
            
            # Supervisor logs
            LogEntry(
                id="log_007",
                timestamp=(now - timedelta(minutes=30)).isoformat(),
                level=LogLevel.INFO,
                source=LogSource.SUPERVISOR,
                message="Routed request to Marcus (CFO) agent",
                details={"intent": "financial_query"}
            ),
            
            # System logs
            LogEntry(
                id="log_008",
                timestamp=(now - timedelta(hours=1)).isoformat(),
                level=LogLevel.INFO,
                source=LogSource.SYSTEM,
                message="System health check completed - all agents online",
                details={"agents": ["alex", "marcus", "sophia"], "status": "healthy"}
            ),
            LogEntry(
                id="log_009",
                timestamp=(now - timedelta(hours=2)).isoformat(),
                level=LogLevel.ERROR,
                source=LogSource.API,
                message="Database connection timeout",
                details={"duration_ms": 5000, "retry_count": 3}
            ),
            LogEntry(
                id="log_010",
                timestamp=(now - timedelta(hours=3)).isoformat(),
                level=LogLevel.INFO,
                source=LogSource.SYSTEM,
                message="Daily backup completed successfully",
                details={"size_mb": 450, "duration_seconds": 120}
            ),
        ]
        
        # Filter by level
        if level:
            mock_logs = [log for log in mock_logs if log.level == level]
        
        # Filter by source
        if source:
            mock_logs = [log for log in mock_logs if log.source == source]
        
        # Limit results
        mock_logs = mock_logs[:limit]
        
        logger.info(f"Retrieved {len(mock_logs)} log entries")
        return mock_logs
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get logs: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_logs_stats(
    current_user: User = Depends(get_current_user),
    hours: int = Query(24, ge=1, le=168),
):
    """
    Get log statistics for the specified time period.
    
    Args:
        hours: Number of hours to analyze (default: 24)
        
    Returns:
        Log statistics by level and source
    """
    try:
        # Mock statistics
        # TODO: Calculate from real logs
        
        return {
            "period_hours": hours,
            "total_logs": 1247,
            "by_level": {
                "debug": 450,
                "info": 680,
                "warning": 95,
                "error": 20,
                "critical": 2
            },
            "by_source": {
                "alex": 420,
                "marcus": 180,
                "sophia": 310,
                "supervisor": 150,
                "system": 120,
                "api": 67
            },
            "error_rate": 1.8,  # percentage
            "last_error": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting log stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get log stats: {str(e)}"
        )
