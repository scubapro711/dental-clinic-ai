# Telegram Bot Setup Guide

Complete guide for setting up and deploying the DentaFlow Telegram Bot.

## 📋 Overview

The Telegram Bot allows patients to:
- Schedule appointments via chat
- Check appointment status
- Receive reminders
- Ask questions to AI agents
- Get clinic information

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Create Bot with BotFather

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name: `DentaFlow Assistant`
4. Choose a username: `dentaflow_bot` (must end with `_bot`)
5. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure Environment

```bash
# Add to .env file
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_WEBHOOK_URL=https://dentaflow.ai/api/v1/telegram/webhook
```

### Step 3: Set Webhook

```bash
# Run setup script
cd backend
python3 scripts/setup_telegram_webhook.py
```

**Expected output:**
```
✓ Webhook set successfully!
URL: https://dentaflow.ai/api/v1/telegram/webhook
```

### Step 4: Test Bot

1. Open Telegram
2. Search for your bot: `@dentaflow_bot`
3. Send `/start`
4. Bot should respond: "שלום! אני עוזר הדיגיטלי של DentaFlow..."

---

## 🔧 Detailed Setup

### Create Bot with BotFather

**Full conversation:**
```
You: /newbot
BotFather: Alright, a new bot. How are we going to call it?

You: DentaFlow Assistant
BotFather: Good. Now let's choose a username for your bot. It must end in `bot`.

You: dentaflow_bot
BotFather: Done! Congratulations on your new bot. You will find it at t.me/dentaflow_bot.

Here is your token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz

For a description of the Bot API, see this page: https://core.telegram.org/bots/api
```

### Configure Bot Settings

```
/setdescription
DentaFlow - Your AI-powered dental clinic assistant. Schedule appointments, get reminders, and chat with our AI agents 24/7.

/setabouttext
DentaFlow helps you manage your dental appointments easily. Powered by AI agents Alex, Marcus, and Sophia.

/setuserpic
[Upload clinic logo]

/setcommands
start - Start conversation
help - Show help message
schedule - Schedule an appointment
status - Check appointment status
cancel - Cancel an appointment
contact - Contact clinic
```

### Set Up Webhook

**Option 1: Using Setup Script (Recommended)**

```bash
cd backend
python3 scripts/setup_telegram_webhook.py
```

**Option 2: Manual Setup**

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://dentaflow.ai/api/v1/telegram/webhook",
    "allowed_updates": ["message", "callback_query"]
  }'
```

**Verify webhook:**
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

**Expected response:**
```json
{
  "ok": true,
  "result": {
    "url": "https://dentaflow.ai/api/v1/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": 0,
    "max_connections": 40,
    "allowed_updates": ["message", "callback_query"]
  }
}
```

---

## 🏗️ Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Telegram User                           │
│                           ↓                                  │
│                    Telegram API                              │
│                           ↓                                  │
│              Webhook (POST /api/v1/telegram/webhook)         │
│                           ↓                                  │
│                  TelegramHandler                             │
│                     ↓         ↓                              │
│          ConversationManager  ↔  Alex Agent                  │
│                     ↓                                        │
│                  Database                                    │
└─────────────────────────────────────────────────────────────┘
```

### Flow

1. **User sends message** → Telegram API
2. **Telegram API** → POST to webhook
3. **Webhook** → Extract message, user info
4. **Handler** → Create/load conversation
5. **Handler** → Send to Alex agent
6. **Alex** → Process with tools (Odoo, etc.)
7. **Alex** → Generate response
8. **Handler** → Send response to Telegram API
9. **Telegram API** → Deliver to user

---

## 💬 Conversation Examples

### Example 1: Schedule Appointment

**User:** היי, אני רוצה לקבוע תור

**Bot:** שלום! אשמח לעזור לך לקבוע תור. מה השם המלא שלך?

**User:** דוד כהן

**Bot:** נעים מאוד דוד! מה מספר הטלפון שלך?

**User:** 0501234567

**Bot:** תודה! מתי תרצה להגיע? (לדוגמה: "מחר בשעה 10:00" או "יום רביעי הבא")

**User:** יום שלישי הבא בשעה 14:00

**Bot:** בודק תורים פנויים...

**Bot:** ✅ התור נקבע בהצלחה!

📋 פרטי התור:
מטופל: דוד כהן
תאריך: 15/10/2025
שעה: 14:00
משך: 45 דקות
מספר תור: 456

תקבל תזכורת 24 שעות לפני התור.

---

### Example 2: Check Status

**User:** /status

**Bot:** בודק את התורים שלך...

**Bot:** יש לך תור אחד קרוב:

תור #456:
תאריך: 15/10/2025 בשעה 14:00
רופא: ד"ר שרה לוי
סטטוס: מאושר

---

### Example 3: Cancel Appointment

**User:** /cancel

**Bot:** איזה תור תרצה לבטל?

1. תור #456 - 15/10/2025 בשעה 14:00

**User:** 1

**Bot:** האם אתה בטוח שברצונך לבטל את התור?

[כן] [לא]

**User:** [לחיצה על "כן"]

**Bot:** ✅ התור בוטל בהצלחה!

תור #456 בוטל. אם תרצה לקבוע תור חדש, פשוט שלח לי הודעה.

---

## 🔐 Security

### Webhook Verification

```python
import hmac
import hashlib

def verify_telegram_webhook(request_data: str, secret_token: str) -> bool:
    """Verify webhook request is from Telegram."""
    received_hash = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    
    if not received_hash:
        return False
    
    expected_hash = hmac.new(
        secret_token.encode(),
        request_data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(received_hash, expected_hash)
```

