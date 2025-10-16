# הסכם רמת שירות | Service Level Agreement (SLA)

**תאריך תחילה:** 16 אוקטובר 2025  
**Effective Date:** October 16, 2025

---

## עברית

### 1. הגדרות

**"זמינות" (Uptime)** - האחוז של הזמן שבו השירות זמין ופעיל.

**"השבתה" (Downtime)** - תקופה שבה השירות אינו זמין או אינו פועל כראוי.

**"תחזוקה מתוכננת"** - השבתה מתוכננת מראש שעליה הודענו 48 שעות מראש.

**"זמן תגובה"** - הזמן מרגע פתיחת פנייה ועד לתגובה ראשונה.

**"זמן פתרון"** - הזמן מרגע פתיחת פנייה ועד לפתרון מלא.

---

### 2. התחייבות זמינות

#### 2.1 יעד זמינות

**99.9% Uptime חודשי**

זה אומר:
- **זמן השבתה מקסימלי**: 43.8 דקות לחודש
- **זמן השבתה מקסימלי**: 10.1 דקות לשבוע
- **זמן השבתה מקסימלי**: 1.44 דקות ליום

#### 2.2 חישוב זמינות

```
Uptime% = (זמן כולל - Downtime) / זמן כולל × 100
```

**לא נכלל בחישוב**:
- תחזוקה מתוכננת (עד 4 שעות לחודש)
- בעיות בצד הלקוח (אינטרנט, דפדפן, מכשיר)
- כוח עליון (מלחמה, רעידת אדמה, שביתות)
- התקפות DDoS או סייבר
- בעיות אצל ספקי צד שלישי (GCP, Stripe)

#### 2.3 מדידה

- **ניטור**: 24/7 מכל העולם
- **דיווח**: דוח זמינות חודשי
- **שקיפות**: Status page זמין ב-status.dentaflow.ai

---

### 3. זמני תגובה ופתרון

#### 3.1 רמות חומרה

| רמה | תיאור | דוגמאות |
|-----|-------|---------|
| **P1 - קריטי** | המערכת לא זמינה לחלוטין | שרת מושבת, אי אפשר להתחבר |
| **P2 - גבוה** | פונקציונליות מרכזית לא עובדת | תיאום תורים לא עובד, סוכן AI לא מגיב |
| **P3 - בינוני** | פונקציונליות משנית לא עובדת | דוח מסוים לא נטען, בעיית עיצוב |
| **P4 - נמוך** | בעיה קוסמטית או שאלה | שאלה כללית, בקשת תכונה |

#### 3.2 זמני תגובה (Response Time)

| תוכנית | P1 | P2 | P3 | P4 |
|--------|----|----|----|----|
| **Basic** | 4 שעות | 8 שעות | 24 שעות | 48 שעות |
| **Professional** | 2 שעות | 4 שעות | 12 שעות | 24 שעות |
| **Enterprise** | 1 שעה | 2 שעות | 4 שעות | 8 שעות |

**שעות תמיכה**: א'-ה', 09:00-18:00 (שעון ישראל)

#### 3.3 זמני פתרון (Resolution Time)

| תוכנית | P1 | P2 | P3 | P4 |
|--------|----|----|----|----|
| **Basic** | 24 שעות | 48 שעות | 5 ימים | 10 ימים |
| **Professional** | 12 שעות | 24 שעות | 3 ימים | 7 ימים |
| **Enterprise** | 4 שעות | 12 שעות | 2 ימים | 5 ימים |

---

### 4. תחזוקה מתוכננת

#### 4.1 הודעה מראש

- **תחזוקה רגילה**: 48 שעות הודעה מראש
- **תחזוקה דחופה**: 4 שעות הודעה מראש
- **תחזוקה קריטית**: ללא הודעה (במקרי חירום)

#### 4.2 חלון תחזוקה

**זמן מועדף**: שבת 02:00-06:00 (שעון ישראל)

**תדירות**: עד 4 שעות לחודש

#### 4.3 תקשורת

- **אימייל**: לכל המשתמשים הרשומים
- **Status Page**: status.dentaflow.ai
- **In-App Notification**: הודעה בממשק

---

### 5. ביצועים

#### 5.1 זמני טעינה

| מדד | יעד |
|-----|-----|
| **זמן טעינת דף** | < 2 שניות |
| **זמן תגובת API** | < 500ms |
| **זמן תגובת AI** | < 3 שניות |

#### 5.2 קיבולת

| תוכנית | משתמשים במקביל | בקשות API/דקה |
|--------|----------------|---------------|
| **Basic** | 10 | 100 |
| **Professional** | 30 | 300 |
| **Enterprise** | ללא הגבלה | ללא הגבלה |

---

### 6. גיבוי ושחזור

#### 6.1 גיבויים

