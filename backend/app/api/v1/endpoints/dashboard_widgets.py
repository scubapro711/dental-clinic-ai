"""
Dashboard Widgets API Endpoints

Provides real-time data for dashboard widgets using OdooClient.
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, date, timedelta

from app.integrations.odoo_client import OdooClient, get_odoo_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/patients/today")
async def get_todays_patients(
    odoo: OdooClient = Depends(get_odoo_client)
) -> List[Dict[str, Any]]:
    """
    Get today's patient appointments for the dashboard.
    
    Returns:
        List of today's appointments with patient details
    """
    try:
        # Get today's date
        today = date.today().isoformat()
        
        # Search for today's appointments
        appointments = odoo.search_appointments(
            date_from=today,
            date_to=today
        )
        
        # Enrich with patient data
        result = []
        for appt in appointments:
            patient = odoo.get_patient(appt["patient_id"])
            if patient:
                result.append({
                    "id": appt["id"],
                    "patient_id": patient["id"],
                    "name": patient["name"],
                    "phone": patient.get("phone", ""),
                    "time": appt["date"],
                    "treatment": appt.get("treatment_type", "General"),
                    "status": appt["status"],
                    "isFirstVisit": patient.get("visit_count", 0) == 0,
                    "notes": appt.get("notes", "")
                })
        
        # Sort by time
        result.sort(key=lambda x: x["time"])
        
        logger.info(f"Found {len(result)} appointments for today")
        return result
        
    except Exception as e:
        logger.error(f"Error getting today's patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue/summary")
async def get_revenue_summary(
    odoo: OdooClient = Depends(get_odoo_client)
) -> Dict[str, Any]:
    """
    Get revenue summary for the dashboard.
    
    Returns:
        Revenue data with trends and insights
    """
    try:
        # Get current month dates
        today = date.today()
        first_day_this_month = today.replace(day=1)
        
        # Get last month dates
        last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_month.replace(day=1)
        
        # Get invoices for this month
        this_month_invoices = odoo.search_invoices(
            date_from=first_day_this_month.isoformat(),
            date_to=today.isoformat()
        )
        
        # Get invoices for last month
        last_month_invoices = odoo.search_invoices(
            date_from=first_day_last_month.isoformat(),
            date_to=last_month.isoformat()
        )
        
        # Calculate totals
        this_month_total = sum(inv.get("amount_total", 0) for inv in this_month_invoices)
        last_month_total = sum(inv.get("amount_total", 0) for inv in last_month_invoices)
        
        # Calculate change percentage
        if last_month_total > 0:
            change_percent = ((this_month_total - last_month_total) / last_month_total) * 100
        else:
            change_percent = 0
        
        # Generate insight
        trend = "up" if change_percent > 0 else "down"
        insight = f"הכנסות {'עלו' if trend == 'up' else 'ירדו'} ב-{abs(change_percent):.1f}% לעומת החודש הקודם"
        
        # Generate recommendation based on data
        paid_count = len([inv for inv in this_month_invoices if inv.get("status") == "paid"])
        total_count = len(this_month_invoices)
        payment_rate = (paid_count / total_count * 100) if total_count > 0 else 0
        
        if payment_rate < 70:
            recommendation = "מרקוס ממליץ: שלח תזכורות לתשלום - שיעור גביה נמוך"
        elif change_percent > 10:
            recommendation = "מרקוס ממליץ: המשך במגמה הנוכחית - הכנסות גדלות"
        else:
            recommendation = "מרקוס ממליץ: התמקד בטיפולים מורכבים - הם מניבים יותר"
        
        result = {
            "thisMonth": this_month_total,
            "lastMonth": last_month_total,
            "change": change_percent,
            "trend": trend,
            "insight": insight,
            "recommendation": recommendation,
            "invoiceCount": total_count,
            "paidCount": paid_count,
            "paymentRate": payment_rate
        }
        
        logger.info(f"Revenue summary: ₪{this_month_total:,.0f} this month, {change_percent:+.1f}% change")
        return result
        
    except Exception as e:
        logger.error(f"Error getting revenue summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decisions/queue")
async def get_decision_queue(
    odoo: OdooClient = Depends(get_odoo_client)
) -> List[Dict[str, Any]]:
    """
    Get decision queue for the dashboard.
    
    Returns:
        List of items requiring doctor's decision/approval
    """
    try:
        decisions = []
        
        # Check for unconfirmed appointments
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        unconfirmed_appts = odoo.search_appointments(
            date_from=today.isoformat(),
            date_to=tomorrow.isoformat()
        )
        unconfirmed_count = len([a for a in unconfirmed_appts if a["status"] == "scheduled"])
        
        if unconfirmed_count > 0:
            decisions.append({
                "id": "unconfirmed_appts",
                "priority": "high",
                "agent": "alex",
                "title": f"{unconfirmed_count} מטופלים ממתינים לאישור תור",
                "description": f"Alex זיהה {unconfirmed_count} מטופלים שלא אישרו תור - צריך להתקשר",
                "action": "התקשר למטופלים",
                "timestamp": datetime.now().isoformat(),
                "count": unconfirmed_count
            })
        
        # Check for overdue invoices
        overdue_invoices = odoo.search_invoices(
            date_to=(today - timedelta(days=30)).isoformat()
        )
        overdue_unpaid = [inv for inv in overdue_invoices if inv.get("status") != "paid"]
        overdue_total = sum(inv.get("amount_total", 0) for inv in overdue_unpaid)
        
        if len(overdue_unpaid) > 0:
            decisions.append({
                "id": "overdue_invoices",
                "priority": "medium",
                "agent": "marcus",
                "title": f"₪{overdue_total:,.0f} חובות לא נגבו",
                "description": f"Marcus מצא {len(overdue_unpaid)} חשבונות פתוחים מעל 30 יום - צריך להחליט על תזכורות",
                "action": "שלח תזכורות",
                "timestamp": datetime.now().isoformat(),
                "count": len(overdue_unpaid),
                "amount": overdue_total
            })
        
        # Check for new patients
        all_patients = odoo.search_patients()
        new_patients = [p for p in all_patients if p.get("visit_count", 0) == 0]
        
        if len(new_patients) > 0:
            decisions.append({
                "id": "new_patients",
                "priority": "medium",
                "agent": "alex",
                "title": f"{len(new_patients)} מטופלים חדשים",
                "description": f"Alex ממליץ לסקור היסטוריה רפואית של מטופלים חדשים",
                "action": "סקור היסטוריה",
                "timestamp": datetime.now().isoformat(),
                "count": len(new_patients)
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        decisions.sort(key=lambda x: priority_order[x["priority"]])
        
        logger.info(f"Found {len(decisions)} items in decision queue")
        return decisions
        
    except Exception as e:
        logger.error(f"Error getting decision queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_stats_summary(
    odoo: OdooClient = Depends(get_odoo_client)
) -> Dict[str, Any]:
    """
    Get general statistics summary for the dashboard.
    
    Returns:
        Summary statistics
    """
    try:
        today = date.today()
        
        # Get counts
        total_patients = odoo.count_patients()
        
        today_appts = odoo.search_appointments(
            date_from=today.isoformat(),
            date_to=today.isoformat()
        )
        today_count = len(today_appts)
        
        this_week_start = today - timedelta(days=today.weekday())
        this_week_appts = odoo.search_appointments(
            date_from=this_week_start.isoformat(),
            date_to=today.isoformat()
        )
        week_count = len(this_week_appts)
        
        # Get invoice stats
        first_day_month = today.replace(day=1)
        month_invoices = odoo.search_invoices(
            date_from=first_day_month.isoformat(),
            date_to=today.isoformat()
        )
        month_revenue = sum(inv.get("amount_total", 0) for inv in month_invoices)
        
        result = {
            "totalPatients": total_patients,
            "todayAppointments": today_count,
            "weekAppointments": week_count,
            "monthRevenue": month_revenue,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Stats summary: {total_patients} patients, {today_count} appointments today")
        return result
        
    except Exception as e:
        logger.error(f"Error getting stats summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
