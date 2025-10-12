import React from 'react';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Confidence Indicator Component
 * 
 * Shows AI confidence level with visual indicators
 * Helps users understand how certain the AI is about its response
 */
export default function ConfidenceIndicator({ confidence, size = 'md', showLabel = true }) {
  if (confidence === undefined || confidence === null) {
    return null;
  }

  // Ensure confidence is between 0 and 1
  const normalizedConfidence = Math.max(0, Math.min(1, confidence));
  const percentage = (normalizedConfidence * 100).toFixed(0);

  // Determine confidence level
  const getConfidenceLevel = (conf) => {
    if (conf >= 0.9) return 'very_high';
    if (conf >= 0.75) return 'high';
    if (conf >= 0.6) return 'medium';
    if (conf >= 0.4) return 'low';
    return 'very_low';
  };

  const level = getConfidenceLevel(normalizedConfidence);

  // Configuration for each confidence level
  const levelConfig = {
    very_high: {
      label: 'ביטחון גבוה מאוד',
      color: 'bg-green-500',
      textColor: 'text-green-700',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-300',
      icon: <TrendingUp className="w-3 h-3" />
    },
    high: {
      label: 'ביטחון גבוה',
      color: 'bg-blue-500',
      textColor: 'text-blue-700',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-300',
      icon: <TrendingUp className="w-3 h-3" />
    },
    medium: {
      label: 'ביטחון בינוני',
      color: 'bg-yellow-500',
      textColor: 'text-yellow-700',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-300',
      icon: <Minus className="w-3 h-3" />
    },
    low: {
      label: 'ביטחון נמוך',
      color: 'bg-orange-500',
      textColor: 'text-orange-700',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-300',
      icon: <TrendingDown className="w-3 h-3" />
    },
    very_low: {
      label: 'ביטחון נמוך מאוד',
      color: 'bg-red-500',
      textColor: 'text-red-700',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-300',
      icon: <AlertTriangle className="w-3 h-3" />
    }
  };

  const config = levelConfig[level];

  // Size configurations
  const sizeConfig = {
    sm: {
      container: 'h-1',
      text: 'text-xs',
      badge: 'text-xs px-1.5 py-0.5'
    },
    md: {
      container: 'h-2',
      text: 'text-sm',
      badge: 'text-xs px-2 py-1'
    },
    lg: {
      container: 'h-3',
      text: 'text-base',
      badge: 'text-sm px-3 py-1.5'
    }
  };

  const sizeStyle = sizeConfig[size] || sizeConfig.md;

  return (
    <div className="space-y-1">
      {/* Progress bar */}
      <div className={cn(
        'w-full bg-gray-200 rounded-full overflow-hidden',
        sizeStyle.container
      )}>
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500',
            config.color
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Label and percentage */}
      {showLabel && (
        <div className="flex items-center justify-between">
          <Badge
            variant="outline"
            className={cn(
              'flex items-center gap-1',
              config.bgColor,
              config.borderColor,
              config.textColor,
              sizeStyle.badge
            )}
          >
            {config.icon}
            {config.label}
          </Badge>
          <span className={cn(
            'font-semibold',
            config.textColor,
            sizeStyle.text
          )}>
            {percentage}%
          </span>
        </div>
      )}
    </div>
  );
}

/**
 * Compact Confidence Badge
 * For inline use in text or small spaces
 */
export function ConfidenceBadge({ confidence }) {
  if (confidence === undefined || confidence === null) {
    return null;
  }

  const normalizedConfidence = Math.max(0, Math.min(1, confidence));
  const percentage = (normalizedConfidence * 100).toFixed(0);

  const getColor = (conf) => {
    if (conf >= 0.9) return 'bg-green-500';
    if (conf >= 0.75) return 'bg-blue-500';
    if (conf >= 0.6) return 'bg-yellow-500';
    if (conf >= 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <Badge variant="secondary" className="text-xs flex items-center gap-1">
      <div className={cn('w-2 h-2 rounded-full', getColor(normalizedConfidence))} />
      {percentage}%
    </Badge>
  );
}

/**
 * Confidence Tooltip
 * Explains what confidence means
 */
export function ConfidenceTooltip() {
  return (
    <div className="text-xs text-gray-600 space-y-2">
      <p className="font-semibold">מה זה ביטחון?</p>
      <p>
        ביטחון מציין עד כמה הסוכן בטוח בתשובה שלו.
      </p>
      <ul className="space-y-1 mr-4">
        <li>• <span className="text-green-600 font-semibold">90%+</span> - תשובה מאוד בטוחה</li>
        <li>• <span className="text-blue-600 font-semibold">75-90%</span> - תשובה בטוחה</li>
        <li>• <span className="text-yellow-600 font-semibold">60-75%</span> - תשובה סבירה</li>
        <li>• <span className="text-orange-600 font-semibold">40-60%</span> - תשובה לא בטוחה</li>
        <li>• <span className="text-red-600 font-semibold">&lt;40%</span> - מומלץ אימות אנושי</li>
      </ul>
      <p className="text-xs text-gray-500 mt-2">
        💡 ביטחון נמוך לא אומר שהתשובה שגויה, אלא שכדאי לבדוק אותה.
      </p>
    </div>
  );
}
