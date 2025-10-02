# תוכנית עבודה V15.0 - מערכת AI לניהול מרפאת שיניים
## מיושרת עם מסגרת העבודה ההוליסטית המקורית

**תאריך עדכון:** 2 באוקטובר 2025  
**גירסה:** 15.0  
**סטטוס פרויקט:** Phase 1 MVP - 95% (עם פערים קריטיים בפרוטוקול)

---

## סיכום מצב נוכחי

### ✅ מה שמיושם (95% מהקוד)
- ✅ 4 סוכנים (Dana, Michal, Yosef, Sarah) עם LangGraph
- ✅ טיפול בשגיאות ו-retry logic
- ✅ Rate limiting (60 req/min)
- ✅ אינטגרציה עם Odoo (Mock)
- ✅ בדיקות מקיפות (unit + integration)

### ❌ פערים קריטיים במסגרת העבודה (חסר לחלוטין)
- ❌ **פרוטוקול Git**: אין Manus-Session-ID בcommits
- ❌ **AWS Secrets Manager**: סודות לא מנוהלים כראוי
- ❌ **OpenManus**: אין MongoDB, Redis, Webhooks
- ❌ **GitHub Actions**: אין backup automation
- ❌ **RTO/RPO**: אין תהליך שחזור מאסון
- ❌ **S3 Glacier**: אין ארכיון ארוך-טווח
- ❌ **טבלת תפקידים**: לא מוגדר מי אחראי על מה

---

## Phase 0: יישור עם מסגרת העבודה ההוליסטית (CRITICAL)

**משך זמן משוער:** 12-16 שעות  
**עדיפות:** CRITICAL - חובה לפני המשך פיתוח

### Epic 0.1: הקמת פרוטוקול Git תקין ✨ NEW

**User Stories:**

#### 0.1.1: יישום Manus-Git Protocol
**משך:** 2 שעות  
**תיאור:** יישום פרוטוקול commit מלא עם Manus-Session-ID

**Acceptance Criteria:**
- [ ] כל commit כולל Manus-Session-ID בפורמט הנכון
- [ ] כל commit כולל Manus-Task-ID
- [ ] כל commit כולל Human-Initiator
- [ ] פורמט commit: `<Type>(<Scope>): <Subject>`
- [ ] Body מכיל הסבר מפורט
- [ ] דוגמה:
```
feat(agents): Add error handling to all 4 agents

Implemented comprehensive error handling system with retry logic
and rate limiting for Dana, Michal, Yosef, and Sarah agents.

Manus-Session-ID: 20251002-143052
Manus-Task-ID: phase-1.2-agent-migration
Human-Initiator: scubapro711
```

**קבצים:**
- `scripts/git_commit_helper.py` - סקריפט עזר לcommit
- `.git/hooks/prepare-commit-msg` - Git hook

---

#### 0.1.2: הקמת Git Bundle Backup
**משך:** 2 שעות  
**תיאור:** יצירת git bundle אוטומטי לכל commit

**Acceptance Criteria:**
- [ ] כל commit יוצר git bundle
- [ ] Bundle נשמר ב-`backups/git-bundles/`
- [ ] Bundle כולל את כל ההיסטוריה
- [ ] Bundle נבדק אוטומטית (git bundle verify)
- [ ] Bundle מועלה ל-S3 (אם מוגדר)

**קבצים:**
- `.git/hooks/post-commit` - Hook ליצירת bundle
- `scripts/create_git_bundle.sh` - סקריפט יצירת bundle

---

#### 0.1.3: הקמת GitHub Actions Backup Workflow
**משך:** 3 שעות  
**תיאור:** יישום workflow אוטומטי לגיבוי

**Acceptance Criteria:**
- [ ] Workflow מופעל אוטומטית ב-push ל-main
- [ ] יוצר git bundle
- [ ] מייצא Manus session (אם זמין)
- [ ] מעלה ל-S3 bucket
- [ ] שולח התראה על הצלחה/כישלון
- [ ] תומך ב-manual trigger

**קבצים:**
- `.github/workflows/backup.yml` - Workflow definition
- `scripts/export_manus_session.py` - ייצוא session

---

### Epic 0.2: הקמת AWS Secrets Manager ✨ NEW

**User Stories:**

#### 0.2.1: הגדרת AWS Secrets Manager
**משך:** 2 שעות  
**תיאור:** הקמת Secrets Manager לניהול סודות

**Acceptance Criteria:**
- [ ] AWS Secrets Manager מוגדר ב-us-east-1
- [ ] סודות מאוחסנים בפורמט JSON
- [ ] שני roles מוגדרים:
  - `HumanDeveloperRole` - גישה מלאה
  - `ManusAgentRole` - קריאה בלבד
