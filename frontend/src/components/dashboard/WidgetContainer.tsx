/**
 * WidgetContainer v2.0 - Modern Dashboard Widget Wrapper
 * 
 * Features:
 * - Collapse/expand functionality with smooth animations
 * - RBAC integration (hides if no permission)
 * - Edit mode support
 * - Modern card design with hover effects
 * - RTL support
 * - Accessibility (ARIA labels, keyboard navigation)
 * 
 * Uses existing design-system.css variables
 */

import { ReactNode } from 'react'
import { ChevronDown, ChevronUp, MoreVertical } from 'lucide-react'
import { useDashboard } from '../../contexts/DashboardContext'

interface WidgetContainerProps {
  widgetId: string
  title: string
  icon?: ReactNode
  iconColor?: 'blue' | 'purple' | 'cyan' | 'green' | 'orange'
  defaultCollapsed?: boolean
  children: ReactNode
}

export function WidgetContainer({
  widgetId,
  title,
  icon,
  iconColor = 'blue',
  defaultCollapsed = false,
  children
}: WidgetContainerProps) {
  const { 
    isCollapsed, 
    toggleCollapse, 
    isEditMode, 
    canViewWidget 
  } = useDashboard()
  
  // Check RBAC permissions
  if (!canViewWidget(widgetId)) {
    return null  // Don't render if no permission
  }
  
  const collapsed = isCollapsed(widgetId)
  
  // Icon background colors using existing design system
  const iconColorMap = {
    blue: { background: 'oklch(0.95 0.05 240)', color: 'var(--primary)' },
    purple: { background: 'oklch(0.95 0.05 300)', color: 'var(--accent)' },
    cyan: { background: 'oklch(0.95 0.05 200)', color: 'var(--secondary)' },
    green: { background: 'oklch(0.95 0.05 145)', color: 'var(--success)' },
    orange: { background: 'oklch(0.95 0.05 60)', color: 'var(--warning)' }
  }
  
  return (
    <div 
      className={`widget-container ${collapsed ? 'widget-collapsed' : ''}`}
      data-testid={`widget-${widgetId}`}
      data-collapsed={collapsed}
      style={{
        background: 'var(--background)',
        borderRadius: 'var(--radius-lg)',
        padding: collapsed ? 'var(--spacing-md)' : 'var(--spacing-lg)',
        boxShadow: 'var(--shadow-md)',
        transition: 'all var(--transition-slow)',
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <div 
        className="widget-header"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: collapsed ? '0' : 'var(--spacing-md)',
          gap: 'var(--spacing-md)'
        }}
      >
        {/* Title with Icon */}
        <div 
          className="widget-title-wrapper"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-sm)',
            flex: '1',
            minWidth: '0'
          }}
        >
          {icon && (
            <div 
              className="widget-icon"
              style={{
                width: '2.5rem',
                height: '2.5rem',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.25rem',
                flexShrink: '0',
                transition: 'all var(--transition-base)',
                ...iconColorMap[iconColor]
              }}
            >
              {icon}
            </div>
          )}
          <h3 
            className="widget-title"
            style={{
              fontSize: 'var(--font-size-xl)',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--foreground)',
              margin: '0',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {title}
          </h3>
        </div>
        
        {/* Actions */}
        <div 
          className="widget-actions"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-xs)',
            flexShrink: '0'
          }}
        >
          {/* Collapse button */}
          <button
            onClick={() => toggleCollapse(widgetId)}
            className="widget-action-button"
            aria-label={collapsed ? `Expand ${title}` : `Collapse ${title}`}
            data-testid={`collapse-${widgetId}`}
            style={{
              width: '2rem',
              height: '2rem',
              borderRadius: 'var(--radius-sm)',
              background: 'transparent',
              border: 'none',
              color: 'var(--foreground-tertiary)',
              cursor: 'pointer',
              transition: 'all var(--transition-base)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--muted)'
              e.currentTarget.style.color = 'var(--primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color = 'var(--foreground-tertiary)'
            }}
          >
            {collapsed ? (
              <ChevronDown size={18} />
            ) : (
              <ChevronUp size={18} />
            )}
          </button>
          
          {/* More menu (edit mode only) */}
          {isEditMode && (
            <button 
              className="widget-action-button"
              aria-label={`More options for ${title}`}
              data-testid={`more-${widgetId}`}
              style={{
                width: '2rem',
                height: '2rem',
                borderRadius: 'var(--radius-sm)',
                background: 'transparent',
                border: 'none',
                color: 'var(--foreground-tertiary)',
                cursor: 'pointer',
                transition: 'all var(--transition-base)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--muted)'
                e.currentTarget.style.color = 'var(--primary)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color = 'var(--foreground-tertiary)'
              }}
            >
              <MoreVertical size={18} />
            </button>
          )}
        </div>
      </div>
      
      {/* Content */}
      {!collapsed && (
        <div 
          className="widget-content animate-fade-in-up"
          data-testid={`${widgetId}-content`}
        >
          {children}
        </div>
      )}
    </div>
  )
}

