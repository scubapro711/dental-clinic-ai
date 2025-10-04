import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

const Button = React.forwardRef(({ 
  className, 
  variant = 'primary', 
  size = 'md',
  loading = false,
  children, 
  disabled,
  ...props 
}, ref) => {
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-sm',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 active:bg-gray-400',
    success: 'bg-green-600 text-white hover:bg-green-700 active:bg-green-800 shadow-sm',
    warning: 'bg-orange-600 text-white hover:bg-orange-700 active:bg-orange-800 shadow-sm',
    danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 shadow-sm',
    ghost: 'bg-transparent hover:bg-gray-100 active:bg-gray-200 text-gray-700',
    outline: 'border-2 border-gray-300 bg-transparent hover:bg-gray-50 active:bg-gray-100',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-lg',
    md: 'px-4 py-2 text-base rounded-lg',
    lg: 'px-6 py-3 text-lg rounded-xl',
    xl: 'px-8 py-4 text-xl rounded-xl',
  };
  
  return (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center gap-2',
        'font-medium',
        'transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
        'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <Loader2 className="w-4 h-4 animate-spin" />
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export { Button };
