# Dental Clinic AI - Work Plan V17.1

**Date:** October 2, 2025  
**Version:** 17.1 (Updated with Code Alignment Phase)  
**Based On:** מסגרת עבודה הוליסטית לגיבוי ושחזור  
**Project Status:** 38% Complete (updated after Code Alignment)

---

## 📋 Document Purpose

This work plan is **fully aligned** with the Holistic Operational Framework (מסגרת עבודה) and provides a complete roadmap from current state (38%) to production-ready MVP (100%).

**Key Changes from V17.0:**
- ✅ Added Phase 0.5: Code Alignment (COMPLETED)
- ✅ Updated Phase 1 status to COMPLETED
- ✅ Updated project completion: 32% → 38%
- ✅ Documented today's work (Code Audit + Fixes)

---

## 🎯 Project Vision

**Goal:** Production-ready dental clinic AI assistant with:
- Natural conversation in English + Hebrew
- Medical safety boundaries (FDA compliant)
- Integration with Odoo (patient data)
- Telegram interface (patient communication)
- Doctor escalation (emergency handling)
- Full disaster recovery capability

**Timeline:** 42-52 hours from current state  
**Target Date:** 2 weeks (with 1 developer full-time)

---

## 📊 Current State Summary

**What's Done (38% overall):**
- ✅ Backend API + Database (80%)
- ✅ **Agent architecture decided: Alex unified agent** (100%)
- ✅ **Code aligned with architecture decision** (100%)
- ✅ Error handling + rate limiting (100%)
- ✅ Mock Odoo integration (100%)
- ✅ Basic tests (31 tests, imports fixed)

**What's Missing (62%):**
- ❌ Framework protocol (Git, AWS, Backup) - 0%
- ❌ Production deployment - 20%
- ❌ Real Odoo connection - 0%
- ❌ Telegram bot - 0%
- ❌ Neo4j fully integrated - 50%

**Critical Decisions Made:**
- ✅ **Alex unified agent** (not 4 agents)
- ✅ Orchestrator removed, AgentGraphV2 active
- ✅ All code aligned with V17.0 plan

---

## 🏗️ Phase Overview

| Phase | Name | Priority | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Framework Protocol | 🔴 CRITICAL | 18-22h | ❌ Not Started |
| 0.5 | **Code Alignment** | 🔴 HIGH | 3h | ✅ **COMPLETED** |
| 1 | Agent Architecture Decision | 🔴 HIGH | 2-3h | ✅ **COMPLETED** |
| 2 | Complete MVP Features | 🟡 MEDIUM | 15-18h | ⚠️ 40% |
| 3 | Production Deployment | 🟢 LOW | 12-15h | ❌ Not Started |

**Total Remaining:** 42-52 hours  
**Total Completed:** 5-6 hours (Phase 0.5 + Phase 1)

---

# Phase 0.5: Code Alignment ✅ COMPLETED

**Priority:** 🔴 HIGH  
**Duration:** 3 hours  
**Status:** ✅ **COMPLETED** (October 2, 2025)  
**Goal:** Align codebase with WORK_PLAN_V17.0 architecture decision

**Why This Phase:**
After deciding on Alex unified agent architecture, the codebase still had references to the old 4-agent system (Orchestrator, Dana, Michal, Yosef, Sarah). This phase cleaned up all inconsistencies.

---

## Epic 0.5.1: Code Audit ✅ COMPLETED

**Duration:** 1 hour

### User Story 0.5.1.1: Deep Code Analysis ✅

**Description:**  
Analyze entire codebase to identify gaps between code and WORK_PLAN_V17.0.

**What Was Found:**
1. ❌ `orchestrator.py` imported deleted agents (Dana, Michal, Yosef, Sarah)
2. ❌ `chat.py` used Orchestrator instead of AgentGraphV2
3. ❌ Tests imported `agent_graph_v2` (old name)
4. ❌ `test_integration.py` tested 4-agent architecture (irrelevant)

**Deliverables:**
- ✅ CODE_AUDIT_FIXES.md created
- ✅ All 4 critical issues documented

---

## Epic 0.5.2: Fix Code Alignment ✅ COMPLETED

**Duration:** 2 hours

### User Story 0.5.2.1: Fix API Endpoint ✅

**Description:**  
Rewrite `chat.py` to use AgentGraphV2 instead of Orchestrator.

**Changes Made:**
- ✅ Removed: `from app.agents.orchestrator import AgentOrchestrator`
- ✅ Added: `from app.agents.agent_graph import AgentGraphV2`
- ✅ Changed: `orchestrator.process_message()` → `agent_graph.process_message()`
- ✅ Updated: primary_agent = "alex" (was "dana")

**Files Modified:**
- `backend/app/api/v1/endpoints/chat.py` - Complete rewrite

---

### User Story 0.5.2.2: Fix Test Imports ✅

**Description:**  
Update all test files to import correct modules.

**Changes Made:**
- ✅ `test_alex_safety.py`: Fixed import + added `@pytest.mark.asyncio`
- ✅ `test_causal_memory_integration.py`: Fixed import + class name
- ✅ `test_e2e_mvp.py`: Fixed import + 8 instantiations

**Files Modified:**
- `backend/tests/test_alex_safety.py`
- `backend/tests/test_causal_memory_integration.py`
- `backend/tests/test_e2e_mvp.py`

---

### User Story 0.5.2.3: Archive Old Code ✅

