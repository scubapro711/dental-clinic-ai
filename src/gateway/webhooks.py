"""
Webhook handlers for WhatsApp and Telegram
מטפלי webhook עבור WhatsApp ו-Telegram
"""

import json
import logging
from typing import Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def whatsapp_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle WhatsApp webhook data
    
    Args:
        data: WhatsApp webhook payload
        
    Returns:
        Dict with processing result
    """
    try:
        # Extract message from WhatsApp webhook format
        if "entry" not in data:
            raise HTTPException(status_code=400, detail="Invalid WhatsApp webhook format")
        
        for entry in data["entry"]:
            if "changes" in entry:
                for change in entry["changes"]:
                    if "value" in change and "messages" in change["value"]:
                        for message in change["value"]["messages"]:
                            # Extract message details
                            message_id = message.get("id", "")
                            sender = message.get("from", "")
                            text = message.get("text", {}).get("body", "")
                            timestamp = message.get("timestamp", "")
                            
                            logger.info(f"WhatsApp message from {sender}: {text}")
                            
                            # Here you would typically:
                            # 1. Validate the message
                            # 2. Add to processing queue
                            # 3. Return acknowledgment
                            
                            return {
                                "status": "received",
                                "message_id": message_id,
                                "sender": sender,
                                "text": text,
                                "timestamp": timestamp
                            }
        
        return {"status": "no_messages", "message": "No messages found in webhook"}
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"WhatsApp webhook processing failed: {str(e)}")

async def telegram_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Telegram webhook data
    
    Args:
        data: Telegram webhook payload
        
    Returns:
        Dict with processing result
    """
    try:
        # Extract message from Telegram webhook format
        if "message" not in data:
            raise HTTPException(status_code=400, detail="Invalid Telegram webhook format")
        
        message = data["message"]
        
        # Extract message details
        message_id = message.get("message_id", "")
        sender_id = message.get("from", {}).get("id", "")
        sender_name = message.get("from", {}).get("first_name", "")
        chat_id = message.get("chat", {}).get("id", "")
        text = message.get("text", "")
        date = message.get("date", "")
        
        logger.info(f"Telegram message from {sender_name} ({sender_id}): {text}")
        
        # Here you would typically:
        # 1. Validate the message
        # 2. Add to processing queue
        # 3. Return acknowledgment
        
        return {
            "status": "received",
            "message_id": message_id,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "chat_id": chat_id,
            "text": text,
            "date": date
        }
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Telegram webhook processing failed: {str(e)}")
