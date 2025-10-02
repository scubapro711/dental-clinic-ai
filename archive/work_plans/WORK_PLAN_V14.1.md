# DentalAI SaaS Platform - Work Plan V14.1

**Date:** 2025-10-02  
**Version:** 14.1  
**Status:** In Progress - MVP Development with Audit Findings  
**Previous Version:** WORK_PLAN_V14.0.md  
**Related Documents:** MVP_AUDIT_REPORT.md, FRAMEWORK_SUMMARY.md

---

## 🎯 Executive Summary

This document outlines the comprehensive work plan for building the **DentalAI SaaS Platform**, a state-of-the-art, AI-powered system for dental clinics. Version 14.1 represents an **honest status update** based on comprehensive audit findings conducted on October 2, 2025, maintaining full alignment with the original Framework (מיסגרתעבודה1.pdf).

### Key Changes in v14.1:

#### **Audit Findings & Status Updates (October 2, 2025):**

**What Actually Works (Validated ✅):**
- ✅ **Backend API (100%)** - Fully tested E2E: register, login, JWT auth, chat, conversations
- ✅ **Database Layer (100%)** - PostgreSQL + Redis operational with proper migrations  
- ✅ **Dana Agent (100%)** - Tested and responding correctly to user messages
- ✅ **Authentication System (100%)** - RBAC, JWT tokens, auto-org assignment working
- ✅ **Git Repository (100%)** - Clean commits with Manus-Session-ID protocol

**What Needs Validation (Created but Not Tested ⚠️):**
- ⚠️ **Epic 2 (Agents): 100% → 70%** - Michal, Yosef, Sarah created but not tested
- ⚠️ **Epic 3 (Odoo): 80% → 50%** - OdooClient + Tools ready but not integrated with agents
- ⚠️ **Epic 4 (Memory): 100% → 40%** - Neo4j installed, CausalMemory code exists, but not integrated
- ⚠️ **Frontend: 100% → 50%** - React app built (Login, Register, Chat, Dashboard) but not tested E2E

**Open Issues Identified (❌):**
1. ❌ **Neo4j Authentication** - Auth configuration issue (non-blocking for MVP)
2. ❌ **3 Agents Untested** - Michal (Medical), Yosef (Billing), Sarah (Scheduling) need validation
3. ❌ **Odoo Tools Not Connected** - Tools exist but agents don't use them yet
4. ❌ **Causal Memory Not Active** - Neo4j running but no agent integration
5. ❌ **Frontend Not Tested** - No E2E user flow validation
6. ❌ **AWS Deployment** - Not started (Epic 11)
7. ❌ **WhatsApp/Telegram** - Not started (Epic 5)

**Roadmap to MVP Complete (8 hours estimated):**
- **Phase 1 (3h):** Validate 3 agents + Frontend E2E testing + Deploy frontend
- **Phase 2 (5h):** Fix Neo4j auth + Integrate Causal Memory + Connect Odoo Tools to agents

**Current Overall Progress: 70%** (was reported as 95%, corrected after audit)

---

### Key Changes in v14.0:

#### **Critical Additions:**
- ✅ **Epic 0.6: Backup & Disaster Recovery** - Automated backups, restoration testing, disaster recovery plan
- ✅ **User Story 0.1.5: Git Repository Hygiene** - Pre-commit hooks, repository cleanliness
- ✅ **User Story 0.1.6: Legal/Licensing Framework** - LICENSE file, copyright headers, third-party attributions
- ✅ **Enhanced Deployment Strategy** - Kubernetes manifests, Helm charts, blue-green deployment, rollback procedures
- ✅ **User Story 11.5: Production Deployment Checklist** - Comprehensive deployment checklist

#### **Previous Changes (v13.0):**
- ✅ **Reduced to 4 Architectural Pillars** (from 11) as per Framework specification
- ✅ **Added Fine-Tuning Strategy** with detailed implementation plan
- ✅ **Sharpened Agent Definitions** with Input/Output/Processing/Metrics
- ✅ **Precise Small Models Definition** (Llama 3.1 8B + vLLM deployment)
- ✅ **Precise Causal Memory Definition** (Neo4j + Sentence-BERT + Bayesian updating)
- ✅ **Enhanced DoD** with rigorous testing, open-source validation, AWS MVP target

This plan is designed to be **fully executable** by a Manus AI agent, following the original framework structure with detailed tasks, measurable acceptance criteria, and comprehensive documentation.

---

## Part I: Master Prompt

### 1.1 Context

**Why are we building this?**

Dental clinics in Israel and worldwide are struggling with:
1. **Administrative overhead** - Manual scheduling, billing, patient management
2. **Inefficient operations** - Lack of data-driven insights and automation
3. **Business management complexity** - Need for expensive consultants (accountants, lawyers, HR, marketing)
4. **System downtime** - Manual intervention required when technical issues arise

The current software landscape is fragmented, expensive, and lacks modern AI capabilities.

**What is the problem?**

1. **For Clinic Owners:** Waste valuable time on administrative tasks instead of patient care, leading to reduced profitability and lower patient satisfaction
2. **For Practice Managers:** Need expensive external consultants for finance, HR, marketing, legal compliance
3. **For System Administrators:** Existing systems require constant manual intervention when issues occur, resulting in downtime and lost revenue

**What is the solution?**

A **three-tier AI-powered SaaS platform** that provides:

#### **Tier 1: Basic (₪0/month)** - Patient-Facing Automation
- Conversational patient management (scheduling, billing, medical info)
- 4 specialized agents: Dana (Coordinator), Michal (Medical), Yosef (Billing), Sarah (Scheduling)
- Odoo ERP integration for data management

#### **Tier 2: Professional (₪1,500/month)** - Basic Business Management
- All Basic features
- CFO Agent (Basic): Financial reporting, expense tracking
- Operations Agent (Basic): Inventory management, equipment maintenance
- Mission Control Dashboard (MVP)

#### **Tier 3: Enterprise (₪4,500/month)** - Complete Business Management
- All Professional features
- 7 Executive Agents with deep Israeli expertise:
  - **CFO Agent:** Complete financial management, Israeli tax compliance, VAT filing
  - **CHRO Agent:** Recruitment, HR management, Israeli labor law compliance
  - **CMO Agent:** Marketing automation, patient acquisition, online reputation
  - **COO Agent:** Operations optimization, inventory, scheduling
  - **CLO Agent:** Legal compliance, Health Ministry regulations, contracts
  - **CSO Agent:** Strategic planning, competitive intelligence, growth strategy
  - **Practice Administrator:** Daily coordination, Telegram communication, issue triage
- Mission Control Dashboard (Full Vision) with Self-Healing System
- 10-17x ROI vs traditional consultants

**Additionally, for DentalAI Business (Internal Use):**
- **Portfolio A Executive Agents:** 7 agents that manage the SaaS company itself
- CPO (Product), CRO (Revenue), CCO (Customer), CFO (Finance), CPO (People), COO (Operations), CSO (Strategy)
- 18x ROI vs traditional management team

**Target Markets:**
- **Primary:** Israel (initial launch)
- **Secondary:** European Union (GDPR compliance built-in)
- **Tertiary:** United States (future expansion)

### 1.2 Clarity

**What are the core features?**

The platform provides 24 core features across three tiers:

#### **Tier 1: Basic (Free)**
1. **Conversational Scheduling** - Natural language appointment booking via WhatsApp/Web
2. **Automated Billing** - Invoice generation, payment tracking, reminders
3. **Medical Info Q&A** - AI-powered answers to common dental questions
4. **Odoo Integration** - Sync patients, appointments, invoices with Odoo

#### **Tier 2: Professional**
5. **CFO Agent (Basic)** - Financial reporting, expense tracking
6. **Operations Agent (Basic)** - Inventory management, equipment maintenance
7. **Mission Control Dashboard (MVP)** - Real-time monitoring of agents and system health

#### **Tier 3: Enterprise**
8. **CFO Agent (Full)** - Tax optimization, forecasting, profitability analysis
9. **CHRO Agent** - Recruitment, HR, Israeli labor law
10. **CMO Agent** - Marketing, patient acquisition, reputation
11. **COO Agent** - Operations optimization, smart inventory
12. **CLO Agent** - Legal compliance, Health Ministry regulations
13. **CSO Agent** - Strategic planning, competitive intelligence
14. **Practice Administrator** - Telegram coordination, issue triage
15. **Self-Healing System** - Automated incident detection and resolution
16. **Knowledge Cards** - Proactive insights and recommendations
17. **Analytics Dashboard** - Business intelligence and KPIs

#### **Platform Features (All Tiers)**
18. **Multi-Tenancy** - Secure data isolation for each clinic
19. **RBAC** - 4 roles: Super Admin, Clinic Admin, Staff, Read-Only
20. **MFA** - Multi-Factor Authentication with TOTP
21. **GDPR Compliance** - Klaro consent management
22. **Prompt Injection Prevention** - Rebuff integration
23. **Streaming** - Real-time agent responses
24. **WhatsApp/Telegram/Web Interfaces** - Multi-channel communication

