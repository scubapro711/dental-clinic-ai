# Agent-Twilio Integration
## How AI Agents Use Twilio for Patient Communication

**Date:** October 11, 2025  
**Purpose:** Explain how Alex, Marcus, Sarah, and Sophia use Twilio to communicate with patients

---

## 🤖 Overview

The AI agents (Alex, Marcus, Sarah, Sophia) have **direct access to Twilio** through **tool calling**.

**How it works:**
1. Agent receives request (e.g., "remind patient about appointment")
2. Agent decides to use `send_sms_tool`
3. Agent calls tool with parameters
4. Tool sends SMS via Twilio
5. Tool returns result to agent
6. Agent responds to user with confirmation

---

## 🔧 Tool Architecture

### Tool Definition
**Location:** `backend/app/agents/tools/alex_communications_tools.py`

```python
def send_sms_tool(
    patient_id: int,
    template: str,
    clinic_id: int,
    custom_message: Optional[str] = None,
    template_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Send SMS to patient via Twilio.
    
    Features:
    - Template support for common messages
    - Hebrew RTL support
    - Delivery tracking
    - GDPR compliance (checks opt-out status)
    - Rate limiting (max 3 SMS per patient per day)
    """
```

### Agent Registration
**Location:** `backend/app/agents/alex_v2.py`

```python
from app.agents.tools.alex_communications_tools import (
    send_sms_tool,
    send_email_tool,
    send_telegram_message_tool,
)

class AlexAgent:
    def __init__(self):
        self.tools = [
            # ... other tools ...
            send_sms_tool,
            send_email_tool,
            send_telegram_message_tool,
            # ... more tools ...
        ]
        
        # Bind tools to LLM
        self.llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(self.tools)
```

---

## 📱 SMS Templates

### Available Templates

**1. Appointment Reminder**
```
שלום {patient_name},
תזכורת לתור שלך ב{clinic_name}:
📅 {date} בשעה {time}
👨‍⚕️ ד"ר {doctor_name}

לביטול/שינוי: {clinic_phone}
```

**2. Appointment Confirmation**
```
שלום {patient_name},
התור שלך אושר! ✅
📅 {date} בשעה {time}
👨‍⚕️ ד"ר {doctor_name}
📍 {clinic_address}

נתראה בקרוב!
```

**3. Payment Reminder**
```
שלום {patient_name},
תזכורת ידידותית:
יתרת חוב: ₪{amount}
לתשלום: {payment_link}

שאלות? {clinic_phone}
```

**4. Welcome Message**
```
שלום {patient_name}!
ברוכים הבאים ל{clinic_name} 🦷
אנחנו כאן בשבילך!

צוות {clinic_name}
```

**5. Custom Message**
- Agent can write any custom message

---

## 🎯 Example: Alex Sends Appointment Reminder

### User Request
```
User: "תזכיר למטופל 123 על התור שלו מחר"
```

### Agent Reasoning
```
Alex thinks:
1. User wants to remind patient 123 about appointment
2. I need to get appointment details first
3. Then I'll send SMS reminder
```

### Tool Calls

**Step 1: Get appointment details**
```python
get_patient_appointments(patient_id=123)
# Returns: {
#   "appointments": [{
#     "id": 456,
#     "date": "2025-10-12",
#     "time": "10:00",
#     "dentist": "Dr. Cohen",
#     "treatment": "Cleaning"
#   }]
# }
```

**Step 2: Send SMS**
```python
send_sms_tool(
    patient_id=123,
    template="appointment_reminder",
    clinic_id=1,
    template_vars={
        "clinic_name": "DentaFlow Clinic",
        "date": "12/10/2025",
        "time": "10:00",
        "doctor_name": "Cohen",
        "clinic_phone": "03-1234567"
    }
)
# Returns: {
#   "success": True,
#   "message_sid": "SM1234567890abcdef",
#   "status": "sent",
#   "cost": 0.15,
#   "confirmation": "SMS נשלח בהצלחה למטופל Shane גבע"
# }
```

