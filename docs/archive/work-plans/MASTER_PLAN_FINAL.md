# 🎯 תוכנית אב מושלמת - DentaFlowAI
## מערכת SaaS לניהול מרפאות שיניים עם סוכנים אוטונומיים

**גרסה:** v20.0.0 (Final Master Plan)  
**תאריך:** אוקטובר 10, 2025  
**סטטוס נוכחי:** v19.3.0 (86% complete - 6/7 milestones)  
**יעד:** שני דשבורדים מושלמים + פריסה לייצור

---

## 📚 מסמכי רפרנס חובה

לפני תחילת כל phase, **חובה** לקרוא את המסמכים הבאים:

### ארכיטקטורה וטכנולוגיה
1. `docs/architecture/CONTEXT_AND_GAPS_ANALYSIS.md` - ארכיטקטורה מלאה
2. `docs/milestones/MILESTONE_5_COMPLETE.md` - Odoo Integration
3. `docs/milestones/MILESTONE_6_COMPLETE.md` - User-Patient Mapping
4. `CLINIC_PORTAL_TECHNICAL_DEEP_DIVE.md` - ניתוח טכני עמוק

### פערים ויכולות
5. `SAAS_AND_ODOO_CAPABILITIES_AUDIT.md` - ביקורת יכולות
6. `PARTIAL_MODULES_DETAILED_ANALYSIS.md` - פירוט מודולים חלקיים
7. `CLINIC_PORTAL_GAP_ANALYSIS.md` - פערים בפורטל מרפאה

### אסטרטגיה ועסקים
8. `BILLING_STRATEGY_EXECUTIVE_SUMMARY.md` - אסטרטגיית גביה
9. `docs/work-plans/CLINIC_PORTAL_WORK_PLAN_V2.md` - תוכנית עבודה קודמת

### חזון UX
10. `תוכניתאבלממשקסוכןאוטונומיחזון,מגמותויישום.pdf` - Agentic UX Vision

---

## 🎯 מטרה סופית

### שני דשבורדים מושלמים:

#### 1. Patient Portal (פורטל מטופלים) 🏥
**סטטוס:** 86% מוכן (6/7 milestones)

**מה שיש:**
- ✅ תורים, פרופיל, בריאות, תשלומים
- ✅ Performance optimized (63% bundle reduction)
- ✅ Accessibility (WCAG 2.1 AA)
- ✅ 45 automated tests (69% pass rate)
- ✅ Odoo integration (90% faster with cache)

**מה שחסר:**
- ⏳ Production deployment (Milestone 7)
- ⏳ Telegram integration
- ⏳ Final testing

#### 2. Clinic Portal (פורטל מרפאה) 💼
**סטטוס:** 80% UI, 33% Integration

