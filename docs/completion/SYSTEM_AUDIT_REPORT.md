# בדיקת מערכת מקיפה - DentaFlow AI
## System Comprehensive Audit Report

**תאריך:** 7 אוקטובר 2025  
**גרסה נוכחית:** v14.2.0  
**מבצע הבדיקה:** Manus AI  

---

## 📋 סיכום מנהלים

### ✅ מה שעובד (Production Ready)

1. **Alex Agent** - סוכן AI מלא ועובד
   - 522 שורות קוד
   - 9/9 בדיקות עוברות
   - Medical safety boundaries
   - Escalation system
   - Hebrew support

2. **Chat System** - מערכת צ'אט מלאה
   - Vercel AI SDK integration (בתיקיית working)
   - Streaming responses
   - Tool call visualization
   - Conversation memory
   - Feedback collection

3. **LangGraph Integration** - ארכיטקטורה אגנטית
   - Multi-agent supervisor system
   - Memory checkpointer
   - State management
   - Agent routing

4. **Database & API** - תשתית מלאה
   - PostgreSQL models (conversations, messages)
   - FastAPI endpoints
   - Authentication & authorization
   - Odoo XML-RPC integration

5. **Hebrew & RTL** - תמיכה מלאה בעברית
   - 450+ CSS rules
   - RTL layout
   - Hebrew translations
   - Israeli localization module

---

## 🔍 ממצאים מפורטים

### 1. Frontend Components

#### ✅ קיים במאגר הראשי (dental-clinic-ai)

```
frontend/src/
├── pages/
│   ├── ChatPage.jsx ✅ (248 lines)
│   ├── AgenticDashboard.jsx ✅ (169 lines)
│   └── DashboardPage.jsx ✅ (8011 lines)
├── components/
│   ├── ConversationHistorySidebar.jsx ✅ (6696 lines)
│   ├── FeedbackButtons.jsx ✅ (4925 lines)
│   ├── transparency/
│   │   ├── AgentActivityPanel.jsx ✅
│   │   ├── FullTransparencyPanel.jsx ✅
│   │   ├── ReasoningPanel.jsx ✅
│   │   └── ToolCallChip.jsx ✅
│   └── widgets/
│       ├── BaseWidget.jsx ✅
│       ├── DecisionQueueWidget.jsx ✅
│       ├── FineTuningWidget.jsx ✅
│       ├── RevenueWidget.jsx ✅
│       └── TodaysPatientsWidget.jsx ✅
└── hooks/
    ├── useAgentActivity.js ✅ (125 lines)
    └── use-mobile.js ✅
```

#### ⚠️ חסר במאגר הראשי (קיים רק ב-working)

```
frontend/src/
├── components/
│   └── AIChat.jsx ❌ (493 lines - עם Vercel AI SDK!)
└── hooks/
    └── useAIChat.js ❌
```

#### 📦 Dependencies - חסר Vercel AI SDK!

**במאגר הראשי:**
```json
{
  "dependencies": {
    // ❌ אין @ai-sdk/react
    // ❌ אין ai package
    // ❌ אין @assistant-ui/react
  }
}
```

**בתיקיית working (נכון!):**
```json
{
  "dependencies": {
    "@ai-sdk/react": "^2.0.60", ✅
    "@assistant-ui/react": "^0.11.28", ✅
    "ai": "^5.0.60", ✅
    "socket.io-client": "^4.8.1" ✅
  }
}
```

---

### 2. Backend Components

#### ✅ קיים במאגר הראשי

```
backend/app/
├── agents/
│   ├── alex.py ✅ (522 lines - COMPLETE!)
│   ├── agent_graph.py ✅ (196 lines - V2, Alex only)
│   ├── graph_state.py ✅
│   ├── error_handler.py ✅
│   └── tools/
│       ├── agent_tools.py ✅
│       └── odoo_tools.py ✅
├── api/v1/endpoints/
│   ├── chat.py ✅ (166 lines)
│   └── ai_chat_transparency.py ✅ (469 lines)
├── memory/
│   └── causal_memory.py ✅
├── models/
│   ├── conversation.py ✅
│   ├── message.py ✅
│   ├── user.py ✅
│   └── consent.py ✅
└── integrations/
    └── odoo_client.py ✅
```

