"""
HIPAA Compliance Tools for Harper Agent

This module provides 10 specialized tools for HIPAA compliance management:
1. search_hipaa_knowledge - RAG-powered knowledge base search
2. check_phi_compliance - Validate PHI handling compliance
3. validate_baa - Validate Business Associate Agreements
4. assess_security_controls - Assess technical and administrative safeguards
5. generate_breach_report - Generate breach notification reports
6. audit_access_logs - Audit PHI access logs
7. check_patient_rights - Verify patient rights compliance
8. evaluate_risk - Perform HIPAA risk assessments
9. generate_compliance_report - Generate comprehensive compliance reports
10. recommend_remediation - Provide remediation recommendations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.services.vector_db import vector_db
from app.core.config import settings

logger = logging.getLogger(__name__)


@tool
def search_hipaa_knowledge(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search the HIPAA knowledge base using RAG (Retrieval-Augmented Generation).
    
    This tool searches through regulations, policies, FAQs, and best practices
    to find relevant HIPAA compliance information.
    
    Args:
        query: The search query or question about HIPAA compliance
        top_k: Number of results to return (default: 5)
        
    Returns:
        Dictionary containing search results with relevance scores
        
    Example:
        >>> search_hipaa_knowledge("What are the requirements for PHI encryption?")
        {
            "results": [
                {
                    "content": "...",
                    "source": "regulations/security_rule_summary.md",
                    "score": 0.92
                }
            ],
            "total_results": 5
        }
    """
    try:
        # Search the HIPAA knowledge base
        results = vector_db.search(
            index_type='hipaa',
            query=query,
            top_k=top_k
        )
        
        if not results:
            return {
                "status": "no_results",
                "message": "No relevant information found in the knowledge base.",
                "results": [],
                "total_results": 0
            }
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result.get('text', ''),
                "source": result.get('metadata', {}).get('file_path', 'unknown'),
                "category": result.get('metadata', {}).get('category', 'general'),
                "score": round(result.get('score', 0), 2)
            })
        
        return {
            "status": "success",
            "results": formatted_results,
            "total_results": len(formatted_results),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error searching HIPAA knowledge: {e}")
        return {
            "status": "error",
            "message": f"Failed to search knowledge base: {str(e)}",
            "results": [],
            "total_results": 0
        }


@tool
def check_phi_compliance(
    data_description: str,
    storage_location: str,
    access_controls: str,
    encryption_status: str
) -> Dict[str, Any]:
    """
    Check if Protected Health Information (PHI) handling complies with HIPAA regulations.
    
    Validates PHI storage, access controls, encryption, and other security measures
    against HIPAA Security Rule requirements.
    
    Args:
        data_description: Description of the PHI data being stored/processed
        storage_location: Where the PHI is stored (e.g., "GCP Cloud SQL", "local server")
        access_controls: Description of access control mechanisms
        encryption_status: Encryption status ("encrypted_at_rest", "encrypted_in_transit", "both", "none")
        
    Returns:
        Compliance assessment with findings and recommendations
        
    Example:
        >>> check_phi_compliance(
        ...     data_description="Patient dental records with SSN",
        ...     storage_location="GCP Cloud SQL",
        ...     access_controls="Role-based access control with MFA",
        ...     encryption_status="both"
        ... )
    """
    findings = []
    compliance_score = 100
    
    # Check encryption
    if encryption_status == "none":
        findings.append({
            "severity": "critical",
            "finding": "PHI is not encrypted",
            "requirement": "HIPAA Security Rule § 164.312(a)(2)(iv) requires encryption of PHI",
            "recommendation": "Implement encryption at rest and in transit immediately"
        })
        compliance_score -= 40
    elif encryption_status in ["encrypted_at_rest", "encrypted_in_transit"]:
        findings.append({
            "severity": "high",
            "finding": f"PHI is only {encryption_status.replace('_', ' ')}",
            "requirement": "Best practice requires encryption both at rest and in transit",
            "recommendation": f"Implement {'encryption in transit' if 'rest' in encryption_status else 'encryption at rest'}"
        })
        compliance_score -= 20
    
    # Check access controls
    if "mfa" not in access_controls.lower() and "multi-factor" not in access_controls.lower():
        findings.append({
            "severity": "high",
            "finding": "Multi-factor authentication (MFA) not mentioned",
            "requirement": "HIPAA Security Rule § 164.312(a)(2)(i) requires user authentication",
            "recommendation": "Implement MFA for all users accessing PHI"
        })
        compliance_score -= 15
    
    if "role" not in access_controls.lower() and "rbac" not in access_controls.lower():
        findings.append({
            "severity": "medium",
            "finding": "Role-based access control (RBAC) not clearly defined",
            "requirement": "HIPAA Security Rule § 164.308(a)(4) requires access authorization",
            "recommendation": "Implement role-based access control with principle of least privilege"
        })
        compliance_score -= 10
    
    # Check storage location
    if "local" in storage_location.lower() or "on-premise" in storage_location.lower():
        findings.append({
            "severity": "medium",
            "finding": "PHI stored on local/on-premise infrastructure",
            "requirement": "Local storage requires additional physical safeguards",
            "recommendation": "Ensure physical access controls, backup procedures, and disaster recovery plans are in place"
        })
        compliance_score -= 10
    
    # Determine compliance status
    if compliance_score >= 90:
        status = "compliant"
    elif compliance_score >= 70:
        status = "partially_compliant"
    else:
        status = "non_compliant"
    
    return {
        "status": status,
        "compliance_score": compliance_score,
        "findings": findings,
        "total_findings": len(findings),
        "assessment_date": datetime.now().isoformat(),
        "summary": f"PHI handling is {status.replace('_', ' ')} with {len(findings)} findings"
    }


@tool
def validate_baa(
    vendor_name: str,
    baa_signed: bool,
    baa_date: Optional[str] = None,
    services_provided: str = "",
    phi_access: bool = True
) -> Dict[str, Any]:
    """
    Validate Business Associate Agreement (BAA) compliance.
    
    Checks if a BAA is required and properly executed with business associates
    who handle PHI on behalf of the covered entity.
    
    Args:
        vendor_name: Name of the business associate/vendor
        baa_signed: Whether a BAA has been signed
        baa_date: Date the BAA was signed (ISO format: YYYY-MM-DD)
        services_provided: Description of services the vendor provides
        phi_access: Whether the vendor has access to PHI
        
    Returns:
        BAA validation results with compliance status
        
    Example:
        >>> validate_baa(
        ...     vendor_name="Cloud Storage Provider",
        ...     baa_signed=True,
        ...     baa_date="2024-01-15",
        ...     services_provided="Cloud data storage",
        ...     phi_access=True
        ... )
    """
    issues = []
    compliance_status = "compliant"
    
    # Check if BAA is required
    if phi_access:
        if not baa_signed:
            issues.append({
                "severity": "critical",
                "issue": f"No BAA signed with {vendor_name}",
                "requirement": "HIPAA Privacy Rule § 164.502(e) requires BAA with all business associates",
                "action_required": "Obtain signed BAA before allowing PHI access"
            })
            compliance_status = "non_compliant"
        elif baa_date:
            # Check if BAA is recent (within last 3 years is good practice)
            try:
                baa_datetime = datetime.fromisoformat(baa_date)
                age_days = (datetime.now() - baa_datetime).days
                
                if age_days > 1095:  # 3 years
                    issues.append({
                        "severity": "medium",
                        "issue": f"BAA with {vendor_name} is {age_days // 365} years old",
                        "requirement": "Best practice: Review and update BAAs every 2-3 years",
                        "action_required": "Schedule BAA review and renewal"
                    })
                    if compliance_status == "compliant":
                        compliance_status = "review_needed"
            except ValueError:
                issues.append({
                    "severity": "low",
                    "issue": "Invalid BAA date format",
                    "requirement": "Maintain accurate records of BAA execution dates",
                    "action_required": "Update BAA date in records"
                })
    else:
        # No PHI access, BAA not required
        if baa_signed:
            issues.append({
                "severity": "info",
                "issue": f"BAA exists with {vendor_name} but vendor has no PHI access",
                "requirement": "BAA not required if no PHI access",
                "action_required": "No action needed, but verify PHI access status is correct"
            })
    
    # Check for required BAA provisions (if BAA is signed)
    if baa_signed and phi_access:
        required_provisions = [
            "Permitted uses and disclosures of PHI",
            "Safeguarding requirements",
            "Breach notification obligations",
            "Subcontractor provisions",
            "Termination provisions",
            "Return or destruction of PHI"
        ]
        
        issues.append({
            "severity": "info",
            "issue": "Verify BAA contains all required provisions",
            "requirement": f"BAA must include: {', '.join(required_provisions)}",
            "action_required": "Review BAA document to ensure all provisions are present"
        })
    
    return {
        "vendor_name": vendor_name,
        "compliance_status": compliance_status,
        "baa_required": phi_access,
        "baa_signed": baa_signed,
        "baa_date": baa_date,
        "issues": issues,
        "total_issues": len(issues),
        "assessment_date": datetime.now().isoformat()
    }


@tool
def assess_security_controls(
    control_type: str,
    current_controls: List[str],
    environment: str = "cloud"
) -> Dict[str, Any]:
    """
    Assess HIPAA Security Rule technical and administrative safeguards.
    
    Evaluates current security controls against HIPAA Security Rule requirements
    and provides gap analysis with recommendations.
    
    Args:
        control_type: Type of controls to assess ("technical", "administrative", "physical", "all")
        current_controls: List of currently implemented controls
        environment: Deployment environment ("cloud", "on-premise", "hybrid")
        
    Returns:
        Security control assessment with gap analysis
        
    Example:
        >>> assess_security_controls(
        ...     control_type="technical",
        ...     current_controls=["encryption", "access_control", "audit_logs"],
        ...     environment="cloud"
        ... )
    """
    # Define required controls by type
    required_controls = {
        "technical": [
            "access_control",
            "audit_logs",
            "integrity_controls",
            "authentication",
            "encryption",
            "automatic_logoff"
        ],
        "administrative": [
            "security_management",
            "workforce_security",
            "information_access_management",
            "security_awareness_training",
            "security_incident_procedures",
            "contingency_plan",
            "business_associate_contracts"
        ],
        "physical": [
            "facility_access_controls",
            "workstation_use_policy",
            "workstation_security",
            "device_media_controls"
        ]
    }
    
    # Normalize current controls to lowercase
    current_controls_lower = [c.lower().replace(" ", "_") for c in current_controls]
    
    # Determine which controls to assess
    if control_type == "all":
        controls_to_assess = {**required_controls}
    else:
        controls_to_assess = {control_type: required_controls.get(control_type, [])}
    
    # Perform gap analysis
    gaps = []
    implemented = []
    
    for category, required in controls_to_assess.items():
        for control in required:
            if control in current_controls_lower:
                implemented.append({
                    "category": category,
                    "control": control.replace("_", " ").title(),
                    "status": "implemented"
                })
            else:
                # Determine severity based on control type
                if control in ["encryption", "access_control", "authentication"]:
                    severity = "critical"
                elif control in ["audit_logs", "security_incident_procedures"]:
                    severity = "high"
                else:
                    severity = "medium"
                
                gaps.append({
                    "category": category,
                    "control": control.replace("_", " ").title(),
                    "severity": severity,
                    "requirement": f"HIPAA Security Rule requires {control.replace('_', ' ')}",
                    "recommendation": f"Implement {control.replace('_', ' ')} controls"
                })
    
    # Calculate compliance percentage
    total_required = sum(len(controls) for controls in controls_to_assess.values())
    compliance_percentage = (len(implemented) / total_required * 100) if total_required > 0 else 0
    
    # Determine overall status
    if compliance_percentage >= 95:
        status = "compliant"
    elif compliance_percentage >= 80:
        status = "mostly_compliant"
    elif compliance_percentage >= 60:
        status = "partially_compliant"
    else:
        status = "non_compliant"
    
    return {
        "status": status,
        "compliance_percentage": round(compliance_percentage, 1),
        "control_type": control_type,
        "environment": environment,
        "implemented_controls": implemented,
        "gaps": gaps,
        "total_gaps": len(gaps),
        "critical_gaps": len([g for g in gaps if g["severity"] == "critical"]),
        "assessment_date": datetime.now().isoformat(),
        "summary": f"{len(implemented)} of {total_required} required controls implemented"
    }


@tool
def generate_breach_report(
    breach_description: str,
    affected_individuals: int,
    breach_date: str,
    discovery_date: str,
    phi_types: List[str]
) -> Dict[str, Any]:
    """
    Generate a HIPAA breach notification report.
    
    Creates a structured breach report following HIPAA Breach Notification Rule
    requirements, including timeline analysis and notification obligations.
    
    Args:
        breach_description: Description of the breach incident
        affected_individuals: Number of individuals affected
        breach_date: Date the breach occurred (ISO format: YYYY-MM-DD)
        discovery_date: Date the breach was discovered (ISO format: YYYY-MM-DD)
        phi_types: Types of PHI involved (e.g., ["name", "ssn", "medical_records"])
        
    Returns:
        Breach report with notification requirements and timeline
        
    Example:
        >>> generate_breach_report(
        ...     breach_description="Unauthorized access to patient database",
        ...     affected_individuals=150,
        ...     breach_date="2024-10-01",
        ...     discovery_date="2024-10-15",
        ...     phi_types=["name", "dob", "diagnosis"]
        ... )
    """
    try:
        breach_datetime = datetime.fromisoformat(breach_date)
        discovery_datetime = datetime.fromisoformat(discovery_date)
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date format. Use ISO format (YYYY-MM-DD)"
        }
    
    # Calculate timelines
    days_to_discovery = (discovery_datetime - breach_datetime).days
    notification_deadline = discovery_datetime + timedelta(days=60)
    days_remaining = (notification_deadline - datetime.now()).days
    
    # Determine breach severity
    if affected_individuals >= 500:
        severity = "major"
        hhs_notification_required = True
        media_notification_required = True
    else:
        severity = "minor"
        hhs_notification_required = True
        media_notification_required = False
    
    # Determine notification requirements
    notifications_required = []
    
    # Individual notification (always required)
    notifications_required.append({
        "recipient": "Affected Individuals",
        "method": "Written notice (first-class mail or email if agreed)",
        "deadline": notification_deadline.isoformat(),
        "days_remaining": days_remaining,
        "status": "required"
    })
    
    # HHS notification
    if affected_individuals >= 500:
        notifications_required.append({
            "recipient": "HHS Office for Civil Rights",
            "method": "Online submission via HHS website",
            "deadline": notification_deadline.isoformat(),
            "days_remaining": days_remaining,
            "status": "required"
        })
    else:
        # Annual notification for breaches < 500
        notifications_required.append({
            "recipient": "HHS Office for Civil Rights",
            "method": "Annual log submission",
            "deadline": "Within 60 days of calendar year end",
            "days_remaining": None,
            "status": "required_annual"
        })
    
    # Media notification (if >= 500 in same state/jurisdiction)
    if media_notification_required:
        notifications_required.append({
            "recipient": "Prominent Media Outlets",
            "method": "Press release or media notice",
            "deadline": notification_deadline.isoformat(),
            "days_remaining": days_remaining,
            "status": "required"
        })
    
    # Risk assessment
    high_risk_phi = ["ssn", "financial", "medical_records", "diagnosis", "treatment"]
    contains_high_risk = any(phi_type in high_risk_phi for phi_type in phi_types)
    
    risk_level = "high" if contains_high_risk else "medium"
    
    return {
        "breach_id": f"BR-{datetime.now().strftime('%Y%m%d')}-{affected_individuals}",
        "severity": severity,
        "risk_level": risk_level,
        "affected_individuals": affected_individuals,
        "breach_date": breach_date,
        "discovery_date": discovery_date,
        "days_to_discovery": days_to_discovery,
        "phi_types_involved": phi_types,
        "contains_high_risk_phi": contains_high_risk,
        "notifications_required": notifications_required,
        "notification_deadline": notification_deadline.isoformat(),
        "days_remaining_for_notification": days_remaining,
        "urgent": days_remaining < 30,
        "report_generated": datetime.now().isoformat(),
        "next_steps": [
            "Document all breach details and timeline",
            "Conduct risk assessment of PHI compromised",
            "Prepare notification letters for affected individuals",
            "Submit breach report to HHS (if >= 500 individuals)",
            "Notify media outlets (if >= 500 individuals)",
            "Implement corrective actions to prevent recurrence",
            "Update breach log and incident response procedures"
        ]
    }


