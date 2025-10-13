"""
Service for synchronizing users between PostgreSQL and Odoo.

This service ensures that for every user who is a patient, there is a
corresponding `res.partner` record in Odoo, and the link is maintained.
"""

from uuid import UUID
from typing import Optional, Tuple
from sqlalchemy.orm import Session
import logging

from app.models.user import User
from app.models.organization_membership import OrganizationMembership
from app.integrations.odoo_client_v3 import OdooClientV3

logger = logging.getLogger(__name__)


class UserSyncService:
    """Service for synchronizing users between PostgreSQL and Odoo."""
    
    def __init__(self, db: Session):
        self.db = db
        self.odoo = OdooClientV3()
    
    def create_user_with_odoo_patient(
        self,
        email: str,
        full_name: str,
        phone: str,
        organization_id: UUID,
        organization_role: str = "patient"
    ) -> Tuple[User, OrganizationMembership]:
        """
        Create a user in PostgreSQL and a corresponding patient in Odoo.
        
        Returns:
            Tuple of (User, OrganizationMembership)
        """
        # 1. Create Odoo patient first
        odoo_partner_id = self.odoo.create_patient(
            name=full_name,
            email=email,
            phone=phone
        )
        
        logger.info(f"Created Odoo patient {odoo_partner_id} for {email}")
        
        # 2. Create PostgreSQL user
        # Note: In a real app, password would be handled securely
        from app.services.auth_service import AuthService
        user = AuthService.create_user(
            db=self.db,
            email=email,
            password="temp_password", # Or generate a random one
            full_name=full_name,
            phone=phone,
            organization_id=organization_id
        )
        
        # 3. Create membership with Odoo link
        membership = self.db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.organization_id == organization_id
        ).first()
        
        if membership:
            membership.odoo_partner_id = odoo_partner_id
            membership.organization_role = organization_role
        else:
            membership = OrganizationMembership(
                user_id=user.id,
                organization_id=organization_id,
                organization_role=organization_role,
                odoo_partner_id=odoo_partner_id,  # The crucial link
                is_active=True
            )
            self.db.add(membership)
        
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(membership)
        
        logger.info(
            f"Created user {user.id} with Odoo patient {odoo_partner_id} "
            f"in organization {organization_id}"
        )
        
        return user, membership
    
    def get_odoo_partner_id(self, user_id: UUID, organization_id: UUID) -> Optional[int]:
        """
        Get Odoo partner ID for a user in a specific organization.
        
        Args:
            user_id: User UUID
            organization_id: Organization UUID
            
        Returns:
            Odoo partner ID (integer) or None
        """
        membership = self.db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.is_active == True
        ).first()
        
        if not membership:
            return None
        
        # If not synced yet, sync now
        if not membership.odoo_partner_id:
            return self.sync_user_to_odoo(user_id, organization_id)
            
        return membership.odoo_partner_id
    
    def sync_user_to_odoo(
        self, 
        user_id: UUID, 
        organization_id: UUID,
        user_email: str = None,
        user_name: str = None,
        user_phone: str = None,
        date_of_birth: str = None,
        gender: str = None,
        blood_type: str = None,
        street: str = None,
        city: str = None,
        zip_code: str = None,
        country: str = None,
        has_allergies: bool = None,
        allergy_notes: str = None,
        has_medications: bool = None,
        medication_notes: str = None,
    ) -> int:
        """
        Sync existing user to Odoo (create patient if doesn't exist).
        
        Args:
            user_id: User UUID
            organization_id: Organization UUID
            user_email: User email (optional, will fetch from DB if not provided)
            user_name: User full name (optional, will fetch from DB if not provided)
            user_phone: User phone (optional, will fetch from DB if not provided)
            date_of_birth: Date of birth in YYYY-MM-DD format
            gender: Gender (male/female/other)
            blood_type: Blood type
            street: Street address
            city: City
            zip_code: Postal code
            country: Country
            has_allergies: Whether patient has allergies
            allergy_notes: Allergy notes
            has_medications: Whether patient is taking medications
            medication_notes: Medication notes
            
        Returns:
            Odoo partner ID
        """
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Use provided values or fall back to user data
        email = user_email or user.email
        name = user_name or user.full_name
        phone = user_phone or user.phone
        
        # Get membership
        membership = self.db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == organization_id
        ).first()
        
        if not membership:
            raise ValueError(f"User {user_id} not member of org {organization_id}")
        
        # Check if already synced
        if membership.odoo_partner_id:
            logger.info(f"User {user_id} already synced to Odoo {membership.odoo_partner_id}")
            return membership.odoo_partner_id
        
        # Check if patient exists in Odoo by email
        existing_patient_ids = self.odoo.search_patients(email=email)
        if existing_patient_ids:
            odoo_partner_id = existing_patient_ids[0]
            logger.info(f"Found existing Odoo patient {odoo_partner_id} for {email}")
        else:
            # Parse name into first and last name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Create Odoo patient with all available fields
            from app.agents.tools.alex_patient_tools import create_patient_tool
            
            result = create_patient_tool(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                clinic_id=int(organization_id) if organization_id else 1,
                email=email,
                date_of_birth=date_of_birth,
                gender=gender,
                blood_type=blood_type,
                address=street,
                city=city,
                zip_code=zip_code,
                notes=f"Allergies: {allergy_notes}" if has_allergies and allergy_notes else None,
            )
            
            odoo_partner_id = result.get('partner_id')
            logger.info(f"Created new Odoo patient {odoo_partner_id} for {email}")
        
        # Update membership
        membership.odoo_partner_id = odoo_partner_id
        self.db.commit()
        
        logger.info(f"Synced user {user_id} to Odoo patient {odoo_partner_id}")
        
        return odoo_partner_id

