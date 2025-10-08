# 🚀 Phase 2 - Enhanced Agentic Dashboard - Work Plan

**תאריך:** 8 באוקטובר 2025  
**גרסה:** 18.0.0 → 19.0.0  
**משך זמן משוער:** 8 שבועות

---

## 🎯 מטרת Phase 2

להפוך את ה-Dashboard ל-**מערכת עובדת מלאה** עם:
- ✅ נתונים אמיתיים (לא mock)
- ✅ Odoo integration עובד
- ✅ Transparency מלא
- ✅ Decision Queue
- ✅ Proactive Suggestions

---

## 📊 סדר העבודה המדויק

### 🔴 שלב 0: תיקון בעיות קריטיות (4-7 שעות)

**חובה לפני שממשיכים!**

#### 0.1 תיקון Odoo Appointments (2-4 שעות) ← **זה השלב הבא!**

**בעיה:**
```python
odoo_client.create_appointment({
    "patient_id": 123,
    "doctor_id": 456,
    "appointment_sdate": "2025-10-10 10:00:00",
    "appointment_edate": "2025-10-10 10:30:00"
})
# ❌ Error: constraint on doctor_id
```

**משימות:**
1. [ ] התחבר ל-Odoo instance (dentaflow.ai)
2. [ ] בדוק Odoo logs לשגיאה
3. [ ] בדוק את ה-constraints ב-medical.appointment model
4. [ ] בדוק אם doctor_id צריך להיות ב-group מסוים
5. [ ] נסה ליצור appointment דרך Odoo UI (לראות מה הוא מצפה)
6. [ ] תקן את הקוד ב-`alex_odoo_tools.py`
7. [ ] בדוק שיצירת appointment עובדת
8. [ ] עדכן tests

**קבצים לעדכן:**
- `backend/app/agents/tools/alex_odoo_tools.py`
- `backend/app/services/odoo_client.py`
- `backend/tests/test_odoo_integration.py`

---

#### 0.2 בדיקת Database Tables (1 שעה)

**משימות:**
1. [ ] התחבר ל-production database
2. [ ] בדוק שהטבלאות קיימות:
   - `organization_memberships`
   - `clinic_settings`
   - `treatment_prices`
3. [ ] בדוק שיש נתונים בטבלאות
4. [ ] אם חסר - הרץ migrations

**פקודות:**
```bash
# SSH to EC2
ssh ubuntu@dentaflow.ai

# Check tables
psql -U dentalai -d dentalai -c "\dt"

# Check data
psql -U dentalai -d dentalai -c "SELECT COUNT(*) FROM organization_memberships;"
psql -U dentalai -d dentalai -c "SELECT COUNT(*) FROM clinic_settings;"
psql -U dentalai -d dentalai -c "SELECT COUNT(*) FROM treatment_prices;"
```

---

#### 0.3 בדיקת RBAC (1 שעה)

**משימות:**
1. [ ] בדוק שיש קישור users ← → Odoo partners
2. [ ] בדוק שמטופל רואה רק את עצמו
3. [ ] בדוק שצוות רואה את כל המטופלים
4. [ ] בדוק שרק Owner/Manager רואים נתונים פיננסיים

**קבצים לבדוק:**
- `backend/app/agents/tools/alex_odoo_tools.py` (RBAC logic)
- `backend/app/agents/rbac.py`

---

### 🟡 שלב 1: Real Data Widgets (שבוע 1, 20-30 שעות)

#### 1.1 Revenue Widget - חיבור ל-Marcus (6-8 שעות)

**משימות:**
1. [ ] שנה את `cfo_tools.py` להשתמש בנתונים אמיתיים מ-Odoo
2. [ ] הוסף API endpoint: `GET /api/v1/analytics/revenue`
3. [ ] עדכן את `RevenueWidget.jsx` להשתמש ב-API אמיתי
4. [ ] הוסף loading states
5. [ ] הוסף error handling
6. [ ] הוסף caching (Redis - אופציונלי)

