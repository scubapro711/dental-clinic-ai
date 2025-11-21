# Communication Modules Inventory
## Existing Communication Infrastructure

**Date:** October 11, 2025  
**Purpose:** Document existing communication modules and their integration with Patient Portal

---

## ✅ Existing Communication Modules

### 1. SMS Service (`sms_service.py`)
**Status:** ✅ Fully Implemented  
**Provider:** AWS SNS (production) / Console (development)  
**Features:**
- ✅ Send verification codes (6-digit)
- ✅ Send 2FA codes for login
- ✅ Israeli phone number formatting (+972)
- ✅ Hebrew message support
- ✅ E.164 format conversion
- ✅ Transactional SMS type (for OTP)

**Use Cases:**
- Phone verification during registration
- 2FA login codes
- **Can be used for:** Appointment reminders, payment reminders

**API:**
```python
await sms_service.send_verification_code(
    phone_number="+972501234567",
    code="123456",
    user_name="שרה"
)
```

**Integration with Patient Portal:**
- ✅ Use for appointment reminders
- ✅ Use for payment due reminders
- ✅ Use for lab results ready notifications
- ✅ Use for prescription ready notifications

---

### 2. Telegram Service (`telegram_service.py`)
**Status:** ✅ Fully Implemented  
**Provider:** Telegram Bot API  
**Features:**
- ✅ User management (get_or_create_user)
- ✅ Patient linking (link_to_patient)
- ✅ New patient creation (create_patient_and_link)
- ✅ Invite code validation
- ✅ Conversation management
- ✅ Onboarding flow

**Database Models:**
- `TelegramUser` - Telegram user info + patient link
- `TelegramConversation` - Chat conversations
- `TelegramInviteCode` - Organization invite codes

**Use Cases:**
- Telegram bot for patient communication
- Onboarding new patients via Telegram
- Chat with agents via Telegram

**Integration with Patient Portal:**
- ✅ Link Telegram account from Profile page
- ✅ Show Telegram status in Profile
- ✅ Option to receive notifications via Telegram
- ✅ "Chat on Telegram" button (if linked)

---

### 3. WhatsApp Client (`whatsapp_client.py`)
**Status:** ✅ Implemented (needs verification)  
**Provider:** WhatsApp Business API  
**Features:** (to be verified)
- Message sending
- Template messages
- Media messages

**Use Cases:**
- WhatsApp notifications (very popular in Israel!)
- Chat with agents via WhatsApp
- Appointment reminders via WhatsApp

**Integration with Patient Portal:**
- ⚠️ Need to verify implementation
- ⚠️ Need to check if active
- ✅ Link WhatsApp account from Profile page
- ✅ Option to receive notifications via WhatsApp

---

### 4. Email Service (`email_service.py`)
**Status:** ✅ Implemented (needs verification)  
**Provider:** (to be determined - likely SendGrid or AWS SES)  
**Features:** (to be verified)
- Send emails
- HTML templates
- Attachments

**Use Cases:**
- Email notifications
- Invoice delivery
- Medical records delivery
- Appointment confirmations

**Integration with Patient Portal:**
- ✅ Use for appointment confirmations
- ✅ Use for invoice delivery
- ✅ Use for medical records delivery
- ✅ Use for password reset

---

## 🎯 Integration Strategy for Patient Portal

### Notification Preferences (Profile Page)

**User can choose preferred channels:**
```
Notification Preferences:
┌─────────────────────────────────────────┐
│ Appointment Reminders:                  │
│ ☑ SMS                                   │
│ ☑ Email                                 │
│ ☐ Telegram (Link account)              │
│ ☐ WhatsApp (Link account)              │
│                                         │
│ Timing: 24 hours before [▼]            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Payment Reminders:                      │
│ ☑ SMS                                   │
│ ☑ Email                                 │
│ ☐ Telegram                              │
│ ☐ WhatsApp                              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Lab Results Ready:                      │
│ ☑ SMS                                   │
│ ☑ Email                                 │
│ ☐ Telegram                              │
│ ☐ WhatsApp                              │
└─────────────────────────────────────────┘
```

### Telegram Linking Flow

**1. Profile Page - Telegram Section:**
```
┌─────────────────────────────────────────┐
│ Telegram Integration                    │
├─────────────────────────────────────────┤
│ Status: Not Connected                   │
│                                         │
│ Connect your Telegram account to:      │
│ • Receive notifications on Telegram    │
│ • Chat with Alex via Telegram          │
│ • Quick appointment booking             │
│                                         │
│ [Connect Telegram Account]              │
└─────────────────────────────────────────┘
```

**2. After clicking "Connect":**
- Show QR code
- Show link: t.me/DentaFlowBot?start={unique_code}
- User scans QR or clicks link
- Bot sends verification message
- User confirms
- Account linked!

**3. After linking:**
```
┌─────────────────────────────────────────┐
│ Telegram Integration                    │
├─────────────────────────────────────────┤
│ Status: ✅ Connected                    │
│ Account: @username                      │
│ Linked: Oct 11, 2025                    │
│                                         │
│ [Open Telegram Chat]                    │
│ [Disconnect]                            │
└─────────────────────────────────────────┘
```

### WhatsApp Linking Flow

**Similar to Telegram:**
- QR code or link
- WhatsApp Business API
- Verification message
- Account linked

---

## 📋 Implementation Tasks for Patient Portal

### Phase 1: SMS Integration (Immediate)
**Priority:** HIGH  
**Effort:** LOW (already implemented)

**Tasks:**
1. ✅ Add notification preferences to Profile page
2. ✅ Add SMS toggle for each notification type
3. ✅ Use existing `sms_service` to send notifications
4. ✅ Implement appointment reminder job (cron)
5. ✅ Implement payment reminder job (cron)