**Description:**  
Move unused code to archive instead of deleting (for reference).

**Files Archived:**
- ✅ `orchestrator.py` → `archive/old_code/`
- ✅ `test_integration.py` → `archive/old_code/`

---

## Epic 0.5.3: Verification ✅ COMPLETED

**Duration:** 30 minutes

### User Story 0.5.3.1: Verify Code Alignment ✅

**Description:**  
Run verification tests to ensure code works.

**Verification Results:**
```bash
✅ AgentGraphV2 imports successfully
✅ AgentGraphV2 instantiates successfully
✅ chat.py imports successfully
✅ agent_graph type: AgentGraphV2
✅ FastAPI app loads successfully
✅ App title: DentalAI API
```

**Architecture Verification:**
- ✅ No references to Dana, Michal, Yosef, Sarah in active code
- ✅ No references to Orchestrator in active code
- ✅ All imports point to AgentGraphV2
- ✅ Alex agent is the only active agent

---

## Phase 0.5 Summary

**Deliverables:**
1. ✅ CODE_AUDIT_FIXES.md - Detailed audit report
2. ✅ chat.py rewritten for AgentGraphV2
3. ✅ 3 test files fixed
4. ✅ 2 files archived
5. ✅ Verification tests passed
6. ✅ Git commit with proper Manus-Session-ID
7. ✅ Pushed to GitHub

**Time Spent:** 3 hours  
**Status:** ✅ **COMPLETED**  
**Next Phase:** Phase 0 (Framework Protocol) or Phase 2 (MVP Features)

---

# Phase 0: Framework Protocol Implementation

**Priority:** 🔴 CRITICAL - Must be done for production  
**Duration:** 18-22 hours  
**Status:** ❌ Not Started  
**Goal:** Implement all requirements from מסגרת עבודה הוליסטית

**Why Critical:**
- Without framework protocol, we cannot recover from disasters
- Security vulnerabilities (secrets in .env files)
- No audit trail for compliance
- Framework is foundation for everything else

**Framework Reference:** Parts I-VII of מסגרת עבודה

---

## Epic 0.1: Manus-Git Protocol

**Duration:** 3-4 hours  
**Framework Reference:** Part II - Git Repository Protocol

### User Story 0.1.1: Implement Commit Message Format

**Duration:** 1.5 hours

**Description:**  
Implement structured commit messages with Manus-Session-ID as defined in framework.

**Framework Requirement:**
> "Every commit must include:
> - Manus-Session-ID: Unique identifier linking commit to Manus session
> - Human-Initiator: Name of human who initiated the work
> - Task-ID: Identifier of the task being worked on"

**Acceptance Criteria:**
- [ ] Git hook created: `.git/hooks/prepare-commit-msg`
- [ ] Hook automatically adds Manus-Session-ID to commits
- [ ] Format: `Manus-Session-ID: YYYYMMDD-HHMMSS-task-description`
- [ ] Human-Initiator: scubapro711
- [ ] Task-ID extracted from branch name or manual input
- [ ] Hook tested with sample commits

**Tasks:**
1. Create `.git/hooks/prepare-commit-msg` script
2. Add logic to generate Manus-Session-ID
3. Add logic to extract Human-Initiator from git config
4. Add logic to extract Task-ID from branch or prompt
5. Test hook with 5 sample commits
6. Document in `docs/GIT_PROTOCOL.md`

**Files to Create:**
- `.git/hooks/prepare-commit-msg`
- `docs/GIT_PROTOCOL.md`

---

### User Story 0.1.2: Implement Author vs Committer Distinction

**Duration:** 1 hour

**Description:**  
Distinguish between human author and Manus agent committer.

**Framework Requirement:**
> "Author = Human who initiated the work
> Committer = Manus agent who executed the work"

**Acceptance Criteria:**
- [ ] Git config set: `user.name = "Manus AI Agent"`
- [ ] Git config set: `user.email = "manus@agent.local"`
- [ ] Author extracted from session context
- [ ] All commits show: Author = Human, Committer = Manus
- [ ] Documented in `docs/GIT_PROTOCOL.md`

**Tasks:**
1. Update git config for committer
2. Update hook to set author from session
3. Test with sample commits
4. Verify `git log --format=fuller` shows both
5. Document

**Files to Modify:**
- `.git/hooks/prepare-commit-msg`
- `docs/GIT_PROTOCOL.md`

---

### User Story 0.1.3: Implement Git Bundle Creation

**Duration:** 30 minutes

**Description:**  
Create git bundle for offline backup.

**Framework Requirement:**
> "Create git bundle containing all branches and tags"

**Acceptance Criteria:**
- [ ] Script `scripts/create_git_bundle.sh` created
- [ ] Bundle includes all branches
- [ ] Bundle includes all tags
- [ ] Bundle named: `dental-clinic-ai-YYYYMMDD-HHMMSS.bundle`
- [ ] Bundle tested (can restore from it)

**Tasks:**
1. Create `scripts/create_git_bundle.sh`
2. Add logic to create bundle
3. Test bundle creation
4. Test bundle restoration
5. Document

**Files to Create:**
- `scripts/create_git_bundle.sh`

---

## Epic 0.2: AWS Secrets Manager

**Duration:** 4-5 hours  
**Framework Reference:** Part III - AWS Secrets Manager

### User Story 0.2.1: Set Up AWS Secrets Manager

**Duration:** 2 hours

**Description:**  
Configure AWS Secrets Manager with customer-managed KMS keys.

