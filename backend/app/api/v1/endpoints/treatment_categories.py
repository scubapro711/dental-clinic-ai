"""
Treatment Categories API Endpoints.

Provides endpoints for managing treatment categories,
financial analysis, and Marcus AI insights.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.user import User
from app.models.treatment_category import (
    TreatmentCategory,
    TreatmentCategoryType,
)
from app.api.v1.endpoints.auth import get_current_user


router = APIRouter()


# Pydantic schemas

class TreatmentCategoryCreate(BaseModel):
    """Create treatment category request."""
    name: str = Field(..., min_length=1, max_length=255)
    category_type: TreatmentCategoryType
    description: Optional[str] = None
    ada_code: Optional[str] = None
    insurance_code: Optional[str] = None
    average_price: Optional[float] = None
    average_cost: Optional[float] = None
    average_duration_minutes: Optional[int] = None
    requires_specialist: bool = False


class TreatmentCategoryUpdate(BaseModel):
    """Update treatment category request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_type: Optional[TreatmentCategoryType] = None
    description: Optional[str] = None
    ada_code: Optional[str] = None
    insurance_code: Optional[str] = None
    average_price: Optional[float] = None
    average_cost: Optional[float] = None
    average_duration_minutes: Optional[int] = None
    success_rate_percent: Optional[float] = None
    patient_satisfaction_score: Optional[float] = None
    requires_specialist: Optional[bool] = None
    is_active: Optional[bool] = None


class TreatmentCategoryResponse(BaseModel):
    """Treatment category response."""
    id: UUID
    organization_id: UUID
    name: str
    category_type: str
    description: Optional[str]
    ada_code: Optional[str]
    insurance_code: Optional[str]
    average_price: Optional[float]
    average_cost: Optional[float]
    average_profit_margin: Optional[float]
    total_revenue_ytd: float
    total_revenue_mtd: float
    total_procedures_ytd: int
    total_procedures_mtd: int
    average_duration_minutes: Optional[int]
    success_rate_percent: Optional[float]
    patient_satisfaction_score: Optional[float]
    marcus_analyzed: bool
    marcus_analysis_date: Optional[str]
    marcus_profitability_score: Optional[int]
    marcus_demand_score: Optional[int]
    marcus_recommendations: Optional[List[dict]]
    marcus_insights: Optional[dict]
    marcus_alerts: Optional[List[dict]]
    marcus_confidence: Optional[int]
    revenue_trend: Optional[str]
    volume_trend: Optional[str]
    profitability_trend: Optional[str]
    is_high_value: bool
    is_high_demand: bool
    is_underutilized: bool
    is_loss_leader: bool
    requires_specialist: bool
    is_active: bool
    profitability_status: str
    demand_status: str
    needs_attention: bool
    created_at: str
    updated_at: str


# Endpoints

