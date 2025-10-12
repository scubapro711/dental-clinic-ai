# Complete Architecture Knowledge for Patient Portal Development

**Date:** October 11, 2025  
**Purpose:** Comprehensive understanding of DentaFlow architecture for perfect Patient Portal implementation

---

## 🏗️ System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌─────────────┬──────────────┬─────────────┬─────────────┐    │
│  │   Patient   │    Clinic    │    Admin    │   Shared    │    │
│  │   Portal    │   Portal     │   Portal    │ Components  │    │
│  │  (5 pages)  │  (6 pages)   │  (6 pages)  │             │    │
│  └─────────────┴──────────────┴─────────────┴─────────────┘    │
│                              │                                   │
│                              │ HTTP/REST API                     │
│                              ▼                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────┴───────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   API Layer (FastAPI)                    │   │
│  │  - Authentication (JWT)                                  │   │
│  │  - Patient Portal Endpoints (17 endpoints)              │   │
│  │  - Clinic Portal Endpoints                              │   │
│  │  - Admin Endpoints                                       │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────┴─────────────────────────────────────────────┐   │
│  │              AI Agents Layer (LangGraph)                 │   │
│  │  ┌──────────┬──────────┬──────────┬──────────────────┐  │   │
│  │  │  Alex    │  Marcus  │  Sophia  │  Sarah (future)  │  │   │
│  │  │(Reception│  (CFO)   │(Practice │   (Clinical)     │  │   │
│  │  │  & Care) │          │  Admin)  │                  │  │   │
│  │  └──────────┴──────────┴──────────┴──────────────────┘  │   │
│  │                        │                                 │   │
│  │                        │ Tool Calls                      │   │
│  │                        ▼                                 │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │              Agent Tools (50+ tools)             │   │   │
│  │  │  - Odoo Tools                                    │   │   │
│  │  │  - Communication Tools (SMS, Telegram, Email)   │   │   │
│  │  │  - Scheduling Tools                              │   │   │
│  │  │  - Financial Tools                               │   │   │
│  │  │  - Clinical Tools                                │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│  ┌────────────────────────────┴──────────────────────────────┐  │
│  │              Integration Layer                            │  │
│  │  - Odoo Client (Mock Odoo Dental)                        │  │
│  │  - Twilio Service (SMS)                                  │  │
│  │  - Telegram Service                                      │  │
│  │  - Email Service                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────┴───────────────────────────────────┐
│                      Data Layer                                  │
│  ┌────────────────┬──────────────────┬────────────────────────┐  │
│  │   PostgreSQL   │  Mock Odoo Dental│   External Services   │  │
│  │   (Users,      │  (1,500 patients,│   - Twilio            │  │
│  │   Orgs, Auth)  │   appointments,  │   - Telegram Bot      │  │
│  │                │   records, etc.) │   - Email (SMTP)      │  │
│  └────────────────┴──────────────────┴────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Agents Architecture (LangGraph)

### Current Agents (3 + 1 planned)

#### 1. Alex - Reception & Patient Relations
**Role:** Front-line patient communication  
**Tier:** 1 (Patient-facing)  
**File:** `backend/app/agents/alex_v2.py`

**Responsibilities:**
- Patient onboarding and registration
- Appointment booking and management
- General inquiries
- SMS/Telegram/Email communication
- Payment information
- Triage (urgent vs non-urgent)
- Escalation to clinical staff

**Tools (12):**
- `search_appointments`
- `create_appointment`
- `cancel_appointment`
- `send_sms`
- `send_email`
- `send_telegram_message`
- `search_patients`
- `get_patient_info`
- `create_patient`
- `update_patient`
- `get_invoices`
- `escalate_to_doctor`

**Personality:**
- Warm, empathetic, patient
- Speaks natural Hebrew
- Uses emojis moderately (😊 🦷 📅)
- Asks one question at a time
- Confirms understanding before proceeding

**Integration Points:**
- Telegram Bot (primary channel for patients)
- Patient Portal (web interface)
- Twilio (SMS verification and reminders)

---

#### 2. Marcus - CFO (Chief Financial Officer)
**Role:** Financial management and reporting  
**Tier:** 2/3 (Clinic management)  
**File:** `backend/app/agents/cfo.py`

