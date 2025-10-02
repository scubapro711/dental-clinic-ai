# Dental Clinic AI - Work Plan V18.0

**Date:** October 2, 2025  
**Version:** 18.0 (Agentic UX + Holistic Framework Integration)  
**Based On:**  
- מסגרת עבודה הוליסטית לגיבוי ושחזור (Holistic Framework)
- תוכנית אב לממשק סוכן אוטונומי (Agentic UX Vision)
- WORK_PLAN_V17.1 (Previous work completed)

**Project Status:** 42% Complete

---

## 📋 Document Purpose

This work plan **fully integrates** three critical components:

1. **Agentic UX Vision** - Mission Control interface, not traditional dashboard
2. **Holistic Framework** - Git protocol, AWS Secrets, Backup/Recovery
3. **Completed Work** - Escalation fix, Telegram bot, Mock Odoo (1500 patients)

**Key Changes from V17.1:**
- ✅ Integrated Agentic UX vision (4 screens with visual hierarchy)
- ✅ Updated to reflect completed work (Telegram, Odoo, Doctor Escalation)
- ✅ Aligned with Holistic Framework requirements
- ✅ Updated project completion: 38% → 42%
- ✅ Added Mission Control frontend implementation

---

## 🎯 Project Vision: Agentic Experience

**Goal:** Production-ready **autonomous agent system** with:

### Core Philosophy: Agentic UX (Not Traditional UI)
> "The user doesn't 'operate' the system - they give it a **mission**. The agent executes autonomously, and the interface shows **what's happening now**, not history."

**Key Principles:**
1. **Mission Control** - User assigns tasks, agent executes
2. **Transparency** - Real-time visibility into agent actions
3. **Explainability** - Clear reasoning for decisions
4. **Human Handoff** - Seamless escalation when needed
5. **Interactive Feedback** - Agent adapts based on user feedback

### Technical Stack
- **Backend:** Alex unified agent (LangGraph)
- **Frontend:** Mission Control interface (4 screens)
- **Integration:** Odoo (patient data), Telegram (communication)
- **Safety:** Medical boundaries, doctor escalation
- **Framework:** Holistic Git protocol, AWS Secrets, Disaster Recovery

**Timeline:** 48-58 hours from current state  
**Target Date:** 3 weeks (with 1 developer full-time)

---

## 📊 Current State Summary (42% Complete)

### ✅ What's Done (42% overall):

**Backend (85%)**
- ✅ Alex unified agent architecture (100%)
- ✅ Escalation detection bug fixed (100%)
- ✅ Telegram bot integration (100%)
- ✅ Mock Odoo with 1500 patients (100%)
- ✅ Statistics API (overview, patients, appointments, revenue) (100%)
- ✅ Doctor escalation endpoints (100%)
- ✅ Error handling + rate limiting (100%)
- ✅ Basic tests (31 tests passing) (80%)

**Data (100%)**
- ✅ 1,500 realistic patients
- ✅ 12,124 appointments (past & future)
- ✅ 5,089 invoices (₪7.8M revenue)
- ✅ 5,089 treatment records
- ✅ Israeli & international names
- ✅ Realistic distributions

**Git & Commits (30%)**
- ✅ Repository structure
- ⚠️ Manus-Session-ID protocol (partial)
- ❌ Holistic commit format (not implemented)

### ❌ What's Missing (58%):

**Framework Protocol (0%)**
- ❌ Full Git protocol (Manus-Session-ID, Author/Committer)
- ❌ AWS Secrets Manager
- ❌ Backup & Recovery (RTO/RPO)
- ❌ GitHub Actions automation

**Frontend (0%)**
- ❌ Mission Control Dashboard
- ❌ Conversation History Screen
- ❌ Performance Analytics Screen
- ❌ Knowledge Management Screen

**Integration (30%)**
- ⚠️ Real Odoo connection (using mock)
- ❌ Neo4j fully integrated (50%)
- ❌ Production deployment

---

## 🏗️ Phase Overview

| Phase | Name | Priority | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Holistic Framework Protocol | 🔴 CRITICAL | 18-22h | ❌ 0% |
| 1 | Agentic UX Frontend | 🔴 HIGH | 20-24h | ❌ 0% |
| 2 | Real Odoo Integration | 🟡 MEDIUM | 4-6h | ⚠️ 50% (mock done) |
| 3 | Production Deployment | 🟢 LOW | 6-8h | ❌ 0% |

**Total Remaining:** 48-60 hours  
**Total Completed:** ~25 hours (from V17.1 + recent work)

---

# Phase 0: Holistic Framework Protocol Implementation

**Priority:** 🔴 CRITICAL  
**Duration:** 18-22 hours  
**Status:** ❌ Not Started  
**Goal:** Implement all requirements from מסגרת עבודה הוליסטית

**Why Critical:**
This is the **foundation** for production deployment. Without it:
- ❌ No disaster recovery capability
- ❌ Security vulnerabilities (secrets exposed)
- ❌ No audit trail for compliance
- ❌ Cannot track Manus agent actions

**Framework Reference:** Parts I-VII of מסגרת עבודה

---

## Epic 0.1: Manus-Git Protocol (3-4 hours)

**Framework Reference:** Part II - Git Repository Protocol

### User Story 0.1.1: Implement Commit Message Format (1.5h)

**Description:**  
Implement structured commit messages with Manus-Session-ID.

**Framework Requirement:**
```
<Type>(<Scope>): <Subject>

<Body>

Manus-Session-ID: <session_id_from_manus_api>
Manus-Task-ID: <specific_task_or_plan_step_id>
Human-Initiator: <username_of_human_who_gave_the_prompt>
```