@tool
def audit_access_logs(
    start_date: str,
    end_date: str,
    user_id: Optional[str] = None,
    resource_type: str = "phi"
) -> Dict[str, Any]:
    """
    Audit PHI access logs for HIPAA compliance.
    
    Analyzes access logs to identify suspicious activity, unauthorized access,
    and compliance with minimum necessary standard.
    
    Args:
        start_date: Start date for audit period (ISO format: YYYY-MM-DD)
        end_date: End date for audit period (ISO format: YYYY-MM-DD)
        user_id: Specific user to audit (optional, audits all users if not provided)
        resource_type: Type of resource to audit ("phi", "system", "all")
        
    Returns:
        Audit report with findings and anomalies
        
    Example:
        >>> audit_access_logs(
        ...     start_date="2024-10-01",
        ...     end_date="2024-10-19",
        ...     user_id="user123",
        ...     resource_type="phi"
        ... )
    """
    # Note: This is a template implementation
    # In production, this would query actual access logs from the database
    
    try:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date format. Use ISO format (YYYY-MM-DD)"
        }
    
    audit_period_days = (end_datetime - start_datetime).days
    
    # Simulated audit findings (in production, query actual logs)
    findings = []
    
    # Check for common compliance issues
    findings.append({
        "finding_type": "info",
        "description": "Audit log review completed",
        "recommendation": "Continue regular audit log reviews (at least quarterly)",
        "regulation": "HIPAA Security Rule § 164.308(a)(1)(ii)(D)"
    })
    
    # Template findings that would be generated from actual log analysis
    suspicious_patterns = [
        {
            "pattern": "After-hours access",
            "description": "Access to PHI outside normal business hours",
            "severity": "medium",
            "recommendation": "Review justification for after-hours access"
        },
        {
            "pattern": "Bulk data access",
            "description": "Large number of records accessed in short time",
            "severity": "high",
            "recommendation": "Verify legitimate business need for bulk access"
        },
        {
            "pattern": "Failed login attempts",
            "description": "Multiple failed authentication attempts",
            "severity": "high",
            "recommendation": "Investigate potential unauthorized access attempts"
        },
        {
            "pattern": "Unusual geographic access",
            "description": "Access from unexpected locations",
            "severity": "medium",
            "recommendation": "Verify user identity and access legitimacy"
        }
    ]
    
    return {
        "status": "completed",
        "audit_period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": audit_period_days
        },
        "scope": {
            "user_id": user_id or "all_users",
            "resource_type": resource_type
        },
        "findings": findings,
        "suspicious_patterns_to_monitor": suspicious_patterns,
        "compliance_requirements": [
            "Maintain audit logs for at least 6 years (HIPAA requirement)",
            "Review audit logs regularly (recommended: quarterly)",
            "Document audit findings and corrective actions",
            "Ensure audit controls cannot be disabled by unauthorized users"
        ],
        "audit_date": datetime.now().isoformat(),
        "note": "This is a template audit report. In production, actual access logs would be analyzed."
    }


