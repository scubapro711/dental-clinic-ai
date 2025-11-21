# Phase 7: Portal Separation - Architecture Context

**תאריך:** 10 באוקטובר 2025  
**מטרה:** הפרדת 3 פורטלים נפרדים עם routing מתקדם ו-RBAC  
**משך זמן:** 1-2 שבועות

---

## 1. סקירה כללית - המצב הנוכחי

כרגע, המערכת כוללת **פורטל יחיד** עם מספר דפים שמשרתים גם מטופלים וגם צוות מרפאה. אין הפרדה ברורה בין ממשקי המשתמש השונים, וה-routing מתבצע בצורה בסיסית ללא בדיקות הרשאות מתקדמות.

### 1.1. מבנה Frontend הנוכחי

```
frontend/
├── src/
│   ├── pages/
│   │   ├── LoginPage.jsx                    # כניסה למערכת
│   │   ├── RegisterPage.jsx                 # הרשמה
│   │   ├── DashboardPage.jsx                # דשבורד בסיסי (patient-facing)
│   │   ├── AgenticDashboard.jsx             # דשבורד אגנטי (clinic-facing)
│   │   ├── ChatPage.jsx                     # צ'אט עם Alex
│   │   ├── MissionControlPage.jsx           # Mission Control (v1)
│   │   ├── MissionControlPageV2.jsx         # Mission Control (v2)
│   │   ├── MissionControlPageV3.jsx         # Mission Control (v3)
│   │   └── CopilotTestPage.jsx              # בדיקות Copilot
│   │
│   ├── components/
│   │   ├── widgets/                         # Widgets למרפאה
│   │   │   ├── TodaysPatientsWidget.jsx
│   │   │   ├── RevenueWidget.jsx
│   │   │   ├── DecisionQueueWidget.jsx
│   │   │   └── FineTuningWidget.jsx
│   │   │
│   │   ├── dashboard/                       # קומפוננטות דשבורד
│   │   │   ├── AgentChatModal.jsx
│   │   │   ├── AgentStatusCardV2.jsx
│   │   │   ├── ProactiveSuggestionsPanel.jsx
│   │   │   └── MissionControlLayout.jsx
│   │   │
│   │   ├── transparency/                    # שקיפות סוכנים
│   │   │   ├── AgentActivityPanel.jsx
│   │   │   └── FullTransparencyPanel.jsx
│   │   │
│   │   ├── layout/                          # Layout components
│   │   ├── ui/                              # UI primitives (shadcn)
│   │   └── agentic/                         # Agentic UX components
│   │
│   └── App.jsx                              # Main routing
│
└── clinic-portal/                           # תיקייה נפרדת (חלקית)
    └── src/
        ├── components/
        │   ├── ClinicalAssistant.tsx
        │   ├── FinancialDashboard.tsx
        │   └── InventoryDashboard.tsx
        └── pages/
            └── ClinicalDashboard.tsx
```

### 1.2. מבנה Backend הנוכחי

```
backend/app/api/v1/endpoints/
├── auth.py                          # Authentication
├── patient_portal.py                # Patient portal endpoints
├── patient_portal_odoo.py           # Patient portal + Odoo integration
├── dashboard.py                     # Dashboard endpoints (clinic)
├── dashboard_metrics.py             # Metrics for dashboard
├── ai_chat.py                       # AI chat endpoints
├── agents.py                        # Agent management
├── organizations.py                 # Organization management
├── clinic_settings.py               # Clinic settings
├── doctor.py                        # Doctor endpoints
├── team_invitations.py              # Team management
└── ... (42 endpoint files total)
```

### 1.3. Routing הנוכחי (App.jsx)

```javascript
<Routes>
  <Route path="/login" element={<MockLoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  <Route path="/chat" element={<ChatPage />} />
  <Route path="/dashboard" element={<DashboardPage />} />
  <Route path="/agentic" element={<AgenticDashboard />} />
  <Route path="/" element={<Navigate to="/agentic" />} />
</Routes>
```

**בעיות:**
- אין הפרדה בין patient portal ל-clinic portal
- אין בדיקות הרשאות ב-routing
- כל המשתמשים רואים את כל הדפים
- אין ארגון ברור של routes

---

## 2. הארכיטקטורה המבוקשת - 3 פורטלים נפרדים

