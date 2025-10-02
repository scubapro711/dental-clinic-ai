# 📱 Telegram Bot Setup Guide

Complete guide for setting up and deploying the Dental Clinic AI Telegram bot.

---

## 🎯 Overview

The Telegram bot provides patients with 24/7 access to:
- **Appointment scheduling** - Book, reschedule, cancel appointments
- **Billing inquiries** - Check invoices and payment status
- **Clinic information** - Hours, location, services
- **Doctor escalation** - Emergency handling and medical questions
- **Multi-language support** - English and Hebrew

---

## 📋 Prerequisites

1. **Telegram Bot Token** - Obtained from @BotFather
2. **Backend Server** - Running and accessible via HTTPS
3. **Domain/URL** - Public HTTPS endpoint for webhook

---

## 🚀 Quick Start

### Step 1: Create Bot with BotFather

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Choose a name: `Dental Clinic AI Assistant`
4. Choose a username: `dental_clinic_ai_bot` (must end with `bot`)
5. Copy the bot token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure Backend

Add the bot token to your `.env` file:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Step 3: Deploy Backend

Deploy your backend server to a public HTTPS endpoint:

```bash
# Example deployment commands
cd backend
docker build -t dental-clinic-backend .
docker run -p 8000:8000 dental-clinic-backend
```

### Step 4: Set Webhook

Configure Telegram to send updates to your backend:

```bash
cd backend
python scripts/setup_telegram_webhook.py --url https://your-domain.com/api/v1/telegram/webhook
```

### Step 5: Test the Bot

1. Open Telegram
2. Search for `@dental_clinic_ai_bot`
3. Send `/start` to begin
4. Try sending a message: "I want to book an appointment"

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional (for customization)
CLINIC_LATITUDE=32.0853
CLINIC_LONGITUDE=34.7818
CLINIC_ADDRESS="123 Dizengoff Street, Tel Aviv"
CLINIC_PHONE="+972-3-123-4567"
```

### Webhook Management

**Check webhook status:**
```bash
python scripts/setup_telegram_webhook.py --info
```

**Update webhook URL:**
```bash
python scripts/setup_telegram_webhook.py --url https://new-domain.com/api/v1/telegram/webhook
```

**Delete webhook:**
```bash
python scripts/setup_telegram_webhook.py --delete
```

---

## 💬 Bot Features

### Commands

- `/start` - Welcome message and quick actions
- `/help` - Usage instructions

### Quick Reply Buttons

- 📅 **Book Appointment** - Start appointment booking flow
- 💰 **Check Invoice** - View billing information
- 👨‍⚕️ **Talk to Doctor** - Request doctor consultation
- 📍 **Clinic Location** - Get clinic address and map

### Natural Language

Users can also type naturally:
- "I have a toothache"
- "What are your hours?"
- "How much does a cleaning cost?"
- "יש לי כאב שיניים" (Hebrew)

---

## 🚨 Medical Safety

The bot follows strict medical safety protocols:

### Emergency Escalation

**Triggers:**
- Severe pain (8-10/10)
- Facial swelling
- Difficulty breathing
- Severe bleeding
- High fever

**Response:**
- Immediate doctor notification
- Emergency instructions
- Option to call 911/ER

### Doctor Required

**Triggers:**
- Medication questions
- Diagnosis requests
- Treatment plan questions

**Response:**
- Refuse to provide medical advice
- Offer doctor consultation options
- Connect with Dr. Smith

---

## 🧪 Testing

### Unit Tests

Run the test suite:

```bash
cd backend
pytest tests/test_telegram_integration.py -v
```

### Manual Testing

1. **Basic conversation:**
   ```
   User: Hello
   Bot: Hello! How can I help you today?
   ```

2. **Appointment booking:**
   ```
   User: I want to book an appointment
   Bot: [Shows available slots]
   ```

3. **Emergency:**
   ```
   User: I have severe pain and swelling
   Bot: 🚨 EMERGENCY ALERT [Escalates to doctor]
   ```

4. **Hebrew:**
   ```
   User: יש לי כאב שיניים
   Bot: אני מבין שיש לך כאב שיניים...
   ```

---

## 🔍 Troubleshooting

### Bot Not Responding

**Check webhook status:**
```bash
python scripts/setup_telegram_webhook.py --info
```

**Common issues:**
- Webhook URL not HTTPS
- Backend server not running
- Firewall blocking requests
- Invalid bot token

### Webhook Errors

**View error logs:**
```bash
# Check backend logs
docker logs dental-clinic-backend

# Check Telegram webhook info
python scripts/setup_telegram_webhook.py --info
```

**Common errors:**
- `Connection refused` - Backend not accessible
- `SSL error` - Invalid SSL certificate
- `404 Not Found` - Wrong webhook URL

### Message Not Reaching Agent

**Check logs:**
```bash
# Backend logs
tail -f backend/logs/app.log

# Look for:
# - "Processing message from user..."
# - "Alex processing message..."
# - "Response sent to chat..."
```

---

## 📊 Monitoring

### Webhook Health

Monitor webhook status:
```bash
# Get webhook info
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### Message Metrics

Track in backend logs:
- Messages received
- Response times
- Escalation rates
- Error rates

---

## 🔐 Security

### Best Practices

1. **Keep token secret** - Never commit to Git
2. **Use HTTPS only** - Telegram requires HTTPS for webhooks
3. **Validate requests** - Check Telegram signature (optional)
4. **Rate limiting** - Prevent abuse
5. **Error handling** - Graceful degradation

### Token Rotation

If token is compromised:

1. Revoke old token via @BotFather
2. Generate new token
3. Update `.env` file
4. Restart backend
5. Update webhook

---

## 📈 Advanced Features

### Custom Keyboards

Create custom button layouts:

```python
from app.integrations.telegram_client import telegram_client

keyboard = telegram_client.create_inline_keyboard([
    [{"text": "Option 1", "callback_data": "opt1"}],
    [{"text": "Option 2", "callback_data": "opt2"}],
])

await telegram_client.send_message(
    chat_id=chat_id,
    text="Choose an option:",
    reply_markup=keyboard
)
```

### Rich Formatting

Use Markdown or HTML:

```python
# Markdown
text = "*Bold* _Italic_ [Link](https://example.com)"

# HTML
text = "<b>Bold</b> <i>Italic</i> <a href='https://example.com'>Link</a>"
```

### Send Images

```python
await telegram_client.send_photo(
    chat_id=chat_id,
    photo="https://example.com/image.jpg",
    caption="Dental diagram"
)
```

---

## 🎓 Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [BotFather Commands](https://core.telegram.org/bots#6-botfather)
- [Webhook Guide](https://core.telegram.org/bots/webhooks)

---

## 📞 Support

For issues or questions:
- Check logs: `backend/logs/app.log`
- Run tests: `pytest tests/test_telegram_integration.py`
- Review webhook: `python scripts/setup_telegram_webhook.py --info`

---

**Last Updated:** October 2, 2025
**Bot Username:** @dental_clinic_ai_bot
**Status:** ✅ Production Ready