- [ ] Rotation policy מוגדר (90 ימים)
- [ ] CloudTrail מופעל לאודיט
- [ ] KMS key מוגדר להצפנה

**סודות לאחסן:**
```json
{
  "openai_api_key": "sk-...",
  "odoo_url": "https://...",
  "odoo_db": "dental_clinic",
  "odoo_username": "admin",
  "odoo_password": "...",
  "neo4j_uri": "bolt://...",
  "neo4j_user": "neo4j",
  "neo4j_password": "...",
  "mongodb_uri": "mongodb://...",
  "redis_url": "redis://..."
}
```

**קבצים:**
- `infrastructure/aws/secrets_manager.tf` - Terraform config
- `backend/app/core/secrets.py` - Secrets client

---

#### 0.2.2: אינטגרציה עם Backend
**משך:** 1 שעה  
**תיאור:** שילוב Secrets Manager בקוד

**Acceptance Criteria:**
- [ ] `settings.py` קורא מ-Secrets Manager
- [ ] Fallback ל-environment variables
- [ ] Cache של secrets (5 דקות)
- [ ] Refresh אוטומטי
- [ ] Error handling מלא

**קבצים:**
- `backend/app/core/config.py` - עדכון settings

---

### Epic 0.3: הקמת OpenManus Infrastructure ✨ NEW

**User Stories:**

#### 0.3.1: הקמת MongoDB
**משך:** 2 שעות  
**תיאור:** הקמת MongoDB לאחסון sessions

**Acceptance Criteria:**
- [ ] MongoDB Atlas cluster מוקם
- [ ] Database: `dental_clinic_ai`
- [ ] Collections:
  - `sessions` - Manus sessions
  - `conversations` - היסטוריית שיחות
  - `events` - אירועים
- [ ] Indexes מוגדרים
- [ ] Backup אוטומטי (mongodump daily)
- [ ] Connection pooling מוגדר

**קבצים:**
- `backend/app/db/mongodb.py` - MongoDB client
- `backend/app/models/session.py` - Session model

---

#### 0.3.2: הקמת Redis
**משך:** 1.5 שעות  
**תיאור:** הקמת Redis לcache ו-rate limiting

**Acceptance Criteria:**
- [ ] Redis instance מוקם (ElastiCache או local)
- [ ] TTL מוגדר (1 שעה)
- [ ] Rate limit counters ב-Redis
- [ ] Session cache ב-Redis
- [ ] Connection pooling מוגדר

**קבצים:**
- `backend/app/db/redis_client.py` - Redis client
- `backend/app/agents/rate_limiter.py` - עדכון לשימוש ב-Redis

---

#### 0.3.3: הקמת Webhooks
**משך:** 2 שעות  
**תיאור:** מערכת webhooks לאינטגרציות

**Acceptance Criteria:**
- [ ] Webhook endpoint: `/api/webhooks/{provider}`
- [ ] תמיכה ב:
  - GitHub (push events)
  - Zapier (custom events)
  - Slack (notifications)
- [ ] Signature verification
- [ ] Retry logic (3 attempts)
- [ ] Logging מלא

**קבצים:**
- `backend/app/api/webhooks.py` - Webhook handlers
- `backend/app/integrations/zapier.py` - Zapier integration

---

### Epic 0.4: הקמת Disaster Recovery ✨ NEW

**User Stories:**

#### 0.4.1: הגדרת RTO/RPO
**משך:** 1 שעה  
**תיאור:** הגדרת יעדי שחזור

**Acceptance Criteria:**
- [ ] RPO מוגדר: 1 שעה (נקודת שחזור אחרונה)
- [ ] RTO מוגדר: 4 שעות (זמן שחזור מקסימלי)
- [ ] תיעוד תהליך שחזור
- [ ] Runbook מפורט
- [ ] טבלת תפקידים מוגדרת

**קבצים:**
- `docs/DISASTER_RECOVERY.md` - תיעוד DR
- `docs/RUNBOOK.md` - הוראות שחזור

---

#### 0.4.2: Disaster Recovery Drill
**משך:** 2 שעות  
**תיאור:** תרגיל שחזור מאסון

**Acceptance Criteria:**
- [ ] תרגיל מתועד (checklist)
- [ ] שחזור מ-git bundle
- [ ] שחזור מ-S3 backup
- [ ] שחזור MongoDB
- [ ] שחזור Redis
- [ ] בדיקת תקינות מערכת
- [ ] תיעוד ממצאים

