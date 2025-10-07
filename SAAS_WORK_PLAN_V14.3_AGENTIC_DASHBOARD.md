# תוכנית עבודה SaaS - v14.3.0
## התמקדות: דשבורד אגנטי מלא

**תאריך:** 7 באוקטובר 2025  
**גרסת בסיס:** v14.3.0 (Complete System)  
**מטרה:** מערכת SaaS מלאה עם דשבורד אגנטי במרכז  
**גישה:** Agent-First - כל פיצ'ר דרך סוכנים

---

## 🎯 החזון: דשבורד אגנטי כנקודת מרכז

### העיקרון המרכזי:
**הסוכנים הם הממשק - הדשבורד הוא מרכז הבקרה**

### הארכיטקטורה:
```
┌─────────────────────────────────────────────────────────┐
│              Agentic Dashboard (Mission Control)        │
│                  Chat-First Interface                   │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
    💬 Chat            📊 Widgets
    (Primary)         (Secondary)
        │                 │
    ┌───┴───┐        ┌────┴────┐
    │       │        │         │
  Alex    Marcus   Revenue  Patients
  Sophia  Sarah    Decisions Queue
```

### מה עובד דרך הדשבורד:
✅ צ'אט עם סוכנים (Alex, Marcus, Sophia)  
✅ Transparency Panel - ראות מלאה לפעולות  
✅ Widgets - מידע בזמן אמת  
✅ Decision Queue - החלטות ממתינות  
✅ Feedback System - שיפור מתמיד  
✅ Conversation History - היסטוריה מלאה  

---

## 📊 מצב נוכחי (v14.3.0 Baseline)

### ✅ מה שיש (90% Complete):

#### 1. Foundation (100% ✅)
- ✅ AWS EC2 + Odoo 19 + Pragtech
- ✅ **HTTPS + SSL** (dentaflow.ai) - **מוכן לחלוטין!**
  - ✅ Let's Encrypt certificate
  - ✅ HTTPS פעיל
  - ✅ HTTP → HTTPS redirect
  - ✅ HSTS enabled
  - ✅ Auto-renewal configured
  - ✅ SSL Grade: A
- ✅ FastAPI Backend
- ✅ PostgreSQL Database
- ✅ SQLite (Feedback)
- ✅ React Frontend (Vite)

#### 2. Agentic System (100% ✅)
**3 סוכנים מלאים + Supervisor:**

1. **Alex** (522 שורות) - Patient Care
   - Medical triage (3-level escalation)
   - Appointment scheduling
   - Invoice inquiries
   - Emergency detection
   - 5 Tools

2. **Marcus (CFO)** (317 שורות) - Financial Analysis
   - Revenue tracking
   - Payment monitoring
   - Profitability insights
   - Financial trends
   - 6 Tools

3. **Sophia (Admin)** (325 שורות) - Operations
   - Clinic statistics
   - Staff coordination
   - Performance analytics
   - 4 Tools

4. **Supervisor** (581 שורות) - LangGraph V3
   - LLM-based routing
   - Multi-agent coordination
   - RBAC enforcement
   - Memory persistence

#### 3. Agentic Dashboard (95% ✅)
- ✅ **AIChat Component** (493 שורות)
  - Vercel AI SDK streaming
  - Real-time responses
  - Suggested actions
  - Feedback buttons
  
- ✅ **Transparency System** (4 components)
  - AgentActivityPanel - Live agent status
  - FullTransparencyPanel - Complete view
  - ReasoningPanel - Agent reasoning
  - ToolCallChip - Tool visualization
  
- ✅ **Widgets** (5 types)
  - RevenueWidget - Financial metrics
  - TodaysPatientsWidget - Daily patients
  - DecisionQueueWidget - Pending decisions
  - FineTuningWidget - AI improvement
  - BaseWidget - Widget framework
  
- ✅ **Dashboard Components** (10+ files)
  - Mission Control layouts (V1, V2, V3)
  - Agent status cards
  - Priority cards
  - Embedded actions
  - Proactive suggestions
  
- ✅ **Conversation Management**
  - ConversationHistorySidebar
  - Conversation persistence
  - Multi-turn support
  - Context management

