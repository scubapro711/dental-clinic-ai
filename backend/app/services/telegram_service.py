"""
Telegram User Service

Handles Telegram user management, onboarding, and patient linking.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.telegram_user import TelegramUser, TelegramUserStatus
from app.models.telegram_conversation import TelegramConversation
from app.models.telegram_invite_code import TelegramInviteCode, InviteCodeStatus
from app.integrations.odoo_client_v3 import OdooClientV3

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for managing Telegram users and onboarding."""
    
    def __init__(self, db: Session):
        self.db = db
        self.odoo_client = OdooClientV3()
    
    def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> TelegramUser:
        """
        Get existing Telegram user or create new one.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            TelegramUser instance
        """
        # Try to find existing user
        user = self.db.query(TelegramUser).filter(
            TelegramUser.telegram_user_id == telegram_id
        ).first()
        
        if user:
            # Update user info if changed
            updated = False
            if username and user.telegram_username != username:
                user.telegram_username = username
                updated = True
            if first_name and user.telegram_first_name != first_name:
                user.telegram_first_name = first_name
                updated = True
            if last_name and user.telegram_last_name != last_name:
                user.telegram_last_name = last_name
                updated = True
            
            if updated:
                user.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(user)
            
            return user
        
        # Create new user
        user = TelegramUser(
            telegram_user_id=telegram_id,
            telegram_username=username,
            telegram_first_name=first_name,
            telegram_last_name=last_name,
            organization_id="00000000-0000-0000-0000-000000000000",  # Default org
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created new Telegram user: {telegram_id} (@{username})")
        return user
    
    def link_to_patient(
        self,
        telegram_user: TelegramUser,
        patient_phone: str,
        organization_id: str,
    ) -> bool:
        """
        Link Telegram user to existing patient in Odoo.
        
        Args:
            telegram_user: TelegramUser instance
            patient_phone: Patient's phone number
            organization_id: Organization ID
            
        Returns:
            True if linked successfully, False otherwise
        """
        try:
            # Search for patient in Odoo by phone
            patients = self.odoo_client.search_patients(
                organization_id=organization_id,
                phone=patient_phone
            )
            
            if not patients:
                logger.warning(f"No patient found with phone {patient_phone}")
                return False
            
            # Take first match
            patient = patients[0]
            
            # Update Telegram user
            telegram_user.patient_id = patient['id']
            telegram_user.organization_id = organization_id
            telegram_user.phone = patient_phone
            telegram_user.status = TelegramUserStatus.LINKED
            telegram_user.linked_at = datetime.utcnow()
            telegram_user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(telegram_user)
            
            logger.info(
                f"Linked Telegram user {telegram_user.telegram_user_id} "
                f"to patient {patient['id']} in org {organization_id}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error linking Telegram user to patient: {e}")
            self.db.rollback()
            return False
    
    def create_patient_and_link(
        self,
        telegram_user: TelegramUser,
        patient_data: Dict[str, Any],
        organization_id: str,
    ) -> bool:
        """
        Create new patient in Odoo and link to Telegram user.
        
        Args:
            telegram_user: TelegramUser instance
            patient_data: Patient information (name, phone, email, birth_date)
            organization_id: Organization ID
            
        Returns:
            True if created and linked successfully, False otherwise
        """
        try:
            # Create patient in Odoo
            patient_id = self.odoo_client.create_patient(
                organization_id=organization_id,
                name=patient_data['name'],
                phone=patient_data['phone'],
                email=patient_data.get('email'),
                birth_date=patient_data.get('birth_date'),
            )
            
            if not patient_id:
                logger.error("Failed to create patient in Odoo")
                return False
            
            # Update Telegram user
            telegram_user.patient_id = patient_id
            telegram_user.organization_id = organization_id
            telegram_user.phone = patient_data['phone']
            telegram_user.status = TelegramUserStatus.LINKED
            telegram_user.linked_at = datetime.utcnow()
            telegram_user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(telegram_user)
            
            logger.info(
                f"Created patient {patient_id} and linked to "
                f"Telegram user {telegram_user.telegram_user_id}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error creating patient and linking: {e}")
            self.db.rollback()
            return False
    
    def validate_invite_code(
        self,
        code: str,
        telegram_user: TelegramUser,
    ) -> Optional[TelegramInviteCode]:
        """
        Validate invite code and use it if valid.
        
        Args:
            code: Invite code string
            telegram_user: TelegramUser instance
            
        Returns:
            TelegramInviteCode if valid, None otherwise
        """
        invite = self.db.query(TelegramInviteCode).filter(
            and_(
                TelegramInviteCode.code == code,
                TelegramInviteCode.status == InviteCodeStatus.ACTIVE,
            )
        ).first()
        
        if not invite:
            logger.warning(f"Invalid or inactive invite code: {code}")
            return None
        
        # Check expiration
        if invite.expires_at and invite.expires_at < datetime.utcnow():
            logger.warning(f"Expired invite code: {code}")
            invite.status = InviteCodeStatus.EXPIRED
            self.db.commit()
            return None
        
        # Check usage limit
        if invite.max_uses and invite.used_count >= invite.max_uses:
            logger.warning(f"Invite code reached max uses: {code}")
            invite.status = InviteCodeStatus.USED
            self.db.commit()
            return None
        
        # Use the invite code
        invite.used_count += 1
        invite.used_at = datetime.utcnow()
        
        # Mark as used if reached max uses
        if invite.max_uses and invite.used_count >= invite.max_uses:
            invite.status = InviteCodeStatus.USED
        
        # Link user to organization via invite
        telegram_user.organization_id = invite.organization_id
        telegram_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(invite)
        self.db.refresh(telegram_user)
        
        logger.info(
            f"Telegram user {telegram_user.telegram_user_id} used invite code "
            f"{code} for org {invite.organization_id}"
        )
        return invite
    
    def get_or_create_conversation(
        self,
        telegram_user: TelegramUser,
        chat_id: int,
    ) -> TelegramConversation:
        """
        Get existing conversation or create new one.
        
        Args:
            telegram_user: TelegramUser instance
            chat_id: Telegram chat ID
            
        Returns:
            TelegramConversation instance
        """
        # Try to find active conversation
        conversation = self.db.query(TelegramConversation).filter(
            and_(
                TelegramConversation.telegram_user_id == telegram_user.id,
                TelegramConversation.chat_id == chat_id,
                TelegramConversation.is_active == True,
            )
        ).first()
        
        if conversation:
            return conversation
        
        # Create new conversation
        conversation = TelegramConversation(
            telegram_user_id=telegram_user.id,
            organization_id=telegram_user.organization_id,
            chat_id=chat_id,
            is_active=True,
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(
            f"Created new conversation for Telegram user "
            f"{telegram_user.telegram_user_id} in chat {chat_id}"
        )
        return conversation
    
    def get_onboarding_status(self, telegram_user: TelegramUser) -> Dict[str, Any]:
        """
        Get onboarding status for Telegram user.
        
        Args:
            telegram_user: TelegramUser instance
            
        Returns:
            Dictionary with onboarding status
        """
        return {
            "status": telegram_user.status,
            "has_organization": telegram_user.organization_id is not None,
            "has_patient_link": telegram_user.patient_id is not None,
            "is_complete": telegram_user.status == TelegramUserStatus.LINKED,
            "next_step": self._get_next_onboarding_step(telegram_user),
        }
    
    def _get_next_onboarding_step(self, telegram_user: TelegramUser) -> str:
        """
        Determine next onboarding step for user.
        
        Args:
            telegram_user: TelegramUser instance
            
        Returns:
            Next step description
        """
        if telegram_user.status == TelegramUserStatus.LINKED:
            return "complete"
        
        if not telegram_user.organization_id:
            return "need_invite_code"
        
        if not telegram_user.patient_id:
            return "need_patient_link"
        
        return "unknown"

