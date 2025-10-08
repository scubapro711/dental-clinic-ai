"""
Treatment Prices API endpoints.

Provides CRUD operations for organization-specific treatment pricing.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.core.database import get_db
from app.models.treatment_price import TreatmentPrice, DEFAULT_ISRAELI_TREATMENTS
from app.models.organization import Organization
from app.schemas.treatment_price import (
    TreatmentPriceCreate,
    TreatmentPriceUpdate,
    TreatmentPriceResponse,
    TreatmentPriceBulkCreate
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/organizations/{org_id}/treatments",
    response_model=TreatmentPriceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create treatment price",
    description="Create a new treatment price for an organization"
)
async def create_treatment_price(
    org_id: UUID,
    treatment_data: TreatmentPriceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new treatment price.
    
    - **org_id**: Organization UUID
    - **treatment_data**: Treatment configuration
    
    Returns the created treatment.
    """
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        logger.warning(f"Attempted to create treatment for non-existent organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found"
        )
    
    # Check if treatment code already exists for this organization
    existing = db.query(TreatmentPrice).filter(
        TreatmentPrice.organization_id == org_id,
        TreatmentPrice.treatment_code == treatment_data.treatment_code
    ).first()
    
    if existing:
        logger.warning(f"Treatment code {treatment_data.treatment_code} already exists for org {org_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Treatment code {treatment_data.treatment_code} already exists"
        )
    
    try:
        # Create treatment
        treatment = TreatmentPrice(
            organization_id=org_id,
            treatment_code=treatment_data.treatment_code,
            treatment_name_hebrew=treatment_data.treatment_name_hebrew,
            treatment_name_english=treatment_data.treatment_name_english,
            category=treatment_data.category,
            description=treatment_data.description,
            base_price=treatment_data.base_price,
            member_price=treatment_data.member_price,
            insurance_price=treatment_data.insurance_price,
            currency=treatment_data.currency,
            duration_minutes=treatment_data.duration_minutes,
            requires_specialist=treatment_data.requires_specialist,
            specialist_type=treatment_data.specialist_type,
            odoo_product_id=treatment_data.odoo_product_id,
            odoo_product_template_id=treatment_data.odoo_product_template_id,
            is_active=treatment_data.is_active,
            is_visible_online=treatment_data.is_visible_online,
            requires_approval=treatment_data.requires_approval,
            notes=treatment_data.notes,
            display_order=treatment_data.display_order
        )
        
        db.add(treatment)
        db.commit()
        db.refresh(treatment)
        
        logger.info(f"Created treatment {treatment.treatment_code} for organization {org_id}")
        
        return TreatmentPriceResponse(**treatment.to_dict())
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating treatment: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violation"
        )
    except ValueError as e:
        db.rollback()
        logger.error(f"Validation error creating treatment: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating treatment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/organizations/{org_id}/treatments",
    response_model=List[TreatmentPriceResponse],
    summary="List treatment prices",
    description="Get all treatment prices for an organization"
)
async def list_treatment_prices(
    org_id: UUID,
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Show only active treatments"),
    visible_only: bool = Query(False, description="Show only visible online treatments"),
    db: Session = Depends(get_db)
):
    """
    List all treatment prices for an organization.
    
    - **org_id**: Organization UUID
    - **category**: Optional category filter
    - **active_only**: Show only active treatments
    - **visible_only**: Show only treatments visible online
    
    Returns list of treatments.
    """
    query = db.query(TreatmentPrice).filter(
        TreatmentPrice.organization_id == org_id
    )
    
    if category:
        query = query.filter(TreatmentPrice.category == category)
    
    if active_only:
        query = query.filter(TreatmentPrice.is_active == True)
    
    if visible_only:
        query = query.filter(TreatmentPrice.is_visible_online == True)
    
    # Order by display_order, then by name
    query = query.order_by(
        TreatmentPrice.display_order.nullslast(),
        TreatmentPrice.treatment_name_hebrew
    )
    
    treatments = query.all()
    
    return [TreatmentPriceResponse(**t.to_dict()) for t in treatments]


