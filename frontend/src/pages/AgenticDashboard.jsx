import { useState, useRef } from 'react';
import './Dashboard.css';
import '../styles/dashboard.css';
import '../styles/transparency.css';
import '../styles/widgets.css';
import '../styles/coordination.css';
import AIChat from '../components/AIChat';
import AgentActivityPanel from '../components/transparency/AgentActivityPanel';
import FullTransparencyPanel from '../components/transparency/FullTransparencyPanel';
import EnhancedTransparencyPanel from '../components/transparency/EnhancedTransparencyPanel';
import TodaysPatientsWidget from '../components/widgets/TodaysPatientsWidget';
import RevenueWidget from '../components/widgets/RevenueWidget';
import DecisionQueueWidget from '../components/widgets/DecisionQueueWidget';
import FineTuningWidget from '../components/widgets/FineTuningWidget';
import ClinicalDashboard from '../components/clinical/ClinicalDashboard';
import EnhancedFineTuningWidget from '../components/fine-tuning/EnhancedFineTuningWidget';
import ConversationHistorySidebar from '../components/ConversationHistorySidebar';
import ProtectedWidget from '../components/rbac/ProtectedWidget';
import useAgentActivity from '../hooks/useAgentActivity';
import { Button } from '@/components/ui/button';
import { PanelLeftClose, PanelLeftOpen, Sparkles, History, Shield } from 'lucide-react';
import ComplianceAlerts from '../components/compliance/ComplianceAlerts';
import { exportReasoningLog } from '../components/transparency/EnhancedTransparencyPanel';
import DashboardStatsBar from '../components/dashboard/DashboardStatsBar';
import { getUserInfo, formatRoleName, getRoleBadgeColor } from '../utils/rbac';

/**
 * Agentic Dashboard - Main Page
 * 
 * Chat in the center with agent widgets around it
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

  const [showLeftWidgets, setShowLeftWidgets] = useState(true);
  const [showRightPanels, setShowRightPanels] = useState(true);
  const [showHistorySidebar, setShowHistorySidebar] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationMessages, setConversationMessages] = useState([]);
  const chatInputRef = useRef(null);

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
    <div className="h-screen flex flex-col dentaflow-dashboard-background">
      {/* Header */}
      <div className="dentaflow-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full dentaflow-header-logo flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-base md:text-xl dentaflow-header-title">
                DentalAI<span className="hidden sm:inline"> Mission Control</span>
              </h1>
              <p className="text-xs dentaflow-header-subtitle hidden md:block">מערכת ניהול אגנטית חכמה</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* User Role Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 dentaflow-user-badge">
              <Shield className="w-4 h-4 dentaflow-user-badge-icon" />
              <div className="text-xs">
                <div className="font-semibold dentaflow-user-badge-email">
                  {getUserInfo().email}
                </div>
                <div className={`text-xs px-2 py-0.5 rounded ${getRoleBadgeColor(getUserInfo().role)} text-white inline-block`}>
                  {formatRoleName(getUserInfo().role)}
                </div>
              </div>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowHistorySidebar(true)}
              className="flex items-center gap-2"
              aria-label="Open conversation history"
            >
              <History className="w-4 h-4" aria-hidden="true" />
              <span className="hidden md:inline">היסטוריה</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowLeftWidgets(!showLeftWidgets)}
              className="hidden lg:flex"
              aria-label={showLeftWidgets ? "Hide left widgets panel" : "Show left widgets panel"}
              aria-expanded={showLeftWidgets}
              aria-controls="left-widgets-panel"
            >
              {showLeftWidgets ? <PanelLeftClose className="w-4 h-4" aria-hidden="true" /> : <PanelLeftOpen className="w-4 h-4" aria-hidden="true" />}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowRightPanels(!showRightPanels)}
              className="hidden lg:flex"
              aria-label={showRightPanels ? "Hide right panels" : "Show right panels"}
              aria-expanded={showRightPanels}
              aria-controls="right-panels"
            >
              {showRightPanels ? <PanelLeftOpen className="w-4 h-4" aria-hidden="true" /> : <PanelLeftClose className="w-4 h-4" aria-hidden="true" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Dashboard Stats Bar */}
      <DashboardStatsBar />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Widgets Panel - Hidden on mobile, show on desktop */}
        {showLeftWidgets && (
          <div 
            id="left-widgets-panel"
            className="dentaflow-sidebar dentaflow-sidebar-left"
            role="complementary"
            aria-label="Dashboard widgets"
          >
            {/* Today's Patients - Staff and Admin only */}
            <ProtectedWidget widgetId="todays-patients">
              <TodaysPatientsWidget onChatWithPatient={handleChatWithAgent} />
            </ProtectedWidget>
            
            {/* Decision Queue - Admin only for interaction */}
            <ProtectedWidget widgetId="decision-queue">
              <DecisionQueueWidget onChatWithAgent={handleChatWithAgent} />
            </ProtectedWidget>
            
            {/* Enhanced Fine-Tuning - Admin only */}
            <ProtectedWidget widgetId="fine-tuning">
              <EnhancedFineTuningWidget onChatWithAgent={handleChatWithAgent} />
            </ProtectedWidget>
            
            {/* HIPAA Compliance Alerts - Admin only */}
            <ProtectedWidget widgetId="compliance-alerts">
              <ComplianceAlerts onChatWithAgent={handleChatWithAgent} />
            </ProtectedWidget>
            
            {/* Clinical System - Staff and Admin */}
            <ProtectedWidget widgetId="clinical-system">
              <div className="widget-card">
                <div className="widget-header">
                  <h3>🩺 Clinical System</h3>
                  <p className="text-sm dentaflow-user-badge-icon">AI-powered clinical analysis</p>
                </div>
                <ClinicalDashboard patient={{ id: 1, name: 'David Cohen', age: 45, lastVisit: '2025-09-15' }} />
              </div>
            </ProtectedWidget>
          </div>
        )}

        {/* Center - Chat */}
        <div className="dentaflow-main-content">
          <AIChat
            ref={chatInputRef}
            conversationId={currentConversationId}
            initialMessages={conversationMessages}
            onStreamEvent={handleStreamEvent}
            onClearChat={clearActivity}
          />
        </div>

        {/* Right Panels - Hidden on mobile, show on desktop */}
        {showRightPanels && (
          <div 
            id="right-panels"
            className="dentaflow-sidebar dentaflow-sidebar-right"
            role="complementary"
            aria-label="Agent activity and transparency panels"
          >
            <div className="p-4 space-y-4">
              {/* Revenue Widget - Admin only */}
              <ProtectedWidget widgetId="revenue">
                <RevenueWidget onChatWithAgent={handleChatWithAgent} />
              </ProtectedWidget>
              
              {/* Agent Activity Panel - Staff and Admin */}
              <ProtectedWidget widgetId="agent-activity">
                <AgentActivityPanel
                  activeAgent={activeAgent}
                  currentTask={currentTask}
                  toolsInUse={toolsInUse}
                  summary={summary}
                />
              </ProtectedWidget>
              
              {/* Enhanced Transparency Panel - Staff and Admin */}
              <ProtectedWidget widgetId="transparency-panel">
                <EnhancedTransparencyPanel 
                  reasoningSteps={reasoningSteps}
                  isActive={!!activeAgent}
                  onClear={clearActivity}
                  onExport={exportReasoningLog}
                />
              </ProtectedWidget>
            </div>
          </div>
        )}
      </div>
      
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
