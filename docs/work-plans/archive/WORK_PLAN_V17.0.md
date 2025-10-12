# 🚀 Dental Clinic AI - Work Plan V17.0

**Date:** October 2, 2025  
**Version:** 17.0 (Framework-Aligned & Comprehensive)  
**Based On:** מסגרת עבודה הוליסטית לגיבוי ושחזור  
**Project Status:** 32% Complete (see PROJECT_STATUS_REPORT.md)

---

## 📋 Document Purpose

This work plan is **fully aligned** with the Holistic Operational Framework and provides a complete roadmap from current state (32%) to production-ready MVP (100%).

**Key Changes from V16.0:**
- ✅ Framework protocol prioritized (Phase 0)
- ✅ Clear decision point: 4 agents vs Alex
- ✅ Realistic time estimates based on actual work completed
- ✅ All tasks mapped to framework requirements
- ✅ Success criteria defined for each phase

---

## 🎯 Project Vision

**Goal:** Production-ready dental clinic AI assistant with:
- Natural conversation in English + Hebrew
- Medical safety boundaries (FDA compliant)
- Integration with Odoo (patient data)
- Telegram interface (patient communication)
- Doctor escalation (emergency handling)
- Full disaster recovery capability

**Timeline:** 45-55 hours from current state  
**Target Date:** 2 weeks (with 1 developer full-time)

---

## 📊 Current State Summary

**What's Done (32% overall):**
- ✅ Backend API + Database (80%)
- ✅ Agent architecture (85%)
  - Option A: 4 agents (Dana, Michal, Yosef, Sarah)
  - Option B: 1 agent (Alex)
- ✅ Error handling + rate limiting
- ✅ Mock Odoo integration
- ✅ Basic tests (31 tests)

**What's Missing (68%):**
- ❌ Framework protocol (Git, AWS, Backup) - 0%
- ❌ Production deployment - 20%
- ❌ Real Odoo connection - 0%
- ❌ Telegram bot - 0%
- ❌ Neo4j fully integrated - 50%

**Critical Decision Needed:**
- ❓ Choose agent architecture: 4 agents vs Alex

---

## 🏗️ Phase Overview

| Phase | Name | Priority | Duration | Dependencies |
|-------|------|----------|----------|--------------|
| 0 | Framework Protocol | 🔴 CRITICAL | 18-22h | None |
| 1 | Agent Architecture Decision | 🔴 HIGH | 2-3h | Phase 0 |
| 2 | Complete MVP Features | 🟡 MEDIUM | 15-18h | Phase 1 |
| 3 | Production Deployment | 🟢 LOW | 12-15h | Phase 2 |

**Total:** 47-58 hours

---

# Phase 0: Framework Protocol Implementation

**Priority:** 🔴 CRITICAL - Must be done first  
**Duration:** 18-22 hours  
**Goal:** Implement all requirements from מסגרת עבודה הוליסטית

**Why First?**
- Without framework protocol, we cannot recover from disasters
- Security vulnerabilities (secrets in .env files)
- No audit trail for compliance
- Framework is foundation for everything else

---

## Epic 0.1: Manus-Git Protocol

**Duration:** 3-4 hours  
**Framework Reference:** Part II

### User Story 0.1.1: Implement Commit Message Format

**Duration:** 1.5 hours

**Description:**  
Implement structured commit messages with Manus-Session-ID as defined in framework.

**Acceptance Criteria:**
- [ ] All commits follow format:
  ```
  <Type>(<Scope>): <Subject>
  
  <Body>
  
  Manus-Session-ID: <session_id>
  Manus-Task-ID: <task_id>
  Human-Initiator: <username>
  ```
- [ ] Git hooks validate commit format
- [ ] Documentation updated with examples

**Tasks:**
1. Create `.git/hooks/commit-msg` script to validate format
2. Create template in `.gitmessage`
3. Configure git: `git config commit.template .gitmessage`
4. Document in `docs/GIT_PROTOCOL.md`

**Files to Create:**
- `.git/hooks/commit-msg`
- `.gitmessage`
- `docs/GIT_PROTOCOL.md`

---

### User Story 0.1.2: Author vs Committer Distinction

