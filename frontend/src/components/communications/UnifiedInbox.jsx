import React, { useState, useEffect } from 'react';
import ConversationList from './ConversationList';
import ChatInterface from './ChatInterface';
import API_CONFIG from '@/config/api';

/**
 * UnifiedInbox - Main container for Human in the Loop
 * 
 * Features:
 * - Unified view of all conversations (WhatsApp, Telegram, SMS)
 * - Real-time updates via WebSocket
 * - Human takeover capability
 * - Filter and search
 */
export default function UnifiedInbox() {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isTakenOver, setIsTakenOver] = useState(false);
  const [ws, setWs] = useState(null);

  // Fetch conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Fetch messages when conversation selected
  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.id);
      setIsTakenOver(false); // Reset takeover state
    }
  }, [selectedConversation]);

  // WebSocket for real-time updates
  useEffect(() => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) return;

    // Note: WebSocket URL should be wss:// in production
    const wsUrl = API_CONFIG.endpoint('ws/monitoring').replace('http', 'ws');
    const websocket = new WebSocket(`${wsUrl}?token=${token}`);

    websocket.onopen = () => {
      console.log('[WebSocket] Connected to monitoring');
      
      // Subscribe to conversation updates
      if (selectedConversation) {
        websocket.send(JSON.stringify({
          type: 'subscribe_conversation',
          conversation_id: selectedConversation.id
        }));
      }
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };

    websocket.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
    };

    websocket.onclose = () => {
      console.log('[WebSocket] Disconnected');
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [selectedConversation]);

  const handleWebSocketMessage = (message) => {
    console.log('[WebSocket] Message:', message);

    switch (message.type) {
      case 'new_message':
        // Add new message to current conversation
        if (message.conversation_id === selectedConversation?.id) {
          setMessages(prev => [...prev, message.message]);
        }
        
        // Update conversation list (last message)
        updateConversationLastMessage(message.conversation_id, message.message);
        break;

      case 'conversation_updated':
        // Update conversation status
        updateConversation(message.data);
        break;

      case 'new_conversation':
        // Add new conversation to list
        setConversations(prev => [message.data, ...prev]);
        break;

      default:
        break;
    }
  };

  const fetchConversations = async () => {
    setIsLoadingConversations(true);
    try {
      const response = await fetch(
        API_CONFIG.endpoint('conversations'),
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`,
            'X-Organization-ID': localStorage.getItem('current_organization_id') || localStorage.getItem('organization_id') || '1'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch conversations');
      }

      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Error fetching conversations:', error);
      // Use mock data for development
      setConversations(getMockConversations());
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const fetchMessages = async (conversationId) => {
    setIsLoadingMessages(true);
    try {
      const response = await fetch(
        API_CONFIG.endpoint(`conversations/${conversationId}/messages`),
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`,
            'X-Organization-ID': localStorage.getItem('current_organization_id') || localStorage.getItem('organization_id') || '1'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch messages');
      }

      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
      // Use mock data for development
      setMessages(getMockMessages(conversationId));
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const handleSendMessage = async (content) => {
    if (!selectedConversation) return;

    try {
      const response = await fetch(
        API_CONFIG.endpoint(`conversations/${selectedConversation.id}/messages`),
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`,
            'X-Organization-ID': localStorage.getItem('current_organization_id') || localStorage.getItem('organization_id') || '1',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content,
            role: 'assistant',
            metadata: {
              human_takeover: isTakenOver,
              agent_name: 'Dr. Ron' // TODO: Get from user context
            }
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      // Add message to list (if not already added via WebSocket)
      setMessages(prev => {
        const exists = prev.some(m => m.id === data.message.id);
        return exists ? prev : [...prev, data.message];
      });
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  };

  const handleTakeover = () => {
    setIsTakenOver(true);
    
    // Send system message
    const systemMessage = {
      id: `system-${Date.now()}`,
      conversation_id: selectedConversation.id,
      role: 'system',
      content: '👤 בן אדם השתלט על השיחה',
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, systemMessage]);
  };

  const updateConversationLastMessage = (conversationId, message) => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === conversationId) {
        return {
          ...conv,
          last_message: message.content,
          last_message_at: message.created_at,
          message_count: conv.message_count + 1
        };
      }
      return conv;
    }));
  };

  const updateConversation = (updatedConversation) => {
    setConversations(prev => prev.map(conv => 
      conv.id === updatedConversation.id ? updatedConversation : conv
    ));
    
    if (selectedConversation?.id === updatedConversation.id) {
      setSelectedConversation(updatedConversation);
    }
  };

  return (
    <div className="h-[calc(100vh-200px)] flex bg-slate-50 rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Left Sidebar - Conversation List */}
      <div className="w-96 flex-shrink-0">
        <ConversationList
          conversations={conversations}
          selectedConversation={selectedConversation}
          onSelectConversation={setSelectedConversation}
          isLoading={isLoadingConversations}
        />
      </div>

      {/* Main Area - Chat Interface */}
      <div className="flex-1">
        <ChatInterface
          conversation={selectedConversation}
          messages={messages}
          onSendMessage={handleSendMessage}
          onTakeover={handleTakeover}
          isLoading={isLoadingMessages}
          isTakenOver={isTakenOver}
        />
      </div>
    </div>
  );
}

// Mock data for development
function getMockConversations() {
  return [
    {
      id: '1',
      patient_name: 'משה כהן',
      patient_phone: '050-1234567',
      channel: 'whatsapp',
      status: 'active',
      last_message: 'שלום, מתי התור שלי?',
      last_message_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      message_count: 5
    },
    {
      id: '2',
      patient_name: 'שרה לוי',
      patient_phone: '052-9876543',
      channel: 'telegram',
      status: 'waiting',
      last_message: 'תודה רבה!',
      last_message_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      message_count: 3
    },
    {
      id: '3',
      patient_name: 'דוד כהן',
      patient_phone: '054-5555555',
      channel: 'sms',
      status: 'resolved',
      last_message: 'אוקי, מצוין',
      last_message_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
      message_count: 8
    }
  ];
}

function getMockMessages(conversationId) {
  return [
    {
      id: '1',
      conversation_id: conversationId,
      role: 'user',
      content: 'שלום, מתי התור שלי?',
      created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString()
    },
    {
      id: '2',
      conversation_id: conversationId,
      role: 'assistant',
      content: 'שלום! התור שלך ביום רביעי הקרוב בשעה 10:00. האם זה מתאים לך?',
      created_at: new Date(Date.now() - 9 * 60 * 1000).toISOString(),
      metadata: { agent_id: 'alex' }
    },
    {
      id: '3',
      conversation_id: conversationId,
      role: 'user',
      content: 'כן, תודה!',
      created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString()
    }
  ];
}
