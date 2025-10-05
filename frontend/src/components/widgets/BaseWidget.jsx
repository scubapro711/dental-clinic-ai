import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

/**
 * Base Widget Component
 * 
 * Reusable widget container for all agent widgets
 */
export default function BaseWidget({
  title,
  agent,
  icon,
  children,
  className,
  headerAction,
  badge,
  isLoading = false
}) {
  // Agent colors
  const agentColors = {
    alex: 'border-blue-500 bg-blue-50/50',
    marcus: 'border-green-500 bg-green-50/50',
    sophia: 'border-purple-500 bg-purple-50/50',
    system: 'border-gray-500 bg-gray-50/50'
  };

  const agentColor = agentColors[agent] || agentColors.system;

  return (
    <Card className={cn(
      'border-2 transition-all duration-200 hover:shadow-lg',
      agentColor,
      className
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            {icon && <span className="text-lg">{icon}</span>}
            {title}
          </CardTitle>
          <div className="flex items-center gap-2">
            {badge && (
              <Badge variant="secondary" className="text-xs">
                {badge}
              </Badge>
            )}
            {headerAction}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  );
}