**קבצים:**
- `scripts/disaster_recovery_drill.sh` - סקריפט תרגיל
- `docs/DR_DRILL_REPORT.md` - דוח תרגיל

---

#### 0.4.3: הקמת S3 Glacier Archive
**משך:** 1.5 שעות  
**תיאור:** ארכיון ארוך-טווח

**Acceptance Criteria:**
- [ ] S3 bucket עם Lifecycle policy
- [ ] Transition ל-Glacier Deep Archive אחרי 90 ימים
- [ ] Retention: 7 שנים
- [ ] Cross-region replication (CRR)
- [ ] Encryption at rest
- [ ] Access logging

**קבצים:**
- `infrastructure/aws/s3_lifecycle.tf` - Terraform config

---

## Phase 1: Core Agent Architecture (95% Complete)

**סטטוס:** ✅ כמעט מושלם (חסר רק Neo4j causal memory)

### Epic 1: Agent Migration to LangGraph ✅ COMPLETE

**סטטוס:** 95% מושלם

**מה שהושלם:**
- ✅ 4 סוכנים (Dana, Michal, Yosef, Sarah)
- ✅ Error handling + retry logic
- ✅ Rate limiting (60 req/min, burst 10)
- ✅ Tool integration (Sarah - availability checking)
- ✅ Comprehensive testing (17 unit + 6 integration)

**מה שחסר:**
- ⚠️ Neo4j causal memory (2 שעות)
- ⚠️ Enhanced tool integration for Yosef (2 שעות)

---

### Epic 2: Neo4j Causal Memory Integration ⚠️ PENDING

**User Stories:**

#### 2.1: Fix Neo4j Authentication
**משך:** 1 שעה  
**תיאור:** תיקון בעיות אימות Neo4j

**Acceptance Criteria:**
- [ ] Neo4j connection working
- [ ] Credentials מ-AWS Secrets Manager
- [ ] Connection pooling
- [ ] Health check endpoint

**קבצים:**
- `backend/app/integrations/neo4j_client.py` - עדכון client

---

#### 2.2: Integrate Causal Memory with Agents
**משך:** 1 שעה  
**תיאור:** שילוב זיכרון סיבתי בסוכנים

**Acceptance Criteria:**
- [ ] כל agent שומר היסטוריה ב-Neo4j
- [ ] Retrieval של context רלוונטי
- [ ] Graph relationships בין entities
- [ ] Query optimization

**קבצים:**
- `backend/app/agents/agent_graph.py` - אינטגרציה

---

## Phase 2: Odoo Integration (50% Complete)

**סטטוס:** ⚠️ Mock בלבד, צריך Odoo אמיתי

### Epic 3: Real Odoo Setup ⚠️ PENDING

**User Stories:**

#### 3.1: Setup Odoo Instance
**משך:** 4 שעות  
**תיאור:** הקמת Odoo production instance

**Acceptance Criteria:**
- [ ] Odoo 17 מותקן
- [ ] Dental module מותקן
- [ ] Sample data נטען
- [ ] API credentials מוגדרים
- [ ] SSL certificate מוגדר

**קבצים:**
- `infrastructure/odoo/docker-compose.yml` - Odoo setup

---

#### 3.2: Migrate from Mock to Real Odoo
**משך:** 2 שעות  
**תיאור:** מעבר מ-Mock ל-Odoo אמיתי

**Acceptance Criteria:**
- [ ] `OdooClient` מחובר ל-Odoo אמיתי
- [ ] כל הכלים עובדים (search_patient, create_appointment, etc.)
- [ ] Error handling מלא
- [ ] Integration tests עוברים

**קבצים:**
- `backend/app/integrations/odoo_client.py` - עדכון
- `backend/tests/test_odoo_integration.py` - בדיקות

---

## Phase 3: WhatsApp Interface (0% Complete)

**סטטוס:** ❌ לא התחיל

### Epic 4: WhatsApp Business API Integration ⚠️ PENDING

**User Stories:**

#### 4.1: Setup WhatsApp Business Account
**משך:** 2 שעות  
**תיאור:** הקמת חשבון WhatsApp Business

**Acceptance Criteria:**
- [ ] WhatsApp Business account מאושר
- [ ] Phone number מאומת
- [ ] API credentials מתקבלים
- [ ] Webhook URL מוגדר

---

#### 4.2: Implement WhatsApp Webhook Handler
**משך:** 3 שעות  
**תיאור:** מטפל בהודעות נכנסות

**Acceptance Criteria:**
- [ ] Webhook endpoint: `/api/whatsapp/webhook`
- [ ] Message parsing
- [ ] Routing לagent graph
- [ ] Response formatting
- [ ] Media handling (images, voice)

