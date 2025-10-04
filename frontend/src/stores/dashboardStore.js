/**
 * Dashboard Store - Zustand state management for Mission Control Dashboard
 * 
 * Manages:
 * - Active conversations
 * - Real-time metrics
 * - Alerts and notifications
 * - Agent status
 * - Widget layout configuration
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useDashboardStore = create(
  persist(
    (set, get) => ({
      // ============================================
      // CONVERSATIONS
      // ============================================
      conversations: [],
      activeConversationId: null,
      conversationFilters: {
        status: 'all', // all, active, escalated, resolved
        channel: 'all', // all, web, telegram, whatsapp
        searchQuery: '',
      },

      setConversations: (conversations) => set({ conversations }),
      
      addConversation: (conversation) =>
        set((state) => ({
          conversations: [conversation, ...state.conversations],
        })),
      
      updateConversation: (conversationId, updates) =>
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId ? { ...conv, ...updates } : conv
          ),
        })),
      
      setActiveConversation: (conversationId) =>
        set({ activeConversationId: conversationId }),
      
      setConversationFilters: (filters) =>
        set((state) => ({
          conversationFilters: { ...state.conversationFilters, ...filters },
        })),

      // ============================================
      // REAL-TIME METRICS
      // ============================================
      metrics: {
        activeConversations: 0,
        todayAppointments: 0,
        avgResponseTime: 0,
        satisfactionScore: 0,
      },

      setMetrics: (metrics) =>
        set((state) => ({
          metrics: { ...state.metrics, ...metrics },
        })),

      // ============================================
      // ALERTS & NOTIFICATIONS
      // ============================================
      alerts: [],
      unreadAlertCount: 0,

      addAlert: (alert) =>
        set((state) => ({
          alerts: [{ ...alert, id: Date.now(), read: false }, ...state.alerts],
          unreadAlertCount: state.unreadAlertCount + 1,
        })),
      
      markAlertAsRead: (alertId) =>
        set((state) => ({
          alerts: state.alerts.map((alert) =>
            alert.id === alertId ? { ...alert, read: true } : alert
          ),
          unreadAlertCount: Math.max(0, state.unreadAlertCount - 1),
        })),
      
      clearAllAlerts: () =>
        set({ alerts: [], unreadAlertCount: 0 }),

      // ============================================
      // AGENT STATUS
      // ============================================
      agentStatus: {
        status: 'online', // online, offline, error, paused
        uptime: 0,
        totalConversations: 0,
        avgResponseTime: 0,
        successRate: 0,
        lastError: null,
      },

      setAgentStatus: (status) =>
        set((state) => ({
          agentStatus: { ...state.agentStatus, ...status },
        })),

      // ============================================
      // WIDGET LAYOUT - All 9 Widgets
      // ============================================
      widgetLayout: [
        // Row 1: Metrics + Agent Status
        { i: 'metrics', x: 0, y: 0, w: 6, h: 2 },
        { i: 'agent-status', x: 6, y: 0, w: 6, h: 2 },
        
        // Row 2: Conversations (full width)
        { i: 'conversations', x: 0, y: 2, w: 12, h: 4 },
        
        // Row 3: Appointments + Analytics
        { i: 'appointments', x: 0, y: 6, w: 6, h: 3 },
        { i: 'analytics', x: 6, y: 6, w: 6, h: 3 },
        
        // Row 4: Alerts (full width)
        { i: 'alerts', x: 0, y: 9, w: 12, h: 3 },
        
        // Row 5: Logs + Patients + Configuration
        { i: 'logs', x: 0, y: 12, w: 4, h: 4 },
        { i: 'patients', x: 4, y: 12, w: 4, h: 4 },
        { i: 'configuration', x: 8, y: 12, w: 4, h: 4 },
      ],

      setWidgetLayout: (layout) => set({ widgetLayout: layout }),
      
      resetWidgetLayout: () =>
        set({
          widgetLayout: [
            // Row 1: Metrics + Agent Status
            { i: 'metrics', x: 0, y: 0, w: 6, h: 2 },
            { i: 'agent-status', x: 6, y: 0, w: 6, h: 2 },
            
            // Row 2: Conversations (full width)
            { i: 'conversations', x: 0, y: 2, w: 12, h: 4 },
            
            // Row 3: Appointments + Analytics
            { i: 'appointments', x: 0, y: 6, w: 6, h: 3 },
            { i: 'analytics', x: 6, y: 6, w: 6, h: 3 },
            
            // Row 4: Alerts (full width)
            { i: 'alerts', x: 0, y: 9, w: 12, h: 3 },
            
            // Row 5: Logs + Patients + Configuration
            { i: 'logs', x: 0, y: 12, w: 4, h: 4 },
            { i: 'patients', x: 4, y: 12, w: 4, h: 4 },
            { i: 'configuration', x: 8, y: 12, w: 4, h: 4 },
          ],
        }),

      // ============================================
      // UI STATE
      // ============================================
      sidebarCollapsed: false,
      rightPanelOpen: false,
      rightPanelContent: null,

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      
      openRightPanel: (content) =>
        set({ rightPanelOpen: true, rightPanelContent: content }),
      
      closeRightPanel: () =>
        set({ rightPanelOpen: false, rightPanelContent: null }),

      // ============================================
      // WEBSOCKET CONNECTION
      // ============================================
      wsConnected: false,
      wsLastUpdate: null,

      setWsConnected: (connected) =>
        set({ wsConnected: connected, wsLastUpdate: Date.now() }),
    }),
    {
      name: 'dental-dashboard-storage',
      partialize: (state) => ({
        // Only persist these fields
        widgetLayout: state.widgetLayout,
        sidebarCollapsed: state.sidebarCollapsed,
        conversationFilters: state.conversationFilters,
      }),
    }
  )
)
