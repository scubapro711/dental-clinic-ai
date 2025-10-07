import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle2, XCircle, Clock, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Decision Queue Widget - System
 * 
 * Shows items that need doctor's decision/approval
 * Organized by priority from all agents
 */
export default function DecisionQueueWidget({ onChatWithAgent }) {
  const [decisions, setDecisions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDecisions();
  }, []);

  const fetchDecisions = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with real API call
      // const response = await fetch('http://localhost:8000/api/v1/decisions/queue');
      // const data = await response.json();
      
      // Mock data for now
      const mockData = [
        {
          id: 1,
          priority: 'high',
          agent: 'alex',
          title: '3 מטופלים ממתינים לאישור תור',
          description: 'Alex זיהה 3 מטופלים שלא אישרו תור - צריך להתקשר',
          action: 'התקשר למטופלים',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
        },
        {
          id: 2,
          priority: 'medium',
          agent: 'marcus',
          title: '₪5,000 חובות לא נגבו',
          description: 'Marcus מצא 5 חשבונות פתוחים מעל 30 יום - צריך להחליט על תזכורות',
          action: 'שלח תזכורות',
          timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000) // 5 hours ago
        },
        {
          id: 3,
          priority: 'low',
          agent: 'sophia',
          title: 'קונפליקט בלוח הזמנים',
          description: 'Sophia מצאה חפיפה בין 2 תורים ביום חמישי - צריך לבחור מי לשנות',
          action: 'פתור קונפליקט',
          timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000) // 1 day ago
        },
        {
          id: 4,
          priority: 'medium',
          agent: 'alex',
          title: 'מטופל חדש עם היסטוריה רפואית מורכבת',
          description: 'Alex ממליץ לקרוא את ההיסטוריה לפני הביקור הראשון מחר',
          action: 'סקור היסטוריה',
          timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000) // 3 hours ago
        }
      ];
      
      // Sort by priority
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      mockData.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
      
      setDecisions(mockData);
    } catch (error) {
      console.error('Error fetching decisions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getPriorityConfig = (priority) => {
    const configs = {
      high: {
        icon: <AlertCircle className="w-4 h-4" />,
        color: 'text-red-600 bg-red-100 border-red-300',
        label: 'דחוף',
        badgeColor: 'bg-red-500'
      },
      medium: {
        icon: <Clock className="w-4 h-4" />,
        color: 'text-orange-600 bg-orange-100 border-orange-300',
        label: 'בינוני',
        badgeColor: 'bg-orange-500'
      },
      low: {
        icon: <CheckCircle2 className="w-4 h-4" />,
        color: 'text-blue-600 bg-blue-100 border-blue-300',
        label: 'נמוך',
        badgeColor: 'bg-blue-500'
      }
    };
    return configs[priority] || configs.medium;
  };

  const getAgentConfig = (agent) => {
    const configs = {
      alex: { name: 'Alex', emoji: '👨‍⚕️', color: 'text-blue-600' },
      marcus: { name: 'Marcus', emoji: '💼', color: 'text-green-600' },
      sophia: { name: 'Sophia', emoji: '📋', color: 'text-purple-600' }
    };
    return configs[agent] || { name: 'System', emoji: '🤖', color: 'text-gray-600' };
  };

  const getTimeAgo = (timestamp) => {
    const seconds = Math.floor((new Date() - timestamp) / 1000);
    
    if (seconds < 60) return 'עכשיו';
    if (seconds < 3600) return `לפני ${Math.floor(seconds / 60)} דקות`;
    if (seconds < 86400) return `לפני ${Math.floor(seconds / 3600)} שעות`;
    return `לפני ${Math.floor(seconds / 86400)} ימים`;
  };

  const handleApprove = (decision) => {
    console.log('Approved:', decision);
    // TODO: Implement approval logic
  };

  const handleReject = (decision) => {
    console.log('Rejected:', decision);
    // TODO: Implement rejection logic
  };

  const handleChatAbout = (decision) => {
    const agentConfig = getAgentConfig(decision.agent);
    if (onChatWithAgent) {
      onChatWithAgent(`${agentConfig.name}, tell me more about: ${decision.title}`);
    }
  };

  const highPriorityCount = decisions.filter(d => d.priority === 'high').length;

  return (
    <BaseWidget
      title="החלטות ממתינות"
      agent="system"
      icon="⚡"
      badge={highPriorityCount > 0 ? `${highPriorityCount} דחופות` : `${decisions.length} פריטים`}
      isLoading={isLoading}
    >
      <div className="space-y-3">
        {decisions.length === 0 ? (
          <div className="text-center text-sm text-gray-500 py-8">
            <CheckCircle2 className="w-12 h-12 mx-auto mb-2 text-green-500" />
            <div>אין החלטות ממתינות</div>
            <div className="text-xs mt-1">כל המשימות טופלו! 🎉</div>
          </div>
        ) : (
          decisions.map((decision) => {
            const priorityConfig = getPriorityConfig(decision.priority);
            const agentConfig = getAgentConfig(decision.agent);
            
            return (
              <div
                key={decision.id}
                className={cn(
                  'rounded-lg border-2 p-3 transition-all duration-200',
                  'hover:shadow-md',
                  priorityConfig.color
                )}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Badge className={cn('text-xs flex items-center gap-1', priorityConfig.color)}>
                      {priorityConfig.icon}
                      {priorityConfig.label}
                    </Badge>
                    <span className={cn('text-xs font-semibold', agentConfig.color)}>
                      {agentConfig.emoji} {agentConfig.name}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {getTimeAgo(decision.timestamp)}
                  </span>
                </div>

                {/* Content */}
                <div className="mb-3">
                  <div className="font-semibold text-sm mb-1">
                    {decision.title}
                  </div>
                  <div className="text-xs text-gray-700">
                    {decision.description}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
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
                    className="text-xs h-7"
                    onClick={() => handleChatAbout(decision)}
                  >
                    <ChevronRight className="w-3 h-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs h-7 text-red-600 hover:text-red-700"
                    onClick={() => handleReject(decision)}
                  >
                    <XCircle className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      {decisions.length > 0 && (
        <div className="mt-4 pt-3 border-t">
          <div className="text-xs text-gray-600 text-center">
            💡 הסוכנים מארגנים עבורך את המשימות החשובות ביותר
          </div>
        </div>
      )}
    </BaseWidget>
  );
}
