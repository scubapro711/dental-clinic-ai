# ארכיטקטורת הסוכנים המלאה - DentaFlow

**תאריך:** 7 באוקטובר 2025  
**מבוסס על:** ניתוח מלא של הקוד, LangGraph, וכלים

---

## 🏗️ ארכיטקטורת LangGraph - סקירה כללית

### מבנה הגרף

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTRY POINT                               │
│                    User Request                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   SUPERVISOR NODE                            │
│  - Analyzes request                                          │
│  - Routes to appropriate agent                               │
│  - Enforces RBAC                                             │
│  - Removes routing messages (performance optimization)       │
└──────────┬────────────┬────────────┬────────────────────────┘
           │            │            │
     ┌─────┘            │            └─────┐
     │                  │                  │
     ▼                  ▼                  ▼
┌─────────┐      ┌──────────┐      ┌──────────┐
│  ALEX   │      │  MARCUS  │      │  SOPHIA  │
│ (Patient│      │  (CFO)   │      │  (Admin) │
│  Care)  │      │(Financial)│      │(Operations)│
└────┬────┘      └────┬─────┘      └────┬─────┘
     │                │                  │
     └────────────────┼──────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   SUPERVISOR  │
              │  (Check if    │
              │   more work)  │
              └───────┬───────┘
                      │
                      ▼
                    [END]
```

---

## 🧠 ניהול זיכרון (Memory Management)

### LangGraph Checkpointer - MemorySaver

**מה זה:**
- מערכת persistence מובנית של LangGraph
- שומר את כל ה-state בין הפעלות
- מאפשר המשכיות שיחה (conversation continuity)

**איך זה עובד:**
```python
# Initialize graph with memory
self.memory = MemorySaver()
self.graph = workflow.compile(checkpointer=self.memory)

# Run with thread_id (conversation_id)
final_state = await self.graph.ainvoke(
    initial_state,
    config={"configurable": {"thread_id": conversation_id}}
)
```

**מה נשמר:**
- כל ההודעות (messages)
- State של כל node
- Tool results
- Agent responses
- User context

**יתרונות:**
- ✅ אוטומטי - לא צריך לכתוב קוד
- ✅ Thread-safe
- ✅ מהיר - in-memory
- ✅ פשוט - רק thread_id

**חסרונות:**
- ⚠️ In-memory only (נאבד בrestart)
- ⚠️ לא persistent לlong-term
- ⚠️ לא scalable למיליוני שיחות

**פתרון עתידי:**
```python
# Replace MemorySaver with PostgreSQL checkpointer
from langgraph.checkpoint.postgres import PostgresSaver

self.memory = PostgresSaver(connection_string=DATABASE_URL)
```

---

### Message History Management

**Optimization: remove_handoff_messages()**

```python
def remove_handoff_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
    """
    Remove supervisor's routing logic from sub-agent context.
    
    This is CRITICAL for performance (50% improvement!).
    """
    routing_keywords = [
        "delegating to", "transferring to", "routing to",
        "calling", "forwarding to", ...
    ]
    
    clean_messages = []
    for msg in messages:
        if any(keyword in msg.content.lower() for keyword in routing_keywords):
            continue  # Skip routing messages
        clean_messages.append(msg)
    
    return clean_messages
```

**למה זה חשוב:**
- 🚀 **50% שיפור ביצועים**
- הסוכנים רואים רק הודעות רלוונטיות
- פחות tokens = מהיר יותר וזול יותר
- הסוכנים לא מבולבלים מהחלטות routing

---

### Thread Management

**Thread ID = Conversation ID**
```python
conversation_id = "conv_abc123"
thread_id = conversation_id  # Same thing!

# All messages in same conversation share same thread_id
# LangGraph automatically loads previous state
```

**דוגמה:**
```python
# First message
state1 = await graph.ainvoke(
    {"messages": [HumanMessage("שלום")]},
    config={"configurable": {"thread_id": "conv_123"}}
)
# State saved automatically

# Second message (same conversation)
state2 = await graph.ainvoke(
    {"messages": [HumanMessage("מה התורים שלי?")]},
    config={"configurable": {"thread_id": "conv_123"}}
)
# Previous messages automatically loaded!
```

---

## 🤖 הסוכנים - תיאור מפורט

### 1. Supervisor (מנתב)

**תפקיד:**
- ניתוב בקשות לסוכן המתאים
- אכיפת RBAC
- ניהול multi-agent workflows
- החלטה מתי לסיים

**איך זה עובד:**
```python
def _supervisor_node(self, state: AgentState) -> AgentState:
    # 1. Analyze request
    last_message = state["messages"][-1]
    
    # 2. Decide which agent
    routing_decision = self.supervisor_llm.invoke([
        SystemMessage(content=supervisor_prompt)
    ])
    
    # 3. RBAC check
    user_role = state.get("user_role", "patient")
    if not can_access_agent(user_role, routing_decision):
        # Deny access
        return permission_denied_message
    
    # 4. Route to agent
    state["next_agent"] = routing_decision
    return state
