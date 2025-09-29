#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dental Clinic AI - Final Enhanced Mission Control Dashboard
מרכז השליטה והבקרה המשודרג הסופי למערכת AI של מרפאת השיניים

Final implementation with:
- 5 fully functional terminals with advanced real-time data
- Complete multilingual support with dynamic content
- Enhanced simulation controls with visual feedback
- Advanced real-time features and monitoring
- Professional dashboard with all original functionality restored
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import random
import time
from datetime import datetime, timedelta
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
    'monthly_appointments': 1456,
    'simulation_active': False,
    'simulation_type': None,
    'simulation_start_time': None
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

# Enhanced multilingual terminal messages with more variety
terminal_messages = {
    'he': {
        'system': [
            'שימוש במעבד: {cpu}% | זיכרון: {memory}% | דיסק: {disk}%',
            'קלט/פלט דיסק: {io}MB/s | רשת: {net}MB/s | זמן פעילות: {uptime}h',
            'תהליכים פעילים: {processes} | חוטים: {threads} | משתמשים: {users}',
            'בדיקת תקינות מערכת: {status} | ביצועים: {performance}',
            'סטטוס גיבוי: {backup_status} | גודל: {backup_size}GB',
            'הפעלה מחדש של שירות: {service} נטען בהצלחה',
            'סיבוב לוגים: {log_file} סובב | גודל: {log_size}MB',
            'טמפרטורה: מעבד {cpu_temp}°C | כרטיס גרפי {gpu_temp}°C | מאוורר: {fan_speed}RPM',
            'עדכון מערכת: {update_status} | חבילות: {packages}',
            'מעקב ביצועים: עומס ממוצע {load_avg} | זמן תגובה: {response_time}ms'
        ],
        'ai': [
            'עיבוד שאילתת מטופל: {patient} | שפה: {language}',
            'דיוק AI: {accuracy}% | רמת ביטחון: {confidence}% | מודל: {model_version}',
            'זמן היסק מודל: {inference}ms | תור: {queue} | זיכרון GPU: {gpu_memory}%',
            'שפה זוהתה: {language} | דיוק זיהוי: {lang_confidence}%',
            'סיווג כוונה: {intent} | ביטחון: {intent_confidence}%',
            'נתוני אימון עודכנו: {samples} דגימות חדשות | דיוק: {training_accuracy}%',
            'ביצועי מודל: F1-score {f1_score} | Precision: {precision} | Recall: {recall}',
            'שאילתת בסיס ידע: {kb_query} | תוצאות: {kb_results}',
            'שיחה הושלמה: שיעור הצלחה {success_rate}% | זמן: {conversation_time}s',
            'אופטימיזציה של מודל: {optimization_status} | שיפור: {improvement}%'
        ],
        'network': [
            'שימוש ברוחב פס: {bandwidth}% | זמן השהיה: {latency}ms | אובדן חבילות: {packet_loss}%',
            'חיבורים פעילים: {connections} | מקסימום: {max_concurrent} | תור: {queue_size}',
            'WhatsApp API: {whatsapp_status} | מגבלת קצב: {rate_limit}% | הודעות/דקה: {msg_rate}',
            'שער SMS: {sms_status} | תור: {sms_queue} | הצלחה: {sms_success}%',
            'מערכת טלפון: {active_calls} שיחות | זמן המתנה: {wait_time}s | איכות: {call_quality}',
            'סטטוס CDN: {edge_servers} שרתי קצה | זמן תגובה: {cdn_response}ms',
            'אישורי SSL: {ssl_days} ימים עד חידוש | סטטוס: {ssl_status}',
            'מאזן עומסים: {load_balancer} פעיל | בריאות: {health_status} | חלוקה: {distribution}%',
            'הגבלת קצב API: {api_requests} בקשות/שעה | שגיאות: {api_errors}%',
            'אבטחת רשת: {network_security} | חסימות: {blocked_attempts} ניסיונות'
        ],
        'database': [
            'חיבורים פעילים: {active_connections}/{max_connections} | זמן חיבור ממוצע: {avg_conn_time}ms',
            'זמן ביצוע שאילתה: {query_time}ms | שאילתות איטיות: {slow_queries} | מטמון: {cache_hit}%',
            'רשומת מטופל עודכנה: ID-{patient_id} | טבלה: {table} | שדות: {fields}',
            'תור נקבע: {date} {time}:00 | רופא: {doctor} | טיפול: {treatment}',
            'גיבוי בסיס נתונים: {backup_status} | גודל: {backup_size}MB | זמן: {backup_time}min',
            'אופטימיזציית אינדקס: טבלת {table_name} | שיפור: {improvement}% | זמן: {optimization_time}s',
            'השהיית שכפול: {replication_lag}ms | סטטוס סנכרון: {sync_status} | נתונים: {data_sync}%',
            'יחס פגיעות במטמון: {cache_hit}% | זיכרון: {cache_memory}% | פינויים: {cache_evictions}',
            'יומן עסקאות: {transaction_log} רשומות/דקה | גודל: {log_size}MB',
            'ניטור ביצועים: QPS {qps} | TPS {tps} | זמן נעילה: {lock_time}ms'
        ],
        'security': [
            'סריקת אבטחה: {security_status} | איומים: {threats_found} | זמן סריקה: {scan_time}s',
            'תאימות HIPAA: {hipaa_status} | מסלול ביקורת: {audit_status} | רשומות: {audit_records}',
            'סטטוס הצפנה: {encryption_status} | אלגוריתם: {encryption_algo} | חוזק: {key_strength}bit',
            'יומן גישה: {access_entries} רשומות | כניסות כושלות: {failed_logins} | חסומים: {blocked_users}',
            'סטטוס חומת אש: {firewall_status} | חסומים: {blocked_ips} IPs | כללים: {firewall_rules}',
            'אימות אישור: {cert_status} | פג תוקף: {cert_expiry} ימים | רשות: {cert_authority}',
            'זיהוי חדירה: {intrusion_status} | התראות: {intrusion_alerts} | רמת סיכון: {risk_level}',
            'אנונימיזציה של נתונים: {anonymized_records} רשומות | שיטה: {anonymization_method}',
            'סריקת פגיעויות: {vuln_status} | ציון: {vuln_score}/100 | פגיעויות: {vulnerabilities}',
            'ניטור אבטחה: {security_events} אירועים | חומרה: {severity_high} גבוהה, {severity_low} נמוכה'
        ]
    },
    'en': {
        'system': [
            'CPU Usage: {cpu}% | Memory: {memory}% | Disk: {disk}%',
            'Disk I/O: {io}MB/s | Network: {net}MB/s | Uptime: {uptime}h',
            'Active processes: {processes} | Threads: {threads} | Users: {users}',
            'System health check: {status} | Performance: {performance}',
            'Backup status: {backup_status} | Size: {backup_size}GB',
            'Service restart: {service} reloaded successfully',
            'Log rotation: {log_file} rotated | Size: {log_size}MB',
            'Temperature: CPU {cpu_temp}°C | GPU {gpu_temp}°C | Fan: {fan_speed}RPM',
            'System update: {update_status} | Packages: {packages}',
            'Performance monitoring: Load avg {load_avg} | Response time: {response_time}ms'
        ],
        'ai': [
            'Processing patient query: {patient} | Language: {language}',
            'AI accuracy: {accuracy}% | Confidence: {confidence}% | Model: {model_version}',
            'Model inference time: {inference}ms | Queue: {queue} | GPU memory: {gpu_memory}%',
            'Language detected: {language} | Detection accuracy: {lang_confidence}%',
            'Intent classification: {intent} | Confidence: {intent_confidence}%',
            'Training data updated: {samples} new samples | Accuracy: {training_accuracy}%',
            'Model performance: F1-score {f1_score} | Precision: {precision} | Recall: {recall}',
            'Knowledge base query: {kb_query} | Results: {kb_results}',
            'Conversation completed: Success rate {success_rate}% | Duration: {conversation_time}s',
            'Model optimization: {optimization_status} | Improvement: {improvement}%'
        ],
        'network': [
            'Bandwidth usage: {bandwidth}% | Latency: {latency}ms | Packet loss: {packet_loss}%',
            'Active connections: {connections} | Max concurrent: {max_concurrent} | Queue: {queue_size}',
            'WhatsApp API: {whatsapp_status} | Rate limit: {rate_limit}% | Messages/min: {msg_rate}',
            'SMS gateway: {sms_status} | Queue: {sms_queue} | Success rate: {sms_success}%',
            'Phone system: {active_calls} active calls | Wait time: {wait_time}s | Quality: {call_quality}',
            'CDN status: {edge_servers} edge servers | Response time: {cdn_response}ms',
            'SSL certificates: {ssl_days} days until renewal | Status: {ssl_status}',
            'Load balancer: {load_balancer} active | Health: {health_status} | Distribution: {distribution}%',
            'API rate limiting: {api_requests} requests/hour | Errors: {api_errors}%',
            'Network security: {network_security} | Blocked attempts: {blocked_attempts}'
        ],
        'database': [
            'Active connections: {active_connections}/{max_connections} | Avg conn time: {avg_conn_time}ms',
            'Query execution time: {query_time}ms | Slow queries: {slow_queries} | Cache hit: {cache_hit}%',
            'Patient record updated: ID-{patient_id} | Table: {table} | Fields: {fields}',
            'Appointment scheduled: {date} {time}:00 | Doctor: {doctor} | Treatment: {treatment}',
            'Database backup: {backup_status} | Size: {backup_size}MB | Duration: {backup_time}min',
            'Index optimization: {table_name} table | Improvement: {improvement}% | Time: {optimization_time}s',
            'Replication lag: {replication_lag}ms | Sync status: {sync_status} | Data sync: {data_sync}%',
            'Cache hit ratio: {cache_hit}% | Memory usage: {cache_memory}% | Evictions: {cache_evictions}',
            'Transaction log: {transaction_log} entries/min | Size: {log_size}MB',
            'Performance monitoring: QPS {qps} | TPS {tps} | Lock time: {lock_time}ms'
        ],
        'security': [
            'Security scan: {security_status} | Threats found: {threats_found} | Scan time: {scan_time}s',
            'HIPAA compliance: {hipaa_status} | Audit trail: {audit_status} | Records: {audit_records}',
            'Encryption status: {encryption_status} | Algorithm: {encryption_algo} | Strength: {key_strength}bit',
            'Access log: {access_entries} entries | Failed logins: {failed_logins} | Blocked users: {blocked_users}',
            'Firewall status: {firewall_status} | Blocked IPs: {blocked_ips} | Rules: {firewall_rules}',
            'Certificate validation: {cert_status} | Expires: {cert_expiry} days | Authority: {cert_authority}',
            'Intrusion detection: {intrusion_status} | Alerts: {intrusion_alerts} | Risk level: {risk_level}',
            'Data anonymization: {anonymized_records} records | Method: {anonymization_method}',
            'Vulnerability scan: {vuln_status} | Score: {vuln_score}/100 | Vulnerabilities: {vulnerabilities}',
            'Security monitoring: {security_events} events | High severity: {severity_high}, Low: {severity_low}'
        ]
    },
    'ar': {
        'system': [
            'استخدام المعالج: {cpu}% | الذاكرة: {memory}% | القرص: {disk}%',
            'إدخال/إخراج القرص: {io}MB/s | الشبكة: {net}MB/s | وقت التشغيل: {uptime}h',
            'العمليات النشطة: {processes} | الخيوط: {threads} | المستخدمون: {users}',
            'فحص صحة النظام: {status} | الأداء: {performance}',
            'حالة النسخ الاحتياطي: {backup_status} | الحجم: {backup_size}GB',
            'إعادة تشغيل الخدمة: تم إعادة تحميل {service} بنجاح',
            'دوران السجلات: تم دوران {log_file} | الحجم: {log_size}MB',
            'درجة الحرارة: المعالج {cpu_temp}°C | كرت الرسوميات {gpu_temp}°C | المروحة: {fan_speed}RPM',
            'تحديث النظام: {update_status} | الحزم: {packages}',
            'مراقبة الأداء: متوسط الحمولة {load_avg} | وقت الاستجابة: {response_time}ms'
        ],
        'ai': [
            'معالجة استفسار المريض: {patient} | اللغة: {language}',
            'دقة الذكاء الاصطناعي: {accuracy}% | الثقة: {confidence}% | النموذج: {model_version}',
            'وقت استنتاج النموذج: {inference}ms | الطابور: {queue} | ذاكرة GPU: {gpu_memory}%',
            'اللغة المكتشفة: {language} | دقة الكشف: {lang_confidence}%',
            'تصنيف النية: {intent} | الثقة: {intent_confidence}%',
            'تم تحديث بيانات التدريب: {samples} عينة جديدة | الدقة: {training_accuracy}%',
            'أداء النموذج: F1-score {f1_score} | الدقة: {precision} | الاستدعاء: {recall}',
            'استفسار قاعدة المعرفة: {kb_query} | النتائج: {kb_results}',
            'اكتملت المحادثة: معدل النجاح {success_rate}% | المدة: {conversation_time}s',
            'تحسين النموذج: {optimization_status} | التحسن: {improvement}%'
        ],
        'network': [
            'استخدام عرض النطاق: {bandwidth}% | زمن الاستجابة: {latency}ms | فقدان الحزم: {packet_loss}%',
            'الاتصالات النشطة: {connections} | الحد الأقصى المتزامن: {max_concurrent} | الطابور: {queue_size}',
            'واتساب API: {whatsapp_status} | حد المعدل: {rate_limit}% | رسائل/دقيقة: {msg_rate}',
            'بوابة الرسائل القصيرة: {sms_status} | الطابور: {sms_queue} | معدل النجاح: {sms_success}%',
            'نظام الهاتف: {active_calls} مكالمات نشطة | وقت الانتظار: {wait_time}s | الجودة: {call_quality}',
            'حالة CDN: {edge_servers} خوادم حافة | وقت الاستجابة: {cdn_response}ms',
            'شهادات SSL: {ssl_days} أيام حتى التجديد | الحالة: {ssl_status}',
            'موازن الأحمال: {load_balancer} نشط | الصحة: {health_status} | التوزيع: {distribution}%',
            'تحديد معدل API: {api_requests} طلب/ساعة | الأخطاء: {api_errors}%',
            'أمان الشبكة: {network_security} | المحاولات المحظورة: {blocked_attempts}'
        ],
        'database': [
            'الاتصالات النشطة: {active_connections}/{max_connections} | متوسط وقت الاتصال: {avg_conn_time}ms',
            'وقت تنفيذ الاستعلام: {query_time}ms | الاستعلامات البطيئة: {slow_queries} | إصابة التخزين المؤقت: {cache_hit}%',
            'تم تحديث سجل المريض: ID-{patient_id} | الجدول: {table} | الحقول: {fields}',
            'تم جدولة الموعد: {date} {time}:00 | الطبيب: {doctor} | العلاج: {treatment}',
            'نسخ احتياطي لقاعدة البيانات: {backup_status} | الحجم: {backup_size}MB | المدة: {backup_time}min',
            'تحسين الفهرس: جدول {table_name} | التحسن: {improvement}% | الوقت: {optimization_time}s',
            'تأخير النسخ المتماثل: {replication_lag}ms | حالة المزامنة: {sync_status} | مزامنة البيانات: {data_sync}%',
            'نسبة إصابة التخزين المؤقت: {cache_hit}% | استخدام الذاكرة: {cache_memory}% | الطرد: {cache_evictions}',
            'سجل المعاملات: {transaction_log} إدخال/دقيقة | الحجم: {log_size}MB',
            'مراقبة الأداء: QPS {qps} | TPS {tps} | وقت القفل: {lock_time}ms'
        ],
        'security': [
            'فحص الأمان: {security_status} | التهديدات الموجودة: {threats_found} | وقت الفحص: {scan_time}s',
            'امتثال HIPAA: {hipaa_status} | مسار التدقيق: {audit_status} | السجلات: {audit_records}',
            'حالة التشفير: {encryption_status} | الخوارزمية: {encryption_algo} | القوة: {key_strength}bit',
            'سجل الوصول: {access_entries} إدخال | تسجيلات دخول فاشلة: {failed_logins} | مستخدمون محظورون: {blocked_users}',
            'حالة جدار الحماية: {firewall_status} | عناوين IP محظورة: {blocked_ips} | القواعد: {firewall_rules}',
            'التحقق من الشهادة: {cert_status} | ينتهي: {cert_expiry} أيام | السلطة: {cert_authority}',
            'كشف التسلل: {intrusion_status} | التنبيهات: {intrusion_alerts} | مستوى المخاطر: {risk_level}',
            'إخفاء هوية البيانات: {anonymized_records} سجل | الطريقة: {anonymization_method}',
            'فحص الثغرات: {vuln_status} | النتيجة: {vuln_score}/100 | الثغرات: {vulnerabilities}',
            'مراقبة الأمان: {security_events} حدث | خطورة عالية: {severity_high}، منخفضة: {severity_low}'
        ]
    }
}