**קבצים:**
- `backend/app/api/whatsapp.py` - WhatsApp handlers
- `backend/app/integrations/whatsapp_client.py` - WhatsApp client

---

#### 4.3: Implement Message Templates
**משך:** 2 שעות  
**תיאור:** תבניות הודעות מאושרות

**Acceptance Criteria:**
- [ ] Appointment confirmation template
- [ ] Appointment reminder template
- [ ] Payment reminder template
- [ ] General info template
- [ ] Templates מאושרות ב-WhatsApp

**קבצים:**
- `backend/app/templates/whatsapp/` - Templates

---

## Phase 4: Production Deployment (30% Complete)

**סטטוס:** ⚠️ חלקי - יש infrastructure אבל לא deployed

### Epic 5: AWS Production Deployment ⚠️ PENDING

**User Stories:**

#### 5.1: Setup AWS Infrastructure
**משך:** 4 שעות  
**תיאור:** הקמת תשתית AWS

**Acceptance Criteria:**
- [ ] VPC עם subnets
- [ ] ECS Fargate cluster
- [ ] RDS PostgreSQL
- [ ] ElastiCache Redis
- [ ] Application Load Balancer
- [ ] CloudWatch logging
- [ ] Auto-scaling מוגדר

**קבצים:**
- `infrastructure/aws/main.tf` - Terraform main
- `infrastructure/aws/ecs.tf` - ECS config
- `infrastructure/aws/rds.tf` - RDS config

---

#### 5.2: Deploy Backend to ECS
**משך:** 2 שעות  
**תיאור:** פריסת backend ל-production

**Acceptance Criteria:**
- [ ] Docker image נבנה
- [ ] Image נדחף ל-ECR
- [ ] ECS task definition מוגדר
- [ ] Service running
- [ ] Health checks passing
- [ ] Logs ב-CloudWatch

**קבצים:**
- `backend/Dockerfile` - Production dockerfile
- `.github/workflows/deploy.yml` - Deploy workflow

---

#### 5.3: Deploy Frontend to S3/CloudFront
**משך:** 2 שעות  
**תיאור:** פריסת frontend ל-CDN

**Acceptance Criteria:**
- [ ] Build מופק
- [ ] Upload ל-S3
- [ ] CloudFront distribution מוגדר
- [ ] SSL certificate מוגדר
- [ ] Custom domain מוגדר

**קבצים:**
- `frontend/deploy.sh` - Deploy script

---

## Phase 5: Monitoring & Observability (10% Complete)

**סטטוס:** ❌ כמעט לא קיים

### Epic 6: Monitoring Setup ⚠️ PENDING

**User Stories:**

#### 6.1: Setup Prometheus + Grafana
**משך:** 3 שעות  
**תיאור:** מערכת ניטור

**Acceptance Criteria:**
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards:
  - Agent performance
  - API latency
  - Error rates
  - Rate limiting
  - Database connections
- [ ] Alerts מוגדרים
- [ ] Slack notifications

**קבצים:**
- `infrastructure/monitoring/prometheus.yml` - Config
- `infrastructure/monitoring/grafana/dashboards/` - Dashboards

---

#### 6.2: Setup CloudWatch Alarms
**משך:** 2 שעות  
**תיאור:** התראות AWS

**Acceptance Criteria:**
- [ ] CPU utilization > 80%
- [ ] Memory utilization > 80%
- [ ] Error rate > 5%
- [ ] Response time > 2s
- [ ] SNS topic לhתראות
- [ ] Email notifications

**קבצים:**
- `infrastructure/aws/cloudwatch.tf` - Alarms config

---

## Phase 6: Security & Compliance (20% Complete)

**סטטוס:** ⚠️ בסיסי בלבד

### Epic 7: Security Hardening ⚠️ PENDING

**User Stories:**

#### 7.1: Implement GDPR Compliance
**משך:** 3 שעות  
**תיאור:** תאימות GDPR

**Acceptance Criteria:**
- [ ] Data retention policy (90 ימים)
- [ ] Right to be forgotten (delete user data)
- [ ] Data export API
- [ ] Consent management
- [ ] Privacy policy
- [ ] Terms of service

**קבצים:**
- `backend/app/api/gdpr.py` - GDPR endpoints
- `docs/PRIVACY_POLICY.md` - Privacy policy

---

#### 7.2: Security Audit
**משך:** 2 שעות  
**תיאור:** ביקורת אבטחה

**Acceptance Criteria:**
- [ ] OWASP Top 10 check
- [ ] Dependency vulnerability scan
- [ ] SQL injection tests
- [ ] XSS tests
- [ ] CSRF protection
- [ ] Rate limiting tests