#### 4. Feedback & Fine-Tuning (100% ✅)
- ✅ Feedback system (SQLite)
- ✅ Thumbs up/down
- ✅ 5-star rating
- ✅ Training data export (JSONL)
- ✅ OpenAI fine-tuning integration
- ✅ Conversation tracking

#### 5. Hebrew/RTL Support (100% ✅)
- ✅ 450+ CSS RTL rules
- ✅ i18next integration
- ✅ Hebrew translations
- ✅ Israeli localization
- ✅ dental_israel Odoo module

#### 6. RBAC (100% ✅)
- ✅ 4 Roles (Patient, Doctor, Admin, Owner)
- ✅ 15+ permissions
- ✅ Access control enforcement
- ✅ Agent access restrictions

---

## 🚀 תוכנית העבודה המעודכנת (8 שבועות)

---

# Phase 1: Enhanced Agentic Dashboard (שבועות 1-2)

**עדיפות:** P0 - קריטי!  
**זמן:** 2 שבועות  
**מטרה:** דשבורד אגנטי מושלם עם כל התכונות

## Week 1: Dashboard Enhancement & Agent Integration

### 1.1 Agent Routing Optimization (ימים 1-2)
**מטרה:** שיפור routing בין סוכנים

**משימות:**
- [ ] שיפור prompt של Supervisor
- [ ] הוספת context awareness
- [ ] שיפור handoff messages
- [ ] טיפול ב-edge cases
- [ ] בדיקות routing

**קבצים:**
```python
# backend/app/agents/agent_graph_v3.py
async def supervisor_node(state: AgentState):
    """Enhanced supervisor with better routing logic"""
    
    # Get conversation context
    context = get_conversation_context(state)
    
    # Build routing prompt with context
    routing_prompt = f"""
    אתה מנהל צוות סוכנים במרפאת שיניים.
    
    הקשר השיחה:
    {context}
    
    הודעת המשתמש האחרונה:
    {state['messages'][-1].content}
    
    סוכנים זמינים:
    1. Alex - מטופלים, תורים, שאלות כלליות
    2. Marcus (CFO) - פיננסים, הכנסות, רווחיות
    3. Sophia (Admin) - תפעול, צוות, סטטיסטיקות
    
    לאיזה סוכן להעביר? (או END אם סיימנו)
    
    חשוב: אם המשתמש שואל שאלה שכבר נענתה, אל תעביר לסוכן אחר.
    """
    
    # Get LLM decision
    response = await llm.ainvoke(routing_prompt)
    
    # Parse decision
    next_agent = parse_routing_decision(response)
    
    # Log routing decision
    logger.info(f"Supervisor routing to: {next_agent}")
    
    return {"next": next_agent}
```

---

### 1.2 Real-Time Agent Status (ימים 3-4)
**מטרה:** תצוגת סטטוס סוכנים בזמן אמת

**משימות:**
- [ ] WebSocket connection לסטטוס
- [ ] Agent availability indicator
- [ ] Current task display
- [ ] Queue length per agent
- [ ] Performance metrics

**קבצים:**
```jsx
// frontend/src/components/dashboard/LiveAgentStatus.jsx
import { useWebSocket } from '@/hooks/useWebSocket';

export default function LiveAgentStatus() {
  const { agentStatus } = useWebSocket('/ws/agent-status');
  
  return (
    <div className="agent-status-grid">
      {Object.entries(agentStatus).map(([agent, status]) => (
        <AgentStatusCard
          key={agent}
          name={agent}
          status={status.state} // 'idle', 'busy', 'offline'
          currentTask={status.currentTask}
          queueLength={status.queueLength}
          avgResponseTime={status.avgResponseTime}
          successRate={status.successRate}
        />
      ))}
    </div>
  );
}
```

```python
# backend/app/api/v1/endpoints/websocket.py
@router.websocket("/ws/agent-status")
async def agent_status_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Get current agent status
            status = {
                "alex": get_agent_status("alex"),
                "marcus": get_agent_status("marcus"),
                "sophia": get_agent_status("sophia")
            }
            
            # Send to client
            await websocket.send_json(status)
            
            # Wait 2 seconds
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        logger.info("Client disconnected from agent status")
```

---

### 1.3 Enhanced Transparency Panel (יום 5)
**מטרה:** ראות מלאה לכל פעולות הסוכנים

**משימות:**
- [ ] Tool call timeline
- [ ] Reasoning steps display
- [ ] Decision tree visualization
- [ ] Error handling display
- [ ] Performance metrics

