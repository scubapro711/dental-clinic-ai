/**
 * AgentSidebarCard Component
 * 
 * Compact agent card for sidebar with two states:
 * - Mini: Single line with icon, name, and primary metric
 * - Expanded: Two lines with icon, name, role, metric, and trend
 * 
 * @component
 */

import { Sparkles, Stethoscope, DollarSign, Calendar, Shield, TrendingUp, TrendingDown } from 'lucide-react';
import PropTypes from 'prop-types';

// Icon mapping for agent types
const AGENT_ICONS = {
  Sparkles,
  Stethoscope,
  DollarSign,
  Calendar,
  Shield
};

/**
 * AgentSidebarCard Component
 * 
 * @param {Object} props
 * @param {Object} props.agent - Agent data object
 * @param {boolean} [props.isActive=false] - Whether agent is currently active/expanded
 * @param {Function} [props.onClick] - Click handler
 * @param {Object} [props.metrics] - Metrics to display on the card
 */
export function AgentSidebarCard({ 
  agent, 
  isActive = false, 
  onClick,
  metrics
}) {
  // Get icon component
  const IconComponent = AGENT_ICONS[agent.icon] || Sparkles;
  
  // Handle click
  const handleClick = () => {
    if (onClick) {
      onClick(agent);
    }
  };
  
  // Handle keyboard interaction
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  // Get color for agent
  const getAgentColor = (agentId) => {
    const colorMap = {
      'alex': '#4F46E5',     // Indigo
      'sarah': '#10B981',    // Emerald
      'marcus': '#F59E0B',   // Amber
      'sophia': '#8B5CF6',   // Violet
      'harper': '#EF4444'    // Red
    };
    return colorMap[agentId] || '#6B7280';
  };
  
  if (isActive) {
    // Expanded state - shows full details
    return (
      <div 
        className="agent-sidebar-card agent-sidebar-card-expanded bg-white text-blue-700 rounded-lg px-4 py-3 cursor-pointer transition-all duration-200 shadow-lg ring-2 ring-blue-400"
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        aria-label={`${agent.name} - ${agent.role} (Active)`}
        aria-pressed={true}
        style={{ '--agent-color': getAgentColor(agent.id) }}
      >
        <div className="flex items-start space-x-3">
          {/* Agent Icon */}
          <div 
            className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: getAgentColor(agent.id) }}
          >
            <IconComponent className="w-5 h-5 text-white" aria-hidden="true" />
          </div>
          
          {/* Agent Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-blue-700 truncate">
                {agent.name}
              </h3>
              {metrics && (
                <span className="text-lg font-bold text-blue-700 ml-2">
                  {metrics.value}
                </span>
              )}
            </div>
            <p className="text-xs text-blue-600 mt-0.5">
              {agent.role}
            </p>
            {metrics && metrics.trend && (
              <div className="flex items-center space-x-1 mt-1">
                {metrics.trend.direction === 'up' ? (
                  <TrendingUp className="w-3 h-3 text-green-600" aria-hidden="true" />
                ) : (
                  <TrendingDown className="w-3 h-3 text-red-600" aria-hidden="true" />
                )}
                <span className={`text-xs font-medium ${
                  metrics.trend.direction === 'up' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {metrics.trend.value}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
  
  // Mini state - single line
  return (
    <div 
      className="agent-sidebar-card agent-sidebar-card-mini text-white hover:bg-blue-700 rounded-lg px-4 py-2.5 cursor-pointer transition-all duration-200"
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label={`${agent.name} - ${agent.role}`}
      aria-pressed={false}
      style={{ '--agent-color': getAgentColor(agent.id) }}
    >
      <div className="flex items-center justify-between">
        {/* Agent Icon + Name */}
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <IconComponent className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
          <span className="text-sm font-medium truncate">
            {agent.name}
          </span>
        </div>
        
        {/* Metric Value */}
        {metrics && (
          <span className="text-sm font-semibold ml-2 flex-shrink-0">
            {metrics.value}
          </span>
        )}
      </div>
    </div>
  );
}

AgentSidebarCard.propTypes = {
  agent: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    role: PropTypes.string.isRequired,
    icon: PropTypes.string.isRequired,
    description: PropTypes.string,
    capabilities: PropTypes.arrayOf(PropTypes.string)
  }).isRequired,
  isActive: PropTypes.bool,
  onClick: PropTypes.func,
  metrics: PropTypes.shape({
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    label: PropTypes.string,
    trend: PropTypes.shape({
      direction: PropTypes.oneOf(['up', 'down']),
      value: PropTypes.string
    })
  })
};

export default AgentSidebarCard;

