# Framework Summary - מיסגרת עבודה

## מטרה
פריימוורק הוליסטי לגיבוי ושחזור בסביבת פיתוח AI מבוססת סוכן

## עקרונות ליבה

### 1. Holistic Operational Snapshot
- גישת AI חוזרת מגיבוי הקוד בלבד ל"תמונת מצב תפעולית הוליסטית"
- כולל: הקוד, התכנון, המחקר, הקידוד, הפריסה, הזיכרון, הסשן

### 2. Git Repository Hygiene
- **תרגיש 1:** אתחול פרויקט חדש - git init, .gitignore, README
- **תרגיש 2:** טיהור תאגר קיים - git checkout --orphan, git-filter-repo
- **Manus-Git Protocol:** פורמט commit מובנה
  ```
  <Type>(<Scope>): <Subject>
  
  <Body>
  
  Manus-Session-ID: <session_id_from_manus_api>
  Manus-Task-ID: <specific_task_or_plan_step_id>
  Human-Initiator: <username_of_human_who_gave_the_prompt>
  ```

### 3. Artifact Management
- commit-hash כדי להבטיח עקיבות
- build artifacts מתויגים ב-Manus Session ID
- git describe --always --dirty או git rev-parse HEAD

### 4. AWS Secrets Manager
- כספת סודות עם ארכיטקטורה של שכבות
- HumanDeveloperRole + ManusAgentRole
- סודות סטטיים + רוטציה אוטומטית

### 5. manus.im Session Integration
- לינקס דיגיטלי n-API-n-manus.im
- getSession API לקבלת נקודת הקצא
- פורמט: Manus -> Commit Hash -> Build -> Artifact

### 6. OpenManus Protocol
- תהליך עבודה עבור משתמשי OpenManus
- MongoDB/Redis, GitHub Actions, Webhooks, Zapier

### 7. Disaster Recovery
- **RPO (Recovery Point Objective):** push יוצר נקודת שחזור
- **RTO (Recovery Time Objective):** זמן להתאוששות
- תרגילי שולחן עגול (Disaster Recovery drills)

### 8. S3 Lifecycle & Archiving
- S3 Lifecycle לניהול עלויות
- S3 Glacier Deep Archive לארכוב ארוך-טווח
- S3 Cross-Region Replication (CRR)

### 9. Backup Responsibilities
טבלה מפורטת של תפקידים:
- **Recovery Lead:** CTO/ראש מחלקת הנדסה
- **צוות שחזור טכני:** Backend/Frontend מהנדסים + DevOps
- **מוביל תקשורת:** מנהל מוצר/הנדסה
- **Manus איש קשר לסוכן:** AI מומחה שילוב
- **מתעד:** כותב טכני/מפתח סוכן

## הוראות יישום ל-WORK_PLAN

1. **כל Epic צריך לכלול:**
   - Status מעודכן (% completion)
   - Open Issues רשימה
   - Dependencies מזוהים
   
2. **כל User Story צריך לכלול:**
   - Acceptance Criteria ברורים
   - Testing Requirements
   - Git commit references
   
3. **עדכון גרסאות:**
   - שינוי Version number
   - שינוי Date
   - הוספת "Key Changes in vX.X"
   - עדכון Status בכל Epic
   - תיעוד Open Issues

4. **Git Workflow:**
   - כל commit עם Manus-Session-ID
   - Build artifacts מתויגים
   - Backup לפני שינויים גדולים

5. **Documentation:**
   - README מעודכן
   - Architecture Decision Records (ADRs)
   - API documentation
   - Deployment guides

## תבנית לעדכון WORK_PLAN

```markdown
# DentalAI Work Plan

**Date:** YYYY-MM-DD
**Version:** X.X
**Status:** [Draft/In Progress/Final]

---

## 🎯 Executive Summary

### Key Changes in vX.X:
- ✅ **[Feature/Fix]:** Description
- ⚠️ **[Open Issue]:** Description
- ❌ **[Blocked]:** Description

---

## Part I: Master Prompt
[Keep original content]

---

## Part II: Architectural Pillars
[Keep original content]

---

## Part III: Quality Gates
[Keep original content]

---

## Part IV: Epics & User Stories

### Epic X: [Name]

**Status:** X% Complete
**Last Updated:** YYYY-MM-DD

**Completed:**
- ✅ User Story X.X: [Name]

**In Progress:**
- ⏳ User Story X.X: [Name] (X% done)

**Open Issues:**
- ⚠️ Issue #X: [Description]
- ❌ Blocked: [Description]

**Dependencies:**
- Requires: [Epic/Story]
- Blocks: [Epic/Story]

[Original User Story content...]
```

---

**מקור:** מיסגרתעבודה1.pdf
**תאריך:** October 2, 2025
