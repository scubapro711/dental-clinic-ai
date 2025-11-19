import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './i18n/config' // Initialize i18n
import './index.css'

// Initialize Sentry for error monitoring
if (import.meta.env.PROD && import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.MODE,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    // Performance Monitoring
    tracesSampleRate: 1.0, // Capture 100% of transactions for performance monitoring
    // Session Replay
    replaysSessionSampleRate: 0.1, // Sample 10% of sessions
    replaysOnErrorSampleRate: 1.0, // Sample 100% of sessions with errors
  });
}
import './styles/responsive.css'
import './styles/accessibility.css'
import './styles/global.css'
import App from './App.jsx'

// Migrate old organization_id to new current_organization_id
// This ensures backward compatibility for existing users
const migrateOrganizationId = () => {
  const oldKey = localStorage.getItem('organization_id');
  const newKey = localStorage.getItem('current_organization_id');
  
  if (oldKey && !newKey) {
    localStorage.setItem('current_organization_id', oldKey);
    console.log('✅ Migrated organization_id to current_organization_id:', oldKey);
  }
};

// Run migration before app starts
migrateOrganizationId();

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
