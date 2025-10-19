import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Search, User, Phone, Calendar, Clock, CheckCircle, AlertCircle,
  MessageCircle, Users, Key, BarChart3, Copy, QrCode, Plus, X, Link2, Unlink
} from 'lucide-react';

/**
 * Telegram Hub - Complete Telegram Management Interface
 * 
 * Features:
 * - Conversations: View and manage all Telegram conversations
 * - Users: Manage Telegram users and patient linkage
 * - Invite Codes: Generate and manage invite codes
 * - Analytics: View Telegram usage statistics
 */
const TelegramHub = () => {
  // Tab state
  const [activeTab, setActiveTab] = useState('conversations');
  
  // Conversations state
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Users state
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  
  // Invite codes state
  const [inviteCodes, setInviteCodes] = useState([]);
  const [newInviteForm, setNewInviteForm] = useState({
    max_uses: 1,
    expires_in_days: 7,
    notes: ''
  });
  
  // Analytics state
  const [analytics, setAnalytics] = useState({
    total_users: 0,
    active_conversations: 0,
    messages_today: 0,
    avg_response_time: 0
  });
  
  // Loading states
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  
  // Refs
  const messagesEndRef = useRef(null);

  // Fetch data on mount and tab change
  useEffect(() => {
    fetchData();
    
    // Set up polling for active tab
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [activeTab]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      if (activeTab === 'conversations') {
        const response = await fetch('/api/v1/telegram/conversations', { headers });
        const data = await response.json();
        setConversations(data.conversations || data || []);
      } else if (activeTab === 'users') {
        const response = await fetch('/api/v1/telegram/users', { headers });
        const data = await response.json();
        setUsers(data.users || data || []);
      } else if (activeTab === 'invites') {
        const response = await fetch('/api/v1/telegram/invite-codes', { headers });
        const data = await response.json();
        setInviteCodes(data.invite_codes || data || []);
      } else if (activeTab === 'analytics') {
        const response = await fetch('/api/v1/telegram/stats', { headers });
        const data = await response.json();
        setAnalytics(data || {});
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      const response = await fetch(`/api/v1/telegram/conversations/${conversationId}/messages`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
    fetchMessages(conversation.id);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedConversation) return;

    try {
      const response = await fetch('/api/v1/telegram/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          chat_id: selectedConversation.telegram_chat_id,
          message: messageInput
        })
      });

      if (response.ok) {
        setMessageInput('');
        fetchMessages(selectedConversation.id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleCreateInviteCode = async (e) => {
    e.preventDefault();
    setActionLoading(true);

    try {
      const response = await fetch('/api/v1/telegram/invite-codes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newInviteForm)
      });

      if (response.ok) {
        setNewInviteForm({ max_uses: 1, expires_in_days: 7, notes: '' });
        fetchData();
      }
    } catch (error) {
      console.error('Error creating invite code:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCopyInviteCode = (code) => {
    navigator.clipboard.writeText(code);
    // TODO: Show toast notification
  };

  const handleLinkUser = async (userId, patientId) => {
    setActionLoading(true);
    try {
      // TODO: Implement user linking API call
      console.log('Linking user', userId, 'to patient', patientId);
      fetchData();
    } catch (error) {
      console.error('Error linking user:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUnlinkUser = async (userId) => {
    setActionLoading(true);
    try {
      const response = await fetch(`/api/v1/telegram/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        fetchData();
      }
    } catch (error) {
      console.error('Error unlinking user:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.patient_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.telegram_username?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredUsers = users.filter(user =>
    user.telegram_username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.first_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.last_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'עכשיו';
    if (diffMins < 60) return `לפני ${diffMins} דקות`;
    if (diffMins < 1440) return `לפני ${Math.floor(diffMins / 60)} שעות`;
    return date.toLocaleDateString('he-IL');
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('he-IL');
  };

  // Tab navigation
  const tabs = [
    { id: 'conversations', label: 'שיחות', icon: MessageCircle },
    { id: 'users', label: 'משתמשים', icon: Users },
    { id: 'invites', label: 'קודי הזמנה', icon: Key },
    { id: 'analytics', label: 'סטטיסטיקה', icon: BarChart3 }
  ];

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">Telegram Hub</h1>
        <p className="text-sm text-gray-600 mt-1">ניהול שיחות Telegram ומשתמשים</p>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex gap-1 px-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'conversations' && (
          <ConversationsTab
            conversations={filteredConversations}
            selectedConversation={selectedConversation}
            messages={messages}
            messageInput={messageInput}
            searchQuery={searchQuery}
            loading={loading}
            onConversationSelect={handleConversationSelect}
            onSendMessage={handleSendMessage}
            onMessageInputChange={setMessageInput}
            onSearchChange={setSearchQuery}
            formatTime={formatTime}
            messagesEndRef={messagesEndRef}
          />
        )}

        {activeTab === 'users' && (
          <UsersTab
            users={filteredUsers}
            searchQuery={searchQuery}
            loading={loading}
            actionLoading={actionLoading}
            onSearchChange={setSearchQuery}
            onLinkUser={handleLinkUser}
            onUnlinkUser={handleUnlinkUser}
            formatTime={formatTime}
          />
        )}

        {activeTab === 'invites' && (
          <InviteCodesTab
            inviteCodes={inviteCodes}
            newInviteForm={newInviteForm}
            loading={loading}
            actionLoading={actionLoading}
            onFormChange={setNewInviteForm}
            onCreateInvite={handleCreateInviteCode}
            onCopyCode={handleCopyInviteCode}
            formatDate={formatDate}
          />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsTab
            analytics={analytics}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
};

// Conversations Tab Component
const ConversationsTab = ({
  conversations,
  selectedConversation,
  messages,
  messageInput,
  searchQuery,
  loading,
  onConversationSelect,
  onSendMessage,
  onMessageInputChange,
  onSearchChange,
  formatTime,
  messagesEndRef
}) => (
  <div className="flex h-full">
    {/* Conversations List */}
    <div className="w-96 bg-white border-r border-gray-200 flex flex-col">
      {/* Search */}
      <div className="p-4 border-b border-gray-200">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="חפש שיחה..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <MessageCircle size={48} className="mb-2" />
            <p>אין שיחות</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => onConversationSelect(conv)}
              className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                selectedConversation?.id === conv.id ? 'bg-blue-50' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">
                      {conv.patient_name || conv.telegram_username || 'אורח'}
                    </h3>
                    {conv.status === 'linked' && (
                      <CheckCircle size={16} className="text-green-500" />
                    )}
                    {conv.status === 'pending' && (
                      <AlertCircle size={16} className="text-yellow-500" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1 truncate">
                    {conv.last_message || 'אין הודעות'}
                  </p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock size={12} />
                      {formatTime(conv.last_message_time)}
                    </span>
                    {conv.phone && (
                      <span className="flex items-center gap-1">
                        <Phone size={12} />
                        {conv.phone}
                      </span>
                    )}
                  </div>
                </div>
                {conv.unread_count > 0 && (
                  <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-1 min-w-[24px] text-center">
                    {conv.unread_count}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>

    {/* Chat Area */}
    <div className="flex-1 flex flex-col bg-gray-50">
      {selectedConversation ? (
        <>
          {/* Chat Header */}
          <div className="bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {selectedConversation.patient_name || selectedConversation.telegram_username || 'אורח'}
                </h2>
                <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                  {selectedConversation.phone && (
                    <span className="flex items-center gap-1">
                      <Phone size={14} />
                      {selectedConversation.phone}
                    </span>
                  )}
                  {selectedConversation.telegram_username && (
                    <span>@{selectedConversation.telegram_username}</span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  selectedConversation.status === 'linked'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {selectedConversation.status === 'linked' ? 'מקושר' : 'ממתין'}
                </span>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>אין הודעות בשיחה זו</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.from_patient ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg px-4 py-2 ${
                      msg.from_patient
                        ? 'bg-white text-gray-900 border border-gray-200'
                        : 'bg-blue-600 text-white'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                    <p className={`text-xs mt-1 ${
                      msg.from_patient ? 'text-gray-500' : 'text-blue-100'
                    }`}>
                      {formatTime(msg.timestamp)}
                    </p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="bg-white border-t border-gray-200 p-4">
            <form onSubmit={onSendMessage} className="flex gap-2">
              <input
                type="text"
                value={messageInput}
                onChange={(e) => onMessageInputChange(e.target.value)}
                placeholder="כתוב הודעה..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                disabled={!messageInput.trim()}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <Send size={20} />
                שלח
              </button>
            </form>
          </div>
        </>
      ) : (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <MessageCircle size={64} className="mx-auto mb-4 text-gray-400" />
            <p className="text-lg">בחר שיחה כדי להתחיל</p>
          </div>
        </div>
      )}
    </div>
  </div>
);

// Users Tab Component
const UsersTab = ({
  users,
  searchQuery,
  loading,
  actionLoading,
  onSearchChange,
  onLinkUser,
  onUnlinkUser,
  formatTime
}) => (
  <div className="h-full bg-white">
    {/* Search */}
    <div className="p-6 border-b border-gray-200">
      <div className="relative max-w-md">
        <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="חפש משתמש..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pr-10 pl-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
    </div>

    {/* Users List */}
    <div className="p-6">
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : users.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <Users size={48} className="mb-2" />
          <p>אין משתמשים</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {users.map((user) => (
            <div
              key={user.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">
                      {user.first_name} {user.last_name}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      user.status === 'linked'
                        ? 'bg-green-100 text-green-800'
                        : user.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {user.status === 'linked' ? 'מקושר' : user.status === 'pending' ? 'ממתין' : 'לא פעיל'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    @{user.telegram_username || 'לא זמין'}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span>Telegram ID: {user.telegram_id}</span>
                    {user.patient_id && <span>Patient ID: {user.patient_id}</span>}
                    <span>הצטרף: {formatTime(user.created_at)}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {user.status === 'linked' ? (
                    <button
                      onClick={() => onUnlinkUser(user.id)}
                      disabled={actionLoading}
                      className="flex items-center gap-1 px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                    >
                      <Unlink size={16} />
                      נתק
                    </button>
                  ) : (
                    <button
                      onClick={() => onLinkUser(user.id, null)}
                      disabled={actionLoading}
                      className="flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
                    >
                      <Link2 size={16} />
                      קשר
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);

// Invite Codes Tab Component
const InviteCodesTab = ({
  inviteCodes,
  newInviteForm,
  loading,
  actionLoading,
  onFormChange,
  onCreateInvite,
  onCopyCode,
  formatDate
}) => (
  <div className="h-full bg-white overflow-y-auto">
    {/* Create New Invite Code */}
    <div className="p-6 border-b border-gray-200">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">צור קוד הזמנה חדש</h2>
      <form onSubmit={onCreateInvite} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              מספר שימושים מקסימלי
            </label>
            <input
              type="number"
              min="1"
              value={newInviteForm.max_uses}
              onChange={(e) => onFormChange({ ...newInviteForm, max_uses: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              תוקף (ימים)
            </label>
            <input
              type="number"
              min="1"
              value={newInviteForm.expires_in_days}
              onChange={(e) => onFormChange({ ...newInviteForm, expires_in_days: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            הערות (אופציונלי)
          </label>
          <input
            type="text"
            value={newInviteForm.notes}
            onChange={(e) => onFormChange({ ...newInviteForm, notes: e.target.value })}
            placeholder="למשל: קוד למטופלים חדשים"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <button
          type="submit"
          disabled={actionLoading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Plus size={20} />
          צור קוד הזמנה
        </button>
      </form>
    </div>

    {/* Invite Codes List */}
    <div className="p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">קודי הזמנה קיימים</h2>
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : inviteCodes.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <Key size={48} className="mb-2" />
          <p>אין קודי הזמנה</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {inviteCodes.map((invite) => (
            <div
              key={invite.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <code className="px-3 py-1 bg-gray-100 text-gray-900 rounded font-mono text-sm">
                      {invite.code}
                    </code>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      invite.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : invite.status === 'used'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {invite.status === 'active' ? 'פעיל' : invite.status === 'used' ? 'בשימוש' : 'פג תוקף'}
                    </span>
                  </div>
                  {invite.notes && (
                    <p className="text-sm text-gray-600 mb-2">{invite.notes}</p>
                  )}
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>שימושים: {invite.current_uses}/{invite.max_uses}</span>
                    <span>תוקף עד: {formatDate(invite.expires_at)}</span>
                    <span>נוצר: {formatDate(invite.created_at)}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => onCopyCode(invite.code)}
                    className="flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Copy size={16} />
                    העתק
                  </button>
                  <button
                    className="flex items-center gap-1 px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <QrCode size={16} />
                    QR
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);

// Analytics Tab Component
const AnalyticsTab = ({ analytics, loading }) => (
  <div className="h-full bg-white overflow-y-auto">
    <div className="p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">סטטיסטיקת Telegram</h2>
      
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Users */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <Users className="text-blue-600" size={24} />
              <span className="text-xs text-blue-600 font-medium">סה"כ משתמשים</span>
            </div>
            <p className="text-3xl font-bold text-blue-900">{analytics.total_users || 0}</p>
          </div>

          {/* Active Conversations */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
            <div className="flex items-center justify-between mb-2">
              <MessageCircle className="text-green-600" size={24} />
              <span className="text-xs text-green-600 font-medium">שיחות פעילות</span>
            </div>
            <p className="text-3xl font-bold text-green-900">{analytics.active_conversations || 0}</p>
          </div>

          {/* Messages Today */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
            <div className="flex items-center justify-between mb-2">
              <Send className="text-purple-600" size={24} />
              <span className="text-xs text-purple-600 font-medium">הודעות היום</span>
            </div>
            <p className="text-3xl font-bold text-purple-900">{analytics.messages_today || 0}</p>
          </div>

          {/* Avg Response Time */}
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 border border-orange-200">
            <div className="flex items-center justify-between mb-2">
              <Clock className="text-orange-600" size={24} />
              <span className="text-xs text-orange-600 font-medium">זמן תגובה ממוצע</span>
            </div>
            <p className="text-3xl font-bold text-orange-900">
              {analytics.avg_response_time ? `${Math.round(analytics.avg_response_time)}s` : 'N/A'}
            </p>
          </div>
        </div>
      )}

      {/* Additional Stats */}
      <div className="mt-8">
        <h3 className="text-md font-semibold text-gray-900 mb-4">סטטיסטיקות נוספות</h3>
        <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">משתמשים מקושרים:</span>
              <span className="font-semibold text-gray-900 mr-2">{analytics.linked_users || 0}</span>
            </div>
            <div>
              <span className="text-gray-600">משתמשים ממתינים:</span>
              <span className="font-semibold text-gray-900 mr-2">{analytics.pending_users || 0}</span>
            </div>
            <div>
              <span className="text-gray-600">הודעות השבוע:</span>
              <span className="font-semibold text-gray-900 mr-2">{analytics.messages_week || 0}</span>
            </div>
            <div>
              <span className="text-gray-600">הודעות החודש:</span>
              <span className="font-semibold text-gray-900 mr-2">{analytics.messages_month || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default TelegramHub;

