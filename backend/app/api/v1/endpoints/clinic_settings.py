"""
Clinic Settings API endpoints.

Provides CRUD operations for organization-specific clinic settings.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.core.database import get_db
from app.models.clinic_settings import ClinicSettings, DEFAULT_ISRAELI_CLINIC_SETTINGS
from app.models.organization import Organization
from app.schemas.clinic_settings import (
    ClinicSettingsCreate,
    ClinicSettingsUpdate,
    ClinicSettingsResponse
)
from app.api.dependencies import get_current_membership
from app.models.organization_membership import OrganizationMembership

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/organizations/{org_id}/settings",
    response_model=ClinicSettingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create clinic settings",
    description="Create settings for an organization. Uses Israeli clinic defaults if not specified."
)
async def create_clinic_settings(
    org_id: UUID,
    settings_data: ClinicSettingsCreate,
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Create clinic settings for an organization.
    
    - **org_id**: Organization UUID
    - **settings_data**: Settings configuration
    
    Returns the created settings with all defaults applied.
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this organization"
        )
    
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        logger.warning(f"Attempted to create settings for non-existent organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found"
        )
    
    # Check if settings already exist
    existing = db.query(ClinicSettings).filter(
        ClinicSettings.organization_id == org_id
    ).first()
    
    if existing:
        logger.warning(f"Settings already exist for organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Settings already exist for organization {org_id}. Use PUT to update."
        )
    
    try:
        # Create settings with defaults
        settings = ClinicSettings(
            organization_id=org_id,
            **DEFAULT_ISRAELI_CLINIC_SETTINGS
        )
        
        # Apply custom settings if provided
        if settings_data.operating_hours:
            hours = settings_data.operating_hours
            for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
                day_hours = getattr(hours, day)
                if day_hours:
                    setattr(settings, f"{day}_open", day_hours.open)
                    setattr(settings, f"{day}_close", day_hours.close)
        
        if settings_data.appointment_settings:
            apt = settings_data.appointment_settings
            settings.default_appointment_duration = apt.default_duration
            settings.buffer_between_appointments = apt.buffer_time
            settings.advance_booking_days = apt.advance_booking_days
            settings.cancellation_notice_hours = apt.cancellation_notice_hours
            settings.no_show_fee = apt.no_show_fee
            settings.allow_online_booking = apt.allow_online_booking
            settings.require_deposit = apt.require_deposit
            settings.deposit_amount = apt.deposit_amount
        
        if settings_data.communication:
            comm = settings_data.communication
            settings.sms_enabled = comm.sms_enabled
            settings.email_enabled = comm.email_enabled
            settings.whatsapp_enabled = comm.whatsapp_enabled
            settings.telegram_enabled = comm.telegram_enabled
            settings.reminder_hours_before = comm.reminder_hours_before
            settings.send_followup_after_hours = comm.followup_after_hours
            settings.send_recall_after_months = comm.recall_after_months
        
        if settings_data.billing:
            bill = settings_data.billing
            settings.currency = bill.currency
            settings.tax_rate = bill.tax_rate
            settings.payment_methods = bill.payment_methods
            settings.invoice_prefix = bill.invoice_prefix
            settings.invoice_starting_number = bill.invoice_starting_number
        
        if settings_data.clinic_info:
            info = settings_data.clinic_info
            settings.clinic_name_hebrew = info.name_hebrew
            settings.clinic_name_english = info.name_english
            settings.clinic_logo_url = info.logo_url
            settings.clinic_address = info.address
            settings.clinic_phone = info.phone
            settings.clinic_email = info.email
            settings.clinic_website = info.website
            settings.business_license_number = info.business_license
            settings.tax_id = info.tax_id
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Created settings for organization: {org_id}")
        
        # Convert to response format
        return ClinicSettingsResponse(**settings.to_dict())
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violation"
        )
    except ValueError as e:
        db.rollback()
        logger.error(f"Validation error creating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/organizations/{org_id}/settings",
    response_model=ClinicSettingsResponse,
    summary="Get clinic settings",
    description="Retrieve settings for an organization"
)
async def get_clinic_settings(
    org_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Get clinic settings for an organization.
    
    - **org_id**: Organization UUID
    
    Returns the settings or 404 if not found.
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this organization"
        )
    
    settings = db.query(ClinicSettings).filter(
        ClinicSettings.organization_id == org_id
    ).first()
    
    if not settings:
        logger.warning(f"Settings not found for organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settings not found for organization {org_id}"
        )
    
    return ClinicSettingsResponse(**settings.to_dict())


@router.put(
    "/organizations/{org_id}/settings",
    response_model=ClinicSettingsResponse,
    summary="Update clinic settings",
    description="Update settings for an organization (partial updates supported)"
)
async def update_clinic_settings(
    org_id: UUID,
    settings_update: ClinicSettingsUpdate,
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Update clinic settings for an organization.
    
    - **org_id**: Organization UUID
    - **settings_update**: Fields to update (all optional)
    
    Returns the updated settings.
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this organization"
        )
    
    settings = db.query(ClinicSettings).filter(
        ClinicSettings.organization_id == org_id
    ).first()
    
    if not settings:
        logger.warning(f"Settings not found for organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settings not found for organization {org_id}"
        )
    
    try:
        # Update operating hours
        if settings_update.operating_hours:
            hours = settings_update.operating_hours
            for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
                day_hours = getattr(hours, day)
                if day_hours is not None:
                    setattr(settings, f"{day}_open", day_hours.open)
                    setattr(settings, f"{day}_close", day_hours.close)
        
        # Update appointment settings
        if settings_update.appointment_settings:
            apt = settings_update.appointment_settings
            settings.default_appointment_duration = apt.default_duration
            settings.buffer_between_appointments = apt.buffer_time
            settings.advance_booking_days = apt.advance_booking_days
            settings.cancellation_notice_hours = apt.cancellation_notice_hours
            settings.no_show_fee = apt.no_show_fee
            settings.allow_online_booking = apt.allow_online_booking
            settings.require_deposit = apt.require_deposit
            settings.deposit_amount = apt.deposit_amount
        
        # Update communication settings
        if settings_update.communication:
            comm = settings_update.communication
            settings.sms_enabled = comm.sms_enabled
            settings.email_enabled = comm.email_enabled
            settings.whatsapp_enabled = comm.whatsapp_enabled
            settings.telegram_enabled = comm.telegram_enabled
            settings.reminder_hours_before = comm.reminder_hours_before
            settings.send_followup_after_hours = comm.followup_after_hours
            settings.send_recall_after_months = comm.recall_after_months
        
        # Update billing settings
        if settings_update.billing:
            bill = settings_update.billing
            settings.currency = bill.currency
            settings.tax_rate = bill.tax_rate
            settings.payment_methods = bill.payment_methods
            settings.invoice_prefix = bill.invoice_prefix
            settings.invoice_starting_number = bill.invoice_starting_number
        
        # Update clinic info
        if settings_update.clinic_info:
            info = settings_update.clinic_info
            settings.clinic_name_hebrew = info.name_hebrew
            settings.clinic_name_english = info.name_english
            settings.clinic_logo_url = info.logo_url
            settings.clinic_address = info.address
            settings.clinic_phone = info.phone
            settings.clinic_email = info.email
            settings.clinic_website = info.website
            settings.business_license_number = info.business_license
            settings.tax_id = info.tax_id
        
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Updated settings for organization: {org_id}")
        
        return ClinicSettingsResponse(**settings.to_dict())
    
    except ValueError as e:
        db.rollback()
        logger.error(f"Validation error updating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/organizations/{org_id}/settings",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete clinic settings",
    description="Delete settings for an organization (resets to defaults)"
)
async def delete_clinic_settings(
    org_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Delete clinic settings for an organization.
    
    - **org_id**: Organization UUID
    
    Note: This will reset the organization to default settings.
    Consider using PUT to update instead of DELETE.
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this organization"
        )
    
    settings = db.query(ClinicSettings).filter(
        ClinicSettings.organization_id == org_id
    ).first()
    
    if not settings:
        logger.warning(f"Settings not found for organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settings not found for organization {org_id}"
        )
    
    try:
        db.delete(settings)
        db.commit()
        
        logger.info(f"Deleted settings for organization: {org_id}")
        
        return None
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/organizations/{org_id}/settings/reset",
    response_model=ClinicSettingsResponse,
    summary="Reset to default settings",
    description="Reset organization settings to Israeli clinic defaults"
)
async def reset_clinic_settings(
    org_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Reset clinic settings to Israeli defaults.
    
    - **org_id**: Organization UUID
    
    This will overwrite all existing settings with defaults.
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this organization"
        )
    
    settings = db.query(ClinicSettings).filter(
        ClinicSettings.organization_id == org_id
    ).first()
    
    if not settings:
        logger.warning(f"Settings not found for organization: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settings not found for organization {org_id}"
        )
    
    try:
        # Apply all defaults
        for key, value in DEFAULT_ISRAELI_CLINIC_SETTINGS.items():
            setattr(settings, key, value)
        
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Reset settings to defaults for organization: {org_id}")
        
        return ClinicSettingsResponse(**settings.to_dict())
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
