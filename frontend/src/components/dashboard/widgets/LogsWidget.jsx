/**
 * Logs Widget - System and agent activity logs
 * 
 * Architecture: Widget → API → Database/Log Store
 * 
 * Displays:
 * - Recent system logs
 * - Agent activity
 * - Errors and warnings
 * - Filterable by source and level
 */

import { useEffect, useState } from 'react'
import { Widget } from '../Widget'
import { Badge } from '@/components/ui/badge'
import { FileText, Sparkles, DollarSign, Calendar, Settings, Server, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'

const SOURCE_CONFIG = {
  alex: {
    name: 'Alex',
    icon: Sparkles,
    color: 'text-blue-600 bg-blue-50',
  },
  marcus: {
    name: 'Marcus',
    icon: DollarSign,
    color: 'text-green-600 bg-green-50',
  },
  sophia: {
    name: 'Sophia',
    icon: Calendar,
    color: 'text-purple-600 bg-purple-50',
  },
  supervisor: {
    name: 'Supervisor',
    icon: Settings,
    color: 'text-orange-600 bg-orange-50',
  },
  system: {
    name: 'System',
    icon: Server,
    color: 'text-gray-600 bg-gray-50',
  },
  api: {
    name: 'API',
    icon: Server,
    color: 'text-gray-600 bg-gray-50',
  },
}

const LEVEL_CONFIG = {
  debug: {
    label: 'DEBUG',
    color: 'bg-gray-100 text-gray-700',
    icon: '🔍',
  },
  info: {
    label: 'INFO',
    color: 'bg-blue-100 text-blue-700',
    icon: 'ℹ️',
  },
  warning: {
    label: 'WARN',
    color: 'bg-yellow-100 text-yellow-700',
    icon: '⚠️',
  },
  error: {
    label: 'ERROR',
    color: 'bg-red-100 text-red-700',
    icon: '❌',
  },
  critical: {
    label: 'CRIT',
    color: 'bg-red-200 text-red-900',
    icon: '🚨',
  },
}

export function LogsWidget() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    level: null,
    source: null,
  })

  useEffect(() => {
    loadLogs()
    
    // Refresh every 10 seconds
    const interval = setInterval(loadLogs, 10000)
    return () => clearInterval(interval)
  }, [filters])

  const loadLogs = async () => {
    try {
      // Architecture: Widget → API → Database/Log Store
      const params = {
        limit: 50,
        ...(filters.level && { level: filters.level }),
        ...(filters.source && { source: filters.source }),
      }
      
      const data = await api.getRecentLogs(params)
      setLogs(data)
      setError(null)
      
      console.log('[LogsWidget] Loaded', data.length, 'logs')
    } catch (err) {
      console.error('Error loading logs:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (isoString) => {
    const date = new Date(isoString)
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const seconds = date.getSeconds().toString().padStart(2, '0')
    return `${hours}:${minutes}:${seconds}`
  }

  const toggleFilter = (type, value) => {
    setFilters(prev => ({
      ...prev,
      [type]: prev[type] === value ? null : value
    }))
  }

  const errorCount = logs.filter(log => log.level === 'error' || log.level === 'critical').length

  return (
    <Widget
      id="logs"
      title="System Logs"
      icon={FileText}
      loading={loading}
      error={error}
      empty={logs.length === 0}
      emptyMessage="No logs available"
      onRefresh={loadLogs}
      badge={errorCount > 0 ? errorCount : null}
      badgeVariant="destructive"
    >
      <div className="space-y-3">
        {/* Filters */}
        <div className="space-y-2">
          {/* Level Filter */}
          <div className="flex flex-wrap gap-1">
            {Object.entries(LEVEL_CONFIG).map(([level, config]) => (
              <button
                key={level}
                onClick={() => toggleFilter('level', level)}
                className={cn(
                  'px-2 py-0.5 text-xs rounded transition-all',
                  filters.level === level
                    ? config.color + ' ring-2 ring-offset-1'
                    : 'bg-muted hover:bg-muted/80'
                )}
              >
                {config.icon} {config.label}
              </button>
            ))}
          </div>
          
          {/* Source Filter */}
          <div className="flex flex-wrap gap-1">
            {Object.entries(SOURCE_CONFIG).map(([source, config]) => {
              const Icon = config.icon
              return (
                <button
                  key={source}
                  onClick={() => toggleFilter('source', source)}
                  className={cn(
                    'px-2 py-0.5 text-xs rounded transition-all flex items-center gap-1',
                    filters.source === source
                      ? config.color + ' ring-2 ring-offset-1'
                      : 'bg-muted hover:bg-muted/80'
                  )}
                >
                  <Icon className="h-3 w-3" />
                  {config.name}
                </button>
              )
            })}
          </div>
        </div>

        {/* Logs List */}
        <div className="space-y-1 max-h-[400px] overflow-y-auto font-mono text-xs">
          {logs.map((log) => {
            const sourceConfig = SOURCE_CONFIG[log.source] || SOURCE_CONFIG.system
            const levelConfig = LEVEL_CONFIG[log.level] || LEVEL_CONFIG.info
            const SourceIcon = sourceConfig.icon
            
            return (
              <div
                key={log.id}
                className="p-2 border rounded hover:bg-muted/50 transition-colors"
              >
                {/* Log Header */}
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-muted-foreground">
                    {formatTime(log.timestamp)}
                  </span>
                  
                  <Badge className={cn('text-xs px-1 py-0', levelConfig.color)}>
                    {levelConfig.label}
                  </Badge>
                  
                  <div className={cn('flex items-center gap-1 px-1.5 py-0.5 rounded text-xs', sourceConfig.color)}>
                    <SourceIcon className="h-3 w-3" />
                    <span>{sourceConfig.name}</span>
                  </div>
                </div>
                
                {/* Log Message */}
                <p className="text-xs text-foreground mb-1">
                  {log.message}
                </p>
                
                {/* Log Details */}
                {log.details && Object.keys(log.details).length > 0 && (
                  <details className="text-xs text-muted-foreground">
                    <summary className="cursor-pointer hover:text-foreground">
                      Details
                    </summary>
                    <pre className="mt-1 p-2 bg-muted rounded overflow-x-auto">
                      {JSON.stringify(log.details, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </Widget>
  )
}
