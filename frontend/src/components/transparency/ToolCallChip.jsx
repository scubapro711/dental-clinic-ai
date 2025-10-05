import React, { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckCircle2, Loader2, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Tool Call Chip - Enhanced visualization of tool calls
 * 
 * Phase 1: Basic Transparency
 * - Shows tool name and status
 * - Expandable to show input/output
 * - Duration display
 * - Status indicators
 */
export default function ToolCallChip({ tool, expandable = true }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { name, status, duration, input, output } = tool;

  // Status configuration
  const statusConfig = {
    pending: {
      icon: <Loader2 className="w-3 h-3 text-gray-400" />,
      label: 'Pending',
      color: 'border-gray-300 bg-gray-50',
      badgeColor: 'bg-gray-500'
    },
    running: {
      icon: <Loader2 className="w-3 h-3 text-blue-600 animate-spin" />,
      label: 'Running',
      color: 'border-blue-300 bg-blue-50 animate-pulse',
      badgeColor: 'bg-blue-500'
    },
    success: {
      icon: <CheckCircle2 className="w-3 h-3 text-green-600" />,
      label: '✓ Success',
      color: 'border-green-300 bg-green-50',
      badgeColor: 'bg-green-500'
    },
    error: {
      icon: <span className="text-red-600 text-xs">✗</span>,
      label: '✗ Error',
      color: 'border-red-300 bg-red-50',
      badgeColor: 'bg-red-500'
    }
  };

  const config = statusConfig[status] || statusConfig.pending;

  // Tool name formatting
  const formatToolName = (name) => {
    // Convert snake_case to Title Case
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Get tool icon based on name
  const getToolIcon = (name) => {
    if (name.includes('revenue') || name.includes('financial')) return '💰';
    if (name.includes('patient') || name.includes('appointment')) return '👤';
    if (name.includes('schedule') || name.includes('calendar')) return '📅';
    if (name.includes('search') || name.includes('query')) return '🔍';
    if (name.includes('chart') || name.includes('graph')) return '📊';
    return '🔧';
  };

  return (
    <div className={cn(
      'rounded-lg border-2 overflow-hidden transition-all duration-200',
      config.color
    )}>
      {/* Main Content */}
      <div className="px-3 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 flex-1">
            <span className="text-lg">{getToolIcon(name)}</span>
            <div className="flex-1">
              <div className="font-semibold text-sm">
                {formatToolName(name)}
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <Badge variant="secondary" className={cn('text-xs', config.badgeColor)}>
                  {config.label}
                </Badge>
                {duration && (
                  <span className="text-xs text-gray-600">{duration}s</span>
                )}
              </div>
            </div>
          </div>
          
          {expandable && (input || output) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-6 w-6 p-0"
            >
              {isExpanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t px-3 py-2 space-y-2 bg-white/50">
          {input && (
            <div>
              <div className="text-xs font-semibold text-gray-600 mb-1">Input:</div>
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                {JSON.stringify(input, null, 2)}
              </pre>
            </div>
          )}
          {output && (
            <div>
              <div className="text-xs font-semibold text-gray-600 mb-1">Output:</div>
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto max-h-32">
                {JSON.stringify(output, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Tool Calls List - Display multiple tool calls
 */
export function ToolCallsList({ toolCalls }) {
  if (!toolCalls || toolCalls.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <div className="text-xs font-semibold text-gray-600 flex items-center gap-1">
        <Sparkles className="w-3 h-3" />
        Tools Used ({toolCalls.length})
      </div>
      <div className="flex flex-wrap gap-2">
        {toolCalls.map((tool, idx) => (
          <ToolCallChip key={idx} tool={tool} expandable={true} />
        ))}
      </div>
    </div>
  );
}
