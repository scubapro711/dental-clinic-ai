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
import { Sparkles, History } from 'lucide-react';
import ComplianceAlerts from '../components/compliance/ComplianceAlerts';
import { exportReasoningLog } from '../components/transparency/EnhancedTransparencyPanel';
import { getUserInfo } from '../utils/rbac';
import { AgentsGrid } from '../components/agents';

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

      {/* AI Agents Grid */}
      <div className="px-4 py-6">
        <AgentsGrid 
          activeAgentId={activeAgent}
          onAgentClick={(agent) => handleChatWithAgent(`I need help with ${agent.role.toLowerCase()}`)}
        />
      </div>

      {/* Dashboard Widgets Grid (2-column layout) */}
      <div className="dashboard-widgets-grid">
        {/* Priority 1: Today's Patients */}
        <ProtectedWidget widgetId="todays-patients">
          <div className="dashboard-widget-card">
            <TodaysPatientsWidget onChatWithPatient={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 2: Decision Queue */}
        <ProtectedWidget widgetId="decision-queue">
          <div className="dashboard-widget-card">
            <DecisionQueueWidget onChatWithAgent={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 3: Revenue Widget */}
        <ProtectedWidget widgetId="revenue">
          <div className="dashboard-widget-card">
            <RevenueWidget onChatWithAgent={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 4: Compliance Alerts */}
        <ProtectedWidget widgetId="compliance-alerts">
          <div className="dashboard-widget-card">
            <ComplianceAlerts onChatWithAgent={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 5: Clinical Dashboard (Full-width) */}
        <ProtectedWidget widgetId="clinical-system">
          <div className="dashboard-widget-card dashboard-widget-full">
            <div className="dashboard-widget-header">
              <h3 className="dashboard-widget-title">
                🩺 Clinical System
              </h3>
              <span className="dashboard-widget-badge dashboard-widget-badge-info">
                AI-Powered
              </span>
            </div>
            <ClinicalDashboard 
              patient={{ 
                id: 1, 
                name: 'David Cohen', 
                age: 45, 
                lastVisit: '2025-09-15' 
              }} 
            />
          </div>
        </ProtectedWidget>

        {/* Priority 6: Enhanced Fine-Tuning */}
        <ProtectedWidget widgetId="fine-tuning">
          <div className="dashboard-widget-card">
            <EnhancedFineTuningWidget onChatWithAgent={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 7: Agent Activity Panel */}
        <ProtectedWidget widgetId="agent-activity">
          <div className="dashboard-widget-card">
            <AgentActivityPanel
              activeAgent={activeAgent}
              currentTask={currentTask}
              toolsInUse={toolsInUse}
              summary={summary}
            />
          </div>
        </ProtectedWidget>

        {/* Priority 8: Enhanced Transparency Panel (Full-width) */}
        <ProtectedWidget widgetId="transparency-panel">
          <div className="dashboard-widget-card dashboard-widget-full">
            <EnhancedTransparencyPanel 
              reasoningSteps={reasoningSteps}
              isActive={!!activeAgent}
              onClear={clearActivity}
              onExport={() => exportReasoningLog(reasoningSteps, activeAgent, currentTask, toolsInUse, summary)}
            />
          </div>
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
  );
}