### 1.3 Layouts

**Tech Stack:**

#### **Core Technologies:**
- **Frontend:** React 18 + TypeScript
- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 15
- **Cache:** Redis 7.0
- **ERP:** Odoo Community 17.0

#### **AI/ML:**
- **LLM (Primary):** Claude Sonnet 3.5
- **LLM (Small Models):** Llama 3.1 8B Instruct
- **Agent Framework:** LangGraph
- **Embeddings:** Sentence-BERT
- **Vector DB:** Pinecone
- **Causal Memory:** Neo4j 5.0
- **Fine-Tuning:** LoRA with Unsloth
- **Small Model Serving:** vLLM

#### **Infrastructure:**
- **Cloud:** AWS
- **Containerization:** Docker, Kubernetes (EKS)
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus, Grafana, ELK Stack
- **Secrets:** AWS Secrets Manager
- **CDN:** CloudFront
- **Storage:** S3

#### **Communication:**
- **WhatsApp:** Twilio API
- **Telegram:** Telegram Bot API
- **Email:** SendGrid
- **SMS:** Twilio

**Agent Architecture:**

The system employs a **5-layer agentic architecture**:

#### **Layer 1: Patient-Facing Agents (Tier 1)**
- **Dana (Coordinator):** Routes conversations, orchestrates other agents
- **Michal (Medical Info):** Answers dental questions, provides treatment info
- **Yosef (Billing):** Handles invoices, payments, financial queries
- **Sarah (Scheduling):** Manages appointments, sends reminders

#### **Layer 2: Basic Executive Agents (Tier 2)**
- **CFO Agent (Basic):** Financial reporting, expense tracking
- **Operations Agent (Basic):** Inventory, equipment maintenance

#### **Layer 3: Full Executive Agents (Tier 3)**
- **CFO Agent (Full):** Tax optimization, forecasting, profitability analysis
- **CHRO Agent:** Recruitment, HR, Israeli labor law
- **CMO Agent:** Marketing, patient acquisition, reputation
- **COO Agent:** Operations optimization, smart inventory
- **CLO Agent:** Legal compliance, Health Ministry regulations
- **CSO Agent:** Strategic planning, competitive intelligence
- **Practice Administrator:** Telegram coordination, issue triage

#### **Layer 4: Self-Healing Agents (Tier 3)**
- **Observer Agent:** Monitors system health, detects incidents
- **Diagnosis Agent:** Analyzes root causes, categorizes issues
- **Healing Planner Agent:** Plans recovery strategies
- **Action Agent:** Executes healing actions
- **Memory Agent:** Maintains Causal Memory Graph, learns from incidents

#### **Layer 5: Internal Executive Agents (Portfolio A)**
- **CPO, CRO, CCO, CFO, CPO (HR), COO, CSO:** Manage DentalAI business

**Data Entities:**

The system manages 24 core data entities:

1. **Organization** - Dental clinic/practice
2. **User** - System users (dentists, staff, admins)
3. **Patient** - Clinic patients
4. **Appointment** - Scheduled appointments
5. **Treatment** - Dental treatments/procedures
6. **Invoice** - Billing invoices
7. **Payment** - Payment transactions
8. **Conversation** - Chat history
9. **Message** - Individual messages
10. **KnowledgeCard** - Medical knowledge base
11. **AgentState** - LangGraph state for each conversation
12. **Checkpoint** - LangGraph checkpoints for persistence
13. **RateLimitCounter** - Tool usage tracking
14. **CacheEntry** - Node-level cache
15. **Incident** - System incidents/errors
16. **CausalMemory** - Incident-solution relationships (Neo4j)
17. **ExecutiveReport** - Reports generated by executive agents
18. **StrategicInsight** - Insights from CSO/CPO agents
19. **FinancialForecast** - ML-based predictions
20. **MarketingCampaign** - Campaign tracking
21. **RecruitmentPipeline** - Hiring process tracking
22. **ComplianceCheck** - Regulatory compliance tracking
23. **InventoryItem** - Stock management
24. **MaintenanceSchedule** - Equipment maintenance

### 1.4 Milestones

The project is divided into **16 weeks** with clear deliverables:

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| **-1** | Deep Learning Phase | LangGraph, LangChain, Odoo, Israeli law research |
| **0** | Project Setup & Infrastructure | GitHub, AWS, PostgreSQL, Redis, CI/CD, Monitoring |
| **0.5** | Migration, Demo Data & Backups | Demo data (100 patients, 200 appointments), migration scripts, automated backups, disaster recovery plan |
| **1** | SaaS Foundation & Security | Multi-tenancy, RBAC, MFA, GDPR, Prompt Injection Prevention |
| **2-3** | Agent Architecture & State Management | Dana, Michal, Yosef, Sarah + State, Error Handling, Rate Limiting |
| **3.5** | Streaming & Real-Time Updates | Token-by-token streaming, progress notifications |
| **4** | Centralized Odoo Integration | Unified Odoo service with caching |
| **5** | Fine-Tuning Executive Agents | LoRA fine-tuning on Israeli law (5,000+ examples) |
| **6-7** | Executive Agents - Portfolio B | CFO, CHRO, CMO, COO, CLO, CSO, Practice Admin (Tier 2 & 3) |
| **8-9** | Mission Control Dashboard | MVP (Week 8) + Full Vision with Self-Healing (Week 9) |
| **10** | Executive Agents - Portfolio A | CPO, CRO, CCO, CFO, CPO (HR), COO, CSO (internal) |
| **11** | Conversational Interfaces | WhatsApp, Telegram, Web Chat |
| **12** | Knowledge Management & Analytics | Knowledge Cards, Analytics Dashboard |
| **13** | Testing, Security Hardening & Deployment | E2E tests, penetration testing, production deployment with comprehensive checklist |

**Total Duration:** 16 weeks (4 months)

### 1.5 Notes

**Budget Constraints:**
- Initial development budget: $50,000-75,000
- Monthly operational costs (AWS, APIs): $2,000-5,000
- Target: Break-even at 50 Enterprise customers (₪225,000/month revenue)

**Compliance Requirements:**
- **GDPR:** Full compliance for EU market (Klaro consent management)
- **Israeli Privacy Protection Law:** Data residency, consent, right to deletion
- **Health Ministry Regulations:** Medical data handling, clinic licensing
- **Israeli Tax Authority:** VAT filing (PCN874), tax reporting

**Technical Constraints:**
- **LLM API Costs:** Claude Sonnet 3.5 at $3/1M input tokens, $15/1M output tokens
- **Small Model Hosting:** AWS g5.xlarge at ~$1/hour for Llama 3.1 8B
- **Context Window:** 200K tokens for Claude Sonnet 3.5
- **Latency Target:** <2 seconds for agent responses

**Assumptions:**
- Odoo Dental Module provides sufficient ERP functionality
- Israeli law corpus can be scraped from public sources (Tax Authority, Knesset)
- Fine-tuning 5,000 examples sufficient for domain adaptation
- Neo4j Aura (managed) acceptable for Causal Memory at scale

---

## Part II: Architectural Pillars

### 1.6 Security by Design

**Primary Directive:** "Act as a security architect. You must create a 'Security and Compliance Blueprint' that addresses core threats and establishes a secure foundation for the project."

#### Sub-Guidelines:

**1.6.1 Threat Modeling**

"Based on the application's context and features, perform a threat modeling exercise. Identify and detail the top five potential attack vectors. For each vector, describe a possible threat scenario."

**Implementation:**
1. **Injection Attacks (SQL, NoSQL, Prompt Injection)**
   - Threat: Attacker injects malicious SQL/prompts to access unauthorized data
   - Mitigation: Parameterized queries, input sanitization, Rebuff for prompt injection

2. **Broken Access Control**
   - Threat: User accesses another tenant's data
   - Mitigation: Row-Level Security (RLS) in PostgreSQL, tenant_id validation in every query

3. **Authentication Failures**
   - Threat: Weak passwords, session hijacking
   - Mitigation: MFA (mandatory for all roles), JWT with short expiration, secure session storage

4. **Cryptographic Failures**
   - Threat: Sensitive data exposed in transit/at rest
   - Mitigation: TLS 1.3, AES-256 encryption at rest, PII masking in non-production

5. **Insecure Design**
   - Threat: Lack of business logic access controls
   - Mitigation: RBAC, rate limiting, business logic validation

**1.6.2 Security Controls**

"Define the specific security controls that will be implemented at each layer of the application (data, application, network)."

**Implementation:**
- **Data Layer:**
  - Encryption at rest (AWS KMS)
  - Data masking for PII in non-production
  - RLS for multi-tenancy
  - Regular backups
- **Application Layer:**
  - Input validation (Pydantic, Zod)
  - Output encoding
  - CSRF protection
  - Security headers (CSP, HSTS)
  - Rate limiting
  - Rebuff for prompt injection