### 2.1. Patient Portal (פורטל מטופלים)

**מטרה:** ממשק פשוט ונגיש למטופלים לניהול התורים, הרשומות הרפואיות והתשלומים שלהם.

**תפקידי משתמש:** `ORG_VIEWER` (מטופל)

**דפים עיקריים:**
1. **Patient Dashboard** - סקירה כללית
   - תורים קרובים
   - Dental Health Score
   - התראות ותזכורות
   - Quick actions (קביעת תור, תשלום)

2. **My Appointments** - ניהול תורים
   - רשימת תורים (עבר, עתיד)
   - קביעת תור חדש
   - ביטול/שינוי תור
   - הורדת אישורים

3. **Medical Records** - רשומות רפואיות
   - היסטוריית טיפולים
   - צילומי רנטגן
   - תוצאות בדיקות
   - תוכניות טיפול

4. **Billing & Payments** - תשלומים
   - חשבוניות
   - היסטוריית תשלומים
   - תשלום מקוון
   - תוכניות תשלום

5. **My Profile** - פרופיל אישי
   - פרטים אישיים
   - פרטי ביטוח
   - העדפות תקשורת
   - הגדרות פרטיות

6. **Chat with Alex** - צ'אט עם הסוכן
   - שאלות כלליות
   - קביעת תורים
   - בירורים פיננסיים

**קומפוננטות נדרשות:**
- `PatientDashboard.jsx`
- `AppointmentsPage.jsx`
- `MedicalRecordsPage.jsx`
- `BillingPage.jsx`
- `PatientProfilePage.jsx`
- `PatientChatPage.jsx`
- `HealthScoreCard.jsx`
- `AppointmentCard.jsx`
- `TreatmentHistoryCard.jsx`
- `InvoiceCard.jsx`

**API Endpoints:**
- `GET /api/v1/patient/profile`
- `GET /api/v1/patient/health-score`
- `GET /api/v1/patient/appointments`
- `POST /api/v1/patient/appointments`
- `GET /api/v1/patient/medical-records`
- `GET /api/v1/patient/invoices`
- `POST /api/v1/patient/payments`

---

### 2.2. Clinic Portal (פורטל מרפאה)

**מטרה:** ממשק מתקדם לצוות המרפאה עם כלים אגנטיים לניהול יומיומי.

**תפקידי משתמש:** `ORG_ADMIN`, `ORG_STAFF` (רופאים, אחיות, פקידות)

**דפים עיקריים:**
1. **Agentic Dashboard** (קיים - `AgenticDashboard.jsx`)
   - Mission Control עם 4 הסוכנים
   - Widgets: Today's Patients, Revenue, Decision Queue, Fine-Tuning
   - צ'אט מרכזי עם Alex
   - Agent Activity Panel
   - Full Transparency Panel

2. **Patients Management** - ניהול מטופלים
   - רשימת מטופלים
   - חיפוש ופילטור
   - פרופיל מטופל מלא
   - הוספת מטופל חדש
   - עריכת פרטים

3. **Schedule Management** - ניהול לוח זמנים
   - תצוגת יומן
   - קביעת תורים
   - ניהול זמינות
   - רשימת המתנה

4. **Clinical Workspace** - עבודה קלינית
   - תוכניות טיפול
   - רשומות קליניות
   - Dental Chart
   - הזמנת צילומים ובדיקות
   - הפניות למומחים

5. **Financial Management** - ניהול פיננסי
   - סקירת הכנסות
   - חשבוניות ותשלומים
   - ניהול ביטוח
   - דוחות פיננסיים

6. **Operations Dashboard** - תפעול
   - ניהול מלאי
   - ניהול צוות
   - משימות ותזכורות
   - Analytics

**קומפוננטות קיימות:**
- `AgenticDashboard.jsx` ✅
- `TodaysPatientsWidget.jsx` ✅
- `RevenueWidget.jsx` ✅
- `DecisionQueueWidget.jsx` ✅
- `FineTuningWidget.jsx` ✅
- `AgentChatModal.jsx` ✅
- `ProactiveSuggestionsPanel.jsx` ✅
- `MissionControlLayout.jsx` ✅

