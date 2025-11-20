/**
 * AgenticDashboardPage Component
 * 
 * Page wrapper for the new Agentic Dashboard v2.
 * Includes full authentication, navigation, and all dashboard features.
 */

import React from 'react';
import { ToastProvider } from '../contexts/ToastContext';
import { AuthProvider, useAuth } from '../contexts/AgenticAuthContext';
import { SubscriptionProvider } from '../contexts/SubscriptionContext';
import MainAppContent from '../components/agentic_dashboard/MainAppContent';

const AgenticDashboardContent = () => {
  const { organization } = useAuth();
  
  return (
    <SubscriptionProvider organization={organization}>
      <MainAppContent />
    </SubscriptionProvider>
  );
};

export const AgenticDashboardPage = () => {
  return (
    <ToastProvider>
      <AuthProvider>
        <AgenticDashboardContent />
      </AuthProvider>
    </ToastProvider>
  );
};

export default AgenticDashboardPage;