**Duration:** 1 hour

**Description:**  
Configure Git to distinguish between human initiator (Author) and AI agent (Committer).

**Acceptance Criteria:**
- [ ] Environment variables set:
  - `GIT_AUTHOR_NAME` = Human username
  - `GIT_AUTHOR_EMAIL` = Human email
  - `GIT_COMMITTER_NAME` = "Manus AI Agent"
  - `GIT_COMMITTER_EMAIL` = "agent@manus.im"
- [ ] Script to set these automatically
- [ ] Verified in `git log --format=fuller`

**Tasks:**
1. Create `scripts/setup_git_identity.sh`
2. Add to manus.im sandbox initialization
3. Test with sample commit
4. Document in `docs/GIT_PROTOCOL.md`

**Files to Create:**
- `scripts/setup_git_identity.sh`

---

### User Story 0.1.3: Artifact Versioning

**Duration:** 1.5 hours

**Description:**  
Embed commit hash in all build artifacts for traceability.

**Acceptance Criteria:**
- [ ] Build script embeds commit hash
- [ ] Artifacts include metadata file with:
  - Commit hash
  - Build timestamp
  - Manus-Session-ID
  - Environment info
- [ ] Metadata accessible at runtime

**Tasks:**
1. Update `backend/Dockerfile` to include `git rev-parse HEAD`
2. Create `scripts/embed_version.py`
3. Add version endpoint: `GET /api/version`
4. Test version appears in logs

**Files to Modify:**
- `backend/Dockerfile`
- `backend/app/main.py` (add /version endpoint)

**Files to Create:**
- `scripts/embed_version.py`

---

## Epic 0.2: AWS Secrets Manager

**Duration:** 4-5 hours  
**Framework Reference:** Part III

### User Story 0.2.1: Set Up AWS Secrets Manager

**Duration:** 2 hours

**Description:**  
Configure AWS Secrets Manager with Customer-Managed KMS keys.

**Acceptance Criteria:**
- [ ] KMS key created with alias `dental-clinic-secrets`
- [ ] Key policy includes `kms:ViaService` condition
- [ ] Secrets Manager configured to use KMS key
- [ ] All secrets migrated from `.env`:
  - `prod/openai-api-key`
  - `prod/neo4j-password`
  - `prod/odoo-credentials`
  - `prod/telegram-bot-token`
  - `prod/jwt-secret`
- [ ] CloudTrail enabled for audit

**Tasks:**
1. Create Terraform config: `terraform/secrets_manager.tf`
2. Create KMS key with policy
3. Migrate secrets from `.env`
4. Enable CloudTrail logging
5. Test secret retrieval

**Files to Create:**
- `terraform/secrets_manager.tf`
- `terraform/kms.tf`
- `terraform/cloudtrail.tf`

---

### User Story 0.2.2: Create IAM Roles

**Duration:** 1.5 hours

**Description:**  
Create IAM roles for humans and AI agent with least privilege.

**Acceptance Criteria:**
- [ ] `HumanDeveloperRole` created:
  - Can list secrets
  - Cannot read secret values (requires MFA)
  - Can trigger "break glass" procedure
- [ ] `ManusAgentRole` created:
  - Can read specific secrets only
  - Limited to `secretsmanager:GetSecretValue`
  - Resource ARN restricted
- [ ] Roles documented in `docs/IAM_ROLES.md`

**Tasks:**
1. Create Terraform config: `terraform/iam_roles.tf`
2. Define policies for each role
3. Test role assumption
4. Document in `docs/IAM_ROLES.md`

**Files to Create:**
- `terraform/iam_roles.tf`
- `docs/IAM_ROLES.md`

---

### User Story 0.2.3: Update Application to Use Secrets Manager

**Duration:** 1.5 hours

**Description:**  
Modify application code to fetch secrets from AWS instead of .env files.

**Acceptance Criteria:**
- [ ] `backend/app/core/config.py` updated to use boto3
- [ ] Secrets fetched at startup
- [ ] Fallback to .env for local development
- [ ] `.env.example` updated (no real secrets)
- [ ] `.env` added to `.gitignore` (if not already)

