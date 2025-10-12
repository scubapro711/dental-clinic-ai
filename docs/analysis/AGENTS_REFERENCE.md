# DentaFlow Agents Reference

**תאריך:** 11 באוקטובר 2025  
**Architecture:** Hybrid (3 Core Agents)

---

## 🤖 הסוכנים במערכת

### 1. Alex - Reception & Patient Relations (Tier 1)
**קובץ:** `backend/app/agents/alex_v2.py`  
**תפקיד:** סוכן פונה מטופלים - שכבת קדמית

**אישיות:**
- ידידותי, מקצועי, סבלני
- דובר עברית ואנגלית
- מגיב מהר ובצורה ברורה

**יכולות:**
- 📅 **ניהול תורים:** קביעה, ביטול, שינוי תורים
- 💬 **תקשורת:** מענה לשאלות כלליות
- 🔔 **תזכורות:** שליחת תזכורות SMS/Email
- 📞 **Triage רפואי:** סינון דחוף/לא דחוף
- 🆘 **Escalation:** העברה לרופא במקרי חירום
- 💳 **תשלומים:** מידע על חשבוניות ותשלומים

**Tools (12):**
- `search_appointments`
- `create_appointment`
- `cancel_appointment`
- `send_sms`
- `send_email`
- `search_patients`
- `get_patient_info`
- `create_patient`
- `update_patient`
- `get_invoices`
- `create_payment_link`
- `escalate_to_doctor`

**Telegram Integration:** ✅ Yes (alex_telegram_personality.py)

**למי:** מטופלים (Patient Portal)

---

### 2. Marcus - CFO (Chief Financial Officer) (Tier 2/3)
**קובץ:** `backend/app/agents/cfo.py`  
**תפקיד:** ניהול פיננסי - דוחות, תזרים, רווחיות

**אישיות:**
- אנליטי, מדויק, עסקי
- מתמקד במספרים ובתובנות
- פרואקטיבי בהתרעות

**יכולות:**
- 💰 **דוחות פיננסיים:** יומי, שבועי, חודשי
- 📊 **ניתוח תזרים:** Cash flow analysis
- 📈 **תחזיות הכנסות:** Revenue forecasting
- 💸 **אופטימיזציה:** זיהוי הוצאות מיותרות
- 🧾 **חשבוניות:** ניהול חשבוניות ותשלומים
- 🎯 **רווחיות:** ניתוח רווחיות לפי טיפול

**Tools (15+):**
- `get_financial_summary`
- `get_cash_flow`
- `get_revenue_forecast`
- `get_expense_breakdown`
- `get_profitability_analysis`
- `get_invoices`
- `create_invoice`
- `send_invoice`
- `get_payments`
- `get_outstanding_balance`
- `analyze_treatment_profitability`
- `get_tax_report`
- `get_profit_loss_statement`

**Proactive:** ✅ Yes (daily reports at 8am)

**למי:** מנהלי מרפאה (Clinic Portal)

---

### 3. Sophia - Practice Administrator (Tier 2/3)
**קובץ:** `backend/app/agents/practice_admin.py`  
**תפקיד:** ניהול תפעול - לו"ז, צוות, מלאי

**אישיות:**
- מאורגנת, יעילה, פרואקטיבית
- רואה את התמונה הגדולה
- מתאמת בין כל הגורמים

**יכולות:**
- 📋 **Morning Briefings:** סקירת יום (7am)
- 👥 **ניהול צוות:** לוחות זמנים, משמרות
- 📦 **ניהול מלאי:** מעקב אחר חומרים וציוד
- 🔧 **תחזוקה:** תזכורות לתחזוקת ציוד
- ✅ **ניהול משימות:** יצירה והקצאת משימות
- 📊 **דוחות תפעול:** ניתוח ביצועים

**Tools (20+):**
- `get_daily_schedule`
- `get_staff_status`
- `get_inventory_status`
- `get_equipment_maintenance`
- `create_task`
- `assign_task`
- `get_pending_tasks`
- `order_supplies`
- `get_supplier_info`
- `schedule_maintenance`
- `get_room_availability`
- `optimize_schedule`

**Proactive:** ✅ Yes (morning briefings at 7am)

**למי:** מנהלי מרפאה (Clinic Portal)

---

### 4. Sarah - Clinical Assistant (Medical) (Tier 2/3)
**קובץ:** `backend/app/agents/sarah_clinical.py`  
**תפקיד:** עוזרת קלינית - רשומות רפואיות, טיפולים

**אישיות:**
- מקצועית, אכפתית, מדויקת
- בעלת ידע רפואי
- שומרת על פרטיות רפואית (HIPAA)

**יכולות:**
- 🦷 **Dental Chart:** ניהול מפת שיניים
- 📋 **Treatment Records:** תיעוד טיפולים
- 💊 **Prescriptions:** מרשמים ותרופות
- 🩺 **Medical History:** היסטוריה רפואית (אלרגיות, מחלות)
- 📸 **X-rays:** הזמנה וניתוח צילומי רנטגן
- 🔬 **Lab Tests:** הזמנת בדיקות מעבדה
- 📝 **Clinical Notes:** הערות קליניות
- 🔄 **Referrals:** הפניות למומחים
- 📅 **Follow-ups:** תזמון ביקורי המשך