# Enhanced multilingual data with more variety
multilingual_data = {
    'patient_names': {
        'he': ['דוד כהן', 'שרה לוי', 'מיכל ברק', 'יוסף אברהם', 'רחל גולדברג', 'אבי רוזן', 'תמר שמיר', 'עמית פרידמן'],
        'en': ['David Cohen', 'Sarah Levy', 'Michael Barak', 'Joseph Abraham', 'Rachel Goldberg', 'Avi Rosen', 'Tamar Shamir', 'Amit Friedman'],
        'ar': ['داود كوهين', 'سارة ليفي', 'ميخائيل باراك', 'يوسف إبراهيم', 'راحيل غولدبرغ', 'آفي روزن', 'تمار شمير', 'عميت فريدمان']
    },
    'intents': {
        'he': ['קביעת תור', 'בקשת מידע', 'חירום', 'תלונה', 'ביטול תור', 'שינוי תור', 'בירור מחיר', 'תזכורת'],
        'en': ['appointment_booking', 'information_request', 'emergency', 'complaint', 'cancellation', 'reschedule', 'price_inquiry', 'reminder'],
        'ar': ['حجز موعد', 'طلب معلومات', 'طوارئ', 'شكوى', 'إلغاء موعد', 'إعادة جدولة', 'استفسار سعر', 'تذكير']
    },
    'treatments': {
        'he': ['ניקוי שיניים', 'טיפול שורש', 'כתר', 'השתלה', 'יישור שיניים', 'הלבנה', 'עקירה', 'סתימה'],
        'en': ['teeth_cleaning', 'root_canal', 'crown', 'implant', 'orthodontics', 'whitening', 'extraction', 'filling'],
        'ar': ['تنظيف الأسنان', 'علاج الجذر', 'تاج', 'زراعة', 'تقويم الأسنان', 'تبييض', 'خلع', 'حشو']
    },
    'doctors': {
        'he': ['ד"ר כהן', 'ד"ר לוי', 'ד"ר ברק', 'ד"ר אברהם'],
        'en': ['Dr. Cohen', 'Dr. Levy', 'Dr. Barak', 'Dr. Abraham'],
        'ar': ['د. كوهين', 'د. ليفي', 'د. باراك', 'د. إبراهيم']
    }
}

