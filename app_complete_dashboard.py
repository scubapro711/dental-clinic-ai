#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dental Clinic AI - Complete Mission Control Dashboard
מרכז השליטה והבקרה המלא למערכת AI של מרפאת השיניים

Complete implementation with:
- 5 fully functional terminals (System, AI, Network, Database, Security)
- Full multilingual support (Hebrew, English, Arabic)
- Real-time data visualization across all terminals
- Advanced simulation capabilities
- Complete dashboard functionality
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import random
import time
from datetime import datetime
import threading
import uuid

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
    'memory_usage': 72,
    'cpu_usage': 45,
    'disk_usage': 68,
    'network_latency': 23,
    'active_languages': ['Hebrew', 'English', 'Arabic'],
    'total_patients': 2847,
    'monthly_appointments': 1456
}

# Terminal outputs for different systems
terminal_outputs = {
    'system': [],
    'ai': [],
    'network': [],
    'database': [],
    'security': []
}

# Activity log for real-time monitoring
activity_log = []

def simulate_real_time_data():
    """Simulate comprehensive real-time data updates across all terminals"""
    while True:
        time.sleep(2)  # Update every 2 seconds for more dynamic feel
        
        # Update core metrics with realistic variations
        dashboard_state['active_chats'] = random.randint(5, 15)
        dashboard_state['system_load'] = random.randint(45, 85)
        dashboard_state['cpu_usage'] = random.randint(30, 70)
        dashboard_state['memory_usage'] = random.randint(60, 85)
        dashboard_state['avg_handling_time'] = random.randint(120, 240)
        dashboard_state['database_connections'] = random.randint(30, 60)
        dashboard_state['network_latency'] = random.randint(15, 45)
        dashboard_state['ai_accuracy'] = round(random.uniform(94.0, 98.5), 1)
        dashboard_state['last_activity'] = datetime.now().isoformat()
        
        # Simulate occasional changes in other metrics
        if random.random() > 0.8:
            dashboard_state['appointments_today'] += random.choice([-1, 0, 1, 2])
            dashboard_state['successful_conversations'] += random.choice([0, 1, 2])
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # System terminal - comprehensive system monitoring
        system_messages = [
            f'[{timestamp}] CPU Usage: {dashboard_state["cpu_usage"]}% | Memory: {dashboard_state["memory_usage"]}%',
            f'[{timestamp}] Disk I/O: {random.randint(10, 50)}MB/s | Network: {random.randint(5, 25)}MB/s',
            f'[{timestamp}] Active processes: {random.randint(120, 180)} | Threads: {random.randint(800, 1200)}',
            f'[{timestamp}] System health check: {"OK" if dashboard_state["system_load"] < 80 else "HIGH LOAD"}',
            f'[{timestamp}] Backup status: {"Completed" if random.random() > 0.7 else "In progress"}',
            f'[{timestamp}] Service restart: nginx reloaded successfully',
            f'[{timestamp}] Log rotation: /var/log/dental-ai.log rotated',
            f'[{timestamp}] Temperature: CPU {random.randint(45, 65)}°C | GPU {random.randint(35, 55)}°C'
        ]
        add_terminal_output('system', random.choice(system_messages))
        
        # AI terminal - AI system monitoring and processing
        ai_messages = [
            f'[{timestamp}] Processing patient query: {random.choice(["דוד כהן", "שרה לוי", "מיכל ברק", "אחמד עלי"])}',
            f'[{timestamp}] AI accuracy: {dashboard_state["ai_accuracy"]}% | Confidence: {random.randint(85, 99)}%',
            f'[{timestamp}] Model inference time: {random.randint(50, 200)}ms | Queue: {random.randint(0, 5)}',
            f'[{timestamp}] Language detected: {random.choice(["Hebrew", "English", "Arabic"])}',
            f'[{timestamp}] Intent classification: {random.choice(["appointment_booking", "information_request", "emergency", "complaint"])}',
            f'[{timestamp}] Training data updated: {random.randint(50, 200)} new samples',
            f'[{timestamp}] Model performance: F1-score {random.uniform(0.92, 0.98):.3f}',
            f'[{timestamp}] Knowledge base query: {random.choice(["treatment_prices", "doctor_schedule", "clinic_hours"])}',
            f'[{timestamp}] Conversation completed: Success rate {random.randint(85, 100)}%'
        ]
        add_terminal_output('ai', random.choice(ai_messages))
        
        # Network terminal - network and communication monitoring
        network_messages = [
            f'[{timestamp}] Bandwidth usage: {random.randint(20, 80)}% | Latency: {dashboard_state["network_latency"]}ms',
            f'[{timestamp}] Active connections: {dashboard_state["active_chats"]} | Max concurrent: {random.randint(50, 100)}',
            f'[{timestamp}] WhatsApp API: {"Connected" if random.random() > 0.1 else "Reconnecting..."} | Rate limit: {random.randint(80, 100)}%',
            f'[{timestamp}] SMS gateway: {"Operational" if random.random() > 0.05 else "Degraded"} | Queue: {random.randint(0, 10)}',
            f'[{timestamp}] Phone system: {random.randint(2, 8)} active calls | Wait time: {random.randint(30, 180)}s',
            f'[{timestamp}] CDN status: {random.randint(15, 25)} edge servers active',
            f'[{timestamp}] SSL certificates: {random.randint(5, 10)} days until renewal',
            f'[{timestamp}] Load balancer: {random.choice(["Primary", "Secondary"])} active | Health: OK',
            f'[{timestamp}] API rate limiting: {random.randint(1000, 5000)} requests/hour'
        ]
        add_terminal_output('network', random.choice(network_messages))
        
        # Database terminal - database operations and performance
        db_messages = [
            f'[{timestamp}] Active connections: {dashboard_state["database_connections"]}/{random.randint(80, 120)}',
            f'[{timestamp}] Query execution time: {random.randint(5, 25)}ms | Slow queries: {random.randint(0, 3)}',
            f'[{timestamp}] Patient record updated: ID-{random.randint(1000, 9999)} | Table: patients',
            f'[{timestamp}] Appointment scheduled: {datetime.now().strftime("%Y-%m-%d")} {random.randint(9, 17)}:00',
            f'[{timestamp}] Database backup: {"Completed" if random.random() > 0.8 else "In progress"} | Size: {random.randint(500, 2000)}MB',
            f'[{timestamp}] Index optimization: {random.choice(["appointments", "patients", "treatments"])} table',
            f'[{timestamp}] Replication lag: {random.randint(0, 5)}ms | Sync status: OK',
            f'[{timestamp}] Cache hit ratio: {random.randint(85, 98)}% | Memory usage: {random.randint(60, 90)}%',
            f'[{timestamp}] Transaction log: {random.randint(100, 500)} entries/min'
        ]
        add_terminal_output('database', random.choice(db_messages))
        
        # Security terminal - security monitoring and compliance
        security_messages = [
            f'[{timestamp}] Security scan: {"No threats detected" if random.random() > 0.05 else "1 low-risk issue found"}',
            f'[{timestamp}] HIPAA compliance: {"Verified" if random.random() > 0.02 else "Checking..."} | Audit trail: Active',
            f'[{timestamp}] Encryption status: {"AES-256 Active" if random.random() > 0.01 else "Updating keys..."}',
            f'[{timestamp}] Access log: {random.randint(50, 200)} entries | Failed logins: {random.randint(0, 5)}',
            f'[{timestamp}] Firewall status: {"Protected" if random.random() > 0.02 else "Updating rules"} | Blocked: {random.randint(10, 100)} IPs',
            f'[{timestamp}] Certificate validation: {"Valid" if random.random() > 0.05 else "Renewing..."} | Expires: {random.randint(30, 365)} days',
            f'[{timestamp}] Intrusion detection: {"Clean" if random.random() > 0.1 else "Investigating anomaly"}',
            f'[{timestamp}] Data anonymization: {random.randint(50, 200)} records processed',
            f'[{timestamp}] Vulnerability scan: {"Completed" if random.random() > 0.7 else "Running..."} | Score: {random.randint(85, 100)}/100'
        ]
        add_terminal_output('security', random.choice(security_messages))
        
        # Add to activity log
        add_activity_log({
            'timestamp': timestamp,
            'type': random.choice(['patient_interaction', 'system_event', 'security_check', 'data_update']),
            'description': random.choice([
                'Patient appointment scheduled successfully',
                'AI model processed multilingual query',
                'System backup completed',
                'Security scan passed',
                'Database optimization completed'
            ]),
            'status': random.choice(['success', 'info', 'warning']) if random.random() > 0.1 else 'error'
        })

