import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Activity, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import API_CONFIG from '@/config/api';

/**
 * AgentStatsGrid Component
 * 
 * Displays 4 key metrics for a specific agent.
 * Fetches real-time data from /api/v1/agents/activity endpoint.
 * 
 * @param {Object} props
 * @param {string} props.agentId - Agent ID (lowercase, e.g., 'alex')
 * @param {string} props.agentColor - Agent theme color
 */
const AgentStatsGrid = ({ agentId, agentColor }) => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAgentStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchAgentStats, 30000);
    return () => clearInterval(interval);
  }, [agentId]);

  const fetchAgentStats = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(API_CONFIG.endpoint('agents/activity'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });

      if (response.ok) {
        const data = await response.json();
        // Find this agent's stats
        const agentData = data.agents.find(a => a.id === agentId);
        if (agentData) {
          setStats(agentData);
        }
      }
    } catch (error) {
      console.error('Error fetching agent stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  const statCards = [
    {
      title: 'Tasks Today',
      value: stats.tasksToday,
      icon: <Activity className="w-5 h-5" />,
      subtitle: `${stats.tasksCompleted} completed`,
      color: agentColor
    },
    {
      title: 'Success Rate',
      value: `${stats.successRate}%`,
      icon: <CheckCircle className="w-5 h-5" />,
      subtitle: 'Completion rate',
      color: agentColor
    },
    {
      title: 'Avg Response',
      value: stats.avgResponseTime,
      icon: <Clock className="w-5 h-5" />,
      subtitle: 'Response time',
      color: agentColor
    },
    {
      title: 'Status',
      value: stats.status === 'active' ? 'Active' : 'Idle',
      icon: <TrendingUp className="w-5 h-5" />,
      subtitle: 'Current state',
      color: stats.status === 'active' ? '#10b981' : '#6b7280'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {statCards.map((stat, index) => (
        <div
          key={index}
          className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-600">{stat.title}</span>
            <div
              className="p-2 rounded-lg"
              style={{ backgroundColor: `${stat.color}20` }}
            >
              <div style={{ color: stat.color }}>
                {stat.icon}
              </div>
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {stat.value}
          </div>
          <div className="text-xs text-gray-500">
            {stat.subtitle}
          </div>
        </div>
      ))}
    </div>
  );
};

AgentStatsGrid.propTypes = {
  agentId: PropTypes.string.isRequired,
  agentColor: PropTypes.string.isRequired,
};

export default AgentStatsGrid;
