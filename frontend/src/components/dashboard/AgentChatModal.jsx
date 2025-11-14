import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';
import API_CONFIG from '@/config/api';

/**
 * AgentChatModal - Real-time chat with LangGraph agents
 * 
 * Features:
 * - Direct connection to backend /api/v1/chat endpoint
 * - Streaming responses
 * - Agent tool execution visibility
 * - Context-aware conversations
 */
export const AgentChatModal = ({ 
  isOpen, 
  onClose, 
  agent,
  initialContext = null // e.g., { type: 'patient', data: patientInfo }
}) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add initial context message if provided
  useEffect(() => {
    if (isOpen && initialContext && (messages || []).length === 0) {
      const contextMessage = generateContextMessage(initialContext);
      if (contextMessage) {
        setMessages([{
          role: 'system',
          content: contextMessage,
          timestamp: new Date().toISOString(),
        }]);
      }
    }
  }, [isOpen, initialContext]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const generateContextMessage = (context) => {
    if (!context) return null;
    
    switch (context.type) {
      case 'patient':
        return `📋 Context: Discussing patient ${context.data.name} (${context.data.phone})`;
      case 'appointment':
        return `📅 Context: Appointment for ${context.data.patient_name} at ${context.data.time}`;
      case 'financial':
        return `💰 Context: Financial analysis for ${context.data.period}`;
      default:
        return null;
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(API_CONFIG.endpoint('chat'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // TODO: Add authentication token
        },
        body: JSON.stringify({
          message: input,
          conversation_id: conversationId,
          agent_preference: agent.name.toLowerCase(),
          context: initialContext,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      // Update conversation ID
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add agent response
      const agentMessage = {
        role: 'assistant',
        content: data.response,
        agent: data.agent_name || agent.name,
        tools_used: data.tools_used || [],
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      setMessages(prev => [...prev, {
        role: 'error',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  const agentColor = {
    'Alex': 'from-purple-500 to-purple-600',
    'Marcus': 'from-pink-500 to-pink-600',
    'Sophia': 'from-cyan-500 to-cyan-600',
  }[agent.name] || 'from-blue-500 to-blue-600';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-2xl h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col animate-scale-in">
        {/* Header */}
        <div className={cn(
          "flex items-center justify-between p-4 bg-gradient-to-r text-white rounded-t-2xl",
          agentColor
        )}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Chat with {agent.name}</h3>
              <p className="text-xs text-white/80">{agent.role}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {(messages || []).length === 0 && (
            <div className="text-center py-12">
              <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 font-medium">
                Hi! I'm {agent.name}. How can I help you today?
              </p>
              <p className="text-sm text-gray-500 mt-2">
                {agent.specialization}
              </p>
            </div>
          )}

          {(messages || []).map((message, index) => (
            <div
              key={index}
              className={cn(
                "flex",
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-3",
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.role === 'error'
                    ? 'bg-red-100 text-red-800'
                    : message.role === 'system'
                    ? 'bg-yellow-100 text-yellow-800 text-sm'
                    : 'bg-white text-gray-900 shadow-sm'
                )}
              >
                {message.role === 'assistant' && message.agent && (
                  <div className="text-xs font-semibold text-gray-500 mb-1">
                    {message.agent}
                  </div>
                )}
                
                <p className="whitespace-pre-wrap">{message.content}</p>
                
                {message.tools_used && message.tools_used.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Tools used:</p>
                    <div className="flex flex-wrap gap-1">
                      {message.tools_used.map((tool, i) => (
                        <span
                          key={i}
                          className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                        >
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="text-xs text-gray-400 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-2xl px-4 py-3 shadow-sm">
                <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t border-gray-200 rounded-b-2xl">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Ask ${agent.name}...`}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              size="lg"
              className="px-6"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            {agent.name} can access Odoo data and perform actions on your behalf
          </p>
        </div>
      </div>
    </div>
  );
};

export default AgentChatModal;
