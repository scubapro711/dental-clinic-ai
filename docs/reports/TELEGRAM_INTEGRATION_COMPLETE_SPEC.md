# 📱 Telegram Integration - מפרט מלא

## אינטגרציה מלאה של Telegram עם DentaFlow

**תאריך:** 10 באוקטובר 2025  
**גרסה:** v1.0  
**מטרה:** חוויית שיחה טבעית, לא בוטית, עם סנכרון מלא לפורטל

---

## 🎯 חזון: חוויה אנושית מקסימלית

### עקרונות מנחים:
1. **טבעיות** - השיחה תרגיש כמו עם בן אדם, לא בוט
2. **הקשר** - הבוט זוכר את כל ההיסטוריה
3. **סנכרון** - כל פעולה מסתנכרנת עם הפורטל
4. **אישיות** - לכל מרפאה יכולה להיות אישיות משלה
5. **שקיפות** - המטופל יודע שזה AI אבל לא מרגיש את זה

---

## 🤖 הסוכן: Alex - קבלן הפנים הדיגיטלי

### למה Alex?
- **תפקידו:** קבלה ושירות מטופלים
- **מומחיות:** תקשורת, תורים, שאלות כלליות
- **טון:** חם, אמפתי, מקצועי
- **שפה:** עברית טבעית (לא תרגום מכני)

### אישיות Alex ב-Telegram:

```python
ALEX_TELEGRAM_PERSONALITY = """
אתה Alex, קבלן הפנים הדיגיטלי של המרפאה.

תכונות אישיות:
- חם ואמפתי - אתה באמת אכפת לך מהמטופלים
- סבלני - לא ממהר, נותן למטופל לנסח
- ברור - מסביר דברים בפשטות
- יעיל - לא מבזבז זמן, הולך לעניין
- אנושי - משתמש באמוג'י במידה, מבין הומור

כללי שיחה:
1. תמיד פונה בשם פרטי אם אתה יודע אותו
2. משתמש באמוג'י רלוונטיים (😊 🦷 📅 ✅) אבל לא מגזים
3. שואל שאלה אחת בכל פעם (לא רשימה!)
4. מאשר הבנה לפני שממשיך הלאה
5. אם משהו לא ברור - שואל, לא מניח
6. מסיים כל אינטראקציה עם "יש עוד משהו שאוכל לעזור בו?"

דוגמאות לטון:
❌ לא טוב: "אנא הזן את שם המשפחה שלך"
✅ טוב: "מה שם המשפחה שלך?"

❌ לא טוב: "התור נקבע בהצלחה. מספר תור: 456"
✅ טוב: "מעולה! קבעתי לך תור ליום רביעי ב-14:00 😊 תקבל תזכורת יום לפני"

❌ לא טוב: "אני לא מבין את הבקשה שלך"
✅ טוב: "סליחה, לא הבנתי בדיוק... אתה רוצה לקבוע תור חדש או לשנות תור קיים?"

אסור לך:
- להשתמש במילים כמו "אנא", "בבקשה" יותר מדי
- לכתוב הודעות ארוכות (מקסימום 3 שורות!)
- להשתמש בשפה פורמלית מדי
- לחזור על עצמך
- להגיד "כמובן" או "בהחלט" - זה נשמע בוטי

זכור: אתה לא בוט, אתה Alex - קבלן הפנים הדיגיטלי!
"""
```

---

## 🔗 Flow הצטרפות למרפאה