def add_terminal_output(terminal_type, message):
    """Add message to specific terminal with color coding"""
    if terminal_type not in terminal_outputs:
        terminal_outputs[terminal_type] = []
    
    terminal_outputs[terminal_type].append(message)
    
    # Keep only last 20 messages per terminal for better performance
    if len(terminal_outputs[terminal_type]) > 20:
        terminal_outputs[terminal_type].pop(0)

def add_activity_log(activity):
    """Add activity to the global activity log"""
    activity['id'] = str(uuid.uuid4())
    activity_log.append(activity)
    
    # Keep only last 50 activities
    if len(activity_log) > 50:
        activity_log.pop(0)

# Start background simulation
simulation_thread = threading.Thread(target=simulate_real_time_data, daemon=True)
simulation_thread.start()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template_string(COMPLETE_DASHBOARD_TEMPLATE)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint for real-time dashboard data"""
    return jsonify({
        'state': dashboard_state,
        'terminals': terminal_outputs,
        'activities': activity_log[-10:],  # Last 10 activities
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agent-control', methods=['POST'])
def agent_control():
    """API endpoint for agent control actions"""
    data = request.get_json()
    action = data.get('action')
    
    if action == 'pause':
        dashboard_state['agent_status'] = 'idle'
        add_activity_log({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'type': 'system_event',
            'description': 'Agent paused by operator',
            'status': 'info'
        })
    elif action == 'resume':
        dashboard_state['agent_status'] = 'active'
        add_activity_log({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'type': 'system_event',
            'description': 'Agent resumed by operator',
            'status': 'success'
        })
    elif action == 'monitor':
        dashboard_state['agent_status'] = 'monitoring'
        add_activity_log({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'type': 'system_event',
            'description': 'Agent switched to monitoring mode',
            'status': 'info'
        })
    
    return jsonify({'status': 'success', 'new_status': dashboard_state['agent_status']})

@app.route('/api/simulation', methods=['POST'])
def run_simulation():
    """API endpoint for running simulations"""
    data = request.get_json()
    sim_type = data.get('type')
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    if sim_type == 'busy_day':
        dashboard_state['active_chats'] = random.randint(15, 25)
        dashboard_state['system_load'] = random.randint(75, 95)
        add_terminal_output('system', f'[{timestamp}] SIMULATION: Busy day scenario activated')
        add_terminal_output('ai', f'[{timestamp}] SIMULATION: High volume patient processing')
        
    elif sim_type == 'emergency':
        dashboard_state['emergency_cases'] = random.randint(5, 10)
        dashboard_state['system_load'] = random.randint(85, 100)
        add_terminal_output('security', f'[{timestamp}] SIMULATION: Emergency protocol activated')
        add_terminal_output('system', f'[{timestamp}] SIMULATION: Emergency mode - all systems alert')
        
    elif sim_type == 'multilang':
        add_terminal_output('ai', f'[{timestamp}] SIMULATION: Hebrew query processed - שלום, איך אפשר לעזור?')
        add_terminal_output('ai', f'[{timestamp}] SIMULATION: English query processed - Hello, how can I help?')
        add_terminal_output('ai', f'[{timestamp}] SIMULATION: Arabic query processed - مرحبا، كيف يمكنني المساعدة؟')
        
    elif sim_type == 'normal':
        dashboard_state['active_chats'] = random.randint(5, 10)
        dashboard_state['system_load'] = random.randint(40, 60)
        add_terminal_output('system', f'[{timestamp}] SIMULATION: Normal operations restored')
    
    add_activity_log({
        'timestamp': timestamp,
        'type': 'simulation',
        'description': f'Simulation {sim_type} executed',
        'status': 'info'
    })
    
    return jsonify({'status': 'success', 'simulation': sim_type})

# Complete Dashboard Template with All 5 Terminals
COMPLETE_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מרכז השליטה והבקרה המלא - DentalAI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Terminal Styles with Distinct Colors */
        .terminal-system { 
            font-family: 'Courier New', monospace; 
            color: #00ff00; 
            background: linear-gradient(135deg, #001100 0%, #002200 100%);
            border: 1px solid #00ff00;
        }
        .terminal-ai { 
            font-family: 'Courier New', monospace; 
            color: #00bfff; 
            background: linear-gradient(135deg, #001122 0%, #002244 100%);
            border: 1px solid #00bfff;
        }
        .terminal-network { 
            font-family: 'Courier New', monospace; 
            color: #ff6600; 
            background: linear-gradient(135deg, #220011 0%, #440022 100%);
            border: 1px solid #ff6600;
        }
        .terminal-database { 
            font-family: 'Courier New', monospace; 
            color: #ffff00; 
            background: linear-gradient(135deg, #112200 0%, #224400 100%);
            border: 1px solid #ffff00;
        }
        .terminal-security { 
            font-family: 'Courier New', monospace; 
            color: #ff0066; 
            background: linear-gradient(135deg, #220022 0%, #440044 100%);
            border: 1px solid #ff0066;
        }
        
        .terminal-content {
            height: 200px;
            overflow-y: auto;
            padding: 12px;
            font-size: 12px;
            line-height: 1.4;
        }
        
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
        
        /* Scrollbar styling for terminals */
        .terminal-content::-webkit-scrollbar {
            width: 6px;
        }
        .terminal-content::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.1);
        }
        .terminal-content::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.3);
            border-radius: 3px;
        }
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
                <h1 id="main-title" class="text-xl font-bold text-blue-900">מרכז השליטה והבקרה המלא</h1>
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
                
                <!-- Agent Controls -->
                <div class="mt-8 p-4 bg-blue-800 rounded-lg">
                    <h3 class="font-semibold mb-3" data-translate="agent-controls">בקרת סוכן</h3>
                    <div class="space-y-2">
                        <button onclick="controlAgent('pause')" class="w-full px-3 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-sm">
                            <i data-lucide="pause" class="w-4 h-4 inline mr-2"></i>
                            <span data-translate="agent-pause">השהה</span>
                        </button>
                        <button onclick="controlAgent('resume')" class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm">
                            <i data-lucide="play" class="w-4 h-4 inline mr-2"></i>
                            <span data-translate="agent-resume">המשך</span>
                        </button>
                        <button onclick="controlAgent('monitor')" class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                            <i data-lucide="eye" class="w-4 h-4 inline mr-2"></i>
                            <span data-translate="agent-monitor">מעקב</span>
                        </button>
                    </div>
                </div>
                
                <!-- Simulation Controls -->
                <div class="mt-4 p-4 bg-blue-800 rounded-lg">
                    <h3 class="font-semibold mb-3" data-translate="simulation-title">בקרת סימולציות</h3>
                    <div class="space-y-2">
                        <button onclick="runSimulation('busy_day')" class="w-full px-3 py-2 bg-orange-600 hover:bg-orange-700 rounded text-sm" data-translate="sim-busy">
                            יום עמוס
                        </button>
                        <button onclick="runSimulation('emergency')" class="w-full px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-sm" data-translate="sim-emergency">
                            מצב חירום
                        </button>
                        <button onclick="runSimulation('normal')" class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm" data-translate="sim-normal">
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

                <!-- System Status and AI Metrics -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- System Status -->
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h3 class="text-lg font-semibold mb-4" data-translate="system-status">סטטוס מערכת</h3>
                        <div class="space-y-4">
                            <div class="flex justify-between items-center">
                                <span data-translate="status-uptime">זמינות מערכת</span>
                                <span id="system-uptime" class="font-semibold text-green-600">98.5%</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span data-translate="status-load">עומס מערכת</span>
                                <span id="system-load" class="font-semibold">67%</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span data-translate="status-memory">זיכרון</span>
                                <span id="memory-usage" class="font-semibold">72%</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span data-translate="status-db">חיבורי DB</span>
                                <span id="db-connections" class="font-semibold">45</span>
                            </div>
                        </div>
                    </div>

                    <!-- AI Metrics -->
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h3 class="text-lg font-semibold mb-4" data-translate="ai-metrics">מדדי AI</h3>
                        <div class="space-y-4">
                            <div class="flex justify-between items-center">
                                <span data-translate="ai-accuracy">דיוק AI</span>
                                <span id="ai-accuracy" class="font-semibold text-green-600">96.2%</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span data-translate="ai-conversations">שיחות מוצלחות</span>
                                <span id="successful-conversations" class="font-semibold">142</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span data-translate="ai-handoff">העברה לאנושי</span>
                                <span id="handoff-rate" class="font-semibold">12.5%</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span data-translate="ai-languages">שפות פעילות</span>
                                <span class="font-semibold">3</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Activity -->
                <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <h3 class="text-lg font-semibold mb-4" data-translate="recent-activity">פעילות אחרונה</h3>
                    <div id="activity-log" class="space-y-2">
                        <!-- Activities will be populated by JavaScript -->
                    </div>
                </div>
            </div>

            <!-- Terminals Tab -->
            <div id="terminals-tab" class="tab-content p-6 space-y-6 hidden">
                <h2 class="text-2xl font-bold text-blue-900" data-translate="terminals-title">טרמינלים בזמן אמת</h2>
                
                <!-- All 5 Terminals Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                    <!-- System Terminal -->
                    <div class="terminal-system rounded-lg glow-green">
                        <div class="p-3 border-b border-green-500">
                            <h3 class="font-semibold flex items-center gap-2">
                                <i data-lucide="cpu" class="w-4 h-4"></i>
                                <span data-translate="terminal-system">טרמינל מערכת</span>
                            </h3>
                        </div>
                        <div id="terminal-system" class="terminal-content">
                            <!-- System terminal output -->
                        </div>
                    </div>

                    <!-- AI Terminal -->
                    <div class="terminal-ai rounded-lg glow-blue">
                        <div class="p-3 border-b border-blue-500">
                            <h3 class="font-semibold flex items-center gap-2">
                                <i data-lucide="brain" class="w-4 h-4"></i>
                                <span data-translate="terminal-ai">טרמינל AI</span>
                            </h3>
                        </div>
                        <div id="terminal-ai" class="terminal-content">
                            <!-- AI terminal output -->
                        </div>
                    </div>

                    <!-- Network Terminal -->
                    <div class="terminal-network rounded-lg glow-orange">
                        <div class="p-3 border-b border-orange-500">
                            <h3 class="font-semibold flex items-center gap-2">
                                <i data-lucide="wifi" class="w-4 h-4"></i>
                                <span data-translate="terminal-network">טרמינל רשת</span>
                            </h3>
                        </div>
                        <div id="terminal-network" class="terminal-content">
                            <!-- Network terminal output -->
                        </div>
                    </div>

                    <!-- Database Terminal -->
                    <div class="terminal-database rounded-lg glow-yellow">
                        <div class="p-3 border-b border-yellow-500">
                            <h3 class="font-semibold flex items-center gap-2">
                                <i data-lucide="database" class="w-4 h-4"></i>
                                <span data-translate="terminal-database">טרמינל בסיס נתונים</span>
                            </h3>
                        </div>
                        <div id="terminal-database" class="terminal-content">
                            <!-- Database terminal output -->
                        </div>
                    </div>

                    <!-- Security Terminal -->
                    <div class="terminal-security rounded-lg glow-pink">
                        <div class="p-3 border-b border-pink-500">
                            <h3 class="font-semibold flex items-center gap-2">
                                <i data-lucide="shield" class="w-4 h-4"></i>
                                <span data-translate="terminal-security">טרמינל אבטחה</span>
                            </h3>
                        </div>
                        <div id="terminal-security" class="terminal-content">
                            <!-- Security terminal output -->
                        </div>
                    </div>

                    <!-- Overview Terminal (6th terminal for general info) -->
                    <div class="bg-gray-800 text-green-400 rounded-lg border border-gray-600">
                        <div class="p-3 border-b border-gray-600">
                            <h3 class="font-semibold flex items-center gap-2">
                                <i data-lucide="activity" class="w-4 h-4"></i>
                                <span data-translate="terminal-overview">סקירה כללית</span>
                            </h3>
                        </div>
                        <div id="terminal-overview" class="terminal-content font-mono text-sm">
                            <div>System Status: OPERATIONAL</div>
                            <div>All terminals: ACTIVE</div>
                            <div>Monitoring: ENABLED</div>
                            <div>Real-time updates: ON</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Analytics Tab -->
            <div id="analytics-tab" class="tab-content p-6 space-y-6 hidden">
                <h2 class="text-2xl font-bold text-blue-900" data-translate="analytics-title">ניתוח ביצועים</h2>
                <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <p data-translate="analytics-content">תוכן ניתוח הביצועים יוצג כאן...</p>
                </div>
            </div>

            <!-- Knowledge Tab -->
            <div id="knowledge-tab" class="tab-content p-6 space-y-6 hidden">
                <h2 class="text-2xl font-bold text-blue-900" data-translate="knowledge-title">ניהול ידע</h2>
                <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <p data-translate="knowledge-content">תוכן ניהול הידע יוצג כאן...</p>
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

        // Complete translations for all content
        const translations = {
            he: {
                'main-title': 'מרכז השליטה והבקרה המלא',
                'agent-active': 'סוכן פעיל',
                'agent-idle': 'סוכן במנוחה',
                'agent-monitoring': 'סוכן במעקב',
                'nav-overview': 'סקירה כללית',
                'nav-terminals': 'טרמינלים',
                'nav-analytics': 'ניתוח ביצועים',
                'nav-knowledge': 'ניהול ידע',
                'agent-controls': 'בקרת סוכן',
                'agent-pause': 'השהה',
                'agent-resume': 'המשך',
                'agent-monitor': 'מעקב',
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
                'recent-activity': 'פעילות אחרונה',
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
                'main-title': 'Complete Mission Control Center',
                'agent-active': 'Agent Active',
                'agent-idle': 'Agent Idle',
                'agent-monitoring': 'Agent Monitoring',
                'nav-overview': 'Overview',
                'nav-terminals': 'Terminals',
                'nav-analytics': 'Analytics',
                'nav-knowledge': 'Knowledge',
                'agent-controls': 'Agent Controls',
                'agent-pause': 'Pause',
                'agent-resume': 'Resume',
                'agent-monitor': 'Monitor',
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
                'recent-activity': 'Recent Activity',
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
                'main-title': 'مركز التحكم والسيطرة الكامل',
                'agent-active': 'الوكيل نشط',
                'agent-idle': 'الوكيل في راحة',
                'agent-monitoring': 'الوكيل في مراقبة',
                'nav-overview': 'نظرة عامة',
                'nav-terminals': 'المحطات',
                'nav-analytics': 'تحليل الأداء',
                'nav-knowledge': 'إدارة المعرفة',
                'agent-controls': 'التحكم في الوكيل',
                'agent-pause': 'إيقاف مؤقت',
                'agent-resume': 'استئناف',
                'agent-monitor': 'مراقبة',
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
                'recent-activity': 'النشاط الأخير',
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
            
            // Update agent status text based on current status
            const statusMap = {
                'active': t['agent-active'],
                'idle': t['agent-idle'],
                'monitoring': t['agent-monitoring']
            };
            
            if (dashboardData.state && statusMap[dashboardData.state.agent_status]) {
                document.getElementById('agent-status-text').textContent = statusMap[dashboardData.state.agent_status];
            }
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

        // Agent control functions
        function controlAgent(action) {
            fetch('/api/agent-control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action: action })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Agent control response:', data);
                // Update agent status dot color
                const dot = document.getElementById('agent-status-dot');
                const statusColors = {
                    'active': 'bg-green-500',
                    'idle': 'bg-yellow-500',
                    'monitoring': 'bg-blue-500'
                };
                
                // Remove all status colors
                Object.values(statusColors).forEach(color => {
                    dot.classList.remove(color);
                });
                
                // Add new status color
                dot.classList.add(statusColors[data.new_status] || 'bg-gray-500');
                
                // Update status text
                updateLanguageContent();
            })
            .catch(error => {
                console.error('Error controlling agent:', error);
            });
        }

        // Simulation controls
        function runSimulation(type) {
            fetch('/api/simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ type: type })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Simulation response:', data);
            })
            .catch(error => {
                console.error('Error running simulation:', error);
            });
        }

        // Update dashboard with real-time data
        function updateDashboard() {
            if (dashboardData.state) {
                // Update KPI cards
                document.getElementById('appointments-today').textContent = dashboardData.state.appointments_today;
                document.getElementById('success-rate').textContent = dashboardData.state.system_uptime.toFixed(1) + '%';
                document.getElementById('avg-handling-time').textContent = 
                    Math.floor(dashboardData.state.avg_handling_time / 60) + ':' + 
                    (dashboardData.state.avg_handling_time % 60).toString().padStart(2, '0');
                document.getElementById('active-chats').textContent = dashboardData.state.active_chats;
                
                // Update system status
                document.getElementById('system-load').textContent = dashboardData.state.system_load + '%';
                document.getElementById('memory-usage').textContent = dashboardData.state.memory_usage + '%';
                document.getElementById('db-connections').textContent = dashboardData.state.database_connections;
                
                // Update AI metrics
                document.getElementById('ai-accuracy').textContent = dashboardData.state.ai_accuracy + '%';
                document.getElementById('successful-conversations').textContent = dashboardData.state.successful_conversations;
                document.getElementById('handoff-rate').textContent = dashboardData.state.handoff_rate + '%';
            }
            
            // Update terminals
            if (dashboardData.terminals) {
                updateTerminals();
            }
            
            // Update activity log
            if (dashboardData.activities) {
                updateActivityLog();
            }
            
            // Update language content to reflect any status changes
            updateLanguageContent();
        }

        function updateTerminals() {
            Object.keys(dashboardData.terminals).forEach(terminalType => {
                const terminalElement = document.getElementById(`terminal-${terminalType}`);
                if (terminalElement) {
                    terminalElement.innerHTML = '';
                    dashboardData.terminals[terminalType].forEach(line => {
                        const div = document.createElement('div');
                        div.textContent = line;
                        div.classList.add('slide-in');
                        terminalElement.appendChild(div);
                    });
                    terminalElement.scrollTop = terminalElement.scrollHeight;
                }
            });
        }

        function updateActivityLog() {
            const activityLogElement = document.getElementById('activity-log');
            if (activityLogElement && dashboardData.activities) {
                activityLogElement.innerHTML = '';
                dashboardData.activities.forEach(activity => {
                    const div = document.createElement('div');
                    div.className = 'flex items-center justify-between p-2 bg-gray-50 rounded';
                    
                    const statusColors = {
                        'success': 'text-green-600',
                        'info': 'text-blue-600',
                        'warning': 'text-yellow-600',
                        'error': 'text-red-600'
                    };
                    
                    div.innerHTML = `
                        <div class="flex items-center gap-2">
                            <span class="text-sm text-gray-500">${activity.timestamp}</span>
                            <span class="text-sm">${activity.description}</span>
                        </div>
                        <span class="text-xs px-2 py-1 rounded ${statusColors[activity.status] || 'text-gray-600'}">${activity.status}</span>
                    `;
                    
                    activityLogElement.appendChild(div);
                });
            }
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
            setInterval(fetchDashboardData, 2000); // Update every 2 seconds
            
            // Initialize with Hebrew
            setLanguage('he');
            
            // Initialize Lucide icons
            lucide.createIcons();
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Starting Complete Mission Control Dashboard...")
    print("📊 Dashboard available at: http://127.0.0.1:5000")
    print("🎯 Features:")
    print("   • 5 Real-time Terminals (System, AI, Network, Database, Security)")
    print("   • Full Multilingual Support (Hebrew, English, Arabic)")
    print("   • Real-time Data Visualization")
    print("   • Agent Control System")
    print("   • Advanced Simulation Capabilities")
    print("   • Complete Activity Monitoring")
    print("🌐 Languages: Hebrew (עברית), English, Arabic (العربية)")
    print("💻 Terminals: All systems operational and monitoring")
    app.run(host='0.0.0.0', port=5000, debug=True)