### Agent Response
```
Alex: "שלחתי תזכורת SMS למטופל Shane גבע על התור שלו מחר ב-10:00 עם ד״ר Cohen. ההודעה נשלחה בהצלחה! ✅"
```

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Request                            │
│  "תזכיר למטופל 123 על התור שלו מחר"                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Alex Agent (LLM)                          │
│  - Understands request                                      │
│  - Plans tool calls                                         │
│  - Decides to use send_sms_tool                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              send_sms_tool (Python Function)                │
│  1. Get patient phone from Odoo                             │
│  2. Check opt-out status (GDPR)                             │
│  3. Fill template with variables                            │
│  4. Call Twilio API                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Twilio API                                │
│  - Sends SMS to patient phone                               │
│  - Returns message SID and status                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Patient's Phone                             │
│  📱 "שלום Shane, תזכורת לתור שלך..."                        │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Tool Returns Result to Agent                   │
│  {                                                          │
│    "success": true,                                         │
│    "message_sid": "SM123...",                               │
│    "confirmation": "SMS נשלח בהצלחה"                        │
│  }                                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Alex Responds to User                          │
│  "שלחתי תזכורת SMS למטופל Shane גבע..."                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Which Agents Can Send SMS?

### Alex (Reception & Patient Relations)
**Primary SMS user**
- ✅ Appointment reminders
- ✅ Appointment confirmations
- ✅ Welcome messages
- ✅ General communication
- ✅ Custom messages

**Example:**
```
User: "תזכיר לכל המטופלים של מחר על התורים שלהם"
Alex: *Uses send_sms_tool for each patient*
```

### Marcus (CFO)
**Financial SMS**
- ✅ Payment reminders
- ✅ Invoice notifications
- ✅ Payment confirmations
- ✅ Payment plan reminders

**Example:**
```
User: "תזכיר למטופלים עם חובות על התשלום"
Marcus: *Uses send_sms_tool with payment_reminder template*
```

### Sarah (Clinical Assistant)
**Clinical SMS** (less common)
- ⚠️ Lab results ready
- ⚠️ Prescription ready
- ⚠️ Follow-up reminders

**Note:** Sarah typically doesn't send SMS directly. She works through Alex.

### Sophia (Practice Administrator)
**Operational SMS**
- ⚠️ Clinic announcements
- ⚠️ Schedule changes
- ⚠️ Emergency notifications

**Note:** Sophia typically doesn't send SMS directly. She works through Alex.

---

## 🔐 Safety Features

### 1. GDPR Compliance
```python
# Check opt-out status before sending
if partner.get('sms_opt_out'):
    return {
        'success': False,
        'error': 'המטופל ביקש להסיר אותו מרשימת SMS',
        'suggestion': 'השתמש באימייל או Telegram במקום'
    }
```

### 2. Rate Limiting
```python
# Max 3 SMS per patient per day
# Prevents spam and reduces costs
```

### 3. Delivery Tracking
```python
# Log every SMS to Odoo
log_data = {
    'patient_id': patient_id,
    'message_type': 'sms',
    'template': template,
    'message_content': message,
    'recipient_phone': phone,
    'status': twilio_message.status,
    'external_id': twilio_message.sid,
    'sent_at': datetime.now(),
}
odoo.create('medical.patient.communication', log_data)
```

### 4. Error Handling
```python
# If Twilio fails, suggest alternatives
if not TWILIO_AVAILABLE:
    return {
        'success': False,
        'error': 'שירות SMS לא זמין',
        'fallback': 'השתמש באימייל או Telegram'
    }
```

---

## 💡 Proactive SMS (Automated)

### Scenario: Appointment Tomorrow

**Trigger:** Cron job runs daily at 9:00 AM

**Process:**
1. System finds all appointments for tomorrow
2. For each appointment:
   - Call Alex agent with context
   - Alex uses `send_sms_tool` to send reminder
   - Alex logs the action

**Code:**
```python
# Cron job (runs daily)
async def send_appointment_reminders():
    tomorrow = date.today() + timedelta(days=1)
    appointments = get_appointments_for_date(tomorrow)
    
    for apt in appointments:
        # Call Alex agent
        alex = AlexAgent()
        result = alex.process({
            "messages": [{
                "role": "system",
                "content": f"Send appointment reminder to patient {apt.patient_id} for appointment on {apt.date} at {apt.time}"
            }]
        })
        
        # Alex will use send_sms_tool automatically
```

---

## 🎨 Patient Portal Integration

### How Patients See SMS Activity

