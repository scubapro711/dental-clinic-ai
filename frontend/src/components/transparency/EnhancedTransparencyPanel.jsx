import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Brain, Eye, CheckCircle2, AlertCircle, Clock, Sparkles, 
  ChevronDown, ChevronRight, Maximize2, Minimize2, Play, Pause 
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Enhanced Transparency Panel - Advanced agent reasoning visualization
 * 
 * Features:
 * - Timeline view of agent thinking process
 * - Expandable/collapsible steps
 * - Real-time updates with animations
 * - Agent confidence scores
 * - Tool call details with input/output
 * - Performance metrics (duration, success rate)
 * - Playback controls (pause/resume)
 * - Full-screen mode
 * - Export reasoning log
 */
export default function EnhancedTransparencyPanel({ 
  reasoningSteps = [],
  isActive = false,
  onClear,
  onExport,
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [selectedStep, setSelectedStep] = useState(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const contentRef = useRef(null);
  
  // Auto-scroll to bottom when new steps are added
  useEffect(() => {
    if (autoScroll && contentRef.current && !isPaused) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [reasoningSteps, autoScroll, isPaused]);
  
  // Calculate statistics
  const stats = calculateStats(reasoningSteps);
  
  if (reasoningSteps.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader className="border-b">
          <CardTitle className="text-sm flex items-center gap-2">
            <Eye className="w-4 h-4 text-purple-600" />
            Enhanced Transparency
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <EmptyState />
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className={cn(
      'flex flex-col transition-all duration-300',
      isFullscreen ? 'fixed inset-4 z-50' : 'h-full'
    )}>
      {/* Header */}
      <CardHeader className="border-b flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-purple-600" />
            <CardTitle className="text-sm">Enhanced Transparency</CardTitle>
            {isActive && (
              <Badge variant="secondary" className="text-xs animate-pulse">
                <Sparkles className="w-3 h-3 mr-1" />
                Live
              </Badge>
            )}
          </div>
          
          <div className="flex items-center gap-1">
            {/* Stats Badge */}
            <Badge variant="outline" className="text-xs">
              {reasoningSteps.length} steps • {stats.duration}s
            </Badge>
            
            {/* Pause/Resume */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsPaused(!isPaused)}
              className="h-7 w-7 p-0"
            >
              {isPaused ? (
                <Play className="w-3 h-3" />
              ) : (
                <Pause className="w-3 h-3" />
              )}
            </Button>
            
            {/* Fullscreen Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="h-7 w-7 p-0"
            >
              {isFullscreen ? (
                <Minimize2 className="w-3 h-3" />
              ) : (
                <Maximize2 className="w-3 h-3" />
              )}
            </Button>
          </div>
        </div>
        
        {/* Performance Stats */}
        <div className="flex items-center gap-4 mt-2 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-green-600" />
            <span>{stats.successCount} success</span>
          </div>
          {stats.errorCount > 0 && (
            <div className="flex items-center gap-1">
              <AlertCircle className="w-3 h-3 text-red-600" />
              <span>{stats.errorCount} errors</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>Avg: {stats.avgDuration}s/step</span>
          </div>
        </div>
      </CardHeader>
      
      {/* Timeline Content */}
      <CardContent 
        ref={contentRef}
        className="flex-1 overflow-y-auto p-4 space-y-2"
      >
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-200 via-blue-200 to-green-200" />
          
          {/* Reasoning Steps */}
          {reasoningSteps.map((step, index) => (
            <TimelineStep
              key={index}
              step={step}
              index={index}
              isSelected={selectedStep === index}
              onSelect={() => setSelectedStep(selectedStep === index ? null : index)}
              isLast={index === reasoningSteps.length - 1}
            />
          ))}
        </div>
      </CardContent>
      
      {/* Footer Actions */}
      <div className="border-t p-3 flex-shrink-0 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1 text-xs text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded"
            />
            Auto-scroll
          </label>
        </div>
        
        <div className="flex items-center gap-2">
          {onExport && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExport(reasoningSteps)}
              className="text-xs"
            >
              Export Log
            </Button>
          )}
          {onClear && (
            <Button
              variant="outline"
              size="sm"
              onClick={onClear}
              className="text-xs"
            >
              Clear
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}

/**
 * Timeline Step Component
 */
function TimelineStep({ step, index, isSelected, onSelect, isLast }) {
  const { type, agent, text, data, status, timestamp, confidence, duration } = step;
  
  // Agent configuration
  const agentConfig = {
    alex: { name: 'Alex', color: 'blue', icon: '👨‍⚕️', bgColor: 'bg-blue-50', borderColor: 'border-blue-300' },
    marcus: { name: 'Marcus', color: 'green', icon: '💼', bgColor: 'bg-green-50', borderColor: 'border-green-300' },
    sarah: { name: 'Sarah', color: 'purple', icon: '🩺', bgColor: 'bg-purple-50', borderColor: 'border-purple-300' },
    sophia: { name: 'Sophia', color: 'pink', icon: '📋', bgColor: 'bg-pink-50', borderColor: 'border-pink-300' },
    supervisor: { name: 'Supervisor', color: 'gray', icon: '🎯', bgColor: 'bg-gray-50', borderColor: 'border-gray-300' },
  };
  
  const config = agentConfig[agent?.toLowerCase()] || agentConfig.supervisor;
  
  // Step type configuration
  const stepConfig = {
    read: { icon: '📖', label: 'Reading', color: 'bg-blue-100' },
    understand: { icon: '💡', label: 'Understanding', color: 'bg-yellow-100' },
    decide: { icon: '🤔', label: 'Deciding', color: 'bg-purple-100' },
    tool_use: { icon: '🔧', label: 'Using Tool', color: 'bg-orange-100' },
    data_found: { icon: '📊', label: 'Data Found', color: 'bg-green-100' },
    analyze: { icon: '🔍', label: 'Analyzing', color: 'bg-indigo-100' },
    conclude: { icon: '✅', label: 'Concluding', color: 'bg-teal-100' },
    error: { icon: '⚠️', label: 'Error', color: 'bg-red-100' },
  };
  
  const stepStyle = stepConfig[type] || stepConfig.decide;
  
  // Format timestamp
  const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }) : '';
  
  return (
    <div className="relative pl-14 pb-4">
      {/* Timeline Node */}
      <div className={cn(
        'absolute left-4 top-2 w-5 h-5 rounded-full border-2 flex items-center justify-center',
        config.bgColor,
        config.borderColor,
        isLast && 'animate-pulse'
      )}>
        <span className="text-xs">{config.icon}</span>
      </div>
      
      {/* Step Card */}
      <div
        className={cn(
          'rounded-lg border-2 p-3 cursor-pointer transition-all duration-200',
          config.bgColor,
          config.borderColor,
          isSelected && 'ring-2 ring-purple-400 shadow-lg',
          'hover:shadow-md'
        )}
        onClick={onSelect}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2 flex-1">
            <span className="text-lg">{stepStyle.icon}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">
                  {config.name}
                </span>
                <Badge variant="secondary" className="text-xs">
                  {stepStyle.label}
                </Badge>
                {confidence && (
                  <Badge 
                    variant="outline" 
                    className={cn(
                      'text-xs',
                      confidence >= 90 && 'bg-green-50 border-green-300',
                      confidence >= 70 && confidence < 90 && 'bg-yellow-50 border-yellow-300',
                      confidence < 70 && 'bg-red-50 border-red-300'
                    )}
                  >
                    {confidence}% confident
                  </Badge>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              {duration && (
                <span>{duration}s</span>
              )}
              <Clock className="w-3 h-3" />
              <span>{timeStr}</span>
            </div>
          </div>
          
          {data && (
            isSelected ? (
              <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
            )
          )}
        </div>
        
        {/* Text */}
        <p className="text-sm text-gray-700 leading-relaxed mb-2">
          {text}
        </p>
        
        {/* Data (expandable) */}
        {data && isSelected && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="text-xs font-semibold text-gray-600 mb-2">
              Details:
            </div>
            <div className="bg-white rounded-md p-3 text-xs font-mono text-gray-700 max-h-64 overflow-y-auto">
              <pre className="whitespace-pre-wrap">
                {typeof data === 'string' ? data : JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        )}
        
        {/* Status */}
        {status && (
          <div className="mt-2 flex items-center gap-1 text-xs">
            {status === 'success' && (
              <>
                <CheckCircle2 className="w-3 h-3 text-green-600" />
                <span className="text-green-600 font-medium">Success</span>
              </>
            )}
            {status === 'error' && (
              <>
                <AlertCircle className="w-3 h-3 text-red-600" />
                <span className="text-red-600 font-medium">Error</span>
              </>
            )}
            {status === 'running' && (
              <>
                <Clock className="w-3 h-3 text-blue-600 animate-spin" />
                <span className="text-blue-600 font-medium">Running...</span>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Empty State Component
 */
function EmptyState() {
  return (
    <div className="text-center text-sm text-gray-500">
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center mx-auto mb-4">
        <Brain className="w-8 h-8 text-purple-600" />
      </div>
      <p className="font-semibold text-gray-700 mb-1">No Agent Activity</p>
      <p className="text-xs">
        Start a conversation to see the agent's thinking process in real-time
      </p>
      <div className="mt-4 p-3 bg-blue-50 rounded-lg text-left">
        <p className="text-xs font-semibold text-blue-900 mb-2">
          What you'll see here:
        </p>
        <ul className="text-xs text-blue-800 space-y-1">
          <li>• Step-by-step reasoning process</li>
          <li>• Tool calls with input/output</li>
          <li>• Confidence scores for decisions</li>
          <li>• Performance metrics and timing</li>
          <li>• Real-time updates as agents think</li>
        </ul>
      </div>
    </div>
  );
}

/**
 * Calculate statistics from reasoning steps
 */
function calculateStats(steps) {
  if (steps.length === 0) {
    return {
      duration: 0,
      successCount: 0,
      errorCount: 0,
      avgDuration: 0,
    };
  }
  
  const successCount = steps.filter(s => s.status === 'success').length;
  const errorCount = steps.filter(s => s.status === 'error').length;
  
  const durations = steps
    .filter(s => s.duration)
    .map(s => s.duration);
  
  const totalDuration = durations.reduce((sum, d) => sum + d, 0);
  const avgDuration = durations.length > 0 
    ? (totalDuration / durations.length).toFixed(1)
    : 0;
  
  // Calculate total duration from first to last timestamp
  const timestamps = steps
    .filter(s => s.timestamp)
    .map(s => s.timestamp);
  
  const duration = timestamps.length > 0
    ? ((Math.max(...timestamps) - Math.min(...timestamps)) / 1000).toFixed(1)
    : 0;
  
  return {
    duration,
    successCount,
    errorCount,
    avgDuration,
  };
}

/**
 * Export reasoning steps to JSON
 */
export function exportReasoningLog(steps) {
  const log = {
    exportDate: new Date().toISOString(),
    totalSteps: steps.length,
    steps: steps.map((step, index) => ({
      stepNumber: index + 1,
      ...step,
    })),
  };
  
  const blob = new Blob([JSON.stringify(log, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `reasoning-log-${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

