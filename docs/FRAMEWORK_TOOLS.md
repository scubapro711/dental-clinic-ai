# 🛠️ Framework Tools - מדריך שימוש

**תאריך:** 3 באוקטובר 2025  
**גרסה:** 1.0  
**Framework:** Improved Holistic Framework V2.0

---

## 📋 סקירה כללית

המסגרת כוללת מספר כלים אוטומטיים שעוזרים לשמור על איכות הקוד, תיעוד מסודר, וסנכרון בין תכנון למימוש.

---

## 🔧 הכלים

### 1. ADR System (Architecture Decision Records)

**מיקום:** `docs/adr/`

**מה זה עושה:**
- מתעד החלטות ארכיטקטוניות חשובות
- שומר את ההיסטוריה של "למה" ולא רק "מה"
- עוזר לאנשים חדשים להבין את ההחלטות

**איך משתמשים:**

```bash
# צור ADR חדש
cd docs/adr
cp TEMPLATE.md ADR-005-your-decision-title.md

# ערוך את הקובץ
# מלא את כל הסעיפים:
# - Status (Proposed/Accepted/Deprecated/Superseded)
# - Context (מה הבעיה?)
# - Decision (מה החלטנו?)
# - Consequences (מה ההשלכות?)
# - Alternatives Considered (אילו אופציות שקלנו?)

# Commit
git add ADR-005-your-decision-title.md
git commit -m "docs(adr): Add ADR-005 - Your Decision Title"
```

**מתי ליצור ADR:**
- ✅ שינוי ארכיטקטורה (למשל: מעבר מ-4 agents ל-Alex)
- ✅ בחירת טכנולוגיה (למשל: LangGraph vs OpenManus)
- ✅ החלטה על deployment (למשל: AWS vs Railway)
- ✅ שינוי במודל העסקי (למשל: תמחור)
- ✅ הסרה/דחיית תכונות (למשל: Portfolio A agents)
- ❌ bug fixes קטנים
- ❌ שינויי UI קטנים

**ADRs קיימים:**
- ADR-001: Merge 4 agents into Alex
- ADR-002: OpenManus to LangGraph migration
- ADR-003: Defer Portfolio A to post-MVP
- ADR-004: Hybrid architecture (3 agents)

---

### 2. Pre-Commit Validation

**מיקום:** `.git/hooks/pre-commit`

**מה זה עושה:**
- רץ אוטומטית לפני כל commit
- בודק שהקוד עומד בסטנדרטים
- מונע commits שגויים

**בדיקות שמתבצעות:**

1. **Python Syntax**
   ```bash
   # בודק שאין syntax errors
   python -m py_compile file.py
   ```

2. **Tests**
   ```bash
   # רץ את כל הטסטים
   pytest backend/tests/ --maxfail=1
   ```

3. **Feature Inventory Sync**
   ```bash
   # בודק שהתכונות מסונכרנות
   python scripts/check_work_plan_sync.py
   ```

4. **Sensitive Data**
   ```bash
   # בודק שאין passwords/tokens בקוד
   grep -r "password\|token\|secret" --exclude-dir=.git
   ```

**איך לדלג (במקרי חירום בלבד!):**
```bash
git commit --no-verify -m "emergency fix"
```

⚠️ **אזהרה:** השתמש ב-`--no-verify` רק במקרי חירום אמיתיים!

---

### 3. Commit Message Validation

**מיקום:** `.git/hooks/commit-msg`

**מה זה עושה:**
- בודק שהודעות commit עוקבות אחרי conventional commits
- מוודא שיש Manus-Session-ID (אם רלוונטי)

**פורמט נדרש:**

```
<type>(<scope>): <subject>

<body>

Manus-Session-ID: <session-id>
Human-Initiator: <name>
```

**סוגי commits:**
- `feat`: תכונה חדשה
- `fix`: תיקון באג
- `docs`: שינוי בתיעוד
- `style`: שינויי פורמט (לא משנה לוגיקה)
- `refactor`: שינוי קוד (לא מוסיף תכונה ולא מתקן באג)
- `test`: הוספת טסטים
- `chore`: משימות תחזוקה

**דוגמאות:**

```bash
# טוב ✅
git commit -m "feat(agents): Add Alex unified agent

Merged Dana, Michal, Yosef, Sarah into single Alex agent
for better user experience and simpler architecture.

Manus-Session-ID: abc123
Human-Initiator: Ronen"

# רע ❌
git commit -m "fixed stuff"
```

