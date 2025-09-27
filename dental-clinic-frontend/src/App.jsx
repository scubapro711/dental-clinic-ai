import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Bot, 
  Monitor, 
  Home, 
  ArrowRight,
  Shield,
  Eye,
  Command,
  CheckCircle
} from 'lucide-react';
import AgenticLandingPage from './components/landing/AgenticLandingPage';
import MissionControlDashboard from './components/dashboard/MissionControlDashboard';
import './App.css';

/**
 * Main App Component
 * 
 * Showcases the complete Agentic UX system:
 * 1. Revolutionary landing page that presents the AI agent concept
 * 2. Full Mission Control Dashboard for managing the autonomous agent
 * 
 * This demonstrates the paradigm shift from traditional software UI
 * to Agentic Experience (AX) where users delegate goals to an AI agent
 * and maintain oversight through a Mission Control interface.
 */
function App() {
  const [currentView, setCurrentView] = useState('landing');

  return (
    <div className="min-h-screen bg-[#f5f5f5]">
      {/* Navigation Bar */}
      <nav className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#001529] rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-[#001529]">DentalAI</h1>
              <p className="text-xs text-gray-600">Agentic UX Demo</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button
              variant={currentView === 'landing' ? 'default' : 'outline'}
              onClick={() => setCurrentView('landing')}
              className="flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              דף הבית
            </Button>
            
            <Button
              variant={currentView === 'dashboard' ? 'default' : 'outline'}
              onClick={() => setCurrentView('dashboard')}
              className="flex items-center gap-2"
            >
              <Monitor className="w-4 h-4" />
              מרכז השליטה
            </Button>

            <Badge className="bg-green-100 text-green-800 flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              סוכן פעיל
            </Badge>
          </div>
        </div>
      </nav>

      {/* View Transition */}
      {currentView === 'landing' && (
        <div className="relative">
          <AgenticLandingPage />
          
          {/* Floating CTA to Dashboard */}
          <div className="fixed bottom-8 left-8 z-50">
            <Button
              size="lg"
              onClick={() => setCurrentView('dashboard')}
              className="bg-[#001529] hover:bg-[#220] text-white shadow-2xl flex items-center gap-3 px-6 py-4 rounded-full"
            >
              <Shield className="w-5 h-5" />
              <span className="font-medium">כנסו למרכז השליטה</span>
              <ArrowRight className="w-5 h-5" />
            </Button>
          </div>
        </div>
      )}

      {currentView === 'dashboard' && (
        <div className="relative">
          <MissionControlDashboard />
          
          {/* Floating Back to Landing */}
          <div className="fixed bottom-8 left-8 z-50">
            <Button
              size="lg"
              variant="outline"
              onClick={() => setCurrentView('landing')}
              className="bg-white hover:bg-gray-50 shadow-2xl flex items-center gap-3 px-6 py-4 rounded-full border-2"
            >
              <Home className="w-5 h-5" />
              <span className="font-medium">חזרה לדף הבית</span>
            </Button>
          </div>
        </div>
      )}

      {/* Demo Information Overlay */}
      <div className="fixed top-20 left-6 z-40 max-w-sm">
        <div className="bg-white/95 backdrop-blur-sm border border-gray-200 rounded-lg p-4 shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Eye className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-gray-900">הדגמת Agentic UX</span>
          </div>
          <p className="text-xs text-gray-600 mb-3">
            זוהי הדגמה של המעבר מממשק משתמש מסורתי לחוויה אגנטית (Agentic Experience)
          </p>
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full" />
              <span className="text-gray-700">דף הבית: הצגת הסוכן האוטונומי</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span className="text-gray-700">מרכז השליטה: Mission Control</span>
            </div>
          </div>
        </div>
      </div>

      {/* Agentic UX Principles Indicator */}
      <div className="fixed bottom-8 right-8 z-40">
        <div className="bg-[#001529] text-white rounded-lg p-4 shadow-2xl max-w-xs">
          <div className="flex items-center gap-2 mb-2">
            <Command className="w-4 h-4" />
            <span className="text-sm font-bold">עקרונות Agentic UX</span>
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-3 h-3 text-green-400" />
              <span>הגדרת מטרות במקום משימות</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-3 h-3 text-green-400" />
              <span>ביצוע אוטונומי של הסוכן</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-3 h-3 text-green-400" />
              <span>שקיפות והסברים</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-3 h-3 text-green-400" />
              <span>שליטה אנושית מתמשכת</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App
