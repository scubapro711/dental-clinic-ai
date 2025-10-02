# תוכנית עבודה V16.0 - מערכת AI לניהול מרפאת שיניים
## גירסה נקייה ומעודכנת לפי מסגרת העבודה ההוליסטית

**תאריך עדכון:** 2 באוקטובר 2025  
**גירסה:** 16.0 (Clean & Focused)  
**סטטוס פרויקט:** Phase 1 - 95% Complete (Code) | 20% Complete (Protocol)

---

## 🎯 מטרת המסמך

תוכנית עבודה זו מיושרת **במלואה** עם מסגרת העבודה ההוליסטית המקורית, ומתמקדת **רק** במה שרלוונטי לפרויקט dental-clinic-ai.

**הוסר מהתוכנית:**
- ❌ OpenManus (MongoDB, Redis, Webhooks) - זה רכיב של Manus.im עצמו, לא של הפרויקט
- ❌ דברים שלא קשורים ישירות לפרויקט

**נשאר בתוכנית:**
- ✅ פרוטוקול Git (Manus-Session-ID, commits, artifacts)
- ✅ AWS Secrets Manager (ניהול סודות)
- ✅ manus.im Digital Links API (לינק לsessions)
- ✅ Backup & Recovery (GitHub Actions, S3, RTO/RPO)
- ✅ הפיתוח בפועל (Agents, Odoo, WhatsApp, Deployment)

---

## 📊 סטטוס נוכחי - מה יש ומה חסר

### ✅ מה שמיושם (95% מהקוד)

**Backend - Agents:**
- ✅ Dana (Coordinator) - עם routing logic
- ✅ Michal (Medical) - עם escalation logic
- ✅ Yosef (Billing) - עם Israeli context
- ✅ Sarah (Scheduling) - עם tool integration (availability)
- ✅ LangGraph architecture
- ✅ Error handling + retry logic (3 attempts, exponential backoff)
- ✅ Rate limiting (60 req/min, burst 10)
- ✅ Mock Odoo integration

**Testing:**
- ✅ 17 unit tests
- ✅ 6 integration tests
- ✅ End-to-end agent graph test

**Infrastructure:**
- ✅ Docker setup
- ✅ Basic deployment scripts

### ❌ מה שחסר (פרוטוקול + תשתית)

**פרוטוקול Git (0% מיושם):**
- ❌ Manus-Session-ID בcommits
- ❌ Git bundle backup
- ❌ Artifact management
- ❌ GitHub Actions backup workflow

**AWS Infrastructure (0% מיושם):**
- ❌ AWS Secrets Manager
- ❌ S3 backup bucket
- ❌ S3 Glacier archive
- ❌ IAM roles

**manus.im Integration (0% מיושם):**
- ❌ Digital Links API integration
- ❌ Session export/import

**Backup & Recovery (0% מיושם):**
- ❌ RTO/RPO definition
- ❌ Disaster Recovery drill
- ❌ Recovery runbook

**Production Features (חסר):**
- ❌ Neo4j causal memory (קיים אבל לא מחובר)
- ❌ Real Odoo (יש רק Mock)
- ❌ WhatsApp interface
- ❌ Production deployment
- ❌ Monitoring & alerting

---

## 🚀 Phase 0: הקמת פרוטוקול עבודה תקין (CRITICAL)

**עדיפות:** 🔴 CRITICAL - חובה לפני המשך פיתוח  
**משך זמן:** 8-10 שעות  
**מטרה:** יישום מסגרת העבודה ההוליסטית

---

### Epic 0.1: פרוטוקול Git תקין

**משך זמן:** 3 שעות

#### User Story 0.1.1: יישום Manus-Git Protocol
**משך:** 1.5 שעות

**תיאור:**  
יישום פרוטוקול commit מלא עם Manus-Session-ID כפי שמוגדר במסגרת העבודה.

**Acceptance Criteria:**
- [ ] כל commit כולל את הפורמט הבא:
```
<Type>(<Scope>): <Subject>

<Body>

Manus-Session-ID: <session_id_from_manus_api>
Manus-Task-ID: <specific_task_or_plan_step_id>
Human-Initiator: <username_of_human_who_gave_the_prompt>
```

- [ ] Types נתמכים: feat, fix, docs, style, refactor, test, chore
- [ ] Scope מתאר את האזור (agents, api, infra, etc.)
- [ ] Body מכיל הסבר מפורט
- [ ] Manus-Session-ID מתקבל מ-manus.im API

**דוגמה:**
```
feat(agents): Add error handling to all 4 agents

Implemented comprehensive error handling system with retry logic
(3 attempts, exponential backoff) and rate limiting (60 req/min)
for Dana, Michal, Yosef, and Sarah agents.

- Added RetryHandler class with exponential backoff
- Added RateLimiter class with token bucket algorithm
- Added @handle_agent_errors decorator
- Updated all 4 agents to use error handling

Manus-Session-ID: 20251002-143052
Manus-Task-ID: phase-1.2-agent-migration
Human-Initiator: scubapro711
```

