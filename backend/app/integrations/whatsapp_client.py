"""
WhatsApp Business API Client.

Integrates with WhatsApp Business API (Cloud API) for sending and receiving messages.

Requirements:
- Meta Business Account
- WhatsApp Business Account
- Phone Number ID
- Access Token
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    Client for WhatsApp Business Cloud API.
    
    Documentation: https://developers.facebook.com/docs/whatsapp/cloud-api
    """
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        phone_number_id: Optional[str] = None
    ):
        """
        Initialize WhatsApp client.
        
        Args:
            access_token: WhatsApp Business API access token
            phone_number_id: WhatsApp Business phone number ID
        """
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )
    
    async def send_text_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """
        Send text message.
        
        Args:
            to: Recipient phone number (with country code, e.g., "972501234567")
            text: Message text
            preview_url: Enable URL preview
        
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text
            }
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Sent WhatsApp message to {to}")
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "he",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send template message.
        
        Templates must be pre-approved by Meta.
        
        Args:
            to: Recipient phone number
            template_name: Template name
            language_code: Language code (default: "he" for Hebrew)
            components: Template components (parameters, buttons, etc.)
        
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Sent WhatsApp template '{template_name}' to {to}")
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to send WhatsApp template: {e}")
            raise
    
    async def send_interactive_message(
        self,
        to: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send interactive message with buttons.
        
        Args:
            to: Recipient phone number
            body_text: Message body text
            buttons: List of buttons (max 3)
            header_text: Optional header text
            footer_text: Optional footer text
        
        Returns:
            API response
        """
        if len(buttons) > 3:
            raise ValueError("Maximum 3 buttons allowed")
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        # Build interactive message
        interactive = {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": btn["id"],
                            "title": btn["title"]
                        }
                    }
                    for btn in buttons
                ]
            }
        }
        
        if header_text:
            interactive["header"] = {"type": "text", "text": header_text}
        
        if footer_text:
            interactive["footer"] = {"text": footer_text}
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": interactive
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Sent WhatsApp interactive message to {to}")
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to send WhatsApp interactive message: {e}")
            raise
    
    async def send_list_message(
        self,
        to: str,
        body_text: str,
        button_text: str,
        sections: List[Dict[str, Any]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send list message with multiple options.
        
        Args:
            to: Recipient phone number
            body_text: Message body text
            button_text: Button text (e.g., "בחר אפשרות")
            sections: List sections with rows
            header_text: Optional header text
            footer_text: Optional footer text
        
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        interactive = {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
        
        if header_text:
            interactive["header"] = {"type": "text", "text": header_text}
        
        if footer_text:
            interactive["footer"] = {"text": footer_text}
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": interactive
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Sent WhatsApp list message to {to}")
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to send WhatsApp list message: {e}")
            raise
    
    async def send_media_message(
        self,
        to: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send media message (image, video, document, audio).
        
        Args:
            to: Recipient phone number
            media_type: Media type ("image", "video", "document", "audio")
            media_url: Public URL of media file
            caption: Optional caption
        
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": media_type,
            media_type: {
                "link": media_url
            }
        }
        
        if caption and media_type in ["image", "video", "document"]:
            payload[media_type]["caption"] = caption
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Sent WhatsApp {media_type} to {to}")
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to send WhatsApp media: {e}")
            raise
    
    async def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark message as read.
        
        Args:
            message_id: WhatsApp message ID
        
        Returns:
            API response
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"Marked WhatsApp message {message_id} as read")
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to mark message as read: {e}")
            raise
    
    async def get_media_url(self, media_id: str) -> str:
        """
        Get media URL from media ID.
        
        Args:
            media_id: WhatsApp media ID
        
        Returns:
            Media URL
        """
        url = f"{self.base_url}/{media_id}"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            result = response.json()
            
            media_url = result.get("url")
            logger.debug(f"Retrieved media URL for {media_id}")
            
            return media_url
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to get media URL: {e}")
            raise
    
    async def download_media(self, media_url: str) -> bytes:
        """
        Download media from URL.
        
        Args:
            media_url: Media URL from get_media_url()
        
        Returns:
            Media bytes
        """
        try:
            response = await self.client.get(media_url)
            response.raise_for_status()
            
            logger.debug(f"Downloaded media from {media_url}")
            return response.content
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to download media: {e}")
            raise
    
    def verify_webhook(
        self,
        mode: str,
        token: str,
        challenge: str,
        verify_token: str
    ) -> Optional[str]:
        """
        Verify webhook subscription.
        
        Args:
            mode: Verification mode
            token: Verification token from request
            challenge: Challenge string from request
            verify_token: Your verify token (from settings)
        
        Returns:
            Challenge string if verification succeeds, None otherwise
        """
        if mode == "subscribe" and token == verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        else:
            logger.warning("WhatsApp webhook verification failed")
            return None
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global instance
whatsapp_client = WhatsAppClient()
