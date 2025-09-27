/**
 * Frontend WebSocket Client - Component 1.3
 * Real-time Communication Client for Mission Control Dashboard
 * 
 * This module provides the frontend WebSocket client that connects the Mission Control
 * Dashboard to the real-time agent broadcasting system. It handles connection management,
 * message parsing, automatic reconnection, and state synchronization.
 * 
 * Features:
 * - Automatic connection management with reconnection logic
 * - Message parsing and routing to appropriate handlers
 * - Connection status indicators for UI
 * - Subscription management for different data channels
 * - Error recovery and graceful degradation
 * - Performance monitoring and metrics
 */

import { EventEmitter } from 'events';
import { useState, useEffect } from 'react';

// WebSocket connection states
export const ConnectionState = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  RECONNECTING: 'reconnecting',
  ERROR: 'error'
};

// Message types from the backend
export const MessageTypes = {
  CONNECTION_ESTABLISHED: 'connection_established',
  AGENT_STATUS_UPDATE: 'agent_status_update',
  AGENT_ACTIVITY: 'agent_activity',
  AGENT_DECISION_EXPLANATION: 'agent_decision_explanation',
  PERFORMANCE_METRICS: 'performance_metrics',
  AGENT_HEARTBEAT: 'agent_heartbeat',
  HUMAN_HANDOFF_REQUIRED: 'human_handoff_required',
  ERROR: 'error',
  PONG: 'pong'
};

// Subscription channels
export const Channels = {
  AGENT_STATUS: 'agent_status',
  AGENT_ACTIVITIES: 'agent_activities',
  PERFORMANCE_METRICS: 'performance_metrics',
  HUMAN_HANDOFFS: 'human_handoffs',
  ALL: 'all'
};

class WebSocketClient extends EventEmitter {
  constructor(url = null, options = {}) {
    super();
    
    // Configuration
    this.url = url || this._getWebSocketUrl();
    this.options = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      pingInterval: 30000,
      connectionTimeout: 10000,
      ...options
    };
    
    // Connection state
    this.ws = null;
    this.connectionState = ConnectionState.DISCONNECTED;
    this.clientId = null;
    this.reconnectAttempts = 0;
    this.lastPingTime = null;
    this.connectionStartTime = null;
    
    // Subscriptions and handlers
    this.subscriptions = new Set();
    this.messageHandlers = new Map();
    this.messageQueue = [];
    
    // Timers
    this.reconnectTimer = null;
    this.pingTimer = null;
    this.connectionTimer = null;
    
    // Statistics
    this.stats = {
      messagesReceived: 0,
      messagesSent: 0,
      reconnectCount: 0,
      lastConnectedAt: null,
      totalUptime: 0,
      averageLatency: 0,
      latencyMeasurements: []
    };
    
    // Setup default message handlers
    this._setupDefaultHandlers();
    