**קומפוננטות נדרשות:**
- `PatientsManagementPage.jsx`
- `PatientProfilePage.jsx` (clinic version)
- `SchedulePage.jsx`
- `ClinicalWorkspacePage.jsx`
- `FinancialManagementPage.jsx`
- `OperationsDashboardPage.jsx`
- `PatientListTable.jsx`
- `AppointmentCalendar.jsx`
- `TreatmentPlanEditor.jsx`
- `DentalChart.jsx`

**API Endpoints:**
- `GET /api/v1/clinic/dashboard`
- `GET /api/v1/clinic/patients`
- `GET /api/v1/clinic/appointments`
- `POST /api/v1/clinic/appointments`
- `GET /api/v1/clinic/treatments`
- `GET /api/v1/clinic/financial`
- `GET /api/v1/clinic/operations`

---

### 2.3. Admin Portal (פורטל ניהול)

**מטרה:** ממשק לניהול מערכת, ארגונים, משתמשים והרשאות.

**תפקידי משתמש:** `SUPER_ADMIN`, `ORG_OWNER`

**דפים עיקריים:**
1. **Admin Dashboard** - סקירה כללית
   - סטטיסטיקות מערכת
   - ארגונים פעילים
   - משתמשים מחוברים
   - ביצועי מערכת

2. **Organizations Management** - ניהול ארגונים
   - רשימת מרפאות
   - הוספת מרפאה חדשה
   - הגדרות מרפאה
   - Billing & Subscriptions

3. **Users & Permissions** - משתמשים והרשאות
   - רשימת משתמשים
   - ניהול תפקידים
   - הרשאות מתקדמות
   - Team invitations

4. **System Settings** - הגדרות מערכת
   - הגדרות כלליות
   - אינטגרציות (Odoo, Stripe, etc.)
   - Email templates
   - SMS settings

5. **Monitoring & Logs** - ניטור ולוגים
   - System health
   - API logs
   - Audit logs
   - Error tracking

6. **Agent Management** - ניהול סוכנים
   - הגדרות סוכנים
   - Fine-tuning
   - Performance metrics
   - Feedback analysis

**קומפוננטות נדרשות:**
- `AdminDashboard.jsx`
- `OrganizationsPage.jsx`
- `UsersManagementPage.jsx`
- `SystemSettingsPage.jsx`
- `MonitoringPage.jsx`
- `AgentManagementPage.jsx`
- `OrganizationCard.jsx`
- `UserTable.jsx`
- `SystemHealthCard.jsx`
- `LogsViewer.jsx`

**API Endpoints:**
- `GET /api/v1/admin/dashboard`
- `GET /api/v1/admin/organizations`
- `POST /api/v1/admin/organizations`
- `GET /api/v1/admin/users`
- `GET /api/v1/admin/system-settings`
- `GET /api/v1/admin/logs`
- `GET /api/v1/admin/agents`

---

## 3. RBAC (Role-Based Access Control)

### 3.1. תפקידי משתמש (User Roles)

המערכת מגדירה 5 תפקידים עיקריים:

```python
# backend/app/core/rbac.py

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"      # מנהל מערכת ראשי
    ORG_OWNER = "org_owner"          # בעלים של מרפאה
    ORG_ADMIN = "org_admin"          # מנהל מרפאה
    ORG_STAFF = "org_staff"          # צוות מרפאה (רופאים, אחיות)
    ORG_VIEWER = "org_viewer"        # מטופל (צפייה בלבד)
```

### 3.2. הרשאות (Permissions)

כל תפקיד מקבל סט של הרשאות:

```python
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        "manage_system",
        "manage_organizations",
        "manage_all_users",
        "view_all_data",
        "manage_agents",
        "view_logs",
    ],
    
    UserRole.ORG_OWNER: [
        "manage_organization",
        "manage_users",
        "manage_billing",
        "view_all_clinic_data",
        "manage_settings",
    ],
    
    UserRole.ORG_ADMIN: [
        "manage_patients",
        "manage_appointments",
        "manage_treatments",
        "view_financial_data",
        "manage_staff",
    ],
    
    UserRole.ORG_STAFF: [
        "view_patients",
        "view_appointments",
        "manage_own_appointments",
        "view_treatments",
        "create_clinical_notes",
    ],
    
    UserRole.ORG_VIEWER: [
        "view_own_profile",
        "view_own_appointments",
        "view_own_medical_records",
        "view_own_invoices",
        "book_appointments",
    ],
}
```