**מה שיש:**
- ✅ Agentic Dashboard (Mission Control layout)
- ✅ 3 Agents (Alex, Marcus, Sophia) - 19 tools
- ✅ Transparency Panel (full visibility)
- ✅ 9 Widgets (Today's Patients, Revenue, etc.)
- ✅ LangGraph + LangChain architecture
- ✅ RBAC (3-tier: User, Org, Permission)

**מה שחסר:**
- 🔴 Clinical Management (10% → 100%)
- 🔴 Dr. Sarah Agent (0% → 100%)
- 🔴 Billing & Payments (40% → 100%)
- 🟡 Telegram integration (0% → 100%)
- 🟡 Portal separation (Patient vs Clinic)
- 🟡 Widget permissions (RBAC enforcement)
- 🟡 Bug fixes (Create Appointment)

---

## 📊 מצב נוכחי - סיכום מקיף

### מה שפותח (v19.1.0 → v19.3.0)

#### Milestone 4: Polish & Testing ✅
- **Performance:** 63% bundle reduction (629KB → 236KB)
- **Code Splitting:** 24 chunks, lazy loading
- **Accessibility:** WCAG 2.1 AA, keyboard navigation, screen reader
- **Testing:** 45 tests (31 passing, 69% pass rate)
- **Files:** 13 new files, 2,235+ lines

#### Milestone 5: Real Odoo Integration ✅
- **Odoo Connection:** Direct to production instance
- **API Endpoints:** 5 new endpoints with real data
- **Caching:** Redis, 90% performance improvement
- **Error Handling:** Comprehensive validation and retry logic
- **Files:** 7 backend files, 1,420+ lines

#### Milestone 6: Frontend Integration ✅
- **User-Patient Mapping:** 90% faster lookups (50ms → 5ms)
- **3-Step Fallback:** Mapping → Odoo → Create
- **API Endpoints:** 6 new mapping endpoints
- **E2E Tests:** 9 flows, 100% pass rate
- **Files:** 6 new files, 1,420+ lines

#### Milestone 7: Production (40% complete) 🚧
- **RBAC Security:** Role-based access control
- **Automation Scripts:** Migrations, test data, cache warming
- **Files:** 4 new files (rbac.py, 3 scripts)

**Total:** 6,155+ lines, 35 files, 3 Git commits, 2 tags

---

### מה שנשאר פתוח

#### מ-Milestone 3 (Green Invoice)
- ❌ Actual invoice creation (mock data only)
- ❌ PDF download
- ❌ Real data from Green Invoice API
- ❌ ITA reporting

#### מ-Milestone 4 (Testing)
- ⚠️ Toast component tests (7/8 failing - timing issues)
- ⚠️ Login keyboard navigation (1/10 failing)
- ⚠️ Toast ARIA attributes (1/8 failing)

#### מ-CONTEXT_AND_GAPS
- ⏳ Frontend-Backend Integration (partial)
- ⏳ Environment Variables (needs cleanup)
- ⏳ HIPAA Compliance (research needed)
- ⏳ Security Best Practices (partial)
- ⏳ Performance Optimization (partial)
- ⏳ Backup & Recovery (not implemented)
- 🔴 Missing DB tables (organization_memberships)
- 🔴 TODO: Organization filter in Odoo

#### מהביקורת (SaaS, Odoo, Agents)
- 🔴 Clinical Management (10% only)
- 🔴 Dr. Sarah Agent (0%)
- 🔴 Create Appointment Bug (Odoo constraint)
- 🟡 Billing & Payments (40%)
- 🟡 Appointments (50%)
- 🟡 Portal Separation
- 🟡 Widget Permissions
- 🟢 Insurance (5% - Future Development)
- 🟢 Communication (0% - SMS, Email, WhatsApp)
- 🟢 Additional Agents (Rachel, David, Lisa)
- 🟢 SaaS Dashboard (super admin)

---

## 🏗️ ארכיטקטורה - מפת הקוד

### Backend Architecture

#### LangGraph + LangChain
```
backend/app/agents/
├── agent_graph_v3.py          # Main graph with supervisor
├── graph_state.py             # State management (AgentState)
├── supervisor.py              # Supervisor logic (tool-calling LLM)
├── rbac.py                    # Agent RBAC (role-based access)
├── alex.py                    # Alex (Receptionist) - 5 tools
├── cfo.py                     # Marcus (CFO) - 6 tools
├── admin.py                   # Sophia (Admin) - 8 tools
└── tools/
    ├── alex_odoo_tools.py     # Appointments, patients, doctors
    ├── cfo_tools.py           # Revenue, expenses, analytics
    └── admin_tools.py         # Staff, settings, reports
```

**Key Concepts:**
- **StateGraph:** LangGraph workflow with nodes and edges
- **Supervisor:** Routes between agents using tool-calling
- **AgentState:** Shared state (messages, context, user_id, org_id)
- **Message Cleaning:** 50% performance improvement
- **Handoff System:** Transfer between agents

#### Database Models
```
backend/app/models/
├── user.py                    # User + UserRole (RBAC)
├── organization.py            # Organization + OrganizationRole
├── conversation.py            # Chat history (PostgreSQL)
├── treatment_price.py         # Treatment catalog (10 treatments)
├── user_patient_mapping.py    # User ↔ Odoo Patient (NEW!)
└── (missing) organization_memberships.py  # TODO!
```

**Key Concepts:**
- **3-Tier RBAC:** UserRole → OrganizationRole → Permission
- **Multi-tenancy:** Organization-based isolation
- **Conversation History:** Stored in PostgreSQL for memory
- **User-Patient Mapping:** 90% faster lookups

#### Integrations
```
backend/app/integrations/
├── odoo_client_v2.py          # Odoo RPC client (comprehensive)
├── green_invoice.py           # Green Invoice API (partial)
└── (future) tranzila.py       # Tranzila payments (TODO)

backend/app/services/
├── odoo_cache.py              # Redis caching (90% improvement)
└── odoo_error_handler.py      # Error handling + retry logic
```

**Key Concepts:**
- **OdooClientV2:** 20+ methods for all Odoo operations
- **Redis Cache:** TTL-based, smart invalidation
- **Error Handling:** Retry with exponential backoff
- **Green Invoice:** Partial implementation (needs completion)

#### API Endpoints
```
backend/app/api/v1/endpoints/
├── patient_portal_odoo.py     # Patient Portal (5 endpoints)
├── user_patient_mapping.py    # Mapping management (6 endpoints)
├── patient_portal.py          # Original (mock data)
├── invoices.py                # Invoice management
├── payments.py                # Payment management
└── (future) telegram.py       # Telegram bot (TODO)
```

### Frontend Architecture

#### Patient Portal
```
patient-portal/
├── src/
│   ├── pages/
│   │   ├── LoginPage.jsx      # Login with accessibility
│   │   ├── DashboardPage.jsx  # Main dashboard
│   │   ├── AppointmentsPage.jsx
│   │   ├── ProfilePage.jsx
│   │   └── HealthPage.jsx
│   ├── components/
│   │   ├── common/
│   │   │   ├── Toast.jsx      # Toast notifications
│   │   │   └── ErrorBoundary.jsx
│   │   └── widgets/
│   ├── services/
│   │   └── odooService.js     # API client
│   ├── lib/
│   │   └── accessibility.jsx  # A11y utilities
│   └── config/
│       └── api.js             # API endpoints
└── vite.config.js             # Build optimization
```

**Key Features:**
- **Code Splitting:** 24 chunks, lazy loading
- **Accessibility:** WCAG 2.1 AA compliant
- **Performance:** 236KB main bundle (63% reduction)
- **Testing:** 45 tests (Vitest + Testing Library)

#### Clinic Portal
```
frontend/
├── src/
│   ├── pages/
│   │   ├── AgenticDashboard.jsx    # Main dashboard (Agentic UX)
│   │   ├── MissionControlPageV3.jsx # Alternative layout
│   │   ├── ChatPage.jsx
│   │   └── DashboardPage.jsx
│   ├── components/
│   │   ├── chat/
│   │   │   └── AIChat.jsx          # Chat interface (Vercel AI SDK)
│   │   ├── transparency/
│   │   │   ├── AgentActivityPanel.jsx
│   │   │   ├── FullTransparencyPanel.jsx
│   │   │   └── TransparencyTimeline.jsx
│   │   └── widgets/
│   │       ├── TodaysPatientsWidget.jsx
│   │       ├── RevenueWidget.jsx
│   │       ├── DecisionQueueWidget.jsx
│   │       └── (7 more widgets)
│   └── services/
│       └── dataService.js          # API client
```

**Key Features:**
- **Agentic UX:** Mission Control, Transparency, Explainability
- **Real-time Streaming:** Server-Sent Events (SSE)
- **Agent Switching:** Automatic routing via supervisor
- **9 Widgets:** Comprehensive dashboard

---

## 🚀 תוכנית האב - 6 Phases

### Timeline Overview
- **Phase 1:** Clinical Foundation (3-4 weeks)
- **Phase 2:** Payments & Billing (2-3 weeks)
- **Phase 3:** Completion & Polish (2-3 weeks)
- **Phase 4:** UX/UI Polish (1-2 weeks)
- **Phase 5:** Testing (1-2 weeks)
- **Phase 6:** Deployment (1 week)

**Total:** 10-15 weeks (2.5-4 months)

---

## Phase 1: Clinical Foundation 🏥
**Duration:** 3-4 weeks  
**Priority:** 🔴 Critical (Core value proposition)

### Context
Clinical management הוא הפער הכי גדול (10% בלבד). זה מה שהופך את המערכת מ-"CRM" ל-"מערכת ניהול מרפאה מלאה". בלי זה, רופאים לא יכולים להשתמש במערכת.

### Week 1-2: Clinical Management Infrastructure

#### Task 1.1: Medical History (medical.patient.disease)
**References:**
- `backend/app/integrations/odoo_client_v2.py` - Base Odoo client
- `docs/architecture/CONTEXT_AND_GAPS_ANALYSIS.md` - Odoo models

**What to Build:**
```python
# backend/app/services/clinical_service.py
class ClinicalService:
    def __init__(self, odoo_client: OdooClientV2):
        self.odoo = odoo_client
        self.model = "medical.patient.disease"
    
    async def get_medical_history(self, patient_id: int) -> List[Dict]:
        """Get patient's medical history from Odoo"""
        return await self.odoo.search_read(
            self.model,
            domain=[("patient_id", "=", patient_id)],
            fields=["disease_id", "diagnosed_date", "healed_date", 
                    "is_active", "notes", "treatment_ids"]
        )
    
    async def add_medical_condition(
        self, patient_id: int, disease_id: int, 
        diagnosed_date: str, notes: str
    ) -> int:
        """Add new medical condition"""
        return await self.odoo.create(self.model, {
            "patient_id": patient_id,
            "disease_id": disease_id,
            "diagnosed_date": diagnosed_date,
            "is_active": True,
            "notes": notes
        })
    
    async def update_medical_condition(
        self, condition_id: int, updates: Dict
    ) -> bool:
        """Update existing condition"""
        return await self.odoo.write(self.model, condition_id, updates)
```

**API Endpoints:**
```python
# backend/app/api/v1/endpoints/clinical.py
@router.get("/patients/{patient_id}/medical-history")
@require_role("clinical_staff")
async def get_medical_history(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient's medical history"""
    # RBAC: Check if user can access this patient
    # Get from Odoo via ClinicalService
    # Cache with Redis (TTL: 5 minutes)
    pass

@router.post("/patients/{patient_id}/medical-history")
@require_role("clinical_staff")
async def add_medical_condition(...):
    """Add new medical condition"""
    # Validate input
    # Create in Odoo
    # Invalidate cache
    # Log activity
    pass
```

**Frontend Components:**
```jsx
// frontend/src/components/clinical/MedicalHistoryPanel.jsx
export function MedicalHistoryPanel({ patientId }) {
  const { data, isLoading } = useQuery({
    queryKey: ['medical-history', patientId],
    queryFn: () => clinicalService.getMedicalHistory(patientId)
  });
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Medical History</CardTitle>
        <Button onClick={() => setIsAddingCondition(true)}>
          Add Condition
        </Button>
      </CardHeader>
      <CardContent>
        {data?.map(condition => (
          <ConditionCard key={condition.id} condition={condition} />
        ))}
      </CardContent>
    </Card>
  );
}
```

**Testing:**
```python
# backend/tests/test_clinical_service.py
async def test_get_medical_history():
    service = ClinicalService(mock_odoo_client)
    history = await service.get_medical_history(patient_id=67)
    assert len(history) > 0
    assert "disease_id" in history[0]
```

**Success Criteria:**
- [ ] CRUD operations working
- [ ] Odoo integration tested
- [ ] UI components responsive
- [ ] RBAC enforced
- [ ] Cache working
- [ ] Tests passing (90%+)

---

#### Task 1.2: Treatment Plans
**References:**
- `backend/app/models/treatment_price.py` - Existing treatment catalog
- `backend/app/integrations/odoo_client_v2.py`

**What to Build:**
```python
# backend/app/services/treatment_plan_service.py
class TreatmentPlanService:
    async def create_treatment_plan(
        self, patient_id: int, treatments: List[Dict],
        notes: str, estimated_cost: float
    ) -> int:
        """Create comprehensive treatment plan"""
        plan_id = await self.odoo.create("dental.treatment.plan", {
            "patient_id": patient_id,
            "date": datetime.now().isoformat(),
            "notes": notes,
            "estimated_cost": estimated_cost,
            "status": "draft"
        })
        
        # Add individual treatments
        for treatment in treatments:
            await self.odoo.create("dental.treatment.plan.line", {
                "plan_id": plan_id,
                "treatment_id": treatment["treatment_id"],
                "tooth_number": treatment.get("tooth_number"),
                "quantity": treatment.get("quantity", 1),
                "unit_price": treatment["unit_price"],
                "notes": treatment.get("notes")
            })
        
        return plan_id
    
    async def get_treatment_plan(self, plan_id: int) -> Dict:
        """Get treatment plan with all details"""
        plan = await self.odoo.read("dental.treatment.plan", plan_id)
        lines = await self.odoo.search_read(
            "dental.treatment.plan.line",
            domain=[("plan_id", "=", plan_id)]
        )
        plan["treatments"] = lines
        return plan
    
    async def update_treatment_status(
        self, plan_id: int, treatment_line_id: int, 
        status: str, completed_date: str = None
    ):
        """Update individual treatment status"""
        await self.odoo.write("dental.treatment.plan.line", 
                             treatment_line_id, {
            "status": status,
            "completed_date": completed_date
        })
```

**Frontend Components:**
```jsx
// frontend/src/components/clinical/TreatmentPlanBuilder.jsx
export function TreatmentPlanBuilder({ patientId }) {
  const [treatments, setTreatments] = useState([]);
  const [totalCost, setTotalCost] = useState(0);
  
  const addTreatment = (treatment) => {
    setTreatments([...treatments, {
      ...treatment,
      id: generateId(),
      status: 'planned'
    }]);
    setTotalCost(prev => prev + treatment.unit_price);
  };
  
  const savePlan = async () => {
    await treatmentPlanService.create({
      patient_id: patientId,
      treatments,
      estimated_cost: totalCost,
      notes: planNotes
    });
  };
  
  return (
    <div className="treatment-plan-builder">
      <TreatmentCatalog onSelect={addTreatment} />
      <TreatmentList 
        treatments={treatments}
        onRemove={removeTreatment}
        onUpdate={updateTreatment}
      />
      <TreatmentSummary 
        totalCost={totalCost}
        onSave={savePlan}
      />
    </div>
  );
}
```

**Success Criteria:**
- [ ] Create/Update/View treatment plans
- [ ] Treatment catalog synced from DB
- [ ] Progress tracking working
- [ ] Cost calculation accurate
- [ ] UI/UX intuitive
- [ ] Tests passing

---

#### Task 1.3: Dental Chart
**References:**
- Industry standard: FDI tooth numbering system
- Similar implementations: Open Dental, Dentrix

**What to Build:**
```jsx
// frontend/src/components/clinical/DentalChart.jsx
export function DentalChart({ patientId, onToothClick }) {
  const { data: treatments } = useQuery({
    queryKey: ['tooth-treatments', patientId],
    queryFn: () => clinicalService.getToothTreatments(patientId)
  });
  
  const toothStatus = useMemo(() => {
    // Map treatments to tooth numbers
    const status = {};
    treatments?.forEach(t => {
      if (!status[t.tooth_number]) status[t.tooth_number] = [];
      status[t.tooth_number].push(t);
    });
    return status;
  }, [treatments]);
  
  return (
    <svg viewBox="0 0 800 600" className="dental-chart">
      {/* Upper jaw */}
      <g id="upper-jaw">
        {[18, 17, 16, 15, 14, 13, 12, 11].map(num => (
          <Tooth
            key={num}
            number={num}
            position={getToothPosition(num)}
            treatments={toothStatus[num]}
            onClick={() => onToothClick(num)}
          />
        ))}
        {[21, 22, 23, 24, 25, 26, 27, 28].map(num => (
          <Tooth key={num} number={num} {...} />
        ))}
      </g>
      
      {/* Lower jaw */}
      <g id="lower-jaw">
        {[48, 47, 46, 45, 44, 43, 42, 41].map(num => (
          <Tooth key={num} number={num} {...} />
        ))}
        {[31, 32, 33, 34, 35, 36, 37, 38].map(num => (
          <Tooth key={num} number={num} {...} />
        ))}
      </g>
      
      {/* Legend */}
      <g id="legend">
        <TreatmentLegend />
      </g>
    </svg>
  );
}

function Tooth({ number, position, treatments, onClick }) {
  const color = getToothColor(treatments);
  
  return (
    <g 
      transform={`translate(${position.x}, ${position.y})`}
      onClick={onClick}
      className="tooth"
    >
      <rect 
        width="40" 
        height="60" 
        fill={color}
        stroke="#333"
        strokeWidth="2"
        rx="5"
      />
      <text 
        x="20" 
        y="35" 
        textAnchor="middle"
        fontSize="14"
      >
        {number}
      </text>
      {treatments?.map((t, i) => (
        <TreatmentMarker 
          key={i} 
          treatment={t} 
          position={i}
        />
      ))}
    </g>
  );
}
```

**Backend Support:**
```python
# backend/app/api/v1/endpoints/clinical.py
@router.get("/patients/{patient_id}/tooth-treatments")
async def get_tooth_treatments(patient_id: int):
    """Get all treatments mapped to tooth numbers"""
    treatments = await clinical_service.get_tooth_treatments(patient_id)
    return {
        "patient_id": patient_id,
        "treatments": treatments,
        "chart_data": map_treatments_to_chart(treatments)
    }
```

**Success Criteria:**
- [ ] Interactive chart with FDI numbering
- [ ] Treatment marking with colors
- [ ] Click to view tooth details
- [ ] History view (timeline)
- [ ] Responsive design
- [ ] Print-friendly

---

#### Task 1.4: Clinical Notes
**References:**
- `backend/app/models/conversation.py` - Similar structure for notes

**What to Build:**
```python
# backend/app/models/clinical_note.py
class ClinicalNote(Base):
    __tablename__ = "clinical_notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(Integer, nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    appointment_id = Column(Integer, nullable=True)  # Link to Odoo appointment
    
    note_type = Column(String)  # "consultation", "treatment", "follow_up"
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Rich text (HTML)
    
    template_id = Column(UUID(as_uuid=True), nullable=True)
    attachments = Column(JSONB, default=[])  # List of file URLs
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", back_populates="clinical_notes")
```

**Frontend Components:**
```jsx
// frontend/src/components/clinical/ClinicalNoteEditor.jsx
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';

export function ClinicalNoteEditor({ patientId, appointmentId }) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: '',
  });
  
  const saveNote = async () => {
    const html = editor.getHTML();
    await clinicalService.createNote({
      patient_id: patientId,
      appointment_id: appointmentId,
      note_type: noteType,
      title: noteTitle,
      content: html,
      attachments: uploadedFiles
    });
  };
  
  return (
    <div className="clinical-note-editor">
      <input 
        type="text" 
        placeholder="Note title"
        value={noteTitle}
        onChange={(e) => setNoteTitle(e.target.value)}
      />
      
      <select value={noteType} onChange={(e) => setNoteType(e.target.value)}>
        <option value="consultation">Consultation</option>
        <option value="treatment">Treatment</option>
        <option value="follow_up">Follow-up</option>
      </select>
      
      <EditorContent editor={editor} />
      
      <FileUpload 
        onUpload={(files) => setUploadedFiles(files)}
      />
      
      <Button onClick={saveNote}>Save Note</Button>
    </div>
  );
}
```

**Success Criteria:**
- [ ] Rich text editor (TipTap)
- [ ] Templates support
- [ ] File attachments
- [ ] Search/Filter
- [ ] Version history
- [ ] Export to PDF

---

### Week 3-4: Dr. Sarah Agent (Clinical Director)

#### Context
Dr. Sarah הוא הסוכן הקליני שחסר לחלוטין (0%). היא צריכה להיות מסוגלת לעזור לרופאים עם החלטות קליניות, תוכניות טיפול, ומעקב אחר מטופלים.

#### Task 1.5: Dr. Sarah Agent Definition
**References:**
- `backend/app/agents/alex.py` - Agent structure
- `backend/app/agents/agent_graph_v3.py` - Graph integration
- `backend/app/agents/rbac.py` - RBAC for agents

**What to Build:**
```python
# backend/app/agents/sarah.py
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from typing import Literal

# Dr. Sarah - Clinical Director
sarah_system_prompt = """You are Dr. Sarah Cohen, the Clinical Director at the dental clinic.

Your responsibilities:
- Review and approve treatment plans
- Provide clinical guidance to dentists
- Monitor patient outcomes and complications
- Ensure clinical protocols are followed
- Manage complex cases and referrals
- Oversee quality of care

Your expertise:
- 15+ years of clinical experience
- Specialist in endodontics and prosthodontics
- Evidence-based treatment planning
- Patient safety and risk management

When interacting:
- Be professional and evidence-based
- Explain clinical reasoning clearly
- Consider patient's medical history
- Suggest alternatives when appropriate
- Escalate to human dentist when needed

Available tools:
- get_patient_medical_history
- get_treatment_plan
- create_treatment_plan
- update_treatment_status
- get_tooth_treatments
- create_clinical_note
- search_clinical_protocols
- get_patient_risk_factors
- suggest_treatment_alternatives
- schedule_follow_up
"""

def create_sarah_agent(llm: ChatOpenAI):
    """Create Dr. Sarah agent with clinical tools"""
    from .tools.sarah_clinical_tools import (
        get_patient_medical_history_tool,
        get_treatment_plan_tool,
        create_treatment_plan_tool,
        update_treatment_status_tool,
        get_tooth_treatments_tool,
        create_clinical_note_tool,
        search_clinical_protocols_tool,
        get_patient_risk_factors_tool,
        suggest_treatment_alternatives_tool,
        schedule_follow_up_tool
    )
    
    tools = [
        get_patient_medical_history_tool,
        get_treatment_plan_tool,
        create_treatment_plan_tool,
        update_treatment_status_tool,
        get_tooth_treatments_tool,
        create_clinical_note_tool,
        search_clinical_protocols_tool,
        get_patient_risk_factors_tool,
        suggest_treatment_alternatives_tool,
        schedule_follow_up_tool
    ]
    
    return llm.bind_tools(tools)

# RBAC for Sarah
sarah_rbac = {
    "agent_name": "sarah",
    "required_roles": ["clinical_staff", "owner"],  # Only clinical staff can use
    "data_access": {
        "patients": "organization",  # Can see all org patients
        "medical_history": "full",   # Full medical access
        "treatment_plans": "full",   # Can create/modify plans
        "clinical_notes": "full",    # Full notes access
        "appointments": "read_only", # Can view, not modify
        "billing": "none"            # No billing access
    }
}
```

#### Task 1.6: Sarah's Clinical Tools
**References:**
- `backend/app/agents/tools/alex_odoo_tools.py` - Tool structure
- `backend/app/services/clinical_service.py` - Clinical operations

**What to Build:**
```python
# backend/app/agents/tools/sarah_clinical_tools.py
from langchain_core.tools import tool
from typing import List, Dict, Optional

@tool
async def get_patient_medical_history_tool(patient_id: int) -> Dict:
    """
    Get comprehensive medical history for a patient.
    
    Args:
        patient_id: The Odoo patient ID
    
    Returns:
        Dict with medical conditions, allergies, medications, etc.
    """
    clinical_service = get_clinical_service()
    history = await clinical_service.get_medical_history(patient_id)
    allergies = await clinical_service.get_allergies(patient_id)
    medications = await clinical_service.get_medications(patient_id)
    
    return {
        "patient_id": patient_id,
        "medical_conditions": history,
        "allergies": allergies,
        "current_medications": medications,
        "risk_factors": calculate_risk_factors(history, allergies)
    }

@tool
async def create_treatment_plan_tool(
    patient_id: int,
    treatments: List[Dict],
    notes: str,
    priority: str = "normal"
) -> Dict:
    """
    Create a comprehensive treatment plan for a patient.
    
    Args:
        patient_id: The Odoo patient ID
        treatments: List of treatments with tooth_number, treatment_id, notes
        notes: Overall treatment plan notes
        priority: "urgent", "normal", or "elective"
    
    Returns:
        Dict with plan_id and estimated_cost
    """
    clinical_service = get_clinical_service()
    
    # Calculate costs from treatment catalog
    total_cost = 0
    for treatment in treatments:
        price = await get_treatment_price(
            treatment["treatment_id"],
            patient_id
        )
        treatment["unit_price"] = price
        total_cost += price
    
    # Create in Odoo
    plan_id = await clinical_service.create_treatment_plan(
        patient_id=patient_id,
        treatments=treatments,
        notes=notes,
        estimated_cost=total_cost,
        priority=priority
    )
    
    # Log activity
    await log_agent_activity(
        agent="sarah",
        action="create_treatment_plan",
        patient_id=patient_id,
        plan_id=plan_id
    )
    
    return {
        "plan_id": plan_id,
        "estimated_cost": total_cost,
        "status": "draft",
        "message": f"Treatment plan created successfully. Estimated cost: ₪{total_cost}"
    }

@tool
async def suggest_treatment_alternatives_tool(
    treatment_id: int,
    patient_id: int,
    reason: str = None
) -> List[Dict]:
    """
    Suggest alternative treatments based on patient's condition and budget.
    
    Args:
        treatment_id: The original treatment ID
        patient_id: The Odoo patient ID
        reason: Why alternatives are needed (e.g., "budget", "medical")
    
    Returns:
        List of alternative treatments with pros/cons
    """
    clinical_service = get_clinical_service()
    
    # Get original treatment details
    original = await clinical_service.get_treatment(treatment_id)
    
    # Get patient's medical history and budget
    history = await get_patient_medical_history_tool(patient_id)
    budget = await get_patient_budget_preference(patient_id)
    
    # Find alternatives
    alternatives = await clinical_service.find_alternative_treatments(
        treatment_id=treatment_id,
        patient_medical_history=history,
        budget_constraint=budget,
        reason=reason
    )
    
    return alternatives

@tool
async def get_patient_risk_factors_tool(patient_id: int) -> Dict:
    """
    Analyze patient's risk factors for complications.
    
    Args:
        patient_id: The Odoo patient ID
    
    Returns:
        Dict with risk assessment and recommendations
    """
    clinical_service = get_clinical_service()
    
    # Get medical history
    history = await clinical_service.get_medical_history(patient_id)
    allergies = await clinical_service.get_allergies(patient_id)
    medications = await clinical_service.get_medications(patient_id)
    
    # Calculate risk factors
    risk_factors = {
        "bleeding_risk": calculate_bleeding_risk(medications),
        "infection_risk": calculate_infection_risk(history),
        "anesthesia_risk": calculate_anesthesia_risk(history, allergies),
        "healing_risk": calculate_healing_risk(history, medications),
        "overall_risk": "low"  # Will be calculated
    }
    
    # Determine overall risk
    if any(r == "high" for r in risk_factors.values()):
        risk_factors["overall_risk"] = "high"
    elif any(r == "medium" for r in risk_factors.values()):
        risk_factors["overall_risk"] = "medium"
    
    # Add recommendations
    risk_factors["recommendations"] = generate_risk_recommendations(risk_factors)
    
    return risk_factors

# ... 6 more tools (10 total)
```

#### Task 1.7: LangGraph Integration
**References:**
- `backend/app/agents/agent_graph_v3.py` - Current graph
- `backend/app/agents/graph_state.py` - State management

**What to Update:**
```python
# backend/app/agents/agent_graph_v3.py
from .sarah import create_sarah_agent, sarah_system_prompt, sarah_rbac

# Add Sarah to the graph
def create_agent_graph_v4():
    """Create agent graph with Sarah (Clinical Director)"""
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
    
    # Create agents
    alex_agent = create_alex_agent(llm)
    marcus_agent = create_marcus_agent(llm)
    sophia_agent = create_sophia_agent(llm)
    sarah_agent = create_sarah_agent(llm)  # NEW!
    
    # Create supervisor
    supervisor = create_supervisor(llm, agents=[
        {"name": "alex", "description": "Receptionist - appointments, patients"},
        {"name": "marcus", "description": "CFO - finance, analytics"},
        {"name": "sophia", "description": "Admin - staff, settings"},
        {"name": "sarah", "description": "Clinical Director - treatments, medical"}  # NEW!
    ])
    
    # Create state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("alex", alex_node)
    workflow.add_node("marcus", marcus_node)
    workflow.add_node("sophia", sophia_node)
    workflow.add_node("sarah", sarah_node)  # NEW!
    
    # Add edges (routing)
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "alex": "alex",
            "marcus": "marcus",
            "sophia": "sophia",
            "sarah": "sarah",  # NEW!
            "FINISH": END
        }
    )
    
    # Add back edges (return to supervisor)
    for agent in ["alex", "marcus", "sophia", "sarah"]:
        workflow.add_edge(agent, "supervisor")
    
    return workflow.compile()

# Update RBAC check
def check_agent_access(agent_name: str, user: User, org: Organization) -> bool:
    """Check if user can access this agent"""
    rbac_rules = {
        "alex": alex_rbac,
        "marcus": marcus_rbac,
        "sophia": sophia_rbac,
        "sarah": sarah_rbac  # NEW!
    }
    
    agent_rbac = rbac_rules.get(agent_name)
    if not agent_rbac:
        return False
    
    # Check required roles
    user_roles = get_user_roles(user, org)
    required_roles = agent_rbac["required_roles"]
    
    return any(role in user_roles for role in required_roles)
```

#### Task 1.8: Frontend Integration
**References:**
- `frontend/src/components/chat/AIChat.jsx` - Chat interface
- `frontend/src/components/transparency/AgentActivityPanel.jsx`

**What to Update:**
```jsx
// frontend/src/components/chat/AIChat.jsx
const AGENTS = [
  {
    id: 'alex',
    name: 'Alex',
    role: 'Receptionist',
    avatar: '/avatars/alex.png',
    color: 'blue'
  },
  {
    id: 'marcus',
    name: 'Marcus',
    role: 'CFO',
    avatar: '/avatars/marcus.png',
    color: 'green'
  },
  {
    id: 'sophia',
    name: 'Sophia',
    role: 'Admin',
    avatar: '/avatars/sophia.png',
    color: 'purple'
  },
  {
    id: 'sarah',  // NEW!
    name: 'Dr. Sarah',
    role: 'Clinical Director',
    avatar: '/avatars/sarah.png',
    color: 'red'
  }
];

export function AIChat() {
  const [currentAgent, setCurrentAgent] = useState(null);
  
  // Detect agent from message
  useEffect(() => {
    if (lastMessage?.agent) {
      setCurrentAgent(lastMessage.agent);
    }
  }, [lastMessage]);
  
  return (
    <div className="ai-chat">
      <AgentIndicator agent={currentAgent} />
      <MessageList messages={messages} />
      <ChatInput onSend={sendMessage} />
    </div>
  );
}
```

**Success Criteria:**
- [ ] Sarah agent responds correctly
- [ ] 10+ clinical tools working
- [ ] LangGraph routing includes Sarah
- [ ] RBAC enforced (clinical staff only)
- [ ] Frontend shows Sarah in agent list
- [ ] Transparency panel shows Sarah's actions
- [ ] Tests passing (unit + integration)

---

## Phase 2: Payments & Billing 💰
**Duration:** 2-3 weeks  
**Priority:** 🔴 Critical (Revenue generation)

### Context
Billing & Payments הוא 40% מוכן. יש מודלים ו-CFO analytics, אבל חסר האינטגרציה האמיתית עם Tranzila ו-Green Invoice. זה קריטי להשקה בישראל.

### Week 1: Tranzila Integration

#### Task 2.1: Tranzila Client Implementation
**References:**
- `backend/app/integrations/odoo_client_v2.py` - Similar structure
- Tranzila API docs: https://www.tranzila.com/docs/

**What to Build:**
```python
# backend/app/integrations/tranzila_client.py
import httpx
from typing import Dict, Optional
import hashlib

class TranzilaClient:
    """Client for Tranzila payment gateway (Israel)"""
    
    def __init__(
        self,
        terminal_name: str,
        api_key: str,
        test_mode: bool = False
    ):
        self.terminal_name = terminal_name
        self.api_key = api_key
        self.test_mode = test_mode
        self.base_url = "https://direct.tranzila.com/api"
        if test_mode:
            self.base_url = "https://sandbox.tranzila.com/api"
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC signature for request"""
        # Tranzila signature algorithm
        sorted_params = sorted(params.items())
        data = "&".join(f"{k}={v}" for k, v in sorted_params)
        signature = hashlib.sha256(
            f"{data}{self.api_key}".encode()
        ).hexdigest()
        return signature
    
    async def create_payment(
        self,
        amount: float,
        currency: str = "ILS",
        customer_email: str = None,
        customer_name: str = None,
        order_id: str = None,
        description: str = None,
        success_url: str = None,
        cancel_url: str = None
    ) -> Dict:
        """
        Create a payment transaction.
        
        Returns:
            Dict with transaction_id and payment_url (hosted page)
        """
        params = {
            "terminal_name": self.terminal_name,
            "amount": int(amount * 100),  # Convert to agorot
            "currency": currency,
            "email": customer_email,
            "contact": customer_name,
            "order_id": order_id,
            "description": description,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "lang": "he"  # Hebrew
        }
        
        # Add signature
        params["signature"] = self._generate_signature(params)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/create-payment",
                data=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_payment_status(self, transaction_id: str) -> Dict:
        """Get payment transaction status"""
        params = {
            "terminal_name": self.terminal_name,
            "transaction_id": transaction_id
        }
        params["signature"] = self._generate_signature(params)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/get-payment",
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[float] = None,
        reason: str = None
    ) -> Dict:
        """Refund a payment (full or partial)"""
        params = {
            "terminal_name": self.terminal_name,
            "transaction_id": transaction_id,
            "reason": reason
        }
        
        if amount:
            params["amount"] = int(amount * 100)
        
        params["signature"] = self._generate_signature(params)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/refund",
                data=params
            )
            response.raise_for_status()
            return response.json()
    
    async def handle_webhook(self, payload: Dict) -> Dict:
        """Handle webhook notification from Tranzila"""
        # Verify signature
        signature = payload.pop("signature")
        expected_signature = self._generate_signature(payload)
        
        if signature != expected_signature:
            raise ValueError("Invalid webhook signature")
        
        # Parse webhook data
        return {
            "transaction_id": payload["transaction_id"],
            "status": payload["status"],
            "amount": float(payload["amount"]) / 100,
            "currency": payload["currency"],
            "order_id": payload.get("order_id"),
            "timestamp": payload["timestamp"]
        }
```

**Configuration:**
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ... existing settings
    
    # Tranzila
    TRANZILA_TERMINAL_NAME: str = Field(..., env="TRANZILA_TERMINAL_NAME")
    TRANZILA_API_KEY: str = Field(..., env="TRANZILA_API_KEY")
    TRANZILA_TEST_MODE: bool = Field(True, env="TRANZILA_TEST_MODE")
    TRANZILA_SUCCESS_URL: str = Field(..., env="TRANZILA_SUCCESS_URL")
    TRANZILA_CANCEL_URL: str = Field(..., env="TRANZILA_CANCEL_URL")
    TRANZILA_WEBHOOK_URL: str = Field(..., env="TRANZILA_WEBHOOK_URL")
```

**Success Criteria:**
- [ ] TranzilaClient implemented
- [ ] Payment creation working
- [ ] Status checking working
- [ ] Refunds working
- [ ] Webhook handling secure
- [ ] Error handling comprehensive
- [ ] PCI DSS compliant (hosted page)
- [ ] Tests passing

---

#### Task 2.2: Payment Flow Implementation
**References:**
- `backend/app/models/treatment_price.py` - Pricing
- `backend/app/api/v1/endpoints/patient_portal_odoo.py` - API structure

**What to Build:**
```python
# backend/app/services/payment_service.py
from .tranzila_client import TranzilaClient
from .odoo_cache import OdooCache

class PaymentService:
    def __init__(
        self,
        tranzila: TranzilaClient,
        odoo: OdooClientV2,
        cache: OdooCache
    ):
        self.tranzila = tranzila
        self.odoo = odoo
        self.cache = cache
    
    async def create_payment_for_invoice(
        self,
        invoice_id: int,
        patient_id: int,
        user_email: str,
        user_name: str
    ) -> Dict:
        """Create payment for an Odoo invoice"""
        # Get invoice details from Odoo
        invoice = await self.odoo.read("account.move", invoice_id)
        
        if invoice["state"] != "posted":
            raise ValueError("Invoice must be posted before payment")
        
        if invoice["payment_state"] == "paid":
            raise ValueError("Invoice already paid")
        
        amount = invoice["amount_residual"]  # Remaining amount
        
        # Create payment in Tranzila
        payment = await self.tranzila.create_payment(
            amount=amount,
            currency="ILS",
            customer_email=user_email,
            customer_name=user_name,
            order_id=f"INV-{invoice_id}",
            description=f"Invoice #{invoice['name']}",
            success_url=f"{settings.FRONTEND_URL}/payments/success",
            cancel_url=f"{settings.FRONTEND_URL}/payments/cancel"
        )
        
        # Store payment record in PostgreSQL
        payment_record = await self.create_payment_record(
            invoice_id=invoice_id,
            patient_id=patient_id,
            transaction_id=payment["transaction_id"],
            amount=amount,
            status="pending"
        )
        
        return {
            "payment_id": payment_record.id,
            "transaction_id": payment["transaction_id"],
            "payment_url": payment["payment_url"],
            "amount": amount,
            "currency": "ILS"
        }
    
    async def handle_payment_webhook(self, webhook_data: Dict):
        """Handle payment webhook from Tranzila"""
        # Verify and parse webhook
        payment_data = await self.tranzila.handle_webhook(webhook_data)
        
        transaction_id = payment_data["transaction_id"]
        status = payment_data["status"]
        
        # Update payment record
        payment_record = await self.get_payment_by_transaction_id(transaction_id)
        payment_record.status = status
        payment_record.completed_at = datetime.utcnow()
        
        # If successful, register payment in Odoo
        if status == "success":
            await self.register_payment_in_odoo(
                invoice_id=payment_record.invoice_id,
                amount=payment_data["amount"],
                payment_date=payment_data["timestamp"],
                payment_method="credit_card",
                transaction_id=transaction_id
            )
            
            # Invalidate cache
            await self.cache.invalidate(f"invoice:{payment_record.invoice_id}")
        
        return payment_record
    
    async def register_payment_in_odoo(
        self,
        invoice_id: int,
        amount: float,
        payment_date: str,
        payment_method: str,
        transaction_id: str
    ):
        """Register payment in Odoo accounting"""
        # Create account.payment record
        payment_id = await self.odoo.create("account.payment", {
            "payment_type": "inbound",
            "partner_type": "customer",
            "amount": amount,
            "date": payment_date,
            "journal_id": 1,  # Bank journal
            "payment_method_id": 1,  # Credit card
            "ref": f"Tranzila: {transaction_id}"
        })
        
        # Link payment to invoice
        await self.odoo.execute(
            "account.payment",
            "action_post",
            [payment_id]
        )
        
        # Reconcile with invoice
        invoice = await self.odoo.read("account.move", invoice_id)
        payment = await self.odoo.read("account.payment", payment_id)
        
        # ... reconciliation logic
        
        return payment_id
```

**API Endpoints:**
```python
# backend/app/api/v1/endpoints/payments.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/create")
async def create_payment(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create payment for an invoice"""
    # Check if user can pay this invoice
    invoice = await payment_service.odoo.read("account.move", invoice_id)
    
    # RBAC: User must be patient or staff of the organization
    if not can_access_invoice(current_user, invoice):
        raise HTTPException(403, "Access denied")
    
    # Create payment
    payment = await payment_service.create_payment_for_invoice(
        invoice_id=invoice_id,
        patient_id=invoice["partner_id"][0],
        user_email=current_user.email,
        user_name=current_user.full_name
    )
    
    return payment

@router.post("/webhook")
async def payment_webhook(
    payload: Dict,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Handle Tranzila webhook"""
    try:
        payment = await payment_service.handle_payment_webhook(payload)
        return {"status": "success", "payment_id": str(payment.id)}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(500, "Webhook processing failed")

@router.get("/{payment_id}/status")
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get payment status"""
    payment = await payment_service.get_payment_by_id(payment_id)
    
    # RBAC check
    if not can_access_payment(current_user, payment):
        raise HTTPException(403, "Access denied")
    
    return {
        "payment_id": str(payment.id),
        "status": payment.status,
        "amount": payment.amount,
        "transaction_id": payment.transaction_id,
        "created_at": payment.created_at,
        "completed_at": payment.completed_at
    }
```

**Success Criteria:**
- [ ] Payment creation flow working
- [ ] Webhook handling secure and reliable
- [ ] Odoo payment registration working
- [ ] Invoice reconciliation working
- [ ] Error handling comprehensive
- [ ] Tests passing (unit + integration)

---

### Week 2: Green Invoice Update

#### Task 2.3: Complete Green Invoice Integration
**References:**
- `backend/app/integrations/green_invoice.py` - Existing partial implementation
- Green Invoice API docs: https://www.greeninvoice.co.il/api/

**What to Update:**
```python
# backend/app/integrations/green_invoice.py
# (Update existing file)

class GreenInvoiceClient:
    # ... existing code
    
    async def create_invoice(
        self,
        customer: Dict,
        items: List[Dict],
        invoice_type: str = "320",  # Tax invoice
        payment_method: str = "1",  # Credit card
        remarks: str = None
    ) -> Dict:
        """
        Create a real invoice in Green Invoice.
        
        Args:
            customer: Dict with name, email, phone, address
            items: List of items with description, quantity, price, vat
            invoice_type: "320" (tax invoice) or "400" (receipt)
            payment_method: "1" (credit), "2" (cash), etc.
        
        Returns:
            Dict with invoice_id, pdf_url, and invoice_number
        """
        payload = {
            "type": invoice_type,
            "client": {
                "name": customer["name"],
                "emails": [customer["email"]],
                "phone": customer.get("phone"),
                "address": customer.get("address"),
                "city": customer.get("city"),
                "zip": customer.get("zip")
            },
            "income": items,
            "payment": {
                "type": payment_method,
                "date": datetime.now().isoformat()
            },
            "remarks": remarks,
            "currency": "ILS",
            "lang": "he"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/documents",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            data = response.json()
        
        return {
            "invoice_id": data["id"],
            "invoice_number": data["documentNumber"],
            "pdf_url": data["url"]["origin"],
            "amount": data["amount"],
            "status": data["status"]
        }
    
    async def download_pdf(self, invoice_id: str) -> bytes:
        """Download invoice PDF"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/documents/{invoice_id}/pdf",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.content
    
    async def send_invoice_email(
        self,
        invoice_id: str,
        recipient_email: str,
        subject: str = None,
        message: str = None
    ) -> bool:
        """Send invoice via email"""
        payload = {
            "email": recipient_email,
            "subject": subject or "חשבונית מס",
            "message": message or "מצורפת חשבונית מס"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/documents/{invoice_id}/send",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return True
    
    async def get_ita_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Get ITA (Israel Tax Authority) report.
        
        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
        
        Returns:
            Dict with report data for tax filing
        """
        params = {
            "from": start_date,
            "to": end_date,
            "type": "ita"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/reports/ita",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
```

**Service Layer:**
```python
# backend/app/services/invoice_service.py
class InvoiceService:
    def __init__(
        self,
        green_invoice: GreenInvoiceClient,
        odoo: OdooClientV2
    ):
        self.green_invoice = green_invoice
        self.odoo = odoo
    
    async def create_invoice_from_odoo(
        self,
        odoo_invoice_id: int,
        send_email: bool = True
    ) -> Dict:
        """
        Create Green Invoice from Odoo invoice.
        
        This syncs the invoice to Green Invoice for Israeli tax compliance.
        """
        # Get invoice from Odoo
        invoice = await self.odoo.read("account.move", odoo_invoice_id)
        partner = await self.odoo.read("res.partner", invoice["partner_id"][0])
        lines = await self.odoo.search_read(
            "account.move.line",
            domain=[("move_id", "=", odoo_invoice_id)],
            fields=["product_id", "name", "quantity", "price_unit", "tax_ids"]
        )
        
        # Map to Green Invoice format
        customer = {
            "name": partner["name"],
            "email": partner["email"],
            "phone": partner.get("phone"),
            "address": partner.get("street"),
            "city": partner.get("city"),
            "zip": partner.get("zip")
        }
        
        items = []
        for line in lines:
            if line["product_id"]:  # Skip non-product lines
                items.append({
                    "description": line["name"],
                    "quantity": line["quantity"],
                    "price": line["price_unit"],
                    "currency": "ILS",
                    "vatType": 1  # Standard VAT (17%)
                })
        
        # Create in Green Invoice
        gi_invoice = await self.green_invoice.create_invoice(
            customer=customer,
            items=items,
            remarks=f"Odoo Invoice: {invoice['name']}"
        )
        
        # Update Odoo with Green Invoice reference
        await self.odoo.write("account.move", odoo_invoice_id, {
            "x_green_invoice_id": gi_invoice["invoice_id"],
            "x_green_invoice_number": gi_invoice["invoice_number"],
            "x_green_invoice_pdf_url": gi_invoice["pdf_url"]
        })
        
        # Send email if requested
        if send_email and partner["email"]:
            await self.green_invoice.send_invoice_email(
                invoice_id=gi_invoice["invoice_id"],
                recipient_email=partner["email"]
            )
        
        return gi_invoice
```

**API Endpoints:**
```python
# backend/app/api/v1/endpoints/invoices.py
@router.post("/{invoice_id}/create-green-invoice")
@require_role("owner", "manager")
async def create_green_invoice(
    invoice_id: int,
    send_email: bool = True,
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    """Create Green Invoice from Odoo invoice"""
    gi_invoice = await invoice_service.create_invoice_from_odoo(
        odoo_invoice_id=invoice_id,
        send_email=send_email
    )
    return gi_invoice

@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    """Download invoice PDF"""
    # Get invoice
    invoice = await invoice_service.odoo.read("account.move", invoice_id)
    
    # RBAC check
    if not can_access_invoice(current_user, invoice):
        raise HTTPException(403, "Access denied")
    
    # Get Green Invoice ID
    gi_id = invoice.get("x_green_invoice_id")
    if not gi_id:
        raise HTTPException(404, "Green Invoice not created yet")
    
    # Download PDF
    pdf_bytes = await invoice_service.green_invoice.download_pdf(gi_id)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"
        }
    )

@router.get("/reports/ita")
@require_role("owner", "manager")
async def get_ita_report(
    start_date: str,
    end_date: str,
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    """Get ITA report for tax filing"""
    report = await invoice_service.green_invoice.get_ita_report(
        start_date=start_date,
        end_date=end_date
    )
    return report
```

**Success Criteria:**
- [ ] Real invoice creation working
- [ ] PDF download working
- [ ] Email sending working
- [ ] ITA reporting working
- [ ] Odoo sync working
- [ ] Tests passing

---

### Week 3: Payment UI & Flows

#### Task 2.4: Patient Portal - Payment Page
**References:**
- `patient-portal/src/pages/` - Existing pages
- `patient-portal/src/services/odooService.js` - API client

**What to Build:**
```jsx
// patient-portal/src/pages/PaymentsPage.jsx
import { useQuery, useMutation } from '@tanstack/react-query';
import { paymentService } from '../services/paymentService';

export function PaymentsPage() {
  const { data: invoices, isLoading } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => paymentService.getInvoices()
  });
  
  const unpaidInvoices = invoices?.filter(inv => inv.payment_state !== 'paid');
  const paidInvoices = invoices?.filter(inv => inv.payment_state === 'paid');
  
  return (
    <div className="payments-page">
      <h1>Payments & Invoices</h1>
      
      {unpaidInvoices?.length > 0 && (
        <section className="unpaid-section">
          <h2>Unpaid Invoices</h2>
          <div className="invoice-list">
            {unpaidInvoices.map(invoice => (
              <UnpaidInvoiceCard 
                key={invoice.id} 
                invoice={invoice}
              />
            ))}
          </div>
        </section>
      )}
      
      <section className="paid-section">
        <h2>Payment History</h2>
        <div className="invoice-list">
          {paidInvoices?.map(invoice => (
            <PaidInvoiceCard 
              key={invoice.id} 
              invoice={invoice}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

function UnpaidInvoiceCard({ invoice }) {
  const payMutation = useMutation({
    mutationFn: () => paymentService.createPayment(invoice.id),
    onSuccess: (data) => {
      // Redirect to Tranzila hosted page
      window.location.href = data.payment_url;
    }
  });
  
  return (
    <Card className="unpaid-invoice">
      <CardHeader>
        <CardTitle>Invoice #{invoice.name}</CardTitle>
        <Badge variant="warning">Unpaid</Badge>
      </CardHeader>
      <CardContent>
        <div className="invoice-details">
          <div>
            <strong>Date:</strong> {formatDate(invoice.invoice_date)}
          </div>
          <div>
            <strong>Amount:</strong> ₪{invoice.amount_total}
          </div>
          <div>
            <strong>Due Date:</strong> {formatDate(invoice.invoice_date_due)}
          </div>
        </div>
        
        <div className="invoice-lines">
          {invoice.invoice_line_ids.map(line => (
            <div key={line.id} className="line-item">
              <span>{line.name}</span>
              <span>₪{line.price_subtotal}</span>
            </div>
          ))}
        </div>
      </CardContent>
      <CardFooter>
        <Button 
          onClick={() => payMutation.mutate()}
          disabled={payMutation.isPending}
          className="pay-button"
        >
          {payMutation.isPending ? 'Processing...' : 'Pay Now'}
        </Button>
      </CardFooter>
    </Card>
  );
}

function PaidInvoiceCard({ invoice }) {
  const downloadMutation = useMutation({
    mutationFn: () => paymentService.downloadPDF(invoice.id),
    onSuccess: (blob) => {
      // Download PDF
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice_${invoice.id}.pdf`;
      a.click();
    }
  });
  
  return (
    <Card className="paid-invoice">
      <CardHeader>
        <CardTitle>Invoice #{invoice.name}</CardTitle>
        <Badge variant="success">Paid</Badge>
      </CardHeader>
      <CardContent>
        <div className="invoice-details">
          <div>
            <strong>Date:</strong> {formatDate(invoice.invoice_date)}
          </div>
          <div>
            <strong>Amount:</strong> ₪{invoice.amount_total}</div>
          <div>
            <strong>Paid:</strong> {formatDate(invoice.payment_date)}
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button 
          variant="outline"
          onClick={() => downloadMutation.mutate()}
          disabled={downloadMutation.isPending}
        >
          Download PDF
        </Button>
      </CardFooter>
    </Card>
  );
}
```

**Payment Service:**
```javascript
// patient-portal/src/services/paymentService.js
import api from '../config/api';

export const paymentService = {
  async getInvoices() {
    const response = await api.get('/api/v1/invoices');
    return response.data;
  },
  
  async createPayment(invoiceId) {
    const response = await api.post('/api/v1/payments/create', {
      invoice_id: invoiceId
    });
    return response.data;
  },
  
  async getPaymentStatus(paymentId) {
    const response = await api.get(`/api/v1/payments/${paymentId}/status`);
    return response.data;
  },
  
  async downloadPDF(invoiceId) {
    const response = await api.get(`/api/v1/invoices/${invoiceId}/pdf`, {
      responseType: 'blob'
    });
    return response.data;
  }
};
```

**Success Criteria:**
- [ ] Payment page responsive
- [ ] Unpaid invoices highlighted
- [ ] Pay button redirects to Tranzila
- [ ] Payment history visible
- [ ] PDF download working
- [ ] Mobile-friendly
- [ ] Accessibility (WCAG 2.1 AA)

---

#### Task 2.5: Clinic Portal - Payment Management
**References:**
- `frontend/src/components/widgets/` - Existing widgets
- `frontend/src/services/dataService.js` - API client

**What to Build:**
```jsx
// frontend/src/components/widgets/PaymentManagementWidget.jsx
export function PaymentManagementWidget() {
  const { data: payments } = useQuery({
    queryKey: ['recent-payments'],
    queryFn: () => dataService.getRecentPayments(),
    refetchInterval: 30000  // Refresh every 30s
  });
  
  const pendingPayments = payments?.filter(p => p.status === 'pending');
  const completedToday = payments?.filter(p => 
    p.status === 'success' && isToday(p.completed_at)
  );
  
  return (
    <Card className="payment-management-widget">
      <CardHeader>
        <CardTitle>Payment Management</CardTitle>
        <RefreshButton />
      </CardHeader>
      <CardContent>
        <div className="payment-stats">
          <StatCard
            label="Pending"
            value={pendingPayments?.length || 0}
            color="yellow"
          />
          <StatCard
            label="Completed Today"
            value={completedToday?.length || 0}
            color="green"
          />
          <StatCard
            label="Total Today"
            value={`₪${calculateTotal(completedToday)}`}
            color="blue"
          />
        </div>
        
        <div className="recent-payments">
          <h3>Recent Payments</h3>
          <PaymentList payments={payments?.slice(0, 5)} />
        </div>
      </CardContent>
      <CardFooter>
        <Button variant="link" onClick={() => navigate('/payments')}>
          View All Payments
        </Button>
      </CardFooter>
    </Card>
  );
}

// frontend/src/pages/PaymentManagementPage.jsx
export function PaymentManagementPage() {
  const [dateRange, setDateRange] = useState({
    start: startOfMonth(new Date()),
    end: endOfMonth(new Date())
  });
  
  const { data: payments } = useQuery({
    queryKey: ['payments', dateRange],
    queryFn: () => dataService.getPayments(dateRange)
  });
  
  const refundMutation = useMutation({
    mutationFn: ({ paymentId, amount, reason }) => 
      dataService.refundPayment(paymentId, amount, reason),
    onSuccess: () => {
      toast.success('Refund processed successfully');
      queryClient.invalidateQueries(['payments']);
    }
  });
  
  return (
    <div className="payment-management-page">
      <PageHeader>
        <h1>Payment Management</h1>
        <DateRangePicker 
          value={dateRange}
          onChange={setDateRange}
        />
      </PageHeader>
      
      <PaymentStats payments={payments} />
      
      <PaymentTable 
        payments={payments}
        onRefund={(payment) => setRefundDialog(payment)}
      />
      
      <RefundDialog
        payment={refundDialog}
        onConfirm={(amount, reason) => {
          refundMutation.mutate({
            paymentId: refundDialog.id,
            amount,
            reason
          });
          setRefundDialog(null);
        }}
        onCancel={() => setRefundDialog(null)}
      />
    </div>
  );
}
```

**Success Criteria:**
- [ ] Payment widget in dashboard
- [ ] Full payment management page
- [ ] Refund functionality
- [ ] Date range filtering
- [ ] Export to Excel
- [ ] Real-time updates
- [ ] RBAC enforced (owner/manager only)

---

## Phase 3: Completion & Polish 🎨
**Duration:** 2-3 weeks  
**Priority:** 🟡 Important (Quality & Features)

### Week 1: Bug Fixes & Missing Features

#### Task 3.1: Fix Create Appointment Bug
**References:**
- `PARTIAL_MODULES_DETAILED_ANALYSIS.md` - Bug description
- `backend/app/agents/tools/alex_odoo_tools.py` - Current implementation

**Problem:**
```
Error: Odoo constraint violation when creating appointments
- Constraint: appointment_time_unique
- Cause: Overlapping time slots or duplicate bookings
```

**What to Fix:**
```python
# backend/app/agents/tools/alex_odoo_tools.py
@tool
async def create_appointment_tool(
    patient_id: int,
    doctor_id: int,
    appointment_date: str,
    appointment_time: str,
    duration: int = 30,
    reason: str = None
) -> Dict:
    """
    Create a new appointment (FIXED).
    
    Args:
        patient_id: Odoo patient ID
        doctor_id: Odoo doctor ID (res.users)
        appointment_date: YYYY-MM-DD
        appointment_time: HH:MM (24-hour format)
        duration: Duration in minutes (default: 30)
        reason: Reason for visit
    
    Returns:
        Dict with appointment_id and confirmation
    """
    odoo = get_odoo_client()
    
    # Parse datetime
    dt_str = f"{appointment_date} {appointment_time}:00"
    start_datetime = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    end_datetime = start_datetime + timedelta(minutes=duration)
    
    # FIX 1: Check for overlapping appointments
    existing = await odoo.search_read(
        "medical.appointment",
        domain=[
            ("doctor_id", "=", doctor_id),
            ("state", "!=", "cancelled"),
            "|",
            "&",
            ("appointment_date", "<=", start_datetime.isoformat()),
            ("appointment_end", ">", start_datetime.isoformat()),
            "&",
            ("appointment_date", "<", end_datetime.isoformat()),
            ("appointment_end", ">=", end_datetime.isoformat())
        ],
        fields=["id", "appointment_date", "appointment_end"]
    )
    
    if existing:
        raise ValueError(
            f"Time slot unavailable. Conflicting appointment: {existing[0]['id']}"
        )
    
    # FIX 2: Validate doctor availability
    # Check doctor's working hours
    doctor = await odoo.read("res.users", doctor_id, ["resource_calendar_id"])
    if doctor.get("resource_calendar_id"):
        calendar_id = doctor["resource_calendar_id"][0]
        is_available = await check_doctor_availability(
            odoo, calendar_id, start_datetime
        )
        if not is_available:
            raise ValueError(
                f"Doctor not available at {appointment_time}. "
                f"Please check working hours."
            )
    
    # FIX 3: Use unique reference to avoid duplicates
    unique_ref = f"APT-{patient_id}-{doctor_id}-{int(start_datetime.timestamp())}"
    
    # Create appointment
    try:
        appointment_id = await odoo.create("medical.appointment", {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_date": start_datetime.isoformat(),
            "appointment_end": end_datetime.isoformat(),
            "duration": duration,
            "reason": reason or "General checkup",
            "state": "draft",
            "x_unique_ref": unique_ref  # Custom field for uniqueness
        })
    except Exception as e:
        if "unique constraint" in str(e).lower():
            # Duplicate detected, return existing
            existing_id = await odoo.search(
                "medical.appointment",
                domain=[("x_unique_ref", "=", unique_ref)],
                limit=1
            )
            if existing_id:
                return {
                    "appointment_id": existing_id[0],
                    "status": "existing",
                    "message": "Appointment already exists"
                }
        raise
    
    # Confirm appointment
    await odoo.execute("medical.appointment", "action_confirm", [appointment_id])
    
    # Log activity
    await log_agent_activity(
        agent="alex",
        action="create_appointment",
        patient_id=patient_id,
        appointment_id=appointment_id
    )
    
    return {
        "appointment_id": appointment_id,
        "status": "confirmed",
        "start_time": start_datetime.isoformat(),
        "end_time": end_datetime.isoformat(),
        "message": f"Appointment created successfully for {appointment_date} at {appointment_time}"
    }

async def check_doctor_availability(
    odoo: OdooClientV2,
    calendar_id: int,
    datetime_to_check: datetime
) -> bool:
    """Check if doctor is available at given time"""
    # Get calendar attendances (working hours)
    attendances = await odoo.search_read(
        "resource.calendar.attendance",
        domain=[("calendar_id", "=", calendar_id)],
        fields=["dayofweek", "hour_from", "hour_to"]
    )
    
    # Check if datetime falls within working hours
    day_of_week = str(datetime_to_check.weekday())  # 0=Monday
    time_of_day = datetime_to_check.hour + datetime_to_check.minute / 60.0
    
    for attendance in attendances:
        if (attendance["dayofweek"] == day_of_week and
            attendance["hour_from"] <= time_of_day <= attendance["hour_to"]):
            return True
    
    return False
```

**Testing:**
```python
# backend/tests/test_create_appointment_fix.py
async def test_create_appointment_no_overlap():
    """Test that overlapping appointments are prevented"""
    # Create first appointment
    apt1 = await create_appointment_tool(
        patient_id=67,
        doctor_id=2,
        appointment_date="2025-10-15",
        appointment_time="10:00",
        duration=30
    )
    assert apt1["status"] == "confirmed"
    
    # Try to create overlapping appointment
    with pytest.raises(ValueError, match="Time slot unavailable"):
        await create_appointment_tool(
            patient_id=68,
            doctor_id=2,
            appointment_date="2025-10-15",
            appointment_time="10:15",  # Overlaps!
            duration=30
        )

async def test_create_appointment_outside_working_hours():
    """Test that appointments outside working hours are rejected"""
    with pytest.raises(ValueError, match="Doctor not available"):
        await create_appointment_tool(
            patient_id=67,
            doctor_id=2,
            appointment_date="2025-10-15",
            appointment_time="22:00",  # After hours
            duration=30
        )
```

**Success Criteria:**
- [ ] No more constraint violations
- [ ] Overlap detection working
- [ ] Doctor availability check working
- [ ] Duplicate prevention working
- [ ] Tests passing (100%)
- [ ] Error messages clear

---

#### Task 3.2: Portal Separation (Patient vs Clinic)
**References:**
- `CLINIC_PORTAL_TECHNICAL_DEEP_DIVE.md` - Architecture
- Current setup: Both portals in same codebase

**What to Build:**
```
# New directory structure
dental-clinic-ai/
├── backend/          # Shared backend
├── patient-portal/   # Patient Portal (existing)
├── clinic-portal/    # Clinic Portal (NEW - move from frontend/)
└── shared/           # Shared components (NEW)
```

**Step 1: Move Clinic Portal**
```bash
# Move frontend/ to clinic-portal/
mv frontend/ clinic-portal/

# Update package.json
cd clinic-portal/
# Change name to "@dentaflow/clinic-portal"
```

**Step 2: Create Shared Library**
```bash
# Create shared package
mkdir -p shared/src/{components,utils,types}

# shared/package.json
{
  "name": "@dentaflow/shared",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts"
}
```

**Step 3: Update Routing**
```javascript
// backend/app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve patient portal at /patient
app.mount(
    "/patient",
    StaticFiles(directory="../patient-portal/dist", html=True),
    name="patient-portal"
)

# Serve clinic portal at /clinic
app.mount(
    "/clinic",
    StaticFiles(directory="../clinic-portal/dist", html=True),
    name="clinic-portal"
)

# Root redirects based on user role
@app.get("/")
async def root(current_user: User = Depends(get_current_user_optional)):
    if not current_user:
        return RedirectResponse("/patient/login")
    
    # Check user role
    if current_user.role in ["patient"]:
        return RedirectResponse("/patient/dashboard")
    else:
        return RedirectResponse("/clinic/dashboard")
```

**Step 4: Update Authentication**
```python
# backend/app/api/v1/endpoints/auth.py
@router.post("/login")
async def login(credentials: LoginRequest):
    user = await authenticate_user(credentials.email, credentials.password)
    
    # Generate token
    token = create_access_token(user.id)
    
    # Determine redirect URL based on role
    if user.role == "patient":
        redirect_url = "/patient/dashboard"
    else:
        redirect_url = "/clinic/dashboard"
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
        "redirect_url": redirect_url
    }
```

**Success Criteria:**
- [ ] Two separate portals
- [ ] Separate URLs (/patient, /clinic)
- [ ] Shared components library
- [ ] Role-based routing
- [ ] No code duplication
- [ ] Both portals build successfully

---

#### Task 3.3: Widget Permissions (RBAC Enforcement)
**References:**
- `backend/app/core/rbac.py` - RBAC decorator
- `frontend/src/components/widgets/` - Widgets

**What to Build:**
```jsx
// clinic-portal/src/hooks/usePermissions.js
import { useAuth } from './useAuth';

export function usePermissions() {
  const { user } = useAuth();
  
  const hasPermission = (permission) => {
    if (!user) return false;
    
    // Super admin has all permissions
    if (user.role === 'super_admin') return true;
    
    // Check user's permissions
    return user.permissions?.includes(permission);
  };
  
  const hasRole = (role) => {
    if (!user) return false;
    return user.organization_role === role || user.role === role;
  };
  
  const canViewWidget = (widgetId) => {
    const widgetPermissions = {
      'todays-patients': ['view_patients', 'manage_appointments'],
      'revenue': ['view_financials'],
      'decision-queue': ['owner', 'manager'],
      'fine-tuning': ['owner'],
      'staff-schedule': ['manage_staff', 'view_staff'],
      'treatment-plans': ['clinical_staff', 'owner'],
      'payment-management': ['owner', 'manager'],
      'analytics': ['view_analytics']
    };
    
    const required = widgetPermissions[widgetId];
    if (!required) return true;  // No restrictions
    
    // Check if user has any of the required permissions/roles
    return required.some(req => 
      hasPermission(req) || hasRole(req)
    );
  };
  
  return {
    hasPermission,
    hasRole,
    canViewWidget
  };
}

// clinic-portal/src/components/dashboard/DashboardGrid.jsx
import { usePermissions } from '../../hooks/usePermissions';

export function DashboardGrid() {
  const { canViewWidget } = usePermissions();
  
  const allWidgets = [
    { id: 'todays-patients', component: TodaysPatientsWidget },
    { id: 'revenue', component: RevenueWidget },
    { id: 'decision-queue', component: DecisionQueueWidget },
    { id: 'fine-tuning', component: FineTuningWidget },
    { id: 'staff-schedule', component: StaffScheduleWidget },
    { id: 'treatment-plans', component: TreatmentPlansWidget },
    { id: 'payment-management', component: PaymentManagementWidget },
    { id: 'analytics', component: AnalyticsWidget }
  ];
  
  // Filter widgets based on permissions
  const visibleWidgets = allWidgets.filter(w => canViewWidget(w.id));
  
  return (
    <div className="dashboard-grid">
      {visibleWidgets.map(widget => (
        <widget.component key={widget.id} />
      ))}
    </div>
  );
}

// Protect individual widgets
export function RevenueWidget() {
  const { hasPermission } = usePermissions();
  
  if (!hasPermission('view_financials')) {
    return (
      <Card>
        <CardContent>
          <p>You don't have permission to view financial data.</p>
        </CardContent>
      </Card>
    );
  }
  
  // ... widget implementation
}
```

**Backend Enforcement:**
```python
# backend/app/api/v1/endpoints/widgets.py
from app.core.rbac import require_permission

@router.get("/widgets/revenue")
@require_permission("view_financials")
async def get_revenue_data(
    current_user: User = Depends(get_current_user)
):
    """Get revenue data for widget"""
    # ... implementation

@router.get("/widgets/patients")
@require_permission("view_patients")
async def get_patients_data(...):
    """Get patients data for widget"""
    # ... implementation
```

**Success Criteria:**
- [ ] Widget visibility based on permissions
- [ ] Backend endpoints protected
- [ ] Frontend checks permissions
- [ ] Graceful fallback for denied access
- [ ] Tests passing

---

### Week 2: Telegram Integration

#### Task 3.4: Telegram Bot Setup
**References:**
- Telegram Bot API: https://core.telegram.org/bots/api
- python-telegram-bot library

**What to Build:**
```python
# backend/app/integrations/telegram_bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
import asyncio

class DentaFlowTelegramBot:
    """Telegram bot for DentaFlow"""
    
    def __init__(self, token: str, webhook_url: str = None):
        self.token = token
        self.webhook_url = webhook_url
        self.app = Application.builder().token(token).build()
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register command and message handlers"""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("appointments", self.appointments_command))
        self.app.add_handler(CommandHandler("book", self.book_command))
        self.app.add_handler(CommandHandler("cancel", self.cancel_command))
        
        # Callback queries (button clicks)
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Messages
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))
    
    async def start_command(self, update: Update, context):
        """Handle /start command"""
        user = update.effective_user
        
        # Check if user is registered
        db_user = await self.get_user_by_telegram_id(user.id)
        
        if not db_user:
            # New user - send registration link
            keyboard = [[
                InlineKeyboardButton(
                    "Register",
                    url=f"{settings.FRONTEND_URL}/register?telegram_id={user.id}"
                )
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"Welcome to DentaFlow! 🦷\n\n"
                f"Please register to link your account:",
                reply_markup=reply_markup
            )
        else:
            # Existing user - show main menu
            await self.show_main_menu(update, db_user)
    
    async def show_main_menu(self, update: Update, user):
        """Show main menu with options"""
        keyboard = [
            [InlineKeyboardButton("📅 My Appointments", callback_data="appointments")],
            [InlineKeyboardButton("➕ Book Appointment", callback_data="book")],
            [InlineKeyboardButton("💳 Payments", callback_data="payments")],
            [InlineKeyboardButton("👤 Profile", callback_data="profile")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Hello {user.full_name}! 👋\n\n"
            f"What would you like to do?",
            reply_markup=reply_markup
        )
    
    async def appointments_command(self, update: Update, context):
        """Show user's appointments"""
        user = await self.get_user_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("Please register first. Use /start")
            return
        
        # Get appointments from Odoo
        appointments = await self.get_user_appointments(user.id)
        
        if not appointments:
            await update.message.reply_text(
                "You have no upcoming appointments.\n\n"
                "Use /book to schedule one!"
            )
            return
        
        # Format appointments
        message = "📅 Your Upcoming Appointments:\n\n"
        for apt in appointments:
            message += (
                f"• {apt['appointment_date']} at {apt['appointment_time']}\n"
                f"  Doctor: {apt['doctor_name']}\n"
                f"  Reason: {apt['reason']}\n\n"
            )
        
        # Add cancel buttons
        keyboard = []
        for apt in appointments:
            keyboard.append([
                InlineKeyboardButton(
                    f"Cancel {apt['appointment_date']}",
                    callback_data=f"cancel_{apt['id']}"
                )
            ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def book_command(self, update: Update, context):
        """Start booking flow"""
        user = await self.get_user_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("Please register first. Use /start")
            return
        
        # Get available doctors
        doctors = await self.get_available_doctors()
        
        keyboard = []
        for doctor in doctors:
            keyboard.append([
                InlineKeyboardButton(
                    f"Dr. {doctor['name']}",
                    callback_data=f"doctor_{doctor['id']}"
                )
            ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Choose a doctor:",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("doctor_"):
            doctor_id = int(data.split("_")[1])
            await self.show_available_slots(query, doctor_id)
        
        elif data.startswith("slot_"):
            # Parse slot data: slot_doctorid_date_time
            parts = data.split("_")
            doctor_id = int(parts[1])
            date = parts[2]
            time = parts[3]
            await self.confirm_booking(query, doctor_id, date, time)
        
        elif data.startswith("cancel_"):
            appointment_id = int(data.split("_")[1])
            await self.cancel_appointment(query, appointment_id)
        
        elif data == "appointments":
            await self.appointments_command(update, context)
        
        # ... more handlers
    
    async def send_appointment_reminder(
        self,
        telegram_id: int,
        appointment: Dict
    ):
        """Send appointment reminder"""
        message = (
            f"🔔 Reminder: You have an appointment tomorrow!\n\n"
            f"📅 {appointment['appointment_date']}\n"
            f"🕐 {appointment['appointment_time']}\n"
            f"👨‍⚕️ Dr. {appointment['doctor_name']}\n\n"
            f"See you soon! 😊"
        )
        
        await self.app.bot.send_message(
            chat_id=telegram_id,
            text=message
        )
    
    async def send_payment_notification(
        self,
        telegram_id: int,
        invoice: Dict
    ):
        """Send payment notification"""
        keyboard = [[
            InlineKeyboardButton(
                "Pay Now",
                url=f"{settings.FRONTEND_URL}/payments/{invoice['id']}"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"💳 New invoice available\n\n"
            f"Amount: ₪{invoice['amount_total']}\n"
            f"Due: {invoice['invoice_date_due']}\n\n"
            f"Click below to pay:"
        )
        
        await self.app.bot.send_message(
            chat_id=telegram_id,
            text=message,
            reply_markup=reply_markup
        )
    
    async def run_webhook(self):
        """Run bot with webhook"""
        await self.app.initialize()
        await self.app.bot.set_webhook(
            url=self.webhook_url,
            allowed_updates=Update.ALL_TYPES
        )
        await self.app.start()
    
    async def run_polling(self):
        """Run bot with polling (development)"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

# Initialize bot
telegram_bot = DentaFlowTelegramBot(
    token=settings.TELEGRAM_BOT_TOKEN,
    webhook_url=settings.TELEGRAM_WEBHOOK_URL
)
```

**API Endpoints:**
```python
# backend/app/api/v1/endpoints/telegram.py
from app.integrations.telegram_bot import telegram_bot

@router.post("/webhook")
async def telegram_webhook(update: Dict):
    """Handle Telegram webhook"""
    try:
        telegram_update = Update.de_json(update, telegram_bot.app.bot)
        await telegram_bot.app.process_update(telegram_update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        raise HTTPException(500, "Webhook processing failed")

@router.post("/send-reminder")
@require_role("owner", "manager")
async def send_appointment_reminder(
    appointment_id: int,
    telegram_service: TelegramService = Depends(get_telegram_service)
):
    """Send appointment reminder via Telegram"""
    await telegram_service.send_appointment_reminder(appointment_id)
    return {"status": "sent"}
```

**Success Criteria:**
- [ ] Bot responds to commands
- [ ] Booking flow working
- [ ] Reminders sent automatically
- [ ] Payment notifications working
- [ ] Webhook secure
- [ ] Tests passing

---

### Week 3: Additional Features

#### Task 3.5: Communication System (SMS, Email, WhatsApp)
**References:**
- Twilio API (SMS, WhatsApp)
- SendGrid API (Email)

**What to Build:**
```python
# backend/app/services/communication_service.py
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class CommunicationService:
    """Unified communication service"""
    
    def __init__(self):
        self.twilio = TwilioClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.sendgrid = SendGridAPIClient(settings.SENDGRID_API_KEY)
    
    async def send_sms(
        self,
        to_phone: str,
        message: str,
        from_phone: str = None
    ):
        """Send SMS via Twilio"""
        from_phone = from_phone or settings.TWILIO_PHONE_NUMBER
        
        message = self.twilio.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        
        return {
            "message_id": message.sid,
            "status": message.status
        }
    
    async def send_whatsapp(
        self,
        to_phone: str,
        message: str
    ):
        """Send WhatsApp message via Twilio"""
        message = self.twilio.messages.create(
            body=message,
            from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{to_phone}"
        )
        
        return {
            "message_id": message.sid,
            "status": message.status
        }
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = None
    ):
        """Send email via SendGrid"""
        from_email = from_email or settings.FROM_EMAIL
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        response = self.sendgrid.send(message)
        
        return {
            "status_code": response.status_code,
            "message_id": response.headers.get("X-Message-Id")
        }
    
    async def send_appointment_reminder(
        self,
        appointment_id: int,
        channels: List[str] = ["email", "sms"]
    ):
        """Send appointment reminder via multiple channels"""
        # Get appointment and patient
        appointment = await odoo.read("medical.appointment", appointment_id)
        patient = await odoo.read("res.partner", appointment["patient_id"][0])
        
        # Format message
        message = (
            f"Reminder: You have an appointment tomorrow at "
            f"{appointment['appointment_time']} with "
            f"Dr. {appointment['doctor_name']}. "
            f"See you soon!"
        )
        
        results = {}
        
        # Send via requested channels
        if "email" in channels and patient.get("email"):
            results["email"] = await self.send_email(
                to_email=patient["email"],
                subject="Appointment Reminder",
                html_content=f"<p>{message}</p>"
            )
        
        if "sms" in channels and patient.get("mobile"):
            results["sms"] = await self.send_sms(
                to_phone=patient["mobile"],
                message=message
            )
        
        if "whatsapp" in channels and patient.get("mobile"):
            results["whatsapp"] = await self.send_whatsapp(
                to_phone=patient["mobile"],
                message=message
            )
        
        return results
```

**Automated Reminders:**
```python
# backend/app/tasks/reminder_tasks.py
from celery import Celery
from datetime import datetime, timedelta

celery = Celery("dentaflow")

@celery.task
async def send_daily_reminders():
    """Send reminders for tomorrow's appointments"""
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    
    # Get appointments for tomorrow
    appointments = await odoo.search_read(
        "medical.appointment",
        domain=[
            ("appointment_date", ">=", f"{tomorrow} 00:00:00"),
            ("appointment_date", "<", f"{tomorrow} 23:59:59"),
            ("state", "=", "confirmed")
        ]
    )
    
    comm_service = CommunicationService()
    
    for apt in appointments:
        try:
            await comm_service.send_appointment_reminder(
                appointment_id=apt["id"],
                channels=["email", "sms", "telegram"]
            )
        except Exception as e:
            logger.error(f"Failed to send reminder for {apt['id']}: {e}")

# Schedule task (run daily at 18:00)
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'app.tasks.reminder_tasks.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0)
    }
}
```

**Success Criteria:**
- [ ] SMS sending working
- [ ] Email sending working
- [ ] WhatsApp sending working
- [ ] Automated reminders scheduled
- [ ] Multi-channel support
- [ ] Error handling
- [ ] Tests passing

---

## Phase 4: UX/UI Polish (Agentic Vision) 🎨
**Duration:** 1-2 weeks  
**Priority:** 🟡 Important (User Experience)

### Context
מהמסמך "תוכנית אב למשק סוכן אוטונומי", יש 4 עקרונות Agentic UX שצריכים להיות מיושמים בפורטל המרפאה:

1. **Mission Control** - משתמש "מפעיל" לא "מאזל"
2. **Explainability** - שקיפות והסבר החלטות
3. **Human Handoff** - העברה חלקה לבני אדם
4. **Interactive Architecture** - מעצב מתפתח מסביב לאינטראקציה

### Task 4.1: Clinic Portal - Mission Control Layout
**References:**
- `תוכניתאבלממשקסוכןאוטונומיחזון,מגמותויישום.pdf` - Agentic UX spec
- `frontend/src/pages/AgenticDashboard.jsx` - Current implementation

**What to Update:**
```jsx
// clinic-portal/src/layouts/MissionControlLayout.jsx
export function MissionControlLayout() {
  return (
    <div className="mission-control-layout">
      {/* Persistent Sidebar (Left) */}
      <Sidebar />
      
      {/* Main Content Area */}
      <div className="main-content">
        {/* Header with KPIs */}
        <Header>
          <KPICards />
        </Header>
        
        {/* 70/30 Split */}
        <div className="content-split">
          {/* Left: Chat Interface (70%) */}
          <div className="chat-area">
            <AIChat />
          </div>
          
          {/* Right: Transparency Panel (30%) */}
          <div className="transparency-area">
            <TransparencyPanel />
          </div>
        </div>
      </div>
    </div>
  );
}

// Sidebar with persistent navigation
function Sidebar() {
  return (
    <aside className="sidebar">
      <Logo />
      <Navigation>
        <NavItem icon="home" label="Dashboard" to="/clinic/dashboard" />
        <NavItem icon="chat" label="AI Assistant" to="/clinic/chat" />
        <NavItem icon="calendar" label="Appointments" to="/clinic/appointments" />
        <NavItem icon="users" label="Patients" to="/clinic/patients" />
        <NavItem icon="treatment" label="Treatments" to="/clinic/treatments" />
        <NavItem icon="payments" label="Payments" to="/clinic/payments" />
        <NavItem icon="analytics" label="Analytics" to="/clinic/analytics" />
        <NavItem icon="settings" label="Settings" to="/clinic/settings" />
      </Navigation>
      <UserMenu />
    </aside>
  );
}

// Header with KPI Cards
function Header() {
  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => dataService.getKPIs()
  });
  
  return (
    <header className="header">
      <div className="kpi-cards">
        <KPICard
          label="Today's Patients"
          value={kpis?.todaysPatients || 0}
          icon="users"
          color="blue"
        />
        <KPICard
          label="Revenue (Month)"
          value={`₪${kpis?.monthlyRevenue || 0}`}
          icon="money"
          color="green"
        />
        <KPICard
          label="Pending Tasks"
          value={kpis?.pendingTasks || 0}
          icon="tasks"
          color="yellow"
        />
        <KPICard
          label="Satisfaction"
          value={`${kpis?.satisfaction || 0}%`}
          icon="smile"
          color="purple"
        />
      </div>
    </header>
  );
}
```

**CSS Layout:**
```css
/* clinic-portal/src/layouts/MissionControlLayout.css */
.mission-control-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: #001529;
  color: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 80px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 16px 24px;
  flex-shrink: 0;
}

.kpi-cards {
  display: flex;
  gap: 16px;
  height: 100%;
}

.content-split {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-area {
  flex: 0 0 70%;
  border-right: 1px solid #e8e8e8;
  overflow: auto;
}

.transparency-area {
  flex: 0 0 30%;
  overflow: auto;
  background: #fafafa;
}

/* Responsive */
@media (max-width: 1200px) {
  .content-split {
    flex-direction: column;
  }
  
  .chat-area,
  .transparency-area {
    flex: 1 1 auto;
  }
}
```

**Success Criteria:**
- [ ] 3-column layout (Sidebar, Chat, Transparency)
- [ ] Persistent sidebar navigation
- [ ] KPI cards in header
- [ ] 70/30 split for chat/transparency
- [ ] Responsive design
- [ ] Smooth transitions

---

#### Task 4.2: Transparency Panel Enhancement
**References:**
- `frontend/src/components/transparency/` - Current components
- Agentic UX spec - Explainability

**What to Update:**
```jsx
// clinic-portal/src/components/transparency/EnhancedTransparencyPanel.jsx
export function EnhancedTransparencyPanel() {
  const { currentAgent, agentActivity, decisionLog } = useAgentState();
  
  return (
    <div className="transparency-panel">
      {/* Current Agent Status */}
      <AgentStatusCard agent={currentAgent} />
      
      {/* Real-time Activity Feed */}
      <section className="activity-feed">
        <h3>Agent Activity</h3>
        <ActivityTimeline activities={agentActivity} />
      </section>
      
      {/* Decision Explanations */}
      <section className="decision-log">
        <h3>Decisions & Reasoning</h3>
        <DecisionList decisions={decisionLog} />
      </section>
      
      {/* Tool Usage */}
      <section className="tool-usage">
        <h3>Tools Used</h3>
        <ToolUsageChart />
      </section>
      
      {/* Human Handoff Queue */}
      <section className="handoff-queue">
        <h3>Needs Your Attention</h3>
        <HandoffQueue />
      </section>
    </div>
  );
}

// Agent Status Card
function AgentStatusCard({ agent }) {
  if (!agent) return null;
  
  return (
    <Card className="agent-status">
      <div className="agent-avatar">
        <img src={agent.avatar} alt={agent.name} />
        <StatusIndicator status="active" />
      </div>
      <div className="agent-info">
        <h3>{agent.name}</h3>
        <p className="role">{agent.role}</p>
        <p className="current-task">{agent.currentTask}</p>
      </div>
      <Tooltip content="Agent capabilities and permissions">
        <InfoIcon />
      </Tooltip>
    </Card>
  );
}

// Decision with Explanation
function DecisionCard({ decision }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <Card className="decision-card">
      <div className="decision-header" onClick={() => setExpanded(!expanded)}>
        <AgentBadge agent={decision.agent} />
        <span className="decision-title">{decision.title}</span>
        <ChevronIcon expanded={expanded} />
      </div>
      
      {expanded && (
        <div className="decision-details">
          <div className="reasoning">
            <h4>Reasoning:</h4>
            <p>{decision.reasoning}</p>
          </div>
          
          <div className="data-used">
            <h4>Data Considered:</h4>
            <ul>
              {decision.dataUsed.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
          
          <div className="alternatives">
            <h4>Alternatives Considered:</h4>
            <ul>
              {decision.alternatives.map((alt, i) => (
                <li key={i}>
                  {alt.option} - {alt.reason}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="confidence">
            <h4>Confidence:</h4>
            <ProgressBar value={decision.confidence} />
          </div>
        </div>
      )}
    </Card>
  );
}

// Human Handoff Queue
function HandoffQueue() {
  const { data: handoffs } = useQuery({
    queryKey: ['handoffs'],
    queryFn: () => dataService.getHandoffQueue()
  });
  
  if (!handoffs || handoffs.length === 0) {
    return (
      <div className="empty-state">
        <CheckCircleIcon />
        <p>All clear! No items need your attention.</p>
      </div>
    );
  }
  
  return (
    <div className="handoff-list">
      {handoffs.map(handoff => (
        <HandoffCard key={handoff.id} handoff={handoff} />
      ))}
    </div>
  );
}

function HandoffCard({ handoff }) {
  const handleTakeover = () => {
    // Take over from agent
    navigate(`/clinic/handoff/${handoff.id}`);
  };
  
  return (
    <Card className="handoff-card">
      <div className="handoff-header">
        <Badge variant={handoff.priority}>
          {handoff.priority}
        </Badge>
        <span className="time">{formatRelativeTime(handoff.created_at)}</span>
      </div>
      
      <div className="handoff-content">
        <p className="reason">{handoff.reason}</p>
        <p className="context">{handoff.context}</p>
      </div>
      
      <div className="handoff-actions">
        <Button onClick={handleTakeover}>
          Take Over
        </Button>
        <Button variant="outline" onClick={() => {}}>
          Dismiss
        </Button>
      </div>
    </Card>
  );
}
```

**Success Criteria:**
- [ ] Real-time agent status
- [ ] Activity timeline
- [ ] Decision explanations
- [ ] Tool usage visualization
- [ ] Handoff queue prominent
- [ ] Expandable details
- [ ] Smooth animations

---

#### Task 4.3: Patient Portal - Simplicity & Clarity
**References:**
- `patient-portal/src/` - Current implementation
- Mobile-first design principles

**What to Update:**
```jsx
// patient-portal/src/layouts/PatientLayout.jsx
export function PatientLayout() {
  return (
    <div className="patient-layout">
      {/* Simple Header */}
      <Header>
        <Logo />
        <Navigation />
        <UserMenu />
      </Header>
      
      {/* Main Content */}
      <main className="main-content">
        <Outlet />
      </main>
      
      {/* Mobile Bottom Navigation */}
      <MobileNav />
    </div>
  );
}

// Simple, clear navigation
function Navigation() {
  return (
    <nav className="navigation">
      <NavLink to="/patient/dashboard">
        <HomeIcon />
        <span>Home</span>
      </NavLink>
      <NavLink to="/patient/appointments">
        <CalendarIcon />
        <span>Appointments</span>
      </NavLink>
      <NavLink to="/patient/payments">
        <PaymentIcon />
        <span>Payments</span>
      </NavLink>
      <NavLink to="/patient/profile">
        <ProfileIcon />
        <span>Profile</span>
      </NavLink>
    </nav>
  );
}

// Mobile bottom navigation
function MobileNav() {
  return (
    <nav className="mobile-nav">
      <NavButton to="/patient/dashboard" icon={<HomeIcon />} label="Home" />
      <NavButton to="/patient/appointments" icon={<CalendarIcon />} label="Appointments" />
      <NavButton to="/patient/payments" icon={<PaymentIcon />} label="Pay" />
      <NavButton to="/patient/profile" icon={<ProfileIcon />} label="Profile" />
    </nav>
  );
}

// Clear, actionable dashboard
export function PatientDashboard() {
  const { data: nextAppointment } = useQuery({
    queryKey: ['next-appointment'],
    queryFn: () => appointmentService.getNextAppointment()
  });
  
  const { data: unpaidInvoices } = useQuery({
    queryKey: ['unpaid-invoices'],
    queryFn: () => paymentService.getUnpaidInvoices()
  });
  
  return (
    <div className="patient-dashboard">
      {/* Hero Section */}
      <section className="hero">
        <h1>Welcome back, {user.firstName}! 👋</h1>
        <p>Here's what's happening with your dental care</p>
      </section>
      
      {/* Next Appointment (Prominent) */}
      {nextAppointment && (
        <Card className="next-appointment-card">
          <CardHeader>
            <CalendarIcon />
            <h2>Your Next Appointment</h2>
          </CardHeader>
          <CardContent>
            <div className="appointment-details">
              <div className="date">
                <strong>{formatDate(nextAppointment.date)}</strong>
                <span>{formatTime(nextAppointment.time)}</span>
              </div>
              <div className="doctor">
                <img src={nextAppointment.doctor.avatar} alt="" />
                <span>Dr. {nextAppointment.doctor.name}</span>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button variant="outline" onClick={() => navigate('/patient/appointments')}>
              View Details
            </Button>
            <Button variant="destructive" onClick={() => {}}>
              Cancel
            </Button>
          </CardFooter>
        </Card>
      )}
      
      {/* Unpaid Invoices (Alert) */}
      {unpaidInvoices?.length > 0 && (
        <Alert variant="warning">
          <AlertIcon />
          <AlertTitle>You have {unpaidInvoices.length} unpaid invoice(s)</AlertTitle>
          <AlertDescription>
            Total: ₪{calculateTotal(unpaidInvoices)}
          </AlertDescription>
          <Button onClick={() => navigate('/patient/payments')}>
            Pay Now
          </Button>
        </Alert>
      )}
      
      {/* Quick Actions */}
      <section className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-grid">
          <ActionCard
            icon={<CalendarPlusIcon />}
            title="Book Appointment"
            description="Schedule your next visit"
            onClick={() => navigate('/patient/appointments/book')}
          />
          <ActionCard
            icon={<PaymentIcon />}
            title="Make Payment"
            description="Pay your invoices"
            onClick={() => navigate('/patient/payments')}
          />
          <ActionCard
            icon={<HistoryIcon />}
            title="Medical History"
            description="View your records"
            onClick={() => navigate('/patient/health')}
          />
          <ActionCard
            icon={<MessageIcon />}
            title="Contact Clinic"
            description="Send a message"
            onClick={() => navigate('/patient/contact')}
          />
        </div>
      </section>
    </div>
  );
}
```

**CSS:**
```css
/* patient-portal/src/layouts/PatientLayout.css */
.patient-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.main-content {
  flex: 1;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Mobile-first */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
    padding-bottom: 80px; /* Space for mobile nav */
  }
  
  .mobile-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid #e8e8e8;
    padding: 8px;
    justify-content: space-around;
    z-index: 1000;
  }
}

@media (min-width: 769px) {
  .mobile-nav {
    display: none;
  }
}

/* Clear, large touch targets */
.action-card {
  padding: 24px;
  min-height: 120px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Prominent CTAs */
.next-appointment-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1.1em;
}
```

**Success Criteria:**
- [ ] Simple, clear layout
- [ ] Mobile-first design
- [ ] Large touch targets (44px+)
- [ ] Prominent CTAs
- [ ] Clear hierarchy
- [ ] Fast loading
- [ ] Accessibility (WCAG 2.1 AA)

---

## Phase 5: Testing 🧪
**Duration:** 1-2 weeks  
**Priority:** 🔴 Critical (Quality Assurance)

### Week 1: Comprehensive Testing

#### Task 5.1: Unit Tests
**References:**
- `backend/tests/` - Existing tests
- `patient-portal/src/test/` - Frontend tests

**What to Build:**
```python
# backend/tests/test_clinical_service.py
import pytest
from app.services.clinical_service import ClinicalService

@pytest.mark.asyncio
async def test_get_medical_history():
    service = ClinicalService(mock_odoo_client)
    history = await service.get_medical_history(patient_id=67)
    
    assert len(history) > 0
    assert "disease_id" in history[0]
    assert "diagnosed_date" in history[0]

@pytest.mark.asyncio
async def test_create_treatment_plan():
    service = TreatmentPlanService(mock_odoo_client)
    
    plan_id = await service.create_treatment_plan(
        patient_id=67,
        treatments=[
            {"treatment_id": 1, "tooth_number": 16, "unit_price": 500},
            {"treatment_id": 2, "tooth_number": 17, "unit_price": 300}
        ],
        notes="Root canal + filling",
        estimated_cost=800
    )
    
    assert plan_id > 0
    
    # Verify plan was created
    plan = await service.get_treatment_plan(plan_id)
    assert plan["estimated_cost"] == 800
    assert len(plan["treatments"]) == 2

# backend/tests/test_payment_service.py
@pytest.mark.asyncio
async def test_create_payment():
    service = PaymentService(mock_tranzila, mock