**Tasks:**
1. Install boto3: `pip install boto3`
2. Update `backend/app/core/config.py`
3. Add `get_secret()` function
4. Test locally with AWS credentials
5. Update documentation

**Files to Modify:**
- `backend/requirements.txt`
- `backend/app/core/config.py`
- `.env.example`

---

## Epic 0.3: Manus Session Integration

**Duration:** 3-4 hours  
**Framework Reference:** Part IV

### User Story 0.3.1: Implement Session Export Script

**Duration:** 2 hours

**Description:**  
Create Python script to export Manus session via getSession API.

**Acceptance Criteria:**
- [ ] Script `scripts/export_manus_session.py` created
- [ ] Accepts `--session-id` parameter
- [ ] Fetches session from `https://api.manus.im/api/chat/getSession`
- [ ] Saves to `<session-id>.json`
- [ ] Extracts artifacts (files, images, reports)
- [ ] Creates directory structure:
  ```
  manus_session_data/
    ├── session.json
    └── artifacts/
        ├── file1.py
        ├── image1.png
        └── report1.md
  ```

**Tasks:**
1. Create `scripts/export_manus_session.py`
2. Implement API call with authentication
3. Parse events array for artifacts
4. Download artifacts from manus.im
5. Test with real session ID

**Files to Create:**
- `scripts/export_manus_session.py`
- `scripts/requirements.txt` (requests library)

---

### User Story 0.3.2: Digital Links API Integration

**Duration:** 1.5 hours

**Description:**  
Add endpoint to generate shareable links to Manus sessions.

**Acceptance Criteria:**
- [ ] Endpoint `POST /api/sessions/link` created
- [ ] Generates link: `https://manus.im/session/{session_id}`
- [ ] Link stored in database with metadata
- [ ] Link can be shared with team members
- [ ] Frontend button "View in Manus" added

**Tasks:**
1. Add endpoint in `backend/app/api/v1/endpoints/sessions.py`
2. Store links in database
3. Add frontend button (optional for MVP)
4. Test link generation

**Files to Create:**
- `backend/app/api/v1/endpoints/sessions.py`
- `backend/app/models/session_link.py`

---

## Epic 0.4: Automated Backup Protocol

**Duration:** 5-6 hours  
**Framework Reference:** Part V

### User Story 0.4.1: Create GitHub Actions Workflow

**Duration:** 3 hours

**Description:**  
Implement automated backup workflow as specified in framework.

**Acceptance Criteria:**
- [ ] Workflow `.github/workflows/backup.yml` created
- [ ] Triggers on push to `main` branch
- [ ] Steps:
  1. Checkout with full history
  2. Extract Manus-Session-ID from commit
  3. Create git bundle
  4. Export Manus session
  5. Package artifacts
  6. Upload to S3
- [ ] Workflow tested and passing

**Tasks:**
1. Create `.github/workflows/backup.yml`
2. Configure AWS credentials as GitHub secrets
3. Test workflow with dummy commit
4. Verify S3 upload successful

**Files to Create:**
- `.github/workflows/backup.yml`

