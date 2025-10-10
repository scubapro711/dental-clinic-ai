"""
User-Patient Mapping API Endpoints

Provides endpoints for managing user-patient mappings.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.rbac import require_role, Role
from app.models.user import User
from app.crud import user_patient_mapping as mapping_crud
from app.integrations.odoo_client_v2 import OdooClientV2

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class MappingResponse(BaseModel):
    """Response model for mapping."""
    id: int
    user_id: str
    odoo_patient_id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
    last_synced_at: Optional[str]
    
    class Config:
        from_attributes = True


class CreateMappingRequest(BaseModel):
    """Request model for creating mapping."""
    user_id: str
    odoo_patient_id: int
    email: str
    full_name: Optional[str] = None


class UpdateMappingRequest(BaseModel):
    """Request model for updating mapping."""
    odoo_patient_id: Optional[int] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/mappings/me", response_model=MappingResponse)
async def get_my_mapping(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's patient mapping.
    
    Returns the mapping between the current user and their Odoo patient record.
    """
    mapping = mapping_crud.get_mapping_by_user_id(db, current_user.id)
    
    if not mapping:
        raise HTTPException(status_code=404, detail="No patient mapping found for current user")
    
    return mapping


@router.get("/mappings", response_model=List[MappingResponse])
@require_role(Role.ADMIN)
async def get_all_mappings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all patient mappings (admin only).
    
    Returns a paginated list of all user-patient mappings.
    Requires admin role.
    """
    mappings = mapping_crud.get_all_mappings(db, skip=skip, limit=limit)
    return mappings


@router.post("/mappings", response_model=MappingResponse)
@require_role(Role.ADMIN)
async def create_mapping(
    request: CreateMappingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new patient mapping (admin only).
    
    Creates a new mapping between a user and an Odoo patient.
    Requires admin role.
    """
    # Check if mapping already exists
    existing = mapping_crud.get_mapping_by_user_id(db, request.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Mapping already exists for this user")
    
    mapping = mapping_crud.create_mapping(
        db=db,
        user_id=request.user_id,
        odoo_patient_id=request.odoo_patient_id,
        email=request.email,
        full_name=request.full_name
    )
    
    return mapping


@router.put("/mappings/{mapping_id}", response_model=MappingResponse)
@require_role(Role.ADMIN)
async def update_mapping(
    mapping_id: int,
    request: UpdateMappingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update patient mapping (admin only).
    
    Updates an existing user-patient mapping.
    Requires admin role.
    """
    mapping = mapping_crud.update_mapping(
        db=db,
        mapping_id=mapping_id,
        odoo_patient_id=request.odoo_patient_id,
        email=request.email,
        full_name=request.full_name,
        is_active=request.is_active
    )
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    return mapping


@router.delete("/mappings/{mapping_id}")
@require_role(Role.ADMIN)
async def delete_mapping(
    mapping_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete patient mapping (admin only).
    
    Permanently deletes a user-patient mapping.
    Requires admin role.
    """
    success = mapping_crud.delete_mapping(db, mapping_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    return {"message": "Mapping deleted successfully"}


@router.post("/mappings/sync")
async def sync_mapping(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync current user's mapping with Odoo.
    
    Fetches latest data from Odoo and updates the mapping.
    """
    try:
        odoo_client = OdooClientV2()
        
        # Get current mapping
        mapping = mapping_crud.get_mapping_by_user_id(db, current_user.id)
        
        if not mapping:
            raise HTTPException(status_code=404, detail="No mapping found for current user")
        
        # Fetch latest data from Odoo
        patient = odoo_client.get_patient_by_id(mapping.odoo_patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found in Odoo")
        
        # Update mapping
        updated_mapping = mapping_crud.update_mapping(
            db=db,
            mapping_id=mapping.id,
            email=patient.get('email', mapping.email),
            full_name=patient.get('name', mapping.full_name)
        )
        
        # Update sync time
        mapping_crud.update_sync_time(db, mapping.id)
        
        return {
            "message": "Mapping synced successfully",
            "mapping": updated_mapping.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error syncing mapping: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync mapping")