### Rate Limiting

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.post("/telegram/webhook")
@limiter.limit("100/minute")  # Max 100 requests per minute
async def telegram_webhook(request: Request):
    ...
```

### User Verification

```python
def verify_user_access(telegram_user_id: int, organization_id: UUID) -> bool:
    """Verify user has access to organization."""
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.telegram_user_id == telegram_user_id,
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.is_active == True
    ).first()
    
    return membership is not None
```

---

## 🧪 Testing

### Test 1: Send Message

```python
import asyncio
from app.integrations.telegram_client import TelegramClient

async def test_send_message():
    client = TelegramClient()
    
    response = await client.send_message(
        chat_id=123456789,  # Your Telegram user ID
        text="Hello from DentaFlow! 🦷"
    )
    
    print(f"Message sent: {response}")

asyncio.run(test_send_message())
```

### Test 2: Webhook Endpoint

```bash
# Send test webhook
curl -X POST "https://dentaflow.ai/api/v1/telegram/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {
        "id": 987654321,
        "first_name": "Test",
        "username": "testuser"
      },
      "chat": {
        "id": 987654321,
        "type": "private"
      },
      "date": 1696800000,
      "text": "/start"
    }
  }'
```

### Test 3: End-to-End

```python
import pytest
from app.integrations.telegram_client import TelegramClient

@pytest.mark.asyncio
async def test_e2e_appointment_booking():
    client = TelegramClient()
    chat_id = 123456789  # Test user
    
    # Start conversation
    await client.send_message(chat_id, "/start")
    
    # User wants to schedule
    await client.send_message(chat_id, "אני רוצה לקבוע תור")
    
    # Provide name
    await client.send_message(chat_id, "דוד כהן")
    
    # Provide phone
    await client.send_message(chat_id, "0501234567")
    
    # Provide date
    await client.send_message(chat_id, "מחר בשעה 10:00")
    
    # Check response contains confirmation
    # (In real test, you'd need to capture the bot's response)
```

---

## 📊 Monitoring

### Webhook Health Check

```python
@router.get("/telegram/health")
async def telegram_health():
    """Check Telegram bot health."""
    client = TelegramClient()
    
    try:
        # Get bot info
        response = await client.client.get(f"{client.base_url}/getMe")
        bot_info = response.json()
        
        # Get webhook info
        webhook_response = await client.client.get(f"{client.base_url}/getWebhookInfo")
        webhook_info = webhook_response.json()
        
        return {
            "status": "healthy",
            "bot": bot_info["result"],
            "webhook": webhook_info["result"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### Metrics

```python
from prometheus_client import Counter, Histogram

telegram_messages_received = Counter(
    'telegram_messages_received_total',
    'Total Telegram messages received'
)

telegram_messages_sent = Counter(
    'telegram_messages_sent_total',
    'Total Telegram messages sent'
)

telegram_response_time = Histogram(
    'telegram_response_time_seconds',
    'Time to process Telegram message'
)
```

---

## 🐛 Troubleshooting

### Issue: Webhook not receiving messages

**Symptoms:**
- Bot doesn't respond to messages
- Webhook endpoint not being called

**Diagnosis:**
```bash
# Check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

**Solutions:**
1. **Webhook URL incorrect:**
   ```bash
   # Reset webhook
   python3 scripts/setup_telegram_webhook.py
   ```

2. **Server not accessible:**
   ```bash
   # Test endpoint
   curl https://dentaflow.ai/api/v1/telegram/webhook
   ```

3. **SSL certificate issue:**
   ```bash
   # Telegram requires HTTPS with valid certificate
   # Check certificate
   openssl s_client -connect dentaflow.ai:443 -servername dentaflow.ai
   ```

---

### Issue: Bot responds slowly

**Symptoms:**
- Messages take >5 seconds to respond
- Timeout errors

**Diagnosis:**
```python
# Add timing logs
import time

start = time.time()
response = await process_message(message)
duration = time.time() - start
logger.info(f"Processed message in {duration:.2f}s")
```

**Solutions:**
1. **Optimize agent processing:**
   - Use streaming responses
   - Cache common queries
   - Reduce tool calls

2. **Use async processing:**
   ```python
   # Respond immediately, process in background
   await telegram_client.send_message(chat_id, "בודק...")
   
   # Process in background
   asyncio.create_task(process_and_respond(message))
   ```

---

### Issue: Bot token invalid

**Symptoms:**
- 401 Unauthorized errors
- "Bot token is invalid"

**Solutions:**
1. **Check token format:**
   ```python
   # Token should be: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   assert re.match(r'^\d+:[A-Za-z0-9_-]+$', TELEGRAM_BOT_TOKEN)
   ```

2. **Regenerate token:**
   - Message @BotFather
   - Send `/token`
   - Select your bot
   - Copy new token

---

## 📚 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [BotFather Commands](https://core.telegram.org/bots#6-botfather)
- [Telegram Bot Best Practices](https://core.telegram.org/bots/tutorial)
- [Webhook Guide](https://core.telegram.org/bots/webhooks)

---

## ✅ Deployment Checklist

- [ ] Create bot with BotFather
- [ ] Set bot description and commands
- [ ] Add bot token to environment variables
- [ ] Configure webhook URL
- [ ] Run setup script
- [ ] Test `/start` command
- [ ] Test appointment booking flow
- [ ] Test appointment cancellation
- [ ] Set up monitoring
- [ ] Configure rate limiting
- [ ] Enable webhook verification
- [ ] Test error handling
- [ ] Document for team

---

**Last Updated:** October 8, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