**GitHub Secrets to Add:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BACKUP_BUCKET`
- `MANUS_API_TOKEN`

---

### User Story 0.4.2: Set Up S3 Backup Infrastructure

**Duration:** 2 hours

**Description:**  
Create S3 buckets with Cross-Region Replication and lifecycle policies.

**Acceptance Criteria:**
- [ ] Primary bucket: `dental-clinic-backups-us-east-1`
- [ ] Secondary bucket: `dental-clinic-backups-us-west-2`
- [ ] CRR enabled (primary → secondary)
- [ ] Lifecycle policy:
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

**Duration:** 1.5 hours

**Description:**  
Document step-by-step recovery procedure.

**Acceptance Criteria:**
- [ ] Document `docs/RECOVERY_RUNBOOK.md` created
- [ ] Includes:
  1. Prerequisites (AWS CLI, Git, GPG)
  2. Download backup from S3
  3. Extract archive
  4. Restore Git repository
  5. Restore secrets from AWS
  6. Restore Manus session context
  7. Verify system functional
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
**Framework Reference:** Part VI

### User Story 0.5.1: Define RTO and RPO

**Duration:** 1 hour

**Description:**  
Define recovery objectives and document them.

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

**Acceptance Criteria:**
- [ ] Table created in `docs/ROLES_RESPONSIBILITIES.md`
- [ ] Roles defined:
  - Recovery Lead
  - Technical Recovery Team
  - Communications Lead
  - Manus Liaison
  - Scribe
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

# Phase 1: Agent Architecture Decision

**Priority:** 🔴 HIGH  
**Duration:** 2-3 hours  
**Dependencies:** Phase 0 complete

**Goal:** Choose between 4-agent architecture vs unified Alex agent, and remove unused code.

---

## Epic 1.1: Architecture Decision

**Duration:** 2-3 hours

### User Story 1.1.1: Evaluate Both Architectures

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

**Recommendation:** **Alex (Unified)** for MVP
- Simpler to maintain
- Faster and cheaper
- Medical safety already implemented
- Can always split later if needed

**Acceptance Criteria:**
- [ ] Decision documented in `docs/ARCHITECTURE_DECISION.md`
- [ ] Stakeholder approval obtained

**Tasks:**
1. Review both implementations
2. Run performance comparison
3. Document decision
4. Get approval

**Files to Create:**
- `docs/ARCHITECTURE_DECISION.md`

---

### User Story 1.1.2: Remove Unused Code

**Duration:** 1-2 hours

**Description:**  
Remove the architecture that wasn't chosen.

**If Alex is chosen:**
- [ ] Delete files:
  - `backend/app/agents/dana.py`
  - `backend/app/agents/michal.py`
  - `backend/app/agents/yosef.py`
  - `backend/app/agents/sarah.py`
  - `backend/app/agents/emma.py`
  - `backend/app/agents/lisa.py`
  - `backend/app/agents/robert.py`
  - `backend/app/agents/jessica.py`
  - `backend/app/agents/agent_graph.py`
- [ ] Rename `agent_graph_v2.py` → `agent_graph.py`
- [ ] Update imports in `main.py`
- [ ] Delete old tests
- [ ] Update documentation

**If 4 Agents are chosen:**
- [ ] Delete files:
  - `backend/app/agents/alex.py`
  - `backend/app/agents/agent_graph_v2.py`
  - `backend/app/agents/emma.py`
  - `backend/app/agents/lisa.py`
  - `backend/app/agents/robert.py`
  - `backend/app/agents/jessica.py`
- [ ] Keep Dana, Michal, Yosef, Sarah
- [ ] Update documentation

**Tasks:**
1. Delete unused files
2. Update imports
3. Run all tests
4. Commit with proper Manus-Session-ID

---

# Phase 2: Complete MVP Features

**Priority:** 🟡 MEDIUM  
**Duration:** 15-18 hours  
**Dependencies:** Phase 1 complete

**Goal:** Complete all features needed for MVP demo.

---

## Epic 2.1: Neo4j Causal Memory Integration

**Duration:** 3 hours

### User Story 2.1.1: Full Integration with Agent

**Duration:** 2 hours

**Description:**  
Complete Neo4j causal memory integration (currently 50% done).

**Current State:**
- ✅ Neo4j connection works
- ✅ `causal_memory.py` exists
- ⚠️ Not fully integrated with agent_graph

**Acceptance Criteria:**
- [ ] Agent retrieves similar past interactions before responding
- [ ] Agent stores new interactions after responding
- [ ] Conversation context maintained across sessions
- [ ] Pattern recognition working (appointment_scheduling, medical_question, etc.)
- [ ] Tests passing

**Tasks:**
1. Review current integration in `agent_graph_v2.py`
2. Fix any remaining bugs
3. Add more patterns
4. Test with real conversations
5. Verify Neo4j data

**Files to Modify:**
- `backend/app/agents/agent_graph_v2.py` (or agent_graph.py after Phase 1)
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
- `backend/app/agents/alex.py` (if Alex is chosen)

---

## Epic 2.3: Telegram Bot Integration

**Duration:** 5 hours

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

## Epic 2.4: Doctor Escalation System

**Duration:** 4 hours

### User Story 2.4.1: Generate Private Chat Link

**Duration:** 2 hours

**Description:**  
When escalation needed, generate private link for doctor to join chat.

**Acceptance Criteria:**
- [ ] Endpoint `POST /api/escalations` created
- [ ] Generates unique link: `https://clinic.example.com/doctor-chat/{token}`
- [ ] Link valid for 24 hours
- [ ] Doctor can view full conversation history
- [ ] Doctor can reply in chat
- [ ] Patient sees doctor joined