**Tools (25+):**
- `get_dental_chart`
- `update_dental_chart`
- `create_treatment_record`
- `get_treatment_history`
- `create_prescription`
- `get_prescriptions`
- `get_medical_history`
- `update_medical_history`
- `add_allergy`
- `get_allergies`
- `order_xray`
- `upload_xray`
- `get_xrays`
- `analyze_xray`
- `order_lab_test`
- `get_lab_results`
- `create_clinical_note`
- `get_clinical_notes`
- `create_referral`
- `get_referrals`
- `schedule_followup`
- `get_treatment_plan`
- `create_treatment_plan`

**HIPAA Compliance:** ✅ Yes (encrypted, audit logs)

**למי:** רופאים וצוות קליני (Clinic Portal - Clinical Workspace)

---

## 🔀 Routing Logic

**קובץ:** `backend/app/agents/agent_graph_v4.py`

### Patient Queries → Alex
- תורים, תזכורות, שאלות כלליות
- תשלומים, חשבוניות
- מידע על המרפאה
- **דוגמאות:**
  - "אני רוצה לקבוע תור"
  - "מתי התור שלי?"
  - "כמה אני חייב?"

### Financial Queries → Marcus (CFO)
- הכנסות, הוצאות, רווחיות
- דוחות פיננסיים
- תזרים מזומנים
- **דוגמאות:**
  - "מה ההכנסה החודש?"
  - "מה ההוצאה הכי גדולה?"
  - "האם אנחנו רווחיים?"

### Operations Queries → Sophia
- לוחות זמנים, צוות
- מלאי, ציוד
- משימות, תפעול
- **דוגמאות:**
  - "מי עובד היום?"
  - "מה המשימות התלויות?"
  - "צריך להזמין חומרים?"

### Clinical Queries → Sarah
- רשומות רפואיות
- טיפולים, מרשמים
- צילומי רנטגן, בדיקות
- **דוגמאות:**
  - "מה ההיסטוריה הרפואית של המטופל?"
  - "צריך להזמין רנטגן"
  - "מה תוכנית הטיפול?"

---

## 🎯 שימוש בפורטלים

### Patient Portal
**סוכן עיקרי:** Alex  
**דפים:**
- Dashboard → Alex (general info)
- Appointments → Alex (booking, canceling)
- Medical Records → Sarah (view only, read-only)
- Billing → Marcus (view invoices, payments)
- Profile → Alex (update info)
- Chat → Alex (main interface)

**Layer 3 (Chat):** Floating chat button בכל דף

---

### Clinic Portal
**סוכנים:** כולם (Alex, Marcus, Sophia, Sarah)  
**דפים:**
- Dashboard (Mission Control) → All agents
- Patients Management → Alex + Sarah
- Schedule Management → Sophia + Alex
- Clinical Workspace → Sarah
- Financial Management → Marcus
- Operations Dashboard → Sophia

**Layout:** 3-column (widgets, chat, transparency)

---

### Admin Portal
**סוכנים:** System-level (no agents)  
**דפים:**
- Admin Dashboard
- Organizations Management
- Users Management
- System Settings
- System Monitoring
- Agent Management

---

## 🔧 כלים לפי סוכן

### Alex Tools (12)
✅ Patient management  
✅ Appointments  
✅ Communications (SMS/Email)  
✅ Basic billing info  
✅ Escalation  

### Marcus Tools (15+)
✅ Financial reports  
✅ Invoices & payments  
✅ Cash flow analysis  
✅ Profitability analysis  
✅ Tax reports  

### Sophia Tools (20+)
✅ Schedule management  
✅ Staff management  
✅ Inventory management  
✅ Equipment maintenance  
✅ Task management  

### Sarah Tools (25+)
✅ Dental chart  
✅ Treatment records  
✅ Prescriptions  
✅ Medical history  
✅ X-rays & lab tests  
✅ Clinical notes  
✅ Referrals  

---

## 📊 Agent Status

| Agent | Status | Tests | Tools | Proactive | Portal |
|-------|--------|-------|-------|-----------|--------|
| Alex | ✅ Active | 9/9 | 12 | ❌ | Patient |
| Marcus | ✅ Active | 8/8 | 15+ | ✅ (8am) | Clinic |
| Sophia | ✅ Active | 8/8 | 20+ | ✅ (7am) | Clinic |
| Sarah | ✅ Active | 10/10 | 25+ | ❌ | Clinic |

---

## 🚀 Integration Guidelines

### Patient Portal Pages
```jsx
// PatientAppointments.jsx
// Primary: Alex (booking, canceling)
// Secondary: None

// PatientMedicalRecords.jsx  
// Primary: Sarah (view records)
// Secondary: None (read-only for patients)

// PatientBilling.jsx
// Primary: Marcus (view invoices)
// Secondary: Alex (payment links)

// PatientProfile.jsx
// Primary: Alex (update info)
// Secondary: None
```

### Clinic Portal Pages
```jsx
// PatientsManagement.jsx
// Primary: Alex (patient info)
// Secondary: Sarah (medical records)

// ScheduleManagement.jsx
// Primary: Sophia (schedule optimization)
// Secondary: Alex (appointments)

// ClinicalWorkspace.jsx
// Primary: Sarah (all clinical tools)
// Secondary: None

// FinancialManagement.jsx
// Primary: Marcus (all financial tools)
// Secondary: None

// OperationsDashboard.jsx
// Primary: Sophia (all operations tools)
// Secondary: None
```

---

**סיכום:** 4 סוכנים פעילים, כל אחד עם תפקיד ברור ו-tools ייעודיים!