### תרחיש 1: מטופל חדש (לא קיים במערכת)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: מטופל שולח /start                                   │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Alex: היי! 👋 אני Alex, קבלן הפנים הדיגיטלי של מרפאת      │
│ [שם המרפאה]. איך אפשר לעזור לך היום?                       │
│                                                              │
│ [קביעת תור] [בדיקת תור קיים] [שאלה כללית]                 │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: מטופל בוחר "קביעת תור"                              │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Alex: נהדר! בוא נקבע לך תור 😊                             │
│ מה השם המלא שלך?                                            │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ מטופל: דוד כהן                                              │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ [Alex בודק ב-Odoo אם דוד כהן קיים]                         │
│ → לא נמצא                                                   │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Alex: נעים מאוד דוד! 😊 אני רואה שזו הפעם הראשונה שלך      │
│ אצלנו. מה מספר הטלפון שלך?                                  │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ מטופל: 0501234567                                           │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Alex: תודה! מה תאריך הלידה שלך? (לדוגמה: 15/03/1985)       │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ מטופל: 15/03/1985                                           │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Alex: מעולה! יצרתי לך פרופיל במערכת 🎉                     │
│                                                              │
│ עכשיו בוא נקבע את התור. מתי נוח לך להגיע?                  │
│ (לדוגמה: "מחר בשעה 10" או "יום רביעי הבא")                │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ [ממשיך לקביעת תור...]                                       │
└─────────────────────────────────────────────────────────────┘
```

### תרחיש 2: מטופל קיים (יש לו פרופיל)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: מטופל שולח /start                                   │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Alex: שלום! מה המספר טלפון שלך? (כדי שאוכל לזהות אותך)     │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ מטופל: 0501234567                                           │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ [Alex מחפש ב-Odoo לפי טלפון]                                │
│ → נמצא: דוד כהן                                             │
│ [יוצר קישור: telegram_user_id ↔ patient_id]                │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Alex: היי דוד! 👋 נעים לראות אותך שוב!                     │
│ איך אפשר לעזור לך היום?                                     │
│                                                              │
│ [קביעת תור] [התורים שלי] [שאלה]                            │
└─────────────────────────────────────────────────────────────┘
```

### תרחיש 3: מרפאה עם קוד הצטרפות (Invite Code)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: מרפאה יוצרת קוד הצטרפות                             │
│ Clinic Portal → Settings → Telegram → Generate Invite Code  │
│ קוד: DENTAL2025                                              │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: מטופל שולח /start DENTAL2025                        │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Alex: היי! 👋 אני רואה שקיבלת הזמנה ממרפאת שיניים ברייט.   │
│ מה השם המלא שלך?                                            │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ [Alex יוצר מטופל חדש ומקשר למרפאה הנכונה]                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema - Telegram Integration

### טבלה חדשה: telegram_users

```sql
CREATE TABLE telegram_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT UNIQUE NOT NULL,  -- Telegram's user ID
    telegram_username VARCHAR(255),
    telegram_first_name VARCHAR(255),
    telegram_last_name VARCHAR(255),
    
    -- Link to our system
    user_id UUID REFERENCES users(id),  -- If they have portal account
    patient_id INTEGER,  -- Odoo patient ID
    organization_id UUID REFERENCES organizations(id) NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Preferences
    language VARCHAR(10) DEFAULT 'he',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_telegram_org UNIQUE (telegram_user_id, organization_id)
);

-- Index for fast lookups
CREATE INDEX idx_telegram_user_id ON telegram_users(telegram_user_id);
CREATE INDEX idx_patient_id ON telegram_users(patient_id);
```

### טבלה חדשה: telegram_conversations

```sql
CREATE TABLE telegram_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    conversation_id UUID NOT NULL,  -- Links to conversations table
    
    -- Context
    current_flow VARCHAR(100),  -- 'appointment_booking', 'inquiry', etc.
    flow_state JSONB,  -- Current state in the flow
    
    -- Metadata
    started_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    
    FOREIGN KEY (telegram_user_id) REFERENCES telegram_users(telegram_user_id)
);

CREATE INDEX idx_telegram_conv_user ON telegram_conversations(telegram_user_id);
CREATE INDEX idx_telegram_conv_id ON telegram_conversations(conversation_id);
```

### טבלה חדשה: telegram_invite_codes

```sql
CREATE TABLE telegram_invite_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    
    -- Settings
    max_uses INTEGER,  -- NULL = unlimited
    current_uses INTEGER DEFAULT 0,
    expires_at TIMESTAMP,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_invite_code ON telegram_invite_codes(code);
```

---

