import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

/**
 * AgentApprovals Component
 * 
 * Displays pending approvals for a specific agent.
 * Fetches from /api/v1/decisions/pending and filters by agent.
 * Allows approve/reject actions.
 * 
 * @param {Object} props
 * @param {string} props.agentId - Agent ID to filter decisions
 * @param {string} props.agentColor - Agent theme color
 */
const AgentApprovals = ({ agentId, agentColor }) => {
  const [decisions, setDecisions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);

  useEffect(() => {
    fetchDecisions();
    // Refresh every 30 seconds
    const interval = setInterval(fetchDecisions, 30000);
    return () => clearInterval(interval);
  }, [agentId]);

  const fetchDecisions = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/decisions/pending', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });

      if (response.ok) {
        const data = await response.json();
        // Filter decisions for this agent
        const agentDecisions = data.decisions.filter(d => d.agent_id === agentId);
        setDecisions(agentDecisions);
      }
    } catch (error) {
      console.error('Error fetching decisions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (decisionId) => {
    setProcessingId(decisionId);
    try {
      const response = await fetch(`/api/v1/decisions/${decisionId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });

      if (response.ok) {
        // Remove from list
        setDecisions(prev => prev.filter(d => d.id !== decisionId));
      }
    } catch (error) {
      console.error('Error approving decision:', error);
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (decisionId) => {
    setProcessingId(decisionId);
    try {
      const response = await fetch(`/api/v1/decisions/${decisionId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });

      if (response.ok) {
        // Remove from list
        setDecisions(prev => prev.filter(d => d.id !== decisionId));
      }
    } catch (error) {
      console.error('Error rejecting decision:', error);
    } finally {
      setProcessingId(null);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div
            className="p-2 rounded-lg"
            style={{ backgroundColor: `${agentColor}20` }}
          >
            <AlertCircle className="w-5 h-5" style={{ color: agentColor }} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Pending Approvals</h2>
            <p className="text-sm text-gray-500">
              {decisions.length} {decisions.length === 1 ? 'decision' : 'decisions'} awaiting review
            </p>
          </div>
        </div>
      </div>

      {/* Decisions List */}
      {decisions.length === 0 ? (
        <div className="text-center py-12">
          <CheckCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No pending approvals</p>
          <p className="text-sm text-gray-400 mt-1">All caught up!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {decisions.map((decision) => (
            <div
              key={decision.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
            >
              {/* Decision Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{decision.title}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getPriorityColor(decision.priority)}`}>
                      {decision.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{decision.description}</p>
                </div>
              </div>

              {/* Decision Details */}
              <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(decision.created_at).toLocaleString()}
                </div>
                {decision.context && (
                  <div className="text-gray-400">
                    {decision.context}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  onClick={() => handleApprove(decision.id)}
                  disabled={processingId === decision.id}
                  size="sm"
                  className="gap-2 bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="w-4 h-4" />
                  Approve
                </Button>
                <Button
                  onClick={() => handleReject(decision.id)}
                  disabled={processingId === decision.id}
                  size="sm"
                  variant="outline"
                  className="gap-2 text-red-600 border-red-200 hover:bg-red-50"
                >
                  <XCircle className="w-4 h-4" />
                  Reject
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

AgentApprovals.propTypes = {
  agentId: PropTypes.string.isRequired,
  agentColor: PropTypes.string.isRequired,
};

export default AgentApprovals;
