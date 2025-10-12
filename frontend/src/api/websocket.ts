/**
 * WebSocket Client for Real-time Agent Communication
 * 
 * Handles:
 * - WebSocket connection management
 * - Message streaming
 * - Reconnection logic
 * - Event handling
 */

type MessageHandler = (data: any) => void;
type ErrorHandler = (error: Event) => void;
type CloseHandler = () => void;

interface WebSocketMessage {
  type: 'message' | 'status' | 'error' | 'agent_action' | 'tool_call';
  data: any;
  timestamp: string;
}

class AgentWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000; // Start with 1 second
  private messageHandlers: Set<MessageHandler> = new Set();
  private errorHandlers: Set<ErrorHandler> = new Set();
  private closeHandlers: Set<CloseHandler> = new Set();
  private isIntentionallyClosed: boolean = false;

  constructor() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`;
    this.url = `${host}/ws`;
  }

  /**
   * Connect to WebSocket
   */
  connect(conversationId: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.warn('[WS] Already connected');
      return;
    }

    this.isIntentionallyClosed = false;
    const token = localStorage.getItem('access_token');
    const wsUrl = `${this.url}/conversations/${conversationId}?token=${token}`;

    console.log('[WS] Connecting to:', wsUrl);

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[WS] Connected');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('[WS] Message received:', message);

          // Notify all handlers
          this.messageHandlers.forEach((handler) => {
            try {
              handler(message);
            } catch (error) {
              console.error('[WS] Handler error:', error);
            }
          });
        } catch (error) {
          console.error('[WS] Failed to parse message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[WS] Error:', error);
        this.errorHandlers.forEach((handler) => handler(error));
      };

      this.ws.onclose = () => {
        console.log('[WS] Closed');
        this.closeHandlers.forEach((handler) => handler());

        // Attempt to reconnect if not intentionally closed
        if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
          console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          
          setTimeout(() => {
            this.connect(conversationId);
          }, delay);
        } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.error('[WS] Max reconnect attempts reached');
        }
      };
    } catch (error) {
      console.error('[WS] Connection error:', error);
    }
  }

  /**
   * Send message through WebSocket
   */
  send(message: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[WS] Not connected');
      throw new Error('WebSocket is not connected');
    }

    const payload = {
      type: 'message',
      message,
      timestamp: new Date().toISOString(),
    };

    console.log('[WS] Sending:', payload);
    this.ws.send(JSON.stringify(payload));
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    if (this.ws) {
      this.isIntentionallyClosed = true;
      this.ws.close();
      this.ws = null;
      console.log('[WS] Disconnected');
    }
  }

  /**
   * Add message handler
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  /**
   * Add error handler
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);
    
    return () => {
      this.errorHandlers.delete(handler);
    };
  }

  /**
   * Add close handler
   */
  onClose(handler: CloseHandler): () => void {
    this.closeHandlers.add(handler);
    
    return () => {
      this.closeHandlers.delete(handler);
    };
  }

  /**
   * Get connection state
   */
  getState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const agentWebSocket = new AgentWebSocket();

export default agentWebSocket;
