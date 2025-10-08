# 🚀 תוכנית עבודה סופית: DentaFlow SaaS v15.0

**תאריך:** 8 באוקטובר 2025  
**גרסת בסיס:** v14.3.0  
**מטרה:** מערכת SaaS מושלמת, מאובטחת ומוכנה לייצור

---

## 📋 תוכן עניינים

1. [עיקרון מנחה](#guiding-principle)
2. [סטטוס נוכחי](#current-status)
3. [ארכיטקטורה כללית](#architecture)
4. [אסטרטגיית פריסה וגיבוי](#deployment-strategy)
5. [תוכנית עבודה - 3 שלבים](#work-plan)
6. [מדדי הצלחה](#success-metrics)

---

<a name="guiding-principle"></a>
## 🎯 עיקרון מנחה: Agent-First + Component-Based

### גישת פיתוח

**1. Agent-First Architecture**
- כל תכונה חדשה = כלי חדש לסוכן
- האינטראקציה דרך שיחה, לא UI מסורתי
- הסוכנים הם הממשק העיקרי

**2. Component-Based Development**
- חלוקה לקומפוננטות קטנות וממוקדות
- כל קומפוננטה מפנה ל-`CONTEXT_AND_GAPS_ANALYSIS.md`
- התגברות על בעיות זיכרון וקונטקסט

**3. Documentation-Driven**
- כל החלטה מבוססת על מחקר מקיף
- קישור למסמכים רלוונטיים בכל משימה
- תיעוד מלא של כל שינוי

---

<a name="current-status"></a>
## 📊 סטטוס נוכחי

### מה שעובד ✅

| רכיב | סטטוס | פירוט |
|------|-------|-------|
| **Multi-Agent System** | ✅ פעיל | LangGraph V3, 3 סוכנים (Alex, Marcus, Sophia) |
| **Agentic Dashboard** | ✅ פעיל | ממשק צ'אט, פאנל שקיפות, ווידג'טים |
| **Odoo Integration** | ✅ חלקי | חיבור פעיל, ניהול מטופלים עובד |
| **Database** | ✅ בסיסי | PostgreSQL עם טבלאות בסיסיות |
| **Security** | ✅ בסיסי | SSL/TLS, RBAC בסיסי |
| **Hebrew & RTL** | ✅ מלא | תמיכה מלאה בעברית |

### מה שחסר ❌

| רכיב | חומרה | השפעה |
|------|--------|--------|
| **organization_memberships table** | 🔴 קריטי | חוסם Multi-Tenancy |
| **clinic_settings table** | 🔴 קריטי | אי אפשר להתאים אישית |
| **treatment_prices table** | 🟡 גבוה | אין ניהול מחירון |
| **AWS Cognito + Google OAuth** | 🔴 קריטי | אבטחה חלשה |
| **JWT with Org Context** | 🟡 גבוה | RBAC לא מלא |
| **Database Encryption** | 🔴 קריטי | לא תואם HIPAA |
| **Audit Logging** | 🔴 קריטי | לא תואם HIPAA |
| **Telegram Bot** | 🟡 בינוני | לא פעיל |
| **WhatsApp Integration** | 🟢 נמוך | לא מיושם |

**מקור:** `GAP_ANALYSIS_REPORT.md` - ניתוח מקיף של כל הפערים

---

<a name="architecture"></a>
## 🏗️ ארכיטקטורה כללית

```
┌─────────────────────────────────────────────────────────────┐
│                    DentaFlow Platform                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Patients   │  │ Clinic Staff │  │ Clinic Owners│      │
│  │              │  │              │  │              │      │
│  │  Telegram    │  │  Web App     │  │  Dashboard   │      │
│  │  WhatsApp    │  │  Mobile      │  │  Analytics   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         └─────────────────┼──────────────────┘               │
│                           │                                  │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │         AWS Cognito (Authentication)              │       │
│  │  - Google OAuth                                   │       │
│  │  - MFA                                            │       │
│  │  - JWT with Org Context                           │       │
│  └──────────────────┬───────────────────────────────┘       │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │         FastAPI Backend (Python)                  │       │
│  │  - JWT Validation                                 │       │
│  │  - RBAC Enforcement                               │       │
│  │  - Audit Logging                                  │       │
│  └──────────────────┬───────────────────────────────┘       │
│                     │                                        │
│         ┌───────────┼───────────┐                           │
│         │           │           │                           │
│         ▼           ▼           ▼                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │  Alex    │ │  Marcus  │ │  Sophia  │                    │
│  │ (Patient)│ │  (CFO)   │ │ (Admin)  │                    │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘                    │
│       │            │            │                           │
│       └────────────┼────────────┘                           │
│                    │                                        │
│                    ▼                                        │
│  ┌─────────────────────────────────────────────┐           │
│  │      LangGraph Supervisor                    │           │
│  │  - Routing Logic                             │           │
│  │  - State Management                          │           │
│  │  - Multi-Turn Conversations                  │           │
│  └─────────────────┬───────────────────────────┘           │
│                    │                                        │
│       ┌────────────┼────────────┐                          │
│       │            │            │                          │
│       ▼            ▼            ▼                          │
│  ┌────────┐  ┌────────┐  ┌────────┐                       │
│  │ Postgre│  │  Odoo  │  │ Redis  │                       │
│  │  SQL   │  │  ERP   │  │ Cache  │                       │
│  │(Encrypt│  │        │  │        │                       │
│  │  ed)   │  │        │  │        │                       │
│  └────────┘  └────────┘  └────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**מקור:** `CONTEXT_AND_GAPS_ANALYSIS.md` - סעיף 2.2

---

<a name="deployment-strategy"></a>
## 🚀 אסטרטגיית פריסה וגיבוי

### עקרון מנחה: Continuous Deployment (פריסה רציפה)

**למה פריסה רציפה?**
- ✅ בדיקה מיידית בסביבת ייצור (Odoo רץ על dentaflow.ai)
- ✅ גילוי באגים מוקדם
- ✅ משוב מהיר מהמערכת האמיתית
- ✅ פחות סיכון (שינויים קטנים)
- ✅ אין הצטברות של שינויים גדולים

---

### 🔄 תהליך עבודה לכל קומפוננטה

```
┌─────────────────────────────────────────────────────────────┐
│  1. פיתוח מקומי                                             │
│     - כתיבת קוד                                             │
│     - בדיקות יחידה (unit tests)                             │
│     - בדיקה מקומית                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. גיבוי לוקאלי                                            │
│     git add .                                               │
│     git commit -m "feat: [component-name]"                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. דחיפה ל-GitHub                                          │
│     git push origin branch-4                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. פריסה ל-EC2 (dentaflow.ai)                             │
│     ssh ubuntu@dentaflow.ai                                 │
│     cd /var/www/dental-clinic-ai                            │
│     git pull origin branch-4                                │
│     source venv/bin/activate                                │
│     pip install -r requirements.txt (אם צריך)              │
│     alembic upgrade head (אם יש migrations)                │
│     sudo systemctl restart dentaflow-backend                │
│     sudo systemctl restart dentaflow-frontend               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. בדיקות Smoke                                            │
│     curl https://dentaflow.ai/api/health                    │
│     בדיקה ידנית בממשק                                       │
│     בדיקה ב-Odoo שהאינטגרציה עובדת                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. תיעוד                                                   │
│     עדכון CHANGELOG.md                                      │
│     תיוג גרסה (אם צריך)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

### 📝 מוסכמות Git Commit

**פורמט:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: תכונה חדשה
- `fix`: תיקון באג
- `docs`: שינוי בתיעוד
- `style`: שינויי פורמט (לא משפיע על קוד)
- `refactor`: שינוי קוד (לא תכונה ולא באג)
- `test`: הוספת בדיקות
- `chore`: משימות תחזוקה

**דוגמאות:**
```bash
git commit -m "feat(memberships): add organization_memberships table and model"
git commit -m "fix(odoo): resolve appointment creation constraint error"
git commit -m "docs(readme): update installation instructions"
```

---

### 💾 תוכנית גיבויים

#### 1. גיבוי קוד (Git)

**תדירות:** אחרי כל קומפוננטה

**מיקומים:**
- ✅ GitHub Repository: `scubapro711/dental-clinic-ai` (branch-4)
- ✅ Local: `/home/ubuntu/dental-clinic-ai`
- ✅ EC2: `/var/www/dental-clinic-ai`

**שמירת נקודות חשובות:**
```bash
# אחרי כל שלב מרכזי - צור tag
git tag -a v15.1-memberships -m "Completed organization memberships"
git push origin v15.1-memberships
```

---

#### 2. גיבוי מסד נתונים (PostgreSQL)

**תדירות:** 
- 🔴 **לפני כל migration** (חובה!)
- 🟡 **אחרי כל שלב** (מומלץ)
- 🟢 **אוטומטי יומי** (cron job)

**סקריפט גיבוי:**
```bash
#!/bin/bash
# backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/dentaflow"
DB_NAME="dentalai"

mkdir -p $BACKUP_DIR

# Full backup
pg_dump -U dentalai -h localhost $DB_NAME | gzip > $BACKUP_DIR/dentaflow_$DATE.sql.gz

# Keep only last 30 backups
ls -t $BACKUP_DIR/dentaflow_*.sql.gz | tail -n +31 | xargs rm -f

echo "Backup completed: dentaflow_$DATE.sql.gz"
```

**שימוש:**
```bash
# לפני migration
./backup-db.sh

# שחזור (אם צריך)
gunzip < /var/backups/dentaflow/dentaflow_20251008_120000.sql.gz | psql -U dentalai -h localhost dentalai
```

**גיבוי אוטומטי (cron):**
```bash
# הוסף ל-crontab
crontab -e

# גיבוי יומי ב-3:00 בלילה
0 3 * * * /var/www/dental-clinic-ai/scripts/backup-db.sh
```

---

#### 3. גיבוי קבצים (אם יש uploads)

**תדירות:** יומי

```bash
#!/bin/bash
# backup-files.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/var/backups/dentaflow/files"
SOURCE_DIR="/var/www/dental-clinic-ai/uploads"

mkdir -p $BACKUP_DIR

# Sync to backup directory
rsync -av --delete $SOURCE_DIR/ $BACKUP_DIR/current/

# Create daily snapshot
tar -czf $BACKUP_DIR/files_$DATE.tar.gz -C $BACKUP_DIR current/

# Keep only last 7 days
ls -t $BACKUP_DIR/files_*.tar.gz | tail -n +8 | xargs rm -f
```

---

#### 4. גיבוי Odoo (חשוב!)

**Odoo רץ על dentaflow.ai - צריך גיבוי נפרד!**

```bash
# גיבוי Odoo database
pg_dump -U odoo -h localhost odoo_db | gzip > /var/backups/odoo/odoo_$(date +%Y%m%d).sql.gz

# גיבוי Odoo filestore
tar -czf /var/backups/odoo/filestore_$(date +%Y%m%d).tar.gz /var/lib/odoo/.local/share/Odoo/filestore/
```

---

### 🔄 תהליך Rollback (חזרה אחורה)

**אם משהו נשבר אחרי פריסה:**

```bash
# 1. חזור לגרסה קודמת בקוד
cd /var/www/dental-clinic-ai
git log --oneline  # ראה את ההיסטוריה
git reset --hard <commit-hash>  # חזור לקומיט הקודם

# 2. שחזר מסד נתונים (אם צריך)
gunzip < /var/backups/dentaflow/dentaflow_YYYYMMDD_HHMMSS.sql.gz | psql -U dentalai dentalai

# 3. Restart services
sudo systemctl restart dentaflow-backend
sudo systemctl restart dentaflow-frontend

# 4. בדוק שהכל עובד
curl https://dentaflow.ai/api/health
```

---

### 📊 Checklist לכל קומפוננטה

```markdown
## קומפוננטה X.X: [שם]

### לפני התחלה
- [ ] גיבוי מסד נתונים
- [ ] git pull (וודא שאתה מעודכן)
- [ ] בדיקת סטטוס: git status

### פיתוח
- [ ] כתיבת קוד
- [ ] בדיקות מקומיות
- [ ] תיעוד (docstrings, comments)

### גיבוי ופריסה
- [ ] git add .
- [ ] git commit -m "feat(scope): description"
- [ ] git push origin branch-4
- [ ] SSH ל-EC2
- [ ] git pull
- [ ] alembic upgrade head (אם יש migrations)
- [ ] restart services
- [ ] smoke tests

### אימות
- [ ] API עובד
- [ ] Odoo integration עובד
- [ ] אין errors ב-logs
- [ ] עדכון CHANGELOG.md

### תיעוד
- [ ] עדכון תוכנית העבודה (✅ סומן כהושלם)
```

---

### 🎯 סיכום

**עקרונות מפתח:**
1. ✅ **גבה לפני כל שינוי קריטי** (במיוחד migrations)
2. ✅ **commit קטנים ותכופים** - קל יותר לחזור אחורה
3. ✅ **פרוס אחרי כל קומפוננטה** - בדיקה מיידית
4. ✅ **בדוק smoke tests** - וודא שהכל עובד
5. ✅ **תעד** - עדכן CHANGELOG ותוכנית העבודה

---

<a name="work-plan"></a>
## 📅 תוכנית עבודה - 3 שלבים (6 שבועות)

### 🔵 שלב 1: יסודות ותשתית (שבועות 1-2)

**מטרה:** תיקון פערים קריטיים במסד הנתונים ו-Authentication

---

#### 📦 קומפוננטה 1.1: טבלת organization_memberships

**חומרה:** 🔴 קריטי  
**זמן:** 2 ימים  
**תלויות:** אין

**הקשר:**
> מסמך: `CONTEXT_AND_GAPS_ANALYSIS.md` - סעיף 1.2, 2.1  
> בעיה: משתמש לא יכול להיות חבר במספר מרפאות, לא ניתן לקשר User ל-Patient ב-Odoo  
> פתרון: יצירת טבלת מיפוי עם קישור ל-Odoo

**משימות:**

**יום 1: Database Migration**
```bash
# 1. יצירת migration חדש
cd backend
alembic revision -m "add_organization_memberships_table"

# 2. עריכת הקובץ החדש ב-alembic/versions/
```

```python
# alembic/versions/XXXXX_add_organization_memberships_table.py
def upgrade():
    op.create_table(
        'organization_memberships',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('organization_role', sa.String(50), nullable=False),
        sa.Column('functional_role', sa.String(50), nullable=True),
        sa.Column('odoo_partner_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'organization_id', name='uq_user_org')
    )
    
    # Indexes
    op.create_index('ix_memberships_user', 'organization_memberships', ['user_id'])
    op.create_index('ix_memberships_org', 'organization_memberships', ['organization_id'])
    op.create_index('ix_memberships_odoo', 'organization_memberships', ['odoo_partner_id'])

def downgrade():
    op.drop_table('organization_memberships')
```

```bash
# 3. הרצת migration
alembic upgrade head
```

**יום 2: Model + API**
```python
# backend/app/models/organization_membership.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class OrganizationMembership(Base):
    """User membership in organization with Odoo link."""
    __tablename__ = "organization_memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    # Roles
    organization_role = Column(String(50), nullable=False)  # owner, manager, staff, patient
    functional_role = Column(String(50), nullable=True)  # dentist, hygienist, receptionist, etc.
    
    # Odoo link
    odoo_partner_id = Column(Integer, nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_org'),
    )
```

```python
# backend/app/api/v1/endpoints/memberships.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.organization_membership import OrganizationMembership
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/api/v1/organizations/{org_id}/memberships")
async def list_memberships(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all members of an organization."""
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == org_id,
        OrganizationMembership.is_active == True
    ).all()
    
    return memberships

@router.post("/api/v1/organizations/{org_id}/memberships")
async def add_member(
    org_id: UUID,
    user_id: UUID,
    organization_role: str,
    functional_role: str = None,
    odoo_partner_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a user to an organization."""
    membership = OrganizationMembership(
        user_id=user_id,
        organization_id=org_id,
        organization_role=organization_role,
        functional_role=functional_role,
        odoo_partner_id=odoo_partner_id
    )
    
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    return membership
```

**בדיקות:**
```python
# backend/tests/test_memberships.py
def test_create_membership():
    """Test creating organization membership."""
    # Test code here
    pass

def test_user_multiple_orgs():
    """Test user can be member of multiple organizations."""
    # Test code here
    pass

def test_odoo_link():
    """Test Odoo partner_id link."""
    # Test code here
    pass
```

**קבצים לעדכן:**
- ✅ `alembic/versions/XXXXX_add_organization_memberships_table.py`
- ✅ `app/models/organization_membership.py`
- ✅ `app/models/__init__.py` (הוסף import)
- ✅ `app/api/v1/endpoints/memberships.py`
- ✅ `app/api/v1/__init__.py` (הוסף router)
- ✅ `tests/test_memberships.py`

**הצלחה מוגדרת:**
- ✅ Migration רץ בהצלחה
- ✅ ניתן ליצור membership חדש
- ✅ משתמש יכול להיות חבר ב-2+ מרפאות
- ✅ קישור ל-Odoo עובד

---

#### 📦 קומפוננטה 1.2: טבלת clinic_settings

**חומרה:** 🔴 קריטי  
**זמן:** 1 יום  
**תלויות:** קומפוננטה 1.1

**הקשר:**
> מסמך: `CONTEXT_AND_GAPS_ANALYSIS.md` - סעיף 1.2, 3.1  
> מסמך: `DENTAL_CLINIC_OPERATIONS_RESEARCH.md` - שעות פעילות, הגדרות תורים  
> בעיה: כל מרפאה צריכה הגדרות משלה (שעות, מחירים, תקשורת)  
> פתרון: טבלת הגדרות לכל organization

**משימות:**

```python
# alembic/versions/XXXXX_add_clinic_settings_table.py
def upgrade():
    op.create_table(
        'clinic_settings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False, unique=True),
        
        # Operating hours (based on Israeli clinic research)
        sa.Column('sunday_open', sa.Time(), nullable=True),
        sa.Column('sunday_close', sa.Time(), nullable=True),
        sa.Column('monday_open', sa.Time(), nullable=True),
        sa.Column('monday_close', sa.Time(), nullable=True),
        sa.Column('tuesday_open', sa.Time(), nullable=True),
        sa.Column('tuesday_close', sa.Time(), nullable=True),
        sa.Column('wednesday_open', sa.Time(), nullable=True),
        sa.Column('wednesday_close', sa.Time(), nullable=True),
        sa.Column('thursday_open', sa.Time(), nullable=True),
        sa.Column('thursday_close', sa.Time(), nullable=True),
        sa.Column('friday_open', sa.Time(), nullable=True),
        sa.Column('friday_close', sa.Time(), nullable=True),
        sa.Column('saturday_open', sa.Time(), nullable=True),
        sa.Column('saturday_close', sa.Time(), nullable=True),
        
        # Appointment settings (from research)
        sa.Column('default_appointment_duration', sa.Integer(), default=30),
        sa.Column('buffer_between_appointments', sa.Integer(), default=10),
        sa.Column('advance_booking_days', sa.Integer(), default=60),
        sa.Column('cancellation_notice_hours', sa.Integer(), default=24),
        sa.Column('no_show_fee', sa.Numeric(10, 2), default=100.00),
        
        # Communication
        sa.Column('sms_enabled', sa.Boolean(), default=True),
        sa.Column('email_enabled', sa.Boolean(), default=True),
        sa.Column('whatsapp_enabled', sa.Boolean(), default=False),
        sa.Column('telegram_enabled', sa.Boolean(), default=False),
        sa.Column('reminder_hours_before', sa.Integer(), default=24),
        
        # Billing (Israeli market)
        sa.Column('currency', sa.String(3), default='ILS'),
        sa.Column('tax_rate', sa.Numeric(5, 2), default=17.00),
        sa.Column('payment_methods', sa.JSON(), default=['cash', 'credit_card', 'bank_transfer', 'bit']),
        
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
```

**ערכי ברירת מחדל (מתוך המחקר):**
```python
DEFAULT_ISRAELI_CLINIC_SETTINGS = {
    "sunday_open": "08:00",
    "sunday_close": "18:00",
    "monday_open": "08:00",
    "monday_close": "18:00",
    "tuesday_open": "08:00",
    "tuesday_close": "18:00",
    "wednesday_open": "08:00",
    "wednesday_close": "18:00",
    "thursday_open": "08:00",
    "thursday_close": "18:00",
    "friday_open": "08:00",
    "friday_close": "13:00",  # Half day for Shabbat
    "saturday_open": None,  # Closed
    "saturday_close": None,
    "default_appointment_duration": 30,
    "buffer_between_appointments": 10,
    "currency": "ILS",
    "tax_rate": 17.00,
    "payment_methods": ["cash", "credit_card", "bank_transfer", "bit"]
}
```

**קבצים לעדכן:**
- ✅ `alembic/versions/XXXXX_add_clinic_settings_table.py`
- ✅ `app/models/clinic_settings.py`
- ✅ `app/api/v1/endpoints/clinic_settings.py`
- ✅ `app/services/clinic_settings_service.py`

---

#### 📦 קומפוננטה 1.3: טבלת treatment_prices

**חומרה:** 🟡 גבוה  
**זמן:** 1 יום  
**תלויות:** קומפוננטה 1.1

**הקשר:**
> מסמך: `DENTAL_CLINIC_OPERATIONS_RESEARCH.md` - טבלת מחירים ישראלית  
> בעיה: כל מרפאה קובעת מחירים משלה  
> פתרון: טבלת מחירים לכל organization עם ערכי ברירת מחדל

**משימות:**

```python
# alembic/versions/XXXXX_add_treatment_prices_table.py
def upgrade():
    op.create_table(
        'treatment_prices',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('treatment_code', sa.String(50), nullable=False),
        sa.Column('treatment_name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), default=30),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'treatment_code', name='uq_org_treatment')
    )
    
    op.create_index('ix_treatment_prices_org', 'treatment_prices', ['organization_id'])
    op.create_index('ix_treatment_prices_code', 'treatment_prices', ['treatment_code'])
```

**מחירון ברירת מחדל (מתוך המחקר):**
```python
DEFAULT_ISRAELI_TREATMENT_PRICES = [
    {"code": "CHECKUP", "name": "בדיקה שגרתית", "category": "preventive", "price": 200, "duration": 30},
    {"code": "CLEANING", "name": "ניקוי אבנית", "category": "preventive", "price": 300, "duration": 45},
    {"code": "FILLING_SIMPLE", "name": "סתימה פשוטה", "category": "restorative", "price": 500, "duration": 45},
    {"code": "ROOT_CANAL", "name": "טיפול שורש", "category": "restorative", "price": 1500, "duration": 90},
    {"code": "CROWN", "name": "כתר חרסינה", "category": "restorative", "price": 2500, "duration": 90},
    {"code": "IMPLANT", "name": "שתל דנטלי", "category": "surgical", "price": 5000, "duration": 120},
    {"code": "EXTRACTION_SIMPLE", "name": "עקירה פשוטה", "category": "surgical", "price": 400, "duration": 30},
    {"code": "WHITENING", "name": "הלבנת שיניים", "category": "cosmetic", "price": 1000, "duration": 60},
]
```

**קבצים לעדכן:**
- ✅ `alembic/versions/XXXXX_add_treatment_prices_table.py`
- ✅ `app/models/treatment_price.py`
- ✅ `app/api/v1/endpoints/treatment_prices.py`
- ✅ `app/services/treatment_price_service.py`
- ✅ `app/scripts/seed_default_prices.py`

---

#### 📦 קומפוננטה 1.4: AWS Cognito + Google OAuth

**חומרה:** 🔴 קריטי  
**זמן:** 3 ימים  
**תלויות:** אין

**הקשר:**
> מסמך: `GAP_ANALYSIS_REPORT.md` - סעיף 4 (Authentication)  
> בעיה: אין אימות מאובטח, אין Social Login  
> פתרון: AWS Cognito עם Google OAuth

**משימות:**

**יום 1: הגדרת AWS Cognito**
```bash
# 1. יצירת User Pool
aws cognito-idp create-user-pool \
  --pool-name dentaflow-users \
  --auto-verified-attributes email \
  --username-attributes email \
  --mfa-configuration OPTIONAL

# 2. יצירת App Client
aws cognito-idp create-user-pool-client \
  --user-pool-id <USER_POOL_ID> \
  --client-name dentaflow-web \
  --generate-secret \
  --allowed-o-auth-flows "code" "implicit" \
  --allowed-o-auth-scopes "openid" "email" "profile" \
  --callback-urls "https://dentaflow.ai/auth/callback" \
  --supported-identity-providers "Google" "COGNITO"

# 3. הוספת Google IdP
aws cognito-idp create-identity-provider \
  --user-pool-id <USER_POOL_ID> \
  --provider-name Google \
  --provider-type Google \
  --provider-details '{
    "client_id": "<GOOGLE_CLIENT_ID>",
    "client_secret": "<GOOGLE_CLIENT_SECRET>",
    "authorize_scopes": "profile email openid"
  }'
```

**יום 2: אינטגרציה ב-Backend**
```python
# backend/app/core/auth.py
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import requests

security = HTTPBearer()

COGNITO_REGION = "eu-west-1"
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")

# Get Cognito public keys
COGNITO_JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
jwks = requests.get(COGNITO_JWKS_URL).json()

def verify_cognito_token(token: str) -> dict:
    """Verify and decode Cognito JWT token."""
    try:
        header = jwt.get_unverified_header(token)
        kid = header['kid']
        key = next((k for k in jwks['keys'] if k['kid'] == kid), None)
        
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        payload = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            audience=COGNITO_APP_CLIENT_ID,
            options={"verify_exp": True}
        )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def get_current_user(credentials = Depends(security)) -> dict:
    """Get current user from Cognito token."""
    token = credentials.credentials
    payload = verify_cognito_token(token)
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "name": payload.get("name"),
        "email_verified": payload.get("email_verified")
    }
```

**יום 3: אינטגרציה ב-Frontend**
```javascript
// frontend/src/auth/cognito.js
import { CognitoUserPool } from 'amazon-cognito-identity-js';

const poolData = {
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID
};

const userPool = new CognitoUserPool(poolData);

export const signInWithGoogle = () => {
  const domain = import.meta.env.VITE_COGNITO_DOMAIN;
  const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
  const redirectUri = encodeURIComponent(window.location.origin + '/auth/callback');
  
  const googleAuthUrl = `https://${domain}/oauth2/authorize?` +
    `identity_provider=Google&` +
    `redirect_uri=${redirectUri}&` +
    `response_type=code&` +
    `client_id=${clientId}&` +
    `scope=openid email profile`;
  
  window.location.href = googleAuthUrl;
};
```

**קבצים לעדכן:**
- ✅ `backend/app/core/auth.py`
- ✅ `backend/app/api/dependencies.py`
- ✅ `frontend/src/auth/cognito.js`
- ✅ `frontend/src/components/LoginButton.jsx`
- ✅ `.env` (הוסף משתני Cognito)

**מקור מפורט:** `GAP_ANALYSIS_REPORT.md` - סעיף 4

---

#### 📦 קומפוננטה 1.5: JWT עם Organization Context

**חומרה:** 🟡 גבוה  
**זמן:** 2 ימים  
**תלויות:** קומפוננטה 1.1, 1.4

**הקשר:**
> מסמך: `GAP_ANALYSIS_REPORT.md` - סעיף 5  
> בעיה: JWT לא מכיל מידע על המרפאות של המשתמש  
> פתרון: Custom Claims ב-Cognito

**משימות:**

```python
# backend/app/core/auth.py (המשך)

async def get_current_user_with_orgs(
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current user with organization memberships."""
    # Verify token
    payload = verify_cognito_token(credentials.credentials)
    user_id = payload.get("sub")
    
    # Load user from database
    user = db.query(User).filter(User.cognito_sub == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Load memberships
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.is_active == True
    ).all()
    
    return {
        "user_id": user.id,
        "email": user.email,
        "name": user.full_name,
        "organizations": [
            {
                "organization_id": m.organization_id,
                "organization_role": m.organization_role,
                "functional_role": m.functional_role,
                "odoo_partner_id": m.odoo_partner_id
            }
            for m in memberships
        ],
        "current_organization_id": memberships[0].organization_id if memberships else None
    }
```

**קבצים לעדכן:**
- ✅ `backend/app/core/auth.py`
- ✅ `backend/app/models/user.py` (הוסף `cognito_sub`)
- ✅ `backend/app/api/v1/endpoints/auth.py`

---

### סיכום שלב 1

**זמן כולל:** 9 ימי עבודה (שבועיים)

**תוצרים:**
- ✅ 3 טבלאות חדשות במסד הנתונים
- ✅ AWS Cognito מוגדר עם Google OAuth
- ✅ JWT מכיל Organization Context
- ✅ Multi-Tenancy מלא

**מדדי הצלחה:**
- ✅ משתמש יכול להיות חבר ב-2+ מרפאות
- ✅ התחברות עם Google עובדת
- ✅ כל מרפאה יכולה להגדיר שעות ומחירים משלה

---

### 🔵 שלב 2: אבטחה ותאימות (שבועות 3-4)

**מטרה:** הפיכת המערכת לתואמת HIPAA ומאובטחת לייצור

---

#### 📦 קומפוננטה 2.1: הצפנת מסד נתונים

**חומרה:** 🔴 קריטי  
**זמן:** 2 ימים  
**תלויות:** אין

**הקשר:**
> מסמך: `GAP_ANALYSIS_REPORT.md` - סעיף 8  
> מסמך: `CONTEXT_AND_GAPS_ANALYSIS.md` - סעיף 4.1  
> בעיה: נתונים רגישים לא מוצפנים  
> פתרון: הצפנה ברמת שדה + RDS encryption

**משימות:**

**יום 1: Field-Level Encryption**
```python
# backend/app/core/encryption.py
from cryptography.fernet import Fernet
from sqlalchemy import TypeDecorator, String
import os
import boto3

# Get encryption key from AWS KMS
def get_encryption_key():
    """Get encryption key from AWS KMS."""
    kms = boto3.client('kms', region_name='eu-west-1')
    response = kms.decrypt(
        CiphertextBlob=os.getenv("ENCRYPTED_FIELD_KEY").encode()
    )
    return response['Plaintext']

ENCRYPTION_KEY = get_encryption_key()
cipher = Fernet(ENCRYPTION_KEY)

class EncryptedString(TypeDecorator):
    """Encrypted string field type."""
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Encrypt on save."""
        if value is not None:
            return cipher.encrypt(value.encode()).decode()
        return value
    
    def process_result_value(self, value, dialect):
        """Decrypt on load."""
        if value is not None:
            return cipher.decrypt(value.encode()).decode()
        return value
```

**שימוש במודלים:**
```python
# backend/app/models/patient.py (דוגמה)
from app.core.encryption import EncryptedString

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(UUID, primary_key=True)
    name = Column(String(255))
    ssn = Column(EncryptedString(255))  # ✅ מוצפן!
    phone = Column(EncryptedString(20))  # ✅ מוצפן!
    medical_history = Column(EncryptedString)  # ✅ מוצפן!
```

**יום 2: RDS Encryption**
```bash
# Enable encryption at rest for RDS
aws rds modify-db-instance \
  --db-instance-identifier dentaflow-db \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:eu-west-1:ACCOUNT_ID:key/KEY_ID \
  --apply-immediately
```

**קבצים לעדכן:**
- ✅ `backend/app/core/encryption.py`
- ✅ `backend/app/models/*.py` (עדכן שדות רגישים)
- ✅ AWS KMS setup script

---

#### 📦 קומפוננטה 2.2: Audit Logging

**חומרה:** 🔴 קריטי  
**זמן:** 2 ימים  
**תלויות:** אין

**הקשר:**
> מסמך: `GAP_ANALYSIS_REPORT.md` - סעיף 9  
> מסמך: `CONTEXT_AND_GAPS_ANALYSIS.md` - סעיף 4.4  
> בעיה: אין תיעוד גישה למידע רגיש  
> פתרון: מערכת Audit Log מלאה

**משימות:**

```python
# backend/app/services/audit_service.py
from datetime import datetime
from app.models.audit_log import AuditLog
from sqlalchemy.orm import Session

class AuditService:
    """Service for audit logging."""
    
    @staticmethod
    async def log(
        db: Session,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: str = None,
        user_agent: str = None,
        details: dict = None
    ):
        """Log an audit event."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        
        return audit_log

# Decorator for automatic audit logging
def audit_log(action: str, resource_type: str):
    """Decorator to automatically log API calls."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request info
            request = kwargs.get('request')
            current_user = kwargs.get('current_user')
            resource_id = kwargs.get('id') or kwargs.get('patient_id')
            
            # Call original function
            result = await func(*args, **kwargs)
            
            # Log audit event
            await AuditService.log(
                db=kwargs.get('db'),
                user_id=current_user['user_id'],
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id),
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent')
            )
            
            return result
        return wrapper
    return decorator
```

**שימוש:**
```python
# backend/app/api/v1/endpoints/patients.py
from app.services.audit_service import audit_log

@router.get("/api/v1/patients/{patient_id}")
@audit_log(action="VIEW_PATIENT", resource_type="patient")
async def get_patient(
    patient_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get patient details."""
    patient = await patient_service.get(db, patient_id)
    return patient
```

**קבצים לעדכן:**
- ✅ `backend/app/models/audit_log.py` (כבר קיים!)
- ✅ `backend/app/services/audit_service.py`
- ✅ `backend/app/api/v1/endpoints/*.py` (הוסף decorators)

---

#### 📦 קומפוננטה 2.3: תיקון יצירת תורים ב-Odoo

**חומרה:** 🟡 גבוה  
**זמן:** 2 ימים  
**תלויות:** אין

**הקשר:**
> מסמך: `CONTEXT_AND_GAPS_ANALYSIS.md` - סעיף 1.1  
> בעיה: constraint error ביצירת תורים  
> פתרון: בדיקה ותיקון של doctor_id

**משימות:**

**יום 1: חקירה**
```python
# backend/scripts/debug_odoo_appointments.py
from app.integrations.odoo_client import OdooClient

client = OdooClient()

# 1. בדוק מודל medical.appointment
fields = client.models.execute_kw(
    client.db, client.uid, client.password,
    'medical.appointment', 'fields_get',
    [], {'attributes': ['string', 'type', 'required']}
)

print("Fields:", fields)

# 2. בדוק constraints
constraints = client.models.execute_kw(
    client.db, client.uid, client.password,
    'medical.appointment', 'search_read',
    [[]], {'fields': [], 'limit': 1}
)

# 3. נסה ליצור תור עם נתונים מינימליים
try:
    appointment_id = client.models.execute_kw(
        client.db, client.uid, client.password,
        'medical.appointment', 'create',
        [{
            'patient_id': 1,
            'doctor_id': 2,  # נסה ערכים שונים
            'appointment_sdate': '2025-10-15 10:00:00',
            'appointment_edate': '2025-10-15 10:30:00'
        }]
    )
    print(f"Success! Appointment ID: {appointment_id}")
except Exception as e:
    print(f"Error: {e}")
```

**יום 2: תיקון**
```python
# backend/app/agents/tools/alex_odoo_tools.py

@tool
def create_appointment_fixed(
    patient_id: int,
    doctor_id: int,
    appointment_date: str,
    duration_minutes: int = 30
) -> str:
    """Create appointment with proper doctor_id handling."""
    try:
        # 1. Verify doctor exists
        doctor = odoo_client.models.execute_kw(
            odoo_client.db, odoo_client.uid, odoo_client.password,
            'hr.employee', 'search_read',
            [[('id', '=', doctor_id)]],
            {'fields': ['id', 'name'], 'limit': 1}
        )
        
        if not doctor:
            return f"Error: Doctor {doctor_id} not found"
        
        # 2. Calculate end time
        start_dt = datetime.fromisoformat(appointment_date)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # 3. Create appointment
        appointment_id = odoo_client.models.execute_kw(
            odoo_client.db, odoo_client.uid, odoo_client.password,
            'medical.appointment', 'create',
            [{
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'appointment_sdate': start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'appointment_edate': end_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'state': 'draft'
            }]
        )
        
        return f"✅ Appointment created: ID {appointment_id}"
        
    except Exception as e:
        return f"❌ Error creating appointment: {str(e)}"
```

**קבצים לעדכן:**
- ✅ `backend/scripts/debug_odoo_appointments.py`
- ✅ `backend/app/agents/tools/alex_odoo_tools.py`
- ✅ `backend/tests/test_odoo_appointments.py`

---

#### 📦 קומפוננטה 2.4: הפעלת Telegram Bot

**חומרה:** 🟡 בינוני  
**זמן:** 1 יום  
**תלויות:** אין

**הקשר:**
> מסמך: `GAP_ANALYSIS_REPORT.md` - סעיף 6  
> בעיה: קוד קיים אבל לא פעיל  
> פתרון: הגדרת Token ו-Webhook

**משימות:**

```bash
# 1. קבל Token מ-BotFather
# פתח Telegram, חפש @BotFather
# שלח: /newbot
# עקוב אחרי ההוראות
# שמור את ה-Token

# 2. הגדר במשתני סביבה
echo "TELEGRAM_BOT_TOKEN=your-token-here" >> backend/.env

# 3. הרץ סקריפט הגדרה
cd backend/scripts
python setup_telegram_webhook.py --url https://dentaflow.ai

# 4. בדוק
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# 5. בדיקת E2E
# שלח הודעה לבוט בטלגרם
# וודא שמגיעה תשובה מ-Alex
```

**קבצים לעדכן:**
- ✅ `backend/.env` (הוסף TELEGRAM_BOT_TOKEN)
- ✅ `backend/scripts/setup_telegram_webhook.py` (כבר קיים!)
- ✅ `backend/tests/test_telegram_integration.py`

---

### סיכום שלב 2

**זמן כולל:** 7 ימי עבודה (שבועיים)

**תוצרים:**
- ✅ הצפנת מסד נתונים (field-level + RDS)
- ✅ Audit Logging מלא
- ✅ תיקון יצירת תורים ב-Odoo
- ✅ Telegram Bot פעיל

**מדדי הצלחה:**
- ✅ נתונים רגישים מוצפנים
- ✅ כל גישה למידע מתועדת
- ✅ ניתן ליצור תורים ב-Odoo
- ✅ מטופלים יכולים לתקשר בטלגרם

---

### 🔵 שלב 3: שיפורים ותכונות (שבועות 5-6)

**מטרה:** שיפור חוויית משתמש והוספת תכונות מתקדמות

---

#### 📦 קומפוננטה 3.1: שיחות רב-תוריות (Multi-Turn)

**חומרה:** 🟡 בינוני  
**זמן:** 2 ימים  
**תלויות:** אין

**הקשר:**
> מסמך: `CONTEXT_AND_GAPS_ANALYSIS.md` - סעיף 2.2  
> בעיה: Supervisor מסיים אחרי קריאה אחת לסוכן  
> פתרון: עדכון לוגיקת Supervisor

**משימות:**

```python
# backend/app/agents/agent_graph_v3.py

def _supervisor_node(state: GraphState) -> dict:
    """Supervisor decides which agent to call next."""
    messages = state["messages"]
    
    # ✅ הוסף היסטוריה לפרומפט
    conversation_history = "\n".join([
        f"{m['role']}: {m['content']}" 
        for m in messages[-10:]  # Last 10 messages
    ])
    
    prompt = f"""You are a supervisor managing a dental clinic AI system.

Conversation history:
{conversation_history}

Current user message: {messages[-1]['content']}

Available agents:
- alex: Patient care, appointments, medical questions
- marcus: Financial operations, billing, reports
- sophia: Practice management, scheduling, operations

Based on the conversation history and current message, decide:
1. Which agent should handle this? (alex/marcus/sophia)
2. Should we continue the conversation or end? (continue/end)

Respond in JSON format:
{{
    "next_agent": "alex",
    "action": "continue",
    "reasoning": "Patient is asking about appointment availability"
}}
"""
    
    response = llm.invoke(prompt)
    decision = json.loads(response.content)
    
    # ✅ לא מסיימים אוטומטית
    if decision["action"] == "end":
        return {"next": END}
    else:
        return {"next": decision["next_agent"]}
```

**קבצים לעדכן:**
- ✅ `backend/app/agents/agent_graph_v3.py`
- ✅ `backend/tests/test_multi_turn_conversations.py`

---

#### 📦 קומפוננטה 3.2: מערכת הצעות פרואקטיביות

**חומרה:** 🟢 נמוך  
**זמן:** 3 ימים  
**תלויות:** אין

**הקשר:**
> מסמך: `DENTAL_CLINIC_OPERATIONS_RESEARCH.md` - KPIs ומדדים  
> רעיון: המערכת מזהה הזדמנויות ומציעה פעולות  
> דוגמאות: תור מתקרב, חשבונית פתוחה, מטופל לא הגיע 6 חודשים

**משימות:**

```python
# backend/app/services/proactive_suggestions_service.py

class ProactiveSuggestionsService:
    """Generate proactive suggestions for clinic staff."""
    
    @staticmethod
    async def get_suggestions(
        db: Session,
        organization_id: UUID
    ) -> List[dict]:
        """Get all proactive suggestions."""
        suggestions = []
        
        # 1. Upcoming appointments (next 24 hours)
        tomorrow = datetime.now() + timedelta(hours=24)
        upcoming = db.query(Appointment).filter(
            Appointment.organization_id == organization_id,
            Appointment.appointment_date.between(datetime.now(), tomorrow),
            Appointment.status == 'confirmed'
        ).all()
        
        for apt in upcoming:
            suggestions.append({
                "type": "upcoming_appointment",
                "priority": "medium",
                "title": f"תור מתקרב: {apt.patient_name}",
                "description": f"תור מחר ב-{apt.appointment_date.strftime('%H:%M')}",
                "action": "send_reminder",
                "data": {"appointment_id": apt.id}
            })
        
        # 2. Overdue invoices
        overdue = db.query(Invoice).filter(
            Invoice.organization_id == organization_id,
            Invoice.status == 'unpaid',
            Invoice.due_date < datetime.now()
        ).all()
        
        for inv in overdue:
            suggestions.append({
                "type": "overdue_invoice",
                "priority": "high",
                "title": f"חשבונית באיחור: {inv.patient_name}",
                "description": f"חוב: ₪{inv.amount}, באיחור {(datetime.now() - inv.due_date).days} ימים",
                "action": "send_payment_reminder",
                "data": {"invoice_id": inv.id}
            })
        
        # 3. Patients due for recall (6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        due_for_recall = db.query(Patient).filter(
            Patient.organization_id == organization_id,
            Patient.last_visit_date < six_months_ago,
            Patient.is_active == True
        ).all()
        
        for patient in due_for_recall:
            suggestions.append({
                "type": "recall_due",
                "priority": "low",
                "title": f"מטופל לא הגיע 6 חודשים: {patient.name}",
                "description": f"ביקור אחרון: {patient.last_visit_date.strftime('%d/%m/%Y')}",
                "action": "send_recall_message",
                "data": {"patient_id": patient.id}
            })
        
        return sorted(suggestions, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])
```

**קבצים לעדכן:**
- ✅ `backend/app/services/proactive_suggestions_service.py`
- ✅ `backend/app/api/v1/endpoints/suggestions.py`
- ✅ `frontend/src/components/dashboard/ProactiveSuggestionsPanel.jsx`

---

#### 📦 קומפוננטה 3.3: אינטגרציה עם WhatsApp (Twilio)

**חומרה:** 🟢 נמוך  
**זמן:** 2 ימים  
**תלויות:** אין

**הקשר:**
> מסמך: `GAP_ANALYSIS_REPORT.md` - סעיף 7  
> מסמך: `DENTAL_CLINIC_OPERATIONS_RESEARCH.md` - תקשורת  
> בעיה: WhatsApp פופולרי מאוד בישראל אבל לא מיושם  
> פתרון: Twilio WhatsApp API

**משימות:**

```python
# backend/app/integrations/whatsapp_client.py
from twilio.rest import Client
import os

class WhatsAppClient:
    """Twilio WhatsApp integration."""
    
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    def send_message(self, to: str, message: str) -> dict:
        """Send WhatsApp message."""
        try:
            msg = self.client.messages.create(
                from_=f"whatsapp:{self.from_number}",
                to=f"whatsapp:{to}",
                body=message
            )
            
            return {
                "success": True,
                "message_id": msg.sid,
                "status": msg.status
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_template(self, to: str, template_name: str, variables: dict) -> dict:
        """Send WhatsApp template message."""
        # Twilio templates
        pass
```

**קבצים לעדכן:**
- ✅ `backend/app/integrations/whatsapp_client.py`
- ✅ `backend/app/api/v1/endpoints/whatsapp.py`
- ✅ `backend/requirements.txt` (הוסף twilio)

---

### סיכום שלב 3

**זמן כולל:** 7 ימי עבודה (שבועיים)

**תוצרים:**
- ✅ שיחות רב-תוריות עובדות
- ✅ מערכת הצעות פרואקטיביות
- ✅ אינטגרציה עם WhatsApp

**מדדי הצלחה:**
- ✅ שיחות מורכבות עם מספר תורות
- ✅ הצעות אוטומטיות לצוות המרפאה
- ✅ תקשורת בוואטסאפ עובדת

---

## 📊 מדדי הצלחה כוללים

### מדדים טכניים

| מדד | יעד | מדידה |
|-----|-----|-------|
| **Uptime** | 99.9% | CloudWatch |
| **Response Time** | <200ms (p95) | Prometheus |
| **Error Rate** | <0.1% | CloudWatch |
| **Test Coverage** | >80% | pytest-cov |
| **Security Score** | A+ | SSL Labs |

### מדדים עסקיים

| מדד | יעד | מדידה |
|-----|-----|-------|
| **Active Clinics** | 10 | Database |
| **Patient Conversations** | 1,000+ | Database |
| **Patient Satisfaction** | 95%+ | Surveys |
| **No-Show Reduction** | 30%+ | Analytics |
| **Time Saved** | 15 hours/week | Surveys |

---

## 📚 מקורות ומסמכים

### מסמכי ייחוס עיקריים

1. **`CONTEXT_AND_GAPS_ANALYSIS.md`** - המסמך המרכזי עם כל ההקשר הטכני
2. **`GAP_ANALYSIS_REPORT.md`** - ניתוח מקיף של 9 פערים קריטיים
3. **`DENTAL_CLINIC_OPERATIONS_RESEARCH.md`** - מחקר מקיף על תחום מרפאות השיניים
4. **`WORK_PLAN_V19.0_UNIFIED.md`** - תוכנית העבודה הקודמת

### תיעוד חיצוני

- AWS Cognito: https://docs.aws.amazon.com/cognito/
- Twilio WhatsApp: https://www.twilio.com/whatsapp
- LangGraph: https://langchain-ai.github.io/langgraph/
- FastAPI: https://fastapi.tiangolo.com/

---

## ✅ סיכום

תוכנית עבודה זו מספקת:

✅ **גישה מבוססת קומפוננטות** - כל משימה קטנה וממוקדת  
✅ **קישור למסמכי ייחוס** - כל קומפוננטה מפנה למסמך הרלוונטי  
✅ **פתרונות מבוססי מחקר** - כל החלטה מבוססת על מחקר מקיף  
✅ **זמנים ריאליים** - 28 ימי עבודה (7 שבועות)  
✅ **מדדי הצלחה ברורים** - ניתן למדוד התקדמות

**הצעד הבא:** התחל עם קומפוננטה 1.1 - טבלת organization_memberships

🚀 **בהצלחה!**
