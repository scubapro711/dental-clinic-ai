/**
 * DashboardGrid v6.0 - Multi-Widget Support
 * 
 * Features:
 * - react-rnd for drag & resize
 * - Integrated with DashboardContext
 * - Delete widget functionality
 * - Fixed: Widget position/size persistence
 * - Support for multiple widgets
 */

import { useState, useCallback, useEffect } from 'react'
import { Rnd } from 'react-rnd'
import { useDashboard } from '../../contexts/DashboardContext'
import TodaysPatientsWidget from '../widgets/TodaysPatientsWidget'
import RevenueWidget from '../widgets/RevenueWidget'
import DecisionQueueWidget from '../widgets/DecisionQueueWidget'
import ComplianceWidget from '../widgets/ComplianceWidget'
import ClinicalInsightsWidget from '../widgets/ClinicalInsightsWidget'
import FineTuningWidget from '../widgets/FineTuningWidget'
import AgentActivityWidget from '../widgets/AgentActivityWidget'
import TransparencyWidget from '../widgets/TransparencyWidget'

// Import custom styles
import '../../styles/dashboard-grid.css'

// Widget position and size type
interface WidgetState {
  x: number
  y: number
  width: number
  height: number
}

// Widget configuration type
interface WidgetConfig {
  id: string
  title: string
  icon: string
  component: React.ComponentType<any>
  defaultState: WidgetState
}

// Widget configurations
const WIDGET_CONFIGS: WidgetConfig[] = [
  {
    id: 'decision-queue',
    title: 'Decision Queue',
    icon: '⚠️',
    component: DecisionQueueWidget,
    defaultState: { x: 20, y: 20, width: 1220, height: 300 }
  },
  {
    id: 'todays-patients',
    title: "Today's Patients",
    icon: '👥',
    component: TodaysPatientsWidget,
    defaultState: { x: 20, y: 340, width: 380, height: 450 }
  },
  {
    id: 'compliance-alerts',
    title: 'Compliance',
    icon: '🛡️',
    component: ComplianceWidget,
    defaultState: { x: 420, y: 340, width: 380, height: 450 }
  },
  {
    id: 'revenue',
    title: 'Revenue',
    icon: '💰',
    component: RevenueWidget,
    defaultState: { x: 820, y: 340, width: 420, height: 450 }
  },
  {
    id: 'clinical-system',
    title: 'Clinical Insights',
    icon: '🩺',
    component: ClinicalInsightsWidget,
    defaultState: { x: 20, y: 810, width: 1220, height: 400 }
  },
  {
    id: 'fine-tuning',
    title: 'Fine-Tuning',
    icon: '⚙️',
    component: FineTuningWidget,
    defaultState: { x: 20, y: 1230, width: 600, height: 400 }
  },
  {
    id: 'agent-activity',
    title: 'Agent Activity',
    icon: '📊',
    component: AgentActivityWidget,
    defaultState: { x: 640, y: 1230, width: 600, height: 400 }
  },
  {
    id: 'transparency-panel',
    title: 'Transparency',
    icon: '👁️',
    component: TransparencyWidget,
    defaultState: { x: 20, y: 1650, width: 1220, height: 450 }
  }
]

// Get localStorage key for widget
const getStorageKey = (widgetId: string) => `dashboard-widget-${widgetId}-v6`

