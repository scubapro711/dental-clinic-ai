import React from 'react';
import PropTypes from 'prop-types';
import './MetricCard.css';

/**
 * MetricCard Component - Production Version
 * 
 * Displays key metrics with trends, icons, and optional agent attribution.
 * Used in the main dashboard to show real-time clinic statistics.
 * 
 * Features:
 * - Icon support
 * - Trend indicators (up/down with percentage)
 * - Agent attribution (optional)
 * - Responsive design
 * - Hover effects
 * 
 * @param {Object} props
 * @param {string} props.title - Metric title
 * @param {string|number} props.value - Main metric value
 * @param {string} props.icon - Icon emoji or component
 * @param {Object} props.trend - Trend data {direction: 'up'|'down', value: '12%', label: 'from last month'}
 * @param {Object} props.agent - Agent info {name: 'Alex', color: '#3b82f6'}
 * @param {string} props.subtitle - Additional context
 * @param {Function} props.onClick - Click handler (optional)
 */
const MetricCard = ({ 
  title, 
  value, 
  icon, 
  trend, 
  agent, 
  subtitle,
  onClick 
}) => {
  return (
    <div 
      className={`metric-card ${onClick ? 'metric-card-clickable' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="metric-card-header">
        <span className="metric-icon">{icon}</span>
        <h3 className="metric-title">{title}</h3>
      </div>

      <div className="metric-value">{value}</div>

      {subtitle && (
        <p className="metric-subtitle">{subtitle}</p>
      )}

      {trend && (
        <div className={`metric-trend metric-trend-${trend.direction}`}>
          <span className="trend-indicator">
            {trend.direction === 'up' ? '↑' : '↓'}
          </span>
          <span className="trend-value">{trend.value}</span>
          {trend.label && (
            <span className="trend-label">{trend.label}</span>
          )}
        </div>
      )}

      {agent && (
        <div className="metric-agent">
          <span 
            className="agent-badge" 
            style={{ backgroundColor: agent.color }}
          >
            {agent.name}
          </span>
        </div>
      )}
    </div>
  );
};

MetricCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  icon: PropTypes.node.isRequired,
  trend: PropTypes.shape({
    direction: PropTypes.oneOf(['up', 'down']).isRequired,
    value: PropTypes.string.isRequired,
    label: PropTypes.string,
  }),
  agent: PropTypes.shape({
    name: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
  }),
  subtitle: PropTypes.string,
  onClick: PropTypes.func,
};

export default MetricCard;

