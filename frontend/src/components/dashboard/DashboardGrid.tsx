/**
 * DashboardGrid v2.0 - Powered by Gridstack.js
 * 
 * Features:
 * - Free widget placement (no auto-compacting)
 * - Drag widgets from sidebar
 * - Resize widgets
 * - Drag to reposition
 * - State persistence
 * - RBAC integration
 * - RTL support
 * - Mobile touch support
 */

import { useEffect, useRef, createRef, useCallback, useMemo } from 'react'
import { GridStack, GridStackWidget } from 'gridstack'
import { X } from 'lucide-react'
import { useDashboard } from '../../contexts/DashboardContext'
import { WIDGET_LIBRARY } from './DashboardSidebar'
import ProtectedWidget from '../rbac/ProtectedWidget'
import TodaysPatientsWidget from '../widgets/TodaysPatientsWidget'
import RevenueWidget from '../widgets/RevenueWidget'
import DecisionQueueWidget from '../widgets/DecisionQueueWidget'
import ComplianceAlerts from '../compliance/ComplianceAlerts'
import ClinicalDashboard from '../clinical/ClinicalDashboard'
import EnhancedFineTuningWidget from '../fine-tuning/EnhancedFineTuningWidget'
import AgentActivityPanel from '../transparency/AgentActivityPanel'
import EnhancedTransparencyPanel from '../transparency/EnhancedTransparencyPanel'

// Import Gridstack CSS
import 'gridstack/dist/gridstack.min.css'

// Widget Content Renderer
function renderWidgetContent(widgetId: string) {
  switch (widgetId) {
    case 'todays-patients':
      return (
        <ProtectedWidget widgetId="todays-patients">
          <TodaysPatientsWidget />
        </ProtectedWidget>
      )
    
    case 'revenue':
      return (
        <ProtectedWidget widgetId="revenue">
          <RevenueWidget />
        </ProtectedWidget>
      )
    
    case 'decision-queue':
      return (
        <ProtectedWidget widgetId="decision-queue">
          <DecisionQueueWidget />
        </ProtectedWidget>
      )
    
    case 'compliance-alerts':
      return (
        <ProtectedWidget widgetId="compliance-alerts">
          <ComplianceAlerts />
        </ProtectedWidget>
      )
    
    case 'clinical-system':
      return (
        <ProtectedWidget widgetId="clinical-system">
          <ClinicalDashboard />
        </ProtectedWidget>
      )
    
    case 'fine-tuning':
      return (
        <ProtectedWidget widgetId="fine-tuning">
          <EnhancedFineTuningWidget />
        </ProtectedWidget>
      )
    
    case 'agent-activity':
      return (
        <ProtectedWidget widgetId="agent-activity">
          <AgentActivityPanel />
        </ProtectedWidget>
      )
    
    case 'transparency-panel':
      return (
        <ProtectedWidget widgetId="transparency-panel">
          <EnhancedTransparencyPanel />
        </ProtectedWidget>
      )
    
    default:
      return (
        <div style={{ 
          padding: 'var(--spacing-md)', 
          textAlign: 'center',
          color: 'var(--foreground-tertiary)'
        }}>
          <p>Widget "{widgetId}" not found</p>
        </div>
      )
  }
}