**משימות:**
1. צור `scripts/git_commit_helper.py` - סקריפט Python ליצירת commits
2. צור `.git/hooks/prepare-commit-msg` - Git hook לאכיפת פורמט
3. עדכן `README.md` עם הוראות שימוש
4. בדוק עם commit אמיתי

**קבצים:**
- `scripts/git_commit_helper.py`
- `.git/hooks/prepare-commit-msg`
- `docs/GIT_PROTOCOL.md`

---

#### User Story 0.1.2: Git Bundle Backup
**משך:** 1 שעה

**תיאור:**  
יצירת git bundle אוטומטי לכל commit כפי שמוגדר במסגרת העבודה.

**Acceptance Criteria:**
- [ ] כל commit יוצר git bundle
- [ ] Bundle נשמר ב-`backups/git-bundles/`
- [ ] Bundle format: `<date>-<commit-hash>.bundle`
- [ ] Bundle כולל את כל ההיסטוריה (`--all`)
- [ ] Bundle נבדק אוטומטית (`git bundle verify`)
- [ ] Bundle מועלה ל-S3 (אם AWS credentials מוגדרים)

**משימות:**
1. צור `scripts/create_git_bundle.sh` - סקריפט יצירת bundle
2. צור `.git/hooks/post-commit` - Hook ליצירת bundle אוטומטי
3. צור `backups/git-bundles/.gitkeep` - תיקייה לbundles
4. בדוק שה-bundle עובד (`git clone repo.bundle`)

**קבצים:**
- `scripts/create_git_bundle.sh`
- `.git/hooks/post-commit`
- `backups/git-bundles/.gitkeep`

---

#### User Story 0.1.3: Artifact Management
**משך:** 0.5 שעות

**תיאור:**  
ניהול artifacts (build outputs) כפי שמוגדר במסגרת העבודה.

**Acceptance Criteria:**
- [ ] כל build יוצר artifact עם commit hash
- [ ] Artifact format: `<date>-<commit-hash>.tar.gz`
- [ ] Artifact כולל:
  - קוד המקור (git bundle)
  - קבצי build (אם יש)
  - דוח בדיקות (test results)
  - לוגים (אם רלוונטי)
- [ ] `.gitignore` מעודכן לא לכלול artifacts בגרסה
- [ ] `git describe --always --dirty` משמש לזיהוי גרסה

**משימות:**
1. צור `scripts/create_artifact.sh` - סקריפט יצירת artifact
2. עדכן `.gitignore` להוציא `backups/` ו-`artifacts/`
3. צור `artifacts/.gitkeep`

**קבצים:**
- `scripts/create_artifact.sh`
- `.gitignore` (עדכון)
- `artifacts/.gitkeep`

---

### Epic 0.2: AWS Secrets Manager

**משך זמן:** 2 שעות

#### User Story 0.2.1: הגדרת AWS Secrets Manager
**משך:** 1.5 שעות

**תיאור:**  
הקמת AWS Secrets Manager לניהול סודות כפי שמוגדר במסגרת העבודה.

**Acceptance Criteria:**
- [ ] AWS Secrets Manager מוגדר ב-region: `us-east-1`
- [ ] Secret name: `prod/dental-clinic-ai/secrets`
- [ ] Secret format: JSON
- [ ] שני IAM roles מוגדרים:
  - `HumanDeveloperRole` - גישה מלאה (קריאה + כתיבה)
  - `ManusAgentRole` - קריאה בלבד
- [ ] KMS key מוגדר להצפנה (Customer-Managed Key)
- [ ] Rotation policy: 90 ימים (אופציונלי למפתחות API)
- [ ] CloudTrail logging מופעל
- [ ] Tags: `Project=dental-clinic-ai`, `Environment=production`

**Secret structure:**
```json
{
  "openai_api_key": "sk-...",
  "odoo_url": "https://odoo.example.com",
  "odoo_db": "dental_clinic",
  "odoo_username": "admin",
  "odoo_password": "...",
  "neo4j_uri": "bolt://neo4j.example.com:7687",
  "neo4j_user": "neo4j",
  "neo4j_password": "...",
  "whatsapp_api_token": "...",
  "whatsapp_phone_number": "+972...",
  "jwt_secret_key": "...",
  "database_url": "postgresql://..."
}
```

**משימות:**
1. צור `infrastructure/aws/secrets_manager.tf` - Terraform config
2. צור `infrastructure/aws/iam_roles.tf` - IAM roles
3. צור `scripts/setup_secrets.sh` - סקריפט הקמה
4. עדכן `backend/app/core/config.py` לקרוא מ-Secrets Manager

**קבצים:**
- `infrastructure/aws/secrets_manager.tf`
- `infrastructure/aws/iam_roles.tf`
- `scripts/setup_secrets.sh`

---

#### User Story 0.2.2: אינטגרציה עם Backend
**משך:** 0.5 שעות

**תיאור:**  
שילוב AWS Secrets Manager בקוד Backend.

