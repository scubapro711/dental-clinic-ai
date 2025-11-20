import React, { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, Phone, User, ArrowRight, UserCog } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import MessageBubble from './MessageBubble';

/**
 * ChatInterface - Main chat area
 * 
 * Props:
 * - conversation: Selected conversation
 * - messages: Array of messages
 * - onSendMessage: Handler for sending a message
 * - onTakeover: Handler for human takeover
 * - isLoading: Loading state
 * - isTakenOver: Whether human has taken over
 */
export default function ChatInterface({ 
  conversation, 
  messages, 
  onSendMessage,
  onTakeover,
  isLoading,
  isTakenOver 
}) {
  const [messageText, setMessageText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!messageText.trim() || isSending) return;

    setIsSending(true);
    try {
      await onSendMessage(messageText);
      setMessageText('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getChannelIcon = (channel) => {
    const iconProps = { className: "w-5 h-5" };
    switch (channel) {
      case 'whatsapp':
        return <MessageCircle {...iconProps} className="w-5 h-5 text-green-600" />;
      case 'telegram':
        return <Send {...iconProps} className="w-5 h-5 text-blue-600" />;
      case 'sms':
        return <Phone {...iconProps} className="w-5 h-5 text-purple-600" />;
      default:
        return <MessageCircle {...iconProps} className="w-5 h-5 text-gray-600" />;
    }
  };

  const getChannelName = (channel) => {
    const names = {
      'whatsapp': 'WhatsApp',
      'telegram': 'Telegram',
      'sms': 'SMS',
      'web': 'Web',
    };
    return names[channel] || channel;
  };

  const getStatusBadge = (status) => {
    const config = {
      active: { label: 'פעיל', className: 'bg-green-100 text-green-800' },
      waiting: { label: 'ממתין', className: 'bg-yellow-100 text-yellow-800' },
      escalated: { label: 'הועבר לרופא', className: 'bg-red-100 text-red-800' },
      resolved: { label: 'טופל', className: 'bg-blue-100 text-blue-800' },
      archived: { label: 'ארכיון', className: 'bg-gray-100 text-gray-800' },
    };
    return config[status] || config.active;
  };

  if (!conversation) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-slate-50">
        <MessageCircle className="w-16 h-16 text-slate-400 mb-4" />
        <h3 className="text-lg font-semibold text-slate-600 mb-2">
          בחר שיחה להתחיל
        </h3>
        <p className="text-slate-500 text-center max-w-md">
          בחר שיחה מהרשימה משמאל כדי להציג את ההודעות ולהשתלט על השיחה
        </p>
      </div>
    );
  }

  const statusConfig = getStatusBadge(conversation.status);

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-slate-200/60 p-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          {/* Patient Info */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-lg font-bold">
              {conversation.patient_name?.charAt(0) || '?'}
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                {conversation.patient_name || conversation.patient_phone || 'לא ידוע'}
              </h2>
              <div className="flex items-center gap-2 text-sm text-slate-600">
                {getChannelIcon(conversation.channel)}
                <span>{getChannelName(conversation.channel)}</span>
                {conversation.patient_phone && (
                  <>
                    <span>•</span>
                    <span>{conversation.patient_phone}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Status & Actions */}
          <div className="flex items-center gap-3">
            <Badge className={`${statusConfig.className} hover:${statusConfig.className}`}>
              {statusConfig.label}
            </Badge>
            
            {!isTakenOver && conversation.status === 'active' && (
              <Button
                onClick={onTakeover}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all"
              >
                <UserCog className="w-4 h-4 ml-1" />
                השתלט על השיחה
              </Button>
            )}

            {isTakenOver && (
              <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-100">
                <User className="w-3 h-3 ml-1" />
                אתה בשליטה
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 bg-slate-50">
        {isLoading ? (
          // Loading skeleton
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className={`flex ${i % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
                  <div className="bg-slate-200 rounded-2xl px-4 py-2 w-1/2 h-16" />
                </div>
              </div>
            ))}
          </div>
        ) : messages.length === 0 ? (
          // Empty state
          <div className="text-center py-12">
            <MessageCircle className="w-12 h-12 mx-auto mb-3 text-slate-400" />
            <p className="text-slate-600">אין הודעות עדיין</p>
            <p className="text-sm text-slate-500">התחל שיחה עם המטופל</p>
          </div>
        ) : (
          // Message list
          <div>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Message Input */}
      {(isTakenOver || conversation.status === 'active') && (
        <div className="border-t border-slate-200 p-4 bg-white">
          <div className="flex gap-3">
            <Textarea
              placeholder="הקלד הודעה..."
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 min-h-[60px] max-h-[120px] rounded-xl resize-none"
              disabled={isSending}
            />
            <Button
              onClick={handleSend}
              disabled={!messageText.trim() || isSending}
              className="bg-blue-600 hover:bg-blue-700 rounded-xl px-6"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
          {isTakenOver && (
            <p className="text-xs text-purple-600 mt-2">
              💜 אתה בשליטה - ההודעות שלך יישלחו למטופל
            </p>
          )}
        </div>
      )}

      {conversation.status === 'resolved' && (
        <div className="border-t border-slate-200 p-4 bg-blue-50 text-center">
          <p className="text-sm text-blue-800">
            ✓ שיחה זו סומנה כטופלה
          </p>
        </div>
      )}

      {conversation.status === 'archived' && (
        <div className="border-t border-slate-200 p-4 bg-gray-50 text-center">
          <p className="text-sm text-gray-800">
            📦 שיחה זו בארכיון
          </p>
        </div>
      )}
    </div>
  );
}