    console.log('WebSocket client initialized', { url: this.url, options: this.options });
  }
  
  /**
   * Get WebSocket URL based on current location
   */
  _getWebSocketUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = process.env.NODE_ENV === 'development' ? '8001' : window.location.port;
    return `${protocol}//${host}:${port}/ws`;
  }
  
  /**
   * Setup default message handlers
   */
  _setupDefaultHandlers() {
    this.onMessage(MessageTypes.CONNECTION_ESTABLISHED, (data) => {
      this.clientId = data.client_id;
      this.stats.lastConnectedAt = new Date();
      console.log('Connection established', { clientId: this.clientId, serverTime: data.server_time });
    });
    
    this.onMessage(MessageTypes.PONG, (data) => {
      if (this.lastPingTime) {
        const latency = Date.now() - this.lastPingTime;
        this._recordLatency(latency);
        this.lastPingTime = null;
      }
    });
    
    this.onMessage(MessageTypes.ERROR, (data) => {
      console.error('Server error:', data.message);
      this.emit('error', new Error(data.message));
    });
  }
  
  /**
   * Connect to WebSocket server
   */
  async connect() {
    if (this.connectionState === ConnectionState.CONNECTED || 
        this.connectionState === ConnectionState.CONNECTING) {
      return Promise.resolve();
    }
    
    return new Promise((resolve, reject) => {
      this._setConnectionState(ConnectionState.CONNECTING);
      this.connectionStartTime = Date.now();
      
      try {
        this.ws = new WebSocket(this.url);
        
        // Connection timeout
        this.connectionTimer = setTimeout(() => {
          if (this.connectionState === ConnectionState.CONNECTING) {
            this.ws.close();
            reject(new Error('Connection timeout'));
          }
        }, this.options.connectionTimeout);
        
        this.ws.onopen = () => {
          clearTimeout(this.connectionTimer);
          this._setConnectionState(ConnectionState.CONNECTED);
          this.reconnectAttempts = 0;
          this._startPingTimer();
          this._processMessageQueue();
          
          console.log('WebSocket connected successfully');
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          this._handleMessage(event.data);
        };
        
        this.ws.onclose = (event) => {
          clearTimeout(this.connectionTimer);
          this._stopPingTimer();
          
          if (this.connectionState === ConnectionState.CONNECTED) {
            console.log('WebSocket connection closed', { code: event.code, reason: event.reason });
            this._handleDisconnection();
          }
        };
        
        this.ws.onerror = (error) => {
          clearTimeout(this.connectionTimer);
          console.error('WebSocket error:', error);
          
          if (this.connectionState === ConnectionState.CONNECTING) {
            reject(error);
          } else {
            this.emit('error', error);
            this._handleDisconnection();
          }
        };
        
      } catch (error) {
        clearTimeout(this.connectionTimer);
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    this._stopReconnectTimer();
    this._stopPingTimer();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this._setConnectionState(ConnectionState.DISCONNECTED);
    console.log('WebSocket disconnected');
  }
  
  /**
   * Send message to server
   */
  send(type, payload = {}) {
    const message = {
      type,
      payload,
      timestamp: new Date().toISOString(),
      client_id: this.clientId
    };
    
    if (this.connectionState === ConnectionState.CONNECTED && this.ws) {
      try {
        this.ws.send(JSON.stringify(message));
        this.stats.messagesSent++;
        return true;
      } catch (error) {
        console.error('Error sending message:', error);
        this.messageQueue.push(message);
        return false;
      }
    } else {
      // Queue message for later sending
      this.messageQueue.push(message);
      return false;
    }
  }
  
  /**
   * Subscribe to specific channels
   */
  subscribe(channels) {
    const channelArray = Array.isArray(channels) ? channels : [channels];
    
    channelArray.forEach(channel => {
      this.subscriptions.add(channel);
    });
    
    this.send('subscribe', { channels: channelArray });
    console.log('Subscribed to channels:', channelArray);
  }
  
  /**
   * Unsubscribe from channels
   */
  unsubscribe(channels) {
    const channelArray = Array.isArray(channels) ? channels : [channels];
    
    channelArray.forEach(channel => {
      this.subscriptions.delete(channel);
    });
    
    this.send('unsubscribe', { channels: channelArray });
    console.log('Unsubscribed from channels:', channelArray);
  }
  
  /**
   * Register message handler for specific message type
   */
  onMessage(messageType, handler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, []);
    }
    this.messageHandlers.get(messageType).push(handler);
  }
  
  /**
   * Remove message handler
   */
  offMessage(messageType, handler) {
    if (this.messageHandlers.has(messageType)) {
      const handlers = this.messageHandlers.get(messageType);
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }
  
  /**
   * Send ping to server
   */
  ping() {
    this.lastPingTime = Date.now();
    this.send('ping');
  }
  
  /**
   * Get connection statistics
   */
  getStats() {
    const now = Date.now();
    const uptime = this.connectionStartTime ? now - this.connectionStartTime : 0;
    
    return {
      ...this.stats,
      connectionState: this.connectionState,
      clientId: this.clientId,
      currentUptime: uptime,
      subscriptions: Array.from(this.subscriptions),
      queuedMessages: this.messageQueue.length
    };
  }
  
  /**
   * Get current connection state
   */
  getConnectionState() {
    return this.connectionState;
  }
  
  /**
   * Check if connected
   */
  isConnected() {
    return this.connectionState === ConnectionState.CONNECTED;
  }
  
  // Private methods
  
  /**
   * Handle incoming message
   */
  _handleMessage(data) {
    try {
      const message = JSON.parse(data);
      this.stats.messagesReceived++;
      
      // Emit generic message event
      this.emit('message', message);
      
      // Call specific handlers
      if (this.messageHandlers.has(message.type)) {
        const handlers = this.messageHandlers.get(message.type);
        handlers.forEach(handler => {
          try {
            handler(message.payload, message);
          } catch (error) {
            console.error('Error in message handler:', error);
          }
        });
      }
      
      // Emit typed event
      this.emit(message.type, message.payload, message);
      
    } catch (error) {
      console.error('Error parsing message:', error, data);
    }
  }
  
  /**
   * Handle disconnection
   */
  _handleDisconnection() {
    this._setConnectionState(ConnectionState.DISCONNECTED);
    this._stopPingTimer();
    
    // Update uptime stats
    if (this.connectionStartTime) {
      const sessionUptime = Date.now() - this.connectionStartTime;
      this.stats.totalUptime += sessionUptime;
      this.connectionStartTime = null;
    }
    
    // Attempt reconnection if not manually disconnected
    if (this.reconnectAttempts < this.options.maxReconnectAttempts) {
      this._scheduleReconnect();
    } else {
      this._setConnectionState(ConnectionState.ERROR);
      this.emit('maxReconnectAttemptsReached');
    }
  }
  
  /**
   * Schedule reconnection attempt
   */
  _scheduleReconnect() {
    this._setConnectionState(ConnectionState.RECONNECTING);
    this.reconnectAttempts++;
    this.stats.reconnectCount++;
    
    const delay = this.options.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);
    
    console.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, delay);
  }
  
  /**
   * Set connection state and emit event
   */
  _setConnectionState(state) {
    if (this.connectionState !== state) {
      const previousState = this.connectionState;
      this.connectionState = state;
      this.emit('connectionStateChange', state, previousState);
      console.log('Connection state changed:', { from: previousState, to: state });
    }
  }
  
  /**
   * Start ping timer
   */
  _startPingTimer() {
    this._stopPingTimer();
    this.pingTimer = setInterval(() => {
      this.ping();
    }, this.options.pingInterval);
  }
  
  /**
   * Stop ping timer
   */
  _stopPingTimer() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }
  
  /**
   * Stop reconnect timer
   */
  _stopReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
  
  /**
   * Process queued messages
   */
  _processMessageQueue() {
    while (this.messageQueue.length > 0 && this.isConnected()) {
      const message = this.messageQueue.shift();
      try {
        this.ws.send(JSON.stringify(message));
        this.stats.messagesSent++;
      } catch (error) {
        console.error('Error sending queued message:', error);
        // Put message back at front of queue
        this.messageQueue.unshift(message);
        break;
      }
    }
  }
  
  /**
   * Record latency measurement
   */
  _recordLatency(latency) {
    this.stats.latencyMeasurements.push(latency);
    
    // Keep only last 100 measurements
    if (this.stats.latencyMeasurements.length > 100) {
      this.stats.latencyMeasurements.shift();
    }
    
    // Calculate average latency
    const sum = this.stats.latencyMeasurements.reduce((a, b) => a + b, 0);
    this.stats.averageLatency = sum / this.stats.latencyMeasurements.length;
  }
}

