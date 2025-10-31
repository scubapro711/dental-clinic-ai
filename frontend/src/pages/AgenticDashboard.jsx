import { useState, useRef } from 'react';
import '../styles/dashboard.css';
import '../styles/transparency.css';
import '../styles/widgets.css';
import '../styles/coordination.css';
import '../styles/design-system.css';  // Import new design system
import FloatingChatButton from '../components/chat/FloatingChatButton';
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
import { Sparkles, History, Users, CheckCircle, DollarSign, AlertTriangle, Activity, Stethoscope, Zap, Eye } from 'lucide-react';
import ComplianceAlerts from '../components/compliance/ComplianceAlerts';
import { exportReasoningLog } from '../components/transparency/EnhancedTransparencyPanel';
import { getUserInfo } from '../utils/rbac';
import { DashboardProvider } from '../contexts/DashboardContext';
import { WidgetContainer } from '../components/dashboard/WidgetContainer';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { isFeatureEnabled } from '../config/features';

/**
 * AgenticDashboard v2.0 - Modern Dashboard with Design System
 * 
 * Features:
 * - Clean, modern card-based layout
 * - Responsive grid (2-4 columns based on screen size)
 * - Widget customization (collapse/expand)
 * - RBAC integration
 * - RTL support
 * - Professional color palette
 * - Smooth animations
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
  const chatInputRef = useRef(null);
  const userInfo = getUserInfo();
  
  // Feature flag: Dashboard customization
  const enableCustomization = isFeatureEnabled('ENABLE_DASHBOARD_CUSTOMIZATION');

  // Handler to send message to chat from widgets
  const handleChatWithAgent = (message) => {
    if (chatInputRef.current) {
      chatInputRef.current.sendMessage(message);
    }
  };

  // Load conversation history
  const handleSelectConversation = async (conversationId) => {
    try {
      const response = await fetch(`/api/v1/ai/conversations/${conversationId}`, {
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
          background: 'var(--background-secondary)',
          padding: 'var(--spacing-xl)'
        }}
      >
        {/* Original Header (keeping for navigation) */}
        <div 
          className="dentaflow-header"
          style={{
            marginBottom: 'var(--spacing-xl)',
            background: 'var(--background)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--spacing-lg)',
            boxShadow: 'var(--shadow-md)'
          }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{
                  background: 'var(--gradient-primary)',
                  borderRadius: 'var(--radius-full)'
                }}
              >
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 
                  className="text-base md:text-xl"
                  style={{
                    fontSize: 'var(--font-size-xl)',
                    fontWeight: 'var(--font-weight-bold)',
                    color: 'var(--foreground)',
                    margin: '0'
                  }}
                >
                  DentaFlow<span className="hidden sm:inline"> Mission Control</span>
                </h1>
                <p 
                  className="text-xs hidden md:block"
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--foreground-tertiary)',
                    margin: '0'
                  }}
                >
                  Welcome back, {userInfo?.name || 'User'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowHistorySidebar(true)}
                className="btn-secondary"
                aria-label="View conversation history"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-xs)',
                  padding: '12px 24px',
                  borderRadius: 'var(--radius-md)',
                  fontWeight: 'var(--font-weight-semibold)',
                  fontSize: 'var(--font-size-base)',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all var(--transition-base)',
                  background: 'var(--muted)',
                  color: 'var(--foreground)'
                }}
              >
                <History className="w-4 h-4" />
                <span className="hidden sm:inline">History</span>
              </button>
            </div>
          </div>
        </div>

        {/* Dashboard Customization Header */}
        {enableCustomization && <DashboardHeader />}

        {/* Dashboard Widgets Grid (Responsive: 2-4 columns) */}
        <div 
          className="dashboard-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 'var(--spacing-lg)'
          }}
        >
          {/* Priority 1: Today's Patients */}
          <ProtectedWidget widgetId="todays-patients">
            <WidgetContainer
              widgetId="todays-patients"
              title="Today's Patients"
              icon={<Users size={20} />}
              iconColor="blue"
            >
              <TodaysPatientsWidget onChatWithPatient={handleChatWithAgent} />
            </WidgetContainer>
          </ProtectedWidget>

          {/* Priority 2: Decision Queue */}
          <ProtectedWidget widgetId="decision-queue">
            <WidgetContainer
              widgetId="decision-queue"
              title="Decision Queue"
              icon={<CheckCircle size={20} />}
              iconColor="green"
            >
              <DecisionQueueWidget onChatWithAgent={handleChatWithAgent} />
            </WidgetContainer>
          </ProtectedWidget>

          {/* Priority 3: Revenue Widget */}
          <ProtectedWidget widgetId="revenue">
            <WidgetContainer
              widgetId="revenue"
              title="Revenue Analytics"
              icon={<DollarSign size={20} />}
              iconColor="cyan"
            >
              <RevenueWidget onChatWithAgent={handleChatWithAgent} />
            </WidgetContainer>
          </ProtectedWidget>

          {/* Priority 4: Compliance Alerts */}
          <ProtectedWidget widgetId="compliance-alerts">
            <WidgetContainer
              widgetId="compliance-alerts"
              title="Compliance Alerts"
              icon={<AlertTriangle size={20} />}
              iconColor="orange"
            >
              <ComplianceAlerts onChatWithAgent={handleChatWithAgent} />
            </WidgetContainer>
          </ProtectedWidget>

          {/* Priority 5: Clinical Dashboard */}
          <ProtectedWidget widgetId="clinical-system">
            <WidgetContainer
              widgetId="clinical-system"
              title="Clinical System"
              icon={<Stethoscope size={20} />}
              iconColor="purple"
            >
              <ClinicalDashboard 
                patient={{ 
                  id: 1, 
                  name: 'David Cohen', 
                  age: 45, 
                  lastVisit: '2025-09-15' 
                }} 
              />
            </WidgetContainer>
          </ProtectedWidget>

          {/* Priority 6: Enhanced Fine-Tuning */}
          <ProtectedWidget widgetId="fine-tuning">
            <WidgetContainer
              widgetId="fine-tuning"
              title="AI Fine-Tuning"
              icon={<Zap size={20} />}
              iconColor="orange"
            >
              <EnhancedFineTuningWidget onChatWithAgent={handleChatWithAgent} />
            </WidgetContainer>
          </ProtectedWidget>

          {/* Priority 7: Agent Activity Panel */}
          <ProtectedWidget widgetId="agent-activity">
            <WidgetContainer
              widgetId="agent-activity"
              title="Agent Activity"
              icon={<Activity size={20} />}
              iconColor="cyan"
            >
              <AgentActivityPanel
                activeAgent={activeAgent}
                currentTask={currentTask}
                toolsInUse={toolsInUse}
                summary={summary}
              />
            </WidgetContainer>
          </ProtectedWidget>

          {/* Priority 8: Enhanced Transparency Panel */}
          <ProtectedWidget widgetId="transparency-panel">
            <WidgetContainer
              widgetId="transparency-panel"
              title="Transparency Panel"
              icon={<Eye size={20} />}
              iconColor="purple"
            >
              <EnhancedTransparencyPanel 
                reasoningSteps={reasoningSteps}
                isActive={!!activeAgent}
                onClear={clearActivity}
                onExport={() => exportReasoningLog(reasoningSteps, activeAgent, currentTask, toolsInUse, summary)}
              />
            </WidgetContainer>
          </ProtectedWidget>
        </div>

        {/* Floating Chat Button */}
        <FloatingChatButton
          conversationId={currentConversationId}
          initialMessages={conversationMessages || []}
          onStreamEvent={handleStreamEvent}
          onClearChat={clearActivity}
          chatInputRef={chatInputRef}
        />

        {/* Conversation History Sidebar */}
        <ConversationHistorySidebar
          isOpen={showHistorySidebar}
          onClose={() => setShowHistorySidebar(false)}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          currentConversationId={currentConversationId}
        />
      </div>
    </DashboardProvider>
  );
}

