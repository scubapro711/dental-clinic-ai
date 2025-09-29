#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dental Clinic AI - Mission Control Dashboard
מרכז השליטה והבקרה למערכת AI של מרפאת השיניים

This is the original dashboard we created together with:
- Language selection (Hebrew, English, Arabic)
- Simulation controls
- Real-time terminals
- Agent monitoring
- Mission Control interface
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import random
import time
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

# Global state for real-time data
dashboard_state = {
    'agent_status': 'active',
    'active_patients': 1234,
    'appointments_today': 56,
    'system_uptime': 98.5,
    'monthly_revenue': 12345,
    'emergency_cases': 3,
    'avg_wait_time': 12,
    'satisfaction': 94.2,
    'system_load': 67,
    'active_chats': 8,
    'successful_conversations': 142,
    'avg_handling_time': 185,
    'handoff_rate': 12.5,
    'last_activity': datetime.now().isoformat()
}

# Agent activities log
agent_activities = [
    {
        'id': 1,
        'time': '14:32',
        'action': 'שיחה עם מטופל - דוד כהן',
        'status': 'completed',
        'channel': 'whatsapp',
        'result': 'תור נקבע ל-15/10'
    },
    {
        'id': 2,
        'time': '14:28',
        'action': 'עדכון יומן - ביטול תור',
        'status': 'completed',
        'channel': 'system',
        'result': 'תור 16:00 בוטל, מטופל הוזמן'
    },
    {
        'id': 3,
        'time': '14:25',
        'action': 'תקשורת עם מטופל - שרה לוי',
        'status': 'needs_handoff',
        'channel': 'phone',
        'result': 'דרושה התערבות אנושית'
    }
]

def simulate_real_time_data():
    """Simulate real-time data updates"""
    while True:
        time.sleep(5)
        
        # Update some metrics
        dashboard_state['active_chats'] = random.randint(5, 15)
        dashboard_state['system_load'] = random.randint(45, 85)
        dashboard_state['avg_handling_time'] = random.randint(120, 240)
        dashboard_state['last_activity'] = datetime.now().isoformat()
        
        # Occasionally add new activity
        if random.random() > 0.7:
            new_activity = {
                'id': int(time.time()),
                'time': datetime.now().strftime('%H:%M'),
                'action': random.choice([
                    'שיחה עם מטופל חדש',
                    'עדכון יומן תורים',
                    'תזכורת נשלחה למטופל',
                    'בקשת מידע על טיפול'
                ]),
                'status': random.choice(['completed', 'completed', 'completed', 'needs_handoff']),
                'channel': random.choice(['whatsapp', 'phone', 'system']),
                'result': 'פעולה אוטומטית'
            }
            agent_activities.insert(0, new_activity)
            if len(agent_activities) > 10:
                agent_activities.pop()