**קבצים:**
- `backend/app/agents/tools/cfo_tools.py`
- `backend/app/api/v1/endpoints/analytics.py` (חדש)
- `frontend/src/components/dashboard/widgets/RevenueWidget.jsx`

---

#### 1.2 Patients Widget - חיבור ל-Alex (4-6 שעות)

**משימות:**
1. [ ] הוסף function ב-`alex_odoo_tools.py`: `get_patient_statistics()`
2. [ ] הוסף API endpoint: `GET /api/v1/analytics/patients`
3. [ ] עדכן את `PatientsWidget.jsx`
4. [ ] הוסף real-time updates (WebSocket - אופציונלי)

**קבצים:**
- `backend/app/agents/tools/alex_odoo_tools.py`
- `backend/app/api/v1/endpoints/analytics.py`
- `frontend/src/components/dashboard/widgets/PatientsWidget.jsx`

---

#### 1.3 Appointments Widget - חיבור ל-Alex (4-6 שעות)

**משימות:**
1. [ ] הוסף function: `get_appointment_statistics()`
2. [ ] הוסף API endpoint: `GET /api/v1/analytics/appointments`
3. [ ] עדכן את `AppointmentsWidget.jsx`
4. [ ] הוסף calendar view (אופציונלי)

**קבצים:**
- `backend/app/agents/tools/alex_odoo_tools.py`
- `backend/app/api/v1/endpoints/analytics.py`
- `frontend/src/components/dashboard/widgets/AppointmentsWidget.jsx`

---

#### 1.4 Alerts Widget - התראות אמיתיות (4-6 שעות)

**משימות:**
1. [ ] הוסף alert engine ב-backend
2. [ ] הוסף API endpoint: `GET /api/v1/alerts`
3. [ ] עדכן את `AlertsWidget.jsx`
4. [ ] הוסף notification system

**סוגי התראות:**
- תשלומים ממתינים
- פגישות שמתקרבות
- מטופלים שלא הגיעו (no-show)
- מלאי נמוך
- ביקורות שליליות

**קבצים:**
- `backend/app/services/alert_engine.py` (חדש)
- `backend/app/api/v1/endpoints/alerts.py` (חדש)
- `frontend/src/components/dashboard/widgets/AlertsWidget.jsx`

---

### 🟢 שלב 2: Transparency Panel Improvements (שבוע 2, 15-20 שעות)

#### 2.1 Agent Activity Timeline (6-8 שעות)

**משימות:**
1. [ ] הוסף timeline visualization
2. [ ] הצג reasoning steps
3. [ ] הצג tool calls עם תוצאות
4. [ ] הוסף confidence scores

**קבצים:**
- `frontend/src/components/transparency/AgentActivityPanel.jsx`
- `frontend/src/components/transparency/TimelineView.jsx` (חדש)

---

#### 2.2 Reasoning Panel Enhancement (4-6 שעות)

**משימות:**
1. [ ] הצג chain of thought
2. [ ] הצג decision points
3. [ ] הצג alternatives considered
4. [ ] הוסף expand/collapse

**קבצים:**
- `frontend/src/components/transparency/ReasoningPanel.jsx`

---

#### 2.3 Tool Call Results Display (4-6 שעות)

**משימות:**
1. [ ] הצג tool call parameters
2. [ ] הצג tool call results
3. [ ] הצג execution time
4. [ ] הצג errors (אם יש)

**קבצים:**
- `frontend/src/components/transparency/ToolCallChip.jsx`
- `frontend/src/components/transparency/ToolCallDetails.jsx` (חדש)

---

### 🔵 שלב 3: Decision Queue (שבוע 3, 20-25 שעות)

#### 3.1 Backend - Decision Queue System (10-12 שעות)

**משימות:**
1. [ ] יצירת טבלה: `decision_queue`
2. [ ] הוספת API endpoints:
   - `GET /api/v1/decisions` - רשימת החלטות
   - `POST /api/v1/decisions/{id}/approve` - אישור
   - `POST /api/v1/decisions/{id}/reject` - דחייה
   - `GET /api/v1/decisions/history` - היסטוריה