**Acceptance Criteria:**
- [ ] Git hook created: `.git/hooks/prepare-commit-msg`
- [ ] Hook automatically adds Manus-Session-ID to commits
- [ ] Session ID extracted from `getSession` API
- [ ] Human-Initiator: scubapro711
- [ ] Task-ID extracted from branch name or manual input
- [ ] Hook tested with 5 sample commits

**Tasks:**
1. Create `.git/hooks/prepare-commit-msg` script
2. Implement logic to call Manus `getSession` API
3. Extract session ID, task ID, human initiator
4. Format commit message per framework
5. Test with sample commits
6. Document in `docs/GIT_PROTOCOL.md`

**Files to Create:**
- `.git/hooks/prepare-commit-msg`
- `docs/GIT_PROTOCOL.md`

---

### User Story 0.1.2: Implement Author vs Committer Distinction (1h)

**Description:**  
Distinguish between human author and Manus agent committer.

**Framework Requirement:**
> "Author = Human who initiated the work  
> Committer = Manus AI Agent"

**Acceptance Criteria:**
- [ ] Git config set: `GIT_COMMITTER_NAME = "Manus AI Agent"`
- [ ] Git config set: `GIT_COMMITTER_EMAIL = "manus@agent.local"`
- [ ] Git config set: `GIT_AUTHOR_NAME = <human_name>`
- [ ] Git config set: `GIT_AUTHOR_EMAIL = <human_email>`
- [ ] All commits show: Author = Human, Committer = Manus
- [ ] Verified with `git log --format=fuller`

**Tasks:**
1. Update `.git/hooks/prepare-commit-msg` to set author/committer
2. Test with sample commits
3. Verify `git log --format=fuller` shows both
4. Document in `docs/GIT_PROTOCOL.md`

**Files to Modify:**
- `.git/hooks/prepare-commit-msg`
- `docs/GIT_PROTOCOL.md`

---

### User Story 0.1.3: Implement Git Bundle Creation (30min)

**Description:**  
Create git bundle for offline backup.

**Framework Requirement:**
> "Create git bundle containing all branches, tags, and commit history"

**Acceptance Criteria:**
- [ ] Script `scripts/create_git_bundle.sh` created
- [ ] Bundle includes all branches
- [ ] Bundle includes all tags
- [ ] Bundle named: `dental-clinic-ai-YYYYMMDD-HHMMSS-<commit-hash>.tar.gz`
- [ ] Bundle tested (can restore from it)

**Tasks:**
1. Create `scripts/create_git_bundle.sh`
2. Add logic: `git bundle create repo.bundle --all`
3. Add logic: tar + gzip bundle
4. Test bundle creation
5. Test bundle restoration: `git clone repo.bundle my-restored-project`
6. Document in `docs/GIT_BACKUP.md`

**Files to Create:**
- `scripts/create_git_bundle.sh`
- `docs/GIT_BACKUP.md`

---

## Epic 0.2: AWS Secrets Manager (4-5 hours)

**Framework Reference:** Part III - AWS Secrets Manager

### User Story 0.2.1: Set Up AWS Secrets Manager (2h)

**Description:**  
Configure AWS Secrets Manager with customer-managed KMS keys.

**Framework Requirement:**
> "Use customer-managed KMS keys (not AWS-managed)  
> Create IAM roles: HumanDeveloperRole, ManusAgentRole"

**Acceptance Criteria:**
- [ ] AWS account configured
- [ ] Customer-managed KMS key created: `dental-clinic-ai-secrets-key`
- [ ] IAM role created: `HumanDeveloperRole` (full access)
- [ ] IAM role created: `ManusAgentRole` (read-only via secretsmanager:GetSecretValue)
- [ ] CloudTrail enabled for audit logging
- [ ] Terraform config created

**Tasks:**
1. Create Terraform config: `terraform/aws_secrets.tf`
2. Define KMS key with rotation
3. Define IAM roles (HumanDeveloperRole, ManusAgentRole)
4. Define CloudTrail logging
5. Apply terraform: `terraform apply`
6. Test access with both roles
7. Document in `docs/AWS_SECRETS_SETUP.md`

**Files to Create:**
- `terraform/aws_secrets.tf`
- `docs/AWS_SECRETS_SETUP.md`

---

### User Story 0.2.2: Migrate Secrets from .env (2h)

**Description:**  
Move all secrets from `.env` files to AWS Secrets Manager.

**Current Secrets (in .env):**
- DATABASE_URL
- REDIS_URL
- NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
- ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
- OPENAI_API_KEY
- JWT_SECRET_KEY
- TELEGRAM_BOT_TOKEN
- SECRET_KEY

**Acceptance Criteria:**
- [ ] All secrets stored in AWS Secrets Manager
- [ ] Secret name: `prod/dental-clinic-ai/openai-api-key`
- [ ] Secret rotation enabled (90 days)
- [ ] `.env` files removed from repository (git history cleaned)
- [ ] `.env.example` created (with placeholders)
- [ ] Code updated to fetch from AWS: `boto3.client('secretsmanager').get_secret_value()`

**Tasks:**
1. Create secrets in AWS Secrets Manager
2. Upload all secrets with proper naming
3. Update `backend/app/core/config.py` to fetch from AWS
4. Test application with AWS secrets
5. Remove `.env` from git: `git filter-repo --path .env --invert-paths`
6. Add `.env` to `.gitignore`
7. Create `.env.example` with placeholders
8. Document in `docs/AWS_SECRETS_MIGRATION.md`

