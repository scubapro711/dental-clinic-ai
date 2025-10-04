/**
 * Conversation Monitor Widget - Live feed of active conversations
 * 
 * Features:
 * - Real-time conversation updates
 * - Status indicators (active, escalated, waiting)
 * - Click to view details
 * - Filter by status/channel
 * - Search conversations
 */

import { useEffect, useState } from 'react'
import { Widget } from '../Widget'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  MessageSquare,
  Search,
  AlertTriangle,
  Clock,
  CheckCircle,
  Send,
  Phone,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDashboardStore } from '@/stores/dashboardStore'
import { api } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

export function ConversationMonitorWidget() {
  const {
    conversations,
    setConversations,
    conversationFilters,
    setConversationFilters,
    openRightPanel,
  } = useDashboardStore()
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadConversations()
    
    // Setup WebSocket for real-time updates
    setupWebSocket()
    
    // Refresh every 30 seconds as backup
    const interval = setInterval(loadConversations, 30000)
    return () => {
      clearInterval(interval)
      // TODO: Close WebSocket connection
    }
  }, [])

  const setupWebSocket = () => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws/monitoring'
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('[ConversationWidget] WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        handleWebSocketMessage(message)
      } catch (err) {
        console.error('[ConversationWidget] Error parsing WebSocket message:', err)
      }
    }
    
    ws.onerror = (error) => {
      console.error('[ConversationWidget] WebSocket error:', error)
    }
    
    ws.onclose = () => {
      console.log('[ConversationWidget] WebSocket disconnected')
      // Reconnect after 5 seconds
      setTimeout(setupWebSocket, 5000)
    }
  }

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'conversation_new':
        // Add new conversation to the list
        setConversations((prev) => [message.conversation, ...prev])
        break
      
      case 'conversation_update':
        // Update existing conversation
        setConversations((prev) =>
          prev.map((conv) =>
            conv.conversation_id === message.conversation_id
              ? { ...conv, ...message.updates }
              : conv
          )
        )
        break
      
      case 'message_new':
        // Update conversation with new message
        setConversations((prev) =>
          prev.map((conv) =>
            conv.conversation_id === message.conversation_id
              ? {
                  ...conv,
                  last_message: message.message.content,
                  last_message_time: message.message.created_at,
                  message_count: (conv.message_count || 0) + 1,
                }
              : conv
          )
        )
        break
      
      case 'escalation':
        // Mark conversation as escalated
        setConversations((prev) =>
          prev.map((conv) =>
            conv.conversation_id === message.conversation_id
              ? {
                  ...conv,
                  escalation_level: message.escalation_level,
                  requires_handoff: true,
                }
              : conv
          )
        )
        break
      
      default:
        console.log('[ConversationWidget] Unknown message type:', message.type)
    }
  }

  const loadConversations = async () => {
    try {
      const data = await api.getActiveConversations()
      setConversations(data)
      setError(null)
    } catch (err) {
      console.error('Error loading conversations:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleConversationClick = (conversation) => {
    openRightPanel({
      type: 'conversation',
      data: conversation,
    })
  }

  const handleTakeOver = async (conversation, e) => {
    e.stopPropagation() // Prevent opening the conversation details
    
    try {
      await api.takeoverConversation(conversation.conversation_id)
      
      // Update local state
      setConversations((prev) =>
        prev.map((conv) =>
          conv.conversation_id === conversation.conversation_id
            ? { ...conv, escalation_level: 'HUMAN_HANDLING', requires_handoff: false }
            : conv
        )
      )
      
      // Show success message (you can add a toast notification here)
      console.log('Successfully took over conversation')
    } catch (err) {
      console.error('Error taking over conversation:', err)
      setError('Failed to take over conversation')
    }
  }

  const handleRequestHandoff = async (conversation, e) => {
    e.stopPropagation()
    
    try {
      await api.requestHandoff(conversation.conversation_id, 'Doctor review requested from dashboard')
      
      // Update local state
      setConversations((prev) =>
        prev.map((conv) =>
          conv.conversation_id === conversation.conversation_id
            ? { ...conv, requires_handoff: true, escalation_level: 'DOCTOR_REQUIRED' }
            : conv
        )
      )
      
      console.log('Handoff requested successfully')
    } catch (err) {
      console.error('Error requesting handoff:', err)
      setError('Failed to request handoff')
    }
  }

  const getStatusIcon = (conversation) => {
    if (conversation.escalation_level) {
      return <AlertTriangle className="h-4 w-4 text-red-500" />
    }
    if (conversation.status === 'active') {
      return <MessageSquare className="h-4 w-4 text-blue-500" />
    }
    if (conversation.status === 'waiting') {
      return <Clock className="h-4 w-4 text-yellow-500" />
    }
    return <CheckCircle className="h-4 w-4 text-green-500" />
  }

  const getStatusColor = (conversation) => {
    if (conversation.escalation_level) return 'border-red-500 bg-red-50'
    if (conversation.status === 'active') return 'border-blue-500 bg-blue-50'
    if (conversation.status === 'waiting') return 'border-yellow-500 bg-yellow-50'
    return 'border-gray-200'
  }

  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'telegram':
        return <Send className="h-3 w-3" />
      case 'whatsapp':
        return <Phone className="h-3 w-3" />
      default:
        return <MessageSquare className="h-3 w-3" />
    }
  }

  const filteredConversations = conversations.filter((conv) => {
    // Status filter
    if (conversationFilters.status !== 'all') {
      if (conversationFilters.status === 'escalated' && !conv.escalation_level) {
        return false
      }
      if (conversationFilters.status !== 'escalated' && conv.status !== conversationFilters.status) {
        return false
      }
    }

    // Channel filter
    if (conversationFilters.channel !== 'all' && conv.channel !== conversationFilters.channel) {
      return false
    }

    // Search filter
    if (conversationFilters.searchQuery) {
      const query = conversationFilters.searchQuery.toLowerCase()
      return (
        conv.patient_name?.toLowerCase().includes(query) ||
        conv.last_message?.toLowerCase().includes(query)
      )
    }

    return true
  })

  return (
    <Widget
      id="conversation-monitor"
      title="Active Conversations"
      icon={MessageSquare}
      loading={loading}
      error={error}
      empty={filteredConversations.length === 0}
      emptyMessage="No conversations found"
      onRefresh={loadConversations}
    >
      <div className="space-y-4">
        {/* Filters */}
        <div className="space-y-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search conversations..."
              value={conversationFilters.searchQuery}
              onChange={(e) =>
                setConversationFilters({ searchQuery: e.target.value })
              }
              className="pl-9"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <Select
              value={conversationFilters.status}
              onValueChange={(value) =>
                setConversationFilters({ status: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="escalated">Escalated</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={conversationFilters.channel}
              onValueChange={(value) =>
                setConversationFilters({ channel: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Channels</SelectItem>
                <SelectItem value="web">Web</SelectItem>
                <SelectItem value="telegram">Telegram</SelectItem>
                <SelectItem value="whatsapp">WhatsApp</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Conversation List */}
        <div className="space-y-2">
          {filteredConversations.map((conversation) => (
            <div
              key={conversation.id}
              onClick={() => handleConversationClick(conversation)}
              className={cn(
                'p-3 border rounded-lg cursor-pointer transition-all hover:shadow-md',
                getStatusColor(conversation)
              )}
            >
              <div className="flex items-start gap-3">
                {/* Avatar */}
                <Avatar className="h-10 w-10">
                  <AvatarFallback>
                    {conversation.patient_name?.charAt(0) || '?'}
                  </AvatarFallback>
                </Avatar>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <p className="font-medium text-sm truncate">
                      {conversation.patient_name || 'Unknown'}
                    </p>
                    <div className="flex items-center gap-2">
                      {getChannelIcon(conversation.channel)}
                      {getStatusIcon(conversation)}
                    </div>
                  </div>
                  
                  <p className="text-xs text-muted-foreground truncate mb-2">
                    {conversation.last_message || 'No messages yet'}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-xs">
                      {conversation.agent_name || 'alex'}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {conversation.last_message_time
                        ? formatDistanceToNow(new Date(conversation.last_message_time), {
                            addSuffix: true,
                          })
                        : 'Just now'}
                    </span>
                  </div>

                  {/* Action Buttons */}
                  {conversation.requires_handoff && (
                    <div className="mt-3 pt-3 border-t flex gap-2">
                      <Button
                        size="sm"
                        variant="default"
                        className="flex-1 h-8 text-xs"
                        onClick={(e) => handleTakeOver(conversation, e)}
                      >
                        👨‍⚕️ Take Over
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-8 text-xs"
                        onClick={(e) => handleConversationClick(conversation)}
                      >
                        View
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Widget>
  )
}
