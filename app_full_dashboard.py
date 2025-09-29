#!/usr/bin/env python3
"""
Dental Clinic AI - Full Dashboard Version
Complete system with investor dashboard, technical monitoring, and Dana AI chat
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

# Business metrics for investors
BUSINESS_METRICS = {
    "monthly_revenue": 125000,
    "patient_satisfaction": 94.8,
    "automation_savings": 286000,
    "roi_percentage": 794,
    "efficiency_increase": 67,
    "cost_reduction": 45,
    "patient_retention": 92.3,
    "average_treatment_value": 850,
    "monthly_new_patients": 89,
    "staff_productivity": 78.5
}

# Technical metrics for experts
TECHNICAL_METRICS = {
    "system_uptime": 99.97,
    "response_time": 185,
    "concurrent_users": 1247,
    "messages_processed": 15847,
    "ai_accuracy": 96.2,
    "language_detection": 98.5,
    "database_performance": 94.1,
    "security_score": 99.8
}

# --- Dana AI Assistant ---
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
                return "שלום! אני דנה, העוזרת הדיגיטלית של המרפאה. איך אני יכולה לעזור לך היום? 😊"
            elif any(word in message_lower for word in ["תור", "קביעת תור", "לקבוע"]):
                return "בשמחה אעזור לך לקבוע תור! באיזה תאריך היית רוצה להגיע? יש לנו זמינות השבוע הבא ברביעי ובחמישי."
            elif any(word in message_lower for word in ["כאב", "כואב", "חירום"]):
                return "אני מבינה שיש לך כאב. זה נשמע דחוף! אני מעבירה אותך מיד לצוות הרפואי שלנו לטיפול מיידי. אנא המתן ברגע."
            elif any(word in message_lower for word in ["מחיר", "עלות", "כמה"]):
                return "המחירים שלנו תחרותיים מאוד. לטיפול בסיסי - 350₪, לטיפול שורש - 1,200₪. האם תרצה פירוט מלא של המחירים?"
            else:
                return "אני כאן לעזור לך עם כל מה שקשור למרפאת השיניים. תוכל לשאול אותי על קביעת תורים, טיפולים, מחירים, או כל שאלה אחרת."
        
        # Arabic responses
        elif language == "ar":
            if any(word in message_lower for word in ["مرحبا", "السلام", "صباح", "مساء"]):
                return "مرحباً! أنا دانا، المساعدة الرقمية للعيادة. كيف يمكنني مساعدتك اليوم؟ 😊"
            elif any(word in message_lower for word in ["موعد", "حجز", "أريد"]):
                return "سأكون سعيدة لمساعدتك في حجز موعد! في أي تاريخ تود الحضور؟ لدينا مواعيد متاحة الأسبوع القادم يومي الأربعاء والخميس."
            elif any(word in message_lower for word in ["ألم", "يؤلم", "طارئ"]):
                return "أفهم أن لديك ألماً. هذا يبدو عاجلاً! سأحولك فوراً إلى فريقنا الطبي للعلاج الفوري. يرجى الانتظار لحظة."
            else:
                return "أنا هنا لمساعدتك في كل ما يتعلق بعيادة الأسنان. يمكنك أن تسألني عن حجز المواعيد أو العلاجات أو الأسعار أو أي سؤال آخر."
        
        # English responses (default)
        else:
            if any(word in message_lower for word in ["hello", "hi", "good morning", "good evening"]):
                return "Hello! I'm Dana, your AI dental assistant. How can I help you today? 😊"
            elif any(word in message_lower for word in ["appointment", "book", "schedule"]):
                return "I'd be happy to help you book an appointment! What date would work best for you? We have availability next week on Wednesday and Thursday."
            elif any(word in message_lower for word in ["pain", "hurt", "emergency"]):
                return "I understand you're experiencing pain. This sounds urgent! I'm connecting you immediately with our medical team for immediate care. Please hold on."
            elif any(word in message_lower for word in ["price", "cost", "how much"]):
                return "Our prices are very competitive. Basic cleaning - $45, Root canal - $150. Would you like a complete price breakdown?"
            else:
                return "I'm here to help you with anything related to our dental clinic. Feel free to ask me about appointments, treatments, prices, or any other questions you might have."

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
    """Main dashboard page with investor and technical views"""
    return """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מערכת ניהול מרפאת שיניים עם בינה מלאכותית - דשבורד מקצועי</title>
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
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.8em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 1.3em;
            font-weight: 500;
        }
        
        .dashboard-tabs {
            display: flex;
            justify-content: center;
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            margin: 20px auto;
            max-width: 600px;
            border-radius: 50px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .tab-button {
            padding: 12px 30px;
            margin: 0 10px;
            background: transparent;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .tab-button.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .dashboard-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            padding: 25px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }
        
        .panel:hover {
            transform: translateY(-5px);
        }
        
        .panel h2 {
            color: #2c3e50;
            margin-bottom: 25px;
            font-size: 1.8em;
            text-align: center;
            font-weight: 700;
        }
        
        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px;
            margin: 12px 0;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            border-left: 5px solid #3498db;
            transition: all 0.3s ease;
        }
        
        .metric-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 1.6em;
            font-weight: bold;
            color: #27ae60;
        }
        
        .roi-highlight {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin: 25px 0;
            box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);
        }
        
        .roi-highlight h3 {
            font-size: 3.2em;
            margin-bottom: 15px;
            font-weight: 800;
        }
        
        .roi-highlight p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .terminal {
            background: #1a1a1a;
            color: #00ff00;
            padding: 25px;
            border-radius: 15px;
            font-family: 'Courier New', monospace;
            height: 320px;
            overflow-y: auto;
            margin: 15px 0;
            border: 2px solid #333;
        }
        
        .terminal-line {
            margin: 6px 0;
            animation: fadeIn 0.5s ease-in;
            font-size: 0.9em;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chat-widget {
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            display: none;
            flex-direction: column;
            z-index: 1000;
            overflow: hidden;
        }
        
        .chat-widget.open {
            display: flex;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin: 12px 0;
            padding: 12px 18px;
            border-radius: 20px;
            max-width: 85%;
            word-wrap: break-word;
        }
        
        .message.dana {
            background: #e3f2fd;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }
        
        .message.user {
            background: #667eea;
            color: white;
            align-self: flex-end;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        
        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            outline: none;
            font-size: 1em;
        }
        
        .chat-input input:focus {
            border-color: #667eea;
        }
        
        .chat-input button {
            padding: 12px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .chat-input button:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .chat-toggle {
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 28px;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            z-index: 1001;
            transition: all 0.3s ease;
        }
        
        .chat-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #27ae60;
            border-radius: 50%;
            margin-left: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .technical-view {
            display: none;
        }
        
        .investor-view {
            display: block;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦷 מערכת ניהול מרפאת שיניים עם בינה מלאכותית</h1>
        <p>דשבורד מקצועי למשקיעים ומומחים טכניים - הדגמה חיה עם דנה AI</p>
    </div>

    <div class="dashboard-tabs">
        <button class="tab-button active" onclick="switchTab('investor')">👔 דשבורד משקיעים</button>
        <button class="tab-button" onclick="switchTab('technical')">🔧 דשבורד טכני</button>
    </div>

    <!-- Investor Dashboard -->
    <div id="investor-dashboard" class="investor-view">
        <div class="dashboard-container">
            <div class="panel">
                <h2>📊 מדדי עסק ו-ROI</h2>
                
                <div class="roi-highlight">
                    <h3>794% ROI</h3>
                    <p>החזר על השקעה תוך 6 חודשים</p>
                </div>
                
                <div class="metric-item">
                    <span>הכנסות חודשיות</span>
                    <span class="metric-value">$125,000</span>
                </div>
                
                <div class="metric-item">
                    <span>חיסכון שנתי מאוטומציה</span>
                    <span class="metric-value">$286,000</span>
                </div>
                
                <div class="metric-item">
                    <span>שביעות רצון מטופלים</span>
                    <span class="metric-value">94.8%</span>
                </div>
                
                <div class="metric-item">
                    <span>שמירה על מטופלים</span>
                    <span class="metric-value">92.3%</span>
                </div>
                
                <div class="metric-item">
                    <span>ערך טיפול ממוצע</span>
                    <span class="metric-value">$850</span>
                </div>
            </div>

            <div class="panel">
                <h2>📈 פעילות עסקית בזמן אמת</h2>
                
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
                    <span>מטופלים חדשים החודש</span>
                    <span class="metric-value">89</span>
                </div>
                
                <div class="terminal" id="businessTerminal">
                    <div class="terminal-line">[BUSINESS] ROI מחושב: 794%</div>
                    <div class="terminal-line">[BUSINESS] חיסכון חודשי: $23,833</div>
                    <div class="terminal-line">[BUSINESS] יעילות תפעולית: +67%</div>
                    <div class="terminal-line">[BUSINESS] מטופל חדש נרשם למערכת</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Technical Dashboard -->
    <div id="technical-dashboard" class="technical-view">
        <div class="dashboard-container">
            <div class="panel">
                <h2>🖥️ מוניטורינג מערכת</h2>
                
                <div class="metric-item">
                    <span>זמינות מערכת</span>
                    <span class="metric-value">99.97%</span>
                </div>
                
                <div class="metric-item">
                    <span>זמן תגובה ממוצע</span>
                    <span class="metric-value">185ms</span>
                </div>
                
                <div class="metric-item">
                    <span>משתמשים מחוברים</span>
                    <span class="metric-value">1,247</span>
                </div>
                
                <div class="metric-item">
                    <span>הודעות מעובדות</span>
                    <span class="metric-value">15,847</span>
                </div>
                
                <div class="metric-item">
                    <span>דיוק AI</span>
                    <span class="metric-value">96.2%</span>
                </div>
                
                <div class="terminal" id="systemTerminal">
                    <div class="terminal-line">[INFO] מערכת AI פעילה - Dana מוכנה לשיחות</div>
                    <div class="terminal-line">[INFO] שרת WebSocket פועל על פורט 8766</div>
                    <div class="terminal-line">[INFO] מעבד 1,500 פרופילי מטופלים</div>
                    <div class="terminal-line">[INFO] זיהוי שפה אוטומטי: עברית, אנגלית, ערבית</div>
                </div>
            </div>

            <div class="panel">
                <h2>🤖 ביצועי AI ושפות</h2>
                
                <div class="metric-item">
                    <span>זיהוי שפה</span>
                    <span class="metric-value">98.5%</span>
                </div>
                
                <div class="metric-item">
                    <span>ביצועי מסד נתונים</span>
                    <span class="metric-value">94.1%</span>
                </div>
                
                <div class="metric-item">
                    <span>ציון אבטחה</span>
                    <span class="metric-value">99.8%</span>
                </div>
                
                <div class="metric-item">
                    <span>פרודוקטיביות צוות</span>
                    <span class="metric-value">78.5%</span>
                </div>
                
                <div class="terminal" id="aiTerminal">
                    <div class="terminal-line">[AI] Dana מגיבה בעברית למטופל</div>
                    <div class="terminal-line">[AI] זיהוי כוונה: קביעת תור (97% ביטחון)</div>
                    <div class="terminal-line">[AI] ניתוב לסוכן תורים</div>
                    <div class="terminal-line">[AI] תור נקבע בהצלחה ל-15:30</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Chat Widget -->
    <button class="chat-toggle" onclick="toggleChat()">💬</button>
    
    <div class="chat-widget" id="chatWidget">
        <div class="chat-header">
            <div>
                <strong>דנה - העוזרת הדיגיטלית</strong>
                <span class="status-indicator"></span>
                <div style="font-size: 0.9em; opacity: 0.9;">🟢 מחוברת ופעילה</div>
            </div>
            <button onclick="toggleChat()" style="background: none; border: none; color: white; font-size: 24px; cursor: pointer;">×</button>
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

        function switchTab(tabName) {
            const investorView = document.getElementById('investor-dashboard');
            const technicalView = document.getElementById('technical-dashboard');
            const buttons = document.querySelectorAll('.tab-button');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            
            if (tabName === 'investor') {
                investorView.style.display = 'block';
                technicalView.style.display = 'none';
                buttons[0].classList.add('active');
            } else {
                investorView.style.display = 'none';
                technicalView.style.display = 'block';
                buttons[1].classList.add('active');
            }
        }

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
            const aiTerminal = document.getElementById('aiTerminal');
            
            const systemMessages = [
                '[INFO] עיבוד הודעה חדשה מ-WhatsApp',
                '[INFO] Dana מגיבה בעברית למטופל',
                '[INFO] תור נקבע בהצלחה ל-15:30',
                '[INFO] התראת חירום נשלחה לרופא',
                '[INFO] סנכרון עם מערכת Open Dental',
                '[INFO] גיבוי אוטומטי הושלם',
                '[INFO] עדכון מסד נתונים מטופלים',
                '[INFO] מערכת אבטחה פעילה'
            ];
            
            const businessMessages = [
                '[BUSINESS] מטופל חדש נרשם למערכת',
                '[BUSINESS] חיסכון זמן: 45 דקות השעה',
                '[BUSINESS] שביעות רצון: 96.2%',
                '[BUSINESS] יעילות תפעולית: +71%',
                '[BUSINESS] הכנסות נוספות: $1,250',
                '[BUSINESS] ROI מעודכן: 798%',
                '[BUSINESS] מטופל חוזר קבע 3 תורים',
                '[BUSINESS] חיסכון בעלויות: $890'
            ];
            
            const aiMessages = [
                '[AI] זיהוי שפה: עברית (98% ביטחון)',
                '[AI] ניתוח רגש: חיובי',
                '[AI] ניתוב לסוכן תורים',
                '[AI] Dana מתחילה שיחת חולין',
                '[AI] זיהוי כוונה: מידע על טיפולים',
                '[AI] תגובה מותאמת תרבותית',
                '[AI] שמירת הקשר שיחה',
                '[AI] העברה לרופא - מקרה דחוף'
            ];
            
            setInterval(() => {
                // Update system terminal
                const randomSystem = systemMessages[Math.floor(Math.random() * systemMessages.length)];
                const systemLine = document.createElement('div');
                systemLine.className = 'terminal-line';
                systemLine.textContent = randomSystem;
                systemTerminal.appendChild(systemLine);
                
                // Update business terminal
                const randomBusiness = businessMessages[Math.floor(Math.random() * businessMessages.length)];
                const businessLine = document.createElement('div');
                businessLine.className = 'terminal-line';
                businessLine.textContent = randomBusiness;
                businessTerminal.appendChild(businessLine);
                
                // Update AI terminal
                const randomAI = aiMessages[Math.floor(Math.random() * aiMessages.length)];
                const aiLine = document.createElement('div');
                aiLine.className = 'terminal-line';
                aiLine.textContent = randomAI;
                aiTerminal.appendChild(aiLine);
                
                // Keep only last 8 lines in each terminal
                [systemTerminal, businessTerminal, aiTerminal].forEach(terminal => {
                    while (terminal.children.length > 8) {
                        terminal.removeChild(terminal.firstChild);
                    }
                });
            }, 2500);
        }

        // Start terminal updates
        updateTerminals();
    </script>
</body>
</html>
    """

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
        },
        "metrics": {
            "business": BUSINESS_METRICS,
            "technical": TECHNICAL_METRICS
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
        "technical_metrics": TECHNICAL_METRICS,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Start chat server in background thread
    chat_thread = threading.Thread(target=run_chat_server, daemon=True)
    chat_thread.start()
    
    # Start Flask app
    logger.info("🦷 Starting Dental Clinic AI System...")
    logger.info("👔 Investor Dashboard: Available")
    logger.info("🔧 Technical Dashboard: Available") 
    logger.info("🤖 Dana AI: Ready for conversations")
    logger.info(f"💬 Chat server: ws://0.0.0.0:{CHAT_SERVER_PORT}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
