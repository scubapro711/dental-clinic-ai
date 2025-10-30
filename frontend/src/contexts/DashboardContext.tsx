/**
 * DashboardContext - Centralized state management for dashboard customization
 * 
 * Features:
 * - Widget collapse/expand state
 * - Multi-tenant isolation (scoped per org + user)
 * - RBAC integration
 * - localStorage persistence
 * - Organization switch handling
 * 
 * Best Practices:
 * - Always validate organizationId and userId before saving
 * - Use defensive checks for all array/object operations
 * - Handle localStorage quota exceeded gracefully
 * - Clear state on organization switch
 */

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { useAuthStore } from '../store/useAuthStore'
import { canViewWidget, canInteractWithWidget } from '../utils/rbac'

// ========== Types ==========

interface WidgetState {
  collapsed: boolean
  visible: boolean
  position: number
}

interface DashboardState {
  widgets: {
    [widgetId: string]: WidgetState
  }
  editMode: boolean
  organizationId: string
  userId: string
  lastModified: string
}

interface DashboardContextValue {
  // State
  state: DashboardState
  isEditMode: boolean
  
  // Actions
  toggleCollapse: (widgetId: string) => void
  toggleEditMode: () => void
  resetToDefaults: () => void
  
  // Helpers
  isCollapsed: (widgetId: string) => boolean
  canViewWidget: (widgetId: string) => boolean
  canInteractWithWidget: (widgetId: string) => boolean
}

// ========== Default State ==========

const DEFAULT_WIDGETS: { [key: string]: WidgetState } = {
  'todays-patients': { collapsed: false, visible: true, position: 0 },
  'decision-queue': { collapsed: false, visible: true, position: 1 },
  'revenue': { collapsed: false, visible: true, position: 2 },
  'compliance-alerts': { collapsed: false, visible: true, position: 3 },
  'clinical-system': { collapsed: false, visible: true, position: 4 },
  'fine-tuning': { collapsed: false, visible: true, position: 5 },
  'agent-activity': { collapsed: false, visible: true, position: 6 },
  'transparency-panel': { collapsed: false, visible: true, position: 7 }
}

function getDefaultState(organizationId: string, userId: string): DashboardState {
  return {
    widgets: { ...DEFAULT_WIDGETS },
    editMode: false,
    organizationId,
    userId,
    lastModified: new Date().toISOString()
  }
}

// ========== localStorage Utilities ==========

function getStorageKey(organizationId: string, userId: string): string {
  // CRITICAL: Use current_organization_id (not organization_id)
  return `dashboard_state_${organizationId}_${userId}`
}

function loadDashboardState(organizationId: string, userId: string): DashboardState {
  if (!organizationId || !userId) {
    console.warn('Missing organizationId or userId, using default state')
    return getDefaultState(organizationId, userId)
  }
  
  try {
    const key = getStorageKey(organizationId, userId)
    const stored = localStorage.getItem(key)
    
    if (!stored) {
      return getDefaultState(organizationId, userId)
    }
    
    const parsed = JSON.parse(stored) as DashboardState
    
    // Validate organization/user match (security check)
    if (parsed.organizationId !== organizationId || parsed.userId !== userId) {
      console.error('Organization/User mismatch in stored state!')
      return getDefaultState(organizationId, userId)
    }
    
    // Merge with defaults (in case new widgets added)
    return {
      ...parsed,
      widgets: {
        ...DEFAULT_WIDGETS,
        ...parsed.widgets
      }
    }
  } catch (error) {
    console.error('Failed to load dashboard state:', error)
    return getDefaultState(organizationId, userId)
  }
}

function saveDashboardState(state: DashboardState): void {
  if (!state.organizationId || !state.userId) {
    console.error('Cannot save state without organizationId and userId')
    return
  }
  
  try {
    const key = getStorageKey(state.organizationId, state.userId)
    const updated = {
      ...state,
      lastModified: new Date().toISOString()
    }
    localStorage.setItem(key, JSON.stringify(updated))
  } catch (error) {
    if (error instanceof Error && error.name === 'QuotaExceededError') {
      console.error('localStorage quota exceeded!')
      // TODO: Clear old dashboard states
    } else {
      console.error('Failed to save dashboard state:', error)
    }
  }
}

// ========== Context ==========

const DashboardContext = createContext<DashboardContextValue | undefined>(undefined)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const { user, organization } = useAuthStore()
  
  // Get organizationId from localStorage (matches useAuthStore)
  const organizationId = localStorage.getItem('current_organization_id') || organization?.id || ''
  const userId = user?.id || ''
  
  const [state, setState] = useState<DashboardState>(() =>
    loadDashboardState(organizationId, userId)
  )
  
  // Handle organization switch
  useEffect(() => {
    if (organizationId && userId) {
      const currentOrgId = state.organizationId
      
      if (currentOrgId !== organizationId) {
        // Organization switched! Load new state
        console.log('Organization switched, loading new dashboard state')
        const newState = loadDashboardState(organizationId, userId)
        setState(newState)
      }
    }
  }, [organizationId, userId])
  
  // Save state on change
  useEffect(() => {
    if (state.organizationId && state.userId) {
      saveDashboardState(state)
    }
  }, [state])
  
  // ========== Actions ==========
  
  const toggleCollapse = useCallback((widgetId: string) => {
    setState(prev => ({
      ...prev,
      widgets: {
        ...prev.widgets,
        [widgetId]: {
          ...prev.widgets[widgetId],
          collapsed: !prev.widgets[widgetId]?.collapsed
        }
      }
    }))
  }, [])
  
  const toggleEditMode = useCallback(() => {
    setState(prev => ({
      ...prev,
      editMode: !prev.editMode
    }))
  }, [])
  
  const resetToDefaults = useCallback(() => {
    const defaultState = getDefaultState(organizationId, userId)
    setState(defaultState)
  }, [organizationId, userId])
  
  // ========== Helpers ==========
  
  const isCollapsed = useCallback((widgetId: string): boolean => {
    return state.widgets[widgetId]?.collapsed || false
  }, [state.widgets])
  
  const canView = useCallback((widgetId: string): boolean => {
    const userRole = user?.role
    if (!userRole) return false
    return canViewWidget(userRole, widgetId)
  }, [user?.role])
  
  const canInteract = useCallback((widgetId: string): boolean => {
    const userRole = user?.role
    if (!userRole) return false
    return canInteractWithWidget(userRole, widgetId)
  }, [user?.role])
  
  const value: DashboardContextValue = {
    state,
    isEditMode: state.editMode,
    toggleCollapse,
    toggleEditMode,
    resetToDefaults,
    isCollapsed,
    canViewWidget: canView,
    canInteractWithWidget: canInteract
  }
  
  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard(): DashboardContextValue {
  const context = useContext(DashboardContext)
  if (!context) {
    throw new Error('useDashboard must be used within DashboardProvider')
  }
  return context
}

