# 🏗️ DentaFlow Phase 2 - מסמך הקשרים טכניים להמשך פיתוח

**אסטרטגיה:** Full PMS Strategy  
**תאריך:** 8 אוקטובר 2025  
**גרסה:** 2.0  
**מטרה:** מסמך טכני מקיף לפיתוח Phase 2 - בניית PMS מלא

---

## 📋 תוכן עניינים

### [חלק 1: מצב נוכחי - Phase 1 Achievements](#part1)
1.1 מה השגנו ב-Phase 1  
1.2 ארכיטקטורה נוכחית  
1.3 Technology Stack קיים  
1.4 נתונים ואינטגרציות

### [חלק 2: מצב יעד - Phase 2 Goals](#part2)
2.1 Full PMS Vision  
2.2 ארכיטקטורה יעד  
2.3 Technology Stack יעד  
2.4 תכונות חדשות

### [חלק 3: ארכיטקטורה טכנית מפורטת](#part3)
3.1 Backend Architecture  
3.2 Frontend Architecture  
3.3 Database Architecture  
3.4 Integration Architecture  
3.5 Security Architecture

### [חלק 4: Data Models & APIs](#part4)
4.1 Core Data Models  
4.2 API Specifications  
4.3 Integration Points  
4.4 Data Flow Diagrams

### [חלק 5: תכונות חדשות - Technical Specs](#part5)
5.1 Patient Portal  
5.2 Clinical Charting  
5.3 RCM Automation  
5.4 Mobile Applications  
5.5 Growth Tools

### [חלק 6: Security & Compliance](#part6)
6.1 Israeli Regulations  
6.2 HIPAA Compliance  
6.3 Data Protection  
6.4 Audit & Logging

### [חלק 7: Implementation Roadmap](#part7)
7.1 Phase 2.1: Patient Engagement (Months 1-3)  
7.2 Phase 2.2: Clinical Tools (Months 4-6)  
7.3 Phase 2.3: RCM & Billing (Months 7-9)  
7.4 Phase 2.4: Mobile & Growth (Months 10-12)

### [חלק 8: Technical Debt & Refactoring](#part8)
8.1 Known Issues  
8.2 Refactoring Needed  
8.3 Performance Optimization  
8.4 Code Quality

---

<a name="part1"></a>
## 📊 חלק 1: מצב נוכחי - Phase 1 Achievements

### 1.1 מה השגנו ב-Phase 1 ✅

#### Backend Infrastructure (90% Complete)
✅ **FastAPI Backend deployed to AWS EC2**
- Server: `dentaflow.ai:8000`
- Status: Running (PID: 554940)
- Health Check: PASSING
- API Docs: `/docs` accessible

✅ **Odoo Integration Working**
- Connected to: `https://dentaflow.ai` (Odoo 19.0)
- Database: `dental_prod`
- Real data flowing from Odoo
- Models integrated: `res.partner`, `medical.appointment`, `hr.employee`

✅ **AI Agents Implemented**
- **Alex (Receptionist)** - Appointment scheduling, patient communication
- **Marcus (CFO)** - Financial analytics, reporting
- **Sophia (Clinical Director)** - Clinical oversight, quality assurance
- **Supervisor Agent** - Orchestrates multi-agent workflows
- Technology: LangGraph V3, OpenAI GPT-4

✅ **Core APIs Operational**
- `/health` - Health check
- `/api/v1/appointments/today` - Today's appointments
- `/api/v1/dashboard/stats` - Dashboard statistics
- Authentication: JWT + OAuth (partial)

✅ **Bug Fixes (20+)**
- Pydantic v2 compatibility
- SQLAlchemy metadata conflicts
- Import path corrections
- Odoo field mapping
- Dependencies installation

#### Frontend (60% Complete)
⚠️ **Admin Dashboard UI** (not approved)
- React + TypeScript
- Tailwind CSS
- Component library built
- Mock data displayed
- Not connected to live Backend

⚠️ **Onboarding Frontend** (30% complete)
- Exists but not integrated
- No routing logic
- Not connected to main system

❌ **Patient Portal** - Not started

---

### 1.2 ארכיטקטורה נוכחית

```
┌─────────────────────────────────────────────────────────────┐
│                      CURRENT ARCHITECTURE                    │
│                         (Phase 1)                            │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Frontend   │
│ (Not Live)   │
│──────────────│
│ React + TS   │
│ Tailwind CSS │
│ Mock Data    │
└──────────────┘
       │
       │ (Not Connected)
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    Backend (AWS EC2)                          │
│                  dentaflow.ai:8000                           │
│──────────────────────────────────────────────────────────────│
│                                                               │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │   FastAPI      │  │  AI Agents     │  │  Auth Service  ││
│  │   REST API     │  │  (LangGraph)   │  │  (JWT/OAuth)   ││
│  │────────────────│  │────────────────│  │────────────────││
│  │ /health        │  │ Alex           │  │ JWT Tokens     ││
│  │ /appointments  │  │ Marcus         │  │ Google OAuth   ││
│  │ /dashboard     │  │ Sophia         │  │ User Mgmt      ││
│  │ /auth/*        │  │ Supervisor     │  │                ││
│  └────────────────┘  └────────────────┘  └────────────────┘│
│                                                               │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │ Odoo Client    │  │  PostgreSQL    │  │     Redis      ││
│  │────────────────│  │────────────────│  │────────────────││
│  │ OdooClientV2   │  │ users          │  │ (Config but    ││
│  │ API Wrapper    │  │ organizations  │  │  not used)     ││
│  │                │  │ conversations  │  │                ││
│  └────────────────┘  └────────────────┘  └────────────────┘│
│         │                     │                              │
└─────────┼─────────────────────┼──────────────────────────────┘
          │                     │
          ▼                     ▼
┌──────────────────┐   ┌──────────────────┐
│   Odoo System    │   │   PostgreSQL     │
│   (External)     │   │   (Local DB)     │
│──────────────────│   │──────────────────│
│ dental_prod DB   │   │ dentalai DB      │
│──────────────────│   │──────────────────│
│ res.partner      │   │ users            │
│ medical.appt     │   │ organizations    │
│ hr.employee      │   │ (Missing tables) │
│ dental modules   │   │                  │
└──────────────────┘   └──────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    NOT YET DEPLOYED                           │
│──────────────────────────────────────────────────────────────│
│ ❌ Telegram Bot (code exists, not deployed)                  │
│ ❌ Patient Portal (not built)                                │
│ ❌ Mobile Apps (not built)                                   │
│ ❌ WhatsApp Integration (not built)                          │
└──────────────────────────────────────────────────────────────┘
```

---

### 1.3 Technology Stack קיים

