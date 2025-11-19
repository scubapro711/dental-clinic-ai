/**
 * AgenticDashboardPage Component
 * 
 * Page wrapper for the new agentic dashboard.
 * Uses existing authentication from ProtectedRoute.
 */

import React from 'react';
import { ToastProvider } from '../contexts/dashboard/ToastContext';
import { DashboardView } from '../components/agentic_dashboard/views/DashboardView';

export const AgenticDashboardPage = () => {
  return (
    <ToastProvider>
      <DashboardView />
    </ToastProvider>
  );
};

export default AgenticDashboardPage;
