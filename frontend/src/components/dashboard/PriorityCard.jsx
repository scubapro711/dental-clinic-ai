import React from 'react';
import { cn } from '@/lib/utils';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Clock, User, MessageCircle, Phone } from 'lucide-react';

const PriorityCard = ({ 
  priority = 'normal', // 'emergency', 'urgent', 'normal'
  patient,
  reason,
  waitTime,
  agent,
  onTakeOver,
  onViewDetails,
}) => {
  const priorityConfig = {
    emergency: {
      bg: 'bg-red-50 border-red-200',
      badge: 'error',
      badgeBg: 'bg-red-100 text-red-800',
      icon: '🚨',
      label: 'EMERGENCY',
      buttonVariant: 'danger',
    },
    urgent: {
      bg: 'bg-orange-50 border-orange-200',
      badge: 'warning',
      badgeBg: 'bg-orange-100 text-orange-800',
      icon: '⚠️',
      label: 'URGENT',
      buttonVariant: 'warning',
    },
    normal: {
      bg: 'bg-blue-50 border-blue-200',
      badge: 'info',
      badgeBg: 'bg-blue-100 text-blue-800',
      icon: 'ℹ️',
      label: 'NORMAL',
      buttonVariant: 'primary',
    },
  };
  
  const config = priorityConfig[priority];
  
  return (
    <Card 
      hover
      className={cn(
        'border-2 transition-all duration-200',
        config.bg,
        'fade-in'
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center flex-shrink-0">
            <User className="w-6 h-6 text-gray-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-lg font-semibold text-gray-900 truncate">
              {patient?.name || 'Unknown Patient'}
            </h4>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Phone className="w-3 h-3" />
              <span className="truncate">{patient?.phone || 'No phone'}</span>
            </div>
          </div>
        </div>
        
        <Badge 
          size="lg" 
          className={cn(config.badgeBg, 'flex-shrink-0')}
          pulse={priority === 'emergency'}
        >
          <span>{config.icon}</span>
          <span>{config.label}</span>
        </Badge>
      </div>
      
      {/* Reason */}
      <div className="mb-4 p-3 bg-white rounded-lg border border-gray-200">
        <p className="text-base text-gray-900 font-medium">
          {reason || 'No reason provided'}
        </p>
      </div>
      
      {/* Meta Info */}
      <div className="flex items-center gap-4 mb-4 text-sm text-gray-600">
        <div className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" />
          <span>Waiting <strong className="text-gray-900">{waitTime || '0m'}</strong></span>
        </div>
        <div className="flex items-center gap-1.5">
          <MessageCircle className="w-4 h-4" />
          <span>Handled by <strong className="text-gray-900">{agent || 'Unknown'}</strong></span>
        </div>
      </div>
      
      {/* Actions */}
      <div className="flex gap-2">
        <Button 
          variant={config.buttonVariant}
          size="lg"
          className="flex-1"
          onClick={onTakeOver}
        >
          Take Over
        </Button>
        <Button 
          variant="ghost" 
          size="lg"
          onClick={onViewDetails}
        >
          Details
        </Button>
      </div>
    </Card>
  );
};

export { PriorityCard };
