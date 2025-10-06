import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Error Boundary
import ErrorBoundary from './components/ErrorBoundary'

// Pages - Only the new Agentic Dashboard
import AgenticDashboard from './pages/AgenticDashboard'

function App() {
  // DEMO MODE: Skip authentication for testing
  const [isAuthenticated] = useState(true)
  const [user] = useState({
    id: 'demo-user',
    name: 'Dr. User',
    email: 'demo@dentalai.com',
    role: 'owner' // Full access for demo
  })

  const handleLogout = () => {
    // For demo, just reload
    window.location.reload()
  }

  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          {/* Main Dashboard - Agentic Dashboard Only */}
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? (
                <AgenticDashboard user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
          
          {/* Root redirects to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Catch all - redirect to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  )
}

export default App
