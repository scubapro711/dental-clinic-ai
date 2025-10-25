"""
Invoices endpoints for Patient Portal
Uses Green Invoice API
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from app.integrations.green_invoice import GreenInvoiceAPI, create_invoice_from_appointment
from app.api.dependencies import get_current_membership, get_db
from app.models.organization_membership import OrganizationMembership
from app.models.user_patient_mapping import UserPatientMapping
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)


class InvoiceItem(BaseModel):
    description: str
    quantity: int = 1
    price: float
    currency: str = "ILS"


class CreateInvoiceRequest(BaseModel):
    patient_name: str
    patient_email: str
    patient_phone: Optional[str] = None
    items: List[InvoiceItem]
    notes: Optional[str] = None
    lang: str = "he"
    currency: str = "ILS"


# Mock function - replace with real database query
def get_clinic_green_invoice_key(organization_id: str) -> Optional[str]:
    """Get clinic's Green Invoice API key from database"""
    # TODO: Implement database query
    # For now, return None (not configured)
    return None


# Mock function - replace with real database query
def is_sandbox_mode(organization_id: str) -> bool:
    """Check if clinic is using sandbox mode"""
    # TODO: Implement database query
    return True  # Default to sandbox for testing


def get_patient_name_from_user(user_id, db: Session) -> Optional[str]:
    """
    Get patient name from user ID via UserPatientMapping
    
    Returns patient's full_name for matching with invoice client_name
    
    NOTE: This is a temporary solution. Ideally, we should:
    1. Store invoice_id -> patient_id mapping in database
    2. Use Odoo patient ID for filtering
    3. Not rely on name matching (can have duplicates)
    """
    mapping = db.query(UserPatientMapping).filter(
        UserPatientMapping.user_id == user_id,
        UserPatientMapping.is_active == True
    ).first()
    
    if not mapping:
        logger.warning(f"No patient mapping found for user {user_id}")
        return None
    
    return mapping.full_name


@router.get("/invoices")
async def list_invoices(
    page: int = 1,
    page_size: int = 25,
    doc_type: Optional[int] = None,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    """
    List invoices for current patient
    
    Query params:
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        doc_type: Filter by document type (320=invoice, 400=receipt)
    """
    organization_id = str(membership.organization_id)
    
    # Get current patient name for filtering
    patient_name = get_patient_name_from_user(membership.user_id, db)
    if not patient_name:
        # User has no patient mapping - return empty list
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size
        }
    
    # Get clinic's Green Invoice API key
    api_key = get_clinic_green_invoice_key(organization_id)
    
    if not api_key:
        # Return mock data if Green Invoice not configured
        # Filter by patient name
        all_items = [
                {
                    "id": "INV-001",
                    "type": 320,
                    "number": "2025001",
                    "date": "2025-10-01",
                    "client_name": "ישראל ישראלי",
                    "amount": 300.0,
                    "currency": "ILS",
                    "status": "paid",
                    "pdf_url": None
                },
                {
                    "id": "INV-002",
                    "type": 320,
                    "number": "2025002",
                    "date": "2025-09-15",
                    "client_name": "ישראל ישראלי",
                    "amount": 450.0,
                    "currency": "ILS",
                    "status": "unpaid",
                    "pdf_url": None
                }
            ]
        
        # Filter by patient name
        filtered_items = [
            item for item in all_items
            if item.get("client_name") == patient_name
        ]
        
        return {
            "items": filtered_items,
            "total": len(filtered_items),
            "page": page,
            "page_size": page_size
        }
    
    # Use Green Invoice API
    try:
        sandbox = is_sandbox_mode(organization_id)
        client = GreenInvoiceAPI(api_key, sandbox=sandbox)
        
        result = client.list_documents(
            doc_type=doc_type,
            page=page,
            page_size=min(page_size, 100)
        )
        
        # Filter by patient name
        if "items" in result:
            filtered_items = [
                item for item in result["items"]
                if item.get("client_name") == patient_name
            ]
            result["items"] = filtered_items
            result["total"] = len(filtered_items)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list invoices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch invoices")


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    """Get invoice by ID"""
    organization_id = str(membership.organization_id)
    
    # Get current patient name for ownership verification
    patient_name = get_patient_name_from_user(membership.user_id, db)
    if not patient_name:
        raise HTTPException(status_code=403, detail="Patient not found")
    
    # Get clinic's Green Invoice API key
    api_key = get_clinic_green_invoice_key(organization_id)
    
    if not api_key:
        # Return mock data
        mock_invoice = {
            "id": invoice_id,
            "type": 320,
            "number": "2025001",
            "date": "2025-10-01",
            "client": {
                "name": "ישראל ישראלי",
                "email": "patient@example.com",
                "phone": "050-1234567"
            },
            "items": [
                {
                    "description": "ניקוי שיניים",
                    "quantity": 1,
                    "price": 300.0,
                    "vat": 51.0,
                    "total": 351.0
                }
            ],
            "subtotal": 300.0,
            "vat": 51.0,
            "total": 351.0,
            "currency": "ILS",
            "status": "paid",
            "pdf_url": None
        }
        
        # Verify ownership
        if mock_invoice.get("client", {}).get("name") != patient_name:
            raise HTTPException(status_code=403, detail="Access denied: You don't have permission to view this invoice")
        
        return mock_invoice
    
    # Use Green Invoice API
    try:
        sandbox = is_sandbox_mode(organization_id)
        client = GreenInvoiceAPI(api_key, sandbox=sandbox)
        
        result = client.get_document(invoice_id)
        
        # Verify ownership
        client_name = result.get("client", {}).get("name") if isinstance(result.get("client"), dict) else result.get("client_name")
        if client_name != patient_name:
            raise HTTPException(status_code=403, detail="Access denied: You don't have permission to view this invoice")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get invoice {invoice_id}: {e}")
        raise HTTPException(status_code=404, detail="Invoice not found")


