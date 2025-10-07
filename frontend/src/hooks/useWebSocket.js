/**
 * WebSocket Hook - Real-time communication with backend
 * 
 * Handles:
 * - Connection management
 * - Event listening
 * - Automatic reconnection
 * - Event dispatching to dashboard store
 */

import { useEffect, useRef, useCallback } from 'react'
import { io } from 'socket.io-client'
import { useDashboardStore } from '../stores/dashboardStore'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useWebSocket() {
  const socketRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  
  const {
    setWsConnected,
    addConversation,
    updateConversation,
    addAlert,
    setMetrics,
    setAgentStatus,
  } = useDashboardStore()

  // Handle incoming events
  const handleEvent = useCallback((eventType, data) => {
    console.log('[WebSocket] Event received:', eventType, data)

    switch (eventType) {
      case 'conversation_new':
        addConversation(data.conversation)
        break

      case 'conversation_update':
        updateConversation(data.conversation_id, data.updates)
        break

      case 'message_new':
        // Update conversation with new message
        updateConversation(data.conversation_id, {
          last_message: data.message.content,
          updated_at: data.message.created_at,
        })
        break

      case 'escalation':
        // Add alert for escalation
        addAlert({
          type: 'escalation',
          severity: data.escalation_level === 'EMERGENCY' ? 'critical' : 'warning',
          title: `Escalation: ${data.escalation_level}`,
          message: `Conversation ${data.conversation_id} requires attention`,
          conversationId: data.conversation_id,
          timestamp: Date.now(),
        })
        // Update conversation status
        updateConversation(data.conversation_id, {
          escalation_level: data.escalation_level,
          requires_human: true,
        })
        break

      case 'agent_status':
        setAgentStatus(data.status)
        break

      case 'metrics_update':
        setMetrics(data.metrics)
        break

      case 'error':
        addAlert({
          type: 'error',
          severity: 'error',
          title: 'System Error',
          message: data.message,
          timestamp: Date.now(),
        })
        break

      default:
        console.warn('[WebSocket] Unknown event type:', eventType)
    }
  }, [addConversation, updateConversation, addAlert, setMetrics, setAgentStatus])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (socketRef.current?.connected) {
      console.log('[WebSocket] Already connected')
      return
    }

    console.log('[WebSocket] Connecting to:', WS_URL)

    const socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: Infinity,
    })

    socket.on('connect', () => {
      console.log('[WebSocket] Connected')
      setWsConnected(true)
      
      // Subscribe to monitoring events
      socket.emit('subscribe', { channel: 'monitoring' })
    })

    socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason)
      setWsConnected(false)
    })

    socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error)
      setWsConnected(false)
    })

    // Listen to all events
    socket.onAny((eventType, data) => {
      handleEvent(eventType, data)
    })

    socketRef.current = socket
  }, [setWsConnected, handleEvent])

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      console.log('[WebSocket] Disconnecting')
      socketRef.current.disconnect()
      socketRef.current = null
      setWsConnected(false)
    }
  }, [setWsConnected])

  // Send event to server
  const emit = useCallback((eventType, data) => {
    if (socketRef.current?.connected) {
      console.log('[WebSocket] Emitting event:', eventType, data)
      socketRef.current.emit(eventType, data)
    } else {
      console.warn('[WebSocket] Cannot emit - not connected')
    }
  }, [])

  // Auto-connect on mount
  useEffect(() => {
    connect()

    return () => {
      disconnect()
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [connect, disconnect])

  return {
    connected: socketRef.current?.connected || false,
    emit,
    connect,
    disconnect,
  }
}

/**
 * Hook for monitoring a specific conversation
 */
export function useConversationWebSocket(conversationId) {
  const { emit } = useWebSocket()

  useEffect(() => {
    if (conversationId) {
      // Subscribe to conversation-specific events
      emit('subscribe_conversation', { conversation_id: conversationId })

      return () => {
        emit('unsubscribe_conversation', { conversation_id: conversationId })
      }
    }
  }, [conversationId, emit])
}