---

### 4. Work Plan Sync Checker

**מיקום:** `scripts/check_work_plan_sync.py`

**מה זה עושה:**
- משווה בין תוכנית העבודה לקוד בפועל
- מזהה agents שתוכננו אבל לא נבנו
- מזהה agents שנבנו אבל לא בתוכנית

**איך להריץ:**

```bash
cd /path/to/dental-clinic-ai-repo
python3 scripts/check_work_plan_sync.py
```

**פלט לדוגמה:**

```
🔍 Work Plan Sync Check
============================================================
📋 Reading: WORK_PLAN_V19.0_UNIFIED.md

📋 Planned Agents (4):
   - Alex
   - Cfo
   - Option
   - Practice_admin

💻 Actual Agents in Code (1):
   - Alex

❌ Missing Agents (3):
   These agents are planned but not built:
   - Cfo
   - Option
   - Practice_admin

🚨 Work plan and code are OUT OF SYNC!

📝 Action required:
   1. Build missing agents, OR
   2. Remove them from work plan, OR
   3. Create ADR explaining why they're deferred
```

**מה לעשות אם יש אי-התאמה:**

1. **אם agent תוכנן אבל לא נבנה:**
   - בנה אותו, **או**
   - הסר אותו מתוכנית העבודה, **או**
   - צור ADR שמסביר למה הוא נדחה

2. **אם agent נבנה אבל לא בתוכנית:**
   - הוסף אותו לתוכנית העבודה, **או**
   - הסר אותו מהקוד, **או**
   - צור ADR שמסביר את השינוי

---

### 5. Framework Compliance Checker

**מיקום:** `scripts/check_framework_compliance.py`

**מה זה עושה:**
- בודק שהפרויקט עוקב אחרי המסגרת
- מזהה חלקים חסרים
- נותן ציון תאימות

**איך להריץ:**

```bash
cd /path/to/dental-clinic-ai-repo
python3 scripts/check_framework_compliance.py
```

**פלט לדוגמה:**

```
🔍 Framework Compliance Check
============================================================

📋 1. ADR System (Architecture Decision Records)
  ✅ ADR directory (6 files)
  ✅ ADR template
  ✅ ADR README
  ✅ At least 1 ADR created (4 found)

🔧 2. Git Workflow & Validation
  ✅ Git hooks installed (pre-commit, commit-msg)
  ✅ Pre-commit hook script
  ✅ Commit-msg hook script

📊 3. Feature Tracking & Inventory
  ✅ Feature inventory
  ✅ Work plan sync checker
  ✅ PR template

📝 4. Work Plans & Documentation
  ✅ Work plan exists (WORK_PLAN_V19.0_UNIFIED.md)
  ✅ Framework document

🧪 5. Testing Infrastructure
  ✅ Test directory (6 files)
  ✅ Multiple test files (4 found)

🚀 6. CI/CD & Automation
  ✅ GitHub Actions (0 files)
  ✅ Docker Compose

============================================================
📊 Summary: 16/16 checks passed
🎯 Compliance: 100.0%
✅ Excellent! Framework is well implemented.
```

**ציוני תאימות:**
- 90-100%: ✅ מצוין!
- 70-89%: ⚠️ טוב, אבל יש מה לשפר
- 50-69%: ⚠️ בסדר, צריך תשומת לב
- 0-49%: ❌ דורש עבודה משמעותית

---

### 6. Feature Inventory

**מיקום:** `FEATURE_INVENTORY.md`

**מה זה עושה:**
- רשימה מרכזית של כל התכונות
- מעקב אחרי סטטוס (Planned/In Progress/Done)
- מקור אמת יחיד (Single Source of Truth)

**מבנה:**

```markdown
## Epic 1: Authentication & Authorization

| Feature | Status | Priority | Assignee | Notes |
|---------|--------|----------|----------|-------|
| User Registration | ✅ Done | High | Ronen | Completed |
| Login | ✅ Done | High | Ronen | JWT-based |
| Password Reset | 📋 Planned | Medium | - | Post-MVP |
```

**איך לעדכן:**

```bash
# 1. ערוך את הקובץ
vim FEATURE_INVENTORY.md

# 2. עדכן סטטוס
# 📋 Planned → 🔨 In Progress → ✅ Done

# 3. Commit
git add FEATURE_INVENTORY.md
git commit -m "docs: Update feature inventory - Alex agent completed"
```

---

### 7. Pull Request Template

