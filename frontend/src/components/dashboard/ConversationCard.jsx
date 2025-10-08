import React from 'react';
import { Clock, User, MessageCircle } from 'lucide-react';

/**
 * Conversation Card Component - כרטיס שיחה
 * 
 * Design (from PDF):
 * - Patient name and time
 * - Last message preview
 * - Status badge (פתוח | ממתין | נפתר)
 * - Trust level (אמון: גבוה | בינוני | נמוך)
 * - Selected state (blue background)
 * 
 * Props:
 * - conversation: object with patient_name, last_message, status, trust_level, timestamp
 * - selected: boolean
 * - onClick: function
 */
export default function ConversationCard({ conversation, selected, onClick }) {
  const {
    id,
    patient_name,
    last_message,
    status,
    trust_level,
    timestamp,
    unread_count = 0
  } = conversation;
  
  // Status badge colors
  const statusColors = {
    active: 'bg-green-100 text-green-700',
    pending: 'bg-yellow-100 text-yellow-700',
    resolved: 'bg-gray-100 text-gray-700',
    escalated: 'bg-red-100 text-red-700'
  };
  
  // Trust level colors
  const trustColors = {
    high: 'text-green-600',
    medium: 'text-yellow-600',
    low: 'text-red-600'
  };
  
  // Status labels in Hebrew
  const statusLabels = {
    active: 'פתוח',
    pending: 'ממתין',
    resolved: 'נפתר',
    escalated: 'דורש טיפול'
  };
  
  // Trust level labels in Hebrew
  const trustLabels = {
    high: 'גבוה',
    medium: 'בינוני',
    low: 'נמוך'
  };
  
  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'עכשיו';
    if (diffMins < 60) return `לפני ${diffMins} דקות`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `לפני ${diffHours} שעות`;
    
    return date.toLocaleDateString('he-IL', { day: '2-digit', month: '2-digit' });
  };
  
  return (
    <div
      onClick={onClick}
      className={`p-4 mb-2 rounded-lg border cursor-pointer transition-all ${
        selected
          ? 'bg-blue-50 border-blue-500 shadow-md'
          : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300'
      }`}
    >
      {/* Header - Name and Time */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
            {patient_name?.charAt(0) || '?'}
          </div>
          <div>
            <div className="font-medium text-gray-900">{patient_name || 'לא ידוע'}</div>
            <div className="text-xs text-gray-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatTime(timestamp)}
            </div>
          </div>
        </div>
        
        {unread_count > 0 && (
          <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
            {unread_count}
          </span>
        )}
      </div>
      
      {/* Last Message Preview */}
      <div className="text-sm text-gray-600 mb-3 line-clamp-2">
        <MessageCircle className="w-4 h-4 inline ml-1" />
        "{last_message || 'אין הודעות'}"
      </div>
      
      {/* Status and Trust Level */}
      <div className="flex items-center justify-between">
        <span className={`text-xs px-2 py-1 rounded ${statusColors[status] || statusColors.pending}`}>
          סטטוס: {statusLabels[status] || status}
        </span>
        
        <span className={`text-xs font-medium ${trustColors[trust_level] || trustColors.medium}`}>
          אמון: {trustLabels[trust_level] || trust_level}
        </span>
      </div>
    </div>
  );
}
