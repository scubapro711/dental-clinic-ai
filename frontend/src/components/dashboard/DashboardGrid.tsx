/**
 * DashboardGrid v5.1 - React-RND with Context Integration
 * 
 * Features:
 * - react-rnd for drag & resize
 * - Integrated with DashboardContext
 * - Delete widget functionality
 * - Auto-save to localStorage via context
 * - Single widget: Today's Patients
 */

import { useCallback } from 'react'
import { Rnd } from 'react-rnd'
import { useDashboard } from '../../contexts/DashboardContext'
import TodaysPatientsWidget from '../widgets/TodaysPatientsWidget'

// Import custom styles
import '../../styles/dashboard-grid.css'

// Widget position and size type
interface WidgetState {
  x: number
  y: number
  width: number
  height: number
}

// Default position and size for Today's Patients widget
const DEFAULT_WIDGET_STATE: WidgetState = {
  x: 20,
  y: 20,
  width: 400,
  height: 350
}

// LocalStorage key
const STORAGE_KEY = 'dashboard-widget-todays-patients-v5'

export function DashboardGrid() {
  const { activeWidgets, removeWidget } = useDashboard()
  
  // Load widget state from localStorage or use default
  const loadWidgetState = (): WidgetState => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        return parsed
      }
    } catch (e) {
      console.error('Failed to load widget state:', e)
    }
    
    return DEFAULT_WIDGET_STATE
  }

  // Get initial state
  const getInitialState = (): WidgetState => {
    return loadWidgetState()
  }

  // Save widget state to localStorage
  const saveWidgetState = useCallback((state: WidgetState) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch (e) {
      console.error('Failed to save widget state:', e)
    }
  }, [])

  // Handle drag stop - save new position
  const handleDragStop = useCallback((e: any, d: { x: number; y: number }) => {
    const currentState = loadWidgetState()
    const newState = {
      ...currentState,
      x: d.x,
      y: d.y
    }
    saveWidgetState(newState)
  }, [saveWidgetState])

  // Handle resize stop - save new size and position
  const handleResizeStop = useCallback((
    e: any,
    direction: any,
    ref: HTMLElement,
    delta: any,
    position: { x: number; y: number }
  ) => {
    const newState = {
      x: position.x,
      y: position.y,
      width: ref.offsetWidth,
      height: ref.offsetHeight
    }
    saveWidgetState(newState)
  }, [saveWidgetState])

  // Handle delete widget
  const handleDelete = useCallback(() => {
    removeWidget('todays-patients')
    // Also clear from localStorage
    localStorage.removeItem(STORAGE_KEY)
  }, [removeWidget])

  // Check if widget is visible
  const isVisible = activeWidgets.includes('todays-patients')
  
  // Get widget state
  const widgetState = getInitialState()

  return (
    <div
      style={{
        width: '100%',
        minHeight: '100vh',
        padding: 'var(--spacing-lg)',
        position: 'relative',
        background: 'var(--background-secondary)'
      }}
    >
      {isVisible && (
        <Rnd
          size={{ width: widgetState.width, height: widgetState.height }}
          position={{ x: widgetState.x, y: widgetState.y }}
          onDragStop={handleDragStop}
          onResizeStop={handleResizeStop}
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
              👥
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
              Today's Patients
            </h3>
            
            {/* Delete Button */}
            <button
              onClick={handleDelete}
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
            <TodaysPatientsWidget />
          </div>
        </Rnd>
      )}
    </div>
  )
}
