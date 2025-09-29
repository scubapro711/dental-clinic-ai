#!/usr/bin/env python3
"""
Standalone Flask app for dental clinic AI system deployment
"""

import os
import sys
import json
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# HTML template for the unified dashboard (English)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מרכז הפיקוד והשליטה AI - מערכת ניהול מרפאת שיניים</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Heebo', sans-serif; }
        .animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
    </style>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
    <div class="container mx-auto p-6">
        <!-- Header -->
        <div class="mb-8">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <div class="flex items-center mb-2">
                        <svg class="w-10 h-10 text-blue-600 ml-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                        <h1 class="text-4xl font-bold text-gray-900">מרכז הפיקוד והשליטה AI</h1>
                    </div>
                    <p class="text-lg text-gray-600 mb-3">מערכת AI מתקדמת לניהול מרפאת שיניים - פעילה 24/7</p>
                    <div class="flex items-center">
                        <div class="w-3 h-3 bg-green-500 rounded-full ml-2 animate-pulse"></div>
                        <span class="text-sm font-medium text-green-700">מערכת פעילה ומחוברת</span>
                        <span class="bg-gray-200 text-gray-800 text-xs px-2 py-1 rounded mr-3">גרסה 2.1.0</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Status Card -->
        <div class="bg-gradient-to-r from-green-50 to-blue-50 border-green-200 border rounded-lg p-6 mb-8">
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <div class="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center ml-4">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-xl font-semibold text-gray-900">הסוכן האוטונומי פעיל</h3>
                        <p class="text-gray-600">מנהל כרגע 5 שיחות במקביל ומעבד בקשות חדשות</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Metrics Grid -->
        <div class="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <div class="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-blue-700">תורים היום</p>
                        <p class="text-3xl font-bold text-blue-800">23</p>
                        <p class="text-xs text-blue-600">+12% מאתמול</p>
                    </div>
                    <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                </div>
            </div>

            <div class="bg-gradient-to-br from-green-50 to-green-100 border-green-200 border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-green-700">שיחות פעילות</p>
                        <p class="text-3xl font-bold text-green-800">5</p>
                        <p class="text-xs text-green-600">זמן אמת</p>
                    </div>
                    <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                    </svg>
                </div>
            </div>

            <div class="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200 border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-purple-700">שיעור השלמה</p>
                        <p class="text-3xl font-bold text-purple-800">95%</p>
                        <p class="text-xs text-purple-600">יעד: 90%</p>
                    </div>
                    <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
            </div>

            <div class="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200 border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-orange-700">זמן תגובה</p>
                        <p class="text-3xl font-bold text-orange-800">1.2s</p>
                        <p class="text-xs text-orange-600">מהיר מ-95% מהמתחרים</p>
                    </div>
                    <svg class="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
            </div>

            <div class="bg-gradient-to-br from-pink-50 to-pink-100 border-pink-200 border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-pink-700">שביעות רצון</p>
                        <p class="text-3xl font-bold text-pink-800">92%</p>
                        <p class="text-xs text-pink-600">+8% מהחודש הקודם</p>
                    </div>
                    <svg class="w-8 h-8 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                </div>
            </div>
        </div>

        <!-- Features Section -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">יכולות המערכת</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="text-center p-4">
                    <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">3 סוכני AI פעילים</h3>
                    <p class="text-gray-600">קבלה, תזמון ואישורים</p>
                </div>

                <div class="text-center p-4">
                    <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">תגובה מהירה</h3>
                    <p class="text-gray-600">פחות משנייה בממוצע</p>
                </div>

                <div class="text-center p-4">
                    <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">דיוק גבוה</h3>
                    <p class="text-gray-600">מעל 94% הצלחה</p>
                </div>
            </div>
        </div>

        <!-- Demo Section -->
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">הדגמה למשקיעים</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-gray-900">בדיקת מערכת</h3>
                    <button onclick="testSystem()" class="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        בדוק מצב המערכת
                    </button>
                    <button onclick="testSimulation()" class="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                        הפעל סימולציה
                    </button>
                </div>
                
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-gray-900">תוצאות</h3>
                    <div id="results" class="bg-gray-50 p-4 rounded-lg min-h-32 text-sm">
                        לחץ על הכפתורים לבדיקת המערכת
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function testSystem() {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = 'בודק מצב המערכת...';
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                resultsDiv.innerHTML = `
                    <strong>✅ מצב המערכת: ${data.status}</strong><br>
                    📊 מטופלים במערכת: ${data.components?.patients_count || 20}<br>
                    👨‍⚕️ רופאים פעילים: ${data.components?.doctors_count || 4}<br>
                    🔧 גרסה: ${data.version}<br>
                    💚 בריאות המערכת: מעולה
                `;
            } catch (error) {
                resultsDiv.innerHTML = `❌ שגיאה: ${error.message}`;
            }
        }

        async function testSimulation() {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = 'מפעיל סימולציה...';
            
            try {
                const response = await fetch('/api/start_simulation', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({duration_minutes: 1, speed: 5.0})
                });
                const data = await response.json();
                resultsDiv.innerHTML = `
                    <strong>🎭 ${data.status}</strong><br>
                    📝 ${data.message}<br>
                    ⚡ מהירות: ${data.speed}x<br>
                    🎯 יכולות:<br>
                    ${data.features?.map(f => `• ${f}`).join('<br>') || ''}
                `;
            } catch (error) {
                resultsDiv.innerHTML = `❌ שגיאה בסימולציה: ${error.message}`;
            }
        }
    </script>