**Responsibilities:**
- Financial reports (daily, weekly, monthly)
- Cash flow analysis
- Revenue forecasting
- Expense optimization
- Invoice management
- Payment tracking
- Profitability analysis per treatment
- Insurance claims (future)

**Tools (15+):**
- `get_financial_summary`
- `get_cash_flow`
- `get_revenue_forecast`
- `get_expense_breakdown`
- `get_profitability_analysis`
- `get_invoices`
- `create_invoice`
- `send_invoice`
- `get_payments`
- `get_outstanding_balance`
- `analyze_treatment_profitability`

**Personality:**
- Analytical, precise, business-focused
- Data-driven insights
- Proactive alerts

**Integration Points:**
- Clinic Portal (Financial Dashboard)
- Green Invoice (future)
- Tranzila (future)

---

#### 3. Sophia - Practice Administrator
**Role:** Operations and resource management  
**Tier:** 2/3 (Clinic management)  
**File:** `backend/app/agents/practice_admin.py`

**Responsibilities:**
- Daily schedule management
- Staff coordination
- Inventory management
- Equipment maintenance tracking
- Task management
- Morning briefings (7am)
- Room availability
- Schedule optimization

**Tools (20+):**
- `get_daily_schedule`
- `get_staff_status`
- `get_inventory_status`
- `get_equipment_maintenance`
- `create_task`
- `assign_task`
- `order_supplies`
- `schedule_maintenance`
- `get_room_availability`
- `optimize_schedule`

**Personality:**
- Organized, efficient, proactive
- Sees the big picture
- Coordinates between stakeholders

**Integration Points:**
- Clinic Portal (Operations Dashboard)
- Morning briefing system

---

#### 4. Sarah - Clinical Assistant (PLANNED)
**Role:** Medical records and clinical support  
**Tier:** 2/3 (Clinical staff)  
**File:** `backend/app/agents/sarah_clinical.py` (to be created)

**Responsibilities:**
- Dental chart management
- Treatment record documentation
- Prescription management
- Medical history tracking
- X-ray ordering and analysis
- Lab test ordering
- Clinical notes
- Referrals to specialists
- Follow-up scheduling

**Tools (25+):**
- `get_dental_chart`
- `update_dental_chart`
- `create_treatment_record`
- `get_treatment_history`
- `create_prescription`
- `get_medical_history`
- `update_medical_history`
- `add_allergy`
- `order_xray`
- `upload_xray`
- `analyze_xray`
- `create_clinical_note`
- `create_referral`
- `schedule_followup`
- `create_treatment_plan`

**Why Sarah is needed:**
- 36% of Odoo models (17 models) have no responsible agent
- Clinical decisions need dedicated expertise
- Separation of concerns (clinical vs administrative)
- HIPAA compliance requirements

---

### LangGraph Implementation

**File:** `backend/app/agents/agent_graph_v4.py`

**Graph Structure:**
```python
StateGraph
    ├── supervisor (routes to agents)
    ├── alex_node (patient relations)
    ├── marcus_node (financial)
    ├── sophia_node (operations)
    └── sarah_node (clinical) [PLANNED]
```

**State Management:**
```python
class GraphState(TypedDict):
    messages: List[BaseMessage]
    next_agent: str
    current_agent: str
    context: Dict[str, Any]
    user_id: str
    clinic_id: int
    patient_id: Optional[int]
```

**Routing Logic:**
- Patient queries → Alex
- Financial queries → Marcus
- Operations queries → Sophia
- Clinical queries → Sarah (future)

---

## 🔌 Integration Layer

### 1. Mock Odoo Dental Integration

**File:** `backend/app/integrations/mock_odoo_realistic.py`

**Data:**
- 1,500 patients with realistic Israeli data
- Appointments (past, upcoming, cancelled)
- Medical records (treatments, X-rays, prescriptions)
- Invoices and payments
- Insurance information
- Dental charts

**Key Models (47 total):**
- `medical.patient` - Patient records
- `medical.appointment` - Appointments
- `medical.teeth.treatment` - Treatment records
- `medical.prescription.order` - Prescriptions
- `account.invoice` - Invoices
- `medical.insurance.plan` - Insurance plans
- `medical.pathology` - Diseases/conditions
- `medical.medicament` - Medications