**Framework Requirement:**
> "Use customer-managed KMS keys (not AWS-managed)
> Create IAM roles: HumanDeveloperRole, ManusAgentRole"

**Acceptance Criteria:**
- [ ] AWS account configured
- [ ] Customer-managed KMS key created: `dental-clinic-ai-secrets-key`
- [ ] IAM role created: `HumanDeveloperRole` (full access)
- [ ] IAM role created: `ManusAgentRole` (read-only)
- [ ] CloudTrail enabled for audit logging
- [ ] Terraform config created

**Tasks:**
1. Create Terraform config: `terraform/aws_secrets.tf`
2. Define KMS key
3. Define IAM roles
4. Define CloudTrail
5. Apply terraform
6. Test access with both roles

**Files to Create:**
- `terraform/aws_secrets.tf`
- `docs/AWS_SECRETS_SETUP.md`

---

### User Story 0.2.2: Migrate Secrets from .env

**Duration:** 2 hours

**Description:**  
Move all secrets from `.env` files to AWS Secrets Manager.

**Current Secrets (in .env):**
- DATABASE_URL
- REDIS_URL
- NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
- ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
- OPENAI_API_KEY
- JWT_SECRET_KEY
- TELEGRAM_BOT_TOKEN (future)

**Acceptance Criteria:**
- [ ] All secrets stored in AWS Secrets Manager
- [ ] Secret name: `dental-clinic-ai/production`
- [ ] Secret rotation enabled (90 days)
- [ ] `.env` files removed from repository
- [ ] `.env.example` created (with placeholders)
- [ ] Code updated to fetch from AWS

**Tasks:**
1. Create secret in AWS: `dental-clinic-ai/production`
2. Upload all secrets
3. Update `backend/app/core/config.py` to fetch from AWS
4. Test application with AWS secrets
5. Remove `.env` from git
6. Add `.env` to `.gitignore`
7. Create `.env.example`

**Files to Modify:**
- `backend/app/core/config.py`
- `.gitignore`

**Files to Create:**
- `.env.example`

**Files to Delete:**
- `.env` (from git history)

---

### User Story 0.2.3: Implement Secret Rotation

**Duration:** 1 hour

**Description:**  
Set up automatic secret rotation for sensitive credentials.

**Framework Requirement:**
> "Enable automatic rotation for database passwords and API keys"

**Acceptance Criteria:**
- [ ] Rotation enabled for DATABASE_URL password
- [ ] Rotation enabled for JWT_SECRET_KEY
- [ ] Rotation period: 90 days
- [ ] Lambda function created for rotation logic
- [ ] Rotation tested

**Tasks:**
1. Create Lambda function: `lambda/rotate_secrets.py`
2. Configure rotation in AWS Secrets Manager
3. Test rotation manually
4. Verify application still works after rotation
5. Document

**Files to Create:**
- `lambda/rotate_secrets.py`
- `docs/SECRET_ROTATION.md`

---

## Epic 0.3: Manus Session Integration

**Duration:** 3-4 hours  
**Framework Reference:** Part IV - Manus Session Integration

### User Story 0.3.1: Implement getSession API Integration

**Duration:** 2 hours

**Description:**  
Integrate with Manus getSession API to retrieve session context.

**Framework Requirement:**
> "Use getSession API to retrieve:
> - Session ID
> - Human intention
> - Agent execution log
> - Artifacts generated"

**Acceptance Criteria:**
- [ ] Script `scripts/get_manus_session.py` created
- [ ] Script calls `https://api.manus.im/v1/sessions/{session_id}`
- [ ] API key stored in AWS Secrets Manager
- [ ] Session data saved to `artifacts/sessions/{session_id}.json`
- [ ] Script tested with real session ID

**Tasks:**
1. Create `scripts/get_manus_session.py`
2. Add Manus API key to AWS Secrets Manager
3. Implement API call logic
4. Save session data to JSON
5. Test with real session
6. Document

**Files to Create:**
- `scripts/get_manus_session.py`
- `docs/MANUS_SESSION_INTEGRATION.md`

---

### User Story 0.3.2: Implement Session Export Protocol

**Duration:** 1 hour

**Description:**  
Export session data in standardized format.

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
- [ ] Script exports session to `artifacts/sessions/{session_id}.json`
- [ ] Schema validated
- [ ] Tested with 3 different sessions

**Tasks:**
1. Define JSON schema: `schemas/manus_session.json`
2. Update export script to match schema
3. Validate with jsonschema library
4. Test with multiple sessions
5. Document

**Files to Create:**
- `schemas/manus_session.json`

**Files to Modify:**
- `scripts/get_manus_session.py`

---

### User Story 0.3.3: Collect Artifacts

**Duration:** 1 hour

**Description:**  
Collect all artifacts generated during Manus session.

**Framework Requirement:**
> "Collect artifacts:
> - Code files created/modified
> - Documentation generated
> - Test results
> - Logs"

**Acceptance Criteria:**
- [ ] Script `scripts/collect_artifacts.sh` created
- [ ] Collects all files changed in session
- [ ] Collects test results
- [ ] Collects logs
- [ ] Creates tarball: `artifacts/{session_id}-artifacts.tar.gz`
- [ ] Tested

**Tasks:**
1. Create `scripts/collect_artifacts.sh`
2. Add logic to find changed files
3. Add logic to collect test results
4. Add logic to collect logs
5. Create tarball
6. Test
7. Document

