/**
 * useAIChat Hook
 * 
 * Custom React hook for chat functionality using Vercel AI SDK.
 * This hook provides a clean interface for interacting with our LangGraph agents.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { sendChatMessage, parseSSEStream, getConversation } from '../lib/vercel-ai-config';

/**
 * Generate a unique conversation ID
 */
function generateConversationId() {
  return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * useAIChat hook
 * 
 * @param {Object} options - Hook options
 * @param {string} options.conversationId - Optional conversation ID
 * @param {Function} options.onError - Error callback
 * @param {Function} options.onFinish - Finish callback
 * @returns {Object} Chat state and methods
 */
export function useAIChat(options = {}) {
  const {
    conversationId: initialConversationId,
    onError,
    onFinish,
  } = options;
  
  // State
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(
    initialConversationId || generateConversationId()
  );
  const [currentAgent, setCurrentAgent] = useState(null);
  const [streamingMessage, setStreamingMessage] = useState('');
  
  // Refs
  const abortControllerRef = useRef(null);
  
  /**
   * Load conversation history
   */
  const loadConversation = useCallback(async (convId) => {
    try {
      const data = await getConversation(convId);
      setMessages(data.messages || []);
      setCurrentAgent(data.metadata?.current_agent);
    } catch (err) {
      console.error('Failed to load conversation:', err);
      setError(err);
      onError?.(err);
    }
  }, [onError]);
  
  /**
   * Send a message
   */
  const sendMessage = useCallback(async (content) => {
    if (!content.trim()) {
      return;
    }
    
    // Add user message immediately
    const userMessage = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    setStreamingMessage('');
    
    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();
    
    try {
      // Prepare messages for API
      const apiMessages = [...messages, userMessage];
      
      // Send message with streaming
      const response = await sendChatMessage(
        apiMessages,
        conversationId,
        true // Enable streaming
      );
      
      let fullMessage = '';
      let agent = null;
      let toolCalls = [];
      
      // Parse SSE stream
      await parseSSEStream(response, (chunk) => {
        const { type, content, tool_name, tool_output, metadata } = chunk;
        
        if (type === 'text') {
          fullMessage += content;
          setStreamingMessage(fullMessage);
          
          if (metadata?.agent) {
            agent = metadata.agent;
            setCurrentAgent(agent);
          }
        } else if (type === 'tool_call') {
          toolCalls.push({ tool_name, tool_output });
        } else if (type === 'done') {
          // Streaming complete
          const assistantMessage = {
            role: 'assistant',
            content: fullMessage,
            agent,
            toolCalls,
          };
          
          setMessages(prev => [...prev, assistantMessage]);
          setStreamingMessage('');
          setIsLoading(false);
          
          onFinish?.(assistantMessage);
        } else if (type === 'error') {
          throw new Error(content || 'Unknown error');
        }
      });
      
    } catch (err) {
      console.error('Chat error:', err);
      setError(err);
      setIsLoading(false);
      setStreamingMessage('');
      onError?.(err);
      
      // Add error message
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          error: true,
        },
      ]);
    }
  }, [messages, conversationId, onError, onFinish]);
  
  /**
   * Reload conversation
   */
  const reload = useCallback(async () => {
    if (conversationId) {
      await loadConversation(conversationId);
    }
  }, [conversationId, loadConversation]);
  
  /**
   * Stop streaming
   */
  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
      setStreamingMessage('');
    }
  }, []);
  
  /**
   * Clear messages
   */
  const clear = useCallback(() => {
    setMessages([]);
    setStreamingMessage('');
    setError(null);
    setCurrentAgent(null);
    setConversationId(generateConversationId());
  }, []);
  
  /**
   * Append a message manually
   */
  const append = useCallback((message) => {
    setMessages(prev => [...prev, message]);
  }, []);
  
  /**
   * Set messages manually
   */
  const setMessagesManually = useCallback((newMessages) => {
    setMessages(newMessages);
  }, []);
  
  // Load conversation on mount if ID provided
  useEffect(() => {
    if (initialConversationId) {
      loadConversation(initialConversationId);
    }
  }, [initialConversationId, loadConversation]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);
  
  return {
    // State
    messages,
    isLoading,
    error,
    conversationId,
    currentAgent,
    streamingMessage,
    
    // Methods
    sendMessage,
    reload,
    stop,
    clear,
    append,
    setMessages: setMessagesManually,
    
    // Computed
    hasMessages: messages.length > 0,
  };
}

export default useAIChat;
