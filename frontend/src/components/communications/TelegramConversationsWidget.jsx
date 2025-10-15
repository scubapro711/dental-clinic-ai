import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { MessageSquare, ExternalLink, Clock, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Telegram Conversations Widget
 * 
 * Display active Telegram conversations
 */
export default function TelegramConversationsWidget() {
  const [conversations, setConversations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/telegram-admin/conversations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getInitials = (conv) => {
    if (conv.telegram_user?.first_name) {
      return conv.telegram_user.first_name.charAt(0).toUpperCase();
    }
    return 'U';
  };

  const getDisplayName = (conv) => {
    const user = conv.telegram_user;
    if (!user) return 'Unknown User';
    
    const parts = [];
    if (user.first_name) parts.push(user.first_name);
    if (user.last_name) parts.push(user.last_name);
    if (parts.length > 0) return parts.join(' ');
    if (user.username) return `@${user.username}`;
    return `User ${user.telegram_id}`;
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'עכשיו';
    if (diffMins < 60) return `לפני ${diffMins} דקות`;
    if (diffMins < 1440) return `לפני ${Math.floor(diffMins / 60)} שעות`;
    return date.toLocaleDateString('he-IL');
  };

  return (
    <Card className="border-2 border-purple-200 bg-purple-50/30">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-purple-600" />
            שיחות פעילות
          </CardTitle>
          <Badge variant="secondary" className="bg-purple-100 text-purple-700">
            {conversations.filter(c => c.is_active).length} פעילות
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        ) : conversations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>אין שיחות פעילות</p>
            <p className="text-sm">שיחות יופיעו כאן כשמטופלים ישלחו הודעות</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={cn(
                  "p-4 border-2 rounded-lg hover:shadow-md transition-all duration-200 bg-white",
                  conv.is_active ? "border-purple-300" : "border-gray-200 opacity-60"
                )}
              >
                <div className="flex items-start gap-3 mb-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-gradient-to-br from-purple-500 to-pink-600 text-white">
                      {getInitials(conv)}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm truncate">
                      {getDisplayName(conv)}
                    </p>
                    <div className="flex items-center gap-1 text-xs text-gray-600 mt-1">
                      <Clock className="w-3 h-3" />
                      <span>{formatTimestamp(conv.updated_at)}</span>
                    </div>
                  </div>
                  
                  {conv.is_active && (
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  )}
                </div>
                
                <div className="space-y-2">
                  {conv.telegram_user?.status === 'LINKED' && (
                    <div className="flex items-center gap-1 text-xs text-green-600">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>מקושר למטופל</span>
                    </div>
                  )}
                  
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full text-xs"
                    onClick={() => {
                      // TODO: Open conversation in chat interface
                      console.log('Open conversation:', conv.id);
                    }}
                  >
                    <ExternalLink className="w-3 h-3 mr-2" />
                    פתח שיחה
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

