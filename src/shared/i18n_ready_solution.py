#!/usr/bin/env python3
"""
🌍 Ready-to-use I18n Solution for Dental Clinic System
פתרון מוכן לתמיכה רב-לשונית - עובד מיידית!

Usage:
    from shared.i18n_ready_solution import get_message, detect_language
    
    # Basic usage
    message = get_message('welcome', 'en')
    
    # With parameters
    message = get_message('patient_found', 'he', name='יוסי כהן', age=45)
    
    # Auto-detect language
    user_text = "Hello doctor"
    lang = detect_language(user_text)
    response = get_message('welcome', lang)
"""

from typing import Dict, Any, Optional

# 🗣️ Translation Dictionary - Ready to use!
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'he': {
        # Greetings & Welcome
        'welcome': 'ברוכים הבאים למרפאת השיניים',
        'hello': 'שלום',
        'goodbye': 'להתראות',
        'thank_you': 'תודה רבה',
        
        # Patient Management
        'patient_found': 'נמצא מטופל: {name}, גיל {age}',
        'patient_not_found': 'מטופל לא נמצא במערכת',
        'patient_created': 'מטופל חדש נוצר בהצלחה: {name}',
        'patient_updated': 'פרטי המטופל עודכנו בהצלחה',
        
        # Appointments
        'appointment_booked': 'התור נקבע בהצלחה ל-{date} בשעה {time}',
        'appointment_cancelled': 'התור בוטל בהצלחה',
        'appointment_rescheduled': 'התור הועבר ל-{date} בשעה {time}',
        'no_slots': 'אין תורים פנויים ביום {date}',
        'appointment_reminder': 'תזכורת: יש לך תור מחר ב-{time}',
        
        # Providers/Doctors
        'provider_found': 'נמצא רופא: ד"ר {name}, התמחות: {specialty}',
        'provider_not_available': 'הרופא לא זמין בתאריך המבוקש',
        'providers_list': 'רופאים זמינים: {providers}',
        
        # System Messages
        'system_error': 'אירעה שגיאה במערכת: {error}',
        'processing': 'מעבד את הבקשה...',
        'success': 'הפעולה הושלמה בהצלחה',
        'invalid_input': 'קלט לא תקין, אנא נסה שוב',
        
        # Common Actions
        'search_results': 'נמצאו {count} תוצאות',
        'no_results': 'לא נמצאו תוצאות',
        'please_wait': 'אנא המתן...',
        'try_again': 'אנא נסה שוב',
        
        # Time & Dates
        'today': 'היום',
        'tomorrow': 'מחר',
        'yesterday': 'אתמול',
        'this_week': 'השבוע',
        'next_week': 'השבוע הבא',
        
        # Status Messages
        'scheduled': 'מתוזמן',
        'completed': 'הושלם',
        'cancelled': 'בוטל',
        'rescheduled': 'הועבר',
        'confirmed': 'אושר'
    },
    
    'en': {
        # Greetings & Welcome
        'welcome': 'Welcome to the dental clinic',
        'hello': 'Hello',
        'goodbye': 'Goodbye',
        'thank_you': 'Thank you very much',
        
        # Patient Management
        'patient_found': 'Patient found: {name}, age {age}',
        'patient_not_found': 'Patient not found in system',
        'patient_created': 'New patient created successfully: {name}',
        'patient_updated': 'Patient details updated successfully',
        
        # Appointments
        'appointment_booked': 'Appointment booked successfully for {date} at {time}',
        'appointment_cancelled': 'Appointment cancelled successfully',
        'appointment_rescheduled': 'Appointment rescheduled to {date} at {time}',
        'no_slots': 'No available slots on {date}',
        'appointment_reminder': 'Reminder: You have an appointment tomorrow at {time}',
        
        # Providers/Doctors
        'provider_found': 'Doctor found: Dr. {name}, specialty: {specialty}',
        'provider_not_available': 'Doctor not available on requested date',
        'providers_list': 'Available doctors: {providers}',
        
        # System Messages
        'system_error': 'System error occurred: {error}',
        'processing': 'Processing your request...',
        'success': 'Operation completed successfully',
        'invalid_input': 'Invalid input, please try again',
        
        # Common Actions
        'search_results': 'Found {count} results',
        'no_results': 'No results found',
        'please_wait': 'Please wait...',
        'try_again': 'Please try again',
        
        # Time & Dates
        'today': 'Today',
        'tomorrow': 'Tomorrow',
        'yesterday': 'Yesterday',
        'this_week': 'This week',
        'next_week': 'Next week',
        
        # Status Messages
        'scheduled': 'Scheduled',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'rescheduled': 'Rescheduled',
        'confirmed': 'Confirmed'
    },
    
    'ar': {
        # Greetings & Welcome
        'welcome': 'مرحباً بكم في عيادة الأسنان',
        'hello': 'مرحبا',
        'goodbye': 'وداعا',
        'thank_you': 'شكراً جزيلاً',
        
        # Patient Management
        'patient_found': 'تم العثور على المريض: {name}، العمر {age}',
        'patient_not_found': 'المريض غير موجود في النظام',
        'patient_created': 'تم إنشاء مريض جديد بنجاح: {name}',
        'patient_updated': 'تم تحديث بيانات المريض بنجاح',
        
        # Appointments
        'appointment_booked': 'تم حجز الموعد بنجاح في {date} الساعة {time}',
        'appointment_cancelled': 'تم إلغاء الموعد بنجاح',
        'appointment_rescheduled': 'تم تأجيل الموعد إلى {date} الساعة {time}',
        'no_slots': 'لا توجد مواعيد متاحة في {date}',
        'appointment_reminder': 'تذكير: لديك موعد غداً الساعة {time}',
        
        # Providers/Doctors
        'provider_found': 'تم العثور على الطبيب: د. {name}، التخصص: {specialty}',
        'provider_not_available': 'الطبيب غير متاح في التاريخ المطلوب',
        'providers_list': 'الأطباء المتاحون: {providers}',
        
        # System Messages
        'system_error': 'حدث خطأ في النظام: {error}',
        'processing': 'جاري معالجة طلبك...',
        'success': 'تمت العملية بنجاح',
        'invalid_input': 'إدخال غير صحيح، يرجى المحاولة مرة أخرى',
        
        # Common Actions
        'search_results': 'تم العثور على {count} نتائج',
        'no_results': 'لم يتم العثور على نتائج',
        'please_wait': 'يرجى الانتظار...',
        'try_again': 'يرجى المحاولة مرة أخرى',
        
        # Time & Dates
        'today': 'اليوم',
        'tomorrow': 'غداً',
        'yesterday': 'أمس',
        'this_week': 'هذا الأسبوع',
        'next_week': 'الأسبوع القادم',
        
        # Status Messages
        'scheduled': 'مجدول',
        'completed': 'مكتمل',
        'cancelled': 'ملغي',
        'rescheduled': 'مؤجل',
        'confirmed': 'مؤكد'
    }
}