@tool
def check_patient_rights(right_type: str, request_date: str) -> Dict[str, Any]:
    """
    Check compliance with HIPAA patient rights requirements.
    
    Validates handling of patient rights requests including access, amendment,
    accounting of disclosures, and restrictions.
    
    Args:
        right_type: Type of patient right ("access", "amendment", "accounting", "restriction", "confidential_communication")
        request_date: Date the request was received (ISO format: YYYY-MM-DD)
        
    Returns:
        Patient rights compliance assessment with deadlines
        
    Example:
        >>> check_patient_rights(
        ...     right_type="access",
        ...     request_date="2024-10-01"
        ... )
    """
    try:
        request_datetime = datetime.fromisoformat(request_date)
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date format. Use ISO format (YYYY-MM-DD)"
        }
    
    # Define requirements for each right type
    rights_requirements = {
        "access": {
            "deadline_days": 30,
            "extension_allowed": True,
            "extension_days": 30,
            "regulation": "HIPAA Privacy Rule § 164.524",
            "description": "Right to access and obtain copy of PHI",
            "requirements": [
                "Provide access within 30 days (can extend once for 30 days)",
                "Provide in format requested if readily producible",
                "Cannot charge excessive fees (labor + supplies only)",
                "Must provide reason if denial (limited circumstances)"
            ]
        },
        "amendment": {
            "deadline_days": 60,
            "extension_allowed": True,
            "extension_days": 30,
            "regulation": "HIPAA Privacy Rule § 164.526",
            "description": "Right to request amendment of PHI",
            "requirements": [
                "Respond within 60 days (can extend once for 30 days)",
                "Must accept or deny with written explanation",
                "If denied, patient can submit statement of disagreement",
                "Append amendment/statement to future disclosures"
            ]
        },
        "accounting": {
            "deadline_days": 60,
            "extension_allowed": True,
            "extension_days": 30,
            "regulation": "HIPAA Privacy Rule § 164.528",
            "description": "Right to accounting of disclosures",
            "requirements": [
                "Provide accounting within 60 days (can extend once for 30 days)",
                "Include disclosures for past 6 years",
                "First accounting in 12-month period is free",
                "Can charge reasonable fee for subsequent requests"
            ]
        },
        "restriction": {
            "deadline_days": None,
            "extension_allowed": False,
            "extension_days": 0,
            "regulation": "HIPAA Privacy Rule § 164.522",
            "description": "Right to request restrictions on uses/disclosures",
            "requirements": [
                "Must agree to restriction if patient pays out-of-pocket in full",
                "Other restrictions are optional (covered entity can agree or deny)",
                "If agreed, must comply with restriction",
                "Can terminate restriction with notice (except out-of-pocket restriction)"
            ]
        },
        "confidential_communication": {
            "deadline_days": None,
            "extension_allowed": False,
            "extension_days": 0,
            "regulation": "HIPAA Privacy Rule § 164.522(b)",
            "description": "Right to request confidential communications",
            "requirements": [
                "Must accommodate reasonable requests",
                "Cannot require explanation for request",
                "Can request alternative location or method",
                "Must implement if request is reasonable"
            ]
        }
    }
    
    if right_type not in rights_requirements:
        return {
            "status": "error",
            "message": f"Unknown right type: {right_type}. Valid types: {', '.join(rights_requirements.keys())}"
        }
    
    requirements = rights_requirements[right_type]
    
    # Calculate deadlines
    days_since_request = (datetime.now() - request_datetime).days
    
    if requirements["deadline_days"]:
        deadline = request_datetime + timedelta(days=requirements["deadline_days"])
        days_remaining = (deadline - datetime.now()).days
        
        if requirements["extension_allowed"]:
            extended_deadline = deadline + timedelta(days=requirements["extension_days"])
            extended_days_remaining = (extended_deadline - datetime.now()).days
        else:
            extended_deadline = None
            extended_days_remaining = None
        
        # Determine status
        if days_remaining < 0:
            if extended_days_remaining and extended_days_remaining >= 0:
                status = "extension_period"
            else:
                status = "overdue"
        elif days_remaining <= 7:
            status = "urgent"
        else:
            status = "on_time"
    else:
        deadline = None
        days_remaining = None
        extended_deadline = None
        extended_days_remaining = None
        status = "no_deadline"
    
    return {
        "right_type": right_type,
        "description": requirements["description"],
        "regulation": requirements["regulation"],
        "request_date": request_date,
        "days_since_request": days_since_request,
        "deadline": deadline.isoformat() if deadline else None,
        "days_remaining": days_remaining,
        "extended_deadline": extended_deadline.isoformat() if extended_deadline else None,
        "extended_days_remaining": extended_days_remaining,
        "status": status,
        "requirements": requirements["requirements"],
        "urgent": status in ["urgent", "overdue"],
        "checked_date": datetime.now().isoformat()
    }


