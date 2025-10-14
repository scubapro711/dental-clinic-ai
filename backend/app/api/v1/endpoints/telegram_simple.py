"""
Fixed version of telegram_simple.py with SYSTEM CONTEXT filtering
Replace: backend/app/api/v1/endpoints/telegram_simple.py
"""

from fastapi import APIRouter, HTTPException, Request
from app.integrations.telegram_client import TelegramClient
from app.agents.agent_graph_v4 import AgentGraphV4
from app.core.config import settings
from app.models.telegram_user import TelegramUser
from app.models.telegram_conversation import TelegramConversation
from app.core.database import get_db
from sqlalchemy.orm import Session
import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

telegram_client = TelegramClient(settings.TELEGRAM_BOT_TOKEN)


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


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram webhook updates.
    Routes all messages to Alex (AgentGraphV4).
    """
    try:
        logger.info("=== WEBHOOK CALLED ===")
        # Parse webhook payload
        data = await request.json()
        logger.info(f"Received Telegram update: {data.get('update_id')}")
        logger.info(f"Full data: {data}")
        
        # Extract message
        message = data.get("message")
        logger.info(f"Message extracted: {message is not None}")
        if not message:
            logger.warning("No message in update - RETURNING EARLY")
            return {"ok": True}
        
        # Extract user and chat info
        from_user = message.get("from", {})
        chat = message.get("chat", {})
        text = message.get("text", "")
        
        telegram_user_id = from_user.get("id")
        telegram_username = from_user.get("username", "")
        first_name = from_user.get("first_name", "")
        last_name = from_user.get("last_name", "")
        chat_id = chat.get("id")
        
        if not telegram_user_id or not text:
            logger.warning(f"Missing user_id or text - user_id={telegram_user_id}, text={text} - RETURNING EARLY")
            return {"ok": True}
        
        # Get or create Telegram user in database
        db: Session = next(get_db())
        try:
            telegram_user = db.query(TelegramUser).filter(
                TelegramUser.telegram_user_id == telegram_user_id
            ).first()
            
            if not telegram_user:
                telegram_user = TelegramUser(
                    telegram_user_id=telegram_user_id,
                    telegram_username=telegram_username,
                    first_name=first_name,
                    last_name=last_name
                )
                db.add(telegram_user)
                db.commit()
                db.refresh(telegram_user)
                logger.info(f"Created new Telegram user: {telegram_user_id}")
            
            # Build context for Alex
            user_context = {
                "telegram_user_id": telegram_user_id,
                "telegram_username": telegram_username,
                "first_name": first_name,
                "last_name": last_name,
                "has_patient_link": telegram_user.patient_id is not None,
                "patient_id": telegram_user.patient_id,
                "organization_id": telegram_user.organization_id,
                "language": "he" if any(ord(c) >= 0x0590 and ord(c) <= 0x05FF for c in text) else "en"
            }
            
            # Create enhanced message with system context
            enhanced_message = f"""SYSTEM CONTEXT - DO NOT SHOW TO USER
User Status: {'⚠️ NEW USER - NOT REGISTERED' if not user_context['has_patient_link'] else '✅ REGISTERED USER'}
Telegram Name: {first_name} {last_name}
Has Organization: {user_context['organization_id'] is not None}
Language: {user_context['language']}
END SYSTEM CONTEXT

User Message: {text}"""
            
            # Route to Alex (AgentGraphV4)
            agent_graph = AgentGraphV4()
            thread_id = f"telegram_{telegram_user_id}"
            
            logger.info(f"[WEBHOOK] Routing message to Alex for user {telegram_user_id}")
            logger.info(f"[WEBHOOK] Thread ID: {thread_id}")
            
            # Get response from Alex
            try:
                result = agent_graph.invoke(
                    message=enhanced_message,
                    thread_id=thread_id,
                    organization_id=user_context.get('organization_id'),
                    user_role='patient'
                )
                logger.info(f"[WEBHOOK] Alex response received: {type(result)}")
            except Exception as e:
                logger.error(f"[WEBHOOK] Error invoking Alex: {e}", exc_info=True)
                raise
            
            # Extract response text
            response = result.get('output', 'מצטער, לא הצלחתי לעבד את הבקשה')
            logger.info(f"[WEBHOOK] Response length: {len(response)} chars")
            logger.info(f"[WEBHOOK] Response preview: {response[:200]}...")
            
            # ✅ CRITICAL: Filter SYSTEM CONTEXT from response
            cleaned_response = _filter_system_context(response)
            logger.info(f"[WEBHOOK] Cleaned response length: {len(cleaned_response)} chars")
            logger.info(f"[WEBHOOK] Cleaned response preview: {cleaned_response[:200]}...")
            
            # Send cleaned response to Telegram
            logger.info(f"[WEBHOOK] Sending message to Telegram chat {chat_id}")
            try:
                await telegram_client.send_message(
                    chat_id=chat_id,
                    text=cleaned_response
                )
                logger.info(f"[WEBHOOK] Message sent successfully")
            except Exception as e:
                logger.error(f"[WEBHOOK] Error sending message to Telegram: {e}", exc_info=True)
                raise
            
            # Save conversation
            conversation = TelegramConversation(
                telegram_user_id=telegram_user.id,
                message=text,
                response=cleaned_response,  # Save cleaned response
                agent="alex"
            )
            db.add(conversation)
            db.commit()
            
            logger.info(f"Successfully processed message for user {telegram_user_id}")
            
        finally:
            db.close()
        
        return {"ok": True}
    
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


@router.get("/webhook-info")
async def get_webhook_info():
    """Get current webhook configuration."""
    try:
        info = await telegram_client.get_webhook_info()
        return info
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-webhook")
async def set_webhook(webhook_url: str):
    """Set Telegram webhook URL."""
    try:
        result = await telegram_client.set_webhook(webhook_url)
        return result
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