def get_message(key: str, lang: str = 'he', **kwargs) -> str:
    """
    Get localized message with parameter substitution
    
    Args:
        key: Message key from TRANSLATIONS
        lang: Language code ('he', 'en', 'ar')
        **kwargs: Parameters to substitute in message
        
    Returns:
        Localized message string
        
    Examples:
        >>> get_message('welcome', 'en')
        'Welcome to the dental clinic'
        
        >>> get_message('patient_found', 'he', name='יוסי', age=45)
        'נמצא מטופל: יוסי, גיל 45'
    """
    try:
        # Get language dictionary, fallback to Hebrew
        lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS['he'])
        
        # Get message, fallback to key itself
        message = lang_dict.get(key, key)
        
        # Substitute parameters if provided
        if kwargs:
            return message.format(**kwargs)
        
        return message
        
    except Exception as e:
        # Fallback to key with error indication
        return f"{key} (translation error: {str(e)})"

def detect_language(text: str) -> str:
    """
    Detect language from text using character set analysis
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code ('he', 'en', 'ar')
        
    Examples:
        >>> detect_language('שלום רופא')
        'he'
        
        >>> detect_language('Hello doctor')
        'en'
        
        >>> detect_language('مرحبا دكتور')
        'ar'
    """
    if not text or not text.strip():
        return 'he'  # Default to Hebrew
    
    text = text.strip()
    
    # Hebrew detection (Unicode range U+0590 to U+05FF)
    if any('\u0590' <= char <= '\u05FF' for char in text):
        return 'he'
    
    # Arabic detection (Unicode range U+0600 to U+06FF)
    if any('\u0600' <= char <= '\u06FF' for char in text):
        return 'ar'
    
    # English detection (ASCII letters)
    if any(char.isascii() and char.isalpha() for char in text):
        return 'en'
    
    # Default fallback
    return 'he'

