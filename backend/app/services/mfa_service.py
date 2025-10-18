"""
Multi-Factor Authentication (MFA) Service for DentaFlow.AI
Handles TOTP-based 2FA using Google Authenticator compatible tokens
"""

import pyotp
import qrcode
import io
import base64
import secrets
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
import logging

from app.models.user import User
from app.core.encryption_service import get_encryption_service

logger = logging.getLogger(__name__)


class MFAService:
    """
    Service for Multi-Factor Authentication using TOTP (Time-based One-Time Password).
    
    Compatible with Google Authenticator, Authy, and other TOTP apps.
    Includes backup codes for account recovery.
    """
    
    def __init__(self):
        """Initialize MFA service."""
        self.encryption_service = get_encryption_service()
        self.issuer_name = "DentaFlow.AI"
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret key.
        
        Returns:
            Base32-encoded secret key
        """
        return pyotp.random_base32()
    
    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """
        Generate QR code for TOTP setup.
        
        Args:
            user_email: User's email address
            secret: TOTP secret key
            
        Returns:
            Base64-encoded PNG image of QR code
        """
        # Create provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_token(self, secret: str, token: str) -> bool:
        """
        Verify a TOTP token.
        
        Args:
            secret: TOTP secret key
            token: 6-digit TOTP code
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret)
            # Allow 1 time step before and after for clock skew
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of backup codes (8 characters each)
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes
    
    def setup_mfa(
        self,
        db: Session,
        user: User
    ) -> Tuple[str, str, List[str]]:
        """
        Set up MFA for a user.
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Tuple of (secret, qr_code_data_uri, backup_codes)
        """
        # Generate secret
        secret = self.generate_secret()
        
        # Generate QR code
        qr_code = self.generate_qr_code(user.email, secret)
        
        # Generate backup codes
        backup_codes = self.generate_backup_codes()
        
        # Encrypt and store secret (not enabled yet)
        encrypted_secret = self.encryption_service.encrypt(secret)
        user.mfa_secret = encrypted_secret
        
        # Store encrypted backup codes
        backup_codes_str = ",".join(backup_codes)
        encrypted_backup_codes = self.encryption_service.encrypt(backup_codes_str)
        user.mfa_backup_codes = encrypted_backup_codes
        
        # Don't enable MFA yet - user needs to verify first
        user.mfa_enabled = False
        
        db.commit()
        
        logger.info(f"MFA setup initiated for user {user.id}")
        
        return secret, qr_code, backup_codes
    
    def enable_mfa(
        self,
        db: Session,
        user: User,
        token: str
    ) -> bool:
        """
        Enable MFA after verifying the first token.
        
        Args:
            db: Database session
            user: User object
            token: 6-digit TOTP code to verify
            
        Returns:
            True if MFA was enabled successfully, False otherwise
        """
        if not user.mfa_secret:
            logger.error(f"No MFA secret found for user {user.id}")
            return False
        
        # Decrypt secret
        try:
            secret = self.encryption_service.decrypt(user.mfa_secret)
        except Exception as e:
            logger.error(f"Failed to decrypt MFA secret: {e}")
            return False
        
        # Verify token
        if not self.verify_token(secret, token):
            logger.warning(f"Invalid MFA token for user {user.id}")
            return False
        
        # Enable MFA
        user.mfa_enabled = True
        db.commit()
        
        logger.info(f"MFA enabled for user {user.id}")
        return True
    
    def disable_mfa(
        self,
        db: Session,
        user: User,
        token: Optional[str] = None,
        backup_code: Optional[str] = None
    ) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            db: Database session
            user: User object
            token: 6-digit TOTP code (optional)
            backup_code: Backup code (optional)
            
        Returns:
            True if MFA was disabled successfully, False otherwise
        """
        if not user.mfa_enabled:
            logger.warning(f"MFA not enabled for user {user.id}")
            return False
        
        # Verify token or backup code
        verified = False
        
        if token:
            try:
                secret = self.encryption_service.decrypt(user.mfa_secret)
                verified = self.verify_token(secret, token)
            except Exception as e:
                logger.error(f"Failed to verify MFA token: {e}")
        
        if not verified and backup_code:
            verified = self.verify_backup_code(user, backup_code)
        
        if not verified:
            logger.warning(f"Failed to verify credentials for MFA disable: user {user.id}")
            return False
        
        # Disable MFA
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        db.commit()
        
        logger.info(f"MFA disabled for user {user.id}")
        return True
    
    def verify_backup_code(
        self,
        user: User,
        backup_code: str
    ) -> bool:
        """
        Verify a backup code.
        
        Args:
            user: User object
            backup_code: Backup code to verify
            
        Returns:
            True if backup code is valid, False otherwise
        """
        if not user.mfa_backup_codes:
            return False
        
        try:
            # Decrypt backup codes
            backup_codes_str = self.encryption_service.decrypt(user.mfa_backup_codes)
            backup_codes = backup_codes_str.split(",")
            
            # Check if code matches (case-insensitive)
            return backup_code.upper() in [code.upper() for code in backup_codes]
        except Exception as e:
            logger.error(f"Failed to verify backup code: {e}")
            return False
    
    def use_backup_code(
        self,
        db: Session,
        user: User,
        backup_code: str
    ) -> bool:
        """
        Use a backup code (removes it from the list).
        
        Args:
            db: Database session
            user: User object
            backup_code: Backup code to use
            
        Returns:
            True if backup code was valid and used, False otherwise
        """
        if not user.mfa_backup_codes:
            return False
        
        try:
            # Decrypt backup codes
            backup_codes_str = self.encryption_service.decrypt(user.mfa_backup_codes)
            backup_codes = backup_codes_str.split(",")
            
            # Find and remove the code (case-insensitive)
            backup_code_upper = backup_code.upper()
            matching_code = None
            for code in backup_codes:
                if code.upper() == backup_code_upper:
                    matching_code = code
                    break
            
            if not matching_code:
                return False
            
            # Remove the code
            backup_codes.remove(matching_code)
            
            # Encrypt and save remaining codes
            if backup_codes:
                new_backup_codes_str = ",".join(backup_codes)
                encrypted_backup_codes = self.encryption_service.encrypt(new_backup_codes_str)
                user.mfa_backup_codes = encrypted_backup_codes
            else:
                # No backup codes left
                user.mfa_backup_codes = None
                logger.warning(f"User {user.id} has used all backup codes")
            
            db.commit()
            
            logger.info(f"Backup code used for user {user.id}. Remaining: {len(backup_codes)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to use backup code: {e}")
            return False
    
    def regenerate_backup_codes(
        self,
        db: Session,
        user: User,
        token: str
    ) -> Optional[List[str]]:
        """
        Regenerate backup codes.
        
        Args:
            db: Database session
            user: User object
            token: 6-digit TOTP code to verify
            
        Returns:
            List of new backup codes, or None if verification failed
        """
        if not user.mfa_enabled or not user.mfa_secret:
            logger.error(f"MFA not enabled for user {user.id}")
            return None
        
        # Verify token
        try:
            secret = self.encryption_service.decrypt(user.mfa_secret)
            if not self.verify_token(secret, token):
                logger.warning(f"Invalid MFA token for user {user.id}")
                return None
        except Exception as e:
            logger.error(f"Failed to verify MFA token: {e}")
            return None
        
        # Generate new backup codes
        backup_codes = self.generate_backup_codes()
        
        # Encrypt and store
        backup_codes_str = ",".join(backup_codes)
        encrypted_backup_codes = self.encryption_service.encrypt(backup_codes_str)
        user.mfa_backup_codes = encrypted_backup_codes
        
        db.commit()
        
        logger.info(f"Backup codes regenerated for user {user.id}")
        return backup_codes


# Global instance
_mfa_service: Optional[MFAService] = None


def get_mfa_service() -> MFAService:
    """Get or create global MFA service instance."""
    global _mfa_service
    
    if _mfa_service is None:
        _mfa_service = MFAService()
    
    return _mfa_service


# Example usage
if __name__ == "__main__":
    import os
    os.environ['ENCRYPTION_KEY'] = 'test-key-for-development-only'
    
    service = MFAService()
    
    # Generate secret
    secret = service.generate_secret()
    print(f"Secret: {secret}")
    
    # Generate QR code
    qr_code = service.generate_qr_code("user@example.com", secret)
    print(f"QR Code (first 100 chars): {qr_code[:100]}...")
    
    # Generate backup codes
    backup_codes = service.generate_backup_codes()
    print(f"Backup codes: {backup_codes}")
    
    # Verify token (you need to get this from your authenticator app)
    # token = input("Enter TOTP code from your authenticator app: ")
    # is_valid = service.verify_token(secret, token)
    # print(f"Token valid: {is_valid}")

