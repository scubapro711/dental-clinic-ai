"""
Diagnostics Endpoint - System Health Check
This endpoint provides diagnostic information about Odoo connection and data availability.
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.integrations.odoo_client import OdooClient

logger = logging.getLogger(__name__)

router = APIRouter()


class OdooModelCheck(BaseModel):
    """Model check result."""
    model: str
    description: str
    record_count: int
    status: str
    sample_records: List[Dict[str, Any]] = []
    error: str | None = None


class DiagnosticsResponse(BaseModel):
    """Diagnostics response model."""
    odoo_connection: Dict[str, Any]
    models_checked: List[OdooModelCheck]
    summary: Dict[str, Any]


@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """
    Simple health check endpoint.
    
    Returns:
        Status message
    """
    return {"status": "ok", "message": "Backend is running"}


@router.get("/odoo-check", response_model=DiagnosticsResponse)
async def check_odoo_data():
    """
    Check Odoo connection and data availability.
    
    This endpoint verifies:
    1. Odoo connection is working
    2. What data exists in Odoo
    3. Sample records from each model
    
    Returns:
        Comprehensive diagnostics report
    """
    try:
        # Initialize Odoo client
        odoo = OdooClient()
        
        connection_info = {
            "url": odoo.url,
            "database": odoo.db,
            "username": odoo.username,
            "status": "connected"
        }
        
        # Models to check
        models_to_check = [
            ('res.partner', 'Patients/Partners'),
            ('calendar.event', 'Appointments'),
            ('account.move', 'Invoices'),
            ('account.move.line', 'Invoice Lines'),
            ('product.product', 'Products/Services'),
            ('product.template', 'Product Templates'),
            ('hr.employee', 'Staff/Employees'),
            ('stock.quant', 'Inventory Items'),
            ('stock.move', 'Stock Movements'),
            ('res.users', 'System Users'),
            ('res.company', 'Companies'),
            ('account.payment', 'Payments'),
            ('mail.message', 'Messages'),
            ('calendar.attendee', 'Appointment Attendees'),
        ]
        
        results = []
        total_records = 0
        models_with_data = 0
        
        for model, description in models_to_check:
            try:
                # Search for records
                record_ids = odoo.search(model, [])
                count = len(record_ids) if record_ids else 0
                total_records += count
                
                if count > 0:
                    models_with_data += 1
                
                status = "✓ Has Data" if count > 0 else "✗ Empty"
                
                # Get sample records (max 3)
                sample_records = []
                if count > 0 and count <= 5:
                    try:
                        records = odoo.read(model, record_ids[:3], ['name', 'display_name', 'id'])
                        sample_records = records or []
                    except Exception as e:
                        logger.warning(f"Could not read sample from {model}: {e}")
                
                results.append(OdooModelCheck(
                    model=model,
                    description=description,
                    record_count=count,
                    status=status,
                    sample_records=sample_records,
                    error=None
                ))
                
            except Exception as e:
                error_msg = str(e)[:200]
                results.append(OdooModelCheck(
                    model=model,
                    description=description,
                    record_count=0,
                    status="✗ Error",
                    sample_records=[],
                    error=error_msg
                ))
                logger.error(f"Error checking {model}: {e}")
        
        # Generate summary
        summary = {
            "total_models_checked": len(results),
            "models_with_data": models_with_data,
            "total_records_found": total_records,
            "database_status": "empty" if total_records == 0 else "populated",
            "recommendation": ""
        }
        
        if total_records == 0:
            summary["recommendation"] = "⚠️ Odoo database is EMPTY. You need to populate it with demo data."
        elif models_with_data < 3:
            summary["recommendation"] = "⚠️ Very little data in Odoo. Consider adding more demo data."
        else:
            summary["recommendation"] = "✓ Odoo has sufficient data for testing."
        
        return DiagnosticsResponse(
            odoo_connection=connection_info,
            models_checked=results,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Diagnostics check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check Odoo: {str(e)}"
        )


@router.get("/backend-endpoints", response_model=Dict[str, Any])
async def list_backend_endpoints():
    """
    List all available backend endpoints.
    
    Returns:
        List of endpoints and their status
    """
    from fastapi.routing import APIRoute
    from app.main import app
    
    endpoints = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            endpoints.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
            })
    
    return {
        "total_endpoints": len(endpoints),
        "endpoints": sorted(endpoints, key=lambda x: x["path"])
    }
