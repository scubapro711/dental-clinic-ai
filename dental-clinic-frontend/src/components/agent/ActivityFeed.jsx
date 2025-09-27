import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, Activity, Clock, User, AlertCircle, CheckCircle, XCircle, Zap } from 'lucide-react';

const ActivityFeed = ({ 
  activities = [], 
  onActivityClick = () => {}, 
  websocketUrl = null,
  maxActivities = 1000 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [isConnected, setIsConnected] = useState(false);
  const [realtimeActivities, setRealtimeActivities] = useState(activities);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!websocketUrl) return;

    const ws = new WebSocket(websocketUrl);
    
    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const newActivity = JSON.parse(event.data);
        setRealtimeActivities(prev => {
          const updated = [newActivity, ...prev];
          return updated.slice(0, maxActivities); // Keep only the latest activities
        });
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [websocketUrl, maxActivities]);

  // Update activities when props change
  useEffect(() => {
    setRealtimeActivities(activities.slice(0, maxActivities));
  }, [activities, maxActivities]);

  // Get unique agents and activity types for filters
  const { uniqueAgents, uniqueTypes } = useMemo(() => {
    const agents = new Set();
    const types = new Set();
    
    realtimeActivities.forEach(activity => {
      if (activity.agent) agents.add(activity.agent);
      if (activity.type) types.add(activity.type);
    });

    return {
      uniqueAgents: Array.from(agents),
      uniqueTypes: Array.from(types)
    };
  }, [realtimeActivities]);

  // Filter activities based on search and filters
  const filteredActivities = useMemo(() => {
    return realtimeActivities.filter(activity => {
      const matchesSearch = !searchTerm || 
        activity.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        activity.description?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesAgent = selectedAgent === 'all' || activity.agent === selectedAgent;
      const matchesType = selectedType === 'all' || activity.type === selectedType;

      return matchesSearch && matchesAgent && matchesType;
    });
  }, [realtimeActivities, searchTerm, selectedAgent, selectedType]);

  // Get activity icon based on type
  const getActivityIcon = (type, status) => {
    const iconProps = { size: 16, className: "flex-shrink-0" };
    
    switch (type) {
      case 'appointment':
        return <Clock {...iconProps} className="text-blue-500" />;
      case 'patient':
        return <User {...iconProps} className="text-green-500" />;
      case 'system':
        return <Activity {...iconProps} className="text-purple-500" />;
      case 'error':
        return <AlertCircle {...iconProps} className="text-red-500" />;
      default:
        if (status === 'completed') return <CheckCircle {...iconProps} className="text-green-500" />;
        if (status === 'failed') return <XCircle {...iconProps} className="text-red-500" />;
        return <Zap {...iconProps} className="text-gray-500" />;
    }
  };

  // Get status badge color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('he-IL', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Activity size={20} />
            פיד פעילות הסוכן
          </h2>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'מחובר' : 'לא מחובר'}
            </span>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="space-y-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="חיפוש פעילויות..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filters */}
          <div className="flex gap-3">
            <div className="flex-1">
              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              >
                <option value="all">כל הסוכנים</option>
                {uniqueAgents.map(agent => (
                  <option key={agent} value={agent}>{agent}</option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              >
                <option value="all">כל הסוגים</option>
                {uniqueTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Activity List */}
      <div className="flex-1 overflow-y-auto">
        {filteredActivities.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Activity size={48} className="mb-4 opacity-50" />
            <p className="text-lg font-medium">אין פעילויות להצגה</p>
            <p className="text-sm">נסה לשנות את הפילטרים או חכה לפעילויות חדשות</p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {filteredActivities.map((activity, index) => (
              <div
                key={activity.id || index}
                onClick={() => onActivityClick(activity)}
                className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 cursor-pointer group"
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className="mt-1">
                    {getActivityIcon(activity.type, activity.status)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                        {activity.title || 'פעילות ללא כותרת'}
                      </h3>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {activity.status && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                            {activity.status}
                          </span>
                        )}
                        <span className="text-xs text-gray-500">
                          {formatTime(activity.timestamp)}
                        </span>
                      </div>
                    </div>

                    {activity.description && (
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                        {activity.description}
                      </p>
                    )}

                    {/* Metadata */}
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      {activity.agent && (
                        <span className="flex items-center gap-1">
                          <User size={12} />
                          {activity.agent}
                        </span>
                      )}
                      {activity.type && (
                        <span className="flex items-center gap-1">
                          <Filter size={12} />
                          {activity.type}
                        </span>
                      )}
                      {activity.duration && (
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          {activity.duration}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            מציג {filteredActivities.length} מתוך {realtimeActivities.length} פעילויות
          </span>
          {isConnected && (
            <span className="flex items-center gap-1 text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              עדכונים בזמן אמת
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ActivityFeed;
