/**
 * AgentsGrid Component
 * 
 * Displays all 5 AI agents in a responsive grid layout.
 * Manages agent selection and active state.
 * 
 * @component
 */

import PropTypes from 'prop-types';
import { AGENTS } from '../../data/agents';
import AgentCard from './AgentCard';

/**
 * AgentsGrid Component
 * 
 * @param {Object} props
 * @param {string} [props.activeAgentId] - ID of currently active agent
 * @param {Function} [props.onAgentClick] - Callback when agent is clicked
 * @param {string} [props.className] - Additional CSS classes
 */
export function AgentsGrid({ 
  activeAgentId,
  onAgentClick,
  className = ''
}) {
  return (
    <section 
      className={`agents-grid-container ${className}`}
      aria-label="AI Agents"
    >
      <div className="agents-grid-header">
        <h2 className="agents-grid-title">AI Agents</h2>
        <p className="agents-grid-subtitle">
          Your intelligent team working 24/7 to optimize clinic operations
        </p>
      </div>
      
      <div className="agents-grid" role="group" aria-label="Available AI agents">
        {AGENTS.map(agent => (
          <AgentCard
            key={agent.id}
            agent={agent}
            isActive={activeAgentId === agent.id}
            onClick={onAgentClick}
          />
        ))}
      </div>
      
      {/* Active Agent Info */}
      {activeAgentId && (
        <div className="agents-grid-active-info" role="status" aria-live="polite">
          <span className="agents-grid-active-label">Currently Active:</span>
          <span className="agents-grid-active-agent">
            {AGENTS.find(a => a.id === activeAgentId)?.name || 'Unknown'}
          </span>
        </div>
      )}
    </section>
  );
}

AgentsGrid.propTypes = {
  activeAgentId: PropTypes.string,
  onAgentClick: PropTypes.func,
  className: PropTypes.string
};

export default AgentsGrid;

