"""
Email service for sending verification and notification emails.

Uses AWS SES for production, console logging for development.
"""

import os
import secrets
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.from_email = os.getenv("FROM_EMAIL", "noreply@dentaflow.ai")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.use_ses = os.getenv("USE_AWS_SES", "false").lower() == "true"
        
        if self.use_ses:
            try:
                import boto3
                self.ses_client = boto3.client('ses', region_name=os.getenv("AWS_REGION", "eu-west-1"))
                logger.info("AWS SES client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize AWS SES: {e}. Falling back to console logging.")
                self.use_ses = False
    
    def generate_verification_token(self) -> str:
        """Generate a secure random verification token."""
        return secrets.token_urlsafe(32)
    
    async def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        verification_token: str
    ) -> bool:
        """
        Send email verification email.
        
        Args:
            to_email: Recipient email address
            user_name: User's full name
            verification_token: Verification token
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        verification_url = f"{self.frontend_url}/auth/verify-email?token={verification_token}"
        
        subject = "אמת את כתובת האימייל שלך - DentaFlow"
        
        html_body = f"""
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f4f4f4; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin: 0;">🦷 DentaFlow</h1>
            <p style="color: #7f8c8d; margin: 10px 0 0 0;">מערכת ניהול מרפאות שיניים חכמה</p>
        </div>
        
        <h2 style="color: #2c3e50;">שלום {user_name},</h2>
        
        <p style="color: #34495e; line-height: 1.6; font-size: 16px;">
            תודה שנרשמת ל-DentaFlow! 
        </p>
        
        <p style="color: #34495e; line-height: 1.6; font-size: 16px;">
            כדי להשלים את תהליך ההרשמה, אנא אמת את כתובת האימייל שלך על ידי לחיצה על הכפתור למטה:
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="display: inline-block; background-color: #3498db; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold;">
                אמת אימייל
            </a>
        </div>
        
        <p style="color: #7f8c8d; font-size: 14px; line-height: 1.6;">
            אם הכפתור לא עובד, העתק והדבק את הקישור הבא לדפדפן שלך:
        </p>
        
        <p style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; word-break: break-all; font-size: 12px; direction: ltr; text-align: left;">
            {verification_url}
        </p>
        
        <div style="border-top: 1px solid #ecf0f1; margin-top: 30px; padding-top: 20px;">
            <p style="color: #95a5a6; font-size: 12px; line-height: 1.6;">
                <strong>שים לב:</strong> הקישור תקף ל-24 שעות בלבד.
            </p>
            
            <p style="color: #95a5a6; font-size: 12px; line-height: 1.6;">
                אם לא ביקשת להירשם ל-DentaFlow, אנא התעלם מאימייל זה.
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
            <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                © 2025 DentaFlow. כל הזכויות שמורות.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        text_body = f"""
שלום {user_name},

תודה שנרשמת ל-DentaFlow!

כדי להשלים את תהליך ההרשמה, אנא אמת את כתובת האימייל שלך על ידי לחיצה על הקישור הבא:

{verification_url}

שים לב: הקישור תקף ל-24 שעות בלבד.

אם לא ביקשת להירשם ל-DentaFlow, אנא התעלם מאימייל זה.

בברכה,
צוות DentaFlow
"""
        
        return await self._send_email(to_email, subject, html_body, text_body)
    
    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """
        Send welcome email after successful verification.
        
        Args:
            to_email: Recipient email address
            user_name: User's full name
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        subject = "ברוך הבא ל-DentaFlow! 🎉"
        
        html_body = f"""
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f4f4f4; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
        <h1 style="color: #2c3e50;">🎉 ברוך הבא ל-DentaFlow, {user_name}!</h1>
        
        <p style="color: #34495e; line-height: 1.6; font-size: 16px;">
            האימייל שלך אומת בהצלחה! אתה יכול עכשיו להתחבר למערכת וליהנות מכל התכונות.
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{self.frontend_url}/login" 
               style="display: inline-block; background-color: #27ae60; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold;">
                התחבר למערכת
            </a>
        </div>
        
        <p style="color: #7f8c8d; font-size: 14px;">
            בברכה,<br>
            צוות DentaFlow
        </p>
    </div>
</body>
</html>
"""
        
        text_body = f"""
ברוך הבא ל-DentaFlow, {user_name}!

האימייל שלך אומת בהצלחה! אתה יכול עכשיו להתחבר למערכת וליהנות מכל התכונות.

התחבר כאן: {self.frontend_url}/login

בברכה,
צוות DentaFlow
"""
        
        return await self._send_email(to_email, subject, html_body, text_body)
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> bool:
        """
        Internal method to send email via AWS SES or console.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body
            
        Returns:
            True if sent successfully
        """
        if self.use_ses:
            try:
                response = self.ses_client.send_email(
                    Source=self.from_email,
                    Destination={'ToAddresses': [to_email]},
                    Message={
                        'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                        'Body': {
                            'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                            'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                        }
                    }
                )
                logger.info(f"Email sent to {to_email}. Message ID: {response['MessageId']}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via SES: {e}")
                return False
        else:
            # Development mode - log to console
            logger.info(f"""
================================================================================
📧 EMAIL (Development Mode)
================================================================================
To: {to_email}
Subject: {subject}
--------------------------------------------------------------------------------
{text_body}
================================================================================
            """)
            return True


# Singleton instance
email_service = EmailService()
