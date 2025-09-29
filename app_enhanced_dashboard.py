#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dental Clinic AI - Enhanced Mission Control Dashboard
מרכז השליטה והבקרה המשודרג למערכת AI של מרפאת השיניים

Enhanced version with:
- Multiple terminals (System, AI, Network, Database, Security)
- Full multilingual support (Hebrew, English, Arabic)
- Real-time data across all terminals
- Advanced monitoring capabilities
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
    'last_activity': datetime.now().isoformat(),
    'network_status': 'optimal',
    'database_connections': 45,
    'security_alerts': 0,
    'ai_accuracy': 96.2,
    'memory_usage': 72
}

# Terminal outputs for different systems
terminal_outputs = {
    'system': [],
    'ai': [],
    'network': [],
    'database': [],
    'security': []
}

def simulate_real_time_data():
    """Simulate real-time data updates across all terminals"""
    while True:
        time.sleep(3)
        
        # Update metrics
        dashboard_state['active_chats'] = random.randint(5, 15)
        dashboard_state['system_load'] = random.randint(45, 85)
        dashboard_state['avg_handling_time'] = random.randint(120, 240)
        dashboard_state['database_connections'] = random.randint(30, 60)
        dashboard_state['memory_usage'] = random.randint(60, 85)
        dashboard_state['last_activity'] = datetime.now().isoformat()
        
        # Add terminal outputs
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # System terminal
        system_messages = [
            f'[{timestamp}] CPU Usage: {dashboard_state["system_load"]}%',
            f'[{timestamp}] Memory: {dashboard_state["memory_usage"]}% used',
            f'[{timestamp}] Active processes: {random.randint(120, 180)}',
            f'[{timestamp}] System health check: OK',
            f'[{timestamp}] Backup completed successfully'
        ]
        add_terminal_output('system', random.choice(system_messages))
        
        # AI terminal
        ai_messages = [
            f'[{timestamp}] Processing patient query: דוד כהן',
            f'[{timestamp}] AI accuracy: {dashboard_state["ai_accuracy"]}%',
            f'[{timestamp}] Model inference time: {random.randint(50, 200)}ms',
            f'[{timestamp}] Training data updated',
            f'[{timestamp}] Natural language processing: Hebrew detected'
        ]
        add_terminal_output('ai', random.choice(ai_messages))
        
        # Network terminal
        network_messages = [
            f'[{timestamp}] Bandwidth usage: {random.randint(20, 80)}%',
            f'[{timestamp}] Active connections: {dashboard_state["active_chats"]}',
            f'[{timestamp}] Latency: {random.randint(10, 50)}ms',
            f'[{timestamp}] WhatsApp API: Connected',
            f'[{timestamp}] SMS gateway: Operational'
        ]
        add_terminal_output('network', random.choice(network_messages))
        
        # Database terminal
        db_messages = [
            f'[{timestamp}] Active connections: {dashboard_state["database_connections"]}',
            f'[{timestamp}] Query execution time: {random.randint(5, 25)}ms',
            f'[{timestamp}] Patient record updated: ID-{random.randint(1000, 9999)}',
            f'[{timestamp}] Appointment scheduled successfully',
            f'[{timestamp}] Database backup: In progress'
        ]
        add_terminal_output('database', random.choice(db_messages))
        
        # Security terminal
        security_messages = [
            f'[{timestamp}] Security scan: No threats detected',
            f'[{timestamp}] HIPAA compliance: Verified',
            f'[{timestamp}] Encryption status: Active',
            f'[{timestamp}] Access log: {random.randint(50, 200)} entries',
            f'[{timestamp}] Firewall status: Protected'
        ]
        add_terminal_output('security', random.choice(security_messages))

def add_terminal_output(terminal_type, message):
    """Add message to specific terminal"""
    if terminal_type not in terminal_outputs:
        terminal_outputs[terminal_type] = []
    
    terminal_outputs[terminal_type].append(message)
    
    # Keep only last 15 messages per terminal
    if len(terminal_outputs[terminal_type]) > 15:
        terminal_outputs[terminal_type].pop(0)