#### ❌ חסר במאגר הראשי (קיים רק ב-working)

```
backend/app/
├── agents/
│   ├── cfo.py ❌ (317 lines - CFO Agent!)
│   ├── practice_admin.py ❌ (325 lines - Practice Admin!)
│   ├── agent_graph_v3.py ❌ (581 lines - Multi-agent with supervisor!)
│   └── tools/
│       ├── cfo_tools.py ❌
│       └── practice_admin_tools.py ❌ (לא קיים!)
```

---

### 3. LangGraph Architecture

#### ✅ גרסה נוכחית במאגר (V2 - Alex Only)

**קובץ:** `backend/app/agents/agent_graph.py`

```python
class AgentGraphV2:
    """Simplified LangGraph with unified Alex agent."""
    
    def __init__(self):
        self.alex = AlexAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("alex", self._alex_node)
        workflow.set_entry_point("alex")
        workflow.add_edge("alex", END)
        return workflow.compile()
```

**מאפיינים:**
- ✅ Single agent (Alex)
- ✅ Simple routing
- ✅ Memory integration
- ✅ Works with chat.py endpoint
- ❌ No multi-agent support
- ❌ No CFO or Practice Admin

---

#### 🚀 גרסה מתקדמת בתיקיית working (V3 - Multi-Agent)

**קובץ:** `backend/app/agents/agent_graph_v3.py`

```python
class AgentGraphV3:
    """Multi-Agent LangGraph with Supervisor architecture."""
    
    def __init__(self, memory=None):
        self.alex = AlexAgent()
        self.cfo = CFOAgent()
        self.admin = PracticeAdminAgent()
        self.supervisor_llm = ChatOpenAI(model="gpt-4.1-mini")
        self.memory = memory if memory else MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("alex", self._alex_node)
        workflow.add_node("cfo", self._cfo_node)
        workflow.add_node("admin", self._admin_node)
        workflow.set_entry_point("supervisor")
        workflow.add_conditional_edges("supervisor", self._route_supervisor, {...})
        workflow.add_edge("alex", "supervisor")
        workflow.add_edge("cfo", "supervisor")
        workflow.add_edge("admin", "supervisor")
        return workflow.compile(checkpointer=self.memory)
```

**מאפיינים:**
- ✅ Multi-agent system
- ✅ Supervisor routing
- ✅ LangGraph MemorySaver (replaces Neo4j!)
- ✅ CFO Agent support
- ✅ Practice Admin support
- ✅ Intelligent delegation
- ✅ Clean context (removes routing messages)
- ✅ Thread-based memory (conversation_id)

---

### 4. Chat Endpoints

#### ✅ Endpoint 1: `/api/v1/chat/` (Simple)

**קובץ:** `backend/app/api/v1/endpoints/chat.py`

```python
@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, ...):
    # Uses AgentGraphV2 (Alex only)
    result = await agent_graph.process_message(...)
    return ChatResponse(
        conversation_id=conversation.id,
        response=result["response"],
        agent="alex",
        requires_human=result.get("escalation_level") in ["EMERGENCY", "DOCTOR_REQUIRED"]
    )
```

**מאפיינים:**
- ✅ Works with current system
- ✅ Database persistence
- ✅ Alex agent only
- ❌ No streaming
- ❌ No transparency events
- ❌ No multi-agent support

---

#### 🚀 Endpoint 2: `/api/v1/ai/chat` (Advanced)

**קובץ:** `backend/app/api/v1/endpoints/ai_chat_transparency.py`

```python
@router.post("/chat")
async def chat_with_transparency(request: ChatRequest, ...):
    # Streaming with transparency events
    return StreamingResponse(
        stream_agent_response_with_transparency(...),
        media_type="text/event-stream"
    )
```

**מאפיינים:**
- ✅ Server-Sent Events (SSE)
- ✅ Real-time streaming
- ✅ Transparency events:
  - `agent_start`
  - `tool_start`
  - `tool_complete`
  - `agent_complete`
  - `text` (streaming content)
  - `suggested_actions`
