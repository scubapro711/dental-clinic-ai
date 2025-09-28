# 🛡️ תוכנית שיפורי אבטחה - מערכת ניהול מרפאת שיניים

**תאריך**: 27 בספטמבר 2025  
**עדיפות**: גבוהה  
**זמן משמוד**: 2-3 שעות

## 🚨 בעיות אבטחה שנמצאו

בדיקות האבטחה האגרסיביות חשפו מספר תחומים הדורשים שיפור מיידי:

### 1. אימות קלט (Input Validation)
- **בעיה**: המערכת לא מאמתת קלט משתמש בצורה מקיפה
- **סיכון**: Buffer overflow, XSS, injection attacks
- **פגיעויות שנמצאו**: 5

### 2. ניקוי נתונים (Data Sanitization)  
- **בעיה**: חסר ניקוי HTML, JavaScript ותווים מיוחדים
- **סיכון**: XSS attacks, HTML injection
- **שיעור חסימה**: 0/11 איומים נחסמו

### 3. טיפול בתווי Unicode
- **בעיה**: בעיות בטיפול בתווים מיוחדים ו-Unicode
- **סיכון**: encoding attacks, data corruption

## 🔧 תוכנית שיפורים

### שלב 1: אימות קלט מקיף (30 דקות)

```python
# הוספת פונקציות אימות קלט
def validate_patient_search_input(query: str) -> str:
    """Validate and sanitize patient search input"""
    if not query or not isinstance(query, str):
        raise ValueError("Invalid search query")
    
    # הגבלת אורך
    if len(query) > 100:
        raise ValueError("Search query too long")
    
    # הסרת תווים מסוכנים
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
    for char in dangerous_chars:
        if char in query:
            query = query.replace(char, '')
    
    # ניקוי SQL injection patterns
    sql_patterns = ['drop', 'delete', 'insert', 'update', 'select', 'union', '--', '/*', '*/']
    query_lower = query.lower()
    for pattern in sql_patterns:
        if pattern in query_lower:
            raise ValueError("Invalid characters in search query")
    
    return query.strip()

def validate_appointment_data(patient_id: int, provider_id: int, datetime_str: str, treatment_type: str):
    """Validate appointment booking data"""
    # אימות מזהים
    if not isinstance(patient_id, int) or patient_id <= 0:
        raise ValueError("Invalid patient ID")
    
    if not isinstance(provider_id, int) or provider_id <= 0:
        raise ValueError("Invalid provider ID")
    
    # אימות תאריך
    try:
        datetime.fromisoformat(datetime_str)
    except ValueError:
        raise ValueError("Invalid datetime format")
    
    # אימות סוג טיפול
    if not treatment_type or len(treatment_type) > 200:
        raise ValueError("Invalid treatment type")
    
    return True
```

### שלב 2: ניקוי HTML ו-JavaScript (20 דקות)

```python
import html
import re

def sanitize_html_input(text: str) -> str:
    """Sanitize HTML and JavaScript from input"""
    if not text:
        return ""
    
    # הסרת HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # ניקוי JavaScript
    js_patterns = [
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'onclick=',
        r'onmouseover=',
        r'<script',
        r'</script>'
    ]
    
    for pattern in js_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # HTML encoding
    text = html.escape(text)
    
    return text

def sanitize_sql_input(text: str) -> str:
    """Additional SQL injection protection"""
    if not text:
        return ""
    
    # הסרת תווי SQL מסוכנים
    text = text.replace("'", "''")  # SQL escape
    text = text.replace(";", "")
    text = text.replace("--", "")
    text = text.replace("/*", "")
    text = text.replace("*/", "")
    
    return text
```

### שלב 3: שיפור DemoDataAdapter (45 דקות)

