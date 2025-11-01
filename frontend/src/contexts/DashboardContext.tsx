/**
 * DashboardContext - Centralized state management for dashboard customization
 * 
 * Features:
 * - Widget collapse/expand state
 * - Grid layout management (react-grid-layout)
 * - Active widgets management
 * - Sidebar state
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

import { createContext, useContext, useState, useEffect, useCallback, ReactNode, useMemo } from 'react'
import { Layout } from 'react-grid-layout'
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
  // NEW: Grid layout state
  layouts: {
    lg: Layout[]
    md: Layout[]
    sm: Layout[]
    xs: Layout[]
    xxs: Layout[]
  }
  activeWidgets: string[]
  isSidebarOpen: boolean
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
  
  // NEW: Grid Layout
  layout: Layout[]
  setLayout: (layout: Layout[]) => void
  layouts: Record<string, Layout[]>
  setLayouts: (layouts: Record<string, Layout[]>) => void
  
  // NEW: Widget Management
  activeWidgets: string[]
  addWidget: (widgetId: string, layoutItem?: Partial<Layout>) => void
  removeWidget: (widgetId: string) => void
  
  // NEW: Sidebar
  isSidebarOpen: boolean
  toggleSidebar: () => void
  
  // NEW: Persistence
  saveLayout: () => void
  isSaving: boolean
}

// ========== Default State ==========

const DEFAULT_WIDGETS: { [key: string]: WidgetState } = {
  'todays-patients': { collapsed: false, visible: true, position: 0 },
  'decision-queue': { collapsed: false, visible: true, position: 1 },
  'revenue': { collapsed: false, visible: true, position: 2 },
  'compliance': { collapsed: false, visible: true, position: 3 },
  'clinical': { collapsed: false, visible: true, position: 4 },
  'fine-tuning': { collapsed: false, visible: true, position: 5 },
  'agent-activity': { collapsed: false, visible: true, position: 6 },
  'transparency': { collapsed: false, visible: true, position: 7 }
}

const DEFAULT_LAYOUT_LG: Layout[] = [
  { i: 'todays-patients', x: 0, y: 0, w: 4, h: 2 },
  { i: 'decision-queue', x: 4, y: 0, w: 4, h: 2 },
  { i: 'revenue', x: 8, y: 0, w: 4, h: 2 },
  { i: 'compliance', x: 0, y: 2, w: 4, h: 2 }
]

const DEFAULT_LAYOUT_MD: Layout[] = [
  { i: 'todays-patients', x: 0, y: 0, w: 5, h: 2 },
  { i: 'decision-queue', x: 5, y: 0, w: 5, h: 2 },
  { i: 'revenue', x: 0, y: 2, w: 5, h: 2 },
  { i: 'compliance', x: 5, y: 2, w: 5, h: 2 }
]

const DEFAULT_LAYOUT_SM: Layout[] = [
  { i: 'todays-patients', x: 0, y: 0, w: 6, h: 2 },
  { i: 'decision-queue', x: 0, y: 2, w: 6, h: 2 },
  { i: 'revenue', x: 0, y: 4, w: 6, h: 2 },
  { i: 'compliance', x: 0, y: 6, w: 6, h: 2 }
]

const DEFAULT_LAYOUT_XS: Layout[] = [
  { i: 'todays-patients', x: 0, y: 0, w: 4, h: 2 },
  { i: 'decision-queue', x: 0, y: 2, w: 4, h: 2 },
  { i: 'revenue', x: 0, y: 4, w: 4, h: 2 },
  { i: 'compliance', x: 0, y: 6, w: 4, h: 2 }
]

const DEFAULT_LAYOUT_XXS: Layout[] = [
  { i: 'todays-patients', x: 0, y: 0, w: 2, h: 2 },
  { i: 'decision-queue', x: 0, y: 2, w: 2, h: 2 },
  { i: 'revenue', x: 0, y: 4, w: 2, h: 2 },
  { i: 'compliance', x: 0, y: 6, w: 2, h: 2 }
]

function getDefaultState(organizationId: string, userId: string): DashboardState {
  return {
    widgets: { ...DEFAULT_WIDGETS },
    editMode: false,
    organizationId,
    userId,
    lastModified: new Date().toISOString(),
    layouts: {
      lg: [...DEFAULT_LAYOUT_LG],
      md: [...DEFAULT_LAYOUT_MD],
      sm: [...DEFAULT_LAYOUT_SM],
      xs: [...DEFAULT_LAYOUT_XS],
      xxs: [...DEFAULT_LAYOUT_XXS]
    },
    activeWidgets: ['todays-patients', 'decision-queue', 'revenue', 'compliance'],
    isSidebarOpen: true
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
    const defaultState = getDefaultState(organizationId, userId)
    return {
      ...parsed,
      widgets: {
        ...defaultState.widgets,
        ...parsed.widgets
      },
      layouts: parsed.layouts || defaultState.layouts,
      activeWidgets: parsed.activeWidgets || defaultState.activeWidgets,
      isSidebarOpen: parsed.isSidebarOpen !== undefined ? parsed.isSidebarOpen : true
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
  
  const [isSaving, setIsSaving] = useState(false)
  
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
  
  // Save state on change (debounced)
  useEffect(() => {
    if (state.organizationId && state.userId) {
      const timeoutId = setTimeout(() => {
        saveDashboardState(state)
        setIsSaving(false)
      }, 1000)
      
      return () => clearTimeout(timeoutId)
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
  
  // NEW: Grid Layout Actions
  
  const setLayout = useCallback((layout: Layout[]) => {
    setState(prev => ({
      ...prev,
      layouts: {
        ...prev.layouts,
        lg: layout
      }
    }))
    setIsSaving(true)
  }, [])
  
  const setLayouts = useCallback((layouts: Record<string, Layout[]>) => {
    setState(prev => ({
      ...prev,
      layouts: {
        lg: layouts.lg || prev.layouts.lg,
        md: layouts.md || prev.layouts.md,
        sm: layouts.sm || prev.layouts.sm,
        xs: layouts.xs || prev.layouts.xs,
        xxs: layouts.xxs || prev.layouts.xxs
      }
    }))
    setIsSaving(true)
  }, [])
  
  const addWidget = useCallback((widgetId: string, layoutItem?: Partial<Layout>) => {
    setState(prev => {
      // Don't add if already active
      if (prev.activeWidgets.includes(widgetId)) {
        return prev
      }
      
      // Find next available position
      const maxY = Math.max(...prev.layouts.lg.map(item => item.y + item.h), 0)
      
      const newLayoutItem: Layout = {
        i: widgetId,
        x: layoutItem?.x ?? 0,
        y: layoutItem?.y ?? maxY,
        w: layoutItem?.w ?? 4,
        h: layoutItem?.h ?? 2,
        minW: layoutItem?.minW,
        maxW: layoutItem?.maxW,
        minH: layoutItem?.minH,
        maxH: layoutItem?.maxH
      }
      
      return {
        ...prev,
        activeWidgets: [...prev.activeWidgets, widgetId],
        layouts: {
          lg: [...prev.layouts.lg, newLayoutItem],
          md: [...prev.layouts.md, { ...newLayoutItem, w: 5 }],
          sm: [...prev.layouts.sm, { ...newLayoutItem, w: 6, x: 0 }],
          xs: [...prev.layouts.xs, { ...newLayoutItem, w: 4, x: 0 }],
          xxs: [...prev.layouts.xxs, { ...newLayoutItem, w: 2, x: 0 }]
        },
        widgets: {
          ...prev.widgets,
          [widgetId]: {
            collapsed: false,
            visible: true,
            position: prev.activeWidgets.length
          }
        }
      }
    })
    setIsSaving(true)
  }, [])
  
  const removeWidget = useCallback((widgetId: string) => {
    console.log('🗑️ Removing widget:', widgetId)
    setState(prev => {
      const newActiveWidgets = prev.activeWidgets.filter(id => id !== widgetId)
      console.log('📊 Active widgets before:', prev.activeWidgets)
      console.log('📊 Active widgets after:', newActiveWidgets)
      return {
        ...prev,
        activeWidgets: newActiveWidgets,
        layouts: {
          lg: prev.layouts.lg.filter(item => item.i !== widgetId),
          md: prev.layouts.md.filter(item => item.i !== widgetId),
          sm: prev.layouts.sm.filter(item => item.i !== widgetId),
          xs: prev.layouts.xs.filter(item => item.i !== widgetId),
          xxs: prev.layouts.xxs.filter(item => item.i !== widgetId)
        }
      }
    })
    setIsSaving(true)
  }, [])
  
  const toggleSidebar = useCallback(() => {
    setState(prev => ({
      ...prev,
      isSidebarOpen: !prev.isSidebarOpen
    }))
  }, [])
  
  const saveLayout = useCallback(() => {
    saveDashboardState(state)
  }, [state])
  
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
  
  // Memoize layout for current breakpoint (lg)
  const currentLayout = useMemo(() => state.layouts.lg, [state.layouts.lg])
  
  const value: DashboardContextValue = {
    state,
    isEditMode: state.editMode,
    toggleCollapse,
    toggleEditMode,
    resetToDefaults,
    isCollapsed,
    canViewWidget: canView,
    canInteractWithWidget: canInteract,
    // NEW
    layout: currentLayout,
    setLayout,
    layouts: state.layouts,
    setLayouts,
    activeWidgets: state.activeWidgets,
    addWidget,
    removeWidget,
    isSidebarOpen: state.isSidebarOpen,
    toggleSidebar,
    saveLayout,
    isSaving
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

