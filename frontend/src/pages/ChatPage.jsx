import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { LogOut, Sparkles, LayoutDashboard } from 'lucide-react'
import AIChat from '@/components/AIChat'

/**
 * Chat Page - Main chat interface with Vercel AI SDK + LangGraph
 * 
 * This page integrates the new AIChat component which uses:
 * - Vercel AI SDK for frontend
 * - LangGraph multi-agent system for backend
 * - Real-time streaming responses
 * - All 3 agents: Alex, CFO, Practice Admin
 */
export default function ChatPage({ user, onLogout }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
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

      {/* Chat Container */}
      <div className="max-w-5xl mx-auto p-4 h-[calc(100vh-100px)]">
        <AIChat user={user} />
      </div>
    </div>
  )
}