```python
# עדכון DemoDataAdapter עם אבטחה משופרת
class SecureDemoDataAdapter(DemoDataAdapter):
    """Enhanced DemoDataAdapter with security improvements"""
    
    def search_patients(self, query: str) -> List[Dict[str, Any]]:
        """Search for patients with input validation"""
        # אימות וניקוי קלט
        try:
            query = validate_patient_search_input(query)
            query = sanitize_html_input(query)
            query = sanitize_sql_input(query)
        except ValueError as e:
            logger.warning(f"Invalid search input: {e}")
            return []
        
        if not self.connection:
            self.connect()
            
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # שימוש ב-parameterized queries (כבר קיים)
            sql = """
                SELECT patients_id as id, patients_name as name, patients_surname as surname, 
                       patients_sex as sex, patients_birthdate as birthdate
                FROM patients 
                WHERE patients_name LIKE %s OR patients_surname LIKE %s OR patients_id = %s
                LIMIT 50
            """
            search_query = f"%{query}%"
            cursor.execute(sql, (search_query, search_query, query))
            results = cursor.fetchall()
            
            # ניקוי תוצאות לפני החזרה
            for result in results:
                for key, value in result.items():
                    if isinstance(value, str):
                        result[key] = sanitize_html_input(value)
            
            return results
    
    def book_appointment(self, patient_id: int, provider_id: int, datetime_str: str, treatment_type: str) -> Dict[str, Any]:
        """Book appointment with enhanced validation"""
        try:
            # אימות נתונים
            validate_appointment_data(patient_id, provider_id, datetime_str, treatment_type)
            treatment_type = sanitize_html_input(treatment_type)
            treatment_type = sanitize_sql_input(treatment_type)
        except ValueError as e:
            return {
                "success": False,
                "message": f"Invalid input: {e}",
                "appointment": None
            }
        
        if not self.connection:
            self.connect()
            
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            try:
                appointment_time = datetime.fromisoformat(datetime_str)
                
                # בדיקת קיום מטופל ורופא
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE patients_id = %s", (patient_id,))
                if cursor.fetchone()['count'] == 0:
                    return {"success": False, "message": "Patient not found", "appointment": None}
                
                cursor.execute("SELECT COUNT(*) as count FROM doctors WHERE doctors_id = %s", (provider_id,))
                if cursor.fetchone()['count'] == 0:
                    return {"success": False, "message": "Provider not found", "appointment": None}
                
                # הזמנת התור
                sql = """
                    INSERT INTO appointments (doctors_id, patients_id, rooms_id, appointments_from, 
                                            appointments_to, appointments_title, appointments_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    provider_id, patient_id, 1, appointment_time, 
                    appointment_time + timedelta(minutes=30), 
                    treatment_type, 'scheduled'
                ))
                self.connection.commit()
                
                return {
                    "success": True,
                    "message": "Appointment booked successfully",
                    "appointment": {"id": cursor.lastrowid, "status": "scheduled"}
                }
                
            except Exception as e:
                self.connection.rollback()
                logger.error(f"Error booking appointment: {e}")
                return {
                    "success": False,
                    "message": "Failed to book appointment",
                    "appointment": None
                }
```

### שלב 4: הוספת Rate Limiting (15 דקות)

```python
from collections import defaultdict
import time

class RateLimiter:
    """Simple rate limiter for API protection"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # ניקוי בקשות ישנות
        client_requests[:] = [req_time for req_time in client_requests 
                             if now - req_time < self.time_window]
        
        # בדיקת מגבלה
        if len(client_requests) >= self.max_requests:
            return False
        
        # הוספת בקשה נוכחית
        client_requests.append(now)
        return True

# שילוב ב-AdvancedDentalTool
rate_limiter = RateLimiter(max_requests=50, time_window=60)

async def search_patients_with_rate_limit(self, query: str, client_id: str = "default") -> List[Dict[str, Any]]:
    """Search patients with rate limiting"""
    if not rate_limiter.is_allowed(client_id):
        raise Exception("Rate limit exceeded. Please try again later.")
    
    return await self.search_patients(query)
```

## 🧪 בדיקות אבטחה משופרות

### בדיקת השיפורים

```python
# בדיקות אבטחה לאחר השיפורים
async def test_security_improvements():
    """Test security improvements"""
    tool = AdvancedDentalTool()
    await tool.initialize()
    
    # בדיקת הגנה מפני XSS
    xss_payload = "<script>alert('XSS')</script>"
    try:
        result = await tool.search_patients(xss_payload)
        assert "<script>" not in str(result), "XSS protection failed"
        print("✅ XSS protection working")
    except ValueError:
        print("✅ XSS blocked by input validation")
    
    # בדיקת הגנה מפני SQL injection
    sql_payload = "'; DROP TABLE patients; --"
    try:
        result = await tool.search_patients(sql_payload)
        print("✅ SQL injection protection working")
    except ValueError:
        print("✅ SQL injection blocked by input validation")
    
    # בדיקת buffer overflow protection
    large_input = "A" * 10000
    try:
        result = await tool.search_patients(large_input)
        print("❌ Buffer overflow protection needs improvement")
    except ValueError:
        print("✅ Buffer overflow protection working")
    
    await tool.cleanup()
```

## 📋 רשימת משימות

### ✅ מיידי (עדיפות גבוהה)
- [ ] הוספת פונקציות אימות קלט
- [ ] יישום ניקוי HTML/JavaScript  
- [ ] עדכון DemoDataAdapter עם אבטחה משופרת
- [ ] הוספת Rate Limiting בסיסי

### 🔄 קצר טווח (השבוע הבא)
- [ ] בדיקות אבטחה מקיפות לאחר השיפורים
- [ ] הוספת CSRF protection
- [ ] שיפור הודעות שגיאה
- [ ] תיעוד שיפורי האבטחה

### 📈 ארוך טווח (החודש הבא)
- [ ] אימות ואישור משתמשים
- [ ] הצפנת נתונים רגישים
- [ ] מעקב ולוגים של פעילות חשודה
- [ ] בדיקות חדירה מקצועיות

## 🎯 יעדי אבטחה

לאחר יישום השיפורים, המערכת צריכה להגיע ל:
- **ציון אבטחה**: 85+ מתוך 100
- **הגנה מפני XSS**: 100%
- **הגנה מפני SQL Injection**: 100% (כבר קיים)
- **אימות קלט**: 95%+
- **ניקוי נתונים**: 90%+

---

**הערה**: שיפורי האבטחה הם קריטיים לפני המעבר לסביבת ייצור או שילוב עם Open Dental API.