**Files to Modify:**
- `backend/app/core/config.py`
- `.gitignore`

**Files to Create:**
- `.env.example`
- `docs/AWS_SECRETS_MIGRATION.md`

**Files to Delete:**
- `.env` (from git history)

---

### User Story 0.2.3: Implement Secret Rotation (1h)

**Description:**  
Set up automatic secret rotation for sensitive credentials.

**Framework Requirement:**
> "Enable automatic rotation for database passwords and API keys"

**Acceptance Criteria:**
- [ ] Rotation enabled for DATABASE_URL password
- [ ] Rotation enabled for JWT_SECRET_KEY
- [ ] Rotation period: 90 days
- [ ] Lambda function created for rotation logic
- [ ] Rotation tested manually

**Tasks:**
1. Create Lambda function: `lambda/rotate_secrets.py`
2. Configure rotation in AWS Secrets Manager
3. Test rotation manually
4. Verify application still works after rotation
5. Document in `docs/SECRET_ROTATION.md`

**Files to Create:**
- `lambda/rotate_secrets.py`
- `docs/SECRET_ROTATION.md`

---

## Epic 0.3: Manus Session Integration (3-4 hours)

**Framework Reference:** Part IV - Manus Session Integration

### User Story 0.3.1: Implement getSession API Integration (2h)

**Description:**  
Integrate with Manus `getSession` API to retrieve session context.

**Framework Requirement:**
> "Call getSession API to retrieve:  
> - session_id  
> - human_intention  
> - agent_execution_log  
> - artifacts_generated"

**API Endpoint:**
```
GET https://api.manus.im/api/chat/getSession?sessionId=xxx
Authorization: Bearer <MANUS_API_TOKEN>
```

**Acceptance Criteria:**
- [ ] Script `scripts/get_manus_session.py` created
- [ ] Script calls getSession API with session ID
- [ ] API token stored in AWS Secrets Manager
- [ ] Session data saved to `artifacts/sessions/<session_id>.json`
- [ ] Script tested with real session ID
- [ ] Error handling for API failures

**Tasks:**
1. Create `scripts/get_manus_session.py`
2. Add Manus API token to AWS Secrets Manager
3. Implement API call logic with requests library
4. Parse JSON response
5. Save session data to `artifacts/sessions/<session_id>.json`
6. Test with real session ID
7. Document in `docs/MANUS_SESSION_INTEGRATION.md`

**Files to Create:**
- `scripts/get_manus_session.py`
- `docs/MANUS_SESSION_INTEGRATION.md`

---

### User Story 0.3.2: Implement Session Export Protocol (1h)

**Description:**  
Export session data in standardized format for backup.

**Framework Requirement:**
> "Export session as JSON with:  
> - session_id  
> - timestamp  
> - human_intention  
> - agent_log  
> - artifacts  
> - outcome"

**Acceptance Criteria:**
- [ ] Export format defined in JSON schema
- [ ] Script exports session to `artifacts/sessions/<session_id>.json`
- [ ] Schema validated with jsonschema library
- [ ] Tested with 3 different sessions

**Tasks:**
1. Define JSON schema: `schemas/manus_session.json`
2. Update export script to match schema
3. Validate with jsonschema library
4. Test with multiple sessions
5. Document in `docs/SESSION_EXPORT.md`

**Files to Create:**
- `schemas/manus_session.json`
- `docs/SESSION_EXPORT.md`

---

## Epic 0.4: GitHub Actions Automation (4-5 hours)

**Framework Reference:** Part V - Backup Automation

### User Story 0.4.1: Implement Holistic Operational Backup (3h)

**Description:**  
Create GitHub Actions workflow for automated backup.

**Framework Requirement:**
> "On every push to main:  
> 1. Extract Manus-Session-ID from commit  
> 2. Call getSession API  
> 3. Create git bundle  
> 4. Package artifacts  
> 5. Upload to S3 with encryption"

**Acceptance Criteria:**
- [ ] Workflow file created: `.github/workflows/backup.yml`
- [ ] Workflow triggers on push to main
- [ ] Extracts Manus-Session-ID from commit message
- [ ] Calls getSession API
- [ ] Creates git bundle
- [ ] Packages artifacts: `tar -czf <timestamp>-<commit-hash>.tar.gz`
- [ ] Uploads to S3 bucket with encryption
- [ ] Tested with sample push

**Tasks:**
1. Create `.github/workflows/backup.yml`
2. Add step: Extract Manus-Session-ID from commit
3. Add step: Call getSession API (use secrets.MANUS_API_TOKEN)
4. Add step: Create git bundle
5. Add step: Package artifacts
6. Add step: Upload to S3 (use aws-actions/configure-aws-credentials@v2)
7. Test workflow with sample push
8. Document in `docs/BACKUP_AUTOMATION.md`

**Files to Create:**
- `.github/workflows/backup.yml`
- `docs/BACKUP_AUTOMATION.md`

---

### User Story 0.4.2: Implement Disaster Recovery Testing (2h)

**Description:**  
Create scripts to test disaster recovery procedures.

**Framework Requirement:**
> "Test disaster recovery monthly:  
> 1. Restore from S3 backup  
> 2. Restore git bundle  
> 3. Restore Manus session  
> 4. Verify data integrity"

**Acceptance Criteria:**
- [ ] Script `scripts/test_disaster_recovery.sh` created
- [ ] Script downloads latest backup from S3
- [ ] Script restores git bundle
- [ ] Script restores Manus session
- [ ] Script verifies data integrity (checksums)
- [ ] Tested successfully

