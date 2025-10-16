"""
Alert Service

Sends email alerts for critical platform events.
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Types of alerts that can be sent."""
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_CANCELED = "subscription_canceled"
    TRIAL_ENDING = "trial_ending"
    HIGH_USAGE = "high_usage"
    HIGH_COST = "high_cost"
    SYSTEM_ERROR = "system_error"
    NEW_SIGNUP = "new_signup"
    CHURN_RISK = "churn_risk"


class AlertService:
    """
    Service for sending email alerts to super admins.
    
    Features:
    - Send alerts for critical events
    - Template-based email generation
    - Multiple recipient support
    - Alert history tracking
    """
    
    def __init__(self):
        """Initialize alert service."""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("ALERT_FROM_EMAIL", self.smtp_user)
        self.admin_emails = os.getenv("ADMIN_ALERT_EMAILS", "").split(",")
        
        # Filter out empty strings
        self.admin_emails = [email.strip() for email in self.admin_emails if email.strip()]
    
    def is_configured(self) -> bool:
        """Check if email alerts are properly configured."""
        return bool(
            self.smtp_user and 
            self.smtp_password and 
            self.admin_emails
        )
    
    def send_alert(
        self,
        alert_type: AlertType,
        subject: str,
        message: str,
        data: Optional[Dict] = None,
        recipients: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email alert.
        
        Args:
            alert_type: Type of alert
            subject: Email subject
            message: Email body (HTML supported)
            data: Additional data to include in email
            recipients: List of email addresses (defaults to admin_emails)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Email alerts not configured, skipping alert")
            return False
        
        if recipients is None:
            recipients = self.admin_emails
        
        if not recipients:
            logger.warning("No recipients specified for alert")
            return False
        
        try:
            # Create email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[DentaFlow Alert] {subject}"
            msg["From"] = self.from_email
            msg["To"] = ", ".join(recipients)
            
            # Create HTML body
            html_body = self._create_html_body(alert_type, subject, message, data)
            msg.attach(MIMEText(html_body, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Alert sent successfully: {alert_type} to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False
    
    def _create_html_body(
        self,
        alert_type: AlertType,
        subject: str,
        message: str,
        data: Optional[Dict] = None
    ) -> str:
        """Create HTML email body."""
        # Color coding by alert type
        colors = {
            AlertType.PAYMENT_FAILED: "#dc2626",  # Red
            AlertType.SUBSCRIPTION_CANCELED: "#ea580c",  # Orange
            AlertType.TRIAL_ENDING: "#f59e0b",  # Amber
            AlertType.HIGH_USAGE: "#3b82f6",  # Blue
            AlertType.HIGH_COST: "#dc2626",  # Red
            AlertType.SYSTEM_ERROR: "#dc2626",  # Red
            AlertType.NEW_SIGNUP: "#10b981",  # Green
            AlertType.CHURN_RISK: "#f59e0b",  # Amber
        }
        
        color = colors.get(alert_type, "#6b7280")
        
        # Build data table if provided
        data_html = ""
        if data:
            data_rows = "".join([
                f"<tr><td style='padding: 8px; border: 1px solid #e5e7eb;'><strong>{key}:</strong></td>"
                f"<td style='padding: 8px; border: 1px solid #e5e7eb;'>{value}</td></tr>"
                for key, value in data.items()
            ])
            data_html = f"""
            <h3 style='color: #374151; margin-top: 20px;'>Details:</h3>
            <table style='width: 100%; border-collapse: collapse; margin-top: 10px;'>
                {data_rows}
            </table>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 0; background-color: #f3f4f6;'>
            <div style='max-width: 600px; margin: 40px auto; background-color: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;'>
                <!-- Header -->
                <div style='background-color: {color}; padding: 20px; text-align: center;'>
                    <h1 style='color: white; margin: 0; font-size: 24px;'>DentaFlow Alert</h1>
                    <p style='color: rgba(255, 255, 255, 0.9); margin: 5px 0 0 0; font-size: 14px;'>{alert_type.value.replace("_", " ").title()}</p>
                </div>
                
                <!-- Body -->
                <div style='padding: 30px;'>
                    <h2 style='color: #111827; margin-top: 0;'>{subject}</h2>
                    <div style='color: #374151; line-height: 1.6; margin-top: 15px;'>
                        {message}
                    </div>
                    {data_html}
                </div>
                
                <!-- Footer -->
                <div style='background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;'>
                    <p style='color: #6b7280; margin: 0; font-size: 12px;'>
                        Sent at {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
                    </p>
                    <p style='color: #6b7280; margin: 5px 0 0 0; font-size: 12px;'>
                        <a href='https://dentaflow.ai/super-admin/dashboard' style='color: #3b82f6; text-decoration: none;'>
                            View Super Admin Dashboard
                        </a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    # Convenience methods for common alerts
    
    def alert_payment_failed(
        self,
        organization_name: str,
        amount: float,
        error_message: str
    ) -> bool:
        """Alert when a payment fails."""
        return self.send_alert(
            alert_type=AlertType.PAYMENT_FAILED,
            subject=f"Payment Failed: {organization_name}",
            message=f"A payment of ${amount:.2f} has failed for {organization_name}.",
            data={
                "Organization": organization_name,
                "Amount": f"${amount:.2f}",
                "Error": error_message,
                "Action Required": "Contact the organization to update payment method"
            }
        )
    
    def alert_subscription_canceled(
        self,
        organization_name: str,
        plan_tier: str,
        mrr_impact: float
    ) -> bool:
        """Alert when a subscription is canceled."""
        return self.send_alert(
            alert_type=AlertType.SUBSCRIPTION_CANCELED,
            subject=f"Subscription Canceled: {organization_name}",
            message=f"{organization_name} has canceled their {plan_tier} subscription.",
            data={
                "Organization": organization_name,
                "Plan": plan_tier,
                "MRR Impact": f"-${mrr_impact:.2f}",
                "Action Required": "Schedule exit interview to understand reasons"
            }
        )
    
    def alert_trial_ending(
        self,
        organization_name: str,
        days_remaining: int
    ) -> bool:
        """Alert when a trial is ending soon."""
        return self.send_alert(
            alert_type=AlertType.TRIAL_ENDING,
            subject=f"Trial Ending Soon: {organization_name}",
            message=f"{organization_name}'s trial ends in {days_remaining} days.",
            data={
                "Organization": organization_name,
                "Days Remaining": days_remaining,
                "Action Required": "Reach out to convert to paid plan"
            }
        )
    
    def alert_high_usage(
        self,
        organization_name: str,
        metric_type: str,
        current_value: int,
        threshold: int
    ) -> bool:
        """Alert when usage exceeds threshold."""
        return self.send_alert(
            alert_type=AlertType.HIGH_USAGE,
            subject=f"High Usage Alert: {organization_name}",
            message=f"{organization_name} has exceeded the usage threshold for {metric_type}.",
            data={
                "Organization": organization_name,
                "Metric": metric_type,
                "Current Value": current_value,
                "Threshold": threshold,
                "Percentage": f"{(current_value / threshold * 100):.1f}%"
            }
        )
    
    def alert_high_cost(
        self,
        service_name: str,
        current_cost: float,
        previous_cost: float,
        increase_percentage: float
    ) -> bool:
        """Alert when costs increase significantly."""
        return self.send_alert(
            alert_type=AlertType.HIGH_COST,
            subject=f"High Cost Alert: {service_name}",
            message=f"Cost for {service_name} has increased by {increase_percentage:.1f}%.",
            data={
                "Service": service_name,
                "Current Cost": f"${current_cost:.2f}",
                "Previous Cost": f"${previous_cost:.2f}",
                "Increase": f"+{increase_percentage:.1f}%",
                "Action Required": "Investigate cost spike and optimize if needed"
            }
        )
    
    def alert_new_signup(
        self,
        organization_name: str,
        plan_tier: str,
        trial_days: int
    ) -> bool:
        """Alert when a new organization signs up."""
        return self.send_alert(
            alert_type=AlertType.NEW_SIGNUP,
            subject=f"New Signup: {organization_name}",
            message=f"{organization_name} has signed up for a {trial_days}-day trial of the {plan_tier} plan.",
            data={
                "Organization": organization_name,
                "Plan": plan_tier,
                "Trial Duration": f"{trial_days} days",
                "Action Required": "Send welcome email and schedule onboarding call"
            }
        )
    
    def alert_churn_risk(
        self,
        organization_name: str,
        risk_score: float,
        reasons: List[str]
    ) -> bool:
        """Alert when an organization is at risk of churning."""
        reasons_html = "<ul>" + "".join([f"<li>{reason}</li>" for reason in reasons]) + "</ul>"
        
        return self.send_alert(
            alert_type=AlertType.CHURN_RISK,
            subject=f"Churn Risk Alert: {organization_name}",
            message=f"{organization_name} is at risk of churning (risk score: {risk_score:.0f}%). "
                   f"<br><br><strong>Risk Factors:</strong>{reasons_html}",
            data={
                "Organization": organization_name,
                "Risk Score": f"{risk_score:.0f}%",
                "Action Required": "Reach out proactively to address concerns"
            }
        )


# Singleton instance
_alert_service = None


def get_alert_service() -> AlertService:
    """Get or create Alert service instance."""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service