// React Hook for WebSocket integration
export function useWebSocket(url, options = {}) {
  const [client, setClient] = useState(null);
  const [connectionState, setConnectionState] = useState(ConnectionState.DISCONNECTED);
  const [stats, setStats] = useState({});
  
  useEffect(() => {
    const wsClient = new WebSocketClient(url, options);
    
    // Connection state handler
    wsClient.on('connectionStateChange', (newState) => {
      setConnectionState(newState);
    });
    
    // Stats update handler
    const updateStats = () => {
      setStats(wsClient.getStats());
    };
    
    const statsInterval = setInterval(updateStats, 5000);
    
    setClient(wsClient);
    
    // Auto-connect
    if (options.autoConnect !== false) {
      wsClient.connect().catch(console.error);
    }
    
    return () => {
      clearInterval(statsInterval);
      wsClient.disconnect();
    };
  }, [url]);
  
  return {
    client,
    connectionState,
    stats,
    isConnected: connectionState === ConnectionState.CONNECTED
  };
}

// Mission Control specific WebSocket service
class MissionControlWebSocket extends WebSocketClient {
  constructor(options = {}) {
    super(null, {
      autoConnect: true,
      reconnectInterval: 2000,
      maxReconnectAttempts: 20,
      ...options
    });
    
    // Mission Control specific state
    this.agents = new Map();
    this.activities = [];
    this.decisions = [];
    this.performanceMetrics = {};
    this.handoffRequests = [];
    
    // Setup Mission Control handlers
    this._setupMissionControlHandlers();
    
    // Auto-subscribe to all channels
    this.on('connectionStateChange', (state) => {
      if (state === ConnectionState.CONNECTED) {
        this.subscribe([
          Channels.AGENT_STATUS,
          Channels.AGENT_ACTIVITIES,
          Channels.PERFORMANCE_METRICS,
          Channels.HUMAN_HANDOFFS
        ]);
      }
    });
  }
  
