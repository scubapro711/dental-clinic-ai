import React, { useState, useEffect } from 'react';
import { MessageSquare, Trash2, Plus, Clock } from 'lucide-react';

const ConversationHistorySidebar = ({ 
  isOpen, 
  onClose, 
  onSelectConversation,
  onNewConversation,
  currentConversationId 
}) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadConversations();
    }
  }, [isOpen]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/ai/conversations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    
    if (!confirm('האם אתה בטוח שברצונך למחוק שיחה זו?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/ai/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        }
      });

      if (response.ok) {
        setConversations(conversations.filter(c => c.id !== conversationId));
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'עכשיו';
    if (diffMins < 60) return `לפני ${diffMins} דקות`;
    if (diffHours < 24) return `לפני ${diffHours} שעות`;
    if (diffDays < 7) return `לפני ${diffDays} ימים`;
    
    return date.toLocaleDateString('he-IL', { 
      day: 'numeric', 
      month: 'short' 
    });
  };

  const getAgentColor = (agent) => {
    const colors = {
      alex: 'text-blue-600',
      cfo: 'text-green-600',
      admin: 'text-purple-600',
      supervisor: 'text-gray-600'
    };
    return colors[agent] || 'text-gray-600';
  };

  const getAgentName = (agent) => {
    const names = {
      alex: 'Alex',
      cfo: 'Marcus',
      admin: 'Sophia',
      supervisor: 'Supervisor'
    };
    return names[agent] || agent;
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="fixed right-0 top-0 h-full w-80 bg-white shadow-2xl z-50 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              היסטוריית שיחות
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <button
            onClick={() => {
              onNewConversation();
              onClose();
            }}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            שיחה חדשה
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="text-center text-gray-500 py-8">
              טוען שיחות...
            </div>
          ) : (conversations || []).length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>אין שיחות קודמות</p>
              <p className="text-sm mt-1">התחל שיחה חדשה!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {(conversations || []).map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => {
                    onSelectConversation(conv.id);
                    onClose();
                  }}
                  className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                    conv.id === currentConversationId
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {conv.title}
                      </p>
                      {conv.agent && (
                        <p className={`text-xs ${getAgentColor(conv.agent)} mt-1`}>
                          {getAgentName(conv.agent)}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={(e) => deleteConversation(conv.id, e)}
                      className="text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-3 h-3" />
                      {conv.message_count} הודעות
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(conv.updated_at)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ConversationHistorySidebar;