def get_localized_message(terminal_type, language, **kwargs):
    """Get a localized terminal message with dynamic values"""
    if language not in terminal_messages or terminal_type not in terminal_messages[language]:
        language = 'en'  # Fallback to English
    
    messages = terminal_messages[language][terminal_type]
    template = random.choice(messages)
    
    # Generate realistic dynamic values
    dynamic_values = generate_dynamic_values(terminal_type, language)
    dynamic_values.update(kwargs)
    
    try:
        return template.format(**dynamic_values)
    except KeyError:
        return template

def generate_dynamic_values(terminal_type, language):
    """Generate realistic dynamic values for terminal messages"""
    values = {}
    
    if terminal_type == 'system':
        values.update({
            'cpu': dashboard_state['cpu_usage'],
            'memory': dashboard_state['memory_usage'],
            'disk': dashboard_state['disk_usage'],
            'io': random.randint(10, 50),
            'net': random.randint(5, 25),
            'uptime': random.randint(24, 720),
            'processes': random.randint(120, 180),
            'threads': random.randint(800, 1200),
            'users': random.randint(5, 15),
            'status': 'OK' if dashboard_state['system_load'] < 80 else 'HIGH_LOAD',
            'performance': random.choice(['Excellent', 'Good', 'Fair']),
            'backup_status': random.choice(['Completed', 'In Progress', 'Scheduled']),
            'backup_size': round(random.uniform(0.5, 5.0), 1),
            'service': random.choice(['nginx', 'postgresql', 'redis', 'elasticsearch']),
            'log_file': random.choice(['/var/log/dental-ai.log', '/var/log/system.log', '/var/log/access.log']),
            'log_size': random.randint(10, 100),
            'cpu_temp': random.randint(45, 65),
            'gpu_temp': random.randint(35, 55),
            'fan_speed': random.randint(1200, 2500),
            'update_status': random.choice(['Available', 'Installing', 'Completed']),
            'packages': random.randint(5, 50),
            'load_avg': round(random.uniform(0.5, 2.0), 2),
            'response_time': random.randint(50, 200)
        })
    
    elif terminal_type == 'ai':
        values.update({
            'patient': random.choice(multilingual_data['patient_names'][language]),
            'language': language.title(),
            'accuracy': dashboard_state['ai_accuracy'],
            'confidence': random.randint(85, 99),
            'model_version': f'v{random.randint(1, 5)}.{random.randint(0, 9)}',
            'inference': random.randint(50, 200),
            'queue': random.randint(0, 5),
            'gpu_memory': random.randint(60, 90),
            'lang_confidence': random.randint(90, 99),
            'intent': random.choice(multilingual_data['intents'][language]),
            'intent_confidence': random.randint(80, 95),
            'samples': random.randint(50, 200),
            'training_accuracy': round(random.uniform(92.0, 98.0), 1),
            'f1_score': f"{random.uniform(0.92, 0.98):.3f}",
            'precision': f"{random.uniform(0.90, 0.97):.3f}",
            'recall': f"{random.uniform(0.88, 0.96):.3f}",
            'kb_query': random.choice(['treatment_prices', 'doctor_schedule', 'clinic_hours']),
            'kb_results': random.randint(5, 25),
            'success_rate': random.randint(85, 100),
            'conversation_time': random.randint(60, 300),
            'optimization_status': random.choice(['Running', 'Completed', 'Scheduled']),
            'improvement': round(random.uniform(1.0, 5.0), 1)
        })
    
    elif terminal_type == 'network':
        values.update({
            'bandwidth': random.randint(20, 80),
            'latency': dashboard_state['network_latency'],
            'packet_loss': round(random.uniform(0.0, 0.5), 2),
            'connections': dashboard_state['active_chats'],
            'max_concurrent': random.randint(50, 100),
            'queue_size': random.randint(0, 10),
            'whatsapp_status': random.choice(['Connected', 'Reconnecting', 'Degraded']),
            'rate_limit': random.randint(80, 100),
            'msg_rate': random.randint(50, 200),
            'sms_status': random.choice(['Operational', 'Degraded', 'Maintenance']),
            'sms_queue': random.randint(0, 15),
            'sms_success': random.randint(95, 100),
            'active_calls': random.randint(2, 8),
            'wait_time': random.randint(30, 180),
            'call_quality': random.choice(['Excellent', 'Good', 'Fair']),
            'edge_servers': random.randint(15, 25),
            'cdn_response': random.randint(20, 100),
            'ssl_days': random.randint(5, 365),
            'ssl_status': random.choice(['Valid', 'Expiring', 'Renewed']),
            'load_balancer': random.choice(['Primary', 'Secondary', 'Backup']),
            'health_status': random.choice(['Healthy', 'Warning', 'Critical']),
            'distribution': random.randint(40, 60),
            'api_requests': random.randint(1000, 5000),
            'api_errors': round(random.uniform(0.1, 2.0), 1),
            'network_security': random.choice(['Secure', 'Monitoring', 'Alert']),
            'blocked_attempts': random.randint(10, 100)
        })
    
    elif terminal_type == 'database':
        values.update({
            'active_connections': dashboard_state['database_connections'],
            'max_connections': random.randint(80, 120),
            'avg_conn_time': random.randint(10, 50),
            'query_time': random.randint(5, 25),
            'slow_queries': random.randint(0, 3),
            'cache_hit': random.randint(85, 98),
            'patient_id': random.randint(1000, 9999),
            'table': random.choice(['patients', 'appointments', 'treatments']),
            'fields': random.randint(3, 8),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': random.randint(9, 17),
            'doctor': random.choice(multilingual_data['doctors'][language]),
            'treatment': random.choice(multilingual_data['treatments'][language]),
            'backup_status': random.choice(['Completed', 'In Progress', 'Failed']),
            'backup_size': random.randint(500, 2000),
            'backup_time': random.randint(5, 30),
            'table_name': random.choice(['appointments', 'patients', 'treatments']),
            'improvement': round(random.uniform(5.0, 25.0), 1),
            'optimization_time': random.randint(10, 120),
            'replication_lag': random.randint(0, 5),
            'sync_status': random.choice(['OK', 'Warning', 'Error']),
            'data_sync': random.randint(95, 100),
            'cache_memory': random.randint(60, 90),
            'cache_evictions': random.randint(0, 10),
            'transaction_log': random.randint(100, 500),
            'log_size': random.randint(50, 200),
            'qps': random.randint(100, 500),
            'tps': random.randint(50, 200),
            'lock_time': random.randint(1, 10)
        })
    
    elif terminal_type == 'security':
        values.update({
            'security_status': random.choice(['Clean', 'Warning', 'Threat Detected']),
            'threats_found': random.randint(0, 3),
            'scan_time': random.randint(30, 300),
            'hipaa_status': random.choice(['Compliant', 'Warning', 'Non-Compliant']),
            'audit_status': random.choice(['Active', 'Reviewing', 'Complete']),
            'audit_records': random.randint(100, 1000),
            'encryption_status': random.choice(['Active', 'Updating', 'Error']),
            'encryption_algo': random.choice(['AES-256', 'RSA-2048', 'ChaCha20']),
            'key_strength': random.choice([256, 512, 1024, 2048]),
            'access_entries': random.randint(50, 200),
            'failed_logins': random.randint(0, 5),
            'blocked_users': random.randint(0, 10),
            'firewall_status': random.choice(['Active', 'Updating', 'Disabled']),
            'blocked_ips': random.randint(10, 100),
            'firewall_rules': random.randint(50, 200),
            'cert_status': random.choice(['Valid', 'Expiring', 'Invalid']),
            'cert_expiry': random.randint(1, 365),
            'cert_authority': random.choice(['Let\'s Encrypt', 'DigiCert', 'Comodo']),
            'intrusion_status': random.choice(['Clean', 'Monitoring', 'Alert']),
            'intrusion_alerts': random.randint(0, 5),
            'risk_level': random.choice(['Low', 'Medium', 'High']),
            'anonymized_records': random.randint(50, 200),
            'anonymization_method': random.choice(['Hashing', 'Masking', 'Encryption']),
            'vuln_status': random.choice(['Completed', 'Running', 'Scheduled']),
            'vuln_score': random.randint(85, 100),
            'vulnerabilities': random.randint(0, 5),
            'security_events': random.randint(10, 100),
            'severity_high': random.randint(0, 3),
            'severity_low': random.randint(5, 20)
        })
    
    return values

