/**
 * DashboardHeader v7.0 - Compact Header with Horizontal Agent Cards
 * 
 * Features:
 * - Compact, normal-sized top bar
 * - Horizontal rectangular agent cards (wider than tall)
 * - Responsive design with scroll for agents
 * - Professional card design
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
        padding: '12px 20px',
        background: 'var(--background)',
        border: 'none',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'none',
        gap: '20px',
        marginBottom: 'var(--spacing-lg)',
        flexWrap: 'wrap',
        minHeight: '60px'
      }}
    >
      {/* Left: Title and Greeting - Compact */}
      <div style={{ minWidth: '200px' }}>
        <h1 
          className="dashboard-title"
          style={{
            fontSize: '24px',
            fontWeight: '700',
            color: 'var(--foreground)',
            margin: '0 0 4px 0'
          }}
        >
          Dashboard
        </h1>
        <p 
          style={{
            fontSize: '13px',
            color: 'var(--foreground-tertiary)',
            margin: '0'
          }}
        >
          Welcome back, <span style={{ fontWeight: '500', color: 'var(--foreground-secondary)' }}>
            {userInfo?.name || 'User'}
          </span>
          {userInfo?.role && (
            <span style={{ marginLeft: '6px' }}>
              • {userInfo.role}
            </span>
          )}
        </p>
      </div>
      
      {/* Right: AI Agents - Horizontal Rectangles */}
      <div 
        style={{ 
          display: 'flex', 
          gap: '10px', 
          flex: 1,
          overflowX: 'auto',
          padding: '2px 4px',
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
              flexDirection: 'row',
              alignItems: 'center',
              gap: '10px',
              padding: '8px 14px',
              borderRadius: '8px',
              background: 'white',
              border: '1px solid var(--border)',
              boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
              minWidth: 'fit-content',
              height: '44px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)'
              e.currentTarget.style.borderColor = agent.color
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.05)'
              e.currentTarget.style.borderColor = 'var(--border)'
            }}
          >
            {/* Agent Avatar - Compact */}
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: `${agent.color}15`,
                border: `2px solid ${agent.color}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: '700',
                color: agent.color,
                flexShrink: 0
              }}
            >
              {agent.icon}
            </div>
            
            {/* Agent Info - Horizontal */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <div
                style={{
                  fontSize: '15px',
                  fontWeight: '700',
                  color: agent.color,
                  lineHeight: '1'
                }}
              >
                {agent.value}
              </div>
              <div
                style={{
                  fontSize: '12px',
                  fontWeight: '500',
                  color: 'var(--foreground-secondary)',
                  lineHeight: '1'
                }}
              >
                {agent.name}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