### 3.3. Widget Permissions

כל widget במערכת דורש הרשאות ספציפיות:

```typescript
// frontend/src/lib/widgetPermissions.ts

export const WIDGET_PERMISSIONS = {
  // Clinic Portal Widgets
  'TodaysPatientsWidget': ['view_patients', 'manage_schedule'],
  'RevenueWidget': ['view_financial_data'],
  'DecisionQueueWidget': ['approve_decisions'],
  'FineTuningWidget': ['manage_agents'],
  'ScheduleWidget': ['view_schedule', 'manage_schedule'],
  'PatientListWidget': ['view_patients'],
  'TreatmentHistoryWidget': ['view_medical_records'],
  'InsuranceWidget': ['view_insurance', 'manage_insurance'],
  
  // Patient Portal Widgets
  'HealthScoreCard': ['view_own_profile'],
  'MyAppointmentsWidget': ['view_own_appointments'],
  'MyInvoicesWidget': ['view_own_invoices'],
  
  // Admin Portal Widgets
  'SystemHealthWidget': ['manage_system'],
  'OrganizationsWidget': ['manage_organizations'],
  'UsersWidget': ['manage_all_users'],
}
```

---

## 4. Routing Strategy

### 4.1. מבנה Routes המבוקש

```
/                           → Redirect based on role
/login                      → Login page (public)
/register                   → Register page (public)

/patient/*                  → Patient Portal (ORG_VIEWER only)
  /patient/dashboard
  /patient/appointments
  /patient/medical-records
  /patient/billing
  /patient/profile
  /patient/chat

/clinic/*                   → Clinic Portal (ORG_ADMIN, ORG_STAFF)
  /clinic/dashboard
  /clinic/patients
  /clinic/schedule
  /clinic/clinical
  /clinic/financial
  /clinic/operations

/admin/*                    → Admin Portal (SUPER_ADMIN, ORG_OWNER)
  /admin/dashboard
  /admin/organizations
  /admin/users
  /admin/settings
  /admin/monitoring
  /admin/agents
```

### 4.2. Protected Routes Implementation

```typescript
// frontend/src/components/routing/ProtectedRoute.tsx

import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles: string[];
  redirectTo?: string;
}

export function ProtectedRoute({ 
  children, 
  allowedRoles, 
  redirectTo = '/login' 
}: ProtectedRouteProps) {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }
  
  if (!allowedRoles.includes(user.role)) {
    // Redirect to appropriate portal based on role
    const defaultPortal = getDefaultPortalForRole(user.role);
    return <Navigate to={defaultPortal} replace />;
  }
  
  return <>{children}</>;
}

function getDefaultPortalForRole(role: string): string {
  switch (role) {
    case 'super_admin':
    case 'org_owner':
      return '/admin/dashboard';
    case 'org_admin':
    case 'org_staff':
      return '/clinic/dashboard';
    case 'org_viewer':
      return '/patient/dashboard';
    default:
      return '/login';
  }
}
```

### 4.3. App.tsx עם Routing מלא

