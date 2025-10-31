/**
 * DashboardHeader v2.0 - Modern Dashboard Header
 * 
 * Features:
 * - Edit Mode toggle with visual feedback
 * - Reset to defaults button (only in edit mode)
 * - User greeting with role display
 * - Responsive design
 * - Uses existing design-system.css variables
 * - RTL support
 */

import { Settings, RotateCcw } from 'lucide-react'
import { useDashboard } from '../../contexts/DashboardContext'
import { getUserInfo } from '../../utils/rbac'

export function DashboardHeader() {
  const { isEditMode, toggleEditMode, resetToDefaults } = useDashboard()
  const userInfo = getUserInfo()
  
  const handleReset = () => {
    if (confirm('Reset dashboard to default layout? This cannot be undone.')) {
      resetToDefaults()
    }
  }
  
  return (
    <div 
      className="dashboard-header"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 'var(--spacing-xl)',
        padding: 'var(--spacing-lg)',
        background: 'var(--background)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-md)',
        gap: 'var(--spacing-md)',
        flexWrap: 'wrap'
      }}
    >
      {/* Title and Greeting */}
      <div>
        <h1 
          className="dashboard-title"
          style={{
            fontSize: 'var(--font-size-3xl)',
            fontWeight: 'var(--font-weight-bold)',
            color: 'var(--foreground)',
            margin: '0 0 var(--spacing-xs) 0'
          }}
        >
          Dashboard
        </h1>
        <p 
          style={{
            fontSize: 'var(--font-size-sm)',
            color: 'var(--foreground-tertiary)',
            margin: '0'
          }}
        >
          Welcome back, <span style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--foreground-secondary)' }}>
            {userInfo?.name || 'User'}
          </span>
          {userInfo?.role && (
            <span style={{ marginLeft: 'var(--spacing-xs)' }}>
              • {userInfo.role}
            </span>
          )}
        </p>
      </div>
      
      {/* Actions */}
      <div 
        className="dashboard-actions"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-sm)'
        }}
      >
        {/* Edit Mode Toggle */}
        <button
          onClick={toggleEditMode}
          className={isEditMode ? 'btn-primary' : 'btn-secondary'}
          aria-label={isEditMode ? 'Exit edit mode' : 'Enter edit mode'}
          data-testid="edit-mode-toggle"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 'var(--spacing-xs)',
            padding: '0.75rem 1.5rem',
            borderRadius: 'var(--radius-md)',
            fontWeight: 'var(--font-weight-semibold)',
            fontSize: 'var(--font-size-base)',
            border: 'none',
            cursor: 'pointer',
            transition: 'all var(--transition-base)',
            background: isEditMode ? 'var(--primary)' : 'var(--muted)',
            color: isEditMode ? 'var(--primary-foreground)' : 'var(--foreground)',
            boxShadow: isEditMode ? 'var(--shadow-md)' : 'none'
          }}
          onMouseEnter={(e) => {
            if (isEditMode) {
              e.currentTarget.style.background = 'var(--primary-hover)'
              e.currentTarget.style.transform = 'translateY(-1px)'
              e.currentTarget.style.boxShadow = 'var(--shadow-lg)'
            } else {
              e.currentTarget.style.background = 'var(--muted-foreground)'
              e.currentTarget.style.color = 'var(--background)'
            }
          }}
          onMouseLeave={(e) => {
            if (isEditMode) {
              e.currentTarget.style.background = 'var(--primary)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'var(--shadow-md)'
            } else {
              e.currentTarget.style.background = 'var(--muted)'
              e.currentTarget.style.color = 'var(--foreground)'
            }
          }}
        >
          <Settings size={16} />
          <span style={{ display: 'inline' }}>
            {isEditMode ? 'Done' : 'Customize'}
          </span>
        </button>
        
        {/* Reset Button (only in edit mode) */}
        {isEditMode && (
          <button
            onClick={handleReset}
            className="btn-secondary"
            aria-label="Reset to default layout"
            data-testid="reset-button"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 'var(--spacing-xs)',
              padding: '0.75rem 1.5rem',
              borderRadius: 'var(--radius-md)',
              fontWeight: 'var(--font-weight-semibold)',
              fontSize: 'var(--font-size-base)',
              border: 'none',
              cursor: 'pointer',
              transition: 'all var(--transition-base)',
              background: 'var(--muted)',
              color: 'var(--foreground)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--muted-foreground)'
              e.currentTarget.style.color = 'var(--background)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--muted)'
              e.currentTarget.style.color = 'var(--foreground)'
            }}
          >
            <RotateCcw size={16} />
            <span style={{ display: 'inline' }}>Reset</span>
          </button>
        )}
      </div>
    </div>
  )
}