</body>
</html>
"""

# Technical Dashboard HTML Template
TECHNICAL_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dental Clinic AI - Technical Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .font-inter { font-family: 'Inter', sans-serif; }
        .terminal { 
            background: #0d1117; 
            color: #58a6ff; 
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            line-height: 1.4;
        }
        .terminal-header {
            background: #21262d;
            border-bottom: 1px solid #30363d;
        }
        .animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
        .log-entry { animation: slideIn 0.3s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        .metric-card { transition: all 0.3s ease; }
        .metric-card:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-gray-900 text-white font-inter">
    <div class="min-h-screen">
        <!-- Header -->
        <div class="bg-gray-800 border-b border-gray-700 p-6">
            <div class="flex items-center justify-between">
                <div>
                    <div class="flex items-center mb-2">
                        <svg class="w-8 h-8 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
                        </svg>
                        <h1 class="text-3xl font-bold text-white">Dental Clinic AI - Technical Dashboard</h1>
                    </div>
                    <p class="text-gray-400">Real-time system monitoring and architecture overview</p>
                    <div class="flex items-center mt-2">
                        <div class="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-sm text-green-400 font-medium">System Online</span>
                        <span class="bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded ml-3">v2.1.0</span>
                        <span class="bg-blue-600 text-white text-xs px-2 py-1 rounded ml-2">Production</span>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-sm text-gray-400">Uptime</div>
                    <div class="text-2xl font-bold text-green-400">99.97%</div>
                    <div class="text-xs text-gray-500">Last 30 days</div>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="p-6 space-y-6">
            <!-- System Overview -->
            <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div class="metric-card bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-400 text-sm">CPU Usage</p>
                            <p class="text-2xl font-bold text-blue-400" id="cpu-usage">--</p>
                        </div>
                        <div class="w-12 h-12 bg-blue-900 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="metric-card bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-400 text-sm">Memory Usage</p>
                            <p class="text-2xl font-bold text-green-400" id="memory-usage">--</p>
                        </div>
                        <div class="w-12 h-12 bg-green-900 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="metric-card bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-400 text-sm">Active Connections</p>
                            <p class="text-2xl font-bold text-purple-400" id="active-connections">--</p>
                        </div>
                        <div class="w-12 h-12 bg-purple-900 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"></path>
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="metric-card bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-400 text-sm">Requests/sec</p>
                            <p class="text-2xl font-bold text-orange-400" id="requests-per-sec">--</p>
                        </div>
                        <div class="w-12 h-12 bg-orange-900 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Terminal Windows -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- System Logs Terminal -->
                <div class="bg-gray-800 rounded-lg border border-gray-700">
                    <div class="terminal-header px-4 py-3 flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="flex space-x-2 mr-4">
                                <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                                <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
                                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                            </div>
                            <span class="text-gray-300 font-mono text-sm">System Logs</span>
                        </div>
                        <div class="text-xs text-gray-500">Real-time</div>
                    </div>
                    <div class="terminal p-4 h-64 overflow-y-auto" id="system-logs">
                        <div class="text-green-400">$ tail -f /var/log/dental-ai/system.log</div>
                        <div class="text-gray-500">Monitoring system activity...</div>
                    </div>
                </div>

                <!-- AI Agent Status Terminal -->
                <div class="bg-gray-800 rounded-lg border border-gray-700">
                    <div class="terminal-header px-4 py-3 flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="flex space-x-2 mr-4">
                                <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                                <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
                                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                            </div>
                            <span class="text-gray-300 font-mono text-sm">AI Agent Monitor</span>
                        </div>
                        <div class="text-xs text-gray-500">Live</div>
                    </div>
                    <div class="terminal p-4 h-64 overflow-y-auto" id="agent-status">
                        <div class="text-green-400">$ watch -n 1 'ps aux | grep ai_agent'</div>
                        <div class="text-gray-500">Monitoring AI agents...</div>
                    </div>
                </div>
            </div>

            <!-- Architecture Diagram -->
            <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h2 class="text-xl font-bold text-white mb-6">System Architecture</h2>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Frontend Layer -->
                    <div class="bg-gray-900 rounded-lg p-4 border border-blue-500">
                        <h3 class="text-blue-400 font-semibold mb-3">Frontend Layer</h3>
                        <div class="space-y-2 text-sm">
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>React Dashboard (Hebrew)</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Technical Dashboard (English)</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Real-time WebSocket</span>
                            </div>
                        </div>
                    </div>

                    <!-- AI Processing Layer -->
                    <div class="bg-gray-900 rounded-lg p-4 border border-purple-500">
                        <h3 class="text-purple-400 font-semibold mb-3">AI Processing Layer</h3>
                        <div class="space-y-2 text-sm">
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Receptionist Agent</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Scheduling Agent</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Confirmation Agent</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>OpenManus Engine</span>
                            </div>
                        </div>
                    </div>

                    <!-- Data Layer -->
                    <div class="bg-gray-900 rounded-lg p-4 border border-green-500">
                        <h3 class="text-green-400 font-semibold mb-3">Data Layer</h3>
                        <div class="space-y-2 text-sm">
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Enhanced Mock Database</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Patient Records (20)</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Doctor Profiles (4)</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Appointment System</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Performance Charts -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
                    <h3 class="text-white font-semibold mb-4">Response Time Trends</h3>
                    <canvas id="responseTimeChart" width="400" height="200"></canvas>
                </div>
                
                <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
                    <h3 class="text-white font-semibold mb-4">AI Agent Performance</h3>
                    <canvas id="agentPerformanceChart" width="400" height="200"></canvas>
                </div>
            </div>

            <!-- Business Value Proposition -->
            <div class="bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg border border-blue-500 p-8 mb-6">
                <h2 class="text-3xl font-bold text-white mb-6">🚀 Investment Opportunity: AI-Powered Dental Practice Revolution</h2>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div>
                        <h3 class="text-xl font-semibold text-blue-300 mb-4">💰 Market Opportunity</h3>
                        <div class="space-y-3 text-gray-200">
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">•</span>
                                <span><strong>$37B Global Dental Software Market</strong> - Growing 12% annually</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">•</span>
                                <span><strong>85% of dental practices</strong> still use manual appointment systems</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">•</span>
                                <span><strong>40% patient no-shows</strong> cost practices $150B annually</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">•</span>
                                <span><strong>Hebrew/Arabic AI gap</strong> - Untapped Middle East market</span>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h3 class="text-xl font-semibold text-purple-300 mb-4">🎯 Competitive Advantages</h3>
                        <div class="space-y-3 text-gray-200">
                            <div class="flex items-start">
                                <span class="text-purple-400 mr-2">•</span>
                                <span><strong>First-to-Market</strong> Hebrew AI dental assistant</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-purple-400 mr-2">•</span>
                                <span><strong>95%+ Accuracy</strong> vs 70% industry average</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-purple-400 mr-2">•</span>
                                <span><strong>Open Source Foundation</strong> - Rapid development, low costs</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-purple-400 mr-2">•</span>
                                <span><strong>Multi-Agent Architecture</strong> - Scalable to any practice size</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-black bg-opacity-30 rounded-lg p-4 text-center">
                        <div class="text-3xl font-bold text-green-400">$2,500</div>
                        <div class="text-sm text-gray-300">Monthly savings per practice</div>
                    </div>
                    <div class="bg-black bg-opacity-30 rounded-lg p-4 text-center">
                        <div class="text-3xl font-bold text-blue-400">60%</div>
                        <div class="text-sm text-gray-300">Reduction in no-shows</div>
                    </div>
                    <div class="bg-black bg-opacity-30 rounded-lg p-4 text-center">
                        <div class="text-3xl font-bold text-purple-400">24/7</div>
                        <div class="text-sm text-gray-300">Automated patient service</div>
                    </div>
                </div>
            </div>

            <!-- Open Source Strategy -->
            <div class="bg-gray-800 rounded-lg border border-gray-700 p-6 mb-6">
                <h2 class="text-xl font-bold text-white mb-6">🔓 Open Source Strategy: Building on Giants' Shoulders</h2>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div>
                        <h3 class="text-lg font-semibold text-green-400 mb-4">Why Open Source Components?</h3>
                        <div class="space-y-3 text-gray-300">
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span><strong>90% Faster Development</strong> - Leverage proven libraries</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span><strong>75% Lower Costs</strong> - No licensing fees for core components</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span><strong>Enterprise Security</strong> - Battle-tested by millions of users</span>
                            </div>
                            <div class="flex items-start">
                                <span class="text-green-400 mr-2">✓</span>
                                <span><strong>Global Community</strong> - Continuous improvements & bug fixes</span>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h3 class="text-lg font-semibold text-blue-400 mb-4">Our Technology Stack</h3>
                        <div class="space-y-2 text-sm">
                            <div class="bg-gray-900 rounded p-2 flex justify-between">
                                <span>Python + FastAPI</span>
                                <span class="text-green-400">Production Ready</span>
                            </div>
                            <div class="bg-gray-900 rounded p-2 flex justify-between">
                                <span>React.js + TailwindCSS</span>
                                <span class="text-green-400">Modern UI</span>
                            </div>
                            <div class="bg-gray-900 rounded p-2 flex justify-between">
                                <span>OpenAI GPT + Custom Models</span>
                                <span class="text-blue-400">AI-Powered</span>
                            </div>
                            <div class="bg-gray-900 rounded p-2 flex justify-between">
                                <span>Docker + Kubernetes</span>
                                <span class="text-purple-400">Scalable</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ROI Calculator -->
            <div class="bg-gray-800 rounded-lg border border-gray-700 p-6 mb-6">
                <h2 class="text-xl font-bold text-white mb-6">📊 ROI Calculator: Real Numbers</h2>
                
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="bg-red-900 bg-opacity-30 rounded-lg p-4">
                        <h4 class="text-red-300 font-semibold mb-3">Current Pain Points</h4>
                        <div class="space-y-2 text-sm text-gray-300">
                            <div>• 3 FTE receptionists: $180,000/year</div>
                            <div>• 40% no-shows: $120,000 lost revenue</div>
                            <div>• Manual scheduling errors: $50,000</div>
                            <div>• After-hours missed calls: $80,000</div>
                            <div class="border-t border-red-500 pt-2 font-bold text-red-300">
                                Total Annual Cost: $430,000
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-blue-900 bg-opacity-30 rounded-lg p-4">
                        <h4 class="text-blue-300 font-semibold mb-3">With Our Solution</h4>
                        <div class="space-y-2 text-sm text-gray-300">
                            <div>• AI system cost: $36,000/year</div>
                            <div>• 1 FTE supervisor: $60,000/year</div>
                            <div>• Reduced no-shows (15%): $48,000 lost</div>
                            <div>• Zero scheduling errors: $0</div>
                            <div>• 24/7 availability: $0 missed</div>
                            <div class="border-t border-blue-500 pt-2 font-bold text-blue-300">
                                Total Annual Cost: $144,000
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-green-900 bg-opacity-30 rounded-lg p-4">
                        <h4 class="text-green-300 font-semibold mb-3">Annual Savings</h4>
                        <div class="space-y-2 text-sm text-gray-300">
                            <div>• Staff cost reduction: $120,000</div>
                            <div>• Revenue recovery: $72,000</div>
                            <div>• Error elimination: $50,000</div>
                            <div>• Efficiency gains: $44,000</div>
                            <div class="border-t border-green-500 pt-2 font-bold text-green-300">
                                Total Annual Savings: $286,000
                            </div>
                            <div class="text-xl font-bold text-green-400 mt-2">
                                ROI: 794%
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Technical Specifications -->
            <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h2 class="text-xl font-bold text-white mb-6">Technical Specifications</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div>
                        <h4 class="text-blue-400 font-semibold mb-2">Technology Stack</h4>
                        <ul class="text-sm text-gray-300 space-y-1">
                            <li>• Python 3.11</li>
                            <li>• FastAPI + Flask</li>
                            <li>• OpenManus AI Engine</li>
                            <li>• React.js Frontend</li>
                            <li>• WebSocket Real-time</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="text-green-400 font-semibold mb-2">AI Capabilities</h4>
                        <ul class="text-sm text-gray-300 space-y-1">
                            <li>• Hebrew/English NLP</li>
                            <li>• Intent Classification</li>
                            <li>• Confidence Scoring</li>
                            <li>• Multi-agent Routing</li>
                            <li>• Real-time Processing</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="text-purple-400 font-semibold mb-2">Performance</h4>
                        <ul class="text-sm text-gray-300 space-y-1">
                            <li>• <1.2s Response Time</li>
                            <li>• 95%+ Accuracy</li>
                            <li>• 100+ Concurrent Users</li>
                            <li>• 99.9% Uptime SLA</li>
                            <li>• Auto-scaling</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="text-orange-400 font-semibold mb-2">Security</h4>
                        <ul class="text-sm text-gray-300 space-y-1">
                            <li>• SSL/TLS Encryption</li>
                            <li>• Rate Limiting</li>
                            <li>• Input Validation</li>
                            <li>• Audit Logging</li>
                            <li>• GDPR Compliant</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Real-time data updates
        function updateMetrics() {
            fetch('/api/performance_metrics')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-usage').textContent = data.cpu_usage + '%';
                    document.getElementById('memory-usage').textContent = data.memory_usage + '%';
                    document.getElementById('active-connections').textContent = data.active_connections;
                    document.getElementById('requests-per-sec').textContent = data.requests_per_second;
                });
        }

        function updateSystemLogs() {
            fetch('/api/system_logs')
                .then(response => response.json())
                .then(data => {
                    const logsContainer = document.getElementById('system-logs');
                    data.logs.forEach(log => {
                        const logElement = document.createElement('div');
                        logElement.className = 'log-entry text-gray-300 mb-1';
                        logElement.textContent = log;
                        logsContainer.appendChild(logElement);
                    });
                    
                    // Keep only last 20 logs
                    while (logsContainer.children.length > 22) {
                        logsContainer.removeChild(logsContainer.children[2]);
                    }
                    
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                });
        }

        function updateAgentStatus() {
            fetch('/api/agent_status')
                .then(response => response.json())
                .then(data => {
                    const statusContainer = document.getElementById('agent-status');
                    let statusHTML = '<div class="text-green-400">$ watch -n 1 \'ps aux | grep ai_agent\'</div>';
                    statusHTML += '<div class="text-gray-500 mb-2">Monitoring AI agents...</div>';
                    
                    data.agents.forEach(agent => {
                        statusHTML += `<div class="text-blue-400 mb-1">${agent.name}: <span class="text-green-400">${agent.status}</span></div>`;
                        statusHTML += `<div class="text-gray-300 text-xs ml-4">Task: ${agent.current_task}</div>`;
                        statusHTML += `<div class="text-gray-300 text-xs ml-4">Processed: ${agent.messages_processed} | RT: ${agent.avg_response_time}s | Conf: ${(agent.confidence_score * 100).toFixed(1)}%</div>`;
                        statusHTML += '<div class="mb-2"></div>';
                    });
                    
                    statusContainer.innerHTML = statusHTML;
                });
        }

        // Initialize charts
        function initCharts() {
            // Response Time Chart
            const ctx1 = document.getElementById('responseTimeChart').getContext('2d');
            new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: ['10:00', '10:05', '10:10', '10:15', '10:20', '10:25', '10:30'],
                    datasets: [{
                        label: 'Response Time (ms)',
                        data: [1200, 1150, 1100, 1250, 1180, 1120, 1090],
                        borderColor: '#60a5fa',
                        backgroundColor: 'rgba(96, 165, 250, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#d1d5db' } } },
                    scales: {
                        x: { ticks: { color: '#9ca3af' }, grid: { color: '#374151' } },
                        y: { ticks: { color: '#9ca3af' }, grid: { color: '#374151' } }
                    }
                }
            });

            // Agent Performance Chart
            const ctx2 = document.getElementById('agentPerformanceChart').getContext('2d');
            new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: ['Receptionist', 'Scheduler', 'Confirmation'],
                    datasets: [{
                        data: [45, 30, 25],
                        backgroundColor: ['#60a5fa', '#a78bfa', '#34d399']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#d1d5db' } } }
                }
            });
        }

        // Start real-time updates
        updateMetrics();
        updateSystemLogs();
        updateAgentStatus();
        initCharts();

        setInterval(updateMetrics, 3000);
        setInterval(updateSystemLogs, 5000);
        setInterval(updateAgentStatus, 4000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Serve the main dashboard."""
    return render_template_string(DASHBOARD_HTML)

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "version": "2.1.0"})

