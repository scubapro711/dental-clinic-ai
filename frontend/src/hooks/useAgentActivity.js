import { useState, useCallback } from 'react';

/**
 * useAgentActivity Hook
 * 
 * Manages agent activity state for transparency panel
 * - Tracks current agent activity
 * - Manages tool calls
 * - Handles activity lifecycle
 */
export default function useAgentActivity() {
  const [activity, setActivity] = useState(null);
  const [toolCalls, setToolCalls] = useState([]);

  // Start agent activity
  const startActivity = useCallback((agent, task) => {
    setActivity({
      agent,
      task,
      status: 'running',
      progress: 0,
      startTime: Date.now()
    });
    setToolCalls([]);
  }, []);

  // Update activity progress
  const updateProgress = useCallback((progress) => {
    setActivity(prev => prev ? { ...prev, progress } : null);
  }, []);

  // Add tool call
  const addToolCall = useCallback((toolCall) => {
    setToolCalls(prev => {
      // Check if tool already exists (update it)
      const existingIndex = prev.findIndex(t => t.name === toolCall.name && t.status === 'running');
      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex] = { ...updated[existingIndex], ...toolCall };
        return updated;
      }
      // Add new tool call
      return [...prev, { ...toolCall, timestamp: Date.now() }];
    });
  }, []);

  // Update tool call status
  const updateToolCall = useCallback((toolName, updates) => {
    setToolCalls(prev => 
      prev.map(tool => 
        tool.name === toolName ? { ...tool, ...updates } : tool
      )
    );
  }, []);

  // Complete activity
  const completeActivity = useCallback(() => {
    setActivity(prev => prev ? { ...prev, status: 'completed' } : null);
  }, []);

  // Clear activity
  const clearActivity = useCallback(() => {
    setActivity(null);
    setToolCalls([]);
  }, []);

  // Handle stream event
  const handleStreamEvent = useCallback((event) => {
    switch (event.type) {
      case 'agent_start':
        startActivity(event.agent, event.task || 'Processing...');
        break;

      case 'agent_progress':
        updateProgress(event.progress);
        break;

      case 'tool_start':
        addToolCall({
          name: event.tool_name,
          status: 'running',
          input: event.tool_input
        });
        break;

      case 'tool_complete':
        updateToolCall(event.tool_name, {
          status: 'success',
          output: event.tool_output,
          duration: event.duration
        });
        break;

      case 'tool_error':
        updateToolCall(event.tool_name, {
          status: 'error',
          error: event.error
        });
        break;

      case 'agent_complete':
        completeActivity();
        break;

      case 'agent_error':
        setActivity(prev => prev ? { ...prev, status: 'error', error: event.error } : null);
        break;

      default:
        break;
    }
  }, [startActivity, updateProgress, addToolCall, updateToolCall, completeActivity]);

  return {
    activity,
    toolCalls,
    startActivity,
    updateProgress,
    addToolCall,
    updateToolCall,
    completeActivity,
    clearActivity,
    handleStreamEvent
  };
}
