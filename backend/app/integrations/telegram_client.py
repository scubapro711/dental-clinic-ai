"""
Telegram Bot Client

Handles communication with Telegram Bot API.
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramClient:
    """Client for Telegram Bot API."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """
        Initialize Telegram client.
        
        Args:
            bot_token: Telegram bot token (defaults to settings)
        """
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a text message to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Text formatting mode (Markdown or HTML)
            reply_markup: Optional inline keyboard or reply markup
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Message sent to chat {chat_id}")
            return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to send message to chat {chat_id}: {e}")
            raise
    
    async def send_photo(
        self,
        chat_id: int,
        photo: str,
        caption: Optional[str] = None,
        parse_mode: str = "Markdown",
    ) -> Dict[str, Any]:
        """
        Send a photo to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            photo: Photo file_id or URL
            caption: Optional photo caption
            parse_mode: Text formatting mode
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.base_url}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo,
            "parse_mode": parse_mode,
        }
        
        if caption:
            payload["caption"] = caption
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Photo sent to chat {chat_id}")
            return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to send photo to chat {chat_id}: {e}")
            raise
    
    async def send_location(
        self,
        chat_id: int,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        Send a location to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.base_url}/sendLocation"
        payload = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Location sent to chat {chat_id}")
            return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to send location to chat {chat_id}: {e}")
            raise
    
    async def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """
        Set the webhook URL for receiving updates.
        
        Args:
            webhook_url: HTTPS URL for webhook
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.base_url}/setWebhook"
        payload = {"url": webhook_url}
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Webhook set to {webhook_url}")
            return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to set webhook: {e}")
            raise
    
    async def get_webhook_info(self) -> Dict[str, Any]:
        """
        Get current webhook status.
        
        Returns:
            Webhook information
        """
        url = f"{self.base_url}/getWebhookInfo"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            result = response.json()
            return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to get webhook info: {e}")
            raise
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """
        Remove the webhook.
        
        Returns:
            Response from Telegram API
        """
        url = f"{self.base_url}/deleteWebhook"
        
        try:
            response = await self.client.post(url)
            response.raise_for_status()
            result = response.json()
            logger.info("Webhook deleted")
            return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete webhook: {e}")
            raise
    
    def create_inline_keyboard(
        self,
        buttons: List[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        """
        Create an inline keyboard markup.
        
        Args:
            buttons: 2D array of button objects
                Each button: {"text": "Button Text", "callback_data": "action"}
                
        Returns:
            Inline keyboard markup
        """
        return {
            "inline_keyboard": buttons
        }
    
    def create_quick_reply_buttons(self) -> Dict[str, Any]:
        """
        Create quick reply buttons for common actions.
        
        Returns:
            Inline keyboard with quick reply buttons
        """
        buttons = [
            [
                {"text": "📅 Book Appointment", "callback_data": "book_appointment"},
                {"text": "💰 Check Invoice", "callback_data": "check_invoice"},
            ],
            [
                {"text": "👨‍⚕️ Talk to Doctor", "callback_data": "talk_to_doctor"},
                {"text": "📍 Clinic Location", "callback_data": "clinic_location"},
            ],
        ]
        return self.create_inline_keyboard(buttons)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Create singleton instance
telegram_client = TelegramClient()