- **תדירות**: יומי (כל 24 שעות)
- **שמירה**: 30 יום
- **מיקום**: 2 אזורים גיאוגרפיים (Europe, US)
- **הצפנה**: AES-256

#### 6.2 שחזור (Recovery)

- **RTO (Recovery Time Objective)**: 4 שעות
- **RPO (Recovery Point Objective)**: 24 שעות

**משמעות**:
- במקרה של אסון, נשחזר את השירות תוך 4 שעות
- תאבדו לכל היותר 24 שעות של נתונים

---

### 7. אבטחה

#### 7.1 הצפנה

- **בהעברה**: TLS 1.3
- **באחסון**: AES-256
- **גיבויים**: AES-256

#### 7.2 בקרת גישה

- **אימות דו-שלבי (2FA)**: זמין לכל המשתמשים
- **RBAC**: בקרת גישה לפי תפקיד
- **Audit Logs**: תיעוד מלא של כל הפעולות

#### 7.3 ציות

- **HIPAA**: ציות מלא
- **ISO 27001**: בתהליך הסמכה
- **SOC 2 Type II**: בתהליך הסמכה

---

### 8. פיצויים (Service Credits)

#### 8.1 זכאות

אם לא עמדנו ביעד הזמינות של 99.9%, תהיו זכאים לפיצוי.

#### 8.2 טבלת פיצויים

| Uptime חודשי | זיכוי |
|--------------|-------|
| 99.0% - 99.9% | 10% מהתשלום החודשי |
| 95.0% - 98.9% | 25% מהתשלום החודשי |
| < 95.0% | 50% מהתשלום החודשי |

#### 8.3 תביעת פיצוי

**איך לתבוע**:
1. שלחו אימייל ל-sla@dentaflow.ai
2. ציינו את התאריכים והשעות של ההשבתה
3. צרפו screenshots אם אפשר

**מועד**: תוך 30 יום מסוף החודש

**עיבוד**: תוך 15 ימי עסקים

**תשלום**: זיכוי בחשבונית הבאה

#### 8.4 הגבלות

- **מקסימום**: 50% מהתשלום החודשי
- **לא מצטבר**: לא ניתן לצבור זיכויים
- **פיצוי יחיד**: זיכוי הוא הפיצוי היחיד

---

### 9. תמיכה

#### 9.1 ערוצי תמיכה

| ערוץ | זמינות | זמן תגובה |
|------|---------|-----------|
| **אימייל** | 24/7 | לפי רמת חומרה |
| **צ'אט** | א'-ה', 09:00-18:00 | < 5 דקות |
| **טלפון** | Enterprise בלבד | < 2 דקות |

#### 9.2 פרטי יצירת קשר

**אימייל**: support@dentaflow.ai  
**טלפון**: [מספר טלפון] (Enterprise)  
**צ'אט**: דרך הממשק  
**Status Page**: status.dentaflow.ai

---

### 10. שינויים ב-SLA

אנו שומרים לעצמנו את הזכות לשנות SLA זה בהודעה של 30 יום מראש.

שינויים יפורסמו:
- באתר
- באימייל
- בממשק המערכת

---

### 11. יצירת קשר

**DentaFlow Ltd.**  
**אימייל**: sla@dentaflow.ai  
**טלפון**: [מספר טלפון]  
**כתובת**: [כתובת המשרד]

---

## English

### 1. Definitions

**"Uptime"** - The percentage of time the Service is available and operational.

**"Downtime"** - Period when the Service is unavailable or not functioning properly.

**"Scheduled Maintenance"** - Pre-planned downtime announced 48 hours in advance.

**"Response Time"** - Time from ticket opening to first response.

**"Resolution Time"** - Time from ticket opening to complete resolution.

---

### 2. Uptime Commitment

#### 2.1 Uptime Target

**99.9% Monthly Uptime**

This means:
- **Maximum downtime**: 43.8 minutes per month
- **Maximum downtime**: 10.1 minutes per week
- **Maximum downtime**: 1.44 minutes per day

#### 2.2 Uptime Calculation

```
Uptime% = (Total Time - Downtime) / Total Time × 100
```

**Excluded from calculation**:
- Scheduled maintenance (up to 4 hours per month)
- Client-side issues (internet, browser, device)
- Force majeure (war, earthquake, strikes)
- DDoS or cyber attacks
- Third-party provider issues (GCP, Stripe)

#### 2.3 Measurement

- **Monitoring**: 24/7 from worldwide locations
- **Reporting**: Monthly uptime report
- **Transparency**: Status page available at status.dentaflow.ai

---

### 3. Response and Resolution Times

#### 3.1 Severity Levels

