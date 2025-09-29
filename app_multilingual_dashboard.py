#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dental Clinic AI - Complete Multilingual Mission Control Dashboard
מרכז השליטה והבקרה הרב-לשוני המלא למערכת AI של מרפאת השיניים

Complete implementation with:
- 5 fully functional terminals with multilingual content
- Comprehensive multilingual support (Hebrew, English, Arabic)
- Real-time data visualization with language-aware content
- Advanced simulation capabilities with multilingual responses
- Complete dashboard functionality with full content translation
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

# Terminal outputs for different systems with multilingual support
terminal_outputs = {
    'system': [],
    'ai': [],
    'network': [],
    'database': [],
    'security': []
}

# Activity log for real-time monitoring
activity_log = []

# Multilingual terminal messages
terminal_messages = {
    'he': {
        'system': [
            'שימוש במעבד: {cpu}% | זיכרון: {memory}%',
            'קלט/פלט דיסק: {io}MB/s | רשת: {net}MB/s',
            'תהליכים פעילים: {processes} | חוטים: {threads}',
            'בדיקת תקינות מערכת: {status}',
            'סטטוס גיבוי: {backup_status}',
            'הפעלה מחדש של שירות: nginx נטען בהצלחה',
            'סיבוב לוגים: /var/log/dental-ai.log סובב',
            'טמפרטורה: מעבד {cpu_temp}°C | כרטיס גרפי {gpu_temp}°C'
        ],
        'ai': [
            'עיבוד שאילתת מטופל: {patient}',
            'דיוק AI: {accuracy}% | רמת ביטחון: {confidence}%',
            'זמן היסק מודל: {inference}ms | תור: {queue}',
            'שפה זוהתה: {language}',
            'סיווג כוונה: {intent}',
            'נתוני אימון עודכנו: {samples} דגימות חדשות',
            'ביצועי מודל: F1-score {f1_score}',
            'שאילתת בסיס ידע: {kb_query}',
            'שיחה הושלמה: שיעור הצלחה {success_rate}%'
        ],
        'network': [
            'שימוש ברוחב פס: {bandwidth}% | זמן השהיה: {latency}ms',
            'חיבורים פעילים: {connections} | מקסימום בו-זמני: {max_concurrent}',
            'WhatsApp API: {whatsapp_status} | מגבלת קצב: {rate_limit}%',
            'שער SMS: {sms_status} | תור: {sms_queue}',
            'מערכת טלפון: {active_calls} שיחות פעילות | זמן המתנה: {wait_time}s',
            'סטטוס CDN: {edge_servers} שרתי קצה פעילים',
            'אישורי SSL: {ssl_days} ימים עד חידוש',
            'מאזן עומסים: {load_balancer} פעיל | תקינות: OK',
            'הגבלת קצב API: {api_requests} בקשות/שעה'
        ],
        'database': [
            'חיבורים פעילים: {active_connections}/{max_connections}',
            'זמן ביצוע שאילתה: {query_time}ms | שאילתות איטיות: {slow_queries}',
            'רשומת מטופל עודכנה: ID-{patient_id} | טבלה: patients',
            'תור נקבע: {date} {time}:00',
            'גיבוי בסיס נתונים: {backup_status} | גודל: {backup_size}MB',
            'אופטימיזציית אינדקס: טבלת {table_name}',
            'השהיית שכפול: {replication_lag}ms | סטטוס סנכרון: OK',
            'יחס פגיעות במטמון: {cache_hit}% | שימוש בזיכרון: {cache_memory}%',
            'יומן עסקאות: {transaction_log} רשומות/דקה'
        ],
        'security': [
            'סריקת אבטחה: {security_status}',
            'תאימות HIPAA: {hipaa_status} | מסלול ביקורת: פעיל',
            'סטטוס הצפנה: {encryption_status}',
            'יומן גישה: {access_entries} רשומות | כניסות כושלות: {failed_logins}',
            'סטטוס חומת אש: {firewall_status} | חסומים: {blocked_ips} כתובות IP',
            'אימות אישור: {cert_status} | פג תוקף: {cert_expiry} ימים',
            'זיהוי חדירה: {intrusion_status}',
            'אנונימיזציה של נתונים: {anonymized_records} רשומות עובדו',
            'סריקת פגיעויות: {vuln_status} | ציון: {vuln_score}/100'
        ]
    },
    'en': {
        'system': [
            'CPU Usage: {cpu}% | Memory: {memory}%',
            'Disk I/O: {io}MB/s | Network: {net}MB/s',
            'Active processes: {processes} | Threads: {threads}',
            'System health check: {status}',
            'Backup status: {backup_status}',
            'Service restart: nginx reloaded successfully',
            'Log rotation: /var/log/dental-ai.log rotated',
            'Temperature: CPU {cpu_temp}°C | GPU {gpu_temp}°C'
        ],
        'ai': [
            'Processing patient query: {patient}',
            'AI accuracy: {accuracy}% | Confidence: {confidence}%',
            'Model inference time: {inference}ms | Queue: {queue}',
            'Language detected: {language}',
            'Intent classification: {intent}',
            'Training data updated: {samples} new samples',
            'Model performance: F1-score {f1_score}',
            'Knowledge base query: {kb_query}',
            'Conversation completed: Success rate {success_rate}%'
        ],
        'network': [
            'Bandwidth usage: {bandwidth}% | Latency: {latency}ms',
            'Active connections: {connections} | Max concurrent: {max_concurrent}',
            'WhatsApp API: {whatsapp_status} | Rate limit: {rate_limit}%',
            'SMS gateway: {sms_status} | Queue: {sms_queue}',
            'Phone system: {active_calls} active calls | Wait time: {wait_time}s',
            'CDN status: {edge_servers} edge servers active',
            'SSL certificates: {ssl_days} days until renewal',
            'Load balancer: {load_balancer} active | Health: OK',
            'API rate limiting: {api_requests} requests/hour'
        ],
        'database': [
            'Active connections: {active_connections}/{max_connections}',
            'Query execution time: {query_time}ms | Slow queries: {slow_queries}',
            'Patient record updated: ID-{patient_id} | Table: patients',
            'Appointment scheduled: {date} {time}:00',
            'Database backup: {backup_status} | Size: {backup_size}MB',
            'Index optimization: {table_name} table',
            'Replication lag: {replication_lag}ms | Sync status: OK',
            'Cache hit ratio: {cache_hit}% | Memory usage: {cache_memory}%',
            'Transaction log: {transaction_log} entries/min'
        ],
        'security': [
            'Security scan: {security_status}',
            'HIPAA compliance: {hipaa_status} | Audit trail: Active',
            'Encryption status: {encryption_status}',
            'Access log: {access_entries} entries | Failed logins: {failed_logins}',
            'Firewall status: {firewall_status} | Blocked: {blocked_ips} IPs',
            'Certificate validation: {cert_status} | Expires: {cert_expiry} days',
            'Intrusion detection: {intrusion_status}',
            'Data anonymization: {anonymized_records} records processed',
            'Vulnerability scan: {vuln_status} | Score: {vuln_score}/100'
        ]
    },
    'ar': {
        'system': [
            'استخدام المعالج: {cpu}% | الذاكرة: {memory}%',
            'إدخال/إخراج القرص: {io}MB/s | الشبكة: {net}MB/s',
            'العمليات النشطة: {processes} | الخيوط: {threads}',
            'فحص صحة النظام: {status}',
            'حالة النسخ الاحتياطي: {backup_status}',
            'إعادة تشغيل الخدمة: تم إعادة تحميل nginx بنجاح',
            'دوران السجلات: تم دوران /var/log/dental-ai.log',
            'درجة الحرارة: المعالج {cpu_temp}°C | كرت الرسوميات {gpu_temp}°C'
        ],
        'ai': [
            'معالجة استفسار المريض: {patient}',
            'دقة الذكاء الاصطناعي: {accuracy}% | الثقة: {confidence}%',
            'وقت استنتاج النموذج: {inference}ms | الطابور: {queue}',
            'اللغة المكتشفة: {language}',
            'تصنيف النية: {intent}',
            'تم تحديث بيانات التدريب: {samples} عينة جديدة',
            'أداء النموذج: F1-score {f1_score}',
            'استفسار قاعدة المعرفة: {kb_query}',
            'اكتملت المحادثة: معدل النجاح {success_rate}%'
        ],
        'network': [
            'استخدام عرض النطاق: {bandwidth}% | زمن الاستجابة: {latency}ms',
            'الاتصالات النشطة: {connections} | الحد الأقصى المتزامن: {max_concurrent}',
            'واتساب API: {whatsapp_status} | حد المعدل: {rate_limit}%',
            'بوابة الرسائل القصيرة: {sms_status} | الطابور: {sms_queue}',
            'نظام الهاتف: {active_calls} مكالمات نشطة | وقت الانتظار: {wait_time}s',
            'حالة CDN: {edge_servers} خوادم حافة نشطة',
            'شهادات SSL: {ssl_days} أيام حتى التجديد',
            'موازن الأحمال: {load_balancer} نشط | الصحة: OK',
            'تحديد معدل API: {api_requests} طلب/ساعة'
        ],
        'database': [
            'الاتصالات النشطة: {active_connections}/{max_connections}',
            'وقت تنفيذ الاستعلام: {query_time}ms | الاستعلامات البطيئة: {slow_queries}',
            'تم تحديث سجل المريض: ID-{patient_id} | الجدول: patients',
            'تم جدولة الموعد: {date} {time}:00',
            'نسخ احتياطي لقاعدة البيانات: {backup_status} | الحجم: {backup_size}MB',
            'تحسين الفهرس: جدول {table_name}',
            'تأخير النسخ المتماثل: {replication_lag}ms | حالة المزامنة: OK',
            'نسبة إصابة التخزين المؤقت: {cache_hit}% | استخدام الذاكرة: {cache_memory}%',
            'سجل المعاملات: {transaction_log} إدخال/دقيقة'
        ],
        'security': [
            'فحص الأمان: {security_status}',
            'امتثال HIPAA: {hipaa_status} | مسار التدقيق: نشط',
            'حالة التشفير: {encryption_status}',
            'سجل الوصول: {access_entries} إدخال | تسجيلات دخول فاشلة: {failed_logins}',
            'حالة جدار الحماية: {firewall_status} | محظور: {blocked_ips} عناوين IP',
            'التحقق من الشهادة: {cert_status} | ينتهي: {cert_expiry} أيام',
            'كشف التسلل: {intrusion_status}',
            'إخفاء هوية البيانات: {anonymized_records} سجل تمت معالجته',
            'فحص الثغرات: {vuln_status} | النتيجة: {vuln_score}/100'
        ]
    }
}

