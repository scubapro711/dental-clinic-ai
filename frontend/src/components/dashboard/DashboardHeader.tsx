/**
 * DashboardHeader v2.0 - Modern Dashboard Header
 * 
 * Features:
 * - Edit Mode toggle with visual feedback
 * - Reset to defaults button (only in edit mode)
 * - User greeting with role display
 * - Responsive design
 * - Modern styling with design system v2.0
 * - RTL support
 * 
 * Design System v2.0:
 * - Clean card design with shadow
 * - Primary blue buttons
 * - Smooth transitions
 * - Professional typography
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
        marginBottom: 'var(--spacing-lg)',
        padding: 'var(--spacing-md)',
        background: 'var(--bg-card)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-card)',
        gap: 'var(--spacing-md)',
        flexWrap: 'wrap'
      }}
    >
      {/* Title and Greeting */}
      <div>
        <h1 
          className="dashboard-title"
          style={{
            fontSize: 'var(--text-3xl)',
            fontWeight: 'var(--font-bold)',
            color: 'var(--gray-900)',
            margin: '0 0 var(--spacing-xs) 0'
          }}
        >
          Dashboard
        </h1>
        <p 
          style={{
            fontSize: 'var(--text-sm)',
            color: 'var(--gray-400)',
            margin: '0'
          }}
        >
          Welcome back, <span style={{ fontWeight: 'var(--font-medium)', color: 'var(--gray-600)' }}>
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
            padding: '12px 24px',
            borderRadius: 'var(--radius-md)',
            fontWeight: 'var(--font-semibold)',
            fontSize: 'var(--text-base)',
            border: 'none',
            cursor: 'pointer',
            transition: 'all var(--transition-base)',
            background: isEditMode ? 'var(--primary-blue)' : 'var(--gray-100)',
            color: isEditMode ? 'var(--white)' : 'var(--gray-700)',
            boxShadow: isEditMode ? 'var(--shadow-md)' : 'none'
          }}
          onMouseEnter={(e) => {
            if (isEditMode) {
              e.currentTarget.style.background = 'var(--primary-blue-hover)'
              e.currentTarget.style.transform = 'translateY(-1px)'
              e.currentTarget.style.boxShadow = 'var(--shadow-lg)'
            } else {
              e.currentTarget.style.background = 'var(--gray-200)'
            }
          }}
          onMouseLeave={(e) => {
            if (isEditMode) {
              e.currentTarget.style.background = 'var(--primary-blue)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'var(--shadow-md)'
            } else {
              e.currentTarget.style.background = 'var(--gray-100)'
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
              padding: '12px 24px',
              borderRadius: 'var(--radius-md)',
              fontWeight: 'var(--font-semibold)',
              fontSize: 'var(--text-base)',
              border: 'none',
              cursor: 'pointer',
              transition: 'all var(--transition-base)',
              background: 'var(--gray-100)',
              color: 'var(--gray-700)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--gray-200)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--gray-100)'
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