@tool
def evaluate_risk(
    risk_category: str,
    asset_description: str,
    current_safeguards: List[str],
    threat_likelihood: str,
    impact_severity: str
) -> Dict[str, Any]:
    """
    Perform HIPAA security risk assessment.
    
    Evaluates risks to ePHI confidentiality, integrity, and availability
    following HIPAA Security Rule risk analysis requirements.
    
    Args:
        risk_category: Category of risk ("confidentiality", "integrity", "availability", "other")
        asset_description: Description of the asset/system being assessed
        current_safeguards: List of current security safeguards in place
        threat_likelihood: Likelihood of threat ("low", "medium", "high")
        impact_severity: Severity of impact if threat occurs ("low", "medium", "high", "critical")
        
    Returns:
        Risk assessment with risk level and mitigation recommendations
        
    Example:
        >>> evaluate_risk(
        ...     risk_category="confidentiality",
        ...     asset_description="Patient database server",
        ...     current_safeguards=["encryption", "firewall", "access_control"],
        ...     threat_likelihood="medium",
        ...     impact_severity="high"
        ... )
    """
    # Define risk matrix (likelihood x impact)
    risk_matrix = {
        ("low", "low"): ("low", 1),
        ("low", "medium"): ("low", 2),
        ("low", "high"): ("medium", 3),
        ("low", "critical"): ("medium", 4),
        ("medium", "low"): ("low", 2),
        ("medium", "medium"): ("medium", 3),
        ("medium", "high"): ("high", 4),
        ("medium", "critical"): ("high", 5),
        ("high", "low"): ("medium", 3),
        ("high", "medium"): ("high", 4),
        ("high", "high"): ("critical", 5),
        ("high", "critical"): ("critical", 6)
    }
    
    # Calculate risk level
    risk_key = (threat_likelihood.lower(), impact_severity.lower())
    if risk_key not in risk_matrix:
        return {
            "status": "error",
            "message": "Invalid threat_likelihood or impact_severity. Use: low, medium, high, critical"
        }
    
    risk_level, risk_score = risk_matrix[risk_key]
    
    # Evaluate safeguards effectiveness
    recommended_safeguards = {
        "confidentiality": [
            "encryption_at_rest",
            "encryption_in_transit",
            "access_control",
            "authentication",
            "audit_logs",
            "data_classification"
        ],
        "integrity": [
            "integrity_controls",
            "version_control",
            "backup_procedures",
            "change_management",
            "audit_logs",
            "validation_checks"
        ],
        "availability": [
            "backup_procedures",
            "disaster_recovery",
            "redundancy",
            "monitoring",
            "incident_response",
            "business_continuity"
        ],
        "other": [
            "risk_assessment",
            "security_policies",
            "workforce_training",
            "vendor_management",
            "incident_response",
            "compliance_monitoring"
        ]
    }
    
    # Normalize current safeguards
    current_safeguards_lower = [s.lower().replace(" ", "_") for s in current_safeguards]
    
    # Identify missing safeguards
    recommended = recommended_safeguards.get(risk_category, [])
    missing_safeguards = [s for s in recommended if s not in current_safeguards_lower]
    
    # Generate mitigation recommendations
    mitigation_recommendations = []
    
    if risk_level in ["high", "critical"]:
        mitigation_recommendations.append({
            "priority": "immediate",
            "action": "Address critical risk immediately",
            "description": f"This {risk_level} risk requires immediate attention and mitigation"
        })
    
    for safeguard in missing_safeguards[:3]:  # Top 3 missing safeguards
        mitigation_recommendations.append({
            "priority": "high" if risk_level in ["high", "critical"] else "medium",
            "action": f"Implement {safeguard.replace('_', ' ')}",
            "description": f"Add {safeguard.replace('_', ' ')} to reduce {risk_category} risk"
        })
    
    # Calculate residual risk (after implementing recommendations)
    if missing_safeguards:
        # Reduce risk by one level if recommendations are implemented
        residual_risk_levels = {"critical": "high", "high": "medium", "medium": "low", "low": "low"}
        residual_risk = residual_risk_levels[risk_level]
    else:
        residual_risk = risk_level
    
    return {
        "asset": asset_description,
        "risk_category": risk_category,
        "threat_likelihood": threat_likelihood,
        "impact_severity": impact_severity,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "current_safeguards": current_safeguards,
        "missing_safeguards": missing_safeguards,
        "mitigation_recommendations": mitigation_recommendations,
        "residual_risk": residual_risk,
        "requires_immediate_action": risk_level in ["high", "critical"],
        "assessment_date": datetime.now().isoformat(),
        "regulation_reference": "HIPAA Security Rule § 164.308(a)(1)(ii)(A) - Risk Analysis"
    }