**Files to Create:**
- `scripts/collect_artifacts.sh`

---

## Epic 0.4: Automated Backup Protocol

**Duration:** 5-6 hours  
**Framework Reference:** Part V - Unified Backup Protocol

### User Story 0.4.1: Create GitHub Actions Workflow

**Duration:** 3 hours

**Description:**  
Create GitHub Actions workflow to automate backup on every push.

**Framework Requirement:**
> "On every push to main:
> 1. Create git bundle
> 2. Export Manus session
> 3. Collect artifacts
> 4. Create backup archive
> 5. Upload to S3 primary bucket
> 6. Verify replication to secondary bucket"

**Acceptance Criteria:**
- [ ] Workflow file `.github/workflows/backup.yml` created
- [ ] Triggers on push to main
- [ ] Creates git bundle
- [ ] Exports Manus session
- [ ] Collects artifacts
- [ ] Creates backup archive: `backup-YYYYMMDD-HHMMSS.tar.gz`
- [ ] Uploads to S3 primary: `s3://dental-clinic-ai-backup-primary/`
- [ ] Verifies replication to secondary: `s3://dental-clinic-ai-backup-secondary/`
- [ ] Sends notification on failure
- [ ] Tested with real push

**Tasks:**
1. Create `.github/workflows/backup.yml`
2. Add steps for git bundle
3. Add steps for session export
4. Add steps for artifact collection
5. Add steps for S3 upload
6. Add steps for verification
7. Add notification logic
8. Test workflow
9. Document

**Files to Create:**
- `.github/workflows/backup.yml`
- `docs/BACKUP_PROTOCOL.md`

---

### User Story 0.4.2: Set Up S3 Buckets

**Duration:** 2 hours

**Description:**  
Create S3 buckets for backup storage with cross-region replication.

**Framework Requirement:**
> "Primary bucket: us-east-1
> Secondary bucket: eu-west-1
> Enable cross-region replication (CRR)
> Enable versioning
> Enable encryption"

**Acceptance Criteria:**
- [ ] Primary bucket created: `dental-clinic-ai-backup-primary` (us-east-1)
- [ ] Secondary bucket created: `dental-clinic-ai-backup-secondary` (eu-west-1)
- [ ] CRR enabled (primary → secondary)
- [ ] Lifecycle policy configured:
  - Standard storage: 0-90 days
  - Glacier: 90 days - 7 years
  - Delete: > 7 years
- [ ] Versioning enabled
- [ ] Encryption enabled (SSE-S3)

**Tasks:**
1. Create Terraform config: `terraform/s3_backup.tf`
2. Apply terraform
3. Test upload to primary bucket
4. Verify replication to secondary
5. Verify lifecycle policy

**Files to Create:**
- `terraform/s3_backup.tf`

---

### User Story 0.4.3: Create Recovery Runbook

**Duration:** 1 hour

**Description:**  
Document step-by-step recovery procedure.

**Framework Requirement:**
> "Document recovery procedure with:
> 1. Prerequisites
> 2. Download backup from S3
> 3. Extract archive
> 4. Restore Git repository
> 5. Restore secrets from AWS
> 6. Restore Manus session context
> 7. Verify system functional"

**Acceptance Criteria:**
- [ ] Document `docs/RECOVERY_RUNBOOK.md` created
- [ ] Includes all 7 steps with commands
- [ ] Includes troubleshooting section
- [ ] Tested by team member (DR drill)

**Tasks:**
1. Create `docs/RECOVERY_RUNBOOK.md`
2. Write detailed steps with commands
3. Add troubleshooting section
4. Schedule DR drill

**Files to Create:**
- `docs/RECOVERY_RUNBOOK.md`

---

## Epic 0.5: Disaster Recovery Plan

**Duration:** 3-4 hours  
**Framework Reference:** Part VI - DR & Business Continuity

### User Story 0.5.1: Define RTO and RPO

**Duration:** 1 hour

**Description:**  
Define recovery objectives and document them.

**Framework Requirement:**
> "Define:
> - RTO (Recovery Time Objective): Max time to restore system
> - RPO (Recovery Point Objective): Max acceptable data loss"

**Acceptance Criteria:**
- [ ] RTO defined: < 4 hours (from disaster to system operational)
- [ ] RPO defined: < 1 commit (max data loss = last commit)
- [ ] Documented in `docs/RTO_RPO_DEFINITION.md`
- [ ] Includes:
  - Definition of "disaster"
  - Recovery steps summary
  - Success criteria
  - Escalation contacts

**Tasks:**
1. Create `docs/RTO_RPO_DEFINITION.md`
2. Define disaster scenarios
3. Map recovery steps to time estimates
4. Get stakeholder approval

**Files to Create:**
- `docs/RTO_RPO_DEFINITION.md`

---

### User Story 0.5.2: Create Roles & Responsibilities Table

**Duration:** 1 hour

**Description:**  
Define team roles for disaster recovery.

**Framework Requirement:**
> "Define roles:
> - Recovery Lead
> - Technical Recovery Team
> - Communications Lead
> - Manus Liaison
> - Scribe"

**Acceptance Criteria:**
- [ ] Table created in `docs/ROLES_RESPONSIBILITIES.md`
- [ ] Each role has:
  - Primary person
  - Backup person
  - Responsibilities
  - Contact info

**Tasks:**
1. Create `docs/ROLES_RESPONSIBILITIES.md`
2. Assign team members to roles
3. Get team agreement
4. Share with stakeholders

