"""
Telegram Bot Webhook Endpoint

Handles incoming messages from Telegram and routes them to Alex agent.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from uuid import uuid4

from app.integrations.telegram_client import telegram_client
from app.agents.agent_graph import agent_graph_v2
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# Store conversation context per Telegram chat
conversation_store: Dict[int, str] = {}


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receive updates from Telegram webhook.
    
    Args:
        request: FastAPI request object
        background_tasks: FastAPI background tasks
        
    Returns:
        Success response
    """
    try:
        # Parse webhook payload
        update = await request.json()
        logger.info(f"Received Telegram update: {update.get('update_id')}")
        
        # Extract message
        message = update.get("message")
        callback_query = update.get("callback_query")
        
        if message:
            # Handle regular message
            background_tasks.add_task(handle_message, message)
        elif callback_query:
            # Handle button callback
            background_tasks.add_task(handle_callback, callback_query)
        
        return {"ok": True}
    
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_message(message: Dict[str, Any]):
    """
    Handle incoming Telegram message.
    
    Args:
        message: Telegram message object
    """
    try:
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username", "unknown")
        text = message.get("text", "")
        
        logger.info(f"Processing message from user {username} (chat {chat_id}): {text}")
        
        # Handle /start command
        if text == "/start":
            await send_welcome_message(chat_id)
            return
        
        # Handle /help command
        if text == "/help":
            await send_help_message(chat_id)
            return
        
        # Get or create conversation ID
        conversation_id = conversation_store.get(chat_id)
        if not conversation_id:
            conversation_id = str(uuid4())
            conversation_store[chat_id] = conversation_id
        
        # Send typing indicator
        await telegram_client.client.post(
            f"{telegram_client.base_url}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"}
        )
        
        # Route to Alex agent
        response = await agent_graph_v2.process_message(
            user_id=str(user_id),
            organization_id="telegram",  # Default org for Telegram users
            conversation_id=conversation_id,
            message=text,
        )
        
        # Format response for Telegram
        response_text = response["response"]
        
        # Add escalation notice if needed
        if response.get("escalation_level") == "EMERGENCY":
            response_text = f"🚨 *EMERGENCY ALERT*\n\n{response_text}"
        elif response.get("escalation_level") == "DOCTOR_REQUIRED":
            response_text = f"⚠️ *Doctor Required*\n\n{response_text}"
        
        # Create quick reply buttons based on context
        reply_markup = None
        if not response.get("requires_human"):
            # Show quick action buttons for non-escalated conversations
            reply_markup = telegram_client.create_quick_reply_buttons()
        
        # Send response
        await telegram_client.send_message(
            chat_id=chat_id,
            text=response_text,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
        
        logger.info(f"Response sent to chat {chat_id}")
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        # Send error message to user
        try:
            await telegram_client.send_message(
                chat_id=chat_id,
                text="Sorry, I encountered an error processing your message. Please try again.",
            )
        except:
            pass


async def handle_callback(callback_query: Dict[str, Any]):
    """
    Handle button callback from Telegram.
    
    Args:
        callback_query: Telegram callback query object
    """
    try:
        query_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        user_id = callback_query["from"]["id"]
        callback_data = callback_query["data"]
        
        logger.info(f"Processing callback from user {user_id}: {callback_data}")
        
        # Answer callback query (removes loading state)
        await telegram_client.client.post(
            f"{telegram_client.base_url}/answerCallbackQuery",
            json={"callback_query_id": query_id}
        )
        
        # Handle different callback actions
        if callback_data == "book_appointment":
            message_text = "I want to book an appointment"
        elif callback_data == "check_invoice":
            message_text = "Show me my invoices"
        elif callback_data == "talk_to_doctor":
            message_text = "I need to talk to a doctor"
        elif callback_data == "clinic_location":
            # Send clinic location
            await send_clinic_location(chat_id)
            return
        else:
            message_text = callback_data
        
        # Process as regular message
        await handle_message({
            "chat": {"id": chat_id},
            "from": {"id": user_id, "username": "callback_user"},
            "text": message_text,
        })
    
    except Exception as e:
        logger.error(f"Error handling callback: {e}")


async def send_welcome_message(chat_id: int):
    """
    Send welcome message to new user.
    
    Args:
        chat_id: Telegram chat ID
    """
    welcome_text = """
👋 *Welcome to Dental Clinic AI Assistant!*

I'm Alex, your AI dental assistant. I can help you with:

📅 *Appointment Scheduling* - Book, reschedule, or cancel appointments
💰 *Billing Questions* - Check invoices and payment status
📍 *Clinic Information* - Hours, location, services
👨‍⚕️ *Doctor Consultation* - Connect you with Dr. Smith when needed

I speak both English and Hebrew - just talk to me naturally! 😊

*Important:* I'm an AI assistant, not a dentist. For medical advice, I'll connect you with Dr. Smith.

How can I help you today?
"""
    
    reply_markup = telegram_client.create_quick_reply_buttons()
    
    await telegram_client.send_message(
        chat_id=chat_id,
        text=welcome_text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def send_help_message(chat_id: int):
    """
    Send help message.
    
    Args:
        chat_id: Telegram chat ID
    """
    help_text = """
🆘 *How to Use This Bot*

*Quick Actions:*
Use the buttons below to quickly:
• 📅 Book an appointment
• 💰 Check your invoices
• 👨‍⚕️ Talk to a doctor
• 📍 Get clinic location

*Natural Conversation:*
Just type your question naturally! For example:
• "I have a toothache"
• "What are your hours?"
• "How much does a cleaning cost?"
• "יש לי כאב שיניים" (Hebrew works too!)

*Medical Safety:*
⚠️ I can't diagnose or prescribe medication. For medical questions, I'll connect you with Dr. Smith immediately.

*Emergency:*
🚨 If you have severe pain, swelling, or bleeding, I'll escalate to Dr. Smith right away!

Need anything else? Just ask!
"""
    
    await telegram_client.send_message(
        chat_id=chat_id,
        text=help_text,
        parse_mode="Markdown",
    )


async def send_clinic_location(chat_id: int):
    """
    Send clinic location.
    
    Args:
        chat_id: Telegram chat ID
    """
    # Dental clinic location (example coordinates - Tel Aviv)
    latitude = 32.0853
    longitude = 34.7818
    
    await telegram_client.send_location(
        chat_id=chat_id,
        latitude=latitude,
        longitude=longitude,
    )
    
    # Send additional info
    location_text = """
📍 *Dental Clinic Location*

123 Dizengoff Street
Tel Aviv, Israel

*Hours:*
Sunday - Thursday: 8:00 AM - 7:00 PM
Friday: 8:00 AM - 2:00 PM
Saturday: Closed

*Phone:* +972-3-123-4567
"""
    
    await telegram_client.send_message(
        chat_id=chat_id,
        text=location_text,
        parse_mode="Markdown",
    )


@router.get("/webhook-info")
async def get_webhook_info():
    """
    Get current webhook status.
    
    Returns:
        Webhook information
    """
    try:
        info = await telegram_client.get_webhook_info()
        return info
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-webhook")
async def set_webhook(webhook_url: str):
    """
    Set webhook URL for Telegram bot.
    
    Args:
        webhook_url: HTTPS URL for webhook
        
    Returns:
        Success response
    """
    try:
        result = await telegram_client.set_webhook(webhook_url)
        return result
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
