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

  // Get emoji for agent
  const getAgentEmoji = (agentId) => {
    const emojiMap = {
      'alex': '👤',
      'sarah': '🏥',
      'marcus': '💰',
      'sophia': '📅',
      'harper': '🛡️'
    };
    return emojiMap[agentId] || '🤖';
  };
  
  if (isActive) {
    // Expanded state - shows full details
    return (
      <div 
        className="agent-sidebar-card agent-sidebar-card-expanded bg-white text-blue-700 rounded-lg px-4 py-3 cursor-pointer transition-all duration-200 shadow-lg"
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        aria-label={`${agent.name} - ${agent.role} (Active)`}
        aria-pressed={true}
      >
        <div className="flex items-start space-x-3">
          {/* Agent Emoji */}
          <span className="text-2xl flex-shrink-0" aria-hidden="true">
            {getAgentEmoji(agent.id)}
          </span>
          
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
    >
      <div className="flex items-center justify-between">
        {/* Agent Emoji + Name */}
        <div className="flex items-center space-x-2 flex-1 min-w-0">
          <span className="text-lg flex-shrink-0" aria-hidden="true">
            {getAgentEmoji(agent.id)}
          </span>
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