**Acceptance Criteria:**
- [ ] `settings.py` קורא מ-Secrets Manager
- [ ] Fallback ל-environment variables (למפתחים מקומיים)
- [ ] Cache של secrets (5 דקות TTL)
- [ ] Refresh אוטומטי כשה-secret משתנה
- [ ] Error handling מלא (אם AWS לא זמין)
- [ ] Logging של קריאות ל-Secrets Manager

**משימות:**
1. צור `backend/app/core/secrets.py` - Secrets Manager client
2. עדכן `backend/app/core/config.py` - שימוש ב-secrets client
3. הוסף `boto3` ל-`requirements.txt`
4. בדוק עם environment variables מקומיים

**קבצים:**
- `backend/app/core/secrets.py` (חדש)
- `backend/app/core/config.py` (עדכון)
- `backend/requirements.txt` (עדכון)

---

### Epic 0.3: manus.im Digital Links Integration

**משך זמן:** 1.5 שעות

#### User Story 0.3.1: אינטגרציה עם manus.im API
**משך:** 1.5 שעות

**תיאור:**  
אינטגרציה עם manus.im Digital Links API לקבלת Session ID ולייצוא sessions.

**Acceptance Criteria:**
- [ ] קריאה ל-`https://api.manus.im/api/chat/getSession?sessionId=xxx`
- [ ] קבלת `session_id` מה-API
- [ ] שמירת `session_id` ב-commit message
- [ ] ייצוא session data ל-JSON (אם זמין)
- [ ] שמירת session ב-`manus_sessions/<session_id>.json`
- [ ] Error handling אם API לא זמין

**API Response Example:**
```json
{
  "sessionId": "20251002-143052",
  "userId": "user_123",
  "organizationId": "org_456",
  "events": [...],
  "planUpdate": {...},
  "toolUsed": {...}
}
```

**משימות:**
1. צור `scripts/export_manus_session.py` - סקריפט ייצוא
2. צור `manus_sessions/.gitkeep` - תיקייה לsessions
3. עדכן `scripts/git_commit_helper.py` לקרוא ל-API
4. בדוק עם session ID אמיתי

**קבצים:**
- `scripts/export_manus_session.py`
- `manus_sessions/.gitkeep`
- `scripts/git_commit_helper.py` (עדכון)

---

### Epic 0.4: GitHub Actions Backup Workflow

**משך זמן:** 2 שעות

#### User Story 0.4.1: יצירת Backup Workflow
**משך:** 2 שעות

**תיאור:**  
יצירת GitHub Actions workflow לגיבוי אוטומטי כפי שמוגדר במסגרת העבודה.

**Acceptance Criteria:**
- [ ] Workflow מופעל אוטומטית ב-push ל-`main`
- [ ] Workflow שלבים:
  1. Checkout repository (fetch-depth: 0)
  2. Extract metadata (session_id, commit_hash, timestamp)
  3. Create git bundle
  4. Export Manus session (אם זמין)
  5. Package artifacts (tar + gzip)
  6. Upload to S3
- [ ] S3 bucket: `s3://dental-clinic-ai-backups/`
- [ ] Archive name: `{timestamp}-{commit_hash}.tar.gz`
- [ ] AWS credentials מ-GitHub Secrets
- [ ] Manual trigger נתמך
- [ ] Notification על הצלחה/כישלון (אופציונלי)

**Workflow Example:**
```yaml
name: Holistic Operational Backup
on:
  push:
    branches:
      - main
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Extract Metadata from Commit
        id: metadata
        run: |
          SESSION_ID=$(git log -1 --pretty=%b | grep 'Manus-Session-ID:' | cut -d ' ' -f 2)
          COMMIT_HASH=$(git rev-parse --short HEAD)
          TIMESTAMP=$(date -u +"%Y-%m-%d-%H-%M-%S")
          echo "session_id=$SESSION_ID" >> $GITHUB_OUTPUT
          echo "archive_name=${TIMESTAMP}-${COMMIT_HASH}.tar.gz" >> $GITHUB_OUTPUT
      
      - name: Backup Git Repository
        run: git bundle create repo.bundle --all
      
      - name: Backup Manus Session
        env:
          MANUS_API_TOKEN: ${{ secrets.MANUS_API_TOKEN }}
          SESSION_ID: ${{ steps.metadata.outputs.session_id }}
        run: |
          python3 scripts/export_manus_session.py --session-id $SESSION_ID --output-dir manus_session_data
      
      - name: Package and Encrypt Artifacts
        run: |
          tar -czf ${{ steps.metadata.outputs.archive_name }} repo.bundle manus_session_data/
      
      - name: Upload to S3
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
        run: |
          aws s3 cp ${{ steps.metadata.outputs.archive_name }} s3://dental-clinic-ai-backups/
```

**משימות:**
1. צור `.github/workflows/backup.yml`
2. הוסף GitHub Secrets:
   - `MANUS_API_TOKEN`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
3. צור S3 bucket (אם לא קיים)
4. בדוק ש-workflow רץ בהצלחה

**קבצים:**
- `.github/workflows/backup.yml`

---

### Epic 0.5: Disaster Recovery Planning