3. [ ] הוספת decision types:
   - Appointment approval (מטופל חדש)
   - Treatment plan approval (טיפול יקר)
   - Refund approval (החזר כספי)
   - Schedule change approval (שינוי לוח זמנים)

**קבצים:**
- `backend/app/models/decision.py` (חדש)
- `backend/app/api/v1/endpoints/decisions.py` (חדש)
- `backend/alembic/versions/xxx_add_decision_queue.py` (חדש)

---

#### 3.2 Frontend - Decision Queue UI (10-13 שעות)

**משימות:**
1. [ ] יצירת `DecisionQueueWidget.jsx`
2. [ ] יצירת `DecisionCard.jsx`
3. [ ] הוספת approve/reject buttons
4. [ ] הוספת decision details modal
5. [ ] הוספת decision history view
6. [ ] הוספת notifications

**קבצים:**
- `frontend/src/components/dashboard/widgets/DecisionQueueWidget.jsx` (חדש)
- `frontend/src/components/decisions/DecisionCard.jsx` (חדש)
- `frontend/src/components/decisions/DecisionModal.jsx` (חדש)

---

### 🟣 שלב 4: Proactive Suggestions (שבוע 4, 20-25 שעות)

#### 4.1 Backend - Suggestion Engine (12-15 שעות)

**משימות:**
1. [ ] יצירת `suggestion_engine.py`
2. [ ] הוספת suggestion types:
   - **Appointment reminders** - שלח תזכורת למטופל
   - **Payment follow-ups** - פנה למטופל עם חוב
   - **Treatment recommendations** - המלץ על טיפול
   - **Schedule optimization** - מלא משבצות ריקות
   - **Staff scheduling** - פתור קונפליקטים
3. [ ] הוספת API endpoints:
   - `GET /api/v1/suggestions` - רשימת הצעות
   - `POST /api/v1/suggestions/{id}/execute` - ביצוע
   - `POST /api/v1/suggestions/{id}/dismiss` - דחייה

**קבצים:**
- `backend/app/services/suggestion_engine.py` (חדש)
- `backend/app/api/v1/endpoints/suggestions.py` (חדש)

---

#### 4.2 Frontend - Suggestions Panel (8-10 שעות)

**משימות:**
1. [ ] יצירת `ProactiveSuggestionsPanel.jsx` (כבר קיים - לשפר)
2. [ ] הוספת suggestion cards
3. [ ] הוספת execute/dismiss buttons
4. [ ] הוספת suggestion details
5. [ ] הוספת suggestion history

**קבצים:**
- `frontend/src/components/dashboard/ProactiveSuggestionsPanel.jsx`
- `frontend/src/components/suggestions/SuggestionCard.jsx` (חדש)

---

### 🟠 שלב 5: Agent Routing Improvements (שבוע 5, 15-20 שעות)

#### 5.1 Supervisor Prompt Tuning (6-8 שעות)

**משימות:**
1. [ ] שיפור supervisor prompts
2. [ ] הוספת confidence scores
3. [ ] הוספת fallback strategies
4. [ ] הוספת agent handoff logging

**קבצים:**
- `backend/app/agents/agent_graph_v3.py`

---

#### 5.2 Agent Performance Monitoring (6-8 שעות)

**משימות:**
1. [ ] הוספת metrics:
   - Response time
   - Success rate
   - User satisfaction
   - Tool call success rate
2. [ ] הוספת dashboard למעקב

**קבצים:**
- `backend/app/services/agent_metrics.py` (חדש)
- `frontend/src/components/dashboard/AgentMetricsWidget.jsx` (חדש)

---

#### 5.3 Fine-Tuning Pipeline (אופציונלי, 8-10 שעות)

**משימות:**
1. [ ] איסוף feedback data
2. [ ] ייצוא training data (JSONL)
3. [ ] Fine-tune GPT-5-mini
4. [ ] A/B test fine-tuned model

**קבצים:**
- `backend/app/services/fine_tuning.py` (חדש)

---

