"""
Mock SaaS Data Generator for Super Admin Dashboard

Generates realistic multi-tenant data for testing:
- 25 dental clinics with varying characteristics
- Subscription data (MRR, ARR, status)
- Usage metrics (API calls, storage, users)
- System costs (infrastructure, AI, support)
- Customer health scores
- Support tickets
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from uuid import uuid4


class MockSaaSData:
    """Generate mock SaaS data for Super Admin dashboard."""

    def __init__(self):
        """Initialize mock data generator."""
        self.clinics = self._generate_clinics()
        self.subscriptions = self._generate_subscriptions()
        self.usage_metrics = self._generate_usage_metrics()
        self.costs = self._generate_costs()
        self.health_scores = self._generate_health_scores()
        self.support_tickets = self._generate_support_tickets()

    def _generate_clinics(self) -> List[Dict[str, Any]]:
        """Generate 25 mock dental clinics."""
        clinic_names = [
            "Smile Dental Clinic",
            "City Dental Center",
            "Family Dental Care",
            "Bright Smile Dentistry",
            "Elite Dental Group",
            "Modern Dental Studio",
            "Gentle Dental Care",
            "Perfect Smile Clinic",
            "Advanced Dental Center",
            "Harmony Dental Practice",
            "Diamond Dental Clinic",
            "Royal Dental Care",
            "Prime Dental Studio",
            "Excellence Dental Group",
            "Prestige Dental Center",
            "Wellness Dental Clinic",
            "Premier Dental Care",
            "Quality Dental Studio",
            "Superior Dental Group",
            "Professional Dental Center",
            "Expert Dental Clinic",
            "Master Dental Care",
            "Champion Dental Studio",
            "Victory Dental Group",
            "Success Dental Center",
        ]

        cities = [
            "Tel Aviv", "Jerusalem", "Haifa", "Rishon LeZion", "Petah Tikva",
            "Ashdod", "Netanya", "Beer Sheva", "Holon", "Ramat Gan",
            "Rehovot", "Herzliya", "Kfar Saba", "Hadera", "Modi'in"
        ]

        statuses = ["active", "trial", "past_due", "suspended", "churned"]
        status_weights = [70, 15, 5, 5, 5]  # 70% active, 15% trial, etc.

        tiers = ["basic", "professional", "enterprise"]
        tier_weights = [50, 35, 15]  # 50% basic, 35% pro, 15% enterprise

        clinics = []
        for i, name in enumerate(clinic_names):
            # Random status (weighted)
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Random tier (weighted)
            tier = random.choices(tiers, weights=tier_weights)[0]
            
            # Created date (between 6 months ago and today)
            days_ago = random.randint(0, 180)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            clinic = {
                "id": str(uuid4()),
                "name": name,
                "city": random.choice(cities),
                "status": status,
                "subscription_tier": tier,
                "created_at": created_at,
                "trial_ends_at": created_at + timedelta(days=14) if status == "trial" else None,
                "active_users": random.randint(3, 25),
                "total_patients": random.randint(200, 5000),
            }
            
            clinics.append(clinic)

        return clinics

    def _generate_subscriptions(self) -> List[Dict[str, Any]]:
        """Generate subscription data for each clinic."""
        tier_prices = {
            "basic": Decimal("500.00"),
            "professional": Decimal("1500.00"),
            "enterprise": Decimal("4500.00"),
        }

        subscriptions = []
        for clinic in self.clinics:
            # Skip churned clinics
            if clinic["status"] == "churned":
                continue

            price = tier_prices[clinic["subscription_tier"]]
            
            # Add some variation to prices (discounts, custom pricing)
            if random.random() < 0.2:  # 20% have custom pricing
                discount = random.uniform(0.8, 0.95)
                price = price * Decimal(str(discount))

            subscription = {
                "id": str(uuid4()),
                "organization_id": clinic["id"],
                "plan": clinic["subscription_tier"],
                "price": float(price),
                "billing_cycle": random.choice(["monthly", "annual"]),
                "status": clinic["status"],
                "current_period_start": clinic["created_at"],
                "current_period_end": clinic["created_at"] + timedelta(days=30),
                "last_payment_date": clinic["created_at"] if clinic["status"] not in ["trial", "past_due"] else None,
                "last_payment_amount": float(price) if clinic["status"] not in ["trial", "past_due"] else None,
            }

            subscriptions.append(subscription)

        return subscriptions

    def _generate_usage_metrics(self) -> List[Dict[str, Any]]:
        """Generate daily usage metrics for last 30 days."""
        usage_metrics = []

        for clinic in self.clinics:
            # Skip churned clinics
            if clinic["status"] == "churned":
                continue

            # Generate last 30 days
            for days_ago in range(30):
                metric_date = datetime.now().date() - timedelta(days=days_ago)

                # Base usage depends on tier and status
                base_multiplier = 1.0
                if clinic["status"] == "trial":
                    base_multiplier = 0.3  # Trials use less
                elif clinic["status"] == "suspended":
                    base_multiplier = 0.0  # Suspended = no usage
                elif clinic["subscription_tier"] == "enterprise":
                    base_multiplier = 2.0  # Enterprise uses more
                elif clinic["subscription_tier"] == "professional":
                    base_multiplier = 1.5

                # Add some randomness and trend
                daily_variation = random.uniform(0.7, 1.3)
                trend = 1.0 + (days_ago / 100)  # Slight growth over time

                usage = {
                    "id": str(uuid4()),
                    "organization_id": clinic["id"],
                    "metric_date": metric_date,
                    "api_calls": int(random.randint(100, 500) * base_multiplier * daily_variation * trend),
                    "storage_gb": round(random.uniform(0.5, 10.0) * base_multiplier, 2),
                    "active_users": int(clinic["active_users"] * random.uniform(0.6, 1.0)),
                    "messages_sent": int(random.randint(50, 300) * base_multiplier * daily_variation),
                    "appointments_created": int(random.randint(10, 80) * base_multiplier * daily_variation),
                    "alex_messages": int(random.randint(30, 200) * base_multiplier * daily_variation),
                    "cfo_queries": int(random.randint(5, 50) * base_multiplier * daily_variation),
                    "admin_tasks": int(random.randint(10, 100) * base_multiplier * daily_variation),
                    "avg_response_time_ms": random.randint(100, 500),
                    "error_count": random.randint(0, 5),
                }

                usage_metrics.append(usage)

        return usage_metrics

    def _generate_costs(self) -> List[Dict[str, Any]]:
        """Generate system costs for last 30 days."""
        costs = []

        # Daily infrastructure costs (AWS, servers)
        for days_ago in range(30):
            cost_date = datetime.now().date() - timedelta(days=days_ago)
            
            costs.append({
                "id": str(uuid4()),
                "cost_date": cost_date,
                "category": "infrastructure",
                "amount": float(random.uniform(150, 250)),
                "description": "AWS hosting, databases, storage",
                "vendor": "AWS",
            })

        # Daily AI/LLM costs (OpenAI)
        for days_ago in range(30):
            cost_date = datetime.now().date() - timedelta(days=days_ago)
            
            costs.append({
                "id": str(uuid4()),
                "cost_date": cost_date,
                "category": "ai_llm",
                "amount": float(random.uniform(200, 400)),
                "description": "OpenAI API usage",
                "vendor": "OpenAI",
            })

        # Weekly support costs
        for weeks_ago in range(4):
            cost_date = datetime.now().date() - timedelta(weeks=weeks_ago)
            
            costs.append({
                "id": str(uuid4()),
                "cost_date": cost_date,
                "category": "support",
                "amount": float(random.uniform(500, 1000)),
                "description": "Customer support team",
                "vendor": "Internal",
            })

        return costs

    def _generate_health_scores(self) -> List[Dict[str, Any]]:
        """Generate customer health scores."""
        health_scores = []

        for clinic in self.clinics:
            # Skip churned clinics
            if clinic["status"] == "churned":
                continue

            # Calculate component scores based on status and tier
            if clinic["status"] == "active":
                usage_score = random.randint(70, 100)
                engagement_score = random.randint(70, 100)
                payment_score = random.randint(90, 100)
            elif clinic["status"] == "trial":
                usage_score = random.randint(40, 80)
                engagement_score = random.randint(50, 90)
                payment_score = 100  # No payment issues in trial
            elif clinic["status"] == "past_due":
                usage_score = random.randint(50, 80)
                engagement_score = random.randint(40, 70)
                payment_score = random.randint(20, 50)
            else:  # suspended
                usage_score = random.randint(10, 40)
                engagement_score = random.randint(10, 40)
                payment_score = random.randint(0, 30)

            satisfaction_score = random.randint(60, 100)

            # Overall score (weighted average)
            overall_score = int(
                usage_score * 0.3 +
                engagement_score * 0.3 +
                payment_score * 0.25 +
                satisfaction_score * 0.15
            )

            # Determine risk
            is_at_risk = overall_score < 60
            churn_probability = max(0, 100 - overall_score) if is_at_risk else random.randint(0, 20)

            # Risk factors
            risk_factors = []
            if usage_score < 50:
                risk_factors.append("Low usage")
            if engagement_score < 50:
                risk_factors.append("Low engagement")
            if payment_score < 70:
                risk_factors.append("Payment issues")
            if satisfaction_score < 60:
                risk_factors.append("Low satisfaction")

            # Upsell opportunity
            upsell_opportunity = (
                clinic["subscription_tier"] in ["basic", "professional"] and
                overall_score > 80 and
                usage_score > 80
            )

            health_score = {
                "id": str(uuid4()),
                "organization_id": clinic["id"],
                "score_date": datetime.now().date(),
                "overall_score": overall_score,
                "usage_score": usage_score,
                "engagement_score": engagement_score,
                "satisfaction_score": satisfaction_score,
                "payment_score": payment_score,
                "is_at_risk": is_at_risk,
                "churn_probability": churn_probability,
                "risk_factors": ", ".join(risk_factors) if risk_factors else None,
                "upsell_opportunity": upsell_opportunity,
                "upsell_reason": f"High engagement, ready for {self._next_tier(clinic['subscription_tier'])}" if upsell_opportunity else None,
            }

            health_scores.append(health_score)

        return health_scores

    def _next_tier(self, current_tier: str) -> str:
        """Get next subscription tier."""
        if current_tier == "basic":
            return "professional"
        elif current_tier == "professional":
            return "enterprise"
        return "enterprise"

    def _generate_support_tickets(self) -> List[Dict[str, Any]]:
        """Generate support tickets."""
        tickets = []

        ticket_subjects = [
            "Login issues",
            "Payment not processing",
            "Feature request: Export to Excel",
            "Agent not responding correctly",
            "Dashboard loading slowly",
            "Need help with setup",
            "Billing question",
            "Integration with Odoo",
            "User permissions issue",
            "Data export request",
        ]

        priorities = ["low", "medium", "high", "urgent"]
        priority_weights = [30, 50, 15, 5]

        statuses = ["open", "in_progress", "resolved", "closed"]
        status_weights = [20, 30, 30, 20]

        categories = ["technical", "billing", "feature_request", "training", "other"]

        for clinic in self.clinics:
            # Skip churned clinics
            if clinic["status"] == "churned":
                continue

            # Generate 0-5 tickets per clinic
            num_tickets = random.randint(0, 5)
            
            for _ in range(num_tickets):
                created_at = datetime.now() - timedelta(days=random.randint(0, 30))
                status = random.choices(statuses, weights=status_weights)[0]
                
                resolved_at = None
                resolution_time_hours = None
                if status in ["resolved", "closed"]:
                    resolution_time_hours = random.randint(1, 72)
                    resolved_at = created_at + timedelta(hours=resolution_time_hours)

                ticket = {
                    "id": str(uuid4()),
                    "organization_id": clinic["id"],
                    "subject": random.choice(ticket_subjects),
                    "description": "Mock ticket description",
                    "priority": random.choices(priorities, weights=priority_weights)[0],
                    "status": status,
                    "category": random.choice(categories),
                    "created_at": created_at,
                    "resolved_at": resolved_at,
                    "resolution_time_hours": resolution_time_hours,
                }

                tickets.append(ticket)

        return tickets

    # ===== Query Methods =====

    def get_all_clinics(self) -> List[Dict[str, Any]]:
        """Get all clinics."""
        return self.clinics

    def get_clinic_by_id(self, clinic_id: str) -> Dict[str, Any]:
        """Get clinic by ID."""
        for clinic in self.clinics:
            if clinic["id"] == clinic_id:
                return clinic
        return None

    def get_active_clinics(self) -> List[Dict[str, Any]]:
        """Get active clinics only."""
        return [c for c in self.clinics if c["status"] == "active"]

    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all subscriptions."""
        return self.subscriptions

    def get_usage_metrics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get usage metrics for last N days."""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        return [m for m in self.usage_metrics if m["metric_date"] >= cutoff_date]

    def get_costs(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get costs for last N days."""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        return [c for c in self.costs if c["cost_date"] >= cutoff_date]

    def get_health_scores(self) -> List[Dict[str, Any]]:
        """Get all health scores."""
        return self.health_scores

    def get_at_risk_clinics(self) -> List[Dict[str, Any]]:
        """Get clinics at risk of churning."""
        at_risk_scores = [h for h in self.health_scores if h["is_at_risk"]]
        at_risk_clinic_ids = [h["organization_id"] for h in at_risk_scores]
        return [c for c in self.clinics if c["id"] in at_risk_clinic_ids]

    def get_upsell_opportunities(self) -> List[Dict[str, Any]]:
        """Get clinics with upsell opportunities."""
        upsell_scores = [h for h in self.health_scores if h["upsell_opportunity"]]
        upsell_clinic_ids = [h["organization_id"] for h in upsell_scores]
        return [c for c in self.clinics if c["id"] in upsell_clinic_ids]

    def get_support_tickets(self, status: str = None) -> List[Dict[str, Any]]:
        """Get support tickets, optionally filtered by status."""
        if status:
            return [t for t in self.support_tickets if t["status"] == status]
        return self.support_tickets

    def calculate_mrr(self) -> float:
        """Calculate Monthly Recurring Revenue."""
        mrr = sum(
            sub["price"] for sub in self.subscriptions
            if sub["status"] in ["active", "past_due"]
        )
        return round(mrr, 2)

    def calculate_arr(self) -> float:
        """Calculate Annual Recurring Revenue."""
        return round(self.calculate_mrr() * 12, 2)

    def calculate_churn_rate(self) -> float:
        """Calculate churn rate (last 30 days)."""
        total_clinics = len([c for c in self.clinics if c["status"] != "trial"])
        churned_clinics = len([c for c in self.clinics if c["status"] == "churned"])
        
        if total_clinics == 0:
            return 0.0
        
        return round((churned_clinics / total_clinics) * 100, 2)

    def calculate_arpu(self) -> float:
        """Calculate Average Revenue Per User."""
        active_clinics = len([c for c in self.clinics if c["status"] in ["active", "trial"]])
        
        if active_clinics == 0:
            return 0.0
        
        return round(self.calculate_mrr() / active_clinics, 2)


# Singleton instance
mock_saas_data = MockSaaSData()
