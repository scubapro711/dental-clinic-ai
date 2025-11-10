# בעיות ידועות ו-TODOs - DentaFlow Backend

**תאריך:** 2025-01-24
**סטטוס:** Active Development

---

## 🐛 באגים שתוקנו

### 1. ✅ TelegramClient - חוסר validation של bot_token

**קובץ:** `app/integrations/telegram_client.py`
**Severity:** High
**Status:** Fixed (2025-01-24)

**תיאור:**
- לא הייתה בדיקה אם bot_token מוגדר לפני שימוש ב-API
- אם `settings.TELEGRAM_BOT_TOKEN` היה None, הקוד היה קורס בזמן ריצה

**Root Cause:**
- חוסר validation ב-`__init__` method
- base_url נוצר עם token שיכול להיות None

**Fix:**
- הוספת `_validate_token()` method
- קריאה ל-validation בכל method שמשתמש ב-API
- base_url נוצר רק אם יש token

**Test:**
- נוסף טסט שמוודא שזורק ValueError כשאין token

**Commit:** `d80e8fb`

---

## 📋 TODOs ממתינים (לפי עדיפות)

### עדיפות גבוהה (Critical)

#### 1. Authentication & Authorization

**קובץ:** `app/api/v1/endpoints/ai_chat.py`
**שורות:** 127, 128, 192

```python
user_role = "owner"  # FIXME: Get from JWT token - current_user["role"]
user_permissions = []  # FIXME: Get from RBAC system based on role
# TODO: Implement proper authentication
```

**בעיה:**
- hardcoded role במקום לקרוא מ-JWT
- אין שימוש במערכת RBAC
- חוסר authentication

**השפעה:**
- פרצת אבטחה - כל משתמש יכול לגשת לכל דבר
- אין הפרדה בין תפקידים
- אין audit trail

**פתרון מוצע:**
1. להשתמש ב-`current_user` dependency מ-FastAPI
2. לקרוא role מ-JWT token
3. להשתמש ב-`rbac_enhanced.py` לבדיקת permissions

**זמן משוער:** 2-3 שעות

---

#### 2. Odoo Integration - Mock vs Real

**קובצים:**
- `app/agents/alex_v2.py` (שורות 38-41)
- `app/api/v1/endpoints/dashboard.py`
- `app/api/v1/endpoints/dashboard_metrics.py`
- ועוד 6 קבצים

```python
get_available_slots_tool,  # TODO: Replace with Odoo when appointment creation works
create_appointment_tool,   # TODO: Replace with Odoo when appointment creation works
get_patient_invoices_tool, # TODO: Replace with Odoo billing integration
get_invoice_details_tool,  # TODO: Replace with Odoo billing integration
```

**בעיה:**
- שימוש ב-mock data במקום Odoo אמיתי
- נתונים לא אמיתיים ב-dashboard
- אין אינטגרציה מלאה עם Odoo

**השפעה:**
- המערכת לא עובדת עם נתונים אמיתיים
- לא ניתן לבדוק בסביבת ייצור
- חוסר אמינות

**פתרון מוצע:**
1. להשלים את האינטגרציה עם Odoo 17
2. להחליף את כל ה-mock tools ב-tools אמיתיים
3. לבדוק שהכל עובד עם Odoo אמיתי

**זמן משוער:** 1-2 שבועות (חלק מ-Phase 3)

---

#### 3. Financial Data - Mock Revenue

**קובץ:** `app/api/v1/endpoints/dashboard.py` (שורה 156)

```python
# TODO: Query actual revenue from Odoo invoices/payments
```

**בעיה:**
- נתוני הכנסות לא אמיתיים
- אין שאילתות לחשבוניות/תשלומים ב-Odoo

**השפעה:**
- dashboard מציג נתונים שגויים
- לא ניתן לסמוך על דוחות כספיים
- בעיות ב-billing

**פתרון מוצע:**
1. לממש שאילתות ל-Odoo invoices
2. לחשב revenue אמיתי מתשלומים
3. להוסיף caching לביצועים

**זמן משוער:** 4-6 שעות

---

### עדיפות בינונית (High)

#### 4. Agent Metrics - Mock Data

**קובץ:** `app/api/v1/endpoints/agents.py` (שורות 28-32)

```python
# TODO: Track real agent metrics in database or in-memory store
```

**בעיה:**
- מטריקות של agents לא אמיתיות
- אין מעקב אחר ביצועים

**השפעה:**
- לא ניתן לנטר agents
- אין נתונים לשיפור
- חוסר visibility

**פתרון מוצע:**
1. ליצור טבלה ב-DB למטריקות
2. לעקוב אחר כל פעולה של agent
3. לחשב מטריקות אמיתיות

**זמן משוער:** 6-8 שעות

---

#### 5. Agent Control - Pause/Resume/Restart

**קובץ:** `app/api/v1/endpoints/agents.py` (שורות 61, 80, 99)

```python
# TODO: Implement actual pause mechanism
# TODO: Implement actual resume mechanism
# TODO: Implement actual restart mechanism
```

**בעיה:**
- אין מנגנון אמיתי לשליטה ב-agents
- endpoints מחזירים success אבל לא עושים כלום

**השפעה:**
- לא ניתן לעצור agent שמתנהג לא נכון
- אין שליטה על המערכת
- בעיות ב-production