```typescript
// frontend/src/App.tsx

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/routing/ProtectedRoute';

// Public pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Patient Portal
import PatientDashboard from './pages/patient/PatientDashboard';
import PatientAppointments from './pages/patient/PatientAppointments';
import PatientMedicalRecords from './pages/patient/PatientMedicalRecords';
import PatientBilling from './pages/patient/PatientBilling';
import PatientProfile from './pages/patient/PatientProfile';
import PatientChat from './pages/patient/PatientChat';

// Clinic Portal
import ClinicDashboard from './pages/clinic/ClinicDashboard';
import PatientsManagement from './pages/clinic/PatientsManagement';
import ScheduleManagement from './pages/clinic/ScheduleManagement';
import ClinicalWorkspace from './pages/clinic/ClinicalWorkspace';
import FinancialManagement from './pages/clinic/FinancialManagement';
import OperationsDashboard from './pages/clinic/OperationsDashboard';

// Admin Portal
import AdminDashboard from './pages/admin/AdminDashboard';
import OrganizationsManagement from './pages/admin/OrganizationsManagement';
import UsersManagement from './pages/admin/UsersManagement';
import SystemSettings from './pages/admin/SystemSettings';
import Monitoring from './pages/admin/Monitoring';
import AgentManagement from './pages/admin/AgentManagement';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Patient Portal Routes */}
        <Route path="/patient/*" element={
          <ProtectedRoute allowedRoles={['org_viewer']}>
            <Routes>
              <Route path="dashboard" element={<PatientDashboard />} />
              <Route path="appointments" element={<PatientAppointments />} />
              <Route path="medical-records" element={<PatientMedicalRecords />} />
              <Route path="billing" element={<PatientBilling />} />
              <Route path="profile" element={<PatientProfile />} />
              <Route path="chat" element={<PatientChat />} />
              <Route path="*" element={<Navigate to="/patient/dashboard" />} />
            </Routes>
          </ProtectedRoute>
        } />
        
        {/* Clinic Portal Routes */}
        <Route path="/clinic/*" element={
          <ProtectedRoute allowedRoles={['org_admin', 'org_staff']}>
            <Routes>
              <Route path="dashboard" element={<ClinicDashboard />} />
              <Route path="patients" element={<PatientsManagement />} />
              <Route path="schedule" element={<ScheduleManagement />} />
              <Route path="clinical" element={<ClinicalWorkspace />} />
              <Route path="financial" element={<FinancialManagement />} />
              <Route path="operations" element={<OperationsDashboard />} />
              <Route path="*" element={<Navigate to="/clinic/dashboard" />} />
            </Routes>
          </ProtectedRoute>
        } />
        
        {/* Admin Portal Routes */}
        <Route path="/admin/*" element={
          <ProtectedRoute allowedRoles={['super_admin', 'org_owner']}>
            <Routes>
              <Route path="dashboard" element={<AdminDashboard />} />
              <Route path="organizations" element={<OrganizationsManagement />} />
              <Route path="users" element={<UsersManagement />} />
              <Route path="settings" element={<SystemSettings />} />
              <Route path="monitoring" element={<Monitoring />} />
              <Route path="agents" element={<AgentManagement />} />
              <Route path="*" element={<Navigate to="/admin/dashboard" />} />
            </Routes>
          </ProtectedRoute>
        } />
        
        {/* Root redirect */}
        <Route path="/" element={<RoleBasedRedirect />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 5. Layout Components

### 5.1. Patient Portal Layout

```typescript
// frontend/src/layouts/PatientPortalLayout.tsx

export function PatientPortalLayout({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <PatientHeader />
      <div className="flex">
        <PatientSidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
      <PatientFooter />
    </div>
  );
}
```

### 5.2. Clinic Portal Layout

```typescript
// frontend/src/layouts/ClinicPortalLayout.tsx

export function ClinicPortalLayout({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <ClinicHeader />
      <div className="flex">
        <ClinicSidebar />
        <main className="flex-1">
          {children}
        </main>
        <AgentActivitySidebar />
      </div>
    </div>
  );
}
```

### 5.3. Admin Portal Layout

```typescript
// frontend/src/layouts/AdminPortalLayout.tsx

export function AdminPortalLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <AdminHeader />
      <div className="flex">
        <AdminSidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

---

## 6. Backend API Organization

### 6.1. מבנה API מוצע

```
backend/app/api/v1/
├── public/              # Public endpoints (no auth)
│   ├── health.py
│   └── version.py
│
├── auth/                # Authentication endpoints
│   ├── login.py
│   ├── register.py
│   ├── refresh.py
│   └── logout.py
│
├── patient/             # Patient Portal endpoints
│   ├── profile.py
│   ├── appointments.py
│   ├── medical_records.py
│   ├── billing.py
│   └── chat.py
│
├── clinic/              # Clinic Portal endpoints
│   ├── dashboard.py
│   ├── patients.py
│   ├── schedule.py
│   ├── clinical.py
│   ├── financial.py
│   └── operations.py
│
└── admin/               # Admin Portal endpoints
    ├── dashboard.py
    ├── organizations.py
    ├── users.py
    ├── settings.py
    ├── monitoring.py
    └── agents.py
```

### 6.2. Middleware & Decorators

