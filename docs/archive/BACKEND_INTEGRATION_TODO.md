# Backend Integration TODO

## 🎯 מטרה
חיבור Mission Control Dashboard ל-Backend אמיתי (במקום Mock Data)

---

## 📋 משימות

### Phase 2.1: Backend APIs for Dashboard (Week 3)

#### 1. Dashboard Metrics API ✅ (TODO)
**Endpoint:** `GET /api/v1/dashboard-metrics`

**Response:**
```json
{
  "appointments_today": 12,
  "appointments_change": 3,
  "success_rate_24h": 87,
  "success_rate_change": 5,
  "conversations_resolved": 24,
  "avg_handling_time": 245,
  "avg_handling_time_weekly": 280,
  "handling_time_change": -35
}
```

**Implementation:**
- File: `backend/app/api/v1/dashboard.py`
- Query Odoo for appointments
- Query conversations table for metrics
- Calculate success rates
- Calculate handling times

**Estimated Time:** 2-3 hours

---

#### 2. Conversations API ✅ (TODO)
**Endpoint:** `GET /api/v1/conversations?status={status}`

**Response:**
```json
[
  {
    "id": 1,
    "patient_name": "שרה לוי",
    "patient_id": "P001",
    "last_message": "אני צריכה לקבוע תור",
    "status": "active",
    "trust_level": "high",
    "timestamp": "2025-10-08T10:30:00Z",
    "unread_count": 2
  }
]
```

**Implementation:**
- File: `backend/app/api/v1/conversations.py`
- Query conversations table
- Join with patients table
- Filter by status
- Calculate trust level

**Estimated Time:** 2-3 hours

---

#### 3. Conversation Messages API ✅ (TODO)
**Endpoint:** `GET /api/v1/conversations/{id}/messages`

**Response:**
```json
[
  {
    "id": 1,
    "content": "שלום, אני רוצה לקבוע תור",
    "sender_type": "patient",
    "from": "user",
    "timestamp": "2025-10-08T10:25:00Z"
  },
  {
    "id": 2,
    "content": "שלום! אשמח לעזור",
    "sender_type": "agent",
    "from": "assistant",
    "agent_name": "Alex",
    "timestamp": "2025-10-08T10:26:00Z"
  }
]
```

**Implementation:**
- File: `backend/app/api/v1/conversations.py`
- Query messages table
- Join with agents table
- Order by timestamp

**Estimated Time:** 1-2 hours

---

#### 4. Agent Actions API ✅ (TODO)
**Endpoint:** `GET /api/v1/agent-actions?status=pending`

**Response:**
```json
[
  {
    "id": 1,
    "action_type": "create_appointment",
    "description": "יצירת תור לשרה לוי",
    "agent_name": "Alex",
    "priority": "high",
    "timestamp": "2025-10-08T10:30:00Z",
    "details": {
      "patient_name": "שרה לוי",
      "treatment": "ניקוי שיניים",
      "date": "2025-10-15",
      "time": "09:00"
    }
  }
]
```

**Implementation:**
- File: `backend/app/api/v1/agent_actions.py`
- Query agent_actions table
- Filter by status
- Join with agents table

**Estimated Time:** 2 hours

---

#### 5. Human Handoff API ✅ (TODO)
**Endpoint:** `POST /api/v1/handoff/{conversation_id}`

**Request:**
```json
{
  "reason": "Manual transfer from mission control",
  "message": "העברה לטיפול אנושי"
}
```

**Implementation:**
- File: `backend/app/api/v1/handoff.py`
- Update conversation status
- Create handoff record
- Send notification

**Estimated Time:** 2 hours

---

#### 6. Approve/Reject Action APIs ✅ (TODO)
**Endpoints:**
- `POST /api/v1/agent-actions/{id}/approve`
- `POST /api/v1/agent-actions/{id}/reject`

**Implementation:**
- File: `backend/app/api/v1/agent_actions.py`
- Update action status
- Execute approved actions
- Log decisions

**Estimated Time:** 3 hours

---

### Phase 2.2: Frontend Integration (Week 3)

#### 1. Remove Mock Data Flag ✅ (TODO)
**File:** `frontend/src/pages/MissionControlDashboard.jsx`

Change:
```javascript
const USE_MOCK_DATA = true; // Change to false
```

**Estimated Time:** 5 minutes

---

#### 2. Update API Base URL ✅ (TODO)
**File:** `frontend/src/config.js`

Add:
```javascript
export const API_BASE_URL = process.env.VITE_API_URL || 'https://api.dentaflow.ai';
```

**Estimated Time:** 10 minutes

---

#### 3. Add Error Handling ✅ (TODO)
- Better error messages
- Retry logic
- Fallback UI

**Estimated Time:** 1 hour

---

#### 4. Add Loading States ✅ (TODO)
- Skeleton loaders
- Progress indicators
- Smooth transitions

**Estimated Time:** 2 hours

---

### Phase 2.3: Testing (Week 4)

#### 1. Integration Testing ✅ (TODO)
- Test all API endpoints
- Test error scenarios
- Test edge cases

**Estimated Time:** 4 hours

---

#### 2. Performance Testing ✅ (TODO)
- Load testing
- Response time optimization
- Caching strategy

**Estimated Time:** 3 hours

---

#### 3. User Acceptance Testing ✅ (TODO)
- Test with real users
- Collect feedback
- Fix issues

**Estimated Time:** 1 week

---

## 📊 סיכום זמנים

| משימה | זמן משוער |
|-------|-----------|
| Backend APIs | 12-15 שעות |
| Frontend Integration | 3-4 שעות |
| Testing | 1-2 שבועות |
| **סה"כ** | **2-3 שבועות** |

---

## 🎯 סדר עדיפויות

1. **High Priority** (Week 3):
   - Dashboard Metrics API
   - Conversations API
   - Conversation Messages API

2. **Medium Priority** (Week 3-4):
   - Agent Actions API
   - Approve/Reject APIs
   - Human Handoff API

3. **Low Priority** (Week 4):
   - Error handling improvements
   - Loading states
   - Performance optimization

---

## ✅ הערות

- כרגע המערכת עובדת עם Mock Data לצורך הדגמה
- כל ה-TODOs מתועדים בקוד עם הערות `// TODO: Replace with real API`
- כשנעבור ל-Backend אמיתי, פשוט נשנה את ה-flag `USE_MOCK_DATA = false`
- כל ה-API endpoints כבר מוכנים בקוד, רק צריך לממש אותם ב-Backend

---

**Created:** 2025-10-08  
**Status:** Pending  
**Priority:** High  
**Assigned To:** Phase 2 Development