#### Backend Stack ✅
```yaml
Language: Python 3.10
Framework: FastAPI 0.104+
ORM: SQLAlchemy 2.0
Database: PostgreSQL 14
Cache: Redis 7.0 (configured, not used)
AI: 
  - OpenAI GPT-4
  - LangChain 0.1.0
  - LangGraph 0.0.20
Authentication: 
  - JWT (python-jose)
  - OAuth 2.0 (Google - partial)
Odoo Integration: 
  - xmlrpc.client (custom OdooClientV2)
Server: 
  - Uvicorn ASGI
  - AWS EC2 (Ubuntu 22.04)
  - Nginx (not configured)
```

#### Frontend Stack ⚠️
```yaml
Language: TypeScript 5.x
Framework: React 18
Build Tool: Vite
Styling: Tailwind CSS 3.x
State Management: React Context (basic)
HTTP Client: Fetch API
Routing: React Router (not fully configured)
UI Components: Custom components
Status: Not deployed, not connected to Backend
```

#### Infrastructure ⚠️
```yaml
Cloud: AWS
Compute: EC2 (t3.medium)
OS: Ubuntu 22.04
Domain: dentaflow.ai
SSL: Not configured
Load Balancer: Not configured
CDN: Not configured
Monitoring: Not configured
Logging: Basic file logging
Backup: Not configured
```

---

### 1.4 נתונים ואינטגרציות

#### Odoo Integration Status ✅

**Connected Models:**
```python
# ✅ Working
res.partner          # Patients (203 fields)
medical.appointment  # Appointments (58 fields)  
hr.employee          # Dentists/Staff (150+ fields)

# ⚠️ Partially Working
dental.insurance.claim.management  # Insurance (not tested)
medical.patient.disease            # Medical history (not tested)

# ❌ Not Integrated
account.move         # Invoices
product.product      # Treatments/Services
stock.picking        # Inventory
```

**Known Issues:**
1. **Appointment Creation Fails**
   - Error: `constraint on doctor_id`
   - Workaround: Using mock data
   - Status: Needs Odoo investigation

2. **Field Mapping Incomplete**
   - Missing: `duration`, `patient_status`
   - Workaround: Removed from API
   - Status: Need to map correct Odoo fields

**Data Flow (Current):**
```
Odoo (Source of Truth)
  ↓
OdooClientV2 (Python wrapper)
  ↓
FastAPI Endpoints
  ↓
(Frontend not connected)
```

#### PostgreSQL Database ⚠️

**Existing Tables:**
```sql
users                    -- ✅ User accounts
organizations            -- ✅ Clinic entities
conversations            -- ⚠️ Assumed (not verified)
messages                 -- ⚠️ Assumed (not verified)
```

**Missing Critical Tables:**
```sql
organization_memberships -- ❌ User-Org relationships
clinic_settings          -- ❌ Clinic configuration
treatment_prices         -- ❌ Pricing catalog
appointments_local       -- ❌ Local appointment cache
audit_logs               -- ❌ Audit trail
consent_records          -- ❌ Patient consents
```

**Status:** Database schema incomplete, needs migration.

---

### 1.5 Phase 1 Completion Summary

| Component | Status | % Complete |
|-----------|--------|------------|
| Backend API | ✅ Deployed | 90% |
| Odoo Integration | ✅ Working | 85% |
| AI Agents | ✅ Implemented | 85% |
| PostgreSQL | ⚠️ Partial | 50% |
| Authentication | ⚠️ Partial | 60% |
| Frontend | ⚠️ Not Live | 30% |
| Telegram Bot | ❌ Not Deployed | 40% |
| Patient Portal | ❌ Not Started | 0% |
| Mobile Apps | ❌ Not Started | 0% |
| Compliance | ⚠️ Basic | 40% |

**Overall Phase 1: 60% Complete**

---

<a name="part2"></a>
## 🎯 חלק 2: מצב יעד - Phase 2 Goals

### 2.1 Full PMS Vision

**מטרה:** להפוך את DentaFlow ל-**PMS מלא ומתקדם** שמתחרה עם Dentrix, Planet DDS, ו-tab32.

**ההבדל שלנו:** **AI-Powered PMS** - לא רק PMS עם AI, אלא PMS שה-AI הוא הליבה שלו.

#### Core Pillars של Full PMS:

```
┌────────────────────────────────────────────────────────────┐
│              DENTAFLOW FULL PMS VISION                      │
│                    (Phase 2 Goal)                           │
└────────────────────────────────────────────────────────────┘

         ┌─────────────────────────────────┐
         │   1. PATIENT ENGAGEMENT          │
         │   "Digital Front Door"           │
         │─────────────────────────────────│
         │ • Patient Portal (24/7)          │
         │ • Online Booking                 │
         │ • Digital Forms                  │
         │ • Secure Messaging               │
         │ • Payment Portal                 │
         └─────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
┌────────▼─────────┐   ┌───────────▼──────────┐
│ 2. CLINICAL      │   │ 3. PRACTICE          │
│    EXCELLENCE    │   │    MANAGEMENT        │
│──────────────────│   │──────────────────────│
│ • Odontogram     │   │ • Scheduling         │
│ • Perio Chart    │   │ • Staff Management   │
│ • Treatment Plan │   │ • Inventory          │
│ • Medical History│   │ • Reporting          │
│ • AI Diagnosis   │   │ • Analytics          │
└──────────────────┘   └──────────────────────┘
         │                         │
         └────────────┬────────────┘
                      │
         ┌────────────▼─────────────┐
         │   4. REVENUE CYCLE       │
         │      MANAGEMENT          │
         │──────────────────────────│
         │ • Insurance Claims       │
         │ • Eligibility Check      │
         │ • Payment Processing     │
         │ • Billing Automation     │
         │ • Collections            │
         └──────────────────────────┘
                      │
         ┌────────────▼─────────────┐
         │   5. GROWTH & MARKETING  │
         │──────────────────────────│
         │ • Reputation Management  │
         │ • Membership Plans       │
         │ • Referral Tracking      │
         │ • Marketing Automation   │
         └──────────────────────────┘
                      │
         ┌────────────▼─────────────┐
         │   6. AI INTELLIGENCE     │
         │   (Our Differentiator)   │
         │──────────────────────────│
         │ • Alex (Receptionist)    │
         │ • Marcus (CFO)           │
         │ • Sophia (Clinical Dir)  │
         │ • AI Diagnosis Support   │
         │ • Predictive Analytics   │
         └──────────────────────────┘
```

---

### 2.2 ארכיטקטורה יעד (Phase 2)

