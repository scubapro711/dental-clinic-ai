/**
 * AgenticDashboardView Component
 * 
 * Main view for the new agentic dashboard.
 * Integrates all widgets and provides the complete dashboard experience.
 */

import React, { useState } from 'react';
import { LogOut, Moon, Sun } from 'lucide-react';
import { useAuth } from '../../../contexts/AgenticAuthContext';
import { useAuth } from '../../../hooks/useAuth';
import { SystemPulseHeader } from '../SystemPulseHeader';
import { WidgetWrapper } from '../WidgetWrapper';
import { DecisionQueueWidget } from '../widgets/DecisionQueueWidget';
import { RevenueWidget } from '../widgets/RevenueWidget';
import { TodaysPatientsWidget } from '../widgets/TodaysPatientsWidget';

export const AgenticDashboardView = () => {
  const { user, logout } = useAuth();
  const [darkMode, setDarkMode] = useState(false);

  return (
    <div 
      className={`min-h-screen ${darkMode ? 'dark' : 'bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50'}`}
      style={darkMode ? { backgroundColor: '#0f172a' } : {}}
    >
      {/* Top Navigation */}
      <nav className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">D</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                  DentaFlow AI
                </h1>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  Agentic Dashboard v2
                </p>
              </div>
            </div>

            {/* Right Side Controls */}
            <div className="flex items-center gap-4">
              {/* Dark Mode Toggle */}
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition"
                aria-label="Toggle dark mode"
              >
                {darkMode ? <Sun size={20} /> : <Moon size={20} />}
              </button>

              {/* User Info */}
              <div className="flex items-center gap-3 px-3 py-2 bg-slate-100 dark:bg-slate-700 rounded-lg">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {user?.email?.charAt(0).toUpperCase() || 'U'}
                </div>
                <span className="text-sm font-medium text-slate-900 dark:text-white">
                  {user?.email || 'User'}
                </span>
              </div>

              {/* Logout */}
              <button
                onClick={logout}
                className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
                aria-label="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* System Pulse Header */}
        <SystemPulseHeader />

        {/* Widget Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <WidgetWrapper title="תורים היום">
            <TodaysPatientsWidget />
          </WidgetWrapper>

          <WidgetWrapper title="תור החלטות">
            <DecisionQueueWidget />
          </WidgetWrapper>

          <WidgetWrapper title="הכנסות">
            <RevenueWidget />
          </WidgetWrapper>
        </div>
      </div>
    </div>
  );
};
