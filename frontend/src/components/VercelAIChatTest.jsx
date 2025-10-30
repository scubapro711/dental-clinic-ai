/**
 * Vercel AI Chat Test Component
 * 
 * Simple test component to verify Vercel AI SDK integration.
 * This will be replaced with full AI Elements UI in Phase 3.
 */

import React, { useState, useRef, useEffect } from 'react';
import { useAIChat } from '../hooks/useAIChat';
import { Card } from './ui/Card';
import { Button } from './ui/Button';

export function VercelAIChatTest() {
  const {
    messages,
    isLoading,
    error,
    conversationId,
    currentAgent,
    streamingMessage,
    sendMessage,
    clear,
  } = useAIChat({
    onError: (err) => {
      console.error('Chat error:', err);
    },
    onFinish: (message) => {
      console.log('Message finished:', message);
    },
  });
  
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      sendMessage(input);
      setInput('');
    }
  };
  
  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold mb-2">
          Vercel AI SDK Test
        </h1>
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>Conversation: {conversationId}</span>
          {currentAgent && (
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
              Agent: {currentAgent}
            </span>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={clear}
          >
            Clear Chat
          </Button>
        </div>
      </div>
      
      {/* Messages */}
      <Card className="flex-1 overflow-y-auto p-4 mb-4 space-y-4">
        {(messages || []).length === 0 && !streamingMessage && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg mb-2">👋 Hello!</p>
            <p>Try asking:</p>
            <ul className="mt-2 space-y-1">
              <li>"Schedule an appointment for next Monday"</li>
              <li>"What is our revenue this month?"</li>
              <li>"Show me today's appointments"</li>
            </ul>
          </div>
        )}
        
        {(messages || []).map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[70%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.error
                  ? 'bg-red-100 text-red-900'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              {message.role === 'assistant' && message.agent && (
                <div className="text-xs opacity-70 mb-1">
                  {message.agent}
                </div>
              )}
              <div className="whitespace-pre-wrap">{message.content}</div>
              {message.toolCalls && message.toolCalls.length > 0 && (
                <div className="mt-2 text-xs opacity-70 border-t pt-2">
                  <div className="font-semibold">Tools used:</div>
                  {message.toolCalls.map((tool, i) => (
                    <div key={i}>• {tool.tool_name}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* Streaming message */}
        {streamingMessage && (
          <div className="flex justify-start">
            <div className="max-w-[70%] rounded-lg px-4 py-2 bg-gray-100 text-gray-900">
              {currentAgent && (
                <div className="text-xs opacity-70 mb-1">
                  {currentAgent}
                </div>
              )}
              <div className="whitespace-pre-wrap">
                {streamingMessage}
                <span className="inline-block w-2 h-4 ml-1 bg-gray-400 animate-pulse" />
              </div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="text-center text-red-600 p-4 bg-red-50 rounded">
            Error: {error.message}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </Card>
      
      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <Button
          type="submit"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </Button>
      </form>
    </div>
  );
}

export default VercelAIChatTest;