```
┌──────────────────────────────────────────────────────────────────┐
│                   TARGET ARCHITECTURE (Phase 2)                   │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────── FRONTEND LAYER ────────────────────────────┐
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Patient    │  │    Admin     │  │   Mobile     │           │
│  │   Portal     │  │  Dashboard   │  │    Apps      │           │
│  │──────────────│  │──────────────│  │──────────────│           │
│  │ React SPA    │  │ React SPA    │  │ React Native │           │
│  │ Tailwind     │  │ Tailwind     │  │ iOS/Android  │           │
│  │ Vite         │  │ Vite         │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│         │                  │                  │                   │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │
                    │   (Nginx/Kong)  │
                    │─────────────────│
                    │ Rate Limiting   │
                    │ Load Balancing  │
                    │ SSL/TLS         │
                    └─────────────────┘
                             │
┌────────────────────────────┴──────────────────────────────────────┐
│                      BACKEND LAYER (FastAPI)                       │
│────────────────────────────────────────────────────────────────────│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                    API Endpoints                              ││
│  │──────────────────────────────────────────────────────────────││
│  │ /auth/*         - Authentication & Authorization             ││
│  │ /patients/*     - Patient management                         ││
│  │ /appointments/* - Scheduling & calendar                      ││
│  │ /clinical/*     - Charting, treatment plans                  ││
│  │ /billing/*      - Invoices, payments, insurance              ││
│  │ /staff/*        - Staff & provider management                ││
│  │ /reports/*      - Analytics & reporting                      ││
│  │ /ai/*           - AI agent interactions                      ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Business   │  │  AI Agents   │  │    Auth      │           │
│  │    Logic     │  │  (LangGraph) │  │   Service    │           │
│  │──────────────│  │──────────────│  │──────────────│           │
│  │ Appointments │  │ Alex         │  │ JWT          │           │
│  │ Billing      │  │ Marcus       │  │ OAuth 2.0    │           │
│  │ Clinical     │  │ Sophia       │  │ RBAC         │           │
│  │ Inventory    │  │ Supervisor   │  │ MFA          │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Odoo       │  │  PostgreSQL  │  │    Redis     │           │
│  │   Client     │  │   Service    │  │    Cache     │           │
│  │──────────────│  │──────────────│  │──────────────│           │
│  │ OdooClientV2 │  │ SQLAlchemy   │  │ Session      │           │
│  │ API Wrapper  │  │ Alembic      │  │ Cache        │           │
│  │              │  │              │  │ Queue        │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│         │                  │                  │                   │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Odoo System    │  │   PostgreSQL     │  │      Redis       │
│   (External)     │  │   (Primary DB)   │  │   (Cache/Queue)  │
│──────────────────│  │──────────────────│  │──────────────────│
│ dental_prod      │  │ dentalai         │  │ Sessions         │
│──────────────────│  │──────────────────│  │ Cache            │
│ res.partner      │  │ users            │  │ Celery Queue     │
│ medical.appt     │  │ organizations    │  │                  │
│ hr.employee      │  │ memberships      │  │                  │
│ dental modules   │  │ clinic_settings  │  │                  │
│                  │  │ treatment_prices │  │                  │
│                  │  │ appointments     │  │                  │
│                  │  │ audit_logs       │  │                  │
│                  │  │ consent_records  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
          │                  │                  
          └──────────────────┴──────────────────────────────────────┐
                                                                     │
┌────────────────────── INTEGRATION LAYER ─────────────────────────▼┐
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Telegram   │  │   WhatsApp   │  │    Stripe    │           │
│  │     Bot      │  │     API      │  │   Payments   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Email      │  │     SMS      │  │   Google     │           │
│  │   Service    │  │   Service    │  │    OAuth     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────── INFRASTRUCTURE LAYER ───────────────────────┐
│                                                                    │
│  AWS Cloud                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │     EC2      │  │     RDS      │  │  ElastiCache │           │
│  │   Backend    │  │  PostgreSQL  │  │    Redis     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │      S3      │  │  CloudFront  │  │  Route 53    │           │
│  │   Storage    │  │     CDN      │  │     DNS      │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  CloudWatch  │  │   Secrets    │  │     WAF      │           │
│  │  Monitoring  │  │   Manager    │  │  Firewall    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

### 2.3 Technology Stack יעד

#### Backend Stack (Enhanced) 🎯

```yaml
Language: Python 3.11+
Framework: FastAPI 0.110+
ORM: SQLAlchemy 2.0
Database: 
  - PostgreSQL 15 (Primary)
  - Odoo PostgreSQL (External, read-only)
Cache: Redis 7.2 (Active usage)
Queue: Celery + Redis
AI: 
  - OpenAI GPT-4 Turbo
  - LangChain 0.1.x
  - LangGraph 0.0.30+
  - LangSmith (monitoring)
Authentication: 
  - JWT (python-jose)
  - OAuth 2.0 (Google, Microsoft)
  - MFA (TOTP)
Odoo Integration: 
  - xmlrpc.client (OdooClientV2)
  - Webhook listeners
Payment: 
  - Stripe API
  - Israeli payment gateways (Tranzila, etc.)
Communication:
  - Telegram Bot API
  - WhatsApp Business API
  - SendGrid (Email)
  - Twilio (SMS)
Server: 
  - Uvicorn ASGI
  - Gunicorn (production)
  - AWS EC2 / ECS (containerized)
API Gateway: Nginx / Kong
Monitoring:
  - Sentry (error tracking)
  - CloudWatch (AWS)
  - Prometheus + Grafana
Testing:
  - Pytest
  - Pytest-asyncio
  - Coverage.py
```

#### Frontend Stack (Enhanced) 🎯

```yaml
Language: TypeScript 5.x
Framework: React 18
Build Tool: Vite 5.x
Styling: 
  - Tailwind CSS 3.x
  - Shadcn/ui components
State Management: 
  - Zustand (lightweight)
  - React Query (server state)
HTTP Client: 
  - Axios
  - React Query
Routing: React Router 6
Form Handling: React Hook Form + Zod
Charts: Recharts / Chart.js
Real-time: Socket.IO client
Authentication: 
  - JWT storage (httpOnly cookies)
  - OAuth flow
Testing:
  - Vitest
  - React Testing Library
  - Playwright (E2E)
```

#### Mobile Stack (New) 🎯

```yaml
Framework: React Native 0.73+
Language: TypeScript 5.x
Navigation: React Navigation 6
State: Zustand + React Query
UI: React Native Paper
Push Notifications: 
  - Firebase Cloud Messaging
  - Apple Push Notification Service
Biometrics: react-native-biometrics
Storage: AsyncStorage + SQLite
Testing: Jest + Detox
```

#### Infrastructure (Enhanced) 🎯

```yaml
Cloud: AWS
Compute: 
  - EC2 (t3.large) or ECS Fargate
  - Auto Scaling Group
Database: 
  - RDS PostgreSQL 15 (Multi-AZ)
  - Read Replicas