- ✅ Compatible with Vercel AI SDK
- ✅ Works with agent_graph_v3
- ⚠️ References agent_graph_v3 (not in main repo!)

---

### 5. Vercel AI SDK Integration

#### ❌ במאגר הראשי - לא קיים!

**ChatPage.jsx** משתמש ב-fetch ידני:
```javascript
const response = await fetch('http://localhost:8000/api/v1/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: input })
});
```

#### ✅ בתיקיית working - יש Vercel AI SDK!

**AIChat.jsx** משתמש ב-SSE streaming:
```javascript
// Parse SSE stream
const parseSSEStream = async (response) => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      
      if (data.type === 'text') {
        currentMessage.content += data.content;
        // Real-time update
      } else if (data.type === 'tool_call') {
        // Show tool usage
      } else if (data.type === 'suggested_actions') {
        // Phase 7: Agentic actions
      }
    }
  }
};
```

**תכונות:**
- ✅ Real-time streaming
- ✅ Tool call visualization
- ✅ Agent status indicators
- ✅ Suggested actions (Phase 7)
- ✅ Beautiful UI with animations
- ✅ Markdown rendering
- ✅ Feedback buttons

---

### 6. Agent Tools

#### ✅ Alex Tools (קיימים)

**קובץ:** `backend/app/agents/tools/agent_tools.py`

```python
# Patient Management
- search_patient_tool
- get_patient_details_tool

# Appointments
- get_available_slots_tool
- create_appointment_tool
- reschedule_appointment_tool

# Billing
- get_patient_invoices_tool
- get_invoice_details_tool
```

#### ❌ CFO Tools (חסרים במאגר הראשי)

**קובץ:** `backend/app/agents/tools/cfo_tools.py` (רק ב-working)

```python
- get_revenue_overview_tool
- get_payment_status_tool
- get_top_treatments_tool
- get_outstanding_invoices_tool
- analyze_profitability_tool
- get_financial_trends_tool
```

#### ❌ Practice Admin Tools (לא קיימים!)

צריך ליצור: `backend/app/agents/tools/practice_admin_tools.py`

```python
# נדרש:
- get_schedule_conflicts_tool
- get_available_slots_tool (כבר קיים ב-agent_tools)
- reschedule_appointment_tool (כבר קיים)
- get_staff_schedule_tool
- get_room_availability_tool
- optimize_schedule_tool
- get_operational_metrics_tool
```

---

### 7. Database Models

#### ✅ קיימים במאגר הראשי

```python
# Conversations & Messages
- Conversation (conversation.py)
- Message (message.py)
- ConversationStatus enum
- ConversationChannel enum
- MessageRole enum

# Users & Organizations
- User (user.py)
- Organization
- UserRole enum

# Privacy & Consent
- Consent (consent.py)
- AuditLog (audit_log.py)

# Israeli Localization
- IsraeliPatient (israeli_patient.py)
- IsraeliDoctor (israeli_doctor.py)
```

#### ✅ כל המודלים נדרשים קיימים!

---

### 8. Odoo Integration

#### ✅ קיים במאגר הראשי

**קובץ:** `backend/app/integrations/odoo_client.py`

```python
class OdooClient:
    """Odoo XML-RPC client."""
    
    def __init__(self):
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.username = settings.ODOO_USERNAME
        self.password = settings.ODOO_PASSWORD
        self.uid = None
    
    def authenticate(self):
        # XML-RPC authentication
    
    def search(self, model, domain):
        # Search records
    
    def read(self, model, ids, fields):
        # Read records
    
    def create(self, model, values):
        # Create record
    
    def write(self, model, ids, values):
        # Update record
```

**מאפיינים:**
- ✅ XML-RPC integration
- ✅ CRUD operations
- ✅ Authentication
- ✅ Used by agent tools

---

### 9. Memory & State Management

#### ✅ V2 (במאגר הראשי) - Causal Memory

**קובץ:** `backend/app/memory/causal_memory.py`

```python
class CausalMemory:
    """PostgreSQL-based conversation memory."""
    
    def store_interaction(self, user_message, agent_response, ...):
        # Store in database
    
    def get_similar_interactions(self, user_message, limit=3):
        # Retrieve similar past interactions
```

