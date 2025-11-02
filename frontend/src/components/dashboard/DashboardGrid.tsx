/**
 * DashboardGrid v4.0 - Clean Rebuild
 * 
 * Simple, working implementation:
 * - One widget: Today's Patients
 * - Always-on drag & resize (no edit mode)
 * - Auto-save to localStorage
 * - No Done/Reset buttons
 */

import { useCallback, useRef } from 'react'
import { Responsive, Layout, Layouts } from 'react-grid-layout'
import { useElementWidth } from '../../hooks/useElementWidth'
import TodaysPatientsWidget from '../widgets/TodaysPatientsWidget'

// Import react-grid-layout CSS
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'
import '../../styles/dashboard-grid.css'

// Default layout for Today's Patients widget
const DEFAULT_LAYOUT: Layout = {
  i: 'todays-patients',
  x: 0,
  y: 0,
  w: 4,
  h: 5,
  minW: 3,
  minH: 4
}

export function DashboardGrid() {
  // Calculate container width
  const containerRef = useRef<HTMLDivElement>(null)
  const containerWidth = useElementWidth(containerRef)
  
  // Load layout from localStorage or use default
  const loadLayout = (): Layouts => {
    try {
      const saved = localStorage.getItem('dashboard-layout-v4')
      if (saved) {
        return JSON.parse(saved)
      }
    } catch (e) {
      console.error('Failed to load layout:', e)
    }
    
    // Return default layout for all breakpoints
    return {
      lg: [DEFAULT_LAYOUT],
      md: [DEFAULT_LAYOUT],
      sm: [DEFAULT_LAYOUT],
      xs: [DEFAULT_LAYOUT],
      xxs: [DEFAULT_LAYOUT]
    }
  }
  
  // Save layout to localStorage
  const saveLayout = (layouts: Layouts) => {
    try {
      localStorage.setItem('dashboard-layout-v4', JSON.stringify(layouts))
      console.log('Layout saved:', layouts)
    } catch (e) {
      console.error('Failed to save layout:', e)
    }
  }
  
  // Handle layout change (auto-save)
  const handleLayoutChange = useCallback((currentLayout: Layout[], allLayouts: Layouts) => {
    console.log('Layout changed:', allLayouts)
    saveLayout(allLayouts)
  }, [])
  
  // Wait for width measurement
  if (!containerWidth) {
    return (
      <div
        ref={containerRef}
        style={{
          width: '100%',
          minHeight: '100vh',
          padding: 'var(--spacing-lg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <div style={{ color: 'var(--foreground-secondary)' }}>
          Loading dashboard...
        </div>
      </div>
    )
  }
  
  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        minHeight: '100vh',
        padding: 'var(--spacing-lg)'
      }}
    >
      <Responsive
        className="layout"
        layouts={loadLayout()}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={60}
        margin={[16, 16]}
        containerPadding={[0, 0]}
        
        // Always draggable and resizable
        isDraggable={true}
        isResizable={true}
        
        // Free positioning
        compactType={null}
        preventCollision={false}
        
        // Resize handles
        resizeHandles={['se', 'sw', 'ne', 'nw']}
        
        // Callbacks
        onLayoutChange={handleLayoutChange}
        
        // Width
        width={containerWidth}
      >
        <div
          key="todays-patients"
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
                margin: 0
              }}
            >
              Today's Patients
            </h3>
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
        </div>
      </Responsive>
    </div>
  )
}
