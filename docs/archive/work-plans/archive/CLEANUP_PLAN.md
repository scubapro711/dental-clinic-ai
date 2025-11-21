# 🧹 Repository Cleanup Plan

**Date:** October 2, 2025  
**Purpose:** Remove duplicate and outdated files to maintain clean repository

---

## Files to Archive (Move to `/archive/` directory)

### Old Work Plans (Keep only V17.0)
- `WORK_PLAN_V14.0.md` (65K) → `archive/work_plans/`
- `WORK_PLAN_V14.0_STATUS_UPDATE.md` (20K) → `archive/work_plans/`
- `WORK_PLAN_V14.1.md` (67K) → `archive/work_plans/`
- `WORK_PLAN_V14.1_FULL.md` (65K) → `archive/work_plans/`
- `WORK_PLAN_V15.0.md` (19K) → `archive/work_plans/`
- `WORK_PLAN_V16.0.md` (33K) → `archive/work_plans/`

### Old Reports (Keep only latest comprehensive ones)
- `MVP_AUDIT_REPORT.md` (6.7K) → `archive/reports/` (superseded by PROJECT_STATUS_REPORT.md)
- `MVP_COMPLETION_SUMMARY.md` (12K) → `archive/reports/` (superseded by ALEX_COMPLETION_REPORT.md)
- `MVP_PROGRESS.md` (9.5K) → `archive/reports/` (superseded by PROJECT_STATUS_REPORT.md)
- `MVP_TEST_REPORT.md` (10K) → `archive/reports/` (superseded by test files)
- `REPOSITORY_VERIFICATION_REPORT.md` (2.6K) → `archive/reports/` (one-time verification)
- `FRAMEWORK_SUMMARY.md` (4.1K) → `archive/reports/` (superseded by PROJECT_STATUS_REPORT.md)

### Keep These Files (Current & Relevant)
- ✅ `README.md` - Project overview
- ✅ `CONTRIBUTING.md` - Contribution guidelines
- ✅ `WORK_PLAN_V17.0.md` - Current work plan
- ✅ `PROJECT_STATUS_REPORT.md` - Current status
- ✅ `ALEX_COMPLETION_REPORT.md` - Alex implementation details
- ✅ `PHASE_1.2_COMPLETION_REPORT.md` - Phase 1.2 completion
- ✅ `PHASE_1_ASSESSMENT_REPORT.md` - Initial assessment

---

## Code Files to Remove/Archive

### If Alex Architecture is Chosen (Recommended)

**Remove these agent files:**
- `backend/app/agents/dana.py`
- `backend/app/agents/michal.py`
- `backend/app/agents/yosef.py`
- `backend/app/agents/sarah.py`
- `backend/app/agents/emma.py`
- `backend/app/agents/lisa.py`
- `backend/app/agents/robert.py`
- `backend/app/agents/jessica.py`
- `backend/app/agents/agent_graph.py` (old 4-agent version)

**Keep these:**
- ✅ `backend/app/agents/alex.py`
- ✅ `backend/app/agents/agent_graph_v2.py` → rename to `agent_graph.py`
- ✅ `backend/app/agents/error_handler.py`
- ✅ `backend/app/agents/tools/`

**Remove these test files:**
- `backend/tests/test_new_agents.py` (tests for Emma, Lisa, Robert, Jessica)

**Keep these:**
- ✅ `backend/tests/test_alex_safety.py`
- ✅ `backend/tests/test_integration.py`
- ✅ `backend/tests/test_e2e_mvp.py`
- ✅ `backend/tests/test_causal_memory_integration.py`

---

## Directory Structure After Cleanup