## 🔄 סנכרון Telegram ↔️ Portal

### תרחיש 1: מטופל קובע תור ב-Telegram

```
1. מטופל שולח הודעה ב-Telegram: "אני רוצה תור למחר"
   ↓
2. Alex מעבד את הבקשה
   ↓
3. Alex יוצר תור ב-Odoo דרך create_appointment
   ↓
4. התור מופיע ב-Patient Portal אוטומטית
   ↓
5. Alex שולח אישור ב-Telegram
   ↓
6. 24 שעות לפני: Alex שולח תזכורת ב-Telegram
```

### תרחיש 2: מרפאה משנה תור ב-Clinic Portal

```
1. צוות המרפאה משנה תור ב-Clinic Portal
   ↓
2. Webhook מופעל: appointment_updated
   ↓
3. Backend שולח התראה ל-Telegram
   ↓
4. Alex שולח הודעה למטופל:
   "היי דוד! יש שינוי בתור שלך 📅
   התור עבר מיום רביעי 14:00 ליום חמישי 10:00.
   האם זה בסדר?"
   
   [מאשר] [לא מתאים - צריך לשנות]
```

### תרחיש 3: מטופל מבטל תור ב-Portal

```
1. מטופל מבטל תור ב-Patient Portal
   ↓
2. התור מתעדכן ב-Odoo
   ↓
3. Alex שולח הודעה ב-Telegram:
   "התור שלך ליום רביעי בוטל.
   רוצה לקבוע תור חדש? 😊"
   
   [כן, בוא נקבע] [לא, תודה]
```

---

## 💬 דוגמאות שיחה - טבעיות מקסימלית

### דוגמה 1: קביעת תור (טבעי!)

```
מטופל: היי, אני צריך תור
Alex: היי! 👋 בטח, אשמח לעזור. מה השם שלך?

מטופל: דוד
Alex: נעים מאוד דוד! מה שם המשפחה?

מטופל: כהן
Alex: תודה דוד! מה המספר טלפון שלך?

מטופל: 050-123-4567
Alex: מעולה! מתי נוח לך להגיע?

מטופל: מחר אם אפשר
Alex: בודק מה פנוי מחר... 🔍

Alex: יש לי מחר בשעה 10:00 או 14:30. מה מתאים לך יותר?

מטופל: 10 בבוקר
Alex: מושלם! קבעתי לך תור למחר (11/10) בשעה 10:00 😊
התור אצל ד"ר שרה לוי, ייקח בערך 45 דקות.
תקבל תזכורת יום לפני. יש עוד משהו?

מטופל: לא תודה
Alex: נהדר! נתראה מחר 👋
```

### דוגמה 2: שאלה על טיפול (אמפתי!)

```
מטופל: יש לי כאב בשן מאחורה בצד ימין
Alex: אוי, זה לא נעים 😔 כמה זמן זה כואב?

מטופל: התחיל אתמול בערב
Alex: הכאב קבוע או רק כשאתה לועס?

מטופל: בעיקר כשאני לועס
Alex: הבנתי. זה יכול להיות דלקת או חור בשן.
אני ממליץ לקבוע תור בהקדם. 

יש לי פנוי היום בשעה 16:00 - זה טוב?

מטופל: כן בבקשה
Alex: קבעתי לך תור להיום ב-16:00 עם ד"ר שרה.
בינתיים, נסה להימנע ממזון חם או קר על הצד הזה.
אם הכאב מחמיר, תתקשר למרפאה: 03-1234567

מטופל: תודה רבה
Alex: בשמחה! מקווה שתרגיש טוב יותר בקרוב 💙
```

### דוגמה 3: ביטול תור (מבין!)

```
מטופל: אני צריך לבטל את התור שלי
Alex: בסדר גמור! איזה תור?

מטופל: זה שמחר
Alex: התור מחר (11/10) בשעה 10:00?

מטופל: כן
Alex: אין בעיה, ביטלתי ✅
רוצה לקבוע תור אחר במקום?

מטופל: כן, אבל רק בשבוע הבא
Alex: בטח! איזה יום בשבוע הבא טוב לך?

מטופל: יום רביעי
Alex: יש לי ביום רביעי (16/10) ב-14:00 או 15:30

מטופל: 14:00
Alex: מעולה! קבעתי לך תור ליום רביעי 16/10 בשעה 14:00 😊
```