**Tasks:**
1. Create escalation model in database
2. Add endpoint to generate link
3. Create doctor chat UI (simple HTML page)
4. Test full flow

**Files to Create:**
- `backend/app/models/escalation.py`
- `backend/app/api/v1/endpoints/escalations.py`
- `frontend/doctor-chat.html` (simple page)

---

### User Story 2.4.2: Doctor Notifications

**Duration:** 1 hour

**Description:**  
Notify doctor when escalation occurs.

**Acceptance Criteria:**
- [ ] SMS sent to doctor (via Twilio or similar)
- [ ] Email sent to doctor
- [ ] Message includes:
  - Urgency level (EMERGENCY, DOCTOR_REQUIRED, ROUTINE)
  - Patient name
  - Brief summary
  - Private chat link
- [ ] Notification logged

**Tasks:**
1. Integrate Twilio for SMS
2. Configure email (SendGrid or AWS SES)
3. Create notification templates
4. Test notifications

**Files to Create:**
- `backend/app/integrations/notification_service.py`

---

### User Story 2.4.3: Transcription & Storage

**Duration:** 1 hour

**Description:**  
Transcribe doctor-patient conversation and store in Odoo + Neo4j.

**Acceptance Criteria:**
- [ ] All messages transcribed
- [ ] Conversation saved to Odoo (patient record)
- [ ] Conversation saved to Neo4j (causal memory)
- [ ] Searchable for future reference
- [ ] Privacy compliant (HIPAA/GDPR)

**Tasks:**
1. Add transcription logic
2. Save to Odoo via API
3. Save to Neo4j
4. Test retrieval

**Files to Modify:**
- `backend/app/api/v1/endpoints/escalations.py`
- `backend/app/integrations/odoo_client.py`
- `backend/app/memory/causal_memory.py`

---

# Phase 3: Production Deployment

**Priority:** 🟢 LOW  
**Duration:** 12-15 hours  
**Dependencies:** Phase 2 complete

**Goal:** Deploy to AWS and make production-ready.

---

## Epic 3.1: AWS Infrastructure

**Duration:** 6 hours

### User Story 3.1.1: Set Up ECS/Fargate

**Duration:** 3 hours

**Description:**  
Deploy backend to AWS ECS with Fargate.

**Acceptance Criteria:**
- [ ] ECS cluster created
- [ ] Task definition for backend
- [ ] Service running with 2 tasks (HA)
- [ ] Auto-scaling configured (2-10 tasks)
- [ ] Health checks configured
- [ ] Logs sent to CloudWatch

**Tasks:**
1. Create Terraform config: `terraform/ecs.tf`
2. Build and push Docker image to ECR
3. Create task definition
4. Create service
5. Test deployment

**Files to Create:**
- `terraform/ecs.tf`
- `terraform/ecr.tf`

---

### User Story 3.1.2: Set Up Load Balancer

**Duration:** 2 hours

**Description:**  
Configure ALB for backend with SSL.

**Acceptance Criteria:**
- [ ] Application Load Balancer created
- [ ] SSL certificate from ACM
- [ ] HTTPS enabled
- [ ] HTTP → HTTPS redirect
- [ ] Health check endpoint configured
- [ ] Domain name configured (e.g., api.dental-clinic.com)

**Tasks:**
1. Create Terraform config: `terraform/alb.tf`
2. Request SSL certificate from ACM
3. Configure DNS (Route 53)
4. Test HTTPS access

**Files to Create:**
- `terraform/alb.tf`
- `terraform/route53.tf`

---

### User Story 3.1.3: Set Up RDS & ElastiCache

**Duration:** 1.5 hours

**Description:**  
Deploy PostgreSQL (RDS) and Redis (ElastiCache) in production.

