"""
Enhanced Telegram webhook handler with callback_query support
Handles both text messages and button callbacks
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
    Supports both text messages and button callbacks.
    Routes all interactions to Alex (AgentGraphV4).
    """
    try:
        logger.info("=== WEBHOOK CALLED ===")
        # Parse webhook payload
        data = await request.json()
        logger.info(f"Received Telegram update: {data.get('update_id')}")
        logger.info(f"Full data: {data}")
        
        # Check if this is a callback query (button click)
        callback_query = data.get("callback_query")
        if callback_query:
            logger.info("Processing callback_query (button click)")
            return await _handle_callback_query(callback_query)
        
        # Otherwise, handle as regular message
        message = data.get("message")
        logger.info(f"Message extracted: {message is not None}")
        if not message:
            logger.warning("No message or callback_query in update - RETURNING EARLY")
            return {"ok": True}
        
        return await _handle_text_message(message)
    
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def _handle_text_message(message: Dict[str, Any]) -> Dict[str, bool]:
    """Handle regular text message from user."""
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
                telegram_first_name=first_name,
                telegram_last_name=last_name,
                organization_id="00000000-0000-0000-0000-000000000000"  # Default org for now
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


async def _handle_callback_query(callback_query: Dict[str, Any]) -> Dict[str, bool]:
    """
    Handle button callback (when user clicks an inline button).
    
    This function:
    1. Extracts callback data and user info
    2. Calls Alex's handle_telegram_callback_tool
    3. Sends the response back to the user
    4. Answers the callback query to remove loading state
    """
    try:
        # Extract callback info
        callback_id = callback_query.get("id")
        callback_data = callback_query.get("data")
        from_user = callback_query.get("from", {})
        message = callback_query.get("message", {})
        
        telegram_user_id = from_user.get("id")
        telegram_username = from_user.get("username", "")
        first_name = from_user.get("first_name", "")
        last_name = from_user.get("last_name", "")
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")
        
        logger.info(f"[CALLBACK] Processing callback: {callback_data} from user {telegram_user_id}")
        
        if not telegram_user_id or not callback_data:
            logger.warning(f"Missing user_id or callback_data - RETURNING EARLY")
            return {"ok": True}
        
        # Get Telegram user from database
        db: Session = next(get_db())
        try:
            telegram_user = db.query(TelegramUser).filter(
                TelegramUser.telegram_user_id == telegram_user_id
            ).first()
            
            if not telegram_user:
                # Create user if doesn't exist
                telegram_user = TelegramUser(
                    telegram_user_id=telegram_user_id,
                    telegram_username=telegram_username,
                    telegram_first_name=first_name,
                    telegram_last_name=last_name,
                    organization_id="00000000-0000-0000-0000-000000000000"
                )
                db.add(telegram_user)
                db.commit()
                db.refresh(telegram_user)
                logger.info(f"Created new Telegram user from callback: {telegram_user_id}")
            
            # Build context for Alex
            user_context = {
                "telegram_user_id": telegram_user_id,
                "telegram_username": telegram_username,
                "first_name": first_name,
                "last_name": last_name,
                "has_patient_link": telegram_user.patient_id is not None,
                "patient_id": telegram_user.patient_id,
                "organization_id": telegram_user.organization_id,
                "callback_data": callback_data,
                "message_id": message_id
            }
            
            # Create message for Alex about the button click
            enhanced_message = f"""SYSTEM CONTEXT - DO NOT SHOW TO USER
User Status: {'⚠️ NEW USER - NOT REGISTERED' if not user_context['has_patient_link'] else '✅ REGISTERED USER'}
Telegram Name: {first_name} {last_name}
Has Organization: {user_context['organization_id'] is not None}
Action Type: BUTTON_CLICK
Callback Data: {callback_data}
Message ID: {message_id}
END SYSTEM CONTEXT

User clicked button: {callback_data}

Please use handle_telegram_callback_tool to process this button click and respond appropriately."""
            
            # Route to Alex (AgentGraphV4)
            agent_graph = AgentGraphV4()
            thread_id = f"telegram_{telegram_user_id}"
            
            logger.info(f"[CALLBACK] Routing callback to Alex for user {telegram_user_id}")
            
            # Get response from Alex
            try:
                result = agent_graph.invoke(
                    message=enhanced_message,
                    thread_id=thread_id,
                    organization_id=user_context.get('organization_id'),
                    user_role='patient'
                )
                logger.info(f"[CALLBACK] Alex response received")
            except Exception as e:
                logger.error(f"[CALLBACK] Error invoking Alex: {e}", exc_info=True)
                raise
            
            # Extract response text
            response = result.get('output', 'מצטער, לא הצלחתי לעבד את הבקשה')
            
            # Filter SYSTEM CONTEXT from response
            cleaned_response = _filter_system_context(response)
            logger.info(f"[CALLBACK] Cleaned response: {cleaned_response[:200]}...")
            
            # Answer the callback query (removes loading state on button)
            try:
                await telegram_client.answer_callback_query(
                    callback_query_id=callback_id,
                    text="✅"  # Simple checkmark
                )
                logger.info(f"[CALLBACK] Answered callback query")
            except Exception as e:
                logger.warning(f"[CALLBACK] Error answering callback query: {e}")
            
            # Send response to user
            try:
                await telegram_client.send_message(
                    chat_id=chat_id,
                    text=cleaned_response
                )
                logger.info(f"[CALLBACK] Response sent successfully")
            except Exception as e:
                logger.error(f"[CALLBACK] Error sending response: {e}", exc_info=True)
                raise
            
            # Save conversation
            conversation = TelegramConversation(
                telegram_user_id=telegram_user.id,
                message=f"[BUTTON_CLICK] {callback_data}",
                response=cleaned_response,
                agent="alex"
            )
            db.add(conversation)
            db.commit()
            
            logger.info(f"Successfully processed callback for user {telegram_user_id}")
            
        finally:
            db.close()
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Error processing callback query: {e}", exc_info=True)
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

