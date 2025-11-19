/**
 * AgenticDashboardPage Component
 * 
 * Page wrapper for the new agentic dashboard.
 * Provides all necessary context providers.
 */

import React from 'react';
import { ToastProvider } from '../contexts/dashboard/ToastContext';
import { AuthProvider } from '../contexts/dashboard/AuthContext';
import { AgenticDashboardView } from '../components/agentic_dashboard/views/AgenticDashboardView';
import { useAuth } from '../contexts/dashboard/AuthContext';

const DashboardContent = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">טוען...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    // Redirect to login
    window.location.href = '/login';
    return null;
  }

  return <AgenticDashboardView />;
};

export const AgenticDashboardPage = () => {
  return (
    <ToastProvider>
      <AuthProvider>
        <DashboardContent />
      </AuthProvider>
    </ToastProvider>
  );
};

export default AgenticDashboardPage;