Cache: ElastiCache Redis (cluster mode)
Storage: S3 (patient documents, images)
CDN: CloudFront
DNS: Route 53
Load Balancer: Application Load Balancer
SSL: ACM (AWS Certificate Manager)
Secrets: AWS Secrets Manager
Monitoring: CloudWatch + Sentry
Logging: CloudWatch Logs
Backup: Automated RDS snapshots + S3
CI/CD: GitHub Actions
IaC: Terraform or CloudFormation
```

---

### 2.4 תכונות חדשות - Overview

#### Phase 2.1: Patient Engagement (Months 1-3)

**1. Patient Portal** 🆕
- User registration & login
- Profile management
- View appointments
- View treatment plans
- View invoices & payments
- Online payment
- Secure messaging with clinic
- Document upload
- Medical history forms

**2. Online Booking** 🆕
- 24/7 appointment scheduling
- Real-time availability
- Provider selection
- Service selection
- Automated confirmation
- Calendar integration (Google, Apple)

**3. Digital Forms** 🆕
- Medical history
- Consent forms
- Insurance information
- Pre-appointment questionnaires
- Auto-fill from previous visits
- E-signature

**4. Communication Hub** 🆕
- SMS reminders
- Email notifications
- Telegram integration (deploy existing bot)
- WhatsApp messages
- In-app messaging

---

#### Phase 2.2: Clinical Tools (Months 4-6)

**1. Odontogram (Interactive Tooth Chart)** 🆕
- Visual tooth chart (32 teeth)
- Condition marking (caries, filling, crown, etc.)
- Treatment history per tooth
- Color-coded status
- Click to add notes
- Print/export

**2. Periodontal Charting** 🆕
- 6-point probing depths
- Bleeding on probing
- Gingival recession
- Furcation involvement
- Mobility assessment
- Progress tracking over time

**3. Treatment Planning** 🆕
- Visual treatment plan builder
- Drag & drop procedures
- Cost estimation
- Insurance coverage calculation
- Alternative treatment options
- Patient presentation mode
- E-signature approval

**4. Clinical Notes** 🆕
- SOAP notes template
- Voice-to-text
- Templates for common procedures
- Attach images/X-rays
- ICD-10 coding
- Auto-save

**5. Imaging Integration** 🆕
- DICOM viewer
- X-ray management
- Intraoral photos
- Before/after comparisons
- Annotations
- Share with patient portal

---

#### Phase 2.3: RCM & Billing (Months 7-9)

**1. Insurance Claims** 🆕
- Electronic claim submission
- Eligibility verification (real-time)
- Pre-authorization requests
- Claim tracking
- Denial management
- Resubmission workflow
- Israeli health funds integration (Clalit, Maccabi, etc.)

**2. Billing Automation** 🆕
- Auto-generate invoices
- Payment plans
- Recurring billing
- Late payment reminders
- Collections workflow
- Refund processing

**3. Payment Processing** 🆕
- Credit card (Stripe)
- Israeli payment gateways (Tranzila, Cardcom)
- Cash/check tracking
- Split payments (insurance + patient)
- Payment receipts (auto-email)
- Refund processing

**4. Financial Reporting** 🆕
- Revenue reports
- Outstanding balances
- Insurance aging report
- Provider productivity
- Treatment acceptance rate
- Marcus AI insights

---

#### Phase 2.4: Mobile & Growth (Months 10-12)

**1. Mobile Apps** 🆕
- **Patient App:**
  - Book appointments
  - View treatment plans
  - Pay bills
  - Secure messaging
  - Push notifications
  - Biometric login

- **Provider App:**
  - View schedule
  - Access patient charts
  - Clinical notes
  - Approve treatment plans
  - View financials

**2. Growth Tools** 🆕
- **Reputation Management:**
  - Auto-request reviews (Google, Facebook)
  - Review monitoring
  - Response templates
  - Reputation score

- **Membership Plans:**
  - Create custom plans
  - Monthly recurring billing
  - Member benefits tracking
  - Churn analysis

- **Referral Tracking:**
  - Referral source tracking
  - Referral rewards program
  - ROI by marketing channel

- **Marketing Automation:**
  - Email campaigns
  - SMS campaigns
  - Birthday/anniversary messages
  - Recall reminders
  - Re-engagement campaigns

---

<a name="part3"></a>
## 🏗️ חלק 3: ארכיטקטורה טכנית מפורטת

### 3.1 Backend Architecture

#### 3.1.1 Layered Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│                      (API Endpoints)                        │
│────────────────────────────────────────────────────────────│
│  FastAPI Routers:                                           │
│  • /api/v1/auth/*         - Authentication                  │
│  • /api/v1/patients/*     - Patient management              │
│  • /api/v1/appointments/* - Scheduling                      │
│  • /api/v1/clinical/*     - Clinical data                   │
│  • /api/v1/billing/*      - Billing & payments              │
│  • /api/v1/staff/*        - Staff management                │
│  • /api/v1/reports/*      - Reporting                       │
│  • /api/v1/ai/*           - AI agent interactions           │
│                                                              │
│  Middleware:                                                 │
│  • CORS                                                      │
│  • Authentication (JWT)                                      │
│  • Rate Limiting                                             │
│  • Request Logging                                           │
│  • Error Handling                                            │
└────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                     SERVICE LAYER                           │
│                   (Business Logic)                          │
│────────────────────────────────────────────────────────────│
│  Services:                                                   │
│  • AuthService           - User authentication              │
│  • PatientService        - Patient CRUD                     │
│  • AppointmentService    - Scheduling logic                 │
│  • ClinicalService       - Clinical data management         │
│  • BillingService        - Billing & invoicing              │
│  • InsuranceService      - Insurance claims                 │
│  • StaffService          - Staff management                 │
│  • ReportService         - Analytics & reporting            │
│  • AIService             - AI agent orchestration           │
│  • NotificationService   - Email/SMS/Push                   │
│                                                              │
│  Business Rules:                                             │
│  • Appointment validation                                    │
│  • Pricing calculations                                      │
│  • Insurance eligibility                                     │
│  • Access control (RBAC)                                     │
│  • Medical safety checks                                     │
└────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                     DATA ACCESS LAYER                       │
│                    (Repositories)                           │
│────────────────────────────────────────────────────────────│
│  Repositories (PostgreSQL):                                  │
│  • UserRepository                                            │
│  • OrganizationRepository                                    │
│  • PatientRepository                                         │
│  • AppointmentRepository                                     │
│  • TreatmentRepository                                       │
│  • InvoiceRepository                                         │
│  • AuditLogRepository                                        │
│                                                              │
│  Odoo Client:                                                │
│  • OdooClientV2 (wrapper for xmlrpc)                        │
│  • Read-only access to Odoo data                            │
│  • Sync service (Odoo → PostgreSQL)                         │
│                                                              │
│  Cache Layer (Redis):                                        │
│  • Session storage                                           │
│  • Query result caching                                      │
│  • Rate limit counters                                       │
└────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                     PERSISTENCE LAYER                       │
│────────────────────────────────────────────────────────────│
│  PostgreSQL:                                                 │
│  • Primary data store                                        │
│  • SQLAlchemy ORM                                            │
│  • Alembic migrations                                        │
│                                                              │
│  Odoo PostgreSQL:                                            │
│  • External, read-only                                       │
│  • Source of truth for legacy data                          │
│                                                              │
│  Redis:                                                      │
│  • Cache                                                     │
│  • Session store                                             │
│  • Celery message broker                                     │
└────────────────────────────────────────────────────────────┘
```

