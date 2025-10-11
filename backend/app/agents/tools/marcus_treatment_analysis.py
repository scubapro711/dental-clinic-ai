"""
Marcus Treatment Category Analysis Tool.

Analyzes treatment categories for financial performance, profitability,
demand trends, and revenue optimization opportunities.

This tool is used by Marcus (CFO Agent) to:
1. Analyze category profitability and margins
2. Identify high-value and underutilized categories
3. Detect revenue optimization opportunities
4. Track trends (increasing, decreasing, stable)
5. Generate proactive financial recommendations
6. Create alerts for Decision Queue

Part of comprehensive financial management system.

NOTE: Marcus understands Israeli tax laws but ALWAYS refers complex
financial/tax advice to human accountants. Marcus suggests, doctor decides.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.treatment_category import (
    TreatmentCategory,
    TreatmentCategoryType,
)
from app.models.proactive_suggestion import (
    ProactiveSuggestion,
    SuggestionPriority,
    SuggestionStatus,
    SuggestionCategory as SuggestionCat,
)


class MarcusTreatmentAnalyzer:
    """Marcus's treatment category analysis engine."""
    
    def __init__(self, db: Session, organization_id: UUID):
        self.db = db
        self.organization_id = organization_id
    
    def analyze_category(self, category_id: UUID) -> Dict[str, Any]:
        """
        Comprehensive treatment category financial analysis.
        
        Returns:
            Analysis results with profitability, demand, recommendations, and alerts
        """
        category = self.db.query(TreatmentCategory).filter(
            TreatmentCategory.id == category_id,
            TreatmentCategory.organization_id == self.organization_id,
            TreatmentCategory.deleted_at == None
        ).first()
        
        if not category:
            raise ValueError("Treatment category not found")
        
        # Profitability analysis
        profitability_score, profitability_insights = self._analyze_profitability(category)
        
        # Demand analysis
        demand_score, demand_insights = self._analyze_demand(category)
        
        # Trend analysis
        trends = self._analyze_trends(category)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            category, profitability_score, demand_score, trends
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(category)
        
        # Compile insights
        insights = {
            "profitability": profitability_insights,
            "demand": demand_insights,
            "trends": trends,
            "flags": {
                "is_high_value": category.is_high_value,
                "is_high_demand": category.is_high_demand,
                "is_underutilized": category.is_underutilized,
                "is_loss_leader": category.is_loss_leader,
            }
        }
        
        # Update category with Marcus's analysis
        category.marcus_analyzed = True
        category.marcus_analysis_date = datetime.utcnow()
        category.marcus_profitability_score = profitability_score
        category.marcus_demand_score = demand_score
        category.marcus_recommendations = recommendations
        category.marcus_insights = insights
        category.marcus_confidence = confidence
        
        # Update flags
        category.is_high_value = profitability_score >= 80 and category.total_revenue_ytd >= 50000
        category.is_high_demand = demand_score >= 80
        category.is_underutilized = profitability_score >= 70 and demand_score < 40
        category.is_loss_leader = (category.average_profit_margin or 0) < 0
        
        # Update trends
        category.revenue_trend = trends["revenue"]
        category.volume_trend = trends["volume"]
        category.profitability_trend = trends["profitability"]
        
        # Generate proactive alerts
        alerts = self._generate_proactive_alerts(
            category, profitability_score, demand_score, recommendations
        )
        category.marcus_alerts = alerts
        
        self.db.commit()
        
        return {
            "category_id": str(category_id),
            "category_name": category.name,
            "category_type": category.category_type.value,
            "analysis_date": datetime.utcnow().isoformat(),
            "profitability_score": profitability_score,
            "demand_score": demand_score,
            "insights": insights,
            "recommendations": recommendations,
            "confidence": confidence,
            "alerts": alerts,
        }
    
    def _analyze_profitability(self, category: TreatmentCategory) -> tuple[int, Dict]:
        """Analyze profitability and return score + insights."""
        score = 50  # Base score
        insights = {}
        
        # Profit margin analysis
        margin = category.average_profit_margin or 0
        if margin >= 50:
            score += 40
            insights["margin_status"] = "excellent"
        elif margin >= 30:
            score += 30
            insights["margin_status"] = "good"
        elif margin >= 10:
            score += 15
            insights["margin_status"] = "fair"
        elif margin >= 0:
            score += 0
            insights["margin_status"] = "poor"
        else:
            score -= 30
            insights["margin_status"] = "loss"
        
        insights["profit_margin"] = round(margin, 2)
        
        # Revenue analysis
        if category.total_revenue_ytd >= 100000:
            score += 10
            insights["revenue_status"] = "very_high"
        elif category.total_revenue_ytd >= 50000:
            score += 5
            insights["revenue_status"] = "high"
        elif category.total_revenue_ytd >= 20000:
            insights["revenue_status"] = "medium"
        else:
            insights["revenue_status"] = "low"
        
        insights["revenue_ytd"] = category.total_revenue_ytd
        insights["revenue_mtd"] = category.total_revenue_mtd
        
        # Cost efficiency
        if category.average_price and category.average_cost:
            cost_ratio = category.average_cost / category.average_price
            if cost_ratio < 0.3:
                insights["cost_efficiency"] = "excellent"
            elif cost_ratio < 0.5:
                insights["cost_efficiency"] = "good"
            elif cost_ratio < 0.7:
                insights["cost_efficiency"] = "fair"
            else:
                insights["cost_efficiency"] = "poor"
        
        return max(0, min(100, score)), insights
    
    def _analyze_demand(self, category: TreatmentCategory) -> tuple[int, Dict]:
        """Analyze demand and return score + insights."""
        score = 50  # Base score
        insights = {}
        
        # Volume analysis
        if category.total_procedures_mtd >= 50:
            score += 40
            insights["volume_status"] = "very_high"
        elif category.total_procedures_mtd >= 20:
            score += 30
            insights["volume_status"] = "high"
        elif category.total_procedures_mtd >= 10:
            score += 15
            insights["volume_status"] = "medium"
        elif category.total_procedures_mtd >= 5:
            score += 5
            insights["volume_status"] = "low"
        else:
            insights["volume_status"] = "very_low"
        
        insights["procedures_ytd"] = category.total_procedures_ytd
        insights["procedures_mtd"] = category.total_procedures_mtd
        
        # Growth rate (mock - in production, calculate from historical data)
        # For now, use trend if available
        if category.volume_trend == "increasing":
            score += 10
            insights["growth"] = "increasing"
        elif category.volume_trend == "decreasing":
            score -= 10
            insights["growth"] = "decreasing"
        else:
            insights["growth"] = "stable"
        
        # Patient satisfaction (if available)
        if category.patient_satisfaction_score:
            if category.patient_satisfaction_score >= 4.5:
                score += 10
                insights["satisfaction"] = "excellent"
            elif category.patient_satisfaction_score >= 4.0:
                score += 5
                insights["satisfaction"] = "good"
            elif category.patient_satisfaction_score >= 3.5:
                insights["satisfaction"] = "fair"
            else:
                score -= 5
                insights["satisfaction"] = "poor"
        
        return max(0, min(100, score)), insights
    
    def _analyze_trends(self, category: TreatmentCategory) -> Dict[str, str]:
        """Analyze trends (mock - in production, use historical data)."""
        # For now, return existing trends or calculate simple ones
        
        # Revenue trend
        revenue_trend = "stable"
        if category.total_revenue_mtd > 0 and category.total_revenue_ytd > 0:
            monthly_avg = category.total_revenue_ytd / 12
            if category.total_revenue_mtd > monthly_avg * 1.2:
                revenue_trend = "increasing"
            elif category.total_revenue_mtd < monthly_avg * 0.8:
                revenue_trend = "decreasing"
        
        # Volume trend
        volume_trend = "stable"
        if category.total_procedures_mtd > 0 and category.total_procedures_ytd > 0:
            monthly_avg = category.total_procedures_ytd / 12
            if category.total_procedures_mtd > monthly_avg * 1.2:
                volume_trend = "increasing"
            elif category.total_procedures_mtd < monthly_avg * 0.8:
                volume_trend = "decreasing"
        
        # Profitability trend (use existing or stable)
        profitability_trend = category.profitability_trend or "stable"
        
        return {
            "revenue": revenue_trend,
            "volume": volume_trend,
            "profitability": profitability_trend
        }
    
    def _generate_recommendations(
        self,
        category: TreatmentCategory,
        profitability_score: int,
        demand_score: int,
        trends: Dict[str, str]
    ) -> List[Dict]:
        """Generate financial recommendations."""
        recommendations = []
        
        # High profitability, low demand → Marketing opportunity
        if profitability_score >= 70 and demand_score < 40:
            recommendations.append({
                "type": "marketing_opportunity",
                "priority": "high",
                "title": "Underutilized High-Value Service",
                "description": f"{category.name} has excellent profitability ({category.average_profit_margin:.1f}% margin) " +
                              f"but low demand ({category.total_procedures_mtd} procedures/month). " +
                              "Consider marketing campaign to increase volume.",
                "potential_impact": "high",
                "actions": [
                    "Launch targeted marketing campaign",
                    "Offer promotional pricing for first-time patients",
                    "Train staff to recommend this service",
                    "Add to website featured services"
                ]
            })
        
        # Low profitability → Cost optimization
        if profitability_score < 40:
            recommendations.append({
                "type": "cost_optimization",
                "priority": "high",
                "title": "Low Profitability - Cost Review Needed",
                "description": f"{category.name} has low profitability ({category.average_profit_margin:.1f}% margin). " +
                              "Review costs and pricing structure.",
                "potential_impact": "high",
                "actions": [
                    "Review supplier costs and negotiate better rates",
                    "Analyze time efficiency and reduce waste",
                    "Consider price adjustment (consult accountant)",
                    "Evaluate if service should be discontinued"
                ],
                "accountant_consultation": True  # Marcus knows to refer to accountant
            })
        
        # Decreasing revenue trend → Alert
        if trends["revenue"] == "decreasing":
            recommendations.append({
                "type": "revenue_decline_alert",
                "priority": "urgent",
                "title": "Revenue Declining - Immediate Action Required",
                "description": f"{category.name} revenue is declining. " +
                              f"MTD: ₪{category.total_revenue_mtd:,.0f} vs YTD avg: ₪{category.total_revenue_ytd/12:,.0f}/month",
                "potential_impact": "high",
                "actions": [
                    "Investigate root cause (competition, quality, pricing)",
                    "Survey patients for feedback",
                    "Review recent changes in service delivery",
                    "Consider strategic pivot or discontinuation"
                ]
            })
        
        # High value, high demand → Capacity expansion
        if profitability_score >= 80 and demand_score >= 80:
            recommendations.append({
                "type": "capacity_expansion",
                "priority": "medium",
                "title": "Star Performer - Consider Capacity Expansion",
                "description": f"{category.name} is a star performer with high profitability and demand. " +
                              "Consider expanding capacity to capture more revenue.",
                "potential_impact": "very_high",
                "actions": [
                    "Hire additional staff for this service",
                    "Extend operating hours",
                    "Invest in additional equipment",
                    "Consider opening second location (consult accountant for ROI)"
                ],
                "accountant_consultation": True
            })
        
        # Loss leader → Urgent review
        if category.is_loss_leader:
            recommendations.append({
                "type": "loss_leader_alert",
                "priority": "urgent",
                "title": "Loss Leader - Negative Margin",
                "description": f"{category.name} is operating at a loss ({category.average_profit_margin:.1f}% margin). " +
                              "Immediate action required to prevent financial drain.",
                "potential_impact": "critical",
                "actions": [
                    "Increase pricing immediately",
                    "Reduce costs or discontinue service",
                    "Consult accountant for tax implications",
                    "Review if this is strategic loss leader"
                ],
                "accountant_consultation": True
            })
        
        # Pricing optimization
        if category.average_price and category.average_cost:
            optimal_margin = 40  # Target 40% margin
            current_margin = category.average_profit_margin or 0
            
            if current_margin < optimal_margin - 10:
                optimal_price = category.average_cost / (1 - optimal_margin/100)
                price_increase = optimal_price - category.average_price
                price_increase_pct = (price_increase / category.average_price) * 100
                
                recommendations.append({
                    "type": "pricing_optimization",
                    "priority": "medium",
                    "title": "Pricing Below Optimal Margin",
                    "description": f"Current margin ({current_margin:.1f}%) is below target ({optimal_margin}%). " +
                                  f"Consider price adjustment of ₪{price_increase:.0f} ({price_increase_pct:.1f}%).",
                    "potential_impact": "medium",
                    "current_price": category.average_price,
                    "suggested_price": round(optimal_price, 2),
                    "actions": [
                        f"Increase price to ₪{optimal_price:.0f}",
                        "Communicate value to patients",
                        "Monitor demand after price change",
                        "Consult accountant for tax implications"
                    ],
                    "accountant_consultation": True
                })
        
        return recommendations
    
    def _calculate_confidence(self, category: TreatmentCategory) -> int:
        """Calculate confidence score for analysis."""
        confidence = 85  # Base confidence
        
        # More data = higher confidence
        if category.total_procedures_ytd >= 100:
            confidence += 10
        elif category.total_procedures_ytd >= 50:
            confidence += 5
        elif category.total_procedures_ytd < 10:
            confidence -= 15
        
        # Price and cost data available
        if category.average_price and category.average_cost:
            confidence += 5
        else:
            confidence -= 10
        
        return max(0, min(100, confidence))
    
    def _generate_proactive_alerts(
        self,
        category: TreatmentCategory,
        profitability_score: int,
        demand_score: int,
        recommendations: List[Dict]
    ) -> List[Dict]:
        """Generate proactive alerts for Decision Queue."""
        alerts = []
        
        # Loss leader alert
        if category.is_loss_leader:
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="marcus",
                title=f"⚠️ Loss Leader Alert: {category.name}",
                message=f"{category.name} is operating at a loss with {category.average_profit_margin:.1f}% margin. " +
                       f"Immediate pricing or cost action required to prevent financial drain.",
                category=SuggestionCat.FINANCIAL_OPPORTUNITY,
                priority=SuggestionPriority.URGENT,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "increase_pricing", "label": "Increase Pricing"},
                    {"action": "review_costs", "label": "Review Costs"},
                    {"action": "consult_accountant", "label": "Consult Accountant"},
                    {"action": "discontinue", "label": "Consider Discontinuing"}
                ],
                suggestion_metadata={
                    "category_id": str(category.id),
                    "category_name": category.name,
                    "profit_margin": category.average_profit_margin,
                    "revenue_ytd": category.total_revenue_ytd,
                    "recommendations": [r for r in recommendations if r["type"] == "loss_leader_alert"]
                },
                confidence=95
            )
            
            self.db.add(suggestion)
            alerts.append(suggestion.to_dict())
        
        # Underutilized high-value alert
        elif category.is_underutilized:
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="marcus",
                title=f"💎 Revenue Opportunity: {category.name}",
                message=f"{category.name} has excellent profitability ({category.average_profit_margin:.1f}% margin) " +
                       f"but low volume ({category.total_procedures_mtd}/month). Marketing could significantly increase revenue.",
                category=SuggestionCat.FINANCIAL_OPPORTUNITY,
                priority=SuggestionPriority.HIGH,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "launch_campaign", "label": "Launch Marketing Campaign"},
                    {"action": "staff_training", "label": "Train Staff to Recommend"},
                    {"action": "promotional_pricing", "label": "Offer Promotion"},
                    {"action": "dismiss", "label": "Not Now"}
                ],
                suggestion_metadata={
                    "category_id": str(category.id),
                    "category_name": category.name,
                    "profit_margin": category.average_profit_margin,
                    "current_volume": category.total_procedures_mtd,
                    "potential_revenue_increase": category.average_price * 20 if category.average_price else 0,
                    "recommendations": [r for r in recommendations if r["type"] == "marketing_opportunity"]
                },
                confidence=85
            )
            
            self.db.add(suggestion)
            alerts.append(suggestion.to_dict())
        
        # Revenue decline alert
        if category.revenue_trend == "decreasing" and category.total_revenue_ytd > 10000:
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="marcus",
                title=f"📉 Revenue Declining: {category.name}",
                message=f"{category.name} revenue is declining. " +
                       f"MTD: ₪{category.total_revenue_mtd:,.0f} vs YTD avg: ₪{category.total_revenue_ytd/12:,.0f}/month. " +
                       "Investigation and action recommended.",
                category=SuggestionCat.FINANCIAL_OPPORTUNITY,
                priority=SuggestionPriority.HIGH,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "investigate", "label": "Investigate Root Cause"},
                    {"action": "survey_patients", "label": "Survey Patients"},
                    {"action": "review_pricing", "label": "Review Pricing"},
                    {"action": "dismiss", "label": "Monitor"}
                ],
                suggestion_metadata={
                    "category_id": str(category.id),
                    "category_name": category.name,
                    "revenue_mtd": category.total_revenue_mtd,
                    "revenue_ytd_avg": category.total_revenue_ytd / 12,
                    "decline_percent": ((category.total_revenue_ytd/12 - category.total_revenue_mtd) / (category.total_revenue_ytd/12)) * 100,
                    "recommendations": [r for r in recommendations if r["type"] == "revenue_decline_alert"]
                },
                confidence=80
            )
            
            self.db.add(suggestion)
            alerts.append(suggestion.to_dict())
        
        self.db.commit()
        
        return alerts


# Tool function for LangChain integration

def analyze_treatment_category_tool(
    category_id: str,
    db: Session,
    organization_id: str
) -> str:
    """
    Analyze treatment category for financial performance and opportunities.
    
    Args:
        category_id: UUID of the treatment category
        db: Database session
        organization_id: UUID of the organization
    
    Returns:
        JSON string with analysis results
    """
    import json
    from uuid import UUID
    
    analyzer = MarcusTreatmentAnalyzer(db, UUID(organization_id))
    results = analyzer.analyze_category(UUID(category_id))
    
    return json.dumps(results, indent=2)