@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    """Download invoice PDF"""
    organization_id = str(membership.organization_id)
    
    # Get current patient name for ownership verification
    patient_name = get_patient_name_from_user(membership.user_id, db)
    if not patient_name:
        raise HTTPException(status_code=403, detail="Patient not found")
    
    # Get clinic's Green Invoice API key
    api_key = get_clinic_green_invoice_key(organization_id)
    
    if not api_key:
        raise HTTPException(status_code=404, detail="PDF not available")
    
    # Use Green Invoice API
    try:
        sandbox = is_sandbox_mode(organization_id)
        client = GreenInvoiceAPI(api_key, sandbox=sandbox)
        
        # First, verify ownership by getting the invoice
        invoice = client.get_document(invoice_id)
        client_name = invoice.get("client", {}).get("name") if isinstance(invoice.get("client"), dict) else invoice.get("client_name")
        if client_name != patient_name:
            raise HTTPException(status_code=403, detail="Access denied: You don't have permission to download this invoice")
        
        # Now download the PDF
        pdf_content = client.get_document_pdf(invoice_id)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to download PDF for invoice {invoice_id}: {e}")
        raise HTTPException(status_code=404, detail="PDF not found")


@router.post("/invoices")
async def create_invoice(
    request: CreateInvoiceRequest,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    """
    Create a new invoice
    
    This is typically called automatically after an appointment,
    but can also be used manually.
    
    NOTE: Patients can only create invoices for themselves.
    """
    organization_id = str(membership.organization_id)
    
    # Get current patient name for validation
    patient_name = get_patient_name_from_user(membership.user_id, db)
    if not patient_name:
        raise HTTPException(status_code=403, detail="Patient not found")
    
    # Verify that the invoice is for the current patient
    if request.patient_name != patient_name:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only create invoices for yourself"
        )
    
    # Get clinic's Green Invoice API key
    api_key = get_clinic_green_invoice_key(organization_id)
    
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Green Invoice not configured for this clinic"
        )
    
    # Use Green Invoice API
    try:
        sandbox = is_sandbox_mode(organization_id)
        client = GreenInvoiceAPI(api_key, sandbox=sandbox)
        
        # Convert items to Green Invoice format
        items = [
            {
                "description": item.description,
                "quantity": item.quantity,
                "price": item.price,
                "currency": item.currency,
                "vatType": GreenInvoiceAPI.VAT_REGULAR
            }
            for item in request.items
        ]
        
        result = client.create_invoice(
            client_name=request.patient_name,
            client_email=request.patient_email,
            items=items,
            client_phone=request.patient_phone,
            notes=request.notes,
            lang=request.lang,
            currency=request.currency
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        raise HTTPException(status_code=500, detail="Failed to create invoice")


@router.get("/invoices/stats/summary")
async def get_invoice_summary(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    """Get invoice statistics for current patient"""
    organization_id = str(membership.organization_id)
    
    # Get current patient name for filtering
    patient_name = get_patient_name_from_user(membership.user_id, db)
    if not patient_name:
        # User has no patient mapping - return empty stats
        return {
            "total_invoices": 0,
            "paid": 0,
            "unpaid": 0,
            "overdue": 0,
            "total_amount": 0.0,
            "paid_amount": 0.0,
            "unpaid_amount": 0.0,
            "currency": "ILS"
        }
    
    # TODO: Calculate real stats from Green Invoice for this specific patient
    # For now, return mock data (would need to filter by patient_name)
    
    return {
        "total_invoices": 12,
        "paid": 10,
        "unpaid": 2,
        "overdue": 0,
        "total_amount": 3600.0,
        "paid_amount": 3000.0,
        "unpaid_amount": 600.0,
        "currency": "ILS"
    }

