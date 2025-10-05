import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle2, Clock, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Agent Activity Panel - Shows real-time agent activity
 * 
 * Phase 1: Basic Transparency
 * - Shows which agent is currently active
 * - Displays current task
 * - Shows tool calls in progress
 * - Progress indicator
 * - Duration timer
 */
export default function AgentActivityPanel({ activity, toolCalls }) {
  if (!activity) {
    return (
      <Card className="h-full">
        <CardHeader className="border-b">
          <CardTitle className="text-sm flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            Agent Activity
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center text-sm text-gray-500">
            <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
              <Sparkles className="w-6 h-6 text-gray-400" />
            </div>
            <p>No active agents</p>
            <p className="text-xs mt-1">Start a conversation to see agent activity</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { agent, task, status, progress, startTime } = activity;

  // Calculate elapsed time
  const elapsed = startTime ? ((Date.now() - startTime) / 1000).toFixed(1) : 0;

  // Agent configuration
  const agentConfig = {
    alex: {
      name: 'Alex',
      role: 'Patient Care',
      color: 'blue',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-900',
      badgeColor: 'bg-blue-500'
    },
    cfo: {
      name: 'Marcus',
      role: 'CFO Agent',
      color: 'green',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-900',
      badgeColor: 'bg-green-500'
    },
    admin: {
      name: 'Sophia',
      role: 'Practice Admin',
      color: 'purple',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-900',
      badgeColor: 'bg-purple-500'
    },
    supervisor: {
      name: 'Supervisor',
      role: 'Coordinator',
      color: 'gray',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      textColor: 'text-gray-900',
      badgeColor: 'bg-gray-500'
    }
  };

  const config = agentConfig[agent] || agentConfig.supervisor;

  return (
    <Card className="h-full">
      <CardHeader className="border-b">
        <CardTitle className="text-sm flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-600" />
          Agent Activity
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        {/* Agent Status */}
        <div className={cn(
          'rounded-lg p-4 border-2',
          config.bgColor,
          config.borderColor
        )}>
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className={cn(
                'w-2 h-2 rounded-full',
                status === 'running' && 'bg-green-500 animate-pulse',
                status === 'completed' && 'bg-gray-400'
              )} />
              <Badge className={config.badgeColor}>
                {config.name}
              </Badge>
            </div>
            <div className="flex items-center gap-1 text-xs text-gray-600">
              <Clock className="w-3 h-3" />
              {elapsed}s
            </div>
          </div>

          <div className="space-y-2">
            <div>
              <div className="text-xs text-gray-600 mb-1">{config.role}</div>
              <div className={cn('text-sm font-medium', config.textColor)}>
                {task || 'Processing...'}
              </div>
            </div>

            {/* Progress Bar */}
            {status === 'running' && progress !== undefined && (
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-gray-600">
                  <span>Progress</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full transition-all duration-300',
                      `bg-${config.color}-500`
                    )}
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {status === 'completed' && (
              <div className="flex items-center gap-2 text-xs text-green-600">
                <CheckCircle2 className="w-4 h-4" />
                Task completed
              </div>
            )}
          </div>
        </div>

        {/* Tools in Use */}
        {toolCalls && toolCalls.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs font-semibold text-gray-600 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Tools in Use
            </div>
            <div className="space-y-2">
              {toolCalls.map((tool, idx) => (
                <ToolCallItem key={idx} tool={tool} />
              ))}
            </div>
          </div>
        )}

        {/* Summary (when completed) */}
        {status === 'completed' && (
          <div className="pt-3 border-t">
            <div className="text-xs font-semibold text-gray-600 mb-2">Summary</div>
            <div className="space-y-1 text-xs text-gray-600">
              <div className="flex justify-between">
                <span>Duration:</span>
                <span className="font-medium">{elapsed}s</span>
              </div>
              <div className="flex justify-between">
                <span>Tools called:</span>
                <span className="font-medium">{toolCalls?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Status:</span>
                <span className="font-medium text-green-600">✓ Success</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Tool Call Item - Individual tool call display
 */
function ToolCallItem({ tool }) {
  const { name, status, duration } = tool;

  const statusConfig = {
    pending: {
      icon: <Loader2 className="w-3 h-3 text-gray-400" />,
      color: 'border-gray-300 bg-gray-50',
      textColor: 'text-gray-600'
    },
    running: {
      icon: <Loader2 className="w-3 h-3 text-blue-600 animate-spin" />,
      color: 'border-blue-300 bg-blue-50',
      textColor: 'text-blue-900'
    },
    success: {
      icon: <CheckCircle2 className="w-3 h-3 text-green-600" />,
      color: 'border-green-300 bg-green-50',
      textColor: 'text-green-900'
    },
    error: {
      icon: <span className="text-red-600">✗</span>,
      color: 'border-red-300 bg-red-50',
      textColor: 'text-red-900'
    }
  };

  const config = statusConfig[status] || statusConfig.pending;

  return (
    <div className={cn(
      'rounded-md p-2 border text-xs',
      config.color
    )}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {config.icon}
          <span className={cn('font-medium', config.textColor)}>
            {name}
          </span>
        </div>
        {duration && (
          <span className="text-gray-600">{duration}s</span>
        )}
      </div>
    </div>
  );
}
