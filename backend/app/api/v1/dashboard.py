"""
Dashboard API Endpoints

Provides metrics and KPIs for dashboard widgets
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Optional
import logging
from decimal import Decimal

from app.core.database import get_db
from app.integrations.odoo_client_v2 import OdooClientV2
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Odoo client
odoo_client = OdooClientV2()


@router.get("/revenue")
async def get_revenue_metrics(
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get revenue metrics for current and last month
    
    Returns revenue data with trends and insights
    """
    try:
        if not odoo_client.authenticate():
            raise HTTPException(status_code=500, detail="Failed to connect to Odoo")
        
        # Calculate date ranges
        today = date.today()
        first_day_this_month = date(today.year, today.month, 1)
        
        # Last month
        if today.month == 1:
            first_day_last_month = date(today.year - 1, 12, 1)
            last_day_last_month = date(today.year, 1, 1) - timedelta(days=1)
        else:
            first_day_last_month = date(today.year, today.month - 1, 1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
        
        # Get this month's revenue
        # TODO: Query actual revenue from Odoo invoices/payments
        # For now, calculate based on appointments
        
        this_month_appointments = odoo_client.models.execute_kw(
            odoo_client.db,
            odoo_client.uid,
            odoo_client.password,
            'medical.appointment',
            'search_count',
            [[
                ('appointment_sdate', '>=', first_day_this_month.strftime('%Y-%m-%d')),
                ('appointment_sdate', '<=', today.strftime('%Y-%m-%d'))
            ]]
        )
        
        last_month_appointments = odoo_client.models.execute_kw(
            odoo_client.db,
            odoo_client.uid,
            odoo_client.password,
            'medical.appointment',
            'search_count',
            [[
                ('appointment_sdate', '>=', first_day_last_month.strftime('%Y-%m-%d')),
                ('appointment_sdate', '<=', last_day_last_month.strftime('%Y-%m-%d'))
            ]]
        )
        
        # Estimate revenue (average 500 ILS per appointment)
        avg_appointment_value = 500
        this_month_revenue = this_month_appointments * avg_appointment_value
        last_month_revenue = last_month_appointments * avg_appointment_value
        
        # Calculate change percentage
        if last_month_revenue > 0:
            change = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
        else:
            change = 0
        
        # Determine trend
        trend = 'up' if change > 0 else 'down' if change < 0 else 'stable'
        
        # Generate insight
        if change > 10:
            insight = f'הכנסות עלו ב-{abs(change):.1f}% לעומת החודש הקודם - מגמה מצוינת!'
        elif change > 0:
            insight = f'הכנסות עלו ב-{abs(change):.1f}% לעומת החודש הקודם'
        elif change < -10:
            insight = f'הכנסות ירדו ב-{abs(change):.1f}% לעומת החודש הקודם - נדרשת תשומת לב'
        elif change < 0:
            insight = f'הכנסות ירדו ב-{abs(change):.1f}% לעומת החודש הקודם'
        else:
            insight = 'הכנסות יציבות לעומת החודש הקודם'
        
        # Generate recommendation
        if change < 0:
            recommendation = 'מרקוס ממליץ: התמקדו בשיווק ובמבצעים למשיכת לקוחות חדשים'
        elif change > 20:
            recommendation = 'מרקוס ממליץ: המשיכו במגמה החיובית - שקלו הרחבת שעות הפעילות'
        else:
            recommendation = 'מרקוס ממליץ: התמקדו בטיפולים מורכבים - הם מניבים 40% מההכנסות'
        
        return {
            'thisMonth': this_month_revenue,
            'lastMonth': last_month_revenue,
            'change': round(change, 1),
            'trend': trend,
            'insight': insight,
            'recommendation': recommendation,
            'appointments_this_month': this_month_appointments,
            'appointments_last_month': last_month_appointments
        }
        
    except Exception as e:
        logger.error(f"Error fetching revenue metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_dashboard_metrics(
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get all dashboard KPI metrics
    
    Returns appointments, success rate, handling time, etc.
    """
    try:
        if not odoo_client.authenticate():
            raise HTTPException(status_code=500, detail="Failed to connect to Odoo")
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        # Appointments today
        appointments_today = odoo_client.models.execute_kw(
            odoo_client.db,
            odoo_client.uid,
            odoo_client.password,
            'medical.appointment',
            'search_count',
            [[
                ('appointment_sdate', '>=', today.strftime('%Y-%m-%d')),
                ('appointment_sdate', '<=', today.strftime('%Y-%m-%d 23:59:59'))
            ]]
        )
        
        # Appointments yesterday
        appointments_yesterday = odoo_client.models.execute_kw(
            odoo_client.db,
            odoo_client.uid,
            odoo_client.password,
            'medical.appointment',
            'search_count',
            [[
                ('appointment_sdate', '>=', yesterday.strftime('%Y-%m-%d')),
                ('appointment_sdate', '<=', yesterday.strftime('%Y-%m-%d 23:59:59'))
            ]]
        )
        
        # Calculate change
        appointments_change = appointments_today - appointments_yesterday
        
        # TODO: Calculate real success rate and handling time from conversation logs
        # For now, use estimates
        success_rate_24h = 87
        success_rate_change = 5
        avg_handling_time = 245  # seconds
        handling_time_change = -35
        conversations_resolved = 24
        
        return {
            'appointments_today': appointments_today,
            'appointments_change': appointments_change,
            'success_rate_24h': success_rate_24h,
            'success_rate_change': success_rate_change,
            'conversations_resolved': conversations_resolved,
            'avg_handling_time': avg_handling_time,
            'avg_handling_time_weekly': avg_handling_time + handling_time_change,
            'handling_time_change': handling_time_change
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