**Tasks:**
1. Create `scripts/test_disaster_recovery.sh`
2. Add logic to download from S3
3. Add logic to restore git bundle
4. Add logic to restore Manus session
5. Add logic to verify integrity
6. Test full recovery process
7. Document in `docs/DISASTER_RECOVERY_TESTING.md`

**Files to Create:**
- `scripts/test_disaster_recovery.sh`
- `docs/DISASTER_RECOVERY_TESTING.md`

---

## Epic 0.5: RTO/RPO Configuration (2-3 hours)

**Framework Reference:** Part VI - RTO/RPO Requirements

### User Story 0.5.1: Configure S3 Lifecycle & Replication (2h)

**Description:**  
Configure S3 for disaster recovery with proper RTO/RPO.

**Framework Requirement:**
> "RTO: 4 hours (Recovery Time Objective)  
> RPO: 1 hour (Recovery Point Objective)  
> Use S3 Cross-Region Replication (CRR)"

**Acceptance Criteria:**
- [ ] S3 bucket created: `dental-clinic-ai-backups`
- [ ] S3 Lifecycle policy: Standard → Glacier (7 days) → Deep Archive (90 days)
- [ ] S3 Cross-Region Replication enabled (us-east-1 → us-west-2)
- [ ] Versioning enabled
- [ ] Terraform config created

**Tasks:**
1. Create Terraform config: `terraform/s3_backup.tf`
2. Define S3 bucket with versioning
3. Define Lifecycle policy
4. Define Cross-Region Replication
5. Apply terraform
6. Test replication
7. Document in `docs/S3_BACKUP_CONFIG.md`

**Files to Create:**
- `terraform/s3_backup.tf`
- `docs/S3_BACKUP_CONFIG.md`

---

### User Story 0.5.2: Document Recovery Procedures (1h)

**Description:**  
Create comprehensive disaster recovery documentation.

**Framework Requirement:**
> "Document step-by-step recovery procedures for:  
> - Git repository recovery  
> - Database recovery  
> - Manus session recovery  
> - Full system recovery"

**Acceptance Criteria:**
- [ ] Document created: `docs/DISASTER_RECOVERY_PLAN.md`
- [ ] Step-by-step procedures for each recovery type
- [ ] Contact information for recovery lead
- [ ] RTO/RPO clearly stated
- [ ] Tested procedures (dry run)

**Tasks:**
1. Create `docs/DISASTER_RECOVERY_PLAN.md`
2. Document Git recovery procedure
3. Document database recovery procedure
4. Document Manus session recovery procedure
5. Document full system recovery procedure
6. Add contact information and escalation
7. Perform dry run test

**Files to Create:**
- `docs/DISASTER_RECOVERY_PLAN.md`

---

# Phase 1: Agentic UX Frontend Implementation

**Priority:** 🔴 HIGH  
**Duration:** 20-24 hours  
**Status:** ❌ Not Started  
**Goal:** Build Mission Control interface per Agentic UX vision

**Why High Priority:**
The frontend is the **face of the autonomous agent**. It's not a traditional UI - it's a **Mission Control** that shows:
- What the agent is doing **right now**
- Why it's making decisions
- When it needs human help

**Vision Reference:** תוכנית אב לממשק סוכן אוטונומי

---

## Epic 1.1: Mission Control Dashboard (8-10 hours)

**Vision Reference:** Section 2.1 - Dashboard Screen

### User Story 1.1.1: Implement Visual Hierarchy (3h)

**Description:**  
Create the main dashboard layout with exact visual hierarchy from vision document.

**Vision Requirement:**
```
Layout:
- Sidebar (Left): #001529 dark, 220px width
- Header (Top): #f0f0f0 light, 64px height
- Content (Center): #f5f5f5 gray
- Footer (Bottom): #f5f5f5 gray, 40px height

Proportions:
- Main content: 65% width
- Right sidebar: 35% width
```

**Acceptance Criteria:**
- [ ] Layout matches vision document exactly
- [ ] Colors match: #001529, #f0f0f0, #f5f5f5, #e6f7ff
- [ ] Sidebar 220px width, collapsible
- [ ] Header 64px height
- [ ] Content area 65% / 35% split
- [ ] Responsive (mobile, tablet, desktop)

**Tasks:**
1. Create React app: `npx create-react-app frontend-mission-control`
2. Install dependencies: `antd`, `@ant-design/icons`, `react-router-dom`
3. Create layout component: `src/components/Layout/MissionControlLayout.jsx`
4. Implement sidebar with navigation
5. Implement header with user info
6. Implement content area with 65/35 split
7. Test responsiveness
8. Document in `frontend/README.md`

**Files to Create:**
- `frontend-mission-control/src/components/Layout/MissionControlLayout.jsx`
- `frontend-mission-control/src/components/Layout/Sidebar.jsx`
- `frontend-mission-control/src/components/Layout/Header.jsx`
- `frontend-mission-control/src/components/Layout/ContentArea.jsx`

---

### User Story 1.1.2: Implement KPI Cards (2h)

**Description:**  
Create KPI cards showing real-time clinic statistics.

**Vision Requirement:**
```
KPIs (Statistic Cards):
1. "הכנסות היום" (Today's Revenue) - ₪XX,XXX
2. "תורים שנקבעו היום" (Appointments Scheduled Today) - XX
3. "יתרת לקוחות" (Outstanding Balance) - ₪XX,XXX
4. "זמן טיפול ממוצע" (Average Treatment Time) - XX דקות
```

