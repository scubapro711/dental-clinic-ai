import React from 'react';
import { Bot, User, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';
import { he } from 'date-fns/locale';

/**
 * MessageBubble - Individual message in chat
 * 
 * Props:
 * - message: Message object
 */
export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const isSystem = message.role === 'system';

  const getAgentName = () => {
    if (message.metadata?.human_takeover) {
      return message.metadata?.agent_name || 'בן אדם';
    }
    if (message.metadata?.agent_id) {
      const agentNames = {
        'alex': 'Alex',
        'sarah': 'Sarah',
        'marcus': 'Marcus',
        'sophia': 'Sophia',
        'harper': 'Harper',
      };
      return agentNames[message.metadata.agent_id] || 'AI';
    }
    return 'AI';
  };

  const formatTime = (timestamp) => {
    try {
      return format(new Date(timestamp), 'HH:mm', { locale: he });
    } catch {
      return '';
    }
  };

  // System message (center, yellow)
  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <div className="flex items-center gap-2 bg-yellow-100 text-yellow-900 rounded-xl px-3 py-1 text-sm">
          <AlertCircle className="w-4 h-4" />
          <span>{message.content}</span>
        </div>
      </div>
    );
  }

  // User message (right, blue)
  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="flex flex-col items-end max-w-[70%]">
          <div className="bg-blue-600 text-white rounded-2xl px-4 py-2">
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
          <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
            <User className="w-3 h-3" />
            <span>מטופל</span>
            <span>•</span>
            <span>{formatTime(message.created_at)}</span>
          </div>
        </div>
      </div>
    );
  }

  // Assistant message (left, gray)
  if (isAssistant) {
    const agentName = getAgentName();
    const isHuman = message.metadata?.human_takeover;

    return (
      <div className="flex justify-start mb-4">
        <div className="flex flex-col items-start max-w-[70%]">
          <div className={`
            rounded-2xl px-4 py-2
            ${isHuman 
              ? 'bg-gradient-to-r from-purple-100 to-blue-100 text-slate-900 border-2 border-purple-300' 
              : 'bg-slate-100 text-slate-900'
            }
          `}>
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
          <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
            <Bot className="w-3 h-3" />
            <span className={isHuman ? 'font-semibold text-purple-600' : ''}>
              {agentName}
            </span>
            {isHuman && (
              <>
                <span>•</span>
                <span className="text-purple-600 font-semibold">השתלטות אנושית</span>
              </>
            )}
            <span>•</span>
            <span>{formatTime(message.created_at)}</span>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
