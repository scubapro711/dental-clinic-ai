/**
 * Agent Status Widget - Monitor all AI agents health and performance
 * 
 * Displays status for all 3 agents:
 * - Alex (Patient Agent)
 * - Marcus (CFO Agent)
 * - Sophia (Admin Agent)
 * 
 * Architecture: Widget → API → LangGraph State (no full agent call)
 */

import { useEffect, useState } from 'react'
import { Widget } from '../Widget'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Sparkles, DollarSign, Calendar, Pause, Play, RotateCw, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'

const AGENT_ICONS = {
  alex: Sparkles,
  marcus: DollarSign,
  sophia: Calendar,
}

const AGENT_COLORS = {
  alex: 'text-blue-600 bg-blue-50',
  marcus: 'text-green-600 bg-green-50',
  sophia: 'text-purple-600 bg-purple-50',
}

export function AgentStatusWidget() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actionLoading, setActionLoading] = useState({})

  useEffect(() => {
    loadAgentsStatus()
    
    // Refresh every 10 seconds
    const interval = setInterval(loadAgentsStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  const loadAgentsStatus = async () => {
    try {
      // Architecture: Widget → API → LangGraph State
      const data = await api.getAllAgentsStatus()
      setAgents(data)
      setError(null)
      
      console.log('[AgentStatusWidget] Loaded status for', data.length, 'agents')
    } catch (err) {
      console.error('Error loading agents status:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handlePause = async (agentName) => {
    setActionLoading({ ...actionLoading, [agentName]: 'pause' })
    try {
      await api.pauseAgent(agentName)
      
      // Update local state optimistically
      setAgents(agents.map(agent =>
        agent.name === agentName
          ? { ...agent, status: 'paused' }
          : agent
      ))
    } catch (err) {
      console.error(`Error pausing agent ${agentName}:`, err)
    } finally {
      setActionLoading({ ...actionLoading, [agentName]: null })
    }
  }

  const handleResume = async (agentName) => {
    setActionLoading({ ...actionLoading, [agentName]: 'resume' })
    try {
      await api.resumeAgent(agentName)
      
      // Update local state optimistically
      setAgents(agents.map(agent =>
        agent.name === agentName
          ? { ...agent, status: 'online' }
          : agent
      ))
    } catch (err) {
      console.error(`Error resuming agent ${agentName}:`, err)
    } finally {
      setActionLoading({ ...actionLoading, [agentName]: null })
    }
  }

  const handleRestart = async (agentName) => {
    setActionLoading({ ...actionLoading, [agentName]: 'restart' })
    try {
      await api.restartAgent(agentName)
      
      // Reload status after restart
      await loadAgentsStatus()
    } catch (err) {
      console.error(`Error restarting agent ${agentName}:`, err)
    } finally {
      setActionLoading({ ...actionLoading, [agentName]: null })
    }
  }

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return 'bg-green-500'
      case 'offline':
        return 'bg-gray-500'
      case 'error':
        return 'bg-red-500'
      case 'paused':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'online':
        return 'default'
      case 'error':
        return 'destructive'
      case 'paused':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  return (
    <Widget
      id="agent-status"
      title="AI Agents"
      icon={Sparkles}
      loading={loading}
      error={error}
      empty={agents.length === 0}
      emptyMessage="No agents available"
      onRefresh={loadAgentsStatus}
    >
      <div className="space-y-3">
        {agents.map((agent) => {
          const Icon = AGENT_ICONS[agent.name] || Sparkles
          const colorClass = AGENT_COLORS[agent.name] || 'text-gray-600 bg-gray-50'
          
          return (
            <div
              key={agent.name}
              className="p-3 border rounded-lg hover:shadow-sm transition-shadow"
            >
              {/* Agent Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={cn('p-1.5 rounded-lg', colorClass)}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-medium text-sm">{agent.display_name}</p>
                    <p className="text-xs text-muted-foreground">{agent.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className={cn('w-2 h-2 rounded-full animate-pulse', getStatusColor(agent.status))} />
                  <Badge variant={getStatusBadgeVariant(agent.status)} className="text-xs uppercase">
                    {agent.status}
                  </Badge>
                </div>
              </div>

              {/* Agent Metrics */}
              <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Uptime</span>
                  <span className="font-medium">{formatUptime(agent.uptime_seconds)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Requests</span>
                  <span className="font-medium">{agent.requests_handled}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Response</span>
                  <span className="font-medium">{agent.avg_response_time.toFixed(1)}s</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Success</span>
                  <span className="font-medium">{agent.success_rate.toFixed(1)}%</span>
                </div>
              </div>

              {/* Success Rate Progress */}
              <div className="mb-3">
                <Progress value={agent.success_rate} className="h-1.5" />
              </div>

              {/* Control Buttons */}
              <div className="grid grid-cols-3 gap-1.5">
                {agent.status === 'online' ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePause(agent.name)}
                    disabled={actionLoading[agent.name] === 'pause'}
                    className="h-7 text-xs"
                  >
                    <Pause className="h-3 w-3 mr-1" />
                    Pause
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleResume(agent.name)}
                    disabled={actionLoading[agent.name] === 'resume'}
                    className="h-7 text-xs"
                  >
                    <Play className="h-3 w-3 mr-1" />
                    Resume
                  </Button>
                )}
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleRestart(agent.name)}
                  disabled={actionLoading[agent.name] === 'restart'}
                  className="h-7 text-xs col-span-2"
                >
                  <RotateCw className="h-3 w-3 mr-1" />
                  Restart
                </Button>
              </div>
            </div>
          )
        })}
      </div>
    </Widget>
  )
}
