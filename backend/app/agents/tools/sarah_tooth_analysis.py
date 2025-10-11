"""
Sarah Tooth Analysis Tool.

Analyzes patient tooth records and generates proactive suggestions.

This tool is used by Sarah (Clinical Agent) to:
1. Analyze tooth chart data
2. Identify teeth needing attention
3. Detect overdue follow-ups
4. Generate proactive suggestions for Decision Queue
5. Calculate risk scores

Part of the Tooth Chart feature for proactive dental care.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.tooth_record import ToothRecord, ToothStatus
from app.models.proactive_suggestion import (
    ProactiveSuggestion,
    SuggestionPriority,
    SuggestionStatus,
    SuggestionCategory,
)


class SarahToothAnalyzer:
    """Sarah's tooth analysis engine."""
    
    def __init__(self, db: Session, organization_id: UUID):
        self.db = db
        self.organization_id = organization_id
    
    def analyze_patient_teeth(self, patient_id: UUID) -> Dict[str, Any]:
        """
        Comprehensive analysis of patient's dental health.
        
        Returns:
            Analysis results with risk scores, suggestions, and flags
        """
        # Get all tooth records
        teeth = self.db.query(ToothRecord).filter(
            ToothRecord.organization_id == self.organization_id,
            ToothRecord.patient_id == patient_id,
            ToothRecord.deleted_at == None
        ).all()
        
        if not teeth:
            return {
                "patient_id": str(patient_id),
                "overall_risk_score": 0,
                "teeth_analyzed": 0,
                "suggestions": [],
                "flags": []
            }
        
        # Analyze each tooth
        tooth_analyses = []
        for tooth in teeth:
            analysis = self._analyze_single_tooth(tooth)
            tooth_analyses.append(analysis)
        
        # Calculate overall risk
        risk_scores = [t["risk_score"] for t in tooth_analyses]
        overall_risk = sum(risk_scores) // len(risk_scores) if risk_scores else 0
        
        # Generate suggestions
        suggestions = self._generate_suggestions(patient_id, tooth_analyses)
        
        # Identify flags
        flags = self._identify_flags(tooth_analyses)
        
        # Update tooth records with Sarah's analysis
        for tooth, analysis in zip(teeth, tooth_analyses):
            tooth.sarah_last_analysis_date = datetime.utcnow()
            tooth.sarah_risk_score = analysis["risk_score"]
            tooth.sarah_confidence = analysis["confidence"]
            tooth.sarah_suggestions = analysis["suggestions"]
        
        self.db.commit()
        
        return {
            "patient_id": str(patient_id),
            "overall_risk_score": overall_risk,
            "teeth_analyzed": len(teeth),
            "tooth_analyses": tooth_analyses,
            "suggestions": suggestions,
            "flags": flags,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    def _analyze_single_tooth(self, tooth: ToothRecord) -> Dict[str, Any]:
        """Analyze a single tooth and calculate risk score."""
        risk_score = 0
        confidence = 85  # Base confidence
        suggestions = []
        
        # Status-based risk
        status_risks = {
            ToothStatus.HEALTHY: 0,
            ToothStatus.FILLING: 10,
            ToothStatus.CAVITY: 60,
            ToothStatus.CROWN: 15,
            ToothStatus.ROOT_CANAL: 20,
            ToothStatus.NEEDS_ATTENTION: 80,
            ToothStatus.UNDER_TREATMENT: 40,
            ToothStatus.MISSING: 0,
            ToothStatus.EXTRACTION: 5,
            ToothStatus.IMPLANT: 10,
            ToothStatus.BRIDGE: 15,
        }
        risk_score += status_risks.get(tooth.status, 0)
        
        # Time-based risk
        if tooth.last_treatment_date:
            days_since = tooth.days_since_treatment
            
            # Old fillings/crowns need monitoring
            if tooth.status in [ToothStatus.FILLING, ToothStatus.CROWN]:
                if days_since > 1825:  # 5 years
                    risk_score += 20
                    suggestions.append("Consider evaluation - restoration is over 5 years old")
                    confidence = 90
                elif days_since > 1095:  # 3 years
                    risk_score += 10
                    suggestions.append("Monitor restoration - approaching 3 years")
            
            # Root canals need follow-up
            if tooth.status == ToothStatus.ROOT_CANAL:
                if days_since < 180:  # 6 months
                    risk_score += 15
                    suggestions.append("Recent root canal - ensure follow-up scheduled")
                    confidence = 95
        
        # Overdue follow-ups
        if tooth.is_followup_overdue:
            days_overdue = abs(tooth.days_until_followup)
            risk_score += min(days_overdue * 2, 50)  # Cap at 50
            suggestions.append(f"Follow-up overdue by {days_overdue} days")
            confidence = 95
        
        # Needs attention flag
        if tooth.needs_attention:
            risk_score += 30
            suggestions.append("Marked as needing attention")
            confidence = 100
        
        # Urgent flag
        if tooth.is_urgent:
            risk_score += 50
            suggestions.append("Marked as urgent")
            confidence = 100
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        return {
            "tooth_number_fdi": tooth.tooth_number_fdi,
            "tooth_name": tooth.tooth_name,
            "status": tooth.status.value,
            "risk_score": risk_score,
            "confidence": confidence,
            "suggestions": suggestions,
            "needs_attention": risk_score >= 60,
            "is_urgent": risk_score >= 80
        }
    
    def _generate_suggestions(
        self,
        patient_id: UUID,
        tooth_analyses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate proactive suggestions for Decision Queue."""
        suggestions = []
        
        # High-risk teeth
        high_risk_teeth = [t for t in tooth_analyses if t["risk_score"] >= 60]
        if high_risk_teeth:
            for tooth in high_risk_teeth:
                priority = SuggestionPriority.URGENT if tooth["risk_score"] >= 80 else SuggestionPriority.HIGH
                
                suggestion = ProactiveSuggestion(
                    organization_id=self.organization_id,
                    agent_name="sarah",
                    title=f"Tooth #{tooth['tooth_number_fdi']} Requires Attention",
                    message=f"{tooth['tooth_name']} (#{tooth['tooth_number_fdi']}) has elevated risk score ({tooth['risk_score']}/100). " +
                           f"Suggestions: {', '.join(tooth['suggestions'])}",
                    category=SuggestionCategory.TREATMENT,
                    priority=priority,
                    status=SuggestionStatus.PENDING,
                    actions=[
                        {"action": "schedule_appointment", "label": "Schedule Appointment"},
                        {"action": "add_to_treatment_plan", "label": "Add to Treatment Plan"},
                        {"action": "dismiss", "label": "Dismiss"}
                    ],
                    suggestion_metadata={
                        "tooth_number_fdi": tooth["tooth_number_fdi"],
                        "tooth_name": tooth["tooth_name"],
                        "risk_score": tooth["risk_score"],
                        "status": tooth["status"],
                        "analysis_suggestions": tooth["suggestions"]
                    },
                    confidence=tooth["confidence"],
                    patient_id=patient_id
                )
                
                self.db.add(suggestion)
                suggestions.append(suggestion.to_dict())
        
        # Overdue follow-ups
        overdue_teeth = [t for t in tooth_analyses if any("overdue" in s.lower() for s in t["suggestions"])]
        if overdue_teeth:
            tooth_numbers = [t["tooth_number_fdi"] for t in overdue_teeth]
            
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="sarah",
                title=f"{len(overdue_teeth)} Overdue Follow-up(s)",
                message=f"Patient has {len(overdue_teeth)} teeth with overdue follow-ups: " +
                       f"Teeth #{', #'.join(map(str, tooth_numbers))}. Schedule follow-up appointments.",
                category=SuggestionCategory.FOLLOW_UP,
                priority=SuggestionPriority.MEDIUM,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "schedule_followup", "label": "Schedule Follow-up"},
                    {"action": "contact_patient", "label": "Contact Patient"},
                    {"action": "dismiss", "label": "Dismiss"}
                ],
                suggestion_metadata={
                    "overdue_teeth": tooth_numbers,
                    "count": len(overdue_teeth)
                },
                confidence=95,
                patient_id=patient_id
            )
            
            self.db.add(suggestion)
            suggestions.append(suggestion.to_dict())
        
        self.db.commit()
        
        return suggestions
    
    def _identify_flags(self, tooth_analyses: List[Dict[str, Any]]) -> List[str]:
        """Identify important flags from analysis."""
        flags = []
        
        urgent_count = sum(1 for t in tooth_analyses if t["is_urgent"])
        if urgent_count > 0:
            flags.append(f"⚠️ {urgent_count} teeth require urgent attention")
        
        high_risk_count = sum(1 for t in tooth_analyses if t["needs_attention"])
        if high_risk_count > 0:
            flags.append(f"🔴 {high_risk_count} teeth need attention")
        
        overdue_count = sum(1 for t in tooth_analyses if any("overdue" in s.lower() for s in t["suggestions"]))
        if overdue_count > 0:
            flags.append(f"📅 {overdue_count} overdue follow-ups")
        
        old_restorations = sum(1 for t in tooth_analyses if any("5 years" in s for s in t["suggestions"]))
        if old_restorations > 0:
            flags.append(f"⏰ {old_restorations} restorations over 5 years old")
        
        return flags


# Tool function for LangChain integration

def analyze_patient_teeth_tool(
    patient_id: str,
    db: Session,
    organization_id: str
) -> str:
    """
    Analyze patient's tooth chart and generate proactive suggestions.
    
    Args:
        patient_id: UUID of the patient
        db: Database session
        organization_id: UUID of the organization
    
    Returns:
        JSON string with analysis results
    """
    import json
    from uuid import UUID
    
    analyzer = SarahToothAnalyzer(db, UUID(organization_id))
    results = analyzer.analyze_patient_teeth(UUID(patient_id))
    
    return json.dumps(results, indent=2)