export function DashboardGrid() {
  const { activeWidgets, removeWidget } = useDashboard()
  
  // State for all widgets - map of widgetId to WidgetState
  const [widgetStates, setWidgetStates] = useState<Record<string, WidgetState>>(() => {
    const initialStates: Record<string, WidgetState> = {}
    
    WIDGET_CONFIGS.forEach(config => {
      try {
        const saved = localStorage.getItem(getStorageKey(config.id))
        if (saved) {
          initialStates[config.id] = JSON.parse(saved)
        } else {
          initialStates[config.id] = config.defaultState
        }
      } catch (e) {
        console.error(`Failed to load state for ${config.id}:`, e)
        initialStates[config.id] = config.defaultState
      }
    })
    
    return initialStates
  })

  // Save widget state to localStorage whenever it changes
  useEffect(() => {
    Object.entries(widgetStates).forEach(([widgetId, state]) => {
      try {
        localStorage.setItem(getStorageKey(widgetId), JSON.stringify(state))
      } catch (e) {
        console.error(`Failed to save state for ${widgetId}:`, e)
      }
    })
  }, [widgetStates])

  // Handle drag stop for a specific widget
  const handleDragStop = useCallback((widgetId: string) => {
    return (e: any, d: { x: number; y: number }) => {
      setWidgetStates(prev => ({
        ...prev,
        [widgetId]: {
          ...prev[widgetId],
          x: d.x,
          y: d.y
        }
      }))
    }
  }, [])

  // Handle resize stop for a specific widget
  const handleResizeStop = useCallback((widgetId: string) => {
    return (
      e: any,
      direction: any,
      ref: HTMLElement,
      delta: any,
      position: { x: number; y: number }
    ) => {
      setWidgetStates(prev => ({
        ...prev,
        [widgetId]: {
          x: position.x,
          y: position.y,
          width: ref.offsetWidth,
          height: ref.offsetHeight
        }
      }))
    }
  }, [])

  // Handle delete widget
  const handleDelete = useCallback((widgetId: string) => {
    return () => {
      removeWidget(widgetId)
      // Also clear from localStorage
      localStorage.removeItem(getStorageKey(widgetId))
    }
  }, [removeWidget])

  // Calculate dynamic grid height based on widgets
  const gridHeight = Object.values(widgetStates).reduce((maxHeight, state) => {
    const widgetBottom = state.y + state.height
    return Math.max(maxHeight, widgetBottom)
  }, 1000) // Minimum 1000px

  return (
    <div
      style={{
        width: '100%',
        minHeight: `${gridHeight + 100}px`, // Add 100px padding at bottom
        padding: 'var(--spacing-lg)',
        position: 'relative',
        background: 'var(--background-secondary)'
      }}
    >
      {WIDGET_CONFIGS.map(config => {
        const isVisible = activeWidgets.includes(config.id)
        if (!isVisible) return null
        
        const widgetState = widgetStates[config.id]
        const WidgetComponent = config.component
        
        return (
          <Rnd
            key={config.id}
            size={{ width: widgetState.width, height: widgetState.height }}
            position={{ x: widgetState.x, y: widgetState.y }}
            onDragStop={handleDragStop(config.id)}
            onResizeStop={handleResizeStop(config.id)}
            minWidth={300}
            minHeight={250}
            bounds="parent"
            dragHandleClassName="widget-drag-handle"
            style={{
              background: 'var(--background)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-md)',
              border: '1px solid var(--border)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}
          >
            {/* Widget Header - Drag Handle */}
            <div
              className="widget-drag-handle"
              style={{
                padding: 'var(--spacing-md)',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                background: 'var(--background-secondary)',
                cursor: 'move'
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '18px'
                }}
              >
                {config.icon}
              </div>
              <h3
                style={{
                  fontSize: 'var(--font-size-lg)',
                  fontWeight: 'var(--font-weight-semibold)',
                  color: 'var(--foreground)',
                  margin: 0,
                  flex: 1
                }}
              >
                {config.title}
              </h3>
              
              {/* Delete Button */}
              <button
                onClick={handleDelete(config.id)}
                style={{
                  padding: '8px',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--foreground-secondary)',
                  fontSize: '18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 'var(--radius-sm)',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'var(--destructive-light)'
                  e.currentTarget.style.color = 'var(--destructive)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--foreground-secondary)'
                }}
                title="Delete widget"
              >
                🗑️
              </button>
            </div>

            {/* Widget Content */}
            <div
              style={{
                flex: '1',
                overflow: 'auto',
                padding: 0
              }}
            >
              <WidgetComponent />
            </div>
          </Rnd>
        )
      })}
    </div>
  )
}
