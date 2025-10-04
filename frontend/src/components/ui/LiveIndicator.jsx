import React from 'react';
import { cn } from '@/lib/utils';

const LiveIndicator = ({ active = true, label = 'Live', className }) => {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="relative">
        <div className={cn(
          'w-2 h-2 rounded-full',
          active ? 'bg-green-500' : 'bg-gray-400'
        )} />
        {active && (
          <>
            <div className="absolute inset-0 w-2 h-2 rounded-full bg-green-500 animate-ping opacity-75" />
            <div className="absolute inset-0 w-2 h-2 rounded-full bg-green-500 pulse-ring" />
          </>
        )}
      </div>
      <span className={cn(
        'text-xs font-medium',
        active ? 'text-green-600' : 'text-gray-400'
      )}>
        {label}
      </span>
    </div>
  );
};

export { LiveIndicator };
