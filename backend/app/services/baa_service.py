"""
Business Associate Agreement (BAA) Service
Manages BAA documents, signatures, and compliance for clinics.
"""

import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.baa_signature import BAASignature
from app.core.config import settings

logger = logging.getLogger(__name__)


class BAAService:
    """
    Handles BAA template management, signing workflows, and verification.
    """
    
    TEMPLATE_PATH = "/home/ubuntu/dental-clinic-ai-repo/docs/compliance/BUSINESS_ASSOCIATE_AGREEMENT_TEMPLATE.md"
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_baa_template(self) -> str:
        """
        Retrieve the latest BAA template content.
        
        Returns:
            BAA template content as a string
        """
        try:
            with open(self.TEMPLATE_PATH, "r") as f:
                template = f.read()
            return template
        except FileNotFoundError:
            logger.error(f"BAA template not found at {self.TEMPLATE_PATH}")
            raise
    
    def get_clinic_baa_template(self, organization: Organization) -> str:
        """
        Personalize BAA template for a specific clinic.
        
        Args:
            organization: Clinic organization
            
        Returns:
            Personalized BAA template
        """
        template = self.get_baa_template()
        
        # Replace placeholders
        template = template.replace("[Dental Clinic Name]", organization.name)
        template = template.replace("[Date]", datetime.utcnow().strftime("%B %d, %Y"))
        template = template.replace("[Address]", organization.address or "[Clinic Address]")
        template = template.replace("[Email]", organization.contact_email or "[Clinic Email]")
        
        return template
    
    def record_baa_signature(
        self, 
        organization_id: int, 
        user_id: int, 
        ip_address: str, 
        user_agent: str,
        signature_name: str,
        signature_title: str,
    ) -> BAASignature:
        """
        Record BAA signature for a clinic.
        
        Args:
            organization_id: Clinic organization ID
            user_id: User ID of the signer
            ip_address: IP address of the signer
            user_agent: User agent of the signer
            signature_name: Name of the person signing
            signature_title: Title of the person signing
            
        Returns:
            The created BAASignature object
        """
        try:
            # Check if already signed
            existing_signature = self.db.query(BAASignature).filter(
                BAASignature.organization_id == organization_id
            ).first()
            
            if existing_signature:
                raise ValueError(f"BAA already signed for organization {organization_id}")
            
            # Create new signature record
            signature = BAASignature(
                organization_id=organization_id,
                user_id=user_id,
                signed_at=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                signature_name=signature_name,
                signature_title=signature_title,
                template_version="1.0"  # TODO: Version the template
            )
            
            self.db.add(signature)
            self.db.commit()
            self.db.refresh(signature)
            
            logger.info(f"BAA signed for organization {organization_id} by user {user_id}")
            return signature
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording BAA signature: {e}")
            raise
    
    def get_baa_signature_status(self, organization_id: int) -> Optional[BAASignature]:
        """
        Get BAA signature status for a clinic.
        
        Args:
            organization_id: Clinic organization ID
            
        Returns:
            BAASignature object if signed, else None
        """
        return self.db.query(BAASignature).filter(
            BAASignature.organization_id == organization_id
        ).first()
    
    def get_all_baa_signatures(self) -> List[BAASignature]:
        """
        Get all BAA signatures (for admin use).
        
        Returns:
            List of all BAASignature objects
        """
        return self.db.query(BAASignature).all()

    def verify_baa_compliance(self, organization_id: int) -> bool:
        """
        Verify if a clinic is BAA compliant.
        
        Args:
            organization_id: Clinic organization ID
            
        Returns:
            True if BAA is signed, False otherwise
        """
        signature = self.get_baa_signature_status(organization_id)
        return signature is not None

