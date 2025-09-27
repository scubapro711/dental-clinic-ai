import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';

/**
 * StatisticsCard Component
 * 
 * A reusable card component for displaying key performance indicators (KPIs)
 * with support for trends, status indicators, and Agentic UX principles.
 * 
 * Features:
 * - Real-time data display
 * - Trend indicators (up/down/neutral)
 * - Status badges (success/warning/error)
 * - Responsive design
 * - Accessibility compliant
 * - Agentic UX integration
 * - Number formatting for better readability
 */

/**
 * Format numeric values for display
 * @param {string|number} value - The value to format
 * @returns {string} - Formatted value
 */
const formatDisplayValue = (value) => {
  if (typeof value === 'string') {
    // Check if the string contains only digits (and possibly commas/periods)
    const numericMatch = value.match(/^[\d,.-]+$/);
    if (numericMatch) {
      // Remove existing formatting and parse as number
      const cleanValue = value.replace(/,/g, '');
      const numValue = parseFloat(cleanValue);
      if (!isNaN(numValue)) {
        // Format with commas for thousands
        return numValue.toLocaleString();
      }
    }
    // Return as-is if not numeric (e.g., "$12,345", "N/A", etc.)
    return value;
  }
  
  if (typeof value === 'number') {
    return value.toLocaleString();
  }
  
  return String(value);
};
const StatisticsCard = ({
  title,
  value,
  subtitle,
  trend,
  trendValue,
  status = 'neutral',
  icon: Icon,
  className,
  isLoading = false,
  agentStatus = 'active',
  lastUpdated,
  onClick,
  ...props
}) => {
  // Trend icon mapping
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" aria-label="Trending up" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" aria-label="Trending down" />;
      case 'neutral':
        return <Minus className="h-4 w-4 text-gray-500" aria-label="No change" />;
      default:
        return null;
    }
  };

  // Status badge configuration
  const getStatusConfig = () => {
    switch (status) {
      case 'success':
        return {
          variant: 'default',
          className: 'bg-green-100 text-green-800 border-green-200',
          icon: <CheckCircle className="h-3 w-3" />,
          label: 'Success'
        };
      case 'warning':
        return {
          variant: 'secondary',
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: <AlertCircle className="h-3 w-3" />,
          label: 'Warning'
        };
      case 'error':
        return {
          variant: 'destructive',
          className: 'bg-red-100 text-red-800 border-red-200',
          icon: <AlertCircle className="h-3 w-3" />,
          label: 'Error'
        };
      default:
        return {
          variant: 'outline',
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: <Clock className="h-3 w-3" />,
          label: 'Neutral'
        };
    }
  };

  // Agent status indicator
  const getAgentStatusColor = () => {
    switch (agentStatus) {
      case 'active':
        return 'bg-green-500';
      case 'idle':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      case 'offline':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <Card 
      className={cn(
        "relative transition-all duration-200 hover:shadow-md cursor-pointer",
        "border-l-4 border-l-blue-500",
        isLoading && "opacity-50 pointer-events-none",
        className
      )}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
      aria-label={`Statistics card: ${title}, value: ${formatDisplayValue(value)}`}
      {...props}
    >
      {/* Agent Status Indicator */}
      <div 
        className={cn(
          "absolute top-2 right-2 w-2 h-2 rounded-full",
          getAgentStatusColor()
        )}
        aria-label={`Agent status: ${agentStatus}`}
        title={`Agent status: ${agentStatus}`}
      />

      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
            {Icon && <Icon className="h-4 w-4" aria-hidden="true" />}
            {title}
          </CardTitle>
          
          {/* Status Badge */}
          <Badge 
            variant={statusConfig.variant}
            className={cn("text-xs", statusConfig.className)}
            aria-label={`Status: ${statusConfig.label}`}
          >
            {statusConfig.icon}
            <span className="ml-1 sr-only">{statusConfig.label}</span>
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Main Value */}
        <div className="flex items-baseline justify-between">
          <div className="flex items-baseline gap-2">
            <span 
              className="text-2xl font-bold text-gray-900"
              aria-label={`Main value: ${formatDisplayValue(value)}`}
            >
              {isLoading ? (
                <div className="h-8 w-16 bg-gray-200 animate-pulse rounded" />
              ) : (
                formatDisplayValue(value)
              )}
            </span>
            
            {/* Trend Indicator */}
            {trend && trendValue && !isLoading && (
              <div className="flex items-center gap-1">
                {getTrendIcon()}
                <span 
                  className={cn(
                    "text-sm font-medium",
                    trend === 'up' && "text-green-600",
                    trend === 'down' && "text-red-600",
                    trend === 'neutral' && "text-gray-600"
                  )}
                  aria-label={`Trend: ${trend} by ${trendValue}`}
                >
                  {trendValue}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Subtitle */}
        {subtitle && (
          <p 
            className="text-sm text-gray-500 mt-1"
            aria-label={`Subtitle: ${subtitle}`}
          >
            {subtitle}
          </p>
        )}

        {/* Last Updated */}
        {lastUpdated && (
          <p 
            className="text-xs text-gray-400 mt-2 flex items-center gap-1"
            aria-label={`Last updated: ${lastUpdated}`}
          >
            <Clock className="h-3 w-3" aria-hidden="true" />
            Last updated: {lastUpdated}
          </p>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="absolute inset-0 bg-white/50 flex items-center justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
            <span className="sr-only">Loading...</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default StatisticsCard;
