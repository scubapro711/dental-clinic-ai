import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

/**
 * Base Widget Component - Enhanced Version
 * 
 * Reusable widget container for all agent widgets with modern styling
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
  // Agent colors with modern gradients
  const agentColors = {
    alex: 'border-blue-400 bg-gradient-to-br from-blue-50 to-white hover:shadow-blue-100',
    marcus: 'border-green-400 bg-gradient-to-br from-green-50 to-white hover:shadow-green-100',
    sophia: 'border-purple-400 bg-gradient-to-br from-purple-50 to-white hover:shadow-purple-100',
    sarah: 'border-orange-400 bg-gradient-to-br from-orange-50 to-white hover:shadow-orange-100',
    system: 'border-gray-400 bg-gradient-to-br from-gray-50 to-white hover:shadow-gray-100'
  };

  const agentColor = agentColors[agent] || agentColors.system;

  return (
    <Card className={cn(
      'border-2 transition-all duration-300 hover:shadow-xl hover:-translate-y-1',
      'backdrop-blur-sm bg-white/90',
      agentColor,
      className
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2 font-semibold">
            {icon && <span className="text-xl">{icon}</span>}
            {title}
          </CardTitle>
          <div className="flex items-center gap-2">
            {badge && (
              <Badge variant="secondary" className="text-xs font-semibold">
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
            <div className="relative">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-t-2 border-blue-600"></div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className="h-6 w-6 bg-blue-100 rounded-full"></div>
              </div>
            </div>
          </div>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  );
}

