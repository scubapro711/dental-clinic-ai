"""
Checkpoint query functions for agent metrics and activity tracking.

This module provides async functions to query LangGraph checkpoint data stored in PostgreSQL.
The checkpoints table stores conversation state, agent interactions, and metadata.

All functions use async/await for non-blocking database operations.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_agent_activity(
    db: AsyncSession,
    org_id: str,
    period_hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Get agent activity metrics from checkpoints.
    
    Args:
        db: Async database session
        org_id: Organization ID to filter by
        period_hours: Time period in hours (default: 24)
    
    Returns:
        List of agent activity metrics with:
        - agent_name: Name of the agent
        - conversations: Number of unique conversations
        - interactions: Total number of interactions
        - last_activity: Timestamp of last activity
    
    Example:
        >>> activity = await get_agent_activity(db, "org_123", 24)
        >>> print(activity)
        [
            {
                "agent_name": "Alex",
                "conversations": 15,
                "interactions": 45,
                "last_activity": "2025-11-12T10:30:00Z"
            },
            ...
        ]
    """
    query = text("""
        SELECT 
            metadata->>'agent_name' as agent_name,
            COUNT(DISTINCT thread_id) as conversations,
            COUNT(*) as interactions,
            MAX((checkpoint->>'ts')::timestamp) as last_activity
        FROM checkpoints
        WHERE metadata->>'org_id' = :org_id
          AND (checkpoint->>'ts')::timestamp > NOW() - INTERVAL '1 hour' * :period
        GROUP BY metadata->>'agent_name'
        ORDER BY conversations DESC
    """)
    
    result = await db.execute(query, {"org_id": org_id, "period": period_hours})
    rows = result.fetchall()
    
    return [
        {
            "agent_name": row.agent_name or "Unknown",
            "conversations": int(row.conversations),
            "interactions": int(row.interactions),
            "last_activity": row.last_activity.isoformat() if row.last_activity else None
        }
        for row in rows
    ]


async def get_active_conversations(
    db: AsyncSession,
    org_id: str,
    active_threshold_minutes: int = 60
) -> int:
    """
    Get count of active conversations (conversations with recent activity).
    
    Args:
        db: Async database session
        org_id: Organization ID to filter by
        active_threshold_minutes: Minutes since last activity to consider active (default: 60)
    
    Returns:
        Count of active conversations
    
    Example:
        >>> count = await get_active_conversations(db, "org_123", 60)
        >>> print(count)
        5
    """
    query = text("""
        SELECT COUNT(DISTINCT thread_id)
        FROM checkpoints
        WHERE metadata->>'org_id' = :org_id
          AND (checkpoint->>'ts')::timestamp > NOW() - INTERVAL '1 minute' * :threshold
    """)
    
    result = await db.execute(query, {"org_id": org_id, "threshold": active_threshold_minutes})
    row = result.fetchone()
    
    return int(row[0]) if row else 0


async def get_agent_metrics(
    db: AsyncSession,
    org_id: str,
    agent_name: str,
    period_hours: int = 24
) -> Dict[str, Any]:
    """
    Get detailed metrics for a specific agent.
    
    Args:
        db: Async database session
        org_id: Organization ID to filter by
        agent_name: Name of the agent (e.g., "Alex", "Sarah", "Marcus")
        period_hours: Time period in hours (default: 24)
    
    Returns:
        Dictionary with agent metrics:
        - total_conversations: Total unique conversations
        - total_interactions: Total interactions
        - avg_response_time: Average response time in seconds
        - success_rate: Success rate percentage
        - last_activity: Timestamp of last activity
    
    Example:
        >>> metrics = await get_agent_metrics(db, "org_123", "Alex", 24)
        >>> print(metrics)
        {
            "total_conversations": 15,
            "total_interactions": 45,
            "avg_response_time": 2.5,
            "success_rate": 95.5,
            "last_activity": "2025-11-12T10:30:00Z"
        }
    """
    query = text("""
        SELECT 
            COUNT(DISTINCT thread_id) as total_conversations,
            COUNT(*) as total_interactions,
            MAX((checkpoint->>'ts')::timestamp) as last_activity,
            AVG(
                CASE 
                    WHEN metadata->>'response_time' IS NOT NULL 
                    THEN (metadata->>'response_time')::float 
                    ELSE NULL 
                END
            ) as avg_response_time,
            AVG(
                CASE 
                    WHEN metadata->>'success' = 'true' THEN 100.0
                    WHEN metadata->>'success' = 'false' THEN 0.0
                    ELSE NULL
                END
            ) as success_rate
        FROM checkpoints
        WHERE metadata->>'org_id' = :org_id
          AND metadata->>'agent_name' = :agent_name
          AND (checkpoint->>'ts')::timestamp > NOW() - INTERVAL '1 hour' * :period
    """)
    
    result = await db.execute(query, {
        "org_id": org_id,
        "agent_name": agent_name,
        "period": period_hours
    })
    row = result.fetchone()
    
    if not row or row.total_conversations is None:
        return {
            "total_conversations": 0,
            "total_interactions": 0,
            "avg_response_time": 0.0,
            "success_rate": 0.0,
            "last_activity": None
        }
    
    return {
        "total_conversations": int(row.total_conversations) if row.total_conversations else 0,
        "total_interactions": int(row.total_interactions) if row.total_interactions else 0,
        "avg_response_time": float(row.avg_response_time) if row.avg_response_time else 0.0,
        "success_rate": float(row.success_rate) if row.success_rate else 0.0,
        "last_activity": row.last_activity.isoformat() if row.last_activity else None
    }


