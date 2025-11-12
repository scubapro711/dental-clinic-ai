/**
 * DashboardHeader v7.1 - Compact Header with Larger Horizontal Agent Cards
 * 
 * Features:
 * - Compact, normal-sized top bar
 * - Larger horizontal rectangular agent cards
 * - Responsive design with scroll for agents
 * - Professional card design
 */

import { getUserInfo } from '../../utils/rbac'
import { OrganizationSelector } from '../OrganizationSelector'
import { useNavigate } from 'react-router-dom'

const AI_AGENTS = [
  { id: 'harper', name: 'Harper', role: 'Compliance', value: '96%', color: '#10b981', icon: 'H' },
  { id: 'sophia', name: 'Sophia', role: 'Scheduling', value: '8', color: '#f59e0b', icon: 'S' },
  { id: 'marcus', name: 'Marcus', role: 'Financial', value: '₪45,230', color: '#06b6d4', icon: 'M' },
  { id: 'sarah', name: 'Sarah', role: 'Clinical Support', value: '98%', color: '#8b5cf6', icon: 'S' },
  { id: 'alex', name: 'Alex', role: 'Patient Experience', value: '247', color: '#3b82f6', icon: 'A' }
]

export function DashboardHeader() {
  const userInfo = getUserInfo()
  const navigate = useNavigate()
  
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
      {/* Left: Organization Selector (if multiple orgs) */}
      <OrganizationSelector />
      
      {/* Center: Title and Greeting - Compact */}
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
      
      {/* Right: AI Agents - Larger Horizontal Rectangles */}
      <div 
        style={{ 
          display: 'flex', 
          gap: '12px', 
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
            onClick={() => navigate(`/clinic/agents/${agent.id}`)}
            style={{
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              gap: '14px',
              padding: '12px 18px',
              borderRadius: '10px',
              background: 'white',
              border: '1.5px solid var(--border)',
              boxShadow: '0 2px 4px rgba(0,0,0,0.06)',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
              minWidth: 'fit-content',
              height: '56px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 12px rgba(0,0,0,0.12)'
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
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: `${agent.color}15`,
                border: `2.5px solid ${agent.color}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700',
                color: agent.color,
                flexShrink: 0
              }}
            >
              {agent.icon}
            </div>
            
            {/* Agent Info - Horizontal with larger text */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
              <div
                style={{
                  fontSize: '18px',
                  fontWeight: '700',
                  color: agent.color,
                  lineHeight: '1.1'
                }}
              >
                {agent.value}
              </div>
              <div
                style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: 'var(--foreground-secondary)',
                  lineHeight: '1.1'
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