**Access Pattern:**
```python
from app.integrations.odoo_client_v3 import OdooClient

odoo = OdooClient()
patients = odoo.search_read('medical.patient', filters, fields)
```

---

### 2. Twilio Integration (SMS)

**File:** `backend/app/services/twilio_service.py`

**Features:**
- SMS sending with templates
- Hebrew RTL support
- Delivery tracking
- GDPR compliance (opt-out checking)
- Rate limiting (max 3 SMS per patient per day)

**Templates:**
- Appointment reminder
- Appointment confirmation
- Payment reminder
- Welcome message
- Custom messages

**Usage by Agents:**
```python
# Alex calls this tool
send_sms_tool(
    patient_id=123,
    template="appointment_reminder",
    clinic_id=1,
    template_vars={
        "clinic_name": "DentaFlow Clinic",
        "date": "12/10/2025",
        "time": "10:00",
        "doctor_name": "Cohen"
    }
)
```

**Environment Variables:**
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

---

### 3. Telegram Integration

**File:** `backend/app/services/telegram_service.py`

**Features:**
- Bot conversation with Alex
- Natural language processing
- Patient identification (phone number)
- User-to-patient mapping
- Conversation history
- Proactive notifications

**Database Schema:**
```sql
CREATE TABLE telegram_users (
    id UUID PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE NOT NULL,
    telegram_username VARCHAR(255),
    patient_id INT,  -- Link to Odoo patient
    clinic_id INT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    last_interaction_at TIMESTAMP
);

CREATE TABLE telegram_conversations (
    id UUID PRIMARY KEY,
    telegram_user_id BIGINT,
    message_text TEXT,
    message_from VARCHAR(10), -- 'user' or 'bot'
    created_at TIMESTAMP
);
```

**Onboarding Flow:**
1. Patient sends `/start` to bot
2. Bot (Alex) asks for phone number
3. System searches Odoo for patient by phone
4. If found: Links telegram_user_id to patient_id
5. If not found: Creates new patient record
6. Patient can now interact naturally with Alex

**Environment Variables:**
- `TELEGRAM_BOT_TOKEN`

---

## 🔐 Authentication & Authorization

### JWT Authentication

**File:** `backend/app/core/security.py`

**Flow:**
1. User registers with email/password
2. Password hashed with bcrypt
3. User logs in → receives JWT tokens
4. Access token (short-lived, 1 hour)
5. Refresh token (long-lived, 7 days)
6. Token includes: user_id, email, role, organization_id, odoo_partner_id

**Token Structure:**
```json
{
  "sub": "user_uuid",
  "email": "patient@example.com",
  "role": "PATIENT",
  "organization_id": "org_uuid",
  "odoo_partner_id": 123,
  "exp": 1728691200
}
```

### User Roles (Database Enum)

**Current Roles:**
- `SUPER_ADMIN` - Platform administrator
- `ORG_ADMIN` - Clinic owner/manager
- `ORG_STAFF` - Clinic staff (dentists, hygienists)
- `ORG_VIEWER` - Read-only access

**Missing Role:**
- `PATIENT` - **NEEDS TO BE ADDED**

**Issue:** Registration fails because code tries to create user with role="patient" but enum doesn't have it.

**Solution:** Create Alembic migration to add PATIENT to UserRole enum.

---

### User-to-Patient Mapping

**Purpose:** Link authenticated users to Odoo patient records

**Database Table:** `organization_memberships`