**משך זמן:** 1.5 שעות

#### User Story 0.5.1: הגדרת RTO/RPO
**משך:** 0.5 שעות

**תיאור:**  
הגדרת יעדי שחזור (Recovery Time Objective & Recovery Point Objective).

**Acceptance Criteria:**
- [ ] **RPO (Recovery Point Objective):** 1 שעה
  - נקודת השחזור האחרונה היא לכל היותר commit שעבר שעה
  - כל commit נשמר ב-git bundle + S3
- [ ] **RTO (Recovery Time Objective):** 4 שעות
  - זמן מקסימלי לשחזור מלא של המערכת
  - כולל: שחזור קוד, deployment, בדיקות
- [ ] תיעוד מפורט של תהליך השחזור
- [ ] Runbook עם צעדים ברורים

**משימות:**
1. צור `docs/DISASTER_RECOVERY.md` - תיעוד DR
2. צור `docs/RUNBOOK.md` - הוראות שחזור צעד-אחר-צעד
3. הגדר טבלת תפקידים (מי אחראי על מה)

**קבצים:**
- `docs/DISASTER_RECOVERY.md`
- `docs/RUNBOOK.md`

---

#### User Story 0.5.2: Disaster Recovery Drill
**משך:** 1 שעה

**תיאור:**  
תרגיל שחזור מאסון (Disaster Recovery drill) כפי שמוגדר במסגרת העבודה.

**Acceptance Criteria:**
- [ ] תרגיל מתועד עם checklist
- [ ] שלבי התרגיל:
  1. **סימולציה:** מחיקת repository מקומי
  2. **שחזור Git:** `git clone <backup-bucket>/<archive-name>.bundle`
  3. **שחזור Secrets:** קריאה מ-AWS Secrets Manager
  4. **שחזור Manus Session:** טעינת `<Manus-Session-ID>.json`
  5. **Deployment:** הרצת המערכת
  6. **בדיקות:** הרצת tests
- [ ] תיעוד זמני שחזור (האם עומדים ב-RTO?)
- [ ] תיעוד ממצאים ושיפורים
- [ ] דוח תרגיל מפורט

**משימות:**
1. צור `scripts/disaster_recovery_drill.sh` - סקריפט תרגיל
2. הרץ תרגיל אמיתי
3. צור `docs/DR_DRILL_REPORT.md` - דוח תרגיל

**קבצים:**
- `scripts/disaster_recovery_drill.sh`
- `docs/DR_DRILL_REPORT.md`

---

### Epic 0.6: S3 Glacier Archive

**משך זמן:** 1 שעה

#### User Story 0.6.1: הקמת S3 Lifecycle Policy
**משך:** 1 שעה

**תיאור:**  
הקמת ארכיון ארוך-טווח ב-S3 Glacier כפי שמוגדר במסגרת העבודה.

**Acceptance Criteria:**
- [ ] S3 bucket: `dental-clinic-ai-backups`
- [ ] Lifecycle policy:
  - **S3 Standard:** 0-30 ימים (גישה מהירה)
  - **S3 Glacier Deep Archive:** 90+ ימים (ארכיון ארוך-טווח)
- [ ] Retention: 7 שנים
- [ ] Cross-Region Replication (CRR): העתקה ל-region נוסף (אופציונלי)
- [ ] Encryption at rest: AES-256
- [ ] Access logging מופעל
- [ ] Versioning מופעל

**משימות:**
1. צור `infrastructure/aws/s3_lifecycle.tf` - Terraform config
2. הפעל lifecycle policy
3. בדוק ש-backups עוברים ל-Glacier אחרי 90 ימים

**קבצים:**
- `infrastructure/aws/s3_lifecycle.tf`

---

## 📋 טבלת תפקידים ואחריות

| תפקיד | בעל תפקיד ראשי | בעל תפקיד גיבוי | אחריות מרכזית |
|-------|---------------|----------------|---------------|
| **מוביל התאוששות (Recovery Lead)** | CTO / מהלק/ית הנדסה | מהנדס בכיר | מכריע על אירוע אסון; מאשר את הפעלת תוכנית ה-DR; מקבל החלטות סופיות |
| **צוות שחזור טכני** | מובילי/ם Backend מהנדסי/ם | מובילי/ם DevOps מהנדסי/ם | מבצע את פרוטוקול השחזור; משחזר את מאגר ה-Git; מסנכרן Manus; מוודא תקינות |
| **מוביל תקשורת** | מנהל מוצר / מנהל הנדסה | | מנהל את כל התקשורת הפנימית והחיצונית |
| **Manus איש קשר לסוכן** | AI מהנדס שילוב | | אחראי על אימות הקשר המשוחזר-Manus והפעלה מחדש של משימות |
| **מתעד** | כותב טכני / מפתח מוסמך | | מתעד כל צעד במהלך השחזור, לוחות זמנים, חריגות, ולקחים |

---

## 🚀 Phase 1: השלמת Core Agent Architecture (5% נותר)

