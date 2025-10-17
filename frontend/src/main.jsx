import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './i18n/config' // Initialize i18n
import './index.css'
import './styles/responsive.css'
import './styles/accessibility.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
