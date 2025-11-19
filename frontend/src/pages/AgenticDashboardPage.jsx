/**
 * AgenticDashboardPage Component
 * 
 * Page wrapper for the new agentic dashboard.
 * Provides all necessary context providers.
 */

import React from 'react';
import { ToastProvider } from '../contexts/dashboard/ToastContext';
import { AgenticDashboardView } from '../components/agentic_dashboard/views/AgenticDashboardView';

export const AgenticDashboardPage = () => {
  return (
    <ToastProvider>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
        <AgenticDashboardView />
      </div>
    </ToastProvider>
  );
};

export default AgenticDashboardPage;
