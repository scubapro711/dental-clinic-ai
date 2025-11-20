import React, { useState, useRef, useEffect } from 'react';
import '../styles/dashboard.css';
import '../styles/transparency.css';
import '../styles/widgets.css';
import '../styles/coordination.css';
import '../styles/design-system.css';
import '../styles/dashboard-grid.css';  // NEW: Grid styles
import DemoChatButton from '../components/DemoChatButton';
import AgentActivityPanel from '../components/transparency/AgentActivityPanel';
import EnhancedTransparencyPanel from '../components/transparency/EnhancedTransparencyPanel';
import TodaysPatientsWidget from '../components/widgets/TodaysPatientsWidget';
import RevenueWidget from '../components/widgets/RevenueWidget';
import DecisionQueueWidget from '../components/widgets/DecisionQueueWidget';
import ClinicalDashboard from '../components/clinical/ClinicalDashboard';
import EnhancedFineTuningWidget from '../components/fine-tuning/EnhancedFineTuningWidget';
import ConversationHistorySidebar from '../components/ConversationHistorySidebar';
import ProtectedWidget from '../components/rbac/ProtectedWidget';
import useAgentActivity from '../hooks/useAgentActivity';
import { Sparkles, History } from 'lucide-react';
import ComplianceAlerts from '../components/compliance/ComplianceAlerts';
import { exportReasoningLog } from '../components/transparency/EnhancedTransparencyPanel';
import { getUserInfo } from '../utils/rbac';
import { DashboardProvider } from '../contexts/DashboardContext';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { NavigationSidebar } from '../components/dashboard/NavigationSidebar';
import DashboardGrid from '../components/dashboard/DashboardGrid';
import PatientModal from '../components/patients/PatientModal';
import FullPatientFile from '../components/patients/FullPatientFile';
import AddTreatmentModal from '../components/patients/AddTreatmentModal';
import DemoModeBanner from '../components/demo/DemoModeBanner';
import { isFeatureEnabled } from '../config/features';
import API_CONFIG from '@/config/api';

/**
 * AgenticDashboard v3.0 - Professional SaaS Dashboard
 * 
 * Features:
 * - Fixed right sidebar with widget library
 * - Drag & drop grid layout (react-grid-layout)
 * - Resize widgets
 * - Responsive breakpoints
 * - Add/remove widgets dynamically
 * - Save/load layout per user+org
 * - RBAC integration
 * - RTL support
 * - Multi-tenant isolation
 */