  _setupMissionControlHandlers() {
    // Agent status updates
    this.onMessage(MessageTypes.AGENT_STATUS_UPDATE, (data) => {
      this.agents.set(data.agent_id, {
        ...this.agents.get(data.agent_id),
        ...data,
        lastUpdated: new Date()
      });
      this.emit('agentStatusUpdated', data);
    });
    
    // Agent activities
    this.onMessage(MessageTypes.AGENT_ACTIVITY, (data) => {
      this.activities.unshift(data);
      
      // Keep only last 1000 activities
      if (this.activities.length > 1000) {
        this.activities = this.activities.slice(0, 1000);
      }
      
      this.emit('agentActivity', data);
    });
    
    // Decision explanations
    this.onMessage(MessageTypes.AGENT_DECISION_EXPLANATION, (data) => {
      this.decisions.unshift(data);
      
      // Keep only last 500 decisions
      if (this.decisions.length > 500) {
        this.decisions = this.decisions.slice(0, 500);
      }
      
      this.emit('agentDecision', data);
    });
    
    // Performance metrics
    this.onMessage(MessageTypes.PERFORMANCE_METRICS, (data) => {
      this.performanceMetrics = {
        ...data.metrics,
        timestamp: data.timestamp,
        activeAgentsCount: data.active_agents_count,
        recentActivitiesCount: data.recent_activities_count
      };
      this.emit('performanceMetrics', this.performanceMetrics);
    });
    
    // Human handoff requests
    this.onMessage(MessageTypes.HUMAN_HANDOFF_REQUIRED, (data) => {
      this.handoffRequests.unshift(data);
      
      // Keep only last 100 handoff requests
      if (this.handoffRequests.length > 100) {
        this.handoffRequests = this.handoffRequests.slice(0, 100);
      }
      
      this.emit('humanHandoffRequired', data);
    });
    
    // Agent heartbeats
    this.onMessage(MessageTypes.AGENT_HEARTBEAT, (data) => {
      if (this.agents.has(data.agent_id)) {
        const agent = this.agents.get(data.agent_id);
        agent.lastHeartbeat = new Date();
        agent.uptime = data.uptime_seconds;
        this.agents.set(data.agent_id, agent);
      }
    });
  }
  