# Start background simulation
simulation_thread = threading.Thread(target=simulate_real_time_data, daemon=True)
simulation_thread.start()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template_string(MISSION_CONTROL_TEMPLATE)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint for real-time dashboard data"""
    return jsonify({
        'state': dashboard_state,
        'activities': agent_activities[:5],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agent-control', methods=['POST'])
def agent_control():
    """API endpoint for agent control actions"""
    data = request.get_json()
    action = data.get('action')
    
    if action == 'pause':
        dashboard_state['agent_status'] = 'idle'
    elif action == 'resume':
        dashboard_state['agent_status'] = 'active'
    elif action == 'monitor':
        dashboard_state['agent_status'] = 'monitoring'
    
    return jsonify({'status': 'success', 'new_status': dashboard_state['agent_status']})

# The original Mission Control Dashboard HTML template
MISSION_CONTROL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מרכז השליטה והבקרה - DentalAI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .terminal-text {
            font-family: 'Courier New', monospace;
            color: #00ff00;
            background: #000;
        }
        
        .pulse-dot {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .slide-in {
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .glow {
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Top Header -->
    <header class="bg-white border-b border-gray-200 h-16 px-6 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div class="flex items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-blue-900 rounded-lg flex items-center justify-center">
                    <i data-lucide="shield" class="w-5 h-5 text-white"></i>
                </div>
                <h1 class="text-xl font-bold text-blue-900">מרכז השליטה והבקרה</h1>
            </div>
            
            <!-- Agent Status -->
            <div class="flex items-center gap-2 bg-gray-100 px-3 py-1 rounded-full">
                <div id="agent-status-dot" class="w-3 h-3 rounded-full bg-green-500 pulse-dot"></div>
                <span id="agent-status-text" class="text-sm font-medium text-blue-900">סוכן פעיל</span>
            </div>
            
            <!-- Language Selector -->
            <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
                <button onclick="setLanguage('he')" class="language-btn px-3 py-1 text-sm rounded bg-blue-900 text-white" data-lang="he">עב</button>
                <button onclick="setLanguage('en')" class="language-btn px-3 py-1 text-sm rounded text-gray-600" data-lang="en">EN</button>
                <button onclick="setLanguage('ar')" class="language-btn px-3 py-1 text-sm rounded text-gray-600" data-lang="ar">عر</button>
            </div>
        </div>

        <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg">
                <i data-lucide="bell" class="w-5 h-5"></i>
            </button>
            <div class="w-8 h-8 bg-blue-900 rounded-full flex items-center justify-center">
                <i data-lucide="user" class="w-4 h-4 text-white"></i>
            </div>
        </div>
    </header>

    <div class="flex h-[calc(100vh-4rem)]">
        <!-- Sidebar -->
        <aside class="w-64 bg-blue-900 text-white flex flex-col">
            <!-- Logo -->
            <div class="p-6 border-b border-blue-800">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                        <i data-lucide="cpu" class="w-5 h-5 text-blue-900"></i>
                    </div>
                    <span class="font-bold">DentalAI</span>
                </div>
            </div>

            <!-- Navigation -->
            <nav class="flex-1 p-4">
                <div class="space-y-2">
                    <button onclick="setActiveTab('overview')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right bg-blue-800 border-r-4 border-r-blue-400" data-tab="overview">
                        <i data-lucide="activity" class="w-5 h-5"></i>
                        <span>סקירה כללית</span>
                    </button>
                    
                    <button onclick="setActiveTab('chat')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800" data-tab="chat">
                        <i data-lucide="message-square" class="w-5 h-5"></i>
                        <span>היסטוריית שיחות</span>
                    </button>
                    
                    <button onclick="setActiveTab('analytics')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800" data-tab="analytics">
                        <i data-lucide="bar-chart-3" class="w-5 h-5"></i>
                        <span>ניתוח ביצועים</span>
                    </button>
                    
                    <button onclick="setActiveTab('knowledge')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800" data-tab="knowledge">
                        <i data-lucide="brain" class="w-5 h-5"></i>
                        <span>ניהול ידע</span>
                    </button>
                </div>
                
                <!-- Simulation Controls -->
                <div class="mt-8 p-4 bg-blue-800 rounded-lg">
                    <h3 class="font-semibold mb-3">בקרת סימולציות</h3>
                    <div class="space-y-2">
                        <button onclick="runSimulation('busy_day')" class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm">
                            יום עמוס
                        </button>
                        <button onclick="runSimulation('emergency')" class="w-full px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-sm">
                            מצב חירום
                        </button>
                        <button onclick="runSimulation('normal')" class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                            יום רגיל
                        </button>
                    </div>
                </div>
            </nav>

            <!-- Bottom Actions -->
            <div class="p-4 border-t border-blue-800 space-y-2">
                <button class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800">
                    <i data-lucide="settings" class="w-5 h-5"></i>
                    <span>הגדרות</span>
                </button>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 overflow-auto">
            <!-- Overview Tab -->
            <div id="overview-tab" class="tab-content p-6 space-y-6">
                <!-- KPI Cards -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600">תורים היום</p>
                                <p id="appointments-today" class="text-2xl font-bold text-blue-900">56</p>
                                <p class="text-sm text-green-600">+12% מאתמול</p>
                            </div>
                            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                <i data-lucide="calendar" class="w-6 h-6 text-blue-600"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600">שיעור הצלחה</p>
                                <p id="success-rate" class="text-2xl font-bold text-blue-900">98.5%</p>
                                <p class="text-sm text-green-600">+0.2% השבוע</p>
                            </div>
                            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                <i data-lucide="check-circle" class="w-6 h-6 text-green-600"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600">זמן טיפול ממוצע</p>
                                <p id="avg-handling-time" class="text-2xl font-bold text-blue-900">3:05</p>
                                <p class="text-sm text-green-600">-15 שניות</p>
                            </div>
                            <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                                <i data-lucide="clock" class="w-6 h-6 text-yellow-600"></i>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Live Monitoring -->
                    <div class="lg:col-span-2 space-y-6">
                        <!-- Real-time Activities -->
                        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
                            <div class="p-6 border-b border-gray-200">
                                <div class="flex items-center justify-between">
                                    <h3 class="text-lg font-semibold flex items-center gap-2">
                                        <div class="w-3 h-3 bg-green-500 rounded-full pulse-dot"></div>
                                        מעקב חי
                                    </h3>
                                    <span id="completed-actions" class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                                        3 פעולות הושלמו
                                    </span>
                                </div>
                            </div>
                            <div class="p-6">
                                <div id="live-activities" class="space-y-3">
                                    <!-- Activities will be populated by JavaScript -->
                                </div>
                            </div>
                        </div>

                        <!-- Terminal Output -->
                        <div class="bg-black rounded-lg shadow-sm border border-gray-200 glow">
                            <div class="p-4 border-b border-gray-700">
                                <h3 class="text-green-400 font-semibold">טרמינל מערכת</h3>
                            </div>
                            <div class="p-4 h-64 overflow-y-auto">
                                <div id="terminal-output" class="terminal-text text-sm space-y-1">
                                    <!-- Terminal output will be populated by JavaScript -->
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Right Column -->
                    <div class="space-y-6">
                        <!-- System Status -->
                        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
                            <div class="p-6 border-b border-gray-200">
                                <h3 class="text-lg font-semibold">סטטוס מערכת</h3>
                            </div>
                            <div class="p-6 space-y-4">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-600">זמינות מערכת</span>
                                    <span class="text-sm font-semibold text-green-600">99.97%</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-600">עומס מערכת</span>
                                    <span id="system-load" class="text-sm font-semibold">67%</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-600">שיחות פעילות</span>
                                    <span id="active-chats" class="text-sm font-semibold">8</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-600">דיוק AI</span>
                                    <span class="text-sm font-semibold text-green-600">96.2%</span>
                                </div>
                            </div>
                        </div>

                        <!-- Quick Actions -->
                        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
                            <div class="p-6 border-b border-gray-200">
                                <h3 class="text-lg font-semibold">פעולות מהירות</h3>
                            </div>
                            <div class="p-6 space-y-3">
                                <button onclick="pauseAgent()" class="w-full px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-sm">
                                    השהה סוכן
                                </button>
                                <button onclick="resumeAgent()" class="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm">
                                    המשך פעילות
                                </button>
                                <button onclick="viewReports()" class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm">
                                    הצג דוחות
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Other tabs (hidden by default) -->
            <div id="chat-tab" class="tab-content hidden p-6">
                <h2 class="text-2xl font-bold mb-6">היסטוריית שיחות</h2>
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <p class="text-gray-600">תוכן היסטוריית השיחות יוצג כאן...</p>
                </div>
            </div>

            <div id="analytics-tab" class="tab-content hidden p-6">
                <h2 class="text-2xl font-bold mb-6">ניתוח ביצועים</h2>
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <p class="text-gray-600">תוכן ניתוח הביצועים יוצג כאן...</p>
                </div>
            </div>

            <div id="knowledge-tab" class="tab-content hidden p-6">
                <h2 class="text-2xl font-bold mb-6">ניהול ידע</h2>
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <p class="text-gray-600">תוכן ניהול הידע יוצג כאן...</p>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();

        // Global state
        let currentLanguage = 'he';
        let currentTab = 'overview';
        let dashboardData = {};

        // Language translations
        const translations = {
            he: {
                title: 'מרכז השליטה והבקרה',
                agentActive: 'סוכן פעיל',
                agentIdle: 'סוכן במנוחה',
                overview: 'סקירה כללית',
                chatHistory: 'היסטוריית שיחות',
                analytics: 'ניתוח ביצועים',
                knowledge: 'ניהול ידע'
            },
            en: {
                title: 'Mission Control Center',
                agentActive: 'Agent Active',
                agentIdle: 'Agent Idle',
                overview: 'Overview',
                chatHistory: 'Chat History',
                analytics: 'Analytics',
                knowledge: 'Knowledge'
            },
            ar: {
                title: 'مركز التحكم والسيطرة',
                agentActive: 'الوكيل نشط',
                agentIdle: 'الوكيل في راحة',
                overview: 'نظرة عامة',
                chatHistory: 'تاريخ المحادثات',
                analytics: 'تحليل الأداء',
                knowledge: 'إدارة المعرفة'
            }
        };

        // Set language
        function setLanguage(lang) {
            currentLanguage = lang;
            
            // Update language buttons
            document.querySelectorAll('.language-btn').forEach(btn => {
                btn.classList.remove('bg-blue-900', 'text-white');
                btn.classList.add('text-gray-600');
            });
            
            document.querySelector(`[data-lang="${lang}"]`).classList.add('bg-blue-900', 'text-white');
            document.querySelector(`[data-lang="${lang}"]`).classList.remove('text-gray-600');
            
            // Update text content based on language
            updateLanguageContent();
        }

        function updateLanguageContent() {
            const t = translations[currentLanguage];
            document.querySelector('h1').textContent = t.title;
            document.getElementById('agent-status-text').textContent = t.agentActive;
        }

        // Set active tab
        function setActiveTab(tab) {
            currentTab = tab;
            
            // Update navigation
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('bg-blue-800', 'border-r-4', 'border-r-blue-400');
                btn.classList.add('hover:bg-blue-800');
            });
            
            document.querySelector(`[data-tab="${tab}"]`).classList.add('bg-blue-800', 'border-r-4', 'border-r-blue-400');
            document.querySelector(`[data-tab="${tab}"]`).classList.remove('hover:bg-blue-800');
            
            // Update content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            
            document.getElementById(`${tab}-tab`).classList.remove('hidden');
        }

        // Simulation controls
        function runSimulation(type) {
            console.log(`Running ${type} simulation`);
            
            // Add terminal output
            addTerminalOutput(`[${new Date().toLocaleTimeString()}] הפעלת סימולציה: ${type}`);
            
            // Simulate different scenarios
            if (type === 'busy_day') {
                dashboardData.state.active_chats = 15;
                dashboardData.state.system_load = 85;
                addTerminalOutput('[SIMULATION] יום עמוס - 15 שיחות פעילות');
            } else if (type === 'emergency') {
                dashboardData.state.emergency_cases = 5;
                addTerminalOutput('[EMERGENCY] מצב חירום - 5 מקרי חירום פעילים');
            }
            
            updateDashboard();
        }

        // Agent controls
        function pauseAgent() {
            fetch('/api/agent-control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'pause' })
            });
            
            document.getElementById('agent-status-text').textContent = 'סוכן במנוחה';
            document.getElementById('agent-status-dot').classList.remove('bg-green-500', 'pulse-dot');
            document.getElementById('agent-status-dot').classList.add('bg-yellow-500');
            
            addTerminalOutput('[CONTROL] סוכן הושהה');
        }

        function resumeAgent() {
            fetch('/api/agent-control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'resume' })
            });
            
            document.getElementById('agent-status-text').textContent = 'סוכן פעיל';
            document.getElementById('agent-status-dot').classList.remove('bg-yellow-500');
            document.getElementById('agent-status-dot').classList.add('bg-green-500', 'pulse-dot');
            
            addTerminalOutput('[CONTROL] סוכן חזר לפעילות');
        }

        function viewReports() {
            addTerminalOutput('[REPORTS] יצירת דוח ביצועים...');
            setTimeout(() => {
                addTerminalOutput('[REPORTS] דוח נוצר בהצלחה');
            }, 1000);
        }

        // Terminal functions
        function addTerminalOutput(text) {
            const terminal = document.getElementById('terminal-output');
            const line = document.createElement('div');
            line.textContent = text;
            terminal.appendChild(line);
            
            // Keep only last 20 lines
            while (terminal.children.length > 20) {
                terminal.removeChild(terminal.firstChild);
            }
            
            // Scroll to bottom
            terminal.scrollTop = terminal.scrollHeight;
        }

        // Update dashboard with real-time data
        function updateDashboard() {
            if (dashboardData.state) {
                document.getElementById('appointments-today').textContent = dashboardData.state.appointments_today;
                document.getElementById('success-rate').textContent = dashboardData.state.system_uptime.toFixed(1) + '%';
                document.getElementById('avg-handling-time').textContent = 
                    Math.floor(dashboardData.state.avg_handling_time / 60) + ':' + 
                    (dashboardData.state.avg_handling_time % 60).toString().padStart(2, '0');
                document.getElementById('system-load').textContent = dashboardData.state.system_load + '%';
                document.getElementById('active-chats').textContent = dashboardData.state.active_chats;
                document.getElementById('completed-actions').textContent = 
                    dashboardData.activities.filter(a => a.status === 'completed').length + ' פעולות הושלמו';
            }
            
            // Update activities
            if (dashboardData.activities) {
                updateActivities();
            }
        }

        function updateActivities() {
            const container = document.getElementById('live-activities');
            container.innerHTML = '';
            
            dashboardData.activities.forEach(activity => {
                const div = document.createElement('div');
                div.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg slide-in';
                
                const statusClass = activity.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
                const statusText = activity.status === 'completed' ? 'הושלם' : 'דרושה התערבות';
                
                div.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div class="flex items-center gap-2">
                            <i data-lucide="${activity.channel === 'whatsapp' ? 'message-circle' : activity.channel === 'phone' ? 'phone' : 'cpu'}" class="w-4 h-4"></i>
                            <span class="text-sm font-medium">${activity.action}</span>
                        </div>
                        <span class="px-2 py-1 ${statusClass} rounded-full text-xs">${statusText}</span>
                    </div>
                    <div class="text-left">
                        <div class="text-sm text-gray-600">${activity.time}</div>
                        <div class="text-xs text-gray-500">${activity.result}</div>
                    </div>
                `;
                
                container.appendChild(div);
            });
            
            // Re-initialize icons
            lucide.createIcons();
        }

        // Fetch real-time data
        function fetchDashboardData() {
            fetch('/api/dashboard-data')
                .then(response => response.json())
                .then(data => {
                    dashboardData = data;
                    updateDashboard();
                })
                .catch(error => {
                    console.error('Error fetching dashboard data:', error);
                });
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Initial terminal output
            addTerminalOutput('[SYSTEM] מערכת DentalAI מופעלת');
            addTerminalOutput('[AGENT] סוכן AI מוכן לפעילות');
            addTerminalOutput('[STATUS] כל המערכות פועלות תקין');
            
            // Start real-time updates
            fetchDashboardData();
            setInterval(fetchDashboardData, 5000);
            
            // Add some terminal activity
            setInterval(() => {
                const activities = [
                    '[MONITOR] בדיקת סטטוס מערכת',
                    '[AI] עיבוד בקשת מטופל',
                    '[SCHEDULER] עדכון יומן תורים',
                    '[NOTIFICATION] שליחת תזכורת',
                    '[ANALYTICS] עדכון מדדי ביצועים'
                ];
                
                addTerminalOutput(activities[Math.floor(Math.random() * activities.length)]);
            }, 3000);
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Starting Mission Control Dashboard...")
    print("📊 Dashboard available at: http://127.0.0.1:5000")
    print("🎯 Features: Language selection, Simulation controls, Real-time monitoring")
    app.run(host='0.0.0.0', port=5000, debug=True)
