/**
 * Mission Control Page - Main dashboard view
 * 
 * Features:
 * - 9 comprehensive widgets
 * - Draggable/resizable widget grid
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
import GridLayout from 'react-grid-layout'
import { useDashboardStore } from '@/stores/dashboardStore'

export default function MissionControlPage({ user, onLogout }) {
  const { widgetLayout, setWidgetLayout } = useDashboardStore()

  const handleLayoutChange = (layout) => {
    setWidgetLayout(layout)
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

        <GridLayout
          className="layout"
          layout={widgetLayout}
          cols={12}
          rowHeight={80}
          width={1200}
          onLayoutChange={handleLayoutChange}
          draggableHandle=".drag-handle"
          isDraggable
          isResizable
          compactType="vertical"
          preventCollision={false}
        >
          {widgetLayout.map((item) => (
            <div key={item.i} id={item.i} className="widget-container">
              {widgets[item.i] || (
                <div className="h-full flex items-center justify-center bg-muted rounded-lg border-2 border-dashed">
                  <p className="text-muted-foreground">Widget: {item.i}</p>
                </div>
              )}
            </div>
          ))}
        </GridLayout>
      </div>
    </MissionControlLayout>
  )
}