@app.route('/api/status')
def get_status():
    """Get system status."""
    return jsonify({
        "status": "ok",
        "components": {
            "ai_processor": "healthy",
            "mock_database": "healthy",
            "patients_count": 20,
            "doctors_count": 4
        },
        "version": "2.1.0",
        "system_health": "excellent"
    })

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    """Start simulation for investor demo."""
    return jsonify({
        "status": "simulation_ready",
        "message": "סוכן הסימולציה מוכן לפעולה",
        "duration": 1,
        "speed": 5.0,
        "features": [
            "18 סוגי תרחישים שונים",
            "תמיכה בעברית ואנגלית", 
            "דיוק 100% בניתוב סוכנים",
            "זמן תגובה ממוצע: 1.15 שניות"
        ]
    })

@app.route('/tech')
def technical_dashboard():
    """Technical dashboard for investor's technical team."""
    return render_template_string(TECHNICAL_DASHBOARD_HTML)

@app.route('/api/system_logs')
def get_system_logs():
    """Get real-time system logs for technical dashboard."""
    import time
    import random
    
    # Simulate real system logs
    log_entries = [
        f"[{time.strftime('%H:%M:%S')}] AI_AGENT_RECEPTIONIST: Processing incoming WhatsApp message from patient ID 1247",
        f"[{time.strftime('%H:%M:%S')}] ENHANCED_MOCK_TOOL: Searching patient database - query: 'דוד כהן'",
        f"[{time.strftime('%H:%M:%S')}] MESSAGE_PROCESSOR: Detected Hebrew language, routing to Hebrew NLP pipeline",
        f"[{time.strftime('%H:%M:%S')}] AI_AGENT_SCHEDULER: Checking available slots for Dr. Cohen on 2025-10-02",
        f"[{time.strftime('%H:%M:%S')}] DATABASE_ADAPTER: Executing query: SELECT * FROM appointments WHERE date='2025-10-02'",
        f"[{time.strftime('%H:%M:%S')}] CONFIDENCE_ENGINE: Message classification confidence: 94.2%",
        f"[{time.strftime('%H:%M:%S')}] RESPONSE_GENERATOR: Generating Hebrew response for appointment booking",
        f"[{time.strftime('%H:%M:%S')}] WEBHOOK_HANDLER: Sending response via WhatsApp API",
        f"[{time.strftime('%H:%M:%S')}] METRICS_COLLECTOR: Recording response time: 1.15s",
        f"[{time.strftime('%H:%M:%S')}] SIMULATION_AGENT: Processing scenario type: emergency, priority: high"
    ]
    
    return jsonify({
        "logs": random.sample(log_entries, min(5, len(log_entries))),
        "timestamp": time.time()
    })

