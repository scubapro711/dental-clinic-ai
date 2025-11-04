import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Activity, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Agent Activity Widget
 * 
 * Shows real-time activity and performance of all AI agents
 */
export default function AgentActivityWidget({ onChatWithAgent }) {
  const [activityData, setActivityData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchActivityData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchActivityData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchActivityData = async () => {
    setIsLoading(true);
    try {
      // TODO: Fetch real activity data from Backend
      // For now, use mock data
      useMockData();
    } catch (error) {
      console.error('Error fetching activity data:', error);
      useMockData();
    } finally {
      setIsLoading(false);
    }
  };

  const useMockData = () => {
    const mockData = {
      agents: [
        {
          id: 'alex',
          name: 'Alex',
          role: 'Patient Coordinator',
          status: 'active',
          tasksToday: 24,
          tasksCompleted: 18,
          avgResponseTime: '2.3s',
          successRate: 94
        },
        {
          id: 'sarah',
          name: 'Sarah',
          role: 'Clinical AI',
          status: 'active',
          tasksToday: 12,
          tasksCompleted: 11,
          avgResponseTime: '1.8s',
          successRate: 98
        },
        {
          id: 'marcus',
          name: 'Marcus',
          role: 'Revenue Optimizer',
          status: 'active',
          tasksToday: 8,
          tasksCompleted: 7,
          avgResponseTime: '3.1s',
          successRate: 92
        },
        {
          id: 'sophia',
          name: 'Sophia',
          role: 'Scheduler',
          status: 'idle',
          tasksToday: 15,
          tasksCompleted: 15,
          avgResponseTime: '1.2s',
          successRate: 100
        },
        {
          id: 'harper',
          name: 'Harper',
          role: 'Compliance Monitor',
          status: 'active',
          tasksToday: 6,
          tasksCompleted: 5,
          avgResponseTime: '2.7s',
          successRate: 96
        }
      ],
      totalTasks: 65,
      totalCompleted: 56,
      systemHealth: 97
    };
    setActivityData(mockData);
  };

  if (!activityData) return null;

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-700 border-green-300';
      case 'idle': return 'bg-gray-100 text-gray-700 border-gray-300';
      case 'error': return 'bg-red-100 text-red-700 border-red-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Activity className="w-3 h-3 animate-pulse" />;
      case 'idle': return <Clock className="w-3 h-3" />;
      case 'error': return <AlertCircle className="w-3 h-3" />;
      default: return <CheckCircle className="w-3 h-3" />;
    }
  };

  return (
    <BaseWidget
      title="פעילות סוכנים"
      agent="system"
      icon="📊"
      isLoading={isLoading}
    >
      <div className="space-y-4">
        {/* System Overview */}
        <div className="grid grid-cols-3 gap-2">
          <div className="p-2 bg-blue-50 rounded text-center">
            <div className="text-lg font-bold text-blue-900">
              {activityData.totalTasks}
            </div>
            <div className="text-xs text-blue-600">משימות היום</div>
          </div>
          <div className="p-2 bg-green-50 rounded text-center">
            <div className="text-lg font-bold text-green-900">
              {activityData.totalCompleted}
            </div>
            <div className="text-xs text-green-600">הושלמו</div>
          </div>
          <div className="p-2 bg-purple-50 rounded text-center">
            <div className="text-lg font-bold text-purple-900">
              {activityData.systemHealth}%
            </div>
            <div className="text-xs text-purple-600">תקינות</div>
          </div>
        </div>

        {/* Agents List */}
        <div className="space-y-2">
          <div className="text-xs font-semibold text-gray-700">
            סוכנים פעילים:
          </div>
          {activityData.agents.map((agent) => (
            <div
              key={agent.id}
              className="p-3 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold">{agent.name}</span>
                    <Badge
                      variant="outline"
                      className={cn('text-xs', getStatusColor(agent.status))}
                    >
                      <span className="flex items-center gap-1">
                        {getStatusIcon(agent.status)}
                        {agent.status}
                      </span>
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-500">{agent.role}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-gray-900">
                    {agent.tasksCompleted}/{agent.tasksToday}
                  </div>
                  <div className="text-xs text-gray-500">משימות</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-gray-100">
                <div className="text-xs">
                  <span className="text-gray-500">זמן תגובה:</span>
                  <span className="font-medium text-gray-900 ml-1">
                    {agent.avgResponseTime}
                  </span>
                </div>
                <div className="text-xs text-right">
                  <span className="text-gray-500">הצלחה:</span>
                  <span className={cn(
                    'font-medium ml-1',
                    agent.successRate >= 95 ? 'text-green-600' : 'text-yellow-600'
                  )}>
                    {agent.successRate}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2 border-t">
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs"
            onClick={() => onChatWithAgent && onChatWithAgent('Show detailed agent logs')}
          >
            <Activity className="w-3 h-3 mr-1" />
            לוגים מפורטים
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs"
            onClick={() => onChatWithAgent && onChatWithAgent('Show performance trends')}
          >
            <TrendingUp className="w-3 h-3 mr-1" />
            מגמות
          </Button>
        </div>
      </div>
    </BaseWidget>
  );
}
