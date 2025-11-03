/**
 * DashboardHeader v5.0 - Simplified Dashboard Header
 * 
 * Features:
 * - Single row layout: Title | AI Agents
 * - User greeting with role display
 * - AI Agents horizontal display
 * - Responsive design with scroll for agents on smaller screens
 * - No edit mode - always editable
 * - No Done/Reset buttons
 */

import { getUserInfo } from '../../utils/rbac'

const AI_AGENTS = [
  { id: 'alex', name: 'Alex', role: 'Patient Experience', value: '247', color: '#3b82f6' },
  { id: 'sarah', name: 'Sarah', role: 'Clinical Support', value: '98%', color: '#8b5cf6' },
  { id: 'marcus', name: 'Marcus', role: 'Financial', value: '₪45,230', color: '#06b6d4' },
  { id: 'sophia', name: 'Sophia', role: 'Scheduling', value: '8', color: '#f59e0b' },
  { id: 'harper', name: 'Harper', role: 'Compliance', value: '96%', color: '#10b981' }
]

export function DashboardHeader() {
  const userInfo = getUserInfo()
  
  return (
    <div 
      className="dashboard-header"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 'var(--spacing-lg)',
        background: 'var(--background)',
        border: 'none',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'none',
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
      
      {/* Right: AI Agents - Compact Horizontal */}
      <div 
        style={{ 
          display: 'flex', 
          gap: 'var(--spacing-xs)', 
          flex: 1,
          overflowX: 'auto',
          maxWidth: '600px',
          padding: '0 8px',
          background: 'transparent',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
          WebkitOverflowScrolling: 'touch'
        }}
        className="ai-agents-container"
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
              transition: 'all var(--transition-base)',
              cursor: 'pointer',
              minWidth: 'fit-content',
              whiteSpace: 'nowrap'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--background-secondary)'
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = 'var(--shadow-md)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--muted)'
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
    </div>
  )
}
