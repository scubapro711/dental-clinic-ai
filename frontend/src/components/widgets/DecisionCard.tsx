import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertCircle,
  CheckCircle2,
  XCircle,
  Clock,
  ChevronDown,
  ChevronUp,
  User,
  TrendingUp,
  Shield,
  ExternalLink
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Decision } from '@/services/dashboardService';

interface DecisionCardProps {
  decision: Decision;
  onApprove: (decision: Decision) => void;
  onReject: (decision: Decision) => void;
  onViewDetails?: (decision: Decision) => void;
}

/**
 * DecisionCard Component
 * 
 * Displays a single decision with compact and expanded views.
 * Compact view shows essential info with quick actions.
 * Expanded view shows full context, AI reasoning, and detailed actions.
 */
export default function DecisionCard({
  decision,
  onApprove,
  onReject,
  onViewDetails
}: DecisionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getPriorityConfig = (priority: Decision['priority']) => {
    const configs = {
      critical: {
        icon: <AlertCircle className="w-4 h-4" />,
        color: 'text-red-700 bg-red-100 border-red-300',
        borderColor: 'border-red-300',
        bgColor: 'bg-red-50',
        label: 'קריטי'
      },
      high: {
        icon: <AlertCircle className="w-4 h-4" />,
        color: 'text-orange-700 bg-orange-100 border-orange-300',
        borderColor: 'border-orange-300',
        bgColor: 'bg-orange-50',
        label: 'דחוף'
      },
      medium: {
        icon: <Clock className="w-4 h-4" />,
        color: 'text-yellow-700 bg-yellow-100 border-yellow-300',
        borderColor: 'border-yellow-300',
        bgColor: 'bg-yellow-50',
        label: 'בינוני'
      },
      low: {
        icon: <Clock className="w-4 h-4" />,
        color: 'text-blue-700 bg-blue-100 border-blue-300',
        borderColor: 'border-blue-300',
        bgColor: 'bg-blue-50',
        label: 'נמוך'
      }
    };
    // Defensive check: ensure priority exists and is valid
    if (!priority || !configs[priority]) {
      console.warn('[DecisionCard] Invalid priority:', priority, '- using medium as fallback');
      return configs.medium;
    }
    return configs[priority];
  };

  const getAgentConfig = (agent: string) => {
    const configs: Record<string, { name: string; color: string }> = {
      alex: { name: 'אלכס', color: 'bg-blue-100 text-blue-700 border-blue-300' },
      sarah: { name: 'שרה', color: 'bg-pink-100 text-pink-700 border-pink-300' },
      marcus: { name: 'מרקוס', color: 'bg-green-100 text-green-700 border-green-300' },
      sophia: { name: 'סופיה', color: 'bg-orange-100 text-orange-700 border-orange-300' },
      harper: { name: 'הארפר', color: 'bg-purple-100 text-purple-700 border-purple-300' },
      system: { name: 'מערכת', color: 'bg-gray-100 text-gray-700 border-gray-300' }
    };
    return configs[agent] || configs.system;
  };

  const getCategoryConfig = (category?: string) => {
    const configs: Record<string, { label: string; icon: React.ReactNode }> = {
      clinical: { label: 'קליני', icon: <User className="w-3 h-3" /> },
      operational: { label: 'תפעולי', icon: <TrendingUp className="w-3 h-3" /> },
      financial: { label: 'פיננסי', icon: <TrendingUp className="w-3 h-3" /> },
      compliance: { label: 'ציות', icon: <Shield className="w-3 h-3" /> }
    };
    return configs[category || 'operational'];
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const diff = now.getTime() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `לפני ${days} ימים`;
    if (hours > 0) return `לפני ${hours} שעות`;
    if (minutes > 0) return `לפני ${minutes} דקות`;
    return 'עכשיו';
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-500';
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const priorityConfig = getPriorityConfig(decision.priority);
  const agentConfig = getAgentConfig(decision.agent);
  const categoryConfig = getCategoryConfig(decision.category);

  return (
    <div
      className={cn(
        'rounded-lg border-2 transition-all duration-200',
        'hover:shadow-md',
        priorityConfig.borderColor,
        priorityConfig.bgColor
      )}
    >
      {/* Compact View */}
      <div className="p-3">
        {/* Header */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            {/* Badges */}
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge className={cn('text-xs border', agentConfig.color)}>
                {agentConfig.name}
              </Badge>
              <Badge className={cn('text-xs flex items-center gap-1 border', priorityConfig.color)}>
                {priorityConfig.icon}
                {priorityConfig.label}
              </Badge>
              {decision.category && (
                <Badge variant="outline" className="text-xs flex items-center gap-1">
                  {categoryConfig.icon}
                  {categoryConfig.label}
                </Badge>
              )}
              {decision.compliance_risk && (
                <Badge variant="destructive" className="text-xs flex items-center gap-1">
                  <Shield className="w-3 h-3" />
                  סיכון ציות
                </Badge>
              )}
            </div>

            {/* Title */}
            <h4 className="font-semibold text-sm mb-1">{decision.title}</h4>

            {/* Patient Name (if applicable) */}
            {decision.patient_name && (
              <div className="text-xs text-gray-600 flex items-center gap-1 mb-1">
                <User className="w-3 h-3" />
                <span>{decision.patient_name}</span>
              </div>
            )}

            {/* Description (compact) */}
            {!isExpanded && (
              <p className="text-xs text-gray-600 line-clamp-2">{decision.description}</p>
            )}

            {/* Time */}
            <div className="text-xs text-gray-500 mt-1">
              {formatTimeAgo(decision.timestamp)}
            </div>
          </div>

          {/* Expand/Collapse Button */}
          <Button
            size="sm"
            variant="ghost"
            className="h-6 w-6 p-0 ml-2"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </Button>
        </div>

        {/* Expanded View */}
        {isExpanded && (
          <div className="mt-3 pt-3 border-t space-y-3">
            {/* Full Description */}
            <div>
              <h5 className="text-xs font-semibold text-gray-700 mb-1">תיאור מלא:</h5>
              <p className="text-xs text-gray-600">{decision.description}</p>
            </div>

            {/* AI Reasoning */}
            {decision.reasoning && (
              <div>
                <h5 className="text-xs font-semibold text-gray-700 mb-1">נימוק AI:</h5>
                <p className="text-xs text-gray-600 bg-white/50 p-2 rounded">
                  {decision.reasoning}
                </p>
              </div>
            )}

            {/* Confidence Score */}
            {decision.confidence !== null && decision.confidence !== undefined && (
              <div>
                <h5 className="text-xs font-semibold text-gray-700 mb-1">רמת ביטחון:</h5>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className={cn(
                        'h-2 rounded-full transition-all',
                        decision.confidence >= 80 ? 'bg-green-500' :
                        decision.confidence >= 60 ? 'bg-yellow-500' : 'bg-orange-500'
                      )}
                      style={{ width: `${decision.confidence}%` }}
                    />
                  </div>
                  <span className={cn('text-xs font-semibold', getConfidenceColor(decision.confidence))}>
                    {decision.confidence}%
                  </span>
                </div>
              </div>
            )}

            {/* Impact Level */}
            {decision.impact_level && (
              <div className="flex items-center gap-2 text-xs">
                <TrendingUp className="w-3 h-3 text-gray-500" />
                <span className="text-gray-600">
                  רמת השפעה: <span className="font-semibold">{decision.impact_level}</span>
                </span>
              </div>
            )}

            {/* Due By */}
            {decision.due_by && (
              <div className="flex items-center gap-2 text-xs">
                <Clock className="w-3 h-3 text-gray-500" />
                <span className="text-gray-600">
                  יש להחליט עד: <span className="font-semibold">{new Date(decision.due_by).toLocaleDateString('he-IL')}</span>
                </span>
              </div>
            )}

            {/* View Details Link */}
            {onViewDetails && (
              <Button
                variant="link"
                size="sm"
                className="text-xs p-0 h-auto"
                onClick={() => onViewDetails(decision)}
              >
                <ExternalLink className="w-3 h-3 mr-1" />
                צפה בפרטים המלאים
              </Button>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 mt-3">
          <Button
            size="sm"
            className="flex-1 text-xs h-7 bg-green-600 hover:bg-green-700"
            onClick={() => onApprove(decision)}
          >
            <CheckCircle2 className="w-3 h-3 mr-1" />
            {decision.action}
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs h-7"
            onClick={() => onReject(decision)}
          >
            <XCircle className="w-3 h-3 mr-1" />
            דחה
          </Button>
        </div>
      </div>
    </div>
  );
}