```

**Routing Logic:**
```
Request: "קבע לי תור"
→ Analyze: appointment scheduling
→ Route to: Alex

Request: "מה ההכנסות החודש?"
→ Analyze: financial query
→ Check RBAC: user_role == "owner"?
→ If yes: Route to Marcus
→ If no: Deny access

Request: "יש לי התנגשות בלוח זמנים"
→ Analyze: scheduling conflict
→ Route to: Sophia
```

**RBAC Enforcement:**
```python
# Check if user can access agent
if routing_decision in ["alex", "marcus", "sophia"]:
    if not can_access_agent(user_role, routing_decision):
        # Log attempt
        logger.warning(f"User '{user_role}' denied access to '{routing_decision}'")
        
        # Return denial message
        denied_message = get_permission_denied_message(user_role, routing_decision)
        state["messages"].append(AIMessage(content=denied_message))
        state["next_agent"] = "end"
        return state
```

---

### 2. Alex (Patient Care Agent)

**תפקיד:**
- נקודת קשר ראשונית למטופלים
- ניהול תורים
- מידע כללי על המרפאה
- Triage רפואי (עם גבולות בטיחות!)

**אחריות:**
- ✅ קביעת תורים
- ✅ ביטול/שינוי תורים
- ✅ מידע על שעות פתיחה
- ✅ חיפוש מטופלים
- ✅ עדכון פרטי מטופל
- ✅ רשימת רופאים
- ⚠️ Triage רפואי (עם escalation)

**גבולות בטיחות רפואית:**
```
❌ אסור:
- אבחון מצבים רפואיים
- מרשם תרופות
- המלצות טיפול
- שינוי תוכניות טיפול
- החלטות קליניות

✅ מותר:
- מידע כללי על בריאות הפה
- קביעת תורים
- Escalation לרופא
- מידע על שירותים
```

**Escalation Protocol:**
```python
# Level 1: EMERGENCY (immediate)
EMERGENCY_KEYWORDS = [
    "severe pain", "can't breathe", "facial swelling",
    "high fever", "severe bleeding", "trauma"
]

# Level 2: DOCTOR REQUIRED (within 2 hours)
DOCTOR_REQUIRED_KEYWORDS = [
    "diagnose", "prescription", "medication",
    "treatment plan", "medical advice"
]

# Level 3: ROUTINE (next available appointment)
# Everything else
```

**כלים זמינים:**

**Production (Odoo):**
- `search_patient_odoo` - חיפוש מטופלים
- `get_patient_details_odoo` - פרטי מטופל
- `create_patient_odoo` - יצירת מטופל חדש
- `update_patient_odoo` - עדכון פרטים
- `get_doctors_list_odoo` - רשימת רופאים

**Mock (Temporary):**
- `get_available_slots_tool` - זמינות תורים (עד שנתקן Odoo)
- `create_appointment_tool` - יצירת תור (עד שנתקן Odoo)
- `get_patient_invoices_tool` - חשבוניות (עד שנממש billing)
- `get_invoice_details_tool` - פרטי חשבונית (עד שנממש billing)

**RBAC:**
- Patient: יכול לראות רק נתונים שלו
- Clinical Staff: יכול לראות כל המטופלים
- Owner: גישה מלאה

---

### 3. Marcus (CFO Agent)

**תפקיד:**
- ניתוח פיננסי
- מעקב אחר הכנסות
- ניהול תשלומים
- ניתוח רווחיות
- המלצות אסטרטגיות

**אחריות:**
- 📊 ניתוח הכנסות
- 💰 מעקב תשלומים
- 📈 ניתוח טרנדים פיננסיים
- 🎯 המלצות לשיפור רווחיות
- 📉 זיהוי בעיות פיננסיות
- 💳 ניהול חשבוניות פתוחות

**כלים זמינים:**
- `get_revenue_overview` - סקירת הכנסות
- `get_payment_status` - סטטוס תשלומים
- `get_top_treatments` - טיפולים רווחיים
- `get_outstanding_invoices` - חשבוניות פתוחות
- `analyze_profitability` - ניתוח רווחיות
- `get_financial_trends` - טרנדים פיננסיים

**Suggested Actions (Agentic):**
Marcus מנתח נתונים ומציע פעולות:

```
דוגמה 1: הכנסות יורדות
"ההכנסות החודש: ₪45,000 (ירידה של 15%)

