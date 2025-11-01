/**
 * DashboardHeader v4.0 - Compact Dashboard Header with Integrated AI Agents
 * 
 * Features:
 * - Single row layout: Title | AI Agents | Actions
 * - Edit Mode toggle with visual feedback
 * - Reset to defaults button (only in edit mode)
 * - User greeting with role display
 * - AI Agents horizontal display IN THE SAME ROW
 * - Responsive design with scroll for agents on smaller screens
 * - Uses existing design-system.css variables
 * - RTL support
 */

import { Settings, RotateCcw } from 'lucide-react'
import { useDashboard } from '../../contexts/DashboardContext'
import { getUserInfo } from '../../utils/rbac'

const AI_AGENTS = [
  { id: 'alex', name: 'Alex', role: 'Patient Experience', value: '247', color: '#3b82f6' },
  { id: 'sarah', name: 'Sarah', role: 'Clinical Support', value: '98%', color: '#8b5cf6' },
  { id: 'marcus', name: 'Marcus', role: 'Financial', value: '₪45,230', color: '#06b6d4' },
  { id: 'sophia', name: 'Sophia', role: 'Scheduling', value: '8', color: '#f59e0b' },
  { id: 'harper', name: 'Harper', role: 'Compliance', value: '96%', color: '#10b981' }
]

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
        padding: 'var(--spacing-lg)',
        background: 'var(--background)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-md)',
        gap: 'var(--spacing-lg)',
        marginBottom: 'var(--spacing-xl)',
        flexWrap: 'wrap'
      }}
    >
      {/* Left: Title and Greeting */}
      <div style={{ minWidth: '200px' }}>
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
      
      {/* Center: AI Agents - Compact Horizontal */}
      <div 
        style={{ 
          display: 'flex', 
          gap: 'var(--spacing-xs)', 
          flex: 1,
          overflowX: 'auto',
          maxWidth: '600px',
          padding: '4px 0'
        }}
      >
        {AI_AGENTS.map(agent => (
          <div
            key={agent.id}
            title={`${agent.name} - ${agent.role}`}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-xs)',
              padding: 'var(--spacing-xs) var(--spacing-sm)',
              borderRadius: 'var(--radius-md)',
              background: 'var(--muted)',
              border: '1px solid var(--border)',
              transition: 'all var(--transition-base)',
              cursor: 'pointer',
              minWidth: 'fit-content',
              whiteSpace: 'nowrap'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--background-secondary)'
              e.currentTarget.style.borderColor = agent.color
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = 'var(--shadow-md)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--muted)'
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div
              style={{
                width: '28px',
                height: '28px',
                borderRadius: 'var(--radius-full)',
                background: `${agent.color}20`,
                border: `2px solid ${agent.color}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 'var(--font-weight-bold)',
                color: agent.color,
                flexShrink: 0
              }}
            >
              {agent.name[0]}
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
              <span
                style={{
                  fontSize: 'var(--font-size-sm)',
                  fontWeight: 'var(--font-weight-semibold)',
                  color: 'var(--foreground)'
                }}
              >
                {agent.name}
              </span>
              <span
                style={{
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 'var(--font-weight-bold)',
                  color: agent.color
                }}
              >
                {agent.value}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {/* Right: Actions */}
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