**מאפיינים:**
- ✅ PostgreSQL storage
- ✅ Similarity search
- ✅ Works with agent_graph.py (V2)
- ⚠️ Not used by agent_graph_v3.py

---

#### 🚀 V3 (בתיקיית working) - LangGraph MemorySaver

**קובץ:** `backend/app/agents/agent_graph_v3.py`

```python
from langgraph.checkpoint.memory import MemorySaver

class AgentGraphV3:
    def __init__(self, memory=None):
        self.memory = memory if memory else MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        return workflow.compile(checkpointer=self.memory)
    
    async def process_message(self, ..., conversation_id, ...):
        final_state = await self.graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": conversation_id}}
        )
```

**מאפיינים:**
- ✅ Built-in LangGraph memory
- ✅ Thread-based (conversation_id)
- ✅ Automatic state persistence
- ✅ No manual storage needed
- ✅ Replaces Neo4j!
- ✅ Simpler than causal_memory

---

### 10. Hebrew & RTL Support

#### ✅ קיים במאגר הראשי

```
frontend/src/i18n/
├── config.js ✅
├── locales/
│   ├── en.json ✅
│   └── he.json ✅ (extended)
└── components/
    └── LanguageSwitcher.jsx ✅

backend/app/models/
├── israeli_patient.py ✅
└── israeli_doctor.py ✅

odoo-addons/dental_israel/ ✅
├── __manifest__.py (v19.0.1.0.1)
├── models/
│   ├── res_partner.py (Israeli fields)
│   └── hr_employee.py (Israeli fields)
├── static/src/css/
│   └── custom_rtl_fixes.css (450+ rules!)
└── data/
    └── health_fund_data.xml
```

**מאפיינים:**
- ✅ 450+ CSS RTL rules
- ✅ Hebrew translations
- ✅ Israeli ID validation
- ✅ Health fund integration
- ✅ RTL layout complete
- ✅ Production ready!

---

## 🎯 פערים קריטיים

### 1. Frontend - חסר Vercel AI SDK Integration

**בעיה:**
- המאגר הראשי לא כולל את `AIChat.jsx` עם Vercel AI SDK
- `package.json` לא כולל את `@ai-sdk/react` ו-`ai`
- `ChatPage.jsx` משתמש ב-fetch ידני במקום streaming

**פתרון:**
```bash
# 1. Copy AIChat.jsx from working to main
cp /home/ubuntu/dental-clinic-working/frontend/src/components/AIChat.jsx \
   /home/ubuntu/dental-clinic-ai/frontend/src/components/

# 2. Update package.json
cd /home/ubuntu/dental-clinic-ai/frontend
npm install @ai-sdk/react@^2.0.60 ai@^5.0.60 socket.io-client@^4.8.1

# 3. Update AgenticDashboard.jsx to use AIChat instead of ChatPage
```

---

### 2. Backend - חסר Multi-Agent System (V3)

**בעיה:**
- המאגר הראשי כולל רק `agent_graph.py` (V2 - Alex only)
- חסרים `cfo.py`, `practice_admin.py`, `agent_graph_v3.py`
- חסרים כלי CFO (`cfo_tools.py`)
- חסרים כלי Practice Admin

**פתרון:**
```bash
# 1. Copy agents from working to main
cp /home/ubuntu/dental-clinic-working/backend/app/agents/cfo.py \
   /home/ubuntu/dental-clinic-ai/backend/app/agents/

cp /home/ubuntu/dental-clinic-working/backend/app/agents/practice_admin.py \
   /home/ubuntu/dental-clinic-ai/backend/app/agents/

cp /home/ubuntu/dental-clinic-working/backend/app/agents/agent_graph_v3.py \
   /home/ubuntu/dental-clinic-ai/backend/app/agents/

# 2. Copy tools
cp /home/ubuntu/dental-clinic-working/backend/app/agents/tools/cfo_tools.py \
   /home/ubuntu/dental-clinic-ai/backend/app/agents/tools/

# 3. Create practice_admin_tools.py (needs to be built)

# 4. Update chat endpoint to use agent_graph_v3
```

---

