import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Pages
import MissionControlPage from './pages/MissionControlPage'

// TEST VERSION - NO AUTHENTICATION REQUIRED
function App() {
  const mockUser = {
    id: 1,
    email: 'test@example.com',
    name: 'Test User'
  }

  const handleLogout = () => {
    console.log('Logout clicked')
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/dashboard"
          element={<MissionControlPage user={mockUser} onLogout={handleLogout} />}
        />
        <Route
          path="/mission-control"
          element={<MissionControlPage user={mockUser} onLogout={handleLogout} />}
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