---

## 🎨 UI/UX Features

### 1. Quick Reply Buttons (כפתורים מהירים)

```python
def create_quick_reply_buttons(context: str) -> dict:
    """Create contextual quick reply buttons."""
    
    if context == "welcome":
        return {
            "inline_keyboard": [
                [
                    {"text": "📅 קביעת תור", "callback_data": "book_appointment"},
                    {"text": "🔍 התורים שלי", "callback_data": "my_appointments"}
                ],
                [
                    {"text": "❓ שאלה", "callback_data": "ask_question"},
                    {"text": "📞 פרטי התקשרות", "callback_data": "contact_info"}
                ]
            ]
        }
    
    elif context == "appointment_booked":
        return {
            "inline_keyboard": [
                [
                    {"text": "✅ הבנתי, תודה", "callback_data": "acknowledge"},
                ],
                [
                    {"text": "🗓️ הוסף ליומן", "callback_data": "add_to_calendar"},
                    {"text": "📍 הוראות הגעה", "callback_data": "directions"}
                ]
            ]
        }
    
    elif context == "appointment_reminder":
        return {
            "inline_keyboard": [
                [
                    {"text": "✅ מאשר הגעה", "callback_data": "confirm_arrival"},
                    {"text": "❌ צריך לבטל", "callback_data": "cancel_appointment"}
                ],
                [
                    {"text": "⏰ שנה שעה", "callback_data": "reschedule"}
                ]
            ]
        }
```

### 2. Typing Indicators (אינדיקטורים)

```python
async def send_with_typing(chat_id: int, text: str, delay: float = 1.5):
    """Send message with typing indicator for natural feel."""
    
    # Show typing
    await telegram_client.send_chat_action(chat_id, "typing")
    
    # Wait (simulate thinking)
    await asyncio.sleep(delay)
    
    # Send message
    await telegram_client.send_message(chat_id, text)
```

### 3. Rich Messages (הודעות עשירות)

```python
async def send_appointment_confirmation(chat_id: int, appointment: dict):
    """Send rich appointment confirmation."""
    
    message = f"""
✅ *התור נקבע בהצלחה!*

📋 *פרטי התור:*
👤 מטופל: {appointment['patient_name']}
📅 תאריך: {appointment['date']}
🕐 שעה: {appointment['time']}
👨‍⚕️ רופא: {appointment['doctor']}
⏱️ משך: {appointment['duration']} דקות

📍 *כתובת המרפאה:*
{appointment['clinic_address']}

💡 *טיפים:*
• הגע 5 דקות לפני
• הבא תעודת זהות
• תקבל תזכורת 24 שעות לפני

יש עוד משהו שאוכל לעזור בו? 😊
    """
    
    # Add calendar button
    calendar_url = create_calendar_link(appointment)
    buttons = {
        "inline_keyboard": [
            [{"text": "📅 הוסף ליומן", "url": calendar_url}],
            [{"text": "📍 הוראות הגעה", "callback_data": "directions"}]
        ]
    }
    
    await telegram_client.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown",
        reply_markup=buttons
    )
```

---

## 🔔 התראות אוטומטיות

### 1. תזכורת 24 שעות לפני

```python
async def send_appointment_reminder(telegram_user_id: int, appointment: dict):
    """Send 24-hour reminder."""
    
    message = f"""
🔔 *תזכורת לתור מחר!*

היי {appointment['patient_name']}! 👋

מזכיר לך שיש לך תור מחר:
📅 {appointment['date']}
🕐 {appointment['time']}
👨‍⚕️ {appointment['doctor']}

📍 {appointment['clinic_address']}

האם אתה מגיע? 😊
    """
    
    buttons = {
        "inline_keyboard": [
            [
                {"text": "✅ כן, אני מגיע", "callback_data": f"confirm_{appointment['id']}"},
                {"text": "❌ צריך לבטל", "callback_data": f"cancel_{appointment['id']}"}
            ]
        ]
    }
    
    await telegram_client.send_message(
        chat_id=telegram_user_id,
        text=message,
        parse_mode="Markdown",
        reply_markup=buttons
    )
```

