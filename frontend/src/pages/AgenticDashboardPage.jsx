/**
 * AgenticDashboardPage Component
 * 
 * Page wrapper for the new Agentic Dashboard v2.
 * Includes full authentication, navigation, and all dashboard features.
 */

import React from 'react';
import { ToastProvider } from '../contexts/ToastContext';
import { AuthProvider } from '../contexts/AgenticAuthContext';
import MainAppContent from '../components/agentic_dashboard/MainAppContent';

export const AgenticDashboardPage = () => {
  return (
    <ToastProvider>
      <AuthProvider>
        <MainAppContent />
      </AuthProvider>
    </ToastProvider>
  );
};

export default AgenticDashboardPage;