| Level | Description | Examples |
|-------|-------------|----------|
| **P1 - Critical** | System completely unavailable | Server down, cannot log in |
| **P2 - High** | Core functionality not working | Appointment scheduling broken, AI agent not responding |
| **P3 - Medium** | Secondary functionality not working | Specific report not loading, design issue |
| **P4 - Low** | Cosmetic issue or question | General question, feature request |

#### 3.2 Response Times

| Plan | P1 | P2 | P3 | P4 |
|------|----|----|----|----|
| **Basic** | 4 hours | 8 hours | 24 hours | 48 hours |
| **Professional** | 2 hours | 4 hours | 12 hours | 24 hours |
| **Enterprise** | 1 hour | 2 hours | 4 hours | 8 hours |

**Support Hours**: Sun-Thu, 09:00-18:00 (Israel Time)

#### 3.3 Resolution Times

| Plan | P1 | P2 | P3 | P4 |
|------|----|----|----|----|
| **Basic** | 24 hours | 48 hours | 5 days | 10 days |
| **Professional** | 12 hours | 24 hours | 3 days | 7 days |
| **Enterprise** | 4 hours | 12 hours | 2 days | 5 days |

---

### 4. Scheduled Maintenance

#### 4.1 Advance Notice

- **Regular maintenance**: 48 hours advance notice
- **Urgent maintenance**: 4 hours advance notice
- **Critical maintenance**: No notice (emergency cases)

#### 4.2 Maintenance Window

**Preferred time**: Saturday 02:00-06:00 (Israel Time)

**Frequency**: Up to 4 hours per month

#### 4.3 Communication

- **Email**: To all registered users
- **Status Page**: status.dentaflow.ai
- **In-App Notification**: Notification in interface

---

### 5. Performance

#### 5.1 Load Times

| Metric | Target |
|--------|--------|
| **Page load time** | < 2 seconds |
| **API response time** | < 500ms |
| **AI response time** | < 3 seconds |

#### 5.2 Capacity

| Plan | Concurrent users | API requests/minute |
|------|------------------|---------------------|
| **Basic** | 10 | 100 |
| **Professional** | 30 | 300 |
| **Enterprise** | Unlimited | Unlimited |

---

### 6. Backup and Recovery

#### 6.1 Backups

- **Frequency**: Daily (every 24 hours)
- **Retention**: 30 days
- **Location**: 2 geographic regions (Europe, US)
- **Encryption**: AES-256

#### 6.2 Recovery

- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 24 hours

**Meaning**:
- In case of disaster, we will restore service within 4 hours
- You will lose at most 24 hours of data

---

### 7. Security

#### 7.1 Encryption

- **In transit**: TLS 1.3
- **At rest**: AES-256
- **Backups**: AES-256

#### 7.2 Access Control

- **Two-Factor Authentication (2FA)**: Available to all users
- **RBAC**: Role-based access control
- **Audit Logs**: Complete logging of all actions

#### 7.3 Compliance

- **HIPAA**: Full compliance
- **ISO 27001**: Certification in progress
- **SOC 2 Type II**: Certification in progress

---

### 8. Service Credits

#### 8.1 Eligibility

If we fail to meet the 99.9% uptime target, you are eligible for compensation.

#### 8.2 Credit Table

| Monthly Uptime | Credit |
|----------------|--------|
| 99.0% - 99.9% | 10% of monthly payment |
| 95.0% - 98.9% | 25% of monthly payment |
| < 95.0% | 50% of monthly payment |

#### 8.3 Claiming Credit

**How to claim**:
1. Send email to sla@dentaflow.ai
2. Specify dates and times of downtime
3. Attach screenshots if possible

**Deadline**: Within 30 days of end of month

**Processing**: Within 15 business days

**Payment**: Credit on next invoice

#### 8.4 Limitations

- **Maximum**: 50% of monthly payment
- **Non-cumulative**: Credits cannot accumulate
- **Sole remedy**: Credit is the only compensation

---

### 9. Support

#### 9.1 Support Channels

| Channel | Availability | Response Time |
|---------|--------------|---------------|
| **Email** | 24/7 | Per severity level |
| **Chat** | Sun-Thu, 09:00-18:00 | < 5 minutes |
| **Phone** | Enterprise only | < 2 minutes |

#### 9.2 Contact Details

**Email**: support@dentaflow.ai  
**Phone**: [Phone Number] (Enterprise)  
**Chat**: Through interface  
**Status Page**: status.dentaflow.ai

---

### 10. SLA Changes

We reserve the right to change this SLA with 30 days' notice.

Changes will be published:
- On website
- By email
- In system interface

---

### 11. Contact

**DentaFlow Ltd.**  
**Email**: sla@dentaflow.ai  
**Phone**: [Phone Number]  
**Address**: [Office Address]

---

**© 2025 DentaFlow Ltd. All rights reserved.**

