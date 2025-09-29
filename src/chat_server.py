
"""
Main Chat Server for Dana AI

Handles WebSocket connections, message processing, synthesis agent routing,
and advanced multilingual support.
"""

import asyncio
import websockets
import json
import re
from langdetect import detect, LangDetectException

# --- Synthesis Agent & Routing Logic ---

def synthesis_agent(message, lang):
    """Analyzes user message and routes to the appropriate agent based on language and intent."""
    message_lower = message.lower()

    # Keywords for routing (expanded for better accuracy)
    booking_keywords = {
        'en': ['book', 'appointment', 'schedule', 'see a doctor', 'check-up'],
        'he': ['תור', 'לקבוע', 'פגישה', 'רופא', 'בדיקה'],
        'ar': ['موعد', 'حجز', 'مقابلة', 'طبيب', 'فحص']
    }
    emergency_keywords = {
        'en': ['emergency', 'urgent', 'pain', 'help', 'hurts', 'bleeding'],
        'he': ['כאב', 'דחוף', 'חירום', 'כואב', 'עזרה', 'דימום'],
        'ar': ['ألم', 'طارئ', 'مساعدة', 'نزيف', 'عاجل']
    }

    # 1. Emergency Check (prioritized)
    if any(keyword in message_lower for keyword in emergency_keywords.get(lang, [])):
        return 'emergency_agent', None

    # 2. Booking Check
    if any(keyword in message_lower for keyword in booking_keywords.get(lang, [])):
        # Simple entity extraction for date/time
        entities = {
            'date': re.search(r'\d{1,2}[/.-]\d{1,2}(?:[/.-]\d{2,4})?', message),
            'time': re.search(r'\d{1,2}:\d{2}', message)
        }
        return 'booking_agent', entities

    # 3. Default to Dana for conversation
    return 'dana_agent', None

# --- Specialist Agent Handlers (with Cultural Nuances) ---

async def handle_emergency_agent(lang):
    """Handles emergency requests with culturally appropriate urgency and empathy."""
    responses = {
        'en': "This sounds urgent. Please call our clinic directly at [Clinic Phone Number] or proceed to the nearest emergency room. I am alerting a human agent right now.",
        'he': "אני מבינה שמדובר במקרה חירום. **אנא צור קשר טלפוני מיידי עם המרפאה** במספר [מספר טלפון] או גש לחדר המיון הקרוב. אני מעבירה את פנייתך לגורם אנושי באופן מיידי.",
        'ar': "يبدو أن هذه حالة طارئة. **يرجى الاتصال بالعيادة فوراً** على الرقم [رقم الهاتف] أو التوجه إلى أقرب غرفة طوارئ. سأقوم بتنبيه موظف بشري على الفور."
    }
    return {'agent': 'Human Alert', 'message': responses.get(lang, responses['en'])}

async def handle_booking_agent(entities, lang):
    """Handles appointment booking with language-specific confirmations."""
    date_str = entities.get('date').group(0) if entities.get('date') else "a future date"
    time_str = entities.get('time').group(0) if entities.get('time') else "a specific time"

    responses = {
        'en': f"I can certainly help you book an appointment. I see you mentioned {date_str} around {time_str}. Let me check our schedule for you.",
        'he': f"בשמחה, אני יכולה לסייע בקביעת תור. אני רואה שציינת {date_str} בסביבות {time_str}. אתן לי לבדוק את היומן.",
        'ar': f"بالتأكيد، يمكنني مساعدتك في حجز موعد. أرى أنك ذكرت {date_str} حوالي الساعة {time_str}. دعني أتحقق من جدولنا لك."
    }
    return {'agent': 'BookingBot', 'message': responses.get(lang, responses['en'])}

async def handle_dana_agent(message, lang):
    """Handles conversation with cultural greetings and small talk."""
    # More nuanced greetings and responses
    responses = {
        'en': {
            'greeting': "Hello! I'm Dana, your personal AI assistant. How can I help you today?",
            'default': "That's interesting to know. Is there anything I can assist you with regarding your dental health or appointments?",
            'opening': "Welcome! I'm Dana. Feel free to ask me anything about our clinic, or we can just chat."
        },
        'he': {
            'greeting': "שלום, מה שלומך? אני דנה, העוזרת האישית שלך. איך אני יכולה לעזור?",
            'default': "זה מעניין. האם תרצה שאעזור לך במשהו שקשור לבריאות השיניים או לקביעת תורים?",
            'opening': "ברוכים הבאים למרפאה! אני דנה. אפשר לשאול אותי כל דבר, או סתם לדבר."
        },
        'ar': {
            'greeting': "مرحباً بك! أنا دانا، مساعدتك الذكية الشخصية. كيف حالك اليوم؟ كيف يمكنني خدمتك؟",
            'default': "هذا مثير للاهتمام. هل هناك أي شيء يمكنني أن أساعدك به بخصوص صحة أسنانك أو تحديد موعد؟",
            'opening': "أهلاً بك في عيادتنا! أنا دانا. يمكنك أن تسألني أي شيء، أو يمكننا الدردشة قليلاً."
        }
    }

    # Simple check for greeting keywords
    greeting_keywords = ['hi', 'hello', 'hey', 'שלום', 'היי', 'מה קורה', 'مرحبا', 'أهلا']
    if any(keyword in message.lower() for keyword in greeting_keywords):
        response_message = responses[lang]['greeting']
    elif message == "__initial_message__":
        response_message = responses[lang]['opening']
    else:
        response_message = responses[lang]['default']
        
    return {'agent': 'Dana', 'message': response_message}

# --- Main WebSocket Handler ---

async def chat_handler(websocket, path):
    """Handles WebSocket connections, including language detection."""
    print(f"New connection from {websocket.remote_address}")
    try:
        # Send initial greeting in English by default
        initial_payload = await handle_dana_agent("__initial_message__", lang='en')
        await websocket.send(json.dumps(initial_payload))

        async for message in websocket:
            data = json.loads(message)
            user_message = data.get('message', '')
            
            # 1. Detect Language
            try:
                # Use langdetect, but fall back to provided lang or 'en'
                detected_lang = detect(user_message)
                # Normalize to 'he' for Hebrew
                if detected_lang == 'he' or detected_lang == 'iw':
                    lang = 'he'
                elif detected_lang == 'ar':
                    lang = 'ar'
                else:
                    lang = 'en'
            except LangDetectException:
                lang = data.get('lang', 'en') # Use client-provided lang as fallback

            print(f'Received message: "{user_message}" (Detected Language: {lang})')

            # 2. Route message using the synthesis agent
            agent, entities = synthesis_agent(user_message, lang)
            print(f"Routing to: {agent}")

            # 3. Handle request with the designated agent
            if agent == 'emergency_agent':
                response_payload = await handle_emergency_agent(lang)
            elif agent == 'booking_agent':
                response_payload = await handle_booking_agent(entities, lang)
            else: # dana_agent
                response_payload = await handle_dana_agent(user_message, lang)
            
            response_payload['original_message'] = user_message
            response_payload['detected_lang'] = lang

            # 4. Send response
            await websocket.send(json.dumps(response_payload))
            print(f"Sent response: {response_payload}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Server Startup ---

async def main():
    host = "0.0.0.0"
    port = 8765
    async with websockets.serve(chat_handler, host, port):
        print(f"Multilingual Chat Server started on ws://{host}:{port}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