**Schema:**
```sql
CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    role VARCHAR(50),
    odoo_partner_id INT,  -- Link to Odoo patient
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Flow:**
1. User registers/logs in
2. System checks if user has odoo_partner_id
3. If not: Show patient selection UI
4. User searches for their patient record (by name/phone)
5. System creates mapping
6. All future API calls use this mapping

**API Endpoints:**
- `GET /api/v1/mappings/me` - Get current user's mapping
- `POST /api/v1/mappings` - Create new mapping
- `PUT /api/v1/mappings/{id}` - Update mapping

---

## 📱 Patient Portal Implementation

### Pages (5 total)

#### 1. Dashboard (`/patient/dashboard`)
**File:** `frontend/src/pages/patient/PatientDashboard.jsx`

**Features:**
- Welcome message with patient name
- Health score widget
- Upcoming appointments (next 3)
- Outstanding balance
- AI suggestions from Alex, Marcus, Sarah
- Quick actions (book appointment, view records)
- Floating chat button

**API Calls:**
- `GET /api/v1/patient/profile` - Patient info
- `GET /api/v1/patient/health-score` - Dental health score
- `GET /api/v1/appointments?status=upcoming&limit=3` - Upcoming appointments
- `GET /api/v1/billing/overview` - Billing summary

**Current Status:** ⚠️ Uses mock data, needs API integration

---

#### 2. Appointments (`/patient/appointments`)
**File:** `frontend/src/pages/patient/PatientAppointments.jsx`

**Features:**
- List all appointments (past, upcoming, cancelled)
- Filter by status
- View appointment details
- Book new appointment (wizard)
- Cancel appointment
- Reschedule appointment

**Booking Wizard Steps:**
1. Select treatment type
2. Select preferred doctor
3. Select date
4. Select available time slot
5. Add notes
6. Confirm booking

**API Calls:**
- `GET /api/v1/appointments` - List appointments
- `GET /api/v1/doctors` - List doctors
- `GET /api/v1/appointments/available-slots?doctor_id=X&date=Y` - Available slots
- `POST /api/v1/appointments` - Create appointment
- `PUT /api/v1/appointments/{id}/cancel` - Cancel appointment

**Current Status:** ⚠️ UI built, needs API integration

---

#### 3. Medical Records (`/patient/medical-records`)
**File:** `frontend/src/pages/patient/PatientMedicalRecords.jsx`

**Features:**
- List all medical records
- Filter by type (X-ray, treatment, report)
- View record details
- Interactive dental chart
- View X-ray images
- Download reports

**API Calls:**
- `GET /api/v1/records` - List records
- `GET /api/v1/records/{id}` - Get record detail

**Current Status:** ⚠️ UI built with dental chart, needs API integration

---

#### 4. Billing (`/patient/billing`)
**File:** `frontend/src/pages/patient/PatientBilling.jsx`

**Features:**
- Billing overview (outstanding, paid, pending)
- List all invoices
- Filter by status (paid, unpaid, overdue)
- View invoice details
- Payment processing (Bit, PayBox, Credit Card)
- Payment history

**Payment Methods:**
- Bit (Israeli mobile payment)
- PayBox (Israeli payment gateway)
- Credit Card (Tranzila integration)

**API Calls:**
- `GET /api/v1/billing/overview` - Overview
- `GET /api/v1/billing/invoices` - List invoices
- `POST /api/v1/billing/pay` - Process payment (future)

**Current Status:** ⚠️ UI built, needs API integration

---

#### 5. Profile (`/patient/profile`)
**File:** `frontend/src/pages/patient/PatientProfile.jsx`

**Features:**
- View profile information
- Edit personal details
- SMS verification status
- Telegram connection status
- Email preferences
- Notification settings
- Privacy settings

**API Calls:**
- `GET /api/v1/patient/profile` - Get profile
- `PUT /api/v1/patient/profile` - Update profile
- `POST /api/v1/auth/send-sms-verification` - Send SMS code
- `POST /api/v1/auth/verify-sms-code` - Verify SMS code
- `POST /api/v1/telegram/generate-link` - Generate Telegram link
- `GET /api/v1/telegram/status` - Check Telegram status

**Current Status:** ⚠️ UI built, needs API integration

---

### Shared Components

**Layout:** `frontend/src/layouts/PatientPortalLayout.jsx`
- 3-column layout (Quick Actions | Main Content | Chat & Suggestions)
- Header with logo, navigation, user menu
- Floating chat button (Alex)
- RTL support for Hebrew

**Components:**
- `FloatingChatButton` - Chat with Alex
- `AISuggestionCard` - Proactive AI suggestions
- `AppointmentCard` - Display appointment
- `InvoiceCard` - Display invoice
- `DentalChart` - Interactive tooth diagram
- `HealthScoreWidget` - Visual health score

---

## 🗄️ Database Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    phone_verified BOOLEAN DEFAULT false,
    role userrole NOT NULL,  -- ENUM: needs PATIENT added
    organization_id UUID REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_login_at TIMESTAMP
);
```

