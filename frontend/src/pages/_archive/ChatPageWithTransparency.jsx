import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { LogOut, Sparkles, LayoutDashboard } from 'lucide-react'
import AIChat from '@/components/AIChat'
import AgentActivityPanel from '@/components/transparency/AgentActivityPanel'
import FullTransparencyPanel, { useReasoningSteps } from '@/components/transparency/FullTransparencyPanel'
import useAgentActivity from '@/hooks/useAgentActivity'

/**
 * Chat Page with Transparency - Split-screen layout
 * 
 * Phase 1: Basic Transparency
 * - Left: Main chat interface
 * - Right: Agent activity panel
 * - Real-time activity updates
 * - Tool call visualization
 */
export default function ChatPageWithTransparency({ user, onLogout }) {
  const { activity, toolCalls, handleStreamEvent, clearActivity } = useAgentActivity();
  const { steps, handleStreamEvent: handleReasoningEvent, clearSteps } = useReasoningSteps();
  
  // Combined event handler
  const handleAllEvents = (event) => {
    handleStreamEvent(event);
    handleReasoningEvent(event);
  };
  
  const handleClearAll = () => {
    clearActivity();
    clearSteps();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-[1600px] mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-xl">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                DentalAI
              </h1>
              <p className="text-sm text-gray-600">AI-Powered Dental Assistant</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/dashboard">
              <Button variant="outline" size="sm">
                <LayoutDashboard className="w-4 h-4 mr-2" />
                Dashboard
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              <Avatar>
                <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
                  {user?.full_name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium">{user?.full_name || 'User'}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={onLogout}>
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Split-Screen Layout */}
      <div className="max-w-[1600px] mx-auto p-4 h-[calc(100vh-100px)]">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-full">
          {/* Main Chat - 2/3 width on large screens */}
          <div className="lg:col-span-2 h-full flex flex-col gap-4">
            <div className="flex-1">
              <AIChat 
                user={user} 
                onStreamEvent={handleAllEvents}
                onClearChat={handleClearAll}
              />
            </div>
          </div>

          {/* Right Panel - Activity + Full Transparency */}
          <div className="hidden lg:block h-full flex flex-col gap-4">
            {/* Activity Panel - Top */}
            <div className="h-1/3">
              <AgentActivityPanel 
                activity={activity} 
                toolCalls={toolCalls}
              />
            </div>
            
            {/* Full Transparency Panel - Bottom */}
            <div className="h-2/3">
              <FullTransparencyPanel steps={steps} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