#### 3.1.2 Directory Structure (Target)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration (Pydantic Settings)
│   │
│   ├── api/                    # API Layer
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies (get_db, get_current_user)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main API router
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── patients.py
│   │           ├── appointments.py
│   │           ├── clinical.py
│   │           ├── billing.py
│   │           ├── staff.py
│   │           ├── reports.py
│   │           └── ai.py
│   │
│   ├── services/               # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── patient_service.py
│   │   ├── appointment_service.py
│   │   ├── clinical_service.py
│   │   ├── billing_service.py
│   │   ├── insurance_service.py
│   │   ├── staff_service.py
│   │   ├── report_service.py
│   │   ├── ai_service.py
│   │   └── notification_service.py
│   │
│   ├── repositories/           # Data Access Layer
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository
│   │   ├── user_repository.py
│   │   ├── organization_repository.py
│   │   ├── patient_repository.py
│   │   ├── appointment_repository.py
│   │   ├── treatment_repository.py
│   │   ├── invoice_repository.py
│   │   └── audit_log_repository.py
│   │
│   ├── models/                 # SQLAlchemy Models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   ├── treatment.py
│   │   ├── invoice.py
│   │   ├── audit_log.py
│   │   └── consent.py
│   │
│   ├── schemas/                # Pydantic Schemas (DTOs)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   ├── clinical.py
│   │   ├── billing.py
│   │   └── common.py
│   │
│   ├── core/                   # Core Utilities
│   │   ├── __init__.py
│   │   ├── security.py         # Password hashing, JWT
│   │   ├── database.py         # DB session management
│   │   ├── cache.py            # Redis client
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── middleware.py       # Custom middleware
│   │
│   ├── integrations/           # External Integrations
│   │   ├── __init__.py
│   │   ├── odoo_client.py      # OdooClientV2
│   │   ├── stripe_client.py    # Stripe payments
│   │   ├── telegram_client.py  # Telegram bot
│   │   ├── whatsapp_client.py  # WhatsApp API
│   │   ├── sendgrid_client.py  # Email
│   │   └── twilio_client.py    # SMS
│   │
│   ├── agents/                 # AI Agents (LangGraph)
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── alex_agent.py       # Receptionist
│   │   ├── marcus_agent.py     # CFO
│   │   ├── sophia_agent.py     # Clinical Director
│   │   ├── supervisor_agent.py # Orchestrator
│   │   └── tools/              # Agent tools
│   │       ├── appointment_tools.py
│   │       ├── patient_tools.py
│   │       └── billing_tools.py
│   │
│   ├── tasks/                  # Background Tasks (Celery)
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── email_tasks.py
│   │   ├── sms_tasks.py
│   │   ├── sync_tasks.py       # Odoo sync
│   │   └── report_tasks.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── validators.py
│       ├── formatters.py
│       └── helpers.py
│
├── alembic/                    # Database Migrations
│   ├── versions/
│   └── env.py
│
├── tests/                      # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── pytest.ini
└── README.md
```

---

### 3.2 Frontend Architecture

#### 3.2.1 Component Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      FRONTEND ARCHITECTURE                  │
│                    (React + TypeScript)                     │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                     │
│                         (Pages)                             │
│────────────────────────────────────────────────────────────│
│  Patient Portal:                                            │
│  • /login              - Login page                         │
│  • /register           - Registration                       │
│  • /dashboard          - Patient dashboard                  │
│  • /appointments       - Appointments list                  │
│  • /book-appointment   - Online booking                     │
│  • /treatment-plans    - Treatment plans                    │
│  • /invoices           - Invoices & payments                │
│  • /messages           - Secure messaging                   │
│  • /profile            - Profile settings                   │
│                                                              │
│  Admin Dashboard:                                            │
│  • /admin/dashboard    - Main dashboard                     │
│  • /admin/calendar     - Appointment calendar               │
│  • /admin/patients     - Patient list                       │
│  • /admin/patient/:id  - Patient details                    │
│  • /admin/clinical     - Clinical charting                  │
│  • /admin/billing      - Billing & invoicing                │
│  • /admin/reports      - Reports & analytics                │
│  • /admin/staff        - Staff management                   │
│  • /admin/settings     - Clinic settings                    │
└────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                     COMPONENT LAYER                         │
│                   (Reusable Components)                     │
│────────────────────────────────────────────────────────────│
│  UI Components (Shadcn/ui):                                 │
│  • Button, Input, Select, Checkbox, etc.                    │
│  • Dialog, Dropdown, Tooltip, Toast                         │
│  • Table, Card, Badge, Avatar                               │
│                                                              │
│  Business Components:                                        │
│  • AppointmentCard                                           │
│  • PatientCard                                               │
│  • TreatmentPlanViewer                                       │
│  • Odontogram (interactive tooth chart)                     │
│  • PerioChart (periodontal charting)                        │
│  • InvoiceViewer                                             │
│  • PaymentForm                                               │
│  • ChatWidget (AI agent)                                     │
│                                                              │
│  Layout Components:                                          │
│  • Header, Sidebar, Footer                                   │
│  • DashboardLayout                                           │
│  • AuthLayout                                                │
└────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                     STATE MANAGEMENT                        │
│                  (Zustand + React Query)                    │
│────────────────────────────────────────────────────────────│
│  Global State (Zustand):                                     │
│  • authStore       - User authentication state              │
│  • uiStore         - UI state (sidebar, theme)              │
│  • notificationStore - Toast notifications                  │
│                                                              │
│  Server State (React Query):                                 │
│  • usePatients()   - Fetch patients                         │
│  • useAppointments() - Fetch appointments                   │
│  • useTreatments() - Fetch treatments                       │
│  • useInvoices()   - Fetch invoices                         │
│  • Automatic caching, refetching, optimistic updates        │
└────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                     API CLIENT LAYER                        │
│                        (Axios)                              │
│────────────────────────────────────────────────────────────│
│  API Client (axios instance):                               │
│  • Base URL configuration                                    │
│  • Request interceptors (add JWT token)                     │
│  • Response interceptors (handle errors)                    │
│  • Retry logic                                               │
│                                                              │
│  API Services:                                               │
│  • authApi.ts      - Login, register, refresh token         │
│  • patientsApi.ts  - Patient CRUD                           │
│  • appointmentsApi.ts - Appointment CRUD                    │
│  • clinicalApi.ts  - Clinical data                          │
│  • billingApi.ts   - Billing & payments                     │
│  • reportsApi.ts   - Reports & analytics                    │
└────────────────────────────────────────────────────────────┘
```

