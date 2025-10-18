import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute, RoleBasedRedirect } from './components/routing/ProtectedRoute'

// Layouts
import PatientLayout from './layouts/PatientLayout'
import ClinicLayout from './layouts/ClinicLayout'

// Auth Pages
import SimpleMockLogin from './pages/SimpleMockLogin'
import RegisterPage from './pages/RegisterPage'

// Onboarding Pages
import ClinicOnboardingWizard from './pages/ClinicOnboardingWizard'
import OnboardingDashboard from './pages/OnboardingDashboard'

// Patient Portal Pages
import PatientDashboard from './pages/patient/PatientDashboard'
import PatientAppointments from './pages/patient/PatientAppointments'
import PatientMedicalRecords from './pages/patient/PatientMedicalRecords'
import PatientBilling from './pages/patient/PatientBilling'
import PatientProfile from './pages/patient/PatientProfile'

// Clinic Portal Pages
import AgenticDashboard from './pages/AgenticDashboard'
import PatientsManagement from './pages/clinic/PatientsManagement'
import CommunicationsHub from './pages/clinic/CommunicationsHub'
import SecuritySettings from './pages/SecuritySettings'

// Billing Components
import { PricingPage, SubscriptionManagement, BillingDashboard } from './components/billing'

// Super Admin Pages
import {
  SuperAdminDashboard,
  OrganizationsPage,
  RevenueDashboard,
  UsageDashboard,
  CostDashboard,
  PilotApplications,
} from './pages/super-admin'

// Shared
import ChatPage from './pages/ChatPage'

// Legal Pages
import LegalDocument from './pages/legal/LegalDocument'

// Onboarding
import ClinicOnboarding from './pages/onboarding/ClinicOnboarding'

// Demo Portal
import { DemoProvider } from './contexts/DemoContext'
import DemoPortal from './pages/DemoPortal'
import DemoPortalEnhanced from './pages/DemoPortalEnhanced'

// Landing Page
import LandingPage from './pages/LandingPage'

// 404 Page
function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-8">Page not found</p>
        <a href="/" className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Go Home
        </a>
      </div>
    </div>
  )
}

// Temporary "Coming Soon" component for unimplemented pages
function ComingSoon({ title }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
          <span className="text-4xl">🚧</span>
        </div>
        <h1 className="text-3xl font-bold text-gray-800 mb-2">{title}</h1>
        <p className="text-gray-600 mb-6">This page is under construction</p>
        <a href="/" className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-block">
          Go Back
        </a>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <DemoProvider>
        <Routes>
        {/* Landing Page (Public) */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Dashboard - Role-based redirect */}
        <Route path="/dashboard-redirect" element={<RoleBasedRedirect />} />
        
        {/* Auth Routes (Public) */}
        <Route path="/login" element={<SimpleMockLogin />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Onboarding Routes (Public/Protected) */}
        <Route path="/onboarding" element={<ClinicOnboardingWizard />} />
        <Route path="/onboarding/dashboard" element={<OnboardingDashboard />} />
        <Route path="/onboarding/flow" element={<ClinicOnboarding />} />
        
        {/* Legal Pages (Public) */}
        <Route path="/legal/:documentId" element={<LegalDocument />} />
        
        {/* Demo Portal (Public) */}
        <Route 
          path="/demo" 
          element={<DemoPortalEnhanced />} 
        />
        
        {/* Demo Portal - Basic Version (Public) */}
        <Route 
          path="/demo-basic" 
          element={<DemoPortal />} 
        />
        
        {/* Pricing Page (Public) */}
        <Route path="/pricing" element={<PricingPage />} />
        
        {/* Patient Portal Routes (ORG_VIEWER) */}
        <Route
          path="/patient"
          element={
            <ProtectedRoute allowedRoles={['org_viewer']}>
              <PatientLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/patient/dashboard" replace />} />
          <Route path="dashboard" element={<PatientDashboard />} />
          <Route path="appointments" element={<PatientAppointments />} />
          <Route path="medical-records" element={<PatientMedicalRecords />} />
          <Route path="billing" element={<PatientBilling />} />
          <Route path="profile" element={<PatientProfile />} />
          <Route path="chat" element={<ChatPage />} />
        </Route>
        
        {/* Clinic Portal Routes (ORG_ADMIN, ORG_STAFF) */}
        <Route
          path="/clinic"
          element={
            <ProtectedRoute allowedRoles={['org_admin', 'org_staff']}>
              <ClinicLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/clinic/dashboard" replace />} />
          <Route path="dashboard" element={<AgenticDashboard />} />
          <Route path="patients" element={<PatientsManagement />} />
          <Route path="communications" element={<CommunicationsHub />} />
          <Route path="appointments" element={<ComingSoon title="Appointments Management" />} />
          <Route path="agents" element={<ComingSoon title="AI Agents" />} />
          <Route path="analytics" element={<ComingSoon title="Analytics" />} />
          <Route path="subscription" element={<SubscriptionManagement />} />
          <Route path="security" element={<SecuritySettings />} />
          <Route path="settings" element={<ComingSoon title="Settings" />} />
        </Route>
        
        {/* Super Admin Portal Routes (SUPER_ADMIN) */}
        <Route
          path="/super-admin/*"
          element={
            <ProtectedRoute allowedRoles={['super_admin']}>
              <Routes>
                <Route path="dashboard" element={<SuperAdminDashboard />} />
                <Route path="organizations" element={<OrganizationsPage />} />
                <Route path="organizations/:id" element={<ComingSoon title="Organization Details" />} />
                <Route path="revenue" element={<RevenueDashboard />} />
                <Route path="usage" element={<UsageDashboard />} />
                <Route path="costs" element={<CostDashboard />} />
                <Route path="pilot-applications" element={<PilotApplications />} />
                <Route path="analytics" element={<ComingSoon title="Analytics & Insights" />} />
                <Route path="settings" element={<ComingSoon title="Settings" />} />
                <Route path="*" element={<Navigate to="/super-admin/dashboard" replace />} />
              </Routes>
            </ProtectedRoute>
          }
        />
        
        {/* Legacy Admin Routes - Redirect to Super Admin */}
        <Route path="/admin/*" element={<Navigate to="/super-admin/dashboard" replace />} />
        
        {/* Legacy Routes (Redirect to new structure) */}
        <Route path="/dashboard" element={<Navigate to="/patient/dashboard" replace />} />
        <Route path="/agentic" element={<Navigate to="/clinic/dashboard" replace />} />
        <Route path="/chat" element={<Navigate to="/patient/chat" replace />} />
        <Route path="/mission-control" element={<Navigate to="/clinic/dashboard" replace />} />
        
        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      </DemoProvider>
    </Router>
  )
}

export default App