export function DashboardGrid() {
  const {
    activeWidgets,
    removeWidget,
    isEditMode,
    layouts,
    setLayouts
  } = useDashboard()
  
  const gridRef = useRef<GridStack | null>(null)
  const refs = useRef<Record<string, React.RefObject<HTMLDivElement>>>({})
  const isUpdatingRef = useRef(false)
  
  // Create refs for each widget
  if (activeWidgets) {
    activeWidgets.forEach((widgetId) => {
      if (!refs.current[widgetId]) {
        refs.current[widgetId] = createRef<HTMLDivElement>()
      }
    })
  }
  
  // Memoize widget positions to prevent race conditions
  // This ensures positions are computed atomically when activeWidgets or layouts change
  const widgetPositions = useMemo(() => {
    if (!activeWidgets || !layouts?.lg) return {}
    
    const positions: Record<string, { x: number, y: number, w: number, h: number }> = {}
    
    activeWidgets.forEach((widgetId) => {
      const layoutItem = layouts.lg.find(item => item.i === widgetId)
      positions[widgetId] = {
        x: layoutItem?.x ?? 0,
        y: layoutItem?.y ?? 0,
        w: layoutItem?.w ?? 4,
        h: layoutItem?.h ?? 4
      }
    })
    
    return positions
  }, [activeWidgets, layouts])
  
  // Initialize Gridstack
  useEffect(() => {
    if (!gridRef.current) {
      gridRef.current = GridStack.init({
        float: true, // Free positioning (no auto-compact)
        cellHeight: 60,
        margin: 16,
        column: 12,
        animate: true,
        disableOneColumnMode: true, // Prevent responsive stacking
        minRow: 1, // Minimum rows
        acceptWidgets: false, // No drag from outside for now
        removable: false, // No drag to remove
        draggable: {
          handle: '.widget-header'
        },
        resizable: {
          handles: 'se, sw, ne, nw'
        }
      })
      
      // Listen to changes
      gridRef.current.on('change', (event, items) => {
        if (!items) return
        
        // Update layouts in context
        const newLayout = items.map((item: GridStackWidget) => ({
          i: item.id || '',
          x: item.x || 0,
          y: item.y || 0,
          w: item.w || 4,
          h: item.h || 4
        }))
        
        setLayouts({
          lg: newLayout,
          md: newLayout,
          sm: newLayout,
          xs: newLayout,
          xxs: newLayout
        })
      })
    }
    
    return () => {
      if (gridRef.current) {
        gridRef.current.destroy(false)
        gridRef.current = null
      }
    }
  }, [])
  
  // Handle change events from Gridstack
  const handleGridChange = useCallback((event: Event, items: GridStackWidget[]) => {
    if (!items || isUpdatingRef.current) return
    
    // Update layouts in context
    const newLayout = items.map((item: GridStackWidget) => ({
      i: item.id || '',
      x: item.x || 0,
      y: item.y || 0,
      w: item.w || 4,
      h: item.h || 4
    }))
    
    setLayouts({
      lg: newLayout,
      md: newLayout,
      sm: newLayout,
      xs: newLayout,
      xxs: newLayout
    })
  }, [setLayouts])
  
  // Update widgets when widgetPositions changes (memoized from activeWidgets + layouts)
  useEffect(() => {
    if (!gridRef.current || !activeWidgets || Object.keys(widgetPositions).length === 0) return
    
    // Prevent re-entry during update
    if (isUpdatingRef.current) return
    isUpdatingRef.current = true
    
    const grid = gridRef.current
    
    // Disable change events temporarily to avoid loops
    grid.off('change')
    
    // Batch update for performance
    grid.batchUpdate()
    
    // Remove all widgets
    grid.removeAll(false)
    
    // Add widgets back with their memoized positions
    activeWidgets.forEach((widgetId) => {
      const ref = refs.current[widgetId]
      if (ref && ref.current) {
        const pos = widgetPositions[widgetId]
        
        // Make widget with position data
        grid.makeWidget(ref.current, {
          id: widgetId,
          x: pos.x,
          y: pos.y,
          w: pos.w,
          h: pos.h
        })
      }
    })
    
    grid.batchUpdate(false)
    
    // Re-enable change events after a delay to allow React to settle
    setTimeout(() => {
      if (gridRef.current) {
        gridRef.current.on('change', handleGridChange)
      }
      isUpdatingRef.current = false
    }, 100)
  }, [widgetPositions, activeWidgets, handleGridChange])
  
  // Enable/disable drag and resize based on edit mode
  useEffect(() => {
    if (!gridRef.current) return
    
    const grid = gridRef.current
    
    if (isEditMode) {
      grid.enable()
    } else {
      grid.disable()
    }
  }, [isEditMode])
  
  // Handle remove widget
  const handleRemoveWidget = useCallback((e: React.MouseEvent, widgetId: string) => {
    e.stopPropagation()
    e.preventDefault()
    
    const widgetDef = WIDGET_LIBRARY.find(w => w.id === widgetId)
    if (confirm(`Remove ${widgetDef?.title || 'widget'} from dashboard?`)) {
      removeWidget(widgetId)
    }
  }, [removeWidget])
  
  // Render empty state
  if (!activeWidgets || activeWidgets.length === 0) {
    return (
      <div
        className="dashboard-grid-container"
        style={{
          width: '100%',
          minHeight: '100vh',
          padding: 'var(--spacing-lg)',
          paddingRight: 'calc(320px + var(--spacing-lg))'
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--background)',
            borderRadius: 'var(--radius-lg)',
            border: '2px dashed var(--border)',
            padding: 'var(--spacing-2xl)',
            textAlign: 'center',
            minHeight: '400px'
          }}
        >
          <h3
            style={{
              fontSize: 'var(--font-size-2xl)',
              fontWeight: 'var(--font-weight-bold)',
              color: 'var(--foreground)',
              margin: '0 0 var(--spacing-sm) 0'
            }}
          >
            No Widgets Added
          </h3>
          <p
            style={{
              fontSize: 'var(--font-size-base)',
              color: 'var(--foreground-tertiary)',
              margin: '0 0 var(--spacing-md) 0',
              maxWidth: '500px'
            }}
          >
            Drag widgets from the sidebar to customize your dashboard
          </p>
          <div
            style={{
              fontSize: 'var(--font-size-sm)',
              color: 'var(--foreground-secondary)',
              background: 'var(--muted)',
              padding: '8px 16px',
              borderRadius: 'var(--radius-md)'
            }}
          >
            👉 Open the sidebar on the right to get started
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div
      className="dashboard-grid-container"
      style={{
        width: '100%',
        minHeight: '100vh',
        padding: 'var(--spacing-lg)',
        paddingRight: 'calc(320px + var(--spacing-lg))'
      }}
    >
      <div className="grid-stack">
        {activeWidgets.map((widgetId) => {
          const widgetDef = WIDGET_LIBRARY.find(w => w.id === widgetId)
          if (!widgetDef) return null
          
          const Icon = widgetDef.icon
          
          return (
            <div
              key={widgetId}
              ref={refs.current[widgetId]}
              className="grid-stack-item"
            >
              <div 
                className="grid-stack-item-content"
                style={{
                  background: 'var(--background)',
                  borderRadius: 'var(--radius-lg)',
                  boxShadow: 'var(--shadow-md)',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column',
                  border: '1px solid var(--border)',
                  height: '100%'
                }}
              >
                {/* Widget Header */}
                <div
                  className="widget-header"
                  style={{
                    padding: 'var(--spacing-md)',
                    borderBottom: '1px solid var(--border)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: 'var(--background-secondary)',
                    cursor: isEditMode ? 'move' : 'default'
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--spacing-sm)',
                      flex: '1',
                      minWidth: '0'
                    }}
                  >
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: 'var(--radius-md)',
                        background: 'oklch(0.95 0.05 240)',
                        color: 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: '0'
                      }}
                    >
                      <Icon size={18} />
                    </div>
                    <h3
                      style={{
                        fontSize: 'var(--font-size-base)',
                        fontWeight: 'var(--font-weight-semibold)',
                        color: 'var(--foreground)',
                        margin: '0',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      {widgetDef.title}
                    </h3>
                  </div>
                  
                  {/* Remove button (edit mode only) */}
                  {isEditMode && (
                    <button
                      onClick={(e) => handleRemoveWidget(e, widgetId)}
                      className="widget-remove-button"
                      aria-label={`Remove ${widgetDef.title}`}
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--foreground-tertiary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all var(--transition-base)',
                        flexShrink: '0'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'var(--destructive)'
                        e.currentTarget.style.color = 'var(--destructive-foreground)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'transparent'
                        e.currentTarget.style.color = 'var(--foreground-tertiary)'
                      }}
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
                
                {/* Widget Content */}
                <div
                  className="widget-content"
                  style={{
                    flex: '1',
                    overflow: 'auto'
                  }}
                >
                  {renderWidgetContent(widgetId)}
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Edit Mode Indicator */}
      {isEditMode && (
        <div
          className="edit-mode-indicator"
          style={{
            position: 'fixed',
            bottom: 'var(--spacing-lg)',
            left: 'var(--spacing-lg)',
            padding: '12px 20px',
            background: 'var(--primary)',
            color: 'var(--primary-foreground)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-lg)',
            fontSize: 'var(--font-size-sm)',
            fontWeight: 'var(--font-weight-semibold)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-sm)'
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: 'var(--primary-foreground)',
              animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
            }}
          />
          Edit Mode Active - Drag & Resize Widgets
        </div>
      )}
    </div>
  )
}