**פתרון מוצע:**
1. לממש state management ל-agents
2. להוסיף signals לעצירה/המשך
3. לוודא שה-agents מגיבים

**זמן משוער:** 8-12 שעות

---

#### 6. Conversation Tracking

**קובץ:** `app/api/v1/endpoints/dashboard_metrics.py` (שורה 45)

```python
# TODO: Implement conversation tracking in database
```

**בעיה:**
- אין מעקב אחר שיחות ב-DB
- נתונים נאבדים

**השפעה:**
- לא ניתן לנתח שיחות
- אין היסטוריה
- חוסר HIPAA compliance

**פתרון מוצע:**
1. ליצור טבלת conversations ב-DB
2. לשמור כל הודעה
3. להוסיף indexing לחיפוש

**זמן משוער:** 6-8 שעות

---

### עדיפות נמוכה (Medium)

#### 7. Email/SMS Notifications

**קובץ:** `app/api/v1/endpoints/doctor.py` (שורה 89)

```python
# TODO: Implement actual email/SMS sending
```

**בעיה:**
- אין שליחת התראות אמיתית
- רופאים לא מקבלים עדכונים

**השפעה:**
- חוסר תקשורת
- missed appointments
- חוויית משתמש גרועה

**פתרון מוצע:**
1. לממש integration עם email service
2. לממש integration עם SMS service (Twilio)
3. להוסיף templates

**זמן משוער:** 4-6 שעות

---

#### 8. Insurance Provider Field

**קובץ:** `app/api/v1/endpoints/dashboard.py` (שורה 272)

```python
"insurance_provider": None,  # TODO: Add insurance field
```

**בעיה:**
- חוסר שדה לביטוח
- נתונים חסרים

**השפעה:**
- לא ניתן לעקוב אחר ביטוחים
- בעיות בחיוב

**פתרון מוצע:**
1. להוסיף שדה insurance_provider למודל Patient
2. להוסיף לטפסים
3. לעדכן את ה-dashboard

**זמן משוער:** 2-3 שעות

---

#### 9. Treatment Type Field

**קובצים:**
- `app/api/v1/appointments.py` (שורה 123)
- `app/api/v1/endpoints/handoff.py` (שורות 89, 123)

```python
'treatment_type': 'General',  # TODO: Add treatment type field
```

**בעיה:**
- חוסר שדה לסוג טיפול
- hardcoded values

**השפעה:**
- לא ניתן לסנן לפי סוג טיפול
- נתונים לא מדויקים

**פתרון מוצע:**
1. להוסיף שדה treatment_type למודל Appointment
2. להוסיף enum לסוגי טיפולים
3. לעדכן את כל המקומות

**זמן משוער:** 2-3 שעות

---

#### 10. Decision Queue - Async Execution

**קובץ:** `app/api/v1/endpoints/decision_queue.py` (שורות 88, 123, 147)

```python
# TODO: Trigger execution asynchronously
# TODO: Send feedback to agent for learning
# TODO: Send feedback to agent for fine-tuning
```

**בעיה:**
- החלטות מבוצעות synchronously
- אין feedback loop ל-agents

**השפעה:**
- ביצועים נמוכים
- agents לא לומדים
- חוסר שיפור

**פתרון מוצע:**
1. להוסיף Celery/Redis לעיבוד async
2. לממש feedback mechanism
3. להוסיף learning pipeline

**זמן משוער:** 12-16 שעות

---

## 📊 סיכום TODOs

| עדיפות | כמות | זמן משוער | השפעה |
|---------|------|-----------|-------|
| Critical | 3 | 2-3 שבועות | High |
| High | 3 | 20-28 שעות | Medium-High |
| Medium | 4 | 10-15 שעות | Medium |
| **סה"כ** | **10** | **3-4 שבועות** | - |

---

## 🎯 תוכנית טיפול

### שלב 1: Critical TODOs (שבוע 1)
1. Authentication & Authorization (2-3 שעות)
2. Financial Data - Real Revenue (4-6 שעות)

### שלב 2: High TODOs (שבוע 2-3)
3. Agent Metrics (6-8 שעות)
4. Agent Control (8-12 שעות)
5. Conversation Tracking (6-8 שעות)

### שלב 3: Odoo Integration (שבוע 3-4)
6. החלפת Mock ב-Real Odoo (1-2 שבועות)

### שלב 4: Medium TODOs (שבוע 5)
7. Email/SMS Notifications (4-6 שעות)
8. Insurance Provider (2-3 שעות)
9. Treatment Type (2-3 שעות)
10. Decision Queue Async (12-16 שעות)

---

## 🔍 ממצאים נוספים

### Patterns שחוזרים

1. **Mock Data** - הרבה מקומות משתמשים ב-mock במקום real data
2. **Hardcoded Values** - הרבה ערכים hardcoded במקום dynamic
3. **Missing Fields** - הרבה שדות חסרים במודלים
4. **No Async** - הרבה פעולות synchronous שצריכות להיות async
5. **No Validation** - חוסר validation במקומות רבים

### המלצות כלליות

1. **לעבור מ-Mock ל-Real** - בכל המקומות
2. **להוסיף Validation** - בכל ה-endpoints
3. **להוסיף Async** - לפעולות ארוכות
4. **להוסיף Tests** - לכל הקוד החדש
5. **לתעד** - כל שינוי

---

**Created:** 2025-01-24
**Last Updated:** 2025-01-24
**Next Review:** Weekly

