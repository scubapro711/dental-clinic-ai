/**
 * AgenticDashboardPage Component
 * 
 * Page wrapper for the new agentic dashboard.
 * Uses existing authentication from ProtectedRoute.
 */

import React from 'react';
import { ToastProvider } from '../contexts/dashboard/ToastContext';
import { AgenticDashboardView } from '../components/agentic_dashboard/views/AgenticDashboardView';

export const AgenticDashboardPage = () => {
  return (
    <ToastProvider>
      <AgenticDashboardView />
    </ToastProvider>
  );
};

export default AgenticDashboardPage;