**Suggested Actions:**
1. [Review Pricing Strategy] - בדוק תמחור מול מתחרים
2. [Analyze Patient Retention] - למה מטופלים לא חוזרים?
3. [Increase Marketing Budget] - הגבר רכישת מטופלים"

דוגמה 2: חשבוניות פתוחות גבוהות
"חשבוניות פתוחות: ₪12,000 (18% מההכנסה החודשית)

**Suggested Actions:**
1. [Send Payment Reminders] - תזכורות אוטומטיות
2. [Offer Payment Plans] - הקל על תשלום
3. [Review Collection Process] - שפר תהליכי גבייה"
```

**RBAC:**
- Patient: ❌ אין גישה
- Clinical Staff: ⚠️ רק סטטיסטיקות כלליות
- Owner: ✅ גישה מלאה

---

### 4. Sophia (Practice Admin Agent)

**תפקיד:**
- ניהול תפעול המרפאה
- פתרון קונפליקטים בלוח זמנים
- תיאום צוות
- אופטימיזציה של workflow

**אחריות:**
- 📅 ניהול לוח זמנים
- ⚠️ פתרון קונפליקטים (double bookings)
- 👥 תיאום צוות
- 🏥 ניהול חדרי טיפול
- 📊 אנליטיקה תפעולית
- ⚡ אופטימיזציה של זרימת עבודה

**כלים זמינים:**
- `get_schedule_conflicts` - זיהוי קונפליקטים
- `get_available_slots` - זמינות תורים
- `reschedule_appointment` - שינוי תור
- `get_staff_schedule` - לוח זמנים צוות
- `get_room_availability` - זמינות חדרים
- `optimize_schedule` - אופטימיזציה של לוח זמנים
- `get_operational_metrics` - מדדי תפעול

**Suggested Actions (Agentic):**
Sophia מנתחת תפעול ומציעה פעולות:

```
דוגמה 1: קונפליקטים בלוח זמנים
"נמצאו 3 double-bookings מחר ו-2 קונפליקטים בצוות

**Suggested Actions:**
1. [Resolve Double-Bookings] - שנה תורים מתנגשים
2. [Adjust Staff Schedule] - תאם כיסוי לקונפליקטים
3. [Add Buffer Time] - מנע קונפליקטים עתידיים"

דוגמה 2: ניצולת נמוכה
"ניצולת המרפאה: 65% (יעד: 85%)

**Suggested Actions:**
1. [Fill Empty Slots] - הצע תורים למטופלים ברשימת המתנה
2. [Adjust Working Hours] - שנה שעות לפי ביקוש
3. [Reduce Appointment Duration] - קצר תורים ארוכים מדי"
```

**RBAC:**
- Patient: ❌ אין גישה
- Clinical Staff: ⚠️ גישה מוגבלת (רק לוח זמנים)
- Manager/Owner: ✅ גישה מלאה

---

## 📊 AgentState - מבנה ה-State

```python
class AgentState(TypedDict):
    # Conversation
    messages: List[BaseMessage]  # All messages (with operator.add)
    
    # Current context
    current_agent: str           # Which agent is processing
    next_agent: Optional[str]    # Where to route next
    
    # User context
    user_id: str                 # User ID
    organization_id: str         # Organization/Clinic ID
    conversation_id: str         # Thread ID for memory
    user_role: str               # NEW! User's role (for RBAC)
    
    # Extracted entities
    patient_id: Optional[str]    # If discussing specific patient
    appointment_id: Optional[str] # If discussing specific appointment
    invoice_id: Optional[str]    # If discussing specific invoice
    
    # Intent & routing
    intent: Optional[str]        # Classified intent
    
    # Tool execution
    tool_results: Dict[str, Any] # Results from tool calls
    
    # Agent responses (for multi-agent)
    agent_responses: Dict[str, str]  # {agent_name: response}
    
    # Error handling
    errors: List[Dict[str, Any]]     # Error log
    rate_limit_counters: Dict[str, int]  # Rate limiting
    
    # Escalation
    requires_human: bool             # Need human intervention?
    escalation_level: Optional[str]  # EMERGENCY/DOCTOR_REQUIRED/ROUTINE
    
    # Suggested actions (Phase 7)
    suggested_actions: List[Dict[str, str]]  # Agentic suggestions
```

**איך State זורם:**
```
1. User sends message
   → messages: [HumanMessage("מה ההכנסות?")]
   → current_agent: "supervisor"