def simulate_real_time_data():
    """Enhanced real-time data simulation with more sophisticated patterns"""
    current_language = 'he'
    
    while True:
        time.sleep(1.5)  # Faster updates for more dynamic feel
        
        # Update core metrics with realistic patterns
        dashboard_state['active_chats'] = random.randint(5, 15)
        dashboard_state['system_load'] = random.randint(45, 85)
        dashboard_state['cpu_usage'] = random.randint(30, 70)
        dashboard_state['memory_usage'] = random.randint(60, 85)
        dashboard_state['disk_usage'] = random.randint(65, 75)
        dashboard_state['avg_handling_time'] = random.randint(120, 240)
        dashboard_state['database_connections'] = random.randint(30, 60)
        dashboard_state['network_latency'] = random.randint(15, 45)
        dashboard_state['ai_accuracy'] = round(random.uniform(94.0, 98.5), 1)
        dashboard_state['last_activity'] = datetime.now().isoformat()
        
        # Simulate simulation effects
        if dashboard_state['simulation_active']:
            apply_simulation_effects()
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Generate messages for current language
        for terminal_type in ['system', 'ai', 'network', 'database', 'security']:
            message = get_localized_message(terminal_type, current_language)
            add_terminal_output(terminal_type, f'[{timestamp}] {message}')
        
        # Add activity log entries
        activity_descriptions = {
            'he': [
                'תור מטופל נקבע בהצלחה',
                'מודל AI עיבד שאילתה רב-לשונית',
                'גיבוי מערכת הושלם',
                'סריקת אבטחה עברה בהצלחה',
                'אופטימיזציה של בסיס נתונים הושלמה',
                'עדכון מערכת הותקן',
                'חיבור חדש של מטופל',
                'תזכורת נשלחה בהצלחה'
            ],
            'en': [
                'Patient appointment scheduled successfully',
                'AI model processed multilingual query',
                'System backup completed',
                'Security scan passed',
                'Database optimization completed',
                'System update installed',
                'New patient connection established',
                'Reminder sent successfully'
            ],
            'ar': [
                'تم جدولة موعد المريض بنجاح',
                'نموذج الذكاء الاصطناعي عالج استفسار متعدد اللغات',
                'اكتمل النسخ الاحتياطي للنظام',
                'نجح فحص الأمان',
                'اكتمل تحسين قاعدة البيانات',
                'تم تثبيت تحديث النظام',
                'تم إنشاء اتصال مريض جديد',
                'تم إرسال التذكير بنجاح'
            ]
        }
        
        add_activity_log({
            'timestamp': timestamp,
            'type': random.choice(['patient_interaction', 'system_event', 'security_check', 'data_update', 'ai_processing']),
            'description': random.choice(activity_descriptions[current_language]),
            'status': random.choice(['success', 'info', 'warning']) if random.random() > 0.05 else 'error'
        })