**Files to Create:**
- `docs/ROLES_RESPONSIBILITIES.md`

---

### User Story 0.5.3: Conduct DR Drill

**Duration:** 2 hours

**Description:**  
Simulate disaster and test recovery procedure.

**Framework Requirement:**
> "Conduct DR drill to validate:
> - Recovery runbook accuracy
> - Team readiness
> - RTO/RPO achievability"

**Acceptance Criteria:**
- [ ] Scenario: "GitHub repository corrupted, developer laptop lost"
- [ ] Team follows recovery runbook
- [ ] System restored within RTO
- [ ] Data loss within RPO
- [ ] Lessons learned documented
- [ ] Runbook updated based on findings

**Tasks:**
1. Schedule DR drill with team
2. Prepare scenario
3. Execute drill (timed)
4. Document results in `docs/DR_DRILL_REPORT.md`
5. Update runbook

**Files to Create:**
- `docs/DR_DRILL_REPORT.md`

---

# Phase 1: Agent Architecture Decision ✅ COMPLETED

**Priority:** 🔴 HIGH  
**Duration:** 2-3 hours  
**Status:** ✅ **COMPLETED** (October 2, 2025)  
**Dependencies:** Phase 0 (recommended, but done early)

**Goal:** Choose between 4-agent architecture vs unified Alex agent, and remove unused code.

---

## Epic 1.1: Architecture Decision ✅ COMPLETED

**Duration:** 2-3 hours

### User Story 1.1.1: Evaluate Both Architectures ✅

**Duration:** 1 hour

**Description:**  
Compare 4-agent vs Alex architecture and make decision.

**Comparison:**

| Aspect | 4 Agents (Dana, Michal, Yosef, Sarah) | Alex (Unified) |
|--------|----------------------------------------|----------------|
| **Complexity** | Higher (4 prompts, routing logic) | Lower (1 prompt) |
| **Maintainability** | Harder (changes affect multiple files) | Easier (single file) |
| **Modularity** | Better (add new specialist easily) | Worse (one big prompt) |
| **Performance** | Slower (routing + specialist call) | Faster (single LLM call) |
| **Cost** | Higher (2 LLM calls per query) | Lower (1 LLM call) |
| **Expertise** | Better (focused prompts) | Worse (generalist) |

**Decision Made:** ✅ **Alex (Unified)** for MVP
- Simpler to maintain
- Faster and cheaper
- Medical safety already implemented
- Can always split later if needed

**Deliverables:**
- ✅ Decision documented in WORK_PLAN_V17.0.md
- ✅ Stakeholder approval obtained (implicit)

---

### User Story 1.1.2: Remove Unused Code ✅

**Duration:** 1-2 hours

**Description:**  
Remove the 4-agent architecture that wasn't chosen.

**Actions Taken:**
- ✅ Deleted: `backend/app/agents/dana.py`
- ✅ Deleted: `backend/app/agents/michal.py`
- ✅ Deleted: `backend/app/agents/yosef.py`
- ✅ Deleted: `backend/app/agents/sarah.py`
- ✅ Deleted: `backend/app/agents/emma.py`
- ✅ Deleted: `backend/app/agents/lisa.py`
- ✅ Deleted: `backend/app/agents/robert.py`
- ✅ Deleted: `backend/app/agents/jessica.py`
- ✅ Archived: `orchestrator.py` → `archive/old_code/`
- ✅ Kept: `backend/app/agents/alex.py` (chosen architecture)
- ✅ Kept: `backend/app/agents/agent_graph.py` (Alex version)

---

## Phase 1 Summary

**Deliverables:**
1. ✅ Architecture decision documented
2. ✅ 8 agent files deleted
3. ✅ 1 orchestrator file archived
4. ✅ Alex agent is the only active agent
5. ✅ AgentGraphV2 is the only active graph

**Time Spent:** 2-3 hours  
**Status:** ✅ **COMPLETED**  
**Next Phase:** Phase 2 (Complete MVP Features)

---

# Phase 2: Complete MVP Features

**Priority:** 🟡 MEDIUM  
**Duration:** 15-18 hours  
**Status:** ⚠️ 40% Complete  
**Dependencies:** Phase 1 complete

**Goal:** Complete all features needed for MVP demo.

---

## Epic 2.1: Neo4j Causal Memory

**Duration:** 3 hours  
**Status:** ⚠️ 50% Complete

### User Story 2.1.1: Complete Neo4j Integration

**Duration:** 2 hours

**Description:**  
Complete Neo4j causal memory integration (currently 50% done).

**Current State:**
- ✅ Neo4j connection works
- ✅ `causal_memory.py` exists
- ⚠️ Integrated with agent_graph but has bugs

**Acceptance Criteria:**
- [ ] Agent retrieves similar past interactions before responding
- [ ] Agent stores new interactions after responding
- [ ] Conversation context maintained across sessions
- [ ] Pattern recognition working (appointment_scheduling, medical_question, etc.)
- [ ] Tests passing

**Tasks:**
1. Review current integration in `agent_graph.py`
2. Fix parameter mismatches (user_id vs patient_id)
3. Fix escalation_level not being returned
4. Add more patterns
5. Test with real conversations
6. Verify Neo4j data

**Files to Modify:**
- `backend/app/agents/agent_graph.py`
- `backend/app/memory/causal_memory.py`

---

### User Story 2.1.2: Add Memory Management