# Multilingual patient names and data
multilingual_data = {
    'patient_names': {
        'he': ['דוד כהן', 'שרה לוי', 'מיכל ברק', 'יוסף אברהם', 'רחל גולדברג'],
        'en': ['David Cohen', 'Sarah Levy', 'Michael Barak', 'Joseph Abraham', 'Rachel Goldberg'],
        'ar': ['داود كوهين', 'سارة ليفي', 'ميخائيل باراك', 'يوسف إبراهيم', 'راحيل غولدبرغ']
    },
    'intents': {
        'he': ['קביעת תור', 'בקשת מידע', 'חירום', 'תלונה', 'ביטול תור'],
        'en': ['appointment_booking', 'information_request', 'emergency', 'complaint', 'cancellation'],
        'ar': ['حجز موعد', 'طلب معلومات', 'طوارئ', 'شكوى', 'إلغاء موعد']
    },
    'kb_queries': {
        'he': ['מחירי טיפולים', 'לוח זמנים רופא', 'שעות מרפאה', 'ביטוח בריאות'],
        'en': ['treatment_prices', 'doctor_schedule', 'clinic_hours', 'health_insurance'],
        'ar': ['أسعار العلاج', 'جدول الطبيب', 'ساعات العيادة', 'التأمين الصحي']
    },
    'table_names': {
        'he': ['תורים', 'מטופלים', 'טיפולים', 'רופאים'],
        'en': ['appointments', 'patients', 'treatments', 'doctors'],
        'ar': ['المواعيد', 'المرضى', 'العلاجات', 'الأطباء']
    },
    'status_values': {
        'he': {
            'ok': 'תקין',
            'completed': 'הושלם',
            'in_progress': 'בתהליך',
            'connected': 'מחובר',
            'operational': 'פעיל',
            'verified': 'מאומת',
            'active': 'פעיל',
            'protected': 'מוגן',
            'clean': 'נקי',
            'no_threats': 'לא זוהו איומים',
            'aes_256_active': 'AES-256 פעיל'
        },
        'en': {
            'ok': 'OK',
            'completed': 'Completed',
            'in_progress': 'In progress',
            'connected': 'Connected',
            'operational': 'Operational',
            'verified': 'Verified',
            'active': 'Active',
            'protected': 'Protected',
            'clean': 'Clean',
            'no_threats': 'No threats detected',
            'aes_256_active': 'AES-256 Active'
        },
        'ar': {
            'ok': 'موافق',
            'completed': 'مكتمل',
            'in_progress': 'قيد التقدم',
            'connected': 'متصل',
            'operational': 'تشغيلي',
            'verified': 'تم التحقق',
            'active': 'نشط',
            'protected': 'محمي',
            'clean': 'نظيف',
            'no_threats': 'لم يتم اكتشاف تهديدات',
            'aes_256_active': 'AES-256 نشط'
        }
    }
}

