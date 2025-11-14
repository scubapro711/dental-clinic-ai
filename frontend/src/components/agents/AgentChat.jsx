import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Send, MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import API_CONFIG from '@/config/api';

/**
 * AgentChat Component
 * 
 * Chat interface for direct communication with a specific agent.
 * Pre-fills agent context and maintains conversation history.
 * 
 * @param {Object} props
 * @param {string} props.agentId - Agent ID
 * @param {string} props.agentName - Agent display name
 * @param {string} props.agentColor - Agent theme color
 */
const AgentChat = ({ agentId, agentName, agentColor }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hi! I'm ${agentName}. How can I help you today?`,
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(API_CONFIG.endpoint('chat/stream'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        },
        body: JSON.stringify({
          message: input.trim(),
          agent: agentId,
          thread_id: `agent-${agentId}-${Date.now()}`,
          context: {
            page: 'agent_detail',
            agent_name: agentName
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage = {
          role: 'assistant',
          content: data.response || 'I\'m here to help!',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm flex flex-col h-[600px]">
      {/* Chat Header */}
      <div
        className="p-4 border-b flex items-center gap-3"
        style={{ borderColor: `${agentColor}40` }}
      >
        <div
          className="p-2 rounded-lg"
          style={{ backgroundColor: `${agentColor}20` }}
        >
          <MessageCircle className="w-5 h-5" style={{ color: agentColor }} />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">Chat with {agentName}</h3>
          <p className="text-xs text-gray-500">Ask questions or request actions</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
              style={
                message.role === 'assistant'
                  ? { backgroundColor: `${agentColor}10`, borderLeft: `3px solid ${agentColor}` }
                  : {}
              }
            >
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              <div
                className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div
              className="rounded-lg p-3"
              style={{ backgroundColor: `${agentColor}10` }}
            >
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask ${agentName}...`}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-opacity-50"
            style={{ focusRingColor: agentColor }}
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="gap-2"
            style={{ backgroundColor: agentColor }}
          >
            <Send className="w-4 h-4" />
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};

AgentChat.propTypes = {
  agentId: PropTypes.string.isRequired,
  agentName: PropTypes.string.isRequired,
  agentColor: PropTypes.string.isRequired,
};

export default AgentChat;