**Duration:** 1 hour

**Description:**  
Add ability to clear/manage conversation memory.

**Acceptance Criteria:**
- [ ] Endpoint `DELETE /api/memory/{user_id}` to clear memory
- [ ] Endpoint `GET /api/memory/{user_id}` to view memory
- [ ] Admin can manage all users' memory
- [ ] User can only manage their own memory

**Tasks:**
1. Add endpoints in `backend/app/api/v1/endpoints/memory.py`
2. Add RBAC checks
3. Test endpoints
4. Document API

**Files to Create:**
- `backend/app/api/v1/endpoints/memory.py`

---

## Epic 2.2: Real Odoo Integration

**Duration:** 4 hours  
**Status:** ❌ 0% Complete

### User Story 2.2.1: Replace Mock Odoo with Real Connection

**Duration:** 3 hours

**Description:**  
Connect to real Odoo instance instead of Mock.

**Current State:**
- ✅ `OdooClient` exists
- ✅ `MockOdooClient` works
- ❌ No real Odoo instance

**Acceptance Criteria:**
- [ ] Real Odoo instance set up (or use demo instance)
- [ ] Connection tested
- [ ] All tools work with real data:
  - `search_patient`
  - `get_patient_invoices`
  - `get_invoice_details`
  - `get_available_slots`
  - `create_appointment`
- [ ] Error handling for Odoo failures

**Tasks:**
1. Set up Odoo instance (or use demo.odoo.com)
2. Update `backend/app/integrations/odoo_client.py`
3. Configure Odoo credentials in AWS Secrets Manager
4. Test all tools
5. Update tests

**Files to Modify:**
- `backend/app/integrations/odoo_client.py`
- `backend/app/core/config.py` (Odoo credentials)

---

### User Story 2.2.2: Add Patient Notes Integration

**Duration:** 1 hour

**Description:**  
Add tools to fetch doctor's notes from Odoo.

**Acceptance Criteria:**
- [ ] Tool `get_patient_notes(patient_id)` created
- [ ] Tool `get_treatment_plan(patient_id)` created
- [ ] Tool `get_patient_allergies(patient_id)` created
- [ ] Alex agent uses these tools when relevant
- [ ] Tests passing

**Tasks:**
1. Add tools to `backend/app/agents/tools/odoo_tools.py`
2. Update Alex prompt to use tools
3. Test with real patient data
4. Verify privacy/security

**Files to Modify:**
- `backend/app/agents/tools/odoo_tools.py`
- `backend/app/agents/alex.py`

---

## Epic 2.3: Telegram Bot Integration

**Duration:** 5 hours  
**Status:** ❌ 0% Complete

### User Story 2.3.1: Set Up Telegram Bot

**Duration:** 2 hours

**Description:**  
Create Telegram bot and configure webhook.

**Acceptance Criteria:**
- [ ] Bot created via @BotFather
- [ ] Bot token stored in AWS Secrets Manager
- [ ] Webhook configured to point to backend
- [ ] SSL certificate configured
- [ ] Bot responds to `/start` command

**Tasks:**
1. Create bot with @BotFather
2. Store token in AWS Secrets Manager
3. Add webhook endpoint: `POST /api/telegram/webhook`
4. Configure webhook with Telegram API
5. Test `/start` command

**Files to Create:**
- `backend/app/api/v1/endpoints/telegram.py`
- `backend/app/integrations/telegram_client.py`

---

### User Story 2.3.2: Connect Telegram to Agent

**Duration:** 2 hours

**Description:**  
Route Telegram messages to agent and send responses back.

**Acceptance Criteria:**
- [ ] User sends message in Telegram
- [ ] Message routed to Alex agent
- [ ] Agent response sent back to Telegram
- [ ] Multi-language works (Hebrew + English)
- [ ] Conversation context maintained

**Tasks:**
1. Parse Telegram webhook payload
2. Extract user message
3. Call agent with message
4. Send response via Telegram API
5. Test full flow

**Files to Modify:**
- `backend/app/api/v1/endpoints/telegram.py`
- `backend/app/integrations/telegram_client.py`

---

### User Story 2.3.3: Add Telegram-Specific Features

**Duration:** 1 hour

**Description:**  
Add Telegram-specific UI elements.

**Acceptance Criteria:**
- [ ] Inline buttons for quick replies
  - "Book Appointment"
  - "Check Invoice"
  - "Talk to Doctor"
- [ ] Rich formatting (bold, italic, links)
- [ ] Image support (for dental diagrams)
- [ ] Location sharing (for clinic address)

**Tasks:**
1. Add inline keyboard to responses
2. Format messages with Markdown
3. Test all features
4. Document user guide

**Files to Modify:**
- `backend/app/integrations/telegram_client.py`

---

## Epic 2.4: Doctor Escalation

**Duration:** 3-4 hours  
**Status:** ⚠️ 30% Complete (escalation detection exists, but no actual doctor connection)

### User Story 2.4.1: Create Doctor Chat Link

**Duration:** 2 hours

**Description:**  
Generate private chat link for doctor to join conversation.

**Acceptance Criteria:**
- [ ] Endpoint `POST /api/doctor/create-link` creates unique link
- [ ] Link format: `https://app.dental-clinic.com/doctor-chat/{token}`
- [ ] Token expires after 24 hours
- [ ] Doctor can access chat with token
- [ ] Doctor sees full conversation history