**Acceptance Criteria:**
- [ ] RDS PostgreSQL instance created
- [ ] Multi-AZ enabled for HA
- [ ] Automated backups configured
- [ ] ElastiCache Redis cluster created
- [ ] Security groups configured
- [ ] Connection strings in Secrets Manager

**Tasks:**
1. Create Terraform config: `terraform/rds.tf`
2. Create Terraform config: `terraform/elasticache.tf`
3. Run migrations
4. Test connections

**Files to Create:**
- `terraform/rds.tf`
- `terraform/elasticache.tf`

---

## Epic 3.2: Monitoring & Alerting

**Duration:** 4 hours

### User Story 3.2.1: CloudWatch Dashboards

**Duration:** 2 hours

**Description:**  
Create CloudWatch dashboards for monitoring.

**Acceptance Criteria:**
- [ ] Dashboard for backend metrics:
  - Request count
  - Error rate
  - Response time (p50, p95, p99)
  - CPU/Memory usage
- [ ] Dashboard for agent metrics:
  - Conversations per hour
  - Escalations per hour
  - Average response time
- [ ] Dashboard for infrastructure:
  - ECS task count
  - RDS connections
  - Redis hit rate

**Tasks:**
1. Create CloudWatch dashboard
2. Add custom metrics from application
3. Configure refresh interval
4. Share dashboard URL

**Files to Modify:**
- `backend/app/main.py` (add custom metrics)

---

### User Story 3.2.2: Alerts & Notifications

**Duration:** 2 hours

**Description:**  
Configure CloudWatch alarms for critical issues.

**Acceptance Criteria:**
- [ ] Alarm for high error rate (> 5%)
- [ ] Alarm for slow response time (> 2s p95)
- [ ] Alarm for escalations (> 10/hour)
- [ ] Alarm for ECS task failures
- [ ] Alarm for RDS high CPU (> 80%)
- [ ] Notifications sent to Slack/email

**Tasks:**
1. Create CloudWatch alarms
2. Configure SNS topic
3. Subscribe to topic (email/Slack)
4. Test alarms

**Files to Create:**
- `terraform/cloudwatch_alarms.tf`
- `terraform/sns.tf`

---

## Epic 3.3: Load Testing & Optimization

**Duration:** 3 hours

### User Story 3.3.1: Load Testing

**Duration:** 2 hours

**Description:**  
Test system with 100+ concurrent users.

**Acceptance Criteria:**
- [ ] Load test with 100 concurrent users
- [ ] 1000 requests per minute sustained
- [ ] Response time < 2s (p95)
- [ ] Error rate < 1%
- [ ] No memory leaks
- [ ] Auto-scaling triggered correctly

**Tasks:**
1. Create load test script (Locust or k6)
2. Run test from multiple regions
3. Monitor metrics
4. Document results

**Files to Create:**
- `tests/load/locustfile.py`
- `docs/LOAD_TEST_REPORT.md`

---

### User Story 3.3.2: Performance Optimization

**Duration:** 1.5 hours

**Description:**  
Optimize based on load test results.

**Acceptance Criteria:**
- [ ] Database queries optimized (indexes added)
- [ ] Redis caching implemented
- [ ] LLM response streaming enabled
- [ ] Connection pooling configured
- [ ] Unnecessary logs removed

**Tasks:**
1. Analyze load test results
2. Add database indexes
3. Implement caching
4. Re-run load test
5. Verify improvements

**Files to Modify:**
- `backend/app/core/database.py` (connection pooling)
- `backend/app/agents/alex.py` (streaming)

---

# Success Criteria for MVP

## Framework Protocol (Must Have)

- [ ] All commits have Manus-Session-ID
- [ ] Secrets in AWS Secrets Manager (not .env)
- [ ] Automated backup to S3 every push
- [ ] Recovery runbook tested in DR drill
- [ ] RTO < 4 hours, RPO < 1 commit

## Code Features (Must Have)

- [ ] Agent architecture chosen and implemented
- [ ] Neo4j causal memory fully integrated
- [ ] Real Odoo connection working
- [ ] Telegram bot functional
- [ ] Doctor escalation working
- [ ] All tests passing (unit + integration + E2E)

