import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './InteractiveDemoChat.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const InteractiveDemoChat = ({ onClose }) => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [suggestedActions, setSuggestedActions] = useState([]);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Create demo session on component mount
  useEffect(() => {
    createDemoSession();
  }, []);

  // Update time remaining every second
  useEffect(() => {
    if (timeRemaining === null) return;

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 0) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [timeRemaining]);

  const createDemoSession = async () => {
    try {
      setIsLoading(true);
      const response = await axios.post(`${API_BASE_URL}/api/v1/demo/session/create`);
      const { session_id, message, expires_at } = response.data;
      
      setSessionId(session_id);
      setMessages([
        {
          type: 'bot',
          content: message,
          timestamp: new Date().toISOString(),
        },
      ]);
      
      // Calculate time remaining
      const expiresAt = new Date(expires_at);
      const now = new Date();
      const remaining = Math.floor((expiresAt - now) / 1000);
      setTimeRemaining(remaining);
      
      setError(null);
    } catch (err) {
      console.error('Error creating demo session:', err);
      setError('Failed to start demo session. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (messageText = null) => {
    const text = messageText || inputMessage.trim();
    if (!text || !sessionId) return;

    // Add user message to chat
    const userMessage = {
      type: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setSuggestedActions([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/demo/chat`, {
        session_id: sessionId,
        message: text,
      });

      const { message, suggested_actions, time_remaining } = response.data;

      // Add bot response to chat
      const botMessage = {
        type: 'bot',
        content: message,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, botMessage]);

      // Update suggested actions and time remaining
      if (suggested_actions) {
        setSuggestedActions(suggested_actions);
      }
      if (time_remaining !== undefined) {
        setTimeRemaining(time_remaining);
      }

      setError(null);
    } catch (err) {
      console.error('Error sending message:', err);
      
      if (err.response?.status === 404 || err.response?.status === 410) {
        // Session expired
        setError('Your demo session has expired. Creating a new session...');
        setTimeout(() => createDemoSession(), 2000);
      } else {
        setError('Failed to send message. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestedAction = (action) => {
    sendMessage(action);
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="interactive-demo-chat">
      <div className="demo-chat-header">
        <div className="demo-chat-title">
          <div className="demo-badge">DEMO MODE</div>
          <h3>Try DentaFlow AI</h3>
          {timeRemaining !== null && (
            <div className={`time-remaining ${timeRemaining < 300 ? 'warning' : ''}`}>
              ⏰ {formatTime(timeRemaining)}
            </div>
          )}
        </div>
        <button className="close-button" onClick={onClose} aria-label="Close demo">
          ✕
        </button>
      </div>

      <div className="demo-chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <div className="message-avatar">
              {msg.type === 'bot' ? '🤖' : '👤'}
            </div>
            <div className="message-content">
              <div className="message-text">{msg.content}</div>
              <div className="message-timestamp">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {suggestedActions.length > 0 && (
        <div className="suggested-actions">
          <div className="suggested-actions-label">Try asking:</div>
          <div className="suggested-actions-buttons">
            {suggestedActions.map((action, index) => (
              <button
                key={index}
                className="suggested-action-button"
                onClick={() => handleSuggestedAction(action)}
                disabled={isLoading}
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="demo-chat-error">
          ⚠️ {error}
        </div>
      )}

      <div className="demo-chat-input">
        <textarea
          ref={inputRef}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Press Enter to send)"
          disabled={isLoading || !sessionId}
          rows="2"
        />
        <button
          onClick={() => sendMessage()}
          disabled={isLoading || !inputMessage.trim() || !sessionId}
          className="send-button"
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </div>

      <div className="demo-chat-footer">
        <p>
          This is an Interactive Demo with sample data. 
          <a href="/register" className="cta-link">Start Free Trial</a> to use with your clinic.
        </p>
      </div>
    </div>
  );
};

export default InteractiveDemoChat;

