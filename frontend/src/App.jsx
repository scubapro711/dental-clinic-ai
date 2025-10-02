import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ChatPage from './pages/ChatPage'
import DashboardPage from './pages/DashboardPage'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)

  // Check if user is logged in (check localStorage)
  useState(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      setIsAuthenticated(true)
      // Fetch user info
      fetch('http://localhost:8000/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then(res => res.json())
        .then(data => setUser(data))
        .catch(() => {
          localStorage.removeItem('access_token')
          setIsAuthenticated(false)
        })
    }
  }, [])

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
          path="/dashboard"
          element={
            isAuthenticated ? (
              <DashboardPage user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="/" element={<Navigate to="/chat" replace />} />
      </Routes>
    </Router>
  )
}

export default App
