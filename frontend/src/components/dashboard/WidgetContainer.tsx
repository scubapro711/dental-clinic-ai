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
 * Design System v2.0:
 * - Clean card design with soft shadows
 * - Icon badges with colored backgrounds
 * - Smooth transitions and hover effects
 * - Consistent spacing (24px padding)
 * - Professional color palette
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
  
  // Icon background colors based on design system
  const iconColorMap = {
    blue: { background: 'var(--primary-blue-light)', color: 'var(--primary-blue)' },
    purple: { background: '#F3E8FF', color: 'var(--secondary-purple)' },
    cyan: { background: '#E0F7FA', color: 'var(--secondary-cyan)' },
    green: { background: '#E8F5E9', color: 'var(--secondary-green)' },
    orange: { background: '#FFF3E0', color: 'var(--secondary-orange)' }
  }
  
  return (
    <div 
      className={`widget-container ${collapsed ? 'widget-collapsed' : ''}`}
      data-testid={`widget-${widgetId}`}
      data-collapsed={collapsed}
      style={{
        background: 'var(--bg-card)',
        borderRadius: 'var(--radius-lg)',
        padding: collapsed ? 'var(--spacing-md)' : 'var(--card-padding)',
        boxShadow: 'var(--shadow-card)',
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
                width: '40px',
                height: '40px',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px',
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
              fontSize: 'var(--text-xl)',
              fontWeight: 'var(--font-semibold)',
              color: 'var(--gray-900)',
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
              width: '32px',
              height: '32px',
              borderRadius: 'var(--radius-sm)',
              background: 'transparent',
              border: 'none',
              color: 'var(--gray-400)',
              cursor: 'pointer',
              transition: 'all var(--transition-base)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--gray-100)'
              e.currentTarget.style.color = 'var(--primary-blue)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color = 'var(--gray-400)'
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
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                background: 'transparent',
                border: 'none',
                color: 'var(--gray-400)',
                cursor: 'pointer',
                transition: 'all var(--transition-base)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--gray-100)'
                e.currentTarget.style.color = 'var(--primary-blue)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color = 'var(--gray-400)'
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
          className="widget-content fade-in"
          data-testid={`${widgetId}-content`}
          style={{
            animation: 'fadeIn var(--transition-slow)'
          }}
        >
          {children}
        </div>
      )}
    </div>
  )
}