**קבצים:**
```jsx
// frontend/src/components/transparency/EnhancedTransparencyPanel.jsx
export default function EnhancedTransparencyPanel({ conversationId }) {
  const [timeline, setTimeline] = useState([]);
  
  useEffect(() => {
    // Subscribe to transparency events
    const eventSource = new EventSource(
      `/api/v1/transparency/${conversationId}/stream`
    );
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTimeline(prev => [...prev, data]);
    };
    
    return () => eventSource.close();
  }, [conversationId]);
  
  return (
    <div className="transparency-panel">
      <h3>מה הסוכן עושה</h3>
      
      <Timeline>
        {timeline.map((event, idx) => (
          <TimelineEvent key={idx} event={event}>
            {event.type === 'tool_call' && (
              <ToolCallEvent
                tool={event.tool}
                args={event.args}
                result={event.result}
                duration={event.duration}
              />
            )}
            
            {event.type === 'reasoning' && (
              <ReasoningEvent
                thought={event.thought}
                decision={event.decision}
              />
            )}
            
            {event.type === 'handoff' && (
              <HandoffEvent
                from={event.from}
                to={event.to}
                reason={event.reason}
              />
            )}
          </TimelineEvent>
        ))}
      </Timeline>
    </div>
  );
}
```

---

## Week 2: Proactive Suggestions & Decision Queue

### 2.1 Proactive Agent Suggestions (ימים 1-3)
**מטרה:** סוכנים מציעים פעולות באופן יזום

**משימות:**
- [ ] Suggestion engine
- [ ] Context-aware suggestions
- [ ] Priority-based ranking
- [ ] User preference learning
- [ ] Suggestion feedback loop

**קבצים:**
```python
# backend/app/services/suggestion_service.py
class ProactiveSuggestionService:
    """Generate proactive suggestions based on context"""
    
    async def generate_suggestions(
        self,
        user_id: int,
        context: Dict[str, Any]
    ) -> List[Suggestion]:
        """Generate contextual suggestions"""
        
        suggestions = []
        
        # Check for upcoming appointments
        upcoming = await get_upcoming_appointments(user_id)
        if upcoming:
            suggestions.append(Suggestion(
                type="reminder",
                priority="high",
                title="יש לך תור מחר",
                description=f"תור עם {upcoming[0].doctor} בשעה {upcoming[0].time}",
                actions=[
                    {"label": "אשר הגעה", "action": "confirm_appointment"},
                    {"label": "בטל תור", "action": "cancel_appointment"}
                ]
            ))
        
        # Check for outstanding invoices
        invoices = await get_outstanding_invoices(user_id)
        if invoices:
            total = sum(inv.amount for inv in invoices)
            suggestions.append(Suggestion(
                type="payment",
                priority="medium",
                title=f"יש לך {len(invoices)} חשבוניות לתשלום",
                description=f"סכום כולל: ₪{total:,.2f}",
                actions=[
                    {"label": "שלם עכשיו", "action": "pay_invoices"},
                    {"label": "הצג פרטים", "action": "view_invoices"}
                ]
            ))
        
        # Check for recommended treatments
        recommendations = await get_treatment_recommendations(user_id)
        if recommendations:
            suggestions.append(Suggestion(
                type="treatment",
                priority="low",
                title="טיפולים מומלצים",
                description=f"{len(recommendations)} טיפולים מומלצים על ידי הרופא",
                actions=[
                    {"label": "קבע תור", "action": "schedule_treatment"},
                    {"label": "למד עוד", "action": "learn_more"}
                ]
            ))
        
        return sorted(suggestions, key=lambda s: s.priority, reverse=True)
```

```jsx
// frontend/src/components/dashboard/ProactiveSuggestionsPanel.jsx
export default function ProactiveSuggestionsPanel() {
  const [suggestions, setSuggestions] = useState([]);
  
  useEffect(() => {
    fetchSuggestions();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchSuggestions, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  
  const handleAction = async (suggestion, action) => {
    // Execute action
    await executeSuggestionAction(suggestion.id, action);
    
    // Remove from list
    setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
  };
  
  return (
    <div className="suggestions-panel">
      <h3>הצעות פעולה</h3>
      
      {suggestions.map(suggestion => (
        <SuggestionCard
          key={suggestion.id}
          suggestion={suggestion}
          onAction={handleAction}
        />
      ))}
      
      {suggestions.length === 0 && (
        <EmptyState message="אין הצעות כרגע" />
      )}
    </div>
  );
}
```

