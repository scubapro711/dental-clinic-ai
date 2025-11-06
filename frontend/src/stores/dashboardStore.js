/**
 * Dashboard Store - Zustand store for Mission Control dashboard state
 * 
 * Manages:
 * - Widget layout and positions
 * - Sidebar and panel states
 * - WebSocket connection status
 * - Metrics and agent status
 * - Alerts and notifications
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Default widget layout for Mission Control
const defaultWidgetLayout = [
  { i: 'metrics', x: 0, y: 0, w: 12, h: 2 },
  { i: 'agent-status', x: 0, y: 2, w: 4, h: 3 },
  { i: 'conversations', x: 4, y: 2, w: 8, h: 3 },
  { i: 'appointments', x: 0, y: 5, w: 6, h: 3 },
  { i: 'analytics', x: 6, y: 5, w: 6, h: 3 },
  { i: 'alerts', x: 0, y: 8, w: 4, h: 3 },
  { i: 'logs', x: 4, y: 8, w: 4, h: 3 },
  { i: 'patients', x: 8, y: 8, w: 4, h: 3 },
  { i: 'configuration', x: 0, y: 11, w: 12, h: 2 },
]

export const useDashboardStore = create(
  persist(
    (set, get) => ({
      // Layout state
      widgetLayout: defaultWidgetLayout,
      setWidgetLayout: (layout) => set({ widgetLayout: layout }),
      resetLayout: () => set({ widgetLayout: defaultWidgetLayout }),

      // Sidebar state
      sidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      // Right panel state
      rightPanelOpen: false,
      rightPanelContent: null,
      openRightPanel: (content) => set({ rightPanelOpen: true, rightPanelContent: content }),
      closeRightPanel: () => set({ rightPanelOpen: false, rightPanelContent: null }),

      // WebSocket state
      wsConnected: false,
      wsLastUpdate: null,
      setWsConnected: (connected) => set({ wsConnected: connected, wsLastUpdate: new Date() }),

      // Metrics state
      metrics: {
        totalConversations: 0,
        activeConversations: 0,
        appointmentsToday: 0,
        pendingTasks: 0,
        systemLoad: 0,
      },
      setMetrics: (metrics) => set({ metrics }),
      updateMetric: (key, value) => set((state) => ({
        metrics: { ...state.metrics, [key]: value }
      })),

      // Agent status
      agentStatus: {
        alex: { status: 'online', load: 0, lastActive: new Date() },
        marcus: { status: 'online', load: 0, lastActive: new Date() },
        sophia: { status: 'online', load: 0, lastActive: new Date() },
      },
      setAgentStatus: (agentStatus) => set({ agentStatus }),
      updateAgentStatus: (agent, status) => set((state) => ({
        agentStatus: { ...state.agentStatus, [agent]: { ...state.agentStatus[agent], ...status } }
      })),

      // Alerts state
      alerts: [],
      unreadAlertCount: 0,
      addAlert: (alert) => set((state) => ({
        alerts: [{ ...alert, id: Date.now(), read: false }, ...state.alerts],
        unreadAlertCount: state.unreadAlertCount + 1,
      })),
      markAlertRead: (id) => set((state) => ({
        alerts: state.alerts.map((a) => (a.id === id ? { ...a, read: true } : a)),
        unreadAlertCount: Math.max(0, state.unreadAlertCount - 1),
      })),
      clearAlerts: () => set({ alerts: [], unreadAlertCount: 0 }),

      // Search state
      searchQuery: '',
      setSearchQuery: (query) => set({ searchQuery: query }),

      // Active widget filter
      activeFilter: 'all',
      setActiveFilter: (filter) => set({ activeFilter: filter }),
    }),
    {
      name: 'dentaflow-dashboard-storage',
      partialize: (state) => ({
        widgetLayout: state.widgetLayout,
        sidebarCollapsed: state.sidebarCollapsed,
        activeFilter: state.activeFilter,
      }),
    }
  )
)
