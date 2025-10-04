/**
 * Configuration Widget - System and agent settings
 * 
 * Architecture: Widget → API → Configuration Store
 * 
 * Displays:
 * - Agent enable/disable toggles
 * - Alert thresholds
 * - System settings
 * - Feature flags
 */

import { useState } from 'react'
import { Widget } from '../Widget'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Settings, Sparkles, DollarSign, Calendar, Save } from 'lucide-react'
import { cn } from '@/lib/utils'

const AGENT_CONFIG = {
  alex: {
    name: 'Alex',
    description: 'Patient-facing agent',
    icon: Sparkles,
    color: 'text-blue-600',
  },
  marcus: {
    name: 'Marcus',
    description: 'CFO agent',
    icon: DollarSign,
    color: 'text-green-600',
  },
  sophia: {
    name: 'Sophia',
    description: 'Practice admin agent',
    icon: Calendar,
    color: 'text-purple-600',
  },
}

export function ConfigurationWidget() {
  const [config, setConfig] = useState({
    agents: {
      alex: { enabled: true, auto_escalate: true },
      marcus: { enabled: true, auto_alerts: true },
      sophia: { enabled: true, conflict_detection: true },
    },
    thresholds: {
      outstanding_payments: 10,
      no_show_rate: 10,
      response_time_warning: 5,
    },
    features: {
      real_time_updates: true,
      notifications: true,
      auto_backup: true,
    },
  })

  const [saving, setSaving] = useState(false)

  const toggleAgent = (agentId) => {
    setConfig(prev => ({
      ...prev,
      agents: {
        ...prev.agents,
        [agentId]: {
          ...prev.agents[agentId],
          enabled: !prev.agents[agentId].enabled
        }
      }
    }))
  }

  const toggleAgentFeature = (agentId, feature) => {
    setConfig(prev => ({
      ...prev,
      agents: {
        ...prev.agents,
        [agentId]: {
          ...prev.agents[agentId],
          [feature]: !prev.agents[agentId][feature]
        }
      }
    }))
  }

  const updateThreshold = (key, value) => {
    setConfig(prev => ({
      ...prev,
      thresholds: {
        ...prev.thresholds,
        [key]: parseInt(value) || 0
      }
    }))
  }

  const toggleFeature = (feature) => {
    setConfig(prev => ({
      ...prev,
      features: {
        ...prev.features,
        [feature]: !prev.features[feature]
      }
    }))
  }

  const handleSave = async () => {
    setSaving(true)
    
    try {
      // TODO: Call API to save configuration
      // await api.updateConfiguration(config)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      console.log('[ConfigurationWidget] Configuration saved:', config)
      alert('Configuration saved successfully!')
    } catch (err) {
      console.error('Error saving configuration:', err)
      alert('Failed to save configuration: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Widget
      id="configuration"
      title="Configuration"
      icon={Settings}
      actions={
        <Button
          variant="default"
          size="sm"
          onClick={handleSave}
          disabled={saving}
          className="h-7 text-xs"
        >
          <Save className="h-3 w-3 mr-1" />
          {saving ? 'Saving...' : 'Save'}
        </Button>
      }
    >
      <div className="space-y-4">
        {/* Agents Section */}
        <div>
          <h3 className="text-sm font-medium mb-3">Agents</h3>
          <div className="space-y-3">
            {Object.entries(AGENT_CONFIG).map(([agentId, agentInfo]) => {
              const Icon = agentInfo.icon
              const agentConfig = config.agents[agentId]
              
              return (
                <div key={agentId} className="p-3 border rounded-lg">
                  {/* Agent Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Icon className={cn('h-4 w-4', agentInfo.color)} />
                      <div>
                        <p className="text-sm font-medium">{agentInfo.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {agentInfo.description}
                        </p>
                      </div>
                    </div>
                    <Switch
                      checked={agentConfig.enabled}
                      onCheckedChange={() => toggleAgent(agentId)}
                    />
                  </div>
                  
                  {/* Agent Features */}
                  {agentConfig.enabled && (
                    <div className="space-y-2 pl-6">
                      {agentId === 'alex' && (
                        <div className="flex items-center justify-between">
                          <Label htmlFor={`${agentId}-escalate`} className="text-xs">
                            Auto-escalate urgent cases
                          </Label>
                          <Switch
                            id={`${agentId}-escalate`}
                            checked={agentConfig.auto_escalate}
                            onCheckedChange={() => toggleAgentFeature(agentId, 'auto_escalate')}
                          />
                        </div>
                      )}
                      
                      {agentId === 'marcus' && (
                        <div className="flex items-center justify-between">
                          <Label htmlFor={`${agentId}-alerts`} className="text-xs">
                            Auto-generate financial alerts
                          </Label>
                          <Switch
                            id={`${agentId}-alerts`}
                            checked={agentConfig.auto_alerts}
                            onCheckedChange={() => toggleAgentFeature(agentId, 'auto_alerts')}
                          />
                        </div>
                      )}
                      
                      {agentId === 'sophia' && (
                        <div className="flex items-center justify-between">
                          <Label htmlFor={`${agentId}-conflict`} className="text-xs">
                            Conflict detection
                          </Label>
                          <Switch
                            id={`${agentId}-conflict`}
                            checked={agentConfig.conflict_detection}
                            onCheckedChange={() => toggleAgentFeature(agentId, 'conflict_detection')}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Thresholds Section */}
        <div>
          <h3 className="text-sm font-medium mb-3">Alert Thresholds</h3>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label htmlFor="threshold-payments" className="text-xs">
                Outstanding Payments (count)
              </Label>
              <Input
                id="threshold-payments"
                type="number"
                value={config.thresholds.outstanding_payments}
                onChange={(e) => updateThreshold('outstanding_payments', e.target.value)}
                className="h-8 text-sm"
              />
            </div>
            
            <div className="space-y-1">
              <Label htmlFor="threshold-noshow" className="text-xs">
                No-Show Rate (%)
              </Label>
              <Input
                id="threshold-noshow"
                type="number"
                value={config.thresholds.no_show_rate}
                onChange={(e) => updateThreshold('no_show_rate', e.target.value)}
                className="h-8 text-sm"
              />
            </div>
            
            <div className="space-y-1">
              <Label htmlFor="threshold-response" className="text-xs">
                Response Time Warning (seconds)
              </Label>
              <Input
                id="threshold-response"
                type="number"
                value={config.thresholds.response_time_warning}
                onChange={(e) => updateThreshold('response_time_warning', e.target.value)}
                className="h-8 text-sm"
              />
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div>
          <h3 className="text-sm font-medium mb-3">System Features</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="feature-realtime" className="text-xs">
                Real-time updates
              </Label>
              <Switch
                id="feature-realtime"
                checked={config.features.real_time_updates}
                onCheckedChange={() => toggleFeature('real_time_updates')}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="feature-notifications" className="text-xs">
                Push notifications
              </Label>
              <Switch
                id="feature-notifications"
                checked={config.features.notifications}
                onCheckedChange={() => toggleFeature('notifications')}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="feature-backup" className="text-xs">
                Automatic backups
              </Label>
              <Switch
                id="feature-backup"
                checked={config.features.auto_backup}
                onCheckedChange={() => toggleFeature('auto_backup')}
              />
            </div>
          </div>
        </div>
      </div>
    </Widget>
  )
}