```
dental-clinic-ai/
├── README.md
├── CONTRIBUTING.md
├── WORK_PLAN_V17.0.md                    # Current work plan
├── PROJECT_STATUS_REPORT.md              # Current status
├── ALEX_COMPLETION_REPORT.md             # Alex details
├── PHASE_1.2_COMPLETION_REPORT.md        # Phase 1.2 completion
├── PHASE_1_ASSESSMENT_REPORT.md          # Initial assessment
├── archive/
│   ├── work_plans/
│   │   ├── WORK_PLAN_V14.0.md
│   │   ├── WORK_PLAN_V14.0_STATUS_UPDATE.md
│   │   ├── WORK_PLAN_V14.1.md
│   │   ├── WORK_PLAN_V14.1_FULL.md
│   │   ├── WORK_PLAN_V15.0.md
│   │   └── WORK_PLAN_V16.0.md
│   └── reports/
│       ├── MVP_AUDIT_REPORT.md
│       ├── MVP_COMPLETION_SUMMARY.md
│       ├── MVP_PROGRESS.md
│       ├── MVP_TEST_REPORT.md
│       ├── REPOSITORY_VERIFICATION_REPORT.md
│       └── FRAMEWORK_SUMMARY.md
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── alex.py                   # Unified agent
│   │   │   ├── agent_graph.py            # Renamed from agent_graph_v2.py
│   │   │   ├── error_handler.py
│   │   │   └── tools/
│   │   │       ├── agent_tools.py
│   │   │       └── odoo_tools.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── integrations/
│   │   ├── memory/
│   │   ├── models/
│   │   └── main.py
│   └── tests/
│       ├── test_alex_safety.py
│       ├── test_integration.py
│       ├── test_e2e_mvp.py
│       └── test_causal_memory_integration.py
└── ...
```

---

## Cleanup Commands

```bash
# Create archive directories
mkdir -p archive/work_plans
mkdir -p archive/reports

# Move old work plans
mv WORK_PLAN_V14.0.md archive/work_plans/
mv WORK_PLAN_V14.0_STATUS_UPDATE.md archive/work_plans/
mv WORK_PLAN_V14.1.md archive/work_plans/
mv WORK_PLAN_V14.1_FULL.md archive/work_plans/
mv WORK_PLAN_V15.0.md archive/work_plans/
mv WORK_PLAN_V16.0.md archive/work_plans/

# Move old reports
mv MVP_AUDIT_REPORT.md archive/reports/
mv MVP_COMPLETION_SUMMARY.md archive/reports/
mv MVP_PROGRESS.md archive/reports/
mv MVP_TEST_REPORT.md archive/reports/
mv REPOSITORY_VERIFICATION_REPORT.md archive/reports/
mv FRAMEWORK_SUMMARY.md archive/reports/

# Remove old agent files (if Alex is chosen)
rm backend/app/agents/dana.py
rm backend/app/agents/michal.py
rm backend/app/agents/yosef.py
rm backend/app/agents/sarah.py
rm backend/app/agents/emma.py
rm backend/app/agents/lisa.py
rm backend/app/agents/robert.py
rm backend/app/agents/jessica.py
rm backend/app/agents/agent_graph.py

# Rename agent_graph_v2.py to agent_graph.py
mv backend/app/agents/agent_graph_v2.py backend/app/agents/agent_graph.py

# Remove old test files
rm backend/tests/test_new_agents.py
rm backend/tests/test_yosef_tools.py
rm backend/tests/test_agents.py
rm backend/tests/test_agent_graph.py

# Update imports in main.py
# (Manual step - update import from agent_graph_v2 to agent_graph)

# Commit cleanup
git add -A
git commit -m "chore: Clean up duplicate files and old code

Moved old work plans and reports to archive/
Removed 4-agent architecture code (chose Alex unified agent)
Renamed agent_graph_v2.py to agent_graph.py
Removed obsolete test files

Manus-Session-ID: <session_id>
Human-Initiator: scubapro711"
```

---

## Benefits of Cleanup

1. **Clarity:** Easier to find current documentation
2. **Reduced Confusion:** No ambiguity about which file is current
3. **Smaller Repository:** Faster clones and checkouts
4. **Better Maintainability:** Less code to maintain
5. **Clear History:** Archive preserves history without cluttering main directory

---

**Cleanup Ready to Execute!**