### 3. API Endpoint - לא מחובר ל-V3

**בעיה:**
- `ai_chat_transparency.py` מתייחס ל-`agent_graph_v3` שלא קיים במאגר הראשי
- `chat.py` משתמש ב-`agent_graph` (V2) ללא streaming

**פתרון:**
```python
# Update backend/app/api/v1/endpoints/ai_chat_transparency.py
from app.agents.agent_graph_v3 import agent_graph_v3

# OR update to use agent_graph_v3 when available
```

---

### 4. Practice Admin Tools - לא קיימים

**בעיה:**
- `practice_admin.py` מתייחס לכלים שלא קיימים:
  - `get_schedule_conflicts_tool`
  - `get_staff_schedule_tool`
  - `get_room_availability_tool`
  - `optimize_schedule_tool`
  - `get_operational_metrics_tool`

**פתרון:**
```bash
# Create backend/app/agents/tools/practice_admin_tools.py
# Implement the 5 tools needed
```

---

## 📊 סטטוס לפי קומפוננטה

| קומפוננטה | במאגר הראשי | בתיקיית Working | נדרש לפיילוט | סטטוס |
|-----------|-------------|------------------|---------------|--------|
| **Alex Agent** | ✅ 100% | ✅ 100% | ✅ | 🟢 Ready |
| **CFO Agent** | ❌ 0% | ✅ 100% | ✅ | 🟡 Needs Copy |
| **Practice Admin** | ❌ 0% | ✅ 90% | ✅ | 🟡 Needs Tools |
| **Agent Graph V2** | ✅ 100% | ✅ 100% | ❌ | 🟢 Works (limited) |
| **Agent Graph V3** | ❌ 0% | ✅ 100% | ✅ | 🟡 Needs Copy |
| **Chat Endpoint** | ✅ 100% | ✅ 100% | ✅ | 🟢 Works |
| **Streaming Endpoint** | ✅ 100% | ✅ 100% | ✅ | 🟡 Needs V3 |
| **AIChat Component** | ❌ 0% | ✅ 100% | ✅ | 🟡 Needs Copy |
| **Vercel AI SDK** | ❌ 0% | ✅ 100% | ✅ | 🟡 Needs Install |
| **Transparency UI** | ✅ 100% | ✅ 100% | ✅ | 🟢 Ready |
| **Database Models** | ✅ 100% | ✅ 100% | ✅ | 🟢 Ready |
| **Odoo Integration** | ✅ 100% | ✅ 100% | ✅ | 🟢 Ready |
| **Hebrew & RTL** | ✅ 100% | ✅ 100% | ✅ | 🟢 Ready |
| **Memory System** | ✅ V2 | ✅ V3 | ✅ | 🟢 Both Work |

---

## 🚀 תוכנית פעולה

### Phase 1: העתקת קומפוננטות (2-3 שעות)

```bash
# 1. Frontend - Vercel AI SDK
cd /home/ubuntu/dental-clinic-ai/frontend
npm install @ai-sdk/react@^2.0.60 ai@^5.0.60 socket.io-client@^4.8.1

# 2. Copy AIChat component
cp /home/ubuntu/dental-clinic-working/frontend/src/components/AIChat.jsx \
   /home/ubuntu/dental-clinic-ai/frontend/src/components/

# 3. Copy agents
cp /home/ubuntu/dental-clinic-working/backend/app/agents/cfo.py \
   /home/ubuntu/dental-clinic-ai/backend/app/agents/
cp /home/ubuntu/dental-clinic-working/backend/app/agents/practice_admin.py \
   /home/ubuntu/dental-clinic-ai/backend/app/agents/
cp /home/ubuntu/dental-clinic-working/backend/app/agents/agent_graph_v3.py \
   /home/ubuntu/dental-clinic-ai/backend/app/agents/

# 4. Copy CFO tools
cp /home/ubuntu/dental-clinic-working/backend/app/agents/tools/cfo_tools.py \
   /home/ubuntu/dental-clinic-ai/backend/app/agents/tools/
```

### Phase 2: יצירת Practice Admin Tools (4-6 שעות)