- **Network Layer:**
  - TLS 1.3 for all traffic
  - VPC with private/public subnets
  - Security groups and NACLs
  - WAF (AWS WAF)

**1.6.3 Compliance**

"Outline the steps to ensure compliance with relevant regulations (GDPR, Israeli Privacy Law)."

**Implementation:**
- **GDPR:**
  - Klaro for consent management
  - Data Processing Addendum (DPA)
  - Right to be forgotten implementation
  - Data residency in EU (Frankfurt region)
- **Israeli Privacy Law:**
  - Data residency in Israel (future)
  - Explicit consent for data processing
  - Secure data handling procedures

### 1.7 Scalability & Performance

**Primary Directive:** "Act as a performance engineer. You must create a 'Scalability and Performance Blueprint' that ensures the system can handle growth and maintain responsiveness."

#### Sub-Guidelines:

**1.7.1 Performance Targets**

"Define specific, measurable performance targets for key system components."

**Implementation:**
- **API Latency:** p95 < 200ms
- **Agent Response Time:** p95 < 2 seconds
- **Page Load Time:** < 1 second (LCP)
- **Concurrent Users:** 100 (MVP), 1000 (Post-MVP)
- **Error Rate:** < 0.1%

**1.7.2 Scalability Strategy**

"Describe the horizontal and vertical scaling strategies for each service."

**Implementation:**
- **Backend (FastAPI):**
  - Horizontal scaling with Kubernetes HPA (CPU/memory)
  - Vertical scaling by increasing pod resources
- **Frontend (React):**
  - Horizontal scaling with multiple pods
- **Database (PostgreSQL):**
  - Vertical scaling (larger RDS instance)
  - Read replicas for read-heavy workloads
- **Cache (Redis):**
  - Vertical scaling (larger ElastiCache instance)
- **LLM Serving (vLLM):**
  - Horizontal scaling with multiple pods

**1.7.3 Caching Strategy**

"Define the caching strategy for different types of data."

**Implementation:**
- **Node-Level Caching (LangGraph):**
  - Cache expensive LLM calls
  - Cache database queries
  - Cache tool outputs
  - Cache key generation: hash of node inputs
  - TTL: 1 hour
- **API Caching:**
  - Redis for caching frequently accessed data (e.g., user profiles)
  - TTL: 5 minutes
- **Frontend Caching:**
  - TanStack Query for client-side caching
  - Service workers for offline access

### 1.8 Multi-Tenancy Architecture

**Primary Directive:** "Act as a multi-tenancy expert. You must create a 'Multi-Tenancy Blueprint' that ensures complete data isolation and customization for each tenant."

#### Sub-Guidelines:

**1.8.1 Data Isolation Model**

"Choose and justify a data isolation model (silo, bridge, or pool)."

**Implementation:**
- **Model:** Pool model with Row-Level Security (RLS)
- **Justification:**
  - Cost-effective (shared database)
  - Strong security (database-level isolation)
  - Scalable (easy to add new tenants)

**1.8.2 Tenant Identification**

"Describe how the system will identify the current tenant for each request."

**Implementation:**
- Tenant ID stored in JWT token
- Middleware extracts tenant ID from JWT
- Middleware sets `app.current_tenant` in database session

**1.8.3 Tenant Customization**

"Outline how tenants can customize their experience."

**Implementation:**
- **Branding:** Custom logo, colors
- **Agent Behavior:** Custom prompts, knowledge base
- **Integrations:** Custom API keys
- **Settings:** Stored in `organizations` table

### 1.9 System Observability

**Primary Directive:** "Act as a DevOps engineer. You must create an 'Observability Blueprint' that provides deep insights into system health and behavior."

#### Sub-Guidelines:

**1.9.1 The Three Pillars of Observability**

"Describe how you will implement logging, metrics, and tracing."

**Implementation:**
- **Logging:**
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - Structured logging (structlog) in JSON format
  - Log correlation with trace IDs
- **Metrics:**
  - Prometheus for time-series metrics
  - Grafana for dashboards
  - Key metrics: requests/min, error rate, latency, CPU/memory
- **Tracing:**
  - OpenTelemetry for distributed tracing
  - Jaeger for trace visualization
  - Trace every request from frontend to backend to database/LLM

**1.9.2 Dashboards and Alerting**

"Design the key dashboards and alerts for monitoring the system."

**Implementation:**
- **Dashboards (Grafana):**
  - System Overview (high-level KPIs)
  - Service Health (CPU, memory, disk for each service)
  - Agent Performance (response time, error rate per agent)
  - Business Metrics (new users, active users, revenue)
- **Alerts (Prometheus Alertmanager):**
  - High error rate (>1%)
  - High latency (>2s)
  - Service down (unreachable)
  - High CPU/memory usage (>80%)
  - Low disk space (<10%)

**1.9.3 Self-Healing Integration**

"Describe how observability will trigger the self-healing system."

**Implementation:**
- Prometheus alerts trigger webhooks
- Webhooks send alerts to Observer Agent
- Observer Agent creates incident in database
- Diagnosis Agent analyzes incident (logs, traces, metrics)
- Healing Planner Agent plans recovery
- Action Agent executes recovery

---




## Part III: Quality Gates & Development Guidelines

### Definition of Ready (DoR)

Before a User Story can be started, it must meet the following criteria:

**Functional Requirements:**
- [ ] User story is written in standard format: "As a [role], I want [feature] so that [benefit]"
- [ ] Acceptance criteria are clearly defined and testable
- [ ] Dependencies on other stories are identified and documented
- [ ] UI/UX mockups are provided (if applicable)

**Technical Requirements:**
- [ ] Technical approach is discussed and agreed upon
- [ ] Database schema changes are documented
- [ ] API contracts are defined (OpenAPI spec)
- [ ] Security implications are assessed

**Resource Requirements:**
- [ ] Required third-party APIs are identified and access is confirmed
- [ ] Test data requirements are documented
- [ ] Estimated effort is provided (story points or hours)

**Context Refresh (Critical for AI Agent Development):**
- [ ] At the start of each User Story, the AI agent must:
  1. Read the relevant sections of this Work Plan
  2. Review the Master Prompt (Part I)
  3. Review the relevant Architectural Pillar (Part II)
  4. Review the agent definitions and data entities
  5. Confirm understanding of the current phase (MVP or Post-MVP)

### Definition of Done (DoD)

A User Story is considered "Done" when ALL of the following criteria are met:

**Code Quality:**
- [ ] Code follows best practices for the language/framework
  - Python: PEP 8, type hints, docstrings
  - TypeScript: ESLint rules, strict mode, JSDoc comments
- [ ] Code passes linter checks with zero errors
  - Python: `ruff check` and `mypy`
  - TypeScript: `eslint` and `tsc --noEmit`
- [ ] Code has been reviewed and approved by at least one other developer
- [ ] No commented-out code or debug statements remain
- [ ] All TODOs are resolved or converted to GitHub issues

**Testing (Rigorous, Especially Frontend):**
- [ ] **Unit tests** written with ≥80% code coverage
  - Backend: pytest with pytest-cov
  - Frontend: Vitest with @vitest/coverage-v8
- [ ] **Integration tests** pass for all relevant workflows
  - Backend: pytest with test database
  - Frontend: React Testing Library
- [ ] **End-to-end tests** pass for critical user flows
  - Playwright tests for complete user journeys
  - **Frontend tests must be 100x more rigorous** (comprehensive scenarios, edge cases, accessibility)
- [ ] **Performance tests** confirm latency targets are met
  - API endpoints: p95 < 200ms
  - Agent responses: p95 < 5s
- [ ] All tests are automated and run in CI/CD pipeline
- [ ] Tests are deterministic (no flaky tests)

**Security:**
- [ ] SAST scan (Bandit for Python, ESLint security plugin for TypeScript) finds no high/critical vulnerabilities
- [ ] Secrets and API keys are managed via AWS Secrets Manager (never hardcoded)
- [ ] Input validation is implemented for all user inputs (Pydantic models, Zod schemas)
- [ ] OWASP Top 10 mitigations are applied where relevant
- [ ] Security review completed for authentication/authorization changes

**Documentation:**
- [ ] API endpoints are documented in OpenAPI spec (Swagger)
- [ ] Code comments added for complex logic
- [ ] Architecture Decision Records (ADRs) updated if design decisions were made
- [ ] README updated if setup/deployment steps changed
- [ ] Inline documentation (docstrings, JSDoc) added for all public functions/classes

**Deployment:**
- [ ] Build artifact is versioned and stored in artifact registry
- [ ] Code is merged to `main` branch successfully
- [ ] Deployment to **Staging** environment is successful
- [ ] Feature is verified in Staging by manual testing
- [ ] Database migrations (if any) are tested in Staging
- [ ] Rollback plan is documented

