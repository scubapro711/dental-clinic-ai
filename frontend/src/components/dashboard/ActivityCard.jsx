import React from 'react';
import PropTypes from 'prop-types';
import './ActivityCard.css';

/**
 * ActivityCard Component - Production Version
 * 
 * Displays recent agent activities and actions.
 * Used to show real-time agent operations and system events.
 * 
 * Features:
 * - Agent attribution with color coding
 * - Timestamp display
 * - Action description
 * - Status indicator
 * - Click handler for details
 * 
 * @param {Object} props
 * @param {Object} props.agent - Agent info {name: 'Alex', color: '#3b82f6'}
 * @param {string} props.action - Action description
 * @param {string} props.details - Additional details (optional)
 * @param {string} props.timestamp - When the action occurred
 * @param {string} props.status - Status: 'success' | 'pending' | 'error'
 * @param {Function} props.onClick - Click handler (optional)
 */
const ActivityCard = ({
  agent,
  action,
  details,
  timestamp,
  status = 'success',
  onClick
}) => {
  const statusConfig = {
    success: {
      icon: '✓',
      className: 'status-success'
    },
    pending: {
      icon: '⏳',
      className: 'status-pending'
    },
    error: {
      icon: '✗',
      className: 'status-error'
    }
  };

  const config = statusConfig[status] || statusConfig.success;

  return (
    <div 
      className={`activity-card ${config.className} ${onClick ? 'activity-card-clickable' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="activity-card-left">
        <div 
          className="activity-agent-avatar" 
          style={{ backgroundColor: agent.color }}
        >
          {agent.name.charAt(0)}
        </div>
        <div className="activity-content">
          <div className="activity-header">
            <span className="activity-agent-name">{agent.name}</span>
            <span className="activity-timestamp">{timestamp}</span>
          </div>
          <p className="activity-action">{action}</p>
          {details && (
            <p className="activity-details">{details}</p>
          )}
        </div>
      </div>
      <div className="activity-status">
        <span className={`status-indicator ${config.className}`}>
          {config.icon}
        </span>
      </div>
    </div>
  );
};

ActivityCard.propTypes = {
  agent: PropTypes.shape({
    name: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
  }).isRequired,
  action: PropTypes.string.isRequired,
  details: PropTypes.string,
  timestamp: PropTypes.string.isRequired,
  status: PropTypes.oneOf(['success', 'pending', 'error']),
  onClick: PropTypes.func,
};

export default ActivityCard;

