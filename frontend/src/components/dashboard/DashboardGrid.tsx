/**
 * DashboardGrid v3.0 - Powered by react-grid-layout
 * 
 * Features:
 * - Free widget placement (compactType={null})
 * - Drag & resize widgets
 * - Persistent layouts via DashboardContext
 * - RBAC integration
 * - Professional UX following F-Pattern
 * - No auto-compacting or position jumping
 * 
 * Configuration based on:
 * - ilert.com case study (Nov 2024)
 * - react-grid-layout best practices
 * - Material Design principles
 */

import { useCallback } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
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

// Import react-grid-layout CSS
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'

// Create responsive grid layout with WidthProvider
const ResponsiveGridLayout = WidthProvider(Responsive)

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
  
  // Handle layout change
  const handleLayoutChange = useCallback((currentLayout: Layout[], allLayouts: Record<string, Layout[]>) => {
    // Update all layouts in context
    setLayouts(allLayouts)
  }, [setLayouts])
  
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
            Click widgets in the sidebar to add them to your dashboard
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
      <ResponsiveGridLayout
        className="layout"
        layouts={layouts}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={60}
        margin={[16, 16]}
        containerPadding={[0, 0]}
        
        // CRITICAL SETTINGS - Prevent auto-compacting and overlapping
        compactType={null}              // NO auto-compact (free positioning)
        preventCollision={true}          // Prevent overlapping
        allowOverlap={false}             // No widget overlap
        
        // Functionality
        isDraggable={isEditMode}
        isResizable={isEditMode}
        
        // Resize handles (all corners)
        resizeHandles={['se', 'sw', 'ne', 'nw']}
        
        // Drag handle (widget header only)
        draggableHandle=".widget-header"
        
        // Callbacks
        onLayoutChange={handleLayoutChange}
        
        // Performance
        useCSSTransforms={true}
        
        // Responsive behavior
        autoSize={true}
      >
        {activeWidgets.map((widgetId) => {
          const widgetDef = WIDGET_LIBRARY.find(w => w.id === widgetId)
          if (!widgetDef) return null
          
          const Icon = widgetDef.icon
          
          return (
            <div
              key={widgetId}
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
          )
        })}
      </ResponsiveGridLayout>
      
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

