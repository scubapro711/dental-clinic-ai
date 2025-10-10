"""
CRUD operations for User-Patient Mapping

Provides database operations for managing user-patient mappings.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user_patient_mapping import UserPatientMapping


def get_mapping_by_user_id(db: Session, user_id: str) -> Optional[UserPatientMapping]:
    """
    Get mapping by user ID.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Mapping or None
    """
    return db.query(UserPatientMapping).filter(
        and_(
            UserPatientMapping.user_id == user_id,
            UserPatientMapping.is_active == True
        )
    ).first()


def get_mapping_by_odoo_patient_id(db: Session, odoo_patient_id: int) -> Optional[UserPatientMapping]:
    """
    Get mapping by Odoo patient ID.
    
    Args:
        db: Database session
        odoo_patient_id: Odoo patient ID
    
    Returns:
        Mapping or None
    """
    return db.query(UserPatientMapping).filter(
        and_(
            UserPatientMapping.odoo_patient_id == odoo_patient_id,
            UserPatientMapping.is_active == True
        )
    ).first()


def get_mapping_by_email(db: Session, email: str) -> Optional[UserPatientMapping]:
    """
    Get mapping by email.
    
    Args:
        db: Database session
        email: Email address
    
    Returns:
        Mapping or None
    """
    return db.query(UserPatientMapping).filter(
        and_(
            UserPatientMapping.email == email,
            UserPatientMapping.is_active == True
        )
    ).first()


def get_all_mappings(db: Session, skip: int = 0, limit: int = 100) -> List[UserPatientMapping]:
    """
    Get all active mappings.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of mappings
    """
    return db.query(UserPatientMapping).filter(
        UserPatientMapping.is_active == True
    ).offset(skip).limit(limit).all()


def create_mapping(
    db: Session,
    user_id: str,
    odoo_patient_id: int,
    email: str,
    full_name: Optional[str] = None
) -> UserPatientMapping:
    """
    Create new mapping.
    
    Args:
        db: Database session
        user_id: User ID
        odoo_patient_id: Odoo patient ID
        email: Email address
        full_name: Full name (optional)
    
    Returns:
        Created mapping
    """
    mapping = UserPatientMapping(
        user_id=user_id,
        odoo_patient_id=odoo_patient_id,
        email=email,
        full_name=full_name,
        is_active=True,
        last_synced_at=datetime.utcnow()
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def update_mapping(
    db: Session,
    mapping_id: int,
    odoo_patient_id: Optional[int] = None,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[UserPatientMapping]:
    """
    Update existing mapping.
    
    Args:
        db: Database session
        mapping_id: Mapping ID
        odoo_patient_id: New Odoo patient ID (optional)
        email: New email (optional)
        full_name: New full name (optional)
        is_active: New active status (optional)
    
    Returns:
        Updated mapping or None
    """
    mapping = db.query(UserPatientMapping).filter(
        UserPatientMapping.id == mapping_id
    ).first()
    
    if not mapping:
        return None
    
    if odoo_patient_id is not None:
        mapping.odoo_patient_id = odoo_patient_id
    if email is not None:
        mapping.email = email
    if full_name is not None:
        mapping.full_name = full_name
    if is_active is not None:
        mapping.is_active = is_active
    
    mapping.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(mapping)
    return mapping


def update_sync_time(db: Session, mapping_id: int) -> Optional[UserPatientMapping]:
    """
    Update last sync time for mapping.
    
    Args:
        db: Database session
        mapping_id: Mapping ID
    
    Returns:
        Updated mapping or None
    """
    mapping = db.query(UserPatientMapping).filter(
        UserPatientMapping.id == mapping_id
    ).first()
    
    if not mapping:
        return None
    
    mapping.last_synced_at = datetime.utcnow()
    mapping.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(mapping)
    return mapping


def deactivate_mapping(db: Session, mapping_id: int) -> Optional[UserPatientMapping]:
    """
    Deactivate mapping (soft delete).
    
    Args:
        db: Database session
        mapping_id: Mapping ID
    
    Returns:
        Deactivated mapping or None
    """
    return update_mapping(db, mapping_id, is_active=False)


def delete_mapping(db: Session, mapping_id: int) -> bool:
    """
    Permanently delete mapping.
    
    Args:
        db: Database session
        mapping_id: Mapping ID
    
    Returns:
        True if deleted, False otherwise
    """
    mapping = db.query(UserPatientMapping).filter(
        UserPatientMapping.id == mapping_id
    ).first()
    
    if not mapping:
        return False
    
    db.delete(mapping)
    db.commit()
    return True


def get_or_create_mapping(
    db: Session,
    user_id: str,
    odoo_patient_id: int,
    email: str,
    full_name: Optional[str] = None
) -> tuple[UserPatientMapping, bool]:
    """
    Get existing mapping or create new one.
    
    Args:
        db: Database session
        user_id: User ID
        odoo_patient_id: Odoo patient ID
        email: Email address
        full_name: Full name (optional)
    
    Returns:
        Tuple of (mapping, created) where created is True if new mapping was created
    """
    # Try to get existing mapping
    mapping = get_mapping_by_user_id(db, user_id)
    
    if mapping:
        # Update if needed
        if mapping.odoo_patient_id != odoo_patient_id or mapping.email != email:
            mapping = update_mapping(
                db,
                mapping.id,
                odoo_patient_id=odoo_patient_id,
                email=email,
                full_name=full_name
            )
        return (mapping, False)
    
    # Create new mapping
    mapping = create_mapping(db, user_id, odoo_patient_id, email, full_name)
    return (mapping, True)

