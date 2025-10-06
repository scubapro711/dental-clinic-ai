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
 * Connected to real OdooClient API
 */
export default function DecisionQueueWidget({ onChatWithAgent }) {
  const [decisions, setDecisions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDecisions();
    
    // Refresh every 2 minutes
    const interval = setInterval(fetchDecisions, 2 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchDecisions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/dashboard/widgets/decisions/queue', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setDecisions(data);
    } catch (error) {
      console.error('Error fetching decisions:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getPriorityConfig = (priority) => {
    const configs = {
      high: {
        badge: 'destructive',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        icon: AlertCircle,
        iconColor: 'text-red-600',
        text: 'דחוף'
      },
      medium: {
        badge: 'default',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        icon: Clock,
        iconColor: 'text-yellow-600',
        text: 'בינוני'
      },
      low: {
        badge: 'secondary',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
        icon: CheckCircle2,
        iconColor: 'text-gray-600',
        text: 'נמוך'
      }
    };
    return configs[priority] || configs.low;
  };

  const getAgentIcon = (agent) => {
    const icons = {
      alex: '👨‍⚕️',
      marcus: '💼',
      sophia: '📋'
    };
    return icons[agent] || '🤖';
  };

  const getAgentName = (agent) => {
    const names = {
      alex: 'Alex',
      marcus: 'Marcus',
      sophia: 'Sophia'
    };
    return names[agent] || agent;
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = Math.floor((now - time) / 1000); // seconds
    
    if (diff < 60) return 'לפני רגע';
    if (diff < 3600) return `לפני ${Math.floor(diff / 60)} דקות`;
    if (diff < 86400) return `לפני ${Math.floor(diff / 3600)} שעות`;
    return `לפני ${Math.floor(diff / 86400)} ימים`;
  };

  const handleAction = (decision) => {
    if (onChatWithAgent) {
      onChatWithAgent(decision.action);
    }
  };

  const urgentCount = decisions.filter(d => d.priority === 'high').length;

  if (error) {
    return (
      <BaseWidget
        title="החלטות ממתינות"
        subtitle="שגיאה בטעינת נתונים"
        icon={AlertCircle}
      >
        <div className="text-center py-4">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-2" />
          <p className="text-sm text-gray-600">{error}</p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchDecisions}
            className="mt-2"
          >
            נסה שוב
          </Button>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget
      title="החלטות ממתינות"
      subtitle={urgentCount > 0 ? `${urgentCount} דחופות` : `${decisions.length} פריטים`}
      icon={AlertCircle}
      isLoading={isLoading}
    >
      <div className="space-y-3">
        {decisions.map((decision) => {
          const config = getPriorityConfig(decision.priority);
          const Icon = config.icon;
          
          return (
            <div
              key={decision.id}
              className={cn(
                "p-3 rounded-lg border transition-all hover:shadow-md",
                config.bgColor,
                config.borderColor
              )}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-2">
                <Badge variant={config.badge} className="flex items-center gap-1">
                  <Icon className={cn("w-3 h-3", config.iconColor)} />
                  <span>{config.text}</span>
                </Badge>
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <span>{getAgentIcon(decision.agent)}</span>
                  <span>{getAgentName(decision.agent)}</span>
                </div>
              </div>

              {/* Content */}
              <div className="mb-2">
                <div className="font-semibold text-gray-900 mb-1">
                  {decision.title}
                </div>
                <div className="text-sm text-gray-600">
                  {decision.description}
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {formatTimeAgo(decision.timestamp)}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleAction(decision)}
                  className="flex items-center gap-1"
                >
                  {decision.action}
                  <ChevronRight className="w-3 h-3" />
                </Button>
              </div>
            </div>
          );
        })}

        {decisions.length === 0 && !isLoading && (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle2 className="w-12 h-12 mx-auto mb-2 opacity-50 text-green-500" />
            <p>כל ההחלטות טופלו! 🎉</p>
            <p className="text-xs mt-1">אין פריטים ממתינים כרגע</p>
          </div>
        )}

        {/* Info Message */}
        {decisions.length > 0 && (
          <div className="text-xs text-center text-gray-500 pt-2 border-t">
            💡 הסוכנים מארגנים עבורך את המשימות החשובות ביותר
          </div>
        )}
      </div>
    </BaseWidget>
  );
}