**מיקום:** `.github/PULL_REQUEST_TEMPLATE.md`

**מה זה עושה:**
- מופיע אוטומטית כשיוצרים PR
- מזכיר לבדוק דברים חשובים
- מבטיח איכות גבוהה

**Checklist בPR:**

- [ ] הקוד עובד locally
- [ ] כל הטסטים עוברים
- [ ] עדכנתי תיעוד
- [ ] עדכנתי Feature Inventory
- [ ] יצרתי ADR (אם צריך)
- [ ] הודעת commit תקינה

---

## 🚀 Workflow מומלץ

### תהליך פיתוח רגיל:

```bash
# 1. התחל feature חדש
git checkout -b feature/new-agent

# 2. פתח
vim backend/app/agents/new_agent.py

# 3. בדוק
pytest backend/tests/test_new_agent.py

# 4. עדכן תיעוד
vim FEATURE_INVENTORY.md
# שנה סטטוס מ-Planned ל-Done

# 5. Commit (pre-commit hook ירוץ אוטומטית)
git add .
git commit -m "feat(agents): Add new agent

Implemented new agent with X, Y, Z capabilities.

Manus-Session-ID: abc123
Human-Initiator: Ronen"

# 6. Push
git push origin feature/new-agent

# 7. צור PR (PR template יופיע אוטומטית)
gh pr create --fill

# 8. Review & Merge
```

---

### תהליך החלטה ארכיטקטונית:

```bash
# 1. זיהית צורך בהחלטה
# למשל: להחליף 4 agents ב-Alex אחד?

# 2. צור ADR
cd docs/adr
cp TEMPLATE.md ADR-005-merge-agents.md

# 3. מלא את כל הסעיפים
vim ADR-005-merge-agents.md

# 4. דון עם הצוות (אם יש)

# 5. קבל החלטה → עדכן Status ל-Accepted

# 6. Commit
git add ADR-005-merge-agents.md
git commit -m "docs(adr): Add ADR-005 - Merge 4 agents into Alex"

# 7. מימוש ההחלטה
git checkout -b refactor/merge-agents
# ... עבודה ...

# 8. עדכן תוכנית עבודה
vim WORK_PLAN_V20.0.md
# הסר Dana, Michal, Yosef, Sarah
# הוסף Alex

# 9. עדכן Feature Inventory
vim FEATURE_INVENTORY.md

# 10. Commit הכל
git add .
git commit -m "refactor(agents): Merge 4 agents into Alex

Implements ADR-005. Merged Dana, Michal, Yosef, Sarah
into single unified Alex agent.

Manus-Session-ID: xyz789
Human-Initiator: Ronen"
```

---

## 🐛 Troubleshooting

### בעיה: Pre-commit hook נכשל

```bash
# בדוק מה הבעיה
cat .git/hooks/pre-commit

# הרץ ידנית לראות שגיאות
bash .git/hooks/pre-commit

# אם זה false positive, דלג (חד-פעמי!)
git commit --no-verify -m "..."
```

---

### בעיה: Work plan sync מראה אי-התאמה

```bash
# הרץ את הבדיקה
python3 scripts/check_work_plan_sync.py

# אם agent חסר בקוד:
# 1. בנה אותו, או
# 2. הסר אותו מתוכנית, או
# 3. צור ADR שמסביר למה נדחה

# אם agent חסר בתוכנית:
# 1. הוסף אותו לתוכנית, או
# 2. הסר אותו מהקוד, או
# 3. צור ADR שמסביר את השינוי
```

---

### בעיה: Framework compliance נמוך

```bash
# הרץ בדיקה
python3 scripts/check_framework_compliance.py

# תקן את הדברים החסרים:
# - צור ADRs אם חסרים
# - התקן git hooks אם לא מותקנים
# - צור tests אם חסרים
# - וכו'

# בדוק שוב
python3 scripts/check_framework_compliance.py
```

---

## 📚 קישורים נוספים

- [Improved Holistic Framework V2.0](../IMPROVED_FRAMEWORK_V2.md)
- [Work Plan V19.0](../WORK_PLAN_V19.0_UNIFIED.md)
- [Feature Inventory](../FEATURE_INVENTORY.md)
- [ADR README](adr/README.md)

---

**מסמך זה:** docs/FRAMEWORK_TOOLS.md  
**גרסה:** 1.0  
**תאריך:** 3 באוקטובר 2025  
**סטטוס:** מוכן לשימוש
