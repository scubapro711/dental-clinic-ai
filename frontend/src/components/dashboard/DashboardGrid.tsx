import React, { useState, useEffect } from 'react'
import { Rnd } from 'react-rnd'
import { useDashboard } from '../../contexts/DashboardContext'
import TodaysPatientsWidget from '../widgets/TodaysPatientsWidget'
import RevenueWidget from '../widgets/RevenueWidget'
import EnhancedDecisionQueueWidget from '../widgets/EnhancedDecisionQueueWidget'
import ComplianceWidget from '../widgets/ComplianceWidget'
import ClinicalInsightsWidget from '../widgets/ClinicalInsightsWidget'
import FineTuningWidget from '../widgets/FineTuningWidget'
import AgentActivityWidget from '../widgets/AgentActivityWidget'
import TransparencyWidget from '../widgets/TransparencyWidget'

interface WidgetState {
  x: number
  y: number
  width: number
  height: number
}

interface WidgetConfig {
  id: string
  title: string
  icon: string
  component: React.ComponentType<any>
  defaultState: WidgetState
}

// Widget configurations - Right sidebar layout
const WIDGET_CONFIGS: WidgetConfig[] = [
  // Row 1: Decision Queue (left, very wide) + Right sidebar starts
  {
    id: 'decision-queue',
    title: 'Decision Queue',
    icon: '⚠️',
    component: EnhancedDecisionQueueWidget,
    defaultState: { x: 20, y: 20, width: 1100, height: 450 }
  },
  {
    id: 'transparency-panel',
    title: 'Transparency',
    icon: '👁️',
    component: TransparencyWidget,
    defaultState: { x: 1140, y: 20, width: 320, height: 300 }
  },
  {
    id: 'compliance-alerts',
    title: 'Compliance',
    icon: '🛡️',
    component: ComplianceWidget,
    defaultState: { x: 1140, y: 340, width: 320, height: 350 }
  },
  {
    id: 'agent-activity',
    title: 'Agent Activity',
    icon: '📊',
    component: AgentActivityWidget,
    defaultState: { x: 1140, y: 710, width: 320, height: 350 }
  },
  // Row 2: Bottom row - 4 widgets
  {
    id: 'todays-patients',
    title: "Today's Patients",
    icon: '👥',
    component: TodaysPatientsWidget,
    defaultState: { x: 20, y: 490, width: 380, height: 450 }
  },
  {
    id: 'revenue',
    title: 'Revenue',
    icon: '💰',
    component: RevenueWidget,
    defaultState: { x: 420, y: 490, width: 340, height: 450 }
  },
  {
    id: 'clinical-system',
    title: 'Clinical Insights',
    icon: '🩺',
    component: ClinicalInsightsWidget,
    defaultState: { x: 780, y: 490, width: 340, height: 450 }
  },
  {
    id: 'fine-tuning',
    title: 'Fine-Tuning',
    icon: '⚙️',
    component: FineTuningWidget,
    defaultState: { x: 1140, y: 1080, width: 320, height: 450 }
  }
]

// Get localStorage key for widget
const getStorageKey = (widgetId: string) => `dashboard-widget-${widgetId}-v6`

// Get initial state from localStorage or default
const getInitialState = (widgetId: string, defaultState: WidgetState): WidgetState => {
  const stored = localStorage.getItem(getStorageKey(widgetId))
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch (e) {
      console.error(`Failed to parse stored state for ${widgetId}:`, e)
    }
  }
  return defaultState
}

// Save state to localStorage
const saveState = (widgetId: string, state: WidgetState) => {
  localStorage.setItem(getStorageKey(widgetId), JSON.stringify(state))
}

export default function DashboardGrid({ onPatientSelect }: { onPatientSelect?: (patient: any) => void }) {
  const { activeWidgets, removeWidget } = useDashboard()

  // State for each widget
  const [widgetStates, setWidgetStates] = useState<Record<string, WidgetState>>(() => {
    const initial: Record<string, WidgetState> = {}
    WIDGET_CONFIGS.forEach(config => {
      initial[config.id] = getInitialState(config.id, config.defaultState)
    })
    return initial
  })

  // Calculate dynamic grid height
  const gridHeight = React.useMemo(() => {
    let maxBottom = 1000 // minimum height
    Object.entries(widgetStates).forEach(([id, state]) => {
      if (activeWidgets.includes(id)) {
        const bottom = state.y + state.height
        if (bottom > maxBottom) {
          maxBottom = bottom
        }
      }
    })
    return maxBottom + 100 // add padding at bottom
  }, [widgetStates, activeWidgets])

  // Save to localStorage when state changes
  useEffect(() => {
    Object.entries(widgetStates).forEach(([id, state]) => {
      saveState(id, state)
    })
  }, [widgetStates])

  const handleDragStop = (widgetId: string, d: any) => {
    setWidgetStates(prev => ({
      ...prev,
      [widgetId]: { ...prev[widgetId], x: d.x, y: d.y }
    }))
  }

  const handleResizeStop = (widgetId: string, ref: any, position: any) => {
    setWidgetStates(prev => ({
      ...prev,
      [widgetId]: {
        x: position.x,
        y: position.y,
        width: parseInt(ref.style.width),
        height: parseInt(ref.style.height)
      }
    }))
  }

  const handleDelete = (widgetId: string) => {
    removeWidget(widgetId)
  }

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        minHeight: `${gridHeight}px`,
        backgroundColor: '#f5f5f5',
        padding: '10px'
      }}
    >
      {WIDGET_CONFIGS.map(config => {
        if (!activeWidgets.includes(config.id)) return null

        const state = widgetStates[config.id]
        const WidgetComponent = config.component

        return (
          <Rnd
            key={config.id}
            position={{ x: state.x, y: state.y }}
            size={{ width: state.width, height: state.height }}
            onDragStop={(e, d) => handleDragStop(config.id, d)}
            onResizeStop={(e, direction, ref, delta, position) =>
              handleResizeStop(config.id, ref, position)
            }
            dragHandleClassName="widget-drag-handle"
            bounds="parent"
            minWidth={280}
            minHeight={250}
            style={{
              zIndex: 1
            }}
          >
            <div
              style={{
                width: '100%',
                height: '100%',
                backgroundColor: 'white',
                borderRadius: '12px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden'
              }}
            >
              {/* Widget Header - Drag Handle */}
              <div
                className="widget-drag-handle"
                style={{
                  padding: '12px 16px',
                  borderBottom: '1px solid #e0e0e0',
                  cursor: 'move',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  backgroundColor: '#fafafa'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>{config.icon}</span>
                  <span style={{ fontWeight: 600, fontSize: '14px' }}>{config.title}</span>
                </div>
                <button
                  onClick={() => handleDelete(config.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '18px',
                    color: '#999',
                    padding: '0 4px'
                  }}
                  title="Remove widget"
                >
                  🗑️
                </button>
              </div>

              {/* Widget Content */}
              <div
                style={{
                  flex: 1,
                  overflow: 'auto',
                  padding: '16px'
                }}
              >
                <WidgetComponent 
                  {...(config.id === 'todays-patients' && onPatientSelect ? { onPatientSelect } : {})}
                />
              </div>
            </div>
          </Rnd>
        )
      })}
    </div>
  )
}
