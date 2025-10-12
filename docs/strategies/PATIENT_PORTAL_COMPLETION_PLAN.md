# Patient Portal 100% Completion Plan

**Date:** October 11, 2025  
**Goal:** Complete Patient Portal with full authentication, SMS/Telegram onboarding, and Mock Odoo integration - NO SHORTCUTS

---

## 📋 Current Understanding

### What We Have
1. ✅ **Backend running** on port 8002 with Mock Odoo Dental (1,500 patients)
2. ✅ **Frontend UI built** - 5 patient portal pages with beautiful design
3. ✅ **API endpoints documented** - 17 patient portal endpoints available
4. ✅ **PostgreSQL database** installed and running
5. ✅ **Database tables created** via Alembic migrations
6. ✅ **Organization created** in database (DentaFlow Clinic)

### Critical Issues Identified
1. ❌ **UserRole enum mismatch** - Database has `{SUPER_ADMIN, ORG_ADMIN, ORG_STAFF, ORG_VIEWER}` but code tries to use `"patient"`
2. ❌ **Bcrypt password hashing** - Fixed in code but needs backend restart
3. ❌ **Frontend-Backend API format mismatch** - Frontend sends form-encoded, backend expects JSON
4. ❌ **Frontend not running** - Build issues with file watchers
5. ❌ **No patient role** in database schema

### What Needs to Work 100%
1. ✅ User registration with email/password
2. ✅ User login with JWT tokens
3. ✅ User-to-Odoo-Patient mapping
4. ✅ SMS verification with Twilio
5. ✅ Telegram integration
6. ✅ Patient Dashboard with real Mock Odoo data
7. ✅ Appointments booking and management
8. ✅ Medical records viewing
9. ✅ Billing and invoices
10. ✅ Profile management

---

## 🔧 Step-by-Step Execution Plan

### Phase 1: Fix Database Schema (CRITICAL)

**Issue:** Database doesn't have "patient" role, only org roles.

**Solution Options:**
A. Add "PATIENT" to UserRole enum
B. Use organization membership for patients
C. Create separate patient table

**Decision:** Option A - Add PATIENT to UserRole enum

**Steps:**
1. Create Alembic migration to add PATIENT to enum
2. Update User model to allow PATIENT role
3. Restart backend
4. Test registration with patient role

**Files to modify:**
- Create new migration file
- Verify `/backend/app/models/user.py`

---

### Phase 2: Fix Authentication Flow

**Current Issues:**
- Bcrypt fixed but backend not restarted with new code
- Frontend sends form-encoded, backend expects JSON

**Steps:**
1. Restart backend to load fixed bcrypt code
2. Update frontend `useAuth` hook to send JSON instead of form-encoded
3. Test registration endpoint
4. Test login endpoint
5. Verify token storage and retrieval

**Files to modify:**
- `/frontend/src/hooks/useAuth.js`
- `/frontend/src/pages/LoginPage.jsx` (if used)
- `/frontend/src/pages/MockLoginPage.jsx`

---

### Phase 3: User-to-Patient Mapping

**Requirement:** Link authenticated users to Mock Odoo patients

**Implementation:**
1. After registration, show patient selection UI
2. User selects their patient record from Mock Odoo
3. Create mapping in `organization_memberships` table with `odoo_partner_id`
4. Store mapping for all future API calls

**API Endpoints:**
- `GET /api/v1/mappings/me` - Get current user's mapping
- `POST /api/v1/mappings` - Create new mapping
- `GET /api/v1/patient/search?query=name` - Search patients in Odoo

**Files to create/modify:**
- `/frontend/src/pages/patient/PatientOnboarding.jsx` (new)
- `/frontend/src/hooks/usePatientMapping.js` (new)

---

### Phase 4: SMS Integration (Twilio)

**Requirement:** Send verification SMS during registration

**Implementation:**
1. During registration, send SMS with verification code
2. User enters code to verify phone
3. Mark phone as verified in database

**API Endpoints:**
- `POST /api/v1/auth/send-sms-verification`
- `POST /api/v1/auth/verify-sms-code`

**Files to check:**
- `/backend/app/services/twilio_service.py`
- `/backend/app/api/v1/endpoints/auth.py`

**Environment Variables:**
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

---

### Phase 5: Telegram Integration

**Requirement:** Allow patients to connect Telegram for notifications

**Implementation:**
1. Generate unique Telegram connection link
2. Patient clicks link and starts bot
3. Bot verifies and links Telegram ID to user
4. Enable Telegram notifications

**API Endpoints:**
- `POST /api/v1/telegram/generate-link`
- `GET /api/v1/telegram/status`

**Files to check:**
- `/backend/app/services/telegram_service.py`
- `/backend/app/api/v1/endpoints/telegram.py`

**Environment Variables:**
- `TELEGRAM_BOT_TOKEN`

---

### Phase 6: Patient Dashboard Integration

**Requirement:** Display real data from Mock Odoo Dental

**API Calls Needed:**
1. `GET /api/v1/patient/profile` - Patient info
2. `GET /api/v1/patient/health-score` - Dental health score
3. `GET /api/v1/appointments?status=upcoming&limit=3` - Upcoming appointments
4. `GET /api/v1/billing/overview` - Billing summary

**Files to modify:**
- `/frontend/src/pages/patient/PatientDashboard.jsx`

**Current State:** Uses mock data in `useState`

**Target State:** Fetch from API on mount, show loading states, handle errors

---

### Phase 7: Appointments Page Integration

**Requirement:** Full appointment booking and management