**עדיפות:** 🟡 HIGH  
**משך זמן:** 4 שעות  
**מטרה:** השלמת 5% האחרונים של Phase 1

---

### Epic 1.1: Neo4j Causal Memory Integration

**משך זמן:** 2 שעות

#### User Story 1.1.1: תיקון Neo4j Authentication
**משך:** 1 שעה

**תיאור:**  
תיקון בעיות חיבור ל-Neo4j והפעלת causal memory.

**Acceptance Criteria:**
- [ ] Neo4j connection working
- [ ] Credentials מ-AWS Secrets Manager
- [ ] Connection pooling מוגדר
- [ ] Health check endpoint: `/health/neo4j`
- [ ] Error handling מלא

**משימות:**
1. עדכן `backend/app/integrations/neo4j_client.py`
2. הוסף credentials ל-AWS Secrets Manager
3. בדוק connection עם `neo4j.ping()`
4. הוסף health check endpoint

**קבצים:**
- `backend/app/integrations/neo4j_client.py` (עדכון)
- `backend/app/api/health.py` (עדכון)

---

#### User Story 1.1.2: אינטגרציה עם Agent Graph
**משך:** 1 שעה

**תיאור:**  
שילוב Neo4j causal memory בסוכנים.

**Acceptance Criteria:**
- [ ] כל agent שומר היסטוריה ב-Neo4j
- [ ] Retrieval של context רלוונטי לפני תשובה
- [ ] Graph relationships:
  - `(User)-[:HAD_CONVERSATION]->(Conversation)`
  - `(Conversation)-[:CONTAINS]->(Message)`
  - `(Message)-[:HANDLED_BY]->(Agent)`
- [ ] Query optimization (indexes)
- [ ] TTL: 90 ימים (GDPR compliance)

**משימות:**
1. עדכן `backend/app/agents/agent_graph.py` - שמירה ב-Neo4j
2. הוסף retrieval logic לפני כל agent call
3. צור indexes ב-Neo4j
4. בדוק עם conversation אמיתי

**קבצים:**
- `backend/app/agents/agent_graph.py` (עדכון)
- `backend/app/integrations/causal_memory.py` (עדכון)

---

### Epic 1.2: Enhanced Tool Integration for Yosef

**משך זמן:** 2 שעות

#### User Story 1.2.1: הוספת Invoice Tools ל-Yosef
**משך:** 2 שעות

**תיאור:**  
הוספת כלים לבדיקת חשבוניות ל-Yosef.

**Acceptance Criteria:**
- [ ] Yosef יכול לקרוא חשבוניות מ-Odoo
- [ ] Yosef יכול להציג פירוט חשבונית
- [ ] Yosef יכול לבדוק סטטוס תשלום
- [ ] כלים:
  - `get_patient_invoices_tool(patient_name, patient_phone)`
  - `get_invoice_details_tool(invoice_id)`
- [ ] Integration עם Mock Odoo עובד
- [ ] Yosef משתמש בכלים אוטומטית

**משימות:**
1. עדכן `backend/app/agents/yosef.py` - הוסף tool calling logic
2. בדוק עם שאלה: "מה החשבונית שלי?"
3. וודא שYosef מחזיר מידע אמיתי מ-Mock Odoo

**קבצים:**
- `backend/app/agents/yosef.py` (עדכון)

---

## 🚀 Phase 2: Real Odoo Integration

**עדיפות:** 🟡 HIGH  
**משך זמן:** 6 שעות  
**מטרה:** מעבר מ-Mock Odoo ל-Odoo אמיתי

---

### Epic 2.1: Odoo Production Setup

**משך זמן:** 6 שעות

#### User Story 2.1.1: הקמת Odoo Instance
**משך:** 4 שעות

**תיאור:**  
הקמת Odoo 17 production instance עם Dental module.

**Acceptance Criteria:**
- [ ] Odoo 17 Community Edition מותקן
- [ ] Dental module מותקן (או custom module)
- [ ] Database: `dental_clinic`
- [ ] Sample data נטען:
  - 10 patients
  - 20 appointments
  - 15 invoices