export default function AgenticDashboard() {
  const {
    activeAgent,
    currentTask,
    toolsInUse,
    summary,
    reasoningSteps,
    handleStreamEvent,
    clearActivity
  } = useAgentActivity();

  const [showHistorySidebar, setShowHistorySidebar] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationMessages, setConversationMessages] = useState([]);
  
  // Drill-down navigation state (v2)
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedPatient, setSelectedPatient] = useState(null);        // Level 1: Quick view modal
  const [fullFilePatientId, setFullFilePatientId] = useState(null);   // Level 2: Full patient file
  const [showTreatmentModal, setShowTreatmentModal] = useState(false); // Level 3: Add treatment
  
  // Demo mode state
  const isDemoMode = localStorage.getItem('demo_mode') === 'true';
  const demoExpiresAt = localStorage.getItem('demo_expires_at');
  // Dark mode with localStorage persistence and system preference detection
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('dentaflow_dark_mode');
    if (saved !== null) {
      return JSON.parse(saved);
    }
    // If no saved preference, use system preference
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const chatInputRef = useRef(null);
  const userInfo = getUserInfo();
  
  // Feature flag: Dashboard customization
  const enableCustomization = isFeatureEnabled('ENABLE_DASHBOARD_CUSTOMIZATION');

  // Dark mode effect with localStorage persistence
  useEffect(() => {
    // Save to localStorage
    localStorage.setItem('dentaflow_dark_mode', JSON.stringify(darkMode));
    
    // Apply to document
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Prevent transitions on initial load
  useEffect(() => {
    // Add no-transitions class on mount
    document.documentElement.classList.add('no-transitions');
    
    // Remove it after a short delay to enable transitions
    const timer = setTimeout(() => {
      document.documentElement.classList.remove('no-transitions');
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);

  // Handler to send message to chat from widgets
  const handleChatWithAgent = (message) => {
    if (chatInputRef.current) {
      chatInputRef.current.sendMessage(message);
    }
  };

  // Load conversation history
  const handleSelectConversation = async (conversationId) => {
    try {
      const response = await fetch(API_CONFIG.endpoint('ai/conversations/${conversationId}'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentConversationId(conversationId);
        setConversationMessages(data.messages || []);
        clearActivity();
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  // Start new conversation
  const handleNewConversation = () => {
    setCurrentConversationId(null);
    setConversationMessages([]);
    clearActivity();
  };

  return (
    <DashboardProvider>
      <div 
        className="dashboard-container" 
        dir="rtl"
        style={{
          minHeight: '100vh',
          background: 'var(--background)',
          position: 'relative',
          paddingTop: isDemoMode ? '140px' : '80px'
        }}
      >
        {/* Demo Mode Banner */}
        {isDemoMode && demoExpiresAt && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 101
          }}>
            <DemoModeBanner expiresAt={demoExpiresAt} />
          </div>
        )}
        
        {/* Header - Sticky (hidden in full patient file) */}
        {currentView !== 'patient_file_full' && (
          <div style={{
            position: 'fixed',
            top: isDemoMode ? '60px' : 0,
            left: 0,
            right: 0,
            zIndex: 100,
            background: 'var(--background)',
            borderBottom: '1px solid var(--border)',
            padding: '0 20px'
          }}>
            <DashboardHeader 
            userInfo={userInfo}
            onExportLog={() => exportReasoningLog(reasoningSteps)}
            onToggleHistory={() => setShowHistorySidebar(!showHistorySidebar)}
            enableCustomization={enableCustomization}
            darkMode={darkMode}
            onToggleDarkMode={() => setDarkMode(!darkMode)}
          />
          </div>
        )}

        {/* Main Content - Conditional based on currentView */}
        {currentView === 'patient_file_full' ? (
          <FullPatientFile 
            patientId={fullFilePatientId}
            onBack={() => {
              setCurrentView('dashboard')
              setFullFilePatientId(null)
            }}
            onAddTreatment={() => setShowTreatmentModal(true)}
          />
        ) : (
          <DashboardGrid onPatientSelect={setSelectedPatient} />
        )}

        {/* Fixed Right Sidebar */}
        <NavigationSidebar 
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode(!darkMode)}
          onLogout={() => {
            localStorage.clear()
            window.location.href = '/login'
          }}
        />

        {/* Conversation History Sidebar (Left) */}
        {showHistorySidebar && (
          <ConversationHistorySidebar
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            onClose={() => setShowHistorySidebar(false)}
          />
        )}

        {/* Draggable Chat Button */}
        <DemoChatButton />

        {/* Agent Activity Indicator */}
        {activeAgent && (
          <div
            style={{
              position: 'fixed',
              top: 'var(--spacing-lg)',
              left: 'var(--spacing-lg)',
              background: 'var(--primary)',
              color: 'var(--primary-foreground)',
              padding: '12px 20px',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-lg)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-sm)',
              zIndex: 'var(--z-fixed)',
              animation: 'pulse 2s ease-in-out infinite'
            }}
          >
            <Sparkles size={18} className="animate-spin" />
            <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 'var(--font-weight-semibold)' }}>
              {activeAgent} is working...
            </span>
          </div>
        )}
        
        {/* Patient Modal (Level 1) */}
        {selectedPatient && (
          <PatientModal 
            patient={selectedPatient}
            onClose={() => setSelectedPatient(null)}
            onOpenFullFile={(pid) => {
              setFullFilePatientId(pid)
              setCurrentView('patient_file_full')
              setSelectedPatient(null)
            }}
          />
        )}
        
        {/* Add Treatment Modal (Level 3) */}
        {showTreatmentModal && (
          <AddTreatmentModal 
            patientId={fullFilePatientId}
            onClose={() => setShowTreatmentModal(false)}
            onSave={(treatment) => {
              setShowTreatmentModal(false)
              // Refresh patient data would happen here
              console.log('Treatment saved:', treatment)
            }}
          />
        )}
      </div>
    </DashboardProvider>
  );
}

