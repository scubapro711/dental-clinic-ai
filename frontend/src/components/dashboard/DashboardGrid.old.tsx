/**
 * DashboardGrid - Drag & Drop Grid Layout
 * 
 * Features:
 * - Drag & drop widgets to reorder
 * - Resize widgets
 * - Responsive breakpoints
 * - Save/load layout
 * - Add widgets from sidebar
 * - Remove widgets
 * - RTL support
 */

import { useState, useCallback, useMemo } from 'react'
import { Responsive as ResponsiveGridLayout, WidthProvider, Layout } from 'react-grid-layout'
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
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'

const ResponsiveGrid = WidthProvider(ResponsiveGridLayout)

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

// Breakpoints configuration
const BREAKPOINTS = {
  lg: 1200,
  md: 996,
  sm: 768,
  xs: 480,
  xxs: 0
}

const COLS = {
  lg: 12,
  md: 10,
  sm: 6,
  xs: 4,
  xxs: 2
}

const ROW_HEIGHT = 60
const MARGIN: [number, number] = [16, 16]

interface DashboardGridProps {
  children?: React.ReactNode
}

export function DashboardGrid({ children }: DashboardGridProps) {
  const {
    layout,
    setLayout,
    layouts,
    setLayouts,
    activeWidgets,
    addWidget,
    removeWidget,
    isEditMode,
    saveLayout
  } = useDashboard()
  
  const [currentBreakpoint, setCurrentBreakpoint] = useState('lg')
  
  // Handle layout change
  const handleLayoutChange = useCallback((newLayout: Layout[], allLayouts: Record<string, Layout[]>) => {
    setLayout(newLayout)
    setLayouts(allLayouts)
    
    // Auto-save (debounced in context)
    if (isEditMode) {
      saveLayout()
    }
  }, [setLayout, setLayouts, isEditMode, saveLayout])
  
  // Handle breakpoint change
  const handleBreakpointChange = useCallback((breakpoint: string) => {
    setCurrentBreakpoint(breakpoint)
  }, [])
  
  // Handle drop from sidebar
  const handleDrop = useCallback((layout: Layout[], layoutItem: Layout, event: DragEvent) => {
    event.preventDefault()
    
    try {
      const data = event.dataTransfer?.getData('application/json')
      if (!data) return
      
      const widget = JSON.parse(data)
      
      // Add widget to active widgets
      addWidget(widget.id, {
        i: widget.id,
        x: layoutItem.x,
        y: layoutItem.y,
        w: widget.defaultSize.w,
        h: widget.defaultSize.h,
        minW: widget.minSize?.w,
        maxW: widget.maxSize?.w,
        minH: widget.minSize?.h,
        maxH: widget.maxSize?.h
      })
    } catch (error) {
      console.error('Error handling drop:', error)
    }
  }, [addWidget])
  
  // Handle remove widget
  const handleRemoveWidget = useCallback((e: React.MouseEvent, widgetId: string) => {
    e.stopPropagation()
    e.preventDefault()
    if (confirm(`Remove ${widgetId} widget from dashboard?`)) {
      removeWidget(widgetId)
    }
  }, [removeWidget])
  
  // Memoize children to improve performance
  const gridChildren = useMemo(() => {
    if (!activeWidgets || activeWidgets.length === 0) {
      return (
        <div
          key="empty-state"
          data-grid={{ i: 'empty-state', x: 0, y: 0, w: 12, h: 4, static: true }}
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--background)',
            borderRadius: 'var(--radius-lg)',
            border: '2px dashed var(--border)',
            padding: 'var(--spacing-2xl)',
            textAlign: 'center'
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
      )
    }
    
    return activeWidgets.map(widgetId => {
      const widgetDef = WIDGET_LIBRARY.find(w => w.id === widgetId)
      if (!widgetDef) return null
      
      const Icon = widgetDef.icon
      
      // Get layout data for this widget
      const layoutItem = layouts[currentBreakpoint]?.find(item => item.i === widgetId)
      
      return (
        <div
          key={widgetId}
          data-grid={layoutItem}
          className="dashboard-widget"
          style={{
            background: 'var(--background)',
            borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-md)',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            transition: 'box-shadow var(--transition-base)',
            border: '1px solid var(--border)'
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
      )
    })
  }, [activeWidgets, isEditMode, handleRemoveWidget, layouts, currentBreakpoint])
  
  return (
    <div
      className="dashboard-grid-container"
      style={{
        width: '100%',
        minHeight: '100vh',
        padding: 'var(--spacing-lg)',
        paddingRight: 'calc(320px + var(--spacing-lg))', // Space for sidebar
        transition: 'padding-right var(--transition-base)'
      }}
    >
      <ResponsiveGrid
        className="dashboard-grid"
        layouts={layouts}
        breakpoints={BREAKPOINTS}
        cols={COLS}
        rowHeight={ROW_HEIGHT}
        margin={MARGIN}
        containerPadding={[0, 0]}
        isDraggable={isEditMode}
        isResizable={isEditMode}
        isBounded={false}
        compactType={null}
        preventCollision={false}
        useCSSTransforms={true}
        isDroppable={isEditMode}
        draggableCancel=".widget-remove-button"
        onLayoutChange={handleLayoutChange}
        onBreakpointChange={handleBreakpointChange}
        onDrop={handleDrop}
        droppingItem={{ i: '__dropping-elem__', w: 4, h: 2 }}
        resizeHandles={['se', 'sw', 'ne', 'nw']}
      >
        {gridChildren}
      </ResponsiveGrid>
      
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
            zIndex: 'var(--z-fixed)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-sm)',
            animation: 'pulse 2s ease-in-out infinite'
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--primary-foreground)',
              animation: 'ping 1s cubic-bezier(0, 0, 0.2, 1) infinite'
            }}
          />
          Edit Mode Active - Drag & Resize Widgets
        </div>
      )}
    </div>
  )
}

