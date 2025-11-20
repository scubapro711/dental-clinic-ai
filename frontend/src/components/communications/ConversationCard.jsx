import React from 'react';
import { MessageCircle, Send, Phone, MessageSquare } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import { he } from 'date-fns/locale';

/**
 * ConversationCard - Individual conversation in the list
 * 
 * Props:
 * - conversation: Conversation object
 * - isActive: Whether this conversation is selected
 * - onClick: Handler for clicking the card
 */
export default function ConversationCard({ conversation, isActive, onClick }) {
  const getChannelIcon = (channel) => {
    const iconProps = { className: "w-4 h-4" };
    switch (channel) {
      case 'whatsapp':
        return <MessageCircle {...iconProps} className="w-4 h-4 text-green-600" />;
      case 'telegram':
        return <Send {...iconProps} className="w-4 h-4 text-blue-600" />;
      case 'sms':
        return <Phone {...iconProps} className="w-4 h-4 text-purple-600" />;
      default:
        return <MessageSquare {...iconProps} className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status) => {
    const config = {
      active: { label: 'פעיל', className: 'bg-green-100 text-green-800' },
      waiting: { label: 'ממתין', className: 'bg-yellow-100 text-yellow-800' },
      escalated: { label: 'הועבר', className: 'bg-red-100 text-red-800' },
      resolved: { label: 'טופל', className: 'bg-blue-100 text-blue-800' },
      archived: { label: 'ארכיון', className: 'bg-gray-100 text-gray-800' },
    };
    return config[status] || config.active;
  };

  const getTimeAgo = (timestamp) => {
    if (!timestamp) return '';
    try {
      return formatDistanceToNow(new Date(timestamp), { 
        addSuffix: true, 
        locale: he 
      });
    } catch {
      return '';
    }
  };

  const statusConfig = getStatusBadge(conversation.status);

  return (
    <div
      onClick={onClick}
      className={`
        p-4 rounded-2xl shadow-sm border cursor-pointer
        transition-all duration-200
        ${isActive 
          ? 'bg-blue-50 border-blue-200 shadow-md' 
          : 'bg-white border-slate-200 hover:bg-blue-50/30 hover:shadow-lg'
        }
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          {getChannelIcon(conversation.channel)}
          <h3 className="font-semibold text-slate-900">
            {conversation.patient_name || conversation.patient_phone || 'לא ידוע'}
          </h3>
        </div>
        <Badge className={`${statusConfig.className} hover:${statusConfig.className} text-xs`}>
          {statusConfig.label}
        </Badge>
      </div>

      {/* Last Message Preview */}
      {conversation.last_message && (
        <p className="text-sm text-slate-600 mb-2 line-clamp-2">
          {conversation.last_message}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>{getTimeAgo(conversation.last_message_at)}</span>
        <span>{conversation.message_count} הודעות</span>
      </div>
    </div>
  );
}
