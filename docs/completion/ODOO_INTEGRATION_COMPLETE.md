# אינטגרציה מלאה עם Odoo - DentaFlow

**תאריך:** 7 באוקטובר 2025  
**מבוסס על:** בדיקות ממשיות, קוד קיים, וניסיון פיתוח

---

## 🔌 פרטי חיבור

```python
ODOO_URL = "https://dentaflow.ai"
ODOO_DB = "dental_prod"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "DentaFlow2024"
ODOO_VERSION = "19.0" (released 2025-09-30)
```

**מודולים מותקנים:**
- `pragtech_dental_management` - Dental Clinic Management
- `dental_israel` - Dental Israel Localization

---

## 📋 מודלים ב-Odoo

### 1. res.partner (מטופלים) ✅ **עובד!**

**תיאור:** מודל סטנדרטי של Odoo לשותפים/לקוחות. משמש למטופלים.

**שדות חשובים:**
```python
{
    "id": int,                    # Odoo ID
    "name": str,                  # שם מלא (חובה)
    "email": str,                 # אימייל
    "phone": str,                 # טלפון
    "mobile": str,                # נייד
    "street": str,                # רחוב
    "city": str,                  # עיר
    "zip": str,                   # מיקוד
    "country_id": [id, name],     # מדינה (many2one)
    "customer_rank": int,         # > 0 = לקוח
    "is_company": bool,           # False למטופלים
}
```

**פעולות נתמכות:**
- ✅ `search` - חיפוש מטופלים
- ✅ `read` - קריאת פרטים
- ✅ `create` - יצירת מטופל חדש
- ✅ `write` - עדכון פרטים

**דוגמה ליצירה:**
```python
patient_id = odoo.execute_kw(
    'res.partner', 'create',
    [{
        'name': 'יוסי כהן',
        'email': 'yossi@example.com',
        'phone': '03-1234567',
        'customer_rank': 1,  # Mark as customer
        'is_company': False
    }]
)
```

**RBAC:**
- Patient: יכול לראות רק את עצמו (`[('id', '=', user.patient_id)]`)
- Staff: יכול לראות כל המטופלים

---

### 2. medical.appointment (תורים) ⚠️ **בעייתי!**

**תיאור:** מודל מותאם אישית למרפאות שיניים מ-Pragtech Dental Management.

**שדות חשובים:**
```python
{
    "id": int,
    "patient_id": [id, name],         # מטופל (many2one, חובה)
    "doctor_id": [id, name],          # רופא (many2one, חובה)
    "appointment_sdate": datetime,    # תאריך התחלה (חובה)
    "appointment_edate": datetime,    # תאריך סיום (חובה)
    "patient_state": str,             # סטטוס מטופל (חובה)
    "state": str,                     # סטטוס תור
    "operations_ids": [[ids]],        # פעולות/טיפולים (one2many)
    "inv_id": [id, name],             # חשבונית (many2one)
    "room_id": [id, name],            # חדר טיפול (many2one)
    "urgency": bool,                  # דחוף
    "no_invoice": bool,               # ללא חשבונית
}
```

**ערכים אפשריים:**

`patient_state`:
- `'new'` - מטופל חדש
- `'old'` - מטופל קיים

`state`:
- (לא ידוע - צריך לבדוק)

**בעיה ידועה:**
```
❌ Error: trying to delete... constraint on doctor_id
```

**סיבה אפשרית:**
1. `doctor_id` צריך להיות מ-`hr.employee` עם תפקיד רופא
2. יש constraint שמונע מחיקה/עדכון לא תקין
3. חסרים שדות נוספים נדרשים

**פעולות:**
- ⚠️ `search` - עובד
- ⚠️ `read` - עובד
- ❌ `create` - נכשל (constraint error)
- ❓ `write` - לא נבדק

**TODO:**
- [ ] לברר מה הבעיה עם doctor_id
- [ ] לבדוק אם צריך שדות נוספים
- [ ] לבדוק אם יש workflow מיוחד ליצירת תור

---

### 3. hr.employee (רופאים/צוות) ✅ **עובד חלקית**

**תיאור:** מודל סטנדרטי של Odoo לעובדים. משמש לרופאים וצוות.

**שדות חשובים:**
```python
{
    "id": int,
    "name": str,                  # שם מלא
    "job_id": [id, name],         # תפקיד (many2one)
    "department_id": [id, name],  # מחלקה (many2one)
    "work_email": str,            # אימייל עבודה
    "work_phone": str,            # טלפון עבודה
    "user_id": [id, name],        # משתמש מקושר (many2one)
}
```

**פעולות נתמכות:**
- ✅ `search` - חיפוש עובדים
- ✅ `read` - קריאת פרטים

**דוגמה:**
```python
# Get all employees
employee_ids = odoo.execute_kw(
    'hr.employee', 'search',
    [[]]
)

# Read employee details
employees = odoo.execute_kw(
    'hr.employee', 'read',
    [employee_ids],
    {'fields': ['id', 'name', 'job_id', 'work_email']}
)
```

