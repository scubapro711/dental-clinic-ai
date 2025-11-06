/**
 * Mission Control Page - Main dashboard view
 * 
 * Features:
 * - 9 comprehensive widgets
 * - Draggable/resizable widget grid (RESPONSIVE)
 * - Real-time updates via WebSocket
 * - Persistent layout configuration
 * 
 * Widgets:
 * 1. MetricsWidget - Dashboard metrics from all agents
 * 2. AgentStatusWidget - Status of Alex, Marcus, Sophia
 * 3. ConversationMonitorWidget - Active conversations
 * 4. AppointmentsWidget - Today's appointments
 * 5. AnalyticsWidget - Financial insights
 * 6. AlertsWidget - Unified alerts
 * 7. LogsWidget - System logs
 * 8. PatientsWidget - Patient lookup
 * 9. ConfigurationWidget - System settings
 */

import { MissionControlLayout } from '@/components/dashboard/MissionControlLayout'
import { MetricsWidget } from '@/components/dashboard/widgets/MetricsWidget'
import { AgentStatusWidget } from '@/components/dashboard/widgets/AgentStatusWidget'
import { ConversationMonitorWidget } from '@/components/dashboard/widgets/ConversationMonitorWidget'
import { AppointmentsWidget } from '@/components/dashboard/widgets/AppointmentsWidget'
import { AnalyticsWidget } from '@/components/dashboard/widgets/AnalyticsWidget'
import { AlertsWidget } from '@/components/dashboard/widgets/AlertsWidget'
import { LogsWidget } from '@/components/dashboard/widgets/LogsWidget'
import { PatientsWidget } from '@/components/dashboard/widgets/PatientsWidget'
import { ConfigurationWidget } from '@/components/dashboard/widgets/ConfigurationWidget'
import { Responsive, WidthProvider } from 'react-grid-layout'
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'
import { useDashboardStore } from '@/stores/dashboardStore'

const ResponsiveGridLayout = WidthProvider(Responsive)

export default function MissionControlPage({ user, onLogout }) {
  const { widgetLayout, setWidgetLayout } = useDashboardStore()

  const handleLayoutChange = (layout, allLayouts) => {
    // Save the large layout as primary
    setWidgetLayout(allLayouts.lg || layout)
  }

  // Widget components map - all 9 widgets
  const widgets = {
    metrics: <MetricsWidget />,
    'agent-status': <AgentStatusWidget />,
    conversations: <ConversationMonitorWidget />,
    appointments: <AppointmentsWidget />,
    analytics: <AnalyticsWidget />,
    alerts: <AlertsWidget />,
    logs: <LogsWidget />,
    patients: <PatientsWidget />,
    configuration: <ConfigurationWidget />,
  }

  return (
    <MissionControlLayout user={user} onLogout={onLogout}>
      <div className="h-full" id="top">
        <div className="mb-6">
          <h2 className="text-3xl font-bold">Mission Control</h2>
          <p className="text-muted-foreground">
            Monitor and manage your AI dental assistant in real-time
          </p>
        </div>

        <ResponsiveGridLayout
          className="layout"
          layouts={{
            lg: widgetLayout,
            md: widgetLayout,
            sm: widgetLayout,
            xs: widgetLayout
          }}
          breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480 }}
          cols={{ lg: 12, md: 10, sm: 6, xs: 4 }}
          rowHeight={80}
          onLayoutChange={handleLayoutChange}
          draggableHandle=".drag-handle"
          isDraggable={true}
          isResizable={true}
          compactType="vertical"
          preventCollision={false}
        >
          {widgetLayout.map((item) => (
            <div 
              key={item.i} 
              id={item.i} 
              className="widget-container"
              data-grid={item}
            >
              {widgets[item.i] || (
                <div className="h-full flex items-center justify-center bg-muted rounded-lg border-2 border-dashed">
                  <p className="text-muted-foreground">Widget: {item.i}</p>
                </div>
              )}
            </div>
          ))}
        </ResponsiveGridLayout>
      </div>
    </MissionControlLayout>
  )
}
