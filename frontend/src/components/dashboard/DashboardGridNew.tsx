/**
 * DashboardGrid v2.0 - Modern Drag & Drop Grid Layout with @dnd-kit
 * 
 * Features:
 * - Free widget placement (no auto-compacting)
 * - Drag widgets from sidebar
 * - Resize widgets
 * - Drag to reposition
 * - State persistence
 * - RBAC integration
 * - RTL support
 */

import { useState, useCallback } from 'react'
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverEvent
} from '@dnd-kit/core'
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

// Grid constants
const GRID_SIZE = 60 // pixels per grid unit
const MARGIN = 16

interface WidgetPosition {
  id: string
  x: number
  y: number
  w: number
  h: number
}

interface DashboardGridProps {
  children?: React.ReactNode
}

export function DashboardGrid({ children }: DashboardGridProps) {
  const {
    activeWidgets,
    addWidget,
    removeWidget,
    isEditMode,
    layouts,
    setLayouts
  } = useDashboard()
  
  const [activeId, setActiveId] = useState<string | null>(null)
  const [draggedFromSidebar, setDraggedFromSidebar] = useState<any>(null)
  
  // Configure sensors for drag
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement before drag starts
      },
    })
  )
  
  // Get widget positions from layouts
  const getWidgetPositions = (): WidgetPosition[] => {
    if (!activeWidgets || !layouts.lg) return []
    
    return activeWidgets.map(widgetId => {
      const layoutItem = layouts.lg.find(item => item.i === widgetId)
      return {
        id: widgetId,
        x: layoutItem?.x || 0,
        y: layoutItem?.y || 0,
        w: layoutItem?.w || 4,
        h: layoutItem?.h || 4
      }
    })
  }
  
  const widgetPositions = getWidgetPositions()
  
  // Handle drag start
  const handleDragStart = useCallback((event: DragStartEvent) => {
    const { active } = event
    setActiveId(active.id as string)
    
    // Check if dragging from sidebar
    if (active.data.current?.fromSidebar) {
      setDraggedFromSidebar(active.data.current.widget)
    }
  }, [])
  
  // Handle drag over (for preview)
  const handleDragOver = useCallback((event: DragOverEvent) => {
    // Can add preview logic here if needed
  }, [])
  
  // Handle drag end
  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, delta } = event
    
    // If dragging from sidebar
    if (draggedFromSidebar) {
      const widget = draggedFromSidebar
      
      // Calculate grid position from drop location
      const x = Math.round(delta.x / (GRID_SIZE + MARGIN))
      const y = Math.round(delta.y / (GRID_SIZE + MARGIN))
      
      // Add widget at drop position
      addWidget(widget.id, {
        i: widget.id,
        x: Math.max(0, x),
        y: Math.max(0, y),
        w: widget.defaultSize.w,
        h: widget.defaultSize.h
      })
      
      setDraggedFromSidebar(null)
    } else {
      // Moving existing widget
      const widgetId = active.id as string
      const currentPos = widgetPositions.find(w => w.id === widgetId)
      
      if (currentPos) {
        const gridDeltaX = Math.round(delta.x / (GRID_SIZE + MARGIN))
        const gridDeltaY = Math.round(delta.y / (GRID_SIZE + MARGIN))
        
        const newX = Math.max(0, currentPos.x + gridDeltaX)
        const newY = Math.max(0, currentPos.y + gridDeltaY)
        
        // Update layout
        const newLayouts = { ...layouts }
        const lgLayout = [...(newLayouts.lg || [])]
        const itemIndex = lgLayout.findIndex(item => item.i === widgetId)
        
        if (itemIndex >= 0) {
          lgLayout[itemIndex] = {
            ...lgLayout[itemIndex],
            x: newX,
            y: newY
          }
          
          newLayouts.lg = lgLayout
          setLayouts(newLayouts)
        }
      }
    }
    
    setActiveId(null)
  }, [draggedFromSidebar, widgetPositions, layouts, setLayouts, addWidget])
  
  // Handle remove widget
  const handleRemoveWidget = useCallback((e: React.MouseEvent, widgetId: string) => {
    e.stopPropagation()
    e.preventDefault()
    if (confirm(`Remove widget from dashboard?`)) {
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
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <div
        className="dashboard-grid-container"
        style={{
          width: '100%',
          minHeight: '100vh',
          padding: 'var(--spacing-lg)',
          paddingRight: 'calc(320px + var(--spacing-lg))',
          position: 'relative'
        }}
      >
        {/* Grid with widgets */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            minHeight: '800px'
          }}
        >
          {widgetPositions.map(pos => {
            const widgetDef = WIDGET_LIBRARY.find(w => w.id === pos.id)
            if (!widgetDef) return null
            
            const Icon = widgetDef.icon
            
            return (
              <div
                key={pos.id}
                id={pos.id}
                style={{
                  position: 'absolute',
                  left: `${pos.x * (GRID_SIZE + MARGIN)}px`,
                  top: `${pos.y * (GRID_SIZE + MARGIN)}px`,
                  width: `${pos.w * GRID_SIZE + (pos.w - 1) * MARGIN}px`,
                  height: `${pos.h * GRID_SIZE + (pos.h - 1) * MARGIN}px`,
                  background: 'var(--background)',
                  borderRadius: 'var(--radius-lg)',
                  boxShadow: 'var(--shadow-md)',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column',
                  border: '1px solid var(--border)',
                  cursor: isEditMode ? 'move' : 'default',
                  transition: activeId === pos.id ? 'none' : 'all 0.2s ease',
                  opacity: activeId === pos.id ? 0.5 : 1
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
                      onClick={(e) => handleRemoveWidget(e, pos.id)}
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
                  {renderWidgetContent(pos.id)}
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
                background: 'var(--primary-foreground)'
              }}
            />
            Edit Mode Active - Drag & Resize Widgets
          </div>
        )}
      </div>
      
      {/* Drag Overlay */}
      <DragOverlay>
        {activeId ? (
          <div
            style={{
              background: 'var(--background)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-xl)',
              padding: 'var(--spacing-md)',
              opacity: 0.8
            }}
          >
            Dragging widget...
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}