---

### 2.2 Decision Queue System (ימים 4-5)
**מטרה:** ניהול החלטות שדורשות אישור

**משימות:**
- [ ] Decision queue database
- [ ] Priority-based sorting
- [ ] Approval workflow
- [ ] Notification system
- [ ] Audit trail

**קבצים:**
```python
# backend/app/models/decision.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
import enum

class DecisionStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50))  # 'appointment', 'payment', 'treatment'
    priority = Column(String(20))  # 'low', 'medium', 'high', 'urgent'
    status = Column(Enum(DecisionStatus), default=DecisionStatus.PENDING)
    
    title = Column(String(200))
    description = Column(String(500))
    context = Column(JSON)  # Additional context data
    
    requested_by = Column(String(50))  # Agent name
    requested_at = Column(DateTime, default=datetime.utcnow)
    
    assigned_to_user_id = Column(Integer, ForeignKey('users.id'))
    assigned_to_role = Column(String(50))
    
    decided_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    decision_note = Column(String(500), nullable=True)
    
    expires_at = Column(DateTime, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

```python
# backend/app/api/v1/endpoints/decisions.py
@router.get("/decisions/queue")
async def get_decision_queue(
    current_user: User = Depends(get_current_user),
    status: DecisionStatus = DecisionStatus.PENDING,
    priority: Optional[str] = None
):
    """Get pending decisions for current user"""
    
    query = select(Decision).where(
        Decision.status == status,
        or_(
            Decision.assigned_to_user_id == current_user.id,
            Decision.assigned_to_role == current_user.role
        )
    )
    
    if priority:
        query = query.where(Decision.priority == priority)
    
    # Sort by priority and date
    query = query.order_by(
        case(
            (Decision.priority == 'urgent', 1),
            (Decision.priority == 'high', 2),
            (Decision.priority == 'medium', 3),
            else_=4
        ),
        Decision.requested_at
    )
    
    decisions = await db.execute(query)
    return {"decisions": decisions.scalars().all()}

