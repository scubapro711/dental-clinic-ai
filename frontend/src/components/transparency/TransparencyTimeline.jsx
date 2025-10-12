import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  Loader2,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Minimize2,
  Play,
  Pause
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Enhanced Transparency Timeline Component
 * 
 * Features:
 * - Vertical timeline view
 * - Real-time updates
 * - Expandable steps
 * - Confidence scores
 * - Duration tracking
 * - Pause/Resume
 * - Full-screen mode
 */
export default function TransparencyTimeline({ steps, isLive = false }) {
  const [expandedSteps, setExpandedSteps] = useState(new Set());
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const timelineEndRef = useRef(null);

  // Auto-scroll to latest step
  useEffect(() => {
    if (autoScroll && !isPaused && timelineEndRef.current) {
      timelineEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [steps, autoScroll, isPaused]);

  const toggleStep = (index) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSteps(newExpanded);
  };

  const toggleAllSteps = () => {
    if (expandedSteps.size === steps.length) {
      setExpandedSteps(new Set());
    } else {
      setExpandedSteps(new Set(steps.map((_, i) => i)));
    }
  };

  if (!steps || steps.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader className="border-b">
          <CardTitle className="text-sm flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-600" />
            Timeline
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center text-sm text-gray-500">
            <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
              <Clock className="w-6 h-6 text-gray-400" />
            </div>
            <p>אין פעילות עדיין</p>
            <p className="text-xs mt-1">Timeline יופיע כאן כשהסוכנים יתחילו לעבוד</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn(
      'flex flex-col transition-all duration-300',
      isFullscreen ? 'fixed inset-4 z-50' : 'h-full'
    )}>
      <CardHeader className="border-b flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-600" />
            Timeline
            {isLive && (
              <Badge variant="destructive" className="text-xs animate-pulse">
                <span className="w-2 h-2 rounded-full bg-white mr-1" />
                LIVE
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setIsPaused(!isPaused)}
              className="h-7 px-2"
            >
              {isPaused ? (
                <Play className="w-3 h-3" />
              ) : (
                <Pause className="w-3 h-3" />
              )}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={toggleAllSteps}
              className="h-7 px-2 text-xs"
            >
              {expandedSteps.size === steps.length ? (
                <>
                  <ChevronUp className="w-3 h-3 mr-1" />
                  Collapse All
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3 mr-1" />
                  Expand All
                </>
              )}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="h-7 px-2"
            >
              {isFullscreen ? (
                <Minimize2 className="w-3 h-3" />
              ) : (
                <Maximize2 className="w-3 h-3" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto p-4">
        <div className="relative">
          {/* Vertical timeline line */}
          <div className="absolute right-6 top-0 bottom-0 w-0.5 bg-gray-200" />
          
          {/* Timeline steps */}
          <div className="space-y-4">
            {steps.map((step, index) => (
              <TimelineStep
                key={index}
                step={step}
                index={index}
                isExpanded={expandedSteps.has(index)}
                onToggle={() => toggleStep(index)}
                isLast={index === steps.length - 1}
              />
            ))}
          </div>
          
          {/* Auto-scroll anchor */}
          <div ref={timelineEndRef} />
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Individual Timeline Step
 */
function TimelineStep({ step, index, isExpanded, onToggle, isLast }) {
  const { type, agent, text, data, status, timestamp, confidence, duration } = step;

  // Agent configuration
  const agentConfig = {
    alex: { name: 'Alex', color: 'blue', icon: '👨‍⚕️', bgColor: 'bg-blue-50' },
    marcus: { name: 'Marcus', color: 'green', icon: '💼', bgColor: 'bg-green-50' },
    sophia: { name: 'Sophia', color: 'purple', icon: '📋', bgColor: 'bg-purple-50' },
    supervisor: { name: 'Supervisor', color: 'gray', icon: '🎯', bgColor: 'bg-gray-50' }
  };

  const config = agentConfig[agent] || agentConfig.supervisor;

  // Status icon
  const statusIcon = {
    success: <CheckCircle2 className="w-5 h-5 text-green-600" />,
    error: <AlertCircle className="w-5 h-5 text-red-600" />,
    running: <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />,
    pending: <Clock className="w-5 h-5 text-gray-400" />
  }[status] || <Clock className="w-5 h-5 text-gray-400" />;

  // Format timestamp
  const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString('he-IL', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }) : '';

  return (
    <div className="relative flex gap-4">
      {/* Timeline node */}
      <div className="flex-shrink-0 relative z-10">
        <div className={cn(
          'w-12 h-12 rounded-full flex items-center justify-center',
          'border-4 border-white shadow-md',
          config.bgColor
        )}>
          {statusIcon}
        </div>
        {!isLast && (
          <div className="absolute top-12 left-1/2 -translate-x-1/2 w-0.5 h-4 bg-gray-200" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 pb-4">
        <div
          className={cn(
            'rounded-lg border-2 p-3 cursor-pointer transition-all duration-200',
            'hover:shadow-md',
            config.bgColor,
            isExpanded && 'shadow-lg'
          )}
          onClick={onToggle}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-lg">{config.icon}</span>
              <div>
                <div className="font-semibold text-sm">{config.name}</div>
                <div className="text-xs text-gray-600">{timeStr}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {confidence !== undefined && (
                <Badge variant="secondary" className="text-xs">
                  {(confidence * 100).toFixed(0)}% confidence
                </Badge>
              )}
              {duration !== undefined && (
                <Badge variant="outline" className="text-xs">
                  {duration}ms
                </Badge>
              )}
              {isExpanded ? (
                <ChevronUp className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              )}
            </div>
          </div>

          {/* Text */}
          <p className="text-sm text-gray-700 leading-relaxed mb-2">
            {text}
          </p>

          {/* Expanded content */}
          {isExpanded && data && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="text-xs font-semibold text-gray-600 mb-2">
                נתונים מפורטים:
              </div>
              <div className="bg-white rounded-lg p-3 text-xs font-mono text-gray-700 max-h-64 overflow-y-auto">
                <pre className="whitespace-pre-wrap">
                  {typeof data === 'string' ? data : JSON.stringify(data, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Progress bar for running steps */}
          {status === 'running' && (
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-1 overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: '60%' }} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