def apply_simulation_effects():
    """Apply effects based on active simulation"""
    sim_type = dashboard_state['simulation_type']
    
    if sim_type == 'busy_day':
        dashboard_state['active_chats'] = random.randint(15, 25)
        dashboard_state['system_load'] = random.randint(75, 95)
        dashboard_state['cpu_usage'] = random.randint(60, 85)
        dashboard_state['memory_usage'] = random.randint(75, 90)
        
    elif sim_type == 'emergency':
        dashboard_state['emergency_cases'] = random.randint(5, 10)
        dashboard_state['system_load'] = random.randint(85, 100)
        dashboard_state['active_chats'] = random.randint(20, 30)
        dashboard_state['security_alerts'] = random.randint(1, 5)
        
    elif sim_type == 'normal':
        dashboard_state['active_chats'] = random.randint(5, 10)
        dashboard_state['system_load'] = random.randint(40, 60)
        dashboard_state['cpu_usage'] = random.randint(30, 50)
        dashboard_state['emergency_cases'] = random.randint(0, 2)

def add_terminal_output(terminal_type, message):
    """Add message to specific terminal"""
    if terminal_type not in terminal_outputs:
        terminal_outputs[terminal_type] = []
    
    terminal_outputs[terminal_type].append(message)
    
    # Keep only last 25 messages per terminal
    if len(terminal_outputs[terminal_type]) > 25:
        terminal_outputs[terminal_type].pop(0)

def add_activity_log(activity):
    """Add activity to the global activity log"""
    activity['id'] = str(uuid.uuid4())
    activity_log.append(activity)
    
    # Keep only last 100 activities
    if len(activity_log) > 100:
        activity_log.pop(0)

