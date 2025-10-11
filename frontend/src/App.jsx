import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Routing components
import { ProtectedRoute, RoleBasedRedirect } from './components/routing/ProtectedRoute'

// Auth pages (public)
import MockLoginPage from './pages/MockLoginPage'
import RegisterPage from './pages/RegisterPage'

// Patient Portal pages
import PatientDashboard from './pages/patient/PatientDashboard'
import PatientAppointments from './pages/patient/PatientAppointments'
import PatientMedicalRecords from './pages/patient/PatientMedicalRecords'
import PatientBilling from './pages/patient/PatientBilling'
import PatientProfile from './pages/patient/PatientProfile'
import ChatPage from './pages/ChatPage'

// Clinic Portal pages
import AgenticDashboard from './pages/AgenticDashboard'
import PatientsManagement from './pages/clinic/PatientsManagement'

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
      <Routes>
        {/* Root - Role-based redirect */}
        <Route path="/" element={<RoleBasedRedirect />} />
        
        {/* Auth Routes (Public) */}
        <Route path="/login" element={<MockLoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Patient Portal Routes (ORG_VIEWER) */}
        <Route
          path="/patient/*"
          element={
            <ProtectedRoute allowedRoles={['org_viewer']}>
              <Routes>
                <Route path="dashboard" element={<PatientDashboard />} />
                <Route path="appointments" element={<PatientAppointments />} />
                <Route path="medical-records" element={<PatientMedicalRecords />} />
                <Route path="billing" element={<PatientBilling />} />
                <Route path="profile" element={<PatientProfile />} />
                <Route path="chat" element={<ChatPage />} />
                <Route path="*" element={<Navigate to="/patient/dashboard" replace />} />
              </Routes>
            </ProtectedRoute>
          }
        />
        
        {/* Clinic Portal Routes (ORG_ADMIN, ORG_STAFF) */}
        <Route
          path="/clinic/*"
          element={
            <ProtectedRoute allowedRoles={['org_admin', 'org_staff']}>
              <Routes>
                <Route path="dashboard" element={<AgenticDashboard />} />
                <Route path="patients" element={<PatientsManagement />} />
                <Route path="schedule" element={<ComingSoon title="Schedule Management" />} />
                <Route path="clinical" element={<ComingSoon title="Clinical Workspace" />} />
                <Route path="financial" element={<ComingSoon title="Financial Management" />} />
                <Route path="operations" element={<ComingSoon title="Operations Dashboard" />} />
                <Route path="*" element={<Navigate to="/clinic/dashboard" replace />} />
              </Routes>
            </ProtectedRoute>
          }
        />
        
        {/* Admin Portal Routes (SUPER_ADMIN) */}
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute allowedRoles={['super_admin']}>
              <Routes>
                <Route path="dashboard" element={<ComingSoon title="Admin Dashboard" />} />
                <Route path="organizations" element={<ComingSoon title="Organizations" />} />
                <Route path="users" element={<ComingSoon title="Users" />} />
                <Route path="settings" element={<ComingSoon title="Settings" />} />
                <Route path="monitoring" element={<ComingSoon title="Monitoring" />} />
                <Route path="agents" element={<ComingSoon title="Agents" />} />
                <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
              </Routes>
            </ProtectedRoute>
          }
        />
        
        {/* Legacy Routes (Redirect to new structure) */}
        <Route path="/dashboard" element={<Navigate to="/patient/dashboard" replace />} />
        <Route path="/agentic" element={<Navigate to="/clinic/dashboard" replace />} />
        <Route path="/chat" element={<Navigate to="/patient/chat" replace />} />
        
        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  )
}

export default App
