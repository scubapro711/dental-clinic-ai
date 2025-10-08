import React, { useState, useRef, useEffect } from 'react';
import { Send, UserPlus, X, Edit2, Bot, User } from 'lucide-react';

/**
 * Conversation Detail Component - פרטי שיחה
 * 
 * Layout (from PDF):
 * - Header: Patient name + Edit button
 * - Messages area: Scrollable chat history
 * - Footer: Human handoff input (100px height)
 * 
 * Features:
 * - Display conversation messages
 * - Show agent vs human messages
 * - Human handoff input
 * - Send message as human
 * - Transfer to human agent
 * - Close conversation
 */
export default function ConversationDetail({ conversation }) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState(conversation.messages || []);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Load messages for this conversation
  useEffect(() => {
    loadMessages();
  }, [conversation.id]);
  
  const loadMessages = async () => {
    try {
      const response = await fetch(`/api/v1/conversations/${conversation.id}/messages`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };
  
  // Send message as human
  const handleSendMessage = async () => {
    if (!message.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/conversations/${conversation.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        },
        body: JSON.stringify({
          content: message,
          from: 'human',
          sender_type: 'staff'
        })
      });
      
      if (response.ok) {
        const newMessage = await response.json();
        setMessages([...messages, newMessage]);
        setMessage('');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('שגיאה בשליחת ההודעה');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Transfer to human agent
  const handleTransferToHuman = async () => {
    if (!confirm('האם להעביר שיחה זו לטיפול אנושי?')) return;
    
    try {
      const response = await fetch(`/api/v1/handoff/${conversation.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        },
        body: JSON.stringify({
          reason: 'Manual transfer from mission control',
          message: message || 'העברה לטיפול אנושי'
        })
      });
      
      if (response.ok) {
        alert('השיחה הועברה לטיפול אנושי בהצלחה');
        setMessage('');
      }
    } catch (error) {
      console.error('Failed to transfer:', error);
      alert('שגיאה בהעברה לטיפול אנושי');
    }
  };
  
  // Close conversation
  const handleCloseConversation = async () => {
    if (!confirm('האם לסגור שיחה זו?')) return;
    
    try {
      const response = await fetch(`/api/v1/conversations/${conversation.id}/close`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      
      if (response.ok) {
        alert('השיחה נסגרה בהצלחה');
      }
    } catch (error) {
      console.error('Failed to close conversation:', error);
      alert('שגיאה בסגירת השיחה');
    }
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Header - Patient Name + Edit */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium text-lg">
            {conversation.patient_name?.charAt(0) || '?'}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {conversation.patient_name || 'לא ידוע'}
            </h3>
            <p className="text-sm text-gray-500">
              ID: {conversation.patient_id || 'N/A'}
            </p>
          </div>
        </div>
        
        <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
          <Edit2 className="w-5 h-5 text-gray-600" />
        </button>
      </div>
      
      {/* Messages Area - Scrollable */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <p>אין הודעות בשיחה זו</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, index) => (
              <MessageBubble key={index} message={msg} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* Footer - Human Handoff Input (100px height) */}
      <div className="h-[100px] border-t border-gray-200 p-4 bg-white">
        <div className="flex gap-2 h-full">
          {/* Text Input */}
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="💬 הקלד את תגובת האנושית..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          
          {/* Action Buttons */}
          <div className="flex flex-col gap-2">
            <button
              onClick={handleSendMessage}
              disabled={!message.trim() || isLoading}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              שלח
            </button>
            
            <div className="flex gap-2">
              <button
                onClick={handleTransferToHuman}
                className="px-3 py-1 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors flex items-center gap-1 text-sm"
              >
                <UserPlus className="w-4 h-4" />
                העבר
              </button>
              
              <button
                onClick={handleCloseConversation}
                className="px-3 py-1 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center gap-1 text-sm"
              >
                <X className="w-4 h-4" />
                סגור
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Message Bubble Component
 */
function MessageBubble({ message }) {
  const isAgent = message.sender_type === 'agent' || message.from === 'assistant';
  const isHuman = message.sender_type === 'staff' || message.from === 'human';
  
  return (
    <div className={`flex ${isAgent ? 'justify-start' : 'justify-end'}`}>
      <div className={`max-w-[70%] ${isAgent ? 'order-2' : 'order-1'}`}>
        {/* Sender Label */}
        <div className={`flex items-center gap-2 mb-1 ${isAgent ? '' : 'justify-end'}`}>
          {isAgent ? (
            <>
              <Bot className="w-4 h-4 text-blue-500" />
              <span className="text-xs text-gray-500">
                {message.agent_name || 'AI Agent'}
              </span>
            </>
          ) : (
            <>
              <span className="text-xs text-gray-500">
                {message.sender_name || 'צוות'}
              </span>
              <User className="w-4 h-4 text-green-500" />
            </>
          )}
        </div>
        
        {/* Message Content */}
        <div
          className={`px-4 py-2 rounded-lg ${
            isAgent
              ? 'bg-white border border-gray-200'
              : 'bg-blue-500 text-white'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          
          {/* Timestamp */}
          <p className={`text-xs mt-1 ${isAgent ? 'text-gray-400' : 'text-blue-100'}`}>
            {new Date(message.timestamp).toLocaleTimeString('he-IL', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </p>
        </div>
      </div>
    </div>
  );
}