#### 3.2.2 Directory Structure (Target)

```
frontend/
├── src/
│   ├── main.tsx                # App entry point
│   ├── App.tsx                 # Root component
│   ├── vite-env.d.ts
│   │
│   ├── pages/                  # Page Components
│   │   ├── patient/            # Patient Portal
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Appointments.tsx
│   │   │   ├── BookAppointment.tsx
│   │   │   ├── TreatmentPlans.tsx
│   │   │   ├── Invoices.tsx
│   │   │   ├── Messages.tsx
│   │   │   └── Profile.tsx
│   │   │
│   │   └── admin/              # Admin Dashboard
│   │       ├── Dashboard.tsx
│   │       ├── Calendar.tsx
│   │       ├── PatientList.tsx
│   │       ├── PatientDetails.tsx
│   │       ├── ClinicalCharting.tsx
│   │       ├── Billing.tsx
│   │       ├── Reports.tsx
│   │       ├── Staff.tsx
│   │       └── Settings.tsx
│   │
│   ├── components/             # Reusable Components
│   │   ├── ui/                 # UI Components (Shadcn)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── table.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/             # Layout Components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── DashboardLayout.tsx
│   │   │   └── AuthLayout.tsx
│   │   │
│   │   ├── appointments/
│   │   │   ├── AppointmentCard.tsx
│   │   │   ├── AppointmentCalendar.tsx
│   │   │   ├── BookingForm.tsx
│   │   │   └── AppointmentDetails.tsx
│   │   │
│   │   ├── patients/
│   │   │   ├── PatientCard.tsx
│   │   │   ├── PatientForm.tsx
│   │   │   ├── PatientSearch.tsx
│   │   │   └── MedicalHistory.tsx
│   │   │
│   │   ├── clinical/
│   │   │   ├── Odontogram.tsx          # Interactive tooth chart
│   │   │   ├── PerioChart.tsx          # Periodontal charting
│   │   │   ├── TreatmentPlanBuilder.tsx
│   │   │   ├── ClinicalNotes.tsx
│   │   │   └── ImageViewer.tsx
│   │   │
│   │   ├── billing/
│   │   │   ├── InvoiceViewer.tsx
│   │   │   ├── PaymentForm.tsx
│   │   │   ├── InsuranceForm.tsx
│   │   │   └── BillingHistory.tsx
│   │   │
│   │   ├── chat/
│   │   │   ├── ChatWidget.tsx          # AI agent chat
│   │   │   ├── MessageList.tsx
│   │   │   └── MessageInput.tsx
│   │   │
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── ProtectedRoute.tsx
│   │       └── DataTable.tsx
│   │
│   ├── stores/                 # State Management (Zustand)
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── notificationStore.ts
│   │
│   ├── api/                    # API Client
│   │   ├── client.ts           # Axios instance
│   │   ├── authApi.ts
│   │   ├── patientsApi.ts
│   │   ├── appointmentsApi.ts
│   │   ├── clinicalApi.ts
│   │   ├── billingApi.ts
│   │   └── reportsApi.ts
│   │
│   ├── hooks/                  # Custom Hooks
│   │   ├── useAuth.ts
│   │   ├── usePatients.ts      # React Query hooks
│   │   ├── useAppointments.ts
│   │   ├── useTreatments.ts
│   │   ├── useInvoices.ts
│   │   └── useDebounce.ts
│   │
│   ├── types/                  # TypeScript Types
│   │   ├── user.ts
│   │   ├── patient.ts
│   │   ├── appointment.ts
│   │   ├── clinical.ts
│   │   ├── billing.ts
│   │   └── common.ts
│   │
│   ├── utils/                  # Utilities
│   │   ├── formatters.ts       # Date, currency formatters
│   │   ├── validators.ts       # Form validation
│   │   └── helpers.ts
│   │
│   ├── lib/                    # Third-party lib configs
│   │   └── utils.ts            # cn() for Tailwind
│   │
│   └── styles/
│       └── globals.css
│
├── public/
│   ├── favicon.ico
│   └── assets/
│
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── README.md
```

---

### 3.3 Database Architecture

#### 3.3.1 PostgreSQL Schema (Complete)

**Core Tables:**