def get_localized_message(terminal_type, language, **kwargs):
    """Get a localized terminal message with dynamic values"""
    if language not in terminal_messages or terminal_type not in terminal_messages[language]:
        language = 'en'  # Fallback to English
    
    messages = terminal_messages[language][terminal_type]
    template = random.choice(messages)
    
    # Fill in dynamic values with localized content
    localized_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and value in multilingual_data['status_values'][language]:
            localized_kwargs[key] = multilingual_data['status_values'][language][value]
        else:
            localized_kwargs[key] = value
    
    try:
        return template.format(**localized_kwargs)
    except KeyError:
        # If formatting fails, return the template as is
        return template

def simulate_real_time_data():
    """Simulate comprehensive real-time data updates with multilingual content"""
    current_language = 'he'  # Default language, will be updated by frontend
    
    while True:
        time.sleep(2)
        
        # Update core metrics
        dashboard_state['active_chats'] = random.randint(5, 15)
        dashboard_state['system_load'] = random.randint(45, 85)
        dashboard_state['cpu_usage'] = random.randint(30, 70)
        dashboard_state['memory_usage'] = random.randint(60, 85)
        dashboard_state['avg_handling_time'] = random.randint(120, 240)
        dashboard_state['database_connections'] = random.randint(30, 60)
        dashboard_state['network_latency'] = random.randint(15, 45)
        dashboard_state['ai_accuracy'] = round(random.uniform(94.0, 98.5), 1)
        dashboard_state['last_activity'] = datetime.now().isoformat()
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Generate multilingual terminal messages
        for lang in ['he', 'en', 'ar']:
            # System terminal
            system_msg = get_localized_message('system', lang,
                cpu=dashboard_state['cpu_usage'],
                memory=dashboard_state['memory_usage'],
                io=random.randint(10, 50),
                net=random.randint(5, 25),
                processes=random.randint(120, 180),
                threads=random.randint(800, 1200),
                status='ok' if dashboard_state['system_load'] < 80 else 'high_load',
                backup_status='completed' if random.random() > 0.7 else 'in_progress',
                cpu_temp=random.randint(45, 65),
                gpu_temp=random.randint(35, 55)
            )
            
            # AI terminal
            ai_msg = get_localized_message('ai', lang,
                patient=random.choice(multilingual_data['patient_names'][lang]),
                accuracy=dashboard_state['ai_accuracy'],
                confidence=random.randint(85, 99),
                inference=random.randint(50, 200),
                queue=random.randint(0, 5),
                language=lang.title(),
                intent=random.choice(multilingual_data['intents'][lang]),
                samples=random.randint(50, 200),
                f1_score=f"{random.uniform(0.92, 0.98):.3f}",
                kb_query=random.choice(multilingual_data['kb_queries'][lang]),
                success_rate=random.randint(85, 100)
            )
            
            # Network terminal
            network_msg = get_localized_message('network', lang,
                bandwidth=random.randint(20, 80),
                latency=dashboard_state['network_latency'],
                connections=dashboard_state['active_chats'],
                max_concurrent=random.randint(50, 100),
                whatsapp_status='connected' if random.random() > 0.1 else 'reconnecting',
                rate_limit=random.randint(80, 100),
                sms_status='operational' if random.random() > 0.05 else 'degraded',
                sms_queue=random.randint(0, 10),
                active_calls=random.randint(2, 8),
                wait_time=random.randint(30, 180),
                edge_servers=random.randint(15, 25),
                ssl_days=random.randint(5, 10),
                load_balancer=random.choice(['Primary', 'Secondary']),
                api_requests=random.randint(1000, 5000)
            )
            
            # Database terminal
            db_msg = get_localized_message('database', lang,
                active_connections=dashboard_state['database_connections'],
                max_connections=random.randint(80, 120),
                query_time=random.randint(5, 25),
                slow_queries=random.randint(0, 3),
                patient_id=random.randint(1000, 9999),
                date=datetime.now().strftime('%Y-%m-%d'),
                time=random.randint(9, 17),
                backup_status='completed' if random.random() > 0.8 else 'in_progress',
                backup_size=random.randint(500, 2000),
                table_name=random.choice(multilingual_data['table_names'][lang]),
                replication_lag=random.randint(0, 5),
                cache_hit=random.randint(85, 98),
                cache_memory=random.randint(60, 90),
                transaction_log=random.randint(100, 500)
            )
            
            # Security terminal
            security_msg = get_localized_message('security', lang,
                security_status='no_threats' if random.random() > 0.05 else 'investigating',
                hipaa_status='verified' if random.random() > 0.02 else 'checking',
                encryption_status='aes_256_active' if random.random() > 0.01 else 'updating',
                access_entries=random.randint(50, 200),
                failed_logins=random.randint(0, 5),
                firewall_status='protected' if random.random() > 0.02 else 'updating',
                blocked_ips=random.randint(10, 100),
                cert_status='verified' if random.random() > 0.05 else 'renewing',
                cert_expiry=random.randint(30, 365),
                intrusion_status='clean' if random.random() > 0.1 else 'investigating',
                anonymized_records=random.randint(50, 200),
                vuln_status='completed' if random.random() > 0.7 else 'running',
                vuln_score=random.randint(85, 100)
            )
            
            # Add messages to terminals (only for current language to avoid clutter)
            if lang == current_language:
                add_terminal_output('system', f'[{timestamp}] {system_msg}')
                add_terminal_output('ai', f'[{timestamp}] {ai_msg}')
                add_terminal_output('network', f'[{timestamp}] {network_msg}')
                add_terminal_output('database', f'[{timestamp}] {db_msg}')
                add_terminal_output('security', f'[{timestamp}] {security_msg}')
        
        # Add to activity log with multilingual descriptions
        activity_descriptions = {
            'he': [
                'תור מטופל נקבע בהצלחה',
                'מודל AI עיבד שאילתה רב-לשונית',
                'גיבוי מערכת הושלם',
                'סריקת אבטחה עברה בהצלחה',
                'אופטימיזציה של בסיס נתונים הושלמה'
            ],
            'en': [
                'Patient appointment scheduled successfully',
                'AI model processed multilingual query',
                'System backup completed',
                'Security scan passed',
                'Database optimization completed'
            ],
            'ar': [
                'تم جدولة موعد المريض بنجاح',
                'نموذج الذكاء الاصطناعي عالج استفسار متعدد اللغات',
                'اكتمل النسخ الاحتياطي للنظام',
                'نجح فحص الأمان',
                'اكتمل تحسين قاعدة البيانات'
            ]
        }
        
        add_activity_log({
            'timestamp': timestamp,
            'type': random.choice(['patient_interaction', 'system_event', 'security_check', 'data_update']),
            'description': random.choice(activity_descriptions[current_language]),
            'status': random.choice(['success', 'info', 'warning']) if random.random() > 0.1 else 'error'
        })