- [ ] XML-RPC API מופעל
- [ ] API user: `api_user` עם הרשאות מתאימות
- [ ] SSL certificate מוגדר (Let's Encrypt)
- [ ] Backup אוטומטי (pg_dump daily)

**משימות:**
1. התקן Odoo 17 (Docker או VM)
2. התקן Dental module
3. טען sample data
4. הגדר API credentials
5. בדוק XML-RPC connection

**קבצים:**
- `infrastructure/odoo/docker-compose.yml`
- `infrastructure/odoo/dental_module/` (אם custom)

---

#### User Story 2.1.2: מעבר מ-Mock ל-Real Odoo
**משך:** 2 שעות

**תיאור:**  
החלפת Mock Odoo ב-Odoo אמיתי.

**Acceptance Criteria:**
- [ ] `backend/app/core/config.py` מצביע על Odoo אמיתי
- [ ] כל הכלים עובדים:
  - `search_patient_tool`
  - `get_available_slots_tool`
  - `create_appointment_tool`
  - `get_patient_invoices_tool`
  - `get_invoice_details_tool`
- [ ] Integration tests עוברים
- [ ] Sarah + Yosef משתמשים ב-Odoo אמיתי
- [ ] Error handling מלא (אם Odoo לא זמין)

**משימות:**
1. עדכן `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD` ב-Secrets Manager
2. בדוק connection: `odoo_client.authenticate()`
3. הרץ integration tests
4. בדוק עם שאלה אמיתית לSarah: "מה הזמינות שלכם?"

**קבצים:**
- `backend/app/core/config.py` (עדכון)
- `backend/tests/test_odoo_integration.py` (עדכון)

---

## 🚀 Phase 3: WhatsApp Interface

**עדיפות:** 🟢 MEDIUM  
**משך זמן:** 7 שעות  
**מטרה:** הוספת ממשק WhatsApp למשתמשים

---

### Epic 3.1: WhatsApp Business API Integration

**משך זמן:** 7 שעות

#### User Story 3.1.1: הקמת WhatsApp Business Account
**משך:** 2 שעות

**תיאור:**  
הקמת חשבון WhatsApp Business והגדרת API.

**Acceptance Criteria:**
- [ ] WhatsApp Business account מאושר
- [ ] Phone number מאומת (+972...)
- [ ] API credentials מתקבלים
- [ ] Webhook URL מוגדר: `https://api.dental-clinic.com/api/whatsapp/webhook`
- [ ] Verify token מוגדר
- [ ] Message templates מאושרים (לפחות 2)

**משימות:**
1. פתח WhatsApp Business account
2. אמת מספר טלפון
3. הגדר webhook
4. צור message templates
5. שמור credentials ב-AWS Secrets Manager

---

#### User Story 3.1.2: Webhook Handler
**משך:** 3 שעות

**תיאור:**  
מטפל בהודעות נכנסות מ-WhatsApp.

**Acceptance Criteria:**
- [ ] Endpoint: `POST /api/whatsapp/webhook`
- [ ] Webhook verification (GET request)
- [ ] Message parsing (text, media, location)
- [ ] Routing ל-agent graph
- [ ] Response formatting (WhatsApp format)
- [ ] Media handling (images, voice notes)
- [ ] Error handling מלא
- [ ] Logging של כל הודעה

**משימות:**
1. צור `backend/app/api/whatsapp.py` - Webhook handlers
2. צור `backend/app/integrations/whatsapp_client.py` - WhatsApp client
3. בדוק עם ngrok local testing
4. בדוק עם הודעה אמיתית

**קבצים:**
- `backend/app/api/whatsapp.py`
- `backend/app/integrations/whatsapp_client.py`

---

#### User Story 3.1.3: Message Templates
**משך:** 2 שעות

**תיאור:**  
יצירת תבניות הודעות מאושרות.

**Acceptance Criteria:**
- [ ] Templates מאושרים ב-WhatsApp:
  1. **Appointment Confirmation** - אישור תור
  2. **Appointment Reminder** - תזכורת תור (24 שעות לפני)
  3. **Payment Reminder** - תזכורת תשלום
  4. **General Info** - מידע כללי
- [ ] Templates בעברית + אנגלית
- [ ] Variables: `{patient_name}`, `{appointment_date}`, `{amount}`
- [ ] Integration עם agent responses

**משימות:**
1. צור templates ב-WhatsApp Business Manager
2. צור `backend/app/templates/whatsapp/` - Template files
3. צור `backend/app/services/whatsapp_templates.py` - Template rendering
4. בדוק שליחת template

**קבצים:**
- `backend/app/templates/whatsapp/appointment_confirmation.json`
- `backend/app/templates/whatsapp/appointment_reminder.json`
- `backend/app/services/whatsapp_templates.py`

---

## 🚀 Phase 4: Production Deployment

**עדיפות:** 🟢 MEDIUM  
**משך זמן:** 8 שעות  
**מטרה:** פריסה ל-production ב-AWS

---

### Epic 4.1: AWS Infrastructure Setup

**משך זמן:** 4 שעות

#### User Story 4.1.1: Terraform Infrastructure
**משך:** 4 שעות

**תיאור:**  
הקמת תשתית AWS עם Terraform.

**Acceptance Criteria:**
- [ ] VPC עם 2 subnets (public + private)
- [ ] ECS Fargate cluster
- [ ] RDS PostgreSQL (db.t3.micro)
- [ ] ElastiCache Redis (cache.t3.micro)
- [ ] Application Load Balancer (ALB)
- [ ] CloudWatch logging
- [ ] Auto-scaling (min: 1, max: 3)
- [ ] Security groups מוגדרים
- [ ] IAM roles מוגדרים

**משימות:**
1. צור `infrastructure/aws/main.tf`
2. צור `infrastructure/aws/vpc.tf`
3. צור `infrastructure/aws/ecs.tf`
4. צור `infrastructure/aws/rds.tf`
5. צור `infrastructure/aws/alb.tf`
6. הרץ `terraform apply`

**קבצים:**
- `infrastructure/aws/*.tf`

---

### Epic 4.2: Backend Deployment

**משך זמן:** 2 שעות

#### User Story 4.2.1: Deploy Backend to ECS
**משך:** 2 שעות

**תיאור:**  
פריסת backend ל-ECS Fargate.

**Acceptance Criteria:**
- [ ] Docker image נבנה
- [ ] Image נדחף ל-ECR
- [ ] ECS task definition מוגדר
- [ ] Service running (1 task)
- [ ] Health checks passing
- [ ] Logs ב-CloudWatch
- [ ] Environment variables מ-Secrets Manager

**משימות:**
1. צור `backend/Dockerfile.prod`
2. צור `.github/workflows/deploy.yml`
3. בנה image: `docker build -t dental-clinic-backend .`
4. דחף ל-ECR
5. Deploy ל-ECS

**קבצים:**
- `backend/Dockerfile.prod`
- `.github/workflows/deploy.yml`

---

### Epic 4.3: Frontend Deployment

**משך זמן:** 2 שעות

#### User Story 4.3.1: Deploy Frontend to S3/CloudFront
**משך:** 2 שעות

**תיאור:**  
פריסת frontend ל-S3 + CloudFront CDN.

**Acceptance Criteria:**
- [ ] Build מופק: `npm run build`
- [ ] Upload ל-S3 bucket
- [ ] CloudFront distribution מוגדר
- [ ] SSL certificate מוגדר (ACM)
- [ ] Custom domain: `app.dental-clinic.com`
- [ ] Cache invalidation אוטומטי

**משימות:**
1. צור `frontend/deploy.sh`
2. צור S3 bucket: `dental-clinic-frontend`
3. צור CloudFront distribution
4. הגדר SSL certificate
5. Deploy: `./deploy.sh`

**קבצים:**
- `frontend/deploy.sh`
- `infrastructure/aws/cloudfront.tf`

---

## 🚀 Phase 5: Monitoring & Observability

**עדיפות:** 🔵 LOW  
**משך זמן:** 5 שעות  
**מטרה:** ניטור ואלרטים

---

### Epic 5.1: Monitoring Setup

**משך זמן:** 5 שעות

#### User Story 5.1.1: CloudWatch Alarms
**משך:** 2 שעות

**תיאור:**  
הגדרת alarms ב-CloudWatch.

**Acceptance Criteria:**
- [ ] Alarms:
  - CPU utilization > 80%
  - Memory utilization > 80%
  - Error rate > 5%
  - Response time > 2s
  - Health check failures
- [ ] SNS topic: `dental-clinic-alerts`
- [ ] Email notifications
- [ ] Slack notifications (אופציונלי)

**משימות:**
1. צור `infrastructure/aws/cloudwatch.tf`
2. צור SNS topic
3. הוסף email subscription
4. בדוק alarm (סימולציה)

**קבצים:**
- `infrastructure/aws/cloudwatch.tf`

---

#### User Story 5.1.2: Application Metrics
**משך:** 3 שעות

**תיאור:**  
הוספת metrics לapplication.

**Acceptance Criteria:**
- [ ] Metrics:
  - Agent response time
  - Agent success rate
  - API latency (p50, p95, p99)
  - Rate limit hits
  - Database connection pool
  - Odoo API calls
- [ ] Dashboard ב-CloudWatch
- [ ] Custom metrics ב-CloudWatch

**משימות:**
1. הוסף `prometheus-client` ל-`requirements.txt`
2. צור `backend/app/monitoring/metrics.py`
3. הוסף metrics לagents
4. צור CloudWatch dashboard

**קבצים:**
- `backend/app/monitoring/metrics.py`
- `infrastructure/aws/cloudwatch_dashboard.json`

---

## 🚀 Phase 6: Security & Compliance

**עדיפות:** 🔵 LOW  
**משך זמן:** 5 שעות  
**מטרה:** אבטחה ותאימות

---

### Epic 6.1: GDPR Compliance

**משך זמן:** 3 שעות

#### User Story 6.1.1: Data Privacy Implementation
**משך:** 3 שעות

**תיאור:**  
יישום תאימות GDPR.

**Acceptance Criteria:**
- [ ] Data retention policy: 90 ימים
- [ ] Right to be forgotten: `DELETE /api/users/{user_id}`
- [ ] Data export: `GET /api/users/{user_id}/export`
- [ ] Consent management
- [ ] Privacy policy (עברית + אנגלית)
- [ ] Terms of service (עברית + אנגלית)

**משימות:**
1. צור `backend/app/api/gdpr.py`
2. צור `docs/PRIVACY_POLICY.md`
3. צור `docs/TERMS_OF_SERVICE.md`
4. הוסף consent checkbox לUI

**קבצים:**
- `backend/app/api/gdpr.py`
- `docs/PRIVACY_POLICY.md`
- `docs/TERMS_OF_SERVICE.md`

---

### Epic 6.2: Security Audit

**משך זמן:** 2 שעות

#### User Story 6.2.1: Security Testing
**משך:** 2 שעות

**תיאור:**  
ביקורת אבטחה.

**Acceptance Criteria:**
- [ ] OWASP Top 10 check
- [ ] Dependency vulnerability scan (`pip-audit`)
- [ ] SQL injection tests
- [ ] XSS tests
- [ ] CSRF protection
- [ ] Rate limiting tests
- [ ] Security headers (HSTS, CSP, X-Frame-Options)

**משימות:**
1. הרץ `pip-audit`
2. הרץ `bandit` (Python security linter)
3. בדוק security headers
4. צור `docs/SECURITY_AUDIT.md`

**קבצים:**
- `docs/SECURITY_AUDIT.md`

---

## 📊 סיכום Timeline

### Week 1: Protocol & Infrastructure (Priority 1)
**ימים 1-2:** Epic 0.1-0.3 (Git Protocol + AWS + manus.im)  
**יום 3:** Epic 0.4-0.6 (Backup + DR + S3 Glacier)  
**סה"כ:** 10 שעות

### Week 2: Complete Phase 1 (Priority 2)
**ימים 1-2:** Epic 1.1-1.2 (Neo4j + Yosef tools)  
**ימים 3-5:** Epic 2.1 (Real Odoo)  
**סה"כ:** 10 שעות

### Week 3: WhatsApp & Deployment (Priority 3)
**ימים 1-2:** Epic 3.1 (WhatsApp)  
**ימים 3-5:** Epic 4.1-4.3 (Production Deployment)  
**סה"כ:** 15 שעות

### Week 4: Monitoring & Security (Priority 4)
**ימים 1-2:** Epic 5.1 (Monitoring)  
**ימים 3-4:** Epic 6.1-6.2 (Security)  
**יום 5:** Testing + Documentation  
**סה"כ:** 10 שעות

---

## ✅ Checklist - מה צריך לעשות עכשיו?

### 🔴 Priority 1: Critical (חובה מיידית)
- [ ] Epic 0.1: Manus-Git Protocol (3 שעות)
- [ ] Epic 0.2: AWS Secrets Manager (2 שעות)
- [ ] Epic 0.3: manus.im API Integration (1.5 שעות)
- [ ] Epic 0.4: GitHub Actions Backup (2 שעות)
- [ ] Epic 0.5: RTO/RPO + DR Drill (1.5 שעות)
- [ ] Epic 0.6: S3 Glacier (1 שעה)

**סה"כ:** 11 שעות

### 🟡 Priority 2: High (חשוב)
- [ ] Epic 1.1: Neo4j (2 שעות)
- [ ] Epic 1.2: Yosef tools (2 שעות)
- [ ] Epic 2.1: Real Odoo (6 שעות)

**סה"כ:** 10 שעות

### 🟢 Priority 3: Medium (פיצ'רים)
- [ ] Epic 3.1: WhatsApp (7 שעות)
- [ ] Epic 4.1-4.3: Production Deployment (8 שעות)

**סה"כ:** 15 שעות

### 🔵 Priority 4: Low (ניס-טו-האב)
- [ ] Epic 5.1: Monitoring (5 שעות)
- [ ] Epic 6.1-6.2: Security (5 שעות)

**סה"כ:** 10 שעות

---

## 📈 Progress Tracking

| Phase | Status | Progress | Priority |
|-------|--------|----------|----------|
| Phase 0: Protocol | ❌ Not Started | 0% | 🔴 Critical |
| Phase 1: Agents | ✅ Almost Done | 95% | 🟡 High |
| Phase 2: Odoo | ⚠️ Mock Only | 50% | 🟡 High |
| Phase 3: WhatsApp | ❌ Not Started | 0% | 🟢 Medium |
| Phase 4: Deployment | ⚠️ Partial | 30% | 🟢 Medium |
| Phase 5: Monitoring | ❌ Not Started | 0% | 🔵 Low |
| Phase 6: Security | ⚠️ Basic | 20% | 🔵 Low |

**Overall Progress:** 35% Complete

---

## 🎯 המלצה: מה לעשות עכשיו?

**אפשרות 1: לפי מסגרת העבודה (מומלץ)**
התחל מ-Phase 0 (Protocol) - 11 שעות
- יישום פרוטוקול Git מלא
- AWS Secrets Manager
- Backup & Recovery
- זה יבטיח שהכל מתועד ומגובה כראוי

**אפשרות 2: להשלים את הקוד**
התחל מ-Phase 1-2 (Agents + Odoo) - 10 שעות
- Neo4j + Yosef tools
- Real Odoo
- זה ישלים את הפונקציונליות

**אפשרות 3: ללכת ל-production**
התחל מ-Phase 3-4 (WhatsApp + Deployment) - 15 שעות
- WhatsApp interface
- Production deployment
- זה יאפשר למשתמשים להשתמש במערכת

**מה אתה רוצה לעשות?**

---

**נוצר על ידי:** Manus AI Agent  
**תאריך:** 2 באוקטובר 2025  
**גירסה:** 16.0 (Clean & Focused)  
**Manus-Session-ID:** [יתקבל מ-API]
