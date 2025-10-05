import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Brain, Eye, CheckCircle2, AlertCircle, Clock, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Full Transparency Panel - Shows agent reasoning in simple human language
 * 
 * Displays:
 * - What the agent read
 * - How it understood the request
 * - What it decided to do
 * - Which tools it used
 * - What data it found
 * - How it analyzed
 * - Why it reached this conclusion
 * - Any errors or issues
 */
export default function FullTransparencyPanel({ steps }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!steps || steps.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader className="border-b">
          <CardTitle className="text-sm flex items-center gap-2">
            <Eye className="w-4 h-4 text-purple-600" />
            שקיפות מלאה
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center text-sm text-gray-500">
            <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
              <Brain className="w-6 h-6 text-gray-400" />
            </div>
            <p>אין פעילות כרגע</p>
            <p className="text-xs mt-1">שלח הודעה כדי לראות את תהליך החשיבה</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <Eye className="w-4 h-4 text-purple-600" />
            שקיפות מלאה - תהליך החשיבה
          </CardTitle>
          <Badge variant="secondary" className="text-xs">
            {steps.length} שלבים
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3">
          {steps.map((step, index) => (
            <ReasoningStep key={index} step={step} index={index} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Individual reasoning step component
 */
function ReasoningStep({ step, index }) {
  const { type, agent, text, data, status, timestamp } = step;

  // Agent configuration
  const agentConfig = {
    alex: { name: 'אלכס', color: 'blue', icon: '👨‍⚕️' },
    cfo: { name: 'מרקוס', color: 'green', icon: '💼' },
    admin: { name: 'סופיה', color: 'purple', icon: '📋' },
    supervisor: { name: 'מתאם', color: 'gray', icon: '🎯' }
  };

  const config = agentConfig[agent] || agentConfig.supervisor;

  // Step type configuration
  const stepConfig = {
    read: { icon: '📖', label: 'קורא', color: 'bg-blue-50 border-blue-200' },
    understand: { icon: '💡', label: 'מבין', color: 'bg-yellow-50 border-yellow-200' },
    decide: { icon: '🤔', label: 'מחליט', color: 'bg-purple-50 border-purple-200' },
    tool_use: { icon: '🔧', label: 'משתמש בכלי', color: 'bg-orange-50 border-orange-200' },
    data_found: { icon: '📊', label: 'מצא נתונים', color: 'bg-green-50 border-green-200' },
    analyze: { icon: '🔍', label: 'מנתח', color: 'bg-indigo-50 border-indigo-200' },
    conclude: { icon: '✅', label: 'מסכם', color: 'bg-teal-50 border-teal-200' },
    error: { icon: '⚠️', label: 'בעיה', color: 'bg-red-50 border-red-200' }
  };

  const stepStyle = stepConfig[type] || stepConfig.decide;

  return (
    <div className={cn(
      'rounded-lg border-2 p-3',
      stepStyle.color,
      'transition-all duration-200 hover:shadow-md'
    )}>
      {/* Header */}
      <div className="flex items-start gap-2 mb-2">
        <div className="flex-shrink-0 mt-0.5">
          <span className="text-lg">{config.icon}</span>
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-semibold text-sm">
              {config.name} {stepStyle.label}:
            </span>
            <Badge variant="secondary" className="text-xs">
              שלב {index + 1}
            </Badge>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">
            {text}
          </p>
        </div>
        <div className="flex-shrink-0">
          <span className="text-xl">{stepStyle.icon}</span>
        </div>
      </div>

      {/* Data section (if available) */}
      {data && (
        <div className="mt-2 pt-2 border-t border-gray-200">
          <div className="text-xs font-semibold text-gray-600 mb-1">נתונים:</div>
          <div className="bg-white rounded p-2 text-xs font-mono text-gray-700 max-h-32 overflow-y-auto">
            {typeof data === 'string' ? data : JSON.stringify(data, null, 2)}
          </div>
        </div>
      )}

      {/* Status indicator */}
      {status && (
        <div className="mt-2 flex items-center gap-1 text-xs">
          {status === 'success' && (
            <>
              <CheckCircle2 className="w-3 h-3 text-green-600" />
              <span className="text-green-600">הושלם בהצלחה</span>
            </>
          )}
          {status === 'error' && (
            <>
              <AlertCircle className="w-3 h-3 text-red-600" />
              <span className="text-red-600">נכשל</span>
            </>
          )}
          {status === 'running' && (
            <>
              <Clock className="w-3 h-3 text-blue-600 animate-spin" />
              <span className="text-blue-600">בתהליך...</span>
            </>
          )}
        </div>
      )}

      {/* Timestamp */}
      {timestamp && (
        <div className="mt-1 text-xs text-gray-500 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {new Date(timestamp).toLocaleTimeString('he-IL')}
        </div>
      )}
    </div>
  );
}

/**
 * Hook to convert LangGraph events to reasoning steps
 */
export function useReasoningSteps() {
  const [steps, setSteps] = useState([]);

  const addStep = (step) => {
    setSteps(prev => [...prev, { ...step, timestamp: Date.now() }]);
  };

  const clearSteps = () => {
    setSteps([]);
  };

  // Convert stream events to reasoning steps
  const handleStreamEvent = (event) => {
    const { type, agent, tool_name, tool_input, tool_output, content } = event;

    switch (type) {
      case 'agent_start':
        addStep({
          type: 'read',
          agent: agent,
          text: `קורא את השאלה ומנסה להבין מה נדרש`,
          status: 'running'
        });
        break;

      case 'tool_start':
        // Translate tool name to human language
        const toolTranslations = {
          'get_revenue_overview_tool': 'בודק את נתוני ההכנסות במערכת הפיננסית',
          'get_patient_info': 'מחפש מידע על המטופל במאגר',
          'get_appointments': 'בודק את התורים במערכת',
          'search_patients': 'מחפש מטופלים במאגר',
          'get_today_schedule': 'מביא את לוח הזמנים של היום'
        };

        const toolText = toolTranslations[tool_name] || `משתמש בכלי: ${tool_name}`;

        addStep({
          type: 'tool_use',
          agent: agent,
          text: toolText,
          data: tool_input,
          status: 'running'
        });
        break;

      case 'tool_complete':
        addStep({
          type: 'data_found',
          agent: agent,
          text: `מצא נתונים ומתחיל לנתח אותם`,
          data: tool_output,
          status: 'success'
        });

        // Add analysis step
        addStep({
          type: 'analyze',
          agent: agent,
          text: `מנתח את הנתונים ומחפש תובנות חשובות`,
          status: 'running'
        });
        break;

      case 'text':
        // When we get the final text, add conclude step
        if (content && content.length > 10) {
          addStep({
            type: 'conclude',
            agent: agent,
            text: `מסכם את הממצאים ומכין תשובה מקצועית`,
            status: 'success'
          });
        }
        break;

      case 'agent_complete':
        addStep({
          type: 'conclude',
          agent: agent,
          text: `סיים את הניתוח ומוכן לענות`,
          status: 'success'
        });
        break;

      case 'error':
        addStep({
          type: 'error',
          agent: agent,
          text: `נתקל בבעיה: ${event.error || 'שגיאה לא ידועה'}`,
          status: 'error'
        });
        break;
    }
  };

  return {
    steps,
    addStep,
    clearSteps,
    handleStreamEvent
  };
}
