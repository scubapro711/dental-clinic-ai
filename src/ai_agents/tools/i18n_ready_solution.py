import json

TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to the dental clinic",
        "patient_found": "Patient found: {name}, age {age}",
        "no_patients_found": "No patients found matching '{query}'",
        "providers_list": "Available providers:\n{providers}",
        "no_providers_found": "No providers found",
        "slots_list": "Available slots for {date}:\n{slots}",
        "no_slots_found": "No available slots for {date}",
        "appointment_booked": "Appointment successfully booked for {date} at {time}",
        "api_error": "An API error occurred: {error}",
        "system_error": "A system error occurred: {error}",
        "invalid_input": "Invalid input for field: {field}"
    },
    "he": {
        "welcome": "ברוכים הבאים למרפאת השיניים",
        "patient_found": "נמצא מטופל: {name}, גיל {age}",
        "no_patients_found": "לא נמצאו מטופלים התואמים לחיפוש '{query}'",
        "providers_list": "רופאים זמינים:\n{providers}",
        "no_providers_found": "לא נמצאו רופאים זמינים",
        "slots_list": "תורים פנויים עבור {date}:\n{slots}",
        "no_slots_found": "אין תורים פנויים עבור {date}",
        "appointment_booked": "התור נקבע בהצלחה לתאריך {date} בשעה {time}",
        "api_error": "שגיאת API: {error}",
        "system_error": "שגיאת מערכת: {error}",
        "invalid_input": "קלט לא תקין עבור השדה: {field}"
    },
    "ar": {
        "welcome": "أهلاً وسهلاً في عيادة الأسنان",
        "patient_found": "تم العثور على المريض: {name}، العمر {age}",
        "no_patients_found": "لم يتم العثور على مرضى مطابقين للبحث '{query}'",
        "providers_list": "الأطباء المتاحون:\n{providers}",
        "no_providers_found": "لم يتم العثور على أطباء متاحين",
        "slots_list": "المواعيد المتاحة لـ {date}:\n{slots}",
        "no_slots_found": "لا توجد مواعيد متاحة لـ {date}",
        "appointment_booked": "تم حجز الموعد بنجاح في {date} الساعة {time}",
        "api_error": "حدث خطأ في واجهة برمجة التطبيقات: {error}",
        "system_error": "حدث خطأ في النظام: {error}",
        "invalid_input": "إدخال غير صالح للحقل: {field}"
    }
}

def get_message(key, language="en", **kwargs):
    """Get a translated message."""
    return TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, key).format(**kwargs)

def detect_language(text: str) -> str:
    """Detect the language of a given text."""
    # Simple detection for demonstration purposes
    if any("\u0590" <= char <= "\u05EA" for char in text):
        return "he"
    if any("\u0600" <= char <= "\u06FF" for char in text):
        return "ar"
    return "en"