**Acceptance Criteria:**
- [ ] 4 KPI cards displayed in row
- [ ] Cards use Ant Design `<Statistic>` component
- [ ] Real-time data from Statistics API
- [ ] Auto-refresh every 30 seconds
- [ ] Loading skeleton while fetching
- [ ] Error handling

**Tasks:**
1. Create component: `src/components/Dashboard/KPICards.jsx`
2. Fetch data from `/api/v1/statistics/overview`
3. Display 4 cards with icons
4. Implement auto-refresh (30s interval)
5. Add loading skeleton
6. Add error handling
7. Test with real API

**Files to Create:**
- `frontend-mission-control/src/components/Dashboard/KPICards.jsx`
- `frontend-mission-control/src/services/statisticsService.js`

---

### User Story 1.1.3: Implement Agent Status Panel (3h)

**Description:**  
Create real-time panel showing what Alex agent is doing right now.

**Vision Requirement:**
> "המשתמש לא 'מפעיל' את המערכת - הוא נותן משימה. האייג'נט מבצע באופן אוטונומי."

**Panel Content:**
- Current mission (e.g., "Scheduling appointment for David Cohen")
- Agent status (Thinking, Acting, Waiting for Human)
- Current tool being used (e.g., "Searching Odoo for patient")
- Progress indicator
- Reasoning explanation

**Acceptance Criteria:**
- [ ] Panel displays current agent activity
- [ ] Real-time updates via WebSocket or polling
- [ ] Shows current mission
- [ ] Shows agent status (Thinking/Acting/Waiting)
- [ ] Shows current tool
- [ ] Shows reasoning explanation
- [ ] Progress indicator (0-100%)

**Tasks:**
1. Create component: `src/components/Dashboard/AgentStatusPanel.jsx`
2. Implement WebSocket connection to backend
3. Display agent status in real-time
4. Add progress indicator
5. Add reasoning explanation
6. Style per vision document
7. Test with real agent execution

**Files to Create:**
- `frontend-mission-control/src/components/Dashboard/AgentStatusPanel.jsx`
- `frontend-mission-control/src/services/websocketService.js`

---

### User Story 1.1.4: Implement Urgent Alerts Sidebar (2h)

**Description:**  
Create right sidebar (35%) showing urgent items requiring attention.

**Vision Requirement:**
```
Right Sidebar (35%):
- "דחוף התעוררות" (Urgent Alerts)
  - Emergency escalations
  - Doctor-required cases
  - Unpaid invoices (overdue)
```

**Acceptance Criteria:**
- [ ] Right sidebar 35% width
- [ ] Shows emergency escalations (red)
- [ ] Shows doctor-required cases (orange)
- [ ] Shows unpaid invoices (yellow)
- [ ] Click to view details
- [ ] Auto-refresh every 60 seconds

**Tasks:**
1. Create component: `src/components/Dashboard/UrgentAlertsSidebar.jsx`
2. Fetch data from `/api/v1/doctor/active-escalations`
3. Fetch data from `/api/v1/statistics/unpaid-invoices`
4. Display alerts by urgency (red/orange/yellow)
5. Implement click to view details
6. Add auto-refresh
7. Test with real data

**Files to Create:**
- `frontend-mission-control/src/components/Dashboard/UrgentAlertsSidebar.jsx`

---

## Epic 1.2: Conversation History Screen (4-5 hours)

**Vision Reference:** Section 2.2 - Conversation History Screen

### User Story 1.2.1: Implement Master-Detail Layout (2h)

**Description:**  
Create conversation history screen with master-detail pattern.

**Vision Requirement:**
```
Layout:
- Left (30%): List of conversations
- Right (70%): Selected conversation details
```

**Acceptance Criteria:**
- [ ] Master-detail layout (30/70 split)
- [ ] Left: List of conversations with filters
- [ ] Right: Selected conversation with full history
- [ ] Click conversation to view details
- [ ] Responsive

**Tasks:**
1. Create component: `src/pages/ConversationHistory.jsx`
2. Create component: `src/components/Conversations/ConversationList.jsx`
3. Create component: `src/components/Conversations/ConversationDetail.jsx`
4. Implement master-detail pattern
5. Fetch conversations from API
6. Display conversation history
7. Test with real data

**Files to Create:**
- `frontend-mission-control/src/pages/ConversationHistory.jsx`
- `frontend-mission-control/src/components/Conversations/ConversationList.jsx`
- `frontend-mission-control/src/components/Conversations/ConversationDetail.jsx`

---

### User Story 1.2.2: Implement Conversation Filters (1h)

**Description:**  
Add filters for conversation list (date, status, agent).

**Vision Requirement:**
> "פילטרים: תאריכים, סטטוס (פתוח/סגור), אייג'נט"

**Acceptance Criteria:**
- [ ] Date range filter (dropdown)
- [ ] Status filter (Open/Closed)
- [ ] Agent filter (Alex)
- [ ] Filters applied in real-time
- [ ] Clear filters button

**Tasks:**
1. Create component: `src/components/Conversations/ConversationFilters.jsx`
2. Implement date range picker
3. Implement status dropdown
4. Implement agent dropdown
5. Apply filters to conversation list
6. Add clear filters button
7. Test filtering

**Files to Create:**
- `frontend-mission-control/src/components/Conversations/ConversationFilters.jsx`

---

### User Story 1.2.3: Implement Human Handoff Interface (2h)

**Description:**  
Add interface for human to take over conversation.