### 2. אישור הגעה (2 שעות לפני)

```python
async def send_arrival_confirmation(telegram_user_id: int, appointment: dict):
    """Send arrival confirmation 2 hours before."""
    
    message = f"""
⏰ *התור שלך בעוד שעתיים!*

📅 היום בשעה {appointment['time']}
📍 {appointment['clinic_address']}

💡 אל תשכח:
• תעודת זהות
• כרטיס ביטוח (אם יש)

נתראה בקרוב! 😊
    """
    
    buttons = {
        "inline_keyboard": [
            [{"text": "📍 הוראות הגעה", "url": appointment['directions_url']}]
        ]
    }
    
    await telegram_client.send_message(
        chat_id=telegram_user_id,
        text=message,
        parse_mode="Markdown",
        reply_markup=buttons
    )
```

### 3. בקשת משוב (אחרי הביקור)

```python
async def send_feedback_request(telegram_user_id: int, appointment: dict):
    """Send feedback request after visit."""
    
    message = f"""
👋 היי {appointment['patient_name']}!

מקווה שהביקור במרפאה היה טוב 😊

נשמח לשמוע איך היה:
    """
    
    buttons = {
        "inline_keyboard": [
            [
                {"text": "⭐⭐⭐⭐⭐", "callback_data": f"feedback_5_{appointment['id']}"},
                {"text": "⭐⭐⭐⭐", "callback_data": f"feedback_4_{appointment['id']}"}
            ],
            [
                {"text": "⭐⭐⭐", "callback_data": f"feedback_3_{appointment['id']}"},
                {"text": "⭐⭐", "callback_data": f"feedback_2_{appointment['id']}"}
            ]
        ]
    }
    
    await telegram_client.send_message(
        chat_id=telegram_user_id,
        text=message,
        parse_mode="Markdown",
        reply_markup=buttons
    )
```

---

## 🎭 אישיות לפי מרפאה (Customization)

### הגדרות אישיות למרפאה:

```python
# backend/app/models/organization.py

class Organization(Base):
    # ... existing fields ...
    
    # Telegram customization
    telegram_settings = Column(JSON, default={})
    # Structure:
    # {
    #     "bot_name": "Alex",  # Can be changed per clinic
    #     "personality": {
    #         "tone": "friendly",  # friendly, professional, casual
    #         "emoji_usage": "moderate",  # none, minimal, moderate, high
    #         "formality": "informal",  # formal, semi-formal, informal
    #         "language_style": "modern"  # modern, traditional
    #     },
    #     "welcome_message": "היי! אני Alex...",  # Custom welcome
    #     "signature": "צוות מרפאת שיניים ברייט",  # Custom signature
    #     "working_hours": {
    #         "sunday": "08:00-18:00",
    #         "monday": "08:00-18:00",
    #         ...
    #     },
    #     "auto_reply_outside_hours": true,
    #     "outside_hours_message": "המרפאה סגורה כרגע..."
    # }
```

### דוגמה: מרפאה פורמלית vs. מרפאה casual

**מרפאה פורמלית:**
```
Alex: שלום רב. אני Alex, עוזר דיגיטלי של מרפאת שיניים פרימיום.
איך אוכל לסייע לך היום?

[קביעת תור] [בדיקת תור קיים]
```

**מרפאה casual:**
```
Alex: היי! 👋 אני Alex, קבלן הפנים הדיגיטלי של מרפאת שיניים קול.
מה נשמע? איך אפשר לעזור?

[בוא נקבע תור 📅] [התורים שלי 🔍]
```

---

## 🔧 Implementation Plan

### Phase 1: Core Integration (Week 1)