### 🔴 שלב 6: Onboarding Integration (שבוע 6, 15-20 שעות)

#### 6.1 Move Onboarding to Main App (8-10 שעות)

**משימות:**
1. [ ] העבר קומפוננטות מ-`dentaflow-onboarding/` ל-`frontend/src/pages/onboarding/`
2. [ ] הוסף routing: `/onboarding`
3. [ ] שתף authentication state
4. [ ] הוסף redirect אחרי השלמה: `/dashboard`

**קבצים:**
- `frontend/src/pages/onboarding/` (חדש)
- `frontend/src/App.jsx` (עדכון routing)

---

#### 6.2 Onboarding Flow Testing (4-6 שעות)

**משימות:**
1. [ ] בדוק את כל 5 הצעדים
2. [ ] בדוק email verification
3. [ ] בדוק SMS verification
4. [ ] בדוק BAA signature
5. [ ] בדוק team invitations

---

#### 6.3 Landing Page Integration (3-4 שעות)

**משימות:**
1. [ ] חבר landing page ל-onboarding
2. [ ] הוסף CTA buttons
3. [ ] הוסף analytics tracking

---

### 🟢 שלב 7: Performance & Caching (שבוע 7, 15-20 שעות)

#### 7.1 Redis Caching (8-10 שעות)

**משימות:**
1. [ ] הוסף Redis caching ל:
   - Session storage
   - API response caching
   - Query result caching
2. [ ] הוסף cache invalidation
3. [ ] הוסף cache warming

**קבצים:**
- `backend/app/core/cache.py` (חדש)

---

#### 7.2 Database Optimization (4-6 שעות)

**משימות:**
1. [ ] הוסף indexes
2. [ ] אופטימיזציה של queries
3. [ ] הוסף connection pooling

---

#### 7.3 Rate Limiting (3-4 שעות)

**משימות:**
1. [ ] הוסף rate limiting ל-APIs
2. [ ] הוסף rate limiting ל-AI chat

**קבצים:**
- `backend/app/core/rate_limit.py` (חדש)

---

### 🔵 שלב 8: Testing & Production (שבוע 8, 20-30 שעות)

#### 8.1 Testing (12-15 שעות)

**משימות:**
1. [ ] Unit tests (90%+ coverage)
2. [ ] Integration tests
3. [ ] E2E tests (Playwright)
4. [ ] Load testing (Locust)

---

#### 8.2 Security Audit (4-6 שעות)

**משימות:**
1. [ ] Penetration testing
2. [ ] Security headers
3. [ ] HIPAA compliance check
4. [ ] Secrets rotation

---

#### 8.3 Documentation (4-6 שעות)

**משימות:**
1. [ ] API documentation
2. [ ] User guides
3. [ ] Admin guides
4. [ ] Deployment guides

---

## 📊 סיכום Timeline

| שלב | משך זמן | תאריכים משוערים |
|-----|---------|-----------------|
| **0. Critical Fixes** | 4-7 שעות | יום 1 |
| **1. Real Data Widgets** | 20-30 שעות | שבוע 1 |
| **2. Transparency Panel** | 15-20 שעות | שבוע 2 |
| **3. Decision Queue** | 20-25 שעות | שבוע 3 |
| **4. Proactive Suggestions** | 20-25 שעות | שבוע 4 |
| **5. Agent Routing** | 15-20 שעות | שבוע 5 |
| **6. Onboarding Integration** | 15-20 שעות | שבוע 6 |
| **7. Performance** | 15-20 שעות | שבוע 7 |
| **8. Testing & Production** | 20-30 שעות | שבוע 8 |
| **סה"כ** | **144-197 שעות** | **8 שבועות** |

---

## 🎯 השלב הבא - מה לעשות עכשיו?

### ✅ השלב הבא הוא: **0.1 תיקון Odoo Appointments**

**משימות:**
1. התחבר ל-Odoo instance
2. בדוק logs
3. בדוק constraints
4. תקן את הקוד
5. בדוק שעובד

**זמן משוער:** 2-4 שעות

---

**מוכן להתחיל? 🚀**
