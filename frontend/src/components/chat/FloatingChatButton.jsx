import React, { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import AIChat from './AIChat';

/**
 * FloatingChatButton Component
 * 
 * A floating action button (FAB) that opens a slide-in chat panel.
 * Follows Material Design 3 FAB guidelines and healthcare UX best practices.
 * 
 * @component
 * @param {Object} props
 * @param {string} props.conversationId - Current conversation ID
 * @param {Array} props.initialMessages - Initial messages for the chat
 * @param {Function} props.onStreamEvent - Handler for stream events
 * @param {Function} props.onClearChat - Handler for clearing chat
 * @param {Object} props.chatInputRef - Ref for chat input
 */
const FloatingChatButton = ({
  conversationId,
  initialMessages = [],
  onStreamEvent,
  onClearChat,
  chatInputRef
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={toggleChat}
        className="floating-chat-button"
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
        aria-expanded={isOpen}
        title="Chat with AI Assistant"
      >
        {isOpen ? (
          <X className="floating-chat-icon" />
        ) : (
          <MessageCircle className="floating-chat-icon" />
        )}
      </button>

      {/* Chat Panel Overlay */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="floating-chat-backdrop"
            onClick={handleClose}
            aria-hidden="true"
          />
          
          {/* Chat Panel */}
          <div 
            className="floating-chat-panel"
            role="dialog"
            aria-label="AI Chat Assistant"
            aria-modal="true"
          >
            {/* Panel Header */}
            <div className="floating-chat-header">
              <div className="flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-indigo-600" />
                <h2 className="text-lg font-semibold text-gray-900">
                  AI Assistant
                </h2>
              </div>
              <button
                onClick={handleClose}
                className="floating-chat-close"
                aria-label="Close chat"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Chat Content */}
            <div className="floating-chat-content">
              <AIChat
                ref={chatInputRef}
                conversationId={conversationId}
                initialMessages={initialMessages}
                onStreamEvent={onStreamEvent}
                onClearChat={onClearChat}
              />
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default FloatingChatButton;