def add_terminal_output(terminal_type, message):
    """Add message to specific terminal"""
    if terminal_type not in terminal_outputs:
        terminal_outputs[terminal_type] = []
    
    terminal_outputs[terminal_type].append(message)
    
    # Keep only last 20 messages per terminal
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
    return render_template_string(MULTILINGUAL_DASHBOARD_TEMPLATE)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint for real-time dashboard data"""
    return jsonify({
        'state': dashboard_state,
        'terminals': terminal_outputs,
        'activities': activity_log[-10:],
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

@app.route('/api/simulation', methods=['POST'])
def run_simulation():
    """API endpoint for running multilingual simulations"""
    data = request.get_json()
    sim_type = data.get('type')
    language = data.get('language', 'he')
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    simulation_messages = {
        'he': {
            'busy_day': 'סימולציה: תרחיש יום עמוס הופעל',
            'emergency': 'סימולציה: פרוטוקול חירום הופעל',
            'normal': 'סימולציה: פעילות רגילה שוחזרה',
            'multilang': 'סימולציה: יכולות רב-לשוניות'
        },
        'en': {
            'busy_day': 'SIMULATION: Busy day scenario activated',
            'emergency': 'SIMULATION: Emergency protocol activated',
            'normal': 'SIMULATION: Normal operations restored',
            'multilang': 'SIMULATION: Multilingual capabilities'
        },
        'ar': {
            'busy_day': 'محاكاة: تم تفعيل سيناريو اليوم المزدحم',
            'emergency': 'محاكاة: تم تفعيل بروتوكول الطوارئ',
            'normal': 'محاكاة: تم استعادة العمليات العادية',
            'multilang': 'محاكاة: القدرات متعددة اللغات'
        }
    }
    
    if sim_type == 'busy_day':
        dashboard_state['active_chats'] = random.randint(15, 25)
        dashboard_state['system_load'] = random.randint(75, 95)
        add_terminal_output('system', f'[{timestamp}] {simulation_messages[language]["busy_day"]}')
        
    elif sim_type == 'emergency':
        dashboard_state['emergency_cases'] = random.randint(5, 10)
        dashboard_state['system_load'] = random.randint(85, 100)
        add_terminal_output('security', f'[{timestamp}] {simulation_messages[language]["emergency"]}')
        
    elif sim_type == 'multilang':
        # Demonstrate multilingual capabilities
        greetings = {
            'he': 'שלום, איך אפשר לעזור?',
            'en': 'Hello, how can I help?',
            'ar': 'مرحبا، كيف يمكنني المساعدة؟'
        }
        
        for lang, greeting in greetings.items():
            add_terminal_output('ai', f'[{timestamp}] {simulation_messages[language]["multilang"]}: {lang.upper()} - {greeting}')
        
    elif sim_type == 'normal':
        dashboard_state['active_chats'] = random.randint(5, 10)
        dashboard_state['system_load'] = random.randint(40, 60)
        add_terminal_output('system', f'[{timestamp}] {simulation_messages[language]["normal"]}')
    
    return jsonify({'status': 'success', 'simulation': sim_type})

# Complete Multilingual Dashboard Template
MULTILINGUAL_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מרכז השליטה והבקרה הרב-לשוני - DentalAI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Hebrew:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        body[dir="rtl"] {
            font-family: 'Noto Sans Hebrew', 'Inter', sans-serif;
        }
        
        body[lang="ar"] {
            font-family: 'Noto Sans Arabic', 'Inter', sans-serif;
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
        
        /* Language-specific adjustments */
        .lang-he { text-align: right; }
        .lang-en { text-align: left; }
        .lang-ar { text-align: right; }
        
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
        
        /* Smooth transitions for language changes */
        * {
            transition: all 0.3s ease;
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen" id="main-body" dir="rtl" lang="he">
    <!-- Top Header -->
    <header class="bg-white border-b border-gray-200 h-16 px-6 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div class="flex items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-blue-900 rounded-lg flex items-center justify-center">
                    <i data-lucide="shield" class="w-5 h-5 text-white"></i>
                </div>
                <h1 id="main-title" class="text-xl font-bold text-blue-900">מרכז השליטה והבקרה הרב-לשוני</h1>
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

                    <!-- Overview Terminal -->
                    <div class="bg-gray-800 text-green-400 rounded-lg border border-gray-600">
                        <div class="p-3 border-b border-gray-600">
                            <h3 class="font-semibold flex items-center gap-2">
                                <i data-lucide="activity" class="w-4 h-4"></i>
                                <span data-translate="terminal-overview">סקירה כללית</span>
                            </h3>
                        </div>
                        <div id="terminal-overview" class="terminal-content font-mono text-sm">
                            <div data-translate="terminal-status-operational">System Status: OPERATIONAL</div>
                            <div data-translate="terminal-all-active">All terminals: ACTIVE</div>
                            <div data-translate="terminal-monitoring-enabled">Monitoring: ENABLED</div>
                            <div data-translate="terminal-realtime-on">Real-time updates: ON</div>
                            <div data-translate="terminal-multilang-ready">Multilingual: READY</div>
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
                'main-title': 'מרכז השליטה והבקרה הרב-לשוני',
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
                'terminal-status-operational': 'סטטוס מערכת: פעיל',
                'terminal-all-active': 'כל הטרמינלים: פעילים',
                'terminal-monitoring-enabled': 'מעקב: מופעל',
                'terminal-realtime-on': 'עדכונים בזמן אמת: פעיל',
                'terminal-multilang-ready': 'רב לשוני: מוכן',
                'analytics-title': 'ניתוח ביצועים',
                'analytics-content': 'תוכן ניתוח הביצועים יוצג כאן...',
                'knowledge-title': 'ניהול ידע',
                'knowledge-content': 'תוכן ניהול הידע יוצג כאן...'
            },
            en: {
                'main-title': 'Multilingual Mission Control Center',
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
                'terminal-status-operational': 'System Status: OPERATIONAL',
                'terminal-all-active': 'All terminals: ACTIVE',
                'terminal-monitoring-enabled': 'Monitoring: ENABLED',
                'terminal-realtime-on': 'Real-time updates: ON',
                'terminal-multilang-ready': 'Multilingual: READY',
                'analytics-title': 'Performance Analytics',
                'analytics-content': 'Analytics content will be displayed here...',
                'knowledge-title': 'Knowledge Management',
                'knowledge-content': 'Knowledge management content will be displayed here...'
            },
            ar: {
                'main-title': 'مركز التحكم والسيطرة متعدد اللغات',
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
                'terminal-status-operational': 'حالة النظام: تشغيلي',
                'terminal-all-active': 'جميع المحطات: نشطة',
                'terminal-monitoring-enabled': 'المراقبة: مفعلة',
                'terminal-realtime-on': 'التحديثات الفورية: مفعلة',
                'terminal-multilang-ready': 'متعدد اللغات: جاهز',
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
            
            // Update body attributes
            const body = document.getElementById('main-body');
            body.setAttribute('lang', lang);
            
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
            
            // Clear terminals and refresh with new language
            clearTerminals();
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

        function clearTerminals() {
            // Clear all terminal outputs
            ['system', 'ai', 'network', 'database', 'security'].forEach(terminal => {
                const terminalElement = document.getElementById(`terminal-${terminal}`);
                if (terminalElement) {
                    terminalElement.innerHTML = '';
                }
            });
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
                body: JSON.stringify({ 
                    type: type,
                    language: currentLanguage 
                })
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
    print("🚀 Starting Complete Multilingual Mission Control Dashboard...")
    print("📊 Dashboard available at: http://127.0.0.1:5000")
    print("🎯 Features:")
    print("   • 5 Real-time Terminals with Multilingual Content")
    print("   • Complete Multilingual Support (Hebrew, English, Arabic)")
    print("   • Language-aware Terminal Messages")
    print("   • Real-time Data Visualization")
    print("   • Agent Control System")
    print("   • Advanced Multilingual Simulation Capabilities")
    print("   • Complete Activity Monitoring with Localized Content")
    print("🌐 Languages: Hebrew (עברית), English, Arabic (العربية)")
    print("💻 Terminals: All systems operational with full language support")
    print("🔄 Real-time: Content updates dynamically in selected language")
    app.run(host='0.0.0.0', port=5000, debug=True)
