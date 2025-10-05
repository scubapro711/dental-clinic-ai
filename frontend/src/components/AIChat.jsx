import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Send, Loader2, Sparkles, User, Bot, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Professional AI Chat Component with Vercel AI SDK + LangGraph Integration
 * 
 * Features:
 * - Real-time streaming responses
 * - Agent status indicators
 * - Markdown rendering
 * - Tool call visualization
 * - Conversation memory
 * - Beautiful UI with animations
 */
export default function AIChat({ user }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [conversationId] = useState(() => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [error, setError] = useState(null);
  const [toolCalls, setToolCalls] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Parse SSE stream
  const parseSSEStream = async (response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let currentMessage = { role: 'assistant', content: '', agent: null };

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'text') {
                // Skip duplicate content from different agents (e.g., alex + supervisor)
                if (currentMessage.content === data.content) {
                  // Same content, just update agent if needed
                  currentMessage.agent = data.metadata?.agent || currentMessage.agent;
                  continue;
                }
                
                currentMessage.content += data.content;
                currentMessage.agent = data.metadata?.agent || currentMessage.agent;
                setCurrentAgent(data.metadata?.agent);
                setIsThinking(false);
                
                // Update messages in real-time
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage && lastMessage.role === 'assistant' && lastMessage.isStreaming) {
                    lastMessage.content = currentMessage.content;
                    lastMessage.agent = currentMessage.agent;
                    lastMessage.toolCalls = currentMessage.toolCalls || [];
                  } else {
                    newMessages.push({ ...currentMessage, isStreaming: true, toolCalls: [] });
                  }
                  return newMessages;
                });
              } else if (data.type === 'tool_call') {
                // Add tool call to current message
                setIsThinking(true);
                const toolCall = {
                  name: data.tool_name,
                  input: data.tool_input,
                  output: data.tool_output,
                  timestamp: Date.now()
                };
                
                if (!currentMessage.toolCalls) {
                  currentMessage.toolCalls = [];
                }
                currentMessage.toolCalls.push(toolCall);
                
                // Update messages with tool call
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage && lastMessage.role === 'assistant' && lastMessage.isStreaming) {
                    lastMessage.toolCalls = currentMessage.toolCalls;
                  }
                  return newMessages;
                });
                
                console.log('Tool call:', data.tool_name, data.tool_input);
              } else if (data.type === 'suggested_actions') {
                // Handle suggested actions (Phase 7: Agentic System)
                const actions = data.metadata?.suggested_actions;
                if (actions && actions.length > 0) {
                  setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.role === 'assistant') {
                      lastMessage.suggestedActions = actions;
                    }
                    return newMessages;
                  });
                  console.log('Suggested actions:', actions);
                }
              } else if (data.type === 'done') {
                // Finalize message
                setIsThinking(false); // Clear "Using tools..." indicator
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage && lastMessage.isStreaming) {
                    lastMessage.isStreaming = false;
                  }
                  return newMessages;
                });
                break;
              } else if (data.type === 'error') {
                setError(data.message);
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Stream reading error:', error);
        setError('Connection interrupted');
      }
    }
  };

  // Send message
  const sendMessage = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    // Create abort controller for this request
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('http://localhost:8000/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Auth will be added later
        },
        body: JSON.stringify({
          messages: [
            ...messages.filter(m => !m.isStreaming).map(m => ({ role: m.role, content: m.content })),
            { role: 'user', content: userMessage.content }
          ],
          conversation_id: conversationId,
          stream: true,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      await parseSSEStream(response);
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Error sending message:', error);
        setError('Failed to send message. Please try again.');
      }
    } finally {
      setIsLoading(false);
      setCurrentAgent(null);
    }
  };

  // Stop generation
  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
      setCurrentAgent(null);
    }
  };

  // Clear chat
  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  // Agent badge component
  const AgentBadge = ({ agent }) => {
    const agentConfig = {
      alex: { label: 'Alex', color: 'bg-blue-500' },
      cfo: { label: 'CFO', color: 'bg-green-500' },
      admin: { label: 'Admin', color: 'bg-purple-500' },
    };

    const config = agentConfig[agent] || { label: agent, color: 'bg-gray-500' };

    return (
      <Badge className={cn('text-xs', config.color)}>
        {config.label}
      </Badge>
    );
  };

  // Message component
  const Message = ({ message }) => {
    const isUser = message.role === 'user';

    return (
      <div className={cn('flex gap-3 mb-4', isUser ? 'justify-end' : 'justify-start')}>
        {!isUser && (
          <div className="flex-shrink-0">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
          </div>
        )}
        
        <div className={cn('flex flex-col gap-1 max-w-[80%]', isUser && 'items-end')}>
          {!isUser && message.agent && (
            <AgentBadge agent={message.agent} />
          )}
          
          {/* Tool Calls Display */}
          {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
            <div className="space-y-2 mb-2">
              {message.toolCalls.map((tool, idx) => (
                <div
                  key={idx}
                  className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 text-xs"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Sparkles className="w-3 h-3 text-blue-600" />
                    <span className="font-semibold text-blue-900">
                      Using tool: {tool.name}
                    </span>
                  </div>
                  {tool.input && (
                    <div className="text-blue-700 ml-5">
                      Input: {JSON.stringify(tool.input)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          
          <div
            className={cn(
              'rounded-2xl px-4 py-3 shadow-sm',
              isUser
                ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white'
                : 'bg-white border border-gray-200'
            )}
          >
            <p className="text-sm whitespace-pre-wrap break-words">
              {message.content}
            </p>
            {message.isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
            )}
          </div>
          
          {/* Suggested Actions (Phase 7: Agentic System) */}
          {!isUser && message.suggestedActions && message.suggestedActions.length > 0 && (
            <div className="mt-3 space-y-2 w-full">
              <div className="text-xs font-semibold text-gray-600 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Suggested Actions
              </div>
              <div className="flex flex-wrap gap-2">
                {message.suggestedActions.map((action, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    className="text-xs hover:bg-blue-50 hover:border-blue-300 transition-colors"
                    onClick={() => {
                      // Handle action click
                      console.log('Action clicked:', action);
                      setInput(action.label);
                    }}
                  >
                    <span className="font-medium">{action.label}</span>
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>

        {isUser && (
          <div className="flex-shrink-0">
            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
              <User className="w-5 h-5 text-gray-600" />
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className="h-full flex flex-col shadow-lg">
      <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <CardTitle>AI Assistant</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {currentAgent && (
              <div className="flex items-center gap-2 animate-pulse">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <AgentBadge agent={currentAgent} />
              </div>
            )}
            <Button variant="ghost" size="sm" onClick={clearChat}>
              Clear
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0 flex flex-col">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Welcome to DentalAI!</h3>
              <p className="text-sm text-gray-600 max-w-md">
                I'm your AI dental assistant. I can help you with appointments, billing, medical questions, and more.
              </p>
              <div className="mt-6 grid grid-cols-1 gap-2 w-full max-w-md">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInput("I need to schedule an appointment")}
                  className="text-left justify-start"
                >
                  📅 Schedule an appointment
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInput("What is our revenue this month?")}
                  className="text-left justify-start"
                >
                  💰 Check revenue
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInput("Show me today's schedule")}
                  className="text-left justify-start"
                >
                  📋 View schedule
                </Button>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <Message key={index} message={message} />
          ))}

          {/* Thinking Indicator */}
          {isThinking && (
            <div className="flex gap-3 mb-4 justify-start">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="flex flex-col gap-1">
                {currentAgent && <AgentBadge agent={currentAgent} />}
                <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                    <span className="text-sm text-blue-900 font-medium">
                      Using tools...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-4">
          <form onSubmit={sendMessage} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1"
            />
            {isLoading ? (
              <Button type="button" onClick={stopGeneration} variant="destructive">
                Stop
              </Button>
            ) : (
              <Button type="submit" disabled={!input.trim()}>
                <Send className="w-4 h-4" />
              </Button>
            )}
          </form>
        </div>
      </CardContent>
    </Card>
  );
}