async def get_conversation_history(
    db: AsyncSession,
    thread_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get conversation history for a specific thread.
    
    Args:
        db: Async database session
        thread_id: Thread ID to get history for
        limit: Maximum number of checkpoints to return (default: 50)
    
    Returns:
        List of checkpoints with conversation data
    
    Example:
        >>> history = await get_conversation_history(db, "user_123_session_456", 50)
        >>> print(history)
        [
            {
                "checkpoint_id": "uuid-123",
                "timestamp": "2025-11-12T10:30:00Z",
                "agent_name": "Alex",
                "messages": [...],
                "metadata": {...}
            },
            ...
        ]
    """
    query = text("""
        SELECT 
            checkpoint_id,
            (checkpoint->>'ts')::timestamp as timestamp,
            metadata->>'agent_name' as agent_name,
            checkpoint->'channel_values'->'messages' as messages,
            metadata
        FROM checkpoints
        WHERE thread_id = :thread_id
        ORDER BY (checkpoint->>'ts')::timestamp DESC
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"thread_id": thread_id, "limit": limit})
    rows = result.fetchall()
    
    return [
        {
            "checkpoint_id": row.checkpoint_id,
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            "agent_name": row.agent_name or "Unknown",
            "messages": row.messages,
            "metadata": row.metadata
        }
        for row in rows
    ]


async def get_total_conversations(
    db: AsyncSession,
    org_id: str,
    period_hours: Optional[int] = None
) -> int:
    """
    Get total number of conversations for an organization.
    
    Args:
        db: Async database session
        org_id: Organization ID to filter by
        period_hours: Optional time period in hours (None = all time)
    
    Returns:
        Total number of unique conversations
    
    Example:
        >>> total = await get_total_conversations(db, "org_123", 24)
        >>> print(total)
        42
    """
    if period_hours:
        query = text("""
            SELECT COUNT(DISTINCT thread_id)
            FROM checkpoints
            WHERE metadata->>'org_id' = :org_id
              AND (checkpoint->>'ts')::timestamp > NOW() - INTERVAL '1 hour' * :period
        """)
        result = await db.execute(query, {"org_id": org_id, "period": period_hours})
    else:
        query = text("""
            SELECT COUNT(DISTINCT thread_id)
            FROM checkpoints
            WHERE metadata->>'org_id' = :org_id
        """)
        result = await db.execute(query, {"org_id": org_id})
    
    row = result.fetchone()
    return int(row[0]) if row else 0


async def get_agent_utilization(
    db: AsyncSession,
    org_id: str,
    period_hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Get agent utilization metrics (percentage of total interactions).
    
    Args:
        db: Async database session
        org_id: Organization ID to filter by
        period_hours: Time period in hours (default: 24)
    
    Returns:
        List of agent utilization metrics with percentages
    
    Example:
        >>> utilization = await get_agent_utilization(db, "org_123", 24)
        >>> print(utilization)
        [
            {"agent_name": "Alex", "interactions": 45, "percentage": 35.0},
            {"agent_name": "Sarah", "interactions": 30, "percentage": 23.4},
            ...
        ]
    """
    query = text("""
        WITH agent_counts AS (
            SELECT 
                metadata->>'agent_name' as agent_name,
                COUNT(*) as interactions
            FROM checkpoints
            WHERE metadata->>'org_id' = :org_id
              AND (checkpoint->>'ts')::timestamp > NOW() - INTERVAL '1 hour' * :period
            GROUP BY metadata->>'agent_name'
        ),
        total_count AS (
            SELECT SUM(interactions) as total
            FROM agent_counts
        )
        SELECT 
            ac.agent_name,
            ac.interactions,
            ROUND((ac.interactions::float / NULLIF(tc.total, 0)::float * 100), 2) as percentage
        FROM agent_counts ac
        CROSS JOIN total_count tc
        ORDER BY ac.interactions DESC
    """)
    
    result = await db.execute(query, {"org_id": org_id, "period": period_hours})
    rows = result.fetchall()
    
    return [
        {
            "agent_name": row.agent_name or "Unknown",
            "interactions": int(row.interactions),
            "percentage": float(row.percentage) if row.percentage else 0.0
        }
        for row in rows
    ]


async def get_recent_agent_activity(
    db: AsyncSession,
    org_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get recent agent activity (latest interactions).
    
    Args:
        db: Async database session
        org_id: Organization ID to filter by
        limit: Maximum number of activities to return (default: 10)
    
    Returns:
        List of recent activities
    
    Example:
        >>> recent = await get_recent_agent_activity(db, "org_123", 10)
        >>> print(recent)
        [
            {
                "timestamp": "2025-11-12T10:30:00Z",
                "agent_name": "Alex",
                "thread_id": "user_123_session_456",
                "action": "message_sent"
            },
            ...
        ]
    """
    query = text("""
        SELECT 
            (checkpoint->>'ts')::timestamp as timestamp,
            metadata->>'agent_name' as agent_name,
            thread_id,
            metadata->>'action' as action,
            metadata->>'user_id' as user_id
        FROM checkpoints
        WHERE metadata->>'org_id' = :org_id
        ORDER BY (checkpoint->>'ts')::timestamp DESC
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"org_id": org_id, "limit": limit})
    rows = result.fetchall()
    
    return [
        {
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            "agent_name": row.agent_name or "Unknown",
            "thread_id": row.thread_id,
            "action": row.action or "interaction",
            "user_id": row.user_id
        }
        for row in rows
    ]


async def check_checkpoints_table_exists(db: AsyncSession) -> bool:
    """
    Check if checkpoints table exists in the database.
    
    Args:
        db: Async database session
    
    Returns:
        True if table exists, False otherwise
    
    Example:
        >>> exists = await check_checkpoints_table_exists(db)
        >>> print(exists)
        True
    """
    query = text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'checkpoints'
        )
    """)
    
    result = await db.execute(query)
    row = result.fetchone()
    
    return bool(row[0]) if row else False
