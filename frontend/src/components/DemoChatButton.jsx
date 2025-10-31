import React, { useState, useEffect } from 'react';
import Draggable from 'react-draggable';
import InteractiveDemoChat from './InteractiveDemoChat';
import './DemoChatButton.css';

const DemoChatButton = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [position, setPosition] = useState(() => {
    // Load saved position from localStorage
    const saved = localStorage.getItem('chatButtonPosition');
    return saved ? JSON.parse(saved) : { x: 0, y: 0 };
  });

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleDrag = (e, data) => {
    const newPosition = { x: data.x, y: data.y };
    setPosition(newPosition);
    // Save position to localStorage
    localStorage.setItem('chatButtonPosition', JSON.stringify(newPosition));
  };

  return (
    <>
      {!isChatOpen && (
        <Draggable
          position={position}
          onStop={handleDrag}
          bounds="parent"
          handle=".demo-chat-fab"
        >
          <button
            className="demo-chat-fab"
            onClick={toggleChat}
            aria-label="Try Interactive Demo (Draggable)"
            style={{
              cursor: 'grab',
              position: 'fixed'
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.cursor = 'grabbing';
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.cursor = 'grab';
            }}
          >
            <div className="demo-chat-fab-content">
              <span className="demo-chat-fab-icon">💬</span>
              <span className="demo-chat-fab-text">Try Demo</span>
            </div>
            <div className="demo-chat-fab-pulse"></div>
          </button>
        </Draggable>
      )}

      {isChatOpen && <InteractiveDemoChat onClose={toggleChat} />}
    </>
  );
};

export default DemoChatButton;

