import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { logger } from '../utils/logger';
import AgentsGrid from '../components/agents/AgentsGrid';
import FloatingChatButton from '../components/chat/FloatingChatButton';
import TodaysPatientsWidget from '../components/widgets/TodaysPatientsWidget';
import DecisionQueueWidget from '../components/widgets/DecisionQueueWidget';
import RevenueWidget from '../components/widgets/RevenueWidget';
import ComplianceAlerts from '../components/compliance/ComplianceAlerts';
import ClinicalDashboard from '../components/clinical/ClinicalDashboard';
import AgentActivityPanel from '../components/transparency/AgentActivityPanel';
import EnhancedTransparencyPanel from '../components/transparency/EnhancedTransparencyPanel';
import EnhancedFineTuningWidget from '../components/fine-tuning/EnhancedFineTuningWidget';
import ConversationHistorySidebar from '../components/ConversationHistorySidebar';
import ProtectedWidget from '../components/rbac/ProtectedWidget';
import '../styles/dashboard.css';

/**
 * AgenticDashboard Component
 * 
 * Main dashboard with 2-column grid layout and floating chat button.
 * Follows healthcare UX best practices:
 * - Clear visual hierarchy
 * - Role-specific content
 * - Calm visual language
 * - Simplified navigation
 * - Reduced cognitive load
 * 
 * @component
 */
export default function AgenticDashboard() {
  const { user } = useAuth();
  const chatInputRef = useRef(null);

  // Conversation state
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationMessages, setConversationMessages] = useState([]);
  const [showHistorySidebar, setShowHistorySidebar] = useState(false);

  // Agent activity state
  const [activeAgent, setActiveAgent] = useState(null);
  const [currentTask, setCurrentTask] = useState('');
  const [toolsInUse, setToolsInUse] = useState([]);
  const [reasoningSteps, setReasoningSteps] = useState([]);
  const [summary, setSummary] = useState('');

  /**
   * Handle stream events from AI chat
   */
  const handleStreamEvent = useCallback((event) => {
    logger.debug('Stream event received:', event);

    if (event.type === 'agent_start') {
      setActiveAgent(event.agent);
      setCurrentTask(event.task || 'Processing...');
      setToolsInUse([]);
      setReasoningSteps([]);
      setSummary('');
    } else if (event.type === 'tool_use') {
      setToolsInUse(prev => [...prev, event.tool]);
    } else if (event.type === 'reasoning') {
      setReasoningSteps(prev => [...prev, event.step]);
    } else if (event.type === 'agent_end') {
      setSummary(event.summary || 'Task completed');
      setCurrentTask('');
    }
  }, []);

  /**
   * Clear agent activity
   */
  const clearActivity = useCallback(() => {
    setActiveAgent(null);
    setCurrentTask('');
    setToolsInUse([]);
    setReasoningSteps([]);
    setSummary('');
  }, []);

  /**
   * Export reasoning log
   */
  const exportReasoningLog = useCallback(() => {
    const log = {
      timestamp: new Date().toISOString(),
      agent: activeAgent,
      task: currentTask,
      tools: toolsInUse,
      reasoning: reasoningSteps,
      summary
    };
    
    const blob = new Blob([JSON.stringify(log, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reasoning-log-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    logger.info('Reasoning log exported');
  }, [activeAgent, currentTask, toolsInUse, reasoningSteps, summary]);

  /**
   * Handle chat with agent
   */
  const handleChatWithAgent = useCallback((message) => {
    if (chatInputRef.current) {
      chatInputRef.current.focus();
      // Optionally pre-fill the message
      logger.info('Chat with agent:', message);
    }
  }, []);

  /**
   * Handle conversation selection
   */
  const handleSelectConversation = useCallback((conversation) => {
    setCurrentConversationId(conversation.id);
    setConversationMessages(conversation.messages || []);
    setShowHistorySidebar(false);
    logger.info('Conversation selected:', conversation.id);
  }, []);

  /**
   * Handle new conversation
   */
  const handleNewConversation = useCallback(() => {
    setCurrentConversationId(null);
    setConversationMessages([]);
    clearActivity();
    setShowHistorySidebar(false);
    logger.info('New conversation started');
  }, [clearActivity]);

  return (
    <div className="h-full flex flex-col dentaflow-dashboard-background">
      {/* Header */}
      <div className="dentaflow-dashboard-header">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              DentaFlow
              <span className="text-indigo-600 ml-2">Mission Control</span>
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Welcome back, {user?.name || 'User'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowHistorySidebar(true)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            aria-label="View conversation history"
          >
            History
          </button>
        </div>
      </div>

      {/* AI Agents Grid */}
      <AgentsGrid 
        activeAgentId={activeAgent}
        onAgentClick={(agent) => handleChatWithAgent(`I need help with ${agent.role.toLowerCase()}`)}
        className="px-4 py-6"
      />

      {/* Dashboard Widgets Grid (2-column layout) */}
      <div className="dashboard-widgets-grid">
        {/* Priority 1: Today's Patients - Immediate action items */}
        <ProtectedWidget widgetId="todays-patients">
          <div className="dashboard-widget-card">
            <TodaysPatientsWidget onChatWithPatient={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 2: Decision Queue - Requires admin attention */}
        <ProtectedWidget widgetId="decision-queue">
          <div className="dashboard-widget-card">
            <DecisionQueueWidget onChatWithAgent={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 3: Revenue Widget - Financial overview (Admin) */}
        <ProtectedWidget widgetId="revenue">
          <div className="dashboard-widget-card">
            <RevenueWidget onChatWithAgent={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 4: HIPAA Compliance Alerts - Critical compliance issues */}
        <ProtectedWidget widgetId="compliance-alerts">
          <div className="dashboard-widget-card">
            <ComplianceAlerts onChatWithAgent={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 5: Clinical Dashboard - Full-width for detailed analysis */}
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

        {/* Priority 6: Enhanced Fine-Tuning - System optimization (Admin) */}
        <ProtectedWidget widgetId="fine-tuning">
          <div className="dashboard-widget-card">
            <EnhancedFineTuningWidget onChatWithAgent={handleChatWithAgent} />
          </div>
        </ProtectedWidget>

        {/* Priority 7: Agent Activity Panel - Real-time agent status */}
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

        {/* Priority 8: Enhanced Transparency Panel - AI reasoning (Full-width) */}
        <ProtectedWidget widgetId="transparency-panel">
          <div className="dashboard-widget-card dashboard-widget-full">
            <EnhancedTransparencyPanel 
              reasoningSteps={reasoningSteps}
              isActive={!!activeAgent}
              onClear={clearActivity}
              onExport={exportReasoningLog}
            />
          </div>
        </ProtectedWidget>
      </div>

      {/* Floating Chat Button */}
      <FloatingChatButton
        conversationId={currentConversationId}
        initialMessages={conversationMessages}
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