2. Supervisor analyzes
   → intent: "financial_query"
   → next_agent: "marcus"
   → current_agent: "supervisor"

3. Route to Marcus
   → current_agent: "marcus"
   → Marcus calls tools
   → tool_results: {"revenue": 45000}

4. Marcus responds
   → messages: [..., AIMessage("ההכנסות: ₪45,000")]
   → agent_responses: {"marcus": "ההכנסות: ₪45,000"}
   → suggested_actions: [{"action": "Review Pricing", ...}]

5. Back to Supervisor
   → current_agent: "supervisor"
   → Supervisor decides: done
   → next_agent: "end"

6. END
```

---

## 🔧 כלים (Tools) - קטגוריות

### Alex Tools

**Production (Odoo):**
| כלי | תיאור | RBAC |
|-----|-------|------|
| `search_patient_odoo` | חיפוש מטופלים | Patient: own only, Staff: all |
| `get_patient_details_odoo` | פרטי מטופל | Patient: own only, Staff: all |
| `create_patient_odoo` | יצירת מטופל | Staff only |
| `update_patient_odoo` | עדכון פרטים | Patient: own only, Staff: all |
| `get_doctors_list_odoo` | רשימת רופאים | All |

**Mock (Temporary):**
| כלי | תיאור | סטטוס |
|-----|-------|--------|
| `get_available_slots_tool` | זמינות תורים | ⏳ עד תיקון Odoo |
| `create_appointment_tool` | יצירת תור | ⏳ עד תיקון Odoo |
| `get_patient_invoices_tool` | חשבוניות | ⏳ עד billing integration |
| `get_invoice_details_tool` | פרטי חשבונית | ⏳ עד billing integration |

---

### Marcus (CFO) Tools

| כלי | תיאור | Output |
|-----|-------|--------|
| `get_revenue_overview` | סקירת הכנסות | Total, trend, comparison |
| `get_payment_status` | סטטוס תשלומים | Paid, pending, overdue |
| `get_top_treatments` | טיפולים רווחיים | Treatment, revenue, count |
| `get_outstanding_invoices` | חשבוניות פתוחות | List of unpaid invoices |
| `analyze_profitability` | ניתוח רווחיות | Margins, costs, profit |
| `get_financial_trends` | טרנדים פיננסיים | Monthly trends, forecasts |

**כולם Mock כרגע** - צריך אינטגרציה עם Odoo billing

---

### Sophia (Admin) Tools

| כלי | תיאור | Output |
|-----|-------|--------|
| `get_schedule_conflicts` | קונפליקטים בלוח זמנים | List of conflicts |
| `get_available_slots` | זמינות תורים | Available time slots |
| `reschedule_appointment` | שינוי תור | Success/failure |
| `get_staff_schedule` | לוח זמנים צוות | Staff availability |
| `get_room_availability` | זמינות חדרים | Room availability |
| `optimize_schedule` | אופטימיזציה | Optimized schedule |
| `get_operational_metrics` | מדדי תפעול | KPIs, utilization |

**כולם Mock כרגע** - צריך אינטגרציה עם Odoo scheduling

---

## 🔐 RBAC בגרף

### איך זה עובד

```python
# 1. User sends request
state = {
    "messages": [HumanMessage("מה ההכנסות?")],
    "user_id": "user_123",
    "user_role": "patient",  # ← From JWT token
}

# 2. Supervisor checks RBAC
routing_decision = "marcus"  # Financial query → CFO

# 3. Check permission
if not can_access_agent(user_role="patient", agent_name="marcus"):
    # DENIED!
    return "Sorry, financial data is only available to clinic owners."

# 4. If allowed, route to agent
state["next_agent"] = "marcus"
```

### Access Matrix

| User Role | Alex | Marcus | Sophia |
|-----------|------|--------|--------|
| **Patient** | ✅ Own data only | ❌ No access | ❌ No access |
| **Dentist** | ✅ All patients | ⚠️ Stats only | ⚠️ Schedule only |
| **Office Manager** | ✅ All patients | ⚠️ Reports only | ✅ Full access |
| **Owner** | ✅ Full access | ✅ Full access | ✅ Full access |

### Tool-Level RBAC

```python
def search_patient_odoo(
    query: str,
    user_id: str,
    user_role: str  # ← Passed from state
) -> List[Dict]:
    # Check if user can search all patients
    if user_role == "patient":
        # Patients can only see themselves
        return get_patient(patient_id=user_id)
    elif user_role in ["dentist", "owner", "manager"]:
        # Staff can search all patients
        return search_all_patients(query)
    else:
        raise PermissionError("You don't have permission to search patients")