**Vision Requirement:**
> "ממשק התעוררות: אפשר לאנוש להשתלט על השיחה"

**Acceptance Criteria:**
- [ ] "Take Over" button in conversation detail
- [ ] Human can send messages directly
- [ ] Agent pauses when human takes over
- [ ] "Resume Agent" button to hand back
- [ ] Visual indicator when human is in control

**Tasks:**
1. Create component: `src/components/Conversations/HumanHandoff.jsx`
2. Add "Take Over" button
3. Implement human message input
4. Pause agent when human takes over
5. Add "Resume Agent" button
6. Add visual indicator
7. Test handoff flow

**Files to Create:**
- `frontend-mission-control/src/components/Conversations/HumanHandoff.jsx`

---

## Epic 1.3: Performance Analytics Screen (4-5 hours)

**Vision Reference:** Section 2.3 - Performance Analytics Screen

### User Story 1.3.1: Implement Analytics Dashboard (3h)

**Description:**  
Create analytics screen with charts and graphs.

**Vision Requirement:**
```
Charts:
1. "משפך המרות" (Conversion Funnel) - Bar chart
2. "נפח שיחות לפי ערוץ ומוצא" (Conversations by Channel) - Stacked bar
3. "נושאים נפוצים בשאלות" (Common Topics) - RAG chart
```

**Acceptance Criteria:**
- [ ] 3 charts displayed
- [ ] Conversion funnel chart (Bar)
- [ ] Conversations by channel chart (Stacked bar)
- [ ] Common topics chart (RAG - Red/Amber/Green)
- [ ] Data from Statistics API
- [ ] Interactive (hover, click)

**Tasks:**
1. Create component: `src/pages/PerformanceAnalytics.jsx`
2. Install chart library: `recharts` or `chart.js`
3. Create conversion funnel chart
4. Create conversations by channel chart
5. Create common topics RAG chart
6. Fetch data from Statistics API
7. Test with real data

**Files to Create:**
- `frontend-mission-control/src/pages/PerformanceAnalytics.jsx`
- `frontend-mission-control/src/components/Analytics/ConversionFunnelChart.jsx`
- `frontend-mission-control/src/components/Analytics/ChannelChart.jsx`
- `frontend-mission-control/src/components/Analytics/TopicsChart.jsx`

---

### User Story 1.3.2: Implement Date Range Selector (1h)

**Description:**  
Add date range selector for analytics.

**Vision Requirement:**
> "פילטרים: תאריכים"

**Acceptance Criteria:**
- [ ] Date range picker (start/end date)
- [ ] Preset ranges (Today, Last 7 days, Last 30 days, Custom)
- [ ] Charts update when date range changes
- [ ] Default: Last 30 days

**Tasks:**
1. Create component: `src/components/Analytics/DateRangeSelector.jsx`
2. Implement date range picker (Ant Design DatePicker.RangePicker)
3. Add preset ranges
4. Update charts when range changes
5. Test with different ranges

**Files to Create:**
- `frontend-mission-control/src/components/Analytics/DateRangeSelector.jsx`

---

## Epic 1.4: Knowledge Management Screen (4-5 hours)

**Vision Reference:** Section 2.4 - Knowledge Management Screen

### User Story 1.4.1: Implement Knowledge Base Tree (2h)

**Description:**  
Create tree view for knowledge base navigation.

**Vision Requirement:**
> "עמודת ניווט (קבצים): Tree structure of knowledge base"

**Acceptance Criteria:**
- [ ] Left sidebar (25%) with tree view
- [ ] Tree shows knowledge base structure
- [ ] Click file to view/edit
- [ ] Drag & drop to reorganize
- [ ] Add/delete files

**Tasks:**
1. Create component: `src/pages/KnowledgeManagement.jsx`
2. Create component: `src/components/Knowledge/KnowledgeTree.jsx`
3. Fetch knowledge base structure from API
4. Implement tree view (Ant Design Tree)
5. Implement click to view
6. Implement drag & drop
7. Test with real knowledge base

**Files to Create:**
- `frontend-mission-control/src/pages/KnowledgeManagement.jsx`
- `frontend-mission-control/src/components/Knowledge/KnowledgeTree.jsx`

---

### User Story 1.4.2: Implement Knowledge Editor (2h)

**Description:**  
Create editor for knowledge base content.

**Vision Requirement:**
> "עריכת מרכזי (משתמש לפי סוג הקובץ): YAML editor, Editable table, Collapsible sections"

**Acceptance Criteria:**
- [ ] Right content area (75%) with editor
- [ ] YAML editor for `.yaml` files
- [ ] Table editor for `.csv` files
- [ ] Markdown editor for `.md` files
- [ ] Save changes button
- [ ] Syntax highlighting

**Tasks:**
1. Create component: `src/components/Knowledge/KnowledgeEditor.jsx`
2. Install editor library: `@monaco-editor/react`
3. Implement YAML editor
4. Implement table editor (Ant Design EditableTable)
5. Implement Markdown editor
6. Add save functionality
7. Test with different file types

**Files to Create:**
- `frontend-mission-control/src/components/Knowledge/KnowledgeEditor.jsx`
- `frontend-mission-control/src/components/Knowledge/YAMLEditor.jsx`
- `frontend-mission-control/src/components/Knowledge/TableEditor.jsx`
- `frontend-mission-control/src/components/Knowledge/MarkdownEditor.jsx`

---

## Epic 1.5: User Flow Implementation (2-3 hours)

**Vision Reference:** Section 3 - User Flow

### User Story 1.5.1: Implement Navigation Flow (2h)

