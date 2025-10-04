import React from 'react';
import { cn, getAgentBgColor } from '@/lib/utils';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Activity, Clock, MessageCircle } from 'lucide-react';

const AgentStatusCardV2 = ({ 
  name,
  role,
  status = 'active', // 'active', 'busy', 'offline'
  activeConversations = 0,
  avgResponseTime = 0,
}) => {
  const statusConfig = {
    active: {
      color: 'text-green-600',
      bg: 'bg-green-500',
      ring: 'ring-green-500',
      label: 'Active',
      pulse: true,
    },
    busy: {
      color: 'text-orange-600',
      bg: 'bg-orange-500',
      ring: 'ring-orange-500',
      label: 'Busy',
      pulse: false,
    },
    offline: {
      color: 'text-gray-400',
      bg: 'bg-gray-400',
      ring: 'ring-gray-400',
      label: 'Offline',
      pulse: false,
    },
  };
  
  const config = statusConfig[status];
  const agentBgColor = getAgentBgColor(name);
  
  return (
    <Card className="relative overflow-hidden hover:shadow-lg transition-shadow">
      {/* Status Indicator Bar */}
      <div 
        className={cn(
          'absolute top-0 left-0 right-0 h-1',
          config.bg
        )}
      />
      
      {/* Avatar with Status */}
      <div className="flex items-center gap-3 mb-4 pt-2">
        <div className="relative">
          <div className={cn(
            'w-14 h-14 rounded-full flex items-center justify-center text-white text-lg font-bold shadow-md',
            agentBgColor
          )}>
            {name?.[0] || '?'}
          </div>
          
          {/* Status Dot */}
          <div className={cn(
            'absolute bottom-0 right-0',
            'w-4 h-4 rounded-full border-2 border-white',
            config.bg,
            config.pulse && 'animate-pulse'
          )} />
        </div>
        
        <div className="flex-1 min-w-0">
          <h4 className="text-base font-semibold text-gray-900 truncate">
            {name || 'Unknown'}
          </h4>
          <p className="text-xs text-gray-600 truncate">
            {role || 'Agent'}
          </p>
        </div>
        
        <Badge 
          variant={status === 'active' ? 'success' : 'default'} 
          size="sm"
        >
          {config.label}
        </Badge>
      </div>
      
      {/* Metrics */}
      <div className="space-y-2">
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <MessageCircle className="w-4 h-4" />
            <span>Active</span>
          </div>
          <span className="text-xl font-bold text-gray-900">
            {activeConversations}
          </span>
        </div>
        
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>Avg Response</span>
          </div>
          <span className="text-lg font-semibold text-gray-900">
            {avgResponseTime}s
          </span>
        </div>
      </div>
      
      {/* Activity Indicator */}
      {status === 'active' && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex items-center gap-2 text-xs text-green-600">
            <Activity className="w-3 h-3 animate-pulse" />
            <span className="font-medium">Currently handling requests</span>
          </div>
        </div>
      )}
    </Card>
  );
};

export { AgentStatusCardV2 };
