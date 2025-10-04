/**
 * Alerts Widget - Unified alerts from all agents
 * 
 * Architecture: Widget → API → Database (aggregate from all agents)
 * 
 * Displays alerts from:
 * - Alex (Patient Agent): Escalations, urgent requests
 * - Marcus (CFO Agent): Financial issues, outstanding payments
 * - Sophia (Admin Agent): Scheduling conflicts, operational issues
 * 
 * Features:
 * - Priority-based sorting (urgent first)
 * - Color-coded by source agent
 * - Dismiss and Resolve actions
 * - Real-time updates
 */

import { useEffect, useState } from 'react'
import { Widget } from '../Widget'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, Sparkles, DollarSign, Calendar, X, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'

const AGENT_CONFIG = {
  alex: {
    name: 'Alex',
    icon: Sparkles,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
  },
  marcus: {
    name: 'Marcus',
    icon: DollarSign,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
  },
  sophia: {
    name: 'Sophia',
    icon: Calendar,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
  },
  system: {
    name: 'System',
    icon: AlertCircle,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
  },
}

const PRIORITY_CONFIG = {
  urgent: {
    label: 'Urgent',
    color: 'bg-red-100 text-red-800 border-red-300',
    dotColor: 'bg-red-500',
  },
  high: {
    label: 'High',
    color: 'bg-orange-100 text-orange-800 border-orange-300',
    dotColor: 'bg-orange-500',
  },
  normal: {
    label: 'Normal',
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    dotColor: 'bg-blue-500',
  },
  low: {
    label: 'Low',
    color: 'bg-gray-100 text-gray-800 border-gray-300',
    dotColor: 'bg-gray-500',
  },
}

export function AlertsWidget() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actionLoading, setActionLoading] = useState({})
  const [filter, setFilter] = useState('all') // all, alex, marcus, sophia

  useEffect(() => {
    loadAlerts()
    
    // Refresh every 15 seconds
    const interval = setInterval(loadAlerts, 15000)
    return () => clearInterval(interval)
  }, [filter])

  const loadAlerts = async () => {
    try {
      // Architecture: Widget → API → Database (aggregate from all agents)
      const params = filter !== 'all' ? { source: filter } : {}
      const data = await api.getActiveAlerts(params)
      
      setAlerts(data)
      setError(null)
      
      console.log('[AlertsWidget] Loaded', data.length, 'alerts')
    } catch (err) {
      console.error('Error loading alerts:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDismiss = async (alertId) => {
    setActionLoading({ ...actionLoading, [alertId]: 'dismiss' })
    
    try {
      await api.dismissAlert(alertId)
      
      // Remove from local state
      setAlerts(alerts.filter(a => a.id !== alertId))
      
      console.log('[AlertsWidget] Alert dismissed:', alertId)
    } catch (err) {
      console.error('Error dismissing alert:', err)
      alert('Failed to dismiss alert: ' + err.message)
    } finally {
      setActionLoading({ ...actionLoading, [alertId]: null })
    }
  }

  const handleResolve = async (alertId) => {
    setActionLoading({ ...actionLoading, [alertId]: 'resolve' })
    
    try {
      await api.resolveAlert(alertId)
      
      // Remove from local state
      setAlerts(alerts.filter(a => a.id !== alertId))
      
      console.log('[AlertsWidget] Alert resolved:', alertId)
    } catch (err) {
      console.error('Error resolving alert:', err)
      alert('Failed to resolve alert: ' + err.message)
    } finally {
      setActionLoading({ ...actionLoading, [alertId]: null })
    }
  }

  const formatTime = (isoString) => {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  const urgentCount = alerts.filter(a => a.priority === 'urgent').length

  return (
    <Widget
      id="alerts"
      title="Alerts"
      icon={AlertCircle}
      loading={loading}
      error={error}
      empty={alerts.length === 0}
      emptyMessage="No active alerts"
      onRefresh={loadAlerts}
      badge={urgentCount > 0 ? urgentCount : null}
      badgeVariant="destructive"
    >
      <div className="space-y-3">
        {/* Filter Tabs */}
        <div className="flex gap-1 p-1 bg-muted rounded-lg">
          {['all', 'alex', 'marcus', 'sophia'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                'flex-1 px-2 py-1 text-xs font-medium rounded transition-colors',
                filter === f
                  ? 'bg-background shadow-sm'
                  : 'hover:bg-background/50'
              )}
            >
              {f === 'all' ? 'All' : AGENT_CONFIG[f].name}
            </button>
          ))}
        </div>

        {/* Alerts List */}
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {alerts.map((alert) => {
            const agentConfig = AGENT_CONFIG[alert.source] || AGENT_CONFIG.system
            const priorityConfig = PRIORITY_CONFIG[alert.priority] || PRIORITY_CONFIG.normal
            const Icon = agentConfig.icon
            
            return (
              <div
                key={alert.id}
                className={cn(
                  'p-3 border rounded-lg transition-all',
                  agentConfig.bgColor,
                  agentConfig.borderColor
                )}
              >
                {/* Alert Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={cn('p-1 rounded', agentConfig.bgColor)}>
                      <Icon className={cn('h-3 w-3', agentConfig.color)} />
                    </div>
                    <span className="text-xs font-medium text-muted-foreground">
                      {agentConfig.name}
                    </span>
                    <div className={cn('w-1.5 h-1.5 rounded-full', priorityConfig.dotColor)} />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatTime(alert.created_at)}
                  </span>
                </div>

                {/* Alert Content */}
                <div className="mb-2">
                  <div className="flex items-start gap-2 mb-1">
                    <p className="text-sm font-medium flex-1">{alert.title}</p>
                    <Badge 
                      variant="outline" 
                      className={cn('text-xs', priorityConfig.color)}
                    >
                      {priorityConfig.label}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {alert.message}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDismiss(alert.id)}
                    disabled={actionLoading[alert.id] === 'dismiss'}
                    className="h-6 text-xs flex-1"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Dismiss
                  </Button>
                  
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => handleResolve(alert.id)}
                    disabled={actionLoading[alert.id] === 'resolve'}
                    className="h-6 text-xs flex-1"
                  >
                    <Check className="h-3 w-3 mr-1" />
                    Resolve
                  </Button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </Widget>
  )
}
