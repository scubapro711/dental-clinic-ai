"""
Alex Telegram Tools

Advanced Telegram tools for Alex to provide rich, interactive experiences.

Tools:
1. send_telegram_message_with_buttons - Send message with quick reply buttons
2. send_telegram_rich_message - Send formatted message with Markdown
3. send_telegram_document - Send PDF/document files
4. send_telegram_photo - Send images
5. handle_telegram_callback - Handle button click callbacks

All tools are designed to work seamlessly with Alex's personality and workflow.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Check if requests is available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available - Telegram tools will not work")

# Check if Odoo client is available
try:
    from app.integrations.odoo_client import OdooClient
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    logger.warning("Odoo client not available")


# ============================================================================
# Tool 1: Send Telegram Message with Buttons
# ============================================================================

class SendTelegramMessageWithButtonsInput(BaseModel):
    """Input schema for sending Telegram message with buttons."""
    patient_id: int = Field(..., description="Patient ID")
    message: str = Field(..., description="Message text")
    buttons: List[List[Dict[str, str]]] = Field(
        ..., 
        description="Button layout. Example: [[{'text': '📅 Book', 'callback_data': 'book'}]]"
    )
    parse_mode: str = Field(default="Markdown", description="Message parse mode")


@tool
def send_telegram_message_with_buttons_tool(
    patient_id: int,
    message: str,
    buttons: List[List[Dict[str, str]]],
    parse_mode: str = "Markdown"
) -> Dict[str, Any]:
    """
    Send Telegram message with interactive quick reply buttons.
    
    This tool allows Alex to send messages with contextual buttons that make
    it easier for patients to respond. Buttons can trigger specific actions
    without requiring the patient to type.
    
    Args:
        patient_id: Patient ID in Odoo
        message: Message text (supports Markdown formatting)
        buttons: Button layout as nested list. Each inner list is a row.
                Example: [[{"text": "📅 Book", "callback_data": "book_appointment"}]]
        parse_mode: Message formatting (Markdown, HTML, or None)
    
    Returns:
        Dictionary with:
        - success: Boolean
        - message_id: Telegram message ID
        - buttons_sent: Number of buttons sent
        - confirmation: Success message
    
    Example:
        send_telegram_message_with_buttons_tool(
            patient_id=123,
            message="היי! איך אוכל לעזור לך היום?",
            buttons=[
                [
                    {"text": "📅 קביעת תור", "callback_data": "book_appointment"},
                    {"text": "🔍 התורים שלי", "callback_data": "my_appointments"}
                ],
                [
                    {"text": "❓ שאלה", "callback_data": "ask_question"}
                ]
            ]
        )
    """
    try:
        if not ODOO_AVAILABLE:
            return {
                'success': False,
                'error': 'Odoo client not available',
                'suggestion': 'Check Odoo configuration'
            }
        
        odoo = OdooClient()
        
        # Get patient Telegram ID
        telegram_user = odoo.search_read('telegram.user', [
            ('patient_id', '=', patient_id),
            ('active', '=', True)
        ], ['telegram_id', 'username'])
        
        if not telegram_user:
            return {
                'success': False,
                'error': 'המטופל לא מחובר ל-Telegram',
                'suggestion': 'שלח למטופל קישור הצטרפות או השתמש ב-SMS/Email'
            }
        
        telegram_id = telegram_user[0]['telegram_id']
        
        # Get bot token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.warning("Telegram bot token not configured")
            return {
                'success': False,
                'error': 'שירות Telegram לא מוגדר (חסר TELEGRAM_BOT_TOKEN)',
                'suggestion': 'הגדר TELEGRAM_BOT_TOKEN',
                'fallback': 'השתמש ב-SMS או Email'
            }
        
        # Send message via Telegram Bot API
        if not REQUESTS_AVAILABLE:
            return {
                'success': False,
                'error': 'requests library not available'
            }
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # Build inline keyboard
            inline_keyboard = []
            button_count = 0
            for row in buttons:
                keyboard_row = []
                for button in row:
                    keyboard_row.append({
                        'text': button.get('text', ''),
                        'callback_data': button.get('callback_data', '')
                    })
                    button_count += 1
                inline_keyboard.append(keyboard_row)
            
            payload = {
                'chat_id': telegram_id,
                'text': message,
                'parse_mode': parse_mode if parse_mode != 'None' else None,
                'reply_markup': {
                    'inline_keyboard': inline_keyboard
                }
            }
            
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            if not result.get('ok'):
                return {
                    'success': False,
                    'error': f"Telegram API error: {result.get('description')}",
                    'error_code': result.get('error_code')
                }
            
            message_id = result['result']['message_id']
            
            # Get patient name for confirmation
            patient = odoo.read('res.partner', patient_id, ['name'])
            
            # Log the message
            log_data = {
                'patient_id': patient_id,
                'message_type': 'telegram_with_buttons',
                'message_content': message,
                'recipient_telegram_id': telegram_id,
                'status': 'sent',
                'external_id': str(message_id),
                'metadata': {'button_count': button_count}
            }
            odoo.create('communication.log', log_data)
            
            return {
                'success': True,
                'message_id': message_id,
                'telegram_id': telegram_id,
                'buttons_sent': button_count,
                'confirmation': f"✅ הודעה עם {button_count} כפתורים נשלחה ל{patient['name']}",
                'delivery_status': 'נשלח בהצלחה',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except requests.exceptions.RequestException as telegram_error:
            logger.error(f"Telegram API request failed: {str(telegram_error)}")
            return {
                'success': False,
                'error': f'שגיאה בשליחת הודעת Telegram: {str(telegram_error)}',
                'suggestion': 'בדוק את ה-bot token או נסה שוב מאוחר יותר',
                'fallback': 'השתמש ב-SMS או Email'
            }
        
    except Exception as e:
        logger.error(f"Telegram tool error: {str(e)}")
        return {
            'success': False,
            'error': f'שגיאה כללית: {str(e)}'
        }


# ============================================================================
# Tool 2: Send Telegram Rich Message
# ============================================================================

class SendTelegramRichMessageInput(BaseModel):
    """Input schema for sending rich Telegram message."""
    patient_id: int = Field(..., description="Patient ID")
    template: str = Field(..., description="Template name (appointment_confirmation, reminder, payment_receipt)")
    data: Dict[str, Any] = Field(..., description="Template data")


@tool
def send_telegram_rich_message_tool(
    patient_id: int,
    template: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send rich formatted Telegram message using predefined templates.
    
    This tool sends beautifully formatted messages for common scenarios like
    appointment confirmations, reminders, and payment receipts.
    
    Args:
        patient_id: Patient ID in Odoo
        template: Template name (appointment_confirmation, reminder, payment_receipt)
        data: Template data (varies by template)
    
    Returns:
        Dictionary with:
        - success: Boolean
        - message_id: Telegram message ID
        - template_used: Template name
        - confirmation: Success message
    
    Templates:
        appointment_confirmation:
            data = {
                'patient_name': str,
                'date': str,
                'time': str,
                'doctor': str,
                'duration': int,
                'clinic_address': str
            }
        
        reminder:
            data = {
                'time': str,
                'doctor': str,
                'clinic_name': str,
                'clinic_address': str
            }
        
        payment_receipt:
            data = {
                'amount': float,
                'date': str,
                'receipt_number': str,
                'description': str
            }
    """
    try:
        # Template definitions
        templates = {
            'appointment_confirmation': """
✅ *התור נקבע בהצלחה!*

📋 *פרטי התור:*
👤 מטופל: {patient_name}
📅 תאריך: {date}
🕐 שעה: {time}
👨‍⚕️ רופא: {doctor}
⏱️ משך: {duration} דקות

📍 *כתובת המרפאה:*
{clinic_address}

💡 *טיפים:*
• הגע 5 דקות לפני
• הבא תעודת זהות
• תקבל תזכורת 24 שעות לפני

יש עוד משהו שאוכל לעזור בו? 😊
""",
            'reminder': """
⏰ *תזכורת לתור!*

📅 *מחר ב-{time}*
👨‍⚕️ עם {doctor}
🏥 {clinic_name}

📍 *כתובת:*
{clinic_address}

💡 *זכור:*
• הגע 5 דקות לפני
• הבא תעודת זהות

נתראה מחר! 😊
""",
            'payment_receipt': """
💰 *תשלום התקבל בהצלחה!*

💵 *סכום:* ₪{amount}
📅 *תאריך:* {date}
📄 *אסמכתא:* {receipt_number}
📝 *תיאור:* {description}

✅ הקבלה נשמרה במערכת

תודה! 😊
"""
        }
        
        # Get template
        if template not in templates:
            return {
                'success': False,
                'error': f'Template not found: {template}',
                'available_templates': list(templates.keys())
            }
        
        # Format message
        try:
            message = templates[template].format(**data)
        except KeyError as e:
            return {
                'success': False,
                'error': f'Missing template data: {str(e)}',
                'required_fields': list(templates[template])
            }
        
        # Define contextual buttons
        buttons_map = {
            'appointment_confirmation': [
                [
                    {"text": "✅ הבנתי, תודה", "callback_data": "acknowledge"}
                ],
                [
                    {"text": "🗓️ הוסף ליומן", "callback_data": "add_to_calendar"},
                    {"text": "📍 הוראות הגעה", "callback_data": "directions"}
                ]
            ],
            'reminder': [
                [
                    {"text": "✅ מאשר הגעה", "callback_data": "confirm_arrival"},
                    {"text": "❌ צריך לבטל", "callback_data": "cancel_appointment"}
                ],
                [
                    {"text": "⏰ שנה שעה", "callback_data": "reschedule"}
                ]
            ],
            'payment_receipt': [
                [
                    {"text": "✅ הבנתי", "callback_data": "acknowledge"}
                ],
                [
                    {"text": "📄 שלח קבלה למייל", "callback_data": "email_receipt"}
                ]
            ]
        }
        
        buttons = buttons_map.get(template, [])
        
        # Send message with buttons
        result = send_telegram_message_with_buttons_tool(
            patient_id=patient_id,
            message=message,
            buttons=buttons,
            parse_mode="Markdown"
        )
        
        if result['success']:
            result['template_used'] = template
        
        return result
        
    except Exception as e:
        logger.error(f"Rich message tool error: {str(e)}")
        return {
            'success': False,
            'error': f'שגיאה כללית: {str(e)}'
        }


