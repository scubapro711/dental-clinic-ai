import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle2, XCircle, Clock, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { dashboardService, Decision } from '@/services/dashboardService';

interface DecisionQueueWidgetProps {
  onChatWithAgent?: (message: string) => void;
}

/**
 * Decision Queue Widget - System
 * 
 * Shows items that need doctor's decision/approval
 * Organized by priority from all agents
 */
export default function DecisionQueueWidget({ onChatWithAgent }: DecisionQueueWidgetProps) {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusMessage, setStatusMessage] = useState('');

  useEffect(() => {
    fetchDecisions();
  }, []);

  const fetchDecisions = async () => {
    setIsLoading(true);
    try {
      const orgId = localStorage.getItem('current_organization_id') || 
                    localStorage.getItem('organization_id') || 
                    '1';
      
      const data = await dashboardService.getDecisionQueue(orgId);
      setDecisions(data);
    } catch (error) {
      console.error('Error fetching decisions:', error);
      setDecisions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getPriorityConfig = (priority: Decision['priority']) => {
    const configs = {
      high: {
        icon: <AlertCircle className="w-4 h-4" />,
        color: 'text-red-600 bg-red-100',
        label: 'דחוף'
      },
      medium: {
        icon: <Clock className="w-4 h-4" />,
        color: 'text-orange-600 bg-orange-100',
        label: 'בינוני'
      },
      low: {
        icon: <ChevronRight className="w-4 h-4" />,
        color: 'text-blue-600 bg-blue-100',
        label: 'נמוך'
      }
    };
    return configs[priority] || configs.medium;
  };

  const getAgentColor = (agent: string) => {
    const colors: Record<string, string> = {
      alex: 'bg-purple-100 text-purple-700',
      sarah: 'bg-pink-100 text-pink-700',
      marcus: 'bg-green-100 text-green-700',
      sophia: 'bg-blue-100 text-blue-700',
      harper: 'bg-gray-100 text-gray-700'
    };
    return colors[agent] || 'bg-gray-100 text-gray-700';
  };

  const formatTimeAgo = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - new Date(timestamp).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `לפני ${days} ימים`;
    if (hours > 0) return `לפני ${hours} שעות`;
    return 'עכשיו';
  };

  const handleApprove = async (decision: Decision) => {
    setStatusMessage('מאשר...');
    try {
      await dashboardService.approveDecision(decision.id);
      setStatusMessage('אושר בהצלחה!');
      // Refresh decisions
      await fetchDecisions();
      setTimeout(() => setStatusMessage(''), 2000);
    } catch (error) {
      console.error('Error approving decision:', error);
      setStatusMessage('שגיאה באישור');
      setTimeout(() => setStatusMessage(''), 2000);
    }
  };

  const handleReject = async (decision: Decision) => {
    setStatusMessage('דוחה...');
    try {
      await dashboardService.rejectDecision(decision.id);
      setStatusMessage('נדחה בהצלחה!');
      // Refresh decisions
      await fetchDecisions();
      setTimeout(() => setStatusMessage(''), 2000);
    } catch (error) {
      console.error('Error rejecting decision:', error);
      setStatusMessage('שגיאה בדחייה');
      setTimeout(() => setStatusMessage(''), 2000);
    }
  };

  const handleChatClick = (decision: Decision) => {
    if (onChatWithAgent) {
      onChatWithAgent(`Tell me more about: ${decision.title}`);
    }
  };

  return (
    <BaseWidget
      title="תור החלטות"
      agent="system"
      icon="⚡"
      badge={`${decisions.length} ממתינים`}
      isLoading={isLoading}
    >
      {statusMessage && (
        <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700 text-center">
          {statusMessage}
        </div>
      )}
      
      <div className="space-y-3">
        {decisions.length === 0 ? (
          <div className="text-center text-sm text-gray-500 py-4">
            אין החלטות ממתינות
          </div>
        ) : (
          decisions.map((decision) => {
            const priorityConfig = getPriorityConfig(decision.priority);
            
            return (
              <div
                key={decision.id}
                className={cn(
                  'rounded-lg border-2 p-3 transition-all duration-200',
                  'hover:shadow-md',
                  decision.priority === 'high' ? 'border-red-200 bg-red-50' :
                  decision.priority === 'medium' ? 'border-orange-200 bg-orange-50' :
                  'border-blue-200 bg-blue-50'
                )}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className={cn('text-xs', getAgentColor(decision.agent))}>
                        {decision.agent.toUpperCase()}
                      </Badge>
                      <Badge className={cn('text-xs flex items-center gap-1', priorityConfig.color)}>
                        {priorityConfig.icon}
                        {priorityConfig.label}
                      </Badge>
                    </div>
                    <h4 className="font-semibold text-sm">{decision.title}</h4>
                    <p className="text-xs text-gray-600 mt-1">{decision.description}</p>
                    <div className="text-xs text-gray-500 mt-1">
                      {formatTimeAgo(decision.timestamp)}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 mt-3">
                  <Button
                    size="sm"
                    className="flex-1 text-xs h-7 bg-green-600 hover:bg-green-700"
                    onClick={() => handleApprove(decision)}
                  >
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    {decision.action}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 text-xs h-7"
                    onClick={() => handleReject(decision)}
                  >
                    <XCircle className="w-3 h-3 mr-1" />
                    דחה
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs h-7 px-2"
                    onClick={() => handleChatClick(decision)}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Action */}
      {decisions.length > 0 && (
        <div className="mt-4 pt-3 border-t">
          <Button
            variant="ghost"
            className="w-full text-xs"
            onClick={() => onChatWithAgent && onChatWithAgent('Show me all pending decisions')}
          >
            הצג את כל ההחלטות הממתינות
          </Button>
        </div>
      )}
    </BaseWidget>
  );
}