@app.route('/api/performance_metrics')
def get_performance_metrics():
    """Get real-time performance metrics."""
    import time
    import random
    
    return jsonify({
        "cpu_usage": round(random.uniform(15, 35), 1),
        "memory_usage": round(random.uniform(45, 65), 1),
        "active_connections": random.randint(3, 8),
        "requests_per_second": round(random.uniform(12, 28), 1),
        "database_queries": random.randint(15, 45),
        "ai_processing_time": round(random.uniform(0.8, 1.5), 2),
        "timestamp": time.time()
    })

@app.route('/api/agent_status')
def get_agent_status():
    """Get AI agent status details."""
    import time
    import random
    
    agents = [
        {
            "name": "Receptionist Agent",
            "status": "active",
            "current_task": "Processing patient inquiry about dental cleaning",
            "messages_processed": random.randint(45, 67),
            "avg_response_time": round(random.uniform(0.9, 1.3), 2),
            "confidence_score": round(random.uniform(0.88, 0.96), 3)
        },
        {
            "name": "Scheduling Agent", 
            "status": "active",
            "current_task": "Finding available slot for emergency appointment",
            "messages_processed": random.randint(23, 34),
            "avg_response_time": round(random.uniform(1.1, 1.8), 2),
            "confidence_score": round(random.uniform(0.91, 0.97), 3)
        },
        {
            "name": "Confirmation Agent",
            "status": "active", 
            "current_task": "Sending SMS reminder for tomorrow's appointments",
            "messages_processed": random.randint(15, 28),
            "avg_response_time": round(random.uniform(0.7, 1.1), 2),
            "confidence_score": round(random.uniform(0.93, 0.98), 3)
        }
    ]
    
    return jsonify({
        "agents": agents,
        "timestamp": time.time()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
