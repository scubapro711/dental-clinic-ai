import React from 'react';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

/**
 * AgentPageLayout Component
 * 
 * Shared layout for all agent detail pages.
 * Maintains consistent design with dashboard (gradient background, white cards).
 * Applies agent-specific color theming.
 * 
 * @param {Object} props
 * @param {Object} props.agent - Agent info {id, name, role, color}
 * @param {React.ReactNode} props.children - Page content
 */
const AgentPageLayout = ({ agent, children }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header with Breadcrumb */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
            <button
              onClick={() => navigate('/clinic/dashboard')}
              className="hover:text-gray-900 transition-colors"
            >
              Dashboard
            </button>
            <span>/</span>
            <span className="text-gray-900 font-medium">{agent.name}</span>
          </div>

          {/* Agent Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Back Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/clinic/dashboard')}
                className="gap-2"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </Button>

              {/* Agent Info */}
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-white text-xl font-bold shadow-lg"
                  style={{ backgroundColor: agent.color }}
                >
                  {agent.name.charAt(0)}
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{agent.name}</h1>
                  <p className="text-sm text-gray-600">{agent.role}</p>
                </div>
              </div>
            </div>

            {/* Agent Status Badge */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Active
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </div>
    </div>
  );
};

AgentPageLayout.propTypes = {
  agent: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    role: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
  }).isRequired,
  children: PropTypes.node.isRequired,
};

export default AgentPageLayout;
