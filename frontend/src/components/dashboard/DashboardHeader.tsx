/**
 * DashboardHeader v6.0 - Enhanced Dashboard Header with Prominent Agent Cards
 * 
 * Features:
 * - Single row layout: Title | AI Agents
 * - User greeting with role display
 * - Large, prominent AI Agent cards with enhanced styling
 * - Responsive design with scroll for agents on smaller screens
 * - Professional card design with better visual hierarchy
 */

import { getUserInfo } from '../../utils/rbac'

const AI_AGENTS = [
  { id: 'harper', name: 'Harper', role: 'Compliance', value: '96%', color: '#10b981', icon: 'H' },
  { id: 'sophia', name: 'Sophia', role: 'Scheduling', value: '8', color: '#f59e0b', icon: 'S' },
  { id: 'marcus', name: 'Marcus', role: 'Financial', value: '₪45,230', color: '#06b6d4', icon: 'M' },
  { id: 'sarah', name: 'Sarah', role: 'Clinical Support', value: '98%', color: '#8b5cf6', icon: 'S' },
  { id: 'alex', name: 'Alex', role: 'Patient Experience', value: '247', color: '#3b82f6', icon: 'A' }
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
        gap: 'var(--spacing-xl)',
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
      
      {/* Right: AI Agents - Large Prominent Cards */}
      <div 
        style={{ 
          display: 'flex', 
          gap: 'var(--spacing-md)', 
          flex: 1,
          overflowX: 'auto',
          padding: '4px 8px',
          background: 'transparent',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
          WebkitOverflowScrolling: 'touch',
          justifyContent: 'flex-end'
        }}
        className="ai-agents-container"
      >
        {AI_AGENTS.map(agent => (
          <div
            key={agent.id}
            title={`${agent.name} - ${agent.role}`}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 'var(--spacing-xs)',
              padding: 'var(--spacing-md)',
              borderRadius: 'var(--radius-lg)',
              background: 'white',
              border: '1px solid var(--border)',
              boxShadow: '0 2px 4px rgba(0,0,0,0.06)',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
              minWidth: '110px',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)'
              e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.12)'
              e.currentTarget.style.borderColor = agent.color
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.06)'
              e.currentTarget.style.borderColor = 'var(--border)'
            }}
          >
            {/* Agent Avatar - Larger */}
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: 'var(--radius-full)',
                background: `${agent.color}15`,
                border: `3px solid ${agent.color}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 'var(--font-size-lg)',
                fontWeight: 'var(--font-weight-bold)',
                color: agent.color,
                flexShrink: 0,
                marginBottom: 'var(--spacing-xs)'
              }}
            >
              {agent.icon}
            </div>
            
            {/* Agent Value - Prominent */}
            <div
              style={{
                fontSize: 'var(--font-size-lg)',
                fontWeight: 'var(--font-weight-bold)',
                color: agent.color,
                lineHeight: '1.2'
              }}
            >
              {agent.value}
            </div>
            
            {/* Agent Name */}
            <div
              style={{
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--foreground)',
                textAlign: 'center'
              }}
            >
              {agent.name}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
