import React, { useState } from 'react';
import { CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';

/**
 * Task Queue Component - תור משימות
 * 
 * Features:
 * - Display pending agent actions
 * - Approve/Reject actions
 * - Priority indicators
 * - Action history
 * 
 * Props:
 * - tasks: array of pending tasks
 */
export default function TaskQueue({ tasks = [] }) {
  const [expandedTask, setExpandedTask] = useState(null);
  
  const handleApprove = async (taskId) => {
    try {
      const response = await fetch(`/api/v1/agent-actions/${taskId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      
      if (response.ok) {
        alert('הפעולה אושרה בהצלחה');
        // Refresh tasks
        window.location.reload();
      }
    } catch (error) {
      console.error('Failed to approve task:', error);
      alert('שגיאה באישור הפעולה');
    }
  };
  
  const handleReject = async (taskId) => {
    const reason = prompt('סיבת דחייה:');
    if (!reason) return;
    
    try {
      const response = await fetch(`/api/v1/agent-actions/${taskId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        },
        body: JSON.stringify({ reason })
      });
      
      if (response.ok) {
        alert('הפעולה נדחתה');
        // Refresh tasks
        window.location.reload();
      }
    } catch (error) {
      console.error('Failed to reject task:', error);
      alert('שגיאה בדחיית הפעולה');
    }
  };
  
  // Priority colors
  const priorityColors = {
    high: 'bg-red-100 text-red-700 border-red-300',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    low: 'bg-green-100 text-green-700 border-green-300'
  };
  
  // Priority icons
  const priorityIcons = {
    high: <AlertTriangle className="w-4 h-4" />,
    medium: <Clock className="w-4 h-4" />,
    low: <CheckCircle className="w-4 h-4" />
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          תור משימות
        </h3>
        <p className="text-sm text-gray-500">
          {tasks.length} משימות ממתינות לאישור
        </p>
      </div>
      
      {/* Task List */}
      <div className="flex-1 overflow-y-auto p-4">
        {tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <CheckCircle className="w-12 h-12 mb-2" />
            <p>אין משימות ממתינות</p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                expanded={expandedTask === task.id}
                onToggleExpand={() => setExpandedTask(
                  expandedTask === task.id ? null : task.id
                )}
                onApprove={() => handleApprove(task.id)}
                onReject={() => handleReject(task.id)}
                priorityColors={priorityColors}
                priorityIcons={priorityIcons}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Task Card Component
 */
function TaskCard({
  task,
  expanded,
  onToggleExpand,
  onApprove,
  onReject,
  priorityColors,
  priorityIcons
}) {
  const {
    id,
    action_type,
    description,
    agent_name,
    priority = 'medium',
    timestamp,
    details
  } = task;
  
  // Action type labels in Hebrew
  const actionLabels = {
    create_appointment: 'יצירת תור',
    send_email: 'שליחת אימייל',
    update_patient: 'עדכון פרטי מטופל',
    cancel_appointment: 'ביטול תור',
    send_sms: 'שליחת SMS',
    other: 'פעולה אחרת'
  };
  
  return (
    <div
      className={`border rounded-lg overflow-hidden transition-all ${
        priorityColors[priority]
      }`}
    >
      {/* Card Header */}
      <div
        className="p-3 cursor-pointer hover:bg-opacity-80 transition-colors"
        onClick={onToggleExpand}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              {priorityIcons[priority]}
              <span className="font-medium">
                {actionLabels[action_type] || action_type}
              </span>
            </div>
            <p className="text-sm opacity-90">{description}</p>
            <div className="flex items-center gap-2 mt-2 text-xs opacity-75">
              <span>🤖 {agent_name}</span>
              <span>•</span>
              <span>{new Date(timestamp).toLocaleTimeString('he-IL')}</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Expanded Details */}
      {expanded && (
        <div className="p-3 bg-white border-t">
          {/* Details */}
          {details && (
            <div className="mb-3 p-2 bg-gray-50 rounded text-sm">
              <pre className="whitespace-pre-wrap text-xs">
                {JSON.stringify(details, null, 2)}
              </pre>
            </div>
          )}
          
          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onApprove();
              }}
              className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              אשר
            </button>
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                onReject();
              }}
              className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center justify-center gap-2"
            >
              <XCircle className="w-4 h-4" />
              דחה
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
