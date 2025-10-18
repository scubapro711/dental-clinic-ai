import React from 'react';
import PropTypes from 'prop-types';
import './InsightCard.css';

/**
 * InsightCard Component - Production Version
 * 
 * Displays AI-generated insights with priority levels and agent attribution.
 * Used to show recommendations, alerts, and actionable insights.
 * 
 * Features:
 * - Priority levels (high, medium, low) with color coding
 * - Agent attribution with color coding
 * - Action button (optional)
 * - Icon support
 * - Responsive design
 * 
 * @param {Object} props
 * @param {string} props.title - Insight title
 * @param {string} props.description - Insight description
 * @param {string} props.priority - Priority level: 'high' | 'medium' | 'low'
 * @param {Object} props.agent - Agent info {name: 'Marcus', color: '#10b981'}
 * @param {string} props.icon - Icon emoji
 * @param {Object} props.action - Action button {label: 'View Details', onClick: function}
 * @param {string} props.timestamp - When the insight was generated
 */
const InsightCard = ({
  title,
  description,
  priority = 'medium',
  agent,
  icon,
  action,
  timestamp
}) => {
  const priorityConfig = {
    high: {
      label: 'High Priority',
      emoji: '🔴',
      className: 'priority-high'
    },
    medium: {
      label: 'Medium Priority',
      emoji: '🟡',
      className: 'priority-medium'
    },
    low: {
      label: 'Low Priority',
      emoji: '🟢',
      className: 'priority-low'
    }
  };

  const config = priorityConfig[priority] || priorityConfig.medium;

  return (
    <div className={`insight-card ${config.className}`}>
      <div className="insight-card-header">
        <div className="insight-header-left">
          {icon && <span className="insight-icon">{icon}</span>}
          <div className="insight-header-text">
            <h3 className="insight-title">{title}</h3>
            {timestamp && (
              <span className="insight-timestamp">{timestamp}</span>
            )}
          </div>
        </div>
        <div className="insight-priority-badge">
          <span className="priority-emoji">{config.emoji}</span>
          <span className="priority-label">{config.label}</span>
        </div>
      </div>

      <p className="insight-description">{description}</p>

      <div className="insight-card-footer">
        {agent && (
          <div className="insight-agent">
            <span 
              className="agent-badge-small" 
              style={{ backgroundColor: agent.color }}
            >
              🤖 {agent.name}
            </span>
          </div>
        )}

        {action && (
          <button 
            className="insight-action-btn"
            onClick={action.onClick}
          >
            {action.label}
          </button>
        )}
      </div>
    </div>
  );
};

InsightCard.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  priority: PropTypes.oneOf(['high', 'medium', 'low']),
  agent: PropTypes.shape({
    name: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
  }),
  icon: PropTypes.string,
  action: PropTypes.shape({
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
  }),
  timestamp: PropTypes.string,
};

export default InsightCard;