# Start background simulation
simulation_thread = threading.Thread(target=simulate_real_time_data, daemon=True)
simulation_thread.start()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template_string(ENHANCED_DASHBOARD_TEMPLATE)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint for real-time dashboard data"""
    return jsonify({
        'state': dashboard_state,
        'terminals': terminal_outputs,
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

# Enhanced Dashboard Template with Multiple Terminals and Full Multilingual Support
ENHANCED_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מרכז השליטה והבקרה המשודרג - DentalAI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .terminal-system { font-family: 'Courier New', monospace; color: #00ff00; background: #000; }
        .terminal-ai { font-family: 'Courier New', monospace; color: #00bfff; background: #001122; }
        .terminal-network { font-family: 'Courier New', monospace; color: #ff6600; background: #220011; }
        .terminal-database { font-family: 'Courier New', monospace; color: #ffff00; background: #112200; }
        .terminal-security { font-family: 'Courier New', monospace; color: #ff0066; background: #220022; }
        
        .pulse-dot { animation: pulse 2s infinite; }
        .slide-in { animation: slideIn 0.3s ease-out; }
        .glow-green { box-shadow: 0 0 20px rgba(0, 255, 0, 0.3); }
        .glow-blue { box-shadow: 0 0 20px rgba(0, 191, 255, 0.3); }
        .glow-orange { box-shadow: 0 0 20px rgba(255, 102, 0, 0.3); }
        .glow-yellow { box-shadow: 0 0 20px rgba(255, 255, 0, 0.3); }
        .glow-pink { box-shadow: 0 0 20px rgba(255, 0, 102, 0.3); }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        
        .rtl { direction: rtl; }
        .ltr { direction: ltr; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen" id="main-body">
    <!-- Top Header -->
    <header class="bg-white border-b border-gray-200 h-16 px-6 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div class="flex items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-blue-900 rounded-lg flex items-center justify-center">
                    <i data-lucide="shield" class="w-5 h-5 text-white"></i>
                </div>
                <h1 id="main-title" class="text-xl font-bold text-blue-900">מרכז השליטה והבקרה המשודרג</h1>
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
                        <span data-translate="nav-overview">סקירה כללית</span>
                    </button>
                    
                    <button onclick="setActiveTab('terminals')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800" data-tab="terminals">
                        <i data-lucide="terminal" class="w-5 h-5"></i>
                        <span data-translate="nav-terminals">טרמינלים</span>
                    </button>
                    
                    <button onclick="setActiveTab('analytics')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800" data-tab="analytics">
                        <i data-lucide="bar-chart-3" class="w-5 h-5"></i>
                        <span data-translate="nav-analytics">ניתוח ביצועים</span>
                    </button>
                    
                    <button onclick="setActiveTab('knowledge')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800" data-tab="knowledge">
                        <i data-lucide="brain" class="w-5 h-5"></i>
                        <span data-translate="nav-knowledge">ניהול ידע</span>
                    </button>
                </div>
                
                <!-- Simulation Controls -->
                <div class="mt-8 p-4 bg-blue-800 rounded-lg">
                    <h3 class="font-semibold mb-3" data-translate="simulation-title">בקרת סימולציות</h3>
                    <div class="space-y-2">
                        <button onclick="runSimulation('busy_day')" class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm" data-translate="sim-busy">
                            יום עמוס
                        </button>
                        <button onclick="runSimulation('emergency')" class="w-full px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-sm" data-translate="sim-emergency">
                            מצב חירום
                        </button>
                        <button onclick="runSimulation('normal')" class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm" data-translate="sim-normal">
                            יום רגיל
                        </button>
                        <button onclick="runSimulation('multilang')" class="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm" data-translate="sim-multilang">
                            רב לשוני
                        </button>
                    </div>
                </div>
            </nav>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 overflow-auto">
            <!-- Overview Tab -->
            <div id="overview-tab" class="tab-content p-6 space-y-6">
                <!-- KPI Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600" data-translate="kpi-appointments">תורים היום</p>
                                <p id="appointments-today" class="text-xl font-bold text-blue-900">56</p>
                                <p class="text-sm text-green-600">+12%</p>
                            </div>
                            <i data-lucide="calendar" class="w-8 h-8 text-blue-600"></i>
                        </div>
                    </div>
                    
                    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600" data-translate="kpi-success">שיעור הצלחה</p>
                                <p id="success-rate" class="text-xl font-bold text-blue-900">98.5%</p>
                                <p class="text-sm text-green-600">+0.2%</p>
                            </div>
                            <i data-lucide="check-circle" class="w-8 h-8 text-green-600"></i>
                        </div>
                    </div>
                    
                    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600" data-translate="kpi-handling">זמן טיפול</p>
                                <p id="avg-handling-time" class="text-xl font-bold text-blue-900">3:05</p>
                                <p class="text-sm text-green-600">-15s</p>
                            </div>
                            <i data-lucide="clock" class="w-8 h-8 text-yellow-600"></i>
                        </div>
                    </div>
                    
                    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600" data-translate="kpi-chats">שיחות פעילות</p>
                                <p id="active-chats" class="text-xl font-bold text-blue-900">8</p>
                                <p class="text-sm text-blue-600" data-translate="kpi-realtime">בזמן אמת</p>
                            </div>
                            <i data-lucide="message-circle" class="w-8 h-8 text-blue-600"></i>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 class="text-lg font-semibold mb-4" data-translate="system-status">סטטוס מערכת</h3>
                        <div class="space-y-3">
                            <div class="flex justify-between">
                                <span data-translate="status-uptime">זמינות מערכת</span>
                                <span class="text-green-600 font-semibold">99.97%</span>
                            </div>
                            <div class="flex justify-between">
                                <span data-translate="status-load">עומס מערכת</span>
                                <span id="system-load" class="font-semibold">67%</span>
                            </div>
                            <div class="flex justify-between">
                                <span data-translate="status-memory">זיכרון</span>
                                <span id="memory-usage" class="font-semibold">72%</span>
                            </div>
                            <div class="flex justify-between">
                                <span data-translate="status-db">חיבורי DB</span>
                                <span id="db-connections" class="font-semibold">45</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 class="text-lg font-semibold mb-4" data-translate="ai-metrics">מדדי AI</h3>
                        <div class="space-y-3">
                            <div class="flex justify-between">
                                <span data-translate="ai-accuracy">דיוק AI</span>
                                <span id="ai-accuracy" class="text-green-600 font-semibold">96.2%</span>
                            </div>
                            <div class="flex justify-between">
                                <span data-translate="ai-conversations">שיחות מוצלחות</span>
                                <span class="font-semibold">142</span>
                            </div>
                            <div class="flex justify-between">
                                <span data-translate="ai-handoff">העברה לאנושי</span>
                                <span class="font-semibold">12.5%</span>
                            </div>
                            <div class="flex justify-between">
                                <span data-translate="ai-languages">שפות פעילות</span>
                                <span class="font-semibold">3</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Terminals Tab -->
            <div id="terminals-tab" class="tab-content hidden p-6">
                <h2 class="text-2xl font-bold mb-6" data-translate="terminals-title">טרמינלים בזמן אמת</h2>
                
                <!-- Terminals Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                    <!-- System Terminal -->
                    <div class="bg-black rounded-lg shadow-sm border border-gray-200 glow-green">
                        <div class="p-3 border-b border-gray-700">
                            <h3 class="text-green-400 font-semibold flex items-center gap-2">
                                <i data-lucide="cpu" class="w-4 h-4"></i>
                                <span data-translate="terminal-system">טרמינל מערכת</span>
                            </h3>
                        </div>
                        <div class="p-3 h-48 overflow-y-auto">
                            <div id="terminal-system" class="terminal-system text-xs space-y-1"></div>
                        </div>
                    </div>

                    <!-- AI Terminal -->
                    <div class="bg-blue-900 rounded-lg shadow-sm border border-gray-200 glow-blue">
                        <div class="p-3 border-b border-blue-700">
                            <h3 class="text-blue-300 font-semibold flex items-center gap-2">
                                <i data-lucide="brain" class="w-4 h-4"></i>
                                <span data-translate="terminal-ai">טרמינל AI</span>
                            </h3>
                        </div>
                        <div class="p-3 h-48 overflow-y-auto">
                            <div id="terminal-ai" class="terminal-ai text-xs space-y-1"></div>
                        </div>
                    </div>

                    <!-- Network Terminal -->
                    <div class="bg-red-900 rounded-lg shadow-sm border border-gray-200 glow-orange">
                        <div class="p-3 border-b border-red-700">
                            <h3 class="text-orange-300 font-semibold flex items-center gap-2">
                                <i data-lucide="wifi" class="w-4 h-4"></i>
                                <span data-translate="terminal-network">טרמינל רשת</span>
                            </h3>
                        </div>
                        <div class="p-3 h-48 overflow-y-auto">
                            <div id="terminal-network" class="terminal-network text-xs space-y-1"></div>
                        </div>
                    </div>

                    <!-- Database Terminal -->
                    <div class="bg-green-900 rounded-lg shadow-sm border border-gray-200 glow-yellow">
                        <div class="p-3 border-b border-green-700">
                            <h3 class="text-yellow-300 font-semibold flex items-center gap-2">
                                <i data-lucide="database" class="w-4 h-4"></i>
                                <span data-translate="terminal-database">טרמינל בסיס נתונים</span>
                            </h3>
                        </div>
                        <div class="p-3 h-48 overflow-y-auto">
                            <div id="terminal-database" class="terminal-database text-xs space-y-1"></div>
                        </div>
                    </div>

                    <!-- Security Terminal -->
                    <div class="bg-purple-900 rounded-lg shadow-sm border border-gray-200 glow-pink">
                        <div class="p-3 border-b border-purple-700">
                            <h3 class="text-pink-300 font-semibold flex items-center gap-2">
                                <i data-lucide="shield" class="w-4 h-4"></i>
                                <span data-translate="terminal-security">טרמינל אבטחה</span>
                            </h3>
                        </div>
                        <div class="p-3 h-48 overflow-y-auto">
                            <div id="terminal-security" class="terminal-security text-xs space-y-1"></div>
                        </div>
                    </div>

                    <!-- Combined Overview Terminal -->
                    <div class="bg-gray-900 rounded-lg shadow-sm border border-gray-200">
                        <div class="p-3 border-b border-gray-700">
                            <h3 class="text-gray-300 font-semibold flex items-center gap-2">
                                <i data-lucide="activity" class="w-4 h-4"></i>
                                <span data-translate="terminal-overview">סקירה כללית</span>
                            </h3>
                        </div>
                        <div class="p-3 h-48 overflow-y-auto">
                            <div id="terminal-overview" class="text-gray-300 text-xs space-y-1 font-mono"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Other tabs -->
            <div id="analytics-tab" class="tab-content hidden p-6">
                <h2 class="text-2xl font-bold mb-6" data-translate="analytics-title">ניתוח ביצועים</h2>
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <p class="text-gray-600" data-translate="analytics-content">תוכן ניתוח הביצועים יוצג כאן...</p>
                </div>
            </div>

            <div id="knowledge-tab" class="tab-content hidden p-6">
                <h2 class="text-2xl font-bold mb-6" data-translate="knowledge-title">ניהול ידע</h2>
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <p class="text-gray-600" data-translate="knowledge-content">תוכן ניהול הידע יוצג כאן...</p>
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

        // Full translations for all content
        const translations = {
            he: {
                'main-title': 'מרכז השליטה והבקרה המשודרג',
                'agent-active': 'סוכן פעיל',
                'agent-idle': 'סוכן במנוחה',
                'nav-overview': 'סקירה כללית',
                'nav-terminals': 'טרמינלים',
                'nav-analytics': 'ניתוח ביצועים',
                'nav-knowledge': 'ניהול ידע',
                'simulation-title': 'בקרת סימולציות',
                'sim-busy': 'יום עמוס',
                'sim-emergency': 'מצב חירום',
                'sim-normal': 'יום רגיל',
                'sim-multilang': 'רב לשוני',
                'kpi-appointments': 'תורים היום',
                'kpi-success': 'שיעור הצלחה',
                'kpi-handling': 'זמן טיפול',
                'kpi-chats': 'שיחות פעילות',
                'kpi-realtime': 'בזמן אמת',
                'system-status': 'סטטוס מערכת',
                'status-uptime': 'זמינות מערכת',
                'status-load': 'עומס מערכת',
                'status-memory': 'זיכרון',
                'status-db': 'חיבורי DB',
                'ai-metrics': 'מדדי AI',
                'ai-accuracy': 'דיוק AI',
                'ai-conversations': 'שיחות מוצלחות',
                'ai-handoff': 'העברה לאנושי',
                'ai-languages': 'שפות פעילות',
                'terminals-title': 'טרמינלים בזמן אמת',
                'terminal-system': 'טרמינל מערכת',
                'terminal-ai': 'טרמינל AI',
                'terminal-network': 'טרמינל רשת',
                'terminal-database': 'טרמינל בסיס נתונים',
                'terminal-security': 'טרמינל אבטחה',
                'terminal-overview': 'סקירה כללית',
                'analytics-title': 'ניתוח ביצועים',
                'analytics-content': 'תוכן ניתוח הביצועים יוצג כאן...',
                'knowledge-title': 'ניהול ידע',
                'knowledge-content': 'תוכן ניהול הידע יוצג כאן...'
            },
            en: {
                'main-title': 'Enhanced Mission Control Center',
                'agent-active': 'Agent Active',
                'agent-idle': 'Agent Idle',
                'nav-overview': 'Overview',
                'nav-terminals': 'Terminals',
                'nav-analytics': 'Analytics',
                'nav-knowledge': 'Knowledge',
                'simulation-title': 'Simulation Control',
                'sim-busy': 'Busy Day',
                'sim-emergency': 'Emergency',
                'sim-normal': 'Normal Day',
                'sim-multilang': 'Multilingual',
                'kpi-appointments': 'Appointments Today',
                'kpi-success': 'Success Rate',
                'kpi-handling': 'Handling Time',
                'kpi-chats': 'Active Chats',
                'kpi-realtime': 'Real-time',
                'system-status': 'System Status',
                'status-uptime': 'System Uptime',
                'status-load': 'System Load',
                'status-memory': 'Memory',
                'status-db': 'DB Connections',
                'ai-metrics': 'AI Metrics',
                'ai-accuracy': 'AI Accuracy',
                'ai-conversations': 'Successful Conversations',
                'ai-handoff': 'Human Handoff',
                'ai-languages': 'Active Languages',
                'terminals-title': 'Real-time Terminals',
                'terminal-system': 'System Terminal',
                'terminal-ai': 'AI Terminal',
                'terminal-network': 'Network Terminal',
                'terminal-database': 'Database Terminal',
                'terminal-security': 'Security Terminal',
                'terminal-overview': 'Overview',
                'analytics-title': 'Performance Analytics',
                'analytics-content': 'Analytics content will be displayed here...',
                'knowledge-title': 'Knowledge Management',
                'knowledge-content': 'Knowledge management content will be displayed here...'
            },
            ar: {
                'main-title': 'مركز التحكم والسيطرة المحسن',
                'agent-active': 'الوكيل نشط',
                'agent-idle': 'الوكيل في راحة',
                'nav-overview': 'نظرة عامة',
                'nav-terminals': 'المحطات',
                'nav-analytics': 'تحليل الأداء',
                'nav-knowledge': 'إدارة المعرفة',
                'simulation-title': 'التحكم في المحاكاة',
                'sim-busy': 'يوم مزدحم',
                'sim-emergency': 'حالة طوارئ',
                'sim-normal': 'يوم عادي',
                'sim-multilang': 'متعدد اللغات',
                'kpi-appointments': 'المواعيد اليوم',
                'kpi-success': 'معدل النجاح',
                'kpi-handling': 'وقت المعالجة',
                'kpi-chats': 'المحادثات النشطة',
                'kpi-realtime': 'في الوقت الفعلي',
                'system-status': 'حالة النظام',
                'status-uptime': 'وقت تشغيل النظام',
                'status-load': 'حمولة النظام',
                'status-memory': 'الذاكرة',
                'status-db': 'اتصالات قاعدة البيانات',
                'ai-metrics': 'مقاييس الذكاء الاصطناعي',
                'ai-accuracy': 'دقة الذكاء الاصطناعي',
                'ai-conversations': 'المحادثات الناجحة',
                'ai-handoff': 'التحويل للبشر',
                'ai-languages': 'اللغات النشطة',
                'terminals-title': 'المحطات في الوقت الفعلي',
                'terminal-system': 'محطة النظام',
                'terminal-ai': 'محطة الذكاء الاصطناعي',
                'terminal-network': 'محطة الشبكة',
                'terminal-database': 'محطة قاعدة البيانات',
                'terminal-security': 'محطة الأمان',
                'terminal-overview': 'نظرة عامة',
                'analytics-title': 'تحليل الأداء',
                'analytics-content': 'سيتم عرض محتوى التحليلات هنا...',
                'knowledge-title': 'إدارة المعرفة',
                'knowledge-content': 'سيتم عرض محتوى إدارة المعرفة هنا...'
            }
        };

        // Set language and update all content
        function setLanguage(lang) {
            currentLanguage = lang;
            
            // Update language buttons
            document.querySelectorAll('.language-btn').forEach(btn => {
                btn.classList.remove('bg-blue-900', 'text-white');
                btn.classList.add('text-gray-600');
            });
            
            document.querySelector(`[data-lang="${lang}"]`).classList.add('bg-blue-900', 'text-white');
            document.querySelector(`[data-lang="${lang}"]`).classList.remove('text-gray-600');
            
            // Update direction
            const body = document.getElementById('main-body');
            if (lang === 'ar' || lang === 'he') {
                body.classList.add('rtl');
                body.classList.remove('ltr');
                body.setAttribute('dir', 'rtl');
            } else {
                body.classList.add('ltr');
                body.classList.remove('rtl');
                body.setAttribute('dir', 'ltr');
            }
            
            // Update all translatable content
            updateLanguageContent();
        }

        function updateLanguageContent() {
            const t = translations[currentLanguage];
            
            // Update all elements with data-translate attribute
            document.querySelectorAll('[data-translate]').forEach(element => {
                const key = element.getAttribute('data-translate');
                if (t[key]) {
                    element.textContent = t[key];
                }
            });
            
            // Update main title
            document.getElementById('main-title').textContent = t['main-title'];
            document.getElementById('agent-status-text').textContent = t['agent-active'];
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
            
            const t = translations[currentLanguage];
            
            if (type === 'multilang') {
                // Demonstrate multilingual capabilities
                addTerminalOutput('overview', `[MULTILANG] Hebrew: שלום, איך אפשר לעזור?`);
                addTerminalOutput('overview', `[MULTILANG] English: Hello, how can I help?`);
                addTerminalOutput('overview', `[MULTILANG] Arabic: مرحبا، كيف يمكنني المساعدة؟`);
            }
        }

        // Terminal functions
        function addTerminalOutput(terminal, text) {
            const terminalElement = document.getElementById(`terminal-${terminal}`);
            if (terminalElement) {
                const line = document.createElement('div');
                line.textContent = text;
                terminalElement.appendChild(line);
                
                // Keep only last 15 lines
                while (terminalElement.children.length > 15) {
                    terminalElement.removeChild(terminalElement.firstChild);
                }
                
                // Scroll to bottom
                terminalElement.scrollTop = terminalElement.scrollHeight;
            }
        }

        // Update dashboard with real-time data
        function updateDashboard() {
            if (dashboardData.state) {
                document.getElementById('appointments-today').textContent = dashboardData.state.appointments_today;
                document.getElementById('success-rate').textContent = dashboardData.state.system_uptime.toFixed(1) + '%';
                document.getElementById('avg-handling-time').textContent = 
                    Math.floor(dashboardData.state.avg_handling_time / 60) + ':' + 
                    (dashboardData.state.avg_handling_time % 60).toString().padStart(2, '0');
                document.getElementById('active-chats').textContent = dashboardData.state.active_chats;
                document.getElementById('system-load').textContent = dashboardData.state.system_load + '%';
                document.getElementById('memory-usage').textContent = dashboardData.state.memory_usage + '%';
                document.getElementById('db-connections').textContent = dashboardData.state.database_connections;
                document.getElementById('ai-accuracy').textContent = dashboardData.state.ai_accuracy + '%';
            }
            
            // Update terminals
            if (dashboardData.terminals) {
                updateTerminals();
            }
        }

        function updateTerminals() {
            Object.keys(dashboardData.terminals).forEach(terminalType => {
                const terminalElement = document.getElementById(`terminal-${terminalType}`);
                if (terminalElement) {
                    terminalElement.innerHTML = '';
                    dashboardData.terminals[terminalType].forEach(line => {
                        const div = document.createElement('div');
                        div.textContent = line;
                        terminalElement.appendChild(div);
                    });
                    terminalElement.scrollTop = terminalElement.scrollHeight;
                }
            });
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
            // Start real-time updates
            fetchDashboardData();
            setInterval(fetchDashboardData, 3000);
            
            // Initialize with Hebrew
            setLanguage('he');
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Starting Enhanced Mission Control Dashboard...")
    print("📊 Dashboard available at: http://127.0.0.1:5000")
    print("🎯 Features: Multiple terminals, Full multilingual support, Real-time monitoring")
    print("🌐 Languages: Hebrew, English, Arabic (full translation)")
    print("💻 Terminals: System, AI, Network, Database, Security")
    app.run(host='0.0.0.0', port=5000, debug=True)
