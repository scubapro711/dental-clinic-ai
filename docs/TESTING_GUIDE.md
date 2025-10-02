# 🧪 Testing Guide - DentalAI

**תאריך:** 3 באוקטובר 2025  
**גרסה:** 1.0  
**מטרה:** חבילת בדיקות מקיפה לפני deployment

---

## 📋 סקירה כללית

המערכת כוללת חבילת בדיקות אגרסיבית ומקיפה שבודקת:
- ✅ Unit Tests - בדיקת כל קומפוננטה
- ✅ Integration Tests - בדיקת אינטגרציה בין מערכות
- ✅ Security Tests - סריקת vulnerabilities
- ✅ Code Quality - בדיקת איכות קוד
- ✅ Load Tests - בדיקת ביצועים
- ✅ API Tests - בדיקת כל ה-endpoints

---

## 🚀 הרצה מהירה

### אופציה 1: הרץ הכל (מומלץ לפני deployment)

```bash
cd /path/to/dental-clinic-ai-repo
./scripts/pre_deployment_tests.sh
```

**זמן ריצה:** ~5-10 דקות  
**פלט:** דוח מפורט עם כל הבדיקות

---

### אופציה 2: הרץ רק טסטים ספציפיים

```bash
# רק unit tests
cd backend
pytest tests/ -v

# רק integration tests
pytest tests/test_e2e_mvp.py -v

# רק security tests
bandit -r app/ -ll

# רק API tests
./scripts/api_tests.sh
```

---

## 📊 חבילת הבדיקות המלאה

### 1. Unit Tests (pytest)

**מה זה בודק:**
- כל agent (Alex)
- כל tool (Odoo, Telegram)
- כל API endpoint
- Error handling

**איך להריץ:**
```bash
cd backend
pytest tests/ -v --tb=short
```

**טסטים:**
- `test_agents.py` - בדיקת agents
- `test_telegram_integration.py` - בדיקת Telegram
- `test_e2e_mvp.py` - בדיקות end-to-end

**יעד:** 90%+ passing

---

### 2. Integration Tests

**מה זה בודק:**
- Backend + Database
- Backend + Redis
- Backend + Mock Odoo
- Agent + Tools
- Telegram + Backend

**איך להריץ:**
```bash
cd backend
pytest tests/test_e2e_mvp.py -v
```

**תרחישים:**
1. שיחה פשוטה
2. שאלה רפואית
3. בירור חשבונית
4. קביעת תור
5. בירור מחירים
6. בדיקת זמינות
7. שיחה רב-תורית
8. זיכרון causal

**יעד:** כל התרחישים עוברים

---

### 3. Code Coverage

**מה זה בודק:**
- כמה אחוז מהקוד מכוסה בטסטים

**איך להריץ:**
```bash
cd backend
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

**פלט:**
- Terminal: סיכום מהיר
- HTML: `htmlcov/index.html` - דוח מפורט

**יעד:** 70%+ coverage

---

### 4. Security Scanning

#### 4a. Bandit - Code Vulnerabilities

**מה זה בודק:**
- SQL injection
- Hardcoded passwords
- Insecure functions
- Weak cryptography

**איך להריץ:**
```bash
cd backend
bandit -r app/ -ll -f txt
```

**רמות חומרה:**
- `HIGH` - 🚨 קריטי, תקן מיד!
- `MEDIUM` - ⚠️ חשוב, תקן בהקדם
- `LOW` - ℹ️ לידיעה

**יעד:** 0 HIGH, 0 MEDIUM

---

#### 4b. Safety - Dependency Vulnerabilities

**מה זה בודק:**
- חבילות Python עם vulnerabilities ידועות

**איך להריץ:**
```bash
cd backend
safety check
```

**יעד:** 0 vulnerabilities

---

### 5. Code Quality

#### 5a. Pylint

**מה זה בודק:**
- Code style
- Best practices
- Potential bugs
- Code complexity

**איך להריץ:**
```bash
cd backend
pylint app/ --output-format=text
```

**ציון:** 0-10 (יעד: 8+)

---

#### 5b. Flake8

**מה זה בודק:**
- PEP 8 compliance
- Syntax errors
- Undefined names

**איך להריץ:**
```bash
cd backend
flake8 app/ --count --statistics
```

**יעד:** 0 errors

---

#### 5c. MyPy - Type Checking

**מה זה בודק:**
- Type hints נכונים
- Type consistency

**איך להריץ:**
```bash
cd backend
mypy app/ --ignore-missing-imports
```

**יעד:** 0 type errors

---

### 6. Load Testing (Locust)

**מה זה בודק:**
- ביצועים תחת עומס
- 100+ concurrent users
- Response times
- Error rates

**איך להריץ:**

```bash
# 1. הרץ את השרת
cd backend
uvicorn app.main:app --reload

# 2. בטרמינל אחר, הרץ locust
cd backend
locust -f tests/load_test.py --host=http://localhost:8000

# 3. פתח דפדפן
# http://localhost:8089

# 4. הגדר:
# - Number of users: 100
# - Spawn rate: 10/sec
# - Host: http://localhost:8000