**קבצים:**
- `docs/SECURITY_AUDIT.md` - Audit report

---

## טבלת תפקידים ואחריות

| תפקיד | בעל תפקיד ראשי | בעל תפקיד גיבוי | אחריות מרכזית |
|-------|---------------|----------------|---------------|
| **מוביל התאוששות (Recovery Lead)** | CTO / מהלק/ית הנדסה | מהנדס בכיר | מכריע על אירוע אסון; מאשר את הפעלת תוכנית ה-DR; מקבל החלטות; סופיות |
| **צוות שחזור טכני** | מובילי/ם Backend מהנדסי/ם | מובילי/ם DevOps מהנדסי/ם | מבצע את פרוטוקול השחזור (טיפול בV.C, השחזור הטכני (סעיף 5), משחזר את מאגר ה-Git; מסנכרן Manus; מוודא את תקינות המערכת לאחר השחזור |
| **מוביל תקשורת** | מנהל מוצר / מנהל הנדסה | | מנהל את כל התקשורת הפנימית לבעלי עניין (צוות, פיתוח, הנהלה) והתקשורת החיצונית במידת הצורך |
| **Manus איש קשר לסוכן** | AI מהנדס שילוב | | אחראי על אימות הקשר המשוחזר-Manus והפעלה מחדש של משימות סוכן קריטיות שנופסקו |
| **מתעד** | כותב טכני / מפתח מוסמך | | מתעד כל צעד שנעשה, במהלך השחזור, לוחות זמנים, חריגות מהתוכנית, ולקחים שיפוקו לתחקיר שלאחר האירוע |

---

## סיכום: מה צריך לעשות עכשיו?

### Priority 1: Critical (חובה לפני המשך)
1. **Epic 0.1**: יישום Manus-Git Protocol (4 שעות)
2. **Epic 0.2**: הקמת AWS Secrets Manager (3 שעות)
3. **Epic 0.4**: הגדרת RTO/RPO + DR Drill (3.5 שעות)

**סה"כ:** 10.5 שעות

### Priority 2: High (חשוב למערכת יציבה)
1. **Epic 0.3**: הקמת OpenManus Infrastructure (5.5 שעות)
2. **Epic 2**: Neo4j Causal Memory (2 שעות)
3. **Epic 3**: Real Odoo Setup (6 שעות)

**סה"כ:** 13.5 שעות

### Priority 3: Medium (פיצ'רים חדשים)
1. **Epic 4**: WhatsApp Interface (7 שעות)
2. **Epic 5**: AWS Production Deployment (8 שעות)
3. **Epic 6**: Monitoring Setup (5 שעות)

**סה"כ:** 20 שעות

### Priority 4: Low (ניס-טו-האב)
1. **Epic 7**: Security Hardening (5 שעות)

**סה"כ:** 5 שעות

---

## Timeline משוער

### Week 1: Foundation (Priority 1)
- ימים 1-2: Epic 0.1 + 0.2 (Git Protocol + Secrets Manager)
- יום 3: Epic 0.4 (RTO/RPO + DR Drill)

### Week 2: Infrastructure (Priority 2)
- ימים 1-2: Epic 0.3 (OpenManus)
- יום 3: Epic 2 (Neo4j)
- ימים 4-5: Epic 3 (Real Odoo)

### Week 3: Features (Priority 3)
- ימים 1-2: Epic 4 (WhatsApp)
- ימים 3-4: Epic 5 (Production Deployment)
- יום 5: Epic 6 (Monitoring)

### Week 4: Polish (Priority 4)
- ימים 1-2: Epic 7 (Security)
- ימים 3-5: Testing + Documentation

---

## הערות חשובות

1. **מסגרת העבודה היא חוק** - כל הפרוטוקולים חייבים להתבצע
2. **Manus-Session-ID חובה** - בכל commit, בכל action
3. **Backup הוא קריטי** - git bundle + S3 + Glacier
4. **RTO/RPO חייבים להיות מוגדרים** - לא אופציונלי
5. **טבלת תפקידים חובה** - כולם צריכים לדעת מי אחראי

---

**סטטוס כללי:**
- **קוד:** 95% מוכן
- **פרוטוקול:** 20% מיושם
- **תשתית:** 30% מוכנה
- **ייצור:** 10% deployed

**המלצה:** התחל מ-Priority 1 (Epic 0.1-0.4) לפני המשך פיתוח פיצ'רים חדשים.

---

**נוצר על ידי:** Manus AI Agent  
**תאריך:** 2 באוקטובר 2025  
**גירסה:** 15.0  
**Manus-Session-ID:** 20251002-current-session
