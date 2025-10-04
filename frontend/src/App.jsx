import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import { API_ENDPOINTS } from './config'

// Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ChatPage from './pages/ChatPage'
import DashboardPage from './pages/DashboardPage'
import MissionControlPage from './pages/MissionControlPage'
import MissionControlPageV2 from './pages/MissionControlPageV2'

function App() {
  // DEMO MODE: Skip authentication for testing
  const [isAuthenticated, setIsAuthenticated] = useState(true)
  const [user, setUser] = useState({
    id: 'demo-user',
    name: 'Demo User',
    email: 'demo@dentalai.com',
    role: 'admin'
  })

  // Check if user is logged in (check localStorage)
  // DISABLED FOR DEMO
  // useState(() => {
  //   const token = localStorage.getItem('access_token')
  //   if (token) {
  //     setIsAuthenticated(true)
  //     // Fetch user info
  //     fetch(API_ENDPOINTS.auth.me, {
  //       headers: {
  //         'Authorization': `Bearer ${token}`
  //       }
  //     })
  //       .then(res => res.json())
  //       .then(data => setUser(data))
  //       .catch(() => {
  //         localStorage.removeItem('access_token')
  //         setIsAuthenticated(false)
  //       })
  //   }
  // }, [])

  const handleLogin = (token, userData) => {
    localStorage.setItem('access_token', token)
    setIsAuthenticated(true)
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setIsAuthenticated(false)
    setUser(null)
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/chat" replace />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/register"
          element={
            isAuthenticated ? (
              <Navigate to="/chat" replace />
            ) : (
              <RegisterPage onRegister={handleLogin} />
            )
          }
        />
        <Route
          path="/chat"
          element={
            isAuthenticated ? (
              <ChatPage user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/dashboard/*"
          element={
            isAuthenticated ? (
              <MissionControlPageV2 user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/dashboard-v1"
          element={
            isAuthenticated ? (
              <MissionControlPage user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/dashboard-old"
          element={
            isAuthenticated ? (
              <DashboardPage user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
