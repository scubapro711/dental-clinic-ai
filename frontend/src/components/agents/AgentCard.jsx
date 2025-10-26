/**
 * AgentCard Component
 * 
 * Displays an individual AI agent with visual identity, status, and interaction.
 * 
 * @component
 * @example
 * <AgentCard 
 *   agent={alexAgent} 
 *   isActive={true} 
 *   onClick={handleAgentClick}
 * />
 */

import { Sparkles, Stethoscope, DollarSign, Calendar, Shield } from 'lucide-react';
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
 * AgentCard Component
 * 
 * @param {Object} props
 * @param {Object} props.agent - Agent data object
 * @param {string} props.agent.id - Agent unique identifier
 * @param {string} props.agent.name - Agent display name
 * @param {string} props.agent.role - Agent role/responsibility
 * @param {string} props.agent.icon - Icon name from lucide-react
 * @param {string} props.agent.description - Agent description
 * @param {boolean} [props.isActive=false] - Whether agent is currently active
 * @param {Function} [props.onClick] - Click handler
 * @param {string} [props.className] - Additional CSS classes
 */
export function AgentCard({ 
  agent, 
  isActive = false, 
  onClick,
  className = ''
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
  
  return (
    <div 
      className={`agent-card agent-card-${agent.id} ${isActive ? 'agent-card-active' : ''} ${className}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label={`${agent.name} - ${agent.role}${isActive ? ' (Active)' : ''}`}
      aria-pressed={isActive}
    >
      {/* Agent Avatar */}
      <div className={`agent-avatar agent-avatar-${agent.id}`}>
        <IconComponent 
          className="w-8 h-8 text-white" 
          aria-hidden="true"
        />
      </div>
      
      {/* Agent Info */}
      <div className="agent-info">
        <h3 className="agent-name">{agent.name}</h3>
        <p className="agent-role">{agent.role}</p>
      </div>
      
      {/* Active Status Indicator */}
      {isActive && (
        <div className="agent-status-active" aria-live="polite">
          <span className="agent-status-dot" aria-hidden="true"></span>
          <span className="agent-status-text">Active</span>
        </div>
      )}
      
      {/* Hover Tooltip */}
      <div className="agent-tooltip" role="tooltip">
        <p className="agent-tooltip-description">{agent.description}</p>
        {agent.capabilities && agent.capabilities.length > 0 && (
          <ul className="agent-tooltip-capabilities">
            {agent.capabilities.slice(0, 3).map((capability, index) => (
              <li key={index}>• {capability}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

AgentCard.propTypes = {
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
  className: PropTypes.string
};

export default AgentCard;