**Description:**  
Implement navigation between screens per user flow diagram.

**Vision Requirement:**
```
Flow:
A (מסך ראשי) --> B (סקירה כללית)
B --> C (היסטוריית שיחות)
B --> D (שיחות אחרונות)
B --> E (ניווט צדדי)

C --> F (מסך היסטוריית שיחות)
F --> G (תצוגת תקציר)
F --> H (משתמש צ'אט להשתלטות)

E --> J (מסך ניתוח ביצועים)
E --> K (מסך ניהול ידע)
```

**Acceptance Criteria:**
- [ ] React Router configured
- [ ] Navigation between all screens
- [ ] Breadcrumbs showing current location
- [ ] Back button functionality
- [ ] Deep linking support

**Tasks:**
1. Configure React Router: `src/App.jsx`
2. Define routes for all screens
3. Implement navigation in sidebar
4. Add breadcrumbs component
5. Test navigation flow
6. Test deep linking

**Files to Modify:**
- `frontend-mission-control/src/App.jsx`

**Files to Create:**
- `frontend-mission-control/src/components/Layout/Breadcrumbs.jsx`

---

### User Story 1.5.2: Implement Real-time Updates (1h)

**Description:**  
Implement WebSocket for real-time updates across all screens.

**Vision Requirement:**
> "Real-time updates for agent status, conversations, alerts"

**Acceptance Criteria:**
- [ ] WebSocket connection established on app load
- [ ] Real-time updates for agent status
- [ ] Real-time updates for conversations
- [ ] Real-time updates for alerts
- [ ] Reconnection logic if connection drops

**Tasks:**
1. Create WebSocket service: `src/services/websocketService.js`
2. Establish connection on app load
3. Subscribe to agent status updates
4. Subscribe to conversation updates
5. Subscribe to alert updates
6. Implement reconnection logic
7. Test with real backend

**Files to Create:**
- `frontend-mission-control/src/services/websocketService.js`

---

# Phase 2: Real Odoo Integration

**Priority:** 🟡 MEDIUM  
**Duration:** 4-6 hours  
**Status:** ⚠️ 50% (Mock completed with 1500 patients)  
**Goal:** Replace mock Odoo with real Odoo connection

**Why Medium Priority:**
Mock Odoo is **good enough for MVP demo**, but for production we need real Odoo integration.

---

## Epic 2.1: Odoo Docker Setup (2-3 hours)

### User Story 2.1.1: Fix Docker Compose & Launch Odoo (2h)

**Description:**  
Fix iptables issue and launch Odoo in Docker.

