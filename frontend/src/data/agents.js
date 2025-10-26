/**
 * DentaFlow AI Agents Configuration
 * 
 * Defines the 5 core AI agents with their visual identity,
 * roles, and capabilities.
 * 
 * @module data/agents
 */

export const AGENTS = [
  {
    id: 'alex',
    name: 'Alex',
    role: 'Patient Experience',
    color: '#4F46E5',
    colorName: 'indigo',
    icon: 'Sparkles',
    description: 'Handles patient communications, appointment scheduling, and experience optimization',
    capabilities: [
      'Appointment scheduling',
      'Patient communication',
      'Experience optimization',
      'Feedback collection'
    ]
  },
  {
    id: 'sarah',
    name: 'Sarah',
    role: 'Clinical Support',
    color: '#10B981',
    colorName: 'emerald',
    icon: 'Stethoscope',
    description: 'Assists with clinical documentation, treatment planning, and medical records',
    capabilities: [
      'Clinical documentation',
      'Treatment planning',
      'Medical records management',
      'Clinical decision support'
    ]
  },
  {
    id: 'marcus',
    name: 'Marcus',
    role: 'Financial & Billing',
    color: '#F59E0B',
    colorName: 'amber',
    icon: 'DollarSign',
    description: 'Manages billing, insurance claims, revenue optimization, and financial reporting',
    capabilities: [
      'Billing automation',
      'Insurance claims',
      'Revenue optimization',
      'Financial reporting'
    ]
  },
  {
    id: 'sophia',
    name: 'Sophia',
    role: 'Operations & Admin',
    color: '#8B5CF6',
    colorName: 'violet',
    icon: 'Calendar',
    description: 'Coordinates scheduling, inventory management, and administrative tasks',
    capabilities: [
      'Schedule coordination',
      'Inventory management',
      'Administrative automation',
      'Resource optimization'
    ]
  },
  {
    id: 'harper',
    name: 'Harper',
    role: 'HIPAA & Compliance',
    color: '#EF4444',
    colorName: 'red',
    icon: 'Shield',
    description: 'Ensures HIPAA compliance, data security, and regulatory adherence',
    capabilities: [
      'HIPAA compliance monitoring',
      'Data security',
      'Audit trail management',
      'Regulatory reporting'
    ]
  }
];

/**
 * Get agent by ID
 * @param {string} agentId - The agent identifier
 * @returns {Object|undefined} Agent object or undefined if not found
 */
export function getAgentById(agentId) {
  return AGENTS.find(agent => agent.id === agentId);
}

/**
 * Get agent color by ID
 * @param {string} agentId - The agent identifier
 * @returns {string} Hex color code
 */
export function getAgentColor(agentId) {
  const agent = getAgentById(agentId);
  return agent ? agent.color : '#6B7280'; // Default gray
}

/**
 * Get all agent IDs
 * @returns {string[]} Array of agent IDs
 */
export function getAllAgentIds() {
  return AGENTS.map(agent => agent.id);
}

