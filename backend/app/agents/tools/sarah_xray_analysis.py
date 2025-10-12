"""
Sarah X-Ray Analysis Tool.

Analyzes dental X-ray images and generates findings, recommendations,
and proactive alerts.

This tool is used by Sarah (Clinical Agent) to:
1. Analyze X-ray images (periapical, bitewing, panoramic, CBCT)
2. Detect abnormalities (cavities, bone loss, infections)
3. Assess severity and urgency
4. Generate clinical recommendations
5. Create proactive alerts for Decision Queue

Part of comprehensive diagnostic support system.

NOTE: This is a mock implementation. In production, this would integrate
with actual AI vision models (e.g., OpenAI Vision, Google Cloud Vision,
or specialized dental AI like Overjet, Pearl, Denti.AI).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.xray import (
    XRay,
    XRayType,
    XRayFindingSeverity,
    XRayQuality,
)
from app.models.proactive_suggestion import (
    ProactiveSuggestion,
    SuggestionPriority,
    SuggestionStatus,
    SuggestionCategory,
)


class SarahXRayAnalyzer:
    """Sarah's X-ray analysis engine."""
    
    def __init__(self, db: Session, organization_id: UUID):
        self.db = db
        self.organization_id = organization_id
    
    def analyze_xray(self, xray_id: UUID) -> Dict[str, Any]:
        """
        Comprehensive X-ray analysis.
        
        Returns:
            Analysis results with findings, severity, recommendations, and alerts
        """
        xray = self.db.query(XRay).filter(
            XRay.id == xray_id,
            XRay.organization_id == self.organization_id,
            XRay.deleted_at == None
        ).first()
        
        if not xray:
            raise ValueError("X-ray not found")
        
        # Analyze based on X-ray type
        if xray.xray_type == XRayType.PERIAPICAL:
            findings, severity = self._analyze_periapical(xray)
        elif xray.xray_type == XRayType.BITEWING:
            findings, severity = self._analyze_bitewing(xray)
        elif xray.xray_type == XRayType.PANORAMIC:
            findings, severity = self._analyze_panoramic(xray)
        elif xray.xray_type == XRayType.CBCT:
            findings, severity = self._analyze_cbct(xray)
        else:
            findings, severity = self._analyze_generic(xray)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(xray, findings, severity)
        
        # Calculate confidence
        confidence = self._calculate_confidence(xray, findings)
        
        # Update X-ray with Sarah's analysis
        xray.sarah_analyzed = True
        xray.sarah_analysis_date = datetime.utcnow()
        xray.sarah_findings = findings
        xray.sarah_severity = severity
        xray.sarah_recommendations = recommendations
        xray.sarah_confidence = confidence
        
        # Generate proactive alerts
        alerts = self._generate_proactive_alerts(xray, findings, severity, recommendations)
        xray.sarah_alerts = alerts
        
        self.db.commit()
        
        return {
            "xray_id": str(xray_id),
            "xray_type": xray.xray_type.value,
            "patient_id": str(xray.patient_id),
            "analysis_date": datetime.utcnow().isoformat(),
            "findings": findings,
            "severity": severity.value,
            "recommendations": recommendations,
            "confidence": confidence,
            "alerts": alerts,
            "requires_immediate_attention": xray.requires_immediate_attention
        }
    
    def _analyze_periapical(self, xray: XRay) -> tuple[List[Dict], XRayFindingSeverity]:
        """Analyze periapical X-ray (single tooth root)."""
        findings = []
        severity = XRayFindingSeverity.NORMAL
        
        # Mock analysis - in production, use AI vision model
        # Simulate various findings based on randomness or patterns
        
        # Check for normal structures
        findings.append({
            "finding": "Crown structure intact",
            "location": "crown",
            "confidence": 95,
            "urgent": False
        })
        
        findings.append({
            "finding": "Root structure visible",
            "location": "root",
            "confidence": 90,
            "urgent": False
        })
        
        findings.append({
            "finding": "Periodontal ligament space normal",
            "location": "periapical",
            "confidence": 85,
            "urgent": False
        })
        
        # Simulate potential findings (mock)
        # In production, AI model would detect these
        
        return findings, severity
    
    def _analyze_bitewing(self, xray: XRay) -> tuple[List[Dict], XRayFindingSeverity]:
        """Analyze bitewing X-ray (crowns of upper/lower teeth)."""
        findings = []
        severity = XRayFindingSeverity.NORMAL
        
        # Mock analysis
        findings.append({
            "finding": "No interproximal decay detected",
            "location": "between teeth",
            "confidence": 90,
            "urgent": False
        })
        
        findings.append({
            "finding": "Bone levels normal",
            "location": "alveolar bone",
            "confidence": 85,
            "urgent": False
        })
        
        findings.append({
            "finding": "No visible calculus",
            "location": "tooth surfaces",
            "confidence": 80,
            "urgent": False
        })
        
        return findings, severity
    
    def _analyze_panoramic(self, xray: XRay) -> tuple[List[Dict], XRayFindingSeverity]:
        """Analyze panoramic X-ray (full mouth)."""
        findings = []
        severity = XRayFindingSeverity.NORMAL
        
        # Mock analysis
        findings.append({
            "finding": "All teeth present and accounted for",
            "location": "full dentition",
            "confidence": 95,
            "urgent": False
        })
        
        findings.append({
            "finding": "TMJ structures normal",
            "location": "temporomandibular joint",
            "confidence": 85,
            "urgent": False
        })
        
        findings.append({
            "finding": "Maxillary sinuses clear",
            "location": "sinuses",
            "confidence": 80,
            "urgent": False
        })
        
        findings.append({
            "finding": "No impacted teeth",
            "location": "third molars",
            "confidence": 90,
            "urgent": False
        })
        
        return findings, severity
    
    def _analyze_cbct(self, xray: XRay) -> tuple[List[Dict], XRayFindingSeverity]:
        """Analyze CBCT (3D cone beam CT)."""
        findings = []
        severity = XRayFindingSeverity.NORMAL
        
        # Mock analysis
        findings.append({
            "finding": "3D bone structure intact",
            "location": "jaw",
            "confidence": 95,
            "urgent": False
        })
        
        findings.append({
            "finding": "Adequate bone density for implant placement",
            "location": "implant site",
            "confidence": 90,
            "urgent": False
        })
        
        findings.append({
            "finding": "No sinus perforation risk",
            "location": "maxillary sinus",
            "confidence": 85,
            "urgent": False
        })
        
        return findings, severity
    
    def _analyze_generic(self, xray: XRay) -> tuple[List[Dict], XRayFindingSeverity]:
        """Generic analysis for other X-ray types."""
        findings = []
        severity = XRayFindingSeverity.NORMAL
        
        findings.append({
            "finding": "Image quality acceptable for diagnosis",
            "location": "overall",
            "confidence": 85,
            "urgent": False
        })
        
        return findings, severity
    
    def _generate_recommendations(
        self,
        xray: XRay,
        findings: List[Dict],
        severity: XRayFindingSeverity
    ) -> List[Dict]:
        """Generate clinical recommendations based on findings."""
        recommendations = []
        
        if severity == XRayFindingSeverity.NORMAL:
            recommendations.append({
                "recommendation": "Continue routine monitoring",
                "priority": "low",
                "timeframe": "next regular checkup"
            })
            
            recommendations.append({
                "recommendation": "Schedule follow-up X-ray in 12 months",
                "priority": "low",
                "timeframe": "12 months"
            })
        
        elif severity == XRayFindingSeverity.MINOR:
            recommendations.append({
                "recommendation": "Monitor area closely",
                "priority": "medium",
                "timeframe": "6 months"
            })
            
            recommendations.append({
                "recommendation": "Consider preventive treatment",
                "priority": "medium",
                "timeframe": "3-6 months"
            })
        
        elif severity == XRayFindingSeverity.MODERATE:
            recommendations.append({
                "recommendation": "Schedule treatment consultation",
                "priority": "high",
                "timeframe": "2-4 weeks"
            })
            
            recommendations.append({
                "recommendation": "Discuss treatment options with patient",
                "priority": "high",
                "timeframe": "immediately"
            })
        
        elif severity in [XRayFindingSeverity.SEVERE, XRayFindingSeverity.CRITICAL]:
            recommendations.append({
                "recommendation": "Immediate clinical evaluation required",
                "priority": "urgent",
                "timeframe": "within 24-48 hours"
            })
            
            recommendations.append({
                "recommendation": "Consider referral to specialist",
                "priority": "urgent",
                "timeframe": "immediately"
            })
            
            recommendations.append({
                "recommendation": "Inform patient of urgent findings",
                "priority": "urgent",
                "timeframe": "immediately"
            })
        
        return recommendations
    
    def _calculate_confidence(self, xray: XRay, findings: List[Dict]) -> int:
        """Calculate confidence score for analysis."""
        base_confidence = 85
        
        # Adjust based on image quality
        if xray.quality == XRayQuality.EXCELLENT:
            base_confidence += 10
        elif xray.quality == XRayQuality.GOOD:
            base_confidence += 5
        elif xray.quality == XRayQuality.POOR:
            base_confidence -= 15
        elif xray.quality == XRayQuality.RETAKE_REQUIRED:
            base_confidence -= 30
        
        # Adjust based on X-ray type (some are easier to analyze)
        if xray.xray_type == XRayType.PERIAPICAL:
            base_confidence += 5  # Single tooth, easier
        elif xray.xray_type == XRayType.PANORAMIC:
            base_confidence -= 5  # Full mouth, more complex
        elif xray.xray_type == XRayType.CBCT:
            base_confidence += 10  # 3D, most detailed
        
        # Cap between 0-100
        return max(0, min(100, base_confidence))
    
    def _generate_proactive_alerts(
        self,
        xray: XRay,
        findings: List[Dict],
        severity: XRayFindingSeverity,
        recommendations: List[Dict]
    ) -> List[Dict]:
        """Generate proactive alerts for Decision Queue."""
        alerts = []
        
        # Critical/Severe findings alert
        if severity in [XRayFindingSeverity.SEVERE, XRayFindingSeverity.CRITICAL]:
            priority = SuggestionPriority.URGENT if severity == XRayFindingSeverity.CRITICAL else SuggestionPriority.HIGH
            
            urgent_findings = [f["finding"] for f in findings if f.get("urgent", False)]
            findings_text = ", ".join(urgent_findings) if urgent_findings else "Critical findings detected"
            
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="sarah",
                title=f"{severity.value.upper()} X-Ray Findings - Immediate Attention Required",
                message=f"X-ray analysis revealed {severity.value} findings: {findings_text}. " +
                       f"Patient requires immediate clinical evaluation. Type: {xray.xray_type.value}",
                category=SuggestionCategory.CLINICAL_ALERT,
                priority=priority,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "schedule_urgent_appointment", "label": "Schedule Urgent Appointment"},
                    {"action": "call_patient", "label": "Call Patient Now"},
                    {"action": "flag_chart", "label": "Flag Patient Chart"},
                    {"action": "dismiss", "label": "Acknowledge"}
                ],
                suggestion_metadata={
                    "xray_id": str(xray.id),
                    "xray_type": xray.xray_type.value,
                    "severity": severity.value,
                    "findings": findings,
                    "recommendations": recommendations
                },
                confidence=xray.sarah_confidence or 85,
                patient_id=xray.patient_id
            )
            
            self.db.add(suggestion)
            alerts.append(suggestion.to_dict())
        
        # Moderate findings alert
        elif severity == XRayFindingSeverity.MODERATE:
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="sarah",
                title="X-Ray Findings Require Follow-Up",
                message=f"X-ray analysis revealed moderate findings that require treatment consultation. " +
                       f"Schedule appointment within 2-4 weeks. Type: {xray.xray_type.value}",
                category=SuggestionCategory.CLINICAL_ALERT,
                priority=SuggestionPriority.MEDIUM,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "schedule_consultation", "label": "Schedule Consultation"},
                    {"action": "add_to_treatment_plan", "label": "Add to Treatment Plan"},
                    {"action": "dismiss", "label": "Acknowledge"}
                ],
                suggestion_metadata={
                    "xray_id": str(xray.id),
                    "xray_type": xray.xray_type.value,
                    "severity": severity.value,
                    "findings": findings
                },
                confidence=xray.sarah_confidence or 85,
                patient_id=xray.patient_id
            )
            
            self.db.add(suggestion)
            alerts.append(suggestion.to_dict())
        
        # Poor quality alert
        if xray.quality == XRayQuality.RETAKE_REQUIRED or xray.needs_retake:
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="sarah",
                title="X-Ray Retake Required",
                message=f"X-ray quality is insufficient for accurate diagnosis. Retake recommended. " +
                       f"Reason: {xray.retake_reason or 'Poor image quality'}",
                category=SuggestionCategory.CLINICAL_ALERT,
                priority=SuggestionPriority.MEDIUM,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "schedule_retake", "label": "Schedule Retake"},
                    {"action": "notify_patient", "label": "Notify Patient"},
                    {"action": "dismiss", "label": "Proceed Anyway"}
                ],
                suggestion_metadata={
                    "xray_id": str(xray.id),
                    "quality": xray.quality.value if xray.quality else "unknown",
                    "retake_reason": xray.retake_reason
                },
                confidence=100,
                patient_id=xray.patient_id
            )
            
            self.db.add(suggestion)
            alerts.append(suggestion.to_dict())
        
        self.db.commit()
        
        return alerts


# Tool function for LangChain integration

def analyze_xray_tool(
    xray_id: str,
    db: Session,
    organization_id: str
) -> str:
    """
    Analyze dental X-ray and generate findings and recommendations.
    
    Args:
        xray_id: UUID of the X-ray
        db: Database session
        organization_id: UUID of the organization
    
    Returns:
        JSON string with analysis results
    """
    import json
    from uuid import UUID
    
    analyzer = SarahXRayAnalyzer(db, UUID(organization_id))
    results = analyzer.analyze_xray(UUID(xray_id))
    
    return json.dumps(results, indent=2)

