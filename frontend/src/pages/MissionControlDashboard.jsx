import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import Sidebar from '../components/layout/Sidebar';
import Header from '../components/layout/Header';
import KPICard from '../components/dashboard/KPICard';
import ConversationMonitor from '../components/dashboard/ConversationMonitor';
import TaskQueue from '../components/dashboard/TaskQueue';

/**
 * Mission Control Dashboard - מרכז פיקוד DentaFlow
 * 
 * Based on Agentic UX principles:
 * - Mission Control: User "operates" the system
 * - Transparency: Always show what agents are doing
 * - Human Control: Always allow human intervention
 * 
 * Layout:
 * - Sidebar (24px width, #001529 background)
 * - Header (#f0f0f0 background)
 * - 3 KPI cards at top
 * - Two columns: Conversations (65%) | Tasks (35%)
 */
export default function MissionControlDashboard() {
  const [selectedConversation, setSelectedConversation] = useState(null);
  
  // Fetch dashboard metrics (real-time, updates every 5 seconds)
  const { data: metrics, isLoading, error } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await fetch('/api/v1/dashboard-metrics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      if (!response.ok) throw new Error('Failed to fetch metrics');
      return response.json();
    },
    refetchInterval: 5000, // Update every 5 seconds
    staleTime: 4000
  });

  // Fetch conversations
  const { data: conversations } = useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      const response = await fetch('/api/v1/conversations?status=active', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      if (!response.ok) throw new Error('Failed to fetch conversations');
      return response.json();
    },
    refetchInterval: 3000 // Update every 3 seconds
  });

  // Fetch pending tasks
  const { data: tasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await fetch('/api/v1/agent-actions?status=pending', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      if (!response.ok) throw new Error('Failed to fetch tasks');
      return response.json();
    },
    refetchInterval: 5000
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">טוען מרכז פיקוד...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-red-500">שגיאה בטעינת הנתונים: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50" dir="rtl">
      {/* Sidebar - 24px width, dark blue background */}
      <Sidebar />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header - light gray background */}
        <Header title="מרכז פיקוד DentaFlow" />
        
        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* KPI Cards - 3 cards in a row */}
          <div className="grid grid-cols-3 gap-6 mb-6">
            <KPICard
              title="תורים שנקבעו היום"
              value={metrics?.appointments_today || 0}
              subtitle={`${metrics?.appointments_change || 0} מאתמול`}
              trend={metrics?.appointments_change > 0 ? 'up' : 'down'}
              icon="📅"
              color="blue"
            />
            
            <KPICard
              title="שיעור הצלחה (24 שעות)"
              value={`${metrics?.success_rate_24h || 0}%`}
              subtitle={`${metrics?.conversations_resolved || 0} שיחות נפתרו`}
              trend={metrics?.success_rate_change > 0 ? 'up' : 'down'}
              icon="✅"
              color="green"
            />
            
            <KPICard
              title="זמן טיפול ממוצע"
              value={formatDuration(metrics?.avg_handling_time || 0)}
              subtitle={`ממוצע שבועי: ${formatDuration(metrics?.avg_handling_time_weekly || 0)}`}
              trend={metrics?.handling_time_change < 0 ? 'up' : 'down'} // Lower is better
              icon="⏱️"
              color="purple"
            />
          </div>
          
          {/* Two Column Layout */}
          <div className="grid grid-cols-[65%_35%] gap-6 h-[calc(100vh-280px)]">
            {/* Right Column (65%) - Conversation Monitor */}
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <ConversationMonitor
                conversations={conversations || []}
                selectedConversation={selectedConversation}
                onSelectConversation={setSelectedConversation}
              />
            </div>
            
            {/* Left Column (35%) - Task Queue */}
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <TaskQueue tasks={tasks || []} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

/**
 * Format duration in seconds to MM:SS
 */
function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}