```bash
# Create backend/app/agents/tools/practice_admin_tools.py
# Implement:
# - get_schedule_conflicts_tool
# - get_staff_schedule_tool
# - get_room_availability_tool
# - optimize_schedule_tool
# - get_operational_metrics_tool
```

### Phase 3: עדכון Endpoints (2-3 שעות)

```python
# Update backend/app/api/v1/endpoints/ai_chat_transparency.py
# Change from agent_graph_v3 import to use the copied version

# Test streaming endpoint with multi-agent system
```

### Phase 4: עדכון Frontend (2-3 שעות)

```javascript
// Update frontend/src/pages/AgenticDashboard.jsx
// Replace ChatPage with AIChat component
// Test streaming, tool calls, transparency
```

### Phase 5: בדיקות (4-6 שעות)

```bash
# 1. Test Alex agent
# 2. Test CFO agent
# 3. Test Practice Admin agent
# 4. Test supervisor routing
# 5. Test streaming
# 6. Test transparency events
# 7. Test Hebrew support
```

---

## ⏱️ הערכת זמן

| משימה | זמן משוער | קריטיות |
|-------|-----------|----------|
| העתקת קומפוננטות | 2-3 שעות | 🔴 גבוהה |
| Practice Admin Tools | 4-6 שעות | 🔴 גבוהה |
| עדכון Endpoints | 2-3 שעות | 🟡 בינונית |
| עדכון Frontend | 2-3 שעות | 🟡 בינונית |
| בדיקות | 4-6 שעות | 🔴 גבוהה |
| **סה"כ** | **14-21 שעות** | **2-3 ימי עבודה** |

---

## 💡 המלצות

### 1. גישה מומלצת: Incremental Migration

**שלב 1: Keep V2 Working (1 day)**
- העתק את כל הקומפוננטות מ-working למאגר הראשי
- אל תשנה את `chat.py` endpoint (ימשיך לעבוד עם V2)
- הוסף endpoint חדש `/api/v1/ai/chat/v3` שמשתמש ב-V3
- Frontend יכול לבחור איזה endpoint להשתמש

**שלב 2: Test V3 in Parallel (2-3 days)**
- בנה את Practice Admin Tools
- בדוק את המערכת Multi-Agent
- תקן באגים
- V2 ממשיך לעבוד כ-fallback

**שלב 3: Switch to V3 (1 day)**
- כשהכל עובד, עדכן את `chat.py` להשתמש ב-V3
- הסר את V2 endpoint
- Deploy לפרודקשן

**יתרונות:**
- ✅ אפס downtime
- ✅ V2 עובד כל הזמן
- ✅ אפשר לבדוק V3 בנפרד
- ✅ Rollback קל אם יש בעיה

---

### 2. גישה אגרסיבית: Direct Migration

**שלב 1: Copy Everything (4 hours)**
- העתק הכל מ-working למאגר הראשי
- עדכן את `chat.py` להשתמש ב-V3
- בנה Practice Admin Tools

**שלב 2: Fix & Test (2-3 days)**
- תקן באגים
- בדוק את כל הסוכנים
- Deploy

**חסרונות:**
- ❌ V2 מפסיק לעבוד
- ❌ אם יש באג, אין fallback
- ❌ סיכון גבוה

---

## ✅ סיכום

### מה שעובד היום:
1. ✅ Alex Agent (100%)
2. ✅ Chat System עם V2 (100%)
3. ✅ Database & API (100%)
4. ✅ Hebrew & RTL (100%)
5. ✅ Odoo Integration (100%)

### מה שחסר לפיילוט:
1. ❌ Vercel AI SDK integration (2-3 hours)
2. ❌ Multi-agent system (V3) (4-6 hours)
3. ❌ Practice Admin Tools (4-6 hours)
4. ❌ Frontend updates (2-3 hours)
5. ❌ Testing (4-6 hours)

### סה"כ זמן לפיילוט:
**16-24 שעות (2-3 ימי עבודה)**

### המלצה סופית:
**✅ Incremental Migration**
- שמור על V2 עובד
- בנה V3 בצד
- בדוק היטב
- עבור ל-V3 כשהכל מוכן

---

**תאריך הבא:** יישום תוכנית ההעתקה והשלמת הפערים