# ============================================================================
# Tool 3: Send Telegram Document
# ============================================================================

class SendTelegramDocumentInput(BaseModel):
    """Input schema for sending Telegram document."""
    patient_id: int = Field(..., description="Patient ID")
    file_path: str = Field(..., description="Path to document file")
    caption: Optional[str] = Field(default=None, description="Document caption")


@tool
def send_telegram_document_tool(
    patient_id: int,
    document_path: str,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send document file (PDF, DOC, etc.) to patient via Telegram.
    
    This tool allows Alex to send documents like receipts, treatment plans,
    medical reports, etc. to patients.
    
    Args:
        patient_id: Patient ID in Odoo
        file_path: Path to the document file
        caption: Optional caption for the document
    
    Returns:
        Dictionary with:
        - success: Boolean
        - message_id: Telegram message ID
        - file_name: Name of the file sent
        - file_size: Size of the file in bytes
        - confirmation: Success message
    
    Example:
        send_telegram_document_tool(
            patient_id=123,
            file_path="/path/to/receipt.pdf",
            caption="הנה הקבלה שלך מהביקור היום 📄"
        )
    """
    try:
        if not ODOO_AVAILABLE:
            return {
                'success': False,
                'error': 'Odoo client not available'
            }
        
        odoo = OdooClient()
        
        # Get patient Telegram ID
        telegram_user = odoo.search_read('telegram.user', [
            ('patient_id', '=', patient_id),
            ('active', '=', True)
        ], ['telegram_id', 'username'])
        
        if not telegram_user:
            return {
                'success': False,
                'error': 'המטופל לא מחובר ל-Telegram',
                'suggestion': 'שלח למטופל קישור הצטרפות או השתמש ב-Email'
            }
        
        telegram_id = telegram_user[0]['telegram_id']
        
        # Get bot token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return {
                'success': False,
                'error': 'שירות Telegram לא מוגדר (חסר TELEGRAM_BOT_TOKEN)'
            }
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'File not found: {file_path}'
            }
        
        # Get file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Check file size (Telegram limit: 50MB for bots)
        if file_size > 50 * 1024 * 1024:
            return {
                'success': False,
                'error': 'הקובץ גדול מדי (מקסימום 50MB)',
                'file_size_mb': file_size / (1024 * 1024)
            }
        
        if not REQUESTS_AVAILABLE:
            return {
                'success': False,
                'error': 'requests library not available'
            }
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
            
            with open(file_path, 'rb') as file:
                files = {'document': file}
                data = {
                    'chat_id': telegram_id,
                    'caption': caption if caption else ''
                }
                
                response = requests.post(url, data=data, files=files, timeout=30)
                result = response.json()
            
            if not result.get('ok'):
                return {
                    'success': False,
                    'error': f"Telegram API error: {result.get('description')}",
                    'error_code': result.get('error_code')
                }
            
            message_id = result['result']['message_id']
            
            # Get patient name
            patient = odoo.read('res.partner', patient_id, ['name'])
            
            # Log the message
            log_data = {
                'patient_id': patient_id,
                'message_type': 'telegram_document',
                'message_content': caption or file_name,
                'recipient_telegram_id': telegram_id,
                'status': 'sent',
                'external_id': str(message_id),
                'metadata': {
                    'file_name': file_name,
                    'file_size': file_size
                }
            }
            odoo.create('communication.log', log_data)
            
            return {
                'success': True,
                'message_id': message_id,
                'telegram_id': telegram_id,
                'file_name': file_name,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'confirmation': f"✅ קובץ {file_name} נשלח ל{patient['name']}",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except requests.exceptions.RequestException as telegram_error:
            logger.error(f"Telegram API request failed: {str(telegram_error)}")
            return {
                'success': False,
                'error': f'שגיאה בשליחת קובץ: {str(telegram_error)}'
            }
        
    except Exception as e:
        logger.error(f"Document tool error: {str(e)}")
        return {
            'success': False,
            'error': f'שגיאה כללית: {str(e)}'
        }


# ============================================================================
# Tool 4: Send Telegram Photo
# ============================================================================

class SendTelegramPhotoInput(BaseModel):
    """Input schema for sending Telegram photo."""
    patient_id: int = Field(..., description="Patient ID")
    photo_path: str = Field(..., description="Path to photo file")
    caption: Optional[str] = Field(default=None, description="Photo caption")


@tool
def send_telegram_photo_tool(
    patient_id: int,
    photo_path: str,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send photo/image to patient via Telegram.
    
    This tool allows Alex to send images like x-rays, diagrams, maps, etc.
    
    Args:
        patient_id: Patient ID in Odoo
        photo_path: Path to the photo file
        caption: Optional caption for the photo
    
    Returns:
        Dictionary with:
        - success: Boolean
        - message_id: Telegram message ID
        - file_name: Name of the file sent
        - confirmation: Success message
    
    Example:
        send_telegram_photo_tool(
            patient_id=123,
            photo_path="/path/to/xray.jpg",
            caption="צילום הרנטגן מהביקור היום 🦷"
        )
    """
    try:
        if not ODOO_AVAILABLE:
            return {
                'success': False,
                'error': 'Odoo client not available'
            }
        
        odoo = OdooClient()
        
        # Get patient Telegram ID
        telegram_user = odoo.search_read('telegram.user', [
            ('patient_id', '=', patient_id),
            ('active', '=', True)
        ], ['telegram_id', 'username'])
        
        if not telegram_user:
            return {
                'success': False,
                'error': 'המטופל לא מחובר ל-Telegram',
                'suggestion': 'שלח למטופל קישור הצטרפות או השתמש ב-Email'
            }
        
        telegram_id = telegram_user[0]['telegram_id']
        
        # Get bot token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return {
                'success': False,
                'error': 'שירות Telegram לא מוגדר (חסר TELEGRAM_BOT_TOKEN)'
            }
        
        # Check if file exists
        if not os.path.exists(photo_path):
            return {
                'success': False,
                'error': f'File not found: {photo_path}'
            }
        
        # Get file info
        file_name = os.path.basename(photo_path)
        file_size = os.path.getsize(photo_path)
        
        # Check file size (Telegram limit: 10MB for photos)
        if file_size > 10 * 1024 * 1024:
            return {
                'success': False,
                'error': 'התמונה גדולה מדי (מקסימום 10MB)',
                'file_size_mb': file_size / (1024 * 1024),
                'suggestion': 'השתמש ב-send_telegram_document_tool במקום'
            }
        
        if not REQUESTS_AVAILABLE:
            return {
                'success': False,
                'error': 'requests library not available'
            }
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': telegram_id,
                    'caption': caption if caption else ''
                }
                
                response = requests.post(url, data=data, files=files, timeout=30)
                result = response.json()
            
            if not result.get('ok'):
                return {
                    'success': False,
                    'error': f"Telegram API error: {result.get('description')}",
                    'error_code': result.get('error_code')
                }
            
            message_id = result['result']['message_id']
            
            # Get patient name
            patient = odoo.read('res.partner', patient_id, ['name'])
            
            # Log the message
            log_data = {
                'patient_id': patient_id,
                'message_type': 'telegram_photo',
                'message_content': caption or file_name,
                'recipient_telegram_id': telegram_id,
                'status': 'sent',
                'external_id': str(message_id),
                'metadata': {
                    'file_name': file_name,
                    'file_size': file_size
                }
            }
            odoo.create('communication.log', log_data)
            
            return {
                'success': True,
                'message_id': message_id,
                'telegram_id': telegram_id,
                'file_name': file_name,
                'confirmation': f"✅ תמונה {file_name} נשלחה ל{patient['name']}",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except requests.exceptions.RequestException as telegram_error:
            logger.error(f"Telegram API request failed: {str(telegram_error)}")
            return {
                'success': False,
                'error': f'שגיאה בשליחת תמונה: {str(telegram_error)}'
            }
        
    except Exception as e:
        logger.error(f"Photo tool error: {str(e)}")
        return {
            'success': False,
            'error': f'שגיאה כללית: {str(e)}'
        }


# ============================================================================
# Tool 5: Handle Telegram Callback
# ============================================================================

class HandleTelegramCallbackInput(BaseModel):
    """Input schema for handling Telegram callback."""
    callback_data: str = Field(..., description="Callback data from button click")
    telegram_id: int = Field(..., description="Telegram user ID")
    message_id: Optional[int] = Field(default=None, description="Original message ID")


@tool
def handle_telegram_callback_tool(
    callback_data: str,
    telegram_id: int,
    message_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Handle Telegram button callback (when patient clicks a button).
    
    This tool processes button clicks and determines what action to take.
    It's called automatically when a patient clicks an inline button.
    
    Args:
        callback_data: The callback data from the button (e.g., "book_appointment")
        telegram_id: Telegram user ID who clicked the button
        message_id: Optional message ID of the message with the button
    
    Returns:
        Dictionary with:
        - success: Boolean
        - action: Action to take
        - response: Response message
        - next_buttons: Optional next set of buttons
    
    Callback Actions:
        - book_appointment: Start appointment booking flow
        - my_appointments: Show patient's appointments
        - ask_question: Start Q&A flow
        - contact_info: Show clinic contact information
        - acknowledge: Simple acknowledgment
        - add_to_calendar: Generate calendar event
        - directions: Show directions to clinic
        - confirm_arrival: Confirm appointment arrival
        - cancel_appointment: Start cancellation flow
        - reschedule: Start rescheduling flow
        - email_receipt: Email receipt to patient
    """
    try:
        if not ODOO_AVAILABLE:
            return {
                'success': False,
                'error': 'Odoo client not available'
            }
        
        odoo = OdooClient()
        
        # Get patient from Telegram ID
        telegram_user = odoo.search_read('telegram.user', [
            ('telegram_id', '=', telegram_id),
            ('active', '=', True)
        ], ['patient_id', 'username'])
        
        if not telegram_user:
            return {
                'success': False,
                'error': 'משתמש לא נמצא',
                'action': 'unknown_user'
            }
        
        patient_id = telegram_user[0]['patient_id']
        
        # Define callback handlers
        callback_handlers = {
            'book_appointment': {
                'action': 'start_booking_flow',
                'response': 'נהדר! בוא נקבע לך תור 😊\n\nמה התאריך המועדף שלך?',
                'next_buttons': []  # Alex will handle the flow
            },
            'my_appointments': {
                'action': 'show_appointments',
                'response': 'רגע, אני בודק את התורים שלך... 🔍',
                'next_buttons': []
            },
            'ask_question': {
                'action': 'start_qa_flow',
                'response': 'בטח! מה השאלה שלך? 😊',
                'next_buttons': []
            },
            'contact_info': {
                'action': 'show_contact',
                'response': None,  # Will be generated dynamically
                'next_buttons': [[
                    {"text": "📞 התקשר", "callback_data": "call_clinic"},
                    {"text": "📍 הוראות הגעה", "callback_data": "directions"}
                ]]
            },
            'acknowledge': {
                'action': 'acknowledge',
                'response': 'מעולה! 😊\n\nיש עוד משהו שאוכל לעזור בו?',
                'next_buttons': [[
                    {"text": "📅 קביעת תור", "callback_data": "book_appointment"},
                    {"text": "❌ לא, תודה", "callback_data": "end_conversation"}
                ]]
            },
            'add_to_calendar': {
                'action': 'generate_calendar_event',
                'response': 'רגע, אני מכין לך קישור ליומן... 📅',
                'next_buttons': []
            },
            'directions': {
                'action': 'show_directions',
                'response': None,  # Will include Google Maps link
                'next_buttons': []
            },
            'confirm_arrival': {
                'action': 'confirm_appointment',
                'response': 'תודה על האישור! 😊\n\nנתראה בקרוב!',
                'next_buttons': []
            },
            'cancel_appointment': {
                'action': 'start_cancellation_flow',
                'response': 'אוקיי, אני מבין שאתה צריך לבטל.\n\nאיזה תור תרצה לבטל?',
                'next_buttons': []
            },
            'reschedule': {
                'action': 'start_reschedule_flow',
                'response': 'בטח! בוא נמצא לך זמן אחר.\n\nמה התאריך החדש שמתאים לך?',
                'next_buttons': []
            },
            'email_receipt': {
                'action': 'email_receipt',
                'response': 'רגע, אני שולח את הקבלה למייל... 📧',
                'next_buttons': []
            },
            'end_conversation': {
                'action': 'end_conversation',
                'response': 'תודה! אם תצטרך משהו, אני פה 😊',
                'next_buttons': []
            }
        }
        
        # Get handler
        handler = callback_handlers.get(callback_data)
        
        if not handler:
            return {
                'success': False,
                'error': f'Unknown callback: {callback_data}',
                'action': 'unknown_callback'
            }
        
        # Log the callback
        log_data = {
            'patient_id': patient_id,
            'message_type': 'telegram_callback',
            'message_content': callback_data,
            'recipient_telegram_id': telegram_id,
            'status': 'processed',
            'metadata': {
                'callback_data': callback_data,
                'message_id': message_id
            }
        }
        odoo.create('communication.log', log_data)
        
        return {
            'success': True,
            'action': handler['action'],
            'callback_data': callback_data,
            'response': handler['response'],
            'next_buttons': handler.get('next_buttons', []),
            'patient_id': patient_id,
            'telegram_id': telegram_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        logger.error(f"Callback tool error: {str(e)}")
        return {
            'success': False,
            'error': f'שגיאה כללית: {str(e)}'
        }


# ============================================================================
# Export all tools
# ============================================================================

__all__ = [
    'send_telegram_message_with_buttons_tool',
    'send_telegram_rich_message_tool',
    'send_telegram_document_tool',
    'send_telegram_photo_tool',
    'handle_telegram_callback_tool',
]