#### organizations
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    subscription_tier subscriptiontier NOT NULL,  -- BASIC, PROFESSIONAL, ENTERPRISE
    subscription_status VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### organization_memberships
```sql
CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    role VARCHAR(50),
    odoo_partner_id INT,  -- Link to Odoo patient
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id, organization_id)
);
```

---

## 🚀 Patient Portal Completion Requirements

### Critical Fixes Needed

#### 1. Database Schema
- [ ] Add PATIENT to UserRole enum
- [ ] Create Alembic migration
- [ ] Apply migration

#### 2. Authentication
- [ ] Fix bcrypt password hashing (already done in code)
- [ ] Restart backend to load fixed code
- [ ] Test registration endpoint
- [ ] Test login endpoint
- [ ] Fix frontend auth hook (JSON format)

#### 3. User-Patient Mapping
- [ ] Create patient onboarding UI
- [ ] Implement patient search
- [ ] Create mapping flow
- [ ] Store odoo_partner_id in token

#### 4. SMS Integration
- [ ] Configure Twilio credentials
- [ ] Test SMS sending
- [ ] Implement SMS verification UI
- [ ] Test verification flow

#### 5. Telegram Integration
- [ ] Configure Telegram bot token
- [ ] Test bot connection
- [ ] Implement Telegram link generation
- [ ] Test patient onboarding via Telegram

#### 6. API Integration (All 5 Pages)
- [ ] Dashboard - Connect to real APIs
- [ ] Appointments - Connect booking flow
- [ ] Medical Records - Connect records API
- [ ] Billing - Connect invoices API
- [ ] Profile - Connect profile update

#### 7. Testing
- [ ] End-to-end registration flow
- [ ] End-to-end booking flow
- [ ] All API calls working
- [ ] Error handling
- [ ] Loading states
- [ ] Hebrew/RTL support

---

## 📝 Implementation Checklist

### Day 1: Foundation
- [ ] Fix UserRole enum (add PATIENT)
- [ ] Create and apply migration
- [ ] Restart backend
- [ ] Test registration
- [ ] Test login
- [ ] Fix frontend auth (JSON format)

### Day 2: Mapping & Onboarding
- [ ] Create patient search API
- [ ] Build onboarding UI
- [ ] Implement mapping flow
- [ ] Test complete registration

### Day 3: Communication
- [ ] Configure Twilio
- [ ] Test SMS sending
- [ ] Build SMS verification UI
- [ ] Configure Telegram bot
- [ ] Test Telegram connection

### Day 4: Dashboard
- [ ] Connect dashboard APIs
- [ ] Implement loading states
- [ ] Implement error handling
- [ ] Test with real data

### Day 5: Appointments
- [ ] Connect appointments list
- [ ] Build booking wizard
- [ ] Connect available slots API
- [ ] Test booking flow

### Day 6: Records & Billing
- [ ] Connect medical records
- [ ] Connect billing page
- [ ] Test data display

### Day 7: Testing & Polish
- [ ] End-to-end testing
- [ ] Fix bugs
- [ ] Polish UI/UX
- [ ] Final verification

---

## ✅ Success Criteria

**Must achieve 100% on all:**
- [ ] User can register with email/password
- [ ] User receives SMS verification
- [ ] User can verify phone
- [ ] User can connect Telegram
- [ ] User can link to Odoo patient
- [ ] User can login and get JWT
- [ ] Dashboard shows real data
- [ ] Appointments page works fully
- [ ] User can book appointment
- [ ] User can cancel appointment
- [ ] Medical records display correctly
- [ ] Billing page shows real invoices
- [ ] Profile page works
- [ ] All API calls succeed
- [ ] Loading states work
- [ ] Error messages are clear
- [ ] Hebrew/RTL works perfectly
- [ ] No console errors
- [ ] Performance < 2s page load

---

## 🎯 Ready to Execute!

**Current Status:** All architecture understood ✅  
**Next Action:** Fix UserRole enum and start Day 1 tasks  
**Estimated Time:** 7 days for 100% completion  
**No Shortcuts:** Every feature must work perfectly


