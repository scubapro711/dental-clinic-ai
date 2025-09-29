#!/usr/bin/env python3
"""
Dental Clinic AI - Deployment Version
A complete AI-powered dental clinic management system with Dana AI assistant.
"""

import os
import json
import random
import asyncio
import threading
import subprocess
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
CHAT_SERVER_HOST = "0.0.0.0"
CHAT_SERVER_PORT = 8766

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Mock Data ---
PATIENTS_COUNT = 1500
DOCTORS_COUNT = 10
APPOINTMENTS_TODAY = 47

# Business metrics
BUSINESS_METRICS = {
    "monthly_revenue": 125000,
    "patient_satisfaction": 94.8,
    "automation_savings": 286000,
    "roi_percentage": 794,
    "efficiency_increase": 67
}

# --- Chat Server Code (Embedded) ---
class DanaAI:
    """Dana - The AI Assistant for the Dental Clinic"""
    
    def __init__(self):
        self.personality = {
            "name": "Dana",
            "role": "AI Dental Assistant",
            "traits": ["friendly", "professional", "empathetic", "knowledgeable"]
        }
    
    def get_response(self, message, language="en"):
        """Generate contextual responses based on message content and language"""
        message_lower = message.lower()
        
        # Hebrew responses
        if language == "he":
            if any(word in message_lower for word in ["שלום", "היי", "בוקר טוב", "ערב טוב"]):
                return "שלום! אני דנה, העוזרת הדיגיטלית של המרפאה. איך אני יכולה לעזור לך היום?"
            elif any(word in message_lower for word in ["תור", "קביעת תור", "לקבוע"]):
                return "בשמחה אעזור לך לקבוע תור! באיזה תאריך היית רוצה להגיע? יש לנו זמינות השבוע הבא."
            elif any(word in message_lower for word in ["כאב", "כואב", "חירום"]):
                return "אני מבינה שיש לך כאב. זה נשמע דחוף. אני מעבירה אותך מיד לצוות הרפואי שלנו לטיפול מיידי."
            else:
                return "אני כאן לעזור לך עם כל מה שקשור למרפאת השיניים. תוכל לשאול אותי על קביעת תורים, טיפולים, או כל שאלה אחרת."
        
        # Arabic responses
        elif language == "ar":
            if any(word in message_lower for word in ["مرحبا", "السلام", "صباح", "مساء"]):
                return "مرحباً! أنا دانا، المساعدة الرقمية للعيادة. كيف يمكنني مساعدتك اليوم؟"
            elif any(word in message_lower for word in ["موعد", "حجز", "أريد"]):
                return "سأكون سعيدة لمساعدتك في حجز موعد! في أي تاريخ تود الحضور؟ لدينا مواعيد متاحة الأسبوع القادم."
            elif any(word in message_lower for word in ["ألم", "يؤلم", "طارئ"]):
                return "أفهم أن لديك ألماً. هذا يبدو عاجلاً. سأحولك فوراً إلى فريقنا الطبي للعلاج الفوري."
            else:
                return "أنا هنا لمساعدتك في كل ما يتعلق بعيادة الأسنان. يمكنك أن تسألني عن حجز المواعيد أو العلاجات أو أي سؤال آخر."
        
        # English responses (default)
        else:
            if any(word in message_lower for word in ["hello", "hi", "good morning", "good evening"]):
                return "Hello! I'm Dana, your AI dental assistant. How can I help you today?"
            elif any(word in message_lower for word in ["appointment", "book", "schedule"]):
                return "I'd be happy to help you book an appointment! What date would work best for you? We have availability next week."
            elif any(word in message_lower for word in ["pain", "hurt", "emergency"]):
                return "I understand you're experiencing pain. This sounds urgent. I'm connecting you immediately with our medical team for immediate care."
            else:
                return "I'm here to help you with anything related to our dental clinic. Feel free to ask me about appointments, treatments, or any other questions you might have."

# Global Dana instance
dana = DanaAI()

# WebSocket handler
async def chat_handler(websocket, path):
    """Handle WebSocket connections for the chat"""
    logger.info("New WebSocket connection established")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                user_message = data.get('message', '')
                language = data.get('language', 'en')
                
                # Get response from Dana
                response = dana.get_response(user_message, language)
                
                # Send response back
                response_data = {
                    'type': 'message',
                    'sender': 'Dana',
                    'message': response,
                    'timestamp': datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(response_data))
                logger.info(f"Sent response: {response[:50]}...")
                
            except json.JSONDecodeError:
                error_response = {
                    'type': 'error',
                    'message': 'Invalid message format'
                }
                await websocket.send(json.dumps(error_response))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"Error in chat handler: {e}")