```

---

## 🎯 Suggested Actions (Phase 7: Agentic System)

### מה זה?

הסוכנים לא רק עונים על שאלות - הם **מציעים פעולות** לשיפור המרפאה!

### איך זה עובד?

```python
# Agent analyzes data
revenue_data = get_revenue_overview()

# Agent decides what to suggest
if revenue_data["trend"] == "declining":
    suggested_actions = [
        {
            "action": "Review Pricing Strategy",
            "description": "Check if prices are competitive",
            "priority": "high",
            "estimated_impact": "15% revenue increase"
        },
        {
            "action": "Analyze Patient Retention",
            "description": "Identify why patients aren't returning",
            "priority": "high",
            "estimated_impact": "10% retention increase"
        }
    ]

# Add to state
state["suggested_actions"] = suggested_actions

# Frontend displays as actionable buttons
```

### דוגמאות

**Marcus (CFO):**
- "Review Pricing Strategy"
- "Send Payment Reminders"
- "Offer Payment Plans"
- "Increase Marketing Budget"
- "Hire Additional Staff"

**Sophia (Admin):**
- "Resolve Double-Bookings"
- "Adjust Staff Schedule"
- "Fill Empty Slots"
- "Send Appointment Reminders"
- "Optimize Schedule"

**Alex:**
- "Schedule Follow-Up Appointment"
- "Send Treatment Plan"
- "Update Patient Contact Info"
- "Escalate to Doctor"

---

## 🚀 Performance Optimizations

### 1. Remove Handoff Messages (50% improvement)
```python
# Before: Agent sees all messages including routing
messages = [
    HumanMessage("מה ההכנסות?"),
    AIMessage("I will delegate to CFO..."),  # ← Noise!
    AIMessage("Routing to Marcus..."),        # ← Noise!
]

# After: Clean context
messages = [
    HumanMessage("מה ההכנסות?"),
]
# Result: 50% faster, cheaper, clearer
```

### 2. LangGraph Checkpointer (vs Neo4j)
```
Before (Neo4j):
- Manual memory management
- Complex queries
- Slow (100-200ms per query)
- Hard to maintain

After (LangGraph Checkpointer):
- Automatic memory
- Simple API
- Fast (<10ms)
- Easy to maintain
```

### 3. Streaming Responses
```python
# Stream graph execution
async for chunk in graph.astream(state, config={"thread_id": conv_id}):
    # Send chunk to frontend immediately
    yield chunk
    
# Result: User sees response as it's generated
```

---

## 📝 סיכום

### מה יש לנו

✅ **LangGraph Architecture:**
- Supervisor + 3 specialized agents
- Automatic memory (MemorySaver)
- RBAC enforcement
- Performance optimizations

✅ **Agents:**
- Alex: Patient care + Odoo integration
- Marcus: Financial analysis (mock tools)
- Sophia: Operations management (mock tools)

✅ **Memory:**
- Thread-based conversations
- Automatic state persistence
- Message history management

✅ **RBAC:**
- Agent-level access control
- Tool-level access control
- Permission denied messages

✅ **Agentic Features:**
- Suggested actions
- Proactive recommendations
- Data-driven insights

### מה חסר

⚠️ **Odoo Integration:**
- Appointments (create_appointment fails)
- Billing/Invoicing (not implemented)
- Treatment notes (not implemented)

⚠️ **Memory:**
- MemorySaver is in-memory only
- Need PostgreSQL checkpointer for production
- No long-term memory (months/years)

⚠️ **Multi-Agent:**
- Currently one agent per request
- No multi-agent collaboration yet
- No agent-to-agent communication

⚠️ **Testing:**
- Need comprehensive E2E tests
- Need performance benchmarks
- Need RBAC tests

---

## 🎯 המלצות לשלב הבא

### 1. תיקון Odoo Appointments (קריטי)
- לפתור את בעיית doctor_id constraint
- לממש create_appointment עם Odoo
- לממש get_available_slots עם Odoo

### 2. Odoo Billing Integration (חשוב)
- לממש account.move (invoices)
- לחבר ל-Marcus tools
- לממש payment tracking

### 3. PostgreSQL Checkpointer (חשוב)
- להחליף MemorySaver
- Persistent memory
- Scalable

### 4. Multi-Agent Workflows (עתידי)
- אפשר לסוכנים לעבוד ביחד
- דוגמה: Alex + Marcus לתכנון טיפול + מחיר

### 5. Testing & Monitoring (קריטי)
- E2E tests
- Performance monitoring
- Error tracking

---

**זה המסמך המלא על ארכיטקטורת הסוכנים!** 🎉
