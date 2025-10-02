# ADR-004: Hybrid Architecture with Three Core Agents

**Date:** 2025-10-02  
**Status:** Accepted  
**Deciders:** scubapro711, Manus AI  
**Manus-Session-ID:** [Current session]  

---

## Context

After implementing Alex as a unified agent (ADR-001) and deferring Portfolio A (ADR-003), we need to decide the final agent architecture for MVP.

### The Question

How many agents should we build for MVP?

### Options

1. **Minimal (1 agent):** Just Alex
2. **Specialized (4 agents):** Dana, Michal, Yosef, Sarah
3. **Hybrid (3 agents):** Alex + CFO + Practice Admin
4. **Full (10 agents):** Alex + 7 Tier 2/3 + CFO + Practice Admin

### Business Context

- **Revenue Model:**
  - Tier 1 (₪500/mo): Alex only
  - Tier 2/3 (₪1,500-4,500/mo): Alex + Executive agents
- **Target:** 10 clinics × ₪1,500/mo = ₪15,000 MRR
- **Timeline:** 5-6 weeks for MVP
- **Goal:** Demonstrate executive agent capability

### Key Insight

**Executive agents (CFO, Practice Admin) are the differentiator:**
- Tier 1 (Alex only) is commodity - many chatbots exist
- Tier 2/3 (Executive agents) is unique - no one else offers this
- Need to demonstrate this capability in MVP

---

## Decision

**Build 3 core agents for MVP:**

1. **Alex** (Tier 1) - Patient-facing agent
   - Handles all patient interactions
   - Proven working (522 lines, 9/9 tests passing)
   - Generates Tier 1 revenue (₪500/mo)

2. **CFO Agent** (Tier 2/3) - Financial management
   - Daily financial reports
   - Cash flow analysis
   - Revenue forecasting
   - Expense optimization
   - Generates Tier 2/3 revenue (₪1,500/mo)

3. **Practice Administrator** (Tier 2/3) - Operations management
   - Morning briefings
   - Task coordination
   - Staff scheduling
   - Inventory management
   - Generates Tier 2/3 revenue (₪1,500/mo)

**Defer to Post-MVP:**
- 5 additional Tier 2/3 agents (CHRO, CMO, COO, CLO, CSO)
- 7 Portfolio A agents (company management)

---

## Consequences

### Positive

1. **Revenue Potential:** Can sell Tier 2/3 (₪1,500/mo vs ₪500/mo)
2. **Differentiation:** Demonstrates executive agent capability
3. **Balanced Scope:** Not too simple, not too complex
4. **Manageable Timeline:** 24-32 hours for 2 agents (vs 60-80h for 7)
5. **Customer Value:** CFO + Practice Admin provide real daily value
6. **Scalability:** Can add more agents post-MVP based on feedback

### Negative

1. **More Complex than Alex-only:** 2 additional agents to build
2. **More Testing:** Need to test 3 agents instead of 1
3. **More Maintenance:** 3 prompts to maintain instead of 1

### Neutral

1. **Architecture:** LangGraph supports multi-agent easily
2. **Cost:** 3 agents = 3x API calls (but customers pay for it)

---

## Alternatives Considered

| Alternative | Agents | Effort | Revenue | Pros | Cons | Decision |
|-------------|--------|--------|---------|------|------|----------|
| **A: Minimal** | 1 (Alex) | 0h | ₪500/mo | Fast, simple | Commodity, low revenue | ❌ Too basic |
| **B: Specialized** | 4 (Dana, Michal, Yosef, Sarah) | 12-16h | ₪500/mo | Specialized | Complex, same revenue as Alex | ❌ Not worth it |
| **C: Hybrid** | 3 (Alex + CFO + Practice Admin) | 24-32h | ₪1,500/mo | Balance, differentiation | Moderate complexity | ✅ **Selected** |
| **D: Full Tier 2/3** | 8 (Alex + 7 Tier 2/3) | 84-112h | ₪4,500/mo | Complete offering | Too long, risky | ❌ Too much |

---

## Implementation

### Phase 1: Alex (Done)
- [x] Implemented (522 lines)
- [x] Tests passing (9/9)
- [x] Telegram integration
- [x] Medical safety
- [x] Doctor escalation

### Phase 2: CFO Agent (Planned)
**Effort:** 12-16 hours