  // Mission Control specific methods
  getAgents() {
    return Array.from(this.agents.values());
  }
  
  getAgent(agentId) {
    return this.agents.get(agentId);
  }
  
  getRecentActivities(limit = 50) {
    return this.activities.slice(0, limit);
  }
  
  getAgentActivities(agentId, limit = 50) {
    return this.activities
      .filter(activity => activity.agent_id === agentId)
      .slice(0, limit);
  }
  
  getRecentDecisions(limit = 20) {
    return this.decisions.slice(0, limit);
  }
  
  getPerformanceMetrics() {
    return this.performanceMetrics;
  }
  
  getPendingHandoffs() {
    return this.handoffRequests.filter(request => !request.resolved);
  }
  
  resolveHandoff(handoffId) {
    const handoff = this.handoffRequests.find(h => h.handoff_id === handoffId);
    if (handoff) {
      handoff.resolved = true;
      handoff.resolvedAt = new Date();
    }
  }
}

// Global Mission Control WebSocket instance
let missionControlWS = null;

export function getMissionControlWebSocket() {
  if (!missionControlWS) {
    missionControlWS = new MissionControlWebSocket();
  }
  return missionControlWS;
}

// React Hook for Mission Control WebSocket
export function useMissionControlWebSocket() {
  const [ws] = useState(() => getMissionControlWebSocket());
  const [connectionState, setConnectionState] = useState(ws.getConnectionState());
  const [agents, setAgents] = useState([]);
  const [activities, setActivities] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState({});
  const [handoffRequests, setHandoffRequests] = useState([]);
  
  useEffect(() => {
    // Connection state handler
    const handleConnectionState = (state) => {
      setConnectionState(state);
    };
    
    // Data update handlers
    const handleAgentUpdate = () => {
      setAgents(ws.getAgents());
    };
    
    const handleActivityUpdate = () => {
      setActivities(ws.getRecentActivities());
    };
    
    const handleMetricsUpdate = (metrics) => {
      setPerformanceMetrics(metrics);
    };
    
    const handleHandoffUpdate = () => {
      setHandoffRequests(ws.getPendingHandoffs());
    };
    
    // Register handlers
    ws.on('connectionStateChange', handleConnectionState);
    ws.on('agentStatusUpdated', handleAgentUpdate);
    ws.on('agentActivity', handleActivityUpdate);
    ws.on('performanceMetrics', handleMetricsUpdate);
    ws.on('humanHandoffRequired', handleHandoffUpdate);
    
    // Initial data load
    setAgents(ws.getAgents());
    setActivities(ws.getRecentActivities());
    setPerformanceMetrics(ws.getPerformanceMetrics());
    setHandoffRequests(ws.getPendingHandoffs());
    
    // Connect if not already connected
    if (!ws.isConnected()) {
      ws.connect().catch(console.error);
    }
    
    return () => {
      ws.off('connectionStateChange', handleConnectionState);
      ws.off('agentStatusUpdated', handleAgentUpdate);
      ws.off('agentActivity', handleActivityUpdate);
      ws.off('performanceMetrics', handleMetricsUpdate);
      ws.off('humanHandoffRequired', handleHandoffUpdate);
    };
  }, [ws]);
  
  return {
    ws,
    connectionState,
    isConnected: connectionState === ConnectionState.CONNECTED,
    agents,
    activities,
    performanceMetrics,
    handoffRequests,
    getAgent: (id) => ws.getAgent(id),
    getAgentActivities: (id, limit) => ws.getAgentActivities(id, limit),
    resolveHandoff: (id) => ws.resolveHandoff(id)
  };
}

export default WebSocketClient;
