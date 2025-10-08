"""
SMS service for sending verification codes.

Uses AWS SNS for production, console logging for development.
"""

import os
import random
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS messages."""
    
    def __init__(self):
        self.use_sns = os.getenv("USE_AWS_SNS", "false").lower() == "true"
        
        if self.use_sns:
            try:
                import boto3
                self.sns_client = boto3.client('sns', region_name=os.getenv("AWS_REGION", "eu-west-1"))
                logger.info("AWS SNS client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize AWS SNS: {e}. Falling back to console logging.")
                self.use_sns = False
    
    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code."""
        return str(random.randint(100000, 999999))
    
    def format_phone_number(self, phone: str) -> str:
        """
        Format phone number to E.164 format.
        
        Examples:
            - "0501234567" -> "+972501234567"
            - "972501234567" -> "+972501234567"
            - "+972501234567" -> "+972501234567"
        
        Args:
            phone: Phone number in various formats
            
        Returns:
            Phone number in E.164 format (+972...)
        """
        # Remove spaces, dashes, parentheses
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # If starts with 0, replace with +972
        if phone.startswith("0"):
            phone = "+972" + phone[1:]
        
        # If starts with 972, add +
        elif phone.startswith("972"):
            phone = "+" + phone
        
        # If doesn't start with +, assume Israeli number
        elif not phone.startswith("+"):
            phone = "+972" + phone
        
        return phone
    
    async def send_verification_code(
        self,
        phone_number: str,
        code: str,
        user_name: str = None
    ) -> bool:
        """
        Send SMS verification code.
        
        Args:
            phone_number: Recipient phone number
            code: 6-digit verification code
            user_name: Optional user name for personalization
            
        Returns:
            True if SMS was sent successfully, False otherwise
        """
        # Format phone number
        formatted_phone = self.format_phone_number(phone_number)
        
        # Create message
        if user_name:
            message = f"שלום {user_name},\n\nקוד האימות שלך ב-DentaFlow הוא: {code}\n\nהקוד תקף ל-10 דקות.\n\nDentaFlow"
        else:
            message = f"קוד האימות שלך ב-DentaFlow: {code}\n\nתקף ל-10 דקות.\n\nDentaFlow"
        
        return await self._send_sms(formatted_phone, message)
    
    async def send_2fa_code(
        self,
        phone_number: str,
        code: str
    ) -> bool:
        """
        Send 2FA code for login.
        
        Args:
            phone_number: Recipient phone number
            code: 6-digit verification code
            
        Returns:
            True if SMS was sent successfully
        """
        formatted_phone = self.format_phone_number(phone_number)
        
        message = f"קוד האימות שלך להתחברות ל-DentaFlow: {code}\n\nתקף ל-10 דקות.\n\nלא ביקשת? התעלם מהודעה זו."
        
        return await self._send_sms(formatted_phone, message)
    
    async def _send_sms(
        self,
        phone_number: str,
        message: str
    ) -> bool:
        """
        Internal method to send SMS via AWS SNS or console.
        
        Args:
            phone_number: Recipient phone number (E.164 format)
            message: SMS message text
            
        Returns:
            True if sent successfully
        """
        if self.use_sns:
            try:
                response = self.sns_client.publish(
                    PhoneNumber=phone_number,
                    Message=message,
                    MessageAttributes={
                        'AWS.SNS.SMS.SMSType': {
                            'DataType': 'String',
                            'StringValue': 'Transactional'  # For OTP codes
                        }
                    }
                )
                logger.info(f"SMS sent to {phone_number}. Message ID: {response['MessageId']}")
                return True
            except Exception as e:
                logger.error(f"Failed to send SMS via SNS: {e}")
                return False
        else:
            # Development mode - log to console
            logger.info(f"""
================================================================================
📱 SMS (Development Mode)
================================================================================
To: {phone_number}
--------------------------------------------------------------------------------
{message}
================================================================================
            """)
            return True


# Singleton instance
sms_service = SMSService()