**TODO:**
- [ ] לברר איך מסמנים עובד כרופא
- [ ] לבדוק אם יש מודל נפרד לרופאים

---

### 4. account.move (חשבוניות) ❓ **לא נבדק**

**תיאור:** מודל סטנדרטי של Odoo לחשבוניות ותנועות חשבונאיות.

**שדות חשובים (משוער):**
```python
{
    "id": int,
    "name": str,                  # מספר חשבונית
    "partner_id": [id, name],     # לקוח/מטופל (many2one)
    "invoice_date": date,         # תאריך חשבונית
    "amount_total": float,        # סכום כולל
    "amount_residual": float,     # יתרה לתשלום
    "state": str,                 # סטטוס (draft/posted/cancel)
    "payment_state": str,         # סטטוס תשלום (not_paid/in_payment/paid)
    "invoice_line_ids": [[ids]],  # שורות חשבונית (one2many)
}
```

**TODO:**
- [ ] לבדוק גישה למודל
- [ ] לבדוק שדות נדרשים
- [ ] לממש אינטגרציה

---

### 5. product.product (שירותים/טיפולים) ❓ **לא נבדק**

**תיאור:** מודל סטנדרטי של Odoo למוצרים/שירותים. משמש לטיפולים דנטליים.

**שדות חשובים (משוער):**
```python
{
    "id": int,
    "name": str,                  # שם טיפול
    "list_price": float,          # מחיר
    "standard_price": float,      # עלות
    "type": str,                  # 'service' לטיפולים
    "categ_id": [id, name],       # קטגוריה (many2one)
}
```

**TODO:**
- [ ] לבדוק גישה למודל
- [ ] לרשום טיפולים נפוצים
- [ ] לחבר למחירון

---

## 🔧 OdooClient - ה-Wrapper שלנו

**מיקום:** `backend/app/integrations/odoo_client.py`

### מתודות מיושמות

#### ניהול מטופלים ✅

```python
class OdooClient:
    def search_patients(
        self, 
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        limit: int = 100
    ) -> List[int]
    
    def get_patient(self, patient_id: int) -> Optional[Dict]
    
    def create_patient(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        **kwargs
    ) -> int
    
    def update_patient(
        self,
        patient_id: int,
        **kwargs
    ) -> bool
```

**סטטוס:** ✅ עובד מצוין!

#### ניהול תורים ⚠️

```python
class OdooClient:
    def search_appointments(
        self,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[int]
    
    def get_appointment(self, appointment_id: int) -> Optional[Dict]
    
    def create_appointment(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_sdate: datetime,
        appointment_edate: datetime,
        patient_state: str = "old",
        **kwargs
    ) -> int  # ❌ נכשל!
    
    def update_appointment(
        self,
        appointment_id: int,
        **kwargs
    ) -> bool
```

**סטטוס:** 
- ✅ `search_appointments` - עובד
- ✅ `get_appointment` - עובד
- ❌ `create_appointment` - נכשל (constraint error)
- ❓ `update_appointment` - לא נבדק

#### ניהול רופאים ✅

```python
class OdooClient:
    def get_doctors(self) -> List[Dict]
```

**סטטוס:** ✅ עובד!

---

## 🛠️ כלים לסוכנים

### Alex Tools - Odoo Integration

**מיקום:** `backend/app/agents/tools/alex_odoo_tools.py`

#### Production Tools (עובדים עם Odoo אמיתי)

```python
def search_patient_odoo(
    query: str,
    user_id: str,
    user_role: str
) -> List[Dict]:
    """חיפוש מטופלים עם RBAC"""
    # ✅ עובד!

def get_patient_details_odoo(
    patient_id: str,
    user_id: str,
    user_role: str
) -> Dict:
    """פרטי מטופל עם RBAC"""
    # ✅ עובד!

def create_patient_odoo(
    name: str,
    email: Optional[str],
    phone: Optional[str],
    user_role: str
) -> Dict:
    """יצירת מטופל חדש (staff only)"""
    # ✅ עובד!

def update_patient_odoo(
    patient_id: str,
    user_id: str,
    user_role: str,
    **updates
) -> Dict:
    """עדכון פרטי מטופל עם RBAC"""
    # ✅ עובד!

def get_doctors_list_odoo() -> List[Dict]:
    """רשימת רופאים"""
    # ✅ עובד!
```

#### Mock Tools (זמני - עד תיקון Odoo)

```python
def get_available_slots_tool(...):
    """זמינות תורים"""
    # ⏳ Mock - צריך Odoo

def create_appointment_tool(...):
    """יצירת תור"""
    # ⏳ Mock - צריך Odoo

def get_patient_invoices_tool(...):
    """חשבוניות מטופל"""
    # ⏳ Mock - צריך Odoo billing

def get_invoice_details_tool(...):
    """פרטי חשבונית"""
    # ⏳ Mock - צריך Odoo billing
```

