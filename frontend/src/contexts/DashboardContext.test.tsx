import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { DashboardProvider, useDashboard } from './DashboardContext'
import { useAuthStore } from '../store/useAuthStore'

// Mock useAuthStore
vi.mock('../store/useAuthStore', () => ({
  useAuthStore: vi.fn()
}))

// Mock rbac utilities
vi.mock('../utils/rbac', () => ({
  canViewWidget: vi.fn((role, widgetId) => {
    if (role === 'org_admin') return true
    if (role === 'org_staff' && widgetId === 'todays-patients') return true
    return false
  }),
  canInteractWithWidget: vi.fn((role, widgetId) => {
    if (role === 'org_admin') return true
    return false
  })
}))

describe('DashboardContext', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
    
    // Default mock user
    ;(useAuthStore as any).mockReturnValue({
      user: { id: 'user-1', role: 'org_admin' },
      organization: { id: 'org-1' }
    })
    
    localStorage.setItem('current_organization_id', 'org-1')
  })
  
  it('provides initial state', () => {
    const { result } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    expect(result.current.state).toBeDefined()
    expect(result.current.state.widgets).toBeDefined()
    expect(result.current.isEditMode).toBe(false)
  })
  
  it('toggles widget collapse state', () => {
    const { result } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    expect(result.current.isCollapsed('todays-patients')).toBe(false)
    
    act(() => {
      result.current.toggleCollapse('todays-patients')
    })
    
    expect(result.current.isCollapsed('todays-patients')).toBe(true)
  })
  
  it('persists state to localStorage', () => {
    const { result } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    act(() => {
      result.current.toggleCollapse('revenue')
    })
    
    const stored = localStorage.getItem('dashboard_state_org-1_user-1')
    expect(stored).toBeDefined()
    
    const parsed = JSON.parse(stored!)
    expect(parsed.widgets.revenue.collapsed).toBe(true)
  })
  
  it('loads state from localStorage on mount', () => {
    // Pre-populate localStorage
    const savedState = {
      widgets: {
        'todays-patients': { collapsed: true, visible: true, position: 0 },
        'decision-queue': { collapsed: false, visible: true, position: 1 },
        'revenue': { collapsed: false, visible: true, position: 2 },
        'compliance': { collapsed: false, visible: true, position: 3 },
        'clinical': { collapsed: false, visible: true, position: 4 },
        'fine-tuning': { collapsed: false, visible: true, position: 5 },
        'agent-activity': { collapsed: false, visible: true, position: 6 },
        'transparency': { collapsed: false, visible: true, position: 7 }
      },
      editMode: false,
      organizationId: 'org-1',
      userId: 'user-1',
      lastModified: new Date().toISOString(),
      layouts: {
        lg: [],
        md: [],
        sm: [],
        xs: [],
        xxs: []
      },
      activeWidgets: [],
      isSidebarOpen: true
    }
    localStorage.setItem('dashboard_state_org-1_user-1', JSON.stringify(savedState))
    
    const { result } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    expect(result.current.isCollapsed('todays-patients')).toBe(true)
  })
  
  it('loads new state when organization switches', () => {
    const { result, rerender } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    // Collapse widget in org-1
    act(() => {
      result.current.toggleCollapse('revenue')
    })
    expect(result.current.isCollapsed('revenue')).toBe(true)
    
    // Switch to org-2
    ;(useAuthStore as any).mockReturnValue({
      user: { id: 'user-1', role: 'org_admin' },
      organization: { id: 'org-2' }
    })
    localStorage.setItem('current_organization_id', 'org-2')
    
    rerender()
    
    // Revenue should be expanded in org-2 (different state)
    expect(result.current.isCollapsed('revenue')).toBe(false)
  })
  
  it('respects RBAC permissions', () => {
    ;(useAuthStore as any).mockReturnValue({
      user: { id: 'user-1', role: 'org_staff' },
      organization: { id: 'org-1' }
    })
    
    const { result } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    expect(result.current.canViewWidget('todays-patients')).toBe(true)
    expect(result.current.canViewWidget('revenue')).toBe(false)
  })
  
  it('resets to defaults', () => {
    const { result } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    // Collapse some widgets
    act(() => {
      result.current.toggleCollapse('revenue')
      result.current.toggleCollapse('compliance')
    })
    
    expect(result.current.isCollapsed('revenue')).toBe(true)
    expect(result.current.isCollapsed('compliance')).toBe(true)
    
    // Reset
    act(() => {
      result.current.resetToDefaults()
    })
    
    expect(result.current.isCollapsed('revenue')).toBe(false)
    expect(result.current.isCollapsed('compliance')).toBe(false)
  })
  
  it('handles localStorage quota exceeded', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    // Mock localStorage.setItem to throw QuotaExceededError
    const originalSetItem = localStorage.setItem
    localStorage.setItem = vi.fn(() => {
      const error = new Error('QuotaExceededError')
      error.name = 'QuotaExceededError'
      throw error
    })
    
    const { result } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    act(() => {
      result.current.toggleCollapse('revenue')
    })
    
    expect(consoleError).toHaveBeenCalledWith(expect.stringContaining('quota exceeded'))
    
    // Restore
    localStorage.setItem = originalSetItem
    consoleError.mockRestore()
  })
  
  it('toggles edit mode', () => {
    const { result } = renderHook(() => useDashboard(), {
      wrapper: DashboardProvider
    })
    
    expect(result.current.isEditMode).toBe(false)
    
    act(() => {
      result.current.toggleEditMode()
    })
    
    expect(result.current.isEditMode).toBe(true)
    
    act(() => {
      result.current.toggleEditMode()
    })
    
    expect(result.current.isEditMode).toBe(false)
  })
  
  it('throws error when useDashboard used outside provider', () => {
    expect(() => {
      renderHook(() => useDashboard())
    }).toThrow('useDashboard must be used within DashboardProvider')
  })
})