# 5. לחץ "Start Swarming"
```

**מדדים:**
- **Response Time:** < 500ms (average)
- **Error Rate:** < 1%
- **Requests/sec:** > 100
- **Concurrent Users:** 100+

**תרחישי בדיקה:**
- Health checks
- Chat greetings
- Appointment inquiries
- Price inquiries
- Medical questions
- Patient search
- Multilingual support

---

### 7. API Integration Tests

**מה זה בודק:**
- כל endpoint עם HTTP requests אמיתיים
- Status codes נכונים
- Error handling
- Request/Response validation

**איך להריץ:**

```bash
# 1. הרץ את השרת
cd backend
uvicorn app.main:app --reload

# 2. בטרמינל אחר, הרץ API tests
./scripts/api_tests.sh
```

**Endpoints שנבדקים:**
- `GET /health` - Health check
- `GET /` - Root
- `POST /api/v1/chat` - Chat (multiple scenarios)
- `POST /api/v1/telegram/webhook` - Telegram
- `POST /api/v1/auth/*` - Authentication (if implemented)
- Error cases (404, 405, 422)

**יעד:** 100% passing

---

### 8. Framework Compliance

**מה זה בודק:**
- ADR System קיים
- Git hooks מותקנים
- Feature Inventory מעודכן
- Work Plan מסונכרן
- Documentation מלא

**איך להריץ:**
```bash
python scripts/check_framework_compliance.py
```

**יעד:** 100% compliance

---

### 9. Work Plan Synchronization

**מה זה בודק:**
- Agents בקוד = Agents בתוכנית
- אין agents שתוכננו אבל לא נבנו
- אין agents שנבנו אבל לא בתוכנית

**איך להריץ:**
```bash
python scripts/check_work_plan_sync.py
```

**יעד:** 100% sync

---

## 📈 CI/CD Integration

### GitHub Actions (עתידי)

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov bandit safety
      - name: Run tests
        run: |
          ./scripts/pre_deployment_tests.sh
```

---

## 🎯 Pre-Deployment Checklist

לפני deployment ל-production, ודא ש:

### בדיקות חובה:
- [ ] `./scripts/pre_deployment_tests.sh` עובר (90%+)
- [ ] `./scripts/api_tests.sh` עובר (100%)
- [ ] `bandit -r app/ -ll` - 0 HIGH/MEDIUM
- [ ] `safety check` - 0 vulnerabilities
- [ ] `pytest --cov` - 70%+ coverage

### תיעוד:
- [ ] Feature Inventory מעודכן
- [ ] Work Plan מסונכרן
- [ ] ADR נוצר (אם יש החלטה חשובה)
- [ ] README מעודכן

### קונפיגורציה:
- [ ] `.env.example` מעודכן
- [ ] אין secrets בקוד
- [ ] Environment variables מוגדרות ב-production

### ביצועים:
- [ ] Load test עובר (100 users, <500ms)
- [ ] אין memory leaks
- [ ] אין N+1 queries

---

## 🐛 Troubleshooting

### בעיה: טסטים נכשלים

```bash
# הרץ טסט ספציפי עם debug
pytest tests/test_agents.py::test_alex_greeting -v -s

# הצג traceback מלא
pytest tests/ --tb=long

# הרץ רק טסטים שנכשלו
pytest tests/ --lf
```

---

### בעיה: Load test איטי

```bash
# בדוק bottlenecks
# 1. Profile הקוד
python -m cProfile -o profile.stats app/main.py

# 2. נתח
python -m pstats profile.stats

# 3. חפש slow queries
# הוסף logging ל-database queries
```

---

### בעיה: Security vulnerabilities

```bash
# עדכן dependencies
pip install --upgrade -r requirements.txt

# בדוק שוב
safety check

# אם עדיין יש בעיות, חפש alternatives
pip search <package-name>
```

---

## 📚 משאבים נוספים

### כלים:
- **pytest:** https://docs.pytest.org/
- **Locust:** https://docs.locust.io/
- **Bandit:** https://bandit.readthedocs.io/
- **Safety:** https://pyup.io/safety/
- **Pylint:** https://pylint.pycqa.org/

### Best Practices:
- **Testing Best Practices:** https://testdriven.io/
- **Python Testing:** https://realpython.com/python-testing/
- **Security Testing:** https://owasp.org/

---

## 🎓 הוספת טסטים חדשים

### Template לטסט חדש:

```python
# tests/test_new_feature.py
import pytest
from app.agents.alex import alex_agent

def test_new_feature():
    """Test description"""
    # Arrange
    input_data = {"message": "test"}
    
    # Act
    result = alex_agent.process(input_data)
    
    # Assert
    assert result["status"] == "success"
    assert "response" in result
```

### הוסף ל-`pre_deployment_tests.sh`:

```bash
run_test "New Feature Test" \
    "pytest tests/test_new_feature.py -v"
```

---

**מסמך זה:** docs/TESTING_GUIDE.md  
**גרסה:** 1.0  
**תאריך:** 3 באוקטובר 2025  
**סטטוס:** מוכן לשימוש
