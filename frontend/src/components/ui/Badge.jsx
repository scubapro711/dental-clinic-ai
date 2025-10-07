import React from 'react';
import { cn } from '@/lib/utils';

const Badge = React.forwardRef(({ 
  className, 
  variant = 'default',
  size = 'md',
  pulse = false,
  children, 
  ...props 
}, ref) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-orange-100 text-orange-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
    alex: 'bg-purple-100 text-purple-800',
    marcus: 'bg-pink-100 text-pink-800',
    sophia: 'bg-cyan-100 text-cyan-800',
  };
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };
  
  return (
    <span
      ref={ref}
      className={cn(
        'inline-flex items-center gap-1',
        'font-medium rounded-full',
        'transition-all duration-200',
        variants[variant],
        sizes[size],
        pulse && 'animate-pulse',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
});

Badge.displayName = 'Badge';

export { Badge };
