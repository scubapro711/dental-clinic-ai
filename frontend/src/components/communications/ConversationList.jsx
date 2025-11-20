import React, { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ConversationCard from './ConversationCard';

/**
 * ConversationList - Left sidebar with conversation list
 * 
 * Props:
 * - conversations: Array of conversations
 * - selectedConversation: Currently selected conversation
 * - onSelectConversation: Handler for selecting a conversation
 * - isLoading: Loading state
 */
export default function ConversationList({ 
  conversations, 
  selectedConversation, 
  onSelectConversation,
  isLoading 
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [channelFilter, setChannelFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  // Filter conversations
  const filteredConversations = conversations.filter(conv => {
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesName = conv.patient_name?.toLowerCase().includes(query);
      const matchesPhone = conv.patient_phone?.includes(query);
      if (!matchesName && !matchesPhone) return false;
    }

    // Channel filter
    if (channelFilter !== 'all' && conv.channel !== channelFilter) {
      return false;
    }

    // Status filter
    if (statusFilter !== 'all' && conv.status !== statusFilter) {
      return false;
    }

    return true;
  });

  // Sort by last_message_at (newest first)
  const sortedConversations = [...filteredConversations].sort((a, b) => {
    const dateA = a.last_message_at ? new Date(a.last_message_at) : new Date(0);
    const dateB = b.last_message_at ? new Date(b.last_message_at) : new Date(0);
    return dateB - dateA;
  });

  return (
    <div className="flex flex-col h-full bg-slate-50 border-l border-slate-200">
      {/* Header */}
      <div className="p-4 bg-white border-b border-slate-200">
        <h2 className="text-lg font-bold text-slate-900 mb-4">שיחות</h2>

        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="חפש לפי שם או טלפון..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pr-10 rounded-xl"
          />
        </div>

        {/* Channel Filter (Tabs) */}
        <Tabs value={channelFilter} onValueChange={setChannelFilter} className="mb-3">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all" className="text-xs">הכל</TabsTrigger>
            <TabsTrigger value="whatsapp" className="text-xs">WhatsApp</TabsTrigger>
            <TabsTrigger value="telegram" className="text-xs">Telegram</TabsTrigger>
            <TabsTrigger value="sms" className="text-xs">SMS</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Status Filter */}
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full rounded-xl">
            <SelectValue placeholder="סטטוס" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">כל הסטטוסים</SelectItem>
            <SelectItem value="active">פעיל</SelectItem>
            <SelectItem value="waiting">ממתין</SelectItem>
            <SelectItem value="escalated">הועבר לרופא</SelectItem>
            <SelectItem value="resolved">טופל</SelectItem>
            <SelectItem value="archived">ארכיון</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isLoading ? (
          // Loading skeleton
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-white rounded-2xl p-4 border border-slate-200">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-4 h-4 bg-slate-200 rounded-full" />
                    <div className="h-4 bg-slate-200 rounded w-1/2" />
                  </div>
                  <div className="h-3 bg-slate-200 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-slate-200 rounded w-1/4" />
                </div>
              </div>
            ))}
          </div>
        ) : sortedConversations.length === 0 ? (
          // Empty state
          <div className="text-center py-12">
            <Filter className="w-12 h-12 mx-auto mb-3 text-slate-400" />
            <p className="text-slate-600">לא נמצאו שיחות</p>
            <p className="text-sm text-slate-500">נסה לשנות את הפילטרים</p>
          </div>
        ) : (
          // Conversation cards
          sortedConversations.map((conversation) => (
            <ConversationCard
              key={conversation.id}
              conversation={conversation}
              isActive={selectedConversation?.id === conversation.id}
              onClick={() => onSelectConversation(conversation)}
            />
          ))
        )}
      </div>
    </div>
  );
}
