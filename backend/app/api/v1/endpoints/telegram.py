"""
Telegram Bot Webhook Endpoint

Handles incoming messages from Telegram and routes them to Alex agent.
"""

import logging
import re
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from uuid import uuid4

from app.integrations.telegram_client import telegram_client
from app.agents.agent_graph_v5 import AgentGraphV5
from app.agents.telegram_onboarding import TelegramOnboarding
from app.core.config import settings
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.telegram_user import TelegramUser
from app.models.telegram_conversation import TelegramConversation
from app.services.telegram_buttons import TelegramButtons, ButtonCallbackHandler

# Initialize Multi-Agent Graph (V4 with 4 Agents: Alex, שרה, Marcus, Sophia)
agent_graph = AgentGraphV5()

logger = logging.getLogger(__name__)

router = APIRouter()


def _filter_system_context(message: str) -> str:
    """
    Remove SYSTEM CONTEXT from message before sending to user.
    
    Args:
        message: The message that may contain SYSTEM CONTEXT
        
    Returns:
        Cleaned message without SYSTEM CONTEXT
    """
    # Remove everything between SYSTEM CONTEXT markers
    pattern = r'SYSTEM CONTEXT.*?END SYSTEM CONTEXT\s*'
    cleaned = re.sub(pattern, '', message, flags=re.DOTALL | re.IGNORECASE)
    
    # Also remove any standalone markers that might remain
    cleaned = re.sub(r'SYSTEM CONTEXT.*?$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    cleaned = re.sub(r'END SYSTEM CONTEXT.*?$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Max 2 newlines
    
    return cleaned.strip()


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
        from app.services.telegram_service import TelegramService
        from app.agents.telegram_onboarding import TelegramOnboarding, OnboardingState
        from app.core.database import SessionLocal
        
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username", "unknown")
        first_name = message["from"].get("first_name")
        last_name = message["from"].get("last_name")
        text = message.get("text", "")
        
        logger.info(f"Processing message from user {username} (chat {chat_id}): {text}")
        
        # Create DB session
        db = SessionLocal()
        try:
            telegram_service = TelegramService(db)
            
            # Get or create Telegram user
            telegram_user = telegram_service.get_or_create_user(
                telegram_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            
            # Handle /start command - always restart onboarding
            if text == "/start":
                # Create new onboarding session
                onboarding = TelegramOnboarding()
                response = onboarding.process_message(text, {"telegram_user": telegram_user})
                
                # Store onboarding state in conversation store
                conversation_store[chat_id] = {
                    "onboarding": onboarding,
                    "telegram_user_id": telegram_user.id,
                }
                
                # Add welcome buttons
                buttons = TelegramButtons.welcome_buttons()
                
                await telegram_client.send_message(
                    chat_id=chat_id,
                    text=response["response"],
                    reply_markup=buttons,
                )
                return
            
            # Handle /help command
            if text == "/help":
                await send_help_message(chat_id)
                return
            
            # Check if user is in onboarding
            session_data = conversation_store.get(chat_id)
            if session_data and "onboarding" in session_data:
                onboarding = session_data["onboarding"]
                
                # Check if onboarding is complete
                if onboarding.state == OnboardingState.COMPLETE:
                    # Remove onboarding from session
                    del session_data["onboarding"]
                    # Continue to normal flow below
                else:
                    # Continue onboarding
                    context = {"telegram_user": telegram_user}
                    
                    # Handle actions from previous state
                    if onboarding.state == OnboardingState.CHECKING_PATIENT:
                        # Search for patient
                        phone = onboarding.data.get("phone")
                        if phone and telegram_user.organization_id:
                            patients = telegram_service.odoo_client.search_patients(
                                organization_id=telegram_user.organization_id,
                                phone=phone
                            )
                            context["patient_found"] = len(patients) > 0
                            context["patient_data"] = patients[0] if patients else None
                    
                    # Process message
                    response = onboarding.process_message(text, context)
                    
                    # Handle actions
                    action = response.get("action")
                    if action == "validate_invite_code":
                        code = onboarding.data.get("invite_code")
                        invite = telegram_service.validate_invite_code(code, telegram_user)
                        if not invite:
                            response["response"] = (
                                "הקוד לא תקף או שפג תוקפו 😔\n\n"
                                "בדוק את הקוד ונסה שוב, או פנה למרפאה לקבלת קוד חדש."
                            )
                            onboarding.state = OnboardingState.NEED_INVITE_CODE
                        else:
                            onboarding.organization_id = invite.organization_id
                    
                    elif action == "link_patient":
                        patient_id = onboarding.data.get("patient_id")
                        if patient_id:
                            telegram_user.patient_id = patient_id
                            telegram_user.status = "linked"
                            db.commit()
                    
                    elif action == "create_patient":
                        patient_data = {
                            "name": onboarding.data.get("name"),
                            "phone": onboarding.data.get("phone"),
                            "email": onboarding.data.get("email"),
                            "birth_date": onboarding.data.get("birth_date"),
                        }
                        success = telegram_service.create_patient_and_link(
                            telegram_user=telegram_user,
                            patient_data=patient_data,
                            organization_id=onboarding.organization_id or telegram_user.organization_id,
                        )
                        if not success:
                            response["response"] = (
                                "אופס! משהו השתבש ביצירת הפרופיל 😔\n\n"
                                "נסה שוב מאוחר יותר או פנה למרפאה."
                            )
                            response["complete"] = False
                    
                    # Send response
                    await telegram_client.send_message(
                        chat_id=chat_id,
                        text=response["response"],
                    )
                    
                    # If complete, remove onboarding
                    if response.get("complete"):
                        del session_data["onboarding"]
                    
                    return
            
            # Normal conversation flow (user is linked)
            
            # Check if user is linked to a patient
            if not telegram_user.patient_id:
                # Automatically start onboarding for unlinked users
                onboarding = TelegramOnboarding()
                response = onboarding.process_message("/start", {"telegram_user": telegram_user})
                
                # Store onboarding state in conversation store
                conversation_store[chat_id] = {
                    "onboarding": onboarding,
                    "telegram_user_id": telegram_user.id,
                }
                
                await telegram_client.send_message(
                    chat_id=chat_id,
                    text=response["response"],
                )
                return
            
            # Get or create conversation
            conversation = telegram_service.get_or_create_conversation(
                telegram_user=telegram_user,
                chat_id=chat_id,
            )
            
            # Send typing indicator
            await telegram_client.client.post(
                f"{telegram_client.base_url}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"}
            )
            
            # Route to Alex agent via AgentGraphV5
            response = await agent_graph.process_message(
                user_id=str(telegram_user.patient_id),
                organization_id=telegram_user.organization_id,
                conversation_id=str(conversation.id),
                message=text,
            )
            
            # Format response for Telegram
            response_text = response.get("response", "")
            
            # ✅ CRITICAL: Filter SYSTEM CONTEXT from response
            response_text = _filter_system_context(response_text)
            
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
            
        finally:
            db.close()
    
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
        username = callback_query["from"].get("username", "callback_user")
        callback_data = callback_query["data"]
        
        logger.info(f"Processing callback from user {user_id}: {callback_data}")
        
        # Answer callback query (removes loading state)
        await telegram_client.client.post(
            f"{telegram_client.base_url}/answerCallbackQuery",
            json={"callback_query_id": query_id}
        )
        
        # Parse callback data
        parsed = ButtonCallbackHandler.parse_callback_data(callback_data)
        action = parsed["action"]
        params = parsed["params"]
        
        # Convert action to natural language message
        message_text = ButtonCallbackHandler.get_action_message(action, params)
        
        # Process as regular message
        await handle_message({
            "chat": {"id": chat_id},
            "from": {"id": user_id, "username": username},
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