**Endpoints:**
- `PUT /api/v1/patient/notification-preferences`
- `POST /api/v1/notifications/send-sms` (internal)

---

### Phase 2: Telegram Integration (High Priority)
**Priority:** HIGH  
**Effort:** MEDIUM

**Tasks:**
1. ✅ Add Telegram section to Profile page
2. ✅ Generate unique linking code
3. ✅ Show QR code + link
4. ✅ Handle Telegram webhook for verification
5. ✅ Update user status when linked
6. ✅ Send notifications via Telegram
7. ✅ "Chat on Telegram" button in portal

**Endpoints:**
- `POST /api/v1/telegram/generate-link-code`
- `GET /api/v1/telegram/link-status`
- `DELETE /api/v1/telegram/unlink`
- `POST /api/v1/telegram/send-notification` (internal)

**Bot Commands:**
- `/start {code}` - Link account
- `/appointments` - View appointments
- `/book` - Book appointment
- `/pay` - Pay invoice
- `/help` - Help menu

---

### Phase 3: WhatsApp Integration (Medium Priority)
**Priority:** MEDIUM  
**Effort:** MEDIUM-HIGH

**Tasks:**
1. ⚠️ Verify WhatsApp client implementation
2. ⚠️ Set up WhatsApp Business API
3. ✅ Add WhatsApp section to Profile page
4. ✅ Generate unique linking code
5. ✅ Show QR code + link
6. ✅ Handle WhatsApp webhook for verification
7. ✅ Send notifications via WhatsApp
8. ✅ "Chat on WhatsApp" button in portal

**Endpoints:**
- `POST /api/v1/whatsapp/generate-link-code`
- `GET /api/v1/whatsapp/link-status`
- `DELETE /api/v1/whatsapp/unlink`
- `POST /api/v1/whatsapp/send-notification` (internal)

---

### Phase 4: Email Integration (Low Priority)
**Priority:** LOW  
**Effort:** LOW

**Tasks:**
1. ⚠️ Verify email service implementation
2. ✅ Add email templates (HTML)
3. ✅ Send appointment confirmations
4. ✅ Send invoice emails (with PDF)
5. ✅ Send medical records (with PDF)
6. ✅ Send password reset emails

**Endpoints:**
- `POST /api/v1/email/send-appointment-confirmation` (internal)
- `POST /api/v1/email/send-invoice` (internal)
- `POST /api/v1/email/send-medical-records` (internal)

---

## 🚀 Recommended Implementation Order

### Week 1: SMS Notifications
1. Add notification preferences UI
2. Implement appointment reminders (SMS)
3. Implement payment reminders (SMS)
4. Test with real phone numbers

### Week 2: Telegram Integration
1. Add Telegram linking UI
2. Implement linking flow
3. Send notifications via Telegram
4. Implement basic bot commands
5. Test end-to-end

### Week 3: WhatsApp Integration
1. Verify WhatsApp client
2. Set up WhatsApp Business API
3. Add WhatsApp linking UI
4. Implement linking flow
5. Send notifications via WhatsApp

### Week 4: Email & Polish
1. Verify email service
2. Create email templates
3. Send appointment confirmations
4. Send invoices via email
5. Polish all notification flows

---

## 📊 Notification Matrix

| Notification Type | SMS | Email | Telegram | WhatsApp | Priority |
|-------------------|-----|-------|----------|----------|----------|
| Appointment Reminder (24h) | ✅ | ✅ | ✅ | ✅ | HIGH |
| Appointment Confirmation | ✅ | ✅ | ✅ | ✅ | HIGH |
| Appointment Cancelled | ✅ | ✅ | ✅ | ✅ | HIGH |
| Payment Due | ✅ | ✅ | ✅ | ✅ | HIGH |
| Payment Received | ✅ | ✅ | ✅ | ✅ | MEDIUM |
| Lab Results Ready | ✅ | ✅ | ✅ | ✅ | HIGH |
| Prescription Ready | ✅ | ✅ | ✅ | ✅ | MEDIUM |
| Health Score Update | ❌ | ✅ | ✅ | ✅ | LOW |
| Preventive Care Reminder | ✅ | ✅ | ✅ | ✅ | MEDIUM |
| Clinic Announcement | ❌ | ✅ | ✅ | ✅ | LOW |

**Legend:**
- ✅ Recommended
- ❌ Not recommended (too much noise)

---

## 🔐 Security & Privacy

### Data Protection
- ✅ Phone numbers encrypted at rest
- ✅ Telegram IDs encrypted at rest
- ✅ WhatsApp IDs encrypted at rest
- ✅ User can unlink at any time
- ✅ User can disable notifications at any time

### Compliance
- ✅ GDPR compliant (user consent required)
- ✅ Israeli privacy laws compliant
- ✅ Opt-in for marketing messages
- ✅ Opt-out available for all messages

### Rate Limiting
- ✅ Max 10 SMS per day per user
- ✅ Max 50 Telegram messages per day per user
- ✅ Max 50 WhatsApp messages per day per user
- ✅ No limit on email (but throttled)

---

## 💡 Future Enhancements

### Voice Calls (Future)
- Appointment reminder voice calls
- IVR for appointment booking
- Voice messages from agents

### Push Notifications (Mobile App)
- Native mobile app push notifications
- Rich notifications with actions
- Silent notifications for background sync

### In-App Notifications (Portal)
- Bell icon with notification count
- Notification center (dropdown)
- Mark as read/unread
- Archive notifications

---

**Document Owner:** AI Development Team  
**Last Updated:** October 11, 2025  
**Version:** 1.0  
**Status:** ✅ Ready for Integration

