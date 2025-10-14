"""
Simplified Telegram Bot Webhook - Routes everything to Alex

This version removes the rigid onboarding flow and lets Alex handle everything.
"""

import logging
import re
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks

from app.integrations.telegram_client import telegram_client
from app.agents.agent_graph_v4 import AgentGraphV4
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.telegram_user import TelegramUser
from app.models.telegram_conversation import TelegramConversation

# Initialize Multi-Agent Graph
agent_graph = AgentGraphV4()

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receive updates from Telegram webhook and route to Alex.
    
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
    Handle incoming Telegram message - route everything to Alex.
    
    Args:
        message: Telegram message object
    """
    try:
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username", "unknown")
        first_name = message["from"].get("first_name", "")
        last_name = message["from"].get("last_name", "")
        text = message.get("text", "")
        
        logger.info(f"Processing message from user {username} (chat {chat_id}): {text}")
        
        # Create DB session
        db = SessionLocal()
        try:
            # Get or create Telegram user
            telegram_user = db.query(TelegramUser).filter(
                TelegramUser.telegram_user_id == user_id
            ).first()
            
            if not telegram_user:
                # Create new user
                telegram_user = TelegramUser(
                    telegram_user_id=user_id,
                    telegram_username=username,
                    telegram_first_name=first_name,
                    telegram_last_name=last_name,
                    is_active=True,
                    language='he',
                )
                db.add(telegram_user)
                db.commit()
                db.refresh(telegram_user)
                logger.info(f"Created new Telegram user: {user_id}")
            
            # Get or create conversation
            conversation = db.query(TelegramConversation).filter(
                TelegramConversation.telegram_user_id == telegram_user.id,
                TelegramConversation.chat_id == chat_id,
                TelegramConversation.is_active == True,
            ).first()
            
            if not conversation:
                conversation = TelegramConversation(
                    telegram_user_id=telegram_user.id,
                    organization_id=telegram_user.organization_id,
                    chat_id=chat_id,
                    is_active=True,
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                logger.info(f"Created new conversation for user {user_id}")
            
            # Send typing indicator
            await telegram_client.client.post(
                f"{telegram_client.base_url}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"}
            )
            
            # Build context for Alex
            user_context = {
                "telegram_user_id": telegram_user.telegram_user_id,
                "telegram_username": telegram_user.telegram_username,
                "first_name": telegram_user.telegram_first_name,
                "last_name": telegram_user.telegram_last_name,
                "has_organization": telegram_user.organization_id is not None,
                "has_patient_link": telegram_user.patient_id is not None,
                "language": telegram_user.language,
            }
            
            # Add context to the message for Alex
            # Format context for Alex
            if telegram_user.patient_id is None:
                patient_status = "⚠️ NEW USER - NOT REGISTERED"
            else:
                patient_status = f"✅ REGISTERED PATIENT (ID: {telegram_user.patient_id})"
            
            enhanced_message = f"""[SYSTEM CONTEXT - DO NOT SHOW TO USER]
User Status: {patient_status}
Telegram Name: {telegram_user.telegram_first_name} {telegram_user.telegram_last_name or ''}
Has Organization: {telegram_user.organization_id is not None}
Language: {telegram_user.language}
[END SYSTEM CONTEXT]

User Message: {text}"""
            
            # Route to Alex via AgentGraphV4
            # Use telegram_user_id as the user_id for now
            response = agent_graph.invoke(
                message=enhanced_message,
                organization_id=str(telegram_user.organization_id) if telegram_user.organization_id else "default",
                thread_id=str(conversation.id),
            )
            
            # Format response for Telegram
            logger.info(f"Alex response: {response}")
            response_text = response.get("output", "")
            
            # Remove SYSTEM CONTEXT if Alex accidentally included it in the response
            response_text = re.sub(r'\[?SYSTEM CONTEXT.*?\[?END SYSTEM CONTEXT\]?\s*', '', response_text, flags=re.DOTALL | re.IGNORECASE)
            response_text = re.sub(r'User Message:.*?\n', '', response_text, count=1)
            response_text = response_text.strip()
            
            logger.info(f"Response text length: {len(response_text)}, preview: {response_text[:200] if response_text else 'EMPTY'}")
            
            # Add escalation notice if needed
            if response.get("escalation_level") == "EMERGENCY":
                response_text = f"🚨 *התראת חירום*\n\n{response_text}"
            elif response.get("escalation_level") == "DOCTOR_REQUIRED":
                response_text = f"⚠️ *נדרש רופא*\n\n{response_text}"
            
            # Send response
            await telegram_client.send_message(
                chat_id=chat_id,
                text=response_text,
                parse_mode="Markdown",
            )
            
            logger.info(f"Response sent to chat {chat_id}")
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        # Send error message to user
        try:
            await telegram_client.send_message(
                chat_id=chat_id,
                text="מצטער, נתקלתי בשגיאה. אנא נסה שוב.",
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
        
        # Convert callback to message and process
        message_text = f"[Button: {callback_data}]"
        
        await handle_message({
            "chat": {"id": chat_id},
            "from": {"id": user_id, "username": "callback_user"},
            "text": message_text,
        })
    
    except Exception as e:
        logger.error(f"Error handling callback: {e}")


@router.get("/webhook-info")
async def get_webhook_info():
    """Get current webhook status."""
    try:
        info = await telegram_client.get_webhook_info()
        return info
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-webhook")
async def set_webhook(webhook_url: str):
    """Set webhook URL for Telegram bot."""
    try:
        result = await telegram_client.set_webhook(webhook_url)
        return result
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

