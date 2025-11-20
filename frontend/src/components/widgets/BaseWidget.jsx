/**
 * BaseWidget v2.0 - Clean v2 Design System
 * 
 * Universal widget wrapper with consistent v2 styling
 * 
 * Features:
 * - rounded-2xl containers
 * - shadow-sm shadows
 * - border border-slate-200 borders
 * - Consistent padding and spacing
 * - Dark mode support
 * - Loading states
 * - Optional header actions
 */

import React from 'react'
import { cn } from '@/lib/utils'

export default function BaseWidget({
  title,
  icon,
  children,
  className,
  headerAction,
  badge,
  isLoading = false,
  contentClassName
}) {
  return (
    <div 
      className={cn(
        // v2 Base Styling
        'bg-white dark:bg-slate-800',
        'rounded-2xl',
        'shadow-sm',
        'border border-slate-200 dark:border-slate-700',
        'overflow-hidden',
        'transition-all duration-200',
        'hover:shadow-md',
        className
      )}
    >
      {/* Header */}
      {(title || icon || headerAction || badge) && (
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {icon && (
                <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400">
                  {icon}
                </div>
              )}
              {title && (
                <h3 className="text-base font-semibold text-slate-800 dark:text-white">
                  {title}
                </h3>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              {badge && (
                <span className="px-2 py-1 text-xs font-medium rounded-md bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                  {badge}
                </span>
              )}
              {headerAction}
            </div>
          </div>
        </div>
      )}
      
      {/* Content */}
      <div className={cn('p-6', contentClassName)}>
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-blue-200 dark:border-blue-800 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"/>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  )
}

/**
 * BaseWidgetCard - For card-based content inside widgets
 */
export function BaseWidgetCard({ children, className, onClick }) {
  return (
    <div 
      className={cn(
        'p-4 rounded-xl',
        'bg-slate-50 dark:bg-slate-700/50',
        'border border-slate-200 dark:border-slate-600',
        'transition-all duration-200',
        onClick && 'cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 hover:border-blue-300 dark:hover:border-blue-600',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

/**
 * BaseWidgetStat - For displaying statistics
 */
export function BaseWidgetStat({ label, value, icon, trend, className }) {
  return (
    <div className={cn('space-y-1', className)}>
      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        {icon && <span>{icon}</span>}
        <span>{label}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold text-slate-800 dark:text-white">
          {value}
        </span>
        {trend && (
          <span className={cn(
            'text-sm font-medium',
            trend > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          )}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>
    </div>
  )
}

/**
 * BaseWidgetList - For list-based content
 */
export function BaseWidgetList({ children, className }) {
  return (
    <div className={cn('space-y-2', className)}>
      {children}
    </div>
  )
}

/**
 * BaseWidgetListItem - Individual list item
 */
export function BaseWidgetListItem({ children, className, onClick }) {
  return (
    <div 
      className={cn(
        'p-3 rounded-lg',
        'border border-slate-200 dark:border-slate-700',
        'transition-all duration-200',
        onClick && 'cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-600',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

/**
 * BaseWidgetEmpty - Empty state
 */
export function BaseWidgetEmpty({ icon, message, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {icon && (
        <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-slate-400 dark:text-slate-500 mb-4">
          {icon}
        </div>
      )}
      <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
        {message || 'No data available'}
      </p>
      {action}
    </div>
  )
}