## Production (Must Have)

- [ ] Deployed to AWS ECS
- [ ] HTTPS with valid SSL certificate
- [ ] Monitoring dashboards active
- [ ] Alerts configured
- [ ] Load tested (100+ users)
- [ ] DR drill completed successfully

---

# Timeline & Milestones

## Week 1 (25-30 hours)

**Days 1-2:** Phase 0 - Framework Protocol
- [ ] Git protocol implemented
- [ ] AWS Secrets Manager configured
- [ ] Backup automation working
- [ ] DR plan documented

**Days 3-4:** Phase 1 - Architecture Decision
- [ ] Architecture chosen
- [ ] Unused code removed
- [ ] Tests updated

**Day 5:** Phase 2 Start - Neo4j & Odoo
- [ ] Neo4j fully integrated
- [ ] Real Odoo connected

## Week 2 (20-25 hours)

**Days 1-2:** Phase 2 Continue - Telegram & Escalation
- [ ] Telegram bot working
- [ ] Doctor escalation implemented

**Days 3-4:** Phase 3 - Production Deployment
- [ ] AWS infrastructure deployed
- [ ] Monitoring configured

**Day 5:** Final Testing & Launch
- [ ] Load testing completed
- [ ] DR drill completed
- [ ] MVP launched! 🎉

---

# Risk Management

## High Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| AWS credentials not available | 🔴 High | Medium | Get credentials early, use personal account if needed |
| Odoo instance not available | 🟡 Medium | High | Use demo.odoo.com as fallback |
| DR drill fails | 🟡 Medium | Medium | Allocate extra time, update runbook |
| Load test reveals performance issues | 🟡 Medium | Medium | Optimize early, use caching |

## Medium Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Telegram API rate limits | 🟡 Medium | Low | Implement backoff, use webhook |
| Neo4j memory issues | 🟡 Medium | Low | Monitor usage, set limits |
| SSL certificate delay | 🟡 Medium | Low | Request early, use Let's Encrypt |

---

# Appendix A: File Structure

