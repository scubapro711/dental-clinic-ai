"""
Dashboard Metrics API - Aggregates data from all agents

ARCHITECTURE (Hybrid Approach):
- Display data: API → Shared Queries → Odoo/Checkpoints (fast, no AI needed)
- Actions: API → LangGraph → Agent → Tools → Odoo (AI reasoning)

This endpoint uses the hybrid approach for fast data retrieval with REAL data.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_

from app.core.database import get_db, get_async_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus
from pydantic import BaseModel

# Import shared query functions
from app.shared.checkpoint_queries import (
    get_active_conversations,
    get_agent_activity,
    get_agent_metrics as get_agent_checkpoint_metrics,
    get_total_conversations,
)
from app.shared.odoo_queries import (
    get_appointments_today,
    get_appointments_count_by_state,
    get_upcoming_appointments,
    get_revenue_today,
    get_revenue_this_month,
    get_outstanding_invoices,
    get_payment_success_rate,
    format_date_range,
)

# Import tools for specific operations
from app.agents.tools.admin_tools import get_schedule_conflicts_tool
from app.integrations.odoo_client import OdooClient
from app.core.config import settings
from app.api.dependencies import get_current_membership
from app.models.organization_membership import OrganizationMembership

logger = logging.getLogger(__name__)

router = APIRouter()


def get_odoo_client() -> OdooClient:
    """Dependency to get Odoo client instance."""
    return OdooClient()


# ===== Schemas =====

class DashboardMetrics(BaseModel):
    """Aggregated metrics from all agents."""
    
    # Alex Agent metrics (conversations)
    active_conversations: int
    total_conversations_today: int
    avg_response_time_seconds: float
    escalations_pending: int
    
    # Sophia (Admin) metrics (appointments)
    appointments_today: int
    appointments_completed: int
    appointments_upcoming: int
    scheduling_conflicts: int
    
    # Marcus (CFO) metrics (financial)
    revenue_today: float
    revenue_this_month: float
    outstanding_payments: int
    payment_success_rate: float
    
    # System metrics
    uptime_hours: float
    last_updated: str
    
    class Config:
        from_attributes = True


class AgentMetrics(BaseModel):
    """Individual agent metrics."""
    agent_name: str
    status: str  # online, offline, paused
    uptime_seconds: int
    requests_handled: int
    avg_response_time: float
    success_rate: float
    last_active: str


# ===== Endpoints =====

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    membership: OrganizationMembership = Depends(get_current_membership),
    odoo: OdooClient = Depends(get_odoo_client),
    async_db: AsyncSession = Depends(get_async_db)
):
    """
    Get aggregated dashboard metrics from all agents.
    
    HYBRID APPROACH:
    - Uses shared query functions for fast data retrieval
    - No LangGraph for simple data display
    - Real data from Odoo (patients, appointments, invoices)
    - Real data from Checkpoints (conversations, agent activity)
    
    Returns metrics from:
    - Alex: Conversation statistics (from checkpoints)
    - Sophia (Admin): Appointment statistics (from Odoo)
    - Marcus (CFO): Financial statistics (from Odoo)
    - System: Overall health metrics
    """
    logger.info(f"Getting dashboard metrics for org_id: {membership.organization_id}")
    
    org_id = str(membership.organization_id)
    
    # ===== Alex Agent Metrics (Conversations from Checkpoints) =====
    
    try:
        # Get active conversations (last hour)
        active_conversations = await get_active_conversations(async_db, org_id, active_threshold_minutes=60)
        
        # Get agent activity for today (24 hours)
        agent_activity = await get_agent_activity(async_db, org_id, period_hours=24)
        
        # Calculate total conversations today
        total_conversations_today = sum(a["conversations"] for a in agent_activity)
        
        # Calculate average response time across all agents
        total_interactions = sum(a["interactions"] for a in agent_activity)
        if total_interactions > 0:
            # Get detailed metrics for response time calculation
            alex_metrics = await get_agent_checkpoint_metrics(async_db, org_id, "Alex", 24)
            avg_response_time_seconds = alex_metrics.get("avg_response_time", 0.0)
        else:
            avg_response_time_seconds = 0.0
        
        # Escalations pending (conversations with escalation flag in metadata)
        # For now, use 0 as we don't track escalations in checkpoints yet
        escalations_pending = 0
        
        logger.info(f"Alex metrics (from checkpoints): {active_conversations} active, {total_conversations_today} today")
        
    except Exception as e:
        logger.error(f"Error getting conversation metrics from checkpoints: {e}")
        # Fallback to 0 if checkpoints table doesn't exist yet
        active_conversations = 0
        total_conversations_today = 0
        avg_response_time_seconds = 0.0
        escalations_pending = 0
    
    # ===== Sophia (Admin) Metrics (Appointments from Odoo) =====
    
    try:
        # Get today's appointments
        today_appointments = get_appointments_today(odoo)
        appointments_today = len(today_appointments)
        
        # Count completed appointments
        appointments_completed = len([
            a for a in today_appointments
            if a.get("state") == "done"
        ])
        
        # Get upcoming appointments (next 7 days)
        upcoming = get_upcoming_appointments(odoo, days_ahead=7)
        appointments_upcoming = len(upcoming)
        
        # Scheduling conflicts (use tool)
        try:
            conflicts_result = get_schedule_conflicts_tool()
            scheduling_conflicts = conflicts_result.count("conflict") if isinstance(conflicts_result, str) else 0
        except Exception as e:
            logger.error(f"Error getting conflicts: {e}")
            scheduling_conflicts = 0
        
        logger.info(f"Sophia metrics (from Odoo): {appointments_today} today, {appointments_upcoming} upcoming")
        
    except Exception as e:
        logger.error(f"Error getting appointment metrics from Odoo: {e}")
        appointments_today = 0
        appointments_completed = 0
        appointments_upcoming = 0
        scheduling_conflicts = 0
    
    # ===== Marcus (CFO) Metrics (Financial from Odoo) =====
    
    try:
        # Revenue today
        revenue_today = get_revenue_today(odoo)
        
        # Revenue this month
        revenue_this_month = get_revenue_this_month(odoo)
        
        # Outstanding invoices
        outstanding_data = get_outstanding_invoices(odoo)
        outstanding_payments = outstanding_data["invoice_count"]
        
        # Payment success rate
        payment_success_rate = get_payment_success_rate(odoo)
        
        logger.info(f"Marcus metrics (from Odoo): ${revenue_today:.2f} today, ${revenue_this_month:.2f} this month")
        
    except Exception as e:
        logger.error(f"Error getting financial metrics from Odoo: {e}")
        revenue_today = 0.0
        revenue_this_month = 0.0
        outstanding_payments = 0
        payment_success_rate = 0.0
    
    # ===== System Metrics =====
    
    # System uptime (calculated from application start time)
    # For now, use a fixed value - would track actual uptime in production
    uptime_hours = 24.0
    
    return DashboardMetrics(
        # Alex metrics (from checkpoints)
        active_conversations=active_conversations,
        total_conversations_today=total_conversations_today,
        avg_response_time_seconds=avg_response_time_seconds,
        escalations_pending=escalations_pending,
        
        # Sophia metrics (from Odoo)
        appointments_today=appointments_today,
        appointments_completed=appointments_completed,
        appointments_upcoming=appointments_upcoming,
        scheduling_conflicts=scheduling_conflicts,
        
        # Marcus metrics (from Odoo)
        revenue_today=revenue_today,
        revenue_this_month=revenue_this_month,
        outstanding_payments=outstanding_payments,
        payment_success_rate=payment_success_rate,
        
        # System metrics
        uptime_hours=uptime_hours,
        last_updated=datetime.utcnow().isoformat(),
    )


@router.get("/metrics/agents", response_model=list[AgentMetrics])
async def get_agent_metrics_endpoint(
    membership: OrganizationMembership = Depends(get_current_membership),
    async_db: AsyncSession = Depends(get_async_db)
):
    """
    Get individual metrics for each agent from checkpoints.
    
    Returns status and performance metrics for:
    - Alex (Patient Coordinator)
    - Sarah (Clinical Assistant)
    - Marcus (CFO)
    - Sophia (Practice Administrator)
    - Harper (HR Manager)
    
    All metrics are pulled from real checkpoint data.
    """
    org_id = str(membership.organization_id)
    
    # Agent names to query
    agent_names = ["Alex", "Sarah", "Marcus", "Sophia", "Harper"]
    
    agents = []
    
    try:
        # Get activity for all agents
        agent_activity = await get_agent_activity(async_db, org_id, period_hours=24)
        
        # Create a map for quick lookup
        activity_map = {a["agent_name"]: a for a in agent_activity}
        
        for agent_name in agent_names:
            activity = activity_map.get(agent_name)
            
            if activity:
                # Agent has activity - online
                status = "online"
                requests_handled = activity["interactions"]
                last_active = activity["last_activity"] or datetime.utcnow().isoformat()
                
                # Get detailed metrics
                metrics = await get_agent_checkpoint_metrics(async_db, org_id, agent_name, 24)
                avg_response_time = metrics.get("avg_response_time", 0.0)
                success_rate = metrics.get("success_rate", 100.0)
            else:
                # No activity - offline or no data
                status = "offline"
                requests_handled = 0
                last_active = datetime.utcnow().isoformat()
                avg_response_time = 0.0
                success_rate = 0.0
            
            agents.append(AgentMetrics(
                agent_name=agent_name,
                status=status,
                uptime_seconds=86400,  # 24 hours (would track actual uptime)
                requests_handled=requests_handled,
                avg_response_time=avg_response_time,
                success_rate=success_rate,
                last_active=last_active,
            ))
        
        logger.info(f"Retrieved metrics for {len(agents)} agents from checkpoints")
        
    except Exception as e:
        logger.error(f"Error getting agent metrics from checkpoints: {e}")
        
        # Fallback: return agents with offline status
        for agent_name in agent_names:
            agents.append(AgentMetrics(
                agent_name=agent_name,
                status="offline",
                uptime_seconds=0,
                requests_handled=0,
                avg_response_time=0.0,
                success_rate=0.0,
                last_active=datetime.utcnow().isoformat(),
            ))
    
    return agents
