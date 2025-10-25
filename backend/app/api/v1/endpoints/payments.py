"""
Payment endpoints using Stripe MCP server
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import subprocess
import json

from app.api.dependencies import get_current_membership
from app.models.organization_membership import OrganizationMembership

router = APIRouter()


class PaymentIntentRequest(BaseModel):
    amount: int  # in cents
    currency: str = "usd"
    description: Optional[str] = None
    customer_id: Optional[str] = None


class CreateCustomerRequest(BaseModel):
    email: str
    name: str
    phone: Optional[str] = None


class CreateInvoiceRequest(BaseModel):
    customer_id: str
    description: str
    amount: int  # in cents
    currency: str = "usd"


def call_stripe_mcp(tool_name: str, input_data: dict) -> dict:
    """Call Stripe MCP tool"""
    try:
        cmd = [
            "manus-mcp-cli",
            "tool",
            "call",
            tool_name,
            "--server",
            "stripe",
            "--input",
            json.dumps(input_data)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Stripe MCP error: {result.stderr}")
        
        # Parse output
        output = result.stdout.strip()
        if output:
            return json.loads(output)
        return {}
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Stripe request timeout")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid Stripe response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-customer")
async def create_customer(
    request: CreateCustomerRequest,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Create a Stripe customer"""
    input_data = {
        "email": request.email,
        "name": request.name,
    }
    if request.phone:
        input_data["phone"] = request.phone
    
    result = call_stripe_mcp("create_customer", input_data)
    return result


@router.get("/customers")
async def list_customers(
    limit: int = 10,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """List Stripe customers"""
    result = call_stripe_mcp("list_customers", {"limit": limit})
    return result


@router.post("/create-payment-link")
async def create_payment_link(
    request: PaymentIntentRequest,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Create a Stripe payment link"""
    # First create a price
    price_data = {
        "unit_amount": request.amount,
        "currency": request.currency,
        "product_data": {
            "name": request.description or "Dental Service Payment"
        }
    }
    
    # Create payment link
    link_data = {
        "line_items": [{
            "price_data": price_data,
            "quantity": 1
        }]
    }
    
    result = call_stripe_mcp("create_payment_link", link_data)
    return result


@router.post("/create-invoice")
async def create_invoice(
    request: CreateInvoiceRequest,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Create a Stripe invoice"""
    # First create invoice item
    item_data = {
        "customer": request.customer_id,
        "amount": request.amount,
        "currency": request.currency,
        "description": request.description
    }
    
    item_result = call_stripe_mcp("create_invoice_item", item_data)
    
    # Then create invoice
    invoice_data = {
        "customer": request.customer_id,
        "auto_advance": True
    }
    
    invoice_result = call_stripe_mcp("create_invoice", invoice_data)
    
    # Finalize invoice
    if invoice_result.get("id"):
        finalize_data = {"invoice_id": invoice_result["id"]}
        finalize_result = call_stripe_mcp("finalize_invoice", finalize_data)
        return finalize_result
    
    return invoice_result


@router.get("/invoices")
async def list_invoices(
    customer_id: Optional[str] = None,
    limit: int = 10,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """List Stripe invoices"""
    input_data = {"limit": limit}
    if customer_id:
        input_data["customer"] = customer_id
    
    result = call_stripe_mcp("list_invoices", input_data)
    return result


@router.get("/balance")
async def get_balance(
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Get Stripe account balance"""
    result = call_stripe_mcp("retrieve_balance", {})
    return result


@router.post("/refund")
async def create_refund(
    payment_intent_id: str,
    amount: Optional[int] = None,
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Create a refund"""
    input_data = {"payment_intent": payment_intent_id}
    if amount:
        input_data["amount"] = amount
    
    result = call_stripe_mcp("create_refund", input_data)
    return result


@router.get("/account")
async def get_account_info(
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """Get Stripe account info"""
    result = call_stripe_mcp("get_stripe_account_info", {})
    return result

