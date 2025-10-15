import React, { useState, useEffect } from 'react';
import BaseWidget from '../widgets/BaseWidget';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Users, CheckCircle2, Clock, XCircle, User } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Telegram Users Widget
 * 
 * Display and manage Telegram users
 */
export default function TelegramUsersWidget() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTelegramUsers();
  }, []);

  const fetchTelegramUsers = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/telegram-admin/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Error fetching telegram users:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'LINKED':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'PENDING':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'NEW':
        return <User className="w-4 h-4 text-blue-500" />;
      default:
        return <XCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'LINKED': { label: 'מקושר', className: 'bg-green-500' },
      'PENDING': { label: 'ממתין', className: 'bg-yellow-500' },
      'NEW': { label: 'חדש', className: 'bg-blue-500' },
      'UNLINKED': { label: 'מנותק', className: 'bg-gray-500' }
    };
    
    const config = statusConfig[status] || statusConfig['UNLINKED'];
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getInitials = (user) => {
    if (user.first_name) {
      return user.first_name.charAt(0).toUpperCase();
    }
    if (user.username) {
      return user.username.charAt(0).toUpperCase();
    }
    return 'U';
  };

  const getDisplayName = (user) => {
    const parts = [];
    if (user.first_name) parts.push(user.first_name);
    if (user.last_name) parts.push(user.last_name);
    if (parts.length > 0) return parts.join(' ');
    if (user.username) return `@${user.username}`;
    return `User ${user.telegram_id}`;
  };

  return (
    <BaseWidget
      title="משתמשי Telegram"
      icon={<Users />}
      agent="alex"
      badge={`${users.filter(u => u.status === 'LINKED').length} מקושרים`}
      isLoading={isLoading}
    >
      <div className="space-y-3">
        {users.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>אין משתמשים עדיין</p>
            <p className="text-sm">משתמשים יופיעו כאן לאחר שיתחברו לבוט</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {users.map((user) => (
              <div
                key={user.id}
                className="p-3 border-2 rounded-lg hover:shadow-md transition-all duration-200 bg-white"
              >
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                      {getInitials(user)}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-semibold text-sm truncate">
                        {getDisplayName(user)}
                      </p>
                      {getStatusIcon(user.status)}
                    </div>
                    
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      {user.username && (
                        <span className="text-blue-600">@{user.username}</span>
                      )}
                      {user.phone && (
                        <span>📱 {user.phone}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end gap-1">
                    {getStatusBadge(user.status)}
                    {user.linked_at && (
                      <span className="text-xs text-gray-500">
                        {new Date(user.linked_at).toLocaleDateString('he-IL')}
                      </span>
                    )}
                  </div>
                </div>
                
                {user.status === 'LINKED' && user.odoo_patient_id && (
                  <div className="mt-2 pt-2 border-t text-xs text-gray-600">
                    <span className="flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-green-500" />
                      מקושר למטופל #{user.odoo_patient_id}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </BaseWidget>
  );
}

