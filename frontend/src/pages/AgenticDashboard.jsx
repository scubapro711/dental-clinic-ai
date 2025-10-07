import React, { useState, useRef } from 'react';
import AIChat from '../components/AIChat';
import AgentActivityPanel from '../components/transparency/AgentActivityPanel';
import FullTransparencyPanel from '../components/transparency/FullTransparencyPanel';
import TodaysPatientsWidget from '../components/widgets/TodaysPatientsWidget';
import RevenueWidget from '../components/widgets/RevenueWidget';
import DecisionQueueWidget from '../components/widgets/DecisionQueueWidget';
import FineTuningWidget from '../components/widgets/FineTuningWidget';
import ConversationHistorySidebar from '../components/ConversationHistorySidebar';
import useAgentActivity from '../hooks/useAgentActivity';
import { Button } from '@/components/ui/button';
import { PanelLeftClose, PanelLeftOpen, Sparkles, History } from 'lucide-react';

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
    <div className="h-screen flex flex-col bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                DentalAI Mission Control
              </h1>
              <p className="text-xs text-gray-500">מערכת ניהול אגנטית חכמה</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowHistorySidebar(true)}
              className="flex items-center gap-2"
            >
              <History className="w-4 h-4" />
              <span className="hidden md:inline">היסטוריה</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowLeftWidgets(!showLeftWidgets)}
            >
              {showLeftWidgets ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4" />}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowRightPanels(!showRightPanels)}
            >
              {showRightPanels ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Widgets Panel */}
        {showLeftWidgets && (
          <div className="w-80 border-r bg-white/50 backdrop-blur-sm overflow-y-auto p-4 space-y-4">
            <TodaysPatientsWidget onChatWithPatient={handleChatWithAgent} />
            <DecisionQueueWidget onChatWithAgent={handleChatWithAgent} />
            <FineTuningWidget onChatWithAgent={handleChatWithAgent} />
          </div>
        )}

        {/* Center - Chat */}
        <div className="flex-1 flex flex-col bg-white/70 backdrop-blur-sm">
          <AIChat
            ref={chatInputRef}
            conversationId={currentConversationId}
            initialMessages={conversationMessages}
            onStreamEvent={handleStreamEvent}
            onClearChat={clearActivity}
          />
        </div>

        {/* Right Panels */}
        {showRightPanels && (
          <div className="w-96 border-l bg-white/50 backdrop-blur-sm overflow-y-auto">
            <div className="p-4 space-y-4">
              {/* Revenue Widget */}
              <RevenueWidget onChatWithAgent={handleChatWithAgent} />
              
              {/* Agent Activity Panel */}
              <AgentActivityPanel
                activeAgent={activeAgent}
                currentTask={currentTask}
                toolsInUse={toolsInUse}
                summary={summary}
              />
              
              {/* Full Transparency Panel */}
              <FullTransparencyPanel reasoningSteps={reasoningSteps} />
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