```sql
-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(500) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_mfa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    mfa_type VARCHAR(20) NOT NULL,  -- 'totp', 'sms'
    secret VARCHAR(255) NOT NULL,
    is_enabled BOOLEAN DEFAULT false,
    backup_codes TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ORGANIZATIONS & MEMBERSHIPS
-- ============================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'clinic', 'dso', 'hospital'
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'IL',
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    odoo_company_id INTEGER,  -- Link to Odoo company
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    organization_role VARCHAR(50) NOT NULL,  -- 'owner', 'manager', 'clinical_staff', 'support_staff', 'patient'
    functional_role VARCHAR(50),  -- 'dentist', 'hygienist', 'receptionist', 'assistant', etc.
    odoo_partner_id INTEGER,  -- Link to Odoo res.partner
    odoo_employee_id INTEGER,  -- Link to Odoo hr.employee (for staff)
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMP DEFAULT NOW(),
    left_at TIMESTAMP,
    UNIQUE(user_id, organization_id)
);

-- ============================================
-- CLINIC SETTINGS
-- ============================================

CREATE TABLE clinic_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
    
    -- Operating hours (JSON for flexibility)
    operating_hours JSONB DEFAULT '{
        "sunday": {"open": "09:00", "close": "17:00", "closed": false},
        "monday": {"open": "09:00", "close": "17:00", "closed": false},
        "tuesday": {"open": "09:00", "close": "17:00", "closed": false},
        "wednesday": {"open": "09:00", "close": "17:00", "closed": false},
        "thursday": {"open": "09:00", "close": "17:00", "closed": false},
        "friday": {"open": "09:00", "close": "13:00", "closed": false},
        "saturday": {"open": null, "close": null, "closed": true}
    }'::jsonb,
    
    -- Appointment settings
    default_appointment_duration INTEGER DEFAULT 30,  -- minutes
    buffer_between_appointments INTEGER DEFAULT 10,  -- minutes
    advance_booking_days INTEGER DEFAULT 60,
    cancellation_notice_hours INTEGER DEFAULT 24,
    no_show_fee DECIMAL(10,2) DEFAULT 100.00,
    late_cancellation_fee DECIMAL(10,2) DEFAULT 50.00,
    
    -- Communication
    sms_enabled BOOLEAN DEFAULT true,
    email_enabled BOOLEAN DEFAULT true,
    whatsapp_enabled BOOLEAN DEFAULT false,
    telegram_enabled BOOLEAN DEFAULT false,
    reminder_hours_before INTEGER DEFAULT 24,
    confirmation_required BOOLEAN DEFAULT true,
    
    -- Billing
    currency VARCHAR(3) DEFAULT 'ILS',
    tax_rate DECIMAL(5,2) DEFAULT 17.00,
    payment_methods JSONB DEFAULT '["cash", "credit_card", "bank_transfer"]'::jsonb,
    invoice_prefix VARCHAR(10) DEFAULT 'INV',
    invoice_starting_number INTEGER DEFAULT 1000,
    
    -- Compliance
    hipaa_enabled BOOLEAN DEFAULT false,
    gdpr_enabled BOOLEAN DEFAULT false,
    israeli_privacy_law BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PATIENTS (Local cache + extensions)
-- ============================================

CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- If patient has portal account
    odoo_partner_id INTEGER UNIQUE,  -- Link to Odoo res.partner
    
    -- Demographics (synced from Odoo)
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    id_number VARCHAR(50),  -- Israeli ID (Teudat Zehut)
    
    -- Contact (synced from Odoo)
    email VARCHAR(255),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    zip_code VARCHAR(20),
    
    -- Emergency contact
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    
    -- Insurance (Israeli specific)
    health_fund VARCHAR(50),  -- Clalit, Maccabi, Meuhedet, Leumit
    health_fund_member_id VARCHAR(50),
    supplementary_insurance VARCHAR(100),
    supplementary_insurance_id VARCHAR(50),
    
    -- Medical (local extensions)
    blood_type VARCHAR(5),
    allergies TEXT[],
    chronic_conditions TEXT[],
    current_medications TEXT[],
    notes TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_visit_date DATE,
    next_appointment_date DATE,
    
    -- Sync
    synced_from_odoo_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- APPOINTMENTS (Local cache + extensions)
-- ============================================

CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    provider_id UUID REFERENCES organization_memberships(id) ON DELETE SET NULL,  -- Dentist
    odoo_appointment_id INTEGER UNIQUE,  -- Link to Odoo medical.appointment
    
    -- Appointment details
    appointment_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    end_time TIMESTAMP GENERATED ALWAYS AS (appointment_date + (duration_minutes || ' minutes')::INTERVAL) STORED,
    
    -- Type & Status
    appointment_type VARCHAR(50),  -- 'checkup', 'cleaning', 'filling', 'extraction', etc.
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',  -- 'scheduled', 'confirmed', 'checked_in', 'in_progress', 'completed', 'cancelled', 'no_show'
    
    -- Reason
    chief_complaint TEXT,
    notes TEXT,
    
    -- Confirmation
    confirmed_at TIMESTAMP,
    confirmed_by VARCHAR(50),  -- 'patient', 'staff', 'auto'
    
    -- Reminders
    reminder_sent_at TIMESTAMP,
    reminder_method VARCHAR(20),  -- 'sms', 'email', 'whatsapp'
    
    -- Cancellation
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    cancelled_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Sync
    synced_from_odoo_at TIMESTAMP,
    synced_to_odoo_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CLINICAL DATA
-- ============================================

CREATE TABLE clinical_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
    provider_id UUID REFERENCES organization_memberships(id) ON DELETE SET NULL,
    
    -- SOAP Notes
    subjective TEXT,  -- Patient's complaint
    objective TEXT,   -- Clinical findings
    assessment TEXT,  -- Diagnosis
    plan TEXT,        -- Treatment plan
    
    -- Additional
    procedure_codes TEXT[],  -- ICD-10 / SNODENT codes
    diagnosis_codes TEXT[],
    
    -- Attachments
    attachment_urls TEXT[],  -- S3 URLs for images, X-rays
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE odontograms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    clinical_note_id UUID REFERENCES clinical_notes(id) ON DELETE SET NULL,
    
    -- Tooth data (JSON for flexibility)
    -- Each tooth: {tooth_number: {conditions: [], notes: ""}}
    tooth_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE perio_charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    clinical_note_id UUID REFERENCES clinical_notes(id) ON DELETE SET NULL,
    
    -- Periodontal data (JSON)
    -- 6-point probing depths, bleeding, recession, etc.
    perio_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE treatment_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    provider_id UUID REFERENCES organization_memberships(id) ON DELETE SET NULL,
    
    -- Plan details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',  -- 'draft', 'presented', 'accepted', 'declined', 'in_progress', 'completed'
    
    -- Pricing
    total_cost DECIMAL(10,2) NOT NULL DEFAULT 0,
    insurance_coverage DECIMAL(10,2) DEFAULT 0,
    patient_responsibility DECIMAL(10,2) GENERATED ALWAYS AS (total_cost - COALESCE(insurance_coverage, 0)) STORED,
    
    -- Approval
    presented_at TIMESTAMP,
    accepted_at TIMESTAMP,
    declined_at TIMESTAMP,
    decline_reason TEXT,
    
    -- E-signature
    signature_url VARCHAR(500),
    signed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE treatment_plan_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    treatment_plan_id UUID REFERENCES treatment_plans(id) ON DELETE CASCADE,
    
    -- Treatment details
    tooth_number VARCHAR(5),  -- e.g., "16", "21", "all"
    procedure_code VARCHAR(50),
    procedure_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Pricing
    unit_price DECIMAL(10,2) NOT NULL,
    quantity INTEGER DEFAULT 1,
    total_price DECIMAL(10,2) GENERATED ALWAYS AS (unit_price * quantity) STORED,
    insurance_coverage DECIMAL(10,2) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'planned',  -- 'planned', 'in_progress', 'completed', 'cancelled'
    completed_at TIMESTAMP,
    
    -- Priority
    priority INTEGER DEFAULT 1,  -- 1=urgent, 2=soon, 3=routine
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- BILLING & PAYMENTS
-- ============================================

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
    
    -- Invoice details
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    
    -- Amounts
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    balance DECIMAL(10,2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft',  -- 'draft', 'sent', 'paid', 'partially_paid', 'overdue', 'cancelled'
    
    -- Notes
    notes TEXT,
    
    -- Odoo sync
    odoo_invoice_id INTEGER,
    synced_to_odoo_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    
    -- Item details
    description VARCHAR(255) NOT NULL,
    procedure_code VARCHAR(50),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    
    -- Payment details
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,  -- 'cash', 'credit_card', 'bank_transfer', 'check'
    
    -- Card details (if applicable)
    card_last4 VARCHAR(4),
    card_brand VARCHAR(20),
    
    -- External references
    stripe_payment_id VARCHAR(255),
    tranzila_transaction_id VARCHAR(255),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'completed',  -- 'pending', 'completed', 'failed', 'refunded'
    
    -- Notes
    notes TEXT,
    
    -- Refund
    refunded_at TIMESTAMP,
    refund_amount DECIMAL(10,2),
    refund_reason TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE insurance_claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    
    -- Claim details
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    claim_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Insurance
    insurance_provider VARCHAR(100) NOT NULL,  -- Clalit, Maccabi, etc.
    policy_number VARCHAR(100),
    
    -- Amounts
    billed_amount DECIMAL(10,2) NOT NULL,
    approved_amount DECIMAL(10,2),
    paid_amount DECIMAL(10,2),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'submitted',  -- 'draft', 'submitted', 'pending', 'approved', 'partially_approved', 'denied', 'paid'
    
    -- Submission
    submitted_at TIMESTAMP,
    submission_method VARCHAR(50),  -- 'electronic', 'paper', 'portal'
    
    -- Response
    response_date DATE,
    denial_reason TEXT,
    
    -- Notes
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- TREATMENT CATALOG & PRICING
-- ============================================

CREATE TABLE treatment_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Treatment details
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),  -- 'preventive', 'restorative', 'cosmetic', 'surgical', 'orthodontic', 'endodontic', 'periodontic'
    
    -- Pricing
    default_price DECIMAL(10,2) NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    
    -- Insurance
    is_covered_by_insurance BOOLEAN DEFAULT false,
    insurance_coverage_percentage DECIMAL(5,2),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(organization_id, code)
);

-- ============================================
-- STAFF & PROVIDERS
-- ============================================

CREATE TABLE staff_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_member_id UUID REFERENCES organization_memberships(id) ON DELETE CASCADE,
    
    -- Schedule details
    day_of_week INTEGER NOT NULL,  -- 0=Sunday, 6=Saturday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Break
    break_start_time TIME,
    break_end_time TIME,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(staff_member_id, day_of_week)
);

CREATE TABLE staff_time_off (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_member_id UUID REFERENCES organization_memberships(id) ON DELETE CASCADE,
    
    -- Time off details
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason VARCHAR(255),
    type VARCHAR(50),  -- 'vacation', 'sick', 'personal', 'conference'
    
    -- Approval
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'approved', 'denied'
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- COMMUNICATIONS
-- ============================================

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Message details
    subject VARCHAR(255),
    body TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL,  -- 'sms', 'email', 'whatsapp', 'telegram', 'in_app'
    direction VARCHAR(10) NOT NULL,  -- 'inbound', 'outbound'
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'sent', 'delivered', 'read', 'failed'
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    
    -- External IDs
    external_message_id VARCHAR(255),
    
    -- Error
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE message_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Template details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL,  -- 'appointment_reminder', 'appointment_confirmation', 'birthday', 'recall', etc.
    channel VARCHAR(20) NOT NULL,  -- 'sms', 'email', 'whatsapp'
    
    -- Content
    subject VARCHAR(255),  -- For email
    body TEXT NOT NULL,
    
    -- Variables: {{patient_name}}, {{appointment_date}}, etc.
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CONSENT & COMPLIANCE
-- ============================================

CREATE TABLE consent_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Consent details
    consent_type VARCHAR(100) NOT NULL,  -- 'treatment', 'data_sharing', 'marketing', 'photography', etc.
    description TEXT,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'granted', 'denied', 'revoked'
    granted_at TIMESTAMP,
    revoked_at TIMESTAMP,
    
    -- Signature
    signature_url VARCHAR(500),
    signed_by VARCHAR(255),
    ip_address INET,
    
    -- Expiry
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- AUDIT & LOGGING
-- ============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Action details
    action VARCHAR(50) NOT NULL,  -- 'create', 'read', 'update', 'delete', 'login', 'logout'
    resource_type VARCHAR(100) NOT NULL,  -- 'patient', 'appointment', 'invoice', etc.
    resource_id UUID,
    
    -- Changes (for update actions)
    old_values JSONB,
    new_values JSONB,
    
    -- Request details
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token);

-- Organizations
CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_memberships_user_id ON organization_memberships(user_id);
CREATE INDEX idx_memberships_organization_id ON organization_memberships(organization_id);
CREATE INDEX idx_memberships_odoo_partner_id ON organization_memberships(odoo_partner_id);

-- Patients
CREATE INDEX idx_patients_organization_id ON patients(organization_id);
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_patients_odoo_partner_id ON patients(odoo_partner_id);
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_patients_name ON patients(first_name, last_name);

-- Appointments
CREATE INDEX idx_appointments_organization_id ON appointments(organization_id);
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_provider_id ON appointments(provider_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_odoo_id ON appointments(odoo_appointment_id);

-- Clinical
CREATE INDEX idx_clinical_notes_patient_id ON clinical_notes(patient_id);
CREATE INDEX idx_clinical_notes_appointment_id ON clinical_notes(appointment_id);
CREATE INDEX idx_odontograms_patient_id ON odontograms(patient_id);
CREATE INDEX idx_perio_charts_patient_id ON perio_charts(patient_id);
CREATE INDEX idx_treatment_plans_patient_id ON treatment_plans(patient_id);
CREATE INDEX idx_treatment_plan_items_plan_id ON treatment_plan_items(treatment_plan_id);

-- Billing
CREATE INDEX idx_invoices_organization_id ON invoices(organization_id);
CREATE INDEX idx_invoices_patient_id ON invoices(patient_id);
CREATE INDEX idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoice_items_invoice_id ON invoice_items(invoice_id);
CREATE INDEX idx_payments_organization_id ON payments(organization_id);
CREATE INDEX idx_payments_patient_id ON payments(patient_id);
CREATE INDEX idx_payments_invoice_id ON payments(invoice_id);
CREATE INDEX idx_insurance_claims_patient_id ON insurance_claims(patient_id);
CREATE INDEX idx_insurance_claims_status ON insurance_claims(status);

-- Catalog
CREATE INDEX idx_treatment_catalog_organization_id ON treatment_catalog(organization_id);
CREATE INDEX idx_treatment_catalog_code ON treatment_catalog(code);
CREATE INDEX idx_treatment_catalog_category ON treatment_catalog(category);

-- Staff
CREATE INDEX idx_staff_schedules_staff_member_id ON staff_schedules(staff_member_id);
CREATE INDEX idx_staff_time_off_staff_member_id ON staff_time_off(staff_member_id);

-- Communications
CREATE INDEX idx_messages_organization_id ON messages(organization_id);
CREATE INDEX idx_messages_patient_id ON messages(patient_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_message_templates_organization_id ON message_templates(organization_id);

-- Compliance
CREATE INDEX idx_consent_records_patient_id ON consent_records(patient_id);
CREATE INDEX idx_audit_logs_organization_id ON audit_logs(organization_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

**מסמך זה ממשיך בחלקים הבאים...**

**(המסמך ארוך מדי לתצוגה מלאה - האם להמשיך עם החלקים הבאים?)**

---

## 📊 סיכום מסמך זה

מסמך זה מכיל:
- ✅ ארכיטקטורה נוכחית מפורטת
- ✅ ארכיטקטורה יעד (Phase 2)
- ✅ Technology stack מלא
- ✅ Database schema מושלם
- ⏳ חלקים נוספים: APIs, Security, Implementation

**האם להמשיך עם החלקים 4-8?**
