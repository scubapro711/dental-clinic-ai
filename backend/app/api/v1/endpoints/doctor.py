"""
Doctor Escalation API Endpoint

Handles doctor escalation, chat links, and notifications.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request
from app.middleware.rate_limiter import limiter, get_rate_limit
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import secrets

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# In-memory storage for escalations (in production, use Redis)
escalations_store: Dict[str, Dict[str, Any]] = {}


class EscalationRequest(BaseModel):
    """Request model for creating doctor escalation."""
    patient_name: str
    patient_id: str
    conversation_id: str
    urgency_level: str  # EMERGENCY, DOCTOR_REQUIRED, ROUTINE
    issue_summary: str
    conversation_history: list


class DoctorResponse(BaseModel):
    """Request model for doctor response."""
    escalation_token: str
    message: str
    doctor_name: str


@router.post("/create-escalation")
@limiter.limit(get_rate_limit("default"))
async def create_escalation(request: Request, escalation_data: EscalationRequest) -> Dict[str, Any]:
    """
    Create a doctor escalation and generate access link.
    
    Args:
        request: Escalation request details
        
    Returns:
        Escalation details with doctor access link
    """
    try:
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Create JWT token with expiration
        jwt_payload = {
            "escalation_id": token,
            "patient_id": escalation_data.patient_id,
            "conversation_id": escalation_data.conversation_id,
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        
        jwt_token = jwt.encode(jwt_payload, settings.SECRET_KEY, algorithm="HS256")
        
        # Store escalation details
        escalation_record = {
            "token": token,
            "jwt_token": jwt_token,
            "patient_name": escalation_data.patient_name,
            "patient_id": escalation_data.patient_id,
            "conversation_id": escalation_data.conversation_id,
            "urgency_level": escalation_data.urgency_level,
            "issue_summary": escalation_data.issue_summary,
            "conversation_history": escalation_data.conversation_history,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "status": "pending",  # pending, active, resolved
            "doctor_name": None,
            "doctor_messages": [],
        }
        
        escalations_store[token] = escalation_record
        
        # Generate doctor access link
        doctor_link = f"/api/v1/doctor/chat/{jwt_token}"
        
        logger.info(f"Created escalation for patient {escalation_data.patient_name} with urgency {escalation_data.urgency_level}")
        
        return {
            "escalation_id": token,
            "doctor_link": doctor_link,
            "jwt_token": jwt_token,
            "urgency_level": escalation_data.urgency_level,
            "expires_at": escalation_record["expires_at"],
            "status": "created",
        }
    
    except Exception as e:
        logger.error(f"Error creating escalation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{jwt_token}", response_class=HTMLResponse)
@limiter.limit(get_rate_limit("default"))
async def doctor_chat_page(request: Request, jwt_token: str):
    """
    Render doctor chat page.
    
    Args:
        request: FastAPI request
        jwt_token: JWT token for authentication
        
    Returns:
        HTML page for doctor chat
    """
    try:
        # Verify JWT token
        payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        escalation_id = payload["escalation_id"]
        
        # Get escalation data
        escalation = escalations_store.get(escalation_id)
        
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        # Check if expired
        expires_at = datetime.fromisoformat(escalation["expires_at"])
        if datetime.now() > expires_at:
            raise HTTPException(status_code=403, detail="Escalation link has expired")
        
        # Mark as active
        if escalation["status"] == "pending":
            escalation["status"] = "active"
        
        # Create response with security headers
        response = templates.TemplateResponse("doctor_chat.html", {
            "request": request,
            "escalation": escalation,
            "jwt_token": jwt_token,
        })
        
        # Add Content Security Policy to prevent XSS
        # Note: We use 'unsafe-inline' for styles only (template has inline CSS)
        # Scripts are now safe (no innerHTML with user data)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self' data:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        return response
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error loading doctor chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/escalation/{escalation_id}")
@limiter.limit(get_rate_limit("default"))
async def get_escalation(request: Request, escalation_id: str) -> Dict[str, Any]:
    """
    Get escalation details.
    
    Args:
        escalation_id: Escalation ID
        
    Returns:
        Escalation details
    """
    escalation = escalations_store.get(escalation_id)
    
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    return escalation


@router.post("/respond")
@limiter.limit(get_rate_limit("default"))
async def doctor_respond(request: Request, response: DoctorResponse) -> Dict[str, Any]:
    """
    Record doctor response to escalation.
    
    Args:
        response: Doctor response details
        
    Returns:
        Success response
    """
    try:
        # Verify JWT token
        payload = jwt.decode(response.escalation_token, settings.SECRET_KEY, algorithms=["HS256"])
        escalation_id = payload["escalation_id"]
        
        # Get escalation
        escalation = escalations_store.get(escalation_id)
        
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        # Add doctor message
        doctor_message = {
            "doctor_name": response.doctor_name,
            "message": response.message,
            "timestamp": datetime.now().isoformat(),
        }
        
        escalation["doctor_messages"].append(doctor_message)
        escalation["doctor_name"] = response.doctor_name
        escalation["status"] = "active"
        
        logger.info(f"Doctor {response.doctor_name} responded to escalation {escalation_id}")
        
        return {
            "status": "success",
            "message": "Response recorded",
            "escalation_id": escalation_id,
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error recording doctor response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve/{escalation_id}")
@limiter.limit(get_rate_limit("default"))
async def resolve_escalation(request: Request, escalation_id: str) -> Dict[str, Any]:
    """
    Mark escalation as resolved.
    
    Args:
        escalation_id: Escalation ID
        
    Returns:
        Success response
    """
    escalation = escalations_store.get(escalation_id)
    
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    escalation["status"] = "resolved"
    escalation["resolved_at"] = datetime.now().isoformat()
    
    logger.info(f"Escalation {escalation_id} marked as resolved")
    
    return {
        "status": "success",
        "escalation_id": escalation_id,
        "resolved_at": escalation["resolved_at"],
    }


@router.get("/active-escalations")
@limiter.limit(get_rate_limit("default"))
async def get_active_escalations(request: Request) -> Dict[str, Any]:
    """
    Get all active escalations.
    
    Returns:
        List of active escalations
    """
    active = [
        {
            "escalation_id": esc_id,
            "patient_name": esc["patient_name"],
            "urgency_level": esc["urgency_level"],
            "issue_summary": esc["issue_summary"],
            "created_at": esc["created_at"],
            "status": esc["status"],
            "doctor_name": esc.get("doctor_name"),
        }
        for esc_id, esc in escalations_store.items()
        if esc["status"] in ["pending", "active"]
    ]
    
    # Sort by urgency (EMERGENCY first)
    urgency_order = {"EMERGENCY": 0, "DOCTOR_REQUIRED": 1, "ROUTINE": 2}
    active.sort(key=lambda x: urgency_order.get(x["urgency_level"], 3))
    
    return {
        "active_escalations": active,
        "count": len(active),
    }


@router.post("/notify-doctor")
@limiter.limit(get_rate_limit("default"))
async def notify_doctor(request: Request, escalation_id: str, doctor_email: str, doctor_phone: Optional[str] = None) -> Dict[str, Any]:
    """
    Send notification to doctor about escalation.
    
    Args:
        escalation_id: Escalation ID
        doctor_email: Doctor's email address
        doctor_phone: Doctor's phone number (optional, for SMS)
        
    Returns:
        Notification status
    """
    escalation = escalations_store.get(escalation_id)
    
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    # TODO: Implement actual email/SMS sending
    # For MVP, we'll just log the notification
    
    notification_message = f"""
🚨 DENTAL CLINIC ESCALATION

Patient: {escalation['patient_name']}
Urgency: {escalation['urgency_level']}
Issue: {escalation['issue_summary']}

Access chat: /api/v1/doctor/chat/{escalation['jwt_token']}

This link expires in 24 hours.
"""
    
    logger.info(f"Notification sent to doctor: {doctor_email}")
    logger.info(notification_message)
    
    return {
        "status": "sent",
        "email": doctor_email,
        "phone": doctor_phone,
        "escalation_id": escalation_id,
    }
