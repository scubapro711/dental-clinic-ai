import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { BarChart3, TrendingUp, Activity } from 'lucide-react';
import API_CONFIG from '@/config/api';

/**
 * AgentDataViz Component
 * 
 * Displays data visualizations and charts for agent performance.
 * Shows activity trends, task completion rates, and other metrics.
 * 
 * @param {Object} props
 * @param {string} props.agentId - Agent ID
 * @param {string} props.agentColor - Agent theme color
 */
const AgentDataViz = ({ agentId, agentColor }) => {
  const [chartData, setChartData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchChartData();
  }, [agentId]);

  const fetchChartData = async () => {
    setIsLoading(true);
    try {
      // Fetch agent activity data
      const response = await fetch(API_CONFIG.endpoint('agents/activity'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });

      if (response.ok) {
        const data = await response.json();
        const agentData = data.agents.find(a => a.id === agentId);
        
        // Generate mock weekly data for visualization
        // In production, this would come from backend analytics endpoint
        const weeklyData = generateWeeklyData(agentData);
        setChartData(weeklyData);
      }
    } catch (error) {
      console.error('Error fetching chart data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateWeeklyData = (agentData) => {
    // Generate last 7 days of data
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const today = new Date().getDay();
    
    return Array.from({ length: 7 }, (_, i) => {
      const dayIndex = (today - 6 + i + 7) % 7;
      return {
        day: days[dayIndex],
        tasks: Math.floor(Math.random() * 20) + 5,
        completed: Math.floor(Math.random() * 18) + 3,
      };
    });
  };

  if (isLoading || !chartData) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const maxValue = Math.max(...chartData.map(d => d.tasks));

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div
          className="p-2 rounded-lg"
          style={{ backgroundColor: `${agentColor}20` }}
        >
          <BarChart3 className="w-5 h-5" style={{ color: agentColor }} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Activity Trends</h2>
          <p className="text-sm text-gray-500">Last 7 days performance</p>
        </div>
      </div>

      {/* Bar Chart */}
      <div className="space-y-4 mb-6">
        {chartData.map((data, index) => {
          const taskPercentage = (data.tasks / maxValue) * 100;
          const completedPercentage = (data.completed / maxValue) * 100;

          return (
            <div key={index}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">{data.day}</span>
                <span className="text-xs text-gray-500">
                  {data.completed}/{data.tasks} completed
                </span>
              </div>
              <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                {/* Total tasks bar */}
                <div
                  className="absolute h-full transition-all duration-300"
                  style={{
                    width: `${taskPercentage}%`,
                    backgroundColor: `${agentColor}30`
                  }}
                />
                {/* Completed tasks bar */}
                <div
                  className="absolute h-full transition-all duration-300"
                  style={{
                    width: `${completedPercentage}%`,
                    backgroundColor: agentColor
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded"
            style={{ backgroundColor: agentColor }}
          />
          <span className="text-gray-600">Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded"
            style={{ backgroundColor: `${agentColor}30` }}
          />
          <span className="text-gray-600">Total Tasks</span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t">
        <div className="text-center">
          <div className="text-2xl font-bold" style={{ color: agentColor }}>
            {chartData.reduce((sum, d) => sum + d.tasks, 0)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Total Tasks</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {chartData.reduce((sum, d) => sum + d.completed, 0)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Completed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {Math.round(
              (chartData.reduce((sum, d) => sum + d.completed, 0) /
                chartData.reduce((sum, d) => sum + d.tasks, 0)) *
                100
            )}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Success Rate</div>
        </div>
      </div>
    </div>
  );
};

AgentDataViz.propTypes = {
  agentId: PropTypes.string.isRequired,
  agentColor: PropTypes.string.isRequired,
};

export default AgentDataViz;