**Current Issue:**
```
Error: iptables v1.8.7 (legacy): can't initialize iptables table `nat'
```

**Acceptance Criteria:**
- [ ] Docker Compose fixed
- [ ] Odoo running on http://localhost:8069
- [ ] PostgreSQL running
- [ ] Can access Odoo web interface
- [ ] Database initialized

**Tasks:**
1. Fix iptables issue (update Docker or use host network)
2. Update `docker-compose.yml` if needed
3. Run: `docker-compose up -d`
4. Wait for Odoo to initialize (5-10 minutes)
5. Access http://localhost:8069
6. Create database: `dental_clinic_db`
7. Test login

**Files to Modify:**
- `docker-compose.yml` (if needed)

---

### User Story 2.1.2: Install Odoo Dental Module (1h)

**Description:**  
Install dental clinic module in Odoo.

**Acceptance Criteria:**
- [ ] Dental module installed
- [ ] Patient management enabled
- [ ] Appointment scheduling enabled
- [ ] Invoice management enabled
- [ ] Treatment records enabled

**Tasks:**
1. Search for Odoo dental module (Odoo Apps Store)
2. Install module: `dental_management` or similar
3. Configure module settings
4. Test patient creation
5. Test appointment creation
6. Document in `docs/ODOO_SETUP.md`

**Files to Create:**
- `docs/ODOO_SETUP.md`

---

## Epic 2.2: Odoo Client Integration (2-3 hours)

### User Story 2.2.1: Update Odoo Client for Real Connection (2h)

**Description:**  
Update `OdooClient` to connect to real Odoo instance.

**Current State:**
- `MockOdooClient` with 1500 patients
- `OdooClient` exists but not fully tested

**Acceptance Criteria:**
- [ ] `OdooClient` connects to Odoo via XML-RPC
- [ ] Can search patients
- [ ] Can create appointments
- [ ] Can create invoices
- [ ] Can retrieve treatment records
- [ ] All tests passing

**Tasks:**
1. Update `backend/app/integrations/odoo_client.py`
2. Test connection to Odoo
3. Test patient search
4. Test appointment creation
5. Test invoice creation
6. Update tests
7. Document in `docs/ODOO_INTEGRATION.md`

**Files to Modify:**
- `backend/app/integrations/odoo_client.py`
- `backend/tests/test_odoo_integration.py`

**Files to Create:**
- `docs/ODOO_INTEGRATION.md`

---

### User Story 2.2.2: Migrate Mock Data to Odoo (1h)

**Description:**  
Migrate 1500 mock patients to real Odoo.

**Acceptance Criteria:**
- [ ] Script `scripts/migrate_mock_to_odoo.py` created
- [ ] Script migrates all 1500 patients
- [ ] Script migrates appointments
- [ ] Script migrates invoices
- [ ] Script migrates treatment records
- [ ] Verified in Odoo UI

**Tasks:**
1. Create `scripts/migrate_mock_to_odoo.py`
2. Load mock data from JSON files
3. Create patients in Odoo
4. Create appointments in Odoo
5. Create invoices in Odoo
6. Create treatment records in Odoo
7. Verify migration

**Files to Create:**
- `scripts/migrate_mock_to_odoo.py`

---

# Phase 3: Production Deployment

**Priority:** 🟢 LOW (after Phase 0, 1, 2)  
**Duration:** 6-8 hours  
**Status:** ❌ Not Started  
**Goal:** Deploy to production with monitoring

---

## Epic 3.1: Deploy Backend (3-4 hours)

### User Story 3.1.1: Deploy to AWS EC2 or Heroku (3h)

**Description:**  
Deploy backend to production server.

**Acceptance Criteria:**
- [ ] Backend deployed to AWS EC2 or Heroku
- [ ] HTTPS enabled
- [ ] Environment variables configured
- [ ] Database connected
- [ ] Redis connected
- [ ] Neo4j connected
- [ ] Health check endpoint working

**Tasks:**
1. Choose deployment platform (AWS EC2 or Heroku)
2. Create deployment script
3. Configure environment variables
4. Deploy backend
5. Test API endpoints
6. Configure HTTPS
7. Document in `docs/DEPLOYMENT.md`

**Files to Create:**
- `scripts/deploy_backend.sh`
- `docs/DEPLOYMENT.md`

---

### User Story 3.1.2: Set Up Monitoring (1h)

**Description:**  
Set up monitoring and logging.

**Acceptance Criteria:**
- [ ] Logging configured (CloudWatch or Papertrail)
- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring (New Relic or Datadog)
- [ ] Alerts configured

**Tasks:**
1. Set up CloudWatch or Papertrail
2. Set up Sentry for error tracking
3. Set up New Relic or Datadog
4. Configure alerts
5. Test monitoring

**Files to Modify:**
- `backend/app/core/config.py`

---

## Epic 3.2: Deploy Frontend (2-3 hours)

### User Story 3.2.1: Deploy to Vercel or Netlify (2h)

**Description:**  
Deploy frontend to production.

**Acceptance Criteria:**
- [ ] Frontend deployed to Vercel or Netlify
- [ ] HTTPS enabled
- [ ] Environment variables configured
- [ ] Connected to backend API
- [ ] Custom domain configured

**Tasks:**
1. Choose deployment platform (Vercel or Netlify)
2. Create deployment script
3. Configure environment variables
4. Deploy frontend
5. Test all pages
6. Configure custom domain
7. Document in `docs/FRONTEND_DEPLOYMENT.md`

**Files to Create:**
- `frontend-mission-control/vercel.json` or `netlify.toml`
- `docs/FRONTEND_DEPLOYMENT.md`

---

## Epic 3.3: Set Up CI/CD (1-2 hours)

### User Story 3.3.1: Configure GitHub Actions for CI/CD (1h)

**Description:**  
Set up continuous integration and deployment.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow for backend tests
- [ ] GitHub Actions workflow for frontend tests
- [ ] Auto-deploy on push to main
- [ ] Rollback capability

**Tasks:**
1. Create `.github/workflows/ci.yml`
2. Add backend tests
3. Add frontend tests
4. Add auto-deploy step
5. Test CI/CD pipeline

**Files to Create:**
- `.github/workflows/ci.yml`

---

# Summary & Next Steps

## ✅ What's Completed (42%)

1. **Backend Core (85%)**
   - Alex unified agent
   - Escalation detection fixed
   - Telegram bot integration
   - Mock Odoo with 1500 patients
   - Statistics API
   - Doctor escalation endpoints

2. **Data (100%)**
   - 1,500 realistic patients
   - 12,124 appointments
   - 5,089 invoices (₪7.8M revenue)
   - 5,089 treatment records

3. **Git & Commits (30%)**
   - Repository structure
   - Partial Manus-Session-ID protocol

---

## 🎯 Priority Order (Recommended)

### Option A: Framework-First (Recommended for Production)
1. **Phase 0:** Holistic Framework (18-22h) - CRITICAL
2. **Phase 1:** Agentic UX Frontend (20-24h) - HIGH
3. **Phase 2:** Real Odoo Integration (4-6h) - MEDIUM
4. **Phase 3:** Production Deployment (6-8h) - LOW

**Total:** 48-60 hours

### Option B: Demo-First (Recommended for Quick MVP)
1. **Phase 1:** Agentic UX Frontend (20-24h) - HIGH
2. **Phase 2:** Real Odoo Integration (4-6h) - MEDIUM
3. **Phase 0:** Holistic Framework (18-22h) - CRITICAL
4. **Phase 3:** Production Deployment (6-8h) - LOW

**Total:** 48-60 hours

---

## 📊 Estimated Timeline

**With 1 developer full-time (8 hours/day):**
- Phase 0: 2.5-3 days
- Phase 1: 2.5-3 days
- Phase 2: 0.5-1 day
- Phase 3: 1 day

**Total:** 6-8 days (1.5-2 weeks)

---

## 🚀 Immediate Next Steps

1. **Decide priority:** Framework-First or Demo-First?
2. **Start Phase 0 or Phase 1** (depending on decision)
3. **Set up development environment** (if needed)
4. **Review and approve this plan**

---

## 📝 Notes

- This plan integrates **Agentic UX vision** with **Holistic Framework**
- All completed work from V17.1 is reflected
- Timeline is realistic (48-60 hours remaining)
- Framework is critical for production, but can be done after demo
- Frontend is the "face" of the autonomous agent

---

**End of Work Plan V18.0**