@router.get(
    "/organizations/{org_id}/treatments/{treatment_id}",
    response_model=TreatmentPriceResponse,
    summary="Get treatment price",
    description="Get a specific treatment price by ID"
)
async def get_treatment_price(
    org_id: UUID,
    treatment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific treatment price.
    
    - **org_id**: Organization UUID
    - **treatment_id**: Treatment UUID
    
    Returns the treatment or 404 if not found.
    """
    treatment = db.query(TreatmentPrice).filter(
        TreatmentPrice.id == treatment_id,
        TreatmentPrice.organization_id == org_id
    ).first()
    
    if not treatment:
        logger.warning(f"Treatment {treatment_id} not found for organization {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Treatment {treatment_id} not found"
        )
    
    return TreatmentPriceResponse(**treatment.to_dict())


@router.get(
    "/organizations/{org_id}/treatments/code/{treatment_code}",
    response_model=TreatmentPriceResponse,
    summary="Get treatment by code",
    description="Get a treatment price by treatment code"
)
async def get_treatment_by_code(
    org_id: UUID,
    treatment_code: str,
    db: Session = Depends(get_db)
):
    """
    Get a treatment price by code.
    
    - **org_id**: Organization UUID
    - **treatment_code**: Treatment code (e.g., 'CLEAN-001')
    
    Returns the treatment or 404 if not found.
    """
    treatment = db.query(TreatmentPrice).filter(
        TreatmentPrice.organization_id == org_id,
        TreatmentPrice.treatment_code == treatment_code
    ).first()
    
    if not treatment:
        logger.warning(f"Treatment code {treatment_code} not found for organization {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Treatment code {treatment_code} not found"
        )
    
    return TreatmentPriceResponse(**treatment.to_dict())


@router.put(
    "/organizations/{org_id}/treatments/{treatment_id}",
    response_model=TreatmentPriceResponse,
    summary="Update treatment price",
    description="Update a treatment price (partial updates supported)"
)
async def update_treatment_price(
    org_id: UUID,
    treatment_id: UUID,
    treatment_update: TreatmentPriceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a treatment price.
    
    - **org_id**: Organization UUID
    - **treatment_id**: Treatment UUID
    - **treatment_update**: Fields to update (all optional)
    
    Returns the updated treatment.
    """
    treatment = db.query(TreatmentPrice).filter(
        TreatmentPrice.id == treatment_id,
        TreatmentPrice.organization_id == org_id
    ).first()
    
    if not treatment:
        logger.warning(f"Treatment {treatment_id} not found for organization {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Treatment {treatment_id} not found"
        )
    
    try:
        # Update fields
        update_data = treatment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(treatment, field, value)
        
        db.commit()
        db.refresh(treatment)
        
        logger.info(f"Updated treatment {treatment_id} for organization {org_id}")
        
        return TreatmentPriceResponse(**treatment.to_dict())
    
    except ValueError as e:
        db.rollback()
        logger.error(f"Validation error updating treatment: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating treatment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/organizations/{org_id}/treatments/{treatment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete treatment price",
    description="Delete a treatment price"
)
async def delete_treatment_price(
    org_id: UUID,
    treatment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a treatment price.
    
    - **org_id**: Organization UUID
    - **treatment_id**: Treatment UUID
    
    Note: Consider soft-delete (is_active=False) instead of hard delete.
    """
    treatment = db.query(TreatmentPrice).filter(
        TreatmentPrice.id == treatment_id,
        TreatmentPrice.organization_id == org_id
    ).first()
    
    if not treatment:
        logger.warning(f"Treatment {treatment_id} not found for organization {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Treatment {treatment_id} not found"
        )
    
    try:
        db.delete(treatment)
        db.commit()
        
        logger.info(f"Deleted treatment {treatment_id} for organization {org_id}")
        
        return None
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting treatment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/organizations/{org_id}/treatments/bulk",
    response_model=List[TreatmentPriceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create treatments",
    description="Create multiple treatment prices at once"
)
async def bulk_create_treatments(
    org_id: UUID,
    bulk_data: TreatmentPriceBulkCreate,
    db: Session = Depends(get_db)
):
    """
    Bulk create treatment prices.
    
    - **org_id**: Organization UUID
    - **bulk_data**: List of treatments to create
    
    Returns list of created treatments.
    """
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        logger.warning(f"Attempted bulk create for non-existent organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found"
        )
    
    created_treatments = []
    errors = []
    
    try:
        for treatment_data in bulk_data.treatments:
            # Check for duplicates
            existing = db.query(TreatmentPrice).filter(
                TreatmentPrice.organization_id == org_id,
                TreatmentPrice.treatment_code == treatment_data.treatment_code
            ).first()
            
            if existing:
                errors.append(f"Treatment code {treatment_data.treatment_code} already exists")
                continue
            
            # Create treatment
            treatment = TreatmentPrice(
                organization_id=org_id,
                **treatment_data.dict(exclude={'organization_id'})
            )
            
            db.add(treatment)
            created_treatments.append(treatment)
        
        db.commit()
        
        # Refresh all created treatments
        for treatment in created_treatments:
            db.refresh(treatment)
        
        logger.info(f"Bulk created {len(created_treatments)} treatments for organization {org_id}")
        
        if errors:
            logger.warning(f"Bulk create had {len(errors)} errors: {errors}")
        
        return [TreatmentPriceResponse(**t.to_dict()) for t in created_treatments]
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk create: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk create failed: {str(e)}"
        )


@router.post(
    "/organizations/{org_id}/treatments/init-defaults",
    response_model=List[TreatmentPriceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Initialize default treatments",
    description="Initialize organization with default Israeli dental treatments"
)
async def initialize_default_treatments(
    org_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Initialize default Israeli dental treatments for an organization.
    
    - **org_id**: Organization UUID
    
    Creates 10 common Israeli dental treatments with standard pricing.
    """
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        logger.warning(f"Attempted to init defaults for non-existent organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found"
        )
    
    # Check if treatments already exist
    existing_count = db.query(TreatmentPrice).filter(
        TreatmentPrice.organization_id == org_id
    ).count()
    
    if existing_count > 0:
        logger.warning(f"Organization {org_id} already has {existing_count} treatments")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization already has {existing_count} treatments. Delete them first or use bulk create."
        )
    
    try:
        created_treatments = []
        
        for default_treatment in DEFAULT_ISRAELI_TREATMENTS:
            treatment = TreatmentPrice(
                organization_id=org_id,
                **default_treatment
            )
            db.add(treatment)
            created_treatments.append(treatment)
        
        db.commit()
        
        # Refresh all
        for treatment in created_treatments:
            db.refresh(treatment)
        
        logger.info(f"Initialized {len(created_treatments)} default treatments for organization {org_id}")
        
        return [TreatmentPriceResponse(**t.to_dict()) for t in created_treatments]
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing defaults: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize defaults: {str(e)}"
        )