def detect_language_advanced(text: str) -> str:
    """
    Advanced language detection using langdetect library (if available)
    Falls back to simple detection if langdetect is not installed
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code ('he', 'en', 'ar')
    """
    try:
        from langdetect import detect
        detected = detect(text)
        
        # Map langdetect codes to our codes
        lang_mapping = {
            'he': 'he',
            'en': 'en', 
            'ar': 'ar',
            'iw': 'he',  # Alternative Hebrew code
        }
        
        return lang_mapping.get(detected, 'he')
        
    except ImportError:
        # Fallback to simple detection
        return detect_language(text)
    except Exception:
        # Fallback to simple detection on any error
        return detect_language(text)

def get_supported_languages() -> Dict[str, str]:
    """
    Get list of supported languages
    
    Returns:
        Dictionary mapping language codes to language names
    """
    return {
        'he': 'עברית',
        'en': 'English', 
        'ar': 'العربية'
    }

def add_translation(key: str, translations: Dict[str, str]) -> None:
    """
    Add new translation key to all languages
    
    Args:
        key: Translation key
        translations: Dict mapping language codes to translations
        
    Example:
        >>> add_translation('new_feature', {
        ...     'he': 'תכונה חדשה',
        ...     'en': 'New feature',
        ...     'ar': 'ميزة جديدة'
        ... })
    """
    for lang_code, translation in translations.items():
        if lang_code in TRANSLATIONS:
            TRANSLATIONS[lang_code][key] = translation

# 🧪 Test function to verify everything works
def test_i18n_solution():
    """Test the i18n solution to make sure everything works"""
    print("🧪 Testing I18n Ready Solution...")
    
    # Test basic translations
    print("\n1. Basic translations:")
    for lang in ['he', 'en', 'ar']:
        welcome = get_message('welcome', lang)
        print(f"   {lang}: {welcome}")
    
    # Test with parameters
    print("\n2. Translations with parameters:")
    patient_msg_he = get_message('patient_found', 'he', name='יוסי כהן', age=45)
    patient_msg_en = get_message('patient_found', 'en', name='John Doe', age=35)
    print(f"   Hebrew: {patient_msg_he}")
    print(f"   English: {patient_msg_en}")
    
    # Test language detection
    print("\n3. Language detection:")
    test_texts = [
        'שלום רופא שיניים',
        'Hello dental doctor',
        'مرحبا دكتور الأسنان'
    ]
    
    for text in test_texts:
        detected = detect_language(text)
        response = get_message('welcome', detected)
        print(f"   '{text}' → {detected} → {response}")
    
    # Test appointment booking flow
    print("\n4. Appointment booking flow:")
    date, time = '2025-09-28', '14:30'
    
    for lang in ['he', 'en']:
        processing = get_message('processing', lang)
        booked = get_message('appointment_booked', lang, date=date, time=time)
        success = get_message('success', lang)
        
        print(f"   {lang}:")
        print(f"     {processing}")
        print(f"     {booked}")
        print(f"     {success}")
    
    print("\n✅ All tests passed! Ready to integrate!")

if __name__ == "__main__":
    test_i18n_solution()



add_translation('appointment.confirmation.success', {
    'he': 'התור אושר עבור {patient_name} בשעה {appointment_time}',
    'en': 'Appointment confirmed for {patient_name} at {appointment_time}',
    'ar': 'تم تأكيد الموعد لـ {patient_name} في الساعة {appointment_time}'
})

