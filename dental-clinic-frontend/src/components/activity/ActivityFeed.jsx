/**
 * Component 2.2: Real-time Activity Feed Frontend
 * 
 * This component provides a real-time, interactive feed of all agent activities.
 * It connects to the WebSocket infrastructure (Phase 1) and displays data from
 * the Activity Logger backend (Component 2.1).
 * 
 * Features:
 * - Real-time activity updates via WebSocket
 * - Filtering by agent and activity type
 * - Smooth animations and modern UI
 * - Professional design with hover states and micro-interactions
 */

import React, { useState, useEffect, useMemo } from 'react';
import { Clock, User, Activity, Filter, Search, ChevronDown } from 'lucide-react';

const ActivityFeed = ({ 
  websocketUrl = 'ws://localhost:8001/ws',
  maxActivities = 100,
  autoScroll = true 
}) => {
  // --- State Management ---
  const [activities, setActivities] = useState([]);
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // --- WebSocket Connection ---
  useEffect(() => {
    const ws = new WebSocket(websocketUrl);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('ActivityFeed: Connected to WebSocket');
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      // Handle agent activity messages
      if (message.type === 'agent_activity') {
        const newActivity = {
          id: message.payload.activity_id,
          agentId: message.payload.agent_id,
          type: message.payload.activity_type,
          title: message.payload.title,
          description: message.payload.description,
          timestamp: new Date(message.payload.timestamp * 1000),
          confidence: message.payload.confidence_score || 0.95
        };
        
        setActivities(prev => {
          const updated = [newActivity, ...prev];
          return updated.slice(0, maxActivities); // Keep only the latest activities
        });
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('ActivityFeed: Disconnected from WebSocket');
    };
    
    ws.onerror = (error) => {
      console.error('ActivityFeed: WebSocket error:', error);
      setIsConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, [websocketUrl, maxActivities]);

  // --- Filtering Logic ---
  useEffect(() => {
    let filtered = activities;
    
    // Filter by agent
    if (selectedAgent !== 'all') {
      filtered = filtered.filter(activity => activity.agentId === selectedAgent);
    }
    
    // Filter by type
    if (selectedType !== 'all') {
      filtered = filtered.filter(activity => activity.type === selectedType);
    }
    
    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(activity => 
        activity.title.toLowerCase().includes(term) ||
        activity.description.toLowerCase().includes(term)
      );
    }
    
    setFilteredActivities(filtered);
  }, [activities, selectedAgent, selectedType, searchTerm]);

  // --- Derived Data ---
  const uniqueAgents = useMemo(() => {
    const agents = [...new Set(activities.map(a => a.agentId))];
    return agents.sort();
  }, [activities]);

  const uniqueTypes = useMemo(() => {
    const types = [...new Set(activities.map(a => a.type))];
    return types.sort();
  }, [activities]);

  // --- Helper Functions ---
  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const getAgentColor = (agentId) => {
    const colors = {
      'dental_agent': 'bg-blue-100 text-blue-800',
      'demo_agent': 'bg-green-100 text-green-800',
      'opendental_agent': 'bg-purple-100 text-purple-800'
    };
    return colors[agentId] || 'bg-gray-100 text-gray-800';
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'USER_REQUEST': return '👤';
      case 'DATA_ANALYSIS': return '📊';
      case 'SYSTEM_TASK': return '⚙️';
      case 'COMMUNICATION': return '💬';
      default: return '🔄';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  // --- Render ---
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Live Activity Feed</h2>
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
              isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="h-4 w-4" />
            <span>Filters</span>
            <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>
        </div>
        
        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-4 p-4 bg-white rounded-lg border border-gray-200 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search activities..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              {/* Agent Filter */}
              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Agents</option>
                {uniqueAgents.map(agent => (
                  <option key={agent} value={agent}>{agent}</option>
                ))}
              </select>
              
              {/* Type Filter */}
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Types</option>
                {uniqueTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Activity List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filteredActivities.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Activity className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">No activities yet</p>
            <p className="text-sm">Agent activities will appear here in real-time</p>
          </div>
        ) : (
          filteredActivities.map((activity, index) => (
            <div
              key={activity.id}
              className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-md transition-all duration-200 hover:border-blue-300 animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-lg">{getTypeIcon(activity.type)}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getAgentColor(activity.agentId)}`}>
                      {activity.agentId}
                    </span>
                    <span className="text-sm text-gray-500 flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {formatTime(activity.timestamp)}
                    </span>
                  </div>
                  
                  <h3 className="font-semibold text-gray-900 mb-1">{activity.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">{activity.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-medium ${getConfidenceColor(activity.confidence)}`}>
                      Confidence: {(activity.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Showing {filteredActivities.length} of {activities.length} activities</span>
          <span>{uniqueAgents.length} active agents</span>
        </div>
      </div>
    </div>
  );
};

export default ActivityFeed;