**Dashboard:**
```
┌─────────────────────────────────────────┐
│ Recent Communications                   │
├─────────────────────────────────────────┤
│ 📱 SMS - Oct 11, 10:30                  │
│    "תזכורת לתור שלך מחר..."             │
│    Status: Delivered ✅                 │
│                                         │
│ 📱 SMS - Oct 10, 14:20                  │
│    "התור שלך אושר!"                     │
│    Status: Delivered ✅                 │
└─────────────────────────────────────────┘
```

**Profile Page - Communication Preferences:**
```
┌─────────────────────────────────────────┐
│ SMS Notifications                       │
├─────────────────────────────────────────┤
│ ☑ Receive SMS notifications            │
│ ☐ Opt out of SMS (GDPR)                │
│                                         │
│ Phone: +972-50-123-4567                 │
│ [Update Phone]                          │
│                                         │
│ SMS sent this month: 5                  │
│ Last SMS: Oct 11, 10:30                 │
└─────────────────────────────────────────┘
```

**Communication History Page:**
```
┌─────────────────────────────────────────┐
│ All Communications                      │
├─────────────────────────────────────────┤
│ Filters: [All ▼] [SMS ▼] [Last 30 days]│
├─────────────────────────────────────────┤
│ 📱 Oct 11, 10:30 - SMS                  │
│    From: Alex                           │
│    "תזכורת לתור שלך מחר..."             │
│    Status: Delivered ✅                 │
│    [View Details]                       │
├─────────────────────────────────────────┤
│ 📱 Oct 10, 14:20 - SMS                  │
│    From: Alex                           │
│    "התור שלך אושר!"                     │
│    Status: Delivered ✅                 │
│    [View Details]                       │
└─────────────────────────────────────────┘
```

---

## 📊 Analytics & Monitoring

### SMS Metrics (for Clinic)

**Dashboard for Clinic Staff:**
```
SMS Statistics (This Month)
├─ Total Sent: 1,234
├─ Delivered: 1,198 (97%)
├─ Failed: 36 (3%)
├─ Cost: ₪185
└─ Opt-outs: 12

By Type:
├─ Appointment Reminders: 856 (69%)
├─ Appointment Confirmations: 234 (19%)
├─ Payment Reminders: 98 (8%)
└─ Other: 46 (4%)

By Agent:
├─ Alex: 1,090 (88%)
├─ Marcus: 98 (8%)
├─ Sarah: 34 (3%)
└─ Sophia: 12 (1%)
```

---

## 🚀 Future Enhancements

### 1. Two-Way SMS (Incoming)
**Feature:** Patients can reply to SMS
**How:**
- Twilio webhook receives incoming SMS
- System routes to appropriate agent
- Agent processes and responds

**Example:**
```
Patient: "אני רוצה לבטל את התור"
→ Twilio webhook
→ Alex agent
→ Alex cancels appointment
→ Alex sends confirmation SMS
```

### 2. Rich SMS (MMS)
**Feature:** Send images, PDFs
**Use cases:**
- X-ray images
- Treatment plans
- Invoices

### 3. SMS Campaigns
**Feature:** Bulk SMS to patient segments
**Use cases:**
- "Cleaning season reminder"
- "New services announcement"
- "Holiday greetings"

### 4. SMS Analytics
**Feature:** Track engagement
**Metrics:**
- Open rate (read receipts)
- Click-through rate (links)
- Response rate
- Conversion rate (bookings)

---

## ✅ Summary

**How Agents Use Twilio:**
1. ✅ Agents have `send_sms_tool` in their toolkit
2. ✅ Agents decide when to send SMS based on context
3. ✅ Agents call tool with parameters (patient, template, vars)
4. ✅ Tool sends SMS via Twilio API
5. ✅ Tool returns result to agent
6. ✅ Agent confirms to user

**Key Benefits:**
- 🤖 **Autonomous:** Agents decide when to send SMS
- 🎯 **Contextual:** Messages are personalized
- 🔒 **Safe:** GDPR compliant, rate limited
- 📊 **Tracked:** Every SMS is logged
- 🌍 **Multi-channel:** SMS + Email + Telegram + WhatsApp

**This is true AI-powered communication!**

---

**Document Owner:** AI Development Team  
**Last Updated:** October 11, 2025  
**Version:** 1.0  
**Status:** ✅ Complete

