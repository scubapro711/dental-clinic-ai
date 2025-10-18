import React from 'react';
import { Card, CardContent } from '../ui/Card';
import './AgentCard.css';

/**
 * AgentCard - Display individual agent activity item
 * Used in the agent activity stream
 */
const AgentCard = ({ 
  agent,
  agentColor,
  action,
  patient,
  status = 'completed', // 'completed', 'in_progress', 'pending'
  timestamp,
  showDot = true,
  className = ''
}) => {
  const getStatusConfig = (status) => {
    const configs = {
      completed: { color: '#10b981', icon: '✓' },
      in_progress: { color: '#3b82f6', icon: '⟳' },
      pending: { color: '#ffaa00', icon: '⏳' }
    };
    return configs[status] || configs.completed;
  };

  const statusConfig = getStatusConfig(status);

  return (
    <div className={`agent-card ${className}`}>
      {showDot && (
        <div 
          className="agent-card__dot"
          style={{ backgroundColor: agentColor }}
        />
      )}
      
      <div className="agent-card__content">
        <div className="agent-card__header">
          <span className="agent-card__agent" style={{ color: agentColor }}>
            {agent}
          </span>
          {status === 'in_progress' && (
            <div className="agent-card__spinner"></div>
          )}
        </div>
        
        <div className="agent-card__action">{action}</div>
        
        {patient && (
          <div className="agent-card__patient">
            Patient: {patient}
          </div>
        )}
        
        <div className="agent-card__timestamp">{timestamp}</div>
      </div>

      <div 
        className="agent-card__status"
        style={{ color: statusConfig.color }}
      >
        {statusConfig.icon}
      </div>
    </div>
  );
};

export default AgentCard;