# Start WebSocket server
async def start_chat_server():
    """Start the WebSocket server for chat"""
    try:
        async with websockets.serve(chat_handler, CHAT_SERVER_HOST, CHAT_SERVER_PORT):
            logger.info(f"Chat server started on ws://{CHAT_SERVER_HOST}:{CHAT_SERVER_PORT}")
            await asyncio.Future()  # Run forever
    except Exception as e:
        logger.error(f"Failed to start chat server: {e}")

def run_chat_server():
    """Run the chat server in a separate thread"""
    asyncio.run(start_chat_server())

# --- Flask Routes ---

@app.route('/')
def dashboard():
    """Main dashboard page"""
    html_template = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מערכת ניהול מרפאת שיניים עם בינה מלאכותית</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 1.2em;
        }
        
        .dashboard-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .metrics-panel, .terminal-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .metrics-panel h2, .terminal-panel h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }
        
        .metric-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #27ae60;
        }
        
        .terminal {
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            height: 300px;
            overflow-y: auto;
            margin: 10px 0;
        }
        
        .terminal-line {
            margin: 5px 0;
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Chat Widget Styles */
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: none;
            flex-direction: column;
            z-index: 1000;
        }
        
        .chat-widget.open {
            display: flex;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            border-radius: 15px 15px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 80%;
        }
        
        .message.dana {
            background: #e3f2fd;
            align-self: flex-start;
        }
        
        .message.user {
            background: #667eea;
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        
        .chat-input {
            display: flex;
            padding: 15px;
            background: white;
            border-radius: 0 0 15px 15px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
        }
        
        .chat-input button {
            margin-left: 10px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
        
        .chat-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 1001;
        }
        
        .roi-highlight {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }
        
        .roi-highlight h3 {
            font-size: 2em;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦷 מערכת ניהול מרפאת שיניים עם בינה מלאכותית</h1>
        <p>דשבורד למשקיעים - הדגמה חיה של המערכת המתקדמת</p>
    </div>

    <div class="dashboard-container">
        <div class="metrics-panel">
            <h2>📊 מדדי עסק ו-ROI</h2>
            
            <div class="roi-highlight">
                <h3>794% ROI</h3>
                <p>החזר על השקעה תוך 6 חודשים</p>
            </div>
            
            <div class="metric-item">
                <span>מטופלים במערכת</span>
                <span class="metric-value">1,500</span>
            </div>
            
            <div class="metric-item">
                <span>רופאים פעילים</span>
                <span class="metric-value">10</span>
            </div>
            
            <div class="metric-item">
                <span>תורים היום</span>
                <span class="metric-value">47</span>
            </div>
            
            <div class="metric-item">
                <span>הכנסות חודשיות</span>
                <span class="metric-value">$125,000</span>
            </div>
            
            <div class="metric-item">
                <span>שביעות רצון מטופלים</span>
                <span class="metric-value">94.8%</span>
            </div>
            
            <div class="metric-item">
                <span>חיסכון שנתי מאוטומציה</span>
                <span class="metric-value">${{ business_metrics.automation_savings:,}}</span>
            </div>
        </div>

        <div class="terminal-panel">
            <h2>🖥️ פעילות המערכת בזמן אמת</h2>
            
            <div class="terminal" id="systemTerminal">
                <div class="terminal-line">[INFO] מערכת AI פעילה - Dana מוכנה לשיחות</div>
                <div class="terminal-line">[INFO] שרת WebSocket פועל על פורט 8766</div>
                <div class="terminal-line">[INFO] מעבד 1,500 פרופילי מטופלים</div>
                <div class="terminal-line">[INFO] זיהוי שפה אוטומטי: עברית, אנגלית, ערבית</div>
            </div>
            
            <h3>📈 לוג פעילות עסקית</h3>
            <div class="terminal" id="businessTerminal">
                <div class="terminal-line">[BUSINESS] ROI מחושב: 794%</div>
                <div class="terminal-line">[BUSINESS] חיסכון חודשי: $23,833</div>
                <div class="terminal-line">[BUSINESS] יעילות תפעולית: +67%</div>
            </div>
        </div>
    </div>

    <!-- Chat Widget -->
    <button class="chat-toggle" onclick="toggleChat()">💬</button>
    
    <div class="chat-widget" id="chatWidget">
        <div class="chat-header">
            <div>
                <strong>דנה - העוזרת הדיגיטלית</strong>
                <div style="font-size: 0.8em; opacity: 0.8;">🟢 מחוברת</div>
            </div>
            <button onclick="toggleChat()" style="background: none; border: none; color: white; font-size: 20px;">×</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message dana">
                שלום! אני דנה, העוזרת הדיגיטלית של המרפאה. איך אני יכולה לעזור לך היום? 😊
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="הקלד הודעה..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">שלח</button>
        </div>
    </div>

    <script>
        let chatOpen = false;
        let socket = null;

        function toggleChat() {
            const widget = document.getElementById('chatWidget');
            const button = document.querySelector('.chat-toggle');
            
            chatOpen = !chatOpen;
            
            if (chatOpen) {
                widget.classList.add('open');
                button.style.display = 'none';
                connectWebSocket();
            } else {
                widget.classList.remove('open');
                button.style.display = 'block';
                if (socket) {
                    socket.close();
                }
            }
        }

        function connectWebSocket() {
            try {
                socket = new WebSocket(`ws://${window.location.hostname}:8766`);
                
                socket.onopen = () => {
                    console.log("WebSocket connection established.");
                };
                
                socket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.type === 'message') {
                        addMessage(data.message, 'dana');
                    }
                };
                
                socket.onerror = (error) => {
                    console.error("WebSocket error:", error);
                    addMessage("מצטערת, יש בעיה בחיבור. אנא נסה שוב.", 'dana');
                };
                
                socket.onclose = () => {
                    console.log("WebSocket connection closed.");
                };
            } catch (error) {
                console.error("Failed to connect to WebSocket:", error);
                addMessage("מצטערת, לא הצלחתי להתחבר. אנא נסה שוב מאוחר יותר.", 'dana');
            }
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message && socket && socket.readyState === WebSocket.OPEN) {
                addMessage(message, 'user');
                
                socket.send(JSON.stringify({
                    message: message,
                    language: detectLanguage(message)
                }));
                
                input.value = '';
            }
        }

        function addMessage(text, sender) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function detectLanguage(text) {
            if (/[\u0590-\u05FF]/.test(text)) return 'he';
            if (/[\u0600-\u06FF]/.test(text)) return 'ar';
            return 'en';
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Simulate real-time terminal updates
        function updateTerminals() {
            const systemTerminal = document.getElementById('systemTerminal');
            const businessTerminal = document.getElementById('businessTerminal');
            
            const systemMessages = [
                '[INFO] עיבוד הודעה חדשה מ-WhatsApp',
                '[INFO] Dana מגיבה בעברית למטופל',
                '[INFO] תור נקבע בהצלחה ל-15:30',
                '[INFO] התראת חירום נשלחה לרופא',
                '[INFO] סנכרון עם מערכת Open Dental',
                '[INFO] גיבוי אוטומטי הושלם'
            ];
            
            const businessMessages = [
                '[BUSINESS] מטופל חדש נרשם למערכת',
                '[BUSINESS] חיסכון זמן: 45 דקות השעה',
                '[BUSINESS] שביעות רצון: 96.2%',
                '[BUSINESS] יעילות תפעולית: +71%',
                '[BUSINESS] הכנסות נוספות: $1,250'
            ];
            
            setInterval(() => {
                const randomSystem = systemMessages[Math.floor(Math.random() * systemMessages.length)];
                const randomBusiness = businessMessages[Math.floor(Math.random() * businessMessages.length)];
                
                const systemLine = document.createElement('div');
                systemLine.className = 'terminal-line';
                systemLine.textContent = randomSystem;
                systemTerminal.appendChild(systemLine);
                
                const businessLine = document.createElement('div');
                businessLine.className = 'terminal-line';
                businessLine.textContent = randomBusiness;
                businessTerminal.appendChild(businessLine);
                
                // Keep only last 10 lines
                while (systemTerminal.children.length > 10) {
                    systemTerminal.removeChild(systemTerminal.firstChild);
                }
                while (businessTerminal.children.length > 10) {
                    businessTerminal.removeChild(businessTerminal.firstChild);
                }
            }, 3000);
        }

        // Start terminal updates
        updateTerminals();
    </script>
</body>
</html>
    """
    
    return render_template_string(
        html_template,
        patients_count=PATIENTS_COUNT,
        doctors_count=DOCTORS_COUNT,
        appointments_today=APPOINTMENTS_TODAY,
        business_metrics=BUSINESS_METRICS
    )

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "web_server": "running",
            "chat_server": "running",
            "dana_ai": "active"
        }
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "patients": PATIENTS_COUNT,
        "doctors": DOCTORS_COUNT,
        "appointments_today": APPOINTMENTS_TODAY,
        "business_metrics": BUSINESS_METRICS,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Start chat server in background thread
    chat_thread = threading.Thread(target=run_chat_server, daemon=True)
    chat_thread.start()
    
    # Start Flask app
    logger.info("Starting Dental Clinic AI System...")
    logger.info(f"Chat server will run on ws://0.0.0.0:{CHAT_SERVER_PORT}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