---

## 🔐 RBAC ב-Odoo Tools

### איך זה עובד

כל כלי מקבל `user_id` ו-`user_role` מה-AgentState:

```python
def search_patient_odoo(query: str, user_id: str, user_role: str):
    odoo = OdooClient()
    odoo.authenticate()
    
    # RBAC check
    if user_role == "patient":
        # Patients can only see themselves
        patient_id = get_patient_id_from_user_id(user_id)
        return [odoo.get_patient(patient_id)]
    
    elif user_role in ["dentist", "receptionist", "owner"]:
        # Staff can search all patients
        patient_ids = odoo.search_patients(name=query)
        return [odoo.get_patient(pid) for pid in patient_ids]
    
    else:
        raise PermissionError("Access denied")
```

### Access Matrix

| User Role | Search All | View All | Create | Update All | Update Own |
|-----------|------------|----------|--------|------------|------------|
| **Patient** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Receptionist** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Dentist** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Owner** | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 📊 סטטוס אינטגרציה

### מה עובד ✅

| תכונה | סטטוס | הערות |
|-------|--------|-------|
| **חיבור ל-Odoo** | ✅ | XML-RPC working |
| **Authentication** | ✅ | UID: 2 |
| **חיפוש מטופלים** | ✅ | עם RBAC |
| **קריאת פרטי מטופל** | ✅ | עם RBAC |
| **יצירת מטופל** | ✅ | Staff only |
| **עדכון מטופל** | ✅ | עם RBAC |
| **רשימת רופאים** | ✅ | All users |
| **חיפוש תורים** | ✅ | Read only |
| **קריאת תור** | ✅ | Read only |

### מה לא עובד ❌

| תכונה | סטטוס | בעיה |
|-------|--------|------|
| **יצירת תור** | ❌ | Constraint error on doctor_id |
| **עדכון תור** | ❓ | לא נבדק |
| **מחיקת תור** | ❓ | לא נבדק |
| **חשבוניות** | ❌ | לא מיושם |
| **טיפולים/שירותים** | ❌ | לא מיושם |
| **תשלומים** | ❌ | לא מיושם |

---

## 🚧 משימות לסיום

### קריטי 🔴

1. **תיקון create_appointment**
   - לברר מה הבעיה עם doctor_id constraint
   - לבדוק אם צריך שדות נוספים
   - לבדוק workflow ב-Odoo UI
   - לתקן ב-OdooClient

2. **Billing Integration**
   - לממש get_patient_invoices
   - לממש get_invoice_details
   - לממש create_invoice (אם נדרש)
   - לחבר ל-Marcus tools

### חשוב 🟡

3. **Appointment Slots**
   - לממש get_available_slots עם Odoo
   - לבדוק אם יש מודל calendar.event
   - לבדוק אם יש resource.calendar

4. **Treatment/Services**
   - לממש get_treatments
   - לממש get_treatment_price
   - לחבר ל-product.product

### רצוי 🟢

5. **Advanced Features**
   - Treatment notes
   - Medical history
   - Prescriptions
   - X-rays/images

---

## 🔍 איך לחקור Odoo

### דרך UI (מומלץ)

1. התחבר ל-https://dentaflow.ai
2. לך ל-Settings → Technical → Database Structure → Models
3. חפש את המודל (למשל `medical.appointment`)
4. לחץ על "Fields" לראות שדות
5. נסה ליצור רשומה ידנית ב-UI
6. בדוק מה השדות הנדרשים

### דרך Python

```python
import xmlrpc.client

url = "https://dentaflow.ai"
db = "dental_prod"
username = "admin"
password = "DentaFlow2024"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

uid = common.authenticate(db, username, password, {})

# Get model fields
fields = models.execute_kw(
    db, uid, password,
    'medical.appointment', 'fields_get',
    [],
    {'attributes': ['string', 'type', 'required', 'help', 'selection']}
)

# Print required fields
for name, info in fields.items():
    if info.get('required'):
        print(f"{name}: {info.get('string')} ({info.get('type')})")
```

---

## 📝 סיכום

**מה יש לנו:**
- ✅ חיבור יציב ל-Odoo 19.0
- ✅ ניהול מטופלים מלא עם RBAC
- ✅ רשימת רופאים
- ✅ קריאת תורים

**מה חסר:**
- ❌ יצירת תורים (בעיית constraint)
- ❌ חשבוניות ותשלומים
- ❌ טיפולים ושירותים

**הצעד הבא:**
1. לפתור את בעיית create_appointment
2. לממש billing integration
3. להחליף את כל ה-Mock tools ב-Odoo אמיתי

---

**מסמך זה מתעדכן ככל שנלמד יותר על Odoo!** 📚