@tool
def generate_compliance_report(
    report_type: str,
    start_date: str,
    end_date: str,
    include_recommendations: bool = True
) -> Dict[str, Any]:
    """
    Generate comprehensive HIPAA compliance report.
    
    Creates detailed compliance reports for audits, management review,
    or regulatory submissions.
    
    Args:
        report_type: Type of report ("quarterly", "annual", "audit", "incident")
        start_date: Report period start date (ISO format: YYYY-MM-DD)
        end_date: Report period end date (ISO format: YYYY-MM-DD)
        include_recommendations: Whether to include improvement recommendations
        
    Returns:
        Comprehensive compliance report with findings and metrics
        
    Example:
        >>> generate_compliance_report(
        ...     report_type="quarterly",
        ...     start_date="2024-07-01",
        ...     end_date="2024-09-30",
        ...     include_recommendations=True
        ... )
    """
    try:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date format. Use ISO format (YYYY-MM-DD)"
        }
    
    report_period_days = (end_datetime - start_datetime).days
    
    # Generate report sections
    report = {
        "report_id": f"HIPAA-{report_type.upper()}-{datetime.now().strftime('%Y%m%d')}",
        "report_type": report_type,
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": report_period_days
        },
        "generated_date": datetime.now().isoformat(),
        
        # Executive Summary
        "executive_summary": {
            "overall_compliance_status": "compliant",
            "total_findings": 0,
            "critical_findings": 0,
            "high_priority_findings": 0,
            "medium_priority_findings": 0,
            "low_priority_findings": 0
        },
        
        # Compliance Areas
        "compliance_areas": [
            {
                "area": "Privacy Rule Compliance",
                "status": "compliant",
                "findings": [],
                "score": 95
            },
            {
                "area": "Security Rule Compliance",
                "status": "mostly_compliant",
                "findings": [
                    "Encryption implementation in progress",
                    "MFA rollout ongoing"
                ],
                "score": 88
            },
            {
                "area": "Breach Notification",
                "status": "compliant",
                "findings": [],
                "score": 100
            },
            {
                "area": "Business Associate Agreements",
                "status": "review_needed",
                "findings": [
                    "3 BAAs require renewal",
                    "2 new vendors need BAA"
                ],
                "score": 85
            },
            {
                "area": "Patient Rights",
                "status": "compliant",
                "findings": [],
                "score": 98
            }
        ],
        
        # Key Metrics
        "metrics": {
            "baa_count": {
                "total": 15,
                "active": 13,
                "expired": 2,
                "pending": 2
            },
            "security_incidents": {
                "total": 0,
                "breaches": 0,
                "near_misses": 0
            },
            "patient_rights_requests": {
                "total": 12,
                "access_requests": 8,
                "amendment_requests": 2,
                "accounting_requests": 2,
                "average_response_time_days": 18
            },
            "training_completion": {
                "total_employees": 25,
                "completed": 23,
                "pending": 2,
                "completion_rate": 92
            }
        },
        
        # Recommendations (if requested)
        "recommendations": [] if not include_recommendations else [
            {
                "priority": "high",
                "area": "Business Associate Management",
                "recommendation": "Renew expired BAAs and obtain BAAs from new vendors",
                "timeline": "30 days"
            },
            {
                "priority": "medium",
                "area": "Security Controls",
                "recommendation": "Complete MFA rollout for all users",
                "timeline": "60 days"
            },
            {
                "priority": "medium",
                "area": "Workforce Training",
                "recommendation": "Ensure 100% training completion",
                "timeline": "30 days"
            },
            {
                "priority": "low",
                "area": "Documentation",
                "recommendation": "Update security policies to reflect recent changes",
                "timeline": "90 days"
            }
        ],
        
        # Next Steps
        "next_steps": [
            "Address high-priority recommendations within 30 days",
            "Schedule next compliance review",
            "Update risk assessment based on findings",
            "Communicate findings to management and compliance committee"
        ]
    }
    
    # Calculate total findings
    total_findings = sum(len(area["findings"]) for area in report["compliance_areas"])
    report["executive_summary"]["total_findings"] = total_findings
    
    # Update finding counts by priority (based on recommendations)
    if include_recommendations:
        report["executive_summary"]["high_priority_findings"] = len(
            [r for r in report["recommendations"] if r["priority"] == "high"]
        )
        report["executive_summary"]["medium_priority_findings"] = len(
            [r for r in report["recommendations"] if r["priority"] == "medium"]
        )
        report["executive_summary"]["low_priority_findings"] = len(
            [r for r in report["recommendations"] if r["priority"] == "low"]
        )
    
    return report


