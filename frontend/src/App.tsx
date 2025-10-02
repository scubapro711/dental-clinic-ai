import { useState } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState<string>('Checking...')

  // Check backend health on mount
  useState(() => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus('Backend offline'))
  })

  return (
    <div className="App">
      <header className="App-header">
        <h1>🦷 DentalAI</h1>
        <p>AI-Powered Dental Clinic Management System</p>
        <div className="status">
          <strong>Backend Status:</strong> {status}
        </div>
        <div className="version">
          Version 14.0.0 - MVP Development
        </div>
      </header>
    </div>
  )
}

export default App
