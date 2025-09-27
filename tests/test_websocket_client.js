/**
 * Comprehensive Test Suite for Frontend WebSocket Client - Component 1.3
 * Aggressive testing protocol for real-time communication client
 * 
 * Test Categories:
 * 1. Connection management and state transitions
 * 2. Message handling and parsing
 * 3. Subscription management
 * 4. Automatic reconnection logic
 * 5. Performance monitoring and statistics
 * 6. Mission Control specific functionality
 * 7. React hooks integration
 * 8. Error handling and recovery
 */

import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import WS from 'jest-websocket-mock';

// Import the WebSocket client components
import WebSocketClient, { 
  ConnectionState, 
  MessageTypes, 
  Channels,
  useWebSocket,
  getMissionControlWebSocket,
  useMissionControlWebSocket
} from '../src/services/websocket.js';

// Mock EventEmitter for Node.js environment
class MockEventEmitter {
  constructor() {
    this.events = {};
  }
  
  on(event, listener) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(listener);
  }
  
  off(event, listener) {
    if (this.events[event]) {
      const index = this.events[event].indexOf(listener);
      if (index > -1) {
        this.events[event].splice(index, 1);
      }
    }
  }
  
  emit(event, ...args) {
    if (this.events[event]) {
      this.events[event].forEach(listener => listener(...args));
    }
  }
  
  removeAllListeners(event) {
    if (event) {
      delete this.events[event];
    } else {
      this.events = {};
    }
  }
}

// Mock WebSocket for testing
class MockWebSocket extends MockEventEmitter {
  constructor(url) {
    super();
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    this.CONNECTING = 0;
    this.OPEN = 1;
    this.CLOSING = 2;
    this.CLOSED = 3;
    
    // Simulate connection after a short delay
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) this.onopen();
    }, 10);
  }
  
  send(data) {
    if (this.readyState === WebSocket.OPEN) {
      // Echo back for testing
      setTimeout(() => {
        if (this.onmessage) {
          this.onmessage({ data });
        }
      }, 5);
    }
  }
  
  close(code, reason) {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose({ code, reason });
    }
  }
}

// Setup global mocks
global.WebSocket = MockWebSocket;
global.EventEmitter = MockEventEmitter;