```python
# backend/app/core/rbac.py

from functools import wraps
from fastapi import HTTPException, Depends
from app.core.auth import get_current_user
from app.models.user import User

def require_role(allowed_roles: list[str]):
    """Decorator to require specific roles"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. Required roles: {allowed_roles}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_permission(required_permissions: list[str]):
    """Decorator to require specific permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_permissions = get_permissions_for_role(current_user.role)
            if not any(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. Required permissions: {required_permissions}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

---

## 7. תוכנית עבודה מפורטת

### Week 1: Infrastructure & Patient Portal

#### Day 1-2: Routing Infrastructure
- [ ] יצירת `ProtectedRoute` component
- [ ] יצירת `RoleBasedRedirect` component
- [ ] עדכון `App.tsx` עם routing מלא
- [ ] יצירת 3 layouts (Patient, Clinic, Admin)
- [ ] בדיקות routing בסיסיות

#### Day 3-4: Patient Portal - Core Pages
- [ ] `PatientDashboard.jsx`
- [ ] `PatientAppointments.jsx`
- [ ] `PatientProfile.jsx`
- [ ] `PatientChat.jsx`
- [ ] Patient Portal Layout + Navigation

#### Day 5: Patient Portal - Medical & Billing
- [ ] `PatientMedicalRecords.jsx`
- [ ] `PatientBilling.jsx`
- [ ] קומפוננטות משותפות (HealthScoreCard, AppointmentCard)
- [ ] אינטגרציה עם API

### Week 2: Clinic Portal & Admin Portal

#### Day 6-7: Clinic Portal Reorganization
- [ ] העברת `AgenticDashboard.jsx` ל-`/clinic/dashboard`
- [ ] `PatientsManagement.jsx`
- [ ] `ScheduleManagement.jsx`
- [ ] Clinic Portal Layout + Navigation
- [ ] Widget permissions implementation

#### Day 8-9: Admin Portal - Core
- [ ] `AdminDashboard.jsx`
- [ ] `OrganizationsManagement.jsx`
- [ ] `UsersManagement.jsx`
- [ ] Admin Portal Layout + Navigation

#### Day 10: Testing & Documentation
- [ ] E2E tests לכל פורטל
- [ ] בדיקות הרשאות
- [ ] תיעוד API
- [ ] תיעוד משתמש

---

## 8. Success Criteria

### 8.1. Functional Requirements
- ✅ 3 פורטלים נפרדים עם routing מלא
- ✅ RBAC מלא עם בדיקות הרשאות
- ✅ Widget permissions
- ✅ Role-based redirects
- ✅ Layouts נפרדים לכל פורטל

### 8.2. Security Requirements
- ✅ אין cross-portal access
- ✅ כל endpoint מוגן עם decorators
- ✅ Token validation
- ✅ Role validation
- ✅ Permission validation

### 8.3. UX Requirements
- ✅ Navigation ברור לכל פורטל
- ✅ Branding שונה לכל פורטל
- ✅ Responsive design
- ✅ Loading states
- ✅ Error handling

### 8.4. Performance Requirements
- ✅ Fast initial load
- ✅ Code splitting per portal
- ✅ Lazy loading
- ✅ Caching strategy

---

## 9. מסמכי רפרנס

### תיעוד קיים:
1. `docs/work-plans/CLINIC_PORTAL_WORK_PLAN_V2.md` - תוכנית מקורית
2. `docs/work-plans/PHASE_3_PATIENT_PORTAL.md` - מפרט Patient Portal
3. `docs/work-plans/MASTER_PLAN_FINAL_V2.md` - תוכנית אב
4. `PHASE_5.5_COMPLETION_REPORT.md` - דוח השלמת כלים
5. `PHASE_6.5_COMPLETION_REPORT.md` - דוח בדיקות ביצועים

### קוד קיים:
1. `frontend/src/App.jsx` - Routing נוכחי
2. `frontend/src/pages/AgenticDashboard.jsx` - Clinic Dashboard
3. `frontend/src/pages/DashboardPage.jsx` - Patient Dashboard (בסיסי)
4. `frontend/src/components/widgets/*` - Widgets קיימים
5. `backend/app/api/v1/endpoints/patient_portal.py` - Patient API
6. `backend/app/core/rbac.py` - RBAC infrastructure

---

**מוכן להתחיל Phase 7! 🚀**