# Start background simulation
simulation_thread = threading.Thread(target=simulate_real_time_data, daemon=True)
simulation_thread.start()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template_string(FINAL_DASHBOARD_TEMPLATE)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint for real-time dashboard data"""
    return jsonify({
        'state': dashboard_state,
        'terminals': terminal_outputs,
        'activities': activity_log[-15:],  # Last 15 activities
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
    """API endpoint for running enhanced simulations"""
    data = request.get_json()
    sim_type = data.get('type')
    language = data.get('language', 'he')
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Start simulation
    dashboard_state['simulation_active'] = True
    dashboard_state['simulation_type'] = sim_type
    dashboard_state['simulation_start_time'] = datetime.now().isoformat()
    
    simulation_messages = {
        'he': {
            'busy_day': 'סימולציה: תרחיש יום עמוס הופעל - עומס גבוה צפוי',
            'emergency': 'סימולציה: פרוטוקול חירום הופעל - כל המערכות במצב כוננות',
            'normal': 'סימולציה: פעילות רגילה שוחזרה - מערכות חזרו לנורמה',
            'multilang': 'סימולציה: יכולות רב-לשוניות - בדיקת תמיכה בשפות'
        },
        'en': {
            'busy_day': 'SIMULATION: Busy day scenario activated - high load expected',
            'emergency': 'SIMULATION: Emergency protocol activated - all systems on standby',
            'normal': 'SIMULATION: Normal operations restored - systems back to normal',
            'multilang': 'SIMULATION: Multilingual capabilities - testing language support'
        },
        'ar': {
            'busy_day': 'محاكاة: تم تفعيل سيناريو اليوم المزدحم - متوقع حمولة عالية',
            'emergency': 'محاكاة: تم تفعيل بروتوكول الطوارئ - جميع الأنظمة في حالة استعداد',
            'normal': 'محاكاة: تم استعادة العمليات العادية - عادت الأنظمة إلى الوضع الطبيعي',
            'multilang': 'محاكاة: القدرات متعددة اللغات - اختبار دعم اللغات'
        }
    }
    
    # Add simulation messages to appropriate terminals
    if sim_type == 'busy_day':
        add_terminal_output('system', f'[{timestamp}] {simulation_messages[language]["busy_day"]}')
        add_terminal_output('ai', f'[{timestamp}] AI: Processing increased patient load')
        
    elif sim_type == 'emergency':
        add_terminal_output('security', f'[{timestamp}] {simulation_messages[language]["emergency"]}')
        add_terminal_output('system', f'[{timestamp}] ALERT: Emergency mode - all systems alert')
        
    elif sim_type == 'multilang':
        greetings = {
            'he': 'שלום, איך אפשר לעזור?',
            'en': 'Hello, how can I help?',
            'ar': 'مرحبا، كيف يمكنني المساعدة؟'
        }
        
        for lang, greeting in greetings.items():
            add_terminal_output('ai', f'[{timestamp}] {simulation_messages[language]["multilang"]}: {lang.upper()} - {greeting}')
        
    elif sim_type == 'normal':
        add_terminal_output('system', f'[{timestamp}] {simulation_messages[language]["normal"]}')
        # Auto-stop simulation after normal is selected
        dashboard_state['simulation_active'] = False
        dashboard_state['simulation_type'] = None
    
    # Schedule simulation auto-stop (except for normal)
    if sim_type != 'normal':
        def stop_simulation():
            time.sleep(30)  # Run simulation for 30 seconds
            dashboard_state['simulation_active'] = False
            dashboard_state['simulation_type'] = None
            add_terminal_output('system', f'[{datetime.now().strftime("%H:%M:%S")}] Simulation ended automatically')
        
        threading.Thread(target=stop_simulation, daemon=True).start()
    
    return jsonify({'status': 'success', 'simulation': sim_type, 'active': dashboard_state['simulation_active']})

# Final Enhanced Dashboard Template
FINAL_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מרכז השליטה והבקרה הסופי - DentalAI</title>
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
        
        /* Enhanced Terminal Styles */
        .terminal-system { 
            font-family: 'Courier New', monospace; 
            color: #00ff00; 
            background: linear-gradient(135deg, #001100 0%, #002200 100%);
            border: 1px solid #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        .terminal-ai { 
            font-family: 'Courier New', monospace; 
            color: #00bfff; 
            background: linear-gradient(135deg, #001122 0%, #002244 100%);
            border: 1px solid #00bfff;
            box-shadow: 0 0 20px rgba(0, 191, 255, 0.3);
        }
        .terminal-network { 
            font-family: 'Courier New', monospace; 
            color: #ff6600; 
            background: linear-gradient(135deg, #220011 0%, #440022 100%);
            border: 1px solid #ff6600;
            box-shadow: 0 0 20px rgba(255, 102, 0, 0.3);
        }
        .terminal-database { 
            font-family: 'Courier New', monospace; 
            color: #ffff00; 
            background: linear-gradient(135deg, #112200 0%, #224400 100%);
            border: 1px solid #ffff00;
            box-shadow: 0 0 20px rgba(255, 255, 0, 0.3);
        }
        .terminal-security { 
            font-family: 'Courier New', monospace; 
            color: #ff0066; 
            background: linear-gradient(135deg, #220022 0%, #440044 100%);
            border: 1px solid #ff0066;
            box-shadow: 0 0 20px rgba(255, 0, 102, 0.3);
        }
        
        .terminal-content {
            height: 220px;
            overflow-y: auto;
            padding: 12px;
            font-size: 11px;
            line-height: 1.3;
        }
        
        /* Enhanced Animations */
        .pulse-dot { animation: pulse 2s infinite; }
        .slide-in { animation: slideIn 0.3s ease-out; }
        .fade-in { animation: fadeIn 0.5s ease-out; }
        .bounce-in { animation: bounceIn 0.6s ease-out; }
        
        @keyframes pulse { 
            0%, 100% { opacity: 1; transform: scale(1); } 
            50% { opacity: 0.7; transform: scale(1.1); } 
        }
        @keyframes slideIn { 
            from { transform: translateX(100%); opacity: 0; } 
            to { transform: translateX(0); opacity: 1; } 
        }
        @keyframes fadeIn { 
            from { opacity: 0; transform: translateY(10px); } 
            to { opacity: 1; transform: translateY(0); } 
        }
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        /* Simulation Active Styles */
        .simulation-active {
            animation: simulationPulse 2s infinite;
            border: 2px solid #ff6b35;
        }
        
        @keyframes simulationPulse {
            0%, 100% { box-shadow: 0 0 5px rgba(255, 107, 53, 0.5); }
            50% { box-shadow: 0 0 20px rgba(255, 107, 53, 0.8); }
        }
        
        /* Enhanced Button Styles */
        .btn-enhanced {
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .btn-enhanced:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .btn-enhanced:active {
            transform: translateY(0);
        }
        
        /* Status Indicators */
        .status-excellent { color: #10b981; }
        .status-good { color: #3b82f6; }
        .status-warning { color: #f59e0b; }
        .status-critical { color: #ef4444; }
        
        /* Scrollbar styling */
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
        .terminal-content::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.5);
        }
        
        /* Language direction support */
        .rtl { direction: rtl; }
        .ltr { direction: ltr; }
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
                <h1 id="main-title" class="text-xl font-bold text-blue-900">מרכז השליטה והבקרה הסופי</h1>
            </div>
            
            <!-- Agent Status -->
            <div class="flex items-center gap-2 bg-gray-100 px-3 py-1 rounded-full">
                <div id="agent-status-dot" class="w-3 h-3 rounded-full bg-green-500 pulse-dot"></div>
                <span id="agent-status-text" class="text-sm font-medium text-blue-900">סוכן פעיל</span>
            </div>
            
            <!-- Simulation Status -->
            <div id="simulation-status" class="hidden flex items-center gap-2 bg-orange-100 px-3 py-1 rounded-full">
                <div class="w-3 h-3 rounded-full bg-orange-500 pulse-dot"></div>
                <span class="text-sm font-medium text-orange-700">סימולציה פעילה</span>
            </div>
            
            <!-- Language Selector -->
            <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
                <button onclick="setLanguage('he')" class="language-btn px-3 py-1 text-sm rounded bg-blue-900 text-white btn-enhanced" data-lang="he">עב</button>
                <button onclick="setLanguage('en')" class="language-btn px-3 py-1 text-sm rounded text-gray-600 btn-enhanced" data-lang="en">EN</button>
                <button onclick="setLanguage('ar')" class="language-btn px-3 py-1 text-sm rounded text-gray-600 btn-enhanced" data-lang="ar">عر</button>
            </div>
        </div>

        <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg btn-enhanced">
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
                    <button onclick="setActiveTab('overview')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right bg-blue-800 border-r-4 border-r-blue-400 btn-enhanced" data-tab="overview">
                        <i data-lucide="activity" class="w-5 h-5"></i>
                        <span data-translate="nav-overview">סקירה כללית</span>
                    </button>
                    
                    <button onclick="setActiveTab('terminals')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800 btn-enhanced" data-tab="terminals">
                        <i data-lucide="terminal" class="w-5 h-5"></i>
                        <span data-translate="nav-terminals">טרמינלים</span>
                    </button>
                    
                    <button onclick="setActiveTab('analytics')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800 btn-enhanced" data-tab="analytics">
                        <i data-lucide="bar-chart-3" class="w-5 h-5"></i>
                        <span data-translate="nav-analytics">ניתוח ביצועים</span>
                    </button>
                    
                    <button onclick="setActiveTab('knowledge')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right hover:bg-blue-800 btn-enhanced" data-tab="knowledge">
                        <i data-lucide="brain" class="w-5 h-5"></i>
                        <span data-translate="nav-knowledge">ניהול ידע</span>
                    </button>
                </div>
                
                <!-- Agent Controls -->
                <div class="mt-8 p-4 bg-blue-800 rounded-lg">
                    <h3 class="font-semibold mb-3" data-translate="agent-controls">בקרת סוכן</h3>
                    <div class="space-y-2">
                        <button onclick="controlAgent('pause')" class="w-full px-3 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-sm btn-enhanced">
                            <i data-lucide="pause" class="w-4 h-4 inline mr-2"></i>
                            <span data-translate="agent-pause">השהה</span>
                        </button>
                        <button onclick="controlAgent('resume')" class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm btn-enhanced">
                            <i data-lucide="play" class="w-4 h-4 inline mr-2"></i>
                            <span data-translate="agent-resume">המשך</span>
                        </button>
                        <button onclick="controlAgent('monitor')" class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm btn-enhanced">
                            <i data-lucide="eye" class="w-4 h-4 inline mr-2"></i>
                            <span data-translate="agent-monitor">מעקב</span>
                        </button>
                    </div>
                </div>
                
                <!-- Enhanced Simulation Controls -->
                <div class="mt-4 p-4 bg-blue-800 rounded-lg">
                    <h3 class="font-semibold mb-3" data-translate="simulation-title">בקרת סימולציות</h3>
                    <div class="space-y-2">
                        <button onclick="runSimulation('busy_day')" class="simulation-btn w-full px-3 py-2 bg-orange-600 hover:bg-orange-700 rounded text-sm btn-enhanced" data-translate="sim-busy" data-sim="busy_day">
                            <i data-lucide="trending-up" class="w-4 h-4 inline mr-2"></i>
                            יום עמוס
                        </button>
                        <button onclick="runSimulation('emergency')" class="simulation-btn w-full px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-sm btn-enhanced" data-translate="sim-emergency" data-sim="emergency">
                            <i data-lucide="alert-triangle" class="w-4 h-4 inline mr-2"></i>
                            מצב חירום
                        </button>
                        <button onclick="runSimulation('normal')" class="simulation-btn w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm btn-enhanced" data-translate="sim-normal" data-sim="normal">
                            <i data-lucide="check-circle" class="w-4 h-4 inline mr-2"></i>
                            יום רגיל
                        </button>
                        <button onclick="runSimulation('multilang')" class="simulation-btn w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm btn-enhanced" data-translate="sim-multilang" data-sim="multilang">
                            <i data-lucide="globe" class="w-4 h-4 inline mr-2"></i>
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
                    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 fade-in">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600" data-translate="kpi-appointments">תורים היום</p>
                                <p id="appointments-today" class="text-xl font-bold text-blue-900">56</p>
                                <p class="text-sm text-green-600">+12%</p>
                            </div>
                            <i data-lucide="calendar" class="w-8 h-8 text-blue-600"></i>
                        </div>
                    </div>
                    
                    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 fade-in">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600" data-translate="kpi-success">שיעור הצלחה</p>
                                <p id="success-rate" class="text-xl font-bold text-blue-900">98.5%</p>
                                <p class="text-sm text-green-600">+0.2%</p>
                            </div>
                            <i data-lucide="check-circle" class="w-8 h-8 text-green-600"></i>
                        </div>
                    </div>
                    
                    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 fade-in">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600" data-translate="kpi-handling">זמן טיפול</p>
                                <p id="avg-handling-time" class="text-xl font-bold text-blue-900">3:05</p>
                                <p class="text-sm text-green-600">-15s</p>
                            </div>
                            <i data-lucide="clock" class="w-8 h-8 text-yellow-600"></i>
                        </div>
                    </div>
                    
                    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 fade-in">
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
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 fade-in">
                        <h3 class="text-lg font-semibold mb-4" data-translate="system-status">סטטוס מערכת</h3>
                        <div class="space-y-4">
                            <div class="flex justify-between items-center">
                                <span data-translate="status-uptime">זמינות מערכת</span>
                                <span id="system-uptime" class="font-semibold status-excellent">98.5%</span>
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
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 fade-in">
                        <h3 class="text-lg font-semibold mb-4" data-translate="ai-metrics">מדדי AI</h3>
                        <div class="space-y-4">
                            <div class="flex justify-between items-center">
                                <span data-translate="ai-accuracy">דיוק AI</span>
                                <span id="ai-accuracy" class="font-semibold status-excellent">96.2%</span>
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
                <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 fade-in">
                    <h3 class="text-lg font-semibold mb-4" data-translate="recent-activity">פעילות אחרונה</h3>
                    <div id="activity-log" class="space-y-2 max-h-64 overflow-y-auto">
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
                    <div class="terminal-system rounded-lg bounce-in">
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
                    <div class="terminal-ai rounded-lg bounce-in">
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
                    <div class="terminal-network rounded-lg bounce-in">
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
                    <div class="terminal-database rounded-lg bounce-in">
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
                    <div class="terminal-security rounded-lg bounce-in">
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
                    <div class="bg-gray-800 text-green-400 rounded-lg border border-gray-600 bounce-in">
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
                            <div data-translate="terminal-simulation-ready">Simulation: READY</div>
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
        let simulationActive = false;

        // Complete translations for all content
        const translations = {
            he: {
                'main-title': 'מרכז השליטה והבקרה הסופי',
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
                'terminal-simulation-ready': 'סימולציה: מוכנה',
                'analytics-title': 'ניתוח ביצועים',
                'analytics-content': 'תוכן ניתוח הביצועים יוצג כאן...',
                'knowledge-title': 'ניהול ידע',
                'knowledge-content': 'תוכן ניהול הידע יוצג כאן...'
            },
            en: {
                'main-title': 'Final Mission Control Center',
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
                'terminal-simulation-ready': 'Simulation: READY',
                'analytics-title': 'Performance Analytics',
                'analytics-content': 'Analytics content will be displayed here...',
                'knowledge-title': 'Knowledge Management',
                'knowledge-content': 'Knowledge management content will be displayed here...'
            },
            ar: {
                'main-title': 'مركز التحكم والسيطرة النهائي',
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
                'terminal-simulation-ready': 'المحاكاة: جاهزة',
                'analytics-title': 'تحليل الأداء',
                'analytics-content': 'سيتم عرض محتوى التحليلات هنا...',
                'knowledge-title': 'إدارة المعرفة',
                'knowledge-content': 'سيتم عرض محتوى إدارة المعرفة هنا...'
            }
        };

        // Enhanced language switching
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

        // Enhanced tab switching
        function setActiveTab(tab) {
            currentTab = tab;
            
            // Update navigation with animation
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('bg-blue-800', 'border-r-4', 'border-r-blue-400');
                btn.classList.add('hover:bg-blue-800');
            });
            
            const activeBtn = document.querySelector(`[data-tab="${tab}"]`);
            activeBtn.classList.add('bg-blue-800', 'border-r-4', 'border-r-blue-400');
            activeBtn.classList.remove('hover:bg-blue-800');
            
            // Update content with fade effect
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            
            const activeTab = document.getElementById(`${tab}-tab`);
            activeTab.classList.remove('hidden');
            activeTab.classList.add('fade-in');
        }

        // Enhanced agent control
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
                
                // Update agent status dot with animation
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
                
                // Add new status color with animation
                dot.classList.add(statusColors[data.new_status] || 'bg-gray-500');
                dot.classList.add('bounce-in');
                
                // Update status text
                updateLanguageContent();
                
                // Remove animation class after animation completes
                setTimeout(() => {
                    dot.classList.remove('bounce-in');
                }, 600);
            })
            .catch(error => {
                console.error('Error controlling agent:', error);
            });
        }

        // Enhanced simulation controls
        function runSimulation(type) {
            // Visual feedback for button press
            const button = document.querySelector(`[data-sim="${type}"]`);
            button.classList.add('simulation-active');
            
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
                
                // Update simulation status
                simulationActive = data.active;
                updateSimulationStatus();
                
                // Remove button animation after delay
                setTimeout(() => {
                    button.classList.remove('simulation-active');
                }, 3000);
            })
            .catch(error => {
                console.error('Error running simulation:', error);
                button.classList.remove('simulation-active');
            });
        }

        function updateSimulationStatus() {
            const statusElement = document.getElementById('simulation-status');
            if (simulationActive) {
                statusElement.classList.remove('hidden');
                statusElement.classList.add('bounce-in');
            } else {
                statusElement.classList.add('hidden');
                statusElement.classList.remove('bounce-in');
            }
        }

        // Enhanced dashboard updates
        function updateDashboard() {
            if (dashboardData.state) {
                // Update KPI cards with status colors
                document.getElementById('appointments-today').textContent = dashboardData.state.appointments_today;
                document.getElementById('success-rate').textContent = dashboardData.state.system_uptime.toFixed(1) + '%';
                document.getElementById('avg-handling-time').textContent = 
                    Math.floor(dashboardData.state.avg_handling_time / 60) + ':' + 
                    (dashboardData.state.avg_handling_time % 60).toString().padStart(2, '0');
                document.getElementById('active-chats').textContent = dashboardData.state.active_chats;
                
                // Update system status with color coding
                const systemLoad = dashboardData.state.system_load;
                const loadElement = document.getElementById('system-load');
                loadElement.textContent = systemLoad + '%';
                
                // Apply status colors
                loadElement.className = 'font-semibold ' + 
                    (systemLoad < 60 ? 'status-excellent' : 
                     systemLoad < 80 ? 'status-good' : 
                     systemLoad < 90 ? 'status-warning' : 'status-critical');
                
                document.getElementById('memory-usage').textContent = dashboardData.state.memory_usage + '%';
                document.getElementById('db-connections').textContent = dashboardData.state.database_connections;
                
                // Update AI metrics
                const aiAccuracy = dashboardData.state.ai_accuracy;
                const accuracyElement = document.getElementById('ai-accuracy');
                accuracyElement.textContent = aiAccuracy + '%';
                accuracyElement.className = 'font-semibold ' + 
                    (aiAccuracy >= 95 ? 'status-excellent' : 
                     aiAccuracy >= 90 ? 'status-good' : 'status-warning');
                
                document.getElementById('successful-conversations').textContent = dashboardData.state.successful_conversations;
                document.getElementById('handoff-rate').textContent = dashboardData.state.handoff_rate + '%';
                
                // Update simulation status
                simulationActive = dashboardData.state.simulation_active;
                updateSimulationStatus();
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
                    // Only update if there are new messages
                    const currentLines = terminalElement.children.length;
                    const newLines = dashboardData.terminals[terminalType];
                    
                    if (newLines.length > currentLines) {
                        // Add only new lines
                        for (let i = currentLines; i < newLines.length; i++) {
                            const div = document.createElement('div');
                            div.textContent = newLines[i];
                            div.classList.add('slide-in');
                            terminalElement.appendChild(div);
                        }
                        
                        // Remove old lines if too many
                        while (terminalElement.children.length > 25) {
                            terminalElement.removeChild(terminalElement.firstChild);
                        }
                        
                        // Auto-scroll to bottom
                        terminalElement.scrollTop = terminalElement.scrollHeight;
                    }
                }
            });
        }

        function updateActivityLog() {
            const activityLogElement = document.getElementById('activity-log');
            if (activityLogElement && dashboardData.activities) {
                activityLogElement.innerHTML = '';
                dashboardData.activities.forEach((activity, index) => {
                    const div = document.createElement('div');
                    div.className = 'flex items-center justify-between p-2 bg-gray-50 rounded fade-in';
                    div.style.animationDelay = `${index * 0.1}s`;
                    
                    const statusColors = {
                        'success': 'text-green-600 bg-green-100',
                        'info': 'text-blue-600 bg-blue-100',
                        'warning': 'text-yellow-600 bg-yellow-100',
                        'error': 'text-red-600 bg-red-100'
                    };
                    
                    div.innerHTML = `
                        <div class="flex items-center gap-2">
                            <span class="text-sm text-gray-500">${activity.timestamp}</span>
                            <span class="text-sm">${activity.description}</span>
                        </div>
                        <span class="text-xs px-2 py-1 rounded ${statusColors[activity.status] || 'text-gray-600 bg-gray-100'}">${activity.status}</span>
                    `;
                    
                    activityLogElement.appendChild(div);
                });
            }
        }

        // Enhanced data fetching
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
            setInterval(fetchDashboardData, 1500); // Faster updates for better UX
            
            // Initialize with Hebrew
            setLanguage('he');
            
            // Initialize Lucide icons
            lucide.createIcons();
            
            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey || e.metaKey) {
                    switch(e.key) {
                        case '1':
                            e.preventDefault();
                            setActiveTab('overview');
                            break;
                        case '2':
                            e.preventDefault();
                            setActiveTab('terminals');
                            break;
                        case '3':
                            e.preventDefault();
                            setActiveTab('analytics');
                            break;
                        case '4':
                            e.preventDefault();
                            setActiveTab('knowledge');
                            break;
                    }
                }
            });
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Starting Final Enhanced Mission Control Dashboard...")
    print("📊 Dashboard available at: http://127.0.0.1:5000")
    print("🎯 Final Features:")
    print("   • 5 Real-time Terminals with Enhanced Data")
    print("   • Complete Multilingual Support with Dynamic Content")
    print("   • Advanced Simulation Controls with Visual Feedback")
    print("   • Enhanced Real-time Features and Monitoring")
    print("   • Professional UI with Animations and Transitions")
    print("   • Keyboard Shortcuts (Ctrl+1-4 for tabs)")
    print("   • Auto-simulation Management")
    print("   • Status Color Coding")
    print("🌐 Languages: Hebrew (עברית), English, Arabic (العربية)")
    print("💻 Terminals: All systems operational with enhanced monitoring")
    print("🔄 Real-time: 1.5s update interval for optimal performance")
    print("🎮 Simulations: Enhanced with auto-stop and visual feedback")
    app.run(host='0.0.0.0', port=5000, debug=True)