**Day 1-2: Database & Models**
- [ ] Create `telegram_users` table
- [ ] Create `telegram_conversations` table
- [ ] Create `telegram_invite_codes` table
- [ ] Update Organization model with telegram_settings
- [ ] Migration scripts

**Day 3-4: Alex Personality**
- [ ] Update Alex system prompt for Telegram
- [ ] Implement natural language responses
- [ ] Add emoji support (contextual)
- [ ] Remove "bot-like" language

**Day 5: Patient Onboarding Flow**
- [ ] Implement /start flow
- [ ] Phone number verification
- [ ] Link telegram_user ↔ patient
- [ ] Invite code support

**Files to create/update:**
```
backend/app/models/telegram_user.py                    ⭐ new
backend/app/models/telegram_conversation.py            ⭐ new
backend/app/models/telegram_invite_code.py             ⭐ new
backend/app/agents/alex_v2.py                          - update personality
backend/app/api/v1/endpoints/telegram.py               - update flows
backend/alembic/versions/xxx_add_telegram_tables.py    ⭐ new
```

---

### Phase 2: Sync & Notifications (Week 2)

**Day 1-2: Telegram ↔️ Portal Sync**
- [ ] Webhook for appointment changes
- [ ] Real-time notifications
- [ ] Bidirectional sync

**Day 3-4: Automated Notifications**
- [ ] 24-hour reminder
- [ ] 2-hour arrival confirmation
- [ ] Post-visit feedback
- [ ] Schedule background jobs

**Day 5: Rich Messages & UX**
- [ ] Quick reply buttons
- [ ] Typing indicators
- [ ] Rich appointment cards
- [ ] Calendar integration

**Files to create/update:**
```
backend/app/services/telegram_sync_service.py          ⭐ new
backend/app/services/telegram_notifications.py         ⭐ new
backend/app/workers/telegram_scheduler.py              ⭐ new
backend/app/integrations/telegram_client.py            - update with rich messages
```

---

### Phase 3: Customization & Polish (Week 3)

**Day 1-2: Per-Clinic Customization**
- [ ] Personality settings UI (Clinic Portal)
- [ ] Custom welcome messages
- [ ] Working hours configuration
- [ ] Auto-reply outside hours

**Day 3-4: Multi-Clinic Support**
- [ ] Invite code generation
- [ ] Clinic selection for multi-clinic patients
- [ ] Organization isolation

**Day 5: Testing & Documentation**
- [ ] E2E tests
- [ ] User documentation
- [ ] Admin documentation

**Files to create/update:**
```
frontend/src/pages/TelegramSettings.jsx                ⭐ new
frontend/src/components/telegram/PersonalityEditor.jsx ⭐ new
backend/app/api/v1/endpoints/telegram_admin.py         ⭐ new
backend/tests/test_telegram_e2e.py                     ⭐ new
```

---

## 📊 Success Metrics

### Technical:
- ✅ Response time < 2 seconds
- ✅ 99.9% uptime
- ✅ Zero message loss
- ✅ Sync latency < 5 seconds

### UX:
- ✅ Conversation completion rate > 80%
- ✅ User satisfaction > 4.5/5
- ✅ "Bot-like" complaints < 5%
- ✅ Natural language understanding > 90%

### Business:
- ✅ 50%+ of appointments via Telegram
- ✅ Reminder response rate > 70%
- ✅ No-show rate reduction by 30%

---

## 🎯 Summary

### הסוכן: Alex
- קבלן פנים דיגיטלי
- אישיות חמה, אמפתית, טבעית
- לא בוטי - אנושי מקסימלי

### הצטרפות:
- /start → זיהוי טלפון → קישור למטופל
- תמיכה בקודי הזמנה
- Multi-clinic support

### סנכרון:
- Bidirectional: Telegram ↔️ Portal
- Real-time notifications
- Webhooks for changes

### UX:
- Quick reply buttons
- Typing indicators
- Rich messages
- Emoji contextual
- שפה טבעית 100%

**הכל מוכן ליישום!** 🚀