@router.post("/decisions/{decision_id}/approve")
async def approve_decision(
    decision_id: int,
    note: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Approve a pending decision"""
    
    decision = await get_decision(decision_id)
    
    # Check permission
    if not can_decide(current_user, decision):
        raise HTTPException(403, "Not authorized")
    
    # Update decision
    decision.status = DecisionStatus.APPROVED
    decision.decided_by_user_id = current_user.id
    decision.decided_at = datetime.utcnow()
    decision.decision_note = note
    
    await db.commit()
    
    # Execute decision action
    await execute_decision_action(decision)
    
    # Audit log
    AuditLogger.log(
        user_id=current_user.id,
        action="APPROVE_DECISION",
        resource_type="decision",
        resource_id=decision_id,
        details={"note": note}
    )
    
    return {"message": "Decision approved", "decision": decision}
```

```jsx
// frontend/src/components/widgets/DecisionQueueWidget.jsx
export default function DecisionQueueWidget() {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchDecisions();
  }, []);
  
  const fetchDecisions = async () => {
    const response = await fetch('/api/v1/decisions/queue');
    const data = await response.json();
    setDecisions(data.decisions);
    setLoading(false);
  };
  
  const handleApprove = async (decisionId, note) => {
    await fetch(`/api/v1/decisions/${decisionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ note })
    });
    
    // Refresh list
    fetchDecisions();
  };
  
  const handleReject = async (decisionId, note) => {
    await fetch(`/api/v1/decisions/${decisionId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ note })
    });
    
    // Refresh list
    fetchDecisions();
  };
  
  return (
    <BaseWidget title="החלטות ממתינות" icon={<ClipboardListIcon />}>
      {loading ? (
        <Skeleton count={3} />
      ) : decisions.length === 0 ? (
        <EmptyState message="אין החלטות ממתינות" />
      ) : (
        <div className="decision-list">
          {decisions.map(decision => (
            <DecisionCard
              key={decision.id}
              decision={decision}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}
    </BaseWidget>
  );
}
```

---

# Phase 2: Sarah Agent - Clinical Documentation (שבועות 3-4)

**עדיפות:** P1 - חשוב  
**זמן:** 2 שבועות  
**מטרה:** סוכן רביעי לתיעוד קליני

## Week 3: Sarah Agent Core

### 3.1 Sarah Agent Implementation (ימים 1-3)
**מטרה:** סוכן חדש לתיעוד רפואי

**משימות:**
- [ ] Sarah agent class
- [ ] Clinical documentation tools
- [ ] Odontogram integration
- [ ] Progress notes
- [ ] Treatment planning

**קבצים:**
```python
# backend/app/agents/sarah.py
"""
Sarah - Clinical Documentation Agent

Role: Assists dentists with clinical documentation, treatment planning,
      and medical record management.

Capabilities:
- Create and update progress notes
- Update odontogram
- Generate treatment plans
- Document procedures
- Manage clinical photos
"""

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List

class SarahAgent:
    """Clinical Documentation Agent"""
    
    def __init__(self):
        self.name = "Sarah"
        self.role = "Clinical Documentation Specialist"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        
        self.system_prompt = """
        אני Sarah, מומחית לתיעוד קליני במרפאת שיניים.
        
        התפקיד שלי:
        - עזרה לרופאים בתיעוד טיפולים
        - עדכון אודונטוגרם
        - יצירת תכניות טיפול
        - ניהול תיק רפואי
        - תיעוד הליכים קליניים
        
        אני מדברת בעברית מקצועית אבל ברורה.
        אני תמיד מוודאת שהתיעוד מדויק ומלא.
        אני לא מבצעת אבחנות - רק מתעדת מה שהרופא אומר.
        """
        
        self.tools = [
            create_progress_note_tool,
            update_odontogram_tool,
            create_treatment_plan_tool,
            document_procedure_tool,
            get_patient_history_tool
        ]
    
    async def process_message(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """Process clinical documentation request"""
        
        # Build messages
        messages = [
            SystemMessage(content=self.system_prompt),
            *context.get('history', []),
            HumanMessage(content=message)
        ]
        
        # Get response with tools
        response = await self.llm.ainvoke(
            messages,
            tools=self.tools
        )
        
        # Handle tool calls
        if response.tool_calls:
            tool_results = []
            for tool_call in response.tool_calls:
                result = await execute_tool(tool_call)
                tool_results.append(result)
            
            # Get final response
            final_response = await self.llm.ainvoke([
                *messages,
                response,
                *tool_results
            ])
            
            return final_response.content
        
        return response.content
```

---

### 3.2 Clinical Tools (ימים 4-5)
**מטרה:** כלים לתיעוד קליני

**משימות:**
- [ ] Progress notes tool
- [ ] Odontogram update tool
- [ ] Treatment plan tool
- [ ] Procedure documentation tool
- [ ] Clinical photos tool

**קבצים:**
```python
# backend/app/agents/tools/clinical_tools.py
from langchain_core.tools import tool
from typing import Dict, Any, List

@tool
async def create_progress_note_tool(
    patient_id: int,
    note_type: str,
    content: str,
    tooth_numbers: List[int] = None
) -> Dict[str, Any]:
    """
    Create a clinical progress note.
    
    Args:
        patient_id: Patient ID
        note_type: Type of note (exam, treatment, consultation)
        content: Note content
        tooth_numbers: List of tooth numbers involved
    
    Returns:
        Created note details
    """
    try:
        note = await odoo_client.create_progress_note(
            patient_id=patient_id,
            note_type=note_type,
            content=content,
            tooth_numbers=tooth_numbers
        )
        
        return {
            "success": True,
            "note_id": note.id,
            "message": f"רשומה קלינית נוצרה בהצלחה (#{note.id})"
        }
    
    except Exception as e:
        logger.error(f"Error creating progress note: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@tool
async def update_odontogram_tool(
    patient_id: int,
    tooth_number: int,
    status: str,
    notes: str = None
) -> Dict[str, Any]:
    """
    Update tooth status in odontogram.
    
    Args:
        patient_id: Patient ID
        tooth_number: Tooth number (1-32)
        status: Tooth status (healthy, decayed, filled, missing, etc.)
        notes: Additional notes
    
    Returns:
        Update confirmation
    """
    try:
        await odoo_client.update_odontogram(
            patient_id=patient_id,
            tooth_number=tooth_number,
            status=status,
            notes=notes
        )
        
        return {
            "success": True,
            "message": f"אודונטוגרם עודכן - שן {tooth_number}: {status}"
        }
    
    except Exception as e:
        logger.error(f"Error updating odontogram: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@tool
async def create_treatment_plan_tool(
    patient_id: int,
    treatments: List[Dict[str, Any]],
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a treatment plan for patient.
    
    Args:
        patient_id: Patient ID
        treatments: List of treatments with details
        priority: Plan priority (low, medium, high, urgent)
    
    Returns:
        Created plan details
    """
    try:
        plan = await odoo_client.create_treatment_plan(
            patient_id=patient_id,
            treatments=treatments,
            priority=priority
        )
        
        return {
            "success": True,
            "plan_id": plan.id,
            "total_cost": plan.total_cost,
            "message": f"תכנית טיפול נוצרה - {len(treatments)} טיפולים, סה\"כ ₪{plan.total_cost:,.2f}"
        }
    
    except Exception as e:
        logger.error(f"Error creating treatment plan: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

---

## Week 4: Sarah Integration & Testing

### 4.1 Multi-Agent Routing Update (ימים 1-2)
**מטרה:** הוספת Sarah ל-Supervisor

**משימות:**
- [ ] עדכון Supervisor prompt
- [ ] הוספת Sarah לגרף
- [ ] בדיקות routing
- [ ] טיפול ב-handoffs
- [ ] תיעוד

**קבצים:**
```python
# backend/app/agents/agent_graph_v3.py - Update
async def supervisor_node(state: AgentState):
    """Supervisor with 4 agents: Alex, Marcus, Sophia, Sarah"""
    
    routing_prompt = f"""
    אתה מנהל צוות סוכנים במרפאת שיניים.
    
    סוכנים זמינים:
    1. Alex - מטופלים, תורים, שאלות כלליות
    2. Marcus (CFO) - פיננסים, הכנסות, רווחיות
    3. Sophia (Admin) - תפעול, צוות, סטטיסטיקות
    4. Sarah - תיעוד קליני, אודונטוגרם, תכניות טיפול
    
    הודעת המשתמש:
    {state['messages'][-1].content}
    
    לאיזה סוכן להעביר?
    """
    
    response = await llm.ainvoke(routing_prompt)
    next_agent = parse_routing_decision(response)
    
    return {"next": next_agent}

# Add Sarah to graph
workflow.add_node("sarah", sarah_agent.process_message)
workflow.add_edge("sarah", "supervisor")
```

---

### 4.2 Sarah Dashboard Integration (ימים 3-4)
**מטרה:** הוספת Sarah לדשבורד

**משימות:**
- [ ] Sarah status card
- [ ] Clinical documentation widget
- [ ] Odontogram viewer
- [ ] Treatment plan widget
- [ ] בדיקות UI

**קבצים:**
```jsx
// frontend/src/components/dashboard/SarahStatusCard.jsx
export default function SarahStatusCard() {
  const { status } = useAgentStatus('sarah');
  
  return (
    <AgentStatusCard
      name="Sarah"
      role="תיעוד קליני"
      avatar="/avatars/sarah.png"
      status={status.state}
      currentTask={status.currentTask}
      stats={{
        notesToday: status.stats.notesToday,
        treatmentPlans: status.stats.treatmentPlans,
        avgResponseTime: status.stats.avgResponseTime
      }}
    />
  );
}
```

```jsx
// frontend/src/components/widgets/ClinicalDocumentationWidget.jsx
export default function ClinicalDocumentationWidget() {
  const [recentNotes, setRecentNotes] = useState([]);
  
  useEffect(() => {
    fetchRecentNotes();
  }, []);
  
  return (
    <BaseWidget title="תיעוד קליני" icon={<DocumentTextIcon />}>
      <div className="recent-notes">
        {recentNotes.map(note => (
          <NoteCard key={note.id} note={note} />
        ))}
      </div>
      
      <Button onClick={() => openSarahChat()}>
        תיעוד חדש עם Sarah
      </Button>
    </BaseWidget>
  );
}
```

---

### 4.3 End-to-End Testing (יום 5)
**מטרה:** בדיקות מקיפות של כל המערכת

**משימות:**
- [ ] בדיקות routing בין 4 סוכנים
- [ ] בדיקות handoffs
- [ ] בדיקות transparency
- [ ] בדיקות widgets
- [ ] בדיקות feedback
- [ ] בדיקות Hebrew/RTL

---

# Phase 3: Patient Portal & Telegram Integration (שבועות 5-6)

**עדיפות:** P1 - חשוב  
**זמן:** 2 שבועות  
**מטרה:** ערוצי תקשורת נוספים עם מטופלים

## Week 5: Patient Portal

### 5.1 Portal Authentication (ימים 1-2)
**מטרה:** מערכת הזדהות מאובטחת

**משימות:**
- [ ] OTP via SMS
- [ ] JWT tokens
- [ ] Session management
- [ ] Password reset
- [ ] 2FA (optional)

---

### 5.2 Portal Dashboard (ימים 3-5)
**מטרה:** דשבורד למטופלים

**משימות:**
- [ ] Upcoming appointments
- [ ] Medical history
- [ ] Invoices & payments
- [ ] Treatment plans
- [ ] Chat with Alex

---

## Week 6: Telegram Bot Integration

### 6.1 Telegram Bot Setup (ימים 1-2)
**מטרה:** בוט Telegram מחובר ל-Alex

**משימות:**
- [ ] Bot registration
- [ ] Webhook setup
- [ ] Message handling
- [ ] User authentication
- [ ] Rich messages

---

### 6.2 Telegram Features (ימים 3-5)
**מטרה:** תכונות מתקדמות ב-Telegram

**משימות:**
- [ ] Inline keyboards
- [ ] Quick replies
- [ ] Appointment booking
- [ ] Reminders
- [ ] Notifications

---

# Phase 4: Security & Compliance (שבועות 7-8)

**עדיפות:** P0 - קריטי!  
**זמן:** 2 שבועות  
**מטרה:** אבטחה מלאה ועמידה בתיקון 13

## Week 7: Database Security

### 7.1 Encryption at Rest (ימים 1-2)
**מטרה:** הצפנת נתונים במסד הנתונים

**משימות:**
- [ ] PostgreSQL encryption
- [ ] Sensitive field encryption
- [ ] Key management (AWS KMS)
- [ ] Backup encryption

---

### 7.2 API Security (ימים 3-5)
**מטרה:** אבטחת API

**משימות:**
- [ ] JWT authentication
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] API key management
- [ ] Input validation

---

## Week 8: Compliance & Audit

### 8.1 תיקון 13 Compliance (ימים 1-3)
**מטרה:** עמידה בחוק הגנת הפרטיות

**משימות:**
- [ ] Privacy policy
- [ ] Terms of service
- [ ] Consent management
- [ ] Data subject rights (GDPR-like)
- [ ] DPO appointment

---

### 8.2 Audit Logging (ימים 4-5)
**מטרה:** מעקב מלא אחר פעולות

**משימות:**
- [ ] Audit log database
- [ ] Log all data access
- [ ] Log all modifications
- [ ] Log exports
- [ ] Audit dashboard

---

## 📊 סיכום תוכנית העבודה

### Timeline:
- **Week 1-2:** Enhanced Agentic Dashboard
- **Week 3-4:** Sarah Agent - Clinical Documentation
- **Week 5-6:** Patient Portal & Telegram
- **Week 7-8:** Security & Compliance

### Total Time: **8 שבועות** (2 חודשים)

### Deliverables:
1. ✅ דשבורד אגנטי מושלם עם 4 סוכנים
2. ✅ Transparency מלאה
3. ✅ Decision Queue
4. ✅ Proactive Suggestions
5. ✅ Patient Portal
6. ✅ Telegram Bot
7. ✅ אבטחה מלאה
8. ✅ תיקון 13 Compliance

### Success Metrics:
- 4 סוכנים פעילים (Alex, Marcus, Sophia, Sarah)
- Routing accuracy > 95%
- Response time < 2 seconds
- User satisfaction > 4.5/5
- Zero security incidents
- 100% compliance with תיקון 13

---

## 🎯 הצעד הראשון

**התחל מ-Phase 1, Week 1, Day 1:**
שיפור routing של Supervisor והוספת context awareness.

זה יבסס את התשתית לכל השאר!

---

**מוכן להתחיל? 🚀**