```
dental-clinic-ai/
├── .github/
│   └── workflows/
│       └── backup.yml                 # Automated backup workflow
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── alex.py                # Unified agent (if chosen)
│   │   │   ├── dana.py                # Coordinator (if 4-agent chosen)
│   │   │   ├── michal.py              # Medical (if 4-agent chosen)
│   │   │   ├── yosef.py               # Billing (if 4-agent chosen)
│   │   │   ├── sarah.py               # Scheduling (if 4-agent chosen)
│   │   │   ├── agent_graph.py         # Agent orchestration
│   │   │   ├── error_handler.py       # Error handling
│   │   │   └── tools/
│   │   │       ├── agent_tools.py     # Tool integration
│   │   │       └── odoo_tools.py      # Odoo tools
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── auth.py        # Authentication
│   │   │           ├── chat.py        # Chat endpoint
│   │   │           ├── telegram.py    # Telegram webhook
│   │   │           ├── escalations.py # Doctor escalation
│   │   │           ├── memory.py      # Memory management
│   │   │           └── sessions.py    # Session links
│   │   ├── core/
│   │   │   ├── config.py              # Configuration (AWS Secrets)
│   │   │   ├── database.py            # Database connection
│   │   │   └── security.py            # Security utilities
│   │   ├── integrations/
│   │   │   ├── odoo_client.py         # Odoo integration
│   │   │   ├── telegram_client.py     # Telegram integration
│   │   │   └── notification_service.py # SMS/Email notifications
│   │   ├── memory/
│   │   │   └── causal_memory.py       # Neo4j integration
│   │   ├── models/
│   │   │   ├── user.py                # User model
│   │   │   ├── conversation.py        # Conversation model
│   │   │   ├── message.py             # Message model
│   │   │   ├── escalation.py          # Escalation model
│   │   │   └── session_link.py        # Session link model
│   │   └── main.py                    # FastAPI app
│   ├── tests/
│   │   ├── test_agents.py             # Agent unit tests
│   │   ├── test_agent_graph.py        # Graph tests
│   │   ├── test_integration.py        # Integration tests
│   │   ├── test_alex_safety.py        # Safety tests
│   │   └── test_e2e_mvp.py            # E2E tests
│   ├── Dockerfile                     # Backend Docker image
│   └── requirements.txt               # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Main app
│   │   ├── pages/
│   │   │   ├── Login.jsx              # Login page
│   │   │   ├── Register.jsx           # Register page
│   │   │   ├── Chat.jsx               # Chat page
│   │   │   └── Dashboard.jsx          # Dashboard
│   │   └── components/
│   ├── doctor-chat.html               # Simple doctor chat page
│   └── package.json                   # Node dependencies
├── terraform/
│   ├── secrets_manager.tf             # AWS Secrets Manager
│   ├── kms.tf                         # KMS keys
│   ├── iam_roles.tf                   # IAM roles
│   ├── s3_backup.tf                   # S3 backup buckets
│   ├── ecs.tf                         # ECS cluster
│   ├── ecr.tf                         # ECR repository
│   ├── alb.tf                         # Load balancer
│   ├── rds.tf                         # PostgreSQL
│   ├── elasticache.tf                 # Redis
│   ├── cloudwatch_alarms.tf           # CloudWatch alarms
│   ├── sns.tf                         # SNS notifications
│   └── route53.tf                     # DNS
├── scripts/
│   ├── export_manus_session.py        # Session export
│   ├── setup_git_identity.sh          # Git identity setup
│   ├── embed_version.py               # Version embedding
│   └── restore_from_backup.sh         # Recovery script
├── docs/
│   ├── GIT_PROTOCOL.md                # Git protocol guide
│   ├── IAM_ROLES.md                   # IAM roles documentation
│   ├── RECOVERY_RUNBOOK.md            # Recovery procedure
│   ├── RTO_RPO_DEFINITION.md          # DR objectives
│   ├── ROLES_RESPONSIBILITIES.md      # Team roles
│   ├── ARCHITECTURE_DECISION.md       # Architecture choice
│   ├── DR_DRILL_REPORT.md             # DR drill results
│   └── LOAD_TEST_REPORT.md            # Load test results
├── .gitmessage                        # Commit message template
├── .gitignore                         # Git ignore
├── docker-compose.yml                 # Local development
├── PROJECT_STATUS_REPORT.md           # This status report
└── WORK_PLAN_V17.0.md                 # This work plan
```

---

# Appendix B: Key Commands

## Git Protocol

```bash
# Configure commit template
git config commit.template .gitmessage

# Set up Git identity
./scripts/setup_git_identity.sh

# Commit with proper format
git commit
# (Opens editor with template)

# View commit with full details
git log --format=fuller
```

## AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
  --name prod/openai-api-key \
  --secret-string "sk-..." \
  --kms-key-id alias/dental-clinic-secrets

# Retrieve secret
aws secretsmanager get-secret-value \
  --secret-id prod/openai-api-key \
  --query SecretString \
  --output text

# Rotate secret
aws secretsmanager rotate-secret \
  --secret-id prod/openai-api-key
```

## Backup & Recovery

```bash
# Manual backup
./scripts/export_manus_session.py --session-id abc123
git bundle create repo.bundle --all
tar -czf backup.tar.gz repo.bundle manus_session_data/
aws s3 cp backup.tar.gz s3://dental-clinic-backups-us-east-1/

# Recovery
aws s3 cp s3://dental-clinic-backups-us-east-1/backup.tar.gz .
tar -xzf backup.tar.gz
git clone repo.bundle my-restored-project
./scripts/restore_from_backup.sh
```

## Deployment

```bash
# Build and push Docker image
docker build -t dental-clinic-backend backend/
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-url>
docker tag dental-clinic-backend:latest <ecr-url>/dental-clinic-backend:latest
docker push <ecr-url>/dental-clinic-backend:latest

# Deploy with Terraform
cd terraform
terraform init
terraform plan
terraform apply

# Update ECS service
aws ecs update-service \
  --cluster dental-clinic \
  --service backend \
  --force-new-deployment
```

---

**Work Plan Prepared By:** Manus AI Agent  
**Date:** October 2, 2025  
**Next Review:** After Phase 0 completion

---

**Ready to start Phase 0!** 🚀
