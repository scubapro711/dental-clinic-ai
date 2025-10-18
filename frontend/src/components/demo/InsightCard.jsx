import React from 'react';
import { Card, CardContent } from '../ui/Card';
import './InsightCard.css';

/**
 * InsightCard - Display AI-generated insights with priority levels
 * Used for revenue opportunities, urgent treatments, inventory alerts, etc.
 */
const InsightCard = ({ 
  title,
  description,
  priority = 'medium', // 'high', 'medium', 'low', 'info'
  agent,
  agentColor,
  actionLabel,
  onAction,
  icon,
  className = ''
}) => {
  const getPriorityConfig = (priority) => {
    const configs = {
      high: { color: '#ff4444', emoji: '🔴', label: 'High Priority' },
      medium: { color: '#ffaa00', emoji: '🟡', label: 'Medium Priority' },
      low: { color: '#00aa00', emoji: '🟢', label: 'Low Priority' },
      info: { color: '#3b82f6', emoji: 'ℹ️', label: 'Info' }
    };
    return configs[priority] || configs.medium;
  };

  const priorityConfig = getPriorityConfig(priority);

  return (
    <Card 
      className={`insight-card insight-card--${priority} ${className}`}
      hover={!!onAction}
    >
      <CardContent>
        <div className="insight-card__header">
          <div className="insight-card__priority" style={{ color: priorityConfig.color }}>
            <span className="insight-card__priority-emoji">{priorityConfig.emoji}</span>
            <span className="insight-card__priority-label">{priorityConfig.label}</span>
          </div>
          {agent && (
            <div className="insight-card__agent" style={{ color: agentColor }}>
              🤖 {agent}
            </div>
          )}
        </div>

        <div className="insight-card__content">
          {icon && <div className="insight-card__icon">{icon}</div>}
          <h4 className="insight-card__title">{title}</h4>
          <p className="insight-card__description">{description}</p>
        </div>

        {actionLabel && onAction && (
          <div className="insight-card__footer">
            <button 
              className="insight-card__action-btn"
              onClick={onAction}
              style={{ borderColor: priorityConfig.color, color: priorityConfig.color }}
            >
              {actionLabel}
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default InsightCard;

