"""
Advanced Analytics Service

Provides cohort analysis, LTV prediction, retention curves, and funnel analysis.
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from collections import defaultdict

from app.models import Organization, Subscription, Payment, UsageMetric

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for advanced analytics calculations.
    
    Features:
    - Cohort analysis by signup month
    - LTV (Lifetime Value) prediction
    - Retention curves
    - Funnel analysis (trial → paid conversion)
    """
    
    def __init__(self, db: Session):
        """Initialize analytics service."""
        self.db = db
    
    def cohort_analysis(
        self,
        months: int = 12
    ) -> List[Dict]:
        """
        Perform cohort analysis grouped by signup month.
        
        Args:
            months: Number of months to include
        
        Returns:
            List of cohort data with retention percentages
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get all organizations grouped by signup month
        cohorts = {}
        
        organizations = self.db.query(Organization).filter(
            Organization.created_at >= start_date
        ).all()
        
        for org in organizations:
            cohort_month = org.created_at.strftime("%Y-%m")
            
            if cohort_month not in cohorts:
                cohorts[cohort_month] = {
                    "cohort": cohort_month,
                    "total_signups": 0,
                    "month_0": 0,  # Active in signup month
                    "month_1": 0,  # Active 1 month later
                    "month_2": 0,  # Active 2 months later
                    "month_3": 0,  # Active 3 months later
                    "month_6": 0,  # Active 6 months later
                    "month_12": 0,  # Active 12 months later
                }
            
            cohorts[cohort_month]["total_signups"] += 1
            
            # Check if organization is still active
            if org.is_active:
                # Calculate months since signup
                months_since_signup = (
                    (date.today().year - org.created_at.year) * 12 +
                    (date.today().month - org.created_at.month)
                )
                
                # Increment retention counters
                if months_since_signup >= 0:
                    cohorts[cohort_month]["month_0"] += 1
                if months_since_signup >= 1:
                    cohorts[cohort_month]["month_1"] += 1
                if months_since_signup >= 2:
                    cohorts[cohort_month]["month_2"] += 1
                if months_since_signup >= 3:
                    cohorts[cohort_month]["month_3"] += 1
                if months_since_signup >= 6:
                    cohorts[cohort_month]["month_6"] += 1
                if months_since_signup >= 12:
                    cohorts[cohort_month]["month_12"] += 1
        
        # Calculate retention percentages
        result = []
        for cohort_month, data in sorted(cohorts.items()):
            total = data["total_signups"]
            if total > 0:
                result.append({
                    "cohort": cohort_month,
                    "total_signups": total,
                    "retention_month_0": round((data["month_0"] / total) * 100, 1),
                    "retention_month_1": round((data["month_1"] / total) * 100, 1),
                    "retention_month_2": round((data["month_2"] / total) * 100, 1),
                    "retention_month_3": round((data["month_3"] / total) * 100, 1),
                    "retention_month_6": round((data["month_6"] / total) * 100, 1),
                    "retention_month_12": round((data["month_12"] / total) * 100, 1),
                })
        
        return result
    
    def calculate_ltv(
        self,
        organization_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate Lifetime Value (LTV) metrics.
        
        Args:
            organization_id: Optional specific organization ID
        
        Returns:
            Dict with LTV metrics
        """
        # Get all payments
        query = self.db.query(Payment).filter(
            Payment.status == "succeeded"
        )
        
        if organization_id:
            query = query.filter(Payment.organization_id == organization_id)
        
        payments = query.all()
        
        # Group by organization
        org_revenues = defaultdict(Decimal)
        org_months = defaultdict(set)
        
        for payment in payments:
            org_revenues[payment.organization_id] += payment.amount
            month = payment.created_at.strftime("%Y-%m")
            org_months[payment.organization_id].add(month)
        
        # Calculate metrics
        if not org_revenues:
            return {
                "average_ltv": 0,
                "median_ltv": 0,
                "average_lifetime_months": 0,
                "total_organizations": 0
            }
        
        ltvs = list(org_revenues.values())
        lifetimes = [len(months) for months in org_months.values()]
        
        return {
            "average_ltv": float(sum(ltvs) / len(ltvs)),
            "median_ltv": float(sorted(ltvs)[len(ltvs) // 2]),
            "average_lifetime_months": sum(lifetimes) / len(lifetimes),
            "total_organizations": len(org_revenues),
            "total_revenue": float(sum(ltvs))
        }
    
    def predict_ltv(
        self,
        organization_id: int
    ) -> Dict:
        """
        Predict LTV for a specific organization based on current behavior.
        
        Args:
            organization_id: Organization ID
        
        Returns:
            Dict with LTV prediction
        """
        org = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not org:
            return {"error": "Organization not found"}
        
        # Get subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.organization_id == organization_id,
            Subscription.status.in_(["active", "trialing"])
        ).first()
        
        if not subscription:
            return {
                "predicted_ltv": 0,
                "confidence": "low",
                "reason": "No active subscription"
            }
        
        # Simple LTV prediction: MRR * Average Lifetime (months)
        mrr = float(subscription.plan_price or 0)
        
        # Get average lifetime from cohort data
        avg_lifetime_months = self.calculate_ltv()["average_lifetime_months"]
        
        # Calculate predicted LTV
        predicted_ltv = mrr * avg_lifetime_months
        
        # Adjust based on usage (if high usage, increase LTV prediction)
        recent_usage = self.db.query(UsageMetric).filter(
            UsageMetric.organization_id == organization_id,
            UsageMetric.date >= date.today() - timedelta(days=30)
        ).count()
        
        usage_multiplier = 1.0
        if recent_usage > 20:  # High usage
            usage_multiplier = 1.2
        elif recent_usage < 5:  # Low usage
            usage_multiplier = 0.8
        
        predicted_ltv *= usage_multiplier
        
        return {
            "predicted_ltv": round(predicted_ltv, 2),
            "mrr": mrr,
            "estimated_lifetime_months": round(avg_lifetime_months, 1),
            "usage_multiplier": usage_multiplier,
            "confidence": "medium"
        }
    
    def retention_curve(
        self,
        months: int = 12
    ) -> List[Dict]:
        """
        Calculate retention curve showing % of organizations still active over time.
        
        Args:
            months: Number of months to analyze
        
        Returns:
            List of retention data points
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get all organizations that signed up before the period
        organizations = self.db.query(Organization).filter(
            Organization.created_at <= start_date
        ).all()
        
        total_orgs = len(organizations)
        
        if total_orgs == 0:
            return []
        
        # Calculate retention for each month
        retention_data = []
        
        for month_offset in range(months + 1):
            check_date = start_date + timedelta(days=month_offset * 30)
            
            # Count organizations still active at this date
            active_count = sum(
                1 for org in organizations
                if org.is_active and (
                    not org.trial_end or org.trial_end >= check_date
                )
            )
            
            retention_percentage = (active_count / total_orgs) * 100
            
            retention_data.append({
                "month": month_offset,
                "date": check_date.isoformat(),
                "active_organizations": active_count,
                "retention_percentage": round(retention_percentage, 1)
            })
        
        return retention_data
    
    def funnel_analysis(self) -> Dict:
        """
        Analyze the conversion funnel from trial to paid.
        
        Returns:
            Dict with funnel metrics
        """
        # Total signups
        total_signups = self.db.query(func.count(Organization.id)).scalar()
        
        # Organizations that started trial
        trial_started = self.db.query(func.count(Organization.id)).filter(
            Organization.trial_end.isnot(None)
        ).scalar()
        
        # Organizations that converted to paid
        paid_converted = self.db.query(func.count(Organization.id)).filter(
            Organization.subscription_status == "active"
        ).scalar()
        
        # Organizations currently in trial
        currently_trialing = self.db.query(func.count(Organization.id)).filter(
            Organization.subscription_status == "trialing",
            Organization.trial_end >= date.today()
        ).scalar()
        
        # Organizations that canceled during trial
        trial_canceled = self.db.query(func.count(Organization.id)).filter(
            Organization.subscription_status == "canceled",
            Organization.trial_end.isnot(None)
        ).scalar()
        
        # Calculate conversion rates
        trial_to_paid_rate = (paid_converted / trial_started * 100) if trial_started > 0 else 0
        signup_to_paid_rate = (paid_converted / total_signups * 100) if total_signups > 0 else 0
        
        return {
            "total_signups": total_signups,
            "trial_started": trial_started,
            "currently_trialing": currently_trialing,
            "paid_converted": paid_converted,
            "trial_canceled": trial_canceled,
            "trial_to_paid_conversion_rate": round(trial_to_paid_rate, 1),
            "signup_to_paid_conversion_rate": round(signup_to_paid_rate, 1),
            "funnel_stages": [
                {
                    "stage": "Signup",
                    "count": total_signups,
                    "percentage": 100
                },
                {
                    "stage": "Trial Started",
                    "count": trial_started,
                    "percentage": round((trial_started / total_signups * 100), 1) if total_signups > 0 else 0
                },
                {
                    "stage": "Paid Conversion",
                    "count": paid_converted,
                    "percentage": round((paid_converted / total_signups * 100), 1) if total_signups > 0 else 0
                }
            ]
        }
    
    def churn_analysis(
        self,
        months: int = 6
    ) -> Dict:
        """
        Analyze churn patterns and identify at-risk organizations.
        
        Args:
            months: Number of months to analyze
        
        Returns:
            Dict with churn metrics
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get churned organizations in period
        churned = self.db.query(Organization).filter(
            Organization.subscription_status == "canceled",
            Organization.created_at >= start_date
        ).all()
        
        # Get active organizations at start of period
        active_at_start = self.db.query(Organization).filter(
            Organization.created_at <= start_date,
            Organization.is_active == True
        ).count()
        
        # Calculate churn rate
        churn_rate = (len(churned) / active_at_start * 100) if active_at_start > 0 else 0
        
        # Analyze churn reasons (based on usage patterns)
        low_usage_churn = 0
        high_cost_churn = 0
        
        for org in churned:
            # Check usage in last 30 days before churn
            usage_count = self.db.query(UsageMetric).filter(
                UsageMetric.organization_id == org.id,
                UsageMetric.date >= (org.created_at - timedelta(days=30))
            ).count()
            
            if usage_count < 5:
                low_usage_churn += 1
        
        return {
            "total_churned": len(churned),
            "churn_rate": round(churn_rate, 1),
            "active_at_period_start": active_at_start,
            "churn_reasons": {
                "low_usage": low_usage_churn,
                "high_cost": high_cost_churn,
                "unknown": len(churned) - low_usage_churn - high_cost_churn
            }
        }


def get_analytics_service(db: Session) -> AnalyticsService:
    """Get analytics service instance."""
    return AnalyticsService(db)

