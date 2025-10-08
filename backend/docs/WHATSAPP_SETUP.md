# WhatsApp Business API Setup Guide

Complete guide for integrating WhatsApp Business API (Cloud API) with DentaFlow.

> **Note:** Currently using Telegram. This guide is for future WhatsApp integration.

---

## 📋 Overview

WhatsApp Business API allows:
- **Send/receive** messages programmatically
- **Rich media** (images, videos, documents)
- **Interactive buttons** and lists
- **Template messages** (pre-approved)
- **Read receipts** and typing indicators
- **End-to-end encryption**

---

## 🚀 Quick Start

### Prerequisites

1. **Meta Business Account** - [Create here](https://business.facebook.com/)
2. **WhatsApp Business Account** - Link to Meta Business
3. **Phone Number** - Dedicated for business (not personal)
4. **Verified Business** - Complete business verification

### Setup Steps (30 minutes)

#### 1. Create Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Select "Business" type
4. Fill in app details
5. Add "WhatsApp" product

#### 2. Get Phone Number

1. In WhatsApp settings, click "Add Phone Number"
2. Choose "Use your own number" or "Get test number"
3. Verify phone number with SMS code
4. Copy **Phone Number ID**

#### 3. Get Access Token

1. Go to WhatsApp → API Setup
2. Copy **Temporary Access Token** (24h expiry)
3. For production: Generate **Permanent Token**
   - Go to System Users
   - Create system user
   - Generate token with `whatsapp_business_messaging` permission

#### 4. Configure Webhook

1. In WhatsApp settings, click "Configuration"
2. Set Callback URL: `https://dentaflow.ai/api/v1/whatsapp/webhook`
3. Set Verify Token: (your secret token)
4. Subscribe to: `messages`, `message_status`

#### 5. Test Integration

```bash
# Send test message
curl -X POST "https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "972501234567",
    "type": "text",
    "text": {
      "body": "Hello from DentaFlow!"
    }
  }'
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Add to .env
WHATSAPP_ACCESS_TOKEN=your-permanent-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_VERIFY_TOKEN=your-webhook-verify-token
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
```

### API Endpoints

```python
# backend/app/api/v1/endpoints/whatsapp.py

from fastapi import APIRouter, Request, HTTPException
from app.integrations.whatsapp_client import whatsapp_client
from app.services.conversation_manager import ConversationManager

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: str = Query(alias="hub.mode"),
    hub_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    """Verify WhatsApp webhook."""
    challenge = whatsapp_client.verify_webhook(
        mode=hub_mode,
        token=hub_token,
        challenge=hub_challenge,
        verify_token=settings.WHATSAPP_VERIFY_TOKEN
    )
    
    if challenge:
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming WhatsApp messages."""
    data = await request.json()
    
    # Process webhook
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            
            # Handle incoming message
            for message in value.get("messages", []):
                await handle_whatsapp_message(message, db)
            
            # Handle message status updates
            for status in value.get("stat

uses", []):
                await handle_message_status(status, db)
    
    return {"status": "ok"}

async def handle_whatsapp_message(message: dict, db: Session):
    """Process incoming WhatsApp message."""
    from_number = message["from"]
    message_type = message["type"]
    message_id = message["id"]
    
    # Mark as read
    await whatsapp_client.mark_message_as_read(message_id)
    
    # Get or create conversation
    manager = ConversationManager(db)
    conversation = manager.get_or_create_conversation(
        organization_id=org_id,  # Get from phone number mapping
        patient_phone=from_number,
        channel=ConversationChannel.WHATSAPP
    )
    
    # Extract message content
    if message_type == "text":
        content = message["text"]["body"]
    elif message_type == "button":
        content = message["button"]["text"]
    elif message_type == "interactive":
        content = message["interactive"]["button_reply"]["title"]
    else:
        content = f"[{message_type} message]"
    
    # Save user message
    manager.add_message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=content
    )
    
    # Process with agent
    response = await process_with_agent(conversation.id, content)
    
    # Send response
    await whatsapp_client.send_text_message(
        to=from_number,
        text=response
    )
    
    # Save assistant message
    manager.add_message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=response,
        agent_name="alex"
    )
```

---

## 💬 Message Types

### 1. Text Message

```python
await whatsapp_client.send_text_message(
    to="972501234567",
    text="שלום! איך אני יכול לעזור לך היום?",
    preview_url=True  # Enable URL preview
)
```

### 2. Interactive Buttons

```python
await whatsapp_client.send_interactive_message(
    to="972501234567",
    body_text="מה תרצה לעשות?",
    buttons=[
        {"id": "schedule", "title": "קבע תור"},
        {"id": "status", "title": "בדוק סטטוס"},
        {"id": "cancel", "title": "בטל תור"}
    ],
    header_text="DentaFlow",
    footer_text="מרפאת השיניים שלך"
)
```

### 3. List Message

```python
await whatsapp_client.send_list_message(
    to="972501234567",
    body_text="בחר תאריך לתור:",
    button_text="בחר תאריך",
    sections=[
        {
            "title": "השבוע",
            "rows": [
                {"id": "mon", "title": "יום שני", "description": "10/10/2025"},
                {"id": "tue", "title": "יום שלישי", "description": "11/10/2025"}
            ]
        },
        {
            "title": "השבוע הבא",
            "rows": [
                {"id": "next_mon", "title": "יום שני", "description": "17/10/2025"}
            ]
        }
    ]
)
```

### 4. Template Message

```python
# First, create template in Meta Business Manager
# Template name: "appointment_reminder"
# Template content: "שלום {{1}}, יש לך תור ב-{{2}} בשעה {{3}}"

await whatsapp_client.send_template_message(
    to="972501234567",
    template_name="appointment_reminder",
    language_code="he",
    components=[
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": "דוד"},
                {"type": "text", "text": "15/10/2025"},
                {"type": "text", "text": "10:00"}
            ]
        }
    ]
)
```

### 5. Media Message

```python
# Image
await whatsapp_client.send_media_message(
    to="972501234567",
    media_type="image",
    media_url="https://dentaflow.ai/images/clinic.jpg",
    caption="מרפאת DentaFlow"
)

# Document
await whatsapp_client.send_media_message(
    to="972501234567",
    media_type="document",
    media_url="https://dentaflow.ai/docs/treatment_plan.pdf",
    caption="תוכנית הטיפול שלך"
)
```

---

## 🎯 Use Cases

### Use Case 1: Appointment Booking

```python
async def book_appointment_flow(phone: str):
    """Complete appointment booking flow."""
    
    # Step 1: Greeting
    await whatsapp_client.send_text_message(
        to=phone,
        text="שלום! בואו נקבע תור. מה השם שלך?"
    )
    
    # Wait for user response...
    # name = get_user_response()
    
    # Step 2: Ask for date
    await whatsapp_client.send_list_message(
        to=phone,
        body_text=f"נעים מאוד {name}! באיזה תאריך תרצה להגיע?",
        button_text="בחר תאריך",
        sections=[...]  # Available dates
    )
    
    # Wait for selection...
    # date = get_user_selection()
    
    # Step 3: Confirm
    await whatsapp_client.send_interactive_message(
        to=phone,
        body_text=f"תור ל-{date}. האם לאשר?",
        buttons=[
            {"id": "confirm", "title": "אשר"},
            {"id": "cancel", "title": "בטל"}
        ]
    )
    
    # Step 4: Confirmation
    await whatsapp_client.send_text_message(
        to=phone,
        text="✅ התור נקבע בהצלחה! תקבל תזכורת 24 שעות לפני."
    )
```

### Use Case 2: Appointment Reminder

```python
async def send_appointment_reminder(phone: str, appointment: dict):
    """Send appointment reminder 24h before."""
    
    await whatsapp_client.send_template_message(
        to=phone,
        template_name="appointment_reminder",
        language_code="he",
        components=[
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": appointment["patient_name"]},
                    {"type": "text", "text": appointment["date"]},
                    {"type": "text", "text": appointment["time"]}
                ]
            },
            {
                "type": "button",
                "sub_type": "quick_reply",
                "index": "0",
                "parameters": [
                    {"type": "payload", "payload": f"confirm_{appointment['id']}"}
                ]
            }
        ]
    )
```

### Use Case 3: Treatment Plan Sharing

```python
async def share_treatment_plan(phone: str, plan_url: str):
    """Share treatment plan document."""
    
    await whatsapp_client.send_media_message(
        to=phone,
        media_type="document",
        media_url=plan_url,
        caption="הנה תוכנית הטיפול שלך. נשמח לענות על כל שאלה!"
    )
    
    await whatsapp_client.send_interactive_message(
        to=phone,
        body_text="יש לך שאלות על תוכנית הטיפול?",
        buttons=[
            {"id": "questions", "title": "יש לי שאלות"},
            {"id": "approve", "title": "אני מאשר"},
            {"id": "call", "title": "התקשר אלי"}
        ]
    )
```

---

## 🔒 Security

### Webhook Verification

```python
def verify_webhook(mode: str, token: str, challenge: str) -> Optional[str]:
    """Verify webhook is from WhatsApp."""
    
    verify_token = settings.WHATSAPP_VERIFY_TOKEN
    
    if mode == "subscribe" and token == verify_token:
        return challenge
    else:
        return None
```

### Message Validation

```python
def validate_whatsapp_signature(payload: bytes, signature: str) -> bool:
    """Validate webhook payload signature."""
    
    import hmac
    import hashlib
    
    app_secret = settings.WHATSAPP_APP_SECRET
    
    expected_signature = hmac.new(
        app_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

---

## 📊 Best Practices

### 1. Message Limits

- **Marketing messages**: Require template approval
- **Session messages**: 24h window after user message
- **Rate limits**: 80 messages/second per phone number

### 2. Template Guidelines

- **Keep short**: Max 1024 characters
- **Clear CTA**: Include clear call-to-action
- **Variables**: Use {{1}}, {{2}} for dynamic content
- **Language**: Submit in all target languages

### 3. User Experience

- **Response time**: Reply within 2 minutes
- **Rich media**: Use images/videos when helpful
- **Interactive**: Use buttons/lists for choices
- **Personalization**: Use user's name

---

## 🐛 Troubleshooting

### Issue: Messages not sending

**Cause:** Invalid phone number format

**Solution:**
```python
# ✅ Correct format (with country code, no + or -)
to = "972501234567"

# ❌ Wrong formats
to = "+972-50-123-4567"  # Has + and -
to = "0501234567"  # Missing country code
```

### Issue: Template rejected

**Cause:** Template doesn't follow guidelines

**Solution:**
- Avoid promotional language
- Don't include links in body
- Use clear, professional language
- Include opt-out option

### Issue: Webhook not receiving messages

**Cause:** Webhook not verified or wrong URL

**Solution:**
```bash
# Test webhook
curl "https://dentaflow.ai/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=CHALLENGE"

# Should return CHALLENGE
```

---

## 💰 Pricing

### WhatsApp Business API Costs

- **Conversation-based pricing** (not per message)
- **Business-initiated**: ~$0.05-0.10 per conversation
- **User-initiated**: Free for 24h session
- **Free tier**: 1000 conversations/month

### Cost Optimization

1. **Use user-initiated**: Respond within 24h window
2. **Batch notifications**: Group multiple updates
3. **Template efficiency**: Reuse approved templates
4. **Monitor usage**: Track conversation counts

---

## 📚 Additional Resources

- [WhatsApp Cloud API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Message Templates Guide](https://developers.facebook.com/docs/whatsapp/message-templates)
- [Interactive Messages](https://developers.facebook.com/docs/whatsapp/guides/interactive-messages)
- [Best Practices](https://developers.facebook.com/docs/whatsapp/guides/best-practices)

---

## ✅ Integration Checklist

- [ ] Create Meta Business Account
- [ ] Create WhatsApp Business Account
- [ ] Add phone number and verify
- [ ] Create Meta app
- [ ] Add WhatsApp product
- [ ] Get Phone Number ID
- [ ] Generate permanent access token
- [ ] Configure webhook URL
- [ ] Set verify token
- [ ] Subscribe to webhook events
- [ ] Test sending message
- [ ] Test receiving message
- [ ] Create message templates
- [ ] Submit templates for approval
- [ ] Implement conversation manager integration
- [ ] Test end-to-end flow
- [ ] Monitor message delivery
- [ ] Set up error alerts

---

**Last Updated:** October 8, 2025  
**Version:** 1.0  
**Status:** Ready for Implementation (Future)  
**Priority:** Medium (Currently using Telegram)

---

## 🎯 When to Implement

**Implement WhatsApp when:**
1. ✅ Telegram bot is stable and working
2. ✅ User base requests WhatsApp
3. ✅ Budget allocated for WhatsApp API costs
4. ✅ Team trained on WhatsApp Business Manager
5. ✅ Message templates prepared and approved

**Estimated effort:** 2-3 days for full integration
