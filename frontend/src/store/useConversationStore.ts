/**
 * Conversation Store
 * 
 * Manages:
 * - Active conversations
 * - Message history
 * - WebSocket connection
 * - Streaming responses
 */

import { create } from 'zustand';
import { api } from '../api/client';
import { agentWebSocket } from '../api/websocket';

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: any;
  created_at: string;
}

export interface Conversation {
  id: string;
  organization_id: string;
  patient_phone?: string;
  patient_name?: string;
  channel: string;
  status: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

interface ConversationState {
  // State
  conversations: Conversation[];
  activeConversation: Conversation | null;
  isLoading: boolean;
  isSending: boolean;
  isStreaming: boolean;
  streamingMessage: string;
  error: string | null;

  // Actions
  fetchConversations: (organizationId: string) => Promise<void>;
  fetchConversation: (id: string) => Promise<void>;
  createConversation: (data: { patient_phone?: string; channel?: string }) => Promise<Conversation>;
  setActiveConversation: (conversation: Conversation | null) => void;
  sendMessage: (conversationId: string, message: string) => Promise<void>;
  connectWebSocket: (conversationId: string) => void;
  disconnectWebSocket: () => void;
  clearError: () => void;
}

export const useConversationStore = create<ConversationState>((set, get) => ({
  // Initial state
  conversations: [],
  activeConversation: null,
  isLoading: false,
  isSending: false,
  isStreaming: false,
  streamingMessage: '',
  error: null,

  // Fetch all conversations
  fetchConversations: async (organizationId: string) => {
    set({ isLoading: true, error: null });

    try {
      const response = await api.conversations.list({ organization_id: organizationId });
      set({
        conversations: response.data,
        isLoading: false,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch conversations';
      set({
        isLoading: false,
        error: errorMessage,
      });
    }
  },

  // Fetch single conversation
  fetchConversation: async (id: string) => {
    set({ isLoading: true, error: null });

    try {
      const response = await api.conversations.get(id);
      const conversation = response.data;

      // Update in list
      set((state) => ({
        conversations: state.conversations.map((c) =>
          c.id === id ? conversation : c
        ),
        activeConversation: conversation,
        isLoading: false,
      }));
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch conversation';
      set({
        isLoading: false,
        error: errorMessage,
      });
    }
  },

  // Create new conversation
  createConversation: async (data: { patient_phone?: string; channel?: string }) => {
    set({ isLoading: true, error: null });

    try {
      const response = await api.conversations.create(data);
      const conversation = response.data;

      set((state) => ({
        conversations: [conversation, ...state.conversations],
        activeConversation: conversation,
        isLoading: false,
      }));

      return conversation;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create conversation';
      set({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  // Set active conversation
  setActiveConversation: (conversation: Conversation | null) => {
    set({ activeConversation: conversation });

    // Connect WebSocket if conversation is set
    if (conversation) {
      get().connectWebSocket(conversation.id);
    } else {
      get().disconnectWebSocket();
    }
  },

  // Send message
  sendMessage: async (conversationId: string, message: string) => {
    set({ isSending: true, error: null });

    try {
      // Add user message optimistically
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        conversation_id: conversationId,
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        activeConversation: state.activeConversation
          ? {
              ...state.activeConversation,
              messages: [...state.activeConversation.messages, userMessage],
            }
          : null,
      }));

      // Send through WebSocket if connected
      if (agentWebSocket.isConnected()) {
        agentWebSocket.send(message);
      } else {
        // Fallback to HTTP
        await api.conversations.sendMessage(conversationId, message);
      }

      set({ isSending: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to send message';
      set({
        isSending: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  // Connect WebSocket
  connectWebSocket: (conversationId: string) => {
    agentWebSocket.connect(conversationId);

    // Handle incoming messages
    agentWebSocket.onMessage((data) => {
      const { type, data: messageData } = data;

      if (type === 'message') {
        // Complete message received
        set((state) => ({
          activeConversation: state.activeConversation
            ? {
                ...state.activeConversation,
                messages: [...state.activeConversation.messages, messageData],
              }
            : null,
          isStreaming: false,
          streamingMessage: '',
        }));
      } else if (type === 'stream') {
        // Streaming chunk received
        set((state) => ({
          isStreaming: true,
          streamingMessage: state.streamingMessage + messageData.content,
        }));
      } else if (type === 'agent_action') {
        // Agent action (e.g., tool call)
        console.log('[Agent Action]', messageData);
      } else if (type === 'error') {
        set({
          error: messageData.message,
          isStreaming: false,
        });
      }
    });

    // Handle errors
    agentWebSocket.onError((error) => {
      console.error('[WebSocket Error]', error);
      set({ error: 'WebSocket connection error' });
    });

    // Handle close
    agentWebSocket.onClose(() => {
      console.log('[WebSocket Closed]');
      set({ isStreaming: false });
    });
  },

  // Disconnect WebSocket
  disconnectWebSocket: () => {
    agentWebSocket.disconnect();
    set({ isStreaming: false, streamingMessage: '' });
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },
}));

export default useConversationStore;
