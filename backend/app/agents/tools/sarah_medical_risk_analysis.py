"""
Sarah Medical Risk Analysis Tool.

Analyzes patient medical questionnaires and generates risk assessments
and proactive alerts for high-risk conditions.

This tool is used by Sarah (Clinical Agent) to:
1. Analyze medical history
2. Identify risk factors
3. Detect contraindications for treatments
4. Generate proactive alerts
5. Calculate overall risk score

Part of comprehensive patient safety and proactive care.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.medical_questionnaire import (
    MedicalQuestionnaire,
    RiskLevel,
    QuestionnaireStatus,
)
from app.models.proactive_suggestion import (
    ProactiveSuggestion,
    SuggestionPriority,
    SuggestionStatus,
    SuggestionCategory,
)


class SarahMedicalRiskAnalyzer:
    """Sarah's medical risk analysis engine."""
    
    # High-risk medical conditions
    HIGH_RISK_CONDITIONS = [
        "diabetes", "heart disease", "hypertension", "bleeding disorder",
        "hemophilia", "cancer", "hiv", "aids", "hepatitis", "kidney disease",
        "liver disease", "stroke", "heart attack", "pacemaker",
        "congenital heart", "heart valve", "endocarditis"
    ]
    
    # Medications requiring caution
    CAUTION_MEDICATIONS = [
        "warfarin", "coumadin", "aspirin", "plavix", "clopidogrel",
        "heparin", "xarelto", "eliquis", "pradaxa",  # Blood thinners
        "bisphosphonate", "fosamax", "boniva",  # Bone medications
        "chemotherapy", "radiation", "immunosuppressant"  # Cancer/immune
    ]
    
    # Allergies requiring special attention
    CRITICAL_ALLERGIES = [
        "penicillin", "latex", "lidocaine", "local anesthetic",
        "epinephrine", "anesthesia"
    ]
    
    def __init__(self, db: Session, organization_id: UUID):
        self.db = db
        self.organization_id = organization_id
    
    def analyze_questionnaire(self, questionnaire_id: UUID) -> Dict[str, Any]:
        """
        Comprehensive risk analysis of medical questionnaire.
        
        Returns:
            Analysis results with risk level, score, factors, and recommendations
        """
        questionnaire = self.db.query(MedicalQuestionnaire).filter(
            MedicalQuestionnaire.id == questionnaire_id,
            MedicalQuestionnaire.organization_id == self.organization_id,
            MedicalQuestionnaire.deleted_at == None
        ).first()
        
        if not questionnaire:
            raise ValueError("Questionnaire not found")
        
        # Calculate risk score
        risk_score = 0
        risk_factors = []
        contraindications = []
        recommendations = []
        confidence = 90  # Base confidence
        
        # Analyze medical conditions
        condition_risk, condition_factors = self._analyze_medical_conditions(questionnaire)
        risk_score += condition_risk
        risk_factors.extend(condition_factors)
        
        # Analyze medications
        medication_risk, medication_factors, med_contraindications = self._analyze_medications(questionnaire)
        risk_score += medication_risk
        risk_factors.extend(medication_factors)
        contraindications.extend(med_contraindications)
        
        # Analyze allergies
        allergy_risk, allergy_factors, allergy_contraindications = self._analyze_allergies(questionnaire)
        risk_score += allergy_risk
        risk_factors.extend(allergy_factors)
        contraindications.extend(allergy_contraindications)
        
        # Analyze lifestyle
        lifestyle_risk, lifestyle_factors = self._analyze_lifestyle(questionnaire)
        risk_score += lifestyle_risk
        risk_factors.extend(lifestyle_factors)
        
        # Analyze pregnancy/women's health
        pregnancy_risk, pregnancy_factors, pregnancy_contraindications = self._analyze_pregnancy(questionnaire)
        risk_score += pregnancy_risk
        risk_factors.extend(pregnancy_factors)
        contraindications.extend(pregnancy_contraindications)
        
        # Analyze dental-specific factors
        dental_risk, dental_factors = self._analyze_dental_factors(questionnaire)
        risk_score += dental_risk
        risk_factors.extend(dental_factors)
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        if risk_score >= 75:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 50:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 25:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            questionnaire, risk_level, risk_factors, contraindications
        )
        
        # Update questionnaire with Sarah's analysis
        questionnaire.sarah_risk_level = risk_level
        questionnaire.sarah_risk_score = risk_score
        questionnaire.sarah_risk_factors = [{"factor": f} for f in risk_factors]
        questionnaire.sarah_contraindications = [{"contraindication": c} for c in contraindications]
        questionnaire.sarah_recommendations = [{"recommendation": r} for r in recommendations]
        questionnaire.sarah_last_analysis_date = datetime.utcnow()
        questionnaire.sarah_confidence = confidence
        
        self.db.commit()
        
        # Generate proactive suggestions
        suggestions = self._generate_proactive_suggestions(
            questionnaire, risk_level, risk_score, risk_factors, contraindications
        )
        
        return {
            "questionnaire_id": str(questionnaire_id),
            "patient_id": str(questionnaire.patient_id),
            "risk_level": risk_level.value,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "contraindications": contraindications,
            "recommendations": recommendations,
            "confidence": confidence,
            "proactive_suggestions": suggestions,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    def _analyze_medical_conditions(self, q: MedicalQuestionnaire) -> tuple[int, List[str]]:
        """Analyze medical conditions for risk."""
        risk = 0
        factors = []
        
        if not q.medical_conditions:
            return 0, []
        
        for condition in q.medical_conditions:
            condition_name = condition.get("name", "").lower()
            
            # Check high-risk conditions
            for high_risk in self.HIGH_RISK_CONDITIONS:
                if high_risk in condition_name:
                    risk += 15
                    factors.append(f"High-risk condition: {condition.get('name')}")
                    break
        
        # Special flags
        if q.has_high_risk_conditions:
            risk += 10
            factors.append("Multiple high-risk conditions present")
        
        if q.requires_antibiotic_prophylaxis:
            risk += 20
            factors.append("Requires antibiotic prophylaxis")
        
        return risk, factors
    
    def _analyze_medications(self, q: MedicalQuestionnaire) -> tuple[int, List[str], List[str]]:
        """Analyze medications for risk and contraindications."""
        risk = 0
        factors = []
        contraindications = []
        
        if not q.medications:
            return 0, [], []
        
        for medication in q.medications:
            med_name = medication.get("name", "").lower()
            
            # Check caution medications
            for caution_med in self.CAUTION_MEDICATIONS:
                if caution_med in med_name:
                    risk += 10
                    factors.append(f"Caution medication: {medication.get('name')}")
                    
                    # Add specific contraindications
                    if "warfarin" in med_name or "coumadin" in med_name:
                        contraindications.append("Avoid procedures with high bleeding risk without medical clearance")
                    elif "bisphosphonate" in med_name or "fosamax" in med_name:
                        contraindications.append("Risk of osteonecrosis - consult before extractions/surgery")
                    elif "chemotherapy" in med_name:
                        contraindications.append("Immunocompromised - infection risk elevated")
                    
                    break
        
        if q.has_bleeding_risk:
            risk += 15
            factors.append("Bleeding risk due to anticoagulant medication")
            contraindications.append("Consult physician before invasive procedures")
        
        return risk, factors, contraindications
    
    def _analyze_allergies(self, q: MedicalQuestionnaire) -> tuple[int, List[str], List[str]]:
        """Analyze allergies for risk and contraindications."""
        risk = 0
        factors = []
        contraindications = []
        
        if not q.allergies:
            return 0, [], []
        
        for allergy in q.allergies:
            allergy_name = allergy.get("name", "").lower()
            severity = allergy.get("severity", "").lower()
            
            # Check critical allergies
            for critical in self.CRITICAL_ALLERGIES:
                if critical in allergy_name:
                    risk += 20 if severity == "severe" else 10
                    factors.append(f"Critical allergy: {allergy.get('name')} ({severity})")
                    
                    # Add contraindications
                    if "penicillin" in allergy_name:
                        contraindications.append("Avoid penicillin-based antibiotics")
                    elif "latex" in allergy_name:
                        contraindications.append("Use latex-free gloves and equipment")
                    elif "lidocaine" in allergy_name or "anesthetic" in allergy_name:
                        contraindications.append("Alternative anesthetic required - consult before procedures")
                    
                    break
        
        return risk, factors, contraindications
    
    def _analyze_lifestyle(self, q: MedicalQuestionnaire) -> tuple[int, List[str]]:
        """Analyze lifestyle factors for risk."""
        risk = 0
        factors = []
        
        if q.smoking:
            risk += 15
            factors.append(f"Smoking: {q.smoking_frequency or 'frequency not specified'}")
            factors.append("Increased risk of gum disease and implant failure")
        
        if q.alcohol:
            risk += 5
            factors.append(f"Alcohol consumption: {q.alcohol_frequency or 'frequency not specified'}")
        
        return risk, factors
    
    def _analyze_pregnancy(self, q: MedicalQuestionnaire) -> tuple[int, List[str], List[str]]:
        """Analyze pregnancy/women's health for risk and contraindications."""
        risk = 0
        factors = []
        contraindications = []
        
        if q.is_pregnant:
            risk += 20
            factors.append(f"Pregnant - Trimester {q.pregnancy_trimester or 'not specified'}")
            contraindications.append("Avoid X-rays unless absolutely necessary")
            contraindications.append("Limit medications - consult OB/GYN")
            if q.pregnancy_trimester == 1:
                contraindications.append("First trimester - defer elective procedures")
        
        if q.is_breastfeeding:
            risk += 10
            factors.append("Breastfeeding")
            contraindications.append("Caution with medications - check compatibility")
        
        return risk, factors, contraindications
    
    def _analyze_dental_factors(self, q: MedicalQuestionnaire) -> tuple[int, List[str]]:
        """Analyze dental-specific factors."""
        risk = 0
        factors = []
        
        if q.has_dental_anxiety:
            risk += 10
            factors.append(f"Severe dental anxiety (level {q.dental_anxiety_level}/10)")
            factors.append("Consider sedation options and extra appointment time")
        
        if q.gum_disease_history:
            risk += 10
            factors.append("History of gum disease")
        
        if q.teeth_grinding:
            risk += 5
            factors.append("Teeth grinding (bruxism)")
        
        if q.jaw_pain:
            risk += 5
            factors.append("Jaw pain (possible TMJ)")
        
        return risk, factors
    
    def _generate_recommendations(
        self,
        q: MedicalQuestionnaire,
        risk_level: RiskLevel,
        risk_factors: List[str],
        contraindications: List[str]
    ) -> List[str]:
        """Generate clinical recommendations."""
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Consult with patient's physician before major procedures")
            recommendations.append("Review medical history at every appointment")
        
        if q.has_bleeding_risk:
            recommendations.append("INR check required before invasive procedures")
        
        if q.requires_antibiotic_prophylaxis:
            recommendations.append("Prescribe antibiotic prophylaxis per AHA guidelines")
        
        if q.has_dental_anxiety:
            recommendations.append("Schedule longer appointments with breaks")
            recommendations.append("Consider sedation dentistry options")
        
        if q.smoking:
            recommendations.append("Provide smoking cessation resources")
        
        if q.gum_disease_history:
            recommendations.append("Increase frequency of periodontal maintenance")
        
        if not recommendations:
            recommendations.append("Standard precautions apply")
        
        return recommendations
    
    def _generate_proactive_suggestions(
        self,
        q: MedicalQuestionnaire,
        risk_level: RiskLevel,
        risk_score: int,
        risk_factors: List[str],
        contraindications: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate proactive suggestions for Decision Queue."""
        suggestions = []
        
        # High/Critical risk alert
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            priority = SuggestionPriority.URGENT if risk_level == RiskLevel.CRITICAL else SuggestionPriority.HIGH
            
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="sarah",
                title=f"{risk_level.value.upper()} Risk Patient - Medical Review Required",
                message=f"Patient has {len(risk_factors)} risk factors with overall risk score of {risk_score}/100. " +
                       f"Medical consultation recommended before procedures. Key factors: {', '.join(risk_factors[:3])}",
                category=SuggestionCategory.CLINICAL_ALERT,
                priority=priority,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "schedule_consultation", "label": "Schedule Medical Consultation"},
                    {"action": "flag_chart", "label": "Flag Patient Chart"},
                    {"action": "dismiss", "label": "Acknowledge"}
                ],
                suggestion_metadata={
                    "risk_level": risk_level.value,
                    "risk_score": risk_score,
                    "risk_factors": risk_factors,
                    "contraindications": contraindications
                },
                confidence=95,
                patient_id=q.patient_id
            )
            
            self.db.add(suggestion)
            suggestions.append(suggestion.to_dict())
        
        # Antibiotic prophylaxis reminder
        if q.requires_antibiotic_prophylaxis:
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="sarah",
                title="Antibiotic Prophylaxis Required",
                message=f"Patient requires antibiotic prophylaxis before dental procedures per AHA guidelines. " +
                       f"Ensure prescription is provided before invasive treatment.",
                category=SuggestionCategory.CLINICAL_ALERT,
                priority=SuggestionPriority.HIGH,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "prescribe_antibiotic", "label": "Prescribe Antibiotic"},
                    {"action": "add_to_chart", "label": "Add to Chart Notes"},
                    {"action": "dismiss", "label": "Already Handled"}
                ],
                suggestion_metadata={
                    "requires_prophylaxis": True,
                    "conditions": [c.get("name") for c in (q.medical_conditions or [])]
                },
                confidence=100,
                patient_id=q.patient_id
            )
            
            self.db.add(suggestion)
            suggestions.append(suggestion.to_dict())
        
        # Bleeding risk alert
        if q.has_bleeding_risk:
            suggestion = ProactiveSuggestion(
                organization_id=self.organization_id,
                agent_name="sarah",
                title="Bleeding Risk - INR Check Required",
                message=f"Patient is on anticoagulant medication. INR check required before invasive procedures. " +
                       f"Consult with physician if INR is outside therapeutic range.",
                category=SuggestionCategory.CLINICAL_ALERT,
                priority=SuggestionPriority.HIGH,
                status=SuggestionStatus.PENDING,
                actions=[
                    {"action": "order_inr", "label": "Order INR Test"},
                    {"action": "consult_physician", "label": "Consult Physician"},
                    {"action": "dismiss", "label": "Already Checked"}
                ],
                suggestion_metadata={
                    "bleeding_risk": True,
                    "medications": [m.get("name") for m in (q.medications or [])]
                },
                confidence=95,
                patient_id=q.patient_id
            )
            
            self.db.add(suggestion)
            suggestions.append(suggestion.to_dict())
        
        self.db.commit()
        
        return suggestions


# Tool function for LangChain integration

def analyze_medical_questionnaire_tool(
    questionnaire_id: str,
    db: Session,
    organization_id: str
) -> str:
    """
    Analyze patient's medical questionnaire and generate risk assessment.
    
    Args:
        questionnaire_id: UUID of the questionnaire
        db: Database session
        organization_id: UUID of the organization
    
    Returns:
        JSON string with analysis results
    """
    import json
    from uuid import UUID
    
    analyzer = SarahMedicalRiskAnalyzer(db, UUID(organization_id))
    results = analyzer.analyze_questionnaire(UUID(questionnaire_id))
    
    return json.dumps(results, indent=2)