**MVP Target:**
- [ ] Feature contributes to **working MVP deployed on AWS**
- [ ] Feature is demo-ready (can be shown to potential customers)
- [ ] Integration tests confirm feature works with other MVP components

**Open-Source Validation:**
- [ ] If using open-source libraries, verify:
  - Library is actively maintained (commits in last 6 months)
  - Library has good reputation (GitHub stars, downloads, community)
  - Library has acceptable license (MIT, Apache 2.0, BSD)
  - Library has no known critical vulnerabilities (npm audit, pip-audit)

### Development Session Guidelines

**For every development session, the AI agent MUST:**

1. **Context Refresh at Session Start:**
   - Read this Work Plan (relevant sections)
   - Review the current Epic and User Story
   - Confirm understanding of acceptance criteria
   - Review relevant agent definitions and data entities

2. **Context Refresh at User Story Start:**
   - Read Master Prompt (Part I)
   - Read relevant Architectural Pillar (Part II)
   - Review DoR checklist
   - Confirm all dependencies are met

3. **Best Code Practices (Mandatory):**
   - **NEVER deviate from the Work Plan** without explicit approval
   - If deviation seems necessary, STOP and propose updating the Work Plan
   - Follow language/framework best practices religiously
   - Write clean, readable, maintainable code
   - Prefer composition over inheritance
   - Keep functions small and focused (single responsibility)
   - Use meaningful variable/function names
   - Avoid premature optimization

4. **Rigorous Testing (Especially Frontend):**
   - Write tests BEFORE or ALONGSIDE code (TDD encouraged)
   - Frontend tests must cover:
     - All user interactions (clicks, inputs, navigation)
     - All edge cases (empty states, error states, loading states)
     - Accessibility (keyboard navigation, screen readers)
     - Responsive design (mobile, tablet, desktop)
   - Backend tests must cover:
     - All API endpoints (success and error cases)
     - All business logic (edge cases, boundary conditions)
     - All database operations (CRUD, transactions, rollbacks)
   - **Testing is YOUR responsibility** - do not skip or defer

5. **MVP Focus:**
   - Every feature must contribute to a **working, deployable MVP on AWS**
   - Prioritize functionality over perfection
   - Avoid scope creep (stick to acceptance criteria)
   - Ensure integration with other MVP components

6. **Integration Testing:**
   - After completing each User Story, run integration tests
   - Verify feature works with:
     - Authentication/authorization
     - Database (PostgreSQL, Redis)
     - External APIs (Odoo, LLMs, Twilio)
   - Test in Staging environment before marking as Done

---

## 🎯 PHASE 1: MVP (Weeks 0-4)

**Goal:** Deploy a working, demo-ready MVP on AWS with core patient-facing agents (Tier 1) and basic SaaS foundation.

**Deliverables:**
- Multi-tenant SaaS platform with RBAC, MFA, GDPR compliance
- 4 conversational agents: Dana, Michal, Yosef, Sarah
- Odoo integration for data management
- WhatsApp interface
- Deployed on AWS with monitoring

**Success Criteria:**
- Demo-ready for potential customers
- Can onboard a real dental clinic
- Handles 100 concurrent users
- <2s agent response time (p95)
- 99.9% uptime

---

### Epic L: Deep Learning Phase (Week -1, 6 days)

**Goal:** Research and understand all technologies, frameworks, and domain knowledge required for the project.

#### User Story L.1: Master LangGraph and LangChain

**As a developer**, I want to deeply understand LangGraph and LangChain so that I can build robust agentic workflows.

**Acceptance Criteria:**
- [ ] Complete LangGraph official tutorial
- [ ] Build a simple multi-agent system with LangGraph
- [ ] Understand state management, checkpoints, persistence
- [ ] Understand error handling patterns
- [ ] Understand streaming capabilities
- [ ] Document key learnings in `/docs/langgraph-learnings.md`

