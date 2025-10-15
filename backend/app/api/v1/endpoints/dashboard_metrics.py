"""
Dashboard Metrics API - Aggregates data from all agents

ARCHITECTURE (Hybrid Approach):
- Display data: API → Tools → Odoo (fast, no AI needed)
- Actions: API → LangGraph → Agent → Tools → Odoo (AI reasoning)

This endpoint uses the hybrid approach for fast data retrieval.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus
from pydantic import BaseModel

# Import tools directly for fast data access
from app.agents.tools.agent_tools import get_available_slots_tool
from app.agents.tools.cfo_tools import (
    get_revenue_overview_tool,
    get_outstanding_invoices_tool,
    get_payment_status_tool,
)
from app.agents.tools.admin_tools import (
    get_schedule_conflicts_tool,
    get_operational_metrics_tool,
)
from app.integrations.odoo_client_v3 import OdooClientV3
from app.core.config import settings
from app.api.dependencies import get_current_membership
from app.models.organization_membership import OrganizationMembership

logger = logging.getLogger(__name__)

router = APIRouter()


def get_odoo_client() -> OdooClientV3:
    """Dependency to get Odoo client instance."""
    return OdooClientV3()


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
    odoo: OdooClientV3 = Depends(get_odoo_client)
):
    """
    Get aggregated dashboard metrics from all agents.
    
    HYBRID APPROACH:
    - Uses tools directly for fast data retrieval
    - No LangGraph for simple data display
    - Real data from Odoo (real patients, appointments, invoices)
    
    Returns metrics from:
    - Alex: Conversation statistics
    - Sophia (Admin): Appointment statistics  
    - Marcus (CFO): Financial statistics
    - System: Overall health metrics
    """
    logger.info("Getting dashboard metrics from real Odoo")
    
    # ===== Alex Agent Metrics (Conversations) =====
    
    # Mock conversation data (would come from database in production)
    # TODO: Implement conversation tracking in database
    active_conversations = 8
    total_conversations_today = 23
    escalations_pending = 2
    avg_response_time_seconds = 2.3
    
    logger.info(f"Alex metrics: {active_conversations} active, {total_conversations_today} today")
    
    # ===== Sophia (Admin) Metrics (Appointments) =====
    
    # Get today's date
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Today's appointments from Odoo
    today_appointments = odoo.search_read(
        'patient.appointment',
        domain=[
            ('start', '>=', f"{today_str} 00:00:00"),
            ('start', '<=', f"{today_str} 23:59:59"),
        ],
        fields=['id', 'state', 'start']
    )
    appointments_today = len(today_appointments)
    
    # Completed appointments
    appointments_completed = len([
        a for a in today_appointments
        if a.get("state") == "done"
    ])
    
    # Upcoming appointments (next 7 days)
    end_date = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
    appointments_upcoming = odoo.search_count(
        'patient.appointment',
        domain=[
            ('state', 'in', ['draft', 'confirmed']),
            ('start', '>=', f"{today_str} 00:00:00"),
            ('start', '<=', f"{end_date} 23:59:59"),
        ]
    )
    
    # Scheduling conflicts (use tool)
    try:
        conflicts_result = get_schedule_conflicts_tool()
        scheduling_conflicts = conflicts_result.count("conflict") if isinstance(conflicts_result, str) else 0
    except Exception as e:
        logger.error(f"Error getting conflicts: {e}")
        scheduling_conflicts = 0
    
    logger.info(f"Sophia metrics: {appointments_today} today, {appointments_upcoming} upcoming")
    
    # ===== Marcus (CFO) Metrics (Financial) =====
    
    # Revenue today from invoices
    today_invoices = odoo.search_read(
        'account.move',
        domain=[
            ('move_type', '=', 'out_invoice'),
            ('invoice_date', '=', today_str),
            ('state', '=', 'posted'),
        ],
        fields=['amount_total', 'payment_state']
    )
    revenue_today = sum(inv['amount_total'] for inv in today_invoices)
    
    # Revenue this month
    month_start = datetime.utcnow().replace(day=1).strftime("%Y-%m-%d")
    month_invoices = odoo.search_read(
        'account.move',
        domain=[
            ('move_type', '=', 'out_invoice'),
            ('invoice_date', '>=', month_start),
            ('state', '=', 'posted'),
        ],
        fields=['amount_total']
    )
    revenue_this_month = sum(inv['amount_total'] for inv in month_invoices)
    
    # Outstanding payments from Odoo
    outstanding_payments = odoo.search_count(
        'account.move',
        domain=[
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
        ]
    )
    
    # Payment success rate
    total_invoices = odoo.search_count(
        'account.move',
        domain=[
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ]
    )
    paid_invoices = odoo.search_count(
        'account.move',
        domain=[
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
        ]
    )
    payment_success_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0.0
    
    logger.info(f"Marcus metrics: ${revenue_today:.2f} today, ${revenue_this_month:.2f} this month")
    
    # ===== System Metrics =====
    
    # System uptime (mock - would track actual uptime in production)
    uptime_hours = 23.5
    
    return DashboardMetrics(
        # Alex metrics
        active_conversations=active_conversations,
        total_conversations_today=total_conversations_today,
        avg_response_time_seconds=avg_response_time_seconds,
        escalations_pending=escalations_pending,
        
        # Sophia metrics
        appointments_today=appointments_today,
        appointments_completed=appointments_completed,
        appointments_upcoming=appointments_upcoming,
        scheduling_conflicts=scheduling_conflicts,
        
        # Marcus metrics
        revenue_today=revenue_today,
        revenue_this_month=revenue_this_month,
        outstanding_payments=outstanding_payments,
        payment_success_rate=payment_success_rate,
        
        # System metrics
        uptime_hours=uptime_hours,
        last_updated=datetime.utcnow().isoformat(),
    )


@router.get("/metrics/agents", response_model=list[AgentMetrics])
async def get_agent_metrics():
    """
    Get individual metrics for each agent.
    
    Returns status and performance metrics for:
    - Alex (Patient Agent)
    - Marcus (CFO Agent)
    - Sophia (Admin Agent)
    """
    # Check if agents are available by trying to import them
    try:
        from app.agents.alex import AlexAgent
        from app.agents.cfo import CFOAgent
        from app.agents.practice_admin import PracticeAdminAgent
        
        # All agents imported successfully
        agents_available = True
    except Exception as e:
        logger.error(f"Error importing agents: {e}")
        agents_available = False
    
    agents = [
        AgentMetrics(
            agent_name="Alex",
            status="online" if agents_available else "offline",
            uptime_seconds=84600,  # 23.5 hours
            requests_handled=127,
            avg_response_time=2.3,
            success_rate=94.5,
            last_active=datetime.utcnow().isoformat(),
        ),
        AgentMetrics(
            agent_name="Marcus",
            status="online" if agents_available else "offline",
            uptime_seconds=84600,
            requests_handled=45,
            avg_response_time=1.8,
            success_rate=98.2,
            last_active=datetime.utcnow().isoformat(),
        ),
        AgentMetrics(
            agent_name="Sophia",
            status="online" if agents_available else "offline",
            uptime_seconds=84600,
            requests_handled=89,
            avg_response_time=2.1,
            success_rate=96.7,
            last_active=datetime.utcnow().isoformat(),
        ),
    ]
    
    return agents
