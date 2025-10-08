import React, { useState } from 'react';
import { Search, MessageSquare, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import ConversationCard from './ConversationCard';
import ConversationDetail from './ConversationDetail';

/**
 * Conversation Monitor Component - ניטור שיחות
 * 
 * Layout (from PDF):
 * - Left (30%): Conversation list with search
 * - Right (70%): Selected conversation detail
 * 
 * Features:
 * - Search conversations
 * - Filter by status
 * - Real-time updates
 * - Conversation cards with status indicators
 */
export default function ConversationMonitor({
  conversations = [],
  selectedConversation,
  onSelectConversation
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'active' | 'pending' | 'resolved'
  
  // Filter conversations based on search and status
  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = 
      conv.patient_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.last_message?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = 
      statusFilter === 'all' || conv.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });
  
  // Status counts for filters
  const statusCounts = {
    all: conversations.length,
    active: conversations.filter(c => c.status === 'active').length,
    pending: conversations.filter(c => c.status === 'pending').length,
    resolved: conversations.filter(c => c.status === 'resolved').length
  };
  
  return (
    <div className="flex h-full">
      {/* Left Side - Conversation List (30%) */}
      <div className="w-[30%] border-l border-gray-200 flex flex-col">
        {/* Search Bar */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <input
              type="text"
              placeholder="🔍 חיפוש שיחות..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 pr-10 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
          </div>
        </div>
        
        {/* Status Filters */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex gap-2">
            <FilterButton
              label="הכל"
              count={statusCounts.all}
              active={statusFilter === 'all'}
              onClick={() => setStatusFilter('all')}
            />
            <FilterButton
              label="פעיל"
              count={statusCounts.active}
              active={statusFilter === 'active'}
              onClick={() => setStatusFilter('active')}
              color="green"
            />
            <FilterButton
              label="ממתין"
              count={statusCounts.pending}
              active={statusFilter === 'pending'}
              onClick={() => setStatusFilter('pending')}
              color="yellow"
            />
            <FilterButton
              label="נפתר"
              count={statusCounts.resolved}
              active={statusFilter === 'resolved'}
              onClick={() => setStatusFilter('resolved')}
              color="gray"
            />
          </div>
        </div>
        
        {/* Conversation List - Scrollable */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <MessageSquare className="w-12 h-12 mb-2" />
              <p>אין שיחות</p>
            </div>
          ) : (
            <div className="p-2">
              {filteredConversations.map((conv) => (
                <ConversationCard
                  key={conv.id}
                  conversation={conv}
                  selected={selectedConversation?.id === conv.id}
                  onClick={() => onSelectConversation(conv)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Right Side - Conversation Detail (70%) */}
      <div className="flex-1">
        {selectedConversation ? (
          <ConversationDetail conversation={selectedConversation} />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <MessageSquare className="w-16 h-16 mb-4" />
            <p className="text-lg">בחר שיחה כדי להציג פרטים</p>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Filter Button Component
 */
function FilterButton({ label, count, active, onClick, color = 'blue' }) {
  const colorClasses = {
    blue: active ? 'bg-blue-500 text-white' : 'bg-blue-50 text-blue-600 hover:bg-blue-100',
    green: active ? 'bg-green-500 text-white' : 'bg-green-50 text-green-600 hover:bg-green-100',
    yellow: active ? 'bg-yellow-500 text-white' : 'bg-yellow-50 text-yellow-600 hover:bg-yellow-100',
    gray: active ? 'bg-gray-500 text-white' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
  };
  
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${colorClasses[color]}`}
    >
      {label} ({count})
    </button>
  );
}