@router.get("/", response_model=List[TreatmentCategoryResponse])
async def list_treatment_categories(
    category_type: Optional[TreatmentCategoryType] = None,
    is_active: Optional[bool] = None,
    is_high_value: Optional[bool] = None,
    is_high_demand: Optional[bool] = None,
    needs_attention: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all treatment categories with optional filtering."""
    query = db.query(TreatmentCategory).filter(
        TreatmentCategory.organization_id == current_user.organization_id,
        TreatmentCategory.deleted_at == None
    )
    
    if category_type:
        query = query.filter(TreatmentCategory.category_type == category_type)
    
    if is_active is not None:
        query = query.filter(TreatmentCategory.is_active == is_active)
    
    if is_high_value is not None:
        query = query.filter(TreatmentCategory.is_high_value == is_high_value)
    
    if is_high_demand is not None:
        query = query.filter(TreatmentCategory.is_high_demand == is_high_demand)
    
    categories = query.order_by(TreatmentCategory.name).all()
    
    # Filter by needs_attention (property, not column)
    if needs_attention is not None:
        categories = [c for c in categories if c.needs_attention == needs_attention]
    
    return [
        TreatmentCategoryResponse(
            **category.to_dict(),
            profitability_status=category.profitability_status,
            demand_status=category.demand_status,
            needs_attention=category.needs_attention
        )
        for category in categories
    ]


@router.get("/{category_id}", response_model=TreatmentCategoryResponse)
async def get_treatment_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific treatment category by ID."""
    category = db.query(TreatmentCategory).filter(
        TreatmentCategory.id == category_id,
        TreatmentCategory.organization_id == current_user.organization_id,
        TreatmentCategory.deleted_at == None
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Treatment category not found")
    
    return TreatmentCategoryResponse(
        **category.to_dict(),
        profitability_status=category.profitability_status,
        demand_status=category.demand_status,
        needs_attention=category.needs_attention
    )


@router.post("/", response_model=TreatmentCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_treatment_category(
    data: TreatmentCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new treatment category."""
    
    # Calculate profit margin if both price and cost provided
    profit_margin = None
    if data.average_price and data.average_cost:
        profit_margin = ((data.average_price - data.average_cost) / data.average_price) * 100
    
    category = TreatmentCategory(
        organization_id=current_user.organization_id,
        name=data.name,
        category_type=data.category_type,
        description=data.description,
        ada_code=data.ada_code,
        insurance_code=data.insurance_code,
        average_price=data.average_price,
        average_cost=data.average_cost,
        average_profit_margin=profit_margin,
        average_duration_minutes=data.average_duration_minutes,
        requires_specialist=data.requires_specialist,
        created_by=current_user.id,
        last_updated_by=current_user.id
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return TreatmentCategoryResponse(
        **category.to_dict(),
        profitability_status=category.profitability_status,
        demand_status=category.demand_status,
        needs_attention=category.needs_attention
    )


@router.put("/{category_id}", response_model=TreatmentCategoryResponse)
async def update_treatment_category(
    category_id: UUID,
    data: TreatmentCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update treatment category."""
    category = db.query(TreatmentCategory).filter(
        TreatmentCategory.id == category_id,
        TreatmentCategory.organization_id == current_user.organization_id,
        TreatmentCategory.deleted_at == None
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Treatment category not found")
    
    # Update fields
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    # Recalculate profit margin if price or cost changed
    if category.average_price and category.average_cost:
        category.average_profit_margin = (
            (category.average_price - category.average_cost) / category.average_price
        ) * 100
    
    category.last_updated_by = current_user.id
    category.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(category)
    
    return TreatmentCategoryResponse(
        **category.to_dict(),
        profitability_status=category.profitability_status,
        demand_status=category.demand_status,
        needs_attention=category.needs_attention
    )


@router.post("/{category_id}/marcus-analyze")
async def marcus_analyze_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger Marcus AI analysis of treatment category."""
    category = db.query(TreatmentCategory).filter(
        TreatmentCategory.id == category_id,
        TreatmentCategory.organization_id == current_user.organization_id,
        TreatmentCategory.deleted_at == None
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Treatment category not found")
    
    # TODO: Implement Marcus AI analysis
    # For now, call the analysis tool
    from app.agents.tools.marcus_treatment_analysis import MarcusTreatmentAnalyzer
    
    analyzer = MarcusTreatmentAnalyzer(db, current_user.organization_id)
    results = analyzer.analyze_category(category_id)
    
    return results


@router.get("/stats/overview")
async def get_category_stats_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overview statistics across all categories."""
    categories = db.query(TreatmentCategory).filter(
        TreatmentCategory.organization_id == current_user.organization_id,
        TreatmentCategory.is_active == True,
        TreatmentCategory.deleted_at == None
    ).all()
    
    total_revenue_ytd = sum(c.total_revenue_ytd for c in categories)
    total_revenue_mtd = sum(c.total_revenue_mtd for c in categories)
    total_procedures_ytd = sum(c.total_procedures_ytd for c in categories)
    total_procedures_mtd = sum(c.total_procedures_mtd for c in categories)
    
    # Calculate weighted average profit margin
    total_weighted_margin = sum(
        (c.average_profit_margin or 0) * c.total_revenue_ytd
        for c in categories
    )
    avg_profit_margin = (
        total_weighted_margin / total_revenue_ytd if total_revenue_ytd > 0 else 0
    )
    
    # Count categories by status
    high_value_count = sum(1 for c in categories if c.is_high_value)
    high_demand_count = sum(1 for c in categories if c.is_high_demand)
    underutilized_count = sum(1 for c in categories if c.is_underutilized)
    loss_leader_count = sum(1 for c in categories if c.is_loss_leader)
    needs_attention_count = sum(1 for c in categories if c.needs_attention)
    
    # Top performers
    top_revenue = sorted(categories, key=lambda c: c.total_revenue_ytd, reverse=True)[:5]
    top_volume = sorted(categories, key=lambda c: c.total_procedures_ytd, reverse=True)[:5]
    top_profit = sorted(
        [c for c in categories if c.average_profit_margin],
        key=lambda c: c.average_profit_margin,
        reverse=True
    )[:5]
    
    return {
        "overview": {
            "total_categories": len(categories),
            "total_revenue_ytd": total_revenue_ytd,
            "total_revenue_mtd": total_revenue_mtd,
            "total_procedures_ytd": total_procedures_ytd,
            "total_procedures_mtd": total_procedures_mtd,
            "average_profit_margin": round(avg_profit_margin, 2),
        },
        "counts": {
            "high_value": high_value_count,
            "high_demand": high_demand_count,
            "underutilized": underutilized_count,
            "loss_leader": loss_leader_count,
            "needs_attention": needs_attention_count,
        },
        "top_performers": {
            "by_revenue": [{"id": str(c.id), "name": c.name, "revenue": c.total_revenue_ytd} for c in top_revenue],
            "by_volume": [{"id": str(c.id), "name": c.name, "procedures": c.total_procedures_ytd} for c in top_volume],
            "by_profitability": [{"id": str(c.id), "name": c.name, "margin": c.average_profit_margin} for c in top_profit],
        }
    }


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete treatment category."""
    category = db.query(TreatmentCategory).filter(
        TreatmentCategory.id == category_id,
        TreatmentCategory.organization_id == current_user.organization_id,
        TreatmentCategory.deleted_at == None
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Treatment category not found")
    
    category.deleted_at = datetime.utcnow()
    category.last_updated_by = current_user.id
    
    db.commit()
    
    return None

