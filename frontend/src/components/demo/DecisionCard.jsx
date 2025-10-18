import React from 'react';
import { Card, CardContent } from '../ui/Card';
import './DecisionCard.css';

/**
 * DecisionCard - Display pending AI decisions with approve/reject actions
 * Used for appointment rescheduling, payment plans, treatment approvals, etc.
 */
const DecisionCard = ({ 
  title,
  description,
  agent,
  agentColor,
  priority = 'medium',
  timestamp,
  onApprove,
  onReject,
  approveLabel = 'Approve',
  rejectLabel = 'Reject',
  className = ''
}) => {
  const getPriorityConfig = (priority) => {
    const configs = {
      high: { color: '#ff4444', emoji: '🔴' },
      medium: { color: '#ffaa00', emoji: '🟡' },
      low: { color: '#00aa00', emoji: '🟢' }
    };
    return configs[priority] || configs.medium;
  };

  const priorityConfig = getPriorityConfig(priority);

  return (
    <Card className={`decision-card ${className}`}>
      <CardContent>
        <div className="decision-card__header">
          <div className="decision-card__agent-badge" style={{ backgroundColor: agentColor }}>
            {agent}
          </div>
          <div 
            className="decision-card__priority-badge"
            style={{ backgroundColor: priorityConfig.color }}
          >
            {priorityConfig.emoji} {priority}
          </div>
        </div>

        <div className="decision-card__content">
          <h4 className="decision-card__title">{title}</h4>
          <p className="decision-card__description">{description}</p>
        </div>

        <div className="decision-card__footer">
          <span className="decision-card__timestamp">{timestamp}</span>
          <div className="decision-card__actions">
            <button 
              className="decision-card__btn decision-card__btn--approve"
              onClick={onApprove}
            >
              ✓ {approveLabel}
            </button>
            <button 
              className="decision-card__btn decision-card__btn--reject"
              onClick={onReject}
            >
              ✗ {rejectLabel}
            </button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default DecisionCard;

