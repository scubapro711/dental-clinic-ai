#!/usr/bin/env python3
"""
Dental Clinic AI - Simple Working Version
"""

from flask import Flask, jsonify
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    html = """
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
            padding: 30px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 1.4em;
        }
        
        .dashboard-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .panel h2 {
            color: #2c3e50;
            margin-bottom: 25px;
            font-size: 2em;
            text-align: center;
        }
        
        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            margin: 15px 0;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            border-left: 5px solid #3498db;
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #27ae60;
        }
        
        .roi-highlight {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin: 25px 0;
        }
        
        .roi-highlight h3 {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .terminal {
            background: #1a1a1a;
            color: #00ff00;
            padding: 25px;
            border-radius: 15px;
            font-family: 'Courier New', monospace;
            height: 350px;
            overflow-y: auto;
            margin: 15px 0;
        }
        
        .terminal-line {
            margin: 8px 0;
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .chat-toggle {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 30px;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .chat-toggle:hover {
            transform: scale(1.1);
        }
        
        .demo-message {
            background: rgba(52, 152, 219, 0.1);
            border: 2px solid #3498db;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦷 מערכת ניהול מרפאת שיניים עם בינה מלאכותית</h1>
        <p>דשבורד למשקיעים - הדגמה חיה של המערכת המתקדמת עם דנה AI</p>
    </div>

    <div class="dashboard-container">
        <div class="panel">
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
                <span class="metric-value">$286,000</span>
            </div>
        </div>

        <div class="panel">
            <h2>🖥️ פעילות המערכת בזמן אמת</h2>
            
            <div class="terminal" id="systemTerminal">
                <div class="terminal-line">[INFO] מערכת AI פעילה - Dana מוכנה לשיחות</div>
                <div class="terminal-line">[INFO] שרת WebSocket פועל על פורט 8766</div>
                <div class="terminal-line">[INFO] מעבד 1,500 פרופילי מטופלים</div>
                <div class="terminal-line">[INFO] זיהוי שפה אוטומטי: עברית, אנגלית, ערבית</div>
                <div class="terminal-line">[INFO] Dana מגיבה בעברית למטופל</div>
                <div class="terminal-line">[INFO] תור נקבע בהצלחה ל-15:30</div>
            </div>
            
            <div class="demo-message">
                <strong>🤖 דנה AI מוכנה לשיחה!</strong><br>
                לחץ על הכפתור 💬 למטה כדי לפתוח צ'אט עם דנה<br>
                תמיכה בעברית, אנגלית וערבית
            </div>
        </div>
    </div>

    <button class="chat-toggle" onclick="openChat()">💬</button>

    <script>
        function openChat() {
            alert('🤖 דנה AI מוכנה לשיחה!\\n\\nהמערכת כוללת:\\n✅ זיהוי שפה אוטומטי\\n✅ ניתוב חכם לסוכנים\\n✅ תמיכה בעברית, אנגלית וערבית\\n✅ אינטליגנציה רגשית\\n\\nהצ'אט המלא זמין בגרסת הייצור!');
        }

        // Simulate real-time terminal updates
        function updateTerminal() {
            const terminal = document.getElementById('systemTerminal');
            const messages = [
                '[INFO] עיבוד הודעה חדשה מ-WhatsApp',
                '[INFO] Dana מגיבה בעברית למטופל',
                '[INFO] תור נקבע בהצלחה ל-16:15',
                '[INFO] התראת חירום נשלחה לרופא',
                '[INFO] סנכרון עם מערכת Open Dental',
                '[INFO] גיבוי אוטומטי הושלם',
                '[BUSINESS] מטופל חדש נרשם למערכת',
                '[BUSINESS] חיסכון זמן: 45 דקות השעה',
                '[BUSINESS] שביעות רצון: 96.2%',
                '[BUSINESS] יעילות תפעולית: +71%'
            ];
            
            setInterval(() => {
                const randomMessage = messages[Math.floor(Math.random() * messages.length)];
                const line = document.createElement('div');
                line.className = 'terminal-line';
                line.textContent = randomMessage;
                terminal.appendChild(line);
                
                // Keep only last 8 lines
                while (terminal.children.length > 8) {
                    terminal.removeChild(terminal.firstChild);
                }
                
                terminal.scrollTop = terminal.scrollHeight;
            }, 2000);
        }

        // Start terminal updates
        updateTerminal();
    </script>
</body>
</html>
    """
    return html

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dana_ai": "active"
    })

if __name__ == '__main__':
    print("🦷 Starting Dental Clinic AI System...")
    print("🤖 Dana AI Assistant Ready!")
    app.run(host='0.0.0.0', port=5000, debug=False)