**Tasks:**
- [ ] Create `backend/app/agents/cfo.py`
- [ ] System prompt with financial expertise
- [ ] Tools:
  - get_financial_summary()
  - get_cash_flow()
  - get_revenue_forecast()
  - get_expense_breakdown()
  - get_profitability_analysis()
- [ ] Daily report generation (8am)
- [ ] Proactive insights
- [ ] Tests

**Capabilities:**
- "What's our revenue this month?"
- "What's our biggest expense?"
- "Are we profitable?"
- "Which treatment is most profitable?"
- "Do we have cash flow issues?"

### Phase 3: Practice Administrator (Planned)
**Effort:** 12-16 hours

**Tasks:**
- [ ] Create `backend/app/agents/practice_admin.py`
- [ ] System prompt with operations expertise
- [ ] Tools:
  - get_daily_schedule()
  - get_staff_status()
  - get_inventory_status()
  - get_equipment_maintenance()
  - create_task()
  - assign_task()
- [ ] Morning briefing generation (7am)
- [ ] Task management
- [ ] Tests

**Capabilities:**
- "Who's working today?"
- "What tasks are pending?"
- "Do we need to order supplies?"
- "When is equipment maintenance due?"
- "Create a task to order supplies"

### Phase 4: Multi-Agent Routing (Planned)
**Effort:** 4-6 hours

**Tasks:**
- [ ] Update agent_graph.py with routing logic
- [ ] Route patient queries → Alex
- [ ] Route financial queries → CFO
- [ ] Route operations queries → Practice Admin
- [ ] Tests

---

## Validation

**Success Criteria:**

1. **Technical:**
   - ✅ All 3 agents working
   - ✅ Routing works correctly
   - ✅ All tests passing
   - ✅ Response time <5 seconds

2. **Business:**
   - ✅ Can sell Tier 2/3 (₪1,500/mo)
   - ✅ 10 clinics onboarded
   - ✅ ₪15,000 MRR

3. **Customer Value:**
   - ✅ CFO provides daily financial insights
   - ✅ Practice Admin sends morning briefings
   - ✅ Customers find value in executive agents
   - ✅ >90% customer satisfaction

**Review Date:** 2025-12-02 (2 months after MVP launch)

**Review Questions:**
1. Are customers using CFO and Practice Admin?
2. Do customers see value in Tier 2/3?
3. Should we build more Tier 2/3 agents?
4. Which agents should we prioritize next?

---

## Architecture

### LangGraph Structure

```
┌─────────────────────────────────────────────────┐
│         LangGraph StateGraph                     │
├─────────────────────────────────────────────────┤
│                                                   │
│  START                                           │
│    ↓                                             │
│  Router (classify query)                         │
│    ├─ "patient query" → Alex                    │
│    ├─ "financial query" → CFO                   │
│    └─ "operations query" → Practice Admin       │
│    ↓                                             │
│  Agent (execute)                                 │
│    ↓                                             │
│  END                                             │
│                                                   │
└─────────────────────────────────────────────────┘
```

### Routing Logic

```python
def route_query(state: AgentState) -> str:
    """Route query to appropriate agent."""
    query = state["messages"][-1].content.lower()
    
    # Financial keywords
    if any(kw in query for kw in ["revenue", "profit", "expense", "invoice", "payment"]):
        return "cfo"
    
    # Operations keywords
    if any(kw in query for kw in ["schedule", "staff", "inventory", "task", "equipment"]):
        return "practice_admin"
    
    # Default to Alex (patient queries)
    return "alex"
```

---

## Future Expansion

### Post-MVP: Add More Tier 2/3 Agents

Based on customer feedback, prioritize:

1. **CHRO** (if hiring is pain point)
2. **CMO** (if marketing is pain point)
3. **COO** (if operations is pain point)
4. **CLO** (if compliance is pain point)
5. **CSO** (if strategy is pain point)

**Effort:** 12-16 hours per agent

**Revenue:** Upsell to Tier 3 (₪4,500/mo)

---

## References

- **Work Plan:** WORK_PLAN_V19.0_UNIFIED.md (Phase 3: Executive Agents)
- **Gap Analysis:** COMPLETE_GAP_ANALYSIS_V1.md (Agent Inventory)
- **Related ADRs:**
  - ADR-001: Merge 4 agents into Alex
  - ADR-002: OpenManus → LangGraph
  - ADR-003: Defer Portfolio A
- **Code (Planned):**
  - `backend/app/agents/cfo.py`
  - `backend/app/agents/practice_admin.py`
  - `backend/app/agents/agent_graph.py` (routing)
