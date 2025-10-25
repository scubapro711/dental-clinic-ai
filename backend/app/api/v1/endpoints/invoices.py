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
from app.api.dependencies import get_current_membership
from app.models.organization_membership import OrganizationMembership

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


@router.get("/invoices")
async def list_invoices(
    page: int = 1,
    page_size: int = 25,
    doc_type: Optional[int] = None,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    List invoices for current patient
    
    Query params:
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        doc_type: Filter by document type (320=invoice, 400=receipt)
    """
    organization_id = str(membership.organization_id)
    
    # Get clinic's Green Invoice API key
    api_key = get_clinic_green_invoice_key(organization_id)
    
    if not api_key:
        # Return mock data if Green Invoice not configured
        return {
            "items": [
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
            ],
            "total": 2,
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
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list invoices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch invoices")


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Get invoice by ID"""
    organization_id = str(membership.organization_id)
    
    # Get clinic's Green Invoice API key
    api_key = get_clinic_green_invoice_key(organization_id)
    
    if not api_key:
        # Return mock data
        return {
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
    
    # Use Green Invoice API
    try:
        sandbox = is_sandbox_mode(organization_id)
        client = GreenInvoiceAPI(api_key, sandbox=sandbox)
        
        result = client.get_document(invoice_id)
        return result
        
    except Exception as e:
        logger.error(f"Failed to get invoice {invoice_id}: {e}")
        raise HTTPException(status_code=404, detail="Invoice not found")


@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Download invoice PDF"""
    organization_id = str(membership.organization_id)
    
    # Get clinic's Green Invoice API key
    api_key = get_clinic_green_invoice_key(organization_id)
    
    if not api_key:
        raise HTTPException(status_code=404, detail="PDF not available")
    
    # Use Green Invoice API
    try:
        sandbox = is_sandbox_mode(organization_id)
        client = GreenInvoiceAPI(api_key, sandbox=sandbox)
        
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
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Create a new invoice
    
    This is typically called automatically after an appointment,
    but can also be used manually.
    """
    organization_id = str(membership.organization_id)
    
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
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Get invoice statistics for current patient"""
    organization_id = str(membership.organization_id)
    # TODO: Calculate real stats from Green Invoice
    
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

