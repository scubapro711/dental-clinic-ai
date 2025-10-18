import React from 'react';
import PropTypes from 'prop-types';
import './StatCard.css';

/**
 * StatCard Component - Production Version
 * 
 * Displays statistical data with optional comparison and breakdown.
 * Used for showing counts, percentages, and other numerical data.
 * 
 * Features:
 * - Large number display
 * - Label and description
 * - Comparison data (vs previous period)
 * - Breakdown list (optional)
 * - Color customization
 * - Icon support
 * 
 * @param {Object} props
 * @param {string|number} props.value - Main statistic value
 * @param {string} props.label - Stat label
 * @param {string} props.description - Additional description
 * @param {string} props.icon - Icon emoji
 * @param {string} props.color - Accent color (hex)
 * @param {Object} props.comparison - Comparison data {value: '+15%', label: 'vs last month', positive: true}
 * @param {Array} props.breakdown - Breakdown items [{label: 'Type A', value: '45%'}, ...]
 * @param {Function} props.onClick - Click handler (optional)
 */
const StatCard = ({
  value,
  label,
  description,
  icon,
  color = '#3b82f6',
  comparison,
  breakdown,
  onClick
}) => {
  return (
    <div 
      className={`stat-card ${onClick ? 'stat-card-clickable' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={{ '--accent-color': color }}
    >
      <div className="stat-card-header">
        {icon && (
          <div className="stat-icon" style={{ backgroundColor: `${color}20` }}>
            <span style={{ color }}>{icon}</span>
          </div>
        )}
        <div className="stat-header-text">
          <h4 className="stat-label">{label}</h4>
          {description && (
            <p className="stat-description">{description}</p>
          )}
        </div>
      </div>

      <div className="stat-value">{value}</div>

      {comparison && (
        <div className={`stat-comparison ${comparison.positive ? 'positive' : 'negative'}`}>
          <span className="comparison-value">{comparison.value}</span>
          {comparison.label && (
            <span className="comparison-label">{comparison.label}</span>
          )}
        </div>
      )}

      {breakdown && breakdown.length > 0 && (
        <div className="stat-breakdown">
          {breakdown.map((item, index) => (
            <div key={index} className="breakdown-item">
              <span className="breakdown-label">{item.label}</span>
              <span className="breakdown-value">{item.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

StatCard.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  label: PropTypes.string.isRequired,
  description: PropTypes.string,
  icon: PropTypes.string,
  color: PropTypes.string,
  comparison: PropTypes.shape({
    value: PropTypes.string.isRequired,
    label: PropTypes.string,
    positive: PropTypes.bool,
  }),
  breakdown: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    })
  ),
  onClick: PropTypes.func,
};

export default StatCard;

