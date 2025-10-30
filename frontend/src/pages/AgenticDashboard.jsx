import { useState, useRef } from 'react';
import '../styles/dashboard.css';
import '../styles/transparency.css';
import '../styles/widgets.css';
import '../styles/coordination.css';
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
 * AgenticDashboard Component
 * 
 * Main dashboard with 2-column grid layout and floating chat button.
 * Follows healthcare UX best practices.
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
      <div className="h-full flex flex-col dentaflow-dashboard-background">
      {/* Header */}
      <div className="dentaflow-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full dentaflow-header-logo flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-base md:text-xl dentaflow-header-title">
                DentaFlow<span className="hidden sm:inline"> Mission Control</span>
              </h1>
              <p className="text-xs dentaflow-header-subtitle hidden md:block">
                Welcome back, {userInfo?.name || 'User'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowHistorySidebar(true)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
              aria-label="View conversation history"
            >
              <History className="w-4 h-4" />
              <span className="hidden sm:inline">History</span>
            </button>
          </div>
        </div>
      </div>

      {/* Dashboard Customization Header */}
      {enableCustomization && <DashboardHeader />}

      {/* Dashboard Widgets Grid (2-column layout) */}
      <div className="dashboard-widgets-grid">
        {/* Priority 1: Today's Patients */}
        <ProtectedWidget widgetId="todays-patients">
          <WidgetContainer
            widgetId="todays-patients"
            title="Today's Patients"
            icon={<Users size={20} />}
          >
            <div className="dashboard-widget-card">
              <TodaysPatientsWidget onChatWithPatient={handleChatWithAgent} />
            </div>
          </WidgetContainer>
        </ProtectedWidget>

        {/* Priority 2: Decision Queue */}
        <ProtectedWidget widgetId="decision-queue">
          <WidgetContainer
            widgetId="decision-queue"
            title="Decision Queue"
            icon={<CheckCircle size={20} />}
          >
            <div className="dashboard-widget-card">
              <DecisionQueueWidget onChatWithAgent={handleChatWithAgent} />
            </div>
          </WidgetContainer>
        </ProtectedWidget>

        {/* Priority 3: Revenue Widget */}
        <ProtectedWidget widgetId="revenue">
          <WidgetContainer
            widgetId="revenue"
            title="Revenue Analytics"
            icon={<DollarSign size={20} />}
          >
            <div className="dashboard-widget-card">
              <RevenueWidget onChatWithAgent={handleChatWithAgent} />
            </div>
          </WidgetContainer>
        </ProtectedWidget>

        {/* Priority 4: Compliance Alerts */}
        <ProtectedWidget widgetId="compliance-alerts">
          <WidgetContainer
            widgetId="compliance-alerts"
            title="Compliance Alerts"
            icon={<AlertTriangle size={20} />}
          >
            <div className="dashboard-widget-card">
              <ComplianceAlerts onChatWithAgent={handleChatWithAgent} />
            </div>
          </WidgetContainer>
        </ProtectedWidget>

        {/* Priority 5: Clinical Dashboard (Full-width) */}
        <ProtectedWidget widgetId="clinical-system">
          <WidgetContainer
            widgetId="clinical-system"
            title="Clinical System"
            icon={<Stethoscope size={20} />}
          >
            <div className="dashboard-widget-card dashboard-widget-full">
              <ClinicalDashboard 
                patient={{ 
                  id: 1, 
                  name: 'David Cohen', 
                  age: 45, 
                  lastVisit: '2025-09-15' 
                }} 
              />
            </div>
          </WidgetContainer>
        </ProtectedWidget>

        {/* Priority 6: Enhanced Fine-Tuning */}
        <ProtectedWidget widgetId="fine-tuning">
          <WidgetContainer
            widgetId="fine-tuning"
            title="AI Fine-Tuning"
            icon={<Zap size={20} />}
          >
            <div className="dashboard-widget-card">
              <EnhancedFineTuningWidget onChatWithAgent={handleChatWithAgent} />
            </div>
          </WidgetContainer>
        </ProtectedWidget>

        {/* Priority 7: Agent Activity Panel */}
        <ProtectedWidget widgetId="agent-activity">
          <WidgetContainer
            widgetId="agent-activity"
            title="Agent Activity"
            icon={<Activity size={20} />}
          >
            <div className="dashboard-widget-card">
              <AgentActivityPanel
                activeAgent={activeAgent}
                currentTask={currentTask}
                toolsInUse={toolsInUse}
                summary={summary}
              />
            </div>
          </WidgetContainer>
        </ProtectedWidget>

        {/* Priority 8: Enhanced Transparency Panel (Full-width) */}
        <ProtectedWidget widgetId="transparency-panel">
          <WidgetContainer
            widgetId="transparency-panel"
            title="Transparency Panel"
            icon={<Eye size={20} />}
          >
            <div className="dashboard-widget-card dashboard-widget-full">
              <EnhancedTransparencyPanel 
                reasoningSteps={reasoningSteps}
                isActive={!!activeAgent}
                onClear={clearActivity}
                onExport={() => exportReasoningLog(reasoningSteps, activeAgent, currentTask, toolsInUse, summary)}
              />
            </div>
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