**Tasks:**
1. Read LangGraph documentation (https://langchain-ai.github.io/langgraph/)
2. Complete "Introduction to LangGraph" tutorial
3. Build a simple 2-agent system (Coordinator + Worker)
4. Implement state persistence with PostgreSQL
5. Implement error handling with retry logic
6. Test streaming with token-by-token output
7. Document learnings

**Estimated Effort:** 2 days

---

#### User Story L.2: Master Odoo Integration

**As a developer**, I want to understand Odoo's architecture and API so that I can integrate it seamlessly.

**Acceptance Criteria:**
- [ ] Odoo Community 17.0 installed locally
- [ ] Odoo Dental Module installed and configured
- [ ] Understand Odoo XML-RPC API
- [ ] Successfully create/read/update/delete records via API
- [ ] Understand Odoo's security model (access rights, record rules)
- [ ] Document key learnings in `/docs/odoo-learnings.md`

**Tasks:**
1. Install Odoo Community 17.0 with Docker
2. Install Odoo Dental Module
3. Explore Odoo UI (patients, appointments, invoices)
4. Read Odoo External API documentation
5. Write Python script to connect via XML-RPC
6. Test CRUD operations (create patient, create appointment)
7. Understand Odoo's multi-company model
8. Document learnings

**Estimated Effort:** 1 day

---

#### User Story L.3: Research Israeli Law and Regulations

**As a developer**, I want to understand Israeli tax law, labor law, and health regulations so that I can build compliant executive agents.

**Acceptance Criteria:**
- [ ] Understand Israeli tax system (VAT, income tax, deductions)
- [ ] Understand Israeli labor law (working hours, vacation, sick leave, severance)
- [ ] Understand Health Ministry regulations for dental clinics
- [ ] Identify public data sources (Tax Authority, Knesset, Ministry of Health)
- [ ] Document key learnings in `/docs/israeli-law-learnings.md`

**Tasks:**
1. Research Israeli VAT system (17% rate, PCN874 form)
2. Research Israeli income tax brackets and deductions
3. Research Israeli labor law (חוק שעות עבודה ומנוחה, חוק חופשה שנתית)
4. Research Health Ministry regulations for dental clinics
5. Identify public data sources:
   - Tax Authority website (https://www.gov.il/he/departments/israel_tax_authority)
   - Knesset Open Data (https://data.gov.il/)
   - Ministry of Health (https://www.health.gov.il/)
6. Document learnings

**Estimated Effort:** 1 day

---

#### User Story L.4: Research Security Best Practices

**As a developer**, I want to understand OWASP Top 10, prompt injection prevention, and data leakage prevention so that I can build a secure system.

**Acceptance Criteria:**
- [ ] Understand OWASP Top 10 (2021)
- [ ] Understand prompt injection attacks and mitigations
- [ ] Understand data leakage risks in multi-tenant systems
- [ ] Research Rebuff for prompt injection detection
- [ ] Document key learnings in `/docs/security-learnings.md`

**Tasks:**
1. Read OWASP Top 10 (2021) documentation
2. Research prompt injection attacks (examples, mitigations)
3. Research Rebuff library (https://github.com/protectai/rebuff)
4. Research PostgreSQL Row-Level Security (RLS)
5. Research data masking techniques
6. Document learnings

**Estimated Effort:** 1 day

---

#### User Story L.5: Research Error Handling and Self-Healing

**As a developer**, I want to understand error handling patterns, self-healing systems, and causal memory so that I can build a resilient system.

**Acceptance Criteria:**
- [ ] Understand LangGraph error handling patterns
- [ ] Understand self-healing system architectures
- [ ] Understand causal memory and graph-based learning
- [ ] Research Neo4j for causal memory
- [ ] Document key learnings in `/docs/error-handling-learnings.md`

**Tasks:**
1. Read LangGraph error handling tutorial
2. Research self-healing system architectures
3. Research causal memory (incident → solution → learning)
4. Research Neo4j graph database
5. Research Sentence-BERT for similarity matching
6. Document learnings

**Estimated Effort:** 1 day

---

### Epic 0: Project Setup & Infrastructure (Week 0, 6.5 days)

**Goal:** Set up the development environment, infrastructure, CI/CD pipeline, and legal framework.

#### User Story 0.1: Initialize GitHub Repository and Project Structure

**As a developer**, I want a well-organized GitHub repository so that the codebase is maintainable.

**Acceptance Criteria:**
- [x] Repository cleaned up (old code removed)
- [ ] GitHub repository created: `dental-clinic-ai`
- [ ] Monorepo structure with `backend/` and `frontend/` directories
- [ ] `.gitignore` configured for Python and Node.js
- [ ] `README.md` with project overview and setup instructions
- [ ] `CONTRIBUTING.md` with development guidelines
- [ ] Branch protection rules enabled on `main` branch

**Tasks:**
0. **Clean up existing repository** (COMPLETED):
   - Remove all old code (`src/`, `tests/`, `scripts/`, etc.)
   - Remove all old documents (analysis, reports, etc.)
   - Keep only: WORK_PLAN_V14.0.md, LICENSE, NOTICE, .gitignore, docs/vision_document.pdf
   - Create clean project structure
   - Update README.md
1. Create GitHub repository: `dental-clinic-ai`
2. Initialize monorepo structure:
   ```
   dental-clinic-ai/
   ├── backend/
   │   ├── app/
   │   ├── tests/
   │   ├── alembic/
   │   ├── requirements.txt
   │   └── pyproject.toml
   ├── frontend/
   │   ├── src/
   │   ├── tests/
   │   ├── package.json
   │   └── tsconfig.json
   ├── docs/
   ├── scripts/
   ├── .github/
   │   └── workflows/
   ├── docker-compose.yml
   ├── .gitignore
   ├── README.md
   └── CONTRIBUTING.md
   ```
3. Configure `.gitignore` (Python, Node.js, IDEs)
4. Write `README.md` with:
   - Project overview
   - Tech stack
   - Setup instructions
   - Development workflow
5. Write `CONTRIBUTING.md` with:
   - Code style guidelines
   - Git workflow (feature branches, PRs)
   - Testing requirements
6. Enable branch protection on `main`:
   - Require PR reviews
   - Require status checks to pass
   - Require branches to be up to date

**Estimated Effort:** 4 hours

---

#### User Story 0.1.5: Implement Git Repository Hygiene

**As a developer**, I want a clean Git repository so that it's maintainable and secure.

**Acceptance Criteria:**
- [ ] Pre-commit hooks installed (detect secrets, large files)
- [ ] `.gitattributes` configured for line endings
- [ ] Repository cleanliness documented in `CONTRIBUTING.md`
- [ ] CI check for repository cleanliness

**Tasks:**
1. Install pre-commit framework:
   ```bash
   pip install pre-commit
   ```
2. Create `.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v4.4.0
       hooks:
         - id: check-added-large-files  # Prevent large files (>500KB)
         - id: check-merge-conflict
         - id: check-yaml
         - id: end-of-file-fixer
         - id: trailing-whitespace
     - repo: https://github.com/Yelp/detect-secrets
       rev: v1.4.0
       hooks:
         - id: detect-secrets  # Prevent secrets in code
   ```
3. Create `.gitattributes`:
   ```
   * text=auto
   *.py text eol=lf
   *.js text eol=lf
   *.ts text eol=lf
   *.md text eol=lf
   ```
4. Document in `CONTRIBUTING.md`:
   - What should be in Git (source code, docs, configs)
   - What should NOT be in Git (secrets, large files, generated files)
5. Add CI check:
   ```yaml
   - name: Check for secrets
     run: detect-secrets scan --baseline .secrets.baseline
   ```

**Estimated Effort:** 0.5 days

---

#### User Story 0.1.6: Establish Legal/Licensing Framework

**As a developer**, I want proper licensing so that the project is legally compliant.

**Acceptance Criteria:**
- [ ] LICENSE file added to repository
- [ ] Copyright headers added to all source files
- [ ] NOTICE file created for third-party attributions
- [ ] CI check for license compliance

**Tasks:**
1. Choose license (recommend: Apache 2.0 for commercial SaaS)
2. Add LICENSE file to repository root
3. Add copyright headers to all source files:
   ```python
   # Copyright 2025 DentalAI
   # Licensed under the Apache License, Version 2.0
   ```
4. Create NOTICE file:
   ```
   DentalAI
   Copyright 2025 DentalAI
   
   This product includes software developed by:
   - LangChain (MIT License)
   - FastAPI (MIT License)
   - React (MIT License)
   ...
   ```
5. Add CI check with `licensecheck`:
   ```bash
   pip install licensecheck
   licensecheck --zero
   ```

**Estimated Effort:** 0.5 days

---

#### User Story 0.2: Set Up Local Development Environment

**As a developer**, I want a Docker Compose setup so that I can run the entire stack locally.

**Acceptance Criteria:**
- [ ] `docker-compose.yml` includes all services:
  - PostgreSQL 15
  - Redis 7.0
  - Odoo Community 17.0
  - Backend (FastAPI)
  - Frontend (React)
- [ ] All services start successfully with `docker-compose up`
- [ ] Backend can connect to PostgreSQL and Redis
- [ ] Frontend can connect to Backend
- [ ] Odoo is accessible at `http://localhost:8069`

**Tasks:**
1. Create `docker-compose.yml`:
   ```yaml
   version: '3.8'
   services:
     postgres:
       image: postgres:15
       environment:
         POSTGRES_DB: dentalai
         POSTGRES_USER: dentalai
         POSTGRES_PASSWORD: dentalai
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
     
     redis:
       image: redis:7.0
       ports:
         - "6379:6379"
     
     odoo:
       image: odoo:17.0
       depends_on:
         - postgres
       environment:
         - HOST=postgres
         - USER=dentalai
         - PASSWORD=dentalai
       ports:
         - "8069:8069"
       volumes:
         - odoo_data:/var/lib/odoo
     
     backend:
       build: ./backend
       depends_on:
         - postgres
         - redis
       environment:
         - DATABASE_URL=postgresql://dentalai:dentalai@postgres:5432/dentalai
         - REDIS_URL=redis://redis:6379
       ports:
         - "8000:8000"
       volumes:
         - ./backend:/app
     
     frontend:
       build: ./frontend
       depends_on:
         - backend
       environment:
         - VITE_API_URL=http://localhost:8000
       ports:
         - "5173:5173"
       volumes:
         - ./frontend:/app
   
   volumes:
     postgres_data:
     odoo_data:
   ```
2. Create `backend/Dockerfile`
3. Create `frontend/Dockerfile`
4. Test `docker-compose up`
5. Verify all services are running
6. Document setup in `README.md`

**Estimated Effort:** 4 hours

---

#### User Story 0.3: Set Up AWS Infrastructure

**As a developer**, I want AWS infrastructure provisioned so that I can deploy the MVP.

**Acceptance Criteria:**
- [ ] AWS account created
- [ ] EKS cluster provisioned
- [ ] RDS PostgreSQL instance provisioned
- [ ] ElastiCache Redis instance provisioned
- [ ] S3 bucket for static assets
- [ ] CloudFront CDN configured
- [ ] AWS Secrets Manager configured
- [ ] Infrastructure documented in `/docs/aws-infrastructure.md`

**Tasks:**
1. Create AWS account (or use existing)
2. Provision EKS cluster:
   - 3 nodes (t3.medium)
   - Auto-scaling enabled
3. Provision RDS PostgreSQL 15:
   - db.t3.medium
   - Multi-AZ for high availability
4. Provision ElastiCache Redis 7.0:
   - cache.t3.micro
5. Create S3 bucket for static assets
6. Configure CloudFront CDN
7. Set up AWS Secrets Manager:
   - Database credentials
   - Redis credentials
   - LLM API keys
8. Document infrastructure in `/docs/aws-infrastructure.md`

**Estimated Effort:** 1 day

---

#### User Story 0.4: Set Up CI/CD Pipeline & Deployment Strategy

**As a developer**, I want a CI/CD pipeline so that code is automatically tested and deployed.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow for backend:
  - Lint (ruff, mypy)
  - Test (pytest with coverage)
  - Build Docker image
  - Push to AWS ECR
- [ ] GitHub Actions workflow for frontend:
  - Lint (eslint, tsc)
  - Test (vitest with coverage)
  - Build Docker image
  - Push to AWS ECR
- [ ] Deployment workflow:
  - Deploy to Staging on merge to `main`
  - Deploy to Production on tag push
- [ ] Blue-green deployment strategy implemented
- [ ] Automated smoke tests run after deployment
- [ ] Rollback procedure documented and tested
- [ ] All workflows documented in `/docs/cicd.md`

**Tasks:**
1. Create `.github/workflows/backend-ci.yml`:
   - Run ruff, mypy
   - Run pytest with coverage (≥80%)
   - Build Docker image
   - Push to AWS ECR
2. Create `.github/workflows/frontend-ci.yml`:
   - Run eslint, tsc
   - Run vitest with coverage (≥80%)
   - Build Docker image
   - Push to AWS ECR
3. Create `.github/workflows/deploy-staging.yml`:
   - Trigger on merge to `main`
   - Deploy to EKS Staging namespace
4. Create `.github/workflows/deploy-production.yml`:
   - Trigger on tag push (e.g., `v1.0.0`)
   - Deploy to EKS Production namespace
5. Implement blue-green deployment:
   - Deploy new version to "green" environment
   - Run smoke tests
   - Switch traffic from "blue" to "green"
   - Keep "blue" for rollback
6. Add smoke tests:
   ```bash
   # Test health endpoint
   curl -f http://backend/health || exit 1
   
   # Test authentication
   curl -f http://backend/auth/login -d '{"email":"test@example.com","password":"test"}' || exit 1
   ```
7. Document rollback procedure:
   ```bash
   # Rollback to previous version
   kubectl rollout undo deployment/backend
   
   # Verify rollback
   kubectl rollout status deployment/backend
   ```
8. Document workflows in `/docs/cicd.md`

**Estimated Effort:** 2 days

---

#### User Story 0.5: Set Up Monitoring and Logging

**As a developer**, I want monitoring and logging so that I can observe system health.

**Acceptance Criteria:**
- [ ] Prometheus deployed to EKS
- [ ] Grafana deployed to EKS with dashboards
- [ ] ELK Stack deployed to EKS
- [ ] Structured logging implemented in backend
- [ ] Metrics exported from backend
- [ ] Alerts configured in Prometheus Alertmanager
- [ ] Monitoring documented in `/docs/monitoring.md`

**Tasks:**
1. Deploy Prometheus to EKS (Helm chart)
2. Deploy Grafana to EKS (Helm chart)
3. Create Grafana dashboards:
   - System Overview (requests/min, error rate, latency)
   - Service Health (CPU, memory, disk)
4. Deploy ELK Stack to EKS (Helm chart)
5. Implement structured logging in backend (structlog)
6. Export Prometheus metrics from backend (prometheus-fastapi-instrumentator)
7. Configure Prometheus Alertmanager:
   - High error rate alert
   - High latency alert
   - Service down alert
8. Document monitoring in `/docs/monitoring.md`

**Estimated Effort:** 1 day

---

### Epic 0.6: Backup & Disaster Recovery (Week 0.5, 3 days)

**Goal:** Implement automated backups, test restoration procedures, and create a disaster recovery plan to protect against data loss.

#### User Story 0.6.1: Implement Automated Database Backups

**As a developer**, I want automated database backups so that data is protected against loss.

**Acceptance Criteria:**
- [ ] PostgreSQL backups run daily at 2 AM UTC
- [ ] Backups stored in S3 with encryption (AWS KMS)
- [ ] Backup retention: 30 days daily, 12 months monthly
- [ ] Backup monitoring with CloudWatch alerts
- [ ] Backup documented in `/docs/backups.md`

**Tasks:**
1. Configure AWS RDS automated backups:
   - Backup window: 2-3 AM UTC
   - Retention: 30 days
2. Set up manual backups to S3:
   ```bash
   #!/bin/bash
   # scripts/backup_database.sh
   TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
   pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | \
     gzip | \
     aws s3 cp - s3://dentalai-backups/postgres/daily/$TIMESTAMP.sql.gz \
       --sse aws:kms --sse-kms-key-id $KMS_KEY_ID
   
   echo "Backup completed: $TIMESTAMP"
   ```
3. Create cron job for daily backups:
   ```bash
   # Add to crontab
   0 2 * * * /app/scripts/backup_database.sh >> /var/log/backup.log 2>&1
   ```
4. Configure S3 lifecycle policy:
   - Keep daily backups for 30 days
   - Transition to Glacier after 30 days
   - Create monthly backups (first of month)
   - Keep monthly backups for 12 months
5. Set up CloudWatch alarm for backup failures:
   ```python
   # Monitor backup script exit code
   if backup_exit_code != 0:
       send_alert("Database backup failed!")
   ```
6. Document in `/docs/backups.md`:
   - Backup schedule
   - Retention policy
   - S3 bucket structure
   - Monitoring and alerts

**Estimated Effort:** 1 day

---

#### User Story 0.6.2: Implement Automated File Backups

**As a developer**, I want automated file backups so that uploaded files are protected.

**Acceptance Criteria:**
- [ ] S3 versioning enabled for file storage bucket
- [ ] S3 replication to secondary region (disaster recovery)
- [ ] Backup retention: 90 days for old versions
- [ ] Backup documented in `/docs/backups.md`

**Tasks:**
1. Enable S3 versioning on file storage bucket:
   ```bash
   aws s3api put-bucket-versioning \
     --bucket dentalai-files \
     --versioning-configuration Status=Enabled
   ```
2. Configure S3 replication to secondary region (us-west-2):
   ```json
   {
     "Role": "arn:aws:iam::ACCOUNT:role/s3-replication",
     "Rules": [{
       "Status": "Enabled",
       "Priority": 1,
       "Filter": {},
       "Destination": {
         "Bucket": "arn:aws:s3:::dentalai-files-backup",
         "ReplicationTime": {
           "Status": "Enabled",
           "Time": {"Minutes": 15}
         }
       }
     }]
   }
   ```
3. Configure S3 lifecycle policy for old versions:
   ```json
   {
     "Rules": [{
       "Status": "Enabled",
       "NoncurrentVersionExpiration": {"Days": 90}
     }]
   }
   ```
4. Test replication:
   - Upload file to primary bucket
   - Verify file appears in secondary bucket within 15 minutes
5. Document in `/docs/backups.md`:
   - S3 versioning configuration
   - Replication setup
   - Retention policy

**Estimated Effort:** 0.5 days

---

#### User Story 0.6.3: Test Backup Restoration

**As a developer**, I want to test backup restoration so that I know backups work when needed.

**Acceptance Criteria:**
- [ ] Database restoration tested successfully in test environment
- [ ] File restoration tested successfully
- [ ] Restoration time documented (<1 hour for database)
- [ ] Restoration procedure documented in `/docs/disaster-recovery.md`

**Tasks:**
1. Create test environment (separate RDS instance)
2. Restore latest database backup:
   ```bash
   # Download backup from S3
   aws s3 cp s3://dentalai-backups/postgres/daily/latest.sql.gz - | \
     gunzip | \
     psql -h $TEST_DB_HOST -U $DB_USER $DB_NAME
   ```
3. Verify data integrity:
   - Count records in each table
   - Check for data consistency
   - Run sample queries
4. Measure restoration time (should be <1 hour)
5. Test file restoration:
   - Restore specific file version from S3
   - Verify file integrity
6. Document procedure in `/docs/disaster-recovery.md`:
   - Step-by-step restoration instructions
   - Expected restoration time
   - Verification steps

**Estimated Effort:** 0.5 days

---

#### User Story 0.6.4: Create Disaster Recovery Plan

**As a developer**, I want a disaster recovery plan so that we can recover from catastrophic failures.

**Acceptance Criteria:**
- [ ] Disaster recovery plan documented in `/docs/disaster-recovery.md`
- [ ] RTO (Recovery Time Objective) defined: <2 hours
- [ ] RPO (Recovery Point Objective) defined: <24 hours
- [ ] Disaster recovery plan tested in simulation
- [ ] Runbooks created for common disaster scenarios

**Tasks:**
1. Write `/docs/disaster-recovery.md`:
   
   **Disaster Recovery Plan**
   
   **RTO/RPO:**
   - RTO: 2 hours (system back online)
   - RPO: 24 hours (max data loss)
   
   **Disaster Scenarios:**
   
   **Scenario 1: Database Corruption**
   - Detection: Database queries failing, data inconsistencies
   - Recovery:
     1. Put system in maintenance mode
     2. Restore latest backup to new RDS instance
     3. Verify data integrity
     4. Update connection strings to new instance
     5. Take system out of maintenance mode
   - Estimated Time: 1 hour
   
   **Scenario 2: AWS Region Failure**
   - Detection: All AWS services unavailable in primary region
   - Recovery:
     1. Activate secondary region (us-west-2)
     2. Promote read replica to primary
     3. Update DNS to point to secondary region
     4. Verify all services operational
   - Estimated Time: 30 minutes
   
   **Scenario 3: Ransomware Attack**
   - Detection: Files encrypted, ransom note found
   - Recovery:
     1. Isolate affected systems immediately
     2. Restore database from backup (before attack)
     3. Restore files from S3 versioning (before attack)
     4. Scan all systems for malware
     5. Reset all passwords and API keys
   - Estimated Time: 4 hours
   
   **Scenario 4: Accidental Data Deletion**
   - Detection: User reports missing data
   - Recovery:
     1. Identify deletion timestamp
     2. Restore data from backup before deletion
     3. Verify restored data
     4. Communicate with affected users
   - Estimated Time: 30 minutes
   
   **Contact Information:**
   - On-Call Engineer: [Phone]
   - AWS Support: [Case Portal]
   - Database Admin: [Phone]
   
   **Escalation Procedures:**
   - If recovery takes >1 hour, escalate to CTO
   - If data loss >24 hours, escalate to CEO
   - If customer data compromised, notify legal team

2. Conduct disaster recovery simulation:
   - Simulate database failure
   - Execute recovery procedure
   - Measure actual recovery time
   - Document lessons learned

3. Create runbooks for each scenario:
   - Step-by-step instructions
   - Commands to execute
   - Verification steps

4. Review and update plan quarterly

**Estimated Effort:** 1 day

---

### Epic 1: SaaS Foundation & Security (Week 1, 5 days)

**Goal:** Build the multi-tenant SaaS foundation with authentication, authorization, and security features.

#### User Story 1.1: Implement Multi-Tenancy with PostgreSQL RLS

**As a developer**, I want multi-tenancy with Row-Level Security so that tenants' data is isolated.

**Acceptance Criteria:**
- [ ] All tables have `tenant_id` column
- [ ] PostgreSQL RLS policies created for all tables
- [ ] Middleware sets `app.current_tenant` for every request
- [ ] Unit tests verify data isolation
- [ ] RLS documented in `/docs/multi-tenancy.md`

**Tasks:**
1. Add `tenant_id` column to all tables:
   ```python
   class Patient(Base):
       __tablename__ = "patients"
       id = Column(UUID, primary_key=True, default=uuid.uuid4)
       tenant_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
       name = Column(String, nullable=False)
       # ...
   ```
2. Create Alembic migration for `tenant_id` column
3. Enable RLS on all tables:
   ```sql
   ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
   ```
4. Create RLS policies:
   ```sql
   CREATE POLICY tenant_isolation ON patients
   FOR ALL
   USING (tenant_id = current_setting('app.current_tenant')::uuid);
   ```
5. Implement middleware:
   ```python
   @app.middleware("http")
   async def set_tenant_context(request: Request, call_next):
       tenant_id = get_tenant_from_jwt(request)
       async with db.begin():
           await db.execute(
               text("SET LOCAL app.current_tenant = :tenant_id"),
               {"tenant_id": tenant_id}
           )
           response = await call_next(request)
       return response
   ```
6. Write unit tests:
   - Test that user A cannot access user B's data
   - Test that queries are automatically filtered by `tenant_id`
7. Document in `/docs/multi-tenancy.md`

**Estimated Effort:** 1 day

---

#### User Story 1.2: Implement Authentication with FastAPI-Users

**As a user**, I want to register and log in so that I can access the system.

**Acceptance Criteria:**
- [ ] User registration endpoint: `POST /auth/register`
- [ ] User login endpoint: `POST /auth/login`
- [ ] JWT tokens issued on login
- [ ] Password hashing with bcrypt
- [ ] Email verification required
- [ ] Unit tests for auth endpoints
- [ ] API documented in Swagger

**Tasks:**
1. Install FastAPI-Users: `pip install fastapi-users[sqlalchemy]`
2. Configure FastAPI-Users:
   - User model
   - JWT strategy
   - Email verification
3. Create auth endpoints:
   - `POST /auth/register`
   - `POST /auth/login`
   - `POST /auth/logout`
   - `POST /auth/verify-email`
4. Implement password hashing (bcrypt)
5. Implement JWT token generation
6. Write unit tests
7. Document API in Swagger

**Estimated Effort:** 1 day

---

#### User Story 1.3: Implement RBAC with 4 Roles

**As a developer**, I want Role-Based Access Control so that users have appropriate permissions.

**Acceptance Criteria:**
- [ ] 4 roles defined: Super Admin, Clinic Admin, Staff, Read-Only
- [ ] Permissions enforced in every API endpoint
- [ ] Decorator for permission checks: `@require_role("admin")`
- [ ] Unit tests for RBAC
- [ ] RBAC documented in `/docs/rbac.md`

**Tasks:**
1. Define roles in `app/models/user.py`:
   ```python
   class UserRole(str, Enum):
       SUPER_ADMIN = "super_admin"
       CLINIC_ADMIN = "clinic_admin"
       STAFF = "staff"
       READ_ONLY = "read_only"
   ```
2. Add `role` column to `users` table
3. Create permission decorator:
   ```python
   def require_role(*allowed_roles):
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               user = get_current_user()
               if user.role not in allowed_roles:
                   raise HTTPException(status_code=403, detail="Forbidden")
               return await func(*args, **kwargs)
           return wrapper
       return decorator
   ```
4. Apply decorator to endpoints:
   ```python
   @app.post("/patients")
   @require_role(UserRole.CLINIC_ADMIN, UserRole.STAFF)
   async def create_patient(patient: PatientCreate):
       # ...
   ```
5. Write unit tests
6. Document in `/docs/rbac.md`

**Estimated Effort:** 1 day

---

#### User Story 1.4: Implement MFA with TOTP

**As a user**, I want Multi-Factor Authentication so that my account is secure.

**Acceptance Criteria:**
- [ ] MFA setup endpoint: `POST /auth/mfa/setup`
- [ ] MFA verify endpoint: `POST /auth/mfa/verify`
- [ ] MFA mandatory for all users
- [ ] Backup codes generated during setup
- [ ] Unit tests for MFA
- [ ] MFA documented in `/docs/mfa.md`

**Tasks:**
1. Install pyotp: `pip install pyotp`
2. Create MFA setup endpoint:
   ```python
   @app.post("/auth/mfa/setup")
   async def setup_mfa(user: User):
       secret = pyotp.random_base32()
       user.mfa_secret = secret
       await db.commit()
       
       # Generate QR code
       totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
           name=user.email,
           issuer_name="DentalAI"
       )
       qr_code = generate_qr_code(totp_uri)
       
       # Generate backup codes
       backup_codes = [secrets.token_hex(4) for _ in range(10)]
       user.backup_codes = backup_codes
       await db.commit()
       
       return {"qr_code": qr_code, "backup_codes": backup_codes}
   ```
3. Create MFA verify endpoint:
   ```python
   @app.post("/auth/mfa/verify")
   async def verify_mfa(user: User, code: str):
       totp = pyotp.TOTP(user.mfa_secret)
       if totp.verify(code):
           user.mfa_verified = True
           await db.commit()
           return {"success": True}
       raise HTTPException(status_code=401, detail="Invalid code")
   ```
4. Enforce MFA on login
5. Write unit tests
6. Document in `/docs/mfa.md`

**Estimated Effort:** 1 day

---

#### User Story 1.5: Implement Prompt Injection Prevention with Rebuff

**As a developer**, I want prompt injection prevention so that users cannot manipulate agents.

**Acceptance Criteria:**
- [ ] Rebuff integrated into agent input pipeline
- [ ] Suspicious inputs are detected and blocked
- [ ] Alerts sent for detected attacks
- [ ] Unit tests for prompt injection detection
- [ ] Documented in `/docs/prompt-injection-prevention.md`

**Tasks:**
1. Install Rebuff: `pip install rebuff`
2. Configure Rebuff:
   ```python
   from rebuff import Rebuff
   
   rebuff = Rebuff(api_key=REBUFF_API_KEY)
   ```
3. Add Rebuff check to agent input:
   ```python
   async def process_user_message(user_input: str):
       # Check for prompt injection
       result = rebuff.detect_injection(user_input)
       if result.is_injection:
           logger.warning("Prompt injection detected", user_input=user_input)
           send_alert("Prompt injection detected")
           raise HTTPException(status_code=400, detail="Invalid input")
       
       # Process message
       response = await agent.run(user_input)
       return response
   ```
4. Write unit tests with injection examples
5. Document in `/docs/prompt-injection-prevention.md`

**Estimated Effort:** 1 day

---

### Epic 2: Core Agent Architecture (Weeks 2-3, 10 days)

**Goal:** Build the 4 core patient-facing agents (Dana, Michal, Yosef, Sarah) with LangGraph, state management, error handling, and rate limiting.

#### User Story 2.1: Design Agent Architecture with LangGraph

**As a developer**, I want a clear agent architecture so that agents can be built consistently.

**Acceptance Criteria:**
- [ ] Agent architecture diagram created
- [ ] Agent state schema defined (TypedDict)
- [ ] Agent graph structure defined (nodes, edges)
- [ ] Agent definitions documented in `/docs/agent-architecture.md`

**Tasks:**
1. Create agent architecture diagram:
   ```
   User Input
       ↓
   Dana (Coordinator)
       ↓
   ┌───────┬───────┬───────┐
   │       │       │       │
   Michal  Yosef  Sarah  Dana
   (Medical) (Billing) (Scheduling) (General)
       │       │       │       │
       └───────┴───────┴───────┘
               ↓
           Response
   ```
2. Define agent state schema:
   ```python
   from typing import TypedDict, List, Optional
   
   class AgentState(TypedDict):
       messages: List[dict]
       current_agent: str
       patient_id: Optional[str]
       appointment_id: Optional[str]
       invoice_id: Optional[str]
       intent: Optional[str]
       errors: List[dict]
       rate_limit_counters: dict
   ```
3. Define agent graph structure:
   - Nodes: dana, michal, yosef, sarah, end
   - Edges: dana → (michal | yosef | sarah | end)
4. Document in `/docs/agent-architecture.md`

**Estimated Effort:** 1 day

---

(Continuing with remaining User Stories for Epic 2, 3, 4...)

---

## 🚀 PHASE 2: Post-MVP (Weeks 5-13)

**Goal:** Add advanced features including fine-tuned executive agents, Mission Control Dashboard, and self-healing capabilities.

**Deliverables:**
- Fine-tuned executive agents with Israeli law expertise (Tier 2 & 3)
- Mission Control Dashboard with self-healing system
- Executive agents for DentalAI business (Portfolio A)
- Full production deployment with monitoring

**Success Criteria:**
- All 3 tiers (Basic, Professional, Enterprise) fully functional
- Self-healing system resolves 80% of incidents automatically
- Executive agents demonstrate 10-17x ROI
- Production-ready with 99.9% uptime SLA

---

### Epic 5: Fine-Tuning Executive Agents (Week 5, 5 days)

**Goal:** Fine-tune Llama 3.1 8B on Israeli law corpus to create domain-expert executive agents.

#### User Story 5.1: Collect and Prepare Israeli Law Dataset

**As a developer**, I want a dataset of Israeli law so that I can fine-tune models.

**Acceptance Criteria:**
- [ ] Dataset collected from public sources:
  - Tax Authority (VAT, income tax)
  - Knesset (labor law, health regulations)
  - Ministry of Health (dental clinic regulations)
- [ ] Dataset formatted as instruction-tuning examples:
  - Input: Question about law
  - Output: Answer with legal citation
- [ ] 5,000-10,000 examples collected
- [ ] Dataset stored in `/datasets/israeli_law/`
- [ ] Dataset documented in `/docs/israeli-law-dataset.md`

**Tasks:**
1. Scrape Tax Authority website for VAT and income tax information
2. Use Knesset Open Data API for labor law
3. Scrape Ministry of Health for dental regulations
4. Format as instruction-tuning examples:
   ```json
   {
     "instruction": "What is the VAT rate in Israel?",
     "input": "",
     "output": "The VAT rate in Israel is 17% as of 2023, as specified in the Value Added Tax Law, 5736-1975."
   }
   ```
5. Collect 5,000-10,000 examples
6. Split into train (80%), validation (10%), test (10%)
7. Store in `/datasets/israeli_law/`
8. Document in `/docs/israeli-law-dataset.md`

**Estimated Effort:** 2 days

---

#### User Story 5.2: Fine-Tune Llama 3.1 8B with LoRA

**As a developer**, I want a fine-tuned model so that executive agents have Israeli law expertise.

**Acceptance Criteria:**
- [ ] Llama 3.1 8B fine-tuned with LoRA using Unsloth
- [ ] Training loss converges
- [ ] Validation accuracy ≥85%
- [ ] Model saved to `/models/llama-3.1-8b-israeli-law/`
- [ ] Fine-tuning documented in `/docs/fine-tuning.md`

**Tasks:**
1. Install Unsloth: `pip install unsloth`
2. Load Llama 3.1 8B base model
3. Configure LoRA:
   ```python
   from unsloth import FastLanguageModel
   
   model, tokenizer = FastLanguageModel.from_pretrained(
       model_name="unsloth/llama-3.1-8b-bnb-4bit",
       max_seq_length=2048,
       dtype=None,
       load_in_4bit=True,
   )
   
   model = FastLanguageModel.get_peft_model(
       model,
       r=16,  # LoRA rank
       target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
       lora_alpha=16,
       lora_dropout=0.05,
       bias="none",
       use_gradient_checkpointing=True,
   )
   ```
4. Load dataset
5. Train model:
   ```python
   from transformers import TrainingArguments, Trainer
   
   trainer = Trainer(
       model=model,
       args=TrainingArguments(
           per_device_train_batch_size=4,
           gradient_accumulation_steps=4,
           warmup_steps=10,
           max_steps=1000,
           learning_rate=2e-4,
           fp16=True,
           logging_steps=10,
           output_dir="outputs",
       ),
       train_dataset=train_dataset,
       eval_dataset=val_dataset,
   )
   
   trainer.train()
   ```
6. Evaluate on test set
7. Save model to `/models/llama-3.1-8b-israeli-law/`
8. Document in `/docs/fine-tuning.md`

**Estimated Effort:** 2 days

---

#### User Story 5.3: Deploy Fine-Tuned Model with vLLM

**As a developer**, I want the fine-tuned model deployed so that agents can use it.

**Acceptance Criteria:**
- [ ] vLLM server deployed on AWS g5.xlarge
- [ ] Model loaded and serving requests
- [ ] API endpoint: `POST /v1/completions`
- [ ] Latency <500ms for 100-token responses
- [ ] Deployment documented in `/docs/vllm-deployment.md`

**Tasks:**
1. Provision AWS g5.xlarge instance
2. Install vLLM: `pip install vllm`
3. Start vLLM server:
   ```bash
   vllm serve /models/llama-3.1-8b-israeli-law \
     --host 0.0.0.0 \
     --port 8000 \
     --tensor-parallel-size 1
   ```
4. Test API:
   ```python
   import requests
   
   response = requests.post(
       "http://vllm-server:8000/v1/completions",
       json={
           "model": "llama-3.1-8b-israeli-law",
           "prompt": "What is the VAT rate in Israel?",
           "max_tokens": 100,
       }
   )
   print(response.json())
   ```
5. Measure latency (should be <500ms)
6. Document in `/docs/vllm-deployment.md`

**Estimated Effort:** 1 day

---

### Epic 6: Executive Agents - Portfolio B (Weeks 6-7, 10 days)

**Goal:** Build 7 executive agents for dental practice management (Tier 2 & 3).

(User Stories 6.1-6.7 for CFO, CHRO, CMO, COO, CLO, CSO, Practice Administrator agents...)

---

### Epic 7: Mission Control Dashboard (Weeks 8-9, 10 days)

**Goal:** Build Mission Control Dashboard with MVP (Week 8) and Full Vision with Self-Healing (Week 9).

(User Stories 7.1-7.8 for dashboard components, self-healing agents...)

---

### Epic 8: Executive Agents - Portfolio A (Week 10, 5 days)

**Goal:** Build 7 executive agents for DentalAI business management (internal use).

(User Stories 8.1-8.7 for CPO, CRO, CCO, CFO, CPO (HR), COO, CSO agents...)

---

### Epic 9: Conversational Interfaces (Week 11, 5 days)

**Goal:** Implement WhatsApp, Telegram, and Web Chat interfaces.

(User Stories 9.1-9.3 for WhatsApp, Telegram, Web Chat...)

---

### Epic 10: Knowledge Management & Analytics (Week 12, 5 days)

**Goal:** Build Knowledge Cards system and Analytics Dashboard.

(User Stories 10.1-10.2 for Knowledge Cards, Analytics...)

---

### Epic 11: Testing, Security Hardening & Deployment (Week 13, 5.5 days)

**Goal:** Comprehensive testing, security hardening, and production deployment.

(User Stories 11.1-11.5 for E2E testing, penetration testing, production deployment...)

---

## Appendix A: Technology Stack Summary

**Frontend:**
- React 18 + TypeScript
- shadcn/ui (Tailwind CSS + Radix UI)
- Zustand (state management)
- TanStack Query (API client)
- Vitest + Playwright (testing)

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy 2.0 + Alembic
- FastAPI-Users (auth)
- Celery + Redis (background jobs)
- pytest (testing)

**Databases:**
- PostgreSQL 15 (primary)
- Redis 7.0 (cache)
- Neo4j 5.0 (causal memory)
- Pinecone (vector DB)

**AI/ML:**
- Claude Sonnet 3.5 (primary LLM)
- Llama 3.1 8B (fine-tuned, small models)
- LangGraph (agent framework)
- Sentence-BERT (embeddings)

**Infrastructure:**
- AWS (EKS, RDS, ElastiCache, S3, CloudFront)
- Kubernetes
- Prometheus + Grafana
- ELK Stack

---

## Appendix B: Success Metrics

**MVP Success Metrics:**
- [ ] 10 pilot customers onboarded
- [ ] 100 concurrent users supported
- [ ] <2s agent response time (p95)
- [ ] 99.9% uptime
- [ ] <1% error rate

**Post-MVP Success Metrics:**
- [ ] 50 Enterprise customers (₪225,000/month revenue)
- [ ] Self-healing resolves 80% of incidents
- [ ] Executive agents demonstrate 10-17x ROI
- [ ] 99.9% uptime SLA met
- [ ] Customer satisfaction ≥4.5/5

---

## Appendix C: Risk Mitigation

**Technical Risks:**
1. **LLM API costs exceed budget**
   - Mitigation: Use small models for simple tasks, cache responses
2. **Fine-tuning doesn't improve accuracy**
   - Mitigation: Fall back to RAG over Israeli law corpus
3. **Self-healing causes more problems**
   - Mitigation: Implement Human-in-the-Loop approval for critical actions

**Business Risks:**
1. **Customers don't adopt Executive Agents**
   - Mitigation: Offer free trial, demonstrate ROI with case studies
2. **Competitors launch similar product**
   - Mitigation: Focus on Israeli market expertise, fast iteration

---

**END OF WORK PLAN V14.0**

---

**Document Version:** 14.0  
**Last Updated:** 2025-10-02  
**Status:** Final - Framework-Compliant  
**Total Duration:** 16 weeks (4 months)  
**Total Epics:** 12  
**Total User Stories:** 100+  
**Target:** Working MVP on AWS + Full Production System
