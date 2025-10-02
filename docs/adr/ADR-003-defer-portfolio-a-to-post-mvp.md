# ADR-003: Defer Portfolio A Agents to Post-MVP

**Date:** 2025-10-02  
**Status:** Accepted  
**Deciders:** scubapro711, Manus AI  
**Manus-Session-ID:** [Current session]  

---

## Context

The original vision (V14.0) included **Portfolio A** - a set of 7 executive agents to manage DentalAI company operations:

1. **CPO (Chief Product Officer)** - Product roadmap, feature prioritization
2. **CRO (Chief Revenue Officer)** - Sales strategy, customer acquisition
3. **CCO (Chief Customer Officer)** - Customer success, retention
4. **CFO (Chief Financial Officer)** - Company finances, fundraising
5. **CPO (Chief People Officer)** - Hiring, team management
6. **COO (Chief Operations Officer)** - Company operations, processes
7. **CSO (Chief Strategy Officer)** - Business strategy, competitive analysis

### Purpose of Portfolio A

Portfolio A agents are designed to help **DentalAI management** (scubapro711 and team) run the company:
- Not for clinic owners (that's Tier 2/3 agents)
- Not for patients (that's Tier 1 agents)
- For the **company itself** - internal operations

### Current Situation

- **Team Size:** 1-2 people (scubapro711 + occasional contractors)
- **Customer Base:** 0 clinics (pre-launch)
- **Revenue:** ₪0 MRR
- **Stage:** Pre-MVP, building product

### The Problem

Building Portfolio A now would:
1. **Take 84-112 hours** (12-16h per agent × 7 agents)
2. **Delay MVP by 2-3 weeks**
3. **Provide limited value** - company is too small to need these agents
4. **Distract from core product** - should focus on customer-facing features

---

## Decision

**Defer Portfolio A agents to post-MVP.**

Focus MVP on:
1. **Tier 1:** Alex (patient-facing)
2. **Tier 2/3:** CFO + Practice Admin (clinic management)
3. **Infrastructure:** Framework, deployment, monitoring

Build Portfolio A **after** achieving MVP success:
- 10+ paying clinics
- ₪15,000+ MRR
- Proven product-market fit
- Team growth (3-5 people)

---

## Consequences

### Positive

1. **Faster MVP:** Save 84-112 hours (2-3 weeks)
2. **Focus:** Concentrate on customer-facing features
3. **Validation:** Prove product-market fit before internal tools
4. **Resource Efficiency:** Don't build what we don't need yet
5. **Flexibility:** Learn what we actually need before building

### Negative

1. **Manual Management:** scubapro711 must manage company manually
2. **No Automation:** Company operations not automated
3. **Scaling Challenges:** May struggle to scale without these agents
4. **Missed Dogfooding:** Can't demo Portfolio A to investors/customers

### Neutral

1. **Future Work:** Will need to build eventually (if company grows)
2. **Architecture:** Design supports adding Portfolio A later

---

## Alternatives Considered

| Alternative | Pros | Cons | Why Not Selected |
|-------------|------|------|------------------|
| **A: Build Now** | Complete product, dogfooding | 84-112h delay, limited value | Not critical for MVP |
| **B: Defer to Post-MVP** | Faster MVP, focus on customers | Manual management | ✅ **Selected** |
| **C: Build Subset (2-3 agents)** | Some automation | Still 24-48h delay | Still not critical |
| **D: Never Build** | Maximum focus | No internal automation | May need eventually |

---

## Implementation

**Immediate Actions:**
- [x] Remove Portfolio A from MVP scope (V19.0)
- [x] Update work plan to mark Portfolio A as "Paused"
- [x] Document decision in this ADR
- [x] Focus on Tier 1 + Tier 2/3 agents

**Post-MVP Triggers:**

Build Portfolio A when **any** of these conditions are met:

1. **Scale Trigger:**
   - 20+ paying clinics
   - ₪30,000+ MRR
   - Team size 5+ people

2. **Pain Trigger:**
   - Manual management becomes bottleneck
   - Missing critical business insights
   - Unable to scale operations

3. **Opportunity Trigger:**
   - Investor demo requires it
   - Customer asks for similar tool
   - Competitive advantage

---

## Validation

**Success Criteria (MVP without Portfolio A):**

1. **Product:**
   - ✅ Alex agent working
   - ✅ CFO + Practice Admin working
   - ✅ Mission Control dashboard
   - ✅ 10 paying clinics

2. **Business:**
   - ✅ ₪15,000 MRR
   - ✅ <5% churn
   - ✅ >90% customer satisfaction

3. **Operations:**
   - ✅ scubapro711 can manage company manually
   - ✅ No critical bottlenecks
   - ✅ Sustainable workload

**Review Date:** 2026-01-02 (3 months after MVP launch)

**Review Questions:**
1. Did we achieve MVP success without Portfolio A?
2. Is manual management sustainable?
3. Do we need Portfolio A now?
4. What would be the ROI of building it?

---

## Future Architecture (When Portfolio A is Built)

### Portfolio A Dashboard (Super Admin)

```
┌─────────────────────────────────────────────────┐
│         Portfolio A Dashboard                    │
│         (For DentalAI Management)                │
├─────────────────────────────────────────────────┤
│                                                   │
│  📊 Company KPIs                                 │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │ MRR      │ Clinics  │ Churn    │ NPS      │ │
│  │ ₪45,000  │ 30       │ 3%       │ 85       │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
│                                                   │
│  🤖 Agent Status                                 │
│  ┌─────────────────────────────────────────────┐│
│  │ CPO: Reviewing feature requests (12 pending)││
│  │ CRO: Analyzing sales pipeline (5 leads)     ││
│  │ CCO: Monitoring customer health (2 at risk) ││
│  │ CFO: Preparing monthly report               ││
│  │ CPO (HR): Screening candidates (3 active)   ││
│  │ COO: Optimizing processes                   ││
│  │ CSO: Analyzing market trends                ││
│  └─────────────────────────────────────────────┘│
│                                                   │
│  📈 Insights & Recommendations                   │
│  • CPO: "Feature X requested by 8 customers"   │
│  • CRO: "Lead Y is ready to close"             │
│  • CCO: "Customer Z needs attention"           │
│  • CFO: "Cash runway: 18 months"               │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## References

- **Work Plans:**
  - V14.0: Original Portfolio A design (Epic 8, Week 10)
  - V17.0: Removed Portfolio A (simplification)
  - V19.0: Confirmed deferral to post-MVP
- **Gap Analysis:** COMPLETE_GAP_ANALYSIS_V1.md (Portfolio A section)
- **Related ADRs:**
  - ADR-001: Merge 4 agents into Alex
  - ADR-004: Hybrid architecture (Alex + CFO + Practice Admin)
- **Future ADRs:**
  - ADR-00X: Portfolio A implementation (when built)