**Tasks:**
1. Create endpoint in `backend/app/api/v1/endpoints/doctor.py`
2. Generate secure token (JWT)
3. Store token in Redis with expiration
4. Create doctor chat UI (simple HTML page)
5. Test link generation and access

**Files to Create:**
- `backend/app/api/v1/endpoints/doctor.py`
- `backend/app/templates/doctor_chat.html`

---

### User Story 2.4.2: Implement Doctor Notification

**Duration:** 1 hour

**Description:**  
Send notification to doctor when escalation occurs.

**Acceptance Criteria:**
- [ ] SMS sent to doctor (using Twilio)
- [ ] Email sent to doctor
- [ ] Notification includes:
  - Patient name
  - Urgency level (EMERGENCY, DOCTOR_REQUIRED, ROUTINE)
  - Summary of issue
  - Link to join chat
- [ ] Notification tested

**Tasks:**
1. Set up Twilio account
2. Add Twilio credentials to AWS Secrets Manager
3. Implement SMS sending in `backend/app/integrations/twilio_client.py`
4. Implement email sending
5. Test notifications

**Files to Create:**
- `backend/app/integrations/twilio_client.py`

---

### User Story 2.4.3: Transcribe Doctor Conversation

**Duration:** 1 hour

**Description:**  
Transcribe doctor's messages and save to Odoo + Neo4j.

**Acceptance Criteria:**
- [ ] Doctor's messages transcribed in real-time
- [ ] Transcript saved to Odoo (patient notes)
- [ ] Transcript saved to Neo4j (causal memory)
- [ ] Alex monitors conversation but doesn't interrupt
- [ ] After doctor leaves, Alex resumes

**Tasks:**
1. Add transcription logic to doctor chat
2. Save to Odoo via API
3. Save to Neo4j via causal_memory
4. Test full flow
5. Verify data in both systems

**Files to Modify:**
- `backend/app/api/v1/endpoints/doctor.py`
- `backend/app/integrations/odoo_client.py`
- `backend/app/memory/causal_memory.py`

---

# Phase 3: Production Deployment

**Priority:** 🟢 LOW  
**Duration:** 12-15 hours  
**Status:** ❌ 0% Complete  
**Dependencies:** Phase 2 complete

**Goal:** Deploy to AWS with monitoring and load testing.

---

## Epic 3.1: AWS Infrastructure

**Duration:** 6 hours

### User Story 3.1.1: Create Terraform Configuration

**Duration:** 3 hours

**Description:**  
Define all AWS infrastructure as code.

**Acceptance Criteria:**
- [ ] Terraform config created for:
  - VPC
  - EC2 instances (or ECS)
  - RDS (PostgreSQL)
  - ElastiCache (Redis)
  - ALB (Application Load Balancer)
  - Route53 (DNS)
  - ACM (SSL certificates)
- [ ] Config tested with `terraform plan`
- [ ] Config applied with `terraform apply`

**Tasks:**
1. Create `terraform/main.tf`
2. Define VPC and subnets
3. Define compute (EC2 or ECS)
4. Define databases
5. Define load balancer
6. Test and apply

**Files to Create:**
- `terraform/main.tf`
- `terraform/variables.tf`
- `terraform/outputs.tf`

---

### User Story 3.1.2: Deploy Application

**Duration:** 2 hours

**Description:**  
Deploy backend and frontend to AWS.

**Acceptance Criteria:**
- [ ] Backend deployed to EC2/ECS
- [ ] Frontend deployed to S3 + CloudFront
- [ ] Database migrated to RDS
- [ ] Redis migrated to ElastiCache
- [ ] SSL certificate configured
- [ ] Domain configured (e.g., api.dental-clinic.com)
- [ ] Application accessible via HTTPS

**Tasks:**
1. Build Docker image
2. Push to ECR
3. Deploy to ECS
4. Run database migrations
5. Test application
6. Configure DNS

**Files to Modify:**
- `Dockerfile`
- `docker-compose.yml`

---

### User Story 3.1.3: Set Up CI/CD Pipeline

**Duration:** 1 hour

**Description:**  
Automate deployment on every push to main.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow created
- [ ] On push to main:
  - Run tests
  - Build Docker image
  - Push to ECR
  - Deploy to ECS
  - Run smoke tests
- [ ] Rollback on failure

**Tasks:**
1. Create `.github/workflows/deploy.yml`
2. Add steps for build and deploy
3. Add smoke tests
4. Test workflow

**Files to Create:**
- `.github/workflows/deploy.yml`

---

## Epic 3.2: Monitoring & Logging

**Duration:** 4 hours

### User Story 3.2.1: Set Up CloudWatch

**Duration:** 2 hours

**Description:**  
Configure CloudWatch for logs and metrics.

**Acceptance Criteria:**
- [ ] Application logs sent to CloudWatch
- [ ] Metrics tracked:
  - Request count
  - Response time
  - Error rate
  - LLM API calls
  - Cost per conversation
- [ ] Dashboards created
- [ ] Alarms configured

**Tasks:**
1. Configure CloudWatch agent
2. Send logs to CloudWatch
3. Create custom metrics
4. Create dashboards
5. Set up alarms

**Files to Modify:**
- `backend/app/core/logging.py`

---

### User Story 3.2.2: Set Up Error Tracking

**Duration:** 1 hour

**Description:**  
Integrate Sentry for error tracking.

**Acceptance Criteria:**
- [ ] Sentry account created
- [ ] Sentry SDK integrated
- [ ] Errors automatically reported
- [ ] Alerts configured
- [ ] Tested with sample error