describe('WebSocketClient', () => {
  let client;
  let mockServer;
  const testUrl = 'ws://localhost:8001/ws';
  
  beforeEach(() => {
    client = new WebSocketClient(testUrl, {
      reconnectInterval: 100,
      maxReconnectAttempts: 3,
      pingInterval: 1000,
      connectionTimeout: 1000
    });
  });
  
  afterEach(() => {
    if (client) {
      client.disconnect();
    }
    vi.clearAllTimers();
  });

  describe('Connection Management', () => {
    it('should initialize with correct default state', () => {
      expect(client.connectionState).toBe(ConnectionState.DISCONNECTED);
      expect(client.clientId).toBeNull();
      expect(client.reconnectAttempts).toBe(0);
    });
    
    it('should connect successfully', async () => {
      const connectPromise = client.connect();
      
      // Wait for connection
      await connectPromise;
      
      expect(client.connectionState).toBe(ConnectionState.CONNECTED);
      expect(client.isConnected()).toBe(true);
    });
    
    it('should handle connection state transitions', async () => {
      const stateChanges = [];
      
      client.on('connectionStateChange', (newState, oldState) => {
        stateChanges.push({ from: oldState, to: newState });
      });
      
      await client.connect();
      
      expect(stateChanges).toContainEqual({
        from: ConnectionState.DISCONNECTED,
        to: ConnectionState.CONNECTING
      });
      
      expect(stateChanges).toContainEqual({
        from: ConnectionState.CONNECTING,
        to: ConnectionState.CONNECTED
      });
    });
    
    it('should disconnect cleanly', async () => {
      await client.connect();
      expect(client.isConnected()).toBe(true);
      
      client.disconnect();
      expect(client.connectionState).toBe(ConnectionState.DISCONNECTED);
      expect(client.isConnected()).toBe(false);
    });
    
    it('should not connect if already connected', async () => {
      await client.connect();
      const firstConnectionState = client.connectionState;
      
      // Try to connect again
      await client.connect();
      
      expect(client.connectionState).toBe(firstConnectionState);
    });
  });

  describe('Message Handling', () => {
    beforeEach(async () => {
      await client.connect();
    });
    
    it('should send messages correctly', () => {
      const result = client.send('test_message', { data: 'test' });
      
      expect(result).toBe(true);
      expect(client.stats.messagesSent).toBe(1);
    });
    
    it('should queue messages when disconnected', () => {
      client.disconnect();
      
      const result = client.send('test_message', { data: 'test' });
      
      expect(result).toBe(false);
      expect(client.messageQueue.length).toBe(1);
    });
    
    it('should handle incoming messages', (done) => {
      const testMessage = {
        type: 'test_type',
        payload: { test: 'data' }
      };
      
      client.onMessage('test_type', (payload) => {
        expect(payload).toEqual(testMessage.payload);
        done();
      });
      
      // Simulate incoming message
      client._handleMessage(JSON.stringify(testMessage));
    });
    
    it('should handle malformed messages gracefully', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      // This should not throw
      client._handleMessage('invalid json');
      
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
    
    it('should register and remove message handlers', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      
      client.onMessage('test_type', handler1);
      client.onMessage('test_type', handler2);
      
      const testMessage = {
        type: 'test_type',
        payload: { test: 'data' }
      };
      
      client._handleMessage(JSON.stringify(testMessage));
      
      expect(handler1).toHaveBeenCalledWith(testMessage.payload, testMessage);
      expect(handler2).toHaveBeenCalledWith(testMessage.payload, testMessage);
      
      // Remove one handler
      client.offMessage('test_type', handler1);
      
      client._handleMessage(JSON.stringify(testMessage));
      
      expect(handler1).toHaveBeenCalledTimes(1); // Still only called once
      expect(handler2).toHaveBeenCalledTimes(2); // Called twice
    });
  });

  describe('Subscription Management', () => {
    beforeEach(async () => {
      await client.connect();
    });
    
    it('should subscribe to channels', () => {
      const sendSpy = vi.spyOn(client, 'send');
      
      client.subscribe(['channel1', 'channel2']);
      
      expect(client.subscriptions.has('channel1')).toBe(true);
      expect(client.subscriptions.has('channel2')).toBe(true);
      expect(sendSpy).toHaveBeenCalledWith('subscribe', { channels: ['channel1', 'channel2'] });
    });
    
    it('should unsubscribe from channels', () => {
      const sendSpy = vi.spyOn(client, 'send');
      
      client.subscribe(['channel1', 'channel2']);
      client.unsubscribe('channel1');
      
      expect(client.subscriptions.has('channel1')).toBe(false);
      expect(client.subscriptions.has('channel2')).toBe(true);
      expect(sendSpy).toHaveBeenCalledWith('unsubscribe', { channels: ['channel1'] });
    });
    
    it('should handle single channel subscription', () => {
      client.subscribe('single_channel');
      
      expect(client.subscriptions.has('single_channel')).toBe(true);
    });
  });

  describe('Reconnection Logic', () => {
    it('should attempt reconnection on disconnect', (done) => {
      const reconnectSpy = vi.spyOn(client, 'connect');
      
      client.on('connectionStateChange', (state) => {
        if (state === ConnectionState.RECONNECTING) {
          expect(client.reconnectAttempts).toBe(1);
          done();
        }
      });
      
      // Connect first
      client.connect().then(() => {
        // Simulate disconnection
        client._handleDisconnection();
      });
    });
    
    it('should stop reconnecting after max attempts', (done) => {
      client.options.maxReconnectAttempts = 2;
      
      client.on('maxReconnectAttemptsReached', () => {
        expect(client.connectionState).toBe(ConnectionState.ERROR);
        expect(client.reconnectAttempts).toBe(2);
        done();
      });
      
      // Simulate multiple failed reconnections
      client.reconnectAttempts = 2;
      client._handleDisconnection();
    });
    
    it('should reset reconnect attempts on successful connection', async () => {
      client.reconnectAttempts = 5;
      
      await client.connect();
      
      expect(client.reconnectAttempts).toBe(0);
    });
  });

  describe('Performance Monitoring', () => {
    beforeEach(async () => {
      await client.connect();
    });
    
    it('should track message statistics', () => {
      client.send('test1', {});
      client.send('test2', {});
      
      const testMessage = { type: 'test', payload: {} };
      client._handleMessage(JSON.stringify(testMessage));
      
      const stats = client.getStats();
      
      expect(stats.messagesSent).toBe(2);
      expect(stats.messagesReceived).toBe(1);
    });
    
    it('should record latency measurements', () => {
      client.lastPingTime = Date.now() - 100; // 100ms ago
      
      client._recordLatency(100);
      
      const stats = client.getStats();
      
      expect(stats.latencyMeasurements).toContain(100);
      expect(stats.averageLatency).toBe(100);
    });
    
    it('should limit latency measurements to 100', () => {
      // Add 150 measurements
      for (let i = 0; i < 150; i++) {
        client._recordLatency(i);
      }
      
      const stats = client.getStats();
      
      expect(stats.latencyMeasurements.length).toBe(100);
      expect(stats.latencyMeasurements[0]).toBe(50); // Should start from 50 (150-100)
    });
    
    it('should handle ping/pong correctly', () => {
      const recordLatencySpy = vi.spyOn(client, '_recordLatency');
      
      client.lastPingTime = Date.now() - 50;
      
      const pongMessage = { type: MessageTypes.PONG, payload: {} };
      client._handleMessage(JSON.stringify(pongMessage));
      
      expect(recordLatencySpy).toHaveBeenCalled();
      expect(client.lastPingTime).toBeNull();
    });
  });

  describe('Error Handling', () => {
    it('should handle connection timeout', (done) => {
      const client = new WebSocketClient(testUrl, {
        connectionTimeout: 50 // Very short timeout
      });
      
      // Mock WebSocket that never connects
      global.WebSocket = class extends MockEventEmitter {
        constructor(url) {
          super();
          this.url = url;
          this.readyState = 0; // CONNECTING
          // Never call onopen
        }
        
        close() {
          this.readyState = 3; // CLOSED
        }
      };
      
      client.connect().catch((error) => {
        expect(error.message).toBe('Connection timeout');
        done();
      });
    });
    
    it('should handle WebSocket errors', (done) => {
      client.on('error', (error) => {
        expect(error).toBeDefined();
        done();
      });
      
      client.connect().then(() => {
        // Simulate WebSocket error
        if (client.ws && client.ws.onerror) {
          client.ws.onerror(new Error('WebSocket error'));
        }
      });
    });
    
    it('should handle message handler errors gracefully', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      // Register a handler that throws
      client.onMessage('test_type', () => {
        throw new Error('Handler error');
      });
      
      const testMessage = { type: 'test_type', payload: {} };
      
      // This should not throw
      expect(() => {
        client._handleMessage(JSON.stringify(testMessage));
      }).not.toThrow();
      
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });
});

describe('MissionControlWebSocket', () => {
  let missionControlWS;
  
  beforeEach(() => {
    missionControlWS = getMissionControlWebSocket();
  });
  
  afterEach(() => {
    if (missionControlWS) {
      missionControlWS.disconnect();
    }
  });

  describe('Agent Management', () => {
    it('should handle agent status updates', () => {
      const agentData = {
        agent_id: 'test_agent',
        status: 'active',
        current_task: 'Processing data'
      };
      
      const statusMessage = {
        type: MessageTypes.AGENT_STATUS_UPDATE,
        payload: agentData
      };
      
      missionControlWS._handleMessage(JSON.stringify(statusMessage));
      
      const agent = missionControlWS.getAgent('test_agent');
      expect(agent).toBeDefined();
      expect(agent.agent_id).toBe('test_agent');
      expect(agent.status).toBe('active');
    });
    
    it('should return all agents', () => {
      // Add test agents
      const agents = [
        { agent_id: 'agent1', status: 'active' },
        { agent_id: 'agent2', status: 'idle' }
      ];
      
      agents.forEach(agentData => {
        const message = {
          type: MessageTypes.AGENT_STATUS_UPDATE,
          payload: agentData
        };
        missionControlWS._handleMessage(JSON.stringify(message));
      });
      
      const allAgents = missionControlWS.getAgents();
      expect(allAgents).toHaveLength(2);
      expect(allAgents.map(a => a.agent_id)).toContain('agent1');
      expect(allAgents.map(a => a.agent_id)).toContain('agent2');
    });
  });

  describe('Activity Management', () => {
    it('should handle agent activities', () => {
      const activityData = {
        activity_id: 'activity_1',
        agent_id: 'test_agent',
        title: 'Test Activity',
        description: 'Testing activity handling'
      };
      
      const activityMessage = {
        type: MessageTypes.AGENT_ACTIVITY,
        payload: activityData
      };
      
      missionControlWS._handleMessage(JSON.stringify(activityMessage));
      
      const activities = missionControlWS.getRecentActivities();
      expect(activities).toHaveLength(1);
      expect(activities[0].activity_id).toBe('activity_1');
    });
    
    it('should limit activity history', () => {
      // Add more than 1000 activities
      for (let i = 0; i < 1200; i++) {
        const activityMessage = {
          type: MessageTypes.AGENT_ACTIVITY,
          payload: {
            activity_id: `activity_${i}`,
            agent_id: 'test_agent',
            title: `Activity ${i}`
          }
        };
        missionControlWS._handleMessage(JSON.stringify(activityMessage));
      }
      
      const activities = missionControlWS.getRecentActivities();
      expect(activities.length).toBeLessThanOrEqual(1000);
    });
    
    it('should filter activities by agent', () => {
      const activities = [
        { activity_id: '1', agent_id: 'agent1', title: 'Activity 1' },
        { activity_id: '2', agent_id: 'agent2', title: 'Activity 2' },
        { activity_id: '3', agent_id: 'agent1', title: 'Activity 3' }
      ];
      
      activities.forEach(activityData => {
        const message = {
          type: MessageTypes.AGENT_ACTIVITY,
          payload: activityData
        };
        missionControlWS._handleMessage(JSON.stringify(message));
      });
      
      const agent1Activities = missionControlWS.getAgentActivities('agent1');
      expect(agent1Activities).toHaveLength(2);
      expect(agent1Activities.every(a => a.agent_id === 'agent1')).toBe(true);
    });
  });

  describe('Decision Management', () => {
    it('should handle decision explanations', () => {
      const decisionData = {
        decision_id: 'decision_1',
        agent_id: 'test_agent',
        decision_type: 'scheduling',
        reasoning_steps: ['Step 1', 'Step 2'],
        confidence_score: 0.95
      };
      
      const decisionMessage = {
        type: MessageTypes.AGENT_DECISION_EXPLANATION,
        payload: decisionData
      };
      
      missionControlWS._handleMessage(JSON.stringify(decisionMessage));
      
      const decisions = missionControlWS.getRecentDecisions();
      expect(decisions).toHaveLength(1);
      expect(decisions[0].decision_id).toBe('decision_1');
    });
    
    it('should limit decision history', () => {
      // Add more than 500 decisions
      for (let i = 0; i < 600; i++) {
        const decisionMessage = {
          type: MessageTypes.AGENT_DECISION_EXPLANATION,
          payload: {
            decision_id: `decision_${i}`,
            agent_id: 'test_agent',
            decision_type: 'test'
          }
        };
        missionControlWS._handleMessage(JSON.stringify(decisionMessage));
      }
      
      const decisions = missionControlWS.getRecentDecisions();
      expect(decisions.length).toBeLessThanOrEqual(500);
    });
  });

  describe('Performance Metrics', () => {
    it('should handle performance metrics updates', () => {
      const metricsData = {
        metrics: {
          total_activities: 100,
          successful_activities: 95,
          failed_activities: 5
        },
        timestamp: new Date().toISOString(),
        active_agents_count: 3,
        recent_activities_count: 10
      };
      
      const metricsMessage = {
        type: MessageTypes.PERFORMANCE_METRICS,
        payload: metricsData
      };
      
      missionControlWS._handleMessage(JSON.stringify(metricsMessage));
      
      const metrics = missionControlWS.getPerformanceMetrics();
      expect(metrics.total_activities).toBe(100);
      expect(metrics.successful_activities).toBe(95);
      expect(metrics.activeAgentsCount).toBe(3);
    });
  });

  describe('Human Handoff Management', () => {
    it('should handle handoff requests', () => {
      const handoffData = {
        handoff_id: 'handoff_1',
        agent_id: 'test_agent',
        reason: 'Complex decision required',
        priority: 'high'
      };
      
      const handoffMessage = {
        type: MessageTypes.HUMAN_HANDOFF_REQUIRED,
        payload: handoffData
      };
      
      missionControlWS._handleMessage(JSON.stringify(handoffMessage));
      
      const handoffs = missionControlWS.getPendingHandoffs();
      expect(handoffs).toHaveLength(1);
      expect(handoffs[0].handoff_id).toBe('handoff_1');
    });
    
    it('should resolve handoff requests', () => {
      const handoffData = {
        handoff_id: 'handoff_1',
        agent_id: 'test_agent',
        reason: 'Test handoff'
      };
      
      const handoffMessage = {
        type: MessageTypes.HUMAN_HANDOFF_REQUIRED,
        payload: handoffData
      };
      
      missionControlWS._handleMessage(JSON.stringify(handoffMessage));
      
      // Resolve the handoff
      missionControlWS.resolveHandoff('handoff_1');
      
      const pendingHandoffs = missionControlWS.getPendingHandoffs();
      expect(pendingHandoffs).toHaveLength(0);
    });
  });
});

describe('React Hooks', () => {
  describe('useWebSocket', () => {
    it('should return WebSocket client and connection state', () => {
      const { result } = renderHook(() => 
        useWebSocket('ws://localhost:8001/ws', { autoConnect: false })
      );
      
      expect(result.current.client).toBeDefined();
      expect(result.current.connectionState).toBe(ConnectionState.DISCONNECTED);
      expect(result.current.isConnected).toBe(false);
    });
  });

  describe('useMissionControlWebSocket', () => {
    it('should return Mission Control WebSocket instance and data', () => {
      const { result } = renderHook(() => useMissionControlWebSocket());
      
      expect(result.current.ws).toBeDefined();
      expect(result.current.agents).toEqual([]);
      expect(result.current.activities).toEqual([]);
      expect(result.current.performanceMetrics).toEqual({});
      expect(result.current.handoffRequests).toEqual([]);
    });
    
    it('should update data when WebSocket receives messages', () => {
      const { result } = renderHook(() => useMissionControlWebSocket());
      
      act(() => {
        // Simulate agent status update
        const agentMessage = {
          type: MessageTypes.AGENT_STATUS_UPDATE,
          payload: {
            agent_id: 'test_agent',
            status: 'active'
          }
        };
        
        result.current.ws._handleMessage(JSON.stringify(agentMessage));
      });
      
      expect(result.current.agents).toHaveLength(1);
      expect(result.current.agents[0].agent_id).toBe('test_agent');
    });
  });
});

describe('Performance and Stress Tests', () => {
  let client;
  
  beforeEach(async () => {
    client = new WebSocketClient('ws://localhost:8001/ws', {
      reconnectInterval: 100,
      maxReconnectAttempts: 3
    });
    await client.connect();
  });
  
  afterEach(() => {
    client.disconnect();
  });

  it('should handle high volume message sending', () => {
    const messageCount = 1000;
    let successCount = 0;
    
    for (let i = 0; i < messageCount; i++) {
      if (client.send('test_message', { index: i })) {
        successCount++;
      }
    }
    
    expect(successCount).toBe(messageCount);
    expect(client.stats.messagesSent).toBe(messageCount);
  });
  
  it('should handle high volume message receiving', (done) => {
    const messageCount = 1000;
    let receivedCount = 0;
    
    client.onMessage('bulk_test', () => {
      receivedCount++;
      if (receivedCount === messageCount) {
        expect(client.stats.messagesReceived).toBe(messageCount);
        done();
      }
    });
    
    // Simulate receiving many messages
    for (let i = 0; i < messageCount; i++) {
      const message = {
        type: 'bulk_test',
        payload: { index: i }
      };
      client._handleMessage(JSON.stringify(message));
    }
  });
  
  it('should maintain performance with many event listeners', () => {
    const listenerCount = 100;
    const handlers = [];
    
    // Add many handlers
    for (let i = 0; i < listenerCount; i++) {
      const handler = vi.fn();
      handlers.push(handler);
      client.onMessage('performance_test', handler);
    }
    
    const message = {
      type: 'performance_test',
      payload: { test: 'data' }
    };
    
    const startTime = performance.now();
    client._handleMessage(JSON.stringify(message));
    const endTime = performance.now();
    
    // Should complete within reasonable time (< 10ms)
    expect(endTime - startTime).toBeLessThan(10);
    
    // All handlers should have been called
    handlers.forEach(handler => {
      expect(handler).toHaveBeenCalledTimes(1);
    });
  });
});

describe('Integration Tests', () => {
  it('should integrate WebSocket client with Mission Control', async () => {
    const missionControlWS = getMissionControlWebSocket();
    
    // Simulate full workflow
    await missionControlWS.connect();
    
    // Agent registration
    const agentMessage = {
      type: MessageTypes.AGENT_STATUS_UPDATE,
      payload: {
        agent_id: 'integration_agent',
        status: 'active',
        current_task: 'Integration test'
      }
    };
    
    missionControlWS._handleMessage(JSON.stringify(agentMessage));
    
    // Activity
    const activityMessage = {
      type: MessageTypes.AGENT_ACTIVITY,
      payload: {
        activity_id: 'integration_activity',
        agent_id: 'integration_agent',
        title: 'Integration test activity'
      }
    };
    
    missionControlWS._handleMessage(JSON.stringify(activityMessage));
    
    // Decision
    const decisionMessage = {
      type: MessageTypes.AGENT_DECISION_EXPLANATION,
      payload: {
        decision_id: 'integration_decision',
        agent_id: 'integration_agent',
        decision_type: 'test'
      }
    };
    
    missionControlWS._handleMessage(JSON.stringify(decisionMessage));
    
    // Verify all data is available
    expect(missionControlWS.getAgents()).toHaveLength(1);
    expect(missionControlWS.getRecentActivities()).toHaveLength(1);
    expect(missionControlWS.getRecentDecisions()).toHaveLength(1);
    
    missionControlWS.disconnect();
  });
});