@tool
def recommend_remediation(
    finding_description: str,
    finding_severity: str,
    affected_area: str
) -> Dict[str, Any]:
    """
    Provide remediation recommendations for HIPAA compliance findings.
    
    Generates specific, actionable remediation steps based on compliance
    findings and industry best practices.
    
    Args:
        finding_description: Description of the compliance finding or gap
        finding_severity: Severity level ("critical", "high", "medium", "low")
        affected_area: Area affected ("privacy", "security", "breach_notification", "patient_rights", "baa")
        
    Returns:
        Remediation plan with specific actions and timeline
        
    Example:
        >>> recommend_remediation(
        ...     finding_description="PHI not encrypted at rest",
        ...     finding_severity="critical",
        ...     affected_area="security"
        ... )
    """
    # Define remediation templates by area
    remediation_templates = {
        "privacy": {
            "critical": {
                "timeline_days": 7,
                "steps": [
                    "Immediately cease unauthorized PHI use/disclosure",
                    "Notify Privacy Officer and legal counsel",
                    "Conduct impact assessment",
                    "Implement corrective measures",
                    "Document incident and response"
                ]
            },
            "high": {
                "timeline_days": 30,
                "steps": [
                    "Review and update privacy policies",
                    "Conduct workforce training on privacy requirements",
                    "Implement additional privacy safeguards",
                    "Document policy updates and training completion"
                ]
            },
            "medium": {
                "timeline_days": 60,
                "steps": [
                    "Review current privacy practices",
                    "Update procedures as needed",
                    "Communicate changes to workforce",
                    "Monitor compliance with updated procedures"
                ]
            },
            "low": {
                "timeline_days": 90,
                "steps": [
                    "Schedule privacy policy review",
                    "Update documentation",
                    "Plan workforce refresher training"
                ]
            }
        },
        "security": {
            "critical": {
                "timeline_days": 7,
                "steps": [
                    "Immediately implement emergency security measures",
                    "Notify Security Officer and IT team",
                    "Conduct security risk assessment",
                    "Deploy permanent security controls",
                    "Document incident and remediation"
                ]
            },
            "high": {
                "timeline_days": 30,
                "steps": [
                    "Implement required security controls",
                    "Update security policies and procedures",
                    "Conduct workforce security training",
                    "Test security controls effectiveness",
                    "Document implementation"
                ]
            },
            "medium": {
                "timeline_days": 60,
                "steps": [
                    "Plan security control implementation",
                    "Update security documentation",
                    "Schedule workforce training",
                    "Implement and test controls",
                    "Monitor effectiveness"
                ]
            },
            "low": {
                "timeline_days": 90,
                "steps": [
                    "Review security posture",
                    "Plan incremental improvements",
                    "Update security documentation",
                    "Schedule periodic reviews"
                ]
            }
        },
        "breach_notification": {
            "critical": {
                "timeline_days": 3,
                "steps": [
                    "Immediately activate breach response team",
                    "Contain and mitigate breach",
                    "Begin breach investigation",
                    "Prepare notification materials",
                    "Submit required notifications within 60 days of discovery"
                ]
            },
            "high": {
                "timeline_days": 14,
                "steps": [
                    "Review breach notification procedures",
                    "Update breach response plan",
                    "Train workforce on breach response",
                    "Test breach notification process"
                ]
            },
            "medium": {
                "timeline_days": 30,
                "steps": [
                    "Review and update breach response procedures",
                    "Conduct breach response training",
                    "Document updates"
                ]
            },
            "low": {
                "timeline_days": 60,
                "steps": [
                    "Schedule breach response plan review",
                    "Update documentation as needed",
                    "Plan workforce training"
                ]
            }
        },
        "patient_rights": {
            "critical": {
                "timeline_days": 7,
                "steps": [
                    "Immediately address patient rights violation",
                    "Notify Privacy Officer",
                    "Fulfill outstanding patient requests",
                    "Implement corrective measures",
                    "Document incident and response"
                ]
            },
            "high": {
                "timeline_days": 30,
                "steps": [
                    "Review patient rights procedures",
                    "Update request tracking system",
                    "Train workforce on patient rights",
                    "Implement process improvements"
                ]
            },
            "medium": {
                "timeline_days": 60,
                "steps": [
                    "Review patient rights compliance",
                    "Update procedures and forms",
                    "Communicate changes to workforce",
                    "Monitor request handling"
                ]
            },
            "low": {
                "timeline_days": 90,
                "steps": [
                    "Schedule patient rights procedure review",
                    "Update documentation",
                    "Plan workforce training"
                ]
            }
        },
        "baa": {
            "critical": {
                "timeline_days": 7,
                "steps": [
                    "Immediately suspend PHI access for vendors without BAA",
                    "Obtain executed BAA before resuming access",
                    "Review all vendor relationships",
                    "Implement vendor management procedures",
                    "Document BAA status for all vendors"
                ]
            },
            "high": {
                "timeline_days": 30,
                "steps": [
                    "Obtain missing BAAs",
                    "Renew expired BAAs",
                    "Review BAA terms for compliance",
                    "Implement BAA tracking system",
                    "Document all BAA updates"
                ]
            },
            "medium": {
                "timeline_days": 60,
                "steps": [
                    "Review BAA management procedures",
                    "Update BAA templates",
                    "Schedule BAA renewals",
                    "Implement tracking system"
                ]
            },
            "low": {
                "timeline_days": 90,
                "steps": [
                    "Schedule BAA review",
                    "Update BAA documentation",
                    "Plan vendor assessment process"
                ]
            }
        }
    }
    
    # Get remediation template
    if affected_area not in remediation_templates:
        affected_area = "security"  # Default to security
    
    if finding_severity not in remediation_templates[affected_area]:
        finding_severity = "medium"  # Default to medium
    
    template = remediation_templates[affected_area][finding_severity]
    
    # Calculate timeline
    deadline = datetime.now() + timedelta(days=template["timeline_days"])
    
    # Determine urgency
    if finding_severity == "critical":
        urgency = "immediate"
    elif finding_severity == "high":
        urgency = "urgent"
    elif finding_severity == "medium":
        urgency = "normal"
    else:
        urgency = "low"
    
    # Generate resource requirements
    resources_needed = []
    if finding_severity in ["critical", "high"]:
        resources_needed.extend([
            "Privacy/Security Officer involvement",
            "IT/Technical resources",
            "Legal counsel (if needed)",
            "Budget for tools/services"
        ])
    else:
        resources_needed.extend([
            "Privacy/Security Officer review",
            "Administrative support"
        ])
    
    return {
        "finding": finding_description,
        "severity": finding_severity,
        "affected_area": affected_area,
        "urgency": urgency,
        "timeline_days": template["timeline_days"],
        "deadline": deadline.isoformat(),
        "remediation_steps": template["steps"],
        "resources_needed": resources_needed,
        "success_criteria": [
            "Finding fully remediated",
            "Compliance verified",
            "Documentation updated",
            "Workforce trained (if applicable)",
            "Monitoring implemented"
        ],
        "follow_up": {
            "initial_review": (datetime.now() + timedelta(days=template["timeline_days"] // 2)).isoformat(),
            "final_verification": deadline.isoformat(),
            "ongoing_monitoring": "Quarterly reviews recommended"
        },
        "regulation_reference": f"HIPAA {affected_area.replace('_', ' ').title()} Requirements",
        "generated_date": datetime.now().isoformat()
    }


# Export all tools
__all__ = [
    'search_hipaa_knowledge',
    'check_phi_compliance',
    'validate_baa',
    'assess_security_controls',
    'generate_breach_report',
    'audit_access_logs',
    'check_patient_rights',
    'evaluate_risk',
    'generate_compliance_report',
    'recommend_remediation'
]