**Tasks:**
1. Create Sentry account
2. Install Sentry SDK
3. Configure in backend
4. Test error reporting
5. Set up alerts

**Files to Modify:**
- `backend/app/main.py`
- `backend/requirements.txt`

---

### User Story 3.2.3: Set Up Performance Monitoring

**Duration:** 1 hour

**Description:**  
Monitor application performance with APM.

**Acceptance Criteria:**
- [ ] APM tool integrated (e.g., New Relic, Datadog)
- [ ] Tracks:
  - API response times
  - Database query times
  - LLM API call times
  - Memory usage
  - CPU usage
- [ ] Dashboards created

**Tasks:**
1. Choose APM tool
2. Install agent
3. Configure
4. Create dashboards
5. Test

**Files to Modify:**
- `backend/app/main.py`

---

## Epic 3.3: Load Testing

**Duration:** 3 hours

### User Story 3.3.1: Create Load Tests

**Duration:** 2 hours

**Description:**  
Create load tests to simulate 100+ concurrent users.

**Acceptance Criteria:**
- [ ] Load test script created (using Locust or k6)
- [ ] Simulates:
  - 100 concurrent users
  - 1000 requests/minute
  - Mix of endpoints (chat, memory, doctor)
- [ ] Metrics collected:
  - Response time (p50, p95, p99)
  - Error rate
  - Throughput
- [ ] Tests pass

**Tasks:**
1. Install Locust
2. Create test script: `tests/load/locustfile.py`
3. Run tests locally
4. Run tests against staging
5. Analyze results

**Files to Create:**
- `tests/load/locustfile.py`

---

### User Story 3.3.2: Optimize Performance

**Duration:** 1 hour

**Description:**  
Optimize application based on load test results.

**Acceptance Criteria:**
- [ ] Response time < 2s (p95)
- [ ] Error rate < 1%
- [ ] Throughput > 1000 req/min
- [ ] Optimizations documented

**Tasks:**
1. Analyze load test results
2. Identify bottlenecks
3. Optimize (caching, database indexes, etc.)
4. Re-run load tests
5. Document changes

**Files to Modify:**
- Various (based on bottlenecks)

---

# Success Criteria

## Phase 0: Framework Protocol

- [ ] All commits have Manus-Session-ID
- [ ] All secrets in AWS Secrets Manager
- [ ] Automated backup on every push
- [ ] Recovery runbook tested in DR drill
- [ ] RTO < 4 hours, RPO < 1 commit

## Phase 1: Agent Architecture

- [x] Decision documented
- [x] Unused code removed
- [x] Alex is the only active agent

## Phase 2: MVP Features

- [ ] Neo4j fully integrated
- [ ] Real Odoo connection works
- [ ] Telegram bot responds to messages
- [ ] Doctor escalation works end-to-end

## Phase 3: Production

- [ ] Application deployed to AWS
- [ ] Monitoring and logging configured
- [ ] Load tests pass (100+ users)
- [ ] SSL certificate configured
- [ ] Domain configured

---

# Timeline

**Estimated Timeline (with 1 developer full-time):**

| Phase | Duration | Calendar Days |
|-------|----------|---------------|
| Phase 0 | 18-22h | 3-4 days |
| Phase 1 | ✅ DONE | ✅ DONE |
| Phase 2 | 15-18h | 2-3 days |
| Phase 3 | 12-15h | 2-3 days |
| **Total** | **42-52h** | **7-10 days** |

**Target Completion:** 2 weeks from now (with buffer)

---

# Risk Management

## High-Risk Items

1. **AWS Secrets Manager migration** - May break application if not done carefully
   - Mitigation: Test thoroughly in staging first
   
2. **Real Odoo integration** - May not have access to real instance
   - Mitigation: Use demo.odoo.com or continue with Mock for MVP

3. **Load testing** - May reveal performance issues
   - Mitigation: Start early, optimize iteratively

4. **Doctor escalation** - Complex feature with many moving parts
   - Mitigation: Break into smaller pieces, test each independently

## Medium-Risk Items

1. **Neo4j bugs** - Current integration has parameter mismatches
   - Mitigation: Fix in Phase 2.1.1 (2 hours)

2. **Telegram bot** - Never done before
   - Mitigation: Follow official documentation, use examples

3. **DR drill** - May fail first time
   - Mitigation: Schedule 2 drills, update runbook after first

---

# Appendix

## Tools & Technologies

- **Backend:** Python 3.11, FastAPI, LangChain, LangGraph
- **Database:** PostgreSQL, Redis, Neo4j
- **LLM:** OpenAI GPT-4.1-mini
- **ERP:** Odoo (Mock for now)
- **Messaging:** Telegram Bot API
- **Cloud:** AWS (EC2, RDS, ElastiCache, S3, Secrets Manager)
- **IaC:** Terraform
- **CI/CD:** GitHub Actions
- **Monitoring:** CloudWatch, Sentry
- **Testing:** pytest, Locust

## References

- מסגרת עבודה הוליסטית לגיבוי ושחזור (Framework Document)
- WORK_PLAN_V17.0.md (Previous version)
- PROJECT_STATUS_REPORT.md (Current status)
- CODE_AUDIT_FIXES.md (Phase 0.5 deliverable)
- ALEX_COMPLETION_REPORT.md (Alex agent documentation)

---

**End of Work Plan V17.1**