**Features:**
1. List all appointments (past, upcoming, cancelled)
2. Filter by status
3. View appointment details
4. Book new appointment (wizard)
5. Cancel appointment

**API Calls Needed:**
1. `GET /api/v1/appointments` - List appointments
2. `GET /api/v1/doctors` - List doctors
3. `GET /api/v1/appointments/available-slots?doctor_id=X&date=Y` - Available slots
4. `POST /api/v1/appointments` - Create appointment
5. `PUT /api/v1/appointments/{id}/cancel` - Cancel appointment

**Files to modify:**
- `/frontend/src/pages/patient/PatientAppointments.jsx`

---

### Phase 8: Medical Records Integration

**Requirement:** Display patient's medical history

**Features:**
1. List all medical records
2. Filter by type (X-ray, treatment, report)
3. View record details
4. Display dental chart
5. View attachments (X-rays)

**API Calls Needed:**
1. `GET /api/v1/records` - List records
2. `GET /api/v1/records/{id}` - Get record detail

**Files to modify:**
- `/frontend/src/pages/patient/PatientMedicalRecords.jsx`

---

### Phase 9: Billing Integration

**Requirement:** Display invoices and payment history

**Features:**
1. Billing overview (outstanding, paid, pending)
2. List all invoices
3. Filter by status
4. View invoice details
5. Payment processing (future)

**API Calls Needed:**
1. `GET /api/v1/billing/overview` - Overview
2. `GET /api/v1/billing/invoices` - List invoices

**Files to modify:**
- `/frontend/src/pages/patient/PatientBilling.jsx`

---

### Phase 10: Profile Management Integration

**Requirement:** View and edit patient profile

**Features:**
1. View profile info
2. Edit personal details
3. SMS verification status
4. Telegram connection status
5. Email preferences

**API Calls Needed:**
1. `GET /api/v1/patient/profile` - Get profile
2. `PUT /api/v1/patient/profile` - Update profile (if exists)

**Files to modify:**
- `/frontend/src/pages/patient/PatientProfile.jsx`

---

### Phase 11: Frontend Build & Deployment

**Requirement:** Get frontend running properly

**Issues to fix:**
1. File watcher limits (already fixed with ulimit)
2. Missing utils.js (already created)
3. Config import issues (already fixed)
4. SPA routing with production build

**Steps:**
1. Use `serve` package (already installed)
2. Build frontend: `npm run build`
3. Serve with: `serve -s dist -l 5173`
4. Test all routes work

---

### Phase 12: Comprehensive Testing

**Test Scenarios:**

1. **Registration Flow**
   - Register new user
   - Verify email format
   - Verify password requirements
   - Check SMS verification
   - Link to Odoo patient
   - Verify Telegram connection

2. **Login Flow**
   - Login with credentials
   - Verify token storage
   - Check token expiration
   - Test refresh token

3. **Dashboard**
   - Load patient profile
   - Display health score
   - Show upcoming appointments
   - Display billing summary
   - Show AI suggestions

4. **Appointments**
   - List all appointments
   - Filter by status
   - View appointment details
   - Book new appointment
   - Cancel appointment

5. **Medical Records**
   - List all records
   - Filter by type
   - View record details
   - Display dental chart

6. **Billing**
   - View billing overview
   - List invoices
   - Filter by status
   - View invoice details

7. **Profile**
   - View profile
   - Edit profile
   - Check SMS status
   - Check Telegram status

---

## 🎯 Success Metrics

### Must Pass (100% Required)
- [ ] User can register with email/password
- [ ] User receives SMS verification code
- [ ] User can verify phone number
- [ ] User can connect Telegram
- [ ] User can link to Odoo patient record
- [ ] User can login and get JWT token
- [ ] Dashboard displays real patient data from Mock Odoo
- [ ] Appointments page shows real appointments
- [ ] User can book new appointment
- [ ] User can cancel appointment
- [ ] Medical records page shows real records
- [ ] Billing page shows real invoices
- [ ] Profile page displays and updates correctly
- [ ] All API calls work without errors
- [ ] Loading states display correctly
- [ ] Error messages are user-friendly
- [ ] Hebrew/RTL works perfectly
- [ ] All 5 pages are fully functional

### Performance Metrics
- [ ] Page load < 2 seconds
- [ ] API response < 500ms
- [ ] No console errors
- [ ] No memory leaks

---

## 📝 Implementation Order

### Day 1: Foundation (Database & Auth)
1. Fix UserRole enum (add PATIENT)
2. Restart backend with fixed bcrypt
3. Test registration endpoint
4. Test login endpoint
5. Fix frontend auth hook (JSON format)

### Day 2: Mapping & Onboarding
1. Implement patient search API
2. Create onboarding UI
3. Implement user-patient mapping
4. Test complete registration flow

### Day 3: SMS & Telegram
1. Configure Twilio credentials
2. Test SMS sending
3. Implement SMS verification UI
4. Configure Telegram bot
5. Test Telegram connection

### Day 4: Dashboard Integration
1. Connect dashboard to APIs
2. Implement loading states
3. Implement error handling
4. Test with real data

### Day 5: Appointments Integration
1. Connect appointments list
2. Implement booking wizard
3. Connect to available slots API
4. Test booking flow

### Day 6: Records & Billing
1. Connect medical records
2. Connect billing page
3. Test data display

### Day 7: Testing & Polish
1. End-to-end testing
2. Fix bugs
3. Polish UI/UX
4. Final verification

---

## 🚀 Let's Start!

**First Task:** Fix the UserRole enum to add PATIENT role.

**Ready to execute?** ✅


